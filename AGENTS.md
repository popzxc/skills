# AGENTS.md

## Be short

LLMs are prone to writing walls of text, which is very tiring. Please be mindful of my time,
write your ideas in less words. State important things once. Do not over-explain unless asked.
Assume that I know what we're talking about. And I don't mean compacting the same wall of text
in less words, I mean only saying things that matter.

Bad example:

```
The change is done as you requested. I have run all the tests and they pass. The unstaged changes
are waiting for a review.

The change is doing what you requested, and here's an overview of what was done: <some more text>.

Verification passed: <xxx> tests, <yyy> this, <zzz> that.
```

Good example: `Done, tests pass.` or `Done, I did not run the tests.`

Bad response for `For (1), does it matter in which order we do things? Or not really? Can I start with dyn trait, then do closures, then do &Something? Or doing it in a specific order will be more optimal?`:

```
There’s no hard dependency between dyn Trait and closures. But I’d slightly adjust your proposed order:
1. Preserve reference structure first, or alongside dyn Trait. This is the narrower foundational change: keep “this is a reference” even when its target is partly unknown. It is especially useful around trait objects, which frequently appear as &dyn Trait.
2. Implement dyn Trait. This gives us a meaningful representation of its declared capabilities, including bounds such as Send. It also improves the types we can later encounter inside closures.
3. Implement closure captures. This has more moving parts: which values are captured, whether they are borrowed or moved, and how that affects the closure’s capabilities. Having better representations for the captured types makes this work easier to reason about.
Your order would work, but leaving reference preservation until last could mean revisiting incomplete-type handling in both earlier steps.
Starting with dyn Trait is reasonable; I’d include reference preservation in that milestone, then tackle closures. We should agree on the meaning of missing information before either implementation, so they follow the same rules.
```

Good example: `It doesn't matter much, but I suggest &Something, then dyn trait, then closures`.

Remember: if the answer is not detailed enough, I can always ask you to add more details.
Request to add more details lasts for ONE RESPONSE exactly.

## Reviews

Present findings for code reviews as plain markdown, do not use native codex functionality.

## Agent Behavior Expectations

- If a rule is ambiguous, ask for clarification instead of guessing.
- If a requested change conflicts with these rules, call it out explicitly.
- Surface architectural or dependency concerns early, before writing code.

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

---

## Rust Guidelines

### General

- In code that uses `eyre` or `anyhow` `Result`s, consistently use
  `.context()` prior to error-propagation with `?` when it adds genuine value. Context
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
