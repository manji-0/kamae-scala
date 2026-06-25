---
name: kamae-scala-review
description: |
  Adversarial review of server-side Scala domain code for Kamae principles:
  explicit domain types, typed state transitions, Either-based domain errors,
  validated boundaries, PII redaction, and persistence/event consistency. Use
  when reviewing Scala pull requests, diffs, audits, or quality checks involving
  domain models, use cases, repositories, DTO conversion, JNI/native boundary
  wrappers, scalafmt/scalafix quality gates, Scaladoc API contracts,
  CI setup for Scala domain checks, or business logic. Skip frontend assets,
  build scripts, pure infrastructure, low-level native/performance tuning
  unrelated to domain boundaries, and code unrelated to domain behavior.
---

# Kamae Scala Review

Review Scala code against the knowledge base in `../kamae-scala/`. Prioritize bugs, invalid states, data leaks, and missing tests over style.

## Step 0: Load Applicable Rules

Read matching rule files in priority order:

1. `.claude/rules/*.md` and `.codex/rules/*.md` in the project root
2. `~/.claude/rules/*.md` and `~/.codex/rules/*.md`
3. `../../rules/defaults/*.md` relative to this `SKILL.md`

Skip rules unless `applies-to` is `kamae-scala-review` or `*`. A `check-toggle` rule with `enabled: false` disables the named check. A `convention` rule changes review expectations.

## Review Procedure

1. Read [`../kamae-scala/SKILL.md`](../kamae-scala/SKILL.md).
2. Read `build.sbt` and relevant library guides under `../kamae-scala/references/library-guides/`.
3. If available, run `python3 skills/kamae-scala-review/scripts/review_probe.py <changed Scala paths>` from the repository root. Treat the output as review leads, not findings.
4. Read the Scala files under review.
5. Choose checklist scope:
   - Full adversarial review: walk every checklist below in order.
   - Small/targeted diff: load only checklist files matched by the routing matrix, plus `tests.md` when behavior changes.
6. Report findings first, ordered by severity. Include `path:line`, risk, principle reference, evidence, and a concrete fix.

Example finding:

```text
High — src/application/AssignDriver.scala:42
Principle: error-handling §Avoid Throws in Domain Code
Evidence: `waiting.get` after `findWaiting` returns `Option`; a missing row throws via `.get` in production.
Fix: use `.toRight(AssignDriverError.RequestNotFound(requestId))` instead.
```

## Document Map

Checklist item numbers (`N.M`) match the checklist order below. Each checklist
links to its topic guide under `../kamae-scala/references/`.

| # | Checklist | Topic guide |
| --- | --- | --- |
| 1 | `domain-modeling.md` | `domain-modeling.md` |
| 2 | `state-transitions.md` | `state-transitions.md` |
| 3 | `error-handling.md` | `error-handling.md` |
| 4 | `boundary.md` | `boundary-defense.md` |
| 5 | `pii-protection.md` | `pii-protection.md` |
| 6 | `logging-metrics.md` | `logging-metrics.md` |
| 7 | `jni-native-boundaries.md` | `jni-native-boundaries.md` |
| 8 | `fmt-lint.md` | `fmt-lint.md` |
| 9 | `scaladoc.md` | `scaladoc.md` |
| 10 | `ci-setup.md` | `ci-setup.md` |
| 11 | `dev-environment.md` | `dev-environment.md` |
| 12 | `persistence-events.md` | `persistence-events.md` |
| 13 | `stream-continuous-queries.md` | `stream-continuous-queries.md` |
| 14 | `service-boundaries.md` | `service-boundaries.md` |
| 15 | `property-based-tests.md` | `property-based-tests.md` |
| 16 | `application-wiring.md` | `application-wiring.md` |
| 17 | `aggregate-transactions.md` | `aggregate-transactions.md` |
| 18 | `orm-adapters.md` | `orm-adapters.md` |
| 19 | `tests.md` | `test-data.md`, `property-based-tests.md` |

## Review Probe

The optional probe at [`scripts/review_probe.py`](./scripts/review_probe.py) scans Scala files for patterns that commonly route to Kamae checklists: native boundaries, suppressions, throws/unsafe gets, codec derives, PII terms, persistence/event code, and Scaladoc gaps.

Use probe output only to choose what to inspect. Do not report a finding until you have read the relevant code and confirmed a reachable invariant break, leak, unsoundness risk, or project-policy violation.

## Routing Matrix

| Changed area | Load these checklists first |
| --- | --- |
| Domain types / states | `domain-modeling.md`, `state-transitions.md`, `error-handling.md`, `tests.md` |
| HTTP/JSON/DB adapters | `boundary.md`, `orm-adapters.md`, `pii-protection.md`, `persistence-events.md`, `tests.md` |
| Use cases / wiring | `application-wiring.md`, `effect-systems` via `application-wiring.md`, `aggregate-transactions.md`, `error-handling.md`, `tests.md` |
| Streams / projections / outbox | `stream-continuous-queries.md`, `persistence-events.md`, `service-boundaries.md`, `tests.md` |
| Logging/metrics | `logging-metrics.md`, `pii-protection.md`, `tests.md` |
| Native/JNI modules | `jni-native-boundaries.md`, `boundary.md`, `tests.md` |
| Build/CI only | `ci-setup.md`, `fmt-lint.md` |

## Checklist Order

1. [`checklist/domain-modeling.md`](./checklist/domain-modeling.md)
2. [`checklist/state-transitions.md`](./checklist/state-transitions.md)
3. [`checklist/error-handling.md`](./checklist/error-handling.md)
4. [`checklist/boundary.md`](./checklist/boundary.md)
5. [`checklist/pii-protection.md`](./checklist/pii-protection.md)
6. [`checklist/logging-metrics.md`](./checklist/logging-metrics.md)
7. [`checklist/jni-native-boundaries.md`](./checklist/jni-native-boundaries.md)
8. [`checklist/fmt-lint.md`](./checklist/fmt-lint.md)
9. [`checklist/scaladoc.md`](./checklist/scaladoc.md)
10. [`checklist/ci-setup.md`](./checklist/ci-setup.md)
11. [`checklist/dev-environment.md`](./checklist/dev-environment.md)
12. [`checklist/persistence-events.md`](./checklist/persistence-events.md)
13. [`checklist/stream-continuous-queries.md`](./checklist/stream-continuous-queries.md)
14. [`checklist/service-boundaries.md`](./checklist/service-boundaries.md)
15. [`checklist/property-based-tests.md`](./checklist/property-based-tests.md)
16. [`checklist/application-wiring.md`](./checklist/application-wiring.md)
17. [`checklist/aggregate-transactions.md`](./checklist/aggregate-transactions.md)
18. [`checklist/orm-adapters.md`](./checklist/orm-adapters.md)
19. [`checklist/tests.md`](./checklist/tests.md)
