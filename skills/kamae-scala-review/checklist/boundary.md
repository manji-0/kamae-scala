# Boundary Checklist
Reference: [`../../kamae-scala/references/boundary-defense.md`](../../kamae-scala/references/boundary-defense.md).

## 4.1 Is external data converted through DTOs into domain types? - High

Flag direct construction of domain aggregates from JSON/row maps without validation.

## 4.2 Are codecs treated as transport only? - Medium

Flag assuming JSON derivation validates business rules.

## 4.3 Are external formats over-derived on domain types? - Medium

Flag Circe/Play codecs on aggregate roots with invariants.

## 4.4 Are unknown fields and defaults handled explicitly? - Medium

Flag silent acceptance of missing discriminators or default enum values on inbound messages.

## 4.5 Are auth/tenant checks at the boundary? - High

Flag controllers or consumers that construct commands before verifying caller scope.
