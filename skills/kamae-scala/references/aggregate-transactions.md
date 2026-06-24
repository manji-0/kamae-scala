# Aggregates and Transactions

## One Aggregate, One Transaction Boundary

When a use case changes one aggregate root, persist the new state and emitted events in a single transaction.

```scala
def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): F[Unit]
```

The adapter should write state and append events atomically.

## Versioning and Optimistic Concurrency

When aggregates use version fields, transitions should check expected versions and return typed retryable errors instead of silently overwriting state.

## Cross-Aggregate Coordination

Prefer domain events and eventual consistency over mutating two aggregate roots in one in-memory object graph. When a workflow must coordinate multiple roots, orchestrate from the use case with explicit failure handling.

See [`persistence-events.md`](./persistence-events.md).
