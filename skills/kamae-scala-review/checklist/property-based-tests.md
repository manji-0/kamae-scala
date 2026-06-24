# Property-Based Tests Checklist
Reference: [`../../kamae-scala/references/property-based-tests.md`](../../kamae-scala/references/property-based-tests.md).

## 14.1 Are high-risk parsers/generators covered? - Medium

Flag complex validators with only hand-picked examples.

## 14.2 Are generators lawful? - Medium

Flag arbitrary strings used for typed IDs when smart constructors exist.
