---
status: waiting-on-tony
filed: 2026-09-16
---

# locust runs at a fixed 1 second, and everything published assumes that

**Found reading the plain-language detector review.** Tony, 2026-09-16: *"locust is duration
based. here you state they are 1sec long, but i hope we are actually using FWHM and
t_peak - t50rise"*. We are not, and the document was right about what ran.

## What the code can do, and what it did

`cicada_detect` takes `active_duration_mode`, and its docstring is explicit that
`"per_event"` reads the producer's own per-event duration out of `width_sec` under the
`width_def` that names the rule which made it — the FOUNDATIONS §7 contract, the one
`rise_durations()` now refuses to go around.

The shipped operating point does not use it:

```python
"cicada": OperatingPoint(
    params=dict(sce_percentile=99.999, active_duration_sec=1.0, n_surrogates=100),
```

`active_duration_mode` is absent, so it takes its default, `"fixed"`. Every locust number in
this project — the bake-off scores, the simulated grading, the calls on the real TTX and
senktide recordings, both streams — comes from holding each cell on for exactly 1 second after
each of its events, whatever the producer measured that event to be.

## Why it is not a one-line fix

**The percentile is coupled to it.** The 99.999 bar was retuned against the fixed 1 s setting
(`cicada.py`, 2026-08-20, with REGIMES). Switching to per-event durations changes how long
cells are held on, which changes the pooled frame counts the bar is a percentile of. Moving one
without re-deriving the other produces a detector nobody calibrated.

**It reaches the parity fixtures.** locust's 1e-9 parity is against interface2's
`generate_sce_cicada`, which is where the fixed duration came from. A change here is a fork
entry (`docs/forks.md`) and a named test exemption, per FOUNDATIONS §2 as amended by ADR-0003 —
which permits the change and requires the evidence that it helped.

**The GLOSSARY already says the other thing.** Its `locust` entry says durations come from the
producer. That is true of the port's capability and false of every run. The old detector
review's handoff flagged the same mismatch and it is still open (watch SAP013 when rewording).

## The decision

1. Re-run locust with `active_duration_mode="per_event"` on the bench, re-derive its percentile
   at that setting, and compare against the fixed-1 s operating point — or
2. keep the fixed second deliberately, and fix the GLOSSARY and every document to say so.

Either is defensible; what cannot stand is the current split, where the capability is documented
and the fixed second is what ran. ⚠ Until Tony rules, any document naming locust's duration must
say **fixed 1 second**, because that is what produced the numbers beside it.
