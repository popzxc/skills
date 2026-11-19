# Rust Glancer Review Checks

- Prefer `rg_std::UniqueVec` for ordered sets instead of manually maintaining unique `Vec` semantics.
- Prefer `rg_std::ExpectedUnique` for values where any number may technically exist, but the normal and expected case is exactly one.
