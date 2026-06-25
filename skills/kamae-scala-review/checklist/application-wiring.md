# 17 — Application Wiring

Topic guide: [`../kamae-scala/references/application-wiring.md`](../kamae-scala/references/application-wiring.md)

## 18.1 Use Case Single Operation

- Does each use case class own one business operation?
- Are there use case classes accumulating many unrelated methods that should be split?

## 18.2 Composition Root Only

- Are concrete adapters wired only in the bootstrap module (`Main`, `Bootstrap`, ZIO `App` layer)?
- Do domain and application packages depend on traits, not JDBC/HTTP drivers or concrete implementations?
- Are there `new ConcreteRepository(...)` calls outside the composition root?

## 18.3 Pure Domain Transitions

- Are domain transitions free of SQL, JSON parsing, HTTP calls, or other side effects?
- Do use cases orchestrate (load state, call transition, persist) without leaking infrastructure into transitions?

## 18.4 Edge Error Mapping

- Do HTTP/gRPC/CLI adapters map `UseCaseError` to response codes and client-safe messages?
- Are repository exception strings or stack traces prevented from leaking to clients?

## 18.5 Test Wiring

- Do use case tests inject fakes or in-memory ports rather than real infrastructure?
- Can business logic be tested without a database, HTTP server, or external service?
