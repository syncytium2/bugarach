# ADR-0012: The bench's inputs are extracted by the detector at its untuned defaults

## Status

**Proposed**, 2026-09-28. Tony asked for it that morning, through the orchestrator (*"yes, brief a
worker"*), and the first run under it is in
[`docs/learned/runs/2026-09-28-one-function-bench/`](../learned/runs/2026-09-28-one-function-bench/README.md).

It **amends [ADR-0010](0010-tune-train-and-review-against-the-data-as-they-are.md) part 2**. It
replaces that part's measurement rule and leaves the rest of ADR-0010 standing: planted gaps are
still drawn from a real, per-stream, baseline-only distribution, replacing the 120 s minimum, and
rulings 1 and 2 (the ORX check and the doubled fast seeds) still hold. It is a replacement of one
rule, not a refinement. ADR-0010 said the spacing is *"measured without a detector … because merging
hides the short gaps"*, and this record says the opposite on purpose. When this record is accepted,
ADR-0010 gets a dated pointer note to it.

## Context

Tony is writing a document for his boss about next steps, and the bench invites a circularity
charge that is better answered before it is raised.

Until today the realistic bench took its three real-data inputs from three different rules:

- **spacing** from `tools/measure_real_intervals.py`: runs of the 2 s co-active count at or above
  each window's floor, placed at each run's peak, with peaks under 2 s apart merged;
- **participation** from moments with at least 4 ROIs co-active within 1 s (`tools/remeasure_bench.py`);
- **timing spread** from the half-width of the cross-ROI onset correlogram
  (`tools/measure_jitter_correlogram.py`).

The spacing rule is, in all but name, count (sliding). count (sliding) was then tuned and scored on
that bench and did well. Nothing on the page said the two were the same function. Tony's ruling:
**say it openly, and fix the extraction setting in advance.**

## Decision

1. **One function extracts every input.** `count_sliding_detect`, run on the real baseline windows
   only (FOUNDATIONS §9), gives the spacing, the participation and the timing spread the generator
   takes (`tools/extract_bench_inputs.py`).
2. **At one setting, fixed now, shared by every stream:** a 2 s window, the window's own ADR-0008
   floor as its minimum (`min_rois` = floor, `k_offset` 0), and a 3 s merge gap. These are the
   floor's own window and count (sliding)'s starting point, and none of them was tuned.
3. **The definitions:**
   - **Spacing:** the gap between neighbouring calls in a window, measured call start to call
     start.
   - **Participation:** each call's peak distinct-ROI count in its 2 s window, as a share of the
     window's ROIs. The middle planted level is the median of that share. The outer two levels keep
     the bench's present ratios to the middle, which were chosen rather than measured, and are
     capped at 0.95.
   - **Timing spread:** the within-call standard deviation of the participating ROIs' first onsets,
     its median over calls. It is mapped to the generator's `jitter_sec` by calibration: the same
     extractor and statistic run on bench recordings planted at known jitter, with the new spacing
     and participation in force.
4. **The same function, tuned per stream on the resulting bench, is the detector output.** The
   floor stays out of the search (`bench.NOT_SEARCHED`, `bench.floored_params` unchanged).
5. **The defence is a sensitivity check, and it is reported with every rebuild.** The spacing is
   rebuilt with CoactDetect at its shipped settings as the extractor instead. count (sliding) is
   scored there at its chosen settings and retuned there, and the report says how far the settings
   and F1 move.

## Consequences

- **The extraction setting cannot be tuned later without a new ADR.** Tuning it on the bench it
  builds would be the circularity this record exists to rule out. `EXTRACTION` in
  `tools/extract_bench_inputs.py` says so beside the values.
- **The bench is built from the detector's view of the data, and says so.** The first run's inputs
  differ from the old rules in three ways:
  - **No gap under the 3 s merge survives**, so none is planted. The share of gaps under 10 s fell
    from 16% to 9% on fast, and less on slow and combined.
  - **Participation is higher by construction**, because a call has to reach the floor: 0.20 → 0.31
    on fast, 0.38 → 0.62 on slow and 0.25 → 0.63 on combined. The high level is capped at 0.95 on
    slow and combined.
  - **The calibrated jitter is 2 to 3 times the correlogram's**: 0.105 → 0.332 s on fast,
    0.131 → 0.320 s on slow and 0.150 → 0.364 s on combined. Which instrument reads real events
    better is not settled.
- **The first run's answer** (fresh-seed F1, run record linked above):
  - On slow and combined, count (sliding) and retuned CoactDetect score the same: 0.847 against
    0.847, and 0.969 against 0.968.
  - On fast, count (sliding) scores 0.970 against CoactDetect's 0.764. That gap is a budget, not a
    detector. Every CoactDetect setting that scored better in its search broke the precision-swing
    limit of 0.10, and its shipped point breaks it too on fresh seeds (0.138). The limit was set on
    the old bench, and whether it holds on this one is open.
- **The sensitivity check did not move the answer materially.** At the chosen settings, F1 moved by
  0.011 on fast, 0.003 on slow and 0.021 on combined with CoactDetect building the spacing.
  Retuning there made these changes, and the retuned F1 stayed within 0.03 of the F1 at the
  setting chosen on count's own bench:
  - fast: kept its setting;
  - slow: the merge gap went from 3 to 8 s;
  - combined: k went from 0 to 1 and the merge gap from 2 to 3 s.
- **The sensitivity check varies the spacing only.** Participation and jitter come from count
  (sliding) in both arms, so the check does not test them. A second extractor for those would be a
  new decision.
- **`bench.INPUTS_ENV` (`BUGARACH_BENCH_INPUTS`)** points the bench at an inputs folder. Unset, the
  bench is byte-identical to before. Which folder is the default bench is a separate step: this
  record is Proposed, so nothing is switched over yet.
- **What would supersede this:** a decision to tune the extraction setting, to take participation or
  jitter from a different instrument, or to measure spacing without a detector again.
