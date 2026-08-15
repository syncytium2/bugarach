---
status: open
filed: 2026-08-15
---

# `generator.md` says all six detectors count distinct ROIs coactive, and two do not

The murderboard on the public landing page
([`docs/reviews/index_2026-08-15.md`](../reviews/index_2026-08-15.md), finding
F1) caught this claim on its way onto `bugarach.tonydefazio.com`:

> every one of them counts *distinct ROIs coactive*

`GLOSSARY.md` says otherwise for two of the six:

- **rate+context (RateDetect)** — "population-rate excess vs a slow context
  rate". It counts events, not distinct ROIs.
- **SPIKE-synch** — "tau-capped adaptive SPIKE-synchronization profile with
  hysteresis detection". A synchronization profile over spike trains, not an
  ROI count.

CoactDetect, LoCo, binned SCE and CICADA do count coactive ROIs, so the claim is
true of four and stated of six.

**Why it matters beyond the wording.** The sentence is load-bearing in the
argument the doc's cold open makes: the flat-background finding is explained *by*
the detectors all counting distinct ROIs, so a flat field shrinks the effective
population. That mechanism holds for the four but is not established for
RateDetect or SPIKE-synch — yet the figure's own numbers (LoCo 5 real vs 10
generated) come from a detector that *is* in the counting group. The site now
says the weaker, checkable thing instead: all six find moments that stand out
from the rest of the recording, so the background's shape sets what stands out.

**Where.** `docs/generator.md`, the "Start here" section — on the unmerged
`rewrite-generator-doc` branch, which is mid-murderboard. Not edited from the
site branch on purpose: that document is a review in flight and an outside edit
would land underneath it.

## Also carried on that branch: `make_reality_check.py` has diverged

`main` now owns the figure and its generator, because the site publishes it.
Two fixes went in on `main` that `rewrite-generator-doc` does not have:

- the lower panel's rotated y-label was **clipped to `9.5 mHz/RC`** — the string
  is `mHz/ROI`, and the bottom panel has less vertical room than the top one
  because it carries the x-axis. Shortened so it fits.
- the header printed `simulate_coordination`, an internal identifier, in text
  that is now public. Now reads "the generator".

Whoever lands `rewrite-generator-doc` must keep both, or the next regeneration
puts the clipped label and the identifier back on the live site.
