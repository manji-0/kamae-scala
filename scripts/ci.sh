#!/usr/bin/env bash
# Run the same checks as .github/workflows/ci.yml locally.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Package validation"
python3 scripts/validate_package.py

echo "==> Review probe smoke test"
python3 skills/kamae-scala-review/scripts/review_probe.py \
  skills/kamae-scala/examples/src/main/scala \
  --json

echo "==> Review probe tests"
python3 -m unittest discover -s skills/kamae-scala-review/scripts -p 'review_probe_test.py' -v

echo "==> Scala formatting"
sbt scalafmtCheckAll

echo "==> Scala scalafix"
sbt "scalafixAll --check"

echo "==> Scala compile"
sbt "project taxiRequest" compile Test/compile

echo "==> Scala tests"
sbt "project taxiRequest" test

echo "==> Scaladoc"
sbt "project taxiRequest" doc

echo "All CI checks passed."
