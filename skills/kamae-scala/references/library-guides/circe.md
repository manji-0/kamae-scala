# Circe

Use Circe for JSON boundaries, not for domain invariants.

## DTOs Get Codecs

```scala
import io.circe.Decoder

final case class RequestDto(requestId: String, passengerId: String, status: String)

object RequestDto:
  given Decoder[RequestDto] = Decoder.derived
```

`Decoder.derived` does not validate business rules. It also does not auto-derive nested field codecs for case classes unless those `Decoder` instances are already in implicit scope.

## Domain Types Get Validators

Decode to DTOs, then convert with explicit `Either` mapping. Avoid `Decoder[WaitingRequest]` on invariant-bearing types unless validation is embedded in the decoder and tested.

```scala
def decodeWaiting(dto: RequestDto): Either[BoundaryError, WaitingRequest] =
  for
    requestId <- RequestId(dto.requestId).left.map(BoundaryError.InvalidId.apply)
    passengerId <- PassengerId(dto.passengerId).left.map(BoundaryError.InvalidId.apply)
    _ <- Either.cond(dto.status == "waiting", (), BoundaryError.UnexpectedStatus(dto.status))
  yield WaitingRequest(requestId, passengerId, requiresAccessibleVehicle = false)
```

## Configured Derivation

When you need snake_case keys, defaults, or discriminators, provide a `Configuration` and use configured derivation:

```scala
import io.circe.derivation.Configuration

given Configuration = Configuration.default.withSnakeCaseMemberNames

object RequestDto:
  given Decoder[RequestDto] = Decoder.derivedConfigured
```

## Sum Types and Enums

For sealed families, `Codec.AsObject.derived` auto-derives nested sum members when subtypes are known. For simple enums:

```scala
enum Status derives Decoder, Encoder:
  case Waiting, EnRoute
```

Prefer explicit decoders for externally controlled status strings instead of accepting any string into domain enums.

## Play JSON

If the project uses Play JSON instead of Circe, keep the same boundary rule: `Reads`/`Writes` on DTOs, validating conversion into domain types afterward. Do not treat `Json.format` derivation as invariant enforcement.
