# Application Wiring

## Model Use Cases as Small Classes

Inject ports through constructor parameters or reader/environment layers. Avoid static singletons for repositories and clients.

```scala
final class AssignDriver[F[_]: Monad](
    requests: TaxiRequestRepository[F],
    drivers: DriverRepository[F]
)
```

## Composition Root

Wire concrete adapters only in the application bootstrap module (`Main`, `Bootstrap`, or ZIO `App` layer). Domain and application packages should depend on traits, not JDBC/HTTP drivers.

## Keep Domain Transitions Pure

Use cases load state, call pure transitions, then persist results. Do not embed SQL or JSON parsing inside transition methods.

## Error Mapping at the Edge

HTTP/gRPC/CLI adapters map `UseCaseError` to response codes and client-safe messages. Do not leak repository exception strings by default.

See [`error-handling.md`](./error-handling.md) and [`state-transitions.md`](./state-transitions.md).
