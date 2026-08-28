#!/usr/bin/env bash
# worktree_sweep.sh — remove worktrees whose branch is already on origin/main,
# and say which ones somebody is sitting in right now.
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
# "not yet merged", and it answers the second question too — WHO IS LIVE.
#
# WHY LIVENESS IS REPORTED ON EVERY ROW, not just where it decides a removal.
# It used to be one veto among several, checked AFTER "has uncommitted changes".
# A worktree that was both dirty and live therefore printed only "3 uncommitted
# file(s)" and never revealed it had been written to minutes earlier. On
# 2026-08-20 a session read exactly that line, plus a branch with no upstream and
# a board block that did not say DONE, and concluded the work had been abandoned
# mid-task — while that session was still in it. Nothing was lost, but the read
# was wrong and the list had the evidence to prevent it and did not show it.
# An absent DONE means "not finished", which is not the same as "died".
#
# Board blocks state INTENT and go stale the moment a session stops updating
# them. A write timestamp states PRESENCE and cannot lie about it. Ask this
# before touching a worktree you did not create:
#
#   bash tools/worktree_sweep.sh --live
#
# WHAT IT REFUSES TO TOUCH, and each guard has caught something real:
#   * written to in the last 15 min — somebody is in it NOW, checked first
#   * uncommitted changes           — work in progress, however old it looks
#   * touched in the last N h       — a session may be thinking in it
#   * a detached HEAD               — no branch to check merged-ness against
#   * not an ancestor of origin/main — unmerged, i.e. the whole point of it
#   * a liveness probe that failed  — see FAILING CLOSED below
#
# FAILING CLOSED. The probe is `find -newermt`, and if it cannot answer, this
# script must not conclude "idle" — that reading deletes the worktree of whoever
# is typing in it. An unanswerable probe is reported as `unknown` and KEEPS.
# The old form sent find's stderr to /dev/null and treated no-output as
# not-recently-touched, which is the same silent-skip shape the browser tests
# were caught in: a check that stops working looks exactly like a check that
# passed. (`-newermt` with a relative string is fine on both GNU and BSD/macOS
# find. Asking for a raw mtime instead is what is not portable — `stat -c %Y`
# against `stat -f %m` — which is why this buckets by probe rather than
# subtracting timestamps.)
#
# THE OTHER DIRECTION — `--board`, and why it lives here rather than in its own tool.
#
# Everything above judges worktrees. Nothing judged the CLAIMS, and the header of
# this very file says why that matters: "Board blocks state INTENT and go stale the
# moment a session stops updating them." It said so while never reading one.
#
# Measured 2026-08-28: 26 blocks said ACTIVE against 16 worktrees. Sixteen claims
# were finished work nobody closed. The cost is this file's own thesis one level up
# — A LIVE CLAIM AND AN ABANDONED ONE LOOK IDENTICAL — and it is worse than a stale
# worktree, because the board is what a session reads to find out who else is
# working. That day a session read the board, reported the scorer area unclaimed,
# and started work beside two sessions already in it.
#
# So this reconciles the two lists and reports three things:
#   * ACTIVE claim, no worktree     — finished work whose block was never closed
#   * worktree, no ACTIVE claim     — unclaimed; the commit gate will refuse it
#   * ACTIVE claim, idle worktree   — nobody has been in it, so the block may be stale
#
# IT NEVER EDITS THE BOARD, and that is deliberate rather than unfinished. This file
# already refuses to `--apply` against other people's directories because git state
# cannot see intent. A board block is nothing BUT intent, so the argument is
# stronger here, not weaker: closing someone's claim because their worktree is gone
# destroys the record of what they held and why. `--apply` is refused with `--board`.
#
# The claim-matching rule is `guard_local_board.sh`'s and is not a second copy of
# it: heading compared EXACTLY after stripping the `machine/` prefix, never as a
# substring. That gate matched by substring once, and a block merely NAMING another
# worktree in its prose counted as a claim. Re-deriving the rule here is how the two
# would disagree again — so if that file's rule changes, change this with it.
#
# Usage:
#   bash tools/worktree_sweep.sh              # report only, changes nothing
#   bash tools/worktree_sweep.sh --live       # only who is live — no removals
#   bash tools/worktree_sweep.sh --board      # reconcile claims against worktrees
#   bash tools/worktree_sweep.sh --apply      # remove them
#   bash tools/worktree_sweep.sh --apply --hours 6
set -euo pipefail

