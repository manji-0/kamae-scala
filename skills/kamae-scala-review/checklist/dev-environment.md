# Development Environment Checklist
Reference: [`../../kamae-scala/references/dev-environment.md`](../../kamae-scala/references/dev-environment.md).

## 11.1 Is the toolchain pinned? - Low

Flag unpinned Scala/sbt versions in new backend repos.

## 11.2 Is module layering respected? - Medium

Flag domain modules depending on infrastructure or interfaces.

## 11.3 Are test layers present? - Medium

Flag domain transitions without unit tests because only e2e tests exist.
