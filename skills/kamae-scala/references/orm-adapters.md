# ORM Adapters and Domain Mappers

> **When to read:** Mapping doobie rows, Slick entities, or Quill records to domain types in repository adapters.
> **Related:** [`boundary-defense.md`](./boundary-defense.md), [`persistence-events.md`](./persistence-events.md), [`adoption.md`](./adoption.md).

Kamae Scala keeps ORM/DB row types in **infrastructure**. Use cases and transitions see only domain states. Adapters own translation between persistence rows and domain types.

## Layering

```text
Use case  →  TaxiRequestRepository[F]  →  DoobieTaxiRequestRepository
                                              ↓
                                         row case class / Slick entity
                                              ↓
                                         mapper functions
                                              ↓
                                         WaitingRequest | EnRouteRequest | ...
```

Never pass Slick `TableQuery` rows, session-bound entities, or Quill records into domain transitions. They carry nullable columns, lazy associations, and storage shape that weaken invariants.

## Doobie Pattern

Define row case classes separately from domain states. Keep SQL and `Read`/`Write` instances in infrastructure.

```scala
final case class RequestRow(
    id: String,
    kind: String,
    passengerId: String,
    driverId: Option[String],
    version: Long
)
```

### Row DTO + domain mapper

Parse through a validating mapper at the adapter boundary:

```scala
def domainFromRow(row: RequestRow): Either[BoundaryError, TaxiRequest] =
  for
    requestId <- RequestId(row.id).left.map(BoundaryError.InvalidId.apply)
    passengerId <- PassengerId(row.passengerId).left.map(BoundaryError.InvalidId.apply)
    state <- row.kind match
      case "waiting" =>
        Right(TaxiRequest.Waiting(WaitingRequest(requestId, passengerId, requiresAccessibleVehicle = false)))
      case "en_route" =>
        for
          driverId <- row.driverId.toRight(BoundaryError.MissingField("driver_id")).flatMap(DriverId(_).left.map(BoundaryError.InvalidId.apply))
        yield TaxiRequest.EnRoute(EnRouteRequest(requestId, passengerId, driverId))
      case other =>
        Left(BoundaryError.UnexpectedStatus(other))
  yield state
```

Prefer narrow repository methods (`findWaiting`, `saveAssigned`) over loading a wide nullable row and guessing state in the use case.

### Persisting domain → SQL

```scala
def saveAssigned(
    state: EnRouteRequest,
    events: List[TaxiRequestEvent],
    expectedVersion: Long
): ConnectionIO[Either[AssignDriverError, Unit]] =
  for
    updated <- sql"""
      update requests
      set kind = 'en_route', driver_id = ${state.driverId.value}, version = ${expectedVersion + 1}
      where id = ${state.requestId.value} and version = $expectedVersion
    """.update.run
    _ <- if updated == 0 then FC.raiseError(VersionConflict(state.requestId))
         else FC.unit
    _ <- insertOutboxEvents(events)
  yield Right(())
```

Keep optimistic locking and outbox inserts in the adapter transaction. The use case passes `expectedVersion` explicitly.

See [`library-guides/doobie.md`](./library-guides/doobie.md).

## Slick Pattern

Keep Slick `Table` definitions and `DBIO` actions in infrastructure modules.

```scala
class Requests(tag: Tag) extends Table[RequestRow](tag, "requests"):
  def id = column[String]("id", O.PrimaryKey)
  def kind = column[String]("kind")
  def passengerId = column[String]("passenger_id")
  def driverId = column[Option[String]]("driver_id")
  def version = column[Long]("version")
  def * = (id, kind, passengerId, driverId, version).mapTo[RequestRow]
```

Map `RequestRow` to domain in the repository adapter before returning to use cases. Do not expose `DBIO` or `Query` types from domain ports.

See [`library-guides/slick.md`](./library-guides/slick.md).

## Repository Port Shape

Ports return domain states, not ORM rows. See [`persistence-events.md`](./persistence-events.md).

## Migration Coexistence

During a strangler migration:

1. Add row DTOs + `domainFromRow`.
2. Wrap legacy service methods to call mappers, then pure transitions.
3. Move queries into doobie/Slick adapter modules.
4. Delete legacy wrappers when use cases own the flow.

Read [`adoption.md`](./adoption.md).

## Tests

- **Mapper tests:** every `kind`, null combinations, corrupt rows.
- **Adapter integration tests:** real transaction, `FOR UPDATE`, version conflict, outbox row in same transaction.
- **Use case tests:** fake ports; no JDBC/ORM.

Do not construct domain states from unchecked row literals unless the test targets corrupt input handling.
