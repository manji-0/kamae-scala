# JNI and Native Boundaries

Scala/JVM domain code should not call JNI, JNA, or native libraries directly.

## Hide Native Code Behind Small Modules

When native interop is required (crypto accelerators, media codecs, legacy SDKs), expose a narrow Scala API that:

- Validates inputs before crossing the boundary
- Maps native failures into typed errors
- Documents invariants the native layer assumes

## No Native Calls in Domain Transitions

Domain transitions remain pure Scala. Native work happens in infrastructure adapters.

## Tests

Mock or fake the native wrapper in domain/application tests. Reserve real native integration tests for adapter modules with explicit CI jobs.
