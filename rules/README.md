# Kamae Scala Rules

Customize how `kamae-scala` and `kamae-scala-review` apply per project. Rules are Markdown files with YAML frontmatter.

## Rule Locations

Highest priority first:

| Tier | Path |
| --- | --- |
| Project | `.claude/rules/*.md`, `.codex/rules/*.md` |
| User | `~/.claude/rules/*.md`, `~/.codex/rules/*.md` |
| Plugin defaults | `rules/defaults/*.md` |

Same `name` on a higher tier wins. Same `name` on the same tier is resolved by lexicographically last filename.

## Rule Schema

```yaml
---
name: <kebab-case identifier>
description: <one-line summary>
applies-to: kamae-scala | kamae-scala-review | "*"
type: library-preference | check-toggle | convention | override
alwaysApply: false
---
```

Required fields:

| Field | Schema |
| --- | --- |
| `name` | Kebab-case rule identifier. Same-name rules override by tier. |
| `description` | One-line summary for humans and package validators. |
| `applies-to` | `kamae-scala`, `kamae-scala-review`, or `"*"`. |
| `type` | `library-preference`, `check-toggle`, `convention`, or `override`. |
| `alwaysApply` | Boolean. Defaults should normally use `false`. |

Optional fields:

| Field | Schema |
| --- | --- |
| `check` | Canonical check ID or alias for `check-toggle` rules. |
| `enabled` | Boolean for `check-toggle`; use `false` to disable a check. |

## Canonical Check IDs

Review checklist headings define canonical numeric check IDs. Rule toggles may also use the aliases below when a project wants a stable semantic name.

