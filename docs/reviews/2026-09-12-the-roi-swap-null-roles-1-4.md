# Murderboard on the ROI-swap proposal — roles 1-4

> **Written as each report arrived, not reconstructed afterwards.** This thread has now lost
> three sets of role reports to the assumption that a transcript is durable; these are landed
> verbatim, scrubbed only for absolute paths.
>
> Artifact reviewed: [`proposals/2026-09-12-the-roi-swap-null.md`](../proposals/2026-09-12-the-roi-swap-null.md)
> at `c8ddb745` (the first draft, before any fix).
>
> ⚠ **Do not grep these reports for a grant line.** Role 4's transcript contains both
> `GRANT 4 ok` and `GRANT 4 MISMATCH`, because every compiled agent file carries the literal
> `GRANT n ok — <tools>` and the transcript quotes it. The role's **final message** is
> authoritative; role 4 declared **MISMATCH**, and so did role 2.

---

## Role 1 — Claim & data verifier, "Prove It" (`murderboard-prove-it`)

**GRANT 1 ok — Read, Grep, Glob, Bash**

Two findings are severe enough to change the document's conclusions, and both are the same
defect that withdrew the two previous drafts.

### CRITICAL 1 — "Fast currently fails it" is WRONG; the production 20-seed control says fast passes

Quoted: *"**One precondition, already failing on one stream.** `real_vs_real` … **Fast currently
fails it**"*

**WRONG.** Source: `<darkroom>/bugarach/2026-09-11-surrogate-screen/discriminator/steps_excluded/fast/controls/negative_seeds.json`

| stream | seeds | flag_rate | significant seeds | accuracy range | mean |
|---|---|---|---|---|---|
| fast | 20 | **0.05** | **seed 0 only** (0.5386, P=0.035) | 0.4373–0.5386 | **0.4948** |
| slow | 20 | 0.0 | none | 0.4446–0.5301 | 0.4977 |
| cossart | 20 | 0.0 | none | 0.4583–0.5298 | 0.4978 |

The 0.5386 / P=0.035 the document quotes **is seed 0**, the single flagged draw of twenty. Fast's
negative control flags at *exactly the nominal alpha* and its mean accuracy is **below** chance.
Fast does not fail its precondition; it passes at n=20.

This is not a new discovery. The review record the document itself cites says so in terms:
*"Production also carries 20-seed negative-control reruns for all three streams that v2 never
used: fast `flag_rate 0.05` (1 of 20, seed 0 only), slow `0.0`, events `0.0`… That is the third
probe-over-production substitution in a document written to end the first."* The document says
"This document does not restate their conclusions" — and then re-inherits the exact error the
record was written to retract.

**Blast radius:** the closing paragraph of the proposal section; the whole precondition-recovery
stage (premise, both expectations, and its STOP condition); the literature section's parenthetical.

### CRITICAL 2 — the "not verified" ROI figure is in the very file cited two columns away

Quoted: *"The outside read reports 1,261 of 2,630 ROIs as not estimable… **This document has not
verified that figure** — the cell-level status counts … are a different granularity"*

**The premise is WRONG.** `discriminator.csv` carries columns **`not_estimable_rois`** and
**`n_roi`**. It is the same file, at the right granularity, and the document read that file for
two other tables.

- `not_estimable_rois == 1261` appears in **exactly 18 rows**, all `slow` / `operational_time`
  cells; `n_roi` = 2630 in every row that reports it.
- 2630 independently reconciles: `sum(n_roi_recorded)` over the 84 rows of `slices.csv` = **2630**.
- Distribution: fast — 40 of 142 reporting rows nonzero, range **1302–1566 (49.5%–59.5%)**;
  slow — 66 of 168 nonzero, range **1261–1538 (47.9%–58.5%)**.

The cell-level counts quoted (326/218 and 106/99) are themselves **CONFIRMED** exactly — but they
are offered as a substitute for a number that did not need substituting.

### HIGH 3 — citing Stella's conclusion against an explicit standing prohibition

`docs/INDEX.md` row 125 carries: *"⚠ **Do not cite Stella 2022's conclusion**: its discussion says
the surrogates agree, its figure 10 says they do not."* Commit `ca8f9ea` records why. The document
uses the withdrawn conclusion as *affirmative support* for its own design.

### HIGH 4 — the provenance citation is a dead link on this branch

