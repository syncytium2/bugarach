# Murderboard run — docs/generator.md

- upstream:  syncytium2/murderboard @ b2b2ba2
- vendored:  b2b2ba2 (`murderboard_freshness.sh --refresh --verbose` → `current (via remote)`, exit 0)
- freshness: current
- artifact:  `docs/generator.md` (`4f44c40` → `1485109`)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds — **neither clean**. See "Why it is not converging".

Run as parallel subagents, one per role, per the process's rule for a substantial
deliverable. The artifact is a hand-written explainer whose ten figures are
generated, so roles 6–7 also reviewed `tools/make_generator_figures.py`,
`src/bugarach/bench.py`, `simulate.py` and `score.py` — the process extends the
review to new analysis code the deliverable rests on.

---

## Role ledger

| # | role | findings | outcome |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 74-row claim ledger; **19 findings, 4 blocking** | every quoted number re-derived; stale ones replaced |
| 2 | Citation & reference validator — "DOI or Die." | **9 findings, 3 high** | wrong producer file, unresolvable path, unreproducible command |
| 3 | Consistency auditor — "Cross-Examiner." | **17 findings, 6 blocking** | doc contradicted the code and its own figure |
| 4 | Adversarial reviewer — "Reviewer 2." | **19 findings, 5 blocking** | verdict: do not ship |
| 5 | Line editor — "Kill Your Darlings." | **4 blocking, 14 major, 26 minor** | named the root pattern (below) |
| 6 | Methods / domain expert — "RTFM." | **20 findings, 7 blocking** | the calibration does not round-trip |
| 7 | Reuse auditor — "Reinventing the Wheel." | **12 findings, 3 blocking** | forked plumbing had lost a bug fix |
| 8 | Naive-reader accessibility — "You Lost Me." | per-section table; **11 of 20 sections blocking** | two documents sharing a file |
| 9 | Density & figure-first — "Show, Don't Tell." | count table; **1 blocking, 6 major** | argument sections carried no figures |
| 10 | Build & craft gate — "Ship It." | figure table; **13 defects, all 10 renders failing** | every figure was stale |
| 11 | Argument order — "Start With the Problem." | spine + **8 findings, 4 critical** | correction arrived after what it corrected |

No role returned "nothing to check."

---

## The root pattern

Role 5 named it and eight other roles independently hit it:

> **The document was updated by appending a correction rather than by revising
> what it had already said.**

The bench was recalibrated on 2026-08-13 and again on 2026-08-14. The prose was
corrected both times by adding a section. So the document simultaneously asserted
and retracted the same claims — the retired `sparse`/`dense` rates at line 69
against their retraction at line 236; "the bench now runs TTX → baseline" twenty
lines above "this is not TTX"; "a benchmark whose realism nothing has measured"
one section below "The measurements existed all along."

A reader who stopped early left with the retracted version, and the document's
own honesty about its history made the stale claims read as authoritative rather
than superseded.

---

## Findings and adjudications

### Fixed in the artifact

