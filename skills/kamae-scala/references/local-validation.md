# Local Validation Setup

Use this guide when bootstrapping a new application repository from Kamae Scala templates.

## Copy Templates

Templates live under `skills/kamae-scala/assets/templates/`. Copy or merge:

- `build.sbt`
- `.scalafmt.conf`
- `.github/workflows/ci.yml`

Do not overwrite existing project files without review.

## First Validation Pass

```bash
sbt scalafmtCheckAll
sbt test
```

For skill-installed copies, also run any `check_kamae_policy` script if your project adds one.

## Review Probe in Application Repos

Point the probe at domain and application source roots:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py src/main/scala/domain --json
```

Treat output as review leads, not automatic findings.
