# ADR-0013: The bench simulates treatment periods, with the treatment's event rates as background and baseline's coordination planted through them

## Status

Proposed, 2026-09-28, drafted at Tony's request (*"draft the ADR for treatment simulations"*). Not
accepted: the open points at the end are his. It amends [ADR-0010](0010-tune-train-and-review-against-the-data-as-they-are.md)
(what the bench is built from) and asks for one clarifying sentence in FOUNDATIONS §9. It feeds the
rethink of [ADR-0008](0008-the-event-floor-is-set-per-window-from-its-own-null.md)'s floor, and it
changes nothing that ships until a later decision uses it.

## Context

**Every bench recording has imitated baseline, so every choice was scored on steady event rates.**
The realistic bench (ADR-0010) copies baseline intervals, participation, jitter and background
rates. The one departure is the elevated-rate test (ADR-0009): a 5-minute stretch at the
background's 99th percentile, in a recording of its own, with nothing planted. No bench recording
has ever had a treatment's event rate rising over time, with coordinated events to find inside it.

**On 2026-09-28 the real treatment windows showed that this was a blind spot, not a detail.**
Sliding simple (`count_sliding`, 2 s window, floor, 3 s merge gap) was drawn under both of
ADR-0008's floors on every senktide and TTX recording (darkroom `2026-09-28-senktide-rasters/`):

- **Under the window's own floor, OVX and ORX lose coordinated events.** Senktide raises the event
  rate per ROI about 4 to 15 times in those groups, and the own floor rises by about 20 ROIs on
  fast and combined, which is 55 to 67% of a recording's ROIs. In 20250911_222 (ORX, combined) the
  clear stripes after the drug takes effect get almost no calls.
- **Under the baseline floor carried over, the same windows are called wall to wall.** OVX fast
  goes from 1.2 calls per hour at baseline to 80 under senktide, and to about 300 with a shorter
  merge gap. A surge in which every cell is busy is called as coordination, which ADR-0006 says
  it is not.
