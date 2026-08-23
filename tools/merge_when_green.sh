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
# with one refinement learned the hard way: "no checks YET" and "no checks EVER"
# are indistinguishable in the seconds after a PR opens, before CI is even
# scheduled. Refusing instantly makes the tool cry wolf in the normal case, and a
# gate that cries wolf gets bypassed. So checks are given a bounded --grace
# window to APPEAR; only then is absence treated as failure.
#
# That is the whole point. Zero checks is not "nothing to worry about", it is
# exactly the condition that produced the bug — an absent gate reads identically
# to a passed one unless you treat absence as failure.
#
# This is WEAKER than branch protection and does not replace it: it only governs
# merges that go through this script. A session calling `gh pr merge` directly
# still bypasses it. See docs/todo/2026-08-12-enable-branch-protection-on-main.md.
#
# THE REAPER — why this script, of all scripts, removes a worktree.
#
# Because it is the only process awake at the moment the worktree becomes
# garbage. It blocks, polling, until the PR lands; the merge is its own return
# value. "Your branch is now on main" and "this worktree is now rubbish" are the
# same sentence, and nothing used to say the second half.
#
# The cost of that silence, measured 2026-08-23: 28 worktrees on one machine, 17
# of them merged-clean-idle, and HALF USED FOR UNDER TWENTY MINUTES — made for one
# task, one PR, never touched again. (Median 37 min across the 27 non-primary
# worktrees, but the distribution is bimodal — 13 under 20 min, 11 over four hours,
# almost nothing between — so no single number describes it. This comment claimed
# "median TEN MINUTES" until a murderboard recomputation showed that was the median
# of the short mode quoted as the median of the whole.)
# Across seven hours that afternoon the count went
# 21 -> 28 while ACTIVE claims on the session board went 8 -> 3. Same sessions,
# same load, opposite directions: the board is gated (`.githooks/pre-commit`
# refuses a commit from an unclaimed worktree) and it held; worktree removal was
# gated by nothing and leaked. The tree records which rules got mechanized.
#
# WHAT IT REMOVES — one thing, and it cannot be talked into a second: the
# worktree YOU ARE STANDING IN, whose branch is the PR you just merged. Not one
# found by scanning, not one that merely looks finished. That is what makes it
# safe where `tools/worktree_sweep.sh` is not — the sweep judges other people's
# directories by git state alone and cannot see their intent, which is why it
# must not be --apply'd today. This one asks nobody's intent but yours, and you
# just merged.
#
# It KEEPS, and says why, on: the primary checkout, a detached HEAD, a branch
# that is not the PR's head, a branch git cannot confirm is on origin/main, any
# uncommitted file, and a head branch it could not read at all. The reap NEVER
# changes the exit status — merging is what this script promises, and a worktree
# it declined to remove is not a failed merge.
#
# It also deletes IGNORED files, because `git worktree remove` does and
# `git status --porcelain` cannot see them — so no dirty-check could have caught
# them. Here that is the built `site/` and `.pytest_cache`, both regenerable;
# they are counted in the output rather than left to be discovered.
#
# USAGE
#   tools/merge_when_green.sh <pr-number> [--timeout SECONDS] [--poll SECONDS]
#                                        [--grace SECONDS] [--no-reap]
#   tools/merge_when_green.sh --selftest
#
#   --no-reap (or MERGE_WHEN_GREEN_NO_REAP=1) leaves the worktree in place.
#
# EXIT  0 merged   1 not merged (checks failed, absent, or timed out)   2 usage/env

set -uo pipefail

TIMEOUT=1800
POLL=20
GRACE=180          # how long to wait for checks to APPEAR before calling it none
PR=""
NO_REAP="${MERGE_WHEN_GREEN_NO_REAP:-0}"

# Print every comment line after the shebang and stop at the first line that is
# not one. A fixed `2,30p` was silently truncating this header the moment it
# grew — a flag that does not appear in --help is an absent gate by another
# route, which is the bug this whole script is about.
usage() { awk 'NR>1 && /^#/ {sub(/^# ?/,""); print; next} NR>1 {exit}' "$0"; exit 2; }

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

