# Persistence and Events

<!-- constrained-by ./aggregate-transactions.md -->
<!-- constrained-by ./state-transitions.md -->
<!-- constrained-by ./boundary-defense.md -->

## Keep Repository Traits Small

Ports should express domain needs, not SQL shape.

```scala
trait TaxiRequestRepository[F[_]]:
  def findWaiting(id: RequestId): F[Option[WaitingRequest]]
  def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): F[Unit]
```

Avoid repository methods that accept raw SQL fragments, generic `Map[String, Any]`, or untyped JSON. The port signature should make it clear which domain types are stored and which events are persisted.

## Adapters Do Not Invent Events

Only domain transitions create business events. Repositories persist what the domain returns in `Transition(state, events)`.

```scala
// Good: use case passes transition results to the repository
val transition = waiting.assignDriver(driver.toAssignment)
requests.saveAssigned(transition.state, transition.events)

// Bad: repository creates events internally
class JdbcTaxiRequestRepository:
  def saveAssigned(state: EnRouteRequest): F[Unit] =
    // ... inserts state AND fabricates a DriverAssigned event
```

When events are created inside repositories, domain tests cannot verify the event stream without integration infrastructure.

## Mirror Invariants in the Database

Use constraints, check constraints, and enum columns that reflect domain states when practical.

```sql
CREATE TYPE request_status AS ENUM ('waiting', 'en_route', 'in_trip', 'completed', 'cancelled');

ALTER TABLE taxi_requests
  ADD CONSTRAINT chk_driver_when_en_route
  CHECK (status != 'en_route' OR driver_id IS NOT NULL);
```

Do not rely on the database to validate what the domain already rejected, but do prevent corrupt rows from silent insertion. Database constraints serve as a second line of defense.

## Outbox Pattern

For reliable event publishing, insert events into an outbox table inside the same transaction that updates aggregate state.

```scala
// Inside one doobie transaction:
for
  _ <- updateAggregate(state)
  _ <- events.traverse_(e => insertOutbox(e))
yield ()
```

A separate polling process or CDC pipeline reads the outbox and publishes to the message broker. This avoids dual-write inconsistency between the database and the event bus.

## Idempotent Retry Handling

Outbox and event consumers should tolerate duplicates with idempotency keys or natural keys derived from domain IDs.

```scala
// Consumer checks processed events before applying
def handleDriverAssigned(event: DriverAssigned): F[Unit] =
  isAlreadyProcessed(event.eventId).flatMap:
    case true  => Monad[F].unit
    case false => applyProjection(event) *> markProcessed(event.eventId)
```

## Event Versioning

When event schemas evolve, version payloads and support backward-compatible readers at the boundary.

```scala
enum TaxiRequestEvent:
  case DriverAssigned(requestId: RequestId, driverId: DriverId)  // v1
  case DriverAssignedV2(requestId: RequestId, driverId: DriverId, assignedAt: Instant)  // v2

// Boundary decoder handles both versions
def decodeEvent(eventType: String, payload: Json): Either[DecodeError, TaxiRequestEvent] =
  eventType match
    case "DriverAssigned.v1" => payload.as[DriverAssignedV1Dto].map(_.toDomain)
    case "DriverAssigned.v2" => payload.as[DriverAssignedV2Dto].map(_.toDomain)
    case other               => Left(DecodeError.UnknownEventType(other))
```

Keep event decoders at the boundary. Domain code works with the current event types.

See [`aggregate-transactions.md`](./aggregate-transactions.md) for transaction scope and [`stream-continuous-queries.md`](./stream-continuous-queries.md) for projection patterns.
