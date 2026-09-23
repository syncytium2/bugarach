# The every-knob search on the ADOPTED slow bench

**Run 2026-09-23, 03:18–03:29 on WSMIP065**, 10.9 minutes, 12 workers.
`tools/search_all_settings.py --bench slow --sliding`, on `main` at `534f24c`, which **contains
`2c19003`** — the adoption (#756). Slow probe **0.0291 Hz**, quiet background **0.0024 Hz**, read
out of the running module before launching.

The integer-floor fix (#755) is in force.

**This changes nothing.** `bench_slow.OPERATING_POINTS` is not edited.

Abbreviations: **F1**, the harmonic mean of recall and precision.

## Held out, against the settings in force

| detector | shipped | pick | gain [95%] |
|---|---|---|---|
| **CoactDetect** | **0.859** | — | nothing in its grid beat it |
| **LoCo** | **0.845** | — | nothing beat it |
| **SPIKE-synch** | **0.845** | — | nothing beat it |
| locust | 0.757 | 0.843 | +0.085 [+0.075, +0.095] |
| rate+context | 0.843 | 0.848 | +0.005 [+0.003, +0.008] |
| binned SCE | 0.803 | 0.827 | +0.024 [+0.017, +0.032] ⚠ unusable, see below |

**Four of six came back unimproved**, against two on fast and none on combined. The slow settings
are the most recently and most deliberately chosen of the three — Tony adopted LoCo, CoactDetect
and SPIKE-synch on this bench himself on 2026-09-21 — and the search cannot beat any of the three
he picked. That is the most useful line in this record: **the slow reference holds under a full
every-knob search on the re-anchored bench.**

**SPIKE-synch in particular.** Its `max_gap` 4 s was Tony's cautious choice over the search's own
8 s pick at the time. On the adopted bench the search now finds nothing better than 4 s at all.

## ⚠ binned SCE's pick contains a NaN and cannot be used

The pair-grid stage proposes `merge_gap_sec` = **NaN**. The declared grid for that setting is
(0.0, 5.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0) — no NaN in it — so the value was produced by the
search, not chosen from the space.

Two consequences, and the second is the one that travels:

1. The +0.024 gain is attached to a setting nothing can run. It is not a proposal.
2. **`search.json` is not strict JSON.** The file contains a literal `NaN` token. Python's `json`
   accepts it; most other readers reject it outright. Any tool that reads a run record with a
   stricter parser will fail on this file, and the failure will look like a corrupt record rather
   than a bad value.

Filed rather than fixed here, because the fix belongs in the search and this run is measure-only.

## The other picks

**locust +0.085** is the largest gain on either bench today: `sce_min_distance_frames` **128**
(12.8 s) again — the same climb the fast, slow and combined searches have all now produced, which
the slow handoff tied to the unsettled anchor question and called *"not a setting to ship until
the anchor is settled."* Three benches agreeing does not settle it; it is the same unanswered
question three times.

**rate+context +0.005** is real but small: merge gap 5 s, additive threshold mode.

## A caution about this record's own `null_per_hour` column

**Do not read it as a budget verdict.** On this run it flagged locust's pick as over its null
budget. Measured properly over 24 seeds it is **0.39 calls/hour against a budget of 1.0**, and
the shipped setting is 0.33 — no violation, and barely a difference.

The same column produced two false flags on the fast run. It is computed on few seeds, and it is
noisy enough to invent violations that a proper measurement refutes. Both runs cost a correction
before anything was written down.
