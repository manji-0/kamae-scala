package kamae.examples

import munit.FunSuite

class CompileTimeSafetySuite extends FunSuite:

  test("EnRouteRequest is not WaitingRequest"):
    val errors = compileErrors("""
      import kamae.examples.*
      def onlyWaiting(request: WaitingRequest): Unit = ()
      val enRoute = EnRouteRequest(
        RequestId("req-1").toOption.get,
        PassengerId("passenger-1").toOption.get,
        DriverId("driver-1").toOption.get
      )
      onlyWaiting(enRoute)
    """)
    assert(errors.nonEmpty, clue = "expected a compile error")
    assert(
      errors.contains("WaitingRequest") || errors.contains("EnRouteRequest"),
      clue = errors
    )

  test("assignDriver is not available on EnRouteRequest"):
    val errors = compileErrors("""
      import kamae.examples.*
      val enRoute = EnRouteRequest(
        RequestId("req-1").toOption.get,
        PassengerId("passenger-1").toOption.get,
        DriverId("driver-1").toOption.get
      )
      val driver = DriverAssignment(DriverId("driver-1").toOption.get, false)
      enRoute.assignDriver(driver)
    """)
    assert(errors.nonEmpty, clue = "expected a compile error")
    assert(errors.contains("assignDriver"), clue = errors)
