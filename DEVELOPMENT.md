# Development Guide

This document explains how to set up a local development environment for the
`kamae-scala` skill package and how to run the checks that keep the package valid.

## Prerequisites

- [sbt](https://www.scala-sbt.org/) 1.10+ with Scala 3.3+
- Java 17+ (Temurin or compatible)
- Python 3 (used for package validation and the review probe)

No additional libraries are required to edit the skill files. The Markdown
guides and checklists are plain text.

## Local Setup

Clone or navigate to the repository and run the package smoke test to confirm
that manifests, links, and scripts are intact:

```bash
python3 scripts/validate_package.py
```

If this passes, the skill package is structurally valid and can be loaded by a
Claude or Codex client that supports the manifest format.

## Running CI Checks Locally

The repository keeps skill content and tooling quality aligned. Run the same
checks that [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) runs before pushing:

```bash
./scripts/ci.sh
```

Or step by step:

```bash
python3 scripts/validate_package.py
python3 skills/kamae-scala-review/scripts/review_probe.py skills/kamae-scala/examples/src/main/scala --json
sbt scalafmtCheckAll "scalafixAll --check" "project taxiRequest" compile Test/compile test doc
```

See [`skills/kamae-scala/references/quality-gates.md`](./skills/kamae-scala/references/quality-gates.md)
for the canonical check commands and
[`skills/kamae-scala/references/ci-setup.md`](./skills/kamae-scala/references/ci-setup.md)
for workflow templates and when to extend the matrix.

For contributors working on this skill repository, read
[`skills/kamae-scala/references/development-setup.md`](./skills/kamae-scala/references/development-setup.md).

Application projects that follow the skill should also read
[`skills/kamae-scala/references/dev-environment.md`](./skills/kamae-scala/references/dev-environment.md)
for toolchain setup, module layout, test layers, and the local check loop, and
[`skills/kamae-scala/references/local-validation.md`](./skills/kamae-scala/references/local-validation.md)
when bootstrapping from templates.

## Working on Skills

Skill files live under `skills/`:

- `skills/kamae-scala/SKILL.md` — dispatcher for implementation guidance
- `skills/kamae-scala/references/*.md` — topic guides
- `skills/kamae-scala-review/SKILL.md` — dispatcher for review procedures
- `skills/kamae-scala-review/checklist/*.md` — review checklists

When adding a new topic:

1. Add a reference file under `skills/kamae-scala/references/`.
2. Link it from `skills/kamae-scala/SKILL.md` in Step 2.
3. Add a matching checklist under `skills/kamae-scala-review/checklist/` if the
   topic needs adversarial review coverage.
4. Link the checklist from `skills/kamae-scala-review/SKILL.md` in the routing
   matrix and checklist order.
5. Run `python3 scripts/validate_package.py` before committing.

## Cross-References

Use directive comments when a document depends on another section or file:

```markdown
<!-- constrained-by ./skills/kamae-scala/references/ci-setup.md -->
```

These directives are checked by the package validator along with ordinary
Markdown links. Declare real dependencies only.

## Submitting Changes

Before opening a pull request, ensure:

- `python3 scripts/validate_package.py` passes.
- Any new Markdown links point to existing files or anchors.
- New skill frontmatter has `name` and `description` fields.
- Skill directory names and frontmatter `name` values match.

## License

This project is released under the MIT License. See [LICENSE](./LICENSE).
