# Scala Property-Based Tests

<!-- constrained-by ./test-data.md -->
<!-- constrained-by ./domain-modeling.md -->
<!-- constrained-by ./state-transitions.md -->

## When Property Tests Earn Their Cost

Use property-based tests when an invariant should hold across many inputs and
example tables would be incomplete or tedious to maintain.

Good targets:

- value-object constructors and validation rules
- parse/format and DTO → domain `Either` round trips
- state-machine transition laws and rejection rules
- money, units, and timestamp boundary behavior
- idempotent handlers and projection replay
- redaction and safe `toString` contracts

Prefer ordinary unit tests when behavior is a small closed set, when the property
is trivially true by construction, or when failure would not shrink to a useful
minimal example.

## Prefer ScalaCheck for Domain Modules

ScalaCheck is the default recommendation for server-side domain code when the
project already uses it or when properties are the clearest coverage tool. Use
ScalaTest `ScalaCheckPropertyChecks` only when the project standardizes on it.

Add ScalaCheck in `Test` scope. Keep generators in test sources or `support`
packages — not in production domain code.

```scala
libraryDependencies += "org.scalacheck" %% "scalacheck" % "1.18.1" % Test
libraryDependencies += "org.scalameta" %% "munit-scalacheck" % "1.0.0" % Test
```

Load [`library-guides/scalacheck.md`](./library-guides/scalacheck.md) when
`org.scalacheck` is on the classpath.

## Generate Through Public Constructors

Generators must produce values the production path can construct. If a strategy
builds raw case class literals or bypasses companions, the test may pass while
real callers still fail.

```scala
import org.scalacheck.Gen
import org.scalacheck.Prop.forAll

def validRequestIdGen: Gen[RequestId] =
  Gen.nonEmptyListOf(Gen.numChar).map(_.mkString).flatMap { raw =>
    RequestId(raw) match
      case Right(id) => Gen.const(id)
      case Left(_)   => Gen.fail
  }

property("request id rejects blank input"):
  forAll(Gen.stringOf(Gen.alphaNumChar)) { raw =>
    if raw.trim.isEmpty then RequestId(raw).isLeft
    else true
  }
```

When invalid inputs matter, generate raw strings or DTOs and assert constructor
rejection — do not build domain types around invalid data.

## Encode Properties Explicitly

Name the law in the test and keep each property focused.

| Property kind | Example law |
| --- | --- |
| Round trip | DTO → domain → DTO preserves safe fields |
| Idempotence | applying the same command twice has no further effect |
| Invariant preservation | valid `Money` plus valid `Money` never produces negative result |
| Rejection | illegal transition always returns the same error variant |
| Projection replay | folding events in order equals snapshot plus tail |

```scala
property("money addition is commutative for same currency"):
  forAll(moneyGen, moneyGen) { (a, b) =>
    a.currency == b.currency ==> (a + b == b + a)
  }
```

Use `==>` or `Prop.when` to discard inputs outside the precondition instead of
asserting vacuous success.

## Model State Machines as Strategies

Build strategies that only produce reachable states, then assert transition outcomes.

```scala
def waitingRequestGen: Gen[WaitingRequest] =
  for
    id        <- validRequestIdGen
    passenger <- validPassengerIdGen
  yield WaitingRequest(id, passenger, requiresAccessibleVehicle = false)

property("assign driver advances state"):
  forAll(waitingRequestGen, validDriverIdGen) { (waiting, driver) =>
    waiting.assignDriver(driver).map(_.state) match
      case Right(_: EnRouteRequest) => true
      case _                        => false
  }
```

For illegal transitions, generate a source state and an action known to be
invalid, then assert a specific error variant — not `isLeft` alone.

## Keep Shrinking Domain-Safe

Shrinking should not produce values that bypass constructors. When a failure
shrinks to an empty string or impossible variant, fix the generator or add
preconditions.

Store reproducible failures with ScalaCheck `Prop.propWithSeed` or committed seed
comments when a bug required a non-obvious input:

```scala
// Seed found: 0xdeadbeef — keep until regression is understood
property("regression example"):
  forAll(strategyGen) { input => /* ... */ }
```

Commit regression notes or minimal failing examples in test comments when they
encode real fixed bugs.

## Do Not Property-Test Non-Deterministic or I/O Boundaries by Default

Property tests belong on pure domain functions and deterministic adapters with
injected clocks or fixed fixtures.

Avoid by default:

- live database or network calls inside `forAll`
- wall-clock time without a seeded clock strategy
- logging or metrics side effects as the property under test

Test DTO conversion, redaction, and error mapping with generated payloads.
Test repositories with fakes or in-memory ports, not uncontrolled I/O.

## Integrate with Existing Test Layers

| Layer | Property test role |
| --- | --- |
| Value object | constructor acceptance/rejection, round trips |
| Domain transition | laws, illegal transition errors |
| Use case | idempotency with fake ports, not real infra |
| Boundary DTO | malformed/generated payloads map to typed errors |
| Projection | replay order and checkpoint idempotency |

Keep example-based tests for readable scenarios and `compileErrors` tests for
type-safety promises (see [`test-data.md`](./test-data.md)).

## CI and Runtime Budget

Property tests multiply case counts. Defaults are usually enough for domain modules;
raise `minSuccessfulTests` locally when debugging.

- Keep default ScalaCheck configuration in CI unless the domain module is small and fast.
- Mark especially slow properties with tags or separate test suites documented in CI.
- Do not disable shrinking in CI to save time unless the team accepts harder reproduction.

## Detection Hints

When `build.sbt` includes `scalacheck` or `munit-scalacheck`, load this guide
together with [`test-data.md`](./test-data.md) and the topic guide for the
invariant under test (modeling, state transitions, boundaries, or persistence).
