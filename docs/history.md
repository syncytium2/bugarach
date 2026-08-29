# History — the moments that changed how this project works

Most of what happens here is work, and work is recorded in commit messages, in
`docs/todo/`, and in `docs/handoffs/`. This file is for the smaller set of moments
where **the project itself changed shape**: a rule was made, a mechanism was built,
or an assumption was reversed.

## What gets an entry

One test, and it is deliberately hard to pass:

> **Something about how the project operates is different afterwards** — a gate now
> fires, a rule now binds, or a belief that guided work turned out to be wrong.

Shipping a feature is not an entry. Fixing a bug is not an entry. A bug that
produced a *rule* is. If you are unsure, it is not one — a history everyone appends
to is a history nobody reads, which is the failure mode the open-todo dump already
demonstrated when it grew to 9.6KB and got the whole session briefing thrown away.

Each entry answers four questions and stops: **what happened, what it cost, what
changed, and where the mechanism lives now.** The last one matters most. An entry
whose lesson lives only in this file has not been learned — it has been written
down, which is not the same thing, and this project has the scar tissue to prove it.

**Order: most recent first**, because the common read is "what changed lately", not a
chronology. **Scope: this is not a complete record of the project** — it starts on
2026-08-11 and holds only what passed the test above. Vocabulary that appears
throughout (sapper, the darkroom, the briefing) is glossed in
[`where_the_data_are.md`](where_the_data_are.md).

---

## 2026-08-27 / 28 — a session lost the data, and the fix could not be seen

**What happened.** A session could not find the recordings and began re-deriving
them from a `.mat` event store. Every document forbidding that was correct and
present. Offered another line of prose in `CLAUDE.md` as the fix, Tony refused it:
*"claude.md is unreliable. help me fix this permanently."*

The mechanism built that day was good — a pointer file, a resolver, a gate, a sapper
rule. **One day later another session ran `find <home> -maxdepth 6 -type d -name
exports` and hand-pathed the result four times.** Every part of the new machinery
addressed a session that had already decided to read a store. None reached one that
simply did not know where the data was.

**What it cost.** A day of churn, then a second day proving the fix had a hole in it.
Earlier, the same confusion had produced a real error: a consumer re-derived the
lab's withdrawals, matched their workbook on date alone, dropped a recording the lab
had *not* withdrawn, and every number in a report was computed over a set one
recording too small.

**What changed.** Three things, and the third is the general lesson.

1. The answer became a **function, not a document**: `current_export.toml` declares
   which folder, `bugarach.dataset.current()` resolves it anywhere.
2. The session briefing now **announces the input** the way it always announced the
   output. That asymmetry was the whole defect — a session was told where to put
   things and left to find where to get them.
3. **The briefing's job is to make a mistake unnecessary; a gate's job is to catch
   the session that made it anyway.** Corrective prose belongs where it fires, not
   in a payload every session pays for. This was settled by a byte budget — the
   alarm came in 13B over — but it is the right division regardless.

**Where it lives.** `current_export.toml`, `src/bugarach/dataset.py`,
`tools/session_briefing.sh` §5a, `.claude/hooks/the-folder-is-the-input.sh` (two
branches), sapper SAP007. Diagnostics and measured baselines:
[`where_the_data_are.md`](where_the_data_are.md).

**A coda worth keeping.** Both defects in the fix were caught by CI and neither by a
green local suite: the byte budget, because a fresh clone renders every alarm at full
length, and a test that could only ever see one branch of a two-branch line, because
this laptop has the data. *The machine that has the data cannot see the state of the
machine that does not* — which is what the whole episode was about, one layer up.

---

## 2026-08-26 — nothing is drawn on the raster

**What happened.** Tony, having changed his mind before and saying so: *"please, lets
never draw on the raster. i know i've changed my mind on this."* The rule was written,
and `make_benchmark_figures.py` broke it the same day — by overlaying from *outside*
the module whose own docstring refuses detection spans.

**What changed.** The raster is one ink, one mark per event. Every cue goes in a lane
above it, and a directional marker there points **down**, at the raster it describes.
Two consequences followed the same day: shape is spoken for, so it cannot also encode
what a mark *is* (recovered and missed are both ▼; the verdict is the colour), and the
rule holds above a trace as well as a raster.

**Where it lives.** Sapper SAP009, `bugarach.ui.diagnostic.raster_panel` /
`lane_panel`, and CLAUDE.md's plot conventions.

---

## 2026-08-25 — the briefing stopped arriving, and every test still passed

