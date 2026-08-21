#!/usr/bin/env bash
# session_start_trimmed.sh — run the vendored session-start hook, but deliver the
# session board as a digest of LIVE claims instead of the whole file.
#
# WHY A WRAPPER AND NOT AN EDIT. `.claude/hooks/session-start.sh` is vendored from
# interface2 and carries "do NOT edit here" on line 1; CLAUDE.md makes that binding,
# because a file edited in place cannot be re-copied when upstream moves. Its own
# header invites exactly this: "A repo may layer its own repo-specific checks around
# this core; keep the core intact so it stays re-copyable." So the core runs unchanged
# and this filters its output.
#
# WHAT IT FIXES. The hook ends with `cat "$board"`. On 2026-08-20 that made the
# briefing 60,235 bytes / 868 lines, and the harness would not inject it: the session
# got a 2KB preview and a file path. The board header is at line 32; the preview ends
# at 26. The board therefore reached nobody — and took the worktree list, the MATLAB
# report and the unpushed-work alarm down with it, since they precede it in the same
# stream. tools/board_digest.sh renders the same board in ~45 lines.
#
# DEGRADE LOUDLY, the rule the vendored header sets for its own budget cuts. If the
# markers this filter depends on are not where it expects — upstream reformatted, the
# hook changed — it prints the ORIGINAL output untouched and says so. A silent
# passthrough would look like a working trim while delivering nothing, which is the
# failure being fixed, wearing a different hat.
#
# USAGE
#   tools/session_start_trimmed.sh     what .claude/settings.json wires as the hook
#   tools/session_start_trimmed.sh --selftest
#
# EXIT  0 always. A SessionStart hook that fails takes the session with it.

set -uo pipefail

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
ROOT=$(dirname "$HERE")
VENDORED="${ROOT}/.claude/hooks/session-start.sh"
DIGEST="${HERE}/board_digest.sh"
BUDGET_BYTES="${BUGARACH_BRIEFING_BUDGET_BYTES:-8000}"

# Replace the board dump with the digest.
#   $1 vendored stdout   $2 rendered digest   -> filtered text on stdout
#   exit 0 replaced   3 no board marker found   4 marker found but no tail marker
filter() {
  awk -v digest="$2" '
    BEGIN { seen = 0; skip = 0 }
    /^--- session board: .* ---$/ && !seen {
      seen = 1; skip = 1
      while ((getline line < digest) > 0) print line
      close(digest)
      next
    }
    skip && /^RULES:/ { skip = 0 }
    skip { next }
    { print }
    END {
      if (!seen) exit 3
      if (skip)  exit 4
    }
  ' "$1"
}

run() {
  local raw filtered board rendered rc
  if [ ! -x "$VENDORED" ] && [ ! -f "$VENDORED" ]; then
    echo "[session-start-trimmed] vendored hook missing: $VENDORED"
    return 0
  fi
  raw=$(mktemp) || { bash "$VENDORED"; return 0; }
  filtered=$(mktemp) || { bash "$VENDORED"; rm -f "$raw"; return 0; }
  rendered=$(mktemp) || { bash "$VENDORED"; rm -f "$raw" "$filtered"; return 0; }

  bash "$VENDORED" > "$raw"          # stderr flows straight through, as the hook expects

  # Take the board path from the hook's own marker, so the digest can never be of a
  # different file than the one the hook resolved.
  board=$(sed -n 's/^--- session board: \(.*\) ---$/\1/p' "$raw" | head -1)
  if [ -n "$board" ] && [ -f "$DIGEST" ]; then
    bash "$DIGEST" "$board" > "$rendered" 2>/dev/null
  fi

  filter "$raw" "$rendered" > "$filtered"; rc=$?

  # SIZE CANARY, and the reason there is one. The harness spills an oversized hook
  # to a file and injects a 2KB preview instead; the two hooks measured here on
  # 2026-08-20 were 60,235 and 13,414 bytes and BOTH were spilled. The exact
  # threshold is not observable from inside a session, so this does not guess it —
  # it holds a budget well under the smaller of the two known failures, re-renders
  # the board terse if the budget is blown, and prints the number either way so the
  # next session can see the creep instead of discovering it as a silence.
  if [ "$rc" -eq 0 ] && [ -s "$filtered" ]; then
    local bytes; bytes=$(wc -c < "$filtered" | tr -d ' ')
    if [ "${bytes:-0}" -gt "$BUDGET_BYTES" ] 2>/dev/null && [ -n "$board" ]; then
      bash "$DIGEST" --terse "$board" > "$rendered" 2>/dev/null
      filter "$raw" "$rendered" > "$filtered"
      bytes=$(wc -c < "$filtered" | tr -d ' ')
      echo "!! [session-start-trimmed] over ${BUDGET_BYTES}B — board digest re-rendered terse." >&2
    fi
  fi

  if [ "$rc" -eq 0 ] && [ -s "$filtered" ]; then
    cat "$filtered"
    echo "briefing delivered: $(wc -l < "$filtered" | tr -d ' ') lines, $(wc -c < "$filtered" | tr -d ' ')B" \
         "(board dump was $(wc -c < "$raw" | tr -d ' ')B before trimming; budget ${BUDGET_BYTES}B)"
  else
    cat "$raw"
    echo
    echo "!! [session-start-trimmed] could not trim the board dump (reason ${rc}) — the"
    echo "   briefing above is the FULL vendored output and may have been truncated on"
    echo "   the way into this session. Check tools/session_start_trimmed.sh against"
    echo "   .claude/hooks/session-start.sh; the markers it keys on have moved."
    echo "   Meanwhile: bash tools/board_digest.sh"
  fi
  rm -f "$raw" "$filtered" "$rendered"
  return 0
}

