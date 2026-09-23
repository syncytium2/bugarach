# The every-knob search on the COMBINED bench: CoactDetect

**Run 2026-09-22 evening on WSMIP065**, 10.6 minutes, 10 workers.
`tools/search_all_settings.py --bench combined --sliding --only coact`, on the combined bench as
measured that night (`src/bugarach/bench_combined.py`, PROVISIONAL cleared the same evening).

Tony, 2026-09-22: the combined stream is a third output beside fast and slow, and CoactDetect is
the priority. **This changes no shipped setting.** The pick is written into
`bench_combined.OPERATING_POINTS` with a source string that says it awaits his review;
`bench.OPERATING_POINTS` and `bench_slow` are untouched.

Abbreviations: **F1**, the harmonic mean of recall and precision; **ROI**, region of interest
(one imaged cell).

## What it found

| | alpha | context (s) | `min_rois` | merge gap (s) | guard (s) |
|---|---|---|---|---|---|
| shipped (the fast settings) | 1e-4 | 60 | 3 | 3 | 0 |
| **search pick** | **1e-5** | **120** | **4** | **8** | **8** |

| | held-out mean F1 | null calls/hour | crowded mean F1 |
|---|---|---|---|
| shipped | 0.718 | 12.9 | 0.880 |
| **search pick** | **0.781** | **3.5** | 0.861 |

**Gain +0.063 F1 [+0.054, +0.073]** on held-out recordings — seeds nothing was chosen on, with a
95% bootstrap interval that does not span zero. Null calls fall by a factor of 3.7.

## Three things the gain does not show

**1. `min_rois` 4 sits just under the smallest planted level.** Combined participation is
(0.40, 0.24, 0.13) of 32 ROIs — about 13, 8 and 4 participants. A floor of 4 is at the bottom
rung, which is the warning `min_rois` always carries in this project: it can learn the
simulation's planted participation rather than anything about tissue. The gain would look the
same either way, so the number cannot distinguish them.

**2. `context_win_sec` 120 s is the null rule's cap, not an interior optimum.** It went to the
edge and stopped because the rule stops it — the same shape LoCo's context showed on the slow
bench, where that handoff recorded it as giving no evidence either way about what the stream
wants.

**3. It is 0.018 worse on the crowded recordings** (0.861 against 0.880). That is inside the 0.02
allowance the search enforces, but on the wrong side of it, and the allowance itself is the
unsigned constant WSMIP064 spent a sweep measuring.

## One thing worth more than the pick

**The starting point broke a budget.** Round 1's first move was alpha, and the log records the
reason as *"the starting point breaks a budget"* — the fast settings, carried over as the search's
origin the way slow's search carried them, are not a neutral default on this bench. Any comparison
that treats "the fast settings on combined" as a baseline is comparing against something the
combined bench already refuses.

## Where the rest is

The other five detectors are searched in a second run,
`2026-09-23-full-search-combined-rest`. Figure 1, the search's own summary, is `full_search.png`
here and in `<darkroom>/bugarach/2026-09-22-full-search-combined/`.

⚠ That darkroom folder was **written before it was claimed**: `search_all_settings.py` defaults
`--out` to the darkroom and names its own dated folder, so running it without `--out` landed
outside the claim on `docs/SESSIONS.md`. Recorded there as soon as it was noticed, and the second
run was given an explicit `--out` inside the claim.
