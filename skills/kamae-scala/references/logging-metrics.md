# Logging and Metrics

## Log Stable Domain Identifiers

Prefer typed IDs with redaction helpers over raw strings in log statements.

## Metrics Use Low-Cardinality Labels

Count transitions and failures with bounded label sets (`result=success|domain_error|infra_error`). Do not use user IDs, emails, or free-form error text as metric labels.

## Correlate Without Leaking PII

Use request/trace IDs at boundaries. Keep person-identifying fields out of info-level logs unless the product explicitly requires them and they are redacted appropriately.

See [`pii-protection.md`](./pii-protection.md).
