# Service Boundaries

## Keep Domain Packages Free of Transport Details

HTTP routes, gRPC services, and message consumers should translate requests into commands, invoke use cases, and map errors to transport responses. They should not contain business rules.

## Anti-Corruption at Module Edges

When integrating with other teams' services, define local DTOs and map into your domain types. Do not leak foreign models into domain transitions.

## Timeouts and Retries Stay in Adapters

Resilience policies belong in infrastructure clients, not domain code. Use cases may interpret retryable errors, but should not configure thread pools or HTTP clients directly.

See [`application-wiring.md`](./application-wiring.md).
