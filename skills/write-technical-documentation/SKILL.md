---
name: write-technical-documentation
description: Write or revise standalone technical documentation, including architecture guides, subsystem explainers, and code-flow walkthroughs. Use simple prose, concrete examples, and verified source references to help a maintainer navigate and change the implementation. Use for requested explanatory documentation. Source-code documentation comments belong to the separate document-code skill.
---

# Write Technical Documentation

## Overview

Write documentation that helps a maintainer understand part of a codebase and
find the code they need to work on it. Assume the reader knows the project's
language but has not already reconstructed the subsystem's implementation.
The examples use Rust and illustrate a way of explaining code that applies
across projects.

Explain what enters the subsystem, what the code does with it, and what readers
can use afterward. Connect the conceptual explanation to actual entrypoints,
representations, and consumers. A symbol inventory alone is not an explainer.

A topic such as "body resolution code flows" is sufficient scope; the user does
not need to supply a symbol list or a chapter outline. Respect their requested
depth, destination, and exclusions. If they leave a subsystem as a black box,
explain its boundary without expanding into its internal algorithm.

This skill writes standalone guides and explanatory documents. Source comments
are a separate task; do not change implementation behavior while documenting it.

## Workflow

1. **Identify the reader's task.** What should they be able to follow, distinguish,
   or change after reading? Locate the relevant checkout or worktree and read
   the applicable `AGENTS.md` or `CLAUDE.md`, documentation conventions, and project vocabulary.
   Ask only when missing scope would materially change the work; choose routine
   organization yourself.
2. **Trace the implementation before drafting.** Read the main entrypoint, the
   representations passed between steps, the callers and consumers, and useful
   behavior fixtures. Follow surrounding code far enough to establish the actual
   flow. Existing docs and symbol names are leads, not proof of behavior.
3. **Choose a small explanatory spine.** Often this is input → preparation →
   transformation → stored result → query consumer. Use the actual control flow:
   recursive walks, deferred retries, and independent queries may not form one
   linear pipeline. Decide which distinctions the reader needs before each step.
4. **Draft in reading order.** Give the overview first, then work through a small
   example. Introduce implementation names where they become useful. Separate
   detailed topics when that makes them easier to read or revisit.
5. **Attach and check source references.** Link claims to the code implementing
   them. Confirm the example follows that code, including what is unknown or
   unsupported. Check that a statement about one path also holds on other paths
   before describing it as a general rule.
6. **Review and build the result.** Remove repetition and terminology that makes
   the reader work unnecessarily. Build generated documentation and check local
   links and anchors. Run behavioral checks only when needed to resolve a real
   uncertainty; documentation work does not automatically require the full test suite.

When extending a guide, preserve its useful structure and voice. Add depth where
requested and update links or earlier statements affected by the new explanation.
Do not rewrite the whole guide merely to make all chapters look alike.

## Voice And Density

Write plain pre-reading notes for a tired maintainer. Explain the part they need
to know before they open the linked code.

- Prefer familiar verbs and concrete subjects: "the table records assignments"
  rather than "assignment evidence is maintained by the inference infrastructure."
- Keep each paragraph about one idea. Use lists for real sequences and tables for
  distinctions the reader needs to compare.
- Short is good, but do not compress away the steps that make an explanation easy
  to enter. A slightly obvious sentence can be useful scaffolding.
- Explain why a distinction or operation matters. Do not invent a design rationale
  that the code or surrounding documentation does not support.
- Use the project's names consistently and qualify similar names when needed.
  Avoid inventing terminology for an existing concept.
- Avoid promotional wording, heavy noun phrases, and filler such as "seamlessly,"
  "robust infrastructure," "intentionally," or "deliberately."
- Prefer a concrete statement of supported behavior over stale-prone wording such
  as "currently" or an unrequested roadmap.

When proofreading user-written prose, preserve its structure, examples, and plain
voice. Fix ambiguity, grammar, or misleading statements. Do not make it more formal
unless the user asks for that rewrite.

## What To Borrow From The rustc Development Guide

Use these as style references when useful:

