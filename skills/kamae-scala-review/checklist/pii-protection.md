# PII Protection Checklist
Reference: [`../../kamae-scala/references/pii-protection.md`](../../kamae-scala/references/pii-protection.md).

## 5.1 Are sensitive values wrapped? - High

Flag raw strings for email, phone, government ID, token, password, or secret fields in domain and application code.

## 5.2 Are logs and debug output redacted? - High

Flag logging of full DTOs, headers, or exception messages that may contain secrets.

## 5.3 Is plaintext exposure narrow? - Medium

Flag public `.value` accessors on sensitive types without a documented reason.

## 5.4 Is observability redacted by default? - Medium

Flag metrics labels or trace attributes using high-cardinality or identifying values.
