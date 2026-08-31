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
# Named after THIS script. It used to read BUGARACH_BRIEFING_BUDGET_BYTES, which
# tools/session_briefing.sh also reads with a different default (9,000) — so one name
# meant two numbers, and setting it to drive either hook silently retuned the other,
# including session_briefing.sh's own selftest, which sets it to 1. (2026-08-25)
BUDGET_BYTES="${BUGARACH_SESSION_START_BUDGET_BYTES:-8000}"

# Replace the board dump with the digest, and slot the site line in above RULES.
#   $1 vendored stdout   $2 rendered digest   $3 site line (optional)
#   -> filtered text on stdout
#   exit 0 replaced   3 no board marker found   4 marker found but no tail marker
filter() {
  awk -v digest="$2" -v siteline="${3:-}" '
    BEGIN { seen = 0; skip = 0; said = 0 }
    /^--- session board: .* ---$/ && !seen {
      seen = 1; skip = 1
      while ((getline line < digest) > 0) print line
      close(digest)
      next
    }
    skip && /^RULES:/ { skip = 0 }
    # Inside the banner, beside the other standing reminders — not trailing after
    # the closing rule where it reads as debris that escaped the briefing.
    /^RULES:/ && !said && siteline != "" { print siteline; said = 1 }
    skip { next }
    { print }
    END {
      if (!seen) exit 3
      if (skip)  exit 4
    }
  ' "$1"
}

# THE SITE LINE. Nothing in this repo publishes bugarach.tonydefazio.com, so the
# page advances only when a person remembers `npm run deploy` — and a stale page
# looks exactly like a current one. On 2026-08-20 it had been three features behind
# for weeks and the way that got noticed was somebody opening it. So the distance
# is printed to whoever starts work, which is the earliest moment anybody is in a
# position to fix it.
#
# It must not cost the session anything: the tool caches its observation for hours,
# takes a 3-second network timeout, and exits 0 whatever it finds. If it is missing,
# slow, or offline this prints nothing at all rather than delaying the briefing.
# BUGARACH_SKIP_SITE_CHECK=1 turns it off; BUGARACH_SITE_STALENESS_CMD replaces the
# command, which is how the selftest drives this without a network.
site_line() {
  [ "${BUGARACH_SKIP_SITE_CHECK:-0}" = "1" ] && return 0
  # Never from a test run. tests/test_board_digest.py drives this whole wrapper,
  # and a suite that reaches the public internet fails for reasons that have
  # nothing to do with this repo — slowly, on an offline machine. A stub in
  # BUGARACH_SITE_STALENESS_CMD is how a test exercises the wiring instead.
  [ -n "${PYTEST_CURRENT_TEST:-}" ] && [ -z "${BUGARACH_SITE_STALENESS_CMD:-}" ] && return 0
  local cmd="${BUGARACH_SITE_STALENESS_CMD:-}" py out
  if [ -z "$cmd" ]; then
    [ -f "${HERE}/site_staleness.py" ] || return 0
    py="${ROOT}/.venv/bin/python"
    [ -x "$py" ] || py=$(command -v python3 2>/dev/null)
    [ -n "$py" ] || return 0
    cmd="\"$py\" \"${HERE}/site_staleness.py\" --brief --exit-zero"
  fi
  out=$(bash -c "$cmd" 2>/dev/null | head -1)
  [ -n "$out" ] && printf '%s\n' "$out"
  return 0
}

run() {
  local raw filtered board rendered rc siteline
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
  # A POINTER, not a dump. Tony, 2026-08-30: "the briefing should just be pointers."
  #
  # The digest was spliced inline and reached 22,296B on 2026-08-30 — on its own,
  # nearly three times the harness's measured spill threshold. The terse re-render
  # below fired, reported success, and still left 15,663B, so the alarm worked and
  # the remedy did not. A spilled briefing delivers none of the alarms above it,
  # which is the whole failure this trimming exists to prevent.
  #
  # The digest is still GENERATED IN FULL — it is written beside the board it
  # describes, so nothing is lost and a session that wants it is one `cat` away.
  # What the briefing carries is the count and the path.
  if [ -n "$board" ] && [ -f "$DIGEST" ]; then
    local full active live
    full="$(dirname "$board")/BOARD_DIGEST.txt"
    if bash "$DIGEST" "$board" > "$full" 2>/dev/null; then
      active=$(grep -c 'Status:.*ACTIVE' "$board" 2>/dev/null || echo 0)
      live=0
      while IFS= read -r wt; do
        [ -d "$wt" ] && live=$((live + 1))
      done <<< "$(git worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p')"
      {
        echo "--- session board: $board ---"
        echo "   ${active} ACTIVE claim(s); ${live} live worktree(s) on this machine."
        echo "   A claim with no worktree is very likely finished and not yours to close."
        echo "   FULL DIGEST (regenerated just now):  $full"
        echo "   CLAIM BEFORE YOUR FIRST FILE WRITE — the commit gate fires hours later,"
        echo "   which is after the collision. tools/guard_local_board.sh"
      } > "$rendered"
    fi
  fi

  siteline=$(site_line)
  filter "$raw" "$rendered" "$siteline" > "$filtered"; rc=$?

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
      filter "$raw" "$rendered" "$siteline" > "$filtered"
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

  # The site line — the whole point of which is that it reaches the briefing.
  out=$(BUGARACH_SITE_STALENESS_CMD='echo "site: 2 commits behind"' site_line)
  t "site line is produced"    "$out" "2 commits behind"  yes
  out=$(BUGARACH_SKIP_SITE_CHECK=1 \
        BUGARACH_SITE_STALENESS_CMD='echo "site: 2 commits behind"' site_line)
  t "opt-out silences it"      "$out" "site:"             no
  out=$(BUGARACH_SITE_STALENESS_CMD='exit 9' site_line)
  t "a broken checker prints nothing" "$out" "site:"      no
  out=$(BUGARACH_SITE_STALENESS_CMD='printf "one\ntwo\n"' site_line)
  t "only one line ever reaches the budget" "$out" "two"  no

  out=$(filter "$tmp/raw.txt" "$tmp/digest.txt" "site: 2 commits behind"); rc=$?
  n "a briefing carrying the site line still filters" "$rc" 0
  t "site line lands in the briefing"   "$out" "2 commits behind"  yes
  t "and the briefing is otherwise intact" "$out" "RULES: your own" yes
  # It goes ABOVE the standing reminders, not after the closing rule where a
  # trailing line reads as debris rather than as part of the briefing.
  printf '%s' "$out" | awk '/^site: /{s=NR} /^RULES:/{r=NR} END{exit !(s && r && s < r)}'
  n "and above RULES, not trailing off the end" "$?" 0

  out=$(filter "$tmp/raw.txt" "$tmp/digest.txt" ""); rc=$?
  n "no site line is not an error"           "$rc" 0
  t "and nothing is inserted"          "$out" "site: "            no

  out=$(filter "$tmp/nomarker.txt" "$tmp/digest.txt" "site: 2 commits behind"); rc=$?
  n "a refused filter is still a refusal"    "$rc" 3

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
