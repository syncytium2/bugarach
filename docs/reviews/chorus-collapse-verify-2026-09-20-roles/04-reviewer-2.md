GRANT 4 ok — Read, Grep, Glob, Bash

**Role 4, adversarial reviewer ("Reviewer 2"). Fresh, blind pass on the built page.**

ARTIFACT: `<worktrees>/chorus-verify/docs/learned/chorus_collapse/index.html`

WHAT I DID (so the trace is checkable): read the built page (SVG stripped for reading only, into scratch); read `census.json`, `collapse_table.json`, `selections.json`, all 14 `replays/*.json`; read `tools/diagnose_chorus_collapse.py` in full; read `src/bugarach/learn/train.py` and `src/bugarach/learn/nets/chorus.py` in the `replicate-run` checkout (`<worktrees>/weekend-runs`); read the sibling `docs/learned/tuned_vs_coact/replicate1/report.html`. I then **re-ran forward passes on the census recording for all 231 collapsed fits plus 8 working fits**, recomputed the §2 counting null with its variance and its ceiling, re-scored two fits from the `scores` archives, and ran one alternative-explanation test of my own. I edited nothing (I do not hold Edit/Write, correctly). I did not open anything under `docs/reviews/`. Note: the worktree venv at `chorus-verify/.venv` has **no torch**, so the model work used `bugarach-worktrees/weekend-runs/.venv` (torch 2.14.0+cu126, registers both chorus nets), read-only.

---

## Findings

### BLOCKING

**B1 · Answer box bullet 3 and §4 · "The signal stops in the head" is false for a measurable minority, and for 42% of chorus_gain_norm's collapsed fits.**
The page states the mechanism universally: *"**The signal stops in the head**, the eight layers that turn the pooled per-ROI votes into the output."* The supporting count (a silent head layer in 153/153 and 75/75) is correct, but it does not establish that claim, because `census.json` stores only `min_share_varying` — the **minimum over the 8 layers**. It does not record *which* layer, and it never records the head's **input**. I measured both directly on the census recording (`quiet:9000`, 26,946 frames, 33 ROIs, EDGE=400, SILENT=1e-3), for every collapsed fit:

| | chorus_norm (155) | chorus_gain_norm (76) |
|---|---|---|
| first silent layer = 1 | 31 | 31 |
| first silent layer = 8 (layers 1–7 all alive) | 12 | 8 |
| first-silent-layer histogram (1..8) | 31, 11, 21, 33, 13, 25, 9, 12 | 31, 8, 3, 6, 9, 4, 7, 8 |
| **head INPUT constant (max channel SD < 1e-3)** | **10** | **32 (42%)** |
| median of head-input max SD | 0.081 | **0.0022** |

