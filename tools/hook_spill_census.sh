#!/usr/bin/env bash
# hook_spill_census.sh — what has the harness actually REFUSED to inject?
#
# Both SessionStart hooks carry a size budget, and both budgets were guessed. The
# comment justifying them said "the exact threshold is not observable from inside a
# session", which is true and which everyone read as "not observable". It is
# observable from OUTSIDE one: refusing an oversized hook payload is exactly what
# writes it to disk. Every spill this machine has ever suffered is still sitting in
#
#     <claude-config>/projects/<slug>/<session>/tool-results/hook-*-stdout.txt
#
# and every payload that arrived whole carries its own canary line into the session
# transcript. Between them they bracket the threshold from both sides.
#
# WHY IT MATTERS. On 2026-08-25 both hooks' headers put the smallest known failure at
# 13,414B. The record on this machine says 10,411B — three kilobytes tighter, and
# close enough to session_briefing.sh's 9,000B budget that "comfortably under" was
# no longer a fair description of it. It also says the largest payload known to have
# been delivered is 8,768B, which is what stopped that budget being LOWERED to the
# sibling's 8,000: doing so would have degraded FOUNDATIONS §9 to its claims on
# every ordinary run and called that normal.
#
# WHAT IT IS FOR. tests/test_session_briefing.py asserts the briefing fits its own
# budget — which is circular: raise the budget and the test still passes while the
# channel dies. This is the outside number that de-circularizes it.
#
# PRIVACY. This repo is public and sapper SAP004 blocks personal absolute paths.
# The census reads under $HOME but PRINTS ONLY SIZES AND COUNTS — never a project
# path, never a session transcript's contents. Keep it that way.
#
# USAGE
#   tools/hook_spill_census.sh            the table
#   tools/hook_spill_census.sh --values   key=value lines, for a test to parse
#   tools/hook_spill_census.sh --check N  exit 1 if a budget of N is not safely under
#                                         the smallest payload ever refused
#   tools/hook_spill_census.sh --selftest prove the parser on a synthetic tree
#
# EXIT  0 fine (or nothing to say)   1 --check failed   2 bad usage

set -uo pipefail

# The margin --check wants between a budget and the smallest observed spill. Not a
# safety factor pulled from nowhere: the briefing's own size tracks the board, the
# todo count and the handoff, so it moves between runs, and 1KB is roughly one more
# waiting-on-tony item plus a root handoff excerpt.
MARGIN=1000

config_root() { echo "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"; }

# Every project directory belonging to this repo — the primary checkout and every
# worktree, since hooks run in worktrees too and a spill there is the same spill.
project_dirs() {
  local base repo
  base=$(git rev-parse --show-toplevel 2>/dev/null) || return 0
  repo=$(basename "$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null | xargs dirname 2>/dev/null || echo "$base")")
  [ -z "$repo" ] && repo=$(basename "$base")
  find "$(config_root)" -maxdepth 1 -type d -name "*${repo}*" 2>/dev/null
}

# SPILLED. The file exists because the injection was refused; its size is the size
# that was refused. Only hook-*-stdout.txt — tool-results holds spilled output from
# ordinary tools as well, and those say nothing about the SessionStart limit.
spilled_sizes() {
  local d
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    find "$d" -path '*/tool-results/hook-*-stdout.txt' -type f \
      -exec stat -f '%z' {} \; 2>/dev/null \
      || find "$d" -path '*/tool-results/hook-*-stdout.txt' -type f \
           -printf '%s\n' 2>/dev/null
  done < <(project_dirs) | grep -E '^[0-9]+$' | sort -n
}

# DELIVERED. A payload that arrived carries its canary into the transcript. A
# payload that was SPILLED can also reach a transcript later — a session reads the
# spill file back, as one did on 2026-08-25 — so the canary of every spill is
# subtracted. Without that subtraction this reports a 10,492B "delivery" that never
# happened, which is the exact mistake the first pass at these numbers made.
canaries_seen() {
  local d
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    grep -hro 'briefing delivered: [0-9]* lines, [0-9]*B' "$d" 2>/dev/null
  done < <(project_dirs) | sed 's/.*, \([0-9]*\)B$/\1/' | sort -u
}

