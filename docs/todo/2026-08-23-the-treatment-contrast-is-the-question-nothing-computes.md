---
status: open
filed: 2026-08-23
---

# Everything rests on the assessor, and the assessor is checked against MATLAB rather than against truth

> **Not murderboarded** — a planning note for sessions in this tree. Every number is
> quoted from a named file. **If any of it reaches an outside reader, murderboard that
> artifact first.**

Tony, 2026-08-23, restating the product end to end and then naming the load-bearing part:

> *"The user shares a folder with a series of recordings. They want to quantify
> coordination and whether it changes with a treatment. … The app assesses their
> recordings to establish parameters for a simulated data set with ground truth. …
> Then the user runs the detectors on the original data set and hits publish."*
>
> *"The whole thing rests on the assessor."*

It does, in four places at once, and that is worth writing out because no single document
currently says it.

## The four things it carries

1. **It sets the generator's knobs** — how often events happen, how many ROIs they recruit,
   how tightly — so the planted events the detectors are scored against are planted to
   *its* description of coordination.

   ⚠ **Corrected 2026-08-24.** This line originally read *"it sets the ground truth"*, and
   Tony withdrew that framing the next day: *"There's no ground truth and I shouldn't have
   allowed the idea of an independent assessor."* The planted events **are** known by
   construction and scoring against them is sound; what is not available is the step this
   sentence quietly took, from *the assessor's description of coordination* to *the truth
   about coordination*. The assessor is a **human-and-machine instrument** whose output
   carries a person's judgement — see
   [`the assessment needs a human in the loop`](2026-08-16-assessment-needs-a-human-in-the-loop.md),
   escalated. Everything else in this note stands; if anything the correction sharpens it,
   because an instrument with a person inside it is one more reason the contrast below
   cannot be read off a table unattended.
2. **It is what stops the loop being circular.** Its own docstring: measuring those knobs
   with the six *"would make every simulated recording a restatement of whichever detector
   measured it, and then training on it would close the circle. The assessment breaks
   that: it is a measurement convention, not a calibrated instrument."*
3. **It is the only rate-controlled instrument in the stack.** Its null is a per-ROI
   circular shift within the window — each train slides by its own lag and wraps — which
   *"holds every ROI's own rate and burstiness and destroys only cross-ROI phase."* The six
   detectors have no such property; that is the whole CFAR argument.
4. **It is therefore the right instrument for the question the user actually asked**, and
   the browser already knows it: any region is measurable, and the comment says why the
   rule does not forbid it — *"Measuring TTX and comparing it to baseline is a legitimate
   thing to want; feeding TTX into the simulator is not."*

Everything downstream inherits whatever it gets wrong, and inherits it **consistently**,
which is the dangerous kind.

## What it is validated against

`measure_coordination_timescale.m`, to **1e-9**. That is the whole of it. `test_assess.py`
holds four tests: it matches MATLAB, `jit_defined` is not the same as `jit_obs` being
finite, a short window returns NaN rather than a number, and ROI order does not change the
answer. Three of those are hygiene. The first is parity.

**Parity is faithfulness to an original, not correctness.** FOUNDATIONS §2 says exactly
what parity buys — it is *"what makes the ports citable in place of the originals"* — and
citable-in-place is not the same claim as right. If
`measure_coordination_timescale.m` carries a bias, bugarach reproduces that bias to nine
decimal places and every test in this repository passes.

**Nothing scores the assessor against planted truth.** `simulate.py` returns what it
planted; no test asks the assessor to find it.

## The circle is displaced, not broken

The docstring's claim is true as far as it goes: taking the generator's knobs from a
detector would make the benchmark a restatement of that detector. Using the assessor
instead breaks *that* loop. But it opens a smaller one that nothing names — **the
simulation is built to the assessor's convention, so the detectors are scored against
events shaped the way the assessor describes coordination.** A mode of coordination the
assessor does not measure is a mode the generator does not plant, and therefore a mode no
detector can be rewarded or penalised for.

That is not hypothetical, and the instance is already recorded in a different document:
**the generator plants no assemblies.** Each planted event draws its participants fresh, so
no group ever recurs — and the entire assembly-detection literature works by finding
recurring co-activation. `model_track.md` states the consequence: the benchmark *"cannot
reward membership structure at all."* A detector that exploits which cells fire together —
ours or anybody's — has no advantage to demonstrate here, because there is none to find.
Every test passes; the stack is internally consistent and blind in one direction.

