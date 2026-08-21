# Testing a port that guesses

Four of the six detectors estimate a threshold by shuffling the data. A second
implementation of one — the browser's — cannot use numpy's random source, so the
two disagree for ever, by sampling error, no matter how correct both are.

FOUNDATIONS §2 makes parity the product, and 1e-9 is the bar everywhere else. This
is what to do when 1e-9 is not available, written down after doing it three times
(LoCo, CoactDetect, SCE) and counting what each attempt missed.

## Split the detector in three. Only one part is soft

| part | example | how to check it |
|---|---|---|
| the observed statistic | distinct ROIs per bin | **exact** — no randomness reaches it |
| the threshold | 99.9th percentile of the shuffles | sampled — see below |
| the detections | merging, episode statistics | **1e-9, given a threshold** |

The third row is the one people miss. Detections are a deterministic function of
the statistic and the bar, so **give both implementations the same bar** and the
whole detection path comes back under a hard bar. Every port here takes an
optional threshold argument for exactly this, used by nothing but the test.

Without it the only available comparison is *"both found about the same number of
events"*, which passes a port that merges runs wrongly, takes the last maximum
instead of the first, or miscounts recruitment — none of which have anything to do
with sampling.

## For the sampled part, test convergence rather than closeness

Any fixed tolerance on a sampled quantity is a guess: tight enough to flake, or
loose enough to pass a port whose null is wrong. There is a better property.

> **Sampling error shrinks when you sample more. A wrong answer does not.**

So run both sides at N surrogates and again at 4N, and require the agreement to
improve. LoCo's exact-agreement fraction goes 73% → 81% → 87% at 100 → 300 → 600
surrogates, which is what two correct estimators of one quantity look like. A port
that pooled the wrong axis converges to a different number and its agreement stays
flat.

Where the statistic is **integer-valued** — a count of ROIs usually is — there is a
second handle: correct samplers land on the *same integer* for most bins, not
merely nearby. "Identical 70% of the time and never more than 3 apart" is a far
sharper assertion than any distance bound.

## Deterministic arithmetic reached only through a sampled path is untested

This is the mistake that cost the most, and it is not obvious.

`CoactDetect` divides by `n-1` to get a sample standard deviation. Using `n`
instead shifts every z-score by half a percent at a hundred surrogates — an order
of magnitude *below* sampling error, so **no comparison that runs through the
shuffles can see it**. It survived every test until the arithmetic was pulled out
into a function of its own and compared to Python's formula directly.

The same was true of MATLAB's percentile convention, of `erfc`, and of the
distinct-ROI binning rule. If a piece of arithmetic is deterministic, test it
deterministically, whatever it is buried inside.

## Simulated recordings do not produce edge cases. Build them

Roughly half the mutations that survived a first pass needed a hand-built vector,
because a simulation never produces:

- two firing bins **exactly** `merge_gap` apart
- tied maxima inside one episode
- a bin exactly equidistant between two threshold anchors
- an event on the recording's final instant
- a p-value landing exactly on alpha

Each is a real rule with a real off-by-one, and each is invisible to a random
recording. Derive the answer by hand, assert it, and say in the test why the
vector exists — otherwise the next reader deletes it as redundant.

## Check the test can fail, then check what it cannot catch

Mutate the port on purpose and count. Across the three ports here, 35 mutations
were tried and the first pass caught roughly half. The survivors are the finding —
they are the list of things the suite was silently not testing.

Two outcomes need naming rather than fixing:

- **Equivalent mutants.** SPIKE-synch's exact-tie shortcut changes no answer,
  because tau is always positive and the neighbour test accepts a separation of
  zero without it. SCE's "biggest bin vs last bin" is equivalent under its default
  merge gap of NaN, since no episode ever spans two bins. Record these, so nobody
  spends an afternoon writing a vector for a branch with no other side.
- **A survivor that is a flaw in the test.** A two-tailed p is exactly twice the
  right answer — and every case originally chosen sat deep enough in the tail that
  an absolute tolerance of `1e-15` swallowed the factor of two. The port was right
  and the assertion was worthless.

## Run the sweep against the whole suite, not one file

Two SCE mutants were caught by LoCo's and CoactDetect's test files. Sweeping one
file at a time overstates what is missing and sends you writing vectors that
already exist somewhere else.
