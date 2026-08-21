#!/usr/bin/env bash
# board_digest.sh — print only the LIVE blocks of a session board.
#
# WHY THIS EXISTS. The vendored session-start hook ends by `cat`-ing the whole
# machine-local board. On 2026-08-20 that briefing measured 60,235 bytes across
# 868 lines, of which the board was 835. The harness refuses an injection that
# size: it truncated the briefing to a 2KB preview and spilled the rest to a
# file. `--- session board:` sits at line 32. The preview ends at line 26.
#
# So the board did not reach that session's context AT ALL — and it was also
# what evicted the MATLAB report, the worktree list and the unpushed-work alarm
# that follow it. The dump was not merely long. It was the reason the rest of
# the briefing went missing, in exchange for delivering nothing itself.
#
# 51 blocks, 8 of them ACTIVE. A session needs the 8. The other 43 are a record,
# and a record belongs in a file you open, not in every session's first 2KB.
#
# WHAT COUNTS AS LIVE. `- **Status:** ACTIVE`. Anything else — DONE, blocked,
# a bare heading — is history for this purpose. Per block the digest keeps the
# heading, Worktree, Touches and Holds; Doing/Landed/Notes stay in the file.
#
# TOUCHES. The paths a block expects to write. Today's three collisions were all
# path overlaps between differently-named branches, so the branch name is not the
# thing to compare — see docs/session_protocol_local.md.
#
# USAGE
#   tools/board_digest.sh                 digest the machine-local board
#   tools/board_digest.sh <board-file>    digest a named board
#   tools/board_digest.sh --selftest      prove every branch fires
#
# EXIT  0 always (a briefing component must never take the session down).

set -uo pipefail

# The one awk program, kept as a function so the selftest drives the real thing
# rather than a copy of it.  $1 board file, $2 terse flag (1 = headings + one field)
digest_body() {
  awk -v TERSE="${2:-0}" '
    function flush(   i, n) {
      if (!have) return
      total++
      if (!active) { buf_n = 0; have = 0; active = 0; return }
      nactive++
      printf "\n"
      n = (buf_n > CAP ? CAP : buf_n)
      for (i = 1; i <= n; i++) print buf[i]
      if (buf_n > CAP) print "    (block trimmed — the rest is in the board file)"
      buf_n = 0; have = 0; active = 0
    }
    BEGIN { CAP = (TERSE ? 3 : 10); buf_n = 0; have = 0; active = 0; total = 0; nactive = 0; keep = 0 }
    /^### / { flush(); have = 1; buf[++buf_n] = $0; keep = 0; next }
    !have { next }
    /^- \*\*Status:\*\* *ACTIVE/ { active = 1; next }
    /^- \*\*(Worktree|Touches|Holds):\*\*/ {
      buf[++buf_n] = $0
      keep = ($0 ~ /^- \*\*(Touches|Holds):\*\*/)
      next
    }
    /^- \*\*/ { keep = 0; next }
    # continuation lines of Touches/Holds — a path list and a resource caveat both
    # wrap, and half a sentence is worse than none
    keep && /^  [^ ]/ { buf[++buf_n] = $0; next }
    { keep = 0 }
    END { flush(); printf "%d %d\n", nactive, total > "/dev/stderr" }
  ' "$1"
}

