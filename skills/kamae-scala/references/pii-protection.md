# Scala PII Protection

<!-- constrained-by ./logging-metrics.md -->
<!-- constrained-by ./boundary-defense.md -->

## Make Sensitive Data Hard to Log

Use redacting wrappers or validated opaque types for personal data by default.
Reserve credential wrappers (see [`library-guides/secrets.md`](./library-guides/secrets.md))
for API keys, tokens, passwords, and cryptographic material. General PII such
as names or email usually belongs in a domain type with safe `toString`, not in
a credential wrapper.

PII examples: names, email, phone, address, government IDs, payment identifiers,
health data, IP addresses, and precise location.

```scala
final case class Patient(
    id: PatientId,
    email: EmailAddress,
    diagnosis: Redacted[DiagnosisCode]
)
```

Avoid default `toString` on case classes that contain raw PII. Use opaque types,
custom `toString`, or `Redacted[T]` wrappers.

For credentials:

```scala
final class ApiToken private (private val value: String):
  override def toString: String = "ApiToken(***)"
```

## Secrets vs Redacted PII — When to Use Which

| Concern | Prefer | Rationale |
| --- | --- | --- |
| API keys, passwords, tokens, private keys | [`secrets.md`](./library-guides/secrets.md) opaque wrappers | Narrow `expose`; hidden `toString` |
| Names, email, phone, address, government ID | `Redacted[T]` or domain opaque type | PII is not crypto material but must not leak to logs |
| Opaque surrogate IDs safe for ops logs | Plain opaque type with safe `toString` | See [`logging-metrics.md`](./logging-metrics.md#which-ids-belong-in-logs) |
| Values shown in UI or audit export | Domain type + explicit `exposeFor*` | Exposure is deliberate and named |

Do not wrap every email in a credential type. Do not store long-lived PII only
behind default case class `toString`.

## Keep Exposure Explicit

Expose sensitive values only at boundaries that need them: email delivery,
payment processors, encryption adapters, or audit export jobs.

```scala
extension (patient: Patient)
  def exposeEmailForDelivery: EmailAddress = patient.email
```

Never format sensitive values into domain errors or info-level logs.

## Classify Identifiers Before Logging

Field names such as `userId` or `passengerId` do not make an identifier safe.
Apply [`logging-metrics.md`](./logging-metrics.md#which-ids-belong-in-logs):

- **Safe by default**: opaque surrogate aggregate IDs, correlation IDs, internal
  job/transaction IDs, bounded domain enums.
- **Never log**: secrets, government IDs, payment identifiers, contact identity,
  person descriptors, health data, precise location, network tracking IDs.
- **Conditional**: person-linked IDs only when documented as opaque surrogates
  with safe `toString`/`Show`.

Encode the decision in the type. Prevent accidental emission through redacted
types, restricted formatting, or adapter-only exposure.

## Tracing and Span Fields

Span and log attributes must not carry PII by default.

### Omit sensitive arguments from auto-instrumentation

When using macros or AOP that log method arguments, exclude patient/user DTOs.
Prefer explicit attribute maps with surrogate IDs only.

### Custom `toString` for redacted types

```scala
opaque type EmailAddress = String

object EmailAddress:
  extension (email: EmailAddress)
    def redacted: String =
      val local = email.value
      val at = local.indexOf('@')
      if at <= 1 then "[redacted email]" else s"${local.head}***${local.substring(at)}"

    private def value: String = email // module-private; no public .value
```

### Defense in depth

When many modules log through shared facades, add a sanitizing appender or
export filter that strips known sensitive keys (`email`, `phone`, `ssn`) before
OTLP or stdout. Layers are not a substitute for redacted types at the source.

## JSON and API Output Redaction

Control Circe/Play JSON output explicitly. Do not encode domain entities with raw
PII unless the response DTO redacts fields.

```scala
final case class PatientResponse(id: PatientId, emailRedacted: String)

object PatientResponse:
  def from(patient: Patient): PatientResponse =
    PatientResponse(patient.id, patient.email.redacted)
```

Prefer separate response DTOs over custom encoders on every field when most of
the struct is safe.

## `toString` vs intentional display

Split behavior when user-facing text and developer diagnostics differ:

```scala
final class EmailAddress private (private val raw: String):
  override def toString: String = "EmailAddress([redacted])"

  def exposeForDelivery: String = raw
```

- **`toString`**: redact by default for PII types; protects logs and tests.
- **Intentional display**: only at adapter call sites via named methods.

Do not add public `.value` on PII opaque types if every access would leak into
logs. Prefer `exposeForDelivery` at the adapter.

## Testing Redaction

Assert that string forms do not contain raw PII:

```scala
test("patient toString does not leak email"):
  val patient = Patient.fixture(email = "patient@example.com")
  assert(!patient.toString.contains("patient@example.com"))
```

For credential types:

```scala
test("api token toString is hidden"):
  val token = ApiToken.parse("super-secret").toOption.get
  assert(!token.toString.contains("super-secret"))
```

Use synthetic fixture data. See [`test-data.md`](./test-data.md).

## Common Stack Combinations

| Stack | PII pattern |
| --- | --- |
| Opaque secret type + adapter | `expose` only in payment/auth module |
| log4cats + redacted types | structured fields; safe `toString` on domain types |
| Circe + response DTOs | separate `PatientResponse`, not domain `Encoder` |
| `Either` errors + PII | error variants carry field names, not raw values |

## Review Signals

Flag when:

- Domain errors include raw email, phone, or government ID in message strings.
- Case classes with PII use default `derives Codec` or unchecked `toString`.
- Structured logs include full user/patient DTOs without redaction policy.
- Credential wrappers used for all personal data indiscriminately.
- Response serialization uses unrestricted encoders on domain entities.

Cross-check [`library-guides/secrets.md`](./library-guides/secrets.md) for
credential-specific patterns.
