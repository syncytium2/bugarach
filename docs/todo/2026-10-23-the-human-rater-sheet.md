---
status: open
filed: 2026-10-23
---

# The human rater sheet: can synthetic data stand in for people's marks?

**Tony, 2026-10-22:** *"can synthetic data be used to train/optimize detectors versus human
marked events. Imagine a one page test sheet for humans. They pick coordinated events in each
row and whether or not the row is synthetic or real. That way if synthetic fails we fall back on
human detected events. Bonus psychophysics data possible."* On 2026-10-23 he chose a hosted
survey for control, and U-M Qualtrics, where custom JavaScript is enabled on his account. The
heat-map question type is not available there.

**Built:** the synthetic-only pilot, [`tools/rater_sheet/`](../../tools/rater_sheet/README.md).
It has 20 rows, a key kept out of the survey, a paste-ready question script, a local preview,
and a scorer. Tested end to end in Chromium.

## How the answer will be read

- **Real or synthetic:** d′ near 0 means people cannot tell the simulator from the data by eye.
  Their reasons for calling a row synthetic are a list of fixes for the generator.
- **Marks:** on synthetic rows, people's recall and precision against planted truth. On real
  rows, people's marks are the reference. **Synthetic is good enough to train on** if a detector
  tuned on synthetic data agrees with people on real rows about as well as people agree with
  each other. If not, people's marks become the training and tuning set.
- **Psychophysics:** recall by participation, timing spread and background puts people on the
  same axes as the detector maps.

## Waiting on Tony

1. **The pilot itself:** set up the survey (README, about 15 minutes) and take it once, to check
   the format, the gestures and the 2.5 s tolerance.
2. **Real rows:** a release by name of baseline-only stretches for this test (FOUNDATIONS §5,
   which does not extend by analogy), and who may see them.
3. **Raters:** at least three, so their agreement with each other sets the ceiling.
4. **If the psychophysics is to be published:** an IRB exempt determination.
5. **Cossart's public DANDI data:** whether figures of it may be committed (§5 does not say).

## Known weaknesses of the pilot

- Every planted row's first event falls at 30–45 s (the generator's spacing and margin).
- The flat and fitted fields differ in total event count (flat has more active ROIs), so "real or
  synthetic" may be judged on density rather than structure. With real rows, match density.
