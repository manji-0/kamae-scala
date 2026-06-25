# Local Validation Setup

Use this guide when bootstrapping a new application repository from Kamae Scala templates.

## Copy Templates

Templates live under `skills/kamae-scala/assets/templates/`. Install them with:

```bash
python3 path/to/kamae-scala/skills/kamae-scala/scripts/apply_templates.py --target /path/to/repo
```

For skill/plugin repositories:

```bash
python3 skills/kamae-scala/scripts/apply_templates.py --ci skill-package --skill-package
```

Use `--dry-run` first. Existing files are skipped unless `--force` is set.

Installed templates include:

- `build.sbt`, `project/build.properties`, `project/plugins.sbt`
- `.scalafmt.conf`, `.scalafix.conf`, `.gitignore`
- `.github/workflows/ci.yml`
- `scripts/validate_package.py` and `scripts/ci.sh` for skill packages

Do not overwrite existing project files without review.

## First Validation Pass

```bash
sbt scalafmtCheckAll "scalafixAll --check" compile Test/compile test doc
```

For skill-installed copies, also run any `check_kamae_policy` script if your project adds one.

## Review Probe in Application Repos

Point the probe at domain and application source roots:

```bash
python3 path/to/kamae-scala/skills/kamae-scala-review/scripts/review_probe.py src/main/scala/domain --json
```

Treat output as review leads, not automatic findings.
