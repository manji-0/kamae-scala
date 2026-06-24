# kamae-scala

_Kamae (構え) - a stance of readiness._

Scala skills for designing and reviewing robust server-side domain code. This is a Scala-oriented sibling of [`kamae-rs`](https://github.com/manji-0/kamae-rs): it keeps the same thin-skill, topic-guide, and review-checklist shape while translating the principles into Scala 3 idioms.

## Provided Skills

### `kamae-scala`

Use when implementing, modifying, refactoring, or fixing Scala domain models, use cases, repositories, state transitions, boundary DTO parsing, typed errors, PII handling, or validation/review-adjacent code.

Core principles:

- Model domain meaning with opaque types, value classes, sealed traits, and validated constructors.
- Make invalid state transitions fail at compile time where practical.
- Use `Either[DomainError, T]` (or effect types with typed failures) with domain-specific error ADTs.
- Convert external data through DTO/row/config case classes before constructing domain types.
- Wire use cases through small ports and inject adapters at the composition root.
- Keep aggregate changes inside one transaction boundary per use case when practical.
- Keep PII and secrets behind redacting wrappers.
- Keep JNI/native interop out of domain logic by default; when unavoidable, hide it behind small safe APIs with documented invariants.
- Keep scalafmt and scalafix gates clean for touched Scala code; treat suppressions as narrow, justified design decisions.
- Use Scaladoc to document public domain contracts: invariants, errors, transition rules, and examples.
- Align CI with review assumptions: package validation, format, lint, tests, Scaladoc, and risk-tied native/security jobs.

### `kamae-scala-review`

Use during Scala code review. It walks severity-tagged checklist files for domain modeling, transitions, error handling, application wiring, aggregate transactions, boundary validation, PII protection, JNI/native boundaries, formatting/lints, Scaladoc, CI setup, persistence/events, service boundaries, and tests.

## Packaging

The package includes both Claude and Codex manifests:

- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` describe the Claude plugin package.
- `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` describe the Codex plugin package and point Codex at `./skills/`.

Run `python3 scripts/validate_package.py` before publishing or sharing a package archive. The smoke test validates JSON manifests, skill frontmatter, relative Markdown links, manifest skill paths, and library-guide references.

CI runs package validation plus Scala example checks in [`.github/workflows/ci.yml`](./.github/workflows/ci.yml). Reproduce locally with `./scripts/ci.sh`.

## Review Tools

Run `python3 skills/kamae-scala-review/scripts/review_probe.py <path>` to collect review leads from Scala files before walking the review checklist. The probe is intentionally conservative: it highlights patterns for human/agent inspection and does not produce findings by itself.

For implementing and testing domain code in application projects, see [`skills/kamae-scala/references/dev-environment.md`](./skills/kamae-scala/references/dev-environment.md).

## Customization

Rules live under `.claude/rules/`, `.codex/rules/`, user-level rule directories, or this repo's `rules/defaults/`. See [`rules/README.md`](./rules/README.md).

## Repository Layout

```text
skills/kamae-scala/          Implementation guidance
skills/kamae-scala-review/   Review procedure and checklist
rules/                       Project/user override format
```

## License

MIT
