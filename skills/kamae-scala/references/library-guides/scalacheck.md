# ScalaCheck

Use ScalaCheck when the project already depends on it or when property tests are
the clearest way to cover input-wide laws.

Keep it in `Test` scope. Prefer generators that call public constructors rather
than building invalid domain states directly.

```scala
import org.scalacheck.Prop.forAll
import org.scalacheck.Gen

property("valid ids construct") {
  forAll(nonEmptyStringGen) { raw =>
    RequestId(raw.trim).isRight
  }
}
```

See [`../property-based-tests.md`](../property-based-tests.md) for generator
design, state properties, CI budget, and regression files.
