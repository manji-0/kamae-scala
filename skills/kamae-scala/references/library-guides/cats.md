# Cats / Cats Effect Guide

> **When to load:** `build.sbt` contains `org.typelevel` with `cats-core` or `cats-effect`.
> **Related:** [`../effect-systems.md`](../effect-systems.md), [`../error-handling.md`](../error-handling.md), [`../application-wiring.md`](../application-wiring.md).

## Default Error Shape

Prefer `F[Either[UseCaseError, A]]` for business errors. Reserve `MonadError` / `ApplicativeError` for infrastructure failures that should short-circuit.

```scala
final class AssignDriver[F[_]: Monad](
    requests: TaxiRequestRepository[F],
    drivers: DriverRepository[F]
):
  def execute(cmd: AssignDriverCommand): F[Either[AssignDriverError, Unit]] = ...
```

Use `MonadError[F, Throwable]` only when the project has an explicit convention for typed error channels via `EitherT` or `ApplicativeError`. Mixing both styles in one codebase invites confusion about which errors are caught where.

## EitherT Usage

`EitherT` can reduce boilerplate in multi-step use cases but hides the error channel from callers who expect plain `F`. Use it inside a use case method and unwrap at the return boundary:

```scala
def execute(cmd: AssignDriverCommand): F[Either[AssignDriverError, Unit]] =
  (for
    waiting <- EitherT.fromOptionF(requests.findWaiting(cmd.requestId), AssignDriverError.NotFound(cmd.requestId))
    profile <- EitherT.fromOptionF(drivers.findAvailable(cmd.driverId), AssignDriverError.DriverNotAvailable(cmd.driverId))
    transition <- EitherT.fromEither[F](waiting.assignDriver(profile.toAssignment).left.map(AssignDriverError.Domain.apply))
    _ <- EitherT.liftF(requests.saveAssigned(transition.state, transition.events))
  yield ()).value
```

Do not expose `EitherT` in port signatures; keep ports returning `F[Option[A]]` or `F[A]`.

## Resource Management

Use `Resource[F, A]` for anything that must be released: database connections, HTTP clients, thread pools.

```scala
def appResources: Resource[IO, AppResources] =
  for
    xa     <- HikariTransactor.newHikariTransactor[IO](...)
    client <- EmberClient.default[IO]
  yield AppResources(xa, client)
```

Never call `.allocated` inside use cases. Allocate in `Main` or the composition root and pass the managed value down.

## Syntax Imports

Prefer selective imports over `cats.implicits._` (now `cats.syntax.all.*` in Scala 3):

```scala
import cats.syntax.flatMap.*
import cats.syntax.functor.*
import cats.syntax.traverse.*
```

Wildcard syntax imports add hundreds of implicit candidates and slow compilation.

## Testing Without IO

Domain tests stay pure. Use case tests can use `cats.Id` or a `StateT`-based fake:

```scala
type TestEffect[A] = cats.Id[A]
val useCase = AssignDriver[TestEffect](fakeRequests, fakeDrivers)
```

For tests that need real concurrency or timing, use `munit-cats-effect` or `weaver-cats`.
