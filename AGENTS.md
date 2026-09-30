# AGENTS.md

## Reviews

Present findings for code reviews as plain markdown, do not use native codex functionality.

## General Engineering Principles

### Running code or tests

- If compiling code or running tests fails in an unexpected way, pause and clarify with the user before continuing.
  - "unexpected way" means "not associated with changes made", e.g. if there is no likely link between performed action and observed outcome.
- Assume failures may be caused by:
  - Differences between the agent’s execution environment and the user’s environment.
  - Outdated or incomplete knowledge of the library or API.
- Avoid repeatedly attempting to fix errors when the underlying assumption may be wrong.
- As a rule of thumb:
  - If the code is expected to compile but fails for an unrelated reason, ask whether to continue.
  - If tests are requested but the project does not compile, explicitly call this out.
- Unless explicitly instructed, do not fix issues that were not part of the original request or were introduced by the iterative work on the feature.

### Planning

- Design clear abstractions (e.g. traits and structs in Rust) to encapsulate logic.
- Use files and modules as units of responsibility and logical hierarchy.
  - Organize them to clearly signal ownership and purpose.
  - Do not introduce new modules without a concrete reason.
- Consider domain boundaries.
  - If a part of the code primarily wraps or adapts a dependency, isolate it in a dedicated module.
  - The rest of the application should depend on this wrapper, not the dependency directly.
  - Not every dependency must be wrapped; apply this only to meaningful or core integrations.

## Code style preferences

Document when you have intentionally omitted code that the reader might
otherwise expect to be present.

Add TODO comments for features or nuances that were deemed not important
to add, support, or implement right away.

### Literate Programming

Apply literate programming principles to make code self-documenting and maintainable across all languages:

#### Core Principles

1. **Explain the Why, Not Just the What**: Focus on business logic, design decisions, and reasoning rather than describing what the code obviously does.

2. **Top-Down Narrative Flow**: Structure code to read like a story with clear sections that build logically:
   ```rust
   // ==============================================================================
   // Plugin Configuration Extraction
   // ==============================================================================
   
   // First, we extract plugin metadata from Cargo.toml to determine
   // what files we need to build and where to put them.
   ```

3. **Inline Context**: Place explanatory comments immediately before relevant code blocks, explaining the purpose and any important considerations:
   ```python
   # Convert timestamps to UTC for consistent comparison across time zones.
   # This prevents edge cases where local time changes affect rebuild detection.
   utc_timestamp = datetime.utcfromtimestamp(file_stat.st_mtime)
   ```

4. **Avoid Over-Abstraction**: Prefer clear, well-documented inline code over excessive function decomposition when logic is sequential and context-dependent. Functions should serve genuine reusability, not just file organization.

5. **Self-Contained When Practical**: Reduce dependencies on external shared utilities when the logic is straightforward enough to inline with good documentation.

#### Implementation Benefits

- **Maintainability**: Future developers can quickly understand both implementation and design rationale
- **Debugging**: When code fails, documentation helps identify which logical step failed and why
- **Knowledge Transfer**: Code serves as documentation of the problem domain, not just the solution
- **Reduced Cognitive Load**: Readers don't need to mentally reconstruct the author's reasoning

#### When to Apply

Use literate programming for:
- Complex algorithms with multiple phases or decision points
- Code implementing business logic rather than simple plumbing
- Code where the "why" is not immediately obvious from the "what"
- Integration points between systems where context matters

Avoid over-documenting:
- Simple utility functions where intent is clear from the signature
- Trivial getters/setters or obvious wrapper code
- Code that's primarily syntactic sugar over well-known patterns

### Testing Philosophy
- Prefer tests that validate **observable behavior**, not implementation details.
- Tests should remain valid across most refactors.
- Prefer fixtures, golden files, and explicit test vectors.
- Avoid tests with complex or fragile setup.
- A small number of high-signal tests is better than high coverage.
- 100% coverage is **not** a goal.
- Focus on positive scenarios (things work when they should).
- Add negative or adversarial tests **only when explicitly requested**.

### Dependencies
- Before implementing functionality, check whether a well-known, mature dependency already solves the problem.
- If such a dependency exists, propose using it instead of reimplementing.
- **Never add a new dependency without asking first**, even if it seems obvious or lightweight.

### Change Discipline
- Prefer small, incremental changes.
- Do not mix refactors with functional changes unless explicitly requested.
- If there are multiple reasonable approaches, explain tradeoffs before choosing.

