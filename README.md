# Personal agent instructions and skills

Exported for easy reuse, not sure if anybody cares about the skills I use.
If you do, welcome.

## Contents

- [`AGENTS.md`](AGENTS.md): shared engineering practices and agent behavior preferences.
- [`code-style-review`](skills/code-style-review/SKILL.md): review Rust code style and propose refactoring.
- [`document-code`](skills/document-code/SKILL.md): document an explicitly scoped part of a Rust project.
- [`next-slice`](skills/next-slice/SKILL.md): implement the next approved slice of a Rust project plan.
- [`plan-feature`](skills/plan-feature/SKILL.md): plan a Rust project feature through explicit approval gates.
- [`review-implemented-change`](skills/review-implemented-change/SKILL.md): review uncommitted changes for correctness and architectural fit.
- [`reviewer-feedback`](skills/reviewer-feedback/SKILL.md): verify and address code-review feedback.
- [`rust-glancer-vscode-before-after`](skills/rust-glancer-vscode-before-after/SKILL.md): capture matched VS Code screenshots comparing Rust Glancer servers.
- [`sketch-diagram`](skills/sketch-diagram/SKILL.md): create hand-drawn SVG diagrams with light and dark variants.
- [`write-technical-documentation`](skills/write-technical-documentation/SKILL.md): write technical guides and code-flow walkthroughs.
- [`zola-add-image`](skills/zola-add-image/SKILL.md): add supplied images to a Zola blog post.

## Import

`AGENTS.md` was copied from `~/.codex/AGENTS.md`. Each directory under `skills/`
was copied from `~/.codex/skills/`, including its existing `agents/openai.yaml`
metadata where present. The imported files retain their original contents,
including local paths and invocation policies.

Bundled `.system` skills, plugin caches, Python cache files, credentials, settings,
and session data are outside the scope of this repository.

These files are independent copies. Editing them here does not update the
installed files in `~/.codex`.
