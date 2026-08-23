# Murderboard run — docs/learned/landscape.html
- upstream:  syncytium2/murderboard @ 783501e
- vendored:  783501e (verified by `murderboard_freshness.sh --refresh`, exit 0)
- freshness: current
- artifact:  `docs/learned/landscape.html` (bb9ae3af -> 1fda88ab)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds to clean

**Deviation, recorded rather than tidied away.** The skill asks for one subagent per
role on a substantial deliverable. This session runs under an instruction not to spawn
subagents, so the eleven roles were walked in turn in-session, each against its own
checklist, with role 10's table produced in full. That is the process's own
small-deliverable mode applied to a larger one: the risk is that a single reader is
less adversarial than eleven independent ones, and it is why the blind pass mattered
here — it caught an error introduced by the fix round.

## Role ledger

| # | role | findings |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | **4** — F1, F2, F3, F12 |
| 2 | Citation & reference validator — "DOI or Die." | **1** — F4 |
| 3 | Consistency auditor — "Cross-Examiner." | **3** — F5, F6, F13 |
| 4 | Adversarial reviewer — "Reviewer 2." | **2** — F7, F8 |
| 5 | Line editor — "Kill Your Darlings." | **1** — F9 |
| 6 | Methods / domain expert — "RTFM." | **1** — F10 |
| 7 | Reuse auditor — "Reinventing the Wheel." | none — see below |
| 8 | Naive-reader accessibility — "You Lost Me." | **2** — F11 |
| 9 | Density & figure-first — "Show, Don't Tell." | none — see below |
| 10 | Build & craft gate — "Ship It." | **1** — F14, plus the table below |
| 11 | Argument order — "Start With the Problem." | none — see below |

### Role 7 — no findings, and here is what I checked
`tools/make_tolerance_figure.py` against the production code it could have duplicated.
It computes **nothing** itself: F1 comes from `bugarach.bench.evaluate`, which pools
through `bench.pool_scores` — the single scoring path that
`README_for_the_webapp.md` requires and that a previous report violated by pooling by
hand on a different denominator. Rendering reuses `make_generator_figures._write`;
detector display names reuse `bugarach.ui.app.TITLES`. No re-derived metric, no
duplicated operating point, no second scoring rule.

### Role 9 — no findings, and here is what I checked
Conventions used, stated as the process requires: flag a section whose argument is
carried by prose where a picture would carry it better. Five sections, two figures and
one table. The central positional claim is carried by the landscape map rather than by
a paragraph, and the measured claim by the sweep figure. Sections 2 and 5 are
prose-only and should be — a verdict and a limits list are not figures. The prose is
load-bearing (caveats and provenance), which the process says to relocate rather than
cut; there is nowhere to relocate it in a single-page report, and it is already at the
end.

### Role 11 — no findings, and here is what I checked
The spine, one claim per section: *(note)* an earlier claim was too strong → *(0)* here
is the question that decides it → *(1)* here is the whole field in one picture →
*(2)* the claim is withdrawn and this narrower one survives → *(3)* the neighbours also
do something better, and here is that measured on our own data → *(4)* go and look at
them yourself → *(5)* here is what none of this establishes. Arc used: problem → what it
costs → the evidence → the residual risk. The cold open is the problem (the note box
states the defect before any content), which is what the arc asks for. No section
arrives before the reader can evaluate it; no section is doing a job another already did.

## Findings and adjudications

