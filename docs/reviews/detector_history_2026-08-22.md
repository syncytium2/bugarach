# Murderboard run — docs/detector_history.md

## What the review was for, and what it changed

The draft was a history of the six coordination detectors, built from two
interface2 reports, with a keep-or-modify verdict on each. It was readable,
sourced, and **wrong in the two places that mattered most** — and both errors had
the same cause: the draft verified its claims against the sources it *named* and
never opened the ones it should have.

**The draft called SPIKE-synch's bake-off score "the largest unexplained
discrepancy in the project" and recommended demoting the detector.** The tree had
explained it four days earlier. `docs/todo/2026-08-18-spike-synch-knob-may-not-be-
the-knob.md` records that the swept knob is `C_threshold` while `C_min` sits
pinned at 0.1 above most of the grid, so the sweep *measures `C_min` while
reporting `C_threshold`*, and every value returns the identical result. The
bake-off's own recall of 0.167 against a mid-pack precision of 0.538 says the same
thing from the other side: the detector is not firing wrongly, it is barely firing.
A recommendation to demote a detector became a much narrower and more useful one —
**that number is not the detector's accuracy and must stop being quoted as such.**

**The draft's evidence section had no evidence in it.** `bakeoff.json` carries a
`probe firings` column — how often each detector fires inside a block containing no
planted events — and it separates the six almost perfectly along the axis the
document's whole argument is about: 215 and 59 firings for the two
stationary-threshold detectors, 1 and 2 for the two rate-local ones. The draft
argued the point in prose and left the measurement out. It is now panel A, and it
is the first thing a reader sees.

A third finding is smaller but changes how §6 must be read: `bench.py`'s own
`source` fields show that three detectors are benched at calibrated operating
points and three at untuned defaults, and **the bake-off's ranking tracks that
split almost exactly**. Reading the table as a ranking of detectors reads a
confound as a result.

The craft round then caught the deliverable failing at the last step: the rendered
page's figure — the lead evidence — was a broken link in both shipped copies, and
the ⚠ banner rendered in the muted aside colour, making the document's most
important warning its faintest text.

## What would validate this, and what generalises

The three findings above are all checkable in one command each against files in
this repository, which is the standard the document now holds itself to. The
document's *own* load-bearing claim — that these detectors re-derive radar's CFAR
design space — is **not** verified to that standard, and it says so in a banner at
the top rather than in a footnote. Role 2 and role 6 both flagged it; neither could
close it, because no radar primary source is reachable from here. It ships as a
stated residual, and §7.2 of the document names which findings survive if the
attributions turn out wrong (the guard-cell finding, the additive-threshold
finding, the calibration confound, the SPIKE-synch diagnosis and panel A all do).

What generalises beyond this document: **two of the three substantive findings came
from `docs/todo/` and from a `source` field in a config dict** — places a reviewer
checking "is this number right?" does not look, because the number *was* right. The
question that found them was "what does this repository already know that the draft
does not cite?"

Two fixes landed in shared code and outlive this document:
`tools/md_to_page.py` now inlines images as data URIs (its docstring already
promised "self-contained"), gives a hoisted ⚠ caveat body-weight styling, and caps
image width to the text column. That closes the one stated reason
`tools/build_assembly_report.py` was forked from it — worth folding back, but out
of scope here and filed as a note in this record rather than done silently.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ f26414a
- vendored:  f26414a (re-vendored in `fa1afc1`; see below)
- freshness: current
- artifact:  `docs/detector_history.md` (5783d246 -> 4d030cbe)
- built:     `docs/learned/detector_history.html` (233 KB) + darkroom copy,
             rebuilt after the last fix; figure `docs/learned/cfar_map.png`
- roles:     11 of 11 run
- rounds:    3 (see the severity table); stopped at the **severity floor**

