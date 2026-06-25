# Test Data

## Use Lawful Fixtures

Test helpers should construct valid IDs and states through the same factories production code uses.

```scala
def requestId(value: String = "req-1"): RequestId =
  RequestId(value).fold(err => throw new IllegalArgumentException(err.toString), identity)
```

Prefer `Either` assertions in tests over `.get` when verifying failure paths.

## Compile-Time Safety Tests

When separate state types enforce transition sources, add munit `compileErrors` tests so illegal states cannot compile:

```scala
test("EnRouteRequest is not WaitingRequest"):
  val errors = compileErrors("""
    import example.domain.*
    def onlyWaiting(request: WaitingRequest): Unit = ()
    onlyWaiting(enRouteFixture)
  """)
  assert(errors.nonEmpty)
```

See [`../examples/src/test/scala/kamae/examples/CompileTimeSafetySuite.scala`](../examples/src/test/scala/kamae/examples/CompileTimeSafetySuite.scala).

## Keep PII Out of Fixtures

Use synthetic identifiers in committed fixtures. Do not copy production exports into the repository.

## Separate Unit and Integration Fixtures

Unit tests should not require databases or external services. Integration tests may build richer rows/DTOs, still converted through boundary parsers.