# ---------------------------------------------------------------- reaper
# Pure decision, six facts in, one word out. Separated from the doing so it can
# be fired in every direction by --selftest, with no git tree and no network —
# the same reason verdict() above is pure.
#
# The order matters: identity questions (is this even mine?) before state
# questions (is it finished?), so a session that merged somebody else's PR from
# its own worktree is turned away before "merged and clean" can ever look true.
#   $1 self  $2 primary  $3 branch  $4 pr-head-branch  $5 merged  $6 dirty-count
reap_verdict() {
  local self="$1" primary="$2" branch="$3" head="$4" merged="$5" dirty="$6"
  if [ -z "$self" ];                              then echo "SKIP:not-a-worktree"; return; fi
  if [ "$self" = "$primary" ];                    then echo "SKIP:primary";        return; fi
  if [ -z "$branch" ] || [ "$branch" = DETACHED ]; then echo "SKIP:detached";       return; fi
  if [ -z "$head" ];                              then echo "SKIP:unknown-head";   return; fi
  if [ "$branch" != "$head" ];                    then echo "SKIP:other-branch";   return; fi
  if [ "$merged" != yes ];                        then echo "SKIP:not-merged";     return; fi
  if [ "$dirty" != 0 ];                           then echo "SKIP:dirty";          return; fi
  echo REAP
}

# The reaped-ignored line, written for the person who reads it. The first live
# run of the reaper printed eight `__pycache__/` entries in full — true, and
# nobody reads to the end of it, which makes the one line whose job is "did that
# just delete something you wanted?" the line most likely to be skipped. So the
# caches nobody grieves are counted and everything else is named.
summarise_ignored() {   # stdin: one path per line. One clause on stdout, or nothing.
  awk '
    /__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache/ { caches++; next }
    { if (shown < 4) named[shown++] = $0; else extra++ }
    END {
      n = shown + extra + caches
      if (n == 0) exit
      if (shown == 0 && extra == 0) {
        printf "%d ignored path(s) went with it, all build/test caches\n", n; exit
      }
      s = ""
      for (i = 0; i < shown; i++) s = s (i ? ", " : "") named[i]
      if (extra)  s = s ", +" extra " more"
      if (caches) s = s ", " caches " cache dir" (caches > 1 ? "s" : "")
      printf "%d ignored path(s) went with it: %s\n", n, s
    }'
}

