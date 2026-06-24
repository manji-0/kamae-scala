# Scala Domain Modeling

## Represent Domain Concepts Explicitly

Use opaque types, value classes, sealed traits, and named case classes instead of primitive strings and numbers for semantically distinct values.

```scala
object RequestIds:
  opaque type RequestId = String

  object RequestId:
    def apply(value: String): Either[RequestIdError, RequestId] =
      val trimmed = value.trim
      if trimmed.isEmpty then Left(RequestIdError.Empty)
      else Right(trimmed)

    extension (id: RequestId) def value: String = id

export RequestIds.RequestId
```

Define opaque types inside an object (or class) module so the underlying representation stays abstract across files. Top-level opaque aliases are transparent only within the same source file.

Keep opaque-type internals private unless the value is deliberately transparent and has no invariant.

Model time, money, and units as explicit concepts. Prefer `OccurredAt`,
`ServiceDate`, `Money`, `CurrencyCode`, `DistanceMeters`, or
`DurationSeconds` over bare primitives whose unit, timezone, precision, or
rounding behavior is implicit. Avoid `Double` for money.

## Prefer Enums and Sealed Traits for Variants and State

Use Scala 3 `enum` or sealed traits for closed sets of states or domain alternatives. Prefer case-class variants when each state carries different data.

```scala
enum TaxiRequest:
  case Waiting(value: WaitingRequest)
  case EnRoute(value: EnRouteRequest)
  case InTrip(value: InTripRequest)
  case Completed(value: CompletedRequest)
  case Cancelled(value: CancelledRequest)
```

Use separate state types when transitions should accept only a specific source state.

## Define Aggregate Boundaries

An aggregate owns the invariants that must change atomically. Put transition
methods on the state or aggregate that owns the rule, and reference other
aggregates by ID unless a use case has loaded a stable snapshot for a decision.

For transaction scope, versioning, and cross-aggregate coordination, see
[`aggregate-transactions.md`](./aggregate-transactions.md).

## Keep Construction Honest

Use `apply`, `from`, or validated factory methods to enforce invariants at construction time. Do not expose public `copy` paths or mutable fields that let callers bypass those invariants.

Accept direct case-class literals only for simple data with no invariants or for test-only builders kept in test sources.

## Derive Behavior Deliberately

Do not provide default values for invariant-bearing domain types unless there is a
real domain default. Empty IDs, zero money, or the first enum case are
usually invalid or misleading defaults.

Keep `case class` types immutable. Broad mutable aggregates make stale copies easy to persist.

Do not derive unrestricted JSON codecs on domain types that
have private invariants. Use DTOs, row case classes, or validated decoders on leaf
value objects so deserialization still runs validation.

## Define Repository Ports with Traits

Keep persistence behind small traits in the domain or application layer:

```scala
trait TaxiRequestRepository[F[_]]:
  def findWaiting(id: RequestId): F[Option[WaitingRequest]]
  def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): F[Unit]
```

Adapters implement these traits with doobie, slick, or other stacks. Domain code should not import driver-specific types.

## Organize by Concept

Prefer modules such as `taxi.request`, `taxi.driver`, and `taxi.assignment` over catch-all `models` or `domain` packages that mix unrelated concepts.

## End-to-End Example

See [`../examples/src/main/scala/kamae/examples/TaxiRequest.scala`](../examples/src/main/scala/kamae/examples/TaxiRequest.scala) for opaque IDs, separate state types, and a typed transition.