`docs/reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md` does not exist on this branch,
nor on `main`. It exists only at `860e5ee`, reachable solely from `origin/surrogate-screen-overnight`.
Every other relative link resolves.

### HIGH 5 — the source of record for group membership was never consulted

`slices.csv` in the current export, columns `group_id`, `mouse_id`, `n_roi_recorded`:

| group | recordings | mice |
|---|---|---|
| ORX | 25 | 12 |
| MALE | 22 | 12 |
| OVX | 20 | 10 |
| DI | 17 | 10 |
| **total** | **84** | **44** |

No mouse appears in two groups. Splitting by mouse makes the side quest a **4-class problem with
n = 44 independent units, smallest class 10 mice**. The document never states this and gives no
power consideration.

### MEDIUM 6 — "surviving out to 1.6 s fast / 1.4 s slow" is right on fast and misleading on slow

- fast `rigid_shift`: survives 0.1, 0.2, 0.4, 0.8, **1.6**; fails at 2.5. Contiguous — exact.
- slow `rigid_shift`: **fails at 0.7 s (P=0.005)**, survives at 1.4 s (P=0.08), then fails at 2.5,
  2.8, 5.6, 11.2. A **single isolated non-significant point at P=0.08**, far more consistent with
  noise than with survival.
- **All five fast survivors carry `void = True`.**

### MEDIUM 7 — "126 of 248" is literally right and understates by half

248 fast candidates, 126 voided, all with void_reason `"negative control (real against real)
flagged: accuracy 0.539, P = 0.035"`. The other 122 are `intractable` with a blank void field.
Among fast candidates that **produced a number at all**, it is **126 of 126 — 100%**. Slow: 0 voided.

### MEDIUM 8 — the run folder does constrain what `real_vs_real` pairs

`fast/controls/negative.json` records `n_pairs = 830`, `n_mice = 44`, `icc = 0.0`, 5 folds, 199
permutations — against `meta.json`'s `n_windows = 1669`. 830 ≈ 1669/2: both classes drawn from the
same 84 recordings / 44 mice, so class membership is not recording identity.

### LOW 9 — "all nineteen rows" — **18**. `leak_table.csv` is 19 lines including the header.

### LOW 10 — fast J=1.6 lower bound is **0.306**, not 0.307. Everything else in that table matches.

### LOW 11 — the leak table's scope is unstated: `n_recordings: 29`, against the screen's 84.

### Confirmed without qualification

`0.40 s` / `3.20 s` floors, every row · `real_share` 0.0 · 543 windows · fast 0.5386/0.035/True and
slow 0.5060/0.415/False · 326/218 and 106/99 · FOUNDATIONS §9 rate IQR 0.0052–0.0190 Hz **verbatim
including provenance** · 3.7× spread · ORX/male/diestrus directions verbatim · tube **1,149
parameters exactly** (dropping `bright` gives 1113) · Stella's six methods exactly · no
cross-preparation surrogate in that catalogue · Amarasingham 2012 in substance · "thirteen
statistics" · `correction_reach` exists · board block 065.

⚠ **Note on "cells are summed":** the code is `bright = pooled.sum(dim=1, keepdim=True) / max(n, 1)`
— a **mean**, not a sum. Permutation invariance holds either way, so the claim is sound as used.
Worth saying because the mean makes `bright` a *per-ROI* activity level, which is exactly the
preparation-identity quantity the proposal predicts will leak.

### Unverifiable

"Most baseline windows contain no coordinated event at all" — no source, none found · the
pseudopopulation / noise-correlation claim — no paper cited · Perkel, Gerstein & Moore (1967) — not
on the shelf · "Two sessions examined it independently" — no artifact records the second.

---

## Role 2 — Citation & reference validator, "DOI or Die" (`murderboard-doi-or-die`)

**GRANT 2 MISMATCH — missing Grep, Glob; holds Read, Bash, WebSearch, WebFetch.** Substituted
`grep`/`find` via Bash, so no check was blocked. Did not write to the shelf.

### C1 — the literature section violates the standing INDEX row-125 prohibition

The sentence is *textually accurate* — Stella's Significance Statement says "using the most robust
surrogate method (trial shifting; TR-SHIFT)". That is precisely the conclusion row 125 forbids
citing, and the document cites it bare and then leans the design's credibility on it.

