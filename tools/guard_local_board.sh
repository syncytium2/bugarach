#!/usr/bin/env bash
# guard_local_board.sh — refuse a commit from a session that has not claimed
# itself on the MACHINE-LOCAL session board.
#
# WHY THIS IS A GATE AND NOT A LINE IN THE BRIEFING. The briefing already said
# it. On 2026-08-18 a session read "(no board yet — create it and claim your
# work)" at startup, worked for hours across two worktrees, wrote a figure to the
# shared darkroom, and never created the board — while at least four other
# sessions ran on the same machine. The in-git board (docs/SESSIONS.md) was kept
# properly, because that one is about outputs other MACHINES can see. The local
# board is about resources this machine shares — the primary checkout, MATLAB,
# the venv, the darkroom mount, a port — and nothing enforced it, so it stayed
# empty exactly when it was most needed.
#
# A hook cannot halt a session at its first thought. The commit is the first
# moment the machine can insist, so this insists there.
#
# WHAT COUNTS AS A CLAIM. A BLOCK HEADING naming this worktree — `### <host>/<id>`,
# where <id> is the worktree's directory basename or its branch. Per-worktree rather
# than per-session, because a worktree is what the machine can actually observe; a
# session id is not knowable from a hook.
#
# ---------------------------------------------------------------------------------
# AND UNTIL 2026-08-26 THAT READ "any line mentioning", which is not the same thing,
# and it let the gate through in the one place it was needed most. The primary
# checkout's directory basename is `bugarach`:
#
#     $ grep -cF -- bugarach ../bugarach-worktrees/SESSIONS.md
#     267
#     $ bash tools/guard_local_board.sh ; echo $?      # from an unclaimed checkout
#     0
#
# Every path written on a 3,000-line board contains the repo name, so the primary
# checkout could never be refused — and neither could any worktree whose name happens
# to be a substring of something already written down. The session that found this had
# been running unclaimed for an hour with the gate saying fine.
#
# The old comment defended the substring: "blocks are headed `### Mac/<branch> — ...`
# and a session may address itself by either name." Both halves are true and neither
# one needs a substring. The heading is parsed now and BOTH names are checked against
# it. What is gone is matching prose — a block that names another worktree in its
# Touches line is a mention, not a claim.
#
# ESCAPE HATCH, deliberate: `ALLOW_UNCLAIMED_BOARD=1 git commit ...`, for the
# same reason guard_branch.sh has one — a guard with no override gets disabled
# wholesale the first time it is in the way, and then it guards nothing.
#
# USAGE
#   tools/guard_local_board.sh                      check this worktree (hook use)
#   tools/guard_local_board.sh --board F --name N   check a hypothetical pair
#   tools/guard_local_board.sh --path               print the board path and exit
#   tools/guard_local_board.sh --audit              every live worktree, old vs new
#   tools/guard_local_board.sh --selftest           prove every branch fires
#
# EXIT  0 allowed   1 blocked   2 could not determine (never a silent pass)

set -uo pipefail

# Resolve the board the same way the vendored session-start hook does, so the
# briefing and this gate can never disagree about which file is the board.
board_path() {
  local cm cma primary base repo
  cm=$(git rev-parse --git-common-dir 2>/dev/null) || return 1
  cma=$( [ -n "$cm" ] && (CDPATH= cd -- "$cm" 2>/dev/null && pwd -P) )
  primary=$( [ -n "$cma" ] && dirname "$cma" )
  base="${primary:-$(git rev-parse --show-toplevel 2>/dev/null)}"
  [ -z "$base" ] && return 1
  repo=$(basename "$base")
  echo "$(dirname "$base")/${repo}-worktrees/SESSIONS.md"
}

# The whole decision, as a pure function of (board contents, this worktree's
# names, override) — so the selftest can drive every branch without a git repo.
#   $1 board file ("" or missing = no board)  $2 worktree name  $3 branch  $4 override
verdict() {
  local file="$1" name="${2:-}" branch="${3:-}" override="${4:-}"
  if [ -n "$override" ]; then echo OVERRIDE; return; fi
  if [ -z "$name" ] && [ -z "$branch" ]; then echo UNKNOWN; return; fi
  if [ -z "$file" ] || [ ! -f "$file" ]; then echo NOBOARD; return; fi
  if claims_heading "$file" "$name" "$branch"; then echo ALLOW; return; fi
  echo UNCLAIMED
}

# Does the board carry a BLOCK HEADING for either of these names?
#
# Headings look like `### <host>/<id> — <task>` per the protocol's template, and
# sometimes `### <id> — <task>` with no host. So: take heading lines, drop the
# marker, drop everything up to the LAST slash (a host may contain one), and take
# the identifier up to the first space. Then compare it EXACTLY — never as a regex,
# because a worktree name may contain characters a regex would read as syntax, and
# never as a substring, which is the bug this replaces.
#
# The comparison is exact but the ACCEPTANCE is not narrow: either the worktree's
# directory basename or its branch will do, since those legitimately differ (this
# machine has run `settle-the-guard` on branch `settle-the-guard-question`) and a
# session may reasonably head its block with either.
#   $1 board file   $2 worktree name   $3 branch
claims_heading() {
  local file="$1" name="${2:-}" branch="${3:-}"
  LC_ALL=C awk -v want1="$name" -v want2="$branch" '
    /^###[[:space:]]/ {
      s = $0
      sub(/^###[[:space:]]+/, "", s)
      if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }
      sub(/[[:space:]].*$/, "", s)
      if (s == "") next
      if ((want1 != "" && s == want1) || (want2 != "" && s == want2)) { found = 1; exit }
    }
    END { exit(found ? 0 : 1) }' "$file"
}

