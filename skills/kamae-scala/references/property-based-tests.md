# Property-Based Tests

Use ScalaCheck when you need broader input coverage for validators, parsers, and transitions.

## Good Properties

- Valid generated IDs always construct successfully
- Invalid blank IDs always fail with the expected error
- Successful transitions never return events for a different aggregate ID
- Redacted PII never equals the raw secret value in logs/strings

## Keep Generators Lawful

Derive generators from domain constraints. Do not generate nonsense strings for typed IDs when a smart constructor exists.

## Scope

Property tests complement example-based tests; they do not replace scenario tests for orchestration and persistence.
