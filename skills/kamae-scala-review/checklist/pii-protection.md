# PII Protection Checklist

Reference: [`../../kamae-scala/references/pii-protection.md`](../../kamae-scala/references/pii-protection.md).
Also see [`../../kamae-scala/references/library-guides/secrets.md`](../../kamae-scala/references/library-guides/secrets.md).

## 5.1 Are PII and secrets wrapped? - High

Flag bare `String`, `Array[Byte]`, or primitive fields carrying email, phone, address, names, government IDs, payment data, health data, IP addresses, precise location, tokens, or passwords.

Suggest opaque credential wrappers from `secrets.md` or project-local redacting types.

Do not require credential wrappers for every PII value. Non-secret identifiers such as display names or emails may use domain opaque types if `toString`, logs, and serialization are redacted or intentionally exposed.

## 5.2 Can toString or logs expose sensitive data? - High

Flag default case class `toString`, structured log fields, formatted errors, or logs that include raw sensitive values.

Also check metrics, span attributes, audit events, and validation errors for raw PII or secrets.

## 5.3 Is plaintext exposure narrow and named? - Medium

Flag broad public `.value` accessors for sensitive types. Suggest adapter-specific exposure methods or wrappers.

## 5.4 Is observability redacted by default? - High

Flag logging/metrics helpers that accept arbitrary domain objects or DTOs without redaction policy, allowlist fields, or explicit safe display wrappers.

## 5.5 Are person-linked IDs treated as conditional, not automatically safe? - High

Cross-check with `logging-metrics.md#which-ids-belong-in-logs`. Flag `userId`,
`passengerId`, `customerId`, `patientId`, `deviceId`, or partner references
logged without evidence that the value is an opaque surrogate.

Do not flag internal aggregate IDs such as `requestId`, `orderId`, or
`correlationId` when they are clearly surrogate keys with safe formatting.
