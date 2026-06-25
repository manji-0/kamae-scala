# Scala Domain Macros and Derivation

<!-- constrained-by ./domain-modeling.md -->
<!-- constrained-by ./boundary-defense.md -->

## Prefer Types First, Derivation Second

Scala 3 gives you opaque types, `given`/`using`, and compile-time derivation. Use
them only for repeated, stable patterns — not to hide missing domain modeling.
Before adding a macro library or blanket `derives Codec`, confirm the pattern
appears in at least three similar types and that hand-written code would drift.

Good derivation targets:

- boundary DTO codecs with explicit field names and defaults documented
- domain event case classes needing stable `name`/`version` metadata for outbox
- ID newtypes with shared non-empty / format validation in the companion

Poor derivation targets:

- one-off business rules or cross-field validation
- state-machine transitions — keep explicit methods on state types
- hiding `throw`, `.get`, or panics inside generated or macro-expanded code

## Use Existing Libraries Before Internal Macros

| Need | Prefer | Notes |
| --- | --- | --- |
| Validated primitives | [`library-guides/refined.md`](./library-guides/refined.md), `iron` | Keep invariants visible in source |
| JSON at the boundary | [`library-guides/circe.md`](./library-guides/circe.md) with explicit codecs | Avoid `derives Decoder` on domain IDs |
| Simple boilerplate | Scala 3 `derives Eq, Show` on **boundary** DTOs | Not on invariant-bearing domain states |
| Repeated event metadata | internal `inline given` or small macro in `domain` module | Only when events share identical shape |

Introduce an internal macro or meta-programming module (for example
`myapp.domain.macros`) when the team owns the pattern and libraries cannot express
the contract without leaking serde or ORM concerns into domain types.

## Opaque Types Beat Macros for IDs

Prefer module-scoped opaque types with validated companions before any macro:

```scala
object TaxiRequestDomain:
  opaque type RequestId = String

  object RequestId:
    def apply(raw: String): Either[DomainError, RequestId] =
      if raw.trim.isEmpty then Left(DomainError.EmptyId("request_id"))
      else Right(raw.trim)

    extension (id: RequestId) def value: String = id
```

See [`domain-modeling.md`](./domain-modeling.md). Macros that generate public
constructors without validation are worse than explicit companions in review.

## Recommended Internal Patterns

### Event metadata helper

Standardize event records used in outbox and projection pipelines:

```scala
trait DomainEvent:
  def name: String
  def version: Int

final case class DriverAssigned(
    requestId: RequestId,
    driverId: DriverId,
    occurredAt: OccurredAt
) extends DomainEvent:
  def name = "taxi.driver_assigned"
  def version = 1
```

If many events share the same shape, a small `inline def eventName[T <: DomainEvent]` or
internal macro may generate `name`/`version` — but keep payload fields explicit and
reviewable. Do not derive unrestricted Circe codecs on event payloads unless schema
evolution is documented (see [`service-boundaries.md`](./service-boundaries.md)).

### Declarative helpers for repetitive match arms

When full macros are heavy, a local `inline` helper can reduce duplication in
projection handlers:

```scala
inline def dispatchEvent[E <: DomainEvent](
    event: StoredEvent,
    handlers: PartialFunction[String, StoredEvent => Either[ProjectionError, Unit]]
): Either[ProjectionError, Unit] =
  handlers.lift(event.name).toRight(ProjectionError.UnknownEvent(event.name)).flatMap(_(event))
```

Keep helpers local to the crate that owns the events. Avoid exporting macro DSLs
across service boundaries.

## Circe / Config Derivation Rules

- Derive codecs on **DTOs** and wire formats, then map with `Either` into domain types.
- Do not `derives Decoder` on opaque domain IDs or state structs unless the project
  documents leaf validation (see [`boundary-defense.md`](./boundary-defense.md)).
- Flag `Configuration.derive` on types that carry domain invariants — config is a
  boundary; domain factories should still validate.

## Review Expectations for Generated Code

- Generated or derived instances must not add public mutable fields, `null` defaults,
  or silent coercion that bypasses invariants.
- `toString` / `Show` on events and IDs must remain safe for logs (see
  [`logging-metrics.md`](./logging-metrics.md)).
- Document on the type which behavior is derived and which validation runs at
  construction — especially for macro-expanded companions.

## When Not to Derive or Macro

- Cross-field validation (amount + currency, date ranges)
- State-machine transitions — explicit methods on `WaitingRequest`, `EnRouteRequest`, etc.
- ORM row mapping — use explicit mappers in infrastructure (see
  [`orm-adapters.md`](./orm-adapters.md))
- JNI/native struct mapping — explicit conversion at the boundary
