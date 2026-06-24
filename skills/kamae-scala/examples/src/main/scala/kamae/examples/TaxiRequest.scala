package kamae.examples

/** Domain types for the taxi-request example.
  *
  * Opaque IDs live inside this object so the underlying representation stays abstract outside the
  * module, per Scala 3 opaque-type guidance.
  */
object TaxiRequestDomain:
  opaque type RequestId = String

  object RequestId:
    def apply(value: String): Either[IdError, RequestId] =
      val trimmed = value.trim
      if trimmed.isEmpty then Left(IdError.Empty("request_id"))
      else Right(trimmed)

    extension (id: RequestId) def value: String = id

  opaque type PassengerId = String

  object PassengerId:
    def apply(value: String): Either[IdError, PassengerId] =
      val trimmed = value.trim
      if trimmed.isEmpty then Left(IdError.Empty("passenger_id"))
      else Right(trimmed)

    extension (id: PassengerId) def value: String = id

  opaque type DriverId = String

  object DriverId:
    def apply(value: String): Either[IdError, DriverId] =
      val trimmed = value.trim
      if trimmed.isEmpty then Left(IdError.Empty("driver_id"))
      else Right(trimmed)

    extension (id: DriverId) def value: String = id

  enum IdError:
    case Empty(field: String)

  final case class WaitingRequest private (
      requestId: RequestId,
      passengerId: PassengerId,
      requiresAccessibleVehicle: Boolean
  )

  object WaitingRequest:
    def apply(
        requestId: RequestId,
        passengerId: PassengerId,
        requiresAccessibleVehicle: Boolean
    ): WaitingRequest =
      new WaitingRequest(requestId, passengerId, requiresAccessibleVehicle)

    extension (request: WaitingRequest)
      def assignDriver(
          driver: DriverAssignment
      ): Either[DomainError, Transition[EnRouteRequest, TaxiRequestEvent]] =
        if request.requiresAccessibleVehicle && !driver.acceptsAccessibilityRequests then
          Left(DomainError.DriverCannotServeAccessibilityRequest)
        else
          val state = EnRouteRequest(
            request.requestId,
            request.passengerId,
            driver.driverId
          )
          Right(
            Transition(
              state,
              List(
                TaxiRequestEvent.DriverAssigned(
                  state.requestId,
                  state.driverId
                )
              )
            )
          )

  final case class EnRouteRequest(
      requestId: RequestId,
      passengerId: PassengerId,
      driverId: DriverId
  )

  final case class DriverAssignment(
      driverId: DriverId,
      acceptsAccessibilityRequests: Boolean
  )

  enum TaxiRequest:
    case Waiting(value: WaitingRequest)
    case EnRoute(value: EnRouteRequest)

  enum TaxiRequestEvent:
    case DriverAssigned(requestId: RequestId, driverId: DriverId)

  enum DomainError:
    case DriverCannotServeAccessibilityRequest

  final case class Transition[TState, TEvent](state: TState, events: List[TEvent])

export TaxiRequestDomain.{
  RequestId,
  PassengerId,
  DriverId,
  IdError,
  WaitingRequest,
  EnRouteRequest,
  DriverAssignment,
  TaxiRequest,
  TaxiRequestEvent,
  DomainError,
  Transition
}
