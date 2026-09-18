#!/usr/bin/env bash
# instrument: verification
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

# ------------------------------------------------------------- is it in use?
# THE SEVENTH FACT, AND THE FIRST ONE GIT CANNOT ANSWER. On 2026-09-17 this script reaped a
# worktree from which an 11-minute search was executing, reading its code from
# PYTHONPATH=<worktree>/src. Merged: yes. Clean: yes — the process held no uncommitted files,
# only the directory. Both facts were true and the run died anyway.
#
# THE ANSWER IS THREE-VALUED ON PURPOSE. Every other fact the reaper uses is knowable from
# git, locally, always. This one can be UNANSWERABLE: there is no portable way to ask an OS
# what holds a directory, and no lsof on Windows. Folding "I could not look" into "free" is
# the failure this estate keeps cataloguing — a check that cannot fire reading as one that
# passed — so `unknown` is its own answer and it keeps the worktree.
#
# IT SETS GLOBALS RATHER THAN PRINTING. `x=$(in_use_state ...)` runs in a subshell, so the
# reason string would be discarded at the closing paren and the refusal would print a verdict
# with no explanation. Written that way first.
#
# THE FALLBACK IS DELIBERATELY THE WEAKER HALF. With armory's in_use.py present we get
# markers AND a live-process probe. Without it we read markers only, in pure shell, with no
# python — and a machine with no markers still reaps, because a reaper that refuses every
# reap on every machine without armory installed gets deleted within a week, and then this
# whole change is worth nothing.
IN_USE_STATE=''
IN_USE_WHY=''
IN_USE_MARKERS_ONLY=''

in_use_tool() {
  [ "${BUGARACH_IN_USE:-}" = off ] && return 1
  for c in "${BUGARACH_IN_USE:-}" "${ARMORY_ROOT:-}/tools/in_use.py" \
           "$HOME/Developer/armory/tools/in_use.py"; do
    if [ -n "$c" ] && [ -f "$c" ]; then printf '%s\n' "$c"; return 0; fi
  done
  return 1
}