| finding | roles | fix |
|---|---|---|
| Every per-detector number stale (measured under abandoned configurations) | 1, 3, 4, 6 | all re-derived on the shipped bench, seeds (1,2,3) |
| "SCE is the most precise (1.00 in both regimes)" — it is 0.56/0.91 and the only one that does not transfer | 1, 3, 4, 6 | claim removed; SCE's transfer failure stated instead |
| "CICADA fires ~59 times a minute" — 17.3 | 1, 3, 6 | replaced, with the full six-way spread |
| "RateDetect's and spike-sync's false alarms sit 30 s+ away" — they had none; the claim described an empty set and was backwards | 1, 3, 4 | replaced with measured distances for all six |
| "The bench now runs TTX → baseline" — re-inherited a label `bench.py` had explicitly retracted | 1, 2, 3, 4, 5 | regimes are now baseline-derived and named as such |
| Retired `sparse` / `dense` vocabulary in prose, table rows and a filename | 1, 2, 3, 4, 5, 10 | live regime names throughout; figure regenerated under the name the tool emits |
| Documented regeneration command produced a differently-named file | 2, 3, 4, 7, 10 | command and filename reconciled; `--bench` choices now derived from `REGIMES` |
| **`_render_png` dropped `.resolve()`** — a relative `--out` silently produced zero PNGs while blaming a missing chromium | 7 | fixed and the exception is now printed |
| Nine PNGs stale at 1× — they predated the 2× fix because of the bug above | 10 | regenerated; verified 2240 px wide |
| 32–34% of every figure was blank canvas; bokeh toolbar baked into static PNGs | 8, 9, 10 | screenshot clipped to rendered content; toolbar disabled |
| `n_roi` panels y-linked, flattening the n=10 row to a sliver | 10 | `shared_axes=False`; each row keeps its own range |
| `min_sep_sec` figure could not show the contaminated null it captions | 4, 6, 8, 9, 10 | 120 s context window drawn to scale; sweep resized so the floor binds |
| `n_distractors` figure showed no distractors at all | 8, 9, 10 | own glyph (▽); recruitment set to measured participation |
| Figure `BASE` hardcoded the four values the bench documents as wrong | 6, 7, 9 | derived from `BENCH_RECORDING` |
| **All six distractors planted inside the promiscuity probe**, recruiting 50% against a measured 18% — negatives stronger than positives, and every hit subtracted out of precision | 6 | `distractor_window` set; hits now range 3–18 across the six, and a test asserts the spread |
| "84 baseline slices" applied to all four measured values; jitter and participation rest on 47 | 1, 4, 6 | per-row denominators tabulated |
| `n_roi ≈ 33` cited to a file with no such column | 1, 2, 4, 6 | marked as derived, with the identity |
| Wrong producer: `measure_coordination_timescale.m` "writes nothing" | 2 | credited to `run_coordination_timescale_batch.m` |
| Scoring rule never defined though every number depends on it; "within 2 s" against a 1.5 s tolerance | 4, 5 | a "how a detection is scored" paragraph precedes the first number |
| "Firing on a distractor is counted but not scored as a false alarm" — it is | 1, 6 | corrected in the doc; `score.py`'s docstring carries the same error and is filed |
| "Four of six operating points not optimal" — the cited table listed five | 1, 3, 5 | re-derived: four, and the four are named |
| Cold open was a quickstart; the correction arrived 100 lines after the defaults it corrects | 9, 11 | reordered — the cost lands first, quickstart moved to an appendix |
| Residual risk absent; "closed 2026-08-13" implied the assumption problem was solved | 4, 11 | new "What is still unsigned" section |
| Terms undefined for a cold reader; `GLOSSARY.md` never linked | 8 | glossary link and a six-detector roster at the top |
| Dates and `§n` references as prose content, against `writing_conventions.md` | 5 | removed or named |

### Withdrawn rather than fixed

| claim | why |
|---|---|
| "An independent bench reproducing an upstream optimum is the useful kind of agreement" (`rate excess_thr=10`) | Not reproducible: the shipped grid stops at 8.0, and at 10 the detector finds nothing (F1 nan/0.04). The result came from an ad-hoc sweep on the pre-measurement generator. Also not independent — shared algorithm, shared generator design, shared calibration input. **Deleted.** (roles 1, 3, 4, 6) |
| "LoCo and CICADA unmoved by the region" | LoCo does move (recall 0.84→0.89 quiet, 0.49→0.56 busy) because its context clamps to the region. **Deleted.** (roles 1, 4) |
| The region before/after table | Its numbers were stale, and the effect is confounded: point→span scoring landed the same day, one hour before the region fix, and moved SCE further. **Table removed; the mechanism and the 44% arithmetic retained.** (roles 1, 3, 4) |

---

## Residual ⚠ — the human must resolve these