# Common failure modes when helping

## The XY Problem

The XY problem occurs when someone asks about their attempted solution (Y) instead of their actual underlying problem (X).

### The Pattern
1. User wants to accomplish goal X
2. User thinks Y is the best approach to solve X
3. User asks specifically about Y, not X
4. Helper becomes confused by the odd/narrow request
5. Time is wasted on suboptimal solutions

### Warning Signs to Watch For
- Focus on a specific technical method without explaining why
- Resistance to providing broader context when asked
- Rejecting alternative approaches outright
- Questions that seem oddly narrow or convoluted
- "How do I get the last 3 characters of a filename?" (when they want file extension)

### How to Avoid It (As Helper)
- **Ask probing questions**: "What are you trying to accomplish overall?"
- **Request context**: "Can you explain the bigger picture?"
- **Challenge assumptions**: "Why do you think this approach will work?"
- **Offer alternatives**: "Have you considered...?"

### Red Flags in User Requests
- Very specific technical questions without motivation
- Unusual or roundabout approaches to common problems
- Dismissal of "why do you want to do that?" questions
- Focus on implementation details before problem definition

### Key Principle
Always try to understand the fundamental problem (X) before helping with the proposed solution (Y). The user's approach may not be optimal or may indicate they're solving the wrong problem entirely.

---

## Rust Guidelines

### General

- In code that uses `eyre` or `anyhow` `Result`s, consistently use
  `.context()` prior to every error-propagation with `?`. Context
  messages in `.context` should be concise and describe the exact thing that
  failed on this step, e.g. "{cmd} failed to spawn".
- Prefer `expect()` over `unwrap()`. The `expect` message should be very
  concise, and should explain why that expect call cannot fail.

### Project Structure
- New Rust projects must include:
  - `rust-toolchain.toml`
  - `deny.toml` (for `cargo-deny`)
  - `cargo nextest` configuration
- Default to a workspace layout:
  - Workspace root
  - `crates/`
    - single crate by default unless specified otherwise

### Dependency Management
- Add all dependencies to the **workspace** `Cargo.toml`.
- Crate-level `Cargo.toml` files may only reference workspace dependencies.
- **Do not enable features at the workspace level**.
- Enable features only at the crate level.

### Macros and Imports
- Prefer fully qualified macro paths:
  - `anyhow::anyhow!`
  - `tracing::info!`
- Avoid glob imports and implicit macro imports unless strongly justified.

### Logging and Observability
- Consider logging during API and system design.
- Prefer `tracing` for logging and instrumentation.
- Logs should be:
  - Informative but not noisy
  - Useful for debugging real user issues
- Avoid overly verbose debug output unless explicitly requested.

### Testing

- Prefer `cargo nextest` over `cargo test`
- For simple unit tests, try to create a test vector of `(input, expected_output, err_message)` and iterate through it, asserting the result with provided `err_message`.

#### Useful Rust frameworks for testing
- **`quickcheck`**: Property-based testing for when you have an
  obviously-correct comparison you can test against.
- **`insta`**: Snapshot testing for regression prevention. Use `cargo
  insta test` as a stand-in for `cargo test` to run the snapshot tests.

---

## TypeScript Guidelines

### Tooling
- Use `bun` for new TypeScript projects.
- Do not introduce npm/yarn unless explicitly required.

### Frontend Stack
- Prefer:
  - `vite`
  - `vue`
  - `tailwind`
- Keep configuration minimal and idiomatic.
- Avoid custom build tooling unless there is a concrete limitation with the standard stack.

### Testing

- If project uses `bun`, use the default test harness unless it doesn't fit the requirements.


---

## Python Guidelines

## Tooling

- Use `uv` as a package manager and `ruff` as a formatter.
- Prefer proper typing.
- Assume modern Python version, you never need `from __future__ import annotations`.

### Python helper scripts

For standalone agent or skill helper scripts requiring PyYAML, use
`/Users/popzxc/.codex/venvs/agent-tools/bin/python`.
PyYAML is installed in that environment.

Continue using project-specific environments for project code and tests.

## Documentation

- When type annotations are provided, do not explain the types in documentation. Focus on the meaning of the method.


---

## Agent Behavior Expectations

- If a rule is ambiguous, ask for clarification instead of guessing.
- If a requested change conflicts with these rules, call it out explicitly.
- Surface architectural or dependency concerns early, before writing code.