# What the rule USED to be, kept for --audit alone so the report can say who changes
# verdict rather than only who fails. Not reachable from the gate.
claims_substring() {
  local file="$1" name="${2:-}" branch="${3:-}"
  { [ -n "$name" ] && grep -qF -- "$name" "$file"; } && return 0
  { [ -n "$branch" ] && grep -qF -- "$branch" "$file"; } && return 0
  return 1
}

# =================================================================================
# AUDIT — run both rules over every live worktree on this machine and report who
# changes verdict. A stricter gate starts refusing commits that pass today, and the
# people it will refuse are other sessions mid-task. They are owed the list before
# it lands rather than a surprise at their next commit.
# =================================================================================
audit() {
  local board line dir branch old new changed=0 total=0
  board=$(board_path) || { echo "not a git repo" >&2; return 2; }
  if [ ! -f "$board" ]; then
    echo "board-guard audit: no board at $board — every worktree here is NOBOARD."
    return 0
  fi
  echo "board-guard audit — $(basename "$board") , $(grep -c '^### ' "$board" 2>/dev/null) block(s)"
  echo
  printf '  %-38s %-9s %-9s %s\n' "worktree (branch)" "was" "now" ""
  while IFS= read -r line; do
    case "$line" in
      worktree\ *) dir=${line#worktree }; branch="" ;;
      branch\ *)   branch=${line#branch refs/heads/} ;;
      "")
        [ -n "${dir:-}" ] || continue
        total=$((total + 1))
        claims_substring "$board" "$(basename "$dir")" "$branch" && old=allow || old=BLOCK
        claims_heading  "$board" "$(basename "$dir")" "$branch" && new=allow || new=BLOCK
        if [ "$old" != "$new" ]; then
          changed=$((changed + 1))
          printf '  %-38s %-9s %-9s <-- CHANGES\n' \
                 "$(basename "$dir") ($branch)" "$old" "$new"
        else
          printf '  %-38s %-9s %-9s\n' "$(basename "$dir") ($branch)" "$old" "$new"
        fi
        dir=""; branch="" ;;
    esac
  done < <(git worktree list --porcelain 2>/dev/null; echo)
  echo
  echo "  ${changed} of ${total} worktree(s) change verdict."
  [ "$changed" -gt 0 ] && {
    echo "  Each one needs a heading on the board: '### $(hostname -s 2>/dev/null || echo Mac)/<branch> — <task>'."
    echo "  One-off escape while they write it: ALLOW_UNCLAIMED_BOARD=1 git commit ..."
  }
  return 0
}

