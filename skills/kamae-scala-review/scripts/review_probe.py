"""Scan Scala files for patterns that route Kamae Scala review checklists.

This script produces review leads, not findings. Run from the repository root:

    python3 skills/kamae-scala-review/scripts/review_probe.py path/to/changed.scala
    python3 skills/kamae-scala-review/scripts/review_probe.py src/ --json
    python3 skills/kamae-scala-review/scripts/review_probe.py src/ --limit 20

Exit code is always 0 unless a path is missing or unreadable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

CHECKLISTS = (
    "domain-modeling",
    "state-transitions",
    "error-handling",
    "boundary",
    "pii-protection",
    "logging-metrics",
    "jni-native-boundaries",
    "fmt-lint",
    "scaladoc",
    "ci-setup",
    "dev-environment",
    "persistence-events",
    "stream-continuous-queries",
    "domain-macros",
    "orm-adapters",
    "service-boundaries",
    "property-based-tests",
    "application-wiring",
    "aggregate-transactions",
    "tests",
)

SKIP_DIRS = frozenset(
    {".git", ".dagayn", "target", "node_modules", ".venv", "venv", "project", ".bsp", ".metals"}
)

SUGGESTED_COMMANDS = (
    "sbt scalafmtCheckAll",
    'sbt "scalafixAll --check"',
    "sbt compile Test/compile test doc",
)

PATTERN_RULES: list[tuple[str, re.Pattern[str], tuple[str, ...], str, tuple[str, ...]]] = [
    (
        "native-boundary",
        re.compile(r"\b(JNI|JNA|sun\.misc\.Unsafe|System\.loadLibrary|native def)\b"),
        ("jni-native-boundaries", "boundary"),
        "Inspect JNI/native containment and safe wrapper boundaries.",
        (),
    ),
    (
        "throws-unsafe",
        re.compile(r"\b(throw new|throw |\?\?\?)\b|\.(get|head|last)\b"),
        ("error-handling", "state-transitions", "tests"),
        "Confirm typed errors or proven invariants; avoid throws/unsafe gets in domain code.",
        ("Suite.scala", "Test.scala", "/test/"),
    ),
    (
        "pii-terms",
        re.compile(
            r"\b(email|phone|password|secret|token|ssn|passport|address|api_key|credential)\b",
            re.IGNORECASE,
        ),
        ("pii-protection", "logging-metrics"),
        "Check redaction, log exposure, and narrow secret access.",
        (),
    ),
    (
        "stream-feeds",
        re.compile(r"\b(fs2\.|ZStream|Pekko|Source\.|outbox|projection|subscribe)\b"),
        ("stream-continuous-queries", "persistence-events", "service-boundaries"),
        "Check cursors, backpressure, idempotency, and CQRS boundaries.",
        (),
    ),
    (
        "orm-adapters",
        re.compile(r"\b(doobie|slick|quill|ConnectionIO|DBIO|Transactor|TableQuery)\b"),
        ("orm-adapters", "boundary", "persistence-events"),
        "Check row DTO mapping, optimistic locking, and transaction scope.",
        (),
    ),
    (
        "persistence-events",
        re.compile(
            r"\b(outbox|repository|transaction|idempoten|optimistic|event_version|"
            r"TaxiRequestEvent|DomainEvent|saveAssigned)\b",
            re.I,
        ),
        ("persistence-events", "aggregate-transactions", "tests"),
        "Check atomicity, idempotency, DB constraints, and event versioning.",
        (),
    ),
    (
        "codec-derive",
        re.compile(
            r"\b(Decoder\.derived|Encoder\.derived|Json\.format|Reads\.derived|Writes\.derived|"
            r"derives\s+(Decoder|Encoder|Codec|Read|Write)|Configuration\.derive|inline def|macro )"
        ),
        ("domain-macros", "boundary", "domain-modeling"),
        "Check DTO/domain separation and generated validation.",
        (),
    ),
    (
        "effect-risk",
        re.compile(r"\b(Future\.|IO\.|ZIO\.|Await\.result|blocking)\b"),
        ("application-wiring", "error-handling"),
        "Check effect boundaries, lost failures, and blocking in async paths.",
        (),
    ),
    (
        "property-test",
        re.compile(r"\b(forAll|Prop\.|Arbitrary|Gen\.|ScalaCheck|PropertyCheck)\b"),
        ("property-based-tests", "tests"),
        "Check lawful generators, explicit properties, and no live I/O.",
        ("Suite.scala", "Test.scala", "/test/"),
    ),
    (
        "service-boundary",
        re.compile(
            r"\b(grpc|protobuf|SchemaRegistry|CircuitBreaker|circuitBreaker|idempotencyKey)\b",
            re.I,
        ),
        ("service-boundaries", "boundary", "persistence-events"),
        "Check DTO conversion, schema evolution, and adapter resilience.",
        (),
    ),
    (
        "error-chain-log",
        re.compile(r"\b(printStackTrace|logger\.error\([^)]*exception|log\.error\([^)]*ex)\b", re.I),
        ("logging-metrics", "error-handling"),
        "Check single authoritative log line and bounded error detail.",
        (),
    ),
    (
        "suppressions",
        re.compile(r"(@nowarn|scalafix:off|//\s*NOSONAR)"),
        ("fmt-lint",),
        "Check whether suppression is narrow and justified.",
        (),
    ),
    (
        "logging",
        re.compile(r"\b(logger\.|log\.|LoggerFactory|StructuredLogging)\b"),
        ("logging-metrics", "pii-protection"),
        "Check structured fields, PII redaction, and metric cardinality.",
        (),
    ),
]

PUBLIC_DEF_RE = re.compile(
    r"^\s*(?:@\w+\s+)*(?:override\s+)?(?:final\s+)?(?:sealed\s+)?(?:abstract\s+)?"
    r"(?:(?:case\s+)?(?:class|object|trait|enum)|def)\s+(\w+)"
)
PRIVATE_PREFIX_RE = re.compile(r"^\s*(private|protected|\[this\])")
EITHER_SIGNATURE_RE = re.compile(r"\bEither\[")


@dataclass
class Lead:
    file: str
    line: int
    pattern: str
    snippet: str
    checklists: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class PublicItem:
    file: str
    line: int
    name: str
    signature: str
    has_doc: bool
    returns_either: bool
    has_throws_doc: bool


@dataclass
class ProbeSummary:
    leads_by_category: dict[str, int]
    leads_by_checklist: dict[str, int]
    public_items: int
    public_items_missing_docs: int
    either_items_missing_throws: int


@dataclass
class ProbeOutput:
    scanned_files: list[str]
    leads: list[Lead]
    public_items: list[PublicItem]
    summary: ProbeSummary
    known_checklists: list[str]
    suggested_commands: list[str]
    lead_count: int


def is_generated(path: Path, text: str) -> bool:
    rel = str(path).lower()
    head = "\n".join(text.splitlines()[:8]).lower()
    return (
        "generated" in rel
        or "bindings" in rel
        or "@generated" in head
        or "automatically generated" in head
        or "do not edit" in head
    )


def collect_scala_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix in {".scala", ".sc"} else []
    files: list[Path] = []
    for root, dirs, filenames in os.walk(path):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(".scala") or name.endswith(".sc"):
                files.append(Path(root) / name)
    return files


def should_skip_file(path: Path, skip_markers: tuple[str, ...]) -> bool:
    text = str(path).replace("\\", "/")
    return any(marker in text for marker in skip_markers)


def doc_block_above(lines: list[str], index: int) -> str:
    j = index - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j < 0 or not lines[j].strip().endswith("*/"):
        return ""
    parts: list[str] = []
    while j >= 0:
        parts.append(lines[j])
        if "/**" in lines[j]:
            return "\n".join(reversed(parts))
        stripped = lines[j].strip()
        if stripped and not stripped.startswith("*") and "*/" not in stripped:
            return ""
        j -= 1
    return ""


def has_scaladoc_above(lines: list[str], index: int) -> bool:
    return bool(doc_block_above(lines, index))


def scan_public_items(path: Path, text: str) -> list[PublicItem]:
    lines = text.splitlines()
    items: list[PublicItem] = []
    for line_no, line in enumerate(lines, start=1):
        if PRIVATE_PREFIX_RE.match(line):
            continue
        match = PUBLIC_DEF_RE.match(line)
        if not match:
            continue
        name = match.group(1)
        if name in {"given", "extension", "apply", "unapply"}:
            continue
        doc = doc_block_above(lines, line_no - 1)
        has_doc = bool(doc)
        signature = line.strip()[:160]
        returns_either = bool(EITHER_SIGNATURE_RE.search(line))
        if not returns_either and line.rstrip().endswith("="):
            body_start = line_no
            for peek in range(line_no, min(line_no + 3, len(lines))):
                if EITHER_SIGNATURE_RE.search(lines[peek]):
                    returns_either = True
                    break
                if lines[peek].strip().startswith("="):
                    body_start = peek + 1
                    break
            if not returns_either and body_start < len(lines):
                returns_either = bool(EITHER_SIGNATURE_RE.search(lines[body_start]))
        has_throws_doc = "@throws" in doc if has_doc else False
        items.append(
            PublicItem(
                file=str(path),
                line=line_no,
                name=name,
                signature=signature,
                has_doc=has_doc,
                returns_either=returns_either,
                has_throws_doc=has_throws_doc,
            )
        )
    return items


def scan_file(path: Path) -> tuple[list[Lead], list[PublicItem]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return (
            [
                Lead(
                    file=str(path),
                    line=0,
                    pattern="read-error",
                    snippet=str(exc)[:200],
                    checklists=["tests"],
                    note="Could not read file for probe scan.",
                )
            ],
            [],
        )

    if is_generated(path, text):
        return [], []

    lines = text.splitlines()
    leads: list[Lead] = []
    for line_no, line in enumerate(lines, start=1):
        if line.strip().startswith("//"):
            continue
        for pattern_name, regex, checklists, note, skip_markers in PATTERN_RULES:
            if skip_markers and should_skip_file(path, skip_markers):
                continue
            if regex.search(line):
                leads.append(
                    Lead(
                        file=str(path),
                        line=line_no,
                        pattern=pattern_name,
                        snippet=line.strip()[:200],
                        checklists=list(checklists),
                        note=note,
                    )
                )
    return leads, scan_public_items(path, text)


def build_summary(leads: list[Lead], public_items: list[PublicItem]) -> ProbeSummary:
    by_category: Counter[str] = Counter(lead.pattern for lead in leads)
    by_checklist: Counter[str] = Counter(
        checklist for lead in leads for checklist in lead.checklists
    )
    missing_docs = sum(1 for item in public_items if not item.has_doc)
    either_missing_throws = sum(
        1
        for item in public_items
        if item.returns_either and item.has_doc and not item.has_throws_doc
    )
    return ProbeSummary(
        leads_by_category=dict(sorted(by_category.items())),
        leads_by_checklist=dict(sorted(by_checklist.items())),
        public_items=len(public_items),
        public_items_missing_docs=missing_docs,
        either_items_missing_throws=either_missing_throws,
    )


def probe_paths(paths: list[Path]) -> ProbeOutput:
    scanned: list[str] = []
    all_leads: list[Lead] = []
    all_public: list[PublicItem] = []
    for raw in paths:
        if not raw.exists():
            continue
        for scala_file in collect_scala_files(raw):
            scanned.append(str(scala_file))
            leads, public_items = scan_file(scala_file)
            all_leads.extend(leads)
            all_public.extend(public_items)
    summary = build_summary(all_leads, all_public)
    return ProbeOutput(
        scanned_files=sorted(scanned),
        leads=all_leads,
        public_items=all_public,
        summary=summary,
        known_checklists=list(CHECKLISTS),
        suggested_commands=list(SUGGESTED_COMMANDS),
        lead_count=len(all_leads),
    )


def render_text(output: ProbeOutput, limit: int) -> str:
    limit = max(1, limit)
    lines = [
        "# kamae-scala Review Probe",
        "",
        "These are review leads, not findings. Confirm reachability, invariants, and project conventions before reporting.",
        "",
        f"Scanned Scala files: {len(output.scanned_files)}",
        "",
        "## Suggested Commands",
    ]
    for command in output.suggested_commands:
        lines.append(f"- `{command}`")

    lines.extend(
        [
            "",
            "## Summary",
            f"- leads_by_category: {output.summary.leads_by_category}",
            f"- leads_by_checklist: {output.summary.leads_by_checklist}",
            f"- public_items: {output.summary.public_items}",
            f"- public_items_missing_docs: {output.summary.public_items_missing_docs}",
            f"- either_items_missing_throws: {output.summary.either_items_missing_throws}",
            "",
            "## Leads",
        ]
    )
    if not output.leads:
        lines.append("- No pattern leads found.")
    else:
        for lead in output.leads[:limit]:
            checks = ", ".join(lead.checklists)
            lines.append(
                f"- `{lead.file}:{lead.line}` [{lead.pattern} -> {checks}] {lead.snippet}\n  {lead.note}"
            )
        if len(output.leads) > limit:
            lines.append(f"- Truncated {len(output.leads) - limit} additional lead(s). Use `--limit` to show more.")

    missing_docs = [item for item in output.public_items if not item.has_doc]
    either_without_throws = [
        item
        for item in output.public_items
        if item.returns_either and item.has_doc and not item.has_throws_doc
    ]
    lines.extend(["", "## Scaladoc Leads"])
    for title, items, note in [
        ("Public items missing Scaladoc", missing_docs, "Review whether this public API needs a domain contract."),
        (
            "Documented Either APIs missing @throws",
            either_without_throws,
            "Callers may need error semantics.",
        ),
    ]:
        lines.append(f"### {title}")
        if not items:
            lines.append("- None.")
        else:
            for item in items[:limit]:
                lines.append(f"- `{item.file}:{item.line}` {item.signature}\n  {note}")
            if len(items) > limit:
                lines.append(f"- Truncated {len(items) - limit} additional item(s).")
    return "\n".join(lines)


def output_to_json(output: ProbeOutput) -> str:
    payload = {
        "scanned_files": output.scanned_files,
        "leads": [asdict(lead) for lead in output.leads],
        "public_items": [asdict(item) for item in output.public_items],
        "summary": asdict(output.summary),
        "known_checklists": output.known_checklists,
        "suggested_commands": output.suggested_commands,
        "lead_count": output.lead_count,
    }
    return json.dumps(payload, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Kamae Scala review probe")
    parser.add_argument("paths", nargs="+", help="Scala files or directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--limit", type=int, default=40, help="Max leads/items in text output")
    args = parser.parse_args()

    input_paths = [Path(raw) for raw in args.paths]
    for path in input_paths:
        if not path.exists():
            print(f"missing path: {path}", file=sys.stderr)
            return 1

    output = probe_paths(input_paths)
    if args.json:
        print(output_to_json(output))
    else:
        print(render_text(output, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