canaries_spilled() {
  local d f
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    find "$d" -path '*/tool-results/hook-*-stdout.txt' -type f 2>/dev/null
  done < <(project_dirs) | while IFS= read -r f; do
    tail -c 400 "$f" 2>/dev/null | grep -o 'briefing delivered: [0-9]* lines, [0-9]*B' | tail -1
  done | sed 's/.*, \([0-9]*\)B$/\1/' | sort -u
}

# comm compares as STRINGS, so both sides are sorted lexically and only the answer
# is put back in numeric order. Feeding it `sort -n` output is the kind of bug that
# reports a delivery that never happened — which is what it did on the first run.
delivered_sizes() { comm -23 <(canaries_seen) <(canaries_spilled) | sort -n; }

# The three numbers, as key=value so a caller never has to parse the table.
values() {
  local sp dl n
  sp=$(spilled_sizes); dl=$(delivered_sizes)
  n=$(printf '%s\n' "$sp" | grep -c '[0-9]')
  echo "spilled_count=${n}"
  echo "spilled_min=$(printf '%s\n' "$sp" | grep '[0-9]' | head -1)"
  echo "delivered_max=$(printf '%s\n' "$dl" | grep '[0-9]' | tail -1)"
}

# Each hook's budget, read from the script that owns it rather than restated here —
# a second copy of the number is a second thing to keep in step.
budgets() {
  local root; root=$(git rev-parse --show-toplevel 2>/dev/null) || return 0
  sed -n 's/.*BUGARACH_BRIEFING_BUDGET_BYTES:-\([0-9]*\)}.*/session_briefing.sh \1/p' \
      "$root/tools/session_briefing.sh" 2>/dev/null | head -1
  sed -n 's/.*BUGARACH_SESSION_START_BUDGET_BYTES:-\([0-9]*\)}.*/session_start_trimmed.sh \1/p' \
      "$root/tools/session_start_trimmed.sh" 2>/dev/null | head -1
}

table() {
  local sp_min dl_max n name b
  eval "$(values)"
  if [ "${spilled_count:-0}" -eq 0 ] && [ -z "${delivered_max:-}" ]; then
    echo "hook spill census: no record on this machine yet."
    echo "  Nothing has been refused and no canary has been seen, so there is no"
    echo "  outside number here. The budgets stand on their headers alone."
    return 0
  fi
  sp_min="${spilled_min:-}"; dl_max="${delivered_max:-}"; n="${spilled_count:-0}"

  echo "hook spill census — what the harness has refused, from this machine's record"
  echo
  printf '  %-38s %s\n' "payloads REFUSED (spilled to a file)" "$n"
  printf '  %-38s %s\n' "smallest one refused" "${sp_min:-—}B"
  printf '  %-38s %s\n' "largest one known DELIVERED whole" "${dl_max:-—}B"
  if [ -n "$sp_min" ] && [ -n "$dl_max" ] && [ "$dl_max" -lt "$sp_min" ]; then
    printf '  %-38s (%s, %s]\n' "so the threshold is somewhere in" "$dl_max" "$sp_min"
  elif [ -n "$sp_min" ] && [ -n "$dl_max" ]; then
    # Not an interval. Either the limit is not a plain byte count on our stdout, or
    # the record spans harness versions with different limits. Say so rather than
    # print an inverted range that reads like a measurement.
    printf '  %-38s\n' "!! a DELIVERY is larger than a REFUSAL —"
    echo "     the limit is not a plain byte count on this stdout, or this record"
    echo "     spans more than one harness version. Trust the refusal, not the range."
  fi
  echo
  echo "  A budget is safe when it is under the smallest refusal by ${MARGIN}B, and"
  echo "  useful when it is over the largest ordinary payload — a budget below that"
  echo "  degrades every run and calls it normal."
  echo
  while read -r name b; do
    [ -n "$name" ] || continue
    if [ -z "$sp_min" ]; then printf '  %-30s %6sB   (nothing refused yet)\n' "$name" "$b"
    elif [ "$b" -le $(( sp_min - MARGIN )) ]; then
      printf '  %-30s %6sB   ok, %sB under the smallest refusal\n' "$name" "$b" "$(( sp_min - b ))"
    elif [ "$b" -lt "$sp_min" ]; then
      printf '  %-30s %6sB   !! only %sB under it — thinner than the %sB margin\n' \
             "$name" "$b" "$(( sp_min - b ))" "$MARGIN"
    else
      printf '  %-30s %6sB   !! AT OR OVER a size already refused\n' "$name" "$b"
    fi
  done < <(budgets)
}

