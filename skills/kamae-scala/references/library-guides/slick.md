# Slick

Use Slick for SQL adapters when the project already standardizes on it.

## Table Definitions Stay in Infrastructure

Keep `Table` subclasses, `DBIO`, and profile imports out of domain modules. Repository ports use `F[_]` and domain types only.

## Map Before Returning

Convert `RequestRow` (or equivalent) to domain states in the adapter with the same validating mappers described in [`../orm-adapters.md`](../orm-adapters.md).

## Sessions and Transactions

Own `db.run(...transactionally)` in adapters. Do not pass `Database` or `DBIO` into use cases.

Avoid lazy loading or navigating foreign-key relations during domain mapping; query explicit columns for the state you need.
