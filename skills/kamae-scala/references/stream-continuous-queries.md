# Streams and Continuous Queries

<!-- constrained-by ./persistence-events.md -->
<!-- constrained-by ./aggregate-transactions.md -->

## Use Streams for Event and Change Feeds

In event-sourced or CQRS designs, consumers often need a continuous feed of
aggregate changes rather than a one-shot query. Model these feeds with typed
stream ports at the adapter boundary, not as ad-hoc `while (true)` polling loops
inside domain code.

```scala
import fs2.Stream

trait AggregateEventSource[F[_]]:
  def subscribe(
      aggregateId: RequestId,
      after: Option[EventSequence]
  ): Stream[F, Either[StreamError, DomainEvent]]
```

Keep domain transitions synchronous. Streams belong in read-side projections,
outbox processors, and integration adapters that poll or subscribe to storage.

## Stack Choices

| Stack | Stream type | Typical use |
| --- | --- | --- |
| FS2 + Cats Effect | `fs2.Stream[F, A]` | Functional backends, outbox processors |
| ZIO | `zio.stream.ZStream[Any, E, A]` | ZIO-native services and projections |
| Pekko | `org.apache.pekko.stream.scaladsl.Source[A, M]` | Actor/streaming systems already on Pekko |

Pick one stream abstraction per bounded context. Do not mix three stream APIs in
the same module without an explicit adapter layer.

## Separate Command Path from Read Streams

| Concern | Shape | Notes |
| --- | --- | --- |
| Write use case | `F[Either[UseCaseError, Unit]]` | One command, one transaction boundary |
| Aggregate replay | `Stream[F, Either[_, DomainEvent]]` | Ordered events for one aggregate |
| Continuous query / projection | `Stream[F, Either[_, ReadModelRow]]` | Derived state, may lag the write model |
| Outbox dispatch | `Stream[F, Either[_, OutboxMessage]]` | At-least-once delivery; handlers must be idempotent |

Do not expose a `Stream` from a domain transition method. Emit events from the
transition, persist them atomically, then let adapters expose the persisted log
as a stream.

## Subscribe After Persisting

Start subscriptions from a durable cursor: event sequence, LSN, or `occurred_at`
plus tie-breaker. Avoid in-memory-only broadcast that drops events when a consumer
reconnects.

```scala
final case class EventCursor(
    aggregateId: RequestId,
    afterSequence: EventSequence
)

trait OutboxReader[F[_]]:
  def streamPending(batchSize: Int): Stream[F, Either[StreamError, OutboxRow]]
```

When a projection catches up, store the checkpoint in the same persistence
technology as the projection table so restarts resume safely.

## Handle Backpressure and Cancellation

Streams that ignore backpressure can exhaust memory or duplicate work when
consumers are slow.

- Use bounded queues/channels between pollers and handlers (`fs2.concurrent.Channel`, `Queue.bounded` in ZIO).
- Tie stream lifetimes to effect cancellation: when an HTTP request or fiber is interrupted, stop polling and release DB cursors.
- Treat terminal stream errors according to documented retry semantics; do not silently restart without deduplication.

```scala
source
  .subscribe(requestId, cursor)
  .evalMap:
    case Left(err) => StreamErrorMapper.toF(err)
    case Right(event) => handler.apply(event)
  .interruptWhen(shutdownSignal)
```

## Projections Must Be Deterministic and Idempotent

Continuous queries rebuild read models from event streams. Each handler should:

1. Parse the payload into a typed domain or integration event at the boundary.
2. Apply the update idempotently using event ID or `(aggregateId, sequence)`.
3. Skip or dead-letter unknown event types/versions according to schema policy.

Do not call aggregate transition methods from projections. React to events; do
not mutate authoritative write-model aggregates from the read path.

For write-side transactions, versioning, and outbox atomicity, see
[`aggregate-transactions.md`](./aggregate-transactions.md) and
[`persistence-events.md`](./persistence-events.md).

## Detection Hints

When `build.sbt` includes `fs2`, `pekko-stream`, or `zio-streams`, prefer typed
stream ports over manual sleep/poll loops. Load this guide with persistence and
service-boundary guides when the diff touches subscriptions, projections, or
outbox processors.

See [`library-guides/fs2.md`](./library-guides/fs2.md) when FS2 is on the classpath.