# The doing. Takes the PR's head branch as an argument rather than asking gh
# itself, which is what keeps it drivable from a test against a scratch repo.
# Returns 0 whatever it decides: the merge already happened, and this script's
# promise is the merge.
reap_worktree() {
  local head="${1:-}" self primary branch merged dirty verdict name ignored
  self="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  primary="$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2; exit}')"
  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo DETACHED)"
  git fetch -q origin 2>/dev/null || true
  if git merge-base --is-ancestor "$branch" origin/main 2>/dev/null; then merged=yes; else merged=no; fi
  dirty="$(git -C "${self:-.}" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  verdict="$(reap_verdict "$self" "$primary" "$branch" "$head" "$merged" "$dirty")"
  name="$(basename "${self:-?}")"

  case "$verdict" in
    # Merged from the primary checkout, or from no worktree at all: there was
    # never anything to reap, so saying so would just be noise on every merge.
    SKIP:primary|SKIP:not-a-worktree) return 0 ;;
    SKIP:detached)     echo "merge_when_green: worktree kept — detached HEAD, nothing to match against the PR." ;;
    SKIP:unknown-head) echo "merge_when_green: worktree kept — could not read PR #${PR:-?}'s head branch, and refusing to guess which worktree that makes disposable." ;;
    SKIP:other-branch) echo "merge_when_green: worktree kept — you are on '$branch' but PR #${PR:-?} merged '$head'." ;;
    SKIP:not-merged)   echo "merge_when_green: worktree kept — '$branch' is not on origin/main, so the merge did not land here." ;;
    SKIP:dirty)        echo "merge_when_green: worktree kept — $dirty uncommitted file(s) in $name." ;;
    REAP)
      ignored="$(git -C "$self" status --porcelain --ignored 2>/dev/null | awk '/^!! /{print $2}' | summarise_ignored)"
      if ! cd "$primary" 2>/dev/null; then
        echo "merge_when_green: worktree kept — cannot reach the primary checkout to remove it from."; return 0
      fi
      if ! git worktree remove "$self"; then
        echo "merge_when_green: worktree kept — git refused to remove it (reason above)."; return 0
      fi
      git branch -d "$branch" >/dev/null 2>&1 || true
      echo "merge_when_green: reaped $name — '$branch' is on main and held nothing uncommitted."
      [ -n "$ignored" ] && echo "  $ignored"
      echo "  YOUR SHELL IS STILL POINTED AT THE DELETED DIRECTORY.  cd $primary"
      ;;
  esac
  return 0
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

  # The reaper deletes a directory, so every refusal it can make gets fired here
  # by name. /p is the primary checkout, /w the worktree you are standing in.
  echo
  r() { # name expected self primary branch head merged dirty
    local got; got=$(reap_verdict "$3" "$4" "$5" "$6" "$7" "$8")
    if [ "$got" = "$2" ]; then printf '  ok   %-40s\n' "$1"
    else printf '  FAIL %-40s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  r "mine, merged, clean -> REAP"   REAP               /w /p feat feat yes 0
  r "the primary is never reaped"   SKIP:primary       /p /p feat feat yes 0
  r "not in a worktree at all"      SKIP:not-a-worktree ''  /p feat feat yes 0
  r "detached HEAD"                 SKIP:detached      /w /p DETACHED feat yes 0
  r "PR head unknown -> refuse"     SKIP:unknown-head  /w /p feat ''   yes 0
  r "somebody else's PR"            SKIP:other-branch  /w /p feat other yes 0
  r "merge did not land here"       SKIP:not-merged    /w /p feat feat no 0
  r "uncommitted work"              SKIP:dirty         /w /p feat feat yes 3
  r "identity beats state"          SKIP:other-branch  /w /p feat other yes 3

  # The line a person actually reads after a reap.
  echo
  s() { # name expected input
    local got; got=$(printf '%s' "$3" | summarise_ignored)
    if [ "$got" = "$2" ]; then printf '  ok   %-40s\n' "$1"
    else printf '  FAIL %-40s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  s "nothing ignored -> say nothing" "" ""
  s "caches only -> counted, not listed" \
    "2 ignored path(s) went with it, all build/test caches" \
    $'src/__pycache__/\n.pytest_cache/'
  s "a real artifact is named" \
    "3 ignored path(s) went with it: site/, 2 cache dirs" \
    $'site/\n.pytest_cache/\nsrc/__pycache__/'
  s "too many to name -> the rest counted" \
    "6 ignored path(s) went with it: a/, b/, c/, d/, +2 more" \
    $'a/\nb/\nc/\nd/\ne/\nf/'

  echo
  [ "$fails" -eq 0 ] && { echo "all checks pass"; return 0; }
  echo "$fails failed"; return 1
}

# Sourcing this file with MERGE_WHEN_GREEN_LIB=1 defines the functions and stops
# here, which is how tests/test_merge_gate.py drives the reaper against a real
# scratch repo — a directory actually gets removed in that test — with no gh, no
# network and no PR.
[ "${MERGE_WHEN_GREEN_LIB:-0}" = "1" ] && return 0 2>/dev/null

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
    --grace)   GRACE="${2:-}";   shift 2 ;;
    --no-reap) NO_REAP=1;        shift   ;;
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
      # The one second at which this branch's worktree becomes garbage, and the
      # only moment anything is awake to notice. See THE REAPER at the top.
      if [ "$NO_REAP" = "1" ]; then
        echo "merge_when_green: --no-reap — worktree left in place."
      else
        reap_worktree "$(gh pr view "$PR" --json headRefName --jq .headRefName 2>/dev/null || true)"
      fi
      exit 0 ;;
    FAIL)
      echo "merge_when_green: PR #$PR — a check FAILED. Not merging."
      gh pr checks "$PR" 2>/dev/null | head -20
      exit 1 ;;
    NONE)
      # Absence is not success — but "no checks YET" and "no checks EVER" look
      # identical for the first few seconds after a PR is opened, and CI has not
      # even been scheduled. Refusing instantly makes the tool cry wolf in the
      # normal case, and a gate that cries wolf gets bypassed. So allow a bounded
      # grace period for checks to APPEAR; if none has by then, refuse as before.
      if [ $(( SECONDS - started )) -lt "$GRACE" ]; then
        sleep "$POLL"; continue
      fi
      echo "merge_when_green: PR #$PR — NO checks reported after ${GRACE}s. Refusing."
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
