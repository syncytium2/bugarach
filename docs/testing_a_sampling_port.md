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

## Test the screen, not the function

Not about sampling, and kept here because this is where the browser ports are
tested and it is what they got wrong.

A window-provenance bug shipped in the browser page because every test called
`analysisSegments` directly and none of them pressed the button. The numbers were
right — the function returned exactly the window the detector then used — and the
sentence rendered beside them said *"whole period — none sent"* about that same
window. Both halves were individually defensible. Only the screen showed them
contradicting each other, and only the screen goes in a slide.

A test that reaches past the interface certifies the arithmetic and says nothing
about what a reader will be told. Drive at least one path per feature the way a
person drives it, all the way to the rendered text.

*(Playwright trap, paid for by the same lane: `inner_text()` returns empty for
content inside a collapsed `<details>`. Use `text_content()`, or open the accordion
first.)*

## A degraded result and an exit code that says success

Four defects found separately on 2026-08-23 were one failure mode, and naming it is
worth more than any of the four.

- A folder declaring no frame interval was reported **conforming**, run on an
  assumed 10 Hz grid, and its assumed value written into `run.json` as though
  measured.
- The site's lead figure lost every detector lane when `_compute` gained a required
  argument its caller did not pass. All six raised into a per-detector `except`
  written for one, and the tool exited 0 — shipping a valid PNG of a raster with six
  blank lanes, which is worse than the link card it could have fallen back to,
  because a fallback announces itself and this looked like a figure.
- `bugarach detect` wrote a `detections.csv` containing only a header and exited 0.
- The front page shipped its nav as unstyled links after the CSS was lifted out for
  injection into other pages and the injector skipped the one page that already had
  the markup.

**In every case a check existed and passed.** The conformance report called the
missing interval a note. The `except` was correct for one detector and wrong for
six. The nav had a suite asserting markup, reachability and link resolution, and all
of it passed while the page looked broken.

Two rules come out of it.

**Put the refusal in the exit code.** It is the only thing a caller reads. A script
testing `$?` cannot tell a stderr complaint from a clean run, and `build_site.py`
judges its figure step by nothing else. Scope it correctly, though: refuse at the
point of *measurement*, not the point of *loading* — `load_folder` still accepts a
folder that declares no interval, because such a folder is conforming and refusing
it would be the consumer overruling the producer.

**Distinguish "some failed" from "all failed."** One detector failing on an awkward
slice is a finding worth printing and carrying on through; all six failing has never
once meant six independent findings — both times it happened it was a caller left
behind by a signature change. The same split applies one level up, to recordings in
a folder. Whichever tool you are writing, the two cases must not look identical from
outside, and the boundary is the exit code.

**And the fourth had no exit code in it at all.** No check caught it; opening a
screenshot did. That is the section above, and it is why it is above.
