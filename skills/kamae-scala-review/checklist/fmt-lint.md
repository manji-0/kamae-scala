# Formatting and Lints Checklist
Reference: [`../../kamae-scala/references/fmt-lint.md`](../../kamae-scala/references/fmt-lint.md).

## 9.1 Is scalafmt clean? - Low

Flag unformatted touched Scala in projects that claim fmt gates.

## 9.2 Are scalafix/compiler warnings addressed? - Medium

Flag new warnings in domain modules when CI enforces clean builds.

## 9.3 Are suppressions narrow? - Medium

Flag broad `@nowarn` or file-level `scalafix:off` in domain code.

## 9.4 Do suppressions hide domain risk? - High

Flag suppressions covering non-exhaustive matches, deprecation of safety APIs, or unused error paths.

## 9.5 Do CI gates cover fmt/lint? - Medium

Flag projects with domain standards but no fmt/lint job.