Re-verified from the shelf PDF, not the commit message. Figure-10 results text: *"the same pattern
occurs for SGLF behavioral context in all surrogates, but TR-SHIFT"* — the recommended method is
the one that misses what the other five find. Pattern counts across 24 datasets: UD (N:203, L:121),
UDD (14,14), JISI-D (10,10), ISI-D (10,10), **TR-SHIFT (7,14)**, WIN-SHUFF (11,11).

**Fix:** cite Stella for what their *measurements* show, never their recommendation.

### C2 — "the pseudopopulation … eliminates noise correlations" is uncited, and the shelf paper offered does not support it

`elsayed_cunningham_2017_byproduct.pdf` **does not support this claim**. Full-text grep:
`pseudopopulation` — 0 hits; `noise correlation` — **1 hit, in a reference title**. That paper is
about rate-preserving maximum-entropy surrogates, a different construction. Citing it here would be
fabricated support.

Candidate replacement: **Cunningham JP & Yu BM (2014), Nat Neurosci 17:1500–1509,
doi:10.1038/nn.3776** (DOI verified via Crossref). ⚠ **I did not read it** — metadata only. Do not
paste it in on my word.

### H1 — "Perkel, Gerstein & Moore (1967)" is ambiguous between two papers

> Perkel DH, Gerstein GL, Moore GP. *Neuronal spike trains and stochastic point processes.
> **II. Simultaneous spike trains.*** Biophys J 1967;7(4):419–440. PMID 4292792, PMC1368069,
> doi:10.1016/S0006-3495(67)86597-4.

There is a **Part I** by the same three authors, same issue, about one train. A bare "(1967)" does
not distinguish them.

"Is 'shift predictor' their term?" — **unresolved.** Amarasingham et al. 2012 calls it the
**"shuffle predictor"** and cites it three ways; Pipa et al. 2008 attributes **"shift-predictors"**
to **König (1994)**. Could not obtain the 1967 text (cell.com 403, PMC bot-check, Europe PMC XML
empty).

### H2 — TR-SHIFT is described but attributed to nobody, and its origin is one paper further back

Stella's methods section: *"As an alternative to the dithering of single spikes, **Pipa et al.
(2008)** introduced dithering of the entire spike train."* And Pipa 2008 is not the root — Pipa
credits the **multiple-shift method (Grün et al. 1999)**, *J Neurosci Methods* 94:67–79.

This is **the exact defect this repo already corrected once**: the shelf README records that "a
citation trace that stops at Gerstein stops one paper short" of Date, Bienenstock & Geman 1998.

### H3 — the central mechanism is NCE and the mixture argument is NCE's own result, both uncited

The optimal-discriminator statement is **Gutmann & Hyvärinen (2012)**, JMLR 13:307–361 —
`ml/gutmann_hyvarinen_2012_nce.pdf`, **on this project's shelf**. The staged design is a
**classifier two-sample test**, **Lopez-Paz & Oquab (2017)** — also on the shelf. Neither is cited.

`lit/ml/README.md` already carries: *"⚠ A 2026-09-12 draft dropped this citation entirely from a
section stating the premise in NCE's own terms."* **The same omission has now recurred.**

### H4 — 3d-SPADE and the Grün group's released harnesses are named prior art and appear nowhere

Stella A, Quaglio P, Torre E, Grün S (2019). *3d-SPADE.* **Biosystems 185:104022**,
doi:10.1016/j.biosystems.2019.104022, PMID 31449837. The forward trace pays off:
`github.com/INM-6/SPADE_surrogates` accompanies a **2021** paper by the same four authors — a
citation set complete on the 2022 paper still misses the group's released harness.

### M1 — "no cross-preparation surrogate in the catalogue" is TRUE; the surrounding rhetoric overreaches

Verified true by full-text grep. **But** cross-subject recombination is a standard, named null in an
adjacent field: **hyperscanning inter-brain synchrony**, where "pseudo-pairs" / "surrogate dyads"
are the routine control, with its own methodological critique literature.

Searched: parallel-spike-train surrogates, jitter/conditional inference, EEG/MEG connectivity
surrogates, hyperscanning, pseudopopulation decoding, calcium assembly surrogates.
**Not searched — residual ⚠:** self-supervised/contrastive learning on neural time series (CEBRA,
MYOW), fMRI surrogate construction, ecology/genomics null models.

