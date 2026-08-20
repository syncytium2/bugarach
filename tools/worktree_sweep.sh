#!/usr/bin/env bash
# worktree_sweep.sh — remove worktrees whose branch is already on origin/main.
#
# WHY THIS EXISTS. Several sessions run against this repo at once and each takes
# its own worktree, which is right. Nobody removes them afterwards, which is
# understandable — the session that could is the one that has just finished and
# is closing down. On 2026-08-20 the count reached 39 worktrees and 81 local
# branches, of which 22 and 66 were finished work.
#
# The cost is not disk. It is that A LIVE WORKTREE AND AN ABANDONED ONE LOOK
# IDENTICAL. A session scanning the list to find out who else is working cannot
# tell last week's finished branch from a colleague mid-edit, so it either stomps
# or freezes. Both happened in one day: one session read a worktree being written
# to as "unpushed and at risk", and another concluded nobody was working on CI
# while somebody was.
#
# So the list is only useful if presence MEANS something. This makes it mean
# "not yet merged".
#
# WHAT IT REFUSES TO TOUCH, and each guard has caught something real:
#   * uncommitted changes      — work in progress, however old it looks
#   * touched in the last N h  — a session may be thinking in it right now
#   * a detached HEAD          — no branch to check merged-ness against
#   * not an ancestor of origin/main — unmerged, i.e. the whole point of it
#
# Usage:
#   bash tools/worktree_sweep.sh              # report only, changes nothing
#   bash tools/worktree_sweep.sh --apply      # remove them
#   bash tools/worktree_sweep.sh --apply --hours 6
set -euo pipefail

APPLY=0
HOURS=2
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --hours) HOURS="${2:?--hours needs a number}"; shift ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

cd "$(git rev-parse --show-toplevel)"
git fetch -q origin 2>/dev/null || echo "note: could not fetch; judging against the origin/main you have" >&2

PRIMARY="$(git rev-parse --show-toplevel)"
removed=0
kept=0

while IFS=$'\t' read -r w b; do
  [ -n "$w" ] || continue
  [ "$w" = "$PRIMARY" ] && continue
  name="$(basename "$w")"

  if [ "$b" = "DETACHED" ]; then
    printf '  keep    %-38s detached HEAD — no branch to judge\n' "$name"; kept=$((kept+1)); continue
  fi
  dirty="$(cd "$w" && git status --porcelain | wc -l | tr -d ' ')"
  if [ "$dirty" != "0" ]; then
    printf '  KEEP    %-38s %s uncommitted file(s)\n' "$name" "$dirty"; kept=$((kept+1)); continue
  fi
  if [ -n "$(find "$w" -newermt "$HOURS hours ago" -not -path '*/.git/*' -type f 2>/dev/null | head -1)" ]; then
    printf '  KEEP    %-38s touched in the last %sh — somebody may be in it\n' "$name" "$HOURS"; kept=$((kept+1)); continue
  fi
  if ! git merge-base --is-ancestor "$b" origin/main 2>/dev/null; then
    ahead="$(git rev-list --count origin/main.."$b" 2>/dev/null || echo '?')"
    printf '  keep    %-38s %s commit(s) not on main\n' "$name" "$ahead"; kept=$((kept+1)); continue
  fi

  if [ "$APPLY" = "1" ]; then
    git worktree remove "$w"
    git branch -d "$b" >/dev/null 2>&1 || true
    printf '  removed %-38s (%s)\n' "$name" "$b"
  else
    printf '  WOULD REMOVE %-33s (%s) — merged, clean, idle\n' "$name" "$b"
  fi
  removed=$((removed+1))
done < <(git worktree list --porcelain | awk '
  /^worktree /{w=$2}
  /^branch /{sub("refs/heads/","",$2); b=$2}
  /^detached/{b="DETACHED"}
  /^$/{if(w){print w"\t"b}; w=""; b=""}
  END{if(w){print w"\t"b}}')

echo "---"
if [ "$APPLY" = "1" ]; then
  echo "removed $removed, kept $kept"
else
  echo "$removed removable, $kept kept — nothing changed. Re-run with --apply."
fi
