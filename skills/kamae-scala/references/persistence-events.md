# Persistence and Events

## Keep Repository Traits Small

Ports should express domain needs, not SQL shape.

```scala
trait TaxiRequestRepository[F[_]]:
  def findWaiting(id: RequestId): F[Option[WaitingRequest]]
  def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): F[Unit]
```

## Adapters Do Not Invent Events

Only domain transitions create business events. Repositories persist what the domain returns in `Transition(state, events)`.

## Mirror Invariants in the Database

Use constraints, check constraints, and enum columns that reflect domain states when practical. Do not rely on the database to validate what the domain already rejected, but do prevent corrupt rows from silent insertion.

## Idempotent Retry Handling

Outbox and event consumers should tolerate duplicates with idempotency keys or natural keys derived from domain IDs.

## Event Versioning

When event schemas evolve, version payloads and support backward-compatible readers at the boundary.