1. **`jitter_sec = 0.36 s` is calibrated to a near-null statistic.** Its own
   circular-shift surrogate null is 0.42 s, and the source file marks the
   statistic "secondary, flagged-soft". The calibration does not round-trip:
   build at 0.36 and the estimator that produced 0.36 measures ~0.64 back;
   ≈0.30 is what inverts. Flagged in the doc and in `bench.py`. **Needs a
   decision on what to calibrate tightness to** — `span_med`/`width_med` are
   not null-dominated and are the obvious candidates. (role 6)
2. **`bg_rate_hz` is a background rate; the measured value is a total rate.**
   Realized total on a bench recording exceeds the value each regime is named
   for. Flagged, not corrected — correcting it means solving for the background
   that makes the realized total match, which shifts every number again. (role 6)
3. **The bench has never been run against a real recording.** The campaign it
   descends from is marked PROVISIONAL by its own record, adopted without the
   real-data validation its deck named as deciding. (roles 4, 13→n/a)
4. **`pick_operating_point` interiority is tested against the finite-F1 subset,
   not the declared grid**, so a grid widened until the detector stops detecting
   is scored as if those points were never searched. (role 6, minor)
5. **`score.py`'s module docstring** repeats the corrected distractor claim.
   Filed; not changed in this run because it is code, not the artifact.
6. **Blind round 1 returned 15 new findings and is recorded below.** Round 2 has
   not yet run, so the artifact is **not "done"**.

---

## Blind verify — round 1

Run by a reviewer given only the artifact, its figures and its sources, with no
knowledge of round-one findings or which parts had been touched. Roles 1, 3 and
10; role 10 re-run in full against the new renders, as the process requires.

**Not clean.** Fifteen new findings, three of them errors introduced or left by
the repair itself:

| finding | severity | disposition |
|---|---|---|
| "Four of six operating points beaten; LoCo and CoactDetect sit at their optimum" — **wrong on both regimes**; the beaten set differs by regime and LoCo is beaten in the busy one | blocking | fixed — stated per regime |
| "`interval_cv` realized CV is near zero regardless; the nominal value does not buy irregularity" — **the knob works**, realizing 0.00/0.06/0.11/0.23; and `bench.py` says "CV ~0.8" for the same recording | blocking | fixed in the doc — both numbers are real on different bases; `bench.py` still needs the same touch |
| Three headline comparisons (probe, distractors, participation floor) carried **no regime** and all three reorder in the busy one | high | fixed — regime named, reversals flagged |
| The two regime endpoints (0.0038 / 0.0175) are **derived through the same ratio the doc ⚠-flags two paragraphs later**, and carried no flag | high | fixed |
| The `jitter_sec` figure is **visually null** — 0.36 s is sub-pixel at 900 s across — and unlike `grid_sec` it was not caveated | high | caveated; an event-scale inset is filed |
| "medians run 31–47 s out" — SCE is 8.3 s, outside the stated band | mismatch | fixed |
| "2700 — the shortest recording that fits" — ~2480 fits | mismatch | fixed |
| "15 events at 120 s need 1680 s" — that is the *uniform* placer's requirement; the renewal placer the bench runs needs >1920 s | mismatch | fixed |
| "each detector's trace, with its threshold drawn" — **CoactDetect and RateDetect expose no threshold** to the viewer | mismatch | fixed |
| "every detector scored F1 0.9–1.0 on the invented values" — not reproducible (the same config also emitted the spurious region) | unverifiable | softened and flagged |
| "recruits six ROIs, just above the min_rois floor" — the shipped floor is 3, so six is 2× it | mismatch | fixed |
| `--param jitter_sec` without `--out` writes to the darkroom, not `docs/generator` | mismatch | fixed |
| The **Bokeh toolbar was still baked into the diagnostic PNG** — `make_generator_figures.py` sets `toolbar=None`, `make_diagnostic.py` did not | craft | fixed in `ui/diagnostic.py` |
| All nine figure y-axes named the swept value but never the plotted quantity, dropping CLAUDE.md's "identity + counts" convention | craft | fixed — `param=value · N ROI` |
| Right margin 229–258 px against a 10 px left margin (clip used the fixed viewport width) | craft | fixed — clip measures ink width too |
| Six load-bearing terms absent from `GLOSSARY.md`; "spike-sync" against the canonical **SPIKE-synch** | medium | fixed — glossary section added |

