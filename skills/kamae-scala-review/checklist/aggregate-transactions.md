# 18 — Aggregate Transactions

Topic guide: [`../kamae-scala/references/aggregate-transactions.md`](../kamae-scala/references/aggregate-transactions.md)

## 19.1 Single Transaction Boundary

- Does each use case persist one aggregate's state and events in a single transaction?
- Are there dual writes (e.g. save state then separately insert events) that could leave inconsistent data?

## 19.2 Optimistic Concurrency

- Do concurrently-updated aggregates carry a version field?
- Does the adapter check `WHERE version = :expected` and return a typed retryable error on mismatch?
- Does the use case handle `StaleVersion` explicitly (retry or propagate)?

## 19.3 Aggregate Scope

- Does the aggregate contain only data it needs to validate its own invariants?
- Are there fields read but never validated together, suggesting the aggregate is too large?
- Do unrelated lifecycles share one root unnecessarily?

## 19.4 Cross-Aggregate Coordination

- When two aggregates change, does the code rely on domain events and eventual consistency rather than a single transaction spanning both?
- If synchronous cross-aggregate coordination exists, is the coupling documented and failure handling explicit?
