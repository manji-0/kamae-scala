# Logging and Metrics Checklist
Reference: [`../../kamae-scala/references/logging-metrics.md`](../../kamae-scala/references/logging-metrics.md).

## 6.1 Are logs using stable identifiers? - Medium

Flag unstructured string interpolation of full entities where typed IDs exist.

## 6.2 Are metric labels low cardinality? - Medium

Flag user IDs, emails, or free-form error text used as metric labels.