**What round 1 confirmed clean:** every measured value against the CSV
(0.0096/84, 0.36 with null 0.4166/47, participation 6, width 0.9, the 4.5/6/9/11
censoring series), the F1 range 0.32–0.78, the probe and distractor tables, the
41%/0% split, the 44% region arithmetic, `tol_sec`, every generator default, the
`optim_history` PROVISIONAL quote verbatim, the `simulation_plan` quotes, and
that the diagnostic figure's documented command reproduces it exactly.

---

## Process notes against this run

- The freshness gate passed via remote, which matters here: the repo carries an
  open report that this gate can return a confident wrong verdict for a family
  `gh` cannot resolve.
- **Two reviewers were briefed with content not in the artifact** — a sentence
  from an earlier summary, and two tables that live in a sibling file. Both
  reviewers caught it and said so. Briefing from memory of one's own writing
  rather than from the file is the same class of error the review exists to
  find, and it wasted part of two roles' budget.
- Roles 6 and 7 justified the process's insistence on extending review to the
  code: the two blocking defects that no prose-level reading could have found
  (the `.resolve()` bug, the distractors inside the probe) came from there.

---

## Blind verify — round 2

Same protocol, a different reviewer, no knowledge of round 1. **Also not clean:**
20 findings. Fixed in the artifact: the distance convention in the ✕/○ section
(measured onset-to-event, which is what makes "0% for every other detector" true —
by the span rule the document itself defines four lines earlier, SCE is 25%); the
unsourced ~0.64 round-trip figure, now marked as a one-off reimplementation
needing redoing; `2471 s` not `~2480`; the participation ratio 2.8–5.6× at both
ends; a ⚠ on `grid_sec`, whose four rows are pixel-indistinguishable and which had
none while `jitter_sec` did; the seed basis, now stated once at the top.

Fixed in code: `score.py`'s module docstring said firing on a distractor is "not
scored as a false alarm", contradicting both this document and its own behaviour;
the `interval_cv` figure caption still said the knob was inert; three figures had
y-labels abutting or clipping their neighbours (raised row height — found by
zoom-cropping, which an ink-box check cannot do); and the diagnostic **counted
distractors in its header and never drew them**, with no legend entry for the
threshold line either.

### Why it is not converging

Round 1 found 15, round 2 found 20, and the overlap is small. That is not two
unlucky draws — it is one defect with many faces:

> **Every number in this document is transcribed by hand from a computation.**

The sweep tally is the clearest case. Three review passes produced three
different counts of "operating points beaten" — four, five, three — from the same
sweep, because the answer turns on ties at the third decimal (CoactDetect 0.768
against 0.776) that reverse with the seed. Each pass was right about its own run.
The claim was never stable enough to state, and no amount of re-transcribing
fixes that. It has been **removed** rather than corrected: the section makes its
argument without a count.

The general form is the same. Sixty-odd quantities are copied from a bench that
has been recalibrated three times in two days. Each recalibration invalidates
them silently, because prose does not fail a test.

**The structural fix is to stop transcribing**: generate the numeric sections
from `bugarach.bench` at build time, the way the figures are generated, so a
recalibration updates the document or breaks the build. Until that lands, this
document needs a review pass after every calibration change, and will keep
drifting between them. Filed as a todo.

**What both rounds agreed was solid:** every measured value against the CSV and
its denominators, the null and censoring series, the region arithmetic, `tol_sec`
and the matching rule, every generator default, the `optim_history` PROVISIONAL
quote, the `simulation_plan` quotes, the TTX confirmation, and that the
diagnostic's documented command reproduces it exactly.
