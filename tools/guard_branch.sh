#!/usr/bin/env bash
# guard_branch.sh — refuse a commit made directly on the default branch.
#
# WHY THIS IS A SCRIPT AND NOT A LINE IN CLAUDE.md. "Never commit on main" was
# written as prose in CLAUDE.md and in docs/session_protocol.md. Prose in
# CLAUDE.md does not reliably change behaviour — it is long, it is read before
# there is anything to attach it to, and it gets skipped. That is the stated
# reason this project has sapper and the murderboard at all: a rule that matters
# gets mechanized, and only then written down.
#
# So this fires by itself, from .githooks/pre-commit, and needs nobody to
# remember it.
#
# The rule it enforces: work happens on a branch and lands on the default branch
# through a PR whose checks have passed (tools/merge_when_green.sh). A commit
# authored directly on main skips that entirely — and CI runs *after* a push to
# main, so it can report the breakage but never prevent it.
#
# ESCAPE HATCH, deliberate: `ALLOW_MAIN_COMMIT=1 git commit ...`. A guard with no
# override gets disabled wholesale the first time it is genuinely in the way,
# and then it protects nothing. Making the override explicit and one-shot keeps
# it visible instead.
#
# USAGE
#   tools/guard_branch.sh                 check the current repo (hook use)
#   tools/guard_branch.sh --branch NAME   check a hypothetical branch name
#   tools/guard_branch.sh --selftest      prove every branch of the logic fires
#
# EXIT  0 allowed   1 blocked   2 could not determine (never a silent pass)

set -uo pipefail

# The protected set. `master` is included so a repo renamed either way is covered.
PROTECTED="main master"

verdict() {
  # $1 = branch name, $2 = value of ALLOW_MAIN_COMMIT ("" if unset)
  local br="$1" override="${2:-}"
  [ -z "$br" ] && { echo UNKNOWN; return; }
  [ "$br" = "HEAD" ] && { echo UNKNOWN; return; }   # detached: cannot tell
  for p in $PROTECTED; do
    if [ "$br" = "$p" ]; then
      [ -n "$override" ] && { echo OVERRIDE; return; }
      echo BLOCK; return
    fi
  done
  echo ALLOW
}

selftest() {
  local fails=0
  t() { # name expected branch override
    local got; got=$(verdict "$3" "${4:-}")
    if [ "$got" = "$2" ]; then printf '  ok   %-42s\n' "$1"
    else printf '  FAIL %-42s (got %s, want %s)\n' "$1" "$got" "$2"; fails=$((fails+1)); fi
  }
  t "main is blocked"                 BLOCK    "main"      ""
  t "master is blocked"               BLOCK    "master"    ""
  t "a feature branch is allowed"     ALLOW    "fix-thing" ""
  t "a branch named main-ish is fine" ALLOW    "main-menu" ""
  t "override releases main"          OVERRIDE "main"      "1"
  t "override is irrelevant off main" ALLOW    "fix-thing" "1"
  t "detached HEAD -> UNKNOWN"        UNKNOWN  "HEAD"      ""
  t "empty branch -> UNKNOWN"         UNKNOWN  ""          ""
  echo
  [ "$fails" -eq 0 ] && { echo "all checks pass"; return 0; }
  echo "$fails failed"; return 1
}

case "${1:-}" in
  --selftest) selftest; exit $? ;;
  -h|--help)  sed -n '2,30p' "$0"; exit 2 ;;
  --branch)   BR="${2:-}" ;;
  "")         BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "") ;;
  *)          sed -n '2,30p' "$0"; exit 2 ;;
esac

case "$(verdict "$BR" "${ALLOW_MAIN_COMMIT:-}")" in
  ALLOW)    exit 0 ;;
  OVERRIDE) echo "guard_branch: committing on '$BR' — ALLOW_MAIN_COMMIT set."; exit 0 ;;
  UNKNOWN)
    echo "guard_branch: cannot determine the branch (detached HEAD?). Refusing."
    echo "  Set ALLOW_MAIN_COMMIT=1 if you mean it."
    exit 2 ;;
  BLOCK)
    cat >&2 <<EOF
guard_branch: refusing to commit directly on '$BR'.

  Work lands on '$BR' through a PR whose checks passed. A commit authored here
  skips that: CI runs AFTER a push to '$BR', so it can report a breakage but
  cannot prevent one.

  Move this work to a branch (your changes are untouched):
      git checkout -b <slug>
      git commit ...
      git push -u origin <slug> && gh pr create
      bash tools/merge_when_green.sh <pr>

  Genuinely meant it?  ALLOW_MAIN_COMMIT=1 git commit ...
EOF
    exit 1 ;;
esac
