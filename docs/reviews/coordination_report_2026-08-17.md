# Murderboard run — docs/learned/coordination_report.html
- upstream:  syncytium2/murderboard @ f43a07b
- vendored:  f43a07b (stamp matches upstream HEAD, checked via remote)
- freshness: current
- artifact:  docs/learned/coordination_report.html (a266c5a → c83622c)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds to clean

## How the roles were run, and what that costs

**Single-pass self-review walking every role's checklist in turn, not eleven parallel
subagents.** The skill prescribes subagents for a deliverable this size; the operator's
standing instruction in this session is not to use the Agent tool unless asked, so the
coverage is complete and the **independence is not**. That matters most for roles 4 and 8
— an adversarial reader and a cold reader are both harder to simulate from inside the
context that produced the draft — and it is recorded here as a residual rather than
smoothed over. ⚠

## Role ledger

| # | role | findings | note |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 1 fixed, 0 residual | Claim ledger below. Every quantity recomputed from `bakeoff.json` / `regime_shift_fitted.json` / the model code, not eyeballed. |
| 2 | Citation & reference validator — "DOI or Die." | **1 blocking, fixed**; 1 residual ⚠ | Caught a **fabricated author list**. Full texts unreachable. |
| 3 | Consistency auditor — "Cross-Examiner." | 2 fixed | A count in prose disagreed with the tables; a percentile claim disagreed with its own caveat. |
| 4 | Adversarial reviewer — "Reviewer 2." | 2 fixed, 1 no-change | "Can the alarm ring?" applied to the flat lines; see below. |
| 5 | Line editor — "Kill Your Darlings." | 1 fixed, 2 no-change | |
| 6 | Methods / domain expert — "RTFM." | 0 findings | What was checked: the `--spec` path drops the spec's fitted `bg_rate_hz` (0.0097, the median) and lets `REGIMES` supply p25/p75 of the *same* measurement, so the axis and the corpus come from one assessment; the threshold is not re-picked on the target; the six are calibrated on a disjoint seed block, so both sides of the comparison get a held-out knob. Receptive fields and parameter counts read off the built modules rather than the docstrings. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 1 fixed | New figure tool duplicated an existing palette. |
| 8 | Naive-reader accessibility — "You Lost Me." | 1 blocking, fixed | F1 / recall / precision / ROI were used throughout and defined nowhere. |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 fixed, 1 no-change | Section 3 was four prose blocks; it is now a table. |
| 10 | Build & craft gate — "Ship It." | 2 fixed | Render table below. |
| 11 | Argument order — "Start With the Problem." | 1 blocking, fixed | The report opened on method. It now opens on the problem. |

## Findings, ranked

### BLOCKING

**B1 · role 2 — a fabricated author list.** The draft cited autoMEA as
"Pradeepan et al. 2024". That name was invented; nothing in the search evidence
supported it. Correct attribution, checked against the publisher record:
**Hernandes, Heuvelmans, Gualtieri, Meijer, van Woerden & Greplova**, *Front. Neurosci.*
18:1446578 (2024), preprint bioRxiv 2024.05.08.593078. **Fixed**, and the page now says
in its own reference note that a fabricated citation was caught here — a reader deciding
how much to trust the survey should know its one measured failure rate.

**B2 · role 11 — the report opened on the method, not the problem.** Section 1 was the
pipeline; a reader met the apparatus before learning what it is for, and nothing in the
document showed what a coordinated event looks like or why finding one is hard. The
process's default arc puts the problem first and calls an *unstated* deviation a defect.
**Fixed**: a new section 0 opens on one recording from the corpus with the planted answer
marked, and the caption says plainly that the events are there and the raw record barely
shows them. The figure was **regenerated on the fitted corpus** rather than reused from
the older flat-background bench, so the opening illustrates the data the report actually
scores on.

