# AGENTS.md

## Communication

Whenever you respond, avoid using jargon. Prefer using simple words, orient your response
to a person for whom English is not a native language. Long sentences are fine, but complex
phrases or overly compacted sentences may increase cognitive overhead.

LLMs are prone to two failure modes: either generating a wall of text, or trying to compact
a lot of meaning into small amount of text. Both are very tiring. Instead, use a way that
is natural to humans: answer on the highest level that is appropriate for question without
digging into lower level details unless asked.

Depending on the context, there are two modes of communication:

**Default mode** Provide a concise, sufficient response, that can omit irrelevant clarifications.
The focus of a response is to answer on a level of detail that corresponds to the topic being
discussed. If user asks a question without mentioning a particular file, you should not respond
as if user knows which file is being discussed / remembers all the concrete decisions. For a
high level question, a high level answer is often sufficient. If user specifies a file, you
might assume that user has this file open and has context about it, but not necessarily context
about 10 other files that might be related. Before answering, think whether the answer assumes
the knowledge user might not have, and whether the answer includes details that are not
significant for the question asked.

In this mode, imagine that user asks you: `For (1), does it matter in which order we do things? Or not really? Can I start with dyn trait, then do closures, then do &Something? Or doing it in a specific order will be more optimal?`:

Bad answer would be:
```
There’s no hard dependency between dyn Trait and closures. But I’d slightly adjust your proposed order:
1. Preserve reference structure first, or alongside dyn Trait. This is the narrower foundational change: keep “this is a reference” even when its target is partly unknown. It is especially useful around trait objects, which frequently appear as &dyn Trait.
2. Implement dyn Trait. This gives us a meaningful representation of its declared capabilities, including bounds such as Send. It also improves the types we can later encounter inside closures.
3. Implement closure captures. This has more moving parts: which values are captured, whether they are borrowed or moved, and how that affects the closure’s capabilities. Having better representations for the captured types makes this work easier to reason about.
Your order would work, but leaving reference preservation until last could mean revisiting incomplete-type handling in both earlier steps.
Starting with dyn Trait is reasonable; I’d include reference preservation in that milestone, then tackle closures. We should agree on the meaning of missing information before either implementation, so they follow the same rules.
```

Good answer would be: `It doesn't matter much, but I suggest &Something, then dyn trait, then closures`.

**Clarification mode** If user asks a clarifying questions, it does not mean that you failed
and need to err to more detailed answers in the future. Clarifications are a normal part of
conversation, and it means that user want to go deeper. Treat it as a different communication
mode: until user keeps digging, your goal is to actually teach them and help understand the
topic, and build a mental model that would allow understanding the thing being discussed.
Depending on the situation, either short recap on the surrounding context or some examples
might be helpful. This is most relevant in situations where user studies LLM output, like
code review stage: in such situations, often what is needed is not an explanation of how
exactly code works, but rather the context on why the code is written that way: which task
does it solve, whether there are some caveats that affect the design, or there is a dependency
that is also important to understand (even if it's not explicitly mentioned; user reviews
code one file at a time, and might forget about some other thing, especially if it's not present
in the diff).

## Reviews

Present findings for code reviews as plain markdown in the reply, do not use the agent's native findings tool or format.

## Testing Philosophy

Good tests are the tests that survive refactoring. A good test should not assume the internal logic of a function
or internal dependencies; it should rely on a public interface.

Tests without setup usually are best checked with test vectors of `(input, expected, message)`.

Tests with setup have tendency of being fragile and hard to read. With such tests, it makes sense to invest into
architecture early. A good pattern is to create `tests/mod.rs` and `tests/utils.rs`, where `utils.rs` will provide
means to implement tests in a way that would allow focusing on the actual test logic.

When possible, the test should follow the arrange/assert pattern: first we perform an action, then we assert the
outcome. When possible, the best way to do it is to use a fixture and a snapshot with crates such as `expect_test`
or `insta`.

For each test, the focus should be on externally observable behavior. Locking the internal implementation details
or limitations is an anti-pattern. We do not seek 100% coverage, we aim to have small amount of high-signal tests.
During self-review, check if added tests justify the functionality being tested; if no, perform a cleanup and
remove the tests that were only useful to validate behavior and are unlikely to provide value in the future.

## Dependencies

Before implementing functionality, check whether a well-known, mature dependency already solves the problem. 
If such a dependency exists, stop and propose using it instead of reimplementing.

**Never add a new dependency to a workspace without asking first**, even if it seems obvious or lightweight.

Adding a common dependency already used inside of the workspace to a crate is fine, as long as it fits
the logical design of workspace and does not create architectural issues. Clear example: if `sqlx` is
used only in a single crate that isolates DB access from the rest of crates, adding `sqlx` elsewhere requires
asking for permission. Adding `tracing`, if it's already present in workspace, is fine in most cases.

---

## Rust Guidelines

### General

- In code that uses `eyre` or `anyhow` `Result`s, consistently use
  `.context()` prior to error-propagation with `?` when it adds genuine value. Context
  messages in `context` should be concise and describe the exact thing that
  failed on this step, e.g. "{cmd} failed to spawn".
- Prefer `expect()` over `unwrap()`. The `expect` message should be very
  concise, and should explain why that expect call cannot fail.
- In tests, `context` is typically not needed, and `unwrap` can be fine on self-obvious statements.
  For tests, it is important that the logical flow can be read.

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

- Prefer `cargo nextest` over `cargo test` when it's installed.
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

### Tooling

- Use `uv` as a package manager and `ruff` as a formatter.
- Prefer proper typing.
- Assume modern Python version, you never need `from __future__ import annotations`.

### Python helper scripts

For standalone agent or skill helper scripts requiring PyYAML, use
`~/.codex/venvs/agent-tools/bin/python` if it exists (PyYAML is installed there).
Otherwise, use `uv run --with pyyaml python ...`.

Continue using project-specific environments for project code and tests.

### Documentation

- When type annotations are provided, do not explain the types in documentation. Focus on the meaning of the method.
