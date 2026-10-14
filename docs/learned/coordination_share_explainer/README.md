# What share of calcium events is coordinated, counted without defining a coordinated event

**Figure 1. The count.** Simulated recording, 32 cells, 5 minutes shown. A, the lane above the raster: the shared moments the simulation planted (▼ blue, one of a close pair, 2 s apart; ▼ orange, one of a medium pair, 10–20 s apart; ▼ green, a single moment). The measure never sees this lane. B: one tick per onset. C: onsets per 1 s window, *X*. D: the same 5 minutes in one shifted copy, each cell's onsets slid in time by its own amount.

![Figure 1](explainer_coordinated-share-fig1-the-count_20261014.png)

**Figure 2. Same mean, wider spread.** Simulated recording at the busy background. A: how many 1 s windows hold each count *X*; green, one shifted copy; black, the recording. B: green dots, *f*₂ and *f*₃ of each of 20 shifted copies; black diamond, the recording; arrow, the excess the measure keeps; and the participants per moment that the two excesses give.

![Figure 2](explainer_coordinated-share-fig2-wider-spread_20261014.png)

**Figure 3. Planted against recovered.** One point per simulated recording, 48 recordings per panel: filled, fixed model (adopted); open, binomial model; grey band, the pass band (within ±25% of planted); line, the right answer. A: moments of three sizes. B: moments all of one size. C: the bench's own recordings, as the tool's built-in check runs them.

![Figure 3](explainer_coordinated-share-fig3-planted-vs-recovered_20261014.png)

**Figure 4. Window size and the intervals between moments.** Median error over 48 simulated recordings per line, fixed model, at windows of 1, 2 and 4 s: ● black, mixed; ■ green, 120 s only; ▲ orange, medium pairs; ◆ blue, close pairs; ▼ yellow, very close pairs. Grey band in A, the pass band. A: the share of events. B: participants per moment. C: moments per minute.

![Figure 4](explainer_coordinated-share-fig4-window-and-intervals_20261014.png)

**Figure 5. What else it counts.** Simulated recordings with nothing planted, 24 per point. A and B: the share of events reported coordinated (line, median; grey, 10th–90th percentile; dotted, no stretch at all), for a stretch where every cell is busier, by its length (A) and by how much busier (B). C: pairs beyond chance, *f*₂, before (open) and after (filled) subtracting the shifted copies, one point per recording.

![Figure 5](explainer_coordinated-share-fig5-what-else-counts_20261014.png)

**Figure 6. How far one recording strays.** Simulated recordings, 24 per group: open, each recording's answer worked out on its own; filled, its answer as the tool reports it, with *f*₃/*f*₂ pooled over the 24; orange bar, median; line, the right answer.

![Figure 6](explainer_coordinated-share-fig6-one-recording_20261014.png)

---

## The question

*How can you count coordinated events if you have not defined what one is?* This measure never
decides which onsets belong together. It counts every onset in short windows of time and asks
how unevenly those counts are spread. What it does count as coordination, implicitly, is this:
**onsets in several cells within one window (1 s here), more often than the same cells' onsets
would line up by chance, and arriving faster than the whole field's rate changes.** The last
part is where it can be fooled, and Figure 5, what else it counts, shows how.

It is the measure `fireflies` will read treatment results through: the share of calcium events
that are coordinated, against the overall event rate. Today it runs on baseline windows only;
running it on treatment windows is the next piece of work.

**Every figure here is simulated, with a known answer. No real recording is shown or quoted.**
The real numbers wait on a corrected export; see *What waits* below.

## Terms

- **Cell**: one imaged neuron, called an ROI (region of interest) elsewhere in this project.
- **Onset**: the time one cell's calcium event reaches half its rise. Each onset is found in one
  cell alone, so it is settled before coordination is asked about.
- **Shared moment**: a time at which several cells have an onset together, give or take about a
  tenth of a second. The simulations plant these; the measure never looks for them.
- **Window**, ***w***: a stretch of *w* seconds (1 s unless a figure says otherwise).
- ***X***: the number of onsets, over all cells, in one window.
- ***N***: the number of cells (32 in every simulation here).
- ***k***: how many cells join one shared moment. **λ** (lambda): how often shared moments
  happen, per second.
- **Share of events coordinated**: of all onsets in a recording, over all cells, the fraction
  that belong to a shared moment.

## How the measure works

### 1. Count onsets in windows, and look at the spread, not the mean

Cut the recording into windows of *w* seconds and count the onsets in each, over all cells: that
is *X*, Figure 1C. The tool counts twice, the second time with the windows moved by half a
window, and averages the two.

