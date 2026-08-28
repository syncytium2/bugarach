#!/usr/bin/env bash
# the-folder-is-the-input.sh — PreToolUse(Bash) gate. A session reaching for a `.mat`
# event store, or going looking for where the data lives, is told before the command
# runs WHICH export folder to read and what to call to get it.
#
# TWO BRANCHES, AND THE SECOND EXISTS BECAUSE THE FIRST WAS NOT ENOUGH. The store
# branch catches a session that has already decided to read a store. The search branch
# catches one that is simply LOST — the state that PRODUCES the first, and which
# nothing here addressed until 2026-08-28, one day after this file shipped. Each
# branch carries its own reasoning where it is implemented;
# `docs/todo/2026-08-28-the-resolver-exists-and-is-invisible.md` records how the gap
# was found and why the briefing alone could not close it.
#
# NOT VENDORED. This one is bugarach's own and is not project-neutral: it names this
# project's data shapes, its pointer file and its contract. Do not copy it upstream.
#
# WHY THIS EXISTS, AND WHY SAPPER COULD NOT DO IT. On 2026-08-27 a session lost track
# of where the data lived and began re-deriving it from a `.mat` event store. Every
# document that forbids this was correct and present: the contract in
# `docs/export_folder_spec.md`, revision 6's write-up of what re-deriving a producer's
# decision already cost, and "The export folder is the input. The store is closed."
# in CLAUDE.md. Sapper rule SAP007 blocks store reads in `src/bugarach/**` and
# `tools/**`, and its exclusion list is EMPTY — every tool that used to read a store
# now reads the folder. That half of the problem is genuinely finished.
#
# The hole is that sapper greps what a COMMIT ADDS. A session doing interactive
# analysis — a throwaway script in the scratchpad, a `python -c`, a one-off notebook —
# never commits, so SAP007 never sees it and never can. The churn is invisible to the
# only mechanism aimed at it.
#
# Tony, 2026-08-27, on being offered another line of prose in CLAUDE.md as the fix:
#
#     "claude.md is unreliable. help me fix this permanently."
#
# So this gate sees the ATTEMPT, not the wreckage — the same argument the sibling hook
# `no-heredoc-source.sh` makes for itself, and the reason both live here.
#
# IT ANSWERS, IT DOES NOT ONLY REFUSE. This is the whole design. The session that
# triggered this was not defying the rule, it was LOST — it reached for the store
# because it could not find the folder. A gate that says only "no" leaves it lost and
# it churns somewhere else. So the message names the current export folder, taken live
# from `current_export.toml`, and gives the one call that opens it.
#
# EXIT  0 allow · 2 block, with stderr fed back to the model.
#
# SELFTEST — a gate that cannot fire manufactures confidence:
#   bash .claude/hooks/the-folder-is-the-input.sh --selftest

set -uo pipefail

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
ROOT=$(CDPATH= cd -- "${HERE}/../.." && pwd -P)
POINTER="${ROOT}/current_export.toml"

# ---- the answer ------------------------------------------------------------
# Read with sed, NOT with python. The message this hook exists to deliver must not
# depend on an interpreter being on a hook's login PATH — that is exactly the bug
# colonel_kernel found in the sibling hook on 2026-08-18, where a missing `python`
# turned a gate into a no-op across seven repos. sed is in POSIX.
current_export() {
  [ -f "$POINTER" ] || return 0
  sed -n '/^\[default\]/,/^\[[a-z]/p' "$POINTER" \
    | sed -n 's/^name[[:space:]]*=[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' | head -1
}

