# Service Boundaries Checklist
Reference: [`../../kamae-scala/references/service-boundaries.md`](../../kamae-scala/references/service-boundaries.md).

## 13.1 Is transport code free of business rules? - High

Flag controllers or route handlers implementing transitions directly.

## 13.2 Are foreign models kept at the edge? - Medium

Flag external service DTOs referenced inside domain packages.

## 13.3 Is resilience confined to adapters? - Medium

Flag retry/timeouts configured inside domain transitions.
