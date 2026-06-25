# Domain Macros Checklist

Reference: [`../../kamae-scala/references/domain-macros.md`](../../kamae-scala/references/domain-macros.md).

## 14.1 Do derives or macros hide domain invariants? - High

Flag `derives Decoder`/`Encoder`, macro-generated companions, or implicit conversions
that add public constructors, default values, or validation that differs from
hand-written domain rules.

## 14.2 Is generated toString/Show safe for logs? - High

Cross-check [`logging-metrics.md`](./logging-metrics.md). Flag derived `toString`,
`Show`, or Circe encoders on IDs, events, or payloads that could expose PII or secrets.

## 14.3 Are macros or derives justified by repetition? - Low

Flag new internal macro modules for one or two types when opaque types with explicit
companions or hand-written codecs would be clearer in review.

## 14.4 Do event types preserve version metadata? - Medium

Flag domain events without stable `name`/`version` (or equivalent) when they are
persisted, queued, or consumed across deploys.

## 14.5 Are Decoder/Read derives avoided on domain types? - Medium

Cross-check [`boundary.md`](./boundary.md). Flag Circe, Play JSON, or doobie `Read`/`Write`
derives on invariant-bearing domain types unless the project documents an explicit
leaf-validation convention.
