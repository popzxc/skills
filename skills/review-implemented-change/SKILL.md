---
name: review-implemented-change
description: Review uncommitted changes for correctness, maintainability, integration, and architectural fit.
---

# Review Implemented Change

Review uncommitted changes, including staged, unstaged, and relevant untracked files. Assume tests and lints pass; run checks only when needed to investigate a concrete concern.

## Primary focus: implementation

Focus on correctness, maintainability, proper integration, and overall architecture. Understand the intended behavior and examine surrounding code, callers, contracts, and related components to assess how the feature fits into the system.

Look for concrete bugs, integration gaps, misplaced responsibilities, and unnecessary complexity introduced by the change. Ground architectural concerns in practical consequences.

Allocate review effort according to implementation risk and impact. The test-quality guidance below is a secondary check; its level of detail should not determine its share of attention.

## Secondary check: test quality

Flag low-signal or bogus tests only with high confidence. Omit borderline cases. Look for tests that:

- Only verify that a dependency behaves as documented, without exercising the application's use of it.
- Lock in implementation details instead of observable behavior.
- Served as temporary implementation checks but have no credible long-term regression value.
- Make incidental side effects, undesired behavior, or a current limitation the intended outcome of the test.

Distinguish acknowledging a limitation from deliberately preserving it: a snapshot containing unsupported bits can be acceptable; a test whose purpose is to require that limitation is suspect.

For each test-quality finding, explain why the test lacks useful protection or preserves the wrong behavior.

## Findings

Present actionable findings in plain Markdown, ordered by importance, with file/line references and concrete impact. Avoid speculative concerns and stylistic preferences.
