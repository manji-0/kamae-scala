# Persistence and Events Checklist
Reference: [`../../kamae-scala/references/persistence-events.md`](../../kamae-scala/references/persistence-events.md).

## 6.1 Are state and events persisted atomically? - High

Flag separate writes with no transaction boundary when events must match state.

## 6.2 Are repository traits small and domain-shaped? - Medium

Flag repositories returning ORM entities directly to use cases.

## 6.3 Do adapters invent events? - High

Flag repositories emitting business events not returned by domain transitions.

## 6.4 Do DB constraints mirror invariants? - Medium

Flag nullable columns or free-form status strings that contradict domain states.

## 6.5 Is retry/idempotency handled? - Medium

Flag outbox consumers without duplicate handling.

## 6.6 Is event versioning considered? - Medium

Flag breaking event schema changes without version markers.
