GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(No editing tool held, nothing edited. One note about the run, not the artifact: during my bench-calibration rerun the PostToolUse naming hook flagged `bugarach\2026-10-14-coordinated-fraction-under-treatment\4x\coordinated-fraction_before-after_pilots-...pdf` in the darkroom. I did not write that file. It belongs to another session or a sync. My commands wrote nothing to the darkroom or the repo, and no scratch files.)

## Grounding: what I checked against the sources

- **The estimator against the theory.** f₂ and f₃ are the factorial cumulants κ₍₂₎ and κ₍₃₎ (`factorial_cumulants`). For a compound-Poisson count they equal λw·E[k(k−1)] and λw·E[k(k−1)(k−2)], so the fixed model's k = f₃/f₂ + 2 holds, and so do the binomial (MIP) model's p = f₃/((N−2)f₂) and share = λk/N ÷ rate (`solve`, `per_recording`). The README's formulas, "90 ordered pairs / 720 triples", "720÷90 = 8 = k−2" and the developer-section formulas are all correct.
- **The shift surrogate (`shifted`).** Slides are distinct multiples of 2 windows plus one common offset, centred, so the span is ±32 s at w = 1 s and 32 cells. At 2 s and 4 s windows it scales to ±64 s and ±128 s. The README states this correctly for 1 s.
- **Whether the explainer's truth matches the tool's.** The script's `recovered/planted` equals the tool's `calibrate` ratio. Decoys count in the tool's `truth()`, as the README says.
- **Figure 5A's "same false excess whatever the length" claim, checked analytically.** For a stretch longer than the slide span, the leftover f₂ is h²·Σ_{i≠j}|dᵢ−dⱼ|/T per window. That is a constant, about 388 pairs per recording for h = 0.1334, 32 cells and 2 s spacing. The README's 350–380 agrees. **Verified.**
- **The 5B, 5C and Figure 6 numbers and the Figure 3 and 4 medians** against `numbers.json`. All match the prose. This includes 0.67–1.12, 14–19%, 22–23%, 26–69% / 34–55%, 0.742 of onsets added by the 28× stretch, and the median interval of 41.25 s from `2026-09-25-real-intervals/summary.json`.
- **The tool's own check at its shipped settings (`mcr._sim` + `calibrate`, realistic spacing, 48 recordings, all three windows), re-run by me:**
  - 1 s: fixed share −15.6%, binomial −2.3%. This matches Figure 3C.
  - 2 s: fixed −16.1%, binomial −3.7%.
  - 4 s: fixed −15.6%, binomial −3.8%.
  - It passes at every window.
- **Citations.**
  - Grün et al. 1999, the "multiple shift" method: abstract fetched.
  - Pipa et al. 2008, J Comput Neurosci 25:64: confirmed.
  - Staude/Rotter/Grün 2010 (29:327), 2008 (Neural Comput 20:1973), Front Comput Neurosci 4:16; Kuhn/Aertsen/Rotter 2003; Reimer et al. 2012; Ehm et al. 2007: these match what I know of them. I did not fetch them. Volume and page numbers look right.

## Findings

**1. "How the method works › Why the fixed model reads low", sentence "From size variation alone it reads 5% low (one size) to 18% low (three sizes)"**
- **Issue:** The cause is attributed wrongly. With one size there is no size variation: the fixed model is exact (analytic error 0.0%), so all of the 5% at one size comes from moments split across window edges. Size variation alone gives −14% for sizes 10, 6 and 3 (analytic). The 18% is about 14 points of size variation plus about 4 of edge splitting.
- **My simulation** (planted moments only, no background, 40 recordings each):
  - one size: −6.7% at 1 s, −1.9% at 2 s, +1.8% at 4 s;
  - three sizes: −18.9%, −16.1%, −13.7%, against −14.0% with no edge splitting.
