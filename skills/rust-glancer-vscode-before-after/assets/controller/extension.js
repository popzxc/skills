const vscode = require('vscode');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
let server;

exports.activate = async (context) => {
  const config = JSON.parse(fs.readFileSync(path.join(context.extensionPath, 'run.json'), 'utf8'));
  const { hooks } = config;
  const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
  const available = new Set(await vscode.commands.getCommands(true));
  let phase = 'before';

  async function bounded(promise, milliseconds, label) {
    let timer;
    try {
      return await Promise.race([promise, new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`${label} timed out`)), milliseconds);
      })]);
    } finally { clearTimeout(timer); }
  }
  async function command(id, ...args) {
    return await bounded(vscode.commands.executeCommand(id, ...args), config.readyTimeoutSeconds * 1000, id);
  }
  async function snapshot() {
    const client = await command(hooks.state);
    const editor = vscode.window.activeTextEditor;
    return { phase, client, focused: vscode.window.state.focused, file: editor?.document.uri.fsPath, visibleRanges: editor?.visibleRanges,
      position: editor?.selection.active, dirty: editor?.document.isDirty };
  }
  async function ready() {
    const deadline = Date.now() + config.readyTimeoutSeconds * 1000;
    let last;
    while (Date.now() < deadline) {
      last = await snapshot();
      if (last.dirty) throw new Error('The isolated capture buffer received edits; input may be interfering with the saved example');
      const session = last.client?.session;
      if (session?.running && session.hasClient && session.status.state === 'ready' &&
          path.resolve(session.status.details.activeWorkspaceRoot ?? '.') === config.readyRoot) {
        const actual = session.status.details.serverCommand ?? '';
        if (!actual.startsWith(config.servers[phase] + ' ')) throw new Error(`Wrong server: ${actual}`);
        return last;
      }
      if (last.client?.status?.state === 'failed') throw new Error(JSON.stringify(last.client));
      await pause(500);
    }
    throw new Error(`Workspace readiness timed out: ${JSON.stringify(last)}`);
  }
  async function provider(scene, id, ...args) {
    const allowEmpty = (scene.allowEmpty ?? []).includes(phase);
    const deadline = Date.now() + config.queryTimeoutSeconds * 1000;
    let result;
    do {
      result = await bounded(command(id, ...args), config.queryTimeoutSeconds * 1000, id);
      const populated = result != null && (Array.isArray(result) ? result.length > 0 :
        result.items ? result.items.length > 0 : true);
      if (populated || allowEmpty) return result ?? null;
      await pause(200);
    } while (Date.now() < deadline);
    throw new Error(`${scene.id}: ${id} returned no results for ${phase}`);
  }
  async function switchServer(next) {
    if (!['before', 'after'].includes(next)) throw new Error('Unknown phase');
    const setting = vscode.workspace.getConfiguration(hooks.configuration).inspect(hooks.serverPathSetting);
    if (setting?.workspaceValue !== undefined || setting?.workspaceFolderValue !== undefined) {
      throw new Error('Workspace settings override the server path; use a clean fixture or workspace copy without that override. Capture does not alter project settings.');
    }
    await bounded(vscode.extensions.getExtension(config.extensionId).activate(), config.readyTimeoutSeconds * 1000, 'activate extension');
    const state = await snapshot();
    phase = next;
    const actual = state.client?.session?.status?.details?.serverCommand ?? '';
    if (!state.client?.session?.running || !actual.startsWith(config.servers[next] + ' ')) {
      await command(hooks.stop);
      await vscode.workspace.getConfiguration(hooks.configuration).update(hooks.serverPathSetting, config.servers[next], vscode.ConfigurationTarget.Global);
      await command(hooks.start);
    }
    return await ready();
  }
  async function scene(id) {
    const spec = config.scenes.find(item => item.id === id);
    if (!spec) throw new Error('Unknown scene');
    for (const id of ['editor.action.hideHover', 'closeReferenceSearch', 'hideSuggestWidget']) {
      if (available.has(id)) await command(id);
    }
    const document = await vscode.workspace.openTextDocument(path.join(config.workspace, spec.file));
    const editor = await vscode.window.showTextDocument(document, {preview: false});
    if (document.isDirty) throw new Error('The isolated capture buffer received edits; use the saved example');
    await command('workbench.action.closeOtherEditors');
    await command('editor.unfoldAll');
    const text = document.getText();
    let offset;
    if (spec.occurrence == null) offset = text.lastIndexOf(spec.marker);
    else {
      offset = -1;
      for (let index = 0; index <= spec.occurrence; index++) {
        offset = text.indexOf(spec.marker, offset + 1);
        if (offset < 0) break;
      }
    }
    if (offset < 0) throw new Error(`Missing marker in ${spec.file}: ${spec.marker}`);
    offset += spec.delta ?? 0;
    if (offset < 0 || offset > text.length) throw new Error('Cursor offset outside the document');
    const position = document.positionAt(offset);
    editor.selection = new vscode.Selection(position, position);
    const top = Math.min(spec.topLine ?? 0, document.lineCount - 1);
    editor.revealRange(new vscode.Range(top, 0, top, 0), vscode.TextEditorRevealType.AtTop);
    for (const id of ['workbench.action.closeSidebar', 'workbench.action.closeAuxiliaryBar', 'workbench.action.closePanel']) {
      if (available.has(id)) await command(id);
    }
    await command('workbench.action.focusActiveEditorGroup');
    await ready();
    await pause(300);
    let results = null;
    const action = spec.action ?? 'hover';
    if (action === 'hover') {
      const hovers = await provider(spec, 'vscode.executeHoverProvider', document.uri, position);
      results = hovers?.map(hover => ({range: hover.range, contents: hover.contents.map(content => typeof content === 'string' ? content : content.value)})) ?? [];
      await command('editor.action.showHover');
    } else if (action === 'implementations') {
      results = await provider(spec, 'vscode.executeImplementationProvider', document.uri, position);
      await command('editor.action.peekImplementation');
    } else if (action === 'definition') {
      results = await provider(spec, 'vscode.executeDefinitionProvider', document.uri, position);
      await command('editor.action.peekDefinition');
    } else if (action === 'references') {
      results = await provider(spec, 'vscode.executeReferenceProvider', document.uri, position);
      if (results?.length) await command('editor.action.showReferences', document.uri, position, results);
    } else if (action === 'folding') {
      results = await provider(spec, 'vscode.executeFoldingRangeProvider', document.uri);
      if (!spec.commands) {
        await command('editor.toggleImportFold');
        await command('editor.foldAllBlockComments');
      }
    } else if (action === 'inlay-hints') {
      results = await provider(spec, 'vscode.executeInlayHintProvider', document.uri, new vscode.Range(0, 0, document.lineCount - 1, document.lineAt(document.lineCount - 1).text.length));
    } else if (action === 'completion') {
      results = await provider(spec, 'vscode.executeCompletionItemProvider', document.uri, position);
      await command('editor.action.triggerSuggest');
    } else if (action !== 'editor') throw new Error(`Unknown action: ${action}`);
    for (const item of spec.commands ?? []) await command(item.id, ...(item.args ?? []));
    await pause(spec.settleMilliseconds ?? 900);
    const final = await snapshot();
    if (document.isDirty || document.getText() !== text) throw new Error('The source changed during the scene; capture may have been interrupted');
    if (final.file !== document.uri.fsPath || !editor.selection.active.isEqual(position)) {
      throw new Error('The selected editor/cursor changed during the scene; capture may have been interrupted');
    }
    return {id, action, results, sourceSha256: crypto.createHash('sha256').update(text).digest('hex'), ...final};
  }

  server = http.createServer(async (request, response) => {
    response.setHeader('Content-Type', 'application/json');
    try {
      if (request.headers.origin || request.headers.authorization !== `Bearer ${config.token}`) {
        response.writeHead(403).end(JSON.stringify({error: 'Authorized local CLI requests only'}));
        return;
      }
      const url = new URL(request.url, 'http://localhost');
      let result;
      if (request.method === 'GET' && url.pathname === '/state') result = await snapshot();
      else if (request.method === 'GET' && url.pathname === '/output') result = hooks.output ? await command(hooks.output) : '';
      else if (request.method === 'POST' && url.pathname === '/phase') result = await switchServer(url.searchParams.get('name'));
      else if (request.method === 'POST' && url.pathname === '/scene') result = await scene(url.searchParams.get('id'));
      else if (request.method === 'POST' && url.pathname === '/close') {
        await command(hooks.stop);
        result = {stopped: await snapshot()};
        setTimeout(() => vscode.commands.executeCommand('workbench.action.closeWindow'), 200);
      } else throw new Error('Unknown capture action');
      response.end(JSON.stringify(result));
    } catch (error) {
      response.writeHead(500).end(JSON.stringify({error: String(error), stack: error.stack}));
    }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  fs.writeFileSync(path.join(context.extensionPath, 'bridge-info.json'), JSON.stringify({port: server.address().port, pid: process.pid}));
  context.subscriptions.push({dispose: () => server.close()});
};
exports.deactivate = () => server?.close();
