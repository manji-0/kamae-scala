---
name: kamae-scala
description: |
  Kamae for Scala - robust server-side Scala 3 domain design. Use when implementing,
  modifying, refactoring, or fixing Scala domain models, use cases, repositories,
  state transitions, error ADTs, Either-based workflows, boundary DTO parsing,
  validation, PII handling, JNI/native boundary wrappers,
  scalafmt/scalafix quality gates, Scaladoc API contracts for domain code,
  CI setup for Scala domain checks, business logic, or review-adjacent remediation.
  Use when bootstrapping or documenting a local dev/test environment for
  Kamae-style Scala domain modules.
  Applies to server-side Scala modules, backend services, domain libraries, and CLIs
  with business rules. Skip frontend assets, build scripts, pure infrastructure,
  low-level native/performance tuning unrelated to domain boundaries, and code
  unrelated to domain logic.
---

# Kamae Scala

Use this skill as a thin dispatcher. Read only the topic and library guide files relevant to the current task.

## Step 0: Load Applicable Rules

Before any other step, read matching rule files in priority order:

1. `.claude/rules/*.md` and `.codex/rules/*.md` in the project root
2. `~/.claude/rules/*.md` and `~/.codex/rules/*.md`
3. `../../rules/defaults/*.md` relative to this `SKILL.md`

For each rule:

- Read YAML frontmatter. Skip it unless `applies-to` is `kamae-scala` or `*`.
- Group by `name`. The first tier above wins over later tiers; within a tier, the lexicographically last filename wins.
- Apply surviving `library-preference`, `convention`, and `override` rules throughout the task.

## Step 1: Detect Scala Context

Read `build.sbt`, `project/*.sbt`, and module manifests relevant to the edited files. Note these dependencies if present. Libraries with guide files load the guide only when relevant; detection-only libraries inform local conventions but do not require a guide.

- Error/effects: `cats`, `zio`; detection-only: `monix`, `fs2`
- Boundary/serialization: `circe`; detection-only: `play-json`, `json4s`, `upickle`, `pureconfig`
- Validation/units: `refined`; detection-only: `squants`
- Logging/tracing/metrics: `slf4s`, `logback`, `trace4cats`; detection-only: `kanela-agent`
- Secrets/credentials: load [`library-guides/secrets.md`](./library-guides/secrets.md) when API keys, tokens, or passwords appear in diff
- Persistence: `doobie`; detection-only: `slick`, `quill`, `skunk`
- Streams: `fs2`; detection-only: `pekko-stream`, `zio-streams`
- Async/RPC: detection-only: `pekko`, `http4s`, `sttp`
- Testing: `scalacheck`, `munit-scalacheck`; detection-only: `munit`, `scalatest`, `weaver`

If a library is relevant, load the matching file under [`references/library-guides/`](./references/library-guides/). Library guides cover library-specific defaults only; prefer the matching topic guide under `references/` for full patterns. If no library guide matches, use Scala 3 standard-library idioms before introducing a new dependency.

## Step 2: Load Topic Guides

Read only the topic file(s) needed for the task. Some topic files include
`constrained-by` HTML comments at the top; load those related guides when
applying the primary topic.

- Application Wiring: [`references/application-wiring.md`](./references/application-wiring.md)
- Aggregates and Transactions: [`references/aggregate-transactions.md`](./references/aggregate-transactions.md)
- Gradual Adoption: [`references/adoption.md`](./references/adoption.md)
- Domain Modeling: [`references/domain-modeling.md`](./references/domain-modeling.md)
- State Transitions: [`references/state-transitions.md`](./references/state-transitions.md)
- Error Handling: [`references/error-handling.md`](./references/error-handling.md)
- Boundary Defense: [`references/boundary-defense.md`](./references/boundary-defense.md)
- PII Protection: [`references/pii-protection.md`](./references/pii-protection.md)
- Logging and Metrics: [`references/logging-metrics.md`](./references/logging-metrics.md)
- JNI/Native Boundaries: [`references/jni-native-boundaries.md`](./references/jni-native-boundaries.md)
- Formatting and Lints: [`references/fmt-lint.md`](./references/fmt-lint.md)
- Quality Gates: [`references/quality-gates.md`](./references/quality-gates.md)
- Scaladoc Contracts: [`references/scaladoc.md`](./references/scaladoc.md)
- CI Setup: [`references/ci-setup.md`](./references/ci-setup.md)
- Local Validation Setup: [`references/local-validation.md`](./references/local-validation.md)
- Development Environment: [`references/dev-environment.md`](./references/dev-environment.md)
- Skill Repository Setup: [`references/development-setup.md`](./references/development-setup.md)
- Persistence and Events: [`references/persistence-events.md`](./references/persistence-events.md)
- ORM Adapters: [`references/orm-adapters.md`](./references/orm-adapters.md)
- Streams and Continuous Queries: [`references/stream-continuous-queries.md`](./references/stream-continuous-queries.md)
- Domain Macros and Derivation: [`references/domain-macros.md`](./references/domain-macros.md)
- Effect Systems: [`references/effect-systems.md`](./references/effect-systems.md)
- Service Boundaries: [`references/service-boundaries.md`](./references/service-boundaries.md)
- Test Data: [`references/test-data.md`](./references/test-data.md)
- Property-Based Tests: [`references/property-based-tests.md`](./references/property-based-tests.md)

## Core Stance

Model invalid states and invalid transitions out of the type system where it is practical:

- Use opaque types, value classes, sealed traits, private constructors, and validated `apply`/`from` factories.
- Use `Either[DomainError, T]` with domain-specific error ADTs in domain and use-case code.
- Avoid `throw`, bare `Exception`, and unsafe `.get`/`.head` in domain code.
- Parse external data into DTOs first, then convert DTOs into domain types.
- Keep persistence models, API DTOs, and domain models separate unless the project has an explicit convention otherwise.
- Keep JNI/native interop out of domain logic by default. When unavoidable, hide it behind a small safe API with documented invariants.
- Keep scalafmt and scalafix clean for touched Scala code. Treat suppressions as design decisions that need narrow scope and a reason.
- Document public domain APIs with Scaladoc that states invariants, errors, state transitions, and examples.
- Keep CI aligned with the checks reviewers rely on: format, lint, tests, Scaladoc, and optional native/security probes.

These are strong defaults, not absolutes. If existing project conventions conflict, follow the convention and leave a brief explanation when the deviation affects domain safety.

## Examples

Read [`examples/src/main/scala/kamae/examples/TaxiRequest.scala`](./examples/src/main/scala/kamae/examples/TaxiRequest.scala) only when a concrete state-transition example would clarify the task. The example intentionally omits full Scaladoc; follow [`references/scaladoc.md`](./references/scaladoc.md) for production public APIs.
