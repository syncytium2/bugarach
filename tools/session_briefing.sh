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
# ---------------------------------------------------------------------------------
# AND ON 2026-08-25 IT STOPPED ARRIVING. This script emitted 17,568 bytes. The harness
# refuses an injection that size: it spilled the output to a file and injected a 2KB
# preview, which ended at line 27 — inside the FOUNDATIONS extract. Everything past
# byte 2,000 reached nobody:
#
#     6,138  the waiting-on-tony alarm, whose own comment says it "prints first, loudly"
#     7,026  70 open threads  (9,658B — the single largest thing here, and the least
#                              actionable: "read as history, not a queue")
#    16,880  whether the commit gates are installed in this clone
#    16,926  the handover gates, including "document deliverable -> /murderboard FIRST"
#    17,495  where darkroom output goes on this machine
#    17,569  !! HANDOFF.md present — work is in flight
#
# The last line is the sharpest: this script is the ONLY thing in the tree that reads
# HANDOFF.md, and its alarm sat 15.5KB past the cut. A root handoff — the mechanism
# CLAUDE.md relies on for "something is in flight" — could not have reached any session.
#
# This is the SAME incident as 2026-08-20, in the other hook. The fix was built then —
# budget, terse re-render, size canary, degrade loudly — and applied only to
# tools/session_start_trimmed.sh. This header used to argue against adopting it:
# "COST: local only ... It is deliberately NOT budget-gated and runs FIRST." That was a
# claim about RUNTIME cost and it was true. The failure was never runtime. It was size,
# and refusing a budget is what made the whole channel silent instead of merely shorter.
#
# WHAT CHANGED
#   1. ORDER. The bounded alarms lead — in flight, waiting-on-tony, commit gates, board,
#      darkroom, handover gates. Together they cost ~1.5KB, so they survive even a 2KB
#      preview if the budget machinery below ever fails. The FOUNDATIONS facts follow.
#      The open-threads dump, 55% of the old payload, is now a count and a pointer.
#   2. BUDGET. BUGARACH_BRIEFING_BUDGET_BYTES, default 9,000 — see briefing_budget()
#      below for where that number comes from. Over budget, the FOUNDATIONS extract
#      degrades to its bolded claims plus a read-the-file pointer, and says so both in
#      the output and on stderr.
#   3. CANARY. It prints its own size every run, like the other hook. The 2026-08-20
#      note asked the next session to WATCH THAT NUMBER; this one had no number to watch,
#      which is how it crossed the line unobserved.
#
# The alarms are never budgeted. Dropping a channel for budget is the "filed but unread"
# failure it exists to prevent — interface2 learned that when their cross-team watch sat
# at the bottom of a briefing behind a spent budget and never ran once. What is budgeted
# here is the bulk, and the bulk was a list nobody was reading.
#
# ---------------------------------------------------------------------------------
# 2026-08-25, LATER THE SAME DAY. Four things the above got right in principle and
# wrong in placement or in arithmetic:
#
#   THE CANARY PRINTED LAST, which is the one position a spilled payload cannot
#   deliver. A spill keeps the first ~2KB and discards the rest, so a size line at the
#   bottom reports only in the case where nothing is wrong. It is line 1 now. That is
#   the whole point of a canary: it has to be the part that survives.
#
#   THE LADDER HAD NO FLOOR. deliver() re-rendered terse, and printed it whatever it
#   measured. A terse render still over budget shipped labelled "(TERSE", which reads
#   as a working degrade. It now says STILL OVER, on stdout and on stderr.
#
#   THE ALARMS WERE BOUNDED IN LINES, NOT BYTES. `head -14 HANDOFF.md` is fourteen
#   lines, and fourteen 300-character lines is 4KB — enough to push the alarms this
#   file reordered to the front straight back out of the preview. bound_bytes() caps
#   them, cutting only at a line end or an ASCII space so a multibyte character is
#   never split. (This repo has already shipped mojibake once, from an in-place
#   rewrite of prose; see docs/reviews/2026-08-25-the-session-hooks_2026-08-25.md.)
#
#   ONE ENV VAR MEANT TWO THINGS. BUGARACH_BRIEFING_BUDGET_BYTES was read by BOTH
#   hooks, defaulting to 9,000 here and 8,000 in session_start_trimmed.sh. Setting it
#   to drive one silently retuned the other, including in this file's own selftest,
#   which sets it to 1. Each script now reads the variable named after it; the sibling
#   takes BUGARACH_SESSION_START_BUDGET_BYTES.
#
# AND THE THRESHOLD IS OBSERVABLE AFTER ALL — see briefing_budget() below.
#
# USAGE
#   tools/session_briefing.sh              what .claude/settings.json wires as the hook
#   tools/session_briefing.sh --selftest   prove the budget ladder and extractor fire
#   tools/hook_spill_census.sh             what the harness has actually refused
#
# EXIT  0 always. A SessionStart hook that fails takes the session with it.

