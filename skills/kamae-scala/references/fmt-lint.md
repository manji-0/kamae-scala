# Formatting and Lints

## Keep scalafmt Clean

Run `sbt scalafmtCheckAll` in CI and `sbt scalafmtAll` locally before pushing. Formatting is not a substitute for design review, but unformatted domain diffs hide risky changes.

Commit a `.scalafmt.conf` at the repository root and keep it aligned across modules.

## Use scalafix for Repeatable Lint Fixes

Enable scalafix rules that match project conventions. Prefer fixing issues over suppressing them.

Common useful rules for domain codebases:

- Remove unused imports and dead code
- Enforce explicit `match` exhaustiveness where possible
- Ban or flag deprecated APIs used accidentally at boundaries

## Suppressions Need Scope and Reason

`@nowarn`, `// scalafix:off`, and compiler `-Wconf` overrides should:

- Apply to the narrowest scope possible
- Name the invariant or external constraint they protect
- Be rare in domain packages

Flag broad module-level suppressions during review.

## CI Alignment

CI should run at least:

```bash
sbt scalafmtCheckAll
sbt test
```

Add `scalafixAll --check` when the project adopts scalafix rules beyond formatting.

See [`quality-gates.md`](./quality-gates.md) for the full gate list.