APPLY=0
LIVE_ONLY=0
BOARD_ONLY=0
BOARD_FILE=""
HOURS=2
FRESH="15 minutes ago"
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --live) LIVE_ONLY=1 ;;
    --board) BOARD_ONLY=1 ;;
    --board-file) BOARD_FILE="${2:?--board-file needs a path}"; shift ;;
    --hours) HOURS="${2:?--hours needs a number}"; shift ;;
    -h|--help) sed -n '2,90p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ "$APPLY" = "1" ] && [ "$LIVE_ONLY" = "1" ]; then
  echo "--live reports only; it does not remove. Drop --apply." >&2; exit 2
fi
if [ "$APPLY" = "1" ] && [ "$BOARD_ONLY" = "1" ]; then
  echo "--board reports only; it never edits the board. Drop --apply." >&2; exit 2
fi
if [ "$LIVE_ONLY" = "1" ] && [ "$BOARD_ONLY" = "1" ]; then
  echo "--live and --board are different reports; run them separately." >&2; exit 2
fi

cd "$(git rev-parse --show-toplevel)"
git fetch -q origin 2>/dev/null || echo "note: could not fetch; judging against the origin/main you have" >&2

# Has anything under $1 been written since $2?
#   0 = yes   1 = no   2 = could not tell, and the caller must treat that as yes.
# find's own exit status is the signal; its output is only consulted when it
# succeeded. A timestamp this find cannot parse exits non-zero and lands on 2.
newer_than() {
  local w="$1" when="$2" out
  if out="$(find "$w" -not -path '*/.git/*' -type f -newermt "$when" 2>/dev/null)"; then
    [ -n "$out" ] && return 0
    return 1
  fi
  return 2
}

# live | recent | idle | unknown — for every worktree, whatever else is true of it.
liveness() {
  local w="$1" rc=0
  newer_than "$w" "$FRESH" || rc=$?
  case "$rc" in
    0) echo live; return ;;
    2) echo unknown; return ;;
  esac
  rc=0
  newer_than "$w" "$HOURS hours ago" || rc=$?
  case "$rc" in
    0) echo recent ;;
    2) echo unknown ;;
    *) echo idle ;;
  esac
}

# THE PRIMARY CHECKOUT IS THE FIRST ROW OF `git worktree list`, ALWAYS — not
# `rev-parse --show-toplevel`, which answers "the worktree I am standing in".
# Run from a worktree, that mistake identifies the wrong thing to protect and
# the sweep offers to delete the main checkout. Caught by the dry-run default
# on the first run from anywhere but the primary, which is the ordinary case:
# a session lives in its own worktree.
PRIMARY="$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')"
removed=0
kept=0
live=0

row() {  # verdict, name, liveness, reason
  printf '  %-7s %-32s %-8s %s\n' "$1" "$2" "$3" "$4"
}

# The machine-local board, found the way guard_local_board.sh finds it — from the
# COMMON git dir, so every worktree resolves the same file and this can never
# disagree with the gate about which board it is judging.
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

