# PII Protection

## Wrap Sensitive Values

Represent emails, phone numbers, government IDs, tokens, and secrets with dedicated types that redact by default in `toString`, logging, and metrics.

```scala
opaque type EmailAddress = String

object EmailAddress:
  def apply(value: String): Either[EmailError, EmailAddress] = ...

  extension (email: EmailAddress)
    def redacted: String =
      val local = email.value
      val at = local.indexOf('@')
      if at <= 1 then "[redacted]" else s"${local.head}***${local.substring(at)}"
```

Do not log raw boundary DTOs that may contain sensitive fields.

## Redact in Logs, Metrics, Errors, and Events

Structured logs and trace attributes should use redacted forms. Error messages returned to clients must not echo secrets or full identifiers unless required by the product contract.

## Narrow Plaintext Exposure

Expose `.value` or equivalent only at intentional boundaries: persistence encryption, outbound provider APIs, or audited exports. Every plaintext accessor should have a documented reason.

## Observability Defaults

Assume log pipelines and metrics backends are broadly visible. Treat PII wrappers as the default for fields that could identify a person or authenticate a session.

See [`logging-metrics.md`](./logging-metrics.md) for log field conventions.
