# Local Validation Setup

> **Audience:** Projects bootstrapping from skill templates (`gh skill`, `npx skills`, or a vendored kamae-scala copy). For this skill repository's dev workflow, read [`development-setup.md`](./development-setup.md).
> **When to read:** Bootstrapping local `build.sbt`, `project/build.properties`, `.gitignore`, GitHub Actions, or skill-package validation.
> **Related:** [`quality-gates.md`](./quality-gates.md) (canonical check commands), [`ci-setup.md`](./ci-setup.md), [`dev-environment.md`](./dev-environment.md).

## Use the Bundled Templates

When this skill is installed with `gh skill` or `npx skills`, repository-root files
such as `build.sbt`, `project/build.properties`, `.github/workflows/ci.yml`, and
`scripts/validate_package.py` are **not** installed automatically. Use the templates
under [`../assets/templates/`](../assets/templates/) when bootstrapping a project.

The quickest path is the bundled script:

```bash
python3 path/to/kamae-scala/skills/kamae-scala/scripts/apply_templates.py \
  --target /path/to/repo --ci backend --dry-run
python3 path/to/kamae-scala/skills/kamae-scala/scripts/apply_templates.py \
  --target /path/to/repo --ci backend
```

For skill/plugin repositories (like kamae-scala itself):

```bash
python3 skills/kamae-scala/scripts/apply_templates.py \
  --target . --ci skill-package --dry-run
python3 skills/kamae-scala/scripts/apply_templates.py \
  --target . --ci skill-package
```

The script does not overwrite existing files unless `--force` is set. Use
`--dry-run` first when applying it to an existing repository.

### Template mapping

| Template | Target | Purpose |
| --- | --- | --- |
| [`build.sbt`](../assets/templates/build.sbt) | `build.sbt` | Scala 3 defaults, semanticdb, baseline deps |
| [`project-build.properties`](../assets/templates/project-build.properties) | `project/build.properties` | sbt version pin |
| [`project-plugins.sbt`](../assets/templates/project-plugins.sbt) | `project/plugins.sbt` | scalafmt + scalafix |
| [`scalafmt.conf`](../assets/templates/scalafmt.conf) | `.scalafmt.conf` | formatting |
| [`scalafix.conf`](../assets/templates/scalafix.conf) | `.scalafix.conf` | lint rules |
| [`gitignore`](../assets/templates/gitignore) | `.gitignore` | sbt / Metals / IDE ignores |
| [`github-ci.yml`](../assets/templates/github-ci.yml) | `.github/workflows/ci.yml` | application CI (sbt + advisory probe) |
| [`github-ci-skill-package.yml`](../assets/templates/github-ci-skill-package.yml) | `.github/workflows/ci.yml` | skill repo CI |
| [`validate_package.py`](../assets/templates/validate_package.py) | `scripts/validate_package.py` | skill package smoke test |
| [`ci.sh`](../assets/templates/ci.sh) | `scripts/ci.sh` | local CI reproduction |

Adjust `organization`, `name`, library versions, and subproject layout before
committing. For application repositories, evolve toward the layout in
[`dev-environment.md`](./dev-environment.md#recommended-module-layout).

After copying CI templates, replace `path/to/kamae-scala` in the review-probe
step with the installed skill path (or a vendored copy in the repo).

## First-Time Toolchain Setup

Install Java 17+ and sbt 1.10+:

```bash
java -version
sbt --version
```

If sbt is missing, install via [Coursier](https://get.coursier.io/) or your OS
package manager, then verify:

```bash
sbt --version
```

If the project does not yet have a `build.sbt`, run the template script first,
then:

```bash
sbt compile
sbt test
```

## First Validation Pass

After bootstrap, run the baseline commands from [`quality-gates.md`](./quality-gates.md):

```bash
sbt scalafmtCheckAll
sbt "scalafixAll --check"
sbt compile Test/compile test doc
```

For skill/plugin repositories, also run:

```bash
python3 scripts/validate_package.py
./scripts/ci.sh
```

Optional policy scripts (team-specific, not bundled): if you add a
`scripts/check_kamae_policy.py` or similar, run it here and wire it into CI when
the team wants a hard gate.

## Review Probe Sanity Check

After bootstrapping, run the bundled review probe on domain and application
source roots to catch common Kamae stance issues before they reach review:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py \
  domain/src/main/scala application/src/main/scala --json
```

For single-module layouts:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py \
  src/main/scala/com/example/domain \
  src/main/scala/com/example/application \
  --json
```

The probe is advisory by default. Treat its output as review leads for throws/unsafe
gets, codec derives, PII terms, persistence patterns, Scaladoc gaps, and suggested
sbt commands — not as a failing gate unless your team wires it that way.

Text output with a lead limit:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py \
  src/main/scala --limit 30
```

## Multi-Module Bootstrap

When splitting a monolith into Kamae layers:

1. Copy base templates into the repo root.
2. Add subprojects in `build.sbt` (`domain`, `application`, `infrastructure`,
   `interfaces`) with `dependsOn` edges as in [`dev-environment.md`](./dev-environment.md).
3. Move packages incrementally; keep compiling after each move:
   `sbt "project domain" compile`.
4. Add fake ports under `application/src/test/scala/.../support/` before adapter
   work (see [`test-data.md`](./test-data.md)).
5. Run the fast loop on touched subprojects, then the full loop before push.

Do not copy production SQL dumps or `.env` files into the repository during
bootstrap.

## Local Check Loop

After bootstrap:

| When | Commands |
| --- | --- |
| While editing domain | `sbt "project domain" test`, probe on changed paths |
| Pre-push | `sbt scalafmtCheckAll "scalafixAll --check" compile Test/compile test doc` |
| Skill repo | `./scripts/ci.sh` |

For crate layout, fake ports, test layers, editor setup, and secrets, read
[`dev-environment.md`](./dev-environment.md).

## Verify CI Parity

1. Push a branch and confirm GitHub Actions runs the same sbt steps as your local
   full path.
2. If the workflow includes an advisory probe step, confirm the skill path is
   correct (broken paths fail silently with `continue-on-error: true`).
3. Document any optional jobs (integration tests, cross-Scala builds) in
   `CONTRIBUTING.md` so local developers know what is merge-blocking.
