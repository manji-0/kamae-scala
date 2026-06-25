# Scala State Transitions

## Constrain Transitions by Source Type

When only one state may transition, accept that specific state instead of a wide enum.

```scala
final case class WaitingRequest(
    requestId: RequestId,
    passengerId: PassengerId
)

final case class EnRouteRequest(
    requestId: RequestId,
    passengerId: PassengerId,
    driverId: DriverId
)

extension (request: WaitingRequest)
  def assignDriver(driverId: DriverId): EnRouteRequest =
    EnRouteRequest(request.requestId, request.passengerId, driverId)
```

This makes invalid source states fail at compile time.

Keep a transition infallible only when every precondition is encoded in the
input types. If any rule depends on data not represented by the source state or
argument types, return a domain error:

```scala
extension (request: WaitingRequest)
  def assignDriver(
      driver: DriverAssignment
  ): Either[DomainError, Transition[EnRouteRequest, TaxiRequestEvent]] =
    if request.requiresAccessibleVehicle && !driver.acceptsAccessibilityRequests then
      Left(DomainError.DriverCannotServeAccessibilityRequest)
    else
      val state = EnRouteRequest(request.requestId, request.passengerId, driver.driverId)
      Right(Transition(state, List(TaxiRequestEvent.DriverAssigned(state.requestId, state.driverId))))
```

Do not hide this behind `throw`, `.get`, or comments such as "caller must
check first". If the compiler cannot enforce the precondition, the transition
signature should show that failure is possible.

## Why Consuming the Source State Matters

Taking the source state as a parameter and returning a new state (rather than mutating a shared aggregate) has concrete benefits:

1. **The old state cannot be reused.** After `waiting.assignDriver(driver)`, callers work with the returned state; the transition method can be defined on the source type without hidden mutation.
2. **Transitions read as state replacement.** The returned case class is the new truth.
3. **Easier persistence mapping.** The use case receives an owned `EnRouteRequest` ready to pass to `saveAssigned` without cloning out of a mutable aggregate.
4. **Clearer event pairing.** `Transition(state, events)` is built once from consumed inputs.

Use `var` fields or in-place mutation only when:

- The aggregate is a performance-critical hot path with measured need, and
- Invariants are revalidated on every mutator, and
- The team documents why compile-time state replacement was not practical.

Default to immutable transition results.

## Keep Use Cases Thin

Use cases orchestrate ports; they should not embed business rules that belong on domain states.

```scala
import cats.Monad
import cats.syntax.all.*

final case class DriverProfile(
    driverId: DriverId,
    acceptsAccessibilityRequests: Boolean
):
  def toAssignment: DriverAssignment =
    DriverAssignment(driverId, acceptsAccessibilityRequests)

trait DriverRepository[F[_]]:
  def findAvailable(driverId: DriverId): F[Option[DriverProfile]]

final class AssignDriver[F[_]: Monad](
    requests: TaxiRequestRepository[F],
    drivers: DriverRepository[F]
):
  def execute(command: AssignDriverCommand): F[Either[AssignDriverError, Unit]] =
    requests.findWaiting(command.requestId).flatMap:
      case None =>
        Monad[F].pure(Left(AssignDriverError.RequestNotFound(command.requestId)))
      case Some(waiting) =>
        drivers.findAvailable(command.driverId).flatMap:
          case None =>
            Monad[F].pure(Left(AssignDriverError.DriverNotAvailable(command.driverId)))
          case Some(profile) =>
            waiting.assignDriver(profile.toAssignment) match
              case Left(err) =>
                Monad[F].pure(Left(AssignDriverError.Domain(err)))
              case Right(transition) =>
                requests
                  .saveAssigned(transition.state, transition.events)
                  .as(Right(()))
```

This example assumes `cats-core` is on the classpath. Map adapter failures with `handleError` or `attempt` at the repository boundary before the use case returns.

Domain transitions stay synchronous and pure when possible. Effectful code belongs in use cases and adapters.

## Model Transition Results Explicitly

Prefer a small `Transition[TState, TEvent]` (or equivalent) when a state change emits domain events that must be persisted atomically with the new state.

See [`persistence-events.md`](./persistence-events.md) for repository expectations.

## Canonical Example

[`../examples/src/main/scala/kamae/examples/TaxiRequest.scala`](../examples/src/main/scala/kamae/examples/TaxiRequest.scala)

[`../examples/src/test/scala/kamae/examples/CompileTimeSafetySuite.scala`](../examples/src/test/scala/kamae/examples/CompileTimeSafetySuite.scala) uses munit `compileErrors` to assert that `EnRouteRequest` cannot be used where `WaitingRequest` is required.
