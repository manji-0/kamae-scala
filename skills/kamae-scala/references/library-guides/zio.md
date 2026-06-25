# ZIO Guide

> **When to load:** `build.sbt` contains `dev.zio` dependencies.
> **Related:** [`../effect-systems.md`](../effect-systems.md), [`../error-handling.md`](../error-handling.md), [`../application-wiring.md`](../application-wiring.md).

## Typed Error Channel

ZIO's `ZIO[R, E, A]` provides a typed error channel. Use domain error ADTs as `E`:

```scala
final class AssignDriver(
    requests: TaxiRequestRepository,
    drivers: DriverRepository
):
  def execute(cmd: AssignDriverCommand): ZIO[Any, AssignDriverError, Unit] =
    for
      waiting    <- requests.findWaiting(cmd.requestId)
                      .someOrFail(AssignDriverError.NotFound(cmd.requestId))
      profile    <- drivers.findAvailable(cmd.driverId)
                      .someOrFail(AssignDriverError.DriverNotAvailable(cmd.driverId))
      transition <- ZIO.fromEither(waiting.assignDriver(profile.toAssignment)
                      .left.map(AssignDriverError.Domain.apply))
      _          <- requests.saveAssigned(transition.state, transition.events)
    yield ()
```

Do not use `Throwable` as the error type in use case signatures unless the project explicitly allows it at the edge. Keep `Throwable` for infrastructure-level defects.

## ZLayer Composition

Define layers close to the adapters they wire. Do not put `ZLayer` definitions inside domain packages.

```scala
object DoobieTaxiRequestRepository:
  val layer: ZLayer[Transactor, Nothing, TaxiRequestRepository] =
    ZLayer.fromFunction(DoobieTaxiRequestRepository(_))
```

Compose layers in the application entry point:

```scala
object Main extends ZIOAppDefault:
  val appLayer =
    TransactorLive.layer ++
    HttpClientLive.layer >>>
    (DoobieTaxiRequestRepository.layer ++ DoobieDriverRepository.layer) >>>
    AssignDriver.layer

  def run = Server.start.provide(appLayer)
```

Keep the layer graph readable. When it grows past 10-15 layers, split into sub-graphs by domain module.

## ZIO.scoped for Resources

Use `ZIO.scoped` and `Scope` instead of manual acquire/release:

```scala
val managedTransactor: ZIO[Scope, Throwable, Transactor] =
  ZIO.acquireRelease(createTransactor)(t => ZIO.succeed(t.close()))
```

## Error Handling Patterns

Map infrastructure errors at adapter boundaries, not inside domain code:

```scala
// Adapter wraps JDBC exceptions
def findWaiting(id: RequestId): ZIO[Any, RepositoryError, Option[WaitingRequest]] =
  ZIO.attemptBlocking(doQuery(id))
    .mapError(RepositoryError.Jdbc.apply)
```

Use `mapError`, `catchSome`, or `orElseFail` over `catchAll` with pattern matching when only specific errors need translation.

## Testing

Use `ZIOSpecDefault` for integration tests. For domain and use case unit tests, prefer plain munit with synchronous assertions when the test does not need the ZIO runtime.

```scala
class AssignDriverSpec extends ZIOSpecDefault:
  def spec = suite("AssignDriver")(
    test("rejects inaccessible driver"):
      for
        result <- useCase.execute(command)
      yield assertTrue(result == Left(AssignDriverError.Domain(...)))
  ).provide(testLayer)
```

Keep test layers small. Inject fakes or in-memory implementations rather than full database layers in unit tests.
