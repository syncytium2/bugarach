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


---

# Round 3 — Tony's read, and two new documents

- artifact:  docs/learned/coordination_report.html (c83622c → rebuilt, see below)
- also:      docs/todo/2026-08-17-literature-deep-dive-handoff.md
- also:      docs/learned/README_for_the_webapp.md
- roles:     11 of 11 re-run against the changes
- rounds:    1 blind pass on the rebuilt page, clean

Round 2 shipped a page with four defects the review did not catch, all four found by
the person who commissioned it. Recorded here because the pattern matters more than the
fixes: **every one of them was a domain claim or a design claim, and every one was
invisible to a reviewer working from the draft's own framing.** This is the cost of
running the roles as a self-review rather than as independent agents, and it is now a
measured cost rather than a stated risk.

## What Tony found that eleven roles did not

**T1 · PySpike was miscredited as a detector.** The page said "the synchrony detector
follows PySpike's semantics". PySpike and cSPIKE (Kreuz lab) supply an adaptive
SPIKE-synchronization *profile* — a coincidence value per spike, synchrony as a
function of time. The detector that finds coordination **events** in that profile
(binning, a hysteresis scan with sustain and gap rules, an artifact gate) is this
project's own, ported from interface2's `SpikyDetect3`. So the page credited a library
with work the lab did, and simultaneously implied a comparison against PySpike that
does not exist. **Fixed in both reports** — this page and the earlier
`report.src.html`, which carried the same sentence. Role 6 (RTFM) owned this and read
the port's docstring, which says it correctly; the review checked that the *method* was
used right and never asked whether the *attribution* was right.

**T2 · frames-not-seconds was absent, and one gloss contradicted it.** The models are
written in samples and nothing inside them knows what a second is — a deliberate
commitment, and the reason a fitted kernel width is a measurement rather than a
hyperparameter. The page never said so, and then glossed a receptive field as "about
three and a half minutes", which reads as if the model reasoned in time. **Fixed**: a
new subsection states the commitment and says where seconds legitimately appear (the
scorer's tolerance, the corpus's rates) and where they do not; the minutes gloss is
gone, with the conversion shown as a conversion.

**T3 · the architecture was never actually shown.** The page had block diagrams —
boxes reading "centre − surround, 4 DoG kernels", "dilated stack, 10 conv, 8 ch". A box
labelled with a mechanism asserts it; it does not let a reader evaluate whether the
kernel is sane, what width it settled on, or whether the claimed cancellation happens.
**Fixed** with `tools/make_architecture_figures.py`, which trains the model and plots
what it fitted: the centre and surround separately at the narrowest scale, all four
fitted kernels against their initialisations, a background step pushed through each
kernel to test the cancellation, and the receptive field after every layer of every
model computed from the dilation schedule. Role 9 asked "what here should be a picture"
and accepted a schematic as the picture; the right question was whether the picture
showed the thing.

**T4 · "competes with state-of-the-art models from the literature" is not supported**,
and the page's framing invited it. Nine detectors were compared: six hand-written ports
plus three of our own networks. The only published methods in the field of play are
CICADA and the cSPIKE/PySpike-derived profile; the assembly-detection algorithms the
survey names were never run. Role 4 attacked the novelty claim and left the
*comparison* claim alone, because the page never made it explicitly — it made it
available. Handled by making the gap the first item of the literature handoff, and by
answering the question directly rather than in the document.

## What the new figure found, which is the argument for having drawn it

- **The four-scale kernel bank collapsed to one scale.** Initialised a doubling apart
  at 1, 2, 4, 8 samples, it trained to 4.0, 4.6, 5.2, 6.6. A bank whose scales
  converge is one scale with redundant copies, and the multi-scale part of the design
  may not be earning its parameters. Untested: run it with one scale.
- **A fitted surround ratio sits within 10% of its clamp** (38 against a ceiling of
  40). By this project's own rule about the threshold grid, a fitted value at the end
  of its range is the search reporting that the range was wrong.
