# `<darkroom>/bugarach/correlogram/` — what is in the folder

This is the copy that ships to the darkroom as that folder's `README.md`; the repo keeps it here so
the folder's contents stay reviewable in git. Gathered 2026-09-22 on Tony's instruction, *"move the
figures into darkroom bugarach correlogram folder"* — before that, these figures were loose PNGs at
the root of `bugarach/`.

Everything here measures the same thing: the **cross-ROI onset correlogram**, which counts onset
pairs between two different ROIs at each lag and divides by the count expected if the two fired
independently. ROI = region of interest, one imaged cell. It defines no event and groups no onsets,
which is the point of it.

| file | what it shows | where it comes from |
|---|---|---|
| `jitter_by_group.png` | **Figure 1**, the peak width per `group_id` on both streams, with the permutation test of whether the widths differ at all | `docs/learned/runs/2026-09-22-jitter-by-group/` |
| `raw_correlograms.png` | **Figure 2**, the same curves as measured — nothing subtracted, nothing normalised, so the peak heights and the slow stream's dip below chance are visible | the same run |
| `one_recording_leverage.png` | **Figure 3**, each group's width with and without the single recording that moves it most | the same run |
| `2026-09-22-jitter-correlogram.png` | the pooled measurement: real peaks against the simulator's, both streams | `docs/learned/runs/2026-09-22-jitter-correlogram/` |
| `2026-09-22-explainer-figure1-building-the-correlogram.png` | the correlogram built in four steps on a toy recording, for a reader who is not math-oriented | `docs/learned/correlogram_explainer/` |
| `2026-09-22-explainer-figure2-what-the-width-means.png` | how the peak's width becomes a timing spread, and the real recordings | `docs/learned/correlogram_explainer/` |
| `2026-09-22-explain-jitter.png` | why the earlier bin-bound jitter figure was circular | `docs/learned/runs/2026-09-22-jitter-correlogram/` |
| `2026-09-21-slow-bench-jitter-vs-bin.png` | the measurement this replaced: within-cluster spread tracking bin ÷ √12 | `tools/measure_slow_bench.py` |

**The findings, in one line each.** Pooled, the measured jitter is **0.103 s fast and 0.132 s
slow** — three times tighter than the benches planted when this was first measured, which is why
both benches then adopted these values (`8137da71`), so the comparison is no longer one to quote.
Split by group, **neither stream has a width difference**: fast p = 0.71, and slow's p = 0.054
collapses to 0.48 when one ORX recording is removed (Figure 3), which is what Figure 2's raw curves
exposed and Figure 1's normalised ones had hidden.