# Slugs of blocks whose Status line says ACTIVE, one per line.
#
# A block runs from its `### ` heading to the next one, so the status is read
# WITHIN that span — reading the file globally would let one ACTIVE line vouch for
# every block after it. The slug is the heading's first token with any `machine/`
# prefix stripped, which is exactly what claims_heading() compares against.
active_claims() {
  LC_ALL=C awk '
    /^###[[:space:]]/ {
      if (slug != "" && is_active) print slug
      s = $0
      sub(/^###[[:space:]]+/, "", s)
      while (index(s, "/")) sub(/^[^\/]*\//, "", s)
      sub(/[[:space:]].*$/, "", s)
      slug = s; is_active = 0; next
    }
    /^-[[:space:]]+\*\*Status:\*\*[[:space:]]*ACTIVE/ { is_active = 1 }
    END { if (slug != "" && is_active) print slug }' "$1"
}

if [ "$BOARD_ONLY" = "1" ]; then
  board="${BOARD_FILE:-$(board_path || true)}"
  if [ -z "$board" ] || [ ! -f "$board" ]; then
    echo "no machine-local board at ${board:-<unresolved>}."
    echo "That is not 'nothing is claimed' — it is 'nothing can be checked'."
    exit 2
  fi

  # Both lists, keyed by the two names a block may legitimately be headed with:
  # the worktree's directory basename or its branch. guard_local_board.sh accepts
  # either, so refusing one here would report claimed worktrees as unclaimed.
  wt_names=""; wt_dirs=""
  while IFS=$'\t' read -r w b; do
    [ -n "$w" ] || continue
    [ "$w" = "$PRIMARY" ] && continue
    wt_names="$wt_names$(basename "$w")"$'\n'
    [ "$b" != "DETACHED" ] && [ -n "$b" ] && wt_names="$wt_names$b"$'\n'
    wt_dirs="$wt_dirs$(basename "$w")	$w"$'\n'
  done < <(git worktree list --porcelain | awk '
    /^worktree /{w=$2}
    /^branch /{sub("refs/heads/","",$2); b=$2}
    /^detached/{b="DETACHED"}
    /^$/{if(w){print w"\t"b}; w=""; b=""}
    END{if(w){print w"\t"b}}')

  claims="$(active_claims "$board")"
  n_claims=$(printf '%s' "$claims" | grep -c . || true)
  stale=0; unclaimed=0; idle=0; ok=0

  echo "board: $board"
  echo
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    if printf '%s' "$wt_names" | grep -qxF -- "$slug"; then
      dir="$(printf '%s' "$wt_dirs" | awk -F'\t' -v s="$slug" '$1==s{print $2; exit}')"
      if [ -z "$dir" ]; then
        # headed with the branch rather than the directory: claimed, and the
        # liveness question belongs to whichever worktree carries that branch
        row 'claimed' "$slug" '-' 'a worktree carries this branch'; ok=$((ok+1)); continue
      fi
      age="$(liveness "$dir")"
      case "$age" in
        live|recent) row 'claimed' "$slug" "$age" 'worktree present and touched'; ok=$((ok+1)) ;;
        unknown)     row 'claimed' "$slug" "$age" 'liveness probe failed — assume in use'; ok=$((ok+1)) ;;
        *)           row 'IDLE' "$slug" "$age" "worktree present, untouched for >${HOURS}h — block may be stale"; idle=$((idle+1)) ;;
      esac
    else
      row 'STALE' "$slug" 'gone' 'ACTIVE claim, no worktree — close the block or say why'
      stale=$((stale+1))
    fi
  done <<< "$claims"

  while IFS=$'\t' read -r name dir; do
    [ -n "$name" ] || continue
    printf '%s' "$claims" | grep -qxF -- "$name" && continue
    branch="$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
    [ -n "$branch" ] && printf '%s' "$claims" | grep -qxF -- "$branch" && continue
    row 'UNCLAIM' "$name" "$(liveness "$dir")" 'worktree with no ACTIVE claim — the commit gate will refuse it'
    unclaimed=$((unclaimed+1))
  done <<< "$wt_dirs"

  echo "---"
  echo "$n_claims ACTIVE claim(s), $(printf '%s' "$wt_dirs" | grep -c . || true) worktree(s):"
  echo "  $ok claimed and in use   $idle idle   $stale stale   $unclaimed unclaimed"
  if [ "$stale" != "0" ]; then
    echo
    echo "A stale claim is not a tidiness problem. The board is what a session reads to"
    echo "find out who else is working, so every one of these makes it over-report — and"
    echo "a session that trusts the count will either duplicate work or avoid free ground."
    echo "Nothing here edits the board: closing a claim is the claimant's call, and the"
    echo "block records what they held and why."
  fi
  exit 0
