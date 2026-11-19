# Capture plan

Copy `assets/plan.example.json` and adapt it. The runner accepts ordinary JSON, not JSONC.

## Required inputs

- `workspace`: the Cargo workspace/fixture opened in the isolated editor.
- `servers.after`: an existing executable for the changed behavior.
- `scenes`: objects with a unique filesystem-safe `id`, workspace-relative `file`, and `marker`.
  `delta` moves the cursor within/after the marker. By default the last occurrence is used;
  `occurrence` selects a zero-based occurrence when needed.

`servers.before` can be omitted/null to use the selected extension's bundled server.
`extension.path` can be omitted to discover the newest installed stable version of
`extension.id` (default `rust-glancer.rust-glancer`) under `~/.vscode/extensions`.
An explicit path is more reproducible and is recorded in the manifest.

`readyRoot` defaults to `workspace`. Set it to the scene's Cargo workspace when the window root
is merely a parent directory. A single plan compares one active Cargo workspace.

For Rust Glancer, retain these defaults unless the extension interface changes:

```json
{
  "extension": {"id": "rust-glancer.rust-glancer"},
  "hooks": {
    "configuration": "rust-glancer",
    "serverPathSetting": "server.path",
    "start": "rust-glancer.startServer",
    "stop": "rust-glancer.stopServer",
    "state": "rust-glancer.test.getState",
    "output": "rust-glancer.test.getOutput"
  },
  "environment": {"RUST_GLANCER_EXTENSION_TEST": "1"}
}
```

The bridge expects the state hook to return Rust Glancer's
`session.running`, `session.hasClient`, `session.status.state`, and
`session.status.details.activeWorkspaceRoot` shape. Another extension needs matching hooks;
do not claim generic readiness support if its API differs. The runner checks that the state
reports the requested executable, so a hidden server override cannot silently invalidate a pair.

## Editor scenes

Supported `action` values:

| Action | Query evidence | Visible editor action |
| --- | --- | --- |
| `hover` (default) | Hover contents/range | Show Hover |
| `implementations` | Implementation locations | Peek Implementations |
| `definition` | Definition locations | Peek Definition |
| `references` | Reference locations | Show References |
| `folding` | Folding ranges | Fold imports and block/line documentation |
| `inlay-hints` | Inlay hints | Editor with inlay hints enabled |
| `completion` | Semantic completion items | Trigger Suggest |
| `editor` | Cursor/document/client state | Editor only, plus configured commands |

`allowEmpty: ["before"]` permits a genuinely absent provider result on the old side, such as a
new hover feature. Without this, queries retry for up to `queryTimeoutSeconds` (default 10) and
fail on persistent empty results. Do not use this to hide an indexing or activation failure.

`topLine` (zero-based, default 0) sets the same editor scroll origin for both sides.
`settleMilliseconds` (default 900) gives hover/peek/suggestion rendering time to finish.
`commands` optionally supplies `{ "id": "editor.someCommand", "args": [] }` entries replayed
after the main action. For a folding scene, commands override the two default fold commands.
These are explicit VS Code command IDs, not JavaScript or shell expressions.
Scenes replay saved source. Commands should present the editor rather than edit its text;
unexpected edits in the isolated buffer stop the capture instead of waiting for indexing.

`crop: [left, top, right, bottom]` uses **native image pixels**, not editor coordinates. Omit it
for a full-window first pass; inspect before deciding a crop. `width` sets the comparison's
maximum width per panel (default 1600); the compositor avoids upscaling.

## Settings and provenance

`settings` supplies isolated-profile VS Code settings. The defaults select Dark Modern,
semantic highlighting, inlay hints, a readable editor font, and hide unrelated panels. The
server path is set separately for each phase; do not set it in `settings`. For a version-specific
cache issue, prepare a fresh fixture/cache with the repository's supported tools before capture.
The runner does not delete user caches.

A project `.vscode/settings.json` server-path override takes precedence over the isolated
profile. The bridge detects that before switching phases and stops with a concrete explanation.
Use a clean fixture/workspace copy without the override; project settings are not edited.

Optional `provenance` is copied to the manifest. Use it for base/changed commits, PR number, or
build commands. None of it is drawn on screenshots. Actual source/binary hashes, client package
version, window IDs, scene query results, and owned-process cleanup are recorded automatically.

`readyTimeoutSeconds` defaults to 150. All API calls, native capture, activation, and shutdown
have finite deadlines. Run long captures as yielded terminal sessions so the agent can continue
providing progress updates. `--overwrite` allows recapturing existing originals; otherwise use
a fresh output directory. `--capture-only` skips composition for an initial crop inspection.

## Other captures

`scripts/window-capture.swift` uses ScreenCaptureKit, captures one owning PID/window, excludes
the pointer/shadow, activates the owning application by PID, and lists windows as JSON. The
renderer reports focus so another same-bundle Code instance cannot satisfy the focus check.
It is compiled into a temporary capture session;
no binary or SDK cache is written into the skill directory. On other operating systems, use an
available window-specific capture/control tool and the independent compositor. Do not fall back
to whole-desktop capture when that would include the user's unrelated work.