- **The cancellation does hold**: a permanent doubling of the background produces a
  transient and returns to zero. So the mechanism works as designed and still transfers
  worse than two of the six, which sharpens rather than softens section 5 — what a
  busier background brings is variance, and the operator only cancels the mean.

Neither of the first two was visible in a block diagram, which is the point.

## Role ledger — round 3

| # | role | outcome |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 4 new quantities (fitted centres, ratios, jitter) wired to `architecture_fitted.json` and `bakeoff.json` as build-time stores; none typed into prose. The "40% width movement" claim is carried from the earlier report and is **not** re-measured here — flagged ⚠ in place. |
| 2 | Citation & reference validator — "DOI or Die." | Kreuz lab / cSPIKE / PySpike attribution corrected per T1 and checked against the port's own docstring and `README.md`'s licensing table. No new bibliography. |
| 3 | Consistency auditor — "Cross-Examiner." | The corrected PySpike sentence appears in two reports; both changed in the same edit. Checked that "six detectors" still counts six after renaming one of them SpikyDetect. |
| 4 | Adversarial reviewer — "Reviewer 2." | T4 adjudicated: the comparison claim is not made and is now explicitly disclaimed in the webapp README. New figure's panel C is exactly the "can the alarm ring" test — it *could* have shown a failure to cancel, and did not. |
| 5 | Line editor — "Kill Your Darlings." | New subsections read; one redundant sentence cut from the frames section. |
| 6 | Methods / domain expert — "RTFM." | Re-read `detectors/sync.py` end to end for T1. The numpy DoG in the new tool is a deliberate independent reimplementation of the torch kernel — if the two disagree the figure is wrong, which is the check; verified the area normalisation matches. |
| 7 | Reuse auditor — "Reinventing the Wheel." | New tool borrows `HAND`/`LEARN`/`ARCH` from the bake-off tool and `_spread` from the regime tool rather than redefining either. |
| 8 | Naive-reader accessibility — "You Lost Me." | New figure's caption names every curve and both line styles; "clamp" and "dilation schedule" are defined where they first appear. |
| 9 | Density & figure-first — "Show, Don't Tell." | T3 is this role's miss and its fix. The block diagrams stay — they are the signal path — but the operator now has its own measured figure. |
| 10 | Build & craft gate — "Ship It." | Rebuilt page re-rendered to 11 slices; one label collision in panel B found and fixed with the shared spreader; four-panel layout kept under the PNG renderer's viewport ceiling. |
| 11 | Argument order — "Start With the Problem." | The operator figure is placed after both block diagrams and before the literature section: a reader must know what the models compute before being asked whether it is new. |

## The two new documents

Both are handoffs for other sessions, both reviewed under the same roles in one pass.

- **`docs/todo/2026-08-17-literature-deep-dive-handoff.md`** — states the novelty
  question in four answerable parts, tabulates what the shallow pass established
  against what it only assumed, names where to look that it did not (forward citations,
  the MEA side, EEG/spindle analogues, preprints, code without papers), and puts
  **running a literature method on our corpus** as the highest-value item rather than
  more searching. Carries the traps: no vendored `fetch_paper.py`, PMC behind a bot
  check, and the fabricated-citation near-miss.
- **`docs/learned/README_for_the_webapp.md`** — the loop as four stages with measured
  wall-clock, what to reuse (`pool_scores`, the `ARCHITECTURES` registry, `train`,
  `darkroom()`, the time-axis hook), the one screen that needs a human (choosing K),
  ten traps each of which has already cost someone time, and an honest "what is not
  ready" list. Ends with a first slice of work chosen so the app can be checked against
  published numbers on day one.

Residual ⚠ from round 2 all still stand, and T1–T4 add one: **four domain-level defects
reached a shipped page after eleven roles reported clean.** The roles are not the
problem; running them from inside the context that wrote the draft is. The next document
of this weight should get at least roles 4, 6 and 9 from something that did not write it.
