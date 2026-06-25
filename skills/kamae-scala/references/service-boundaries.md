# Service Boundaries

<!-- constrained-by ./boundary-defense.md -->
<!-- constrained-by ./application-wiring.md -->
<!-- constrained-by ./error-handling.md -->

## Keep Domain Packages Free of Transport Details

HTTP routes, gRPC services, and message consumers should translate requests into commands, invoke use cases, and map errors to transport responses. They should not contain business rules.

```scala
// Good: route delegates to use case
def assignDriverRoute(assignDriver: AssignDriver[IO]): HttpRoutes[IO] =
  HttpRoutes.of:
    case req @ POST -> Root / "requests" / requestId / "assign" =>
      for
        body   <- req.as[AssignDriverRequest]
        cmd     = AssignDriverCommand(RequestId.unsafeFrom(requestId), DriverId.unsafeFrom(body.driverId))
        result <- assignDriver.execute(cmd)
        resp   <- result.fold(toErrorResponse, _ => Ok())
      yield resp

// Bad: route contains business logic
def assignDriverRoute: HttpRoutes[IO] =
  HttpRoutes.of:
    case req @ POST -> Root / "requests" / requestId / "assign" =>
      // Fetching from DB, checking accessibility, updating state — all in the route
```

## Anti-Corruption at Module Edges

When integrating with other teams' services, define local DTOs and map into your domain types. Do not leak foreign models into domain transitions.

```scala
// External API returns their model
final case class ExternalDriverDto(id: String, vehicleType: String, accessible: Boolean)

// Map to your domain at the boundary
object ExternalDriverDto:
  def toDomain(dto: ExternalDriverDto): Either[BoundaryError, DriverAssignment] =
    for
      driverId <- DriverId(dto.id).left.map(BoundaryError.InvalidId.apply)
    yield DriverAssignment(driverId, dto.accessible)
```

## Contract Versioning

For gRPC and message queue contracts shared across services, version schemas explicitly. Use separate message types or version fields rather than optional fields that silently break consumers.

## Timeouts and Retries Stay in Adapters

Resilience policies belong in infrastructure clients, not domain code. Use cases may interpret retryable errors, but should not configure thread pools or HTTP clients directly.

```scala
// Good: adapter handles retry
class HttpDriverClient[F[_]: Temporal](client: Client[F]) extends DriverRepository[F]:
  def findAvailable(id: DriverId): F[Option[DriverProfile]] =
    retryingOnSomeErrors(
      policy = RetryPolicies.limitRetries[F](3),
      isWorthRetrying = (e: Throwable) => e.isInstanceOf[TimeoutException].pure[F],
      onError = (e, d) => Logger[F].warn(s"Retrying driver lookup: $e")
    )(doRequest(id))
```

See [`application-wiring.md`](./application-wiring.md) and [`error-handling.md`](./error-handling.md).