set +e
root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -z "$root" ] && exit 0
cd "$root" || exit 0

# THE NUMBER, and it is measured now rather than inferred. This used to read "the
# exact threshold is not observable from inside a session". It is observable from
# outside one: every payload the harness has ever refused is still on disk, because
# refusing it is what writes it there —
#
#   <claude-config>/projects/<slug>/<session>/tool-results/hook-*-stdout.txt
#
# tools/hook_spill_census.sh reads that record. Against this machine's history on
# 2026-08-25 it reports a band four kilobytes tighter than the guess above:
#
#   largest payload DELIVERED whole      8,768B   (this briefing, root HANDOFF present)
#   smallest payload SPILLED            10,186B   (of 55 refusals on record)
#   therefore the threshold is in       (8,768, 10,186]
#
# 9,000 stays, and the census is why rather than the guess being why. Two things
# pin it from both sides: it must sit under the smallest observed spill, and it must
# sit ABOVE the ordinary briefing — 8,016B bare, 8,768B with a root handoff. Lowering
# it to match the sibling's 8,000, which was this file's first instinct, would have
# degraded §9 to its claims on every single run and called that normal.
#
# Read inside deliver(), never captured at load, so a caller can override it.
# The variable is named after THIS script: the sibling hook reads
# BUGARACH_SESSION_START_BUDGET_BYTES, because sharing one name meant setting it to
# test either hook silently retuned the other.
briefing_budget() { echo "${BUGARACH_BRIEFING_BUDGET_BYTES:-9000}"; }

# Cap a variable-length alarm at a byte budget, cutting ONLY at a line end or an
# ASCII space — never mid-character, which is how prose becomes mojibake. LC_ALL=C
# so length()/substr() count bytes in every awk; an ASCII space cannot be part of a
# UTF-8 multibyte sequence, so a cut located at one is always on a character
# boundary.  $1 = cap in bytes, text on stdin.
bound_bytes() {
  LC_ALL=C awk -v cap="$1" '
    function trim(s, room,   c, i) {
      if (length(s) <= room) return s
      c = substr(s, 1, room)
      i = length(c)
      while (i > 0 && substr(c, i, 1) != " ") i--
      return (i > 1 ? substr(c, 1, i - 1) " […]" : "")
    }
    { room = cap - used
      if (room <= 0) { over = 1; next }
      line = trim($0, room)
      if (line == "" && $0 != "") { over = 1; next }
      print line
      used += length(line) + 1
      if (line != $0) over = 1 }
    END { if (over) print "   […] truncated at " cap "B — read the file" }'
}

# The variable alarms spend from ONE shared allowance, in the order they are
# rendered, so what is bounded is the block rather than each piece separately. A live
# root handoff renders first and therefore outranks the waiting list, which is the
# priority the ordering already asserts; the per-call caps stop either one alone from
# eating the allowance.  $1 = per-call cap, $2 = text.
#
# WHY THE ALLOWANCE IS 1,400 AND NOT 1,000. The first cut of this said 1,000, sized so
# canary + banner + both variable alarms + ~690B of fixed alarms held the whole block
# under a 2KB preview. That number was measured on a configured machine, where the
# fixed alarms collapse to one line each: "commit gates: ACTIVE", "darkroom: -> ...".
# On a FRESH CLONE every one of them fires at full length — gates OFF with its fix,
# no board with its path, darkroom not found with its probe — and the block runs past
# 2.3KB no matter what the variable alarms do. Squeezing the waiting list to make room
# for that is backwards twice over: it truncates the one list with a person waiting at
# the end of it, in order to protect standing context that has no deadline.
#
# So the block is NOT held under 2KB, and the guarantee is stated on position instead:
# the alarms that cannot wait — a live handoff, work finished and waiting on a person,
# and whether the commit gates are installed — are rendered first and land inside the
# first 2,000 bytes whatever else is wrong with the machine. That is what the ordering
# was for. tests/test_session_briefing.py asserts the offsets, not the total.
ALARM_ROOM=1400

