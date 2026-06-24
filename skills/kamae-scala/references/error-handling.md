# Scala Error Handling

## Use Domain-Specific Error ADTs

Use `Either[DomainError, T]` and specific error enums or sealed traits in domain and use-case code.

```scala
enum AssignDriverError:
  case RequestNotFound(requestId: RequestId)
  case InvalidState
  case DriverNotAvailable(driverId: DriverId)
  case Domain(cause: DomainError)
```

Avoid returning bare `Throwable`, `Exception`, or `String` from domain functions. Those are acceptable near application edges where errors are reported or logged.

## Avoid Throws in Domain Code

Flag or avoid `throw`, `???`, and unsafe `.get`, `.head`, or `.last` on `Option`/`Either` in domain and use-case code. Use typed errors or test-only helpers instead.

Acceptable exceptions:

- Tests and fixtures
- Truly unreachable branches guarded by exhaustive domain reasoning and `compiletime.error` or `MatchError` on sealed sets
- Process startup configuration failures where crashing is the intended behavior

## Convert Infrastructure Errors Deliberately

Map repository and adapter errors into use-case errors at the boundary between infrastructure and application logic.

```scala
requests.findWaiting(requestId).attempt.map:
  case Left(cause) => Left(AssignDriverError.Repository(cause))
  case Right(value) => Right(value)
```

Do not let low-level driver error types become the public error contract of a domain use case unless that is an explicit project convention.

## Effectful Use Cases

In Scala server code, the idiomatic shape depends on the effect system:

| Stack | Typical shape |
| --- | --- |
| Cats Effect / FS2 | `F[Either[UseCaseError, T]]` or `F[T]` with typed errors via `ApplicativeError` |
| ZIO | `ZIO[Any, UseCaseError, T]` |
| Future (legacy) | `Future[Either[UseCaseError, T]]` with explicit error mapping at boundaries |

Keep layers distinct:

| Layer | Typical shape | Error type |
| --- | --- | --- |
| Domain transition | sync method | `DomainError` |
| Use case | effectful | `UseCaseError` with mapped variants |
| Port / adapter | effectful trait method | `RepositoryError`, `ClientError`, ... |

Domain transitions should stay synchronous and pure when possible. Async belongs
in use cases and adapters that perform I/O.

## Chain Errors with Cause Fields

When wrapping infrastructure failures, keep the original cause in a named field for debugging without exposing it in user-facing messages.

```scala
enum AssignDriverError:
  case Repository(cause: Throwable)
```

Redact or strip causes before returning errors to external clients.

## Preferred Pattern: Early Return with Either

```scala
enum AssignDriverError:
  case RequestNotFound(requestId: RequestId)
  case DriverNotAvailable(driverId: DriverId)
  case Domain(cause: DomainError)
  case PersistenceFailed

final case class DriverProfile(
    driverId: DriverId,
    acceptsAccessibilityRequests: Boolean
):
  def toAssignment: DriverAssignment =
    DriverAssignment(driverId, acceptsAccessibilityRequests)

trait TaxiRequestRepositorySync:
  def findWaiting(id: RequestId): Option[WaitingRequest]
  def saveAssigned(state: EnRouteRequest, events: List[TaxiRequestEvent]): Either[AssignDriverError, Unit]

def execute(command: AssignDriverCommand): Either[AssignDriverError, Unit] =
  for
    waiting <- requests
      .findWaiting(command.requestId)
      .toRight(AssignDriverError.RequestNotFound(command.requestId))
    profile <- drivers
      .findAvailable(command.driverId)
      .toRight(AssignDriverError.DriverNotAvailable(command.driverId))
    transition <- waiting
      .assignDriver(profile.toAssignment)
      .left
      .map(AssignDriverError.Domain.apply)
    _ <- requests.saveAssigned(transition.state, transition.events)
  yield ()
```

The sync ports above keep the control flow easy to read. In effectful code, lift each step into `F[_]` and map repository failures before returning. See [`state-transitions.md`](./state-transitions.md#keep-use-cases-thin) for a `cats` example.

See [`application-wiring.md`](./application-wiring.md) for wiring use cases with injected ports.