## The check that does not exist and is cheap

Run the assessor on generated recordings whose coordination is known, and ask whether what
it reports tracks what was planted. It cannot validate the convention against biology —
nothing here can — but it would answer a narrower question that nobody has asked:
**does the headline statistic move monotonically with the thing it claims to measure?**

- plant more frequent events → excess should rise
- plant wider participation → excess should rise
- plant tighter jitter → the jitter statistic should fall, where it is defined
- **plant nothing at all → excess should be zero**, and this is the one worth running
  first, because a rate-matched null that leaks gives a nonzero reading on an
  uncoordinated recording and every generator spec derived afterwards inherits it

`simulate.py` already returns the planted truth and the bench already generates at two
backgrounds, so this is a test file, not a campaign.

## Two places it is already known to be soft

- **The jitter statistic goes missing exactly where it is most needed.** It is undefined
  unless the observed *and* the surrogate ensemble each form at least one cluster, so it
  vanishes on quiet recordings. The docstring flags it: *"the `jit_defined` flag is not
  decoration; a caller that ignores it will silently read NaN as zero."*
- **K is a human's call and the output does not carry it.** `derive_spec` requires `--k`
  explicitly because an assessment must not parameterize anything shipped without somebody
  signing off on which K. That is right, and it means the assessment's headline number is
  conditional on a decision that travels beside the file rather than inside it.

## And the question the loop opens with is never computed

Separate from all of the above, and smaller. `detect_folder` says what it is for in its
first line — *"run them, and write the events down"* — and that scope is correct. But it
means the pipeline ends at a table with `region_idx` and `region_label` per detection, and
**no function anywhere in `src/` puts two regions side by side.** No contrast, no ratio, no
paired statistic, no per-period summary. The user does the comparison in something else.

The raw material is deliberately right: `emit.py` carries the producer's own region index
and label unchanged, with *"No privileged region and no protocol vocabulary … there is no
reserved `baseline` and no 'treatment slot'"*. Keep that. Having no protocol vocabulary prevents the
app naming which window is the drug; it does not prevent computing *these two windows, this
detector, this stream, how different*.

**If that contrast is built, build it on the assessor first and the detectors second.**
The assessor is rate-controlled and the detectors are not: CoactDetect recalls **0.817** at
`baseline_quiet` and **0.560** at `baseline_busy`, so **0.26** of recall moves across a
3.7-fold rate change that is merely the interquartile spread of untreated slices. A
treatment that moves the background rate moves the instrument, and a detector-based
contrast reports coordination change plus sensitivity change with nothing separating them.
FOUNDATIONS §9 makes that concrete: coordination under TTX splits by stream, FAST at
**0.46** of its own baseline and SLOW at **2.50**. A result that runs in opposite
directions in two streams is the shape a sensitivity artifact could manufacture — and the
shape it could hide.

⚠ **The assessor is safer here, not immune.** Its excess is an absolute magnitude, co-active
ROI·events per minute, and whether two windows at different rates yield comparable
excesses is not established anywhere. That is the question to answer before the contrast
ships, and it is the same question as the sensitivity curve in
[`revise the bench recording before the re-fit`](2026-08-23-revise-the-bench-recording-before-the-refit.md).

## What must not happen

- **Do not add a treatment-derived endpoint to `REGIMES`.** Tried and withdrawn: a
  TTX-derived endpoint *"is still a treatment"* and pooled 37 slices whose effects *"run in
  opposite directions by group."*
- **Do not parameterize the generator from a treatment window.** The browser refuses this
  already and the refusal is load-bearing.
- **Do not read a detector's silence in a TTX window as validation**, and do not raise
  `min_rois` until a nonzero coactivity excess on TTX slices disappears. §9 names both by
  hand, because a session proposed the second one.
- **"Hits publish" has no referent.** The page writes `detections.csv` and `run.json` and
  stops; the only "publish" in the viewer is a comment about un-hiding the training panel.
  Whether the last step is an export, a report or a figure is an open product question, and
  it is Tony's.
