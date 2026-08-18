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
# WHAT COUNTS AS A CLAIM. A block naming this worktree — its directory basename
# or its branch. Per-worktree rather than per-session, because a worktree is what
# the machine can actually observe; a session id is not knowable from a hook.
#
# ESCAPE HATCH, deliberate: `ALLOW_UNCLAIMED_BOARD=1 git commit ...`, for the
# same reason guard_branch.sh has one — a guard with no override gets disabled
# wholesale the first time it is in the way, and then it guards nothing.
#
# USAGE
#   tools/guard_local_board.sh                      check this worktree (hook use)
#   tools/guard_local_board.sh --board F --name N   check a hypothetical pair
#   tools/guard_local_board.sh --path               print the board path and exit
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
  # A claim is any line mentioning this worktree or branch. Substring, not exact:
  # blocks are headed "### Mac/<branch> — <task>" by the protocol's own template,
  # and a session may address itself by either name.
  if [ -n "$name" ] && grep -qF -- "$name" "$file"; then echo ALLOW; return; fi
  if [ -n "$branch" ] && grep -qF -- "$branch" "$file"; then echo ALLOW; return; fi
  echo UNCLAIMED
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
  rm -rf "$tmp"
  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails failed"; return 1
}

BOARD=""; NAME=""; BRANCH=""
case "${1:-}" in
  --selftest) selftest; exit $? ;;
  -h|--help)  sed -n '2,33p' "$0"; exit 2 ;;
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
  echo "  - **Holds:** <local resources, or none>"
  echo "  - **Notes:** <anything a session on this machine must not stomp>"
  echo
  echo "One-off escape: ALLOW_UNCLAIMED_BOARD=1 git commit ..."
  echo
} >&2
exit 1
