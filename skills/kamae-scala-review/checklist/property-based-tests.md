# Property-Based Tests Checklist

Reference: [`../../kamae-scala/references/property-based-tests.md`](../../kamae-scala/references/property-based-tests.md).

## 16.1 Do generators use public constructors? - High

Flag ScalaCheck strategies that build domain case classes with raw literals or
bypass companions instead of validated `apply`/`from` factories.

## 16.2 Is each property a named invariant? - Medium

Flag property tests that only assert `isRight`/`isEmpty` or compare unstructured
output without stating the law (round trip, idempotence, rejection rule, etc.).

## 16.3 Are preconditions enforced explicitly? - Medium

Flag properties that treat out-of-domain inputs as success or failure ambiguously
instead of discarding them with `==>` or guarded generators.

## 16.4 Are illegal transitions tested for specific errors? - Medium

Cross-check [`state-transitions.md`](./state-transitions.md). Flag property
tests that only check `isLeft` on invalid transitions when callers depend on
the error variant.

## 16.5 Is non-deterministic I/O avoided inside properties? - High

Flag `forAll` blocks that hit live databases, networks, or wall-clock time
without injected fakes or seeded clocks.

## 16.6 Are regression seeds or minimal examples committed for fixed shrink cases? - Low

Suggest documenting or committing seeds when a property found a subtle bug and
the minimal counterexample should not disappear silently.
