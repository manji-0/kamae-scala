# Aggregates and Transactions

<!-- constrained-by ./persistence-events.md -->
<!-- constrained-by ./state-transitions.md -->
<!-- constrained-by ./application-wiring.md -->

## One Aggregate, One Transaction Boundary

When a use case changes one aggregate root, persist the new state and emitted events in a single transaction.

```scala
trait TaxiRequestRepository[F[_]]:
  def findWaiting(id: RequestId): F[Option[WaitingRequest]]
  def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): F[Unit]
```

The adapter should write state and append events atomically. If the database supports transactional outbox, insert events into an outbox table inside the same commit:

```scala
class DoobieTaxiRequestRepository[F[_]: MonadCancelThrow](xa: Transactor[F])
    extends TaxiRequestRepository[F]:

  def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): F[Unit] =
    val program = for
      _ <- sql"""UPDATE taxi_requests
                  SET status = \'en_route\', driver_id = \${state.driverId.value}
                  WHERE request_id = \${state.requestId.value}
                    AND version = \${state.version}"""
             .update.run
             .flatMap(rows =>
               if rows == 0 then FC.raiseError(StaleVersionException(state.requestId))
               else FC.unit
             )
      _ <- events.traverse_(e =>
             sql"""INSERT INTO outbox (aggregate_id, event_type, payload)
                    VALUES (\${state.requestId.value}, \${e.eventType}, \${e.toJson})"""
               .update.run
           )
    yield ()
    program.transact(xa)
```

Do not split aggregate state and its events across separate transactions. If the write succeeds but event insertion fails, downstream consumers see an inconsistent view.

## Versioning and Optimistic Concurrency

Add a `version` field to aggregate roots that are updated concurrently. Transitions check expected versions and return typed retryable errors instead of silently overwriting state.

```scala
final case class WaitingRequest(
    requestId: RequestId,
    passengerId: PassengerId,
    requiresAccessibleVehicle: Boolean,
    version: Long
)

enum PersistenceError:
  case StaleVersion(id: RequestId, expected: Long)
```

The adapter checks `WHERE version = :expected` and returns `StaleVersion` when zero rows are affected. Use cases decide whether to retry or propagate the error.

## Aggregate Scope Rules

Keep aggregates small. An aggregate should own only the data it needs to validate its own invariants. Signs that an aggregate is too large:

- Fields that are read but never validated together
- Multiple independent lifecycle states sharing one root
- Transactions that lock unrelated rows because they live under the same aggregate

When two concepts have separate lifecycles (e.g. `TaxiRequest` and `DriverProfile`), model them as separate aggregates and reference by ID.

## Cross-Aggregate Coordination

Prefer domain events and eventual consistency over mutating two aggregate roots in one transaction.

When a use case touches two aggregates, save the primary aggregate with an event and let a subscriber update the secondary. This avoids distributed locking and long transactions.

When a workflow must coordinate multiple roots synchronously (rare), orchestrate from the use case with explicit failure handling and document the coupling.

See [`persistence-events.md`](./persistence-events.md) and [`stream-continuous-queries.md`](./stream-continuous-queries.md).
