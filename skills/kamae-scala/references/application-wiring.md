# Application Wiring

<!-- constrained-by ./state-transitions.md -->
<!-- constrained-by ./error-handling.md -->
<!-- constrained-by ./effect-systems.md -->

## Model Use Cases as Small Classes

Inject ports through constructor parameters or reader/environment layers. Avoid static singletons for repositories and clients.

```scala
final class AssignDriver[F[_]: Monad](
    requests: TaxiRequestRepository[F],
    drivers: DriverRepository[F]
)
```

Each use case class should own one business operation. When a class accumulates many unrelated methods, split it by command or query.

## Composition Root

Wire concrete adapters only in the application bootstrap module (`Main`, `Bootstrap`, or ZIO `App` layer). Domain and application packages should depend on traits, not JDBC/HTTP drivers.

```scala
// Good: Main wires everything
object Main extends IOApp.Simple:
  def run: IO[Unit] =
    val xa = Transactor.fromDriverManager[IO](...)
    val requestRepo = DoobieTaxiRequestRepository(xa)
    val driverRepo  = DoobieDriverRepository(xa)
    val assignDriver = AssignDriver(requestRepo, driverRepo)
    HttpServer.start(assignDriver)
```

### ZIO Layer Pattern

```scala
object Main extends ZIOAppDefault:
  val layer =
    DoobieTaxiRequestRepository.layer ++
    DoobieDriverRepository.layer >>>
    AssignDriver.layer

  def run = Server.start.provide(layer)
```

Keep layer definitions close to the adapters they wire. Do not define layers inside domain packages.

## Keep Domain Transitions Pure

Use cases load state, call pure transitions, then persist results. Do not embed SQL or JSON parsing inside transition methods.

```scala
// Good: use case orchestrates, transition is pure
def execute(command: AssignDriverCommand): F[Either[AssignDriverError, Unit]] =
  for
    waiting <- requests.findWaiting(command.requestId)
    result  =  waiting.map(_.assignDriver(driver.toAssignment))
    _       <- result.traverse(t => requests.saveAssigned(t.state, t.events))
  yield result.toRight(AssignDriverError.RequestNotFound(command.requestId)).flatten.void
```

## Error Mapping at the Edge

HTTP/gRPC/CLI adapters map `UseCaseError` to response codes and client-safe messages. Do not leak repository exception strings by default.

```scala
def handleAssignDriver(command: AssignDriverCommand): F[Response] =
  assignDriver.execute(command).map:
    case Right(_)                                    => Response(Status.Ok)
    case Left(AssignDriverError.RequestNotFound(_))  => Response(Status.NotFound)
    case Left(AssignDriverError.DriverNotAvailable(_))=> Response(Status.Conflict)
    case Left(AssignDriverError.Domain(_))           => Response(Status.UnprocessableEntity)
```

Do not catch and rethrow infrastructure exceptions inside use cases. Let them propagate to the adapter or middleware for logging and generic error responses.

## Test Wiring

Use case tests inject fakes or in-memory implementations of ports. Avoid spinning up databases or HTTP servers for business logic tests.

```scala
class AssignDriverSuite extends FunSuite:
  val fakeRequests = InMemoryTaxiRequestRepository()
  val fakeDrivers  = InMemoryDriverRepository()
  val useCase      = AssignDriver(fakeRequests, fakeDrivers)
```

See [`error-handling.md`](./error-handling.md), [`state-transitions.md`](./state-transitions.md), and [`effect-systems.md`](./effect-systems.md).
