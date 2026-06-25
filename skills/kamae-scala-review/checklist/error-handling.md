# Error Handling Checklist
Reference: [`../../kamae-scala/references/error-handling.md`](../../kamae-scala/references/error-handling.md).

## 3.1 Are throws and unsafe gets avoided in domain code? - High

Flag `throw`, `???`, `.get`, `.head`, and `.last` on `Option`/`Either` in domain and use-case code outside tests.

## 3.2 Are domain errors specific? - High

Flag bare `Exception`, `Throwable`, or `String` error returns from domain functions.

## 3.3 Are infrastructure errors mapped intentionally? - Medium

Flag repository/driver exceptions leaking to HTTP responses or crossing into domain transitions unchanged.

## 3.4 Do error variants carry useful meaning? - Medium

Flag catch-all error cases that hide distinct business failures reviewers and operators need to distinguish.

## 3.5 Are effect boundaries respected in async use cases? - Medium

Cross-check [`application-wiring.md`](./application-wiring.md). Flag `Future`/`IO`/`ZIO`
use cases that block, lose failures across async boundaries, or call ports without
mapping infrastructure errors to use-case ADTs.

## 3.6 Is the same failure logged at every layer? - Low

Cross-check [`logging-metrics.md`](./logging-metrics.md). Flag duplicate error logs
in adapters when the use case already logs the authoritative failure.

## 3.7 Are infrastructure errors mapped before crossing boundaries? - Medium

Flag JDBC, HTTP client, or messaging exceptions reaching HTTP responses or domain
transitions without semantic mapping.

## 3.8 Do error messages avoid PII and secrets? - High

Cross-check [`pii-protection.md`](./pii-protection.md). Flag `getMessage`, ADT
`toString`, or client-facing error text that echoes email, phone, tokens, or
government IDs.
