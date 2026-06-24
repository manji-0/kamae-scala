# Quality Gates

> **When to read:** Before finishing changes to domain, boundary, PII, persistence, tests, or sample code. **Canonical command list** for local and CI checks.
> **Related:** [`local-validation.md`](./local-validation.md), [`ci-setup.md`](./ci-setup.md), [`dev-environment.md`](./dev-environment.md).

## Baseline Commands

Prefer the repository's existing commands when present; otherwise use these defaults for touched Scala code:

```bash
sbt scalafmtAll
sbt scalafixAll
sbt compile Test/compile
sbt test
sbt doc
```

In this skill repository, run the full local CI loop with:

```bash
./scripts/ci.sh
```

For narrow changes, run the smallest command set that covers the touched modules and state the limitation:

```bash
sbt "project domain" scalafmtCheck
sbt "project domain" test
```

Use `scalafmtCheckAll` in CI; apply with `scalafmtAll` locally when the format check fails.

## Skill-Package and Review Probe Checks

Skill/plugin repositories should also run:

```bash
python3 scripts/validate_package.py
python3 skills/kamae-scala-review/scripts/review_probe.py skills/kamae-scala/examples/src/main/scala --json
```

In the **kamae-scala** repository itself, use `scripts/validate_package.py` and the review probe script above. Example code lives in the sbt subproject `kamae-scala-taxi-request` under `skills/kamae-scala/examples/`; run `sbt test` from the repository root. See [`development-setup.md`](./development-setup.md) for this repo's dev workflow.

Application projects that install the skill may add the probe to CI or pre-push hooks when domain directories change:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py src/main/scala/domain/ src/main/scala/application/
```

## Compiler and Scalafix Signals That Matter for Domain Safety

Formatting keeps diffs reviewable so domain, boundary, PII, native, and persistence changes are easier to inspect.

Pay special attention to patterns that can hide invalid states or operational failures:

- `throw`, `???`, and unsafe `.get`/`.head` in domain/use-case code.
- Non-exhaustive `match` on sealed domain types.
- `Double` arithmetic in money, quantity, duration, or unit code.
- Broad `@nowarn` or `// scalafix:off` suppressions.
- Blocking calls inside effectful use cases without explicit boundaries.

See [`fmt-lint.md`](./fmt-lint.md) for suppression rules.

## Scaladoc

Generate docs for public domain APIs in CI when the project publishes libraries:

```bash
sbt doc
```

See [`scaladoc.md`](./scaladoc.md) for contract expectations.
