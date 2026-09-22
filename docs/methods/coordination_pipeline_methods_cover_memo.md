# Cover memo: the coordination-pipeline methods section

**For Tony, 2026-09-22.** This goes with `coordination_pipeline_methods.docx`. It holds what three
rounds of review found that is not manuscript text:
- code defects that stop results;
- design choices a referee will attack;
- decisions that are yours;
- why the section order is not your list's.

The run record is `docs/reviews/coordination_pipeline_methods_2026-09-22.md`.

## 0. A question for the producer today

**Pinning is not closed for three analyzed recordings** — `20250926_237`, `20260629_314` and
`20260630_325`. All three are among the 67 analyzed recordings, all three are diestrus females,
and each is the other recording of a mouse that already has a pinned one. A whole-frame scan
ranks all three beside the four known pinned recordings.

**Corrected 2026-09-22.** This section said `20260629_314` had never been run through the
pinning detector, taking that from the export's own note. It is false, and the producer withdrew
it the day they wrote it — their answer of 2026-09-18 carries a same-day correction
(`<darkroom>/bugarach/2026-09-18-pinned-rois-answer/README.md`). All 85 archive slices went
through the per-ROI trace-derivative detector: `20260630_325` came back marginal and is in the
census, and `20250926_237` and `20260629_314` came back with no ROI flagged. The note in
`current_export.toml` has now been corrected too, which is where this section and the round-3
review both read it from.

**What is actually open is sensitivity, not coverage.** The census tests manually selected hROIs
only, so a flooded patch holding no hROI leaves it silent; `20260629_314` is the most exposed case
at 14 ROIs, the fewest of any DI slice. The producer reads the residual as cutting in our favour,
because a whole-frame artifact where no ROI sits cannot reach the event table. The test that would
settle it is geometric — pinned pixels against ROI masks — and that has not been run on these
three. **That is the ask, and it is narrow.**

## 1. Stop before reporting results: five code defects

Each makes a number the methods describe differ from what the code produces. The methods state
the intended rule. Results for the detectors named should not be reported until each defect is
fixed and the affected outputs are regenerated. All were confirmed independently by two or more
reviewers.

| # | defect | affects | fix |
|---|---|---|---|
| 1 | **LoCo and locust rates count calls from outside the window.** Both run on the whole recording and tag each call with its raw *period*. `make_before_after_figure` then divides by the *analysis window's* duration. In the fast stream this puts 212 of 1,810 LoCo calls and 234 of 6,546 locust calls in the numerator although their onsets fall outside the window. The detectors already compute `in_stats_window`, but `emit` drops it. | before/after rates for LoCo and locust | carry `in_stats_window` into `detections.csv`, or filter on it in `detect_folder._run_nested`; regenerate |
| 2 | **binned SCE's width and amplitude are measured over the wrong interval.** `measure_calls` uses onset to onset + width. For binned SCE that is the bin start plus the *spread of its events*, not the bin. 157 of 1,665 fast SCE calls find no events, and searching the whole bin would change the core group of 456 of them (27%). `score.py` already takes the bin from `extent_sec`, which `emit` does not export. | binned SCE width and amplitude | export `extent_sec`, build the search span from it (one `call_span()` shared with the scorer), re-measure |
| 3 | **`measure_calls` overwrites the detector's `n_roi` column** with its own search-span count, although its docstring says every detections column is kept. In the fast stream, 265 binned SCE rows now show fewer than 3 cells. | anyone reading `calls_measured.csv` | rename the measured field (e.g. `span_n_roi`); add a test that the detections columns survive |
| 4 | **locust's threshold spans drug periods.** `threshold_scope="global"` pools baseline, treatments, high-K⁺ and the exchange intervals into one null. A treatment that raises the rate both sets the bar and clears it more easily. | locust before/after rates | run `threshold_scope="regional"` (it exists), or drop locust from treatment contrasts |
| 5 | **Table 3's CoactDetect and LoCo settings are not the stored defaults.** `bench.OPERATING_POINTS` still holds the binned points. The run used a settings file, now committed as `docs/methods/recorded_data_detector_settings.csv`. | reproducibility of CoactDetect and LoCo results | land the sliding switch in `OPERATING_POINTS`, or cite the file in every run record |

Minor: 14 rate+context calls count toward a window although their onset, after the 0.5 s widening,
falls up to 0.5 s before it.

## 2. Design choices a referee will attack (the methods now disclose each)

- **Distractors.**
  - They are identical to planted 18% events and are scored as false alarms, so F1 is capped at
    0.83 and detecting 6-cell events is barely rewarded.
  - They are not spaced from planted events. 572 of 576 fall within 120 s of one, which brings
    back the contaminated null the 120 s spacing exists to prevent. 17 fall within 2.5 s, where a
    call on the distractor scores as a hit.
  - Fix: give distractors a property a detector could reject, and the same spacing rule.
- **The elevated-rate test counts calls.** A longer merge gap turns many firings into one call, so
  the count falls while the time called rises. Measured on rate+context at merge gap 3 → 8 s:
  calls 1.75 → 1.50 min⁻¹, block time covered 5.3% → 8.5%. The adopted CoactDetect and LoCo
  settings are not affected. Fix: limit the fraction of block time called as well.
- **No benchmark puts planted events on a treatment-rate background, and everything was tuned at 33
  cells.** The recordings have 9–61 cells. Sensitivity at treatment rates is unmeasured.
