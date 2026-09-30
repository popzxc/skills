# Personal agent instructions and skills

Exported for easy reuse, not sure if anybody cares about the skills I use.
If you do, welcome.

## Contents

- [`AGENTS.md`](AGENTS.md): shared engineering practices and agent behavior preferences.
- [`review-implemented-change`](skills/review-implemented-change/SKILL.md): review uncommitted changes for correctness and architectural fit.
- [`reviewer-feedback`](skills/reviewer-feedback/SKILL.md): verify and address code-review feedback.
- [`rust-glancer-code-style-review`](skills/rust-glancer-code-style-review/SKILL.md): review rust-glancer code style and propose refactoring.
- [`rust-glancer-document-code`](skills/rust-glancer-document-code/SKILL.md): document an explicitly scoped part of rust-glancer.
- [`rust-glancer-next-slice`](skills/rust-glancer-next-slice/SKILL.md): implement the next approved slice of a rust-glancer plan.
- [`rust-glancer-plan-feature`](skills/rust-glancer-plan-feature/SKILL.md): plan a rust-glancer feature through explicit approval gates.

## Import

`AGENTS.md` was copied from `~/.codex/AGENTS.md`. Each directory under `skills/`
was copied from `~/.codex/skills/`, including its existing `agents/openai.yaml`
metadata where present. The imported files retain their original contents,
including local paths and invocation policies.

Bundled `.system` skills, plugin caches, credentials, settings, and session data
are outside the scope of this repository.

These files are independent copies. Editing them here does not update the
installed files in `~/.codex`.
