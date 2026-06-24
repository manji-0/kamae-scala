# Aggregate Transactions Checklist
Reference: [`../../kamae-scala/references/aggregate-transactions.md`](../../kamae-scala/references/aggregate-transactions.md).

## 16.1 Is one aggregate changed per transaction when practical? - High

Flag multi-root mutations depending on caller persistence discipline.

## 16.2 Is optimistic concurrency handled? - Medium

Flag version fields ignored during updates.

## 16.3 Is cross-aggregate work orchestrated explicitly? - Medium

Flag hidden cross-aggregate updates inside a single aggregate object.