**I found no use of "chimeric surrogate" in EEG/MEG connectivity.** Four searches returned only
chimeric brain models and chimeric antigen receptors. "Could not locate" is not "does not exist."

### M2 — Amarasingham is cited for the rule and not for the warning that bears on this design

The paper's worked example of conditional inference **is trial shuffling**, and it carries a caveat
the document does not:

> "an excess of synchronies in the original pairing, relative to the trial-shuffled pairings,
> **rejects the hypothesis that all pairings are equally likely**, not a hypothesized lack of
> precision of spike timing."

Invoking "Amarasingham's rule" to bless the construction while omitting the same paper's warning
about the same construction is selective citation.

### M3 — TR-SHIFT is shifted per trial, and the edge-loss defect is bugarach's, not the method's

Stella: *"shifting all spike times identically … **independently neuron by neuron and trial by
trial**."* And they measured the opposite of a count defect: *"For TR-SHIFT, the differences in
spike count are negligible."* The edge loss is a property of **bugarach's no-wrap implementation**.

### M4 — dead internal citation (same as role 1's HIGH 4).

### L1 — "Stella's catalogue" — first author used as the lab. The last author is **Sonja Grün**.
### L2 — no reference list, no DOIs, no venues, for any of the three external attributions.
### L3 — "shortcut" is canonically *shortcut learning* (Geirhos et al. 2020) — ⚠ cited from memory.

### What the document does NOT get wrong

Stella 2022 metadata exactly right · the sub-floor claim correctly kept as bugarach's own
measurement, **not** misattributed to Gerstein — the known trap was not repeated · the dithering
lineage error not repeated · Amarasingham author order right and says what it is cited for · all
internal todo links resolve except the one · FOUNDATIONS §9 supports its claim · the no-pruning
ruling accurately characterised · **no claim of novelty for the construction.**

### Residual ⚠

1. **NOBODY WAS ASKED.** No evidence anyone corresponded with Grün, Stella or Amarasingham about
   whether a cross-session surrogate exists. **One email to the INM-6 group is the cheapest check
   available and it has not been sent.** Per CLAUDE.md, cite any reply, never quote it.
2. Verified to one step short on Perkel 1967.
3. Not read, cited on shelf-README authority only: Gutmann & Hyvärinen, Lopez-Paz & Oquab.
4. Not held: Grün et al. 1999; 3d-SPADE; Perkel 1967; Cunningham & Yu 2014.
5. Unsearched fields (above).
6. Fetched nothing to the shelf — the main thread is the only legitimate operator.

---

## Role 3 — Consistency auditor, "Cross-Examiner" (`murderboard-cross-examiner`)

**GRANT 3 ok — Read, Grep, Glob.** No Bash, so three off-branch rows are marked unverifiable.

### B1 — the precondition stage's "first task" is already answered in a companion ON THIS BRANCH

`docs/reviews/2026-09-11-surrogate-screen-build-agents.md` line 50, describing
`surrogate_discriminator.py`:

> "**Negative control: consecutive real windows of the same recording**, with which one is called
> 'real' drawn at random."

It pairs **within** a recording. Corroborated arithmetically: candidates carry `n_pairs=1669`, both
`real_vs_real` rows carry `n_pairs=830`. The whole of the precondition stage is asking a settled
question, and the answer falls on the branch the plan labels "Expected if the design is viable."

### B2 — the support argument presents a definitional zero as the screen's headline measurement

`report_steps_excluded.html`, its own glossary: *"**the floor** — the shortest within-ROI interval
actually present in a folder's baselines"*, and: *"⚠ Because the real sub-floor rate is 0 in every
window **by construction**, this reduces exactly to 0.5 × (1 + the dithered share)"*.

The floor is *defined* as the observed minimum, so `real_share = 0` **cannot take another value**.
The support argument may still be sound on extractor-physics grounds, but it is sourced to a
measurement that cannot fail.

### B3 — the literature section cites a fast result the proposal section declares void

Every fast candidate, rigid shift included, is stamped `void=True`. One result is treated as both
established and as a precondition failure.

### B4 — the load-bearing rate IQR is under an open non-reproduction finding the doc never mentions

