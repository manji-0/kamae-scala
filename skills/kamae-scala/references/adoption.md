# Gradual Adoption

Adopt Kamae Scala incrementally when brownfield code already exists.

## Start at Boundaries

Introduce DTO parsing and validating constructors at HTTP, DB, and message edges first. Keep existing internal models temporarily if needed, but stop new invalid states from entering the domain.

## Extract One Workflow at a Time

Pick a high-risk workflow (stateful, money-moving, PII-heavy) and model it with typed states and `Either`-based transitions. Leave unrelated modules unchanged until the pattern is proven.

## Strangler for Persistence

Add repository traits and adapters beside legacy data access. Route one use case through the new port before deleting old query code.

## Coexist with Legacy Error Types

Map legacy exceptions to new `UseCaseError` ADTs at the use-case boundary. Do not rewrite every module to `Either` in one pass unless the team has capacity for a focused migration.

## When Not to Force Compile-Time States

If a workflow is genuinely dynamic and external rules change at runtime, document why sealed states were not used and keep runtime validation explicit with tests.
