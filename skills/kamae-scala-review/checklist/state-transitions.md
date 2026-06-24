# State Transitions Checklist
Reference: [`../../kamae-scala/references/state-transitions.md`](../../kamae-scala/references/state-transitions.md).

## 2.1 Do transitions accept typed source states? - High

Flag methods that take a broad enum or string status when only one state should be legal.

## 2.2 Are domain matches exhaustive? - Medium

Flag non-exhaustive `match` on sealed domain types without a documented default for external boundaries only.

## 2.3 Are transitions pure? - High

Flag transitions that perform I/O, read clocks, generate random IDs, or mutate shared state.

## 2.4 Do transitions live on the owning concept? - Medium

Flag use cases or controllers embedding business rules that belong on domain state types.

## 2.5 Do mutators preserve invariants? - High

Flag update methods that leave aggregates in illegal combined states.

## 2.6 Are auth/tenant guards enforced before transitions? - High

Flag transitions callable without tenant or permission checks when the workflow requires them.

## 2.7 Is concurrent transition safety considered? - Medium

Flag lost-update patterns without versioning, optimistic locking, or explicit conflict errors.