`docs/todo/2026-09-10-the-foundations-rate-range-does-not-reproduce.md`: *"**None of them gives that
range.** Counting zero-event ROIs, which FOUNDATIONS §9 itself says must stay in, the lower quartile
is zero."* And GLOSSARY describes the same two numbers as a quartile across **recordings** where
§9 calls them per-**ROI**. The leak prediction needs the per-ROI reading specifically.

### B5 — the Stella claim contradicts INDEX row 125, the 2026-09-10 ruling, and a 2026-09-12 todo

`docs/todo/2026-09-10-which-surrogates-enter-the-screen.md` (status done, RULED): *"**Their TR-SHIFT
recommendation is a tiebreak, not a performance claim** — Tony's read … The first of the five
reasons given is that it *'is easy to explain and to implement'*."*

### M1 — the 1,261/2,630 figure is in the file the doc says it is not, and "minority" is wrong

Same file, same granularity (`not_estimable_rois`, `n_roi`). 2,630 − 1,261 = **1,369 estimable, a
majority**. And the eighteen rows are all `slow`/`operational_time`; every other row sampled reads 0.

### M2 — the construction-validity stage asserts a stronger invariant than the proposal establishes

Subset-of-support does not give identical marginals. At the global matching level the pools differ
in rate — exactly the leak the proposal predicts. So that stage can beat chance **for the reason the
design exists to test**, and its stop rule instructs the reader to "Fix and re-run" the builder.

### M3 — broken internal link (the only one; the other four resolve). Two code references point off-branch.
### M4 — "nineteen rows" — eighteen.
### M5 — the precondition stage's STOP condition depends on the stage after it, which the ordering rule forbids.
### M6 — "Every stage emits its figure" — three of five name none.
### M7 — the ladder figure cannot show the prediction it tells the reader to look for: `k/N = 0` **is** the real class, not a point on the axis. And dispersion (rate units) and accuracy ([0.5,1]) have no stated mapping.
### M8 — the leak table's two evidence columns are one number: AUC = 0.5 × (1 + share), verified exactly.
### M9 — "band statistic" is coined, uncounted, and collides with two existing senses of "band".

### Minor

m1 numeric slip 0.306 · m2 "session" and "preparation" each carry two referents · m3 the ladder is
declared with four rungs and used with two or three · m4 "item 4" resolves two ways in the file it
points at · m5 the slow floor: the artifact is right and a todo is wrong (2.80 s) — worth fixing
there · m6 two published tables of the same leak measurement disagree and neither cites the other ·
m7 the stop rule is claimed to close a todo written about something else · m8 the proposal and the
closing section disagree about whether per-ROI leak power matters · m9 "cells are summed" is the
docstring's word and the code takes a mean.

---

## Role 4 — Adversarial reviewer, "Reviewer 2" (`murderboard-reviewer-2`)

**GRANT 4 MISMATCH — missing Grep, Glob; holds Read, Bash.** Bash covered the grep work.

**Verdict: reject in present form, revise and resubmit.** The core construction is sound and the
support-violation argument is the best thing in the thread. But the two load-bearing inferences —
*the leak cannot be per-ROI* and *intercept is signal, slope is leak* — are both false, the second
in a way that converts the two worst documented confounds in this tree into the affirmative result.

### F1 (blocking) — the ladder is structurally blind to the confounds that matter

Whole-field brightness steps (**74% fast / 82% slow cells "fire" at once**) and the unflagged
motion-correction pinning of 12 ROIs in 4 recordings are **real-only cross-ROI coincidences,
destroyed identically at every matching rung** → they load on the **intercept** and are scored as
coordination. Two open todos say this; the proposal cites neither.

### F2 (blocking) — "the leak cannot be a per-ROI statistic" is false

Support-subset ⇒ no *support violation*. It does **not** ⇒ no per-ROI leak. The document's own
mixing section draws exactly this hard/soft distinction and the proposal section forgets it. Four
counterexamples, all made of untouched real trains: **window position within the donor's own
recording** (rate runs down over a recording; baseline windows are cut backward off a 20-minute cap);
**donor sampling weight** (uniform over ROIs vs over recordings give different marginals);
**duration eligibility** (long-T targets can only draw from long-baseline recordings); and **the
encoder**.

### F3 (blocking) — the precondition paragraph is false in three ways, and the code is on the branch

