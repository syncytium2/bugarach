---
status: open
opened: 2026-09-25
area: bench tests; ADR-0009 follow-up
waits_on: Tony (the decoy finding); nobody (the re-measurement)
---

# Pinned bench measurements that predate ADR-0009 still run on the old bench

ADR-0009 decision 1 (PR #809, the final-parameters night) took the elevated-rate stretch off every
recording with planted events. Some tests pin a measurement taken on the bench with the stretch
inside, and their docstrings say that a change is a finding to measure, not a value to re-baseline.
Those tests now run on the pre-ADR-0009 bench through `pre_adr_0009_bench`, a fixture in
`tests/conftest.py`. Its single-test form is `pre_adr_0009_bench_here`. The fixture puts the
stretch back on every bench's `BENCH_RECORDING` while the test runs. It is the same pattern as
`pre_adr_0008_bench` for the floor.

**Due for re-measurement on the ADR-0009 bench:**

- **`tests/test_background_curve.py`, the whole module.** This covers the per-background F1 curves
  and the three conclusions CI showed moving without the stretch:
  - SPIKE-synch is no longer second at 25 mHz;
  - the largest rank change across the axis is now 4 places, by locust, against 3 by SPIKE-synch
    measured 2026-09-23;
  - on the flat field the winners are now CoactDetect, LoCo, rate+context and SPIKE-synch, not
    LoCo, rate+context and SPIKE-synch.
- **`tests/test_bench.py::test_the_distractors_can_actually_discriminate`.** ⚠ **This one is a
  finding for Tony, not only a re-measurement.**
  - Without the stretch, SCE hits all 12 decoys on seeds 1–2, as the other five detectors do. With
    the stretch it hit 2, and that was the whole spread.
  - SCE's threshold is a percentile over bins. The stretch used to fill the top of that
    distribution; without it, the decoys do.
  - So on the ADR-0009 bench the decoys do not separate the six detectors at their shipped
    operating points. Whether that is acceptable, or whether the decoys or SCE's operating point
    should change, is a decision, not a re-measurement.

When one is re-measured, move its assertions to the current bench and take it out of the fixture.
The measurement belongs in the same commit as the new values.