# A named function rather than a loop inlined into emit_bounded's argument: the body
# carries an apostrophe and a quoted question, and nesting that inside "$( ... )" is
# a parse hazard for no gain.
waiting_list() {
  local f
  for f in docs/todo/*.md; do
    [ -r "$f" ] || continue
    [ "$(basename "$f")" = "README.md" ] && continue
    grep -q '^status: waiting-on-tony[[:space:]]*$' "$f" 2>/dev/null || continue
    echo "   $(sed -n 's/^# //p' "$f" | head -1 | cut -c1-70)"
    echo "     $f"
    # The action line is the item's own one-sentence answer to "what do I do?".
    sed -n 's/^waiting: //p' "$f" | head -1 | sed 's/^/     -> /'
  done
}

emit_bounded() {
  local cap="$1" text="$2" room
  [ -z "$text" ] && return 0
  room=$ALARM_ROOM
  [ "$cap" -lt "$room" ] && room=$cap
  [ "$room" -le 0 ] && { echo "   […] alarm allowance spent — read the file"; return 0; }
  text=$(printf '%s\n' "$text" | bound_bytes "$room")
  printf '%s\n' "$text"
  ALARM_ROOM=$(( ALARM_ROOM - $(printf '%s\n' "$text" | wc -c | tr -d ' ') ))
  [ "$ALARM_ROOM" -lt 0 ] && ALARM_ROOM=0
  return 0
}

# =================================================================================
# The FOUNDATIONS extract, and its degraded form. Extracted rather than restated so
# this cannot drift from the canonical file — and the terse form is that same
# extraction reduced to each fact's own bolded claim, never a hand-written summary.
# =================================================================================
facts_full() {
  if [ -r docs/FOUNDATIONS.md ]; then
    awk '/^## 9\. Facts about the preparation/{f=1} /^## 10\./{f=0} f' docs/FOUNDATIONS.md
  else
    echo "!! docs/FOUNDATIONS.md is missing — that file is canonical truth. Stop and find out why."
  fi
}

# A fact's claim runs from `- **` to the closing `**`, and for some of them that wraps
# across lines — so this accumulates until the marker closes rather than taking line one
# and cutting mid-sentence.
facts_terse() {
  facts_full | awk '
    # The claim is "- **" ... "**". Search from char 4 so the OPENING marker is not
    # what gets found; i is then the closer offset within that substring, and i+4 is
    # the closer end in the whole line. i+5 keeps the space after it, which reads as
    # a clean line and fails the marker check for five claims out of six.
    function claim(s,   i) {
      gsub(/[ \t]+/, " ", s)          # joining wrapped lines doubles the spaces
      i = index(substr(s, 4), "**")
      return (i ? substr(s, 1, i + 4) : s)
    }
    /^## 9\./            { print; next }
    /^- \*\*/            { if (gsub(/\*\*/, "**", $0) >= 2) { print claim($0); want = 0 }
                           else { acc = $0; want = 1 }
                           next }
    want && index($0, "**") { print claim(acc " " $0); want = 0; next }
    want                 { acc = acc " " $0 }'
  echo
  echo "   ^ THE CLAIMS ONLY — this briefing was over budget. The reasoning, the numbers,"
  echo "     and the consequences that bind code are in docs/FOUNDATIONS.md §9. Read it"
  echo "     before acting on any of them; a claim without its consequence is a slogan."
}

