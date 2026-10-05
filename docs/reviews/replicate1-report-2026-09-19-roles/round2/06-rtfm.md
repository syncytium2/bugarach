GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (methods / domain expert): findings on replicate1/report.html

**How I grounded it.** I read the code that produced both runs (weekend-runs @ 7a95e8a; `git diff e8764aa 7a95e8a` confirms the two runs differ only in the `--replicate` option): `score.py`, `bench.py` (BenchResult, pool_scores, FULL_GRIDS, budgets), `simulate.py` (distractors), `tune_learned_vs_coact.py`, `search_all_settings.py`, `learn/train.py`, `nets/chorus*.py`, `tube.py`, `line*.py`, `detectors/sliding.py`, `coact.py`, `cicada.py`, `sce.py`, `forks.md §14`. I also read the report builder `tools/make_replicate_report.py`.

To check the numbers I reran the run's own code paths on its own chosen settings and checkpoints. They reproduced the stored score rows exactly: 0 mismatches over 48 coded recordings and 240 net recording-refits. All intermediates were piped scripts, and the only files written were extracted checkpoints under `...\scratchpad\mb2\role06\ck`.

Literature: Bengio & Grandvalet 2004 (JMLR 5), "No unbiased estimator of the variance of K-fold CV", fetched; it supports the page's statement that folds within a draw are not independent. For Deep Sets (Zaheer et al. 2017, arXiv 1703.06114) I could reach only the abstract page, which does not state the pooling form; the citation is appropriate as the "shape". No other paper was needed.

## Findings
Columns: location · issue · severity · suggested fix · verified against a source (yes/no)

**1. §9 "Where the gap is", Figure 9, and the Figure 1 caption · HIGH · verified: yes**

*Issue.* The false-alarm split is not a partition. `archive_facts`/`other()` computes "anywhere else" as `n_fa − hot_fa − distractor_hits`. But `score.py`'s `distractor_hits` counts distractors (at most 6) touched by *any* call. That includes matched calls, and one call can touch several distractors. It is not a count of false-alarm calls.

*Evidence.*
- Figure 9 gives LoCo −0.70 and −0.67 "per recording anywhere else". That value is impossible, and `fig_split` hides it by clipping the bar with `max(0, wv)`.
- Recounting call by call, held-out, under the budget, first/second draw:
  - CoactDetect: anywhere else **1.69 / 1.28** (page 0.57 / 0.24); on a distractor 4.73 / 4.75 (page 5.84 / 5.79).
  - chorus_gain_norm: anywhere else **3.88 / 2.44** (page 3.51 / 2.10); on a distractor 5.23 / 5.11 (page 5.59 / 5.46).
- So the nets make about 2× CoactDetect's "elsewhere" false alarms, not the 6–9× the figure shows.
- Figure 1's "6 of its 6 unmatched calls fell on distractors" is false. On seed 2000 quiet at the reference settings, 4 of the 6 did (206, 341, 480 and 975 s) and 2 did not (1090.5 and 2213.6 s). The other 2 counted distractors (285 and 542 s) sit inside *matched* calls 8.7 s and 10.9 s wide.
- The build's assertions (`other_g`, "about as often on distractors") test the wrong quantity.

*Fix.* Classify each unmatched call from `fa_times` plus its span, or add a per-call "FA on a distractor" count to `score_row`. The rescore is cheap: about 20 s for the coded side and about 1 min per net per draw. Then redraw Figure 9 and correct the Figure 1 caption.

**2. §9 duplicate-call "suspicion", the summary ("Whether the gap survives a matched merge was not tested") and §10 · HIGH · verified: yes**

*Issue.* The test the page calls undone is about a minute of compute. I ran it, and the stated mechanism is refuted.

*Evidence.*
- There were **0 duplicate calls** (an unmatched call within 2.5 s of a planted event, `score.Score.dup_times` semantics) for chorus_gain_norm, chorus_norm, CoactDetect and LoCo, in the second draw, fold 0.
- I re-decoded chorus_gain_norm's 20 budgeted refits per draw at `merge_gap_frames=80` (8 s), keeping the same threshold:

  | Draw | F1, 2 s merge | F1, 8 s merge | Gap to CoactDetect (0.748) |
  |---|---|---|---|
  | First | 0.7177 | 0.7313 | 0.030 → 0.017 |
  | Second | 0.7227 | 0.7328 | 0.025 → 0.015 |

