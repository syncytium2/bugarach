---
status: open
filed: 2026-10-23
---

# Rate-matched negatives as a tool, and the bench without decoys

From [ADR-0019](../adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md) (Tony,
2026-10-23: *"Consider old decoys dead. We'll add rate matched negatives to our toolset."*).
Two pieces of work, in this order:

1. **A rate-matched negative tool.** Input: any multichannel recording of event times,
   simulated or real, with no labels. Output: matched negatives that keep each channel's own
   rate and the shared slow change in rate (minute-scale and above), and destroy the
   alignment between channels. The per-ROI rigid shift at a *J* of seconds (ADR-0006
   decision 3; `bugarach.event_floor`) is the existing instance. Open questions: whether to
   offer a second construction (dithering in operational time, Louis et al. 2010), and how a
   test shows the slow part survived and the alignment did not. ADR-0006 already measured this
   for the rigid shift at *J* = 20 s.
2. **The bench without decoys.** Set `n_distractors=0` in the fast and slow bench configurations
   (combined inherits its decoy count from slow's) and re-derive the scores. This changes every bench
   number, so it is a PR of its own, with a run record. Until it lands, report only the
   `*_without_decoys` scores.

This is part of the general-toolset direction Tony set out on 2026-10-22: unlabelled event
times in, measured parameters, synthetic data, detectors chosen and tuned, and then a run on the
original data.

**2026-11-13, piece 1 is built in its first form.** `bugarach.negatives` takes onset times per channel and a
duration and returns per-channel rigid shifts at *J* = 20 s. Its tests show planted events stop being co-active
(37 to 40 crowded 2 s windows become 0 to 2 per draw) and a shared slow change in rate survives (the
count-variance ratio at 60 s bins goes from 30.8 to 30.0; an even scatter of each channel's onsets takes it to 0.7).
Still open: a command line, the second construction, and the same two checks on the simulator once it can plant a
shared slow change. Piece 2 is untouched.
