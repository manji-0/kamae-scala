# Skill Repository Setup

This guide is for contributors working on the `kamae-scala` skill package itself.

## Repository Goals

- Keep skill Markdown, manifests, and examples valid via `scripts/validate_package.py`
- Keep the taxi-request example compiling and tested via sbt
- Keep review probe smoke tests runnable without external services

## Contributor Loop

```bash
./scripts/ci.sh
```

When changing `skills/kamae-scala-review/scripts/review_probe.py`, run the probe
unit tests (included in `./scripts/ci.sh`):

```bash
python3 -m unittest discover -s skills/kamae-scala-review/scripts -p 'review_probe_test.py' -v
```

## Adding Topics

Follow the checklist in [`../../../DEVELOPMENT.md`](../../../DEVELOPMENT.md#working-on-skills).

## Templates

Starter templates for application repos live under [`../assets/templates/`](../assets/templates/). Installed skills include files under the skill directory, but do not reliably install this repository's root `build.sbt`, `.github/`, or `scripts/`.

Install templates into a target repository with [`../scripts/apply_templates.py`](../scripts/apply_templates.py):

```bash
python3 skills/kamae-scala/scripts/apply_templates.py --target /path/to/repo --dry-run
python3 skills/kamae-scala/scripts/apply_templates.py --ci skill-package --skill-package --target /path/to/skill-repo
```