selftest() {
  local fails=0 tmp
  tmp=$(mktemp -d) || { echo "cannot mktemp"; return 1; }
  printf '# board\n\n### Mac/known-branch — a task\n- Status: ACTIVE\n' > "$tmp/board.md"
  : > "$tmp/empty.md"

  t() { # label expected board wtname branch override
    local got; got=$(verdict "$3" "${4:-}" "${5:-}" "${6:-}")
    if [ "$got" = "$2" ]; then printf '  ok   %-46s\n' "$1"
    else printf '  FAIL %-46s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  t "missing board blocks"               NOBOARD   "$tmp/nope.md"  "wt" "br" ""
  t "empty board blocks"                 UNCLAIMED "$tmp/empty.md" "wt" "br" ""
  t "board without my block blocks"      UNCLAIMED "$tmp/board.md" "wt" "other" ""
  t "a block naming my branch allows"    ALLOW     "$tmp/board.md" "wt" "known-branch" ""
  t "a block naming my worktree allows"  ALLOW     "$tmp/board.md" "known-branch" "x" ""
  t "override releases a missing board"  OVERRIDE  "$tmp/nope.md"  "wt" "br" "1"
  t "override releases an unclaimed one" OVERRIDE  "$tmp/empty.md" "wt" "br" "1"
  t "no names at all -> UNKNOWN"         UNKNOWN   "$tmp/board.md" "" "" ""

  # ------------------------------------------------------------------------------
  # THE BUG THIS REPLACES, driven directly. Every case below returned ALLOW under
  # the substring rule, and the first one is why the gate could not fail in the
  # primary checkout: the repo name is in every path on the board.
  # ------------------------------------------------------------------------------
  {
    printf '# Machine-local board for bugarach\n\n'
    printf '### Mac/known-branch — a task\n'
    printf -- '- **Worktree:** `bugarach-worktrees/known-branch`\n'
    printf -- '- **Touches:** `tools/guard_local_board.sh`, docs/ under bugarach\n\n'
    printf '### Mac/known-branch-extended — a different task\n'
    printf -- '- **Status:** ACTIVE\n\n'
    printf '### no-host-prefix — a block written without a host\n'
    printf -- '- **Status:** ACTIVE\n'
  } > "$tmp/real.md"

  t "the repo name in every path is not a claim"  UNCLAIMED "$tmp/real.md" "bugarach" "main" ""
  t "a prefix of another block is not a claim"    UNCLAIMED "$tmp/real.md" "known" "known" ""
  t "being named in someone's Touches is not one" UNCLAIMED "$tmp/real.md" "guard_local_board.sh" "x" ""
  t "an exact heading still allows"               ALLOW     "$tmp/real.md" "x" "known-branch" ""
  t "and the longer neighbour allows separately"  ALLOW     "$tmp/real.md" "x" "known-branch-extended" ""
  t "a heading with no host prefix allows"        ALLOW     "$tmp/real.md" "no-host-prefix" "x" ""
  t "a superstring of a heading is not a claim"   UNCLAIMED "$tmp/real.md" "known-branch-extended-more" "y" ""

  # A name carrying regex syntax must be compared literally, not interpreted. The
  # old rule used grep -F for this reason; the new one must not lose it.
  printf '### Mac/v1.2+rc — a task\n- **Status:** ACTIVE\n' > "$tmp/meta.md"
  t "a name with regex syntax matches itself"     ALLOW     "$tmp/meta.md" "x" 'v1.2+rc' ""
  t "and does not match what the regex would"     UNCLAIMED "$tmp/meta.md" "x" 'v1X2+rc' ""

  # --audit must not crash outside a worktree tree, and must report rather than gate.
  if audit >/dev/null 2>&1; then printf '  ok   %-46s\n' "--audit runs and reports"
  else printf '  FAIL %-46s\n' "--audit runs and reports"; fails=$((fails+1)); fi

  rm -rf "$tmp"
  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails failed"; return 1
}

BOARD=""; NAME=""; BRANCH=""
case "${1:-}" in
  --selftest) selftest; exit $? ;;
  --audit)    audit; exit $? ;;
  -h|--help)  sed -n '2,56p' "$0"; exit 2 ;;
  --path)     board_path || { echo "not a git repo" >&2; exit 2; }; exit 0 ;;
  --board)    BOARD="${2:-}"
              if [ "${3:-}" = "--name" ]; then NAME="${4:-}"; BRANCH="${4:-}"; fi ;;
  "")         BOARD=$(board_path) || { echo "[board-guard] not a git repo" >&2; exit 2; }
              NAME=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null)
              BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "") ;;
  *)          sed -n '2,33p' "$0"; exit 2 ;;
esac

V=$(verdict "$BOARD" "$NAME" "$BRANCH" "${ALLOW_UNCLAIMED_BOARD:-}")
case "$V" in
  ALLOW)    exit 0 ;;
  OVERRIDE) echo "[board-guard] ALLOW_UNCLAIMED_BOARD set — claim skipped for this commit." >&2; exit 0 ;;
  UNKNOWN)  echo "[board-guard] cannot determine this worktree's name or branch — refusing rather than passing silently." >&2; exit 2 ;;
esac

# BLOCKED: say exactly what to write, and where. A gate that only says "no" gets
# overridden; one that hands you the fix gets obeyed.
{
  echo
  if [ "$V" = "NOBOARD" ]; then
    echo "[board-guard] BLOCKED — the machine-local session board does not exist."
  else
    echo "[board-guard] BLOCKED — this worktree has no block on the machine-local board."
  fi
  echo
  echo "  board:    $BOARD"
  echo "  worktree: ${NAME:-?}   branch: ${BRANCH:-?}"
  echo
  echo "That board tracks what THIS MACHINE shares — the primary checkout, MATLAB,"
  echo "the venv, the darkroom mount, a port. Several sessions run here at once and"
  echo "none of them can see each other any other way."
  echo
  echo "Add a block, then commit again:"
  echo
  echo "  ### $(hostname -s 2>/dev/null || echo Mac)/${BRANCH:-<branch>} — <what you are doing>"
  echo "  - **Status:** ACTIVE"
  echo "  - **Worktree:** ${NAME:-<dir>}"
  echo "  - **Touches:** <the paths you expect to write — globs are fine>"
  echo "  - **Holds:** <local resources, or none>"
  echo "  - **Notes:** <anything a session on this machine must not stomp>"
  echo
  echo "One-off escape: ALLOW_UNCLAIMED_BOARD=1 git commit ..."
  echo
  echo "AND YOU ARE READING THIS TOO LATE — by construction, not by accident. This"
  echo "gate fires at your first commit, so the work already exists. On 2026-08-20"
  echo "three sessions each did good work twice: two tool conversions, one spec"
  echo "revision, one CI change. Every one of them had claimed correctly — just"
  echo "afterwards. None of the three shared a branch name and all three overlapped"
  echo "in PATHS, which is what the Touches line is for. Next session: write the"
  echo "block when you pick up the task, not when the machine finally insists."
  echo
} >&2
exit 1
