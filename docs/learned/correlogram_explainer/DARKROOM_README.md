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
| `2026-09-22-jitter-correlogram.png` | the pooled measurement: real peaks against the simulator's, both streams | `docs/learned/runs/2026-09-22-jitter-correlogram/` |
| `2026-09-22-explainer-figure1-building-the-correlogram.png` | the correlogram built in four steps on a toy recording, for a reader who is not math-oriented | `docs/learned/correlogram_explainer/` |
| `2026-09-22-explainer-figure2-what-the-width-means.png` | how the peak's width becomes a timing spread, and the real recordings | `docs/learned/correlogram_explainer/` |
| `2026-09-22-explain-jitter.png` | why the earlier bin-bound jitter figure was circular | `docs/learned/runs/2026-09-22-jitter-correlogram/` |
| `2026-09-21-slow-bench-jitter-vs-bin.png` | the measurement this replaced: within-cluster spread tracking bin ÷ √12 | `tools/measure_slow_bench.py` |

**The findings, in one line each.** Pooled, both streams are about three times tighter than the
jitter their benches plant (fast 0.106 s against a 0.36 s bench, slow 0.135 s against 0.30 s). Split
by group, the fast stream shows no difference between groups at all (p = 0.71), and the slow stream
shows one that does not clear its own test (p = 0.054, under a null biased toward significance).
