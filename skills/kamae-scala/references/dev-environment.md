# Development Environment

## Toolchain

Default to:

- Scala 3.3+
- Java 17+
- sbt 1.10+

Pin versions in `project/build.properties` and document any native dependencies separately.

## Module Layout

A typical Kamae-style backend layout:

```text
domain/          pure domain types and transitions
application/     use cases and ports
infrastructure/  adapters (db, http, messaging)
interfaces/      HTTP/gRPC/CLI entrypoints
```

Domain modules should not depend on infrastructure modules.

## Test Layers

| Layer | Focus |
| --- | --- |
| Domain unit tests | constructors, transitions, invariant failures |
| Application tests | use-case orchestration with fake ports |
| Adapter integration tests | SQL/HTTP/message boundaries |
| End-to-end smoke | critical workflows only |

## Local Check Loop

```bash
sbt scalafmtAll
sbt test
```

Run the review probe on changed domain files before opening a PR when the skill is installed.

## Example Project

This repository's taxi-request example lives under `skills/kamae-scala/examples/`.