A shared moment of 10 cells puts 10 onsets in one window. Cells with independent onsets rarely
do. So sharing shows in **how spread out the counts are**. In Figure 2A, same mean, wider
spread, the recording and a shifted copy of it have the same number of onsets, 0.44 per window
on average, but only the recording has windows holding 6 to 11.

Two numbers measure that extra spread: ***f*₂**, pairs of onsets in one window beyond what
chance gives, and ***f*₃**, triples beyond chance (their formulas are under *For developers*,
at the end). For cells whose onsets are independent and arrive at steady rates, both are close
to zero. Triples outnumber pairs in a shared moment: 10 cells make 90 ordered pairs but 720
ordered triples, which is why *f*₃ sits far above *f*₂ in Figure 2B.

### 2. Chance is measured, not assumed

Real cells are not that tidy. One cell's own onsets come in clumps, and the whole field drifts
over minutes. So chance is measured: the tool makes 20 copies of the recording in which **each
cell's whole train of onsets is slid along in time by its own amount**, wrapping round at the
end, with every two cells' amounts at least two windows apart. Each cell keeps its rate and its
own rhythm; what is destroyed is which cells had onsets at the same time. Figure 1D is one such
copy: the columns of ticks in Figure 1B are gone, and every cell has the same number of ticks.

The copies' *f*₂ and *f*₃ are subtracted from the recording's. In Figure 2B, the copies' *f*₂
sits a little above zero (0.03 per window), because each cell's own clumping survives the
sliding, and the subtraction removes it. What is left is the excess: 0.20 pairs and 1.21
triples per window.

### 3. From two numbers to three answers

If every shared moment is joined by *k* cells, the excess triples divided by the excess pairs is
*k* − 2. In Figure 2B: 1.21 ÷ 0.20 + 2 ≈ **8.1 cells per moment**. The excess pairs then give
how often such moments happen, λ. Each cell's coordinated onsets per second are λ*k*/*N*, and
**dividing that by the average cell's event rate gives the share of events coordinated**.

One recording's *f*₃ is noisy, so the tool does not use each recording's own *f*₃ ÷ *f*₂. It
pools that ratio over every recording it analyses together, and takes *f*₂ and the event rate
from each recording on its own. Figure 6 shows what that does.

## Does it get the right answer?

### The check, and the two models

The tool checks itself on simulated recordings where every planted moment's cells are known. It
passes when the median error of the share is within ±25%. Figure 3, planted against recovered,
is that check on three sets of recordings.

Step 3 assumed every moment is joined by the same number of cells: the tool's **fixed** model.
Its other model, **binomial**, lets each cell join each moment with the same probability, so
the number varies. Pairs and triples alone cannot tell the two apart: two numbers cannot fix how
often moments happen, how big they are on average and how much their size varies. The tool
adopts the fixed model.

- **Moments of three sizes** (10, 6 and 3 cells, as the bench plants them; Figure 3A): the fixed
  model reads **18% low** and the binomial 8% low (medians).
- **Moments all of one size** (6 cells; Figure 3B): the fixed model reads **5% low** and the
  binomial **17% high**.
- **The bench's own recordings** (Figure 3C), as the tool's check builds them: fixed 16% low,
  binomial 2% low.

All three medians pass. Single recordings under the fixed model recover from 0.67 to 1.12 of the
planted share, so some fall outside the band.

**Why the fixed model reads low, and by how much.** Two reasons. First, the ratio of triples to
pairs is pulled up by the biggest moments, so when moment sizes vary, *k* reads high and λ reads
low, and their product, the share, ends up low. Second, a moment whose onsets straddle a window
edge is split, and loses some of its pairs and triples; counting twice with shifted windows
steadies this but does not recover what is lost. **How low it reads depends on how much moment
sizes vary, and in real recordings that is not known.** On these simulations it ranges from 5%
(one size) to 18% (three sizes). The binomial model's closeness in Figure 3A is a cancellation:
on its own it reads high (Figure 3B).

The tool adopts the fixed model because the bench plants a fixed number of cells at each level,
so it is the model that matches how the bench was built. That is a reason about matching the
bench, not about accuracy. Read a fixed-model share as an underestimate, by an amount that
depends on how much the moment sizes vary.

### Window size, and moments close together