fi

while IFS=$'\t' read -r w b; do
  [ -n "$w" ] || continue
  [ "$w" = "$PRIMARY" ] && continue
  name="$(basename "$w")"
  age="$(liveness "$w")"
  [ "$age" = "live" ] && live=$((live+1))

  if [ "$LIVE_ONLY" = "1" ]; then
    case "$age" in
      live)    row 'IN USE' "$name" "$age" 'written to in the last 15 min — do not touch' ;;
      unknown) row 'unsure' "$name" "$age" 'liveness probe failed — assume somebody is in it' ;;
    esac
    continue
  fi

  # Liveness first, so a worktree somebody is in is never described only by its
  # dirtiness. This is the ordering the 2026-08-20 misread turned on.
  if [ "$age" = "live" ]; then
    row 'KEEP' "$name" "$age" 'written to in the last 15 min — somebody is in it NOW'; kept=$((kept+1)); continue
  fi
  if [ "$age" = "unknown" ]; then
    row 'KEEP' "$name" "$age" 'liveness probe failed — refusing to guess idle'; kept=$((kept+1)); continue
  fi
  if [ "$b" = "DETACHED" ]; then
    row 'keep' "$name" "$age" 'detached HEAD — no branch to judge'; kept=$((kept+1)); continue
  fi
  dirty="$(cd "$w" && git status --porcelain | wc -l | tr -d ' ')"
  if [ "$dirty" != "0" ]; then
    row 'KEEP' "$name" "$age" "$dirty uncommitted file(s)"; kept=$((kept+1)); continue
  fi
  if [ "$age" = "recent" ]; then
    row 'KEEP' "$name" "$age" "touched in the last ${HOURS}h — somebody may be in it"; kept=$((kept+1)); continue
  fi
  if ! git merge-base --is-ancestor "$b" origin/main 2>/dev/null; then
    ahead="$(git rev-list --count origin/main.."$b" 2>/dev/null || echo '?')"
    row 'keep' "$name" "$age" "$ahead commit(s) not on main"; kept=$((kept+1)); continue
  fi

  if [ "$APPLY" = "1" ]; then
    git worktree remove "$w"
    git branch -d "$b" >/dev/null 2>&1 || true
    row 'removed' "$name" "$age" "($b)"
  else
    row 'WOULD' "$name" "$age" "REMOVE ($b) — merged, clean, idle"
  fi
  removed=$((removed+1))
done < <(git worktree list --porcelain | awk '
  /^worktree /{w=$2}
  /^branch /{sub("refs/heads/","",$2); b=$2}
  /^detached/{b="DETACHED"}
  /^$/{if(w){print w"\t"b}; w=""; b=""}
  END{if(w){print w"\t"b}}')

echo "---"
if [ "$LIVE_ONLY" = "1" ]; then
  if [ "$live" = "0" ]; then
    echo "nobody is live — no worktree written to in the last 15 min."
    echo "That is not a promise the tree is yours: a session can be thinking"
    echo "between writes. Check the board for intent before you assume."
  else
    echo "$live live. Presence, not intent — the board says what they MEAN to touch."
  fi
elif [ "$APPLY" = "1" ]; then
  echo "removed $removed, kept $kept ($live live)"
else
  echo "$removed removable, $kept kept, $live live — nothing changed. Re-run with --apply."
fi
