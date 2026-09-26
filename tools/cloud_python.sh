#!/usr/bin/env bash
# cloud_python.sh — give a Claude Code cloud container the Python bugarach requires.
#
# WHY. ADR-0011 set `requires-python = ">=3.14"` (#825, 2026-09-26). The cloud
# container ships Python 3.11, so from that merge on a cloud session could not
# install the package or collect the suite: every check fell to CI. The fix
# belongs in the environment's setup script, but that lives in a settings page the
# phone app does not expose, so it runs from here instead: versioned with the
# code, picked up by every session from `main`, and a no-op everywhere else.
#
# WHAT. Only when CLAUDE_CODE_REMOTE=true (the harness sets it in cloud containers
# and nowhere else): upgrade uv, whose preinstalled 0.8 release knows only the
# 3.14 release candidate, then `uv python install 3.14`. It installs the
# interpreter and nothing more. It does not replace `python3`, because tools that
# run bare `python3` rely on the container's own packages. To build the venv:
#
#     uv venv -p 3.14 .venv && uv pip install --python .venv/bin/python -e ".[dev]"
#
# SILENT ON SUCCESS. Its output would land in the session-start channel, which has
# a byte budget (CLAUDE.md, "Multi-session coordination"), so it prints one line
# only when the install fails. Once 3.14 is present it costs one `uv python find`.
#
# EXIT 0 always: a SessionStart hook that fails takes the session with it.
#
# USAGE  tools/cloud_python.sh             what .claude/settings.json runs
#        BUGARACH_CLOUD_PYTHON_FORCE=1 tools/cloud_python.sh   run it off-cloud too

set -uo pipefail

WANT="${BUGARACH_CLOUD_PYTHON_VERSION:-3.14}"

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || [ "${BUGARACH_CLOUD_PYTHON_FORCE:-0}" = "1" ] || exit 0

uv_cmd() {
  if python3 -m uv --version >/dev/null 2>&1; then python3 -m uv "$@"
  elif command -v uv >/dev/null 2>&1; then uv "$@"
  else return 127
  fi
}

# Already there: nothing to do, nothing to say.
uv_cmd python find "$WANT" >/dev/null 2>&1 && exit 0

python3 -m pip install -q -U uv >/dev/null 2>&1
if uv_cmd python install "$WANT" >/dev/null 2>&1 && uv_cmd python find "$WANT" >/dev/null 2>&1; then
  exit 0
fi
echo "!! [cloud-python] could not install Python ${WANT} in this container; the suite will not collect here. Try: pip install -U uv && uv python install ${WANT}"
exit 0