The bench's recordings since 2026-10-07 space their moments by intervals drawn from real
recordings (median 41 s on the fast stream), measured after merging any two events less than
2 s apart. So the closest moments real recordings hold are the ones the bench never plants.
These recordings plant them deliberately: on top of the bench's older layout, where every moment
is at least 120 s from the next, each recording in a set carries 2 pairs of moments closer
together. Figure 4, window size and the intervals between moments, compares five sets.

- **The share hardly moves**, except for moments closer than a window. For 120 s gaps only,
  medium pairs and the mixed set at every window, and close pairs at 1 and 2 s, the fixed model
  reads 14% to 19% low (Figure 4A). At 4 s,
  close pairs (2 s apart) read 21% low against 14% for 120 s gaps only: a 2 s pair falls in one
  4 s window about half the time, and two merged moments of different sizes read as one moment
  of the wrong size. Very close pairs (0.5 s apart) read 22% to 23% low at every window.
- **Participants per moment and moments per minute move a great deal.** When two moments land in
  one window, the measure sees one moment of both together, half as often. At 4 s, close pairs
  push participants per moment to 56% high (against 33% for 120 s gaps only) and moments per
  minute to 49% low (against 35%; Figures 4B and 4C). Very close pairs do it at every window: 50%
  to 69% high, and 48% to 55% low.
- **Medium pairs, 10 to 20 s apart**, move each number by no more than about 5 percentage points
  from the 120 s set.

The pass band applies to the share only. Participants per moment and moments per minute read
26% to 69% high and 33% to 55% low on every set here, outside ±25%, because of the size bias
above. They describe a recording; they are not checked against a tolerance. Under the binomial
model the share reads 3% to 17% low across the same sets and windows.

## What else it counts

Figure 5, what else it counts, uses recordings with **nothing planted**, where the right answer
is no coordination at all.

- **A stretch where the whole field is busier is counted, mostly at its edges.** Add a stretch in
  which every cell's rate rises by 0.1334 onsets per second (the bench's elevated-rate level, about
  27 times the quiet background, so 28 times in all) and switches on and off sharply. The shifted copies remove most
  of it: they slide each cell by at most about half a minute, so a long stretch still largely
  lines up with itself in the copies. What survives is its edges, where the rate changes faster
  than the slides. So it is counted most when it is short: a median 8% of events reported
  coordinated for a 30 s to 1 minute stretch, 3.0% for 5 minutes and 1.2% for 15 minutes (Figure
  5A). **It is how fast the rate changes that matters, not how long the change lasts.**
- **How much busier matters too** (Figure 5B). A 5-minute stretch with the bench's 30 s ramps,
  at twice the background in all, reads 0.14%, the same as no stretch at all; at 10 times, 1.0%;
  at 28 times, 2.8%. At 28 times, three quarters of all the recording's onsets fall inside the stretch.
- **A slow, steady change is removed.** Raise the background threefold, smoothly, over the 45
  minutes. At a busy enough background (13 times quiet), the change adds clearly to *f*₂, and
  subtracting the shifted copies removes 99% of it (Figure 5C, bottom row). At the quiet
  background the same rise barely registers at all, so that row shows nothing either way.
- **Each cell's own clumping is removed** in the same way (Figure 5C, the steady rows).
- **With no stretch, a recording reports close to zero, on either side of it**: a median 0.1%,
  from −0.4% to +0.6% (the dotted line in Figure 5A). A share can come out negative, when a
  recording has fewer pairs than its shifted copies. If every recording in a run has no shared
  moments at all, the pooled triples are not above zero and the tool gives no answer.

## How far one recording strays

The tool reports a share for each recording. Figure 6, how far one recording strays, shows how
far that answer can be from the truth, for one recording.

- **Fewer shared moments, more spread.** With 15 moments in 45 minutes at the quiet background,
  the middle 80% of recordings recover 0.78 to 0.86 of the planted share as the tool reports it.
  With 6 moments, 0.59 to 0.98; with 3, 0.69 to 1.02, and single recordings from 0.55 to 1.09.
- **Pooling steadies the median, not the single recording.** The tool's pooled answers (filled)
  spread about as widely as each recording's own (open), and more widely with 6 moments. With few
  moments, each recording's moments have their own mix of sizes, and one pooled *k* does not fit
  them all.
- **A lower event rate on its own does not add spread** (¼ quiet: 0.77 to 0.87). **A busier
  background does** (busy: 0.76 to 0.92, and 0.74 to 0.95 on its own), because the shared moments
  are a smaller part of everything.

Every simulated recording gave an answer. The tool also leaves recordings shorter than 300 s,
with fewer than 20 onsets or fewer than 5 cells, out of the background rates it reports; every
simulated recording here clears those limits.