- [Getting Started](https://rustc-dev-guide.rust-lang.org/getting-started.html):
  orient the reader toward useful work and entrypoints without promising completeness.
- [Compiler overview](https://rustc-dev-guide.rust-lang.org/overview.html):
  explain the overall process before the implementation details.
- [HIR](https://rustc-dev-guide.rust-lang.org/hir.html):
  introduce a representation, then show how its storage and IDs are used.
- [Representing types](https://rustc-dev-guide.rust-lang.org/ty.html):
  distinguish similarly named representations with small examples before discussing internals.
- [Type inference](https://rustc-dev-guide.rust-lang.org/type-inference.html):
  start with observable Rust behavior, then explain the state and operations behind it.

The reusable pattern is: orientation, concrete example, necessary distinctions,
code flow, source pointers, then deeper details. Adapt that pattern to the topic;
do not force every chapter into a fixed template or fixed length.

Borrow the teaching style. Check the target checkout before making claims about
its behavior, supported features, or phase ordering.
These links are optional refreshers, not a requirement to reread the entire guide
for every documentation task.

## Explain Flows Through Data

For each important step, establish enough of the following to let the reader
follow it in code:

- Where execution enters and which operation owns the work.
- What its inputs mean, including the scope or owner needed to interpret them.
- Which representation it reads and which representation it produces.
- Whether it creates a value, changes shared state, records a relationship, or
  merely reads an existing result.
- What is retained, what is temporary, and when conversion or finalization happens.
- How a later consumer finds the result.

Choose the relevant questions rather than repeating this checklist in each section.
Name a type or field when it helps locate or distinguish the operation. Avoid
explaining every field or helper just because it exists.

Separate concepts that look alike but have different jobs. Common examples include
syntax versus semantic identity, a declaration parameter versus a call argument,
a live variable versus missing information, and a candidate versus a selected result.

Show the point where information changes, not just a list of methods called.
If later evidence helps earlier expressions, explain the shared state or retry
that connects them. Do not describe that as another syntax walk unless it is one.

## Examples And Counter-Examples

The examples below demonstrate writing patterns. Verify their technical claims
against the target checkout before using them in project documentation; they are
not a frozen architecture specification. Add verified source links to named
entrypoints in the actual document.

### 1. Start With Something The Reader Can Picture

Bad:

> Body resolution performs semantic enrichment over the lowered executable IR.

Better:

> Body IR first records expressions, statements, and scopes. For `user.name`, the
> structural node records the base expression and the field name. Resolution later
> records which field it refers to and the type of the result.

The better version supplies a concrete object and shows what the phase adds.
It does not require the reader to translate "semantic enrichment" first.

### 2. Walk Through A Transformation, Not A Call Inventory

Bad:

> `infer_body` calls `infer_parameters`, `infer_expr`, `fulfill_pending`, and `finish`.

Better:

```rust
fn identity<T>(value: T) -> T { value }

fn demo() {
    let value = identity(1u8);
}
```

> The call gives `identity`'s `T` a fresh variable, `?A`. Its parameter and return
> type both use that variable. Checking the argument learns `?A = u8`. The binding
> `value` shares the call result, so it learns the same type. Finalization exports
> the result as an owned type.

Attach entrypoints to these steps in the document. The list of calls can still
be a useful reading aid, but it cannot substitute for explaining what flows through them.

### 3. Distinguish Representations Before Comparing Their Operations

Bad:

> Types are lowered and raised as required by the resolver.

Better:

| Representation | What the reader needs to know |
| --- | --- |
| `TypeRef` | Describes written type syntax, including paths and `_`. |
| `solver::Ty<'s>` | A working semantic type that can retain live inference variables. |
| `rg_ty::Ty` | An owned semantic shape that can outlive the inference operation. |

> A body annotation is lowered into the body's working storage. Inference keeps
> those working types while constraints arrive. At completion, finalization follows
> learned assignments and exports owned types for body facts.

After establishing this distinction, link the actual lowering and finalization
functions. If another path exports earlier, explain that path instead of saying
all exports happen at the end.

### 4. Keep Declaration And Use-Site Context Separate

Bad:

> Generic `T` is inferred as `u8`.

Better:

> In `fn identity<T>(value: T) -> T`, `T` is a named parameter belonging to the
> declaration. In `identity(1u8)`, the call creates a fresh argument for that
> parameter and learns that the argument is `u8`. Another call can choose `bool`
> without changing the declaration's `T`.

When an item inherits generics, show both the full parameter order and its own
section. For `impl<T> Slot<T>` with `fn keep<U>`, the argument list includes
the impl's `T` as well as the method's `U`; a method turbofish supplies `U`.

### 5. Explain Why A Representation Matters

Bad:

> The live representation preserves inference-aware semantics across resolution boundaries.

Better:

> A field declared as `T` on `Wrapper<?A>` must return the same `?A` used by the
> receiver. Exporting the receiver as `Wrapper<Unknown>` would lose that connection:
> learning `?A = u8` later could no longer update what the field resolves to.

This explains why the representation matters before asking the reader to inspect
its implementation.

### 6. Explain The Consumer As Well As The Producer

Bad:

> Call inference stores the result in `CallFacts`.

Better:

| Question | Result to read |
| --- | --- |
| What type does the call return here? | The call expression's type facts. |
| Which function and generic arguments were selected? | `CallFacts`. |
| Which declarations can navigation offer? | Expression declaration resolutions. |

> `CallFacts` is attached to the call expression. For a path call, the callee path
> is a separate expression, so reading its type does not retrieve the call's final
> generic arguments.

The reader now knows both what was stored and how to avoid reading the wrong object.

### 7. Keep An Excluded Subsystem Useful As A Black Box

Bad, when the user asked to leave trait solving out:

> We must first understand canonical goal evaluation and response instantiation.

Better:

> Call preparation registers the selected function's requirements using the call's
> live arguments. Solver answers can refine those variables. The body then uses
> the new evidence to retry pending operations. This chapter stops at that boundary.

Explain the input, output, and effect on the surrounding flow. Cover the internal
algorithm when it is part of the requested scope.

### 8. Use Precise Source Pointers

Bad:

> See the `ty` crate for details.

Better:

> `InferenceState::finish` finalizes expression and binding types into `BodyFacts`.
> `BodyView::expr_ty` reads the stored result for an expression ID.

Link each named function to its verified source location. The prose should still
explain the step without requiring the reader to open every link.

## Source References And Accuracy

Put source links beside the claim or step they support. Prefer a meaningful
entrypoint or definition over a directory listing. Use a short label such as
`prepare_call`, not a paragraph-length path.

Use link targets that work in the chosen medium. Local file links, repository
links, or generated source pages can all be appropriate. Verify that a line anchor
lands on the named function or type; checking that the line exists is insufficient.
When rebuilding an existing guide, recheck locations that moved with code changes.

Use behavior fixtures or expected dumps to connect the explanation to observable
results when that helps. Do not run unrelated tests merely to produce a validation
statement. If a behavior remains uncertain after reading, verify it with an
appropriate focused check or describe the uncertainty precisely.

Document supported behavior at the point it matters. For example, storing a
function-pointer type does not establish that an indirect call gets selected by
the call resolver. Check the invocation path as well as the representation.

## Structure And Delivery

Prefer a small overview followed by chapters organized around flows or useful
distinctions. Use diagrams for phase or ownership relationships, tables for
representations and lookup choices, and Rust examples for concrete transformations.
Skip a visual when a short paragraph is clearer.

Use the requested format and destination. Otherwise follow the surrounding
documentation setup and favor a simple, already available backend. mdBook,
Markdown, or generated HTML are means of delivering the content, not requirements
of this skill. Avoid building a documentation framework before writing the explanation.

For generated output, keep the editable sources and a reproducible build command.
Local source pages are useful when offline code links matter, but do not introduce
them when existing repository links or tooling already serve the reader.

End with useful code-reading or change entrypoints when that helps the reader's
task. Do not append a repeated summary of everything the guide just explained.

## Final Review

- Can a maintainer follow one concrete value through the important steps?
- Are similarly named representations and different ownership scopes distinguished?
- Does the prose separate reading a result from computing, constraining, or finalizing it?
- Are ordinary paths, retries, and independent queries described accurately?
- Do examples match the implementation without implying unsupported behavior?
- Can readers find the relevant code and the result consumers from nearby links?
- Is each paragraph teaching something needed for the requested scope?
- Do generated output and links work, with editable sources left available?

Do not require every document to contain every example or section in this skill.
Use the guidance that helps the requested explanation.
