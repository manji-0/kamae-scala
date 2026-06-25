# Scala Logging and Metrics

<!-- constrained-by ./pii-protection.md -->
<!-- constrained-by ./state-transitions.md -->
<!-- constrained-by ./error-handling.md -->

## Log with Domain Context

Every log entry should answer three questions: what happened, to which domain
object, and why it matters. Emit logs from use cases, application services, and
adapters rather than from deep inside domain invariants.

1. **Meaningful message**: describe the event in domain terms, not the method
   name. Prefer `"driver assigned to waiting request"` over `"assignDriver called"`.
2. **Domain object state**: include identifiers, current state variant, and
   decision-relevant values as structured fields.
3. **Transition information**: when the operation changes lifecycle, log source
   state, target state, and the command or event that triggered it.

```scala
import org.typelevel.log4cats.Logger
import org.typelevel.log4cats.syntax.*

final case class AssignDriverLog(
    requestId: RequestId,
    passengerId: PassengerId,
    driverId: DriverId,
    from: TaxiRequestState,
    to: TaxiRequestState,
    commandId: CommandId
)

def logAssignment[F[_]: Logger](log: AssignDriverLog): F[Unit] =
  Logger[F].info(
    s"driver assigned to waiting request" +
      s" requestId=${log.requestId.value}" +
      s" passengerId=${log.passengerId.value}" + // safe only for opaque surrogate IDs
      s" driverId=${log.driverId.value}" +
      s" from=${log.from}" +
      s" to=${log.to}" +
      s" commandId=${log.commandId.value}"
  )
```

Prefer structured logging APIs (log4cats, SLF4J with key-value markers, or
OpenTelemetry log attributes) over string interpolation of whole entities.

## Prefer Structured Logging

Keep log message templates stable so aggregators can group by message and filter
by field.

```scala
// Good: stable template, structured context map or MDC.
Logger[F].info(Map(
  "requestId" -> requestId.value,
  "state"     -> state.toString
))("request state persisted")

// Avoid: values baked only into free-form sentence text.
Logger[F].info(s"request ${requestId.value} persisted in state $state")
```

Choose log levels deliberately:

- `ERROR`: domain invariant failure, use case could not complete, or unhealthy
  dependency. Include context without secrets.
- `WARN`: recoverable anomaly (retryable timeout, handled edge case).
- `INFO`: significant business event or lifecycle step.
- `DEBUG`: detailed state for diagnosis; guard expensive values at DEBUG.

## Protect Logs from PII Leaks

Logs are long-lived and broadly accessible: treat them as a public boundary.
Follow [`pii-protection.md`](./pii-protection.md) and
[`library-guides/secrets.md`](./library-guides/secrets.md).

- Do not log raw names, emails, phone numbers, addresses, location, tokens, or
  credentials.
- Use opaque types and redacting wrappers so `toString` and structured fields
  stay safe by default.
- When an identifier is sensitive, log a hash or opaque reference instead.