selftest() {
  local fails=0 tmp out rc
  tmp=$(mktemp -d) || { echo "cannot mktemp"; return 1; }

  {
    echo "===================== repo — SESSION START ====================="
    echo "branch: main    cwd: /somewhere"
    echo "--- worktrees ---"
    echo "/somewhere  abc123 [main]"
    echo "--- session board: /somewhere/SESSIONS.md ---"
    echo "# Machine-local session board"
    echo "### Mac/finished — long dead"
    echo "- **Status:** DONE"
    echo "- **Notes:** eight hundred more lines of this"
    echo "RULES: your own worktree; never commit on main;"
    echo "briefing took 3s"
    echo "==============================================================="
  } > "$tmp/raw.txt"
  printf -- '--- session board — LIVE CLAIMS ONLY (0 ACTIVE of 1) ---\n    Nothing is claimed.\n' > "$tmp/digest.txt"

  t() { # label haystack needle want
    local hit=no
    case "$2" in *"$3"*) hit=yes ;; esac
    if [ "$hit" = "$4" ]; then printf '  ok   %-52s\n' "$1"
    else printf '  FAIL %-52s (%s, wanted %s)\n' "$1" "$hit" "$4"; fails=$((fails+1)); fi
  }
  n() { # label got want
    if [ "$2" = "$3" ]; then printf '  ok   %-52s\n' "$1"
    else printf '  FAIL %-52s (got %s, want %s)\n' "$1" "$2" "$3"; fails=$((fails+1)); fi
  }

  out=$(filter "$tmp/raw.txt" "$tmp/digest.txt"); rc=$?
  n "a well-formed briefing filters cleanly"  "$rc" 0
  t "header survives"          "$out" "SESSION START"        yes
  t "worktree list survives"   "$out" "/somewhere  abc123"   yes
  t "board dump is gone"       "$out" "eight hundred more"   no
  t "dead block is gone"       "$out" "Mac/finished"         no
  t "digest is in its place"   "$out" "LIVE CLAIMS ONLY"     yes
  t "the tail survives"        "$out" "RULES: your own"      yes
  t "the canary survives"      "$out" "briefing took"        yes

  grep -v '^--- session board' "$tmp/raw.txt" > "$tmp/nomarker.txt"
  out=$(filter "$tmp/nomarker.txt" "$tmp/digest.txt"); rc=$?
  n "no board marker refuses (3), never silent"  "$rc" 3

  grep -v '^RULES:' "$tmp/raw.txt" > "$tmp/notail.txt"
  out=$(filter "$tmp/notail.txt" "$tmp/digest.txt"); rc=$?
  n "marker but no tail refuses (4)"             "$rc" 4

  rm -rf "$tmp"
  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails failed"; return 1
}

case "${1:-}" in
  --selftest) selftest; exit $? ;;
  -h|--help)  sed -n '2,29p' "$0"; exit 0 ;;
  *)          run; exit 0 ;;
esac
