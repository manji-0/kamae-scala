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
- `org.tpolecat` with `doobie` -> `references/library-guides/doobie.md`
- `co.fs2` -> `references/library-guides/fs2.md`
- `com.typesafe.slick` -> `references/library-guides/slick.md`
- `eu.timepit.refined` -> `references/library-guides/refined.md`
- `org.scalacheck` -> `references/library-guides/scalacheck.md`

Detection-only libraries:

- Error/effects: `monix`
- Boundary/serialization: `play-json`, `json4s`, `upickle`
- Validation/units: `org.typelevel.squants`
- Secrets/credentials: load `references/library-guides/secrets.md` when auth tokens or API keys appear in diff
- Persistence: `quill`, `skunk`
- Streams: `pekko-stream`, `zio-streams`
- Testing: `org.scalacheck` -> load `property-based-tests.md`; detection-only: `weaver`, `scalatest`

Detection-only means the library should inform local code review or implementation context, but there is no plugin guide to load. Prefer existing project conventions and Scala 3 standard patterns before adding dependencies.
