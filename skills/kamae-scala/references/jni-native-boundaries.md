# JNI and Native Boundaries

<!-- constrained-by ./boundary-defense.md -->
<!-- constrained-by ./application-wiring.md -->

Scala/JVM domain code should not call JNI, JNA, or native libraries directly.

## Hide Native Code Behind Small Modules

When native interop is required (crypto accelerators, media codecs, legacy SDKs), expose a narrow Scala API that:

- Validates inputs before crossing the boundary
- Maps native failures into typed errors
- Documents invariants the native layer assumes

```scala
// Good: small safe wrapper
trait ImageEncoder[F[_]]:
  def encode(image: RawImage, format: OutputFormat): F[Either[EncodeError, EncodedImage]]

// Adapter hides JNI
class JniImageEncoder[F[_]: Sync] extends ImageEncoder[F]:
  def encode(image: RawImage, format: OutputFormat): F[Either[EncodeError, EncodedImage]] =
    Sync[F].blocking:
      try
        val result = NativeImageLib.encode(image.bytes, format.toNativeCode)
        Right(EncodedImage(result))
      catch
        case e: NativeException => Left(EncodeError.NativeFailure(e.getMessage))
```

## No Native Calls in Domain Transitions

Domain transitions remain pure Scala. Native work happens in infrastructure adapters. This keeps domain tests fast and free of native library loading.

## Resource Safety

Native resources (handles, pointers, allocated buffers) must be managed with `Resource[F, A]` or `ZManaged` to guarantee cleanup:

```scala
def withNativeSession[F[_]: Sync, A](f: NativeSession => F[A]): F[A] =
  Resource
    .make(Sync[F].blocking(NativeLib.openSession()))(s => Sync[F].blocking(s.close()))
    .use(f)
```

## Tests

Mock or fake the native wrapper in domain/application tests. Reserve real native integration tests for adapter modules with explicit CI jobs.

When JNI tests require specific OS or architecture, gate them behind sbt tags or CI matrix entries so they do not block the main test suite:

```scala
// build.sbt
lazy val nativeTests = (project in file("native-tests"))
  .settings(
    Test / testOptions += Tests.Argument("-l", "NativeOnly")
  )
```

See [`boundary-defense.md`](./boundary-defense.md) and [`application-wiring.md`](./application-wiring.md).