if [ "${1:-}" = "--selftest" ]; then
  fail=0
  probe() { # $1 want-exit  $2 command text  $3 label
    local got
    got=$(printf '{"tool_input":{"command":%s}}' "$(printf '%s' "$2" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/')" \
          | bash "$0" 2>/dev/null; echo $?)
    got=${got##*$'\n'}
    if [ "$got" != "$1" ]; then echo "  FAIL want=$1 got=$got — $3"; fail=1
    else echo "  ok   ($1) $3"; fi
  }
  echo "the-folder-is-the-input --selftest"
  echo "  pointer names: $(current_export)"
  probe 2 'python -c "from scipy.io import loadmat; loadmat(\"x.mat\")"' 'scipy loadmat'
  probe 2 'python3 analyse.py --store ~/data/processed_archive/event_store_onset_revised_2v' 'processed_archive'
  probe 2 'python -c "import mat73; mat73.loadmat(f)"' 'mat73'
  probe 0 'grep -rn "event_store" docs/'                     'grep for the name is not a read'
  probe 0 'pytest tests/test_io.py'                          'the suite reads fixtures on purpose'
  probe 0 'git log --oneline -- src/bugarach/store.py'       'git is not a read'
  probe 0 'python -c "from bugarach import dataset; dataset.current()"' 'the sanctioned call'
  probe 0 'BUGARACH_STORE_OK=1 python probe.py --store s.mat' 'stated intent opts out'
  # The search half. The first is the shape a session ran on 2026-08-28 (with a
  # synthetic root — SAP004 keeps home paths out), one day after this gate shipped.
  probe 2 'find /mnt/lab -maxdepth 6 -type d -name "exports"'  'the search that got past it'
  probe 2 'ls /mnt/lab/data/exports/bugarach'          'listing the export root'
  probe 2 'ls /mnt/lab/data/processed_archive/event_store_onset_revised_2v | wc -l' 'counting a store'
  probe 2 'find /mnt/lab/data -maxdepth 4 -name "slices.csv"' 'hunting inside the data root'
  probe 0 'BUGARACH_DATA_OK=1 ls /mnt/lab/data/exports' 'stated intent opts out of the search gate'
  # Negatives. Each is a shape the measured 12,009-command census contains and does not
  # fire on; a gate that also caught these would be trained away inside a day.
  probe 0 'ls docs/'                                          'an ordinary repo listing'
  probe 0 'find docs -name "export_folder_spec.md"'           'the contract is not the data'
  probe 0 'find ~/Developer -maxdepth 4 -iname "eval_modularity*"' 'unrelated home search'
  probe 0 'grep -rn "exports/bugarach" docs/'                 'naming the path is not reading it'
  probe 0 'ls src/bugarach/'                                  'the source tree'
  # The one that matters most: still blocks with no interpreter anywhere on PATH.
  nopy=$(printf '%s' "$PATH" | tr ':' '\n' | grep -vi python | paste -sd: -)
  got=$(printf '%s' '{"tool_input":{"command":"python -c \"loadmat(1)\""}}' \
        | PATH="$nopy" bash "$0" >/dev/null 2>&1; echo $?)
  if [ "$got" = "2" ]; then echo "  ok   (2) still fires with no python on PATH"
  else echo "  FAIL want=2 got=$got — DEGRADED MODE IS OPEN"; fail=1; fi
  [ "$fail" = "0" ] && echo "PASS" || echo "FAIL"
  exit "$fail"
fi

payload="$(cat)"

PYBIN=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then
    if [ "$c" = "py" ]; then PYBIN="py -3"; else PYBIN="$c"; fi
    break
  fi
done

cmd=""
if [ -n "$PYBIN" ]; then
  cmd="$(printf '%s' "$payload" | $PYBIN -c '
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print((d.get("tool_input") or {}).get("command", ""))
' 2>/dev/null)"
fi

# DEGRADE, DO NOT SURRENDER — the sibling hook'"'"'s rule, and its scar. With no
# interpreter, scan the raw JSON payload: the command text is in there with its
# quoting escaped, and every token below still shows through.
DEGRADED=0
if [ -z "$cmd" ]; then DEGRADED=1; cmd="$payload"; fi

# ---- stated intent opts out -------------------------------------------------
# There ARE legitimate store readers: `src/bugarach/store.py` is the reader itself,
# `tools/matlab_ref/**` regenerates parity fixtures from MATLAB, `tools/lab_excluded.py`
# reads the lab spreadsheet on purpose, and `cli.py` / `ui/app.py` are the store path's
# own entry points (FOUNDATIONS §4 keeps the two input routes separate on purpose).
# The suite reads `.mat` fixtures to prove all of that works.
#
# The escape hatch is deliberately a thing you have to TYPE. `BUGARACH_STORE_OK=1`
# costs nothing when the read is intended and cannot be arrived at by drift.
printf '%s' "$cmd" | grep -qE 'BUGARACH_(STORE|DATA)_OK=1' && exit 0
printf '%s' "$cmd" | grep -qE '(^|[^a-zA-Z_/])(pytest|tox|nox)([^a-zA-Z_]|$)' && exit 0
printf '%s' "$cmd" | grep -qE '(tools/matlab_ref/|src/bugarach/store\.py|tools/lab_excluded\.py|tools/sapper\.py)' && exit 0

# ---- is this command SEARCHING FOR THE DATA? --------------------------------
# THE HALF THAT WAS MISSING, and the hole it left is measured rather than argued.
# Everything below this block addresses a session that has already decided to read a
# store. None of it reaches one that simply does not know where the data is — and on
# 2026-08-28, one day after this gate shipped, a session ran
#
#     find <home> -maxdepth 6 -type d -name "exports"
#
# and hand-pathed the result into --folder four separate times. The gate stayed silent,
# correctly by its own design: `find` is not store access. SAP007 stayed silent too, for
# its own stated reason: it greps what a COMMIT adds, and an interactive --folder is
# never committed. `dataset.current()` would have answered instantly on that machine.
#
# THE TRIGGER IS MEASURED, NOT GUESSED, because the objection to a gate here was always
# noise. Scored against every Bash command in the 54 bugarach session transcripts on this
# machine — 12,009 of them — this pair fires 30 times (0.25%). All 30 were read by hand:
# every one is a session locating the data root, listing export folders, or counting a
# store's slices. Not one is unrelated work. A wider variant was measured and REJECTED:
# allowing the verb after `;` or `&&` took it to 140 hits including a heredoc writing a
# todo file, and anchoring on `find` over the home directory generally ran at roughly a
# 50% false-positive rate — 23 interruptions to buy 2 extra true positives.
#
# It must sit ABOVE the read-only-verb opt-out below, which exempts find/ls so that
# `grep -rn event_store docs/` never trips the store check. That exemption is right for
# the store branch and is exactly what hid this one.
if printf '%s' "$cmd" | grep -qE '^[[:space:]]*(find|ls|tree)[[:space:]]' \
  && printf '%s' "$cmd" | grep -qE '(exports?/|exports([^a-zA-Z0-9_]|$)|processed_archive|/data([^a-zA-Z0-9_]|$))'; then
  folder="$(current_export)"
  [ -n "$folder" ] || folder="(see current_export.toml — it could not be read)"
  {
    echo "BLOCKED: this looks like a search for where the data lives. There is a"
    echo "resolver, it is correct, and it answers on any machine:"
    echo
    echo "    from bugarach import dataset"
    echo "    dataset.current()     # -> the export folder ${folder}"
    echo "    dataset.data_root()   # -> the directory holding exports/ and processed_archive/"
    echo
    echo "    python -m bugarach.dataset      # both, printed, from a shell"
    echo
    echo "You do not need BUGARACH_DATA_ROOT set -- data_root() finds the Dropbox mount"
    echo "by itself. current_export.toml at the repo root declares WHICH export is current"
    echo "and is the only place that does; every analysis tool takes --dataset <name>, so"
    echo "a path never has to be typed. Contract: docs/export_folder_spec.md."
    echo
    echo "WHY THIS FIRES AT ALL. On 2026-08-27 a session that could not find the data began"
    echo "re-deriving it from a .mat store, and the machinery built that day -- the pointer"
    echo "file, the resolver, this gate, sapper SAP007 -- fixed the store half only. One day"
    echo "later a session ran 'find <home> -maxdepth 6 -type d -name exports' and hand-pathed"
    echo "the result into --folder four times, because nothing addressed a session that was"
    echo "simply LOST. This trigger was measured over 12,009 recorded commands: it fires on"
    echo "30, and all 30 were sessions hunting for the data."
    echo
    echo "IF YOU MEANT IT -- inspecting what the producer shipped, checking a raw 2R"
    echo "acquisition folder, counting a store's slices -- say so and prefix the command:"
    echo
    echo "    BUGARACH_DATA_OK=1 <your command>"
  } >&2
  exit 2
fi

printf '%s' "$cmd" | grep -qE '^[[:space:]]*(git|grep|rg|ag|find|ls|wc|diff|gh)([[:space:]]|$)' && exit 0

# ---- does this command LOAD a store? ---------------------------------------
# Fire on loading verbs, not on the mere appearance of a name. `grep -rn event_store
# docs/` mentions a store and reads nothing; blocking that would train the gate away.
hit=""
if printf '%s' "$cmd" | grep -qiE '(loadmat|scipy\.io|\bmat73\b|\bh5py\b|load_slice[[:space:]]*\(|load_store[[:space:]]*\(|bugarach\.store|from[[:space:]]+\.?store[[:space:]]+import)'; then
  hit="a .mat store reader"
elif printf '%s' "$cmd" | grep -qiE 'processed_archive|event_store(_onset)?[a-z0-9_]*' \
  && printf '%s' "$cmd" | grep -qiE '(python|matlab|octave|--store|open[[:space:]]*\()'; then
  hit="an event store"
fi
[ -z "$hit" ] && exit 0

folder="$(current_export)"
[ -n "$folder" ] || folder="(see current_export.toml — it could not be read)"

{
  echo "BLOCKED: this command reaches for ${hit}. The export folder is the input."
  echo
  echo "THE ANSWER YOU ARE PROBABLY LOOKING FOR:"
  echo
  echo "    from bugarach import dataset"
  echo "    folder = dataset.current()          # -> ${folder}"
  echo "    folder = dataset.current('pensub')  # the crosstalk control's pair"
  echo
  echo "That resolves the folder on THIS machine. You do not need a path, you do not"
  echo "need BUGARACH_DATA_ROOT set, and you do not need to know which export is"
  echo "current -- current_export.toml at the repo root declares it and is the only"
  echo "place that does. Contract: docs/export_folder_spec.md."
  echo
  echo "WHY NOT THE STORE. It holds recordings the lab has WITHDRAWN. Re-deriving the"
  echo "withdrawals here has already produced a wrong published result: a consumer"
  echo "matched the lab's workbook on date alone (bugarach has no slice_order), dropped"
  echo "a recording the lab had NOT withdrawn, and every number in a report was then"
  echo "computed over a set one recording too small -- by machinery built to be careful."
  echo "The producer's export had it right. Contract revision 6 records it."
  echo
  echo "A consumer re-deriving a producer's decision works from strictly less"
  echo "information than the producer had. When it disagrees, it is the one that is"
  echo "wrong. If a folder looks like it holds something it should not, that is a"
  echo "conversation with the producer, not a filter here."
  echo
  echo "IF YOU GENUINELY NEED THE STORE -- regenerating parity fixtures, or working on"
  echo "the store reader itself -- say so and prefix the command:"
  echo
  echo "    BUGARACH_STORE_OK=1 <your command>"
  if [ "$DEGRADED" = "1" ]; then
    echo
    echo "(NOTE: no python3/python/py found, so this matched the RAW payload rather"
    echo " than the parsed command. Precision is reduced, gating is not.)"
  fi
} >&2
exit 2
