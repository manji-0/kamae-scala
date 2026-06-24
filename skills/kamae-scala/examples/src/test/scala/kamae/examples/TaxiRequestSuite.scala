package kamae.examples

import munit.FunSuite

class TaxiRequestSuite extends FunSuite:

  private def requestId(value: String): RequestId =
    RequestId(value) match
      case Right(id) => id
      case Left(err) => fail(s"fixture request id is invalid: $err")

  private def passengerId(value: String): PassengerId =
    PassengerId(value) match
      case Right(id) => id
      case Left(err) => fail(s"fixture passenger id is invalid: $err")

  private def driverId(value: String): DriverId =
    DriverId(value) match
      case Right(id) => id
      case Left(err) => fail(s"fixture driver id is invalid: $err")

  test("assignDriver preserves identity and emits event"):
    val reqId = requestId("req-1")
    val passId = passengerId("passenger-1")
    val drvId = driverId("driver-1")
    val request = WaitingRequest(reqId, passId, requiresAccessibleVehicle = false)
    val driver = DriverAssignment(drvId, acceptsAccessibilityRequests = false)

    request.assignDriver(driver) match
      case Right(transition) =>
        assertEquals(
          transition.state,
          EnRouteRequest(reqId, passId, drvId)
        )
        assertEquals(
          transition.events,
          List(TaxiRequestEvent.DriverAssigned(reqId, drvId))
        )
      case Left(err) => fail(s"expected success, got $err")

  test("assignDriver serves accessibility request when driver accepts"):
    val request = WaitingRequest(
      requestId("req-3"),
      passengerId("passenger-3"),
      requiresAccessibleVehicle = true
    )
    val driver = DriverAssignment(driverId("driver-3"), acceptsAccessibilityRequests = true)

    request.assignDriver(driver) match
      case Right(transition) =>
        assert(transition.state.isInstanceOf[EnRouteRequest])
        assertEquals(transition.events.length, 1)
      case Left(err) => fail(s"expected success, got $err")

  test("taxi request enum stores waiting state"):
    val waiting = WaitingRequest(
      requestId("req-4"),
      passengerId("passenger-4"),
      requiresAccessibleVehicle = false
    )
    val request = TaxiRequest.Waiting(waiting)

    assert(request.isInstanceOf[TaxiRequest.Waiting])

  test("rejects empty request id"):
    assertEquals(RequestId(" "), Left(IdError.Empty("request_id")))

  test("rejects empty passenger id"):
    assertEquals(PassengerId(""), Left(IdError.Empty("passenger_id")))

  test("rejects empty driver id"):
    assertEquals(DriverId("  "), Left(IdError.Empty("driver_id")))

  test("rejects driver that cannot satisfy precondition"):
    val request = WaitingRequest(
      requestId("req-2"),
      passengerId("passenger-2"),
      requiresAccessibleVehicle = true
    )
    val driver = DriverAssignment(driverId("driver-2"), acceptsAccessibilityRequests = false)

    request.assignDriver(driver) match
      case Left(error) =>
        assertEquals(error, DomainError.DriverCannotServeAccessibilityRequest)
      case Right(_) => fail("expected domain error")