- So a matched merge closes about 40% of the gap, and about 60% survives.
- In the second draw, 983 of 1,173 "elsewhere" false alarms are more than 20 s from any other call. None are within 2 s, and 72 are 2–8 s away.
- The longer merge helps by folding a nearby distractor into an event's matched call, not by fixing duplicates. In fold 0, 13% of distractors were covered only by CoactDetect's matched calls, against 5% for chorus_gain_norm.
- "The score files do not count duplicate calls" is true of `score_row`, but `Score.n_duplicate` exists.

*Fix.* Replace the suspicion with this measurement, and say the threshold was not re-selected at 8 s. Merging can only lower call counts, so budget admissibility can only improve.

**3. §10 "the coded detectors tune their merge (up to 8–30 s)" · MEDIUM · verified: yes**

*Issue.* The tops of the merge grids in `bench.FULL_GRIDS` are:
- CoactDetect, LoCo, rate+context: 8 s
- binned SCE: 30 s
- SPIKE-synch `max_gap`: **2 s**
- locust `sce_min_distance_frames`: **16 frames = 1.6 s** (the bench grid is dt 0.1 s)

Two coded detectors therefore top out at or below the nets' fixed 2 s.

*Fix.* "Up to 1.6–30 s", naming the two short ones.

**4. §3, chorus_norm vs chorus_gain_norm, "differ only in whether the vote's steepness is fitted" · MEDIUM · verified: yes**

*Issue.* chorus_gain_norm's vote is sigmoid(g·(h−b)), with a learnable per-channel gain (started at 8) **and** a learnable offset (started at 0.5). That is 8 parameters, which matches 1,905 − 1,897. chorus_norm's vote is sigmoid(h): steepness fixed at 1, no offset.

*Fix.* "chorus_gain_norm adds a fitted steepness and offset to each vote."

**5. §10 asymmetries · MEDIUM · verified: yes (from code; effect not measured)**

*Issue.* An unlisted train/inference mismatch affects the two chorus nets. `norm=True` standardises each cell over whatever span the model sees. That is a 4,096-frame crop in training but the whole 27,000-frame recording, dense stretch included, at inference. `chorus.py`'s own docstring records this.

*Fix.* List it among "not treated alike".

**6. §8, collapse counts ("292 of 864 and 306 of 864 scored inner fits…") · MEDIUM-LOW · verified: yes**

*Issue.* 864 counts (fit, scored fold) pairs: each of the 432 inner fits is scored on 2 folds. Every collapse held on both folds, except one tube fit in the first draw. The per-fit counts out of 432 are:

| Net | First draw | Second draw |
|---|---|---|
| chorus_norm | 146 | 153 |
| chorus_gain_norm | 75 | 75 |
| line_length | 8 | 11 |
| tube | 7, plus 1 on one fold only | 6 |

§4 says "432 inner fits".

*Fix.* Count fits.

**7. §5 "a Gaussian z-test against the exact null at α = 10⁻⁵" · LOW-MEDIUM · verified: yes**

*Issue.* The null's mean and SD are exact, but its tail is Gaussian-approximated, and the exact Poisson-binomial tail is far heavier. On 6 recordings (seeds 2000–2002, both backgrounds, reference settings):
- 625 windows pass the Gaussian test and 306 pass the exact one.
- Where the Gaussian p ≤ 10⁻³, the exact tail is a median of about 4.4×10³ times larger.

α is nominal. This does not change the comparison, because the budget uses measured rates.

*Fix.* "A z-score using the exact null's mean and SD, at a nominal α = 10⁻⁵."

**8. Summary and §9, "It is a lower bound" · LOW · verified: no (a statistical argument)**

*Issue.* One realised difference per entry is not a bound. Also, the untuned, F1-alone and budgeted entries of one net share fits, so its 8 "moves" are not independent.

*Fix.* "Likely understates."

**9. §3, locust "against a per-cell circular-shift threshold" · LOW · verified: yes**

*Issue.* The threshold is one absolute population count, built from circular shifts of each cell. The null uses single-frame sums while detection uses windowed sums (`cicada.py`), which is consistent with locust's 449–527 calls per hour in the dense stretch.

*Fix.* Reword.

