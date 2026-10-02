#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"

REPORT_PATH="$ROOT/report.json"

run_probe() {
  local target="$1"
  TARGET="$target" REPORT_PATH="$REPORT_PATH" python3 <<'PY'
import json, os
from pathlib import Path
from probe import probe
from servers import FIXTURES

target = os.environ["TARGET"]
report_path = Path(os.environ["REPORT_PATH"])
server = FIXTURES[target]
report = probe(server)
payload = report.to_dict()

existing = []
if report_path.exists():
    try:
        existing = json.loads(report_path.read_text())
        if not isinstance(existing, list):
            existing = []
    except json.JSONDecodeError:
        existing = []
existing = [r for r in existing if r.get("target") != target]
existing.append(payload)
report_path.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n")
print(json.dumps(payload, sort_keys=True))
PY
}

jq_field() {
  python3 -c 'import json,sys; o=json.loads(sys.argv[1]); print(o'"$2"')' "$1"
}

pass_count=0
fail_count=0

rm -f "$REPORT_PATH"

echo "=== McpWireEcho demo ==="
echo "Offering protocolVersion 2026-07-28 to three fixtures."
echo

# PATH A: old_only
echo "PATH A (old_only): BEFORE class=unset"
a1=$(run_probe old_only)
echo "PATH A AFTER=$a1"
a_class=$(jq_field "$a1" '["class"]')
a_echo=$(jq_field "$a1" '["initializeEcho"]')
a_disc_ok=$(jq_field "$a1" '["discover"]["ok"]')
a_err=$(jq_field "$a1" '["discover"]["errorCode"]')
if [[ "$a_class" == "old_only" && "$a_echo" == "2025-06-18" && "$a_disc_ok" == "False" && "$a_err" == "-32601" ]]; then
  echo "PATH A (old_only): PASS"
  pass_count=$((pass_count + 1))
else
  echo "PATH A (old_only): FAIL (class=$a_class echo=$a_echo discover.ok=$a_disc_ok errorCode=$a_err)"
  fail_count=$((fail_count + 1))
fi
echo

# PATH B: echo_negotiator
echo "PATH B (echo_negotiator): BEFORE class=unset"
b1=$(run_probe echo_negotiator)
echo "PATH B AFTER=$b1"
b_class=$(jq_field "$b1" '["class"]')
b_echo=$(jq_field "$b1" '["initializeEcho"]')
b_disc_ok=$(jq_field "$b1" '["discover"]["ok"]')
b_err=$(jq_field "$b1" '["discover"]["errorCode"]')
if [[ "$b_class" == "echo_negotiator" && "$b_echo" == "2026-07-28" && "$b_disc_ok" == "False" && "$b_err" == "-32601" ]]; then
  echo "PATH B (echo_negotiator): PASS"
  pass_count=$((pass_count + 1))
else
  echo "PATH B (echo_negotiator): FAIL (class=$b_class echo=$b_echo discover.ok=$b_disc_ok errorCode=$b_err)"
  fail_count=$((fail_count + 1))
fi
echo

# PATH C: discover_ok
echo "PATH C (discover_ok): BEFORE class=unset"
c1=$(run_probe discover_ok)
echo "PATH C AFTER=$c1"
c_class=$(jq_field "$c1" '["class"]')
c_disc_ok=$(jq_field "$c1" '["discover"]["ok"]')
c_has=$(python3 -c 'import json,sys; print("2026-07-28" in json.loads(sys.argv[1])["discover"]["supportedVersions"])' "$c1")
if [[ "$c_class" == "discover_ok" && "$c_disc_ok" == "True" && "$c_has" == "True" ]]; then
  echo "PATH C (discover_ok): PASS"
  pass_count=$((pass_count + 1))
else
  echo "PATH C (discover_ok): FAIL (class=$c_class discover.ok=$c_disc_ok has_offered=$c_has)"
  fail_count=$((fail_count + 1))
fi
echo

echo "Wrote $REPORT_PATH"
echo "SUMMARY: $pass_count passed, $fail_count failed"
if [[ "$fail_count" -ne 0 || "$pass_count" -ne 3 ]]; then
  exit 1
fi
echo "ALL CLAIMS PASSED"
exit 0
