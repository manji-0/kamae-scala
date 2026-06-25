# Gradual Kamae Adoption

<!-- constrained-by ./boundary-defense.md -->
<!-- constrained-by ./application-wiring.md -->
<!-- constrained-by ./orm-adapters.md -->

## Default Stance

Apply Kamae to new code paths first. Tighten existing code where you already
touch it for a feature or bugfix. Do not block delivery on a full-domain rewrite.

When legacy conventions conflict, follow the local convention for untouched code
and document the new boundary clearly where old and new meet.

## Recognize Legacy Shapes

Common starting points in Scala server codebases:

- anemic case classes with service objects or implicit extensions everywhere
- Slick/doobie row types used as domain entities
- `String` IDs and status strings instead of opaque types
- `throw`, `.get`, or bare `Exception` through business logic
- controllers or routes that call JDBC/HTTP directly

These are migration sources, not failures. Pick the smallest change that removes
the next likely bug.

## Adoption Ladder

Move one rung at a time. Each step should be reviewable on its own.

| Step | Change | Typical touch points | Risk |
| --- | --- | --- | --- |
| 0. Boundary only | DTO/row → `Either` parsing for new endpoints | http4s/Pekko routes, consumers | Low |
| 1. IDs and value objects | `RequestId`, `Money`, `OccurredAt` opaque types | models in the changed flow | Low |
| 2. Domain errors | error ADTs in new use cases | application layer | Low |
| 3. Typed state | sealed states for one important aggregate | domain module | Medium |
| 4. Ports | small repository traits behind the new use case | application + infrastructure | Medium |
| 5. Transactions and versions | atomic save, outbox, optimistic version checks | persistence adapter | Medium–High |

Skip steps only when the codebase already satisfies them.

## Strangler-Fig a Feature, Not the Whole Service

For a legacy module:

1. Add a new use-case class for the changed workflow.
2. Keep old entry points calling legacy code until the new path is proven.
3. Route new API versions, flags, or commands to the new use case.
4. Delete the old path after parity tests pass.

```text
legacy route -> legacy service -> JDBC
new route    -> AssignDriver use case -> port -> adapter -> JDBC
```

Prefer one aggregate or one endpoint per migration slice.

## Step-by-Step Legacy Roadmap

Example: migrating `POST /requests/{id}/assign` in a monolithic http4s + doobie service.

### Phase 1 — Freeze behavior, add tests (week 1)

1. Capture current HTTP contract with integration tests (status codes, JSON shape).
2. Add logging/metrics around the legacy path to measure traffic.
3. Do not change behavior yet.

### Phase 2 — Boundary DTO (week 1–2)

1. Introduce `AssignDriverBody` and `AssignDriverDto` in an `interfaces` module.
2. Replace direct field access in the route with `AssignDriverCommand` parsing via `Either`.
3. Legacy service still receives strings; validation now lives at the boundary.
4. Ship behind the same route; tests must stay green.

See [`boundary-defense.md`](./boundary-defense.md).

### Phase 3 — Opaque IDs on touched fields (week 2)

1. Add `RequestId`, `DriverId` opaque types in a `domain` module.
2. Change boundary parsing to construct opaque types; legacy service accepts `.value` at the seam.
3. Enable stricter scalafix/scalac options on the new `domain` module only.

See [`domain-modeling.md`](./domain-modeling.md).

### Phase 4 — Use case extraction (week 3)

1. Create `AssignDriver` with legacy SQL inlined in a private method.
2. Route handler calls `useCase.execute(cmd)` only.
3. Replace exceptions in this path with `AssignDriverError` ADT and `Either`.

See [`error-handling.md`](./error-handling.md).

### Phase 5 — Typed state for one aggregate (week 3–4)

1. Model `WaitingRequest` and `EnRouteRequest`; move assignment to `WaitingRequest.assignDriver`.
2. Legacy `status: String` remains in DB; adapter maps rows ↔ state types.
3. Add unit tests on transitions without HTTP.

See [`state-transitions.md`](./state-transitions.md) and [`orm-adapters.md`](./orm-adapters.md).

### Phase 6 — Repository port (week 4–5)

1. Define `TaxiRequestRepository[F]` and related port traits.
2. Move SQL from use case to `DoobieTaxiRequestRepository`.
3. Use case depends on traits only; wire in `main` or composition root.

See [`persistence-events.md`](./persistence-events.md) and [`application-wiring.md`](./application-wiring.md).

### Phase 7 — Transactions, version, outbox (week 5–6)

1. Add `version` column and conditional `UPDATE`.
2. Wrap state save + outbox insert in one transaction.
3. Add idempotency key support for retried clients.

See [`aggregate-transactions.md`](./aggregate-transactions.md).

### Phase 8 — Remove legacy path (week 6+)

1. Confirm feature flag or route traffic is 100% on new path.
2. Delete legacy service function and dead `status` string checks.
3. Run `kamae-scala-review` on the migrated module.

Adjust pacing to team size. Each phase is an independent PR when possible.

## Keep Diffs Reviewable

- Do not mix mechanical refactors with behavior changes in one PR when avoidable.
- Add tests at the new boundary before deleting the old path.
- Introduce opaque types and DTO conversion on touched fields only; widen later.
- Enable extra scalafix rules on the module you are hardening.
- Leave a short comment or ADR only when old and new semantics differ.

## When to Stop Climbing the Ladder

Not every struct needs a state machine or repository trait. Stay at the current
rung when:

- the code is stable, low-risk, and rarely changes
- the aggregate has no meaningful lifecycle or invariants
- the team cannot yet test persistence or concurrency behavior credibly

Raise the rung when bugs, compliance needs, or concurrency show the current
shape is too weak.

## Agent and Reviewer Expectations

When migrating:

- load [`adoption.md`](./adoption.md) for scope decisions
- load the target topic guide for the rung you are implementing
- use `kamae-scala-review` on changed paths even if surrounding code is legacy
- call out residual legacy risk explicitly instead of pretending the service is fully migrated