- **In 20240814a47 (OVX, 17 ROIs) no call is possible.** Its own floor is 18. The event rate is
  ordinary (297 events per ROI per hour against the group's 351), but the co-active count stays
  at 10 or more of 17 ROIs for 82 to 90 s after the drug arrives. A ±20 s rigid shift cannot
  break an 80-second shared stretch, so the shuffles reach all 17 ROIs (`a47-floor/`).

Tony, on seeing it: *"we would have caught this right away if we tried."* One simulated senktide
recording would have shown both failures before any floor was adopted.

**FOUNDATIONS §9 constrains how.** *"Calibrate from baseline recordings only … do not use senk or
ttx as sources for the properties of coordination."* The reason is that taking coordination
properties from treatment windows assumes the answer the treatment question asks. That reason
does not reach the background: how often each cell has a calcium event, and how that rate
changes over a treatment period, is the noise a detector must see coordination through. It is
not a property of coordination.

## Decision

1. **The bench gains treatment recordings.** Each one is a baseline segment, a 2-minute wash-in
   segment at baseline rates (the delay before the drug reaches the slice), and a treatment
   segment. They are built for senktide and for TTX, on the fast, slow and combined streams.
2. **The treatment segment's background is measured from the real treatment windows**:
   - each ROI's event rate over time, by group (DI, OVX, MALE, ORX), treatment and stream;
   - the surge after the drug takes effect, and the steady state that follows;
   - the spread across ROIs, including ROIs that are active nearly all the time.

   The generator already has the pieces nearest to this: the spread of rates across ROIs
   (`bg_rate_shape`), unevenness over time (`bg_burst_shape`), and one raised stretch with a ramp
   (`hot_window`, `ramp_sec`). A measured rate course over time is new: an extension to
   `simulate.py`, not a new generator.
3. **Coordination is centred on baseline and swept, never assumed unchanged.** Senktide and TTX
   may change any property of coordinated events. Tony, 2026-09-28: *"we know intervals decrease
   in senktide"*, and *"both senktide and ttx could alter these coordinated event properties"*.
   So in the treatment segment each property is planted at baseline's measured value **and** at
   levels around it:

   | Property | Levels in the treatment segment (multiples of baseline, dimensionless) |
   |---|---|
   | Intervals | 1×, 0.5×, 0.25× |
   | Participation (share of ROIs) | 0.5×, 1×, 1.5× |
   | Jitter (onset spread, s) | 1×, 2×, 4× |

   Each property is swept with the other two held at 1×, plus the two hardest corners: short
   intervals with low participation, and short intervals with wide jitter. That makes 9 conditions
   per treatment, group and stream, not 27. Planting baseline values alone would test the easiest
   regime, where close coordinated events are rare and merging costs nothing.

   The levels are **difficulty axes, not measurements**. No property is taken from a treatment
   window, so FOUNDATIONS §9's reason holds, and the detector has to work wherever on each axis
   the truth lies. The range is set by what the detector must survive (open point 6).

   **Whether the treatments really change participation, jitter or intervals is an analysis
   result, not a bench input.** It is measured on the real recordings with the detector this bench
   validates, compared per group between baseline and treatment, and only read where the bench
   shows the detector recovers that property at that level.
4. **Every treatment recording has a null twin**: the same background with nothing planted, where
   every call is a false alarm.
5. **Scores are reported by segment and by group, never pooled into one number:**
   - baseline, surge and steady treatment;
   - recall, precision, and false calls per hour on the null twin;
   - a window where the floor is at or above the ROI count, counted as **"unmeasurable"**, not as
     zero calls.
6. **No floor or call rule is adopted without being scored here.** The candidates from the
   2026-09-28 rethink go through it first:
   - the own floor and the baseline floor;
   - a floor per fixed time block;
   - a floor from each ROI's local event rate;
   - CoactDetect's local null without the floor minimum.

## Consequences

- **The failure found on 2026-09-28 becomes a test.** A floor that deafens a window after its
  surge, or calls the surge itself, fails on the bench where it can be measured, not on a real
  page where it has to be noticed by eye.
- **FOUNDATIONS §9 needs one sentence**, which is Tony's to write, since FOUNDATIONS is canonical:
  treatment windows may supply the background event rates a simulation runs at; coordination
  properties still come from baseline only. This ADR does not edit FOUNDATIONS.
- **ADR-0009's elevated-rate test becomes a special case.** It was a crude stand-in for a
  treatment background and it stays as it is; the treatment recordings are the realistic version.
- **ADR-0010's inputs are unchanged for baseline.** It gains a second recording type, not a
  replacement.
- **The bench can still only test what it plants.** Whether the surge itself is coordination is a
  question about the preparation, and this bench cannot answer it (open point 1).
- **Compute and code:** a rate-course measurement tool; a rate-course input to the generator;
  per-group rate courses for each treatment;
  recordings and null twins for each treatment, group and stream; and scoring by segment. It is
  small against a tuning night, because nothing is searched until a floor is chosen.

- **The merge rule is tested where it matters.** At 0.25× the fast intervals, pairs of
  coordinated events closer than the 3 s merge gap plus the 2 s window are common, which is the
  failure Tony found on the DI combined senktide page.

## Open points for Tony

1. **Is the surge coordination?** ADR-0006 counts a shared rise in event rate as chance, so the
   bench plants nothing extra in it and scores a call there as a false alarm. If the surge is
   coordinated recruitment, the definition changes, not only the bench.
2. **Removing coordination from the measured rates.** The treatment rates include the onsets of
   real coordinated events. Proposed default: measure each ROI's rate from onsets outside any call
   by a permissive rule (the floor with no merge), and record the share removed. A pre-agreed
   alternative is to accept the small over-count at baseline-like rates and correct only the surge.
3. **Where the surge ends.** Proposed default: the segment boundary is where the population rate
   falls back to within 20% of its post-surge median, measured per recording and reported as a
   distribution. The alternative is a fixed length per treatment.
4. **Rate courses per group, or pooled?** Proposed default: per group, since OVX and ORX surge far
   more than DI and MALE, and pooling would hide exactly the failure this ADR exists to catch.
5. **High K⁺.** The last period of some recordings (e.g. 20250912_225) has its own surge.
   Proposed default: out of scope for now, since it is a positive control, not a treatment the
   analysis compares.
6. **How far each axis goes.** Proposed defaults, as multiples of baseline:
   - intervals 1× to 0.25× (fast median 41 s becomes 21 s and 10 s);
   - participation 0.5× to 1.5× (fast 0.20 of ROIs becomes 0.10 and 0.30);
   - jitter 1× to 4× (fast 0.105 s becomes 0.21 s and 0.42 s).

   If Tony's knowledge of either treatment says a property moves further, that axis extends to
   cover it. The range is set by what the detector must survive, not fitted to treatment windows.
7. **The recovery bench for the analysis.** Beyond detection, the bench should report how well
   each property is recovered from the calls: the participation and jitter measured on called
   events against what was planted, at each level. Without that, a real baseline-vs-treatment
   difference in participation or jitter cannot be told apart from a measurement that shifts
   with the background rate. Proposed: yes, in the same run.

## References

- Darkroom `bugarach/2026-09-28-senktide-rasters/`: the four-lane pages under both floors, the
  calls-per-hour table (`merge-options/`), and the a47 floor check (`a47-floor/`).
- Darkroom `bugarach/2026-09-28-floor-sensitivity/` and PR #853: the floor's sensitivity to its
  settings on baseline and treatment windows.
- [ADR-0006](0006-a-false-alarm-is-coincidence-the-event-rates-explain.md) (what counts as
  chance), [ADR-0008](0008-the-event-floor-is-set-per-window-from-its-own-null.md) (the floor),
  [ADR-0009](0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md) (the
  elevated-rate test), [ADR-0010](0010-tune-train-and-review-against-the-data-as-they-are.md) (the
  realistic bench).
- ADR-0012 (Proposed, PR #848): the bench's inputs extracted by the detector. It is independent of
  this ADR, and the two can be accepted in either order.