**B3 · role 8 — the vocabulary was never defined.** F1, recall, precision, "fold",
"operating point", "knob" and `Hz/ROI` all appear before any definition; a colleague
reading cold cannot evaluate a single number. **Fixed**: a short paragraph in section 0
defines the three metrics, the matching rule and the tolerance, and says what an ROI is.

### SHOULD FIX

**S1 · role 3 — a count in prose contradicted the tables.** The standfirst said "the two
learned models" while section 4's table lists three learned rows. **Fixed**: "the two
candidate networks", with the third named as a control wherever it appears.

**S2 · role 3 — the regime endpoints were described two ways.** Section 5 called them the
25th and 75th percentiles; caveat 4 in section 6 corrects that to roughly the 60th and
83rd as per-cell rates. A reader who stops before section 6 gets the wider claim.
**Fixed** at first mention, with the caveat cross-referenced.

**S3 · role 9 — the literature survey was prose where its claim is positional.** The
argument is about *where in the pipeline* the learning sits, which is a table with that
column, not four paragraphs. **Fixed**: a four-row table, one row per level of the
analysis, with the row this work occupies highlighted, and the prose cut to what the
table cannot say.

**S4 · role 7 — the new figure tool re-declared an existing palette.** `make_regime_figure.py`
defined its own `HAND`/`LEARN` colours and architecture names, both already owned by
`make_bakeoff_figures.py`. Two figures in one report are free to drift apart in exactly
the way that teaches a reader to distrust the colour key. **Fixed**: imported.

**S5 · role 10 — a shared generator clobbered another artifact.** Adding `--spec` to
`make_tube_figure.py` and running it overwrote `docs/learned/tube_view.png`, which the
*earlier* report embeds. Caught by `git status`, not by the report under review — this is
the process's "a fix inside a shared helper changes every artifact that calls it" rule
firing. **Fixed**: figure restored from git, and the tool now takes `--name` so a new
figure cannot land on an old one's filename.

**S6 · role 10 — the figure exported nothing and said so only in a log.** The three-panel
regime figure exceeded the PNG renderer's viewport, so its ink-clipping pass measured
920×0 and skipped the export while still writing a perfectly good HTML. **Fixed**: panel
heights reduced to fit, with the reason recorded in the builder so the next person who
adds a panel knows the ceiling exists.

**S7 · role 1 — six numbers in section 5's prose were typed by hand.** They were all
correct, which is luck rather than process, and this page's own builder exists because a
murderboard already caught transcribed numbers drifting. **Fixed**: `regime_shift_fitted.json`
is now a build-time store and every one of those numbers resolves from it.

**S8 · role 5 — the diagrams had three legibility defects**, found by rendering them
rather than reading their source: overlapping annotations in the per-cell diagram, a
caption wider than the viewBox that lost its last two words, and an arrow that read as
"the six feed the learned models" — the opposite of the independence the figure exists to
show. All **fixed** and re-rendered.

### NO CHANGE (adjudicated, deliberately kept)

- **Role 4 — "the flat lines are not robustness."** The two models that never trained
  hold their score exactly across the shift. Applying the process's ceiling/saturation
  diagnostic: a model that almost never fires has no dynamic range to lose, so its
  stability **cannot** register a transfer failure. The page already says this in section
  5 and the point is kept rather than softened, because it is the honest reading of a
  number that would otherwise flatter two failed models.
- **Role 4 — the novelty claim is left as a claim, not upgraded.** It is stated as "no
  prior work was found", with the survey's scope, and with the observation that no
  individual component is novel. That is as far as four searches licenses.
- **Role 5 — "the quantity most of the six threshold"** uses *threshold* as a verb. Kept:
  it is this project's established usage and the alternative phrasings are longer and no
  clearer.

## Claim ledger (role 1) — recomputed, not eyeballed