**10. §5 "the best F1 among candidates…" and the Figure 3 box · LOW · verified: yes**

*Issue.*
- For coded detectors the budgeted choice is a coordinate-search path, not the best over all candidates.
- A move away from an over-budget current point is taken regardless of F1 (`rescue`).
- The rule "keep a move only if F1 rises by >0.002" describes the search on F1 alone.

*Fix.* One clause.

**11. §2, distractors and the "15/21, F1 0.83 practical ceiling" · LOW · verified: yes**

*Issue.* Distractors are placed uniformly in 120–1100 s, independently of planted events. A long merge can fold one into a hit; Figure 1's own recording shows 2 of 6. So a long-merge detector can beat the "ceiling".

*Fix.* Add a clause.

**12. §4, how a net picks its threshold (not stated on the page) · LOW · verified: yes**

*Issue.*
- `pick_threshold` maximises F1 pooled across both backgrounds, while every other selection averages per-background F1.
- `train` asks it for `n_val=4` seeds from 2 recordings, so each recording is read twice. This is harmless for pooled F1.

*Fix.* Optional note.

**13. §8, the explanation under Table 3 · LOW · verified: no**

*Issue.* "Threshold … carried onto refits whose output is calibrated differently" is plausible but unmeasured. A held-out fold is 1 h of dense stretch per background, so Poisson noise alone can push one refit over a ceiling of about 16 per hour.

*Fix.* Hedge it, or compare inner-fit and refit rates at the same threshold.

**14. §5 citation of `docs/forks.md` §14 · INFO · verified: yes**

*Issue.* forks.md says sliding has shipped in `OPERATING_POINTS` since 2026-09-16. The code (`CODED_BASE` comment, 8525be3) and the page say the binned versions are still listed. The page is right and the cited doc is stale.

**15. The screenshots I was given · INFO · verified: yes**

*Issue.* `light_1100_08.png` shows older §9 text ("That is the pattern a short, fixed merge would produce — …") than the built HTML. The renders may predate this build.

## What I checked and found correct
- **Nested CV and fold dealing:**
  - No held-out seed reaches any selection (audit assert).
  - Budgets come from training seeds only.
  - Round-robin dealing and `fold_check` both pass.
  - Refits train on 10 of 70 recordings in disjoint windows per seed; inner fits on 10 of 46.
  - Thresholds are picked on 2 recordings from the training folds.
  - 432 inner fits per net (24 × 3 × 6), 50–55 refits per net, 1,943 fits in total.
- **Leakage:** goal 1's sliding values were searched on seeds 1–96, which overlap neither draw.
- **Scoring:**
  - F1 pooled per background, then averaged.
  - Precision excludes false alarms overlapping the dense stretch (`BenchResult.n_scored`).
  - Match tolerance 2.5 s against the call's span.
  - F1 = 0.125 for a one-call collapse is exact.
- **Budget:** ceilings are 1.6 × the reference's rates (7.0/4.4 in bench), the floor never binds, and only the quiet empty recording is gated. Figure 4's numbers match `meta.json`.
- **Paired gaps:** means and SDs (0.030/0.005 and 0.025/0.018), 8 of 8 folds negative, gap move 0.005.
- **Between-draw spread:** medians 0.010 and 0.006.
- **Figure 7:** same configuration in B and C, seeds 1 and 2 hatched.
- **Nets:** merge 2 s (20 frames at dt 0.1 s); 23 configurations drawn plus the untuned one, identical in both draws.
- **Raster figure:** same recording and `run_detector` path as the run; the CoactDetect dense-stretch average of 0.75 matches.
- **Simulation parameters:** planted-event cell counts 10/6/3 (matlab_round), jitter is an SD, and the quiet/busy rates are 0.0052/0.019.
- **Attributions** (checked against `docs/detector_history.md` and code): Cossart, Aronov & Yuste 2003; the CICADA derivation; Kreuz SPIKE-synchronization 2015.

## Files
- Artifact: `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`
- Builder: `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py` (`archive_facts`, `other()`, `fig_split`, the §9 assertions)
- Scoring semantics: `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\score.py` (`distractor_hits`, `dup_times`)
- Merge grids: `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\bench.py` (`FULL_GRIDS`)
- Vote and norm: `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\learn\nets\chorus.py`
