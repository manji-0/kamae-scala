# Scala Development Environment

<!-- constrained-by ./application-wiring.md -->
<!-- constrained-by ./ci-setup.md -->
<!-- constrained-by ./quality-gates.md -->
<!-- constrained-by ./test-data.md -->

## Goal

Set up a workspace where domain code can be implemented and tested the way
Kamae expects: typed domain models, port-based use cases, constructor-based
fixtures, and the same checks reviewers and CI rely on.

This guide is for **application projects** that follow the skill. For editing the
kamae-scala skill package itself, see [`development-setup.md`](./development-setup.md).

## Toolchain

Install Java and sbt:

| Component | Minimum | Pin location |
| --- | --- | --- |
| Java | 17 (LTS) | `JAVA_HOME`, CI `setup-java` |
| Scala | 3.3+ | `ThisBuild / scalaVersion` in `build.sbt` |
| sbt | 1.10+ | `project/build.properties` |

```properties
# project/build.properties
sbt.version=1.10.11
```

Optional but useful for domain work:

| Tool | Purpose |
| --- | --- |
| [Coursier](https://get-coursier.io/) | Faster dependency fetch; `cs install sbt` |
| [Metals](https://scalameta.org/metals/) | IDE support for Scala 3, go-to-definition, compile errors |
| [sbt-revolver](https://github.com/spray/sbt-revolver) | Fast app reload during adapter/API work |

Keep domain subproject builds fast. Prefer `sbt "project domain" test` over
testing the entire monorepo while iterating on transitions or value objects.

## Recommended Module Layout

Split responsibilities so domain logic stays free of I/O and framework types.

**Multi-module sbt** (preferred for services):

```text
my-service/
  build.sbt                    # aggregate root
  project/
    build.properties
    plugins.sbt
  domain/                      # entities, opaque IDs, transitions, domain errors
  application/                 # use cases, port traits, use-case errors
  infrastructure/              # doobie/Slick adapters, outbox, telemetry wiring
  interfaces/                  # http4s/Pekko handlers, DTOs, composition root
```

**Single-module** projects can use packages instead of subprojects:

```text
src/main/scala/
  com/example/domain/
  com/example/application/
  com/example/infrastructure/
  com/example/interfaces/
src/test/scala/
  com/example/domain/
  com/example/application/
  com/example/infrastructure/support/   # fakes, fixtures
```

Rules:

- `domain` must not depend on doobie, Slick, http4s, Pekko, or JDBC drivers.
- Handlers and `main` wire adapters; use cases depend on port traits only (see
  [`application-wiring.md`](./application-wiring.md)).
- Keep DTOs next to the boundary that owns them (`interfaces`, `infrastructure`),
  not inside `domain`.

Example aggregate `build.sbt`:

```scala
lazy val domain = (project in file("domain"))
  .settings(
    name := "my-service-domain",
    libraryDependencies ++= Seq(
      "org.typelevel" %% "cats-core" % "2.12.0"
    )
  )

lazy val application = (project in file("application"))
  .dependsOn(domain)
  .settings(name := "my-service-application")

lazy val infrastructure = (project in file("infrastructure"))
  .dependsOn(domain, application)
  .settings(
    name := "my-service-infrastructure",
    libraryDependencies ++= Seq(
      "org.tpolecat" %% "doobie-core" % "1.0.0-RC9"
    )
  )

lazy val interfaces = (project in file("interfaces"))
  .dependsOn(application, infrastructure)
  .settings(name := "my-service-interfaces")
```

## Baseline Dependencies

Start from what the project already uses. When bootstrapping Kamae-style code,
these are common pairings:

```scala
libraryDependencies ++= Seq(
  "org.typelevel" %% "cats-core" % "2.12.0",
  "org.typelevel" %% "cats-effect" % "3.6.1",
  "io.circe" %% "circe-core" % "0.14.10",
  "org.typelevel" %% "log4cats-slf4j" % "2.7.0"
)

libraryDependencies ++= Seq(
  "org.scalameta" %% "munit" % "1.1.0" % Test,
  "org.scalacheck" %% "scalacheck" % "1.18.1" % Test
)
```

Load library guides from [`library-guides/`](./library-guides/) when the dependency
is present. Do not add libraries to `domain` solely because a guide exists.

Enable semanticdb in the root build when using scalafix (see template `build.sbt`):

```scala
ThisBuild / semanticdbEnabled := true
ThisBuild / semanticdbVersion := scalafixSemanticdb.revision
```

## Test Dependencies by Skill Topic

| Topic | Typical test dependencies | Notes |
| --- | --- | --- |
| Effectful use cases | `munit-cats-effect`, `cats-effect` (Test) | Test `IO`/`F[_]` use cases with controlled runtime |
| Property tests | `scalacheck`, `munit-scalacheck` | See [`property-based-tests.md`](./property-based-tests.md) |
| Compile-fail state safety | munit `compileErrors` | See [`test-data.md`](./test-data.md) |
| HTTP boundary tests | `http4s-munit`, `http4s-circe` (Test) | Test routes with fake use cases |
| Persistence integration | Testcontainers, doobie (Test) | Optional; keep most domain tests on fakes |
| Fake time | injected `Clock`/`Instant` trait | Avoid wall-clock flakiness |

Keep integration-test dependencies in the subproject that owns the adapter, not
in `domain`.

## Test Layers

Run tests at the lowest layer that can prove the invariant.

| Layer | What to test | I/O |
| --- | --- | --- |
| Domain unit | constructors, transitions, domain errors | None |
| Use case | orchestration with fake ports | None |
| Adapter unit | SQL mapping, DTO `Either` parsing, redaction | Fake or in-memory |
| API/integration | handler → use case → adapter | Test DB or container optional |
| Property | input-wide laws | None in the property body |

```bash
# Fast loop while editing domain code
sbt "project domain" test

# Use case tests with fakes
sbt "project application" test

# Full workspace before push
sbt scalafmtCheckAll "scalafixAll --check" compile Test/compile test doc
```

Domain and use-case tests should not require Docker. Reserve containers for
adapter integration tests that truly need PostgreSQL, Redis, or similar.

## Fake Ports and Test Fixtures

Inject fakes at the composition root used by tests. Build fixtures through the
same constructors as production code (see [`test-data.md`](./test-data.md)).

```scala
// application/src/test/scala/.../support/FakeTaxiRequestRepository.scala
final class FakeTaxiRequestRepository extends TaxiRequestRepository[Id]:
  val saved: mutable.ListBuffer[(EnRouteRequest, List[TaxiRequestEvent])] =
    mutable.ListBuffer.empty

  def saveAssigned(
      state: EnRouteRequest,
      events: List[TaxiRequestEvent],
      expectedVersion: Long
  ): Id[Either[AssignDriverError, Unit]] =
    Id.pure:
      saved += ((state, events))
      Right(())

def assignDriverUseCase(): AssignDriver[Id] =
  AssignDriver(FakeDriverResolver(), FakeTaxiRequestRepository())
```

Guidelines:

- Share fixture helpers under `src/test/scala/.../support/` or a dedicated test
  subproject.
- Use `assertEquals(obtained, expected)` on `Either` results; avoid `.get` except
  in helpers where failure means the fixture itself is wrong (document the invariant).
- Prefer one fake per port over a mega-mock that hides missing behavior.

## Optional Local Services

When adapter integration tests need real infrastructure, document one blessed
path for the team.

**docker-compose** (simple, checked into the repo):

```yaml
# compose.yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: my_service_test
    ports:
      - "5432:5432"
```

**Testcontainers** (self-contained in tests):

- Good for CI parity when compose is not available.
- Slower; scope to `infrastructure` integration tests only.

Load migration SQL or schema before tests. Never point local dev databases at
production credentials.

## Environment and Secrets

- Commit `.env.example` with non-secret placeholders; keep `.env` out of git.
- Read secrets through config loading at startup (`pureconfig`, `caliban` config,
  or platform env), not inside domain code.
- Use [`pii-protection.md`](./pii-protection.md) and [`library-guides/secrets.md`](./library-guides/secrets.md)
  before logging locally.

```bash
# .env.example
DATABASE_URL=jdbc:postgresql://localhost:5432/my_service_test
LOG_LEVEL=INFO
```

For local logging, SLF4J + logback with package-level loggers is enough.
OpenTelemetry exporters are optional during domain development.

## Local Check Loop

Align local commands with [`quality-gates.md`](./quality-gates.md) and
[`ci-setup.md`](./ci-setup.md). Use a fast path while editing and a full path
before opening a pull request.

**Fast path** (touched subprojects):

```bash
sbt scalafmtAll
sbt "project domain" "project application" compile Test/compile
sbt "project domain" "project application" test
```

**Full path** (pre-push):

```bash
sbt scalafmtCheckAll
sbt "scalafixAll --check"
sbt compile Test/compile test doc
```

When the project installs the kamae-scala skill, run the review probe on changed
Scala files before requesting review:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py \
  domain/src/main/scala application/src/main/scala
```

Treat probe output as review leads, not automatic failures. For first-time
project bootstrap, read [`local-validation.md`](./local-validation.md).

If the repo vendors `scripts/ci.sh` from templates, run `./scripts/ci.sh` for
the full skill-package loop.

## Editor and Agent Setup

**Metals (VS Code / Cursor)**

- Import the build after changing `build.sbt` (`Metals: Import build`).
- Enable format on save with `.scalafmt.conf` from templates.
- Use `-Xfatal-warnings` in dev builds when the team tolerates stricter local signal.

**Kamae skill**

- Load the `kamae-scala` skill when implementing or refactoring domain code.
- Add project rules under `.claude/rules/` or `.codex/rules/` for library
  preferences (see [`rules/README.md`](../../../rules/README.md)).
- Point agents at `build.sbt` and `project/*.sbt` first so library guides and
  topic files load correctly.

**Watch mode** (optional, sbt):

```bash
sbt ~"project domain" test
```

## Bootstrap Checklist for a New Domain Module

1. Create or identify the `domain` / `application` subproject (or package).
2. Add domain error ADTs and validated opaque ID companions.
3. Write unit tests for valid/invalid construction before adding use cases.
4. Define port traits shaped by one use case, not by the database schema.
5. Implement the use case with generic port parameters and fake adapters in tests.
6. Add DTO → domain `Either` parsing at the interface or infrastructure boundary.
7. Wire the use case in `main` or test bootstrap only.
8. Run the fast check loop; run the full path before push.
9. Run `kamae-scala-review` (or the probe + relevant checklists) on the diff.

For legacy codebases, climb the adoption ladder in
[`adoption.md`](./adoption.md) instead of restructuring everything first.

## When Local Setup Differs from CI

Document differences explicitly in the project README or `CONTRIBUTING.md`:

- Scala or Java versions tested in CI but not locally
- optional Docker-only integration jobs
- advisory review-probe or policy-check steps
- cross-build or platform-specific jobs

Developers should know which failures block merge and which are scheduled
advisory checks (see [`ci-setup.md`](./ci-setup.md)).

## Example Project

This skill repository's taxi-request example is the sbt subproject
`kamae-scala-taxi-request` under `skills/kamae-scala/examples/`. Run from the
repo root:

```bash
sbt "project taxiRequest" test
```

See [`development-setup.md`](./development-setup.md) for skill-package contributor
commands.
