# Doobie

Use doobie for SQL adapters, not domain modeling.

## Rows Are Boundary Types

Keep `Read`/`Write` instances on row case classes in infrastructure. Map rows to domain types with explicit `Either` mappers before returning from repository ports.

## Transactions Belong in Adapters

Use `transact(xa)` at the adapter or use-case boundary, not inside domain transitions. State changes and outbox inserts for one command should share one transaction.

## Avoid Leaking ConnectionIO

Repository traits should use `F[_]` (typically `IO`) at the port level. `ConnectionIO` stays inside adapter implementations.

See [`../orm-adapters.md`](../orm-adapters.md) for mapper patterns.
