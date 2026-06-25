# ORM Adapters Checklist

Reference: [`../../kamae-scala/references/orm-adapters.md`](../../kamae-scala/references/orm-adapters.md).

## 18.1 Are ORM/row types kept out of domain modules? - High

Flag Slick `Table` rows, doobie result types, or Quill entities imported by domain states, transitions, or use-case modules.

## 18.2 Do mappers validate on the way in and out? - High

Flag row-to-domain conversion that uses unchecked casts, `.asInstanceOf`, or nullable columns without explicit `Either` mapping.

## 18.3 Are sessions and transactions owned by adapters? - Medium

Flag use cases that manage JDBC connections, `ConnectionIO`, or `DBIO` directly when repository adapters should own persistence concerns.

## 18.4 Does lazy loading stay out of domain/use-case paths? - Medium

Flag implicit lazy loads or N+1 query patterns triggered during transition or use-case logic.

## 18.5 Are optimistic-lock columns mapped consistently? - High

Flag version columns ignored on save, or ORM updates that can silently overwrite concurrent changes.

Cross-check [`aggregate-transactions.md`](./aggregate-transactions.md).
