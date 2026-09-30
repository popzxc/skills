---
name: reviewer-feedback
description: Verify and address supplied code-review feedback, applying clear fixes and discussing findings that require clarification of the intended behavior or design.
---

# Reviewer Feedback

Evaluate each feedback item against the implementation, surrounding code, agreed requirements, and relevant conversation context. The reviewer may lack context about deliberate tradeoffs and design decisions.

## Apply clear fixes

Fix findings when they are correct, applicable, and have a clear resolution consistent with the agreed intent.

Use ordinary engineering judgment for implementation details and straightforward adjustments to the suggested fix that preserve its purpose. Routine choices do not require discussion.

## Discuss meaningful uncertainty

When a finding or proposed solution is not applicable as written, proceed only if the appropriate adjustment is clear and preserves the agreed intent.

If applying it requires resolving conflicting assumptions or choosing between interpretations that affect the feature's behavior, scope, or architecture, explain the mismatch and discuss it with the user before changing that part. Technical correctness alone does not settle these questions.

Do not silently reconcile conflicting assumptions by introducing a new design or requirement. State the competing interpretations and ask a focused question. Keep that item pending while continuing with independent, clearly applicable fixes.

If a finding is incorrect, explain why with evidence. Evaluate previously agreed decisions critically as well.

## Report the outcome

Respond in plain Markdown. Account for each item: fixed, needs discussion, or disagreed with, giving concise reasoning where needed. Summarize relevant validation and distinguish completed checks from assumptions.
