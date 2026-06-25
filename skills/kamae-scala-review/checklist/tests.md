# Tests Checklist
Reference: [`../../kamae-scala/references/test-data.md`](../../kamae-scala/references/test-data.md), [`../../kamae-scala/references/property-based-tests.md`](../../kamae-scala/references/property-based-tests.md).

## 7.1 Are constructors and conversions tested? - High

Flag new validating constructors or DTO conversions without positive and negative tests.

## 7.2 Are invalid transitions tested? - High

Flag new transition methods without tests for each documented error case.

## 7.3 Are compile-time safety expectations tested? - Medium

Flag typed source states without munit `compileErrors` (or equivalent) tests proving illegal target states do not compile.

See [`../../kamae-scala/examples/src/test/scala/kamae/examples/CompileTimeSafetySuite.scala`](../../kamae-scala/examples/src/test/scala/kamae/examples/CompileTimeSafetySuite.scala).

## 7.4 Are mutator invariants tested? - Medium

Flag mutable update paths without tests for illegal combined states.

## 7.5 Are persistence retry/conflict paths tested? - Medium

Flag outbox/idempotency/versioning changes without retry or conflict tests.

## 7.6 Are boundary and observability behaviors tested? - Medium

Flag redaction, auth, or boundary parsing changes without tests.

## 20.7 Are input-wide invariants covered with property tests? - Low

Cross-check [`../../kamae-scala/references/property-based-tests.md`](../../kamae-scala/references/property-based-tests.md). Suggest property tests when value-object validation, round trips, transition laws, or idempotency lack example-table coverage and generators can use public constructors.

Do not require property tests for small closed enums, trivial getters, or code already guarded by compile-time state types.