**F1 · Prove It · blocking · FIXED.** Standfirst read "Twelve papers, ten of them read
in full." Recount against the shelf README's per-entry marks: **nine** read closely
(four of those scoped to the relevant sections), **two** skimmed, **one** not read
(Chambon's 2018 short version, which the 2019 paper supersedes). Corrected on the page,
in `docs/SESSIONS.md`, and in the shelf README, which now states the split in its
opening and marks the 2018 file as unread.

**F2 · Prove It · blocking · FIXED.** The licence column gave CASCADE as "—". It is
**GPL-3.0** (`gh api repos/HelmchenLabSoftware/Cascade`). A wrong licence in a table
whose purpose is licence facts, on a page that argues from licence facts elsewhere.

**F3 · Prove It · minor · FIXED.** CICADA's licence also showed "—", which reads as
"none". GitLab's API does not expose one; changed to "not stated", which is what is
actually known.

**F4 · DOI or Die · blocking · FIXED.** The page asserted SpikeNet detects discharges
"at what its authors measure as expert level" — a claim about the contents of a paper
that **was not retrieved** (indexed in Europe PMC, outside the open-access subset).
Rewritten to attribute the phrase to the paper's title, which was verified against the
bibliographic record, and to say plainly that nothing is asserted about its contents.
All seven code links were fetched and returned 200; every other attribution traces to a
full text on the shelf.

**F5 · Cross-Examiner · major · FIXED.** The wrong read-count had already propagated to
the `docs/SESSIONS.md` block merged to `main`. One counting basis now, stated in both
places, with the earlier wrong version named rather than silently replaced.

**F6 · Cross-Examiner · major · FIXED.** *(found in blind round 1)* The two panels of
the sweep figure ordered their legends differently, because each was ranked by its own
F1 and the leader changes between regimes. The process forbids two panels disagreeing
on category order — a reader cannot line them up. Fixed to one canonical order for both
panels; the ranking remains visible in the plot itself.

**F7 · Reviewer 2 · major · FIXED.** "An empty cell here is a field that does not need
the tool, not a gap" asserted a cause for the empty learned-assembly cell that no paper
states and no search established. Rewritten as an explicit reading, with the competing
explanation (tried, did not work well enough to publish) named as not ruled out.

**F8 · Reviewer 2 · major · FIXED.** "The published ranking is safe" is a null result
and needed a demonstrated ability to fail. The page now says what would have shown a
failure and reports that three of six detectors move by more than 0.1 of F1 across the
range — so the sweep had the power to overturn the ranking and did not.

**F9 · Kill Your Darlings · minor · FIXED.** The style refactor left `HAND = "#4c78a8"`
unused in `make_tolerance_figure.py` under a comment describing a colour scheme the
tool no longer uses. Removed.

**F10 · RTFM · major · FIXED.** The scoring tolerance is a distance between structures,
and the page never stated its convention — the process names this rule explicitly and
notes the two conventions are not interconvertible. The page now says the tolerance is
a **gap measured edge to edge**, and that the sleep-EEG criterion it is compared against
is a **ratio** while ours is an absolute number of seconds. *Verified in passing:* the
sweep runs every detector at its declared operating point (`run_detector` applies
`OPERATING_POINTS[name].params`), so it benchmarks the shipped tool, and
`tools/fair_bakeoff.py` calls `score_stream` without `tol_sec`, confirming the published
bake-off does use the 1.5 s default the page attributes to it.

**F11 · You Lost Me · major · FIXED.** Two blocking terms for a cold reader, both first
used in section 3: **F1** and the **quiet / busy** regimes. Both now defined where they
first appear, in plain language, before the figure that uses them.

**F12 · Prove It · blocking · FIXED.** *(found in blind round 1, in text added by the
F8 fix)* The new sentence claimed "two of the six move by more than 0.2 of F1". Recomputed
from `tolerance_sweep.json`: **one** does (CICADA, 0.44 in the busy regime); three move
by more than 0.1. Also "below a third of the leader" was recomputed as 0.186 and
corrected to "below a fifth". This is the finding the blind pass exists for — it was
introduced by a fix, so no follow-up pass driven by the original list would have seen it.

**F13 · Cross-Examiner · major · FIXED.** The `SESSIONS.md` block on `main` described
DOSED's swept tolerance as "an answer to
`2026-08-13-scoring-tolerance-vs-detector-resolution.md`". That todo is **closed** and
fixed a different defect (point matching read SCE at 0.08 recall on correct detections).
Corrected in the board block and in the literature handoff, both naming the earlier
wrong version.

**F14 · Ship It · minor · FIXED.** The sweep figure's alt text identified its panels as
"above" and "below". The process forbids referring to panels by spatial words; rewritten
to name them by their y-axis labels, F1 (quiet) and F1 (busy), which is how the repo's
plot conventions carry panel identity.

## Role 10 — build & craft table

Checked against the render of `landscape.html` at `1fda88ab` (full-page screenshot,
1000 × 5963, inspected in four bands).

| element | build current | overlap / off-page | axes named + units | shared limits | every mark identified | verdict |
|---|---|---|---|---|---|---|
| page shell | html newer than `.src.html`, `report.css`, both figures | none | n/a | n/a | n/a | pass |
| landscape map (SVG) | newer than source | none; arrow lands inside its target cell | n/a (categorical grid) | n/a | green = frame gate and red = ours both labelled in place | pass |
| sweep fig, F1 (quiet) | regenerated after the legend fix | none | `scoring tolerance (s)`; F1 dimensionless | y 0–1, shared with the busy panel | 6 curves in legend, colour + dash; the shipped rule is annotated in place | pass |
| sweep fig, F1 (busy) | same render | none | x-axis on this panel only, per repo convention | y 0–1, shared | legend order now identical to the quiet panel | pass |
| licence table | rebuilt after F2/F3 | none; no cell wrap | n/a | n/a | all 7 links resolve (HTTP 200) | pass |

**What this gate cannot see:** it is a flowing HTML page, so the fixed-box overflow
class that bites slide decks does not apply; and the check was run at one viewport
width (1000 px). Narrow-viewport reflow of the licence table was not tested.

## Residual ⚠ — for the human

1. **⚠ SpikeNet is cited without its text.** It appears on the page and in the figure on
   its bibliographic record alone. If it is ever load-bearing, fetch it by hand.
2. **⚠ Malvache et al. 2016 is still not on the shelf**, so the canonical SCE rule
   remains second-hand. Nothing on the page depends on it — the SCE detector here is
   ported from interface2, not from the paper — but the page names the rule.
3. **⚠ The "membership, never event timing" claim rests on two benchmarks.** It is
   stated on the page as resting on the papers read, and a single assembly paper
   reporting temporal agreement would overturn it. No exhaustive search was done.
4. **⚠ Nothing from the page has been run on this project's corpus.** Section 5 says so.
   The route that removes this is
   `docs/todo/2026-08-17-run-a-literature-method-on-our-recordings.md`.
