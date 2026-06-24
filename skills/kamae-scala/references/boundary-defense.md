# Boundary Defense

## Parse Externally, Validate Internally

External systems provide untrusted shapes. Parse them into boundary DTOs, then convert DTOs into domain types through validating constructors.

```scala
final case class RequestRowDto(
    requestId: String,
    passengerId: String,
    status: String,
    requiresAccessibleVehicle: Boolean
)

object RequestRowDto:
  def toWaiting(dto: RequestRowDto): Either[BoundaryError, WaitingRequest] =
    for
      requestId <- RequestId(dto.requestId).left.map(BoundaryError.InvalidId.apply)
      passengerId <- PassengerId(dto.passengerId).left.map(BoundaryError.InvalidId.apply)
      _ <- Either.cond(dto.status == "waiting", (), BoundaryError.UnexpectedStatus(dto.status))
    yield WaitingRequest(requestId, passengerId, dto.requiresAccessibleVehicle)
```

Keep JSON/DB/queue codecs on DTOs and row types, not on aggregate roots with invariants.

## Codec Derivation Is Not Validation

Automatic Circe or Play JSON derivation can deserialize invalid domain states. Treat codecs as transport mechanics; run domain validation after decoding DTOs.

See [`library-guides/circe.md`](./library-guides/circe.md) when Circe is present.

## Reject Unknown and Defaulted Fields Deliberately

For externally controlled input, prefer explicit schemas over silently ignored fields. Document how unknown enum strings, missing discriminators, and default values are handled.

## Auth and Tenant Checks Belong at Boundaries

Verify caller identity, tenant scope, and authorization before constructing domain commands. Do not rely on repository queries alone to enforce access rules.

## Anti-Patterns

- Deserializing directly into domain case classes with public constructors
- Using `asInstanceOf` or unchecked casts from `Any`/JSON nodes in domain code
- Sharing ORM entity classes between persistence and domain layers without conversion
