# eu.timepit.refined

Use `refined` for validated primitive newtypes at boundaries or for simple
single-field invariants. Prefer opaque types with explicit `Either` factories in
domain modules when validation messages must be domain-specific.

## When to Use

- Config keys, query parameters, or DTO fields with format rules (non-empty, UUID, positive Int)
- Gradual adoption: wrap legacy `String`/`Int` columns before full domain modeling

## When Not to Use

- Multi-field or state-dependent rules — use domain types and transitions instead
- Persisted aggregate roots where ORM mapping obscures the refined predicate

## Pattern

```scala
import eu.timepit.refined.api.*
import eu.timepit.refined.collection.NonEmpty
import eu.timepit.refined.refineEither

type NonEmptyString = String Refined NonEmpty

def parseRequestId(raw: String): Either[BoundaryError, NonEmptyString] =
  refineEither[NonEmpty](raw).left.map(_ => BoundaryError.EmptyId("request_id"))
```

Map refined DTO fields into opaque domain IDs with explicit error ADTs at the
adapter boundary. See [`../boundary-defense.md`](../boundary-defense.md) and
[`../domain-macros.md`](../domain-macros.md).
