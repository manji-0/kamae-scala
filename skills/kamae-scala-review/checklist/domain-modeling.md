# Domain Modeling Checklist
Reference: [`../../kamae-scala/references/domain-modeling.md`](../../kamae-scala/references/domain-modeling.md).

## 1.1 Are semantic primitives represented as value types? - High

Flag bare `String`, `Int`, `Long`, `BigDecimal`, or `UUID` types used directly for distinct domain concepts such as user IDs, order IDs, email addresses, money amounts, quantities, or external references.

Suggest opaque types, value classes, or validating companions.

Do not flag primitives used as local temporaries, private adapter fields, test literals, serialization-only DTO fields, or values that have no domain-specific invariant beyond their Scala type.

## 1.2 Can callers bypass invariants? - High

Flag public `var` fields or public case-class `copy` paths on domain types that have invariants. Constructors must be the authoritative path.

Flag mutator methods that update only one field of a multi-field invariant, skip revalidation, or allow invalid intermediate states to escape.

## 1.3 Are states modeled explicitly? - Medium

Flag a single case class with `status: String` plus many optional fields when state-specific types or enum variants would make required fields explicit.

## 1.4 Are DTOs, DB rows, and domain entities separated? - Medium

Flag domain entities carrying automatic JSON/ORM codecs when that lets external data bypass validation or couples domain invariants to storage shape.

## 1.5 Is domain code organized by concept? - Low

Flag catch-all `Models.scala` or `package object domain` aggregations that mix unrelated concepts.

## 1.6 Are money, time, and units explicit? - Medium

Flag amounts, quantities, durations, rates, and timestamps when code mixes units, currencies, time zones, or inclusive/exclusive ranges without types or named constructors.
