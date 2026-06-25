# Secrets and Credential Types

For full patterns, prefer [`../pii-protection.md`](../pii-protection.md). This
file covers Scala-specific defaults for credentials and API keys.

Do not store secrets as bare `String` in domain or use-case layers. Prefer opaque
types with restricted `toString`, or dedicated wrapper types that never log raw
values.

```scala
final class ApiToken private (private val value: String):
  override def toString: String = "ApiToken(***)"

object ApiToken:
  def parse(raw: String): Either[BoundaryError, ApiToken] =
    if raw.trim.isEmpty then Left(BoundaryError.EmptyField("api_token"))
    else Right(new ApiToken(raw.trim))

  extension (token: ApiToken) def expose: String = token.value
```

Expose secret values only in narrow adapter functions (`expose`, `value`) at
HTTP/auth/payment boundaries. Avoid including exposed values in error ADTs.

## Common Combinations

| Stack | Pattern | Topic guide |
| --- | --- | --- |
| Opaque secret type + adapter | `expose` only in auth module | [`pii-protection.md`](../pii-protection.md) |
| Logging | Never log token fields; use structured `***` placeholders | [`logging-metrics.md`](../logging-metrics.md) |
| PII vs secrets | Personal data in redacted types; credentials in secret wrappers | [`pii-protection.md`](../pii-protection.md) |

Detection-only: `com.github.pureconfig` secret loaders — still validate at the
boundary and map into opaque types before domain code runs.
