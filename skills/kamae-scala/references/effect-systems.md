# Effect Systems

> **When to read:** Choosing or reviewing Cats Effect, FS2, or ZIO wiring for use cases and repository ports.
> **Related:** [`error-handling.md`](./error-handling.md), [`application-wiring.md`](./application-wiring.md), [`state-transitions.md`](./state-transitions.md).

Domain transitions stay **synchronous and pure**. Effect types belong in use cases, repository ports, and adapters.

## Choose One Primary Stack

| Stack | Use case shape | Error channel |
| --- | --- | --- |
| Cats Effect + FS2 | `F[Either[UseCaseError, A]]` or `F[A]` with `ApplicativeError` | explicit `Either` or typed errors via type classes |
| ZIO | `ZIO[Env, UseCaseError, A]` | typed error channel on `ZIO` |
| `Future` (legacy) | `Future[Either[UseCaseError, A]]` | explicit `Either`; avoid bare `Future[A]` for business failures |

Pick one stack per service boundary. Mixing `IO`, `ZIO`, and `Future` in the same use-case layer requires explicit conversion at the composition root.

## Cats Effect Pattern

Keep domain code free of `F[_]`:

```scala
import cats.Monad

final class AssignDriver[F[_]: Monad](
    requests: TaxiRequestRepository[F],
    drivers: DriverRepository[F]
):
  def execute(command: AssignDriverCommand): F[Either[AssignDriverError, Unit]]
```

See [`state-transitions.md`](./state-transitions.md#keep-use-cases-thin) for a complete Cats Effect example.

Map infrastructure failures at the `.flatMap` site:

```scala
requests.findWaiting(id).attempt.flatMap:
  case Left(cause) => Monad[F].pure(Left(AssignDriverError.Repository(cause)))
  case Right(value) => ...
```

Prefer `MonadError`/`ApplicativeError` only when the project already standardizes on them. `F[Either[E, A]]` is the default Kamae shape for explicit business errors.

See [`library-guides/cats.md`](./library-guides/cats.md).

## ZIO Pattern

```scala
final class AssignDriver(
    requests: TaxiRequestRepository,
    drivers: DriverRepository
):
  def execute(command: AssignDriverCommand): ZIO[Any, AssignDriverError, Unit] =
    for
      waiting <- requests.findWaiting(command.requestId).someOrFail(AssignDriverError.RequestNotFound(command.requestId))
      profile <- drivers.findAvailable(command.driverId).someOrFail(AssignDriverError.DriverNotAvailable(command.driverId))
      transition <- ZIO.fromEither(waiting.assignDriver(profile.toAssignment).left.map(AssignDriverError.Domain.apply))
      _ <- requests.saveAssigned(transition.state, transition.events)
    yield ()
```

Use typed errors in the `ZIO` error channel for business failures. Do not use `Throwable` as the public use-case error unless the project explicitly allows it at the edge.

See [`library-guides/zio.md`](./library-guides/zio.md).

## Layering Rules

| Layer | Effect? | Notes |
| --- | --- | --- |
| Domain transition | No | `Either[DomainError, T]` only |
| Use case | Yes | orchestrates ports |
| Repository port | Yes | returns domain types, not rows |
| HTTP/RPC adapter | Yes | maps use-case errors to responses |

Do not block inside `F` (`Await.result`, `.unsafeRunSync()`) in use cases or domain code.

## Testing

- Domain tests: pure, no effect runtime.
- Use case tests: `Identity`/`StateT` fakes, or stub interpreters for ZIO layers.
- Integration tests: real runtime (`IOSuite`, `ZIOSpecDefault`) at adapter boundaries only.

See [`library-guides/cats.md`](./library-guides/cats.md) and [`library-guides/zio.md`](./library-guides/zio.md).
