#!/usr/bin/env bash
# bugarach-specific SessionStart briefing — runs ALONGSIDE the vendored generic hook
# (.claude/hooks/session-start.sh), wired as a separate entry in .claude/settings.json.
#
# Why a separate script rather than edits to that file: it carries a vendoring stamp
# and must stay byte-identical to interface2's tools/session-start.hook.sh so it can be
# re-copied. Its own header invites exactly this — "a repo may layer its own
# repo-specific checks around this core; keep the core intact".
#
# WHAT THIS EXISTS TO FIX, and it is not a nicety. CLAUDE.md's first line says to read
# docs/FOUNDATIONS.md at session start. On 2026-08-13 a session ran an entire day of
# work without doing so, and proposed calibrating the detectors until TTX slices stopped
# showing coordination — the dominant-paradigm assumption that TTX silences the field,
# which this project's own data refutes and which FOUNDATIONS forbids in terms. Tony:
# "claude.md is the first thing you ignore. we have built tools for this purpose."
#
# A rule written in a file that must be read to be obeyed is not mechanized. This is:
# the facts that BIND are injected into every session's context whether anyone opens
# the file or not.
#
# COST: local only — a couple of file reads and a git config lookup, milliseconds. It is
# deliberately NOT budget-gated and runs FIRST. interface2 learned that the hard way:
# their cross-team watch was written at the bottom of the briefing, sat behind a spent
# budget, and never ran once. A channel dropped for budget is the "filed but unread"
# failure it was built to prevent.

set +e
root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -z "$root" ] && exit 0
cd "$root" || exit 0

echo "=================== bugarach — WHAT BINDS THIS SESSION ==================="

# --- 1. the facts about the preparation, straight out of FOUNDATIONS ----------
# Extracted rather than restated, so this cannot drift from the canonical file.
if [ -r docs/FOUNDATIONS.md ]; then
  awk '/^## 9\. Facts about the preparation/{f=1} /^## 10\./{f=0} f' docs/FOUNDATIONS.md
else
  echo "!! docs/FOUNDATIONS.md is missing — that file is canonical truth. Stop and find out why."
fi

echo
echo "FOUNDATIONS is canonical and wins over anything said in conversation."
echo "For facts about the PREPARATION that it does not cover, the authority is"
echo "syncytium2/foundations FOUNDATIONS §15 — check it before assuming what a"
echo "condition does. Do not reason from textbook priors where the lab has a finding."

