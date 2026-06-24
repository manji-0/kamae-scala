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