check() {
  local want="$1" sp_min
  eval "$(values)"
  sp_min="${spilled_min:-}"
  if [ -z "$sp_min" ]; then
    echo "no spill on record — nothing to check ${want}B against."
    return 0
  fi
  if [ "$want" -le $(( sp_min - MARGIN )) ]; then
    echo "ok: ${want}B is $(( sp_min - want ))B under the smallest payload ever refused (${sp_min}B)."
    return 0
  fi
  echo "!! ${want}B is not safely under the smallest payload ever refused (${sp_min}B)."
  echo "   Wanted at least ${MARGIN}B of margin; there is $(( sp_min - want ))B."
  return 1
}

# =================================================================================
# SELFTEST — the parser, driven over a synthetic tree, so it can be proved on a
# machine with no session history at all (CI has none, which is the point).
# =================================================================================
selftest() {
  local tmp fails=0 got
  tmp=$(mktemp -d) || { echo "cannot mktemp"; return 1; }
  mkdir -p "$tmp/projects/x-repo/sess1/tool-results"
  # A refused payload, with its canary in the tail — the shape that fooled the first
  # pass at these numbers into reporting it as a delivery.
  # Padded past the margin so --check has something realistic to be under; a 48-byte
  # "spill" leaves no budget that could satisfy a 1KB margin.
  { head -c 3000 /dev/zero | tr '\0' 'x'; printf '\nbriefing delivered: 9 lines, 4000B (budget 1B)\n'; } \
    > "$tmp/projects/x-repo/sess1/tool-results/hook-aaa-stdout.txt"
  # A transcript carrying both that canary (read back later) and a real delivery.
  printf 'x briefing delivered: 9 lines, 4000B y\nz briefing delivered: 3 lines, 1200B w\n' \
    > "$tmp/projects/x-repo/sess1.jsonl"

  t() { if [ "$2" = "$3" ]; then printf '  ok   %-50s\n' "$1"
        else printf '  FAIL %-50s (got %s, want %s)\n' "$1" "$2" "$3"; fails=$((fails+1)); fi }

  CLAUDE_CONFIG_DIR="$tmp" ; export CLAUDE_CONFIG_DIR
  project_dirs() { echo "$tmp/projects/x-repo"; }

  got=$(spilled_sizes | head -1)
  t "a refused payload is counted by its file size" "$got" \
    "$(wc -c < "$tmp/projects/x-repo/sess1/tool-results/hook-aaa-stdout.txt" | tr -d ' ')"
  t "canaries seen includes both"      "$(canaries_seen | tr '\n' ',')"     "1200,4000,"
  t "the refused one is subtracted"    "$(delivered_sizes | tr '\n' ',')"   "1200,"
  t "delivered_max is the real one"    "$(values | sed -n 's/delivered_max=//p')" "1200"

  # --check is the whole point: it must refuse a budget that is not under the floor.
  spilled_min_of() { values | sed -n 's/spilled_min=//p'; }
  check 1 >/dev/null 2>&1; t "a tiny budget passes --check" "$?" "0"
  check "$(spilled_min_of)" >/dev/null 2>&1; t "a budget AT the floor fails --check" "$?" "1"

  # No history at all must be quiet and successful, never a red CI on a fresh clone.
  project_dirs() { echo ""; }
  got=$(table); case "$got" in *"no record on this machine"*) t "empty history says so" ok ok ;;
                               *) t "empty history says so" "${got:0:20}" ok ;; esac
  check 99999 >/dev/null 2>&1; t "and --check stays quiet with no record" "$?" "0"

  rm -rf "$tmp"
  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails failed"; return 1
}

case "${1:-}" in
  --values)   values ;;
  --check)    [ $# -eq 2 ] || { echo "usage: $0 --check <bytes>" >&2; exit 2; }; check "$2" ;;
  --selftest) selftest ;;
  -h|--help)  sed -n '2,36p' "$0" ;;
  "")         table ;;
  *)          echo "usage: $0 [--values|--check <bytes>|--selftest]" >&2; exit 2 ;;
esac
