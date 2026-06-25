# FS2

Use FS2 for stream ports on the read side, outbox dispatch, and projections.

## Keep Streams Out of Domain Code

Domain transitions return `Either` and event lists. Adapters expose `Stream[F, A]` over persisted logs or outbox tables.

## Prefer Typed Errors in Stream Elements

`Stream[F, Either[StreamError, DomainEvent]]` keeps mapper and decode failures explicit. Do not swallow failures with bare `handleErrorWith(_ => Stream.empty)` without metrics and dead-letter policy.

## Cancellation

Compile streams with `interruptWhen` or fiber cancellation so DB polling stops when consumers disconnect.

See [`../stream-continuous-queries.md`](../stream-continuous-queries.md).