# =================================================================================
# THE BRIEFING.  Rendered to stdout by one function so it can be measured before it
# is delivered.  $1 = "terse" to use the degraded FOUNDATIONS extract.
# =================================================================================
render() {
  local mode="${1:-full}"

  echo "=================== bugarach — WHAT BINDS THIS SESSION ==================="

  # --- 1. is anything mid-flight? ------------------------------------------------
  # FIRST, because it was last and therefore invisible. CLAUDE.md: "No handoff file
  # on main == nothing in flight", so the root is a signal and it has to stay honest.
  # Nothing else in the tree reads this file.
  # Bounded in BYTES, not just lines: `head -14` of a file whose lines run 300
  # characters is 4KB, which puts the alarms this render deliberately front-loaded
  # right back behind the preview cut. The whole alarm block has to stay inside 2KB
  # for the ordering to be worth anything.
  if [ -f HANDOFF.md ]; then
    echo
    echo "--- !! HANDOFF.md present — work is in flight, read it before starting ---"
    emit_bounded 700 "$(head -14 HANDOFF.md)"
  fi

  # --- 2. finished work that only Tony can move ----------------------------------
  # `status: open` means somebody should do this. It does not distinguish "nobody has
  # started" from "it is DONE and waiting on a human to press send" -- and the second
  # kind drowns in a list of fifty. The PySpike report sat written-but-unfiled for
  # twelve days partly because nothing told anyone it was ready (2026-08-24).
  # README.md documents the format, so it carries the frontmatter as an EXAMPLE and
  # would otherwise report itself as a waiting item -- it did, first run.
  local waiting f
  waiting=$(grep -l '^status: waiting-on-tony[[:space:]]*$' docs/todo/*.md 2>/dev/null \
            | grep -v '/README\.md$' | wc -l | tr -d ' ')
  if [ "${waiting:-0}" -gt 0 ]; then
    echo
    echo ">> ${waiting} item(s) FINISHED and waiting on Tony — nothing else unblocks these:"
    # Bounded like the handoff excerpt above: the count is already printed, so what
    # this list can afford to lose is its tail, not the alarms behind it.
    emit_bounded 1200 "$(waiting_list)"
  fi

  # --- 3. is the commit gate actually installed in THIS clone? --------------------
  # core.hooksPath is per-clone and stored in .git/config, so it travels with nothing.
  # docs/todo/2026-08-13-hookspath-is-opt-in-per-clone.md is the writeup; this is the
  # part of it that can fire by itself.
  echo
  if [ "$(git config --get core.hooksPath 2>/dev/null)" = ".githooks" ]; then
    echo "commit gates: ACTIVE (branch guard + sapper run on every commit)"
  else
    echo "!! commit gates: OFF in this clone — the branch guard and sapper are NOT running."
    echo "   git config core.hooksPath .githooks"
  fi

  # --- 4. the machine-local board is a precondition, not a suggestion -------------
  # The vendored hook prints "(no board yet — create it ...)" and that has proved
  # too quiet: on 2026-08-18 a session read it, worked all day across two worktrees
  # and never created the board, while four others ran on this machine. So the
  # board is scaffolded here if absent — a session should only ever have to add its
  # own block — and tools/guard_local_board.sh refuses the commit until it has.
  local board
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

  # --- 5. where does figure output actually go on THIS machine? -------------------
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
    local found
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

  # --- 6. the gates that apply before work is handed over -------------------------
  # Listed because these are the ones sessions skip. Every item here was skipped by
  # a session that had read neither CLAUDE.md nor this list.
  echo
  echo "--- gates, before you hand anything over ---"
  echo "   document deliverable (report, explainer, methodology, figure + caption, handoff)?"
  echo "     -> /murderboard <artifact> FIRST. Not a first draft. docs/doc_review_process.md"
  echo "   landing work?  branch + green PR; never commit on main."
  echo "   a visual finding?  render the figure and show it — do not describe it."
  echo "     -> tools/make_diagnostic.py, tools/make_generator_figures.py"
  echo "   writing to the darkroom?  it is shared across machines — claim it on docs/SESSIONS.md."

  # --- 7. the facts about the preparation, straight out of FOUNDATIONS -----------
  # Below the alarms because it is the one section large enough to bury them, and
  # everything above costs ~1.5KB together — so if the budget ladder below ever
  # fails, a 2KB preview still carries every alarm AND the first fact.
  echo
  if [ "$mode" = "terse" ]; then facts_terse; else facts_full; fi

  echo
  echo "FOUNDATIONS is canonical and wins over anything said in conversation."
  echo "For facts about the PREPARATION that it does not cover, the authority is"
  echo "syncytium2/foundations FOUNDATIONS §15 — check it before assuming what a"
  echo "condition does. Do not reason from textbook priors where the lab has a finding."

  # --- 8. open threads: a COUNT, not a dump --------------------------------------
  # This was 9,658 of the 17,568 bytes that got the hook spilled, and PR #305's own
  # handoff describes the list it printed as "71 open todos, most written before the
  # reset. Read as history, not a queue." The largest thing in the briefing was also
  # the least actionable, and it is what evicted the six alarms behind it. The count
  # and the query are what a session needs; the list is a file you open.
  local opens feedback
  opens=$(grep -l '^status: open[[:space:]]*$' docs/todo/*.md 2>/dev/null | wc -l | tr -d ' ')
  feedback=$(grep -l '^status: open[[:space:]]*$' docs/sapper_feedback/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "${opens:-0}" -gt 0 ] || [ "${feedback:-0}" -gt 0 ]; then
    echo
    echo "--- open threads: ${opens} todo, ${feedback} sapper_feedback ---"
    echo "    A record, not a queue — most predate the 2026-08-24 reset. Not listed:"
    echo "    that dump was 9.6KB and it is what truncated this briefing on 2026-08-25."
    echo "    grep -l '^status: open\$' docs/todo/*.md docs/sapper_feedback/*.md"
  fi

  echo "========================================================================="
}

# =================================================================================
# DELIVER.  Render, measure, degrade once if over budget, and always print the size.
# The ladder has exactly one rung on purpose: the alarms are not droppable, and if
# FOUNDATIONS §9's six claims alone blow 8KB then the thing to fix is §9, not this.
# It does have a FLOOR, which it did not: a terse render that is STILL over budget
# used to ship labelled "(TERSE", which reads as a degrade that worked.
# =================================================================================

# The canary, as a function of what it is describing, because it has to be emitted
# BEFORE the body it measures — which makes its own length part of the number. Two
# passes settle that: the second only moves if the first changed a digit count.
#   $1 body   $2 parenthetical (the mode leads it, so a reader sees TERSE first)
canary_line() {
  local body="$1" paren="$2" lines base n line total i
  lines=$(printf '%s\n' "$body" | wc -l | tr -d ' ')
  # Both halves counted the way they are emitted — printf '%s\n', so each carries
  # exactly one newline. wc -c, never ${#line}: the parenthetical holds an em dash,
  # and a character count would report it as one byte where the harness sees three.
  base=$(printf '%s\n' "$body" | wc -c | tr -d ' ')
  n=$base
  for i in 1 2 3; do
    line="briefing delivered: ${lines} lines, ${n}B (${paren})"
    total=$(( base + $(printf '%s\n' "$line" | wc -c | tr -d ' ') ))
    [ "$n" -eq "$total" ] && break
    n=$total
  done
  printf '%s\n' "$line"
}

deliver() {
  local body bytes budget
  budget=$(briefing_budget)
  body=$(render full)
  bytes=$(printf '%s\n' "$body" | wc -c | tr -d ' ')

  if [ "${bytes:-0}" -gt "$budget" ] 2>/dev/null; then
    local terse tbytes floor=""
    terse=$(render terse)
    tbytes=$(printf '%s\n' "$terse" | wc -c | tr -d ' ')
    echo "!! [session-briefing] ${bytes}B over the ${budget}B budget — FOUNDATIONS §9" >&2
    echo "   degraded to its claims (${tbytes}B). An oversized hook is SPILLED to a file" >&2
    echo "   and delivered as a 2KB preview, which is how this channel went silent on" >&2
    echo "   2026-08-25. Trim the briefing or raise BUGARACH_BRIEFING_BUDGET_BYTES." >&2
    # THE FLOOR. There is no third rung to fall to — the alarms are not droppable —
    # so when the last rung does not fit either, the only honest move is to say so
    # in the place a reader is looking, rather than label it a successful degrade.
    if [ "${tbytes:-0}" -gt "$budget" ] 2>/dev/null; then
      floor=", STILL OVER"
      echo "!! and the terse render is STILL over: ${tbytes}B against ${budget}B. There is" >&2
      echo "   no rung below this one. If this is real and not a test, only the alarms at" >&2
      echo "   the top are certain to arrive — FOUNDATIONS §9 needs trimming, not this." >&2
    fi
    canary_line "$terse" "TERSE${floor} — ${bytes}B full, over the ${budget}B budget"
    printf '%s\n' "$terse"
    return 0
  fi

  # THE CANARY, and it goes FIRST. The 2026-08-20 note on the other hook ends "Watch
  # that number", and this one printed it as the LAST line — the one position a
  # spilled payload cannot deliver, since a spill keeps the opening ~2KB and drops
  # the rest. A size line that only arrives when the size was fine is not a canary.
  # On stdout, so it lands in the session's context rather than on a stderr nobody reads.
  canary_line "$body" "budget ${budget}B"
  printf '%s\n' "$body"
}

# =================================================================================
# SELFTEST — sapper-style: prove every branch of the ladder can fire. The pytest
# module drives the real briefing; this is what a person runs by hand.
# =================================================================================
selftest() {
  local fails=0 out claim reasoning wrapped
  t() { # label haystack needle want
    local hit=no
    case "$2" in *"$3"*) hit=yes ;; esac
    if [ "$hit" = "$4" ]; then printf '  ok   %-54s\n' "$1"
    else printf '  FAIL %-54s (%s, wanted %s)\n' "$1" "$hit" "$4"; fails=$((fails+1)); fi
  }

  # NEEDLES ARE DERIVED, NEVER TYPED. tests/test_session_briefing.py asserts that no
  # FOUNDATIONS fact appears literally in this file — a hardcoded needle is a second
  # copy of canonical text, and the two would drift the first time §9 was edited. It
  # caught exactly that in the first draft of this selftest.
  claim=$(facts_full | grep -m1 '^- \*\*' | sed 's/^- \*\*//' | cut -c1-28)
  # Something in §9's prose that is NOT part of any bolded claim, so it is present in
  # the full extract and absent from the terse one.
  reasoning=$(facts_full | grep -v '^- \*\*' | grep -v '^ *$' | grep -v '^#' \
              | tail -2 | head -1 | sed 's/^ *//' | cut -c1-36)
  # A claim that WRAPS across lines, which is the case a line-one extractor cuts in half.
  wrapped=$(facts_full | awk '/^- \*\*/ { t = $0
                                          if (gsub(/\*\*/, "**", t) < 2) { print substr($0, 4, 26); exit } }')
  if [ -z "$claim" ] || [ -z "$reasoning" ]; then
    echo "  FAIL could not derive needles from FOUNDATIONS §9 — has the section moved?"
    return 1
  fi

  out=$(BUGARACH_BRIEFING_BUDGET_BYTES=100000 deliver)
  t "under budget: full extract"     "$out" "$claim"             yes
  t "under budget: reasoning kept"   "$out" "$reasoning"         yes
  t "under budget: canary printed"   "$out" "briefing delivered:" yes
  t "under budget: not marked terse" "$out" "(TERSE"             no

  out=$(BUGARACH_BRIEFING_BUDGET_BYTES=1 deliver 2>/dev/null)
  t "over budget: claim survives"    "$out" "$claim"             yes
  t "over budget: bulk is dropped"   "$out" "$reasoning"         no
  t "over budget: says so"           "$out" "THE CLAIMS ONLY"    yes
  t "over budget: canary says TERSE" "$out" "(TERSE"             yes
  t "over budget: alarms survive"    "$out" "commit gates:"      yes
  t "over budget: gates survive"     "$out" "murderboard"        yes

  out=$(BUGARACH_BRIEFING_BUDGET_BYTES=1 deliver 2>&1 >/dev/null)
  t "over budget: loud on stderr"    "$out" "over the 1B budget" yes
  t "over budget: floor is named"    "$out" "STILL over"         yes

  # THE CANARY'S POSITION IS THE POINT. A spill keeps the opening ~2KB and discards
  # the rest, so a size line at the bottom reports only when the size was fine.
  out=$(deliver | head -1)
  case "$out" in
    "briefing delivered:"*) printf '  ok   %-54s\n' "canary is line 1, not the last line" ;;
    *) printf '  FAIL %-54s (%s)\n' "canary is line 1, not the last line" "${out:0:40}"
       fails=$((fails+1)) ;;
  esac
  out=$(BUGARACH_BRIEFING_BUDGET_BYTES=1 deliver 2>/dev/null | head -1)
  t "canary leads the degraded form too" "$out" "briefing delivered:" yes

  # And it must be TRUE. The number describes the whole payload including the canary
  # line itself, which is why canary_line settles a fixed point rather than measuring
  # the body alone. A canary that is merely present was what this file already had.
  local claimed actual
  claimed=$(deliver | head -1 | sed 's/.*lines, \([0-9]*\)B.*/\1/')
  actual=$(deliver | wc -c | tr -d ' ')
  if [ "$claimed" = "$actual" ]; then
    printf '  ok   %-54s\n' "the canary's number is the payload's real size"
  else
    printf '  FAIL %-54s (says %s, is %s)\n' "the canary's number is the payload's real size" \
           "$claimed" "$actual"; fails=$((fails+1))
  fi

  # THE ALARMS WITH A DEADLINE MUST BE INSIDE THE PREVIEW. Stated as an offset, not
  # a total: on a fresh clone the standing alarms all fire at full length and the
  # block runs past 2.3KB whatever the variable ones do. What ordering buys is that
  # the urgent ones are in front of that, and `head -14` of a file bounds lines
  # rather than bytes — fourteen 300-character lines would undo it.
  local at
  at=$(deliver | head -c 2000 | grep -c 'commit gates:')
  if [ "${at:-0}" -ge 1 ]; then
    printf '  ok   %-54s\n' "urgent alarms land inside the first 2000B"
  else
    printf '  FAIL %-54s\n' "urgent alarms land inside the first 2000B"; fails=$((fails+1))
  fi

  # bound_bytes cuts at a line end or an ASCII space and never mid-character. This
  # repo has already shipped mojibake from an in-place rewrite of prose; a truncator
  # that splits a UTF-8 sequence is the same failure with a budget as its excuse.
  out=$(printf 'ααααα βββββ γγγγγ δδδδδ\n' | bound_bytes 14)
  if printf '%s' "$out" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1; then
    printf '  ok   %-54s\n' "a mid-character cut still leaves valid UTF-8"
  else
    printf '  FAIL %-54s\n' "a mid-character cut still leaves valid UTF-8"; fails=$((fails+1))
  fi
  t "and it says it truncated" "$out" "truncated at 14B" yes

  # The claim extractor must not cut mid-sentence — the failure mode of taking line
  # one, since some claims wrap across two or three of them.
  out=$(facts_terse)
  if [ -n "$wrapped" ]; then
    t "wrapped claim is whole"  "$out" "$wrapped"  yes
  else
    printf '  ok   %-54s\n' "no wrapped claim in §9 right now"
  fi
  # Every emitted claim must open AND close its bold marker, and carry no doubled
  # space from the line-joining. Checked over the claim lines only — the pointer
  # beneath them is deliberately indented.
  if printf '%s\n' "$out" | grep '^- ' | grep -qv '^- \*\*.*\*\*$'; then
    printf '  FAIL %-54s\n' "a claim does not close its bold marker"; fails=$((fails+1))
  else printf '  ok   %-54s\n' "claims open and close their marker"; fi
  if printf '%s\n' "$out" | grep '^- ' | grep -q '  '; then
    printf '  FAIL %-54s\n' "a joined claim carries a doubled space"; fails=$((fails+1))
  else printf '  ok   %-54s\n' "wrapped claims join without gaps"; fi

  # The whole point of the budget is that the COMMON case never reaches it.
  out=$(deliver)
  t "the real briefing fits"  "$out" "(TERSE"      no
  t "and it carries §9 whole" "$out" "$reasoning"  yes

  echo
  if [ "$fails" -eq 0 ]; then echo "all checks pass"; return 0; fi
  echo "$fails failed"; return 1
}

case "${1:-}" in
  --selftest) selftest; exit $? ;;
  -h|--help)  sed -n '2,70p' "$0"; exit 0 ;;
  *)          deliver; exit 0 ;;
esac
