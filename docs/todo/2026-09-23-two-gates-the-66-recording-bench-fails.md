---
status: open
opened: 2026-09-23
area: bench
---

# Two gates the bench fails once it is retuned to the 66-recording default

**Waits on Tony.** The bench was re-measured on the default folder
(`2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED`, 66 recordings) and every
measured constant adopted, on his instruction to retune the numbers on the data set the work
now reads. Every constant sat inside its new 95% interval. Two design gates that sit
downstream of those constants then failed. Neither is a broken measurement, and each has more
than one reasonable fix, so both are marked in the suite as pending rather than resolved there.

## CoactDetect's precision swings 0.12 between the regimes, against a budget of 0.10

`tests/test_bench.py::test_precision_survives_the_regime_shift[coact]`. Precision is 0.60 at
busy (0.0169 Hz) and 0.72 at quiet (0.0049 Hz), at CoactDetect's shipped operating point, over
the test's two seeds. The budget, `bench.MAX_PRECISION_DROP["coact"]`, is 0.10 and has not
been touched. Options: re-tune CoactDetect on this bench (the search has not been run here),
re-budget, or keep the operating point and report the swing.

The marker is `OVER_BUDGET_PENDING` in that test file. It fails again if CoactDetect comes back
inside its budget.

## Seed 1's crowded recording is 18% isolated, under the 20% floor

`tests/test_bench.py::test_the_crowded_recording_contains_its_own_control`. The crowded
recording needs both populations, crowded (gap under 30 s) and isolated (gap of 60 s or more),
for the crowding effect to be measured inside one recording. On the new bench, seed 1 draws
42% crowded and 18% isolated events. The design is intact: across seeds 1–8 the isolated share
is 18–31%, and seven of the eight seeds clear the floor. But seed 1 is the recording the
crowding analyses read (`bench.py`, `tests/test_guard_on_surrogates.py` and three tests in
`tests/test_bench.py`), so its control group really is thinner. Options: move those analyses
to a seed that clears, pool several seeds, or lengthen the recording.

The marker is `CROWDED_CONTROL_PENDING`. It fails again if seed 1's shares change.