- **No statistics plan and no time control.** Baseline always precedes treatment. The 5 untreated
  recordings could give a time-matched control. How recordings from one mouse are handled (67
  recordings from 36 mice) is not described.
- **The close-events limit was reported, not applied, in the comparison.** It would have failed 19
  of 48 coded choices, and 16 of 48 in the replication. The adopted sliding settings lose 0.040 and
  0.042 F1 against their own sliding starting points; they pass only because the reference is the
  binned default. The held-out gains are also measured against a sliding starting point that was
  itself inadmissible.
- **Selective adoption.** The rejected proposals had held-out gains as large as or larger than the
  adopted ones: SPIKE-synch +0.042, locust +0.119. A reason is on record only for locust.
- **Amplitude is mostly 1/width.** In the fast calls, log amplitude and log width correlate at
  r = −0.61. Zero-width groups take their amplitude from the 0.1 s floor, so a 3-cell group in one
  frame (30 cells s⁻¹) outranks a 30-cell group over 2 s (15). The rule chains at senktide rates
  (a 64.8 s group) and has never been checked against planted events.
- **The benchmark constants were set from earlier data and re-checked by the same cluster method.**
  That method cannot see events under 4 cells.
- **Separability applies √(3/7) to every contrast**, including learned refits whose training set is
  smaller than the test set. It is disclosed as a descriptive bar.
- **The learned detector on recorded data is one refit, chosen by judgement, run at 2 s** (the
  re-selection chose 8 s).
- **Judgement constants:** the 2.5 s tolerance (1.5 s until 2026-08-28), the admissibility margins,
  the 1.6× factor, and the width rule's 1 s span and 0.5 s gap.

## 3. Decisions that are yours

- **Participation 0.18 → 0.19** (your todo for after today's meeting). At 33 cells both give 6
  cells, so the planted events do not change. Figure 1's tool reads the levels from
  `BENCH_RECORDING`.
- **The 12-minute first-treatment floor** is recorded in `docs/conditioned_run.md`.
- **"Amplitude" = cells ÷ width.** That is your definition, and it is kept. Reviewers in all three
  rounds asked for another name ("recruitment rate"), and round 3 found that it largely duplicates
  width (above).
- **Citations for CoactDetect and LoCo.** The repo README asks publications to cite unitary-event
  and jitter-resampling work (Grün et al., 2002; Amarasingham et al., 2012) for these two. Nobody
  here has read those papers, so they are not cited. Someone has to read them first.
- **The Kreuz personal communication has been dropped.** The published record (Kreuz et al., 2017;
  Cecchini et al., 2021) carries the claim, so no permission to cite him is needed.
- **Code names.** The manuscript no longer prints them. Population filter = `tube`,
  smoothed-fraction filter = `line_length`, cell-set network = `chorus_norm`, and with channel
  gain = `chorus_gain_norm`.
- **Width counts** were moved out of the methods and belong in Results. For the coded fast calls
  over all periods: 308 zero-width, 185 single-cell and 157 with an empty search span. These
  include binned SCE, whose measurement is wrong (defect 2).

## 4. Questions for the producer and for correspondents

- **Pinning** (section 0).
- **Versions.** Which MATLAB release produced the `findpeaks` widths? Which PySpike and cSPIKE
  versions did the parity checks use?
- **CICADA.** Nobody has asked its authors (Dard, Picardo, Cossart) how they want the software
  cited, or which version interface2 ported.
- **Sources.** Mao et al. (2001) and Finn (1967) are not on the shelf, so two lineage traces stop
  one step short.

## 5. Why the section order differs from your list

Your list runs: data, synthetic data, optimization, training, benchmark, scoring parameters, knobs,
real data, width and amplitude. The section follows dependency instead:
1. data;
2. synthetic recordings (the benchmark and its derivation);
3. coded detectors (the knobs, Table 3);
4. scoring;
5. optimization;
6. learned detectors (training, with their knobs);
7. comparison;
8. recorded data;
9. width and amplitude;
10. limitations.

Optimization cannot be stated before its objective, its limits and the parameters it moves. Every
item on your list is answered except one part of "how the real data are assessed": the
statistics, which the section says are out of scope.

"The benchmark" is read as the synthetic benchmark recording and its derivation. Please confirm
that reading. The coded-versus-learned comparison is added because the learned detector used on
recorded data came from it.

## 6. Stale notes found in passing (not fixed here)

- **`docs/GLOSSARY.md`:**
  - "guard" says no operating point sets a guard;
  - "merge gap" says binned SCE merges;
  - "no-coordination test" says one per seed at each background;
  - "admissible" has the goal-2 sense only;
  - "onset field" says `locs` is the peak, but on an export folder it holds t50rise.
- **`src/bugarach/detectors/coact.py`:** the docstring says sliding mode takes no guard, but the
  code applies one.
- **`bench.py`:**
  - the `BENCH_RECORDING` docstring gives the planted spacing a CV of about 0.8, where the measured
    CV is about 0.1;
  - `NOT_SEARCHED["sync"]` says the generator draws continuous times, but it rounds them to 0.1 s.
- **`tools/search_all_settings.py`:** the docstring says minimum cells and merge gaps are not
  searched, but the search log shows both were.
- **`docs/sapper_feedback/2026-08-12-sap-id-namespace-collides-with-interface2.md`:** says PySpike
  pull request 89 is fixed; it is open.
- **The darkroom `lit/DL/README.md`:** gives Deep Sets' second author as Kumar; it is Kottur.