- This is also why "120 s only" improves from −18% at 1 s to −14% at 2 and 4 s in Figure 4.
- **Severity:** medium. It is a wrong causal claim in the one paragraph that explains the bias.
- **Fix:** "Size variation alone reads about 14% low with three sizes (none with one). Splitting at window edges adds about 5 points at 1 s (the whole of Figure 3B's 5%) and fades at 2–4 s."
- **Verified:** yes (analytic, plus my own simulation using the tool's `population_cumulants` and `solve`).

**2. "The question", sentence "One input comes from real recordings: the bench's intervals between moments (Figure 3C), measured on the default data set, which is now under a contamination stop"**
- **Issue:** This is false. Every simulated recording takes these settings from real recordings:
  - the quiet and busy rates (`bench.REGIMES`, re-measured 2026-09-23 "on the default folder's 66 recordings", which is `senktide_ttx`, the folder now under the stop);
  - the per-cell rate shape and the burst shape;
  - N = 32 and participation 0.203 (re-measured on the same 66);
  - the jitter of 0.106 s (from the correlogram on an earlier folder);
  - the stretch level of 0.1334 (the same 66-recording run).
- The quiet and busy rates are also *background* rates, made by subtracting this measure's own fixed-model share, which this page shows reads about 16% low.
- So the stop's artifact (cells showing events at the same moments) reaches every figure's settings, not just Figure 3C.
- **Severity:** medium-high. It understates what depends on the stopped data set, on the page whose whole subject is that artifact's kind.
- **Fix:** "The simulations' settings (cell count, rates, burst shape, jitter, how many cells join a moment, the stretch level, and Figure 3C's intervals) were measured on real recordings, most of them on the default data set now under a contamination stop. The background rates were themselves measured with this tool's fixed model." Also qualify the Terms entry for Quiet/busy: these are background rates (coordinated share subtracted) over the recordings that clear the shape floors.
- **Verified:** yes (bench.py lines 896–898, 1056–1071; `current_export.toml` default = `senktide_ttx`, 66 recordings).

**3. "Where the method comes from", the phrase "the spike-train shifting surrogate (Pipa … 2008, after the multiple-shift method of Grün and colleagues)"**
- **Issue:** Grün et al. 1999's multiple-shift method shifts trains against each other to *detect* coincidences without binning (it integrates exact coincidences over all small shifts). It is not a way of measuring chance. Calling the surrogate "after" it mixes up two uses of shifting.
- The tool's two-offset window averaging is closer to the MS idea than the surrogate is.
- I could not confirm "where the published ones are random" for NeuroXidence from the sources I reached.
- **Severity:** low.
- **Fix:** Drop "after the multiple-shift method…", or say "related in spirit to the multiple-shift coincidence count of Grün et al. 1999, J Neurosci Methods 94:67". Soften or verify "the published ones are random".
- **Verified:** partly (Grün 1999 abstract fetched; NeuroXidence shift scheme not read in full).

**4. "For developers", the list of docstring disagreements**
- **Issue:** The page lists two places where the code's docstrings disagree with the figures, and misses two more that a developer reading the sources will hit:
  - (a) `bench.REGIMES`' docstring says the fast estimator "is calibrated at the 1 s counting window and, on the fast stream, at no other", with errors of +0.46 at 2 s and +1.00 at 4 s. My rerun of the tool's own check at shipped settings gives −16% at 2 s and −16% at 4 s, both passing. Figure 4 agrees with the rerun, so the docstring is stale.
  - (b) `population_cumulants`' docstring says the two offsets "halve the share of shared moments split by a window edge". Averaging two offsets with the same expected loss does not reduce that loss. The README's "steadies this but does not recover it" is the correct version.
- **Severity:** low.
- **Fix:** Add both to the developer notes, or file them against the code.
- **Verified:** yes (rerun above; the expectation argument plus the simulation in finding 1).

**5. "The check, and the two models", sentence "with the stretch in, the check fails, reading the share 43% high"**
- **Issue:** `CAL_NO_PROBE`'s +43% was measured on 2026-09-22 on the old spacing (15 events), with the 0.127 Hz stretch and the backgrounds of that time. The bench now has about 7 events per recording and a stretch of 0.1334. Since ADR-0009, `BENCH_RECORDING` carries no stretch anyway, so the tool's `hot_window=None` is now redundant rather than a choice.
- The present tense reads as a current measurement.
- **Severity:** low.
- **Fix:** "recorded on 2026-09-22, before the bench moved to realistic spacing, that with a stretch in the check failed (+43%)". Note that the bench's own recording no longer carries the stretch.
- **Verified:** yes (`CAL_NO_PROBE` text; bench.py lines 1045–1048 and 1162–1170).

## Confirmed correct, no finding

- Step 1's two-offset averaging.
- The step 2 slide geometry (±32 s at 1 s; distinct by at least 2 windows; circular).
- The step 3 algebra and Figure 2B's 1.21/0.20 + 2 ≈ 8.1. With no edge splitting the figure would be 8.7, and edge splitting pulls it down.
- The "k reads high, λ low, share low" mechanism (analytic −14%).
- The decoys are included in C's right answer.
- The `pooled_ratio` and no-answer behaviour, and that the share can come out negative.
- `shape_usable` floors (300 s / 20 events / 5 cells) and `MIN_BASELINE_SEC` = 900 s (the "15 minutes").
- The stretch is additive in `simulate.py`, so "rises by 0.1334, 28× in all" is correct.
- Figure 5C's thinning gives a true threefold rise with the mean held.
- The "bracket" disagreement the page already lists: confirmed, since both models read low on 3A and 3C.

Paths:
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\bench.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\simulate.py

Sources:
- [Grün et al. 1999 abstract, Detecting unitary events without discretization of time](https://brainworks.biologie.uni-freiburg.de/1999/journal%20papers/abs-jnscimeth1999-gruen.htm)
- [NeuroXidence (Pipa et al. 2008)](https://www.epistemio.com/p/Xd4R46GB)
- [Elephant spike train surrogates documentation](https://elephant.readthedocs.io/en/v0.7.0/reference/spike_train_surrogates.html)