**Freshness was a hard stop and blocked the run.** The vendored murderboard was at
`729fb06` against upstream `f26414a`. Diffed file by file against a fresh clone,
the five vendored files were byte-identical apart from one comment line, so the
drift was a stamp — but the gate is right to refuse, and the re-vendor landed on
`main` (PR #203) before the review started, because vendoring onto a leaf branch
leaves every new worktree inheriting the old copy.

**Stated deviation from the process:** step 2 prescribes parallel subagents for a
substantial deliverable. This session carries an explicit instruction not to use
the Agent tool, so the roles ran as a **single-pass self-review walking every
role's checklist in turn**, which the process permits for small deliverables and
which is weaker here. Role 10's table ran in full regardless, against each render.
Recorded rather than silently taken.

### Findings by severity, per round

| round | blocking | major | minor | note |
|---|---|---|---|---|
| 1 — full roster | 3 | 5 | 6 | see ledger |
| 2 — blind, on the rebuilt artifact | 1 | 2 | 2 | all three from the render; none visible in the source |
| 3 — blind, role 10 on the new render | 0 | 0 | 1 | severity floor reached |

Blocking in round 1: the SPIKE-synch misdiagnosis; the missing probe-firings
evidence; a citation to a paper not on the shelf. Blocking in round 2: the figure
was a broken link in both shipped copies.

### Role ledger

| # | role | findings | what it checked / found |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 5 | Recomputed every quantity against `bakeoff.json`, `bench.py`, the detector docstrings and the interface2 handoff. Verified: MATLAB F1 table, bake-off F1/recall/precision/probe columns, 4× and 17× ratios, 0.005 s, 34.8/58.8/214.8/1.2/2.5 firings, LoCo and CoactDetect shipped defaults, half-context 60 s/30 s, 74%→10%, ~4.6 s, 3-vs-0 boundary false alarms. **Found:** (a) the draft said nobody had explained SPIKE-synch's gap — `docs/todo/2026-08-18-...` had, in `bench.py`, in plain sight; (b) the draft called CoactDetect "top of the bake-off" when centre−surround leads on the mean; (c) the draft said nothing explained LoCo's SLOW 0.466 when the same handoff calls anything under ~0.6 a weak optimum; (d) the τ-cap "look here first" advice was already closed by the PySpike regression test; (e) the calibrated-vs-default confound in `bench.py`'s `source` fields, unremarked anywhere. |
| 2 | Citation & reference validator — "DOI or Die." | 2 | Checked every named attribution against the darkroom shelf's file list and read-status table. **Found:** the draft cited "Lopes-dos-Santos as recorded on the shelf" — **not on the shelf** (removed; Romano's PROMAX toolbox, which is, replaces it). **Found:** the four CFAR attributions are unverifiable from here — no radar primary is reachable and `fetch_paper.py` is deliberately not vendored. Escalated from a parenthetical to a banner at the top of the document plus a table-column flag plus §7.2. **Residual ⚠ — see below.** |
| 3 | Consistency auditor — "Cross-Examiner." | 3 | Cross-checked detector names against `GLOSSARY.md` (canonical six used throughout; interface2's "spike-sync" appears only inside quotations), the five-vs-six count between the two reports, and every figure↔text number. **Found:** "second in the bake-off" for LoCo was ambiguous between the six and the nine rows (fixed to "second among the hand-written detectors"); "third in the bake-off" for rate+context likewise; new terms (CFAR, guard interval, cell under test, reference cells, greatest-of) were used without entering the glossary — **added in the same change**, as the process requires. |
| 4 | Adversarial reviewer — "Reviewer 2." | 4 | Attacked every claim for overreach. **Found:** (a) "maxlt *is* GO-CFAR" overstated an identity — LoCo matches the *combination rule* but its estimator is a surrogate percentile, not a reference mean; narrowed. (b) The guard-interval recommendation shipped with no cost stated — added CFAR loss, and the wrap-length interaction specific to a circular-shift null. (c) The "state a design Pfa" recommendation appeared to contradict the repo's own rule that operating points come from baseline recordings, not from making a curve look like a curve — now reconciled explicitly. (d) "Can the alarm ring?" applied to the document's own §5.3 claim: the promiscuity probe's firings are *reported* (the column) but cannot enter the score, so the claim was restated precisely. |
| 5 | Line editor — "Kill Your Darlings." | 3 | Every sentence read for one true assertion. Trimmed three ornate constructions; cut a paragraph of §5.5 that restated §5.4. No finding survives as residual. |
| 6 | Methods / domain expert — "RTFM." | 2 | Grounded in the actual method by reading `loco.py`, `coact.py`, `rate.py`, `sync.py` and `bench.py` rather than the reports' descriptions of them — which is how the guard-cell absence and the additive threshold were established, both from source lines quoted in the document. **Found:** the draft's τ-cap suspicion contradicted `sync.py`, which computes its own τ. **Cannot close:** the CFAR side of this role requires primary sources this role could not retrieve; it read no radar paper and says so. **Residual ⚠.** |
| 7 | Reuse auditor — "Reinventing the Wheel." | 2 | The new figure code was checked against the project's existing figure path: it reuses `make_generator_figures._write`, the HoloViews/bokeh idiom, `_time_axis_hook` for the 60-base time axis, and `bugarach.paths.darkroom()` with `--also` per SAP006 — no new stack. **Found:** the document itself needed no new renderer; it goes through the existing `tools/md_to_page.py`. **Found:** `build_assembly_report.py`'s docstring says it was forked from `md_to_page.py` in "exactly one way — that one does not embed images"; the image-inlining fix removes that reason, and the merge is noted here rather than done. |
| 8 | Naive-reader accessibility — "You Lost Me." | 2 | Read cold for terms first used without definition. CFAR, clutter edge, reference cells, guard cells and cell under test are each defined at first use in §3 and again in the glossary. **Found:** "cell under test" was used in §5.1 before §3 defined it (fixed by ordering). **Found:** internal identifiers (`maxlt`, `c_lo`, `loco.py`) appear in audience-facing text — kept deliberately, because they *are* the evidence for the central finding and the audience is this project; recorded as a judged exception, not an oversight. |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 | **The single largest finding of round 1.** The draft was 533 lines of unbroken prose about a claim that is fundamentally geometric — where a window sits relative to the moment it judges — in a repository whose CLAUDE.md says "if a finding is visual, render it before writing about it." Named the replacement figure rather than asking for condensing: panel A, probe firings against F1 coloured by null locality (the measurement the argument rests on); panel B, the three reference windows drawn around the moment under test. Both built (`tools/make_cfar_figures.py`) and hoisted above the history. |
| 10 | Build & craft gate — "Ship It." | 4 | Table below. Ran against three renders: the first figure, the rebuilt figure, and the rebuilt page. |
| 11 | Argument order — "Start With the Problem." | 1 | Reduced the draft to its spine and judged only the order. **Found:** the cold open was "what the two reports say" — process and history — while the actual finding, that three detectors have no guard interval and it already cost two weeks, sat at roughly 60% depth in §5.1. Restructured: the finding and its figure now open the document, the history follows as the explanation, the verdicts follow that. The two-report integration was the *request*, so it is kept in full at §1 rather than cut. |

### Role 10 — craft table

| render | row | verdict |
|---|---|---|
| `cfar_map.png` (build 1) | panel A point labels | **FAIL** — CoactDetect's label sat left of its marker and landed beside LoCo's; each read as labelling the other. Fixed with per-detector placement, re-checked. |
| `cfar_map.png` (build 1) | panel B time axis | **FAIL** — schematic drawn at absolute t=150 s, so 60-base ticks rendered "2m30s" and read as real recording times. Re-centred on t=0; axis now reads distance from the moment under test. |
| `cfar_map.png` (build 1) | panel B seam | minor — LoCo's dotted half-window seam was drawn under the red bar at the same x and was invisible. Removed; the note text carries it. |
| `cfar_map.png` (build 2) | axes named with units | pass — "firings inside a block containing no planted events (log)", "F1 on the held-out fold (mean of 4)", "time either side of the moment under test" |
| `cfar_map.png` (build 2) | every colour legended | pass — four-entry legend, in colour, inside the panel, at body size |
| `cfar_map.png` (build 2) | panels lettered | pass — A and B, referred to by letter in the text, never "top/bottom" |
| `detector_history.html` (build 1) | figure present | **FAIL, blocking** — `src="learned/cfar_map.png"` is correct relative to the markdown in `docs/`, and resolves to nothing from `docs/learned/` or the darkroom root. The lead evidence was a broken link in both shipped copies while the source read as correct. Fixed in `md_to_page.py` by inlining as a data URI. |
| `detector_history.html` (build 1) | ⚠ banner prominence | **FAIL** — rendered as a plain blockquote in the muted aside colour, making the document's most important warning its faintest text. Fixed with a `warn` treatment at body weight. |
| `detector_history.html` (build 1) | figure within the column | **FAIL** — 1840 px figure overflowed the 74ch column and cropped. Fixed with `img { max-width: 100% }`. |
| `detector_history.html` (build 2) | all three re-checked | pass — screenshot inspected; banner legible and prominent, figure inline and complete, nothing overlapping |
| `detector_history.html` (build 2) | build is current | pass — rebuilt after the last fix, 233 KB, self-contained, no external requests |
| `detector_history.html` (build 2) | double rule under the banner | **minor, residual** — the `---` separator and the following `h2`'s border-top render as two rules with a gap. Cosmetic; not fixed, per the round-cap rule. |

### Residual ⚠ — for Tony to resolve

1. **The CFAR attributions are unverified.** Finn & Johnson 1968, Hansen & Sawyers
   1980, Rohling 1983, Gandhi & Kassam 1988 are from working knowledge; no primary
   was retrieved, and neither role 2 nor role 6 could close it from here. The
   document carries this in a banner, a table-column flag and §7.2, and §7.2 names
   the findings that stand regardless. **One radar-detection textbook settles all
   four.**
2. **A published number is wrong and this document does not fix it.** The README
   and the site report 0.254 as SPIKE-synch's bake-off accuracy. Per §6.6 that is
   the score of a degenerate sweep. Correcting those two surfaces is a separate
   change and is not in this branch.
3. **Cosmetic:** the double rule under the rendered banner.