**What happened.** `session_briefing.sh` emitted 17,568 bytes. The harness refuses an
injection that size: it spilled the output to a file and delivered a ~2KB preview.
88% of the payload reached nobody — the waiting-on-Tony alarm, the commit-gate report,
the handover gates, the darkroom line, and the `HANDOFF.md`-in-flight alarm, which
nothing else in the tree prints.

**What it cost.** Fifteen tests were green throughout. Every one asserted what the
script *printed*; none asserted what a session *received*. One asserted an ordering
and passed with both sides of the comparison past the cut.

**What changed.** A byte budget with a terse fallback, a size canary printed as
**line 1** (a spill keeps the opening bytes, so a canary anywhere else reports only
when nothing is wrong), and ordering as a survival property: alarms first, bulk after.
The largest section — a dump of every open todo — became a count and a `grep`.

**Where it lives.** `tools/session_briefing.sh` (`briefing_budget`, `deliver`),
`tests/test_session_briefing.py`, `tools/hook_spill_census.sh` — which supplies the
outside number, because a budget the tests read out of the script cannot validate
itself.

---

## 2026-08-20 — the export folder is the input, and the store is closed

**What happened.** An analysis read the `.mat` store, noticed it held recordings the
lab had withdrawn, and re-derived the exclusions from the lab's workbook — which keys
on `(date, mouse, slice_order)`. bugarach has no `slice_order`, so it matched on date
and dropped a recording the lab had **not** withdrawn. The producer's own export had
it right.

**What changed.** Analysis reads an export folder and nothing else — no store, no
workbook, no roster. Which recordings are analysable and which ROIs are alive are the
producer's calls, already applied. **A consumer re-deriving a producer's decision
works from strictly less information than the producer had; when it disagrees, it is
the one that is wrong.** If a folder looks like it holds something it should not, that
is a conversation with the producer, not a filter in the consumer.

**Where it lives.** Sapper SAP007 (exclusion list empty), `docs/export_folder_spec.md`
revision 6, and the gate above.

---

## 2026-08-18 — the one artifact written for a person to read could not reach them

**What happened.** The assembly report was built to `docs/learned/` and stopped there.
Its builder took `--out` as *required* while every figure tool defaults to the
darkroom, so the only output meant for a human was the only one that could not find
its way to one. Tony had to ask where it was.

**What changed.** A tool that renders something to be read defaults its destination to
`darkroom()` and takes `--also` for the repo copy. Both copies are kept: the repo one
is what review and git history need, the darkroom one is what a person opens.

**Where it lives.** Sapper SAP006, `bugarach.paths.darkroom()`, FOUNDATIONS §5.

---

## 2026-08-13 — reasoning from the textbook where the lab has a finding

**What happened.** A session ran a full day without reading `docs/FOUNDATIONS.md`, and
proposed calibrating the detectors until TTX slices stopped showing coordination — the
dominant-paradigm assumption that TTX silences the field, which this project's own data
refutes and which FOUNDATIONS §9 forbids in terms. Tony: *"claude.md is the first thing
you ignore. we have built tools for this purpose."*

**What it cost.** A day, and very nearly a calibration built to erase a real finding.

**What changed.** The binding facts stopped depending on being read. They are extracted
from FOUNDATIONS and injected into every session's context at startup, whether or not
anyone opens the file. **A rule written in a file that must be read to be obeyed is not
mechanized.**

**Where it lives.** `tools/session_briefing.sh`, wired in `.claude/settings.json`;
`tests/test_session_briefing.py` proves the channel can fire.

---

## 2026-08-11 — a public repo with a person's name in the paths

**What happened.** Absolute home-directory paths were committed to a repo that is
public. The rule written to stop it matched a surname folder and a Dropbox folder by
name, and was believed to cover the case; a home directory spelled in lowercase
matched neither, and `tools/matlab_ref/prep_ref_input.py` carried two of them from the
day it was written until 2026-08-20.

**What changed.** The rule now matches any absolute home-directory path. The broader
lesson is the one worth carrying: **a rule that covers the shape you thought of is
worth less than it looks.**

**Where it lives.** Sapper SAP004 — and it is the most alive rule in the tree. On
2026-08-28 alone it blocked this project's own test fixtures, a paragraph written
*about* the rule, and then **the first draft of this very entry**, which quoted the two
patterns literally. A rule you cannot describe without tripping is a rule that works.

*One thing that catches people:* `sapper.py --all` scans the **tracked** tree, so a
brand-new file reports clear until it is staged. The commit gate (`--staged`) is what
sees it. That is the correct division — but do not read a clean `--all` on an
uncommitted file as a pass.
