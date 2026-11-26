---
name: implement-feature
description: Implement an already-agreed Rust feature, clean up the implementation, run independent correctness and code-style reviews in parallel, and address verified feedback. Use when the user requests this complete implementation-and-review workflow from an agreed discussion; no written plan is required.
---

# Implement Feature

Carry the feature agreed in the conversation through implementation, sanity cleanup, two independent reviews, and feedback resolution. The main agent owns all edits; reviewers only investigate and report.

Invoking this workflow requests its delegated skill calls and authorizes clear, in-scope fixes from their feedback. Do not ask again for permission to implement the already-agreed feature or to apply routine cleanup. Questions that change behavior, scope, or architecture still need the user's decision.

## Establish the scope

- Read the applicable `AGENTS.md` and inspect the current checkout. Record the starting working-tree changes so unrelated user work stays outside the implementation and review scope.
- Recover the agreed behavior, constraints, and non-goals from the conversation. Ask only about missing decisions that materially affect implementation. Do not require or create a written plan.
- Resolve the three companion skills: [review-implemented-change](../review-implemented-change/SKILL.md), [code-style-review](../code-style-review/SKILL.md), and [reviewer-feedback](../reviewer-feedback/SKILL.md). These links refer to sibling skill directories; use their installed equivalents if the skills live elsewhere. Read their instructions rather than substituting remembered summaries.
- Confirm that two independent subagents can run with the main agent's model and reasoning effort. Prefer inherited settings when the delegation tool guarantees them; otherwise pass the known matching settings explicitly. Do not silently downgrade either setting. If the necessary skills, delegation, or matching settings are unavailable, explain the limitation before proceeding with a reduced workflow.

## 1. Implement

Implement the agreed feature using the repository's conventions. Preserve unrelated working-tree changes and keep any necessary refactoring within the feature's scope. Add or adjust high-signal tests for observable behavior and run the checks appropriate to the change.

Respect repository-specific dependency and approval requirements. This workflow does not authorize new dependencies or scope expansion by itself.

## 2. Sanity cleanup

Make a focused cleanup pass over the implementation and its immediate integration points:

- awkward APIs, unnecessary parameters or compatibility wrappers, and test-only alternatives to production APIs;
- fully qualified type or function paths where an import would be clearer and idiomatic, while preserving qualifications required by project conventions, including macros;
- leftovers of the replaced design: obsolete branches, helpers, comments, names, or duplicated logic;
- misplaced responsibilities, needless indirection, and inconsistencies with neighboring code;
- temporary or redundant tests with no useful regression value.

Fix clear issues without broadening the assignment into a general refactor. Re-run affected checks after cleanup. Resolve implementation failures before review; accurately report unavailable or blocked checks instead of presenting them as passing.

## 3. Independent parallel reviews

Freeze the implementation after cleanup. Both reviewers must inspect the same code state, including the scoped staged, unstaged, and untracked changes. Do not edit the shared checkout while either review is running. If the user or another process changes that state, resolve the scope and restart the affected review before treating its report as current.

Spawn two fresh subagents with the same model and reasoning effort as the main agent. Start both before waiting for either. Use an empty conversation history, such as `fork_turns="none"`, rather than inheriting the implementation discussion. Give each reviewer this neutral task context:

- the target checkout and exact review scope, including any relevant pre-existing changes and excluded user work;
- the agreed behavior, constraints, and non-goals needed to judge the change;
- validation commands and their actual results or limitations;
- the resolved path to its assigned skill and instructions to read applicable repository guidance and surrounding code.

Do not send the implementer's reasoning, self-assessment, suspected findings, or preferred verdict. Do not share one reviewer's findings with the other.

Assign the reviewers separately:

1. Invoke `$review-implemented-change` to review correctness, integration, maintainability, and architectural fit, with its secondary test-quality check.
2. Invoke `$code-style-review` to review high-confidence style and structure issues and return its proposed refactoring plan. This reviewer remains review-only; the main agent evaluates and applies applicable suggestions in the next stage.

Tell both reviewers to make no edits, run no formatting or other source-mutating commands, and send only their final report to the main agent. A focused check for a concrete concern is allowed if it preserves the reviewed code state; avoid concurrent checks that would conflict through shared artifacts. Reports must use plain Markdown with actionable file/line references, or explicitly state that there are no findings. A failed or incomplete review is not a clean review.

### Wait without inspecting their work

After dispatch, the main agent waits for completion. Use completion/status notifications only; do not read live transcripts, inspect reviewer scratch files, request interim findings, steer their reasoning, or conduct another review in parallel. Keep any required user-facing progress update brief and limited to completion status.

If one final report arrives first, hold it until the other reviewer finishes. Do not begin feedback resolution, edit the checkout, or relay that report to the other reviewer. If a reviewer needs a missing requirement clarified, handle that blocker explicitly and then resume the affected review; do not infer successful completion from silence or a timeout.

## 4. Resolve feedback

Once both reviews finish successfully, use `$reviewer-feedback` in the main agent on both final reports. Invocation of this workflow already requests applying clear, in-scope review fixes; the style review's proposed plan does not add a blanket approval gate here.

Evaluate findings against the actual code and the agreed intent. Merge duplicate findings while retaining their sources. Address correctness issues first where they affect style suggestions, and re-check each remaining suggestion against the code after earlier fixes. Parallel reports describe the same pre-fix state, so a suggestion may already have been resolved or become obsolete.

Apply correct, clearly applicable fixes. Explain rejected findings with evidence. If reports conflict or a proposed fix requires a consequential behavior, scope, or architecture decision, ask a focused question and keep that item pending while completing independent fixes. Do not settle such a conflict by inventing a new requirement.

Run the affected checks after fixes. The default is one parallel review round followed by feedback resolution, not a loop until both reviewers agree. Do not automatically restart the full workflow. Be clear that post-review fixes were validated by the main agent unless another review actually occurred.

If a review failed or was incomplete, report that stage as pending rather than claiming the full workflow is complete.

## Completion

Give a concise, self-contained result: what now works, validation performed, and the disposition of review findings. Group fixed items when useful, but account for pending and rejected findings with the reasoning the user needs. Do not repeat the full reports unless asked.

Leave the changes ready for the user. Commit or push only when requested; completing this workflow alone does not request either action.
