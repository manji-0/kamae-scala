"""Scan Scala files for patterns that route Kamae Scala review checklists.

This script produces review leads, not findings. Run from the repository root:

    python3 skills/kamae-scala-review/scripts/review_probe.py path/to/changed.scala
    python3 skills/kamae-scala-review/scripts/review_probe.py src/ --json

Exit code is always 0 unless a path is missing or unreadable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
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
    "service-boundaries",
    "property-based-tests",
    "application-wiring",
    "aggregate-transactions",
    "tests",
)

PATTERN_RULES: list[tuple[str, re.Pattern[str], tuple[str, ...], tuple[str, ...]]] = [
    (
        "native-boundary",
        re.compile(r"\b(JNI|JNA|sun\.misc\.Unsafe|System\.loadLibrary|native def)\b"),
        ("jni-native-boundaries", "boundary"),
        (),
    ),
    (
        "throws-unsafe",
        re.compile(r"\b(throw new|throw |\?\?\?)\b|\.(get|head|last)\b"),
        ("error-handling", "state-transitions", "tests"),
        ("Suite.scala", "Test.scala", "/test/"),
    ),
    (
        "pii-terms",
        re.compile(
            r"\b(email|phone|password|secret|token|ssn|passport|address)\b",
            re.IGNORECASE,
        ),
        ("pii-protection", "logging-metrics"),
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
        (),
    ),
    (
        "codec-derive",
        re.compile(r"\b(Decoder\.derived|Encoder\.derived|Json\.format|Reads\.derived|Writes\.derived)\b"),
        ("boundary", "domain-modeling"),
        (),
    ),
    (
        "effect-risk",
        re.compile(r"\b(Future\.|IO\.|ZIO\.|Await\.result|blocking)\b"),
        ("application-wiring", "error-handling"),
        (),
    ),
    (
        "suppressions",
        re.compile(r"(@nowarn|scalafix:off|//\s*NOSONAR)"),
        ("fmt-lint",),
        (),
    ),
    (
        "logging",
        re.compile(r"\b(logger\.|log\.|LoggerFactory|StructuredLogging)\b"),
        ("logging-metrics", "pii-protection"),
        (),
    ),
]


@dataclass
class Lead:
    file: str
    line: int
    pattern: str
    snippet: str
    checklists: list[str] = field(default_factory=list)


def iter_scala_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix in {".scala", ".sc"} else []
    return sorted(p for p in path.rglob("*.scala") if p.is_file())


def should_skip_file(path: Path, skip_markers: tuple[str, ...]) -> bool:
    text = str(path).replace("\\", "/")
    return any(marker in text for marker in skip_markers)


def scan_file(path: Path) -> list[Lead]:
    text = path.read_text(encoding="utf-8")
    leads: list[Lead] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("//"):
            continue
        for pattern_name, regex, checklists, skip_markers in PATTERN_RULES:
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
                    )
                )
    return leads


def main() -> int:
    parser = argparse.ArgumentParser(description="Kamae Scala review probe")
    parser.add_argument("paths", nargs="+", help="Scala files or directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    all_leads: list[Lead] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"missing path: {path}", file=sys.stderr)
            return 1
        for scala_file in iter_scala_files(path):
            all_leads.extend(scan_file(scala_file))

    payload = {
        "leads": [
            {
                "file": lead.file,
                "line": lead.line,
                "pattern": lead.pattern,
                "snippet": lead.snippet,
                "checklists": lead.checklists,
            }
            for lead in all_leads
        ],
        "known_checklists": list(CHECKLISTS),
        "lead_count": len(all_leads),
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for lead in all_leads:
            checks = ", ".join(lead.checklists)
            print(f"{lead.file}:{lead.line} [{lead.pattern}] -> {checks}")
            print(f"  {lead.snippet}")
        print(f"\n{len(all_leads)} lead(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