| quoted | source | recomputed | verdict |
|---|---|---|---|
| 1,149 params (centre−surround) | `nets.py`, summed over `requires_grad` | 1,149 | match |
| 2,393 params (per-cell bank) | same | 2,393 | match |
| 2,065 params (pooled trace) | same | 2,065 | match |
| "12-parameter operator" (DoG) | `log_center` + `log_ratio` + `gain`, 4 each | 12 | match |
| head sees 127 / 2,047 samples | `receptive_field(6)`, `receptive_field(10)` | 127, 2047 | match |
| "about three and a half minutes" | 2047 × 0.1 s | 204.7 s = 3.41 min | match |
| "a sixteenth of the span" | 2047 / 127 | 16.1 | match |
| "half the parameters" | 1149 / 2393 | 0.48 | match |
| F1 0.668 ± 0.061 / 0.651 ± 0.044 | `bakeoff.json` | resolved at build time | match |
| detect 0.014 / 0.060 / 0.245 s | `bakeoff.json` | resolved at build time | match |
| "more than forty times the training" | 236.45 / 5.62 | 42.1 | match |
| 4.6-fold regime span | 0.0175 / 0.0038 | 4.61 | match |
| 30 planted events per fold | `n_per_level` (5,5,5) × 2 recordings | 30 | match |
| 470 recording-minutes | 3525 s × 8 / 60 | 470 | match |
| every section-5 number | `regime_shift_fitted.json` | resolved at build time | match |
| autoMEA authors | publisher record | **mismatch — fabricated** | fixed (B1) |
| "every compared algorithm is hand-written" | abstract + method list only | unverifiable from full text | flagged ⚠ |

## Render table (role 10)

Checked against `render2/p00–p08.png`, 1180 px wide, device scale 1.5, taken from the
**rebuilt** artifact (fingerprint c83622c, newer than every input it embeds).

| section | figure | axes named + units | panels lettered | every mark identified | overlap / off-page |
|---|---|---|---|---|---|
| 0 problem | problem_view.png | yes (time, cells, fraction active) | A/B/C | triangles, shaded band and both trace types named in caption | clean |
| 1 pipeline | pipeline.svg | n/a (schematic) | n/a — stages numbered 1–4 | dashed line labelled as ground truth; solid = signal path | clean after S8 |
| 2 per-cell | arch_tiny.svg | shapes and param counts per stage | n/a | every box and both spans labelled | clean after S8 |
| 2 centre−surround | architecture.svg | as above | n/a | fifth-channel bypass labelled | clean (pre-existing figure) |
| 4 bake-off | bakeoff.png | yes; log time axis named | A/B | colour = hand vs learned, stated in caption; marker area = params | clean |
| 5 regime shift | regime_shift_fitted.png | yes, F1 and precision, rates on ticks | A/B/C | every line labelled with name + value; thick = learned, stated | clean after label de-collision |

Two rounds. Round 1 was the blind pass that produced B2, B3, S1 and S8. Round 2 re-read
the rebuilt render and produced S2 only; a third blind read of the corrected file produced
nothing new.

## Residual ⚠ — for Tony to resolve

1. **Independence, not coverage.** All eleven roles ran, in one pass, by the same context
   that wrote the draft. Roles 4 and 8 are the ones that lose most. If this page is going
   anywhere external, it is worth one adversarial pass by something that did not write it.
2. **No paper was read in full.** Bibliographic details are verified against publisher
   records; claims about paper *contents* rest on abstracts and method lists, because the
   open-access copies are behind a bot check here. The load-bearing one is "assembly
   detection is hand-written everywhere found" — the basis of the novelty claim.
3. **The novelty claim is a survey result**, four searches deep, and is stated that way in
   the page. It should not be repeated anywhere as "novel" without that qualifier.
4. **One training run per fold**, still. Every learned number lacks a seed error bar, so
   the regime-shift result — including the finding that the learned model transfers *worse*
   than two of the six — is one run per cell. This is the cheapest thing that could change
   a conclusion in this report and it has not been done.
5. **The architecture comparison remains uncontrolled** (10× learning-rate difference).
   Section 4 says so; a reader in a hurry may still take "building the invariant in beats
   hoping for it" as established. It is not.
