# 15 — Service Boundaries

Topic guide: [`../kamae-scala/references/service-boundaries.md`](../kamae-scala/references/service-boundaries.md)

## 16.1 No Business Logic in Routes

- Do HTTP routes, gRPC services, and message consumers only translate requests to commands, invoke use cases, and map errors?
- Is there business logic (validation, state checks, calculations) embedded in route handlers?

## 16.2 Anti-Corruption Layer

- When integrating with external services, are local DTOs defined and mapped into domain types?
- Do foreign models leak into domain transitions or repository ports?

## 16.3 Resilience in Adapters

- Do timeouts, retries, and circuit breakers live in infrastructure clients, not domain code?
- Do use cases interpret retryable errors without configuring thread pools or HTTP clients?

## 16.4 Contract Versioning

- For gRPC and message queue contracts, are schemas versioned explicitly?
- Are optional fields used to silently evolve contracts without consumers noticing breakage?