| ID | Alias | Checklist |
| --- | --- | --- |
| `1.1` | `semantic-value-types` | Domain modeling |
| `1.2` | `invariant-bypass` | Domain modeling |
| `1.3` | `explicit-states` | Domain modeling |
| `1.4` | `dto-row-domain-separation` | Domain modeling |
| `1.5` | `concept-organization` | Domain modeling |
| `1.6` | `explicit-money-time-units` | Domain modeling |
| `2.1` | `typed-source-state` | State transitions |
| `2.2` | `exhaustive-domain-match` | State transitions |
| `2.3` | `pure-transitions` | State transitions |
| `2.4` | `transition-ownership` | State transitions |
| `2.5` | `invariant-preserving-mutators` | State transitions |
| `2.6` | `auth-tenant-transition-guards` | State transitions |
| `2.7` | `concurrent-transition-protection` | State transitions |
| `3.1` | `no-domain-throws` | Error handling |
| `3.2` | `specific-domain-errors` | Error handling |
| `3.3` | `intentional-infra-error-mapping` | Error handling |
| `3.4` | `meaningful-error-variants` | Error handling |
| `4.1` | `boundary-dto-domain-conversion` | Boundary defense |
| `4.2` | `codec-is-not-validation` | Boundary defense |
| `4.3` | `external-format-overderive` | Boundary defense |
| `4.4` | `dto-defaults-unknown-fields` | Boundary defense |
| `4.5` | `auth-tenant-boundary-checks` | Boundary defense |
| `5.1` | `sensitive-wrapper` | PII protection |
| `5.2` | `pii-debug-log-redaction` | PII protection |
| `5.3` | `narrow-plaintext-exposure` | PII protection |
| `5.4` | `observability-redaction` | PII protection |
| `6.1` | `atomic-state-events` | Persistence and events |
| `6.2` | `use-case-repository-traits` | Persistence and events |
| `6.3` | `adapter-does-not-invent-events` | Persistence and events |
| `6.4` | `db-constraints-mirror-invariants` | Persistence and events |
| `6.5` | `idempotent-retry-handling` | Persistence and events |
| `6.6` | `event-versioning` | Persistence and events |
| `7.1` | `constructor-conversion-tests` | Tests |
| `7.2` | `invalid-transition-tests` | Tests |
| `7.3` | `compile-time-safety-tests` | Tests |
| `7.4` | `mutator-invariant-tests` | Tests |
| `7.5` | `persistence-retry-tests` | Tests |
| `7.6` | `boundary-observability-tests` | Tests |
| `8.1` | `no-native-domain-logic` | JNI/native boundaries |
| `8.2` | `safe-native-abstraction` | JNI/native boundaries |
| `8.3` | `native-invariant-docs` | JNI/native boundaries |
| `8.4` | `native-does-not-bypass-domain` | JNI/native boundaries |
| `8.5` | `native-boundary-tests` | JNI/native boundaries |
| `9.1` | `scalafmt-clean` | Formatting and lints |
| `9.2` | `scalafix-clean` | Formatting and lints |
| `9.3` | `narrow-lint-suppressions` | Formatting and lints |
| `9.4` | `lint-suppression-domain-risk` | Formatting and lints |
| `9.5` | `fmt-lint-ci-gates` | Formatting and lints |
| `10.1` | `scaladoc-public-contracts` | Scaladoc |
| `10.2` | `scaladoc-errors-throws` | Scaladoc |
| `10.3` | `scaladoc-safe-examples` | Scaladoc |
| `10.4` | `scaladoc-links` | Scaladoc |
| `10.5` | `scaladoc-lint-scope` | Scaladoc |
| `11.1` | `ci-required-reviewer-checks` | CI setup |
| `11.2` | `ci-representative-matrix` | CI setup |
| `11.3` | `ci-risk-tied-safety-jobs` | CI setup |
| `11.4` | `ci-advisory-check-clarity` | CI setup |
| `11.5` | `ci-local-reproduction` | CI setup |
| `12.1` | `dev-env-toolchain-pinned` | Dev environment |
| `12.2` | `dev-env-local-check-loop` | Dev environment |
| `12.3` | `dev-env-fake-port-test-isolation` | Dev environment |
| `13.1` | `log-structured-context` | Logging and metrics |
| `13.2` | `log-no-pii-in-default-level` | Logging and metrics |
| `13.3` | `log-correlation-ids` | Logging and metrics |
| `13.4` | `log-no-duplicate-error-chain` | Logging and metrics |
| `13.5` | `metrics-domain-counters` | Logging and metrics |
| `14.1` | `stream-backpressure-bounded` | Streams and continuous queries |
| `14.2` | `stream-error-supervision` | Streams and continuous queries |
| `14.3` | `projection-idempotent-offset` | Streams and continuous queries |
| `14.4` | `stream-resource-safety` | Streams and continuous queries |
| `15.1` | `macro-justified-repetition` | Domain macros |
| `15.2` | `macro-no-hidden-throw` | Domain macros |
| `15.3` | `derive-boundary-only-codecs` | Domain macros |
| `15.4` | `macro-visible-expansion` | Domain macros |
| `16.1` | `service-no-business-logic-in-routes` | Service boundaries |
| `16.2` | `service-anti-corruption-layer` | Service boundaries |
| `16.3` | `service-resilience-in-adapters` | Service boundaries |
| `16.4` | `service-contract-versioning` | Service boundaries |
| `17.1` | `property-constructor-roundtrip` | Property-based tests |
| `17.2` | `property-transition-laws` | Property-based tests |
| `17.3` | `property-gen-through-constructors` | Property-based tests |
| `17.4` | `property-shrink-diagnostics` | Property-based tests |
| `18.1` | `wiring-use-case-single-operation` | Application wiring |
| `18.2` | `wiring-composition-root-only` | Application wiring |
| `18.3` | `wiring-pure-domain-transitions` | Application wiring |
| `18.4` | `wiring-edge-error-mapping` | Application wiring |
| `18.5` | `wiring-test-fakes` | Application wiring |
| `19.1` | `aggregate-single-transaction` | Aggregate transactions |
| `19.2` | `aggregate-optimistic-concurrency` | Aggregate transactions |
| `19.3` | `aggregate-scope-minimal` | Aggregate transactions |
| `19.4` | `aggregate-cross-eventual-consistency` | Aggregate transactions |
| `20.1` | `orm-row-domain-separation` | ORM adapters |
| `20.2` | `orm-adapter-behind-port` | ORM adapters |
| `20.3` | `orm-no-domain-import-of-driver` | ORM adapters |

Example disabling a check:

```yaml
---
name: allow-generic-exception-in-domain
description: Permit generic Exception in this module's domain layer while migrating errors.
applies-to: kamae-scala-review
type: check-toggle
check: specific-domain-errors
enabled: false
alwaysApply: false
---
```

Rule bodies may add the rationale, scope, replacement convention, and sunset condition. Keep examples project-specific in project-level rules rather than plugin defaults.
