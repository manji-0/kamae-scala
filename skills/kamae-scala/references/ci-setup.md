# CI Setup

> **When to read:** When adding or changing GitHub Actions workflows for a Kamae-style Scala project or this skill repository.
> **Related:** [`quality-gates.md`](./quality-gates.md), [`development-setup.md`](./development-setup.md)

## Skill Repository Workflow

The `kamae-scala` repository runs two jobs in [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml):

| Job | Purpose |
| --- | --- |
| `package` | `validate_package.py`, review-probe smoke test, Python syntax checks |
| `scala` | `scalafmtCheckAll`, `scalafixAll --check`, compile, test, Scaladoc for `taxiRequest` |

The Scala job depends on `package` so manifest/link failures fail fast without downloading the JVM toolchain.

Local reproduction:

```bash
./scripts/ci.sh
```

Or step by step:

```bash
python3 scripts/validate_package.py
python3 skills/kamae-scala-review/scripts/review_probe.py skills/kamae-scala/examples/src/main/scala --json
sbt scalafmtCheckAll "scalafixAll --check" "project taxiRequest" compile Test/compile test doc
```

## Required Reviewer Checks

CI for Kamae-style Scala application projects should include, at minimum:

1. `sbt scalafmtCheckAll`
2. `sbt "scalafixAll --check"` when scalafix rules are configured
3. `sbt compile Test/compile` with `-Xfatal-warnings` when practical
4. `sbt test`
5. `sbt doc` when the project publishes libraries or documents public domain APIs

Skill/plugin repositories should also run:

```bash
python3 scripts/validate_package.py
python3 skills/kamae-scala-review/scripts/review_probe.py <domain-or-example-path> --json
```

## Representative Matrix

Match CI to the stacks you use:

| Stack present | Add |
| --- | --- |
| Circe / JSON APIs | boundary parsing tests |
| doobie / slick | integration tests or testcontainers job |
| http4s / pekko | route/handler contract tests |
| ZIO / Cats Effect | separate test config if runtime layers differ |

## Workflow Hygiene

- Pin Java to an LTS release (17 or 21) and enable `cache: sbt` in `actions/setup-java`.
- Use `sbt/setup-sbt@v1` so CI uses the sbt version from `project/build.properties`.
- Add `concurrency` with `cancel-in-progress: true` on pull requests.
- Keep `permissions: contents: read` unless a job needs more.

## Risk-Tied Safety Jobs

Add dedicated jobs when the codebase uses:

- JNI or native libraries
- crypto/token handling
- migration scripts that touch production-shaped data

## Application Template

See [`../assets/templates/github-ci.yml`](../assets/templates/github-ci.yml) for a starter workflow when bootstrapping application repos.