in_use_state() {   # $1 dir -> sets IN_USE_STATE to free|held|unknown, IN_USE_WHY to the reason
  local dir="${1:-.}" tool out rc gd f pid host me
  IN_USE_STATE=free; IN_USE_WHY=''; IN_USE_MARKERS_ONLY=''
  [ -n "$dir" ] || return 0

  if tool="$(in_use_tool)"; then
    # Executed directly when it is executable, so a stub in the selftest can stand in for it;
    # otherwise handed to python3, which is how it is normally found.
    if [ -x "$tool" ]; then out="$("$tool" "$dir" 2>/dev/null)"; rc=$?
    else out="$(python3 "$tool" "$dir" 2>/dev/null)"; rc=$?; fi
    IN_USE_WHY="$(printf '%s\n' "$out" | sed -n '2,4p')"
    # rc 3 is MARKER-ONLY: nobody claimed the directory, and this machine has no process
    # probe to contradict them. THAT IS EVERY WINDOWS WORKSTATION IN THE ESTATE, where there
    # is no lsof at all. Refusing on it would refuse every reap ever offered on half the
    # machines, and the check would be gone within a week. So we reap, and the message says
    # only markers were checked rather than implying a probe looked and found nothing.
    if [ "$rc" = 0 ]; then IN_USE_STATE=free
    elif [ "$rc" = 1 ]; then IN_USE_STATE=held
    elif [ "$rc" = 3 ]; then IN_USE_STATE=free; IN_USE_MARKERS_ONLY=yes
    else IN_USE_STATE=unknown; fi
    return 0
  fi

  IN_USE_MARKERS_ONLY=yes
  gd="$(git -C "$dir" rev-parse --absolute-git-dir 2>/dev/null || true)"
  [ -n "$gd" ] || return 0
  me="$(hostname 2>/dev/null || echo unknown-host)"
  for f in "$gd"/in-use/*.json; do
    [ -f "$f" ] || continue
    pid="$(sed -n 's/.*"pid"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$f" | head -1)"
    host="$(sed -n 's/.*"host"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$f" | head -1)"
    [ -n "$pid" ] || continue
    if [ "$host" != "$me" ]; then
      IN_USE_STATE=unknown
      IN_USE_WHY="  a marker written on '$host', and a pid from another machine cannot be checked"
      return 0
    fi
    if kill -0 "$pid" 2>/dev/null; then
      IN_USE_STATE=held
      IN_USE_WHY="  a marker held by live pid $pid on $host"
      return 0
    fi
  done
  return 0
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
#   $7 in-use: free | held | anything else, including absent, meaning unknown
reap_verdict() {
  local self="$1" primary="$2" branch="$3" head="$4" merged="$5" dirty="$6" inuse="${7:-}"
  if [ -z "$self" ];                              then echo "SKIP:not-a-worktree"; return; fi
  if [ "$self" = "$primary" ];                    then echo "SKIP:primary";        return; fi
  if [ -z "$branch" ] || [ "$branch" = DETACHED ]; then echo "SKIP:detached";       return; fi
  if [ -z "$head" ];                              then echo "SKIP:unknown-head";   return; fi
  if [ "$branch" != "$head" ];                    then echo "SKIP:other-branch";   return; fi
  if [ "$merged" != yes ];                        then echo "SKIP:not-merged";     return; fi
  if [ "$dirty" != 0 ];                           then echo "SKIP:dirty";          return; fi
  # NO DEFAULT FOR $7. An absent seventh argument is "nobody told me", which is exactly the
  # unknown case — defaulting it to free would let a caller that forgets the fact reproduce
  # the 2026-09-17 loss in silence. The selftest fires that row by name.
  if [ "$inuse" = held ];                         then echo "SKIP:in-use";         return; fi
  if [ "$inuse" != free ];                        then echo "SKIP:in-use-unknown"; return; fi
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
  # TWO CALLS, AND THE SECOND ONE IS WHY THE PROBE IS AFFORDABLE. lsof over a worktree is
  # the only expensive fact here, and on most merges some cheaper fact already refuses. So
  # ask the pure function first with `free`, and only pay for the probe when everything else
  # has already said REAP. reap_verdict stays pure either way.
  verdict="$(reap_verdict "$self" "$primary" "$branch" "$head" "$merged" "$dirty" free)"
  if [ "$verdict" = REAP ]; then
    in_use_state "$self"
    verdict="$(reap_verdict "$self" "$primary" "$branch" "$head" "$merged" "$dirty" "$IN_USE_STATE")"
  fi
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
    SKIP:in-use)
      echo "merge_when_green: worktree kept — something is still running in $name."
      [ -n "$IN_USE_WHY" ] && printf '%s\n' "$IN_USE_WHY"
      echo "  The branch IS merged; only the directory is held. Re-run this when the run ends,"
      echo "  or remove it by hand once you know what that process is."
      ;;
    SKIP:in-use-unknown)
      echo "merge_when_green: worktree kept — could not establish whether anything is running in $name."
      [ -n "$IN_USE_WHY" ] && printf '%s\n' "$IN_USE_WHY"
      echo "  Refusing rather than guessing: a wrong answer here kills a run. The branch IS merged."
      ;;
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
      [ "$IN_USE_MARKERS_ONLY" = yes ] && \
        echo "  Nothing claimed it, but this machine has no process probe — markers only."
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
  r() { # name expected self primary branch head merged dirty [in-use]
    local got; got=$(reap_verdict "$3" "$4" "$5" "$6" "$7" "$8" "${9:-}")
    if [ "$got" = "$2" ]; then printf '  ok   %-40s\n' "$1"
    else printf '  FAIL %-40s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  r "mine, merged, clean, idle"     REAP               /w /p feat feat yes 0 free
  r "the primary is never reaped"   SKIP:primary       /p /p feat feat yes 0
  r "not in a worktree at all"      SKIP:not-a-worktree ''  /p feat feat yes 0
  r "detached HEAD"                 SKIP:detached      /w /p DETACHED feat yes 0
  r "PR head unknown -> refuse"     SKIP:unknown-head  /w /p feat ''   yes 0
  r "somebody else's PR"            SKIP:other-branch  /w /p feat other yes 0
  r "merge did not land here"       SKIP:not-merged    /w /p feat feat no 0
  r "uncommitted work"              SKIP:dirty         /w /p feat feat yes 3
  r "identity beats state"          SKIP:other-branch  /w /p feat other yes 3 free

  # The fact that cost a run on 2026-09-17. Merged and clean were both TRUE for this row.
  r "a run is executing inside it"  SKIP:in-use         /w /p feat feat yes 0 held
  r "cannot tell -> refuse"         SKIP:in-use-unknown /w /p feat feat yes 0 unknown
  r "nobody supplied the fact"      SKIP:in-use-unknown /w /p feat feat yes 0
  r "dirty is answered before it"   SKIP:dirty          /w /p feat feat yes 3 held

  # THE PROBE ITSELF, AGAINST A REAL DIRECTORY AND A REAL PID. The rows above test the
  # decision; these test the fact it decides on. Both routes are fired — with armory's
  # in_use.py if this machine has it, and with BUGARACH_IN_USE=off, which forces the pure
  # shell marker path a machine without armory would take. Whichever route is missing here
  # would otherwise be the one that has never run anywhere.
  echo
  # `VAR=value some_function` LEAKS IN BASH. For a function, unlike an external command, the
  # prefix assignment persists after the call returns — so the first `BUGARACH_IN_USE=off`
  # row disabled armory's probe for the REST of the selftest, and the row that claims to test
  # the armory route silently tested the shell fallback a second time while printing ok.
  # Found by noticing that route reported absent on a machine that has armory.
  u() { # name expected dir [env]
    local got had="${BUGARACH_IN_USE+set}" saved="${BUGARACH_IN_USE:-}"
    if [ -n "${4:-}" ]; then BUGARACH_IN_USE="$4"; fi
    in_use_state "$3"
    if [ "$had" = set ]; then BUGARACH_IN_USE="$saved"; else unset BUGARACH_IN_USE; fi
    got="$IN_USE_STATE"
    if [ "$got" = "$2" ]; then printf '  ok   %-40s\n' "$1"
    else printf '  FAIL %-40s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  probe_tmp="$(mktemp -d)"
  ( cd "$probe_tmp" && git init -q . && git config user.email t@t.invalid && git config user.name t \
    && echo x > f.txt && git add -A && git commit -qm one ) >/dev/null 2>&1
  probe_gd="$(git -C "$probe_tmp" rev-parse --absolute-git-dir 2>/dev/null)"
  mkdir -p "$probe_gd/in-use"
  probe_host="$(hostname 2>/dev/null || echo unknown-host)"

  u "no marker, nothing running -> free"  free    "$probe_tmp" off
  printf '{"pid": %s, "host": "%s"}\n' "$$" "$probe_host" > "$probe_gd/in-use/live.json"
  u "a live marker holds it"              held    "$probe_tmp" off
  printf '{"pid": 2147483647, "host": "%s"}\n' "$probe_host" > "$probe_gd/in-use/live.json"
  u "a dead pid does NOT hold it"         free    "$probe_tmp" off
  printf '{"pid": %s, "host": "%s-elsewhere"}\n' "$$" "$probe_host" > "$probe_gd/in-use/live.json"
  u "another machine's pid -> unknown"    unknown "$probe_tmp" off
  rm -f "$probe_gd/in-use/live.json"

  # THE EXIT-CODE CONTRACT WITH ARMORY, FIRED BY NUMBER. This is the seam between two
  # repositories: in_use.py promises 0/1/2/3 and this script maps them. Nothing else here
  # would notice if that mapping drifted, and a stub costs four lines.
  # SAVE AND RESTORE ONCE AROUND THE WHOLE BLOCK. The first draft unset BUGARACH_IN_USE after
  # each stub, which wiped an override supplied from OUTSIDE the selftest -- so running with
  # BUGARACH_IN_USE pointed at a real in_use.py silently lost it partway through and the
  # armory-route row stopped running while everything still printed pass. Second instance of
  # the same leak in this file; the first is in u() above.
  probe_had="${BUGARACH_IN_USE+set}"; probe_saved="${BUGARACH_IN_USE:-}"
  for pair in "0 free" "1 held" "2 unknown" "3 free"; do
    set -- $pair
    printf '#!/bin/sh\nexit %s\n' "$1" > "$probe_tmp/stub.py"
    chmod +x "$probe_tmp/stub.py"
    BUGARACH_IN_USE="$probe_tmp/stub.py" in_use_state "$probe_tmp"
    if [ "$IN_USE_STATE" = "$2" ]; then printf '  ok   %-40s\n' "in_use.py exit $1 -> $2"
    else printf '  FAIL %-40s (got %s, want %s)\n' "in_use.py exit $1 -> $2" "$IN_USE_STATE" "$2"; fails=$((fails+1)); fi
  done
  printf '#!/bin/sh\nexit 3\n' > "$probe_tmp/stub.py"
  BUGARACH_IN_USE="$probe_tmp/stub.py" in_use_state "$probe_tmp"
  if [ "$IN_USE_MARKERS_ONLY" = yes ]; then printf '  ok   %-40s\n' "exit 3 also records markers-only"
  else printf '  FAIL %-40s\n' "exit 3 also records markers-only"; fails=$((fails+1)); fi
  if [ "$probe_had" = set ]; then BUGARACH_IN_USE="$probe_saved"; else unset BUGARACH_IN_USE; fi
  rm -f "$probe_tmp/stub.py"

  # A marker must never dirty the tree, or it trips this script's own `clean` check and the
  # right answer arrives for the wrong reason.
  printf '{"pid": %s, "host": "%s"}\n' "$$" "$probe_host" > "$probe_gd/in-use/live.json"
  if [ -z "$(git -C "$probe_tmp" status --porcelain 2>/dev/null)" ]; then
    printf '  ok   %-40s\n' "a marker leaves git status clean"
  else
    printf '  FAIL %-40s\n' "a marker leaves git status clean"; fails=$((fails+1))
  fi
  # NOT `ok`, BECAUSE NOTHING WAS ASSERTED. A skipped check that prints ok is how a suite
  # reports coverage it does not have; this estate has the case reports to prove it.
  if in_use_tool >/dev/null 2>&1; then
    u "armory's probe agrees the dir is held" held "$probe_tmp"
  else
    printf '  note %-40s\n' "armory's in_use.py is not on this machine — that route was NOT tested"
  fi
  rm -rf "$probe_tmp"

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
