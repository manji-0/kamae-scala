---
name: library-detection
description: Auto-detect Scala libraries from build.sbt
applies-to: "*"
type: library-preference
alwaysApply: false
---

# Library Detection

Read `build.sbt`, `project/*.sbt`, and relevant module manifests during implementation and review. Load library guides only when their library is present and relevant to the task.

Guide-backed detections:

- `io.circe` -> `references/library-guides/circe.md`
- `org.typelevel` with `cats` -> `references/library-guides/cats.md`
- `dev.zio` -> `references/library-guides/zio.md`
- `com.github.pureconfig` -> `references/library-guides/pureconfig.md`

Detection-only libraries:

- Error/effects: `monix`, `fs2`
- Boundary/serialization: `play-json`, `json4s`, `upickle`
- Validation/units: `eu.timepit.refined`, `org.typelevel.squants`
- Persistence: `doobie`, `slick`, `quill`, `skunk`
- Async/RPC: `pekko`, `http4s`, `sttp`
- Testing: `org.scalacheck` -> load `property-based-tests.md`; detection-only: `weaver`, `scalatest`

Detection-only means the library should inform local code review or implementation context, but there is no plugin guide to load. Prefer existing project conventions and Scala 3 standard patterns before adding dependencies.