For those 10 and 32 fits the pooled statistics the head receives are constant — the signal **never reaches** the head, so the head is not where it stops. For chorus_gain_norm the median collapsed fit's head input sits at 2× the silence threshold, i.e. the "the head is at fault" story is threshold-marginal for that net as a whole. Separately, the 12+8 fits whose *only* silence is at layer 8 directly contradict the answer box's *"a collapsed fit's [head] is never woken"*: in those fits seven of eight head layers are awake.
*Suggested fix:* add the head-input SD to the census (the builder already hooks it in `_onset_response`, and `census`'s own module docstring at line 17–19 already promises *"how well the head's input and the output separate event frames"* — the field was never stored); store the per-layer `varying` vector, not its min; restate the bullet as *"in most collapsed fits the signal reaches the head and dies inside it; in 10 of 153 chorus_norm and 32 of 75 chorus_gain_norm fits it never reaches the head"*; and split the chorus_gain_norm claim from the chorus_norm one. **Verifiable against a source: yes — I ran it.**

**B2 · §5 "Related work", last sentence · "That it prevents this collapse is this page's result." — "collapse" is a calls-on-held-out-recordings definition, and no warm-up run was ever scored on calls.**
Collapse is defined in the terms box as *exactly one call on every recording a fit was scored on*. The warm-up evidence is: **7 distinct runs, hand-picked, judged by final training loss < 0.5**, on **one net** (no chorus_gain_norm), with **no held-out scoring**. Worse, the `replay` function returns only the log — **no `state_dict`** — so the counterfactual models were discarded and *nobody, including the authors, can now score them* without re-running the GPU replays. The page's most consequential claim is therefore not re-checkable from the published artifacts at all. §7 does disclose "judged by training loss, not by calls"; the Related-work sentence, which is where a reader takes away the result, does not.
*Suggested fix:* either soften to *"a 200-step warm-up brought training loss below 0.5 in 6 of 7 hand-picked collapsed runs of chorus_norm; whether those fits would have made normal calls on held-out recordings was not tested"*, or save the counterfactual checkpoints and score them. **Verifiable: yes** (replay JSON schema at `diagnose_chorus_collapse.py:411-420` carries no weights; §7's own wording).

### MAJOR

**M2 · Answer box / §4 / Figure 4 · The vote-response test borrowed from PR #596 demonstrably lacks the power the page gives it. I MADE IT FAIL.**
The page reports *"4 of 153 chorus_norm and 19 of 75 chorus_gain_norm are as deaf as plain chorus"*, and concludes *"For them the votes still respond and the head does not pass the response on."* Using the page's own deaf cut (max plain-chorus control, 0.000281) against my direct measurement of the head's input on the census recording:

- chorus_norm: 10 fits have a constant head input; only 4 fail the onset test → **6 fits pass the deafness test while their votes are, in fact, constant on a real recording** (their onset values: 0.000, 0.000, 0.000, 0.002, 0.002, 0.002).
- chorus_gain_norm: 32 have a constant head input; 19 fail → **13 false passes**.

So the test can fail (untrained plain chorus does fail it, as the page says, and 4+19 trained fits do) — but it under-detects the encoder-dead population by 2.5× and 1.7×. It is a synthetic 32-ROI / 4,096-frame probe with a threshold inherited from a *different architecture at initialisation*, and the page has a strictly better, already-computed measurement available. Related: the headline contrast *"a median of 0.40 against at most 0.0003 for plain chorus"* compares a **trained chorus_norm fit** against an **untrained plain chorus** — two differences at once. The page's own matched control (untrained chorus_norm, 0.02–0.03) shows most of that gap is the `norm` layer, not training; collapsed 0.40 vs working 0.52 is the honest contrast and it is far less dramatic.
*Suggested fix:* report head-input SD on the census recording as the primary deafness measure and demote the #596 probe to a consistency check; lead with the 0.40-vs-0.52 contrast. **Verifiable: yes — I ran it.**

**M3 · §3, second paragraph · The "correction" of the replicate report is a straw man, in a public repo, about a sibling public report.**
The page says: *"That report reads the 111 fits collapsed in both draws as the same fits failing twice. The comparison in §2 shows that is what the configurations' rates alone predict: this page corrects that reading."* What the replicate report actually says (`docs/learned/tuned_vs_coact/replicate1/report.html`, §8): *"The two draws share their configurations and training seeds, so the same fits largely fail in both (111 of chorus_norm's are the same fit): Table 2 shows where training fails in this search, not two independent measurements of how often."* It attributes the overlap to **shared configurations and seeds** — the same explanation §2 reaches — and draws the conclusion that the draws are not independent replicates of the rate, which §2 does not overturn. There is nothing to correct. Given CLAUDE.md's portfolio posture and that both documents are public, publicly "correcting" a sibling report for something it did not say is a cost with no benefit.
*Suggested fix:* replace with *"the replicate report already attributed the overlap to the shared configurations and seeds; §2 quantifies that and confirms no excess remains for the individual fit."* **Verifiable: yes — quoted from the sibling report.**

**M4 · §2 last paragraph · "The configuration accounts for the overlap and nothing is left for the particular fit" is an accepted null reported without its spread. (The test DOES have power — I checked — but not the power the sentence claims.)**
I reproduced the null (conditional/hypergeometric: per configuration, E|A∩B| = k₁k₂/18) and added what the page omits:

| | observed | expected | **null SD** | max possible | headroom above expectation |
|---|---|---|---|---|---|
| chorus_norm | 111 | 111.5 | **2.5** | 135 | 23.5 = **9.4 null SDs** |
| chorus_gain_norm | 38 | 39.6 | **2.3** | 63 | 23.4 = **10.2 null SDs** |

Good news for the page: this is **not** a ceiling-saturated test — it could have moved by ~9 SDs, and the observed z is −0.2. But with SD 2.5 the result rules out a fit-level effect larger than about **5 fits**, not "nothing". Nor is the independence assumption free: the page itself reports significant within-draw seed clustering (p = 0.002), which is exactly the kind of dependence that inflates the true null spread.
*Suggested fix:* give the null's spread and restate as *"no excess is detectable; an excess of more than about 5 fits would have shown"*. **Verifiable: yes — recomputed from `collapse_table.json`.**

**M5 · §2 last paragraph · "So the seed's effect cannot be put down to its starting weights" is a strong causal negative resting on p = 0.147 with a positive point estimate (r = 0.24).**
Nineteen configurations × 3 seeds, deviation-from-configuration-mean correlation; a one-sided permutation p of 0.147 with r = 0.24 is a failure to reject in an underpowered test, not a demonstration of absence. The follow-on — *"the recordings it picks are at least as likely"* — is elimination without a positive test, and it does not distinguish "which recordings" from the **crop order**, which the seed also fixes and which would equally fail to carry across draws.
*Suggested fix:* *"a carry-over of the seed's effect across draws was not detected (r = 0.24, p = 0.147), so the starting weights are not established as the cause; which recordings the seed picks, and the crop order, remain untested."*
I also tested the one cheap mechanism the page gestures at: `pos_weight = (1−pos)/pos` from the 10 recordings each seed draws, for all 18 second-draw fits of Figure 1's configuration. It ranges only **175.3–186.0**, and the single working fit (seed 2) sits at 176.7, inside the collapsed range. So that candidate is largely ruled out — a check the page could have run in one second and did not. **Verifiable: yes — I ran it.**

**M6 · §2 / Table 1 · Table 1 does not support "the learning rate separates the configurations almost completely" — and the page owns two clean matched contrasts that do, and shows neither.**
Table 1's cells are unbalanced and are not crossed: chorus_norm 4×4 is 1 configuration at lr 0.003, 3 at lr 0.01, 3 at lr 0.03, each with different `top_m` and step counts, so every cell comparison confounds lr with top-m and length. The page flags depth×length but not this. However, the grid **does** contain fully matched sets (everything but lr held fixed):

- chorus_norm, **4×4, top m 4, 1,800 steps**: lr 0.003 → **0 of 36**; lr 0.01 → **0 of 36**; lr 0.03 → **26 of 36**.
- chorus_norm, **8×6, top m 2, 3,600 steps**: lr 0.01 → **1 of 36**; lr 0.03 → **31 of 36**.
- chorus_gain_norm, 4×6, top m 8, 900 steps, gain 16: lr 0.01 → 12/36; lr 0.03 → 23/36.
- chorus_gain_norm, 4×6, top m 8, 3,600 steps, gain 8: lr 0.003 → 3/36; lr 0.01 → 8/36.

The first row is a three-point, fully controlled dose-response and is the strongest single piece of evidence in the whole diagnosis. *Suggested fix:* add a small "matched configurations" table; it converts §2's claim from descriptive separation to a controlled contrast, and it also shows lr matters for chorus_gain_norm too (which the answer box currently hedges away as "shape at least as much"). **Verifiable: yes — recomputed from `collapse_table.json`.**

**M7 · §2 / Table 1 · chorus_gain_norm's starting vote gain is a declared grid factor, is in the data, and is never analysed — while the page attributes that net's pattern to encoder shape.**
The terms box lists *"and, for chorus_gain_norm, the vote gain's starting value"* as part of a configuration. It then never appears again: not in Table 1, not in Figure 2's mark encoding (which carries shape), not in §2's prose. It orders collapse cleanly within cells:

- lr 0.03, 4×4: gain 4 → 15/72 (21%); gain 8 → 3/36 (8%); gain 16 → 3/72 (4%)
- lr 0.03, 4×6: gain 4 → 61/72 (85%); gain 16 → 23/36 (64%)
- lr 0.01, 4×6: gain 8 → 24/108 (22%); gain 16 → 12/36 (33%)

This is a design variable the study manipulates, and the result is pooled across it. *Suggested fix:* add a gain column/row to Table 1 or state explicitly that gain was not examined and why. **Verifiable: yes — recomputed.**

**M8 · Answer box bullet 6 / §3 / §6 · Both of chorus_norm's collapsed refits came from lr 0.01 — so neither of the page's two concrete remedies would have prevented the only chorus_norm collapses that actually reached the comparison.**
From `collapse_table.json`, the four collapsed refits are: chorus_gain_norm lr 0.03 (one per draw), and **chorus_norm lr 0.01, 4×6, top m 8, 3,600 steps, second draw, seeds 1 and 2** — configuration `75d44745`, which collapses in only 3 of 36 inner fits (8%), i.e. one of the "rare" ones the page exonerates. §3 states the lr 0.01 fact in passing but §6's remedy list ("drop lr 0.03 from chorus_norm's grid… add a warm-up… change the head") never notes that the first two would not have touched either delivered failure. The answer box's *"Tuning picked no lr-0.03 configuration for chorus_norm under either selection rule"* reads as reassurance while chorus_norm still shipped two collapsed refits.
*Suggested fix:* say so in §6, explicitly — it is the strongest argument for the fourth (catch-at-the-end) option, which is the only one of the four that covers what actually happened. **Verifiable: yes.**

**M9 · §3 / Table 2 · The "refits that collapsed" column under "the false-alarm budget" is measured with a rule that cannot see the failure the budgeted rule actually produced.**
`collapse_table()` (`diagnose_chorus_collapse.py:119`) scores collapse as `n_detected == 1` **at the fit's own threshold**. The replicate report — quoted in this very paragraph for its footnote *"made one call per recording **or called nothing** on the held-out fold"* — states: *"Under the budget the threshold sits above everything those refits output, so they call nothing"*, and *"under the budget 3 refits called nothing at all (1 of tube's in the first draw, fold 0; 2 of chorus_norm's in the second draw, fold 1)"*. So the page's Table 2 describes chorus_norm's budgeted refits as having made one call, when the sibling report says they made none. The column header will be read as "collapsed under this rule"; what it actually counts is "a refit whose configuration this rule picked, and which collapsed at its own F1-picked threshold". I scanned every score row in **both** draws' `scores` archives for both nets and found **0 fits that called nothing at their own threshold** — confirming the zero-call mode exists only under the budgeted threshold, which the page's data path never reads.
*Suggested fix:* either compute collapse at each selection rule's own threshold, or rename the column and state in the tnote that the zero-call mode is invisible to this measurement. **Verifiable: yes — sibling report text plus my archive scan.**

**M10 · §5, first paragraph · "standard deviation 0.0003 to 0.0025 logits on the first batch" is an UNTRIMMED number, while every other SD in the page is trimmed — and §4 spends a paragraph explaining why trimming is necessary.**
`replay()` logs `logit_sd=float(out.detach().std())` (line 407) with **no `EDGE` slice**, while the head-varying hook beside it *does* slice `[..., EDGE:-EDGE]` (line 374). 800 of each 4,096-frame crop (20%) are inside the padding-contaminated region. The effect is large: the as-run collapsed replay's final logged `logit_sd` is **0.166**, while the census says every collapsed fit's trimmed output SD is ≤ 0.00012 — three orders of magnitude, i.e. that 0.166 is essentially all edge. No headline claim rests on it, but the quoted "0.0003 to 0.0025 logits" is presented as evidence the output starts flat and is in fact measuring the zero-padding.
*Suggested fix:* trim it, or label it "untrimmed, whole crop" wherever it appears. **Verifiable: yes — read the code, cross-checked against `census.json`.**

**M11 · §5 / Table 3 / Figure 7 · The warm-up's "1.4 of 7" null mixes two different outcome definitions, and the fits in Table 3 were never replayed as-run.**
Two problems, compounding:
(a) `reroll = Σ(1 − collapse-rate-of-configuration)` is a **calls-based** expectation ("would not have collapsed"), compared against `wu_ok`, a **training-loss-based** count ("final loss < 0.5"). The page writes both as "train", so 6-of-7 vs 1.4-of-7 is apples to oranges unless the proxy is validated — and it is validated on exactly **one** working fit (the single as-run working replay).
(b) *"A replay with nothing changed reproduces the collapse, so doing nothing trains none of them"* — the only as-run collapsed replay is `2736f584…, **seed 0**`. Table 3's row for that configuration is `2736f584…, **seed 1**`. **None of the 8 fits in Table 3 was ever replayed as-run.** Determinism was verified (bit-exact checkpoint match on 2 replays), so the inference is defensible, but the sentence asserts a measurement that was not made on these fits.
In the page's favour, I checked the proxy against everything the replays do record and it holds perfectly: all 12 "trains" runs end with **0 silent layers and batch output SD 2.48–9.36**; both "does not train" runs end with **3 or 8 silent layers and SD 0.000–0.166**. So the 0.5 cut is not knife-edge (0.07–0.22 vs 1.50/1.70) — but that also means the page had a criterion much closer to its own collapse definition available and chose the weaker one.
*Suggested fix:* report the outcome as "head fully awake and output SD ≥ 2.5 at the end", which the replay logs already carry, and state the null in the same units; and say explicitly that the table's fits were not replayed as-run but that the replay is bit-deterministic. **Verifiable: yes — recomputed from all 14 replay JSONs and the replay filenames.**

**M12 · §5 / §7 / Table 3 · The hand-picking is disclosed, but its direction is not, and the within-configuration choice is not disclosed at all.**
§5 says the 8 fits were *"picked by hand, not at random: of the 3 lr-0.03 configurations left out, 2 collapse least of all"*. Excluding the least-collapsing configurations **lowers the reroll null** (`1 − share` is largest exactly there), i.e. the exclusion runs in the direction that flatters the warm-up. The page does not say which way the bias points. Separately: within Figure 1's configuration 33 of 36 fits collapsed, so *which* collapsed fit was chosen was a 1-in-33 decision, and the page says nothing about how any of the 8 within-configuration choices was made. If any was made after looking at a curve, that is selection on outcome.
*Suggested fix:* state the direction of the exclusion bias, state the within-configuration selection rule (or that it was arbitrary/first-by-key), and give the reroll null recomputed over **all 11** lr-0.03 configurations as a sensitivity. **Verifiable: partially — the selection procedure is not recorded anywhere I could find.**

### MINOR

**m13 · §4, footnote on EDGE / the builder's `EDGE` comment · The justification for trimming 400 frames is a receptive-field argument that does not apply to these two nets.** `diagnose_chorus_collapse.py:61-64` reasons *"the net's receptive field is at most 318 frames each way (encoder 63, head 255), so 400 clears it."* But `chorus_norm`/`chorus_gain_norm` standardise the encoder output **over the whole time axis** (`chorus.py:105-107`, `h.mean(dim=2)` / `h.std(dim=2)`), a global operation: the padded ends contaminate the normalising constants used at **every** frame, so no finite trim "clears it". The contamination is a per-channel shift/scale and so does not threaten a variation-based verdict, but the stated reason is wrong and a future reader will reuse it. *Fix:* state that the normaliser is global, and that the trim removes the convolutional edge artefact only. **Verifiable: yes — read the architecture.**

**m14 · §4 / §5 · The census and the replays normalise over different windows, and the page moves between them without saying so.** The census recording is **26,946 frames**; training crops are **4,096**. `chorus.py`'s own docstring says in terms: *"a 4,096-frame training crop and a whole recording at inference are standardised over different spans."* Figure 3 (census) and Figure 5 (training batches) are therefore not the same measurement, and §5's "the head starts mostly silent" is measured on one span while §4's "every collapsed fit has a silent layer" is measured on the other. *Fix:* one sentence in §4 or §7. **Verifiable: yes.**

**m15 · Figure 3 caption · "no working fit has either" bundles an empirical finding with a near-tautology and presents both as evidence.** §4 states the implication itself — *"A silent layer passes nothing that changes, so the output is flat"* — and the head is a plain feed-forward `_dilated_stack` with no skip connections, so *working ⟹ no silent layer* is essentially forced. The empirical content is entirely in the other direction (collapsed ⟹ silent layer). Across all 974 census fits I confirmed the three measures are perfectly coextensive with **zero** disagreements: `min_share_varying == 0` ⟺ `logit_sd < 0.01` ⟺ `collapsed`. *Fix:* caption the finding as "every collapsed fit has a silent head layer" and note that the converse follows from the architecture. **Verifiable: yes.**

**m16 · §6, fourth bullet · The proposed catch was validated against a quantity it is nearly identical to, and its blind spot is not named.** "Flag a fit whose held-out output does not vary" is being validated against "the fit made one call covering the recording" — and a flat output *is* what makes one call. The gap (0.00023 vs 0.82) is therefore not evidence that the guard generalises. The unnamed blind spot is the other route to one call: an output that varies a lot but never dips below a floor threshold. **I tried to make this fail and could not**: the two working chorus_norm fits sitting on the grid floor sit above their threshold for **96.2% and 95.5%** of the census recording's frames, which looked promising, but on their own scored folds they return median F1 **0.708** and **0.738** with ~20 calls. So the blind spot is real in principle and had no instance in these runs. *Fix:* name the blind spot in one clause; say the guard is validated against a near-identical quantity. **Verifiable: yes — I ran both checks.**

**m17 · §3 · "4 refits collapsed across both draws" is a raw count with no denominator.** There are **210 refits** in `collapse_table.json`; the page never gives that number, so a reader cannot size the damage (4/210 = 1.9%). *Fix:* give the rate. **Verifiable: yes.**

**m18 · Terms box · The page's collapse rule is narrower than the footnote it quotes, and that is never said.** `collapse_table()` counts only `n_detected == 1`; the replicate footnote quoted in §3 covers *"one call per recording **or** called nothing"*. A fit that called nothing is counted as **working** in every table on this page. I scanned both draws' full `scores` archives: **0 fits called nothing at their own threshold**, so the branch is empty here — but that is a fact worth one clause, because it is what makes the page's rule and the report's footnote interchangeable. **Verifiable: yes — I ran the scan.**

**m19 · §5 / §6 · 200 steps is a magic number whose value the result is demonstrably sensitive to.** The page justifies 200 only *relatively* (10× smaller than Ma & Yarats's 2,000) and never says why 200 was chosen. Its own 50-step run fails. Nothing between 50 and 200, and nothing above 200, was tried, so the honest statement is "200 worked on 6 of 7 hand-picked runs, 50 did not", not "a warm-up prevents this collapse". *Fix:* say what was tried and what was not, beside the number. **Verifiable: yes.**

**m20 · `diagnose_chorus_collapse.py:17-19` · The builder's docstring promises two measurements the census does not store.** It says `census` records *"how many units of **each** head layer … pass anything that varies"* (only the min is stored) and *"how well **the head's input** and the output separate event frames from the rest"* (no head-input field exists). Both are exactly the measurements that would settle B1. *Fix:* store them, or correct the docstring. **Verifiable: yes.**

---

## Explicitly: for every test I probed, could I make it fail?

| Test | Could I make it fail? |
|---|---|
| Silent-layer rule ("every collapsed fit has one, no working fit does") | **No** as stated — 0 disagreements in 974 fits, and the working→not-silent half is near-deductive given the architecture. But I broke its **interpretation** (B1). |
| The #596 vote-response test | **YES.** 6 chorus_norm + 13 chorus_gain_norm collapsed fits pass it while their head input is constant on a real recording. |
| §6 output-SD separation | **No.** Best candidate (two working fits above threshold 96% of the census recording) still scores median F1 0.71/0.74 on its own folds. Blind spot is theoretical only. |
| The collapse label ("exactly one call") vs "called nothing" | **No** at the fit's own threshold (0 zero-call fits in either draw), but the mode exists under the budgeted threshold the page never reads (M9). |
| §2 counting argument | **The test itself CAN fail** — headroom 23.5 = 9.4 null SDs, observed z = −0.2. Not vacuous. The failure is in the *wording* ("nothing is left"), not the arithmetic (M4). |
| The 0.5 training-loss cut | **No** on the 14 replays (0.07–0.22 vs 1.50/1.70) and it agrees perfectly with silent-layers and output-SD on all 14. Its problem is that it was never tied to calls (B2, M11). |
| My own alternative (per-seed `pos_weight` drives the seed effect) | **Tested and largely ruled out**: 175.3–186.0 across all 18 fits of Figure 1's configuration, the one working fit at 176.7, inside the collapsed range. |

## Credit where due (so the ledger is not one-sided)
The bit-exact checkpoint reproduction of both as-run replays is a strong check that could have failed and did not. The 50-step warm-up is a genuine negative control for the warm-up claim. The untrained-plain-chorus control is a genuine negative control for the onset test. The step-count-twin design for "settled early" is clever and correct. §2's counting null is the right conditional null and is not ceiling-limited. §7's Limits are unusually honest — four of my findings are aggravated versions of things §7 already half-says, and the fix for those is to move the caveat up into the answer box and the captions, where the reader takes the claim away.

## Files referenced
- Artifact: `<worktrees>/chorus-verify/docs/learned/chorus_collapse/index.html`
- Data: `…/chorus-verify/docs/learned/chorus_collapse/{census.json, collapse_table.json, selections.json, trace.json, replays/*.json}`
- Builder: `<worktrees>/chorus-verify/tools/diagnose_chorus_collapse.py` (key lines: 56–64 EDGE/SILENT, 119 collapse rule, 218–238 `_head_probe`, 259–262 census fields, 370–408 replay logging — note `logit_sd` at 407 is untrimmed, 892–896 overlap null, 1030 `reroll`)
- Architecture: `<worktrees>/weekend-runs/src/bugarach/learn/nets/chorus.py` (lines 72–74 and 105–107, the global normaliser)
- Sibling report: `…/chorus-verify/docs/learned/tuned_vs_coact/replicate1/report.html` (§8, the "111 of chorus_norm's are the same fit" passage)
- Scratch (mine only, nothing written to repo or darkroom): `<scratch>/{page_stripped.html, replicate_stripped.html, perlayer.json}`
