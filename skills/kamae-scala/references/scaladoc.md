# Scaladoc Contracts

## Document Public Domain APIs

Public domain types and transition methods should have Scaladoc that states:

- What invariant the type enforces
- What errors a method can return in `Either` left cases
- Which source state a transition accepts
- A short lawful example when non-obvious

```scala
/** A taxi request waiting for driver assignment.
  *
  * Construct with [[WaitingRequest.apply]] after validating IDs.
  */
final case class WaitingRequest(...)

/** Assigns a driver when accessibility preconditions are satisfied.
  *
  * @return [[DomainError.DriverCannotServeAccessibilityRequest]] when the driver cannot serve the request.
  */
def assignDriver(driver: DriverAssignment): Either[DomainError, Transition[EnRouteRequest, TaxiRequestEvent]]
```

## Errors and Throws

If a method can fail, document the left/error cases. Do not document `throws` for domain methods that should use `Either`.

## Examples Must Be Lawful

Scaladoc examples should use valid IDs and reachable transitions. Do not copy test-only shortcuts that use `.get` on invalid input.

## Link to Related Types

Use `[[Type]]` links between states, events, and errors so readers can navigate the state machine from docs.

## Scope

Full Scaladoc coverage is expected for published domain libraries. Internal application modules may scope docs to public ports and aggregate roots first.
