#!/usr/bin/env bash
# merge_when_green.sh — merge a PR only after its checks have actually passed.
#
# WHY THIS EXISTS. `gh pr merge --auto` waits for *required* status checks. If a
# repo has no branch protection, nothing is required, so --auto merges instantly
# and the PR gates nothing. That was live here for a whole session: every PR
# merged ~90 s before its own CI finished. They all happened to pass, so it
# looked fine.
#
# The server-side fix is branch protection, which needs repo-admin rights. This
# script is the half that does NOT need anyone's permission: it does the waiting
# and the verifying itself, in the client, and refuses to merge otherwise.
#
#   *** IT FAILS CLOSED ON "NO CHECKS FOUND." ***
#
# That is the whole point. Zero checks is not "nothing to worry about", it is
# exactly the condition that produced the bug — an absent gate reads identically
# to a passed one unless you treat absence as failure.
#
# This is WEAKER than branch protection and does not replace it: it only governs
# merges that go through this script. A session calling `gh pr merge` directly
# still bypasses it. See docs/todo/2026-08-12-enable-branch-protection-on-main.md.
#
# USAGE
#   tools/merge_when_green.sh <pr-number> [--timeout SECONDS] [--poll SECONDS]
#   tools/merge_when_green.sh --selftest
#
# EXIT  0 merged   1 not merged (checks failed, absent, or timed out)   2 usage/env

set -uo pipefail

TIMEOUT=1800
POLL=20
PR=""

usage() { sed -n '2,30p' "$0"; exit 2; }

# ---------------------------------------------------------------- self-test
# Proves the decision logic can fire in every direction, without touching the
# network: verdict() is pure, so feed it the JSON shapes gh actually returns.
verdict() {
  # stdin: JSON array of {state|conclusion, name}. Echoes PASS/FAIL/PENDING/NONE.
  python3 -c '
import json,sys
try: rollup=json.load(sys.stdin)
except Exception: print("NONE"); sys.exit()
runs=[c for c in rollup if c.get("__typename")!="StatusContext" or True]
if not runs: print("NONE"); sys.exit()
def norm(c):
    # check runs use status/conclusion; legacy statuses use state
    if c.get("status") and c.get("status")!="COMPLETED": return "PENDING"
    v=(c.get("conclusion") or c.get("state") or "").upper()
    if v in ("SUCCESS","NEUTRAL","SKIPPED"): return "PASS"
    if v in ("","PENDING","EXPECTED","QUEUED","IN_PROGRESS"): return "PENDING"
    return "FAIL"
s=[norm(c) for c in runs]
print("FAIL" if "FAIL" in s else ("PENDING" if "PENDING" in s else "PASS"))
'
}

selftest() {
  local fails=0
  t() { # name expected json
    local got; got=$(printf '%s' "$3" | verdict)
    if [ "$got" = "$2" ]; then printf '  ok   %-40s\n' "$1"
    else printf '  FAIL %-40s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  t "all success -> PASS"      PASS    '[{"status":"COMPLETED","conclusion":"SUCCESS","name":"a"},{"status":"COMPLETED","conclusion":"SUCCESS","name":"b"}]'
  t "one failure -> FAIL"      FAIL    '[{"status":"COMPLETED","conclusion":"SUCCESS","name":"a"},{"status":"COMPLETED","conclusion":"FAILURE","name":"b"}]'
  t "still running -> PENDING" PENDING '[{"status":"IN_PROGRESS","conclusion":null,"name":"a"}]'
  t "queued -> PENDING"        PENDING '[{"status":"QUEUED","conclusion":null,"name":"a"}]'
  t "EMPTY -> NONE (the bug)"  NONE    '[]'
  t "garbage -> NONE"          NONE    'not json'
  t "skipped counts as pass"   PASS    '[{"status":"COMPLETED","conclusion":"SKIPPED","name":"a"}]'
  t "cancelled -> FAIL"        FAIL    '[{"status":"COMPLETED","conclusion":"CANCELLED","name":"a"}]'
  t "legacy state success"     PASS    '[{"state":"SUCCESS","name":"a"}]'
  t "legacy state failure"     FAIL    '[{"state":"FAILURE","name":"a"}]'
  echo
  [ "$fails" -eq 0 ] && { echo "all checks pass"; return 0; }
  echo "$fails failed"; return 1
}

# ---------------------------------------------------------------- args
[ $# -eq 0 ] && usage
case "${1:-}" in
  --selftest) selftest; exit $? ;;
  -h|--help)  usage ;;
esac
PR="$1"; shift
while [ $# -gt 0 ]; do
  case "$1" in
    --timeout) TIMEOUT="${2:-}"; shift 2 ;;
    --poll)    POLL="${2:-}";    shift 2 ;;
    *) usage ;;
  esac
done
printf '%s' "$PR" | grep -qE '^[0-9]+$' || usage
command -v gh >/dev/null 2>&1 || { echo "merge_when_green: gh not found"; exit 2; }

# ---------------------------------------------------------------- wait
started=$SECONDS
while :; do
  rollup=$(gh pr view "$PR" --json statusCheckRollup --jq '.statusCheckRollup' 2>/dev/null)
  state=$(printf '%s' "$rollup" | verdict)
  n=$(printf '%s' "$rollup" | python3 -c 'import json,sys
try: print(len(json.load(sys.stdin)))
except Exception: print(0)')

  case "$state" in
    PASS)
      echo "merge_when_green: PR #$PR — $n check(s) passed; merging."
      gh pr merge "$PR" --merge || { echo "merge_when_green: merge command failed"; exit 1; }
      echo "merge_when_green: merged."
      exit 0 ;;
    FAIL)
      echo "merge_when_green: PR #$PR — a check FAILED. Not merging."
      gh pr checks "$PR" 2>/dev/null | head -20
      exit 1 ;;
    NONE)
      # The exact condition that made --auto a no-op. Absence is not success.
      echo "merge_when_green: PR #$PR — NO checks reported. Refusing to merge."
      echo "  An absent gate is indistinguishable from a passed one, so this"
      echo "  script treats it as failure. If CI genuinely does not run on this"
      echo "  PR, that is the thing to fix."
      exit 1 ;;
  esac

  if [ $(( SECONDS - started )) -ge "$TIMEOUT" ]; then
    echo "merge_when_green: PR #$PR — checks still pending after ${TIMEOUT}s. Not merging."
    exit 1
  fi
  sleep "$POLL"
done
