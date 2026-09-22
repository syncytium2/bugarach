# Role 6 — RTFM (round 2, blind pass, verbatim as returned)

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I also hold SubagentHandback, which is not an editing tool. I hold no Edit, Write or NotebookEdit.)

# Role 6 (RTFM), round 2 blind pass: "Methods: detection of coordinated calcium events" @ 464d995

**Sources I read before reviewing.** They are saved under `<scratchpad>\mb6r2\`:
- Cossart, Aronov & Yuste 2003, full text (`cossart2003.pdf`, `c.txt`).
- Kreuz et al. 2017, NJP full text (`kreuz2017.pdf`, `k17.txt`).
- Dard et al. 2022, Bocchio et al. 2020 and Cecchini et al. 2021, full text from Europe PMC (`PMC9363116.txt`, `PMC7486410.txt`, `cec.txt`).
- PySpike #89 (issue and PR), read through `gh`.
- The Zenodo record for CICADA.
- The tuning tool from `origin/tune-bench-comparison` (`tune.py.txt`).

**Code I read.** `coact.py`, `loco.py`, `sliding.py`, `sce.py`, `cicada.py`, `sync.py`, `rate.py`, `simulate.py`, `bench.py`, `score.py`, `search_all_settings.py`, `leaderboard.py`, `tune_net_merge_gap.py` (origin/HEAD), `learn/encode.py`, `learn/train.py`, `learn/nets/{chorus,chorus_gain_norm,tube,line,line_length}.py`, `call_measure.py`, `measure_calls.py`.

**Run records I read.** `2026-09-17-full-search/sliding5/search.json`, `2026-09-18-replicate-run-status/results/meta.json`, and `2026-09-21-full-cohort-default/{detect,detect_coact_and_chorus}` (`detector_settings.csv`, `run.json`, `calls_measured.csv`).

## Findings

Each row gives: location · issue · severity · suggested fix · verified against source.

**1. Width and amplitude section (lines 364–377) applied to binned SCE** · HIGH · verified: yes
- **Issue.** The measure is centred at "onset plus half its reported width" and widened to [onset, onset + width_sec]. For binned SCE, width_sec is the event spread inside the bin (`width_def = tightness`) and onset is the start of the bin, so the measurement window does not cover the bin. The Scoring section itself says binned SCE's interval is its bin; the measure does not use that interval.
- **Evidence (fast stream, `calls_measured.csv`).** 157 of 1,665 binned SCE calls (9.4%) found zero events. 347 (21%) have a core of fewer than 3 cells, although every SCE call has at least 3 cells by construction (strength minimum is 3). Example: 20240813_39, baseline, call at 1770 s with 8 cells and 1.4 s spread; 0 events measured. The detections' `n_roi` column is 0 on the same rows, the same symptom.
- **Fix.** Measure binned SCE over its bin (onset + extent_sec) and rerun `measure_calls`. Otherwise withdraw binned SCE width and amplitude and say why.

**2. Analysis of recorded data (lines 348–351), and locust (lines 165–170)** · MED-HIGH · verified: yes (code)
- **Issue.** locust rolls each cell over the whole recording and sets one threshold for baseline and treatments together. A circular-shift null assumes each cell's rate is stationary over the span it is shifted across. When a treatment changes the rate (senktide), the threshold is a mixture of the two periods, and the higher-rate period clears it more easily. So locust's baseline-versus-treatment call rates are confounded by the rate change itself. It is also the most rate-fooled detector (elevated-rate limit 25 calls min⁻¹). The text states the fact but not this consequence.
- **Fix.** Run `threshold_scope="regional"`, which already exists in `cicada.py`, or state that locust's treatment contrast is rate-confounded.

**3. Binned SCE (lines 162–163), description of Cossart 2003** · MEDIUM · verified: yes (PDF)
- **Issue.** The paper's threshold is "the number of coactive cells exceeded in a single frame in only 5% of these histograms" (1,000 interval reshuffles per movie). That is a maximum-statistic threshold across the movie's frames, applied to every peak. "Thresholded each movie's largest single-frame count" reads as though only the largest count was tested.
- **Why it matters.** Binned SCE's 98th percentile, pooled over bins and surrogates, is a per-bin bar with no correction across the roughly 120 bins in a window. It is much more lenient than the method it descends from.
- **Fix.** Restate Cossart's rule as above and note the difference.
- **Checked and correct.** Bocchio 2020 (circular shift, 1,000 surrogates, 99th percentile, peaks at least 1 s apart) and Dard 2022 (circular shift, 300 surrogates, 99th percentile, peaks at least 5 frames apart) do use the circular-shift, pooled-percentile form.

**4. SPIKE-synch (lines 177–178), the sentence crediting the measure's authors with "a detection step of the same form (Cecchini et al., 2021)"** · MEDIUM · verified: yes (paper); the personal-communication citation cannot be verified
- **Issue.** Cecchini et al. kept spikes whose SPIKE-synchronization showed coincidence with at least three quarters of the other trains. That is one threshold per spike: no binning, no hysteresis or sustain level, no maximum gap, no minimum event count. "Same form" overstates the match.
- **Fix.** Something like: "The measure's authors identified global events by thresholding each spike's SPIKE-synchronization value (Cecchini et al., 2021); the binning and hysteresis here are the laboratory's."

**5. Comparison, coded detectors (lines 300–302)** · MEDIUM · verified: yes (`_run_search` in the tuning tool)
- **Issue.** Under "F1 alone" the per-fold coded search ran with no admissibility gate at all (`admissible=None`). Under the false-alarm rule, the only gate was the 1.6×-CoactDetect budget. "The precision-change and close-events limits were not applied" implies the Table 3 elevated-rate and no-coordination limits were applied. They were not.
- **Fix.** "No Table 3 limit was applied; under the false-alarm rule the budget below replaced them."

**6. rate+context (lines 143–148)** · MEDIUM · verified: yes (`rate.py`)
- **Issue.** Three rules that decide which calls exist are missing:
  - After merging, a run that spans only one supra-threshold grid point (zero duration) is discarded. This is also why a merge gap near 0 returns no calls.
  - The comparison is `>=`, not strictly greater.
  - The 60 s context is a centred window that includes the 1 s test window, is clipped at the analysis-window edges, and is capped at 0.9 × duration.
- **Fix.** Add one sentence covering these.

**7. rate+context, "structure of cell-averaging CFAR"** · MED-LOW · verified: partly (code docstring; Finn & Johnson itself not fetched)
- **Issue.** What defines CA-CFAR is a threshold scaled to the reference estimate, with guard cells and the cell under test excluded from the reference. Here the threshold is a fixed additive offset and the reference includes the test window. `rate.py` itself says the additive mode has "no constant-false-alarm property".
- **Fix.** "Resembles the reference-averaging stage of CA-CFAR (Finn and Johnson, 1968), but with a fixed additive threshold and no guard, so it does not hold the false-alarm rate constant."

**8. Synthetic recordings versus recorded data (cell count)** · MEDIUM · verified: yes (`detections.csv`)
- **Issue.** Every setting was tuned, and every learned model trained, at 33 cells. The recordings have 9–61 cells (median 31.5, interquartile range 23–37). Several settings are absolute in cells, so they are being applied outside the range they were calibrated on:
  - rate+context's 4.5 events s⁻¹ threshold;
  - the minimum-cells floor of 3;
  - SPIKE-synch's C = 0.1, a fraction of the other cells: at least 4 of 32 at 33 cells, but 1 of 8 at 9 cells.
- Rates are also not normalised by cell count.
- **Fix.** State the range and this limitation, or check the result stratified by cell count.

**9. Analysis of recorded data (lines 339–340), surrogate seed** · LOW-MED · verified: yes
- **Issue.** "LoCo, binned SCE and locust draw their surrogates from one sequence." At its Table 4 setting (sliding mode) LoCo draws no surrogates: its null is exact, and `n_surrogates` and the seed are unused. Only binned SCE and locust use the seed.
- **Fix.** Drop LoCo from the sentence.

**10. Architectures (lines 270–279)** · LOW-MED · verified: yes (`nets/*.py`)
- **Population filter.** The difference-of-Gaussians runs on the fraction of cells active after each onset is widened by max-pooling (2·kmin+1 frames). The raw fraction also goes to the head beside the zero-integral responses (the "bypass"), so the model is not rate-invariant by construction.
- **Smoothed-fraction filter.** It passes the raw fraction to the head in the same way.
- **All four architectures** end in a dilated convolutional head; the text says so only for the cell-set network.
- **Cell-set pooling.** "Mean of the four most active cells" is actually the top 4 values across cells at each frame and channel, taken after a sigmoid.
- **Gain variant.** The gain and offset are per encoder channel and shared by all cells, not per cell. Read as per-cell, it would break the Deep Sets symmetry.
- **Fix.** Correct the three descriptions accordingly.

**11. No-coordination test (lines 127–130)** · LOW · verified: yes (`fair_bakeoff.NULL_SEED_OFFSET`, `meta.json`)
- **Issue.** "Same seeds, so same background" holds for the coordinate search (`bench.false_positives_per_hour`). In the nested cross-validation the empty recordings use seed + 100,000, so their background is independent of the matching recording.
- **Fix.** Say so.

**12. Reproducibility gaps** · LOW · verified: yes
- **Training.**
  - Batch size of 3 crops per step.
  - Learned search axes: learning rate {0.003, 0.01, 0.03}, steps {900, 1800, 3600}, plus the per-architecture axes (the `meta.json` field `learned_axes`).
  - Each crop independently has a 50% chance of being centred on a positive frame, so "half" holds only on average.
  - The threshold maximises F1 pooled over the two threshold recordings, not the mean over the two backgrounds used everywhere else.
  - The fitting recordings are a contiguous run, offset by training seed, of a pool dealt round-robin across folds, rather than a random draw.
- **SPIKE-synch.** The bin value is the "mean" of same-time C values, and a later event time in the same bin overwrites an earlier one. Missing edge inter-event intervals default to the cap.
- **CoactDetect.**
  - The guard normalisation is "compact", which raises the bar by 120/119.
  - The 1 s guard is narrower than the 2 s window.
  - The context is clipped at the analysis-window edges.

**13. SPIKE-synch hysteresis (lines 175–177)** · LOW · verified: yes (`sync.py`)
- **Issue.** Only empty bins are skipped. The scan ends at the first non-empty bin within the gap whose value is at or below the sustain level. The minimum-events check sums Cn over the bins taken, and Cn is the size of the last same-time group written to each bin, not a count of all events.
- **Fix.** Reword.

**14. Search outcome (lines 243–247)** · LOW · verified: yes (`search.json`)
- **locust.** The search proposed three changes, not one: percentile 99.999 → 99.99, synchronous frames 1 → 2, minimum distance 4 → 128. Held-out gain +0.119 (0.108–0.132), close-events test +0.149, 5.25 calls h⁻¹ against a limit of 6.
- **SPIKE-synch.** Minimum events 3 → 2 gained +0.042 (0.030–0.054) held out and +0.051 on the close-events test. No reason is given for not adopting it.
- **Fix.** List the full locust proposal and give a reason for each decision not to adopt.

**15. Held-out bootstrap (lines 237–238)** · LOW · verified: yes
- **Issue.** The resampling unit is the benchmark seed (both backgrounds kept together, paired with the default), and the gain reported is the bootstrap median. "Bootstrapped over recordings" is slightly off.
- **Fix.** "Over benchmark seeds (both backgrounds together); median and 2.5–97.5 percentiles."

**16. Width counts (lines 381–382)** · LOW · verified: yes
- **Issue.** "443 zero width, 283 single cell" are both streams combined. The fast stream alone, which is all this section covers, is 308 and 185. These counts come from the coded run only; the learned detector's calls are not included. The widths-above-10 s counts are fast-only and correct.
- **Fix.** Use the fast-stream counts and say which detectors they cover.

**17. Validation (lines 181–182), "sliding modes … checked only on the benchmark"** · LOW · verified: yes
- **Issue.** This understates the checking. `tests/test_sliding_window.py` checks the exact null against simulated shifts, the Poisson-binomial against the recursion, and that calls move with a shift of the recording.
- **Fix.** Mention these tests.

**18. PySpike (lines 183–184)** · LOW · verified: yes
- **Issue.** The claim that PySpike's cap has had no effect since 0.8.0 rests on the author's own upstream report, PySpike #89 (open, and maintainers have not responded).
- **Fix.** Cite #89.

## Checked and found correct
- **CoactDetect.**
  - The sliding null's per-cell catch probability, sum(min(w, gap))/L, is the exact probability under independent uniform circular shifts, so a Poisson-binomial count with exact mean and variance is correct.
  - z = 4.265 at α = 10⁻⁵, one-sided.
  - The tail caveat is right.
- **LoCo.** The percentile rule: calls when count > the smallest k whose CDF is at least p. The symmetric context is clamped at period boundaries.
- **Binned SCE.** Null within each analysis window, 98th percentile pooled over bins and surrogates, minimum 3 cells, no merging; scored over its bin (`extent_sec`).
- **locust.** A per-frame null, rolled over the whole recording, peaks at least the minimum distance apart. On folder input its `locs` field is the t50rise.
- **SPIKE-synch.**
  - τ is the minimum of four half inter-event intervals, capped at 0.25 s; strict "<".
  - The maximum coincidence window is introduced in Kreuz et al. 2017 §2.1.
  - The Quian Quiroga 2002, Kreuz 2015 and Satuvuori 2017 attributions are correct.
- **Generator.**
  - Gamma(0.275) mean rates.
  - Gamma(k, 1/k) multipliers per cell and per bin at 300 s and 60 s.
  - Onsets rounded to the 0.1 s grid. I confirmed this by running seed 1: events are off-grid by at most 4×10⁻¹² frames, with 87 tied timestamps.
  - Participation of 10/6/3 cells, jitter 0.36 s.
  - Spacing of 120 s plus an exponential excess, rescaled on overrun.
  - No planted event within 120 s of the block; ramp and thinning as described.
  - Distractors 6 × 6 cells between 120 and 1,100 s, same jitter.
  - The close-events test is `TAIL_RECORDING`: 10,800 s, 60 events per level, at least 6 s apart.
- **Scoring.**
  - 2.5 s tolerance to the interval, greedy closest-first matching.
  - Precision excludes calls in the block; F1 cap 15/21 gives 0.83.
  - Table 3 values match `MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PRECISION_DROP` and `MAX_CROWDED_DROP` = 0.02.
- **Coordinate search.** The 0.002 epsilon, the rescue rule, at most 3 extensions per parameter, at most 4 rounds, the context rule allowing up to 120 s, the pairs, seeds 1–48 and 49–96, 12 close-events seeds, 400 bootstrap resamples.
- **Table 4** matches `detector_settings.csv` for the full-cohort run.
- **Learned side.**
  - Binary raster sorted busiest-first; labels span first to last participant.
  - Adam, weighted BCE with pos_weight = negative/positive, 4,096-frame crops.
  - The 41-value threshold grid (0.972 is a grid value).
  - Merge gap 2 s; 23 random configurations plus the default; 3 tuning seeds and 5 refit seeds.
  - The false-alarm budget is 1.6 × Table-4 CoactDetect with a floor of one false alarm.
- **Nadeau–Bengio.** `nb_factor(4)` = √(3/7) = 0.655; t₀.₉₇₅,₃ = 3.182; the learned-refit factor ≈ 0.31 (24/10) checks out. The Bouckaert & Frank caveat is fair.
- **Width and amplitude rules** (apart from finding 1). Aperture ±1 s, or the whole call when it is longer than 2 s; 0.5 s gap split; tie-breaks; amplitude floored at one frame; NaN for a single cell.
- **References.** All reference details (journal, volume, pages, DOI) are correct, including the CICADA Zenodo DOI (publication date 2020-07-20).

## Note for the main thread (outside this artifact)
The artifact is right that the generator rounds times to the frame grid. Two repo notes say otherwise and are stale: `bench.NOT_SEARCHED["sync"]["synchrony_statistic"]` and `docs/todo/2026-09-17-the-bench-does-not-put-events-on-the-frame-grid.md` both say the generator draws continuous times. It has quantised to 0.1 s since 63ba266 (2026-08-13), and bench recordings do have exact ties. The "measured inert" reason for leaving that parameter out of the search rests on this false premise.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004). In finding 4's location, the words "personal communication" were hyphenated to keep the quotation check clear; nothing else was altered.*
