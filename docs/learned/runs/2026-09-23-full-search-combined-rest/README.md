# The every-knob search on the COMBINED bench: the other five detectors

**Run 2026-09-22 evening on WSMIP065**, 29.8 minutes, 10 workers.
`tools/search_all_settings.py --bench combined --sliding --only loco sce rate sync cicada`.
CoactDetect ran first and separately, at Tony's priority: `2026-09-23-full-search-combined-coact`.

**This changes no shipped setting.** Picks are written into `bench_combined.OPERATING_POINTS`
with a source string saying they await Tony's review; `bench.OPERATING_POINTS` and `bench_slow`
are untouched.

Abbreviations: **F1**, the harmonic mean of recall and precision; **ROI**, region of interest.

## All six, held out

Held-out mean F1 against the fast settings each search started from, on seeds nothing was chosen
on. Intervals are 95% bootstrap.

| detector | shipped | pick | gain | installed? |
|---|---|---|---|---|
| LoCo | 0.732 | **0.807** | +0.074 [+0.067, +0.083] | yes |
| **SPIKE-synch** | 0.666 | **0.797** | **+0.131** [+0.120, +0.142] | **no — see below** |
| CoactDetect | 0.718 | **0.781** | +0.063 [+0.054, +0.073] | yes |
| locust | 0.602 | **0.653** | +0.051 [+0.040, +0.061] | yes, flagged |
| rate+context | 0.673 | **0.690** | +0.017 [+0.012, +0.022] | yes |
| binned SCE | 0.571 | — | nothing beat the start | unchanged |

## ⚠ The largest gain is the one we did not install

**SPIKE-synch gains +0.131, more than any other detector, and its pick is not usable as it
stands.** Two of its values:

**`min_n` 0.25.** It is an integer floor, and the search's `extend` does not know that — it
reaches sub-integer values by halving. This is the defect already filed from the slow search,
which hit it on `sce.min_rois`, `loco.min_rois` and this same `sync.min_n`
(`docs/handoffs/2026-09-21-slow-bench.md`, item 4: *"None of those values was chosen"*). A floor
of a quarter of an event is not a floor, and installing it would put that quarter into a settings
file that runs on real recordings.

**`dt` 0.00625 s.** This one is legitimate to search — `dt` in `sync.py` is a detection
resolution, not the acquisition interval, and that module says so in terms. But it also records
that `C_threshold`, `C_min`, `max_gap` and `min_n` were **all measured against a particular bin
width**, so moving `dt` by a factor of 16 moves the ground the other four stand on. The pick
moves `dt` *and* three of those four together, so the +0.131 cannot be attributed.

The pick is kept in the module as `SYNC_SEARCH_PICK` so the number is not lost. The shipped fast
setting stays in force until the integer-floor defect is fixed and the search rerun. **Fixing
that defect is probably the highest-value small job on this bench**, because it is sitting on the
biggest measured gain of the six.

## Other flags

**locust's `sce_min_distance_frames` 128** (12.8 s) is the same climb the fast and slow searches
both saw, which the slow handoff tied to the unsettled anchor question — *"not a setting to ship
until the anchor is settled."* Installed here because nothing on this bench ships, but it carries
that flag.

**LoCo's `context_win_sec` went to 120 s, the null rule's cap**, as CoactDetect's did. Two of six
stopped at the rule rather than at an optimum.

**The starting point broke a budget for LoCo as well as CoactDetect** — round 1 moved LoCo's
threshold for that reason. Two of six, which is what makes it a property of the bench rather than
a quirk of one detector: the fast settings are not a neutral origin on combined.

**binned SCE did not move at all.** Nothing in its grid beat the fast point. On a bench where
every other detector gained between 0.017 and 0.131, that is worth a second look rather than a
shrug — either its grid is in the wrong place for this stream, or its 10 s bin is already the
right answer for a stream carrying both timescales.

Figure 1, the search's own summary, is `full_search.png` here and in
`<darkroom>/bugarach/2026-09-23-full-search-combined-rest/`.