See [Which IDs Belong in Logs](#which-ids-belong-in-logs).

## Which IDs Belong in Logs

Classify every identifier before it reaches logs, spans, metrics, or errors. The
field name does not decide safety; meaning and re-identification risk do.

### Default: safe to log

| Kind | Examples | Why it is usually safe |
| --- | --- | --- |
| Correlation / tracing | `correlationId`, `traceId`, `spanId`, HTTP `requestId` | Operational; not identity |
| Internal aggregate IDs | `orderId`, `requestId`, `shipmentId`, `commandId`, `eventId` | Opaque surrogate keys |
| Process / job IDs | `jobId`, `outboxId`, `batchId`, internal `transactionId` | Infrastructure correlation |
| Tenant context | `tenantId`, `organizationId`, `fleetId` | Multi-tenant ops when access is controlled |
| Bounded domain enums | `state`, `commandName`, `eventType`, `errorCode` | Low cardinality |

Requirements: opaque surrogate, not a secret, low standalone re-identification
risk, and safe `toString`/`Show` reviewed for logging.

### Default: do not log

| Kind | Examples | Why |
| --- | --- | --- |
| Secrets / auth | API keys, passwords, session tokens, signed URLs | Credential disclosure |
| Government / regulated IDs | SSN, passport, national health ID | Direct personal identity |
| Payment identifiers | PAN, CVV, full bank account | PCI exposure |
| Contact identity | email, phone used as account identity | Direct PII |
| Person descriptors | legal name, birth date, address, notes about a person | Direct PII |
| Health data | diagnosis, prescription | Regulated sensitive data |
| Precise location | lat/long, full street address | Location privacy |
| Network identity | client IP, device fingerprint | Tracking / PII in many jurisdictions |

Route incident needs through restricted audit export with authorization — not
general log retention.

### Conditional: classify in the domain model

| Kind | Log when | Do not log when |
| --- | --- | --- |
| `userId`, `passengerId`, `customerId` | Opaque surrogate UUID/ULID from your system | Value is email/phone or reversible hash of PII |
| `deviceId`, `installationId` | Opaque app-generated surrogate | Vendor advertising ID or hardware serial |
| `externalId`, `partnerRef` | Opaque partner reference with contract | Partner value contains email or national ID |

Encode the decision in the type. Non-loggable identifiers use redacted types or
adapter-only `expose` methods (see [`pii-protection.md`](./pii-protection.md)).

### Metric and span rules for IDs

IDs safe for logs are not automatically safe as metric labels.

- **Do log** aggregate IDs in log fields and trace attributes when per-request
  cardinality is acceptable.
- **Do not label metrics with** raw user/customer/passenger IDs, timestamps,
  email, phone, IP, or unbounded strings. Prefer `state`, `command`, `errorCode`,
  or bounded `tenantId`.

```scala
// Good: bounded domain vocabulary.
metrics.counter("taxi_request.driver_assigned", "fleet" -> fleet.value).increment()

// Avoid: per-user labels explode cardinality and leak identity.
metrics.counter("notification.sent", "userId" -> userId.value).increment()
```

### Quick decision checklist

1. Secret or auth token? → do not log.
2. Direct PII or regulated identifier? → do not log.
3. Opaque surrogate with no embedded PII? → usually safe.
4. Does this field expose more than intended? → redact or restricted audit path.
5. Is `toString`/`Show` reviewed for safe logging? → fix the type first.

## Log State Transitions Explicitly

Log both before and after state so investigations can reconstruct lifecycle.
When transitions emit events, include event names/types, not full payloads,
unless the payload is already safe for operations.

```scala
Logger[F].info(Map(
  "requestId" -> outcome.state.requestId.value,
  "from"      -> "waiting",
  "to"        -> "en-route",
  "events"    -> outcome.events.map(_.name).mkString(",")
))("driver assignment completed")
```

Keep transition logging at the use case that owns the transaction. Do not
scatter logs in every getter or validation helper.

## Keep Errors Actionable

Log domain errors with enough context to trace the failing path. Reuse structured
identifiers from the surrounding use case.

```scala
repository.findWaiting(requestId).flatMap {
  case None =>
    Logger[F].warn(Map("requestId" -> requestId.value))("request not found") >>
      ME.raiseError(AssignDriverError.RequestNotFound(requestId))
  case Some(waiting) =>
    ME.pure(waiting)
}
```

Avoid logging the same failure at every layer. Let the use case own the
authoritative log line and propagate the typed error upward.

## Integrate Error Chains with Structured Logging

`Either` error ADTs and logging should expose domain context and underlying
cause in one place.

```scala
execute(requestId, driver).flatMap {
  case Left(error) =>
    Logger[F].error(Map(
      "requestId" -> requestId.value,
      "driverId"  -> driver.id.value,
      "error"     -> error.toString // ADT with safe Display, not raw PII
    ))("assign driver use case failed") >>
      ME.raiseError(error)
  case Right(value) =>
    ME.pure(value)
}
```

Guidelines:

- Prefer error ADTs whose `toString` includes `cause` via nested errors when
  infrastructure failures wrap JDBC/HTTP errors mapped to semantic variants.
- Add domain fields alongside the error, not inside free-form message strings.
- Map infrastructure failures before logging when raw messages would leak
  endpoints, SQL, or secrets.
- Increment metrics with bounded labels (`errorCode` from enum), not full error text.

Cross-check [`error-handling.md`](./error-handling.md). Do not duplicate logging
in repository adapters if the use case already logs with richer context.

## Tracing and Spans (trace4cats / OpenTelemetry)

When the project uses trace4cats or OpenTelemetry:

- Keep spans around use-case or application-service boundaries, not every helper.
- Name spans after operations (`use_case.assign_driver`) and carry aggregate IDs.
- Use `IO`/`F` syntax that adds attributes explicitly; avoid auto-serializing
  whole DTOs or patient/user structs into span fields.
- Apply the same ID classification rules as logs.

```scala
import trace4cats.Span

Span[F].trace("use_case.assign_driver") {
  Span[F].putAll(
    "requestId" -> requestId.value,
    "driverId"  -> driver.id.value
  ) >> /* ... */
}
```

Do not treat spans as domain events or audit records. Persist business events
through domain event types or an outbox when durability is required.

## Measure Domain Outcomes

Metrics should reflect business outcomes, not only JVM machinery.

- **Counters**: transitions, commands accepted/rejected, published events.
- **Histograms**: time in each aggregate state, use-case latency.
- **Gauges**: point-in-state values (waiting request count).

Use consistent labels from domain types. Keep cardinality low — bounded state or
command names, not raw IDs or timestamps.

## Export Telemetry Through OpenTelemetry

Wire exporters at application startup, not in domain code. Common Scala stacks:

- **Metrics**: Micrometer + OTLP, or OpenTelemetry Java SDK bridged from Cats
  effect apps at the composition root.
- **Tracing**: trace4cats OTLP exporter, or OpenTelemetry agent for JVM services.
- **Logs**: logback with JSON appenders or OTLP log exporter.

Do not design domain or application layers around a specific vendor backend.

## Correlate Logs and Metrics

Carry a correlation identifier through the request or command. Include it in
structured logs and, when practical, trace attributes so operations can pivot
between logs, metrics, and traces.

```scala
val correlationId = CorrelationId.generate()
// MDC, span attribute, or log context map
```

Keep tracing spans at use-case boundaries. The span names the operation and
carries the aggregate identifier, not thread details.
