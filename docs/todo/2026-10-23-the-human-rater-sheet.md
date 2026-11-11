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
It has 10 rows of 15 minutes, an opening walk-through, a key kept out of the survey, a paste-ready question script, a local preview,
and a scorer. Tested end to end in Chromium.

## Settled on 2026-10-23, after Tony tried the first version

- **One x-axis length, 15 minutes, for every row** (*"ideally we take the x-axis length as constant"*,
  and *"choose a length that we can share with the dandiset"*). It fits all 59 Cossart recordings
  (shortest 1153.5 s) and this lab's 20-minute windows. Two-minute rows were *"very unrealistic for
  our data"*.
- **Zoom and pan are buttons**, with a readable axis (*"our people are very sensitive to the x-axis
  and being able to zoom … it is just hidden in gray tiny font"*).
- **A 30-second animated walk-through opens the survey.**
- **The judgement is a slider**: real, no idea in the middle, synthetic.
- **Cossart has plenty of events**, more than we do: about 6 clusters a minute at K = 12, around 90
  per 15-minute row. That is a heavier marking load than ours; how many Cossart rows a rater gets is
  open.

## Added 2026-10-25: the separation test

Tony: *"What is the limit of human detection of separation"*. Four rows (r11 to r14) plant pairs at
0.5 to 8 s apart, plus singles as controls, at 20% participation. The scorer reports P(resolved)
against separation and the fitted limit, with zoom logged per mark. How to read it is in the
[README](../../tools/rater_sheet/README.md), *The separation rows*. The handoff that asked for it is
[`2026-10-25-handoff-rater-sheet-separation.md`](2026-10-25-handoff-rater-sheet-separation.md).

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

- The flat and fitted fields differ in total event count (flat has more active ROIs), so "real or
  synthetic" may be judged on density rather than structure. With real rows, match density.