## The simulated recordings

Every recording starts from the fast-stream bench's own generator: 32 cells over 45 minutes;
each cell's background rate drawn so that a few cells are busy and many nearly silent; each
cell's onsets clumped in time as in real recordings; at the bench's quiet background (0.0049
onsets per second per cell) or its busy one (0.0169), 24 recordings at each. The bench's planted
events and its decoys (near-coincidences it plants to test detectors) are turned off, and shared
moments are planted here instead: 15 per recording, 5 each joined by 10, 6 and 3 cells, onsets
scattered around each moment by 0.106 s (the jitter the tool's own check uses).

The mixed set (Tony, 2026-10-14) holds **2 close pairs** (moments 2 s apart), **2 medium
pairs** (10 to 20 s apart) and **7 single moments** per recording, every pair and single at
least 120 s from the next. The other sets in Figure 4 replace the four pairs with 2 pairs of one
kind, or with none. Figure 3C instead uses the bench's own recordings, built exactly as the
tool's check builds them, with intervals drawn from real recordings, about 7 events per 45
minutes, and the decoys on. The bench itself is not changed; what its revised version should be
is waiting on Tony ([todo](../../todo/2026-10-08-the-stack-ceiling-and-the-short-interval-bench.md)).

Figure 1 shows 30m to 35m of quiet recording 13, chosen as the 5 minutes holding a close pair, a
medium pair and a single moment. Figure 2 uses busy recording 3.

## Where the method comes from

Reading shared events from the spread of the population count is not new. Staude, Rotter and Grün
(2010, *J Comput Neurosci* 29:327, "CuBIC") use cumulants of the population count to infer how
many neurons take part in coordinated events in spike trains, building on Ehm, Staude and Rotter
(2007, *Electron J Stat* 1:473). The binomial model is the multiple-interaction process of Kuhn,
Aertsen and Rotter (2003, *Neural Comput* 15:67); the fixed model is the same family of model
with every event the same size. Sliding whole trains to measure chance is the spike-train
shifting surrogate (Pipa, Wheeler, Singer and Nikolić 2008, *J Comput Neurosci* 25:64; see also
the *rigid shift* entry in [`GLOSSARY.md`](../../GLOSSARY.md), which this tool's shift is not).

What is this project's: using factorial cumulants and solving them for *k* and λ, reporting the
share of events, the slides set at least two windows apart, applying it to calcium-event onsets,
and the checks above. A later paper by the same authors (Staude, Grün and Rotter 2010, *Front
Comput Neurosci* 4:16) extends the cumulant method to rates that change over time, which is the
weakness Figure 5 shows; it has not been tried here.

## What waits

- **The real numbers.** The baseline run on the default export (66 recordings, `senktide_ttx`)
  gives each stream's share under both models. **They are not quoted here.** That export has
  been under a contamination stop since 2026-10-05: the motion-correction check that removes
  cells pinned at the frame's lowest value missed some cells in one recording and removed too
  much in another, and four recordings from the diestrus (DI) group await review cell by cell.
  Pinned cells show events at the same moments, which is exactly what this measure counts. The
  numbers go in when the producer's corrected export is the default and the run is repeated on
  it ([the stop](../../todo/2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md)).
- **The interval schedule here is temporary.** When the revised bench is decided, this page should
  be redrawn on it.

## For developers

- The measure: [`tools/measure_coordination_rates.py`](../../../tools/measure_coordination_rates.py).
  The share is `coordinated_share_of_rate`; the shift is `shifted`; the solve is `solve` (one
  recording) and `per_recording` with `pooled_ratio` (pooled, as reported); the adopted model is
  `ADOPTED_MODEL`; the pass band is `CAL_TOL`; the limits on recordings are `shape_usable`; the
  elevated-rate note is `CAL_NO_PROBE`.
- *f*₂ = E[*X*(*X*−1)] − E[*X*]² and *f*₃ = E[*X*(*X*−1)(*X*−2)] − 3 E[*X*(*X*−1)] E[*X*] +
  2 E[*X*]³, where E[·] is the average over windows. With moments of *k* cells at rate λ, falling
  whole inside windows, *f*₂ = λ*wk*(*k*−1) and *f*₃ = λ*wk*(*k*−1)(*k*−2).
- The figures: [`explain_coordination_share.py`](explain_coordination_share.py); every number
  quoted above is in [`numbers.json`](numbers.json).
- The review: [murderboard record](../../reviews/coordination_share_explainer_2026-10-14.md)
  (written when the review finishes).