# Print the digest for a board file. $1 board path, $2 terse flag.
render() {
  local board="$1" terse="${2:-0}" body counts nactive total
  if [ ! -f "$board" ]; then
    echo "--- session board: $board"
    echo "    (no board yet — the briefing scaffolds it; add your block before you start)"
    return 0
  fi
  # counts come back on stderr so the body stays a clean stdout stream
  local tmp; tmp=$(mktemp) || { cat "$board"; return 0; }
  body=$(digest_body "$board" "$terse" 2>"$tmp")
  counts=$(cat "$tmp"); rm -f "$tmp"
  nactive=${counts%% *}; total=${counts##* }
  [ -z "$nactive" ] && nactive=0
  [ -z "$total" ] && total=0

  echo "--- session board — LIVE CLAIMS ONLY (${nactive} ACTIVE of ${total}): $board ---"
  if [ "$nactive" -eq 0 ] 2>/dev/null; then
    echo "    Nothing is claimed on this machine right now."
  else
    printf '%s\n' "$body"
    echo
    echo "    Compare your paths against the Touches lines above BEFORE you start."
  fi
  echo "    Finished blocks stay in the file, not in this briefing. Claim yours as the"
  echo "    first act of the session — the commit gate fires hours after the waste."
}

selftest() {
  local fails=0 tmp out
  tmp=$(mktemp -d) || { echo "cannot mktemp"; return 1; }
  {
    echo "# board"
    echo
    echo "### Mac/live-one — a live task"
    echo "- **Status:** ACTIVE"
    echo "- **Worktree:** live-wt   **branch:** live-one"
    echo "- **Touches:** src/alpha.py,"
    echo "  tools/beta.sh"
    echo "- **Holds:** the venv, and the port it"
    echo "  serves on"
    echo "- **Notes:** a long note that should not travel into every briefing"
    echo
    echo "### Mac/finished-one — a finished task"
    echo "- **Status:** DONE 2026-08-20 — merged as PR #1"
    echo "- **Touches:** src/gamma.py"
    echo "- **Notes:** more history"
    echo
    echo "### Mac/finished-two — another finished task"
    echo "- **Status:** DONE 2026-08-19"
  } > "$tmp/board.md"
  printf '# board\n\n### Mac/x — all done\n- **Status:** DONE\n' > "$tmp/none.md"

  t() { # label haystack needle want(yes|no)
    local hit=no
    case "$2" in *"$3"*) hit=yes ;; esac
    if [ "$hit" = "$4" ]; then printf '  ok   %-52s\n' "$1"
    else printf '  FAIL %-52s (%s, wanted %s)\n' "$1" "$hit" "$4"; fails=$((fails+1)); fi
  }

  out=$(render "$tmp/board.md")
  t "live block survives"                "$out" "Mac/live-one"        yes
  t "DONE block is dropped"              "$out" "Mac/finished-one"    no
  t "second DONE block is dropped"       "$out" "Mac/finished-two"    no
  t "Touches line survives"              "$out" "src/alpha.py"        yes
  t "Touches continuation survives"      "$out" "tools/beta.sh"       yes
  t "Holds survives"                     "$out" "the venv"            yes
  t "Holds continuation survives"        "$out" "serves on"           yes
  t "Notes do not travel"                "$out" "should not travel"   no
  t "counts are reported"                "$out" "1 ACTIVE of 3"       yes
  t "it says what to compare"            "$out" "Compare your paths"  yes

  out=$(render "$tmp/board.md" 1)
  t "terse keeps the live heading"       "$out" "Mac/live-one"        yes
  t "terse keeps the Touches line"       "$out" "src/alpha.py"        yes
  t "terse drops the wrapped tail"       "$out" "serves on"           no
  t "terse says it trimmed"              "$out" "block trimmed"       yes

  out=$(render "$tmp/none.md")
  t "an all-DONE board says so"          "$out" "Nothing is claimed"  yes
  t "an all-DONE board counts honestly"  "$out" "0 ACTIVE of 1"       yes

  out=$(render "$tmp/absent.md")
  t "a missing board is named, not fatal" "$out" "no board yet"       yes

  rm -rf "$tmp"
  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails failed"; return 1
}

TERSE=0
if [ "${1:-}" = "--terse" ]; then TERSE=1; shift; fi

case "${1:-}" in
  --selftest) selftest; exit $? ;;
  -h|--help)  sed -n '2,32p' "$0"; exit 0 ;;
  "")         board=$(bash "$(dirname "$0")/guard_local_board.sh" --path 2>/dev/null)
              [ -z "$board" ] && { echo "[board-digest] not a git repo — no board to digest."; exit 0; }
              render "$board" "$TERSE" ;;
  *)          render "$1" "$TERSE" ;;
esac
exit 0
