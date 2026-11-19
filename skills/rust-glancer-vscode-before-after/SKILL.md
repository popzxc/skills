---
name: rust-glancer-vscode-before-after
description: Capture matched VS Code screenshots comparing Rust Glancer servers for PR descriptions or release posts, with labeled PNG and lossless WebP exports. Use only when explicitly invoked by the user.
---

# Rust Glancer VS Code Before/After

Use this skill only when the user explicitly invokes it. Do not select it automatically for
Rust Glancer changes, PR descriptions, or release work.

Produce native editor captures showing the same example and action before and after a change.
Preserve the originals and export a stacked comparison in **PNG and lossless WebP**. Its only
labels are **Before** and **After**, in the upper-left corner of each part. Keep version names,
project names, PR numbers, and explanatory prose out of the comparison headers.

## Choose the demonstration

Read the change and select a small number of scenes that visibly explain it. For hover changes,
show the hover over the same symbol. For implementation results, show the same Peek
Implementations view. For folding or inlay hints, show the same editor region. A still screenshot
usually cannot explain navigation motion or an internal performance change; do not force those
into a misleading picture.

Use the real project when the difference is clear there. Otherwise prepare a small fixture that
works with both versions. Keep its source, cursor target, theme, font, viewport, and editor
settings the same. Read the project's instructions for building historical/current binaries and
creating fixtures. Preserve the user's working changes.

## Capture on macOS

Read [references/capture-plan.md](references/capture-plan.md) for the plan schema and supported
editor scenes. Copy [assets/plan.example.json](assets/plan.example.json) to the chosen artifact
directory and fill in the workspace, server binaries, and scene markers. Paths are relative to
the plan file unless absolute; `~` and environment variables are expanded.

Use existing binaries, or build the before/after revisions separately with the repository's
normal workflow. The capture script intentionally does not build, check out, replace binaries,
or clear project caches. It uses the same installed VS Code client for both servers; supply an
explicit extension path when client choice matters. Changes to the client itself need a separate
client comparison, rather than this server-swap mode.

Choose an output directory in the user's requested location, or an ignored local reference
directory if the project provides one. Use a Python runtime with **Pillow already available**;
the Codex workspace dependency loader can locate one. Do not install dependencies just to run
this skill. The capture helper requires VS Code, the existing Swift command-line tools, and
macOS 14 or later. Composition alone works wherever Python and Pillow are available.

```sh
python /absolute/path/to/rust-glancer-vscode-before-after/scripts/capture.py \
  /absolute/path/to/plan.json --output /absolute/path/to/screenshots
```

Run editor launches/capture outside the sandbox when the environment requires it. The helper
uses a fresh profile, copies the selected installed extension, launches only its own VS Code
instance, and captures the window identified by that instance's PID. It batches all **before**
scenes, then all **after** scenes. No physical typing or mouse automation is needed.

It waits for the language server's active workspace, not merely a connected client, and records
provider results beside the screenshots. The packaged bridge defaults to Rust Glancer's server
path setting and lifecycle/test commands; the reference describes the configurable hooks for
another compatible extension. Test mode enables inspection/logging hooks, while the ordinary
language client still performs the editor actions.

Native window capture still needs Screen Recording access. If macOS prompts for access, report
that concrete blocker and allow the user to grant it. A fresh window ID is selected from the
owned process at capture time, since reloading can replace a window. The helper activates the
isolated profile before each scene because inactive VS Code windows can retain stale hover or
peek pixels even when their API results have changed.

If the user's app switching or input interferes with capture, explain what happened and stop
the affected capture instead of inventing alternate media. On a genuine activation/indexing
failure, preserve the diagnostic artifacts and follow the project's failure instructions.
Correct a demonstrated helper/plan mistake, but do not silently retry the same failed setup
indefinitely. Cleanup is bounded and targets only processes descended from the isolated editor.

## Inspect and compose

The output contains `SCENE/before.png`, `SCENE/after.png`, their JSON scene evidence,
`SCENE/comparison.png`, `SCENE/comparison.webp`, and a provenance/cleanup `manifest.json`.
Inspect both originals and the comparison with `view_image`. Confirm that the actual widgets
are visible, the difference is representative, and neither part shows a stale view. Provider
data alone does not verify a rendered screenshot.

Both parts use one crop and one scale. Put captions in separate header strips so they never
cover code, hover text, or results. Native originals remain unannotated. Prefer a tight crop
that retains enough code context and keeps text readable at the intended display size.

To adjust crops after seeing the originals, edit the scene's `crop`/`width` in the plan and run:

```sh
python /absolute/path/to/rust-glancer-vscode-before-after/scripts/compose.py \
  --plan /absolute/path/to/plan.json --input /absolute/path/to/screenshots
```

For a pair captured through another suitable tool:

```sh
python /absolute/path/to/rust-glancer-vscode-before-after/scripts/compose.py \
  --before /absolute/path/to/before.png --after /absolute/path/to/after.png \
  --output /absolute/path/to/comparison-directory --crop 0 64 2400 1200 --width 1600
```

The compositor verifies equal source dimensions and lossless PNG/WebP pixel equality, reports
sizes, and preserves a shared color profile. If the native captures differ in size, fix the
capture geometry; do not stretch one side to match. An identical-pixels warning means the
scene needs inspection and likely a better example.

Return clickable local PNG/WebP links and, when useful, show the comparison inline. Record
binary revisions and checksums in metadata rather than on the image. Local artifact paths are
not GitHub-hosted image URLs; a future PR attachment needs an appropriate upload step within
that task's authorized scope.
