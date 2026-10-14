#!/usr/bin/env bash
# instrument: concurrency
# require-a-name-before-message.sh — a session messages another only once it has a name
# the other can reply to.
#
# THE GAP THIS CLOSES. Sessions message each other by session name (SendMessage), on
# this machine and across machines over Remote Control. A session nobody has renamed
# is addressed by its auto-generated title, which changes as the title does. On
# 2026-10-14 the Mac's armory session could not reach this machine's session by its
# local handle, only by whatever its title was at that moment. After Tony renamed it
# in VS Code ("065 bugarach coord"), the Mac reached it by that bare name. Tony's
# ruling the same day: rename every session at its start, and do not make it a line
# in CLAUDE.md, "the least reliable option of all the tools we have for this
# persisting behavior". So it is this hook.
#
# HOW IT KNOWS. A rename is written into the session's own transcript as a record of
# "type":"custom-title". Every hook is handed that transcript's path on stdin. No
# such record means the session still answers to an auto title.
#
# TWO MODES, one rule:
#   (no argument)    PreToolUse on SendMessage. Unnamed: BLOCK (exit 2), and say why.
#   --session-start  SessionStart. Unnamed: print one line telling the session to ask
#                    Tony for a name. Never blocks; a start cannot be refused.
#
# IT FAILS OPEN. If the transcript path is missing or unreadable, it allows: the
# record format is Claude Code's, not ours, and a format change must not stop every
# message on the estate. It never fails open on a transcript it CAN read.
#
# ESCAPE HATCH, deliberate: BUGARACH_ALLOW_UNNAMED=1, for a session that must send
# before Tony can rename it (a message expecting no reply, say).
#
#   require-a-name-before-message.sh --selftest   prove every branch can trigger
#
# EXIT CODES  0 = allow   2 = block (stderr is shown to the model)

set -uo pipefail

NAME_FORM='<machine> <repo> <role>, e.g. "065 bugarach coord"'

# The transcript path from the hook's JSON on stdin, with JSON's escaped backslashes
# undone and turned into forward slashes so Git Bash on Windows can open it.
transcript_from_stdin() {
  local payload path
  payload="$(cat 2>/dev/null)"
  path="$(printf '%s' "$payload" \
    | grep -o '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 \
    | sed 's/^"transcript_path"[[:space:]]*:[[:space:]]*"//; s/"$//; s/\\\\/\//g; s/\\/\//g')"
  printf '%s' "$path"
}

# 0 = named, 1 = unnamed, 2 = cannot tell (missing or unreadable transcript).
named() {
  local t="$1"
  [ -n "$t" ] && [ -r "$t" ] || return 2
  grep -q '"type":"custom-title"' "$t" && return 0
  return 1
}

gate() {
  [ "${BUGARACH_ALLOW_UNNAMED:-}" = "1" ] && return 0
  local t rc
  t="$(transcript_from_stdin)"
  named "$t"; rc=$?
  [ "$rc" -ne 1 ] && return 0
  {
    echo "BLOCKED: this session has no name another session can reply to."
    echo
    echo "It is still addressed by its auto-generated title, which changes as the title"
    echo "does, so a reply sent to it now can land nowhere. Ask Tony to rename this"
    echo "session (in VS Code: the session's rename) as $NAME_FORM,"
    echo "then send. A session cannot rename itself."
    echo
    echo "If this message expects no reply, BUGARACH_ALLOW_UNNAMED=1 lets it through."
  } >&2
  return 2
}

session_start() {
  local t rc
  t="$(transcript_from_stdin)"
  named "$t"; rc=$?
  [ "$rc" -ne 1 ] && return 0
  echo "!! unnamed session: ask Tony to rename it ($NAME_FORM) before any SendMessage; the send is blocked until then."
  return 0
}

# --- selftest ----------------------------------------------------------------
# A gate that cannot trigger is worse than no gate. Every branch proves itself here.
selftest() {
  local fails=0 rc out SELF="${BASH_SOURCE[0]}"
  SELFTEST_TMP="$(mktemp -d)" || return 2
  trap 'rm -rf "${SELFTEST_TMP:-}"' EXIT
  local tmp="$SELFTEST_TMP"

  printf '%s\n' '{"type":"user","message":"hi"}' '{"type":"ai-title","aiTitle":"Some title"}' > "$tmp/unnamed.jsonl"
  cp "$tmp/unnamed.jsonl" "$tmp/named.jsonl"
  printf '%s\n' '{"type":"custom-title","customTitle":"065 bugarach coord"}' >> "$tmp/named.jsonl"

  payload() { printf '{"session_id":"x","transcript_path":"%s","tool_name":"SendMessage"}' "$1"; }
  check() { # name expected_rc payload [env]
    if [ -n "${4:-}" ]; then out="$(payload "$3" | env "$4" bash "$SELF" 2>&1)"; rc=$?
    else out="$(payload "$3" | env -u BUGARACH_ALLOW_UNNAMED bash "$SELF" 2>&1)"; rc=$?; fi
    if [ "$rc" -eq "$2" ]; then printf '  PASS  %-44s (rc=%s)\n' "$1" "$rc"
    else printf '  FAIL  %-44s (rc=%s, expected %s)\n' "$1" "$rc" "$2"; fails=$((fails+1)); fi
  }

  check "renamed session: allow" 0 "$tmp/named.jsonl"
  check "unnamed session: BLOCK" 2 "$tmp/unnamed.jsonl"
  check "unnamed, BUGARACH_ALLOW_UNNAMED=1: allow" 0 "$tmp/unnamed.jsonl" BUGARACH_ALLOW_UNNAMED=1
  check "missing transcript: allow (fails open)" 0 "$tmp/nope.jsonl"
  check "no transcript_path at all: allow" 0 ""

  # On Windows the path arrives JSON-escaped: C:\\Users\\... must still be opened.
  # Only meaningful where there is a Windows form of the path to build.
  if command -v cygpath >/dev/null 2>&1; then
    local win; win="$(cygpath -w "$tmp/unnamed.jsonl" | sed 's/\\/\\\\/g')"
    check "JSON-escaped Windows path, unnamed: BLOCK" 2 "$win"
  fi

  out="$(payload "$tmp/unnamed.jsonl" | bash "$SELF" --session-start 2>&1)"; rc=$?
  if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "unnamed session"; then
    printf '  PASS  %-44s (rc=%s)\n' "session start, unnamed: one-line alarm" "$rc"
  else printf '  FAIL  %-44s (rc=%s)\n' "session start, unnamed: one-line alarm" "$rc"; fails=$((fails+1)); fi
  out="$(payload "$tmp/named.jsonl" | bash "$SELF" --session-start 2>&1)"; rc=$?
  if [ "$rc" -eq 0 ] && [ -z "$out" ]; then
    printf '  PASS  %-44s (rc=%s)\n' "session start, renamed: silent" "$rc"
  else printf '  FAIL  %-44s (rc=%s)\n' "session start, renamed: silent" "$rc"; fails=$((fails+1)); fi

  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails FAILED"; return 1
}

case "${1:-}" in
  --selftest)      selftest; exit $? ;;
  --session-start) session_start; exit $? ;;
  -h|--help)       sed -n '2,34p' "$0"; exit 0 ;;
  "")              gate; exit $? ;;
  *)               echo "unknown option: $1" >&2; exit 2 ;;
esac