```python
def negative_control_pairs(X, recording_ids, mice, seed=0):
    """Real against real: each real window paired with another real window of its own
    recording, which of the two is called "real" drawn at random.
    ... The random orientation makes the pair exchangeable by construction — slow drift
    within a recording cannot masquerade as a label — so this checks the machinery
    (folds, scaling, the null), and must not be flagged."""
```

And `run_summary.json`: `flag_rate: 0.05, n_seeds: 20`. One flag in twenty at α = 0.05.

**A consequence beyond this document: 126 of 248 fast candidates were voided on a seed-0 coin flip
while the 20-seed flag rate sat in the same JSON.** That is worth its own todo regardless of what
happens to this proposal.

### F4 (blocking) — the arithmetic stage cannot predict what it is claimed to predict

It measures dispersion of per-ROI **first-order summaries**. A field step adds one onset to 74% of
ROIs — in real *and* in chimera the per-ROI rate/ISI/width/burstiness dispersion is unchanged. The
number cannot move for the failure it is claimed to predict.

### F5 (blocking) — no fold rule on the main test, and donors are not fold-controlled

A chimera built from a donor whose mouse sits in the test fold puts test data in the training set.

### F6 (blocking) — "flat within seed noise" passes for the wrong reason: the noisier the seeds, the more certainly it passes. No `n_seeds` is declared anywhere.

### F7 (major) — the construction-validity stop rule has only one exit, so the null gets tuned until its own check goes quiet. No tolerance band on "exactly chance", where the same instrument flags a perfect control 1 time in 20.

### F8 (major) — "destruction is total" sold as a virtue. **A null that destroys everything identifies nothing.** This is the canonical Elsayed & Cunningham 2017 objection — on the shelf, flagged in the shelf README as exactly this, and **not cited**. Amarasingham 2015 (nonidentifiability) likewise.

### F9 (major) — "slope" is computed over a nominal 4-level axis with no metric. The only zero-leak rung — donors from the target recording, time-displaced — **is rigid/circular shift, already measured**, and the literature section says so without putting it on the ladder.

### F10 (major) — the ablation is a false dichotomy. Removing `bright` removes an **absolute level**, not composition.

### F11 (major) — FOUNDATIONS §9 records a group × **treatment** interaction. The side quest trains on **baseline** trains. The premise is not supported by the source it cites.

### F12 (major) — mouse-folds do not break a **batch** confound, and the within-group chimera **preserves** the batch signature.

### F13–F16 (major) — the precondition STOP can never fire · the arithmetic GO accepts H₀ with no power and no multiplicity, and rewards its least-powered arm · no n anywhere; units differ per stage (window 1669, recording 84, mouse 44), and the screen's own machinery reports `powered: False` for six of twelve positive controls with `required_mice` up to **104** against 44 · the encoder is an unstated third party: `encode()` **truncates** rather than rounds and **clips** out-of-range onsets onto frames 0 and n−1, manufacturing a boundary pile-up — the exact support violation the first design died of.

### F17–F22 (minor–major) — nineteen/eighteen · two windowings quoted without naming either · the dead link · the 1,261 figure is settleable in one pass and is **0 for 102 fast and 102 slow cells** · Perkel and pseudopopulation uncited · **the document never says which export folder the main test runs on**, and the field-step severity depends on the answer.

### The strongest alternative explanation for any result this can produce

**"The tube learned to recognise whole-field acquisition artifacts."** It beats coordination on every
criterion the design uses to award credit: cross-ROI (so "the leak cannot be per-ROI" waves it
through), real-only (chimeras cannot contain it), destroyed equally at every matching level (so the
ladder reads it as **intercept, i.e. signal**), and large — 74% / 82% of cells appearing to fire at
once, which the todo describes in terms as "exactly the signature a coordination detector exists to
find."

### Power, computed

- `real_vs_real` at 830 pairs has an MDE of ≈**0.543**. Fast's observed 0.5386 is **below its own
  MDE**. The negative control is less powered than the tests it voids.
- At 1669 pairs the MDE is ≈0.530. A chimera leak of 0.52 is invisible to the construction-validity
  stage and entirely available to the tube.
- Side quest: significance threshold ≈**0.357** accuracy at 44 mice; ~**124 mice** for 80% power
  against a true 0.35.
- The ladder as specified is 4 × 4 × S training runs, doubled by the ablation to **32S**, with S
  undeclared and the GO rule a function of S.