# --- 1b. finished work that only Tony can move ---------------------------------
# `status: open` means somebody should do this. It does not distinguish "nobody has
# started" from "it is DONE and waiting on a human to press send" -- and the second
# kind drowns in a list of fifty. The PySpike report sat written-but-unfiled for
# twelve days partly because nothing told anyone it was ready (2026-08-24). These
# print first, loudly, and name the one action left.
# README.md documents the format, so it carries the frontmatter as an EXAMPLE and
# would otherwise report itself as a waiting item -- it did, first run.
waiting=$(grep -l '^status: waiting-on-tony[[:space:]]*$' docs/todo/*.md 2>/dev/null \
          | grep -v '/README\.md$' | wc -l | tr -d ' ')
if [ "${waiting:-0}" -gt 0 ]; then
  echo
  echo ">> ${waiting} item(s) FINISHED and waiting on Tony — nothing else unblocks these:"
  for f in docs/todo/*.md; do
    [ -r "$f" ] || continue
    [ "$(basename "$f")" = "README.md" ] && continue
    grep -q '^status: waiting-on-tony[[:space:]]*$' "$f" 2>/dev/null || continue
    echo "   $(sed -n 's/^# //p' "$f" | head -1 | cut -c1-70)"
    echo "     $f"
    # The action line is the item's own one-sentence answer to "what do I do?".
    sed -n 's/^waiting: //p' "$f" | head -1 | sed 's/^/     -> /'
  done
fi

# --- 2. open threads: filed-but-unread is luck, not a channel -----------------
opens=$(grep -l '^status: open[[:space:]]*$' docs/todo/*.md 2>/dev/null | wc -l | tr -d ' ')
feedback=$(grep -l '^status: open[[:space:]]*$' docs/sapper_feedback/*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "${opens:-0}" -gt 0 ] || [ "${feedback:-0}" -gt 0 ]; then
  echo
  echo "--- open threads: ${opens} todo, ${feedback} sapper_feedback ---"
  for f in docs/todo/*.md docs/sapper_feedback/*.md; do
    [ -r "$f" ] || continue
    grep -q '^status: open[[:space:]]*$' "$f" 2>/dev/null || continue
    printf '   %-58s %s\n' "$(basename "$f")" "$(sed -n 's/^# //p' "$f" | head -1 | cut -c1-64)"
  done
fi

# --- 3. is the commit gate actually installed in THIS clone? ------------------
# core.hooksPath is per-clone and stored in .git/config, so it travels with nothing.
# docs/todo/2026-08-13-hookspath-is-opt-in-per-clone.md is the writeup; this is the
# part of it that can fire by itself.
if [ "$(git config --get core.hooksPath 2>/dev/null)" = ".githooks" ]; then
  echo
  echo "commit gates: ACTIVE (branch guard + sapper run on every commit)"
else
  echo
  echo "!! commit gates: OFF in this clone — the branch guard and sapper are NOT running."
  echo "   git config core.hooksPath .githooks"
fi

# --- 4. the gates that apply before work is handed over ----------------------
# Listed because these are the ones sessions skip. Every item here was skipped by
# a session that had read neither CLAUDE.md nor this list.
echo
echo "--- gates, before you hand anything over ---"
echo "   document deliverable (report, explainer, methodology, figure + caption)?"
echo "     -> /murderboard <artifact> FIRST. Not a first draft. docs/doc_review_process.md"
echo "   landing work?  branch + green PR; never commit on main."
echo "   a visual finding?  render the figure and show it — do not describe it."
echo "     -> tools/make_diagnostic.py, tools/make_generator_figures.py"
echo "   writing to the darkroom?  it is shared across machines — claim it on docs/SESSIONS.md."

# --- 5. where does figure output actually go on THIS machine? -----------------
# Printed rather than left to be asked about. On 2026-08-17 a session reported the
# darkroom unavailable and skipped its export while Dropbox sat mounted and visible
# in Finder: BUGARACH_DARKROOM was exported from a ~/.zshrc, which zsh reads for
# interactive shells only, so nothing a session runs ever saw it. FOUNDATIONS §5 now
# carries the rule; this is the part of it that fires without being read.
#
# The env branch is pure shell so the common case costs nothing. Only discovery pays
# for a python spawn, and paths.py imports stdlib alone, so it works in a worktree
# with no venv (docs/todo/2026-08-15-worktrees-import-the-primary-checkouts-src.md)
# and on a machine with no dependencies installed.
echo
if [ -n "${BUGARACH_DARKROOM:-}" ]; then
  if [ -d "$BUGARACH_DARKROOM" ]; then
    echo "darkroom: \$BUGARACH_DARKROOM -> $BUGARACH_DARKROOM"
  else
    echo "!! darkroom: \$BUGARACH_DARKROOM is set to a path that does not exist:"
    echo "   $BUGARACH_DARKROOM"
  fi
else
  found=$(PYTHONPATH=src python3 -c 'from bugarach.paths import discover_darkroom
p = discover_darkroom()
print(p if p else "")' 2>/dev/null)
  if [ -n "$found" ]; then
    echo "darkroom: found via Dropbox info.json -> $found"
  else
    echo "!! darkroom: not found — figure/report exports will be SKIPPED, not failed."
    echo "   python -m bugarach.paths   says what this machine can see"
  fi
fi

# --- 5b. the machine-local board is a precondition, not a suggestion ---------
# The vendored hook prints "(no board yet — create it ...)" and that has proved
# too quiet: on 2026-08-18 a session read it, worked all day across two worktrees
# and never created the board, while four others ran on this machine. So the
# board is scaffolded here if absent — a session should only ever have to add its
# own block — and tools/guard_local_board.sh refuses the commit until it has.
board=$(bash tools/guard_local_board.sh --path 2>/dev/null)
if [ -n "$board" ]; then
  if [ ! -f "$board" ]; then
    mkdir -p "$(dirname "$board")" 2>/dev/null
    {
      echo "# Machine-local session board — $(hostname -s 2>/dev/null || echo this machine)"
      echo
      echo "**Not in git, and that is the point.** This half of the board carries what"
      echo "cannot travel: which session holds the primary checkout, a MATLAB process, the"
      echo "venv, a port, the darkroom mount. Anything another MACHINE can see belongs on"
      echo "\`docs/SESSIONS.md\` instead."
      echo
      echo "Claiming is enforced: \`.githooks/pre-commit\` refuses a commit from a worktree"
      echo "with no block here. But that gate fires at your FIRST COMMIT, which is after"
      echo "the work exists — so write your block when you pick up the task, and mark it"
      echo "DONE on the way out. Blocks carry a \`Touches:\` line naming the paths they"
      echo "expect to write: on 2026-08-20 three sessions duplicated each other's work and"
      echo "no two of them shared a branch name, but all three overlapped in paths."
      echo
      echo "The session briefing shows only ACTIVE blocks (\`tools/board_digest.sh\`)."
      echo "Finished ones stay here as the record; move them under \`## Archive\` when the"
      echo "live list gets long."
      echo
      echo "---"
      echo
    } > "$board" 2>/dev/null
    echo
    echo "--- machine-local board CREATED: $board"
    echo "    It was missing. Add a block for this worktree before you commit —"
    echo "    the pre-commit gate refuses until you do."
  elif ! bash tools/guard_local_board.sh >/dev/null 2>&1; then
    echo
    echo "--- !! this worktree has NO block on the machine-local board"
    echo "    $board"
    echo "    Add one before starting; the pre-commit gate refuses the commit otherwise."
  fi
fi

# --- 6. is anything mid-flight? ----------------------------------------------
if [ -f HANDOFF.md ]; then
  echo
  echo "--- !! HANDOFF.md present — work is in flight, read it before starting ---"
  head -20 HANDOFF.md
fi

echo "========================================================================="
exit 0
