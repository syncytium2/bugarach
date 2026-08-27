---
status: open
filed: 2026-08-27
---

# Nobody typed the wrong number, and five documents still disagree

*These are the criteria the bake-off replacement has to pass before any number it
produces is quoted outside the repo. They were derived from a defect in the
current one.*

Five documents quote how much faster the learned detector is than LoCo. One says
eighteen times, four say seventeen. The obvious reading is that someone mistyped,
and it is wrong: **every one of the five is a defensible reading of the bench's own
output.** No arithmetic error was made anywhere.

That makes this a bench defect rather than a proofreading defect, and it is worth
writing down now because the replacement will reproduce it. The values are about to
change; the shape that let five careful readings land on two different integers is
not, unless something is done about it.

Throughout, **the learned detector** is `center−surround`, the 1,149-parameter model
that leads the bake-off table on mean F1, and **the bench replacement** is the
in-progress rework of the bake-off that supersedes the numbers quoted here.

## What the disagreement actually was

`docs/learned/bakeoff.json` records detection time per held-out fold. Computing the
two published speed ratios **within each fold**, rather than from the rounded means
the table prints:

| fold | learned s | LoCo s | CoactDetect s | LoCo / learned | Coact / learned |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.01376 | 0.24226 | 0.06260 | 17.60 | 4.55 |
| 1 | 0.01383 | 0.25171 | 0.06182 | **18.20** | 4.47 |
| 2 | 0.01398 | 0.22886 | 0.05414 | 16.37 | 3.87 |
| 3 | 0.01410 | 0.25658 | 0.06336 | **18.20** | 4.49 |

The LoCo ratio has a mean of 17.59 and a standard deviation of 0.86 across four
folds. A 95% interval on that mean — Student's *t*, three degrees of freedom — runs
**16.22 to 18.96**: it contains seventeen and eighteen both, and stops just short of
nineteen. **Two of the four folds measured 18.2.**

So "eighteen" is not a slip. It is inside the interval, and it is the figure two of
the four folds returned. "Seventeen" is the mean of the four, correctly rounded
down. A reader recomputing from the published table gets `0.245 / 0.014 = 17.5`,
which sits between them and settles nothing — and the published `0.014` carries only
two significant figures, so that recomputation is itself good only to about ±4%
before fold variation is counted at all.

There is no integer this quantity supports. The bench published it in a form that
required each reader to invent one, and its readers obliged.

## The criteria

Four are blocking: a claim that fails them is not publishable, however good the
underlying measurement is. The rest improve the artifact without gating it.

### Blocking — the derived number that lives only in prose

**Every quantity that will be quoted is emitted by the bench, including ratios.**
`17×` appears nowhere in `bakeoff.json`. It exists only inside hand-written
sentences in five documents, which is precisely why they could differ and why no
test could see it. A speed advantage is the headline claim; it should be a field,
not an exercise left to the reader. Emit the comparisons the write-up intends to
make, and prose cites them instead of deriving them.

### Blocking — the bare column

**Any column a headline rests on carries its spread in the published table.** The
bake-off table gives F1 as `0.668 ± 0.061` with a fold range beside it, and gives
`detect s` as `0.014`, bare. The speed claim is the strongest claim the bench makes
and it is the one column shown without dispersion. The spread was measured — it is
in the JSON, and LoCo's is 5% of its mean — and dropped on the way to the table. Had
it been printed, nobody would have written a whole integer.

### Blocking — one measurement per fold is not a timing measurement

**Timing needs repeats of identical work, and this bench has none.** `detect_sec`
has `n = 4`: one measurement per fold, four folds. Its standard deviation therefore
conflates two causes it cannot separate — folds genuinely differing in content, and
the machine being busy during one of them. Fold 2 is the whole story of the LoCo
ratio's low end: LoCo ran fastest there while the learned model did not, and the
artifact cannot say whether that is fold 2 being an easier scan or the timer catching
a quiet moment.

Time each fold several times and report within-fold and across-fold spread as
separate numbers. Timing noise is one-sided — interference can only slow a run — so
report the **minimum or median** of the repeats rather than the mean, which a single
descheduled run drags upward.

### Blocking — hand-carried numbers

**The prose derives from the artifact, or the build breaks.** This is the same defect
already filed against the generator write-up
([`2026-08-14-generator-doc-numbers-are-transcribed.md`](2026-08-14-generator-doc-numbers-are-transcribed.md)):
roughly sixty quantities copied by hand out of `bugarach.bench`, three
recalibrations in two days, each invalidating a different subset, and *"Prose does
not fail a test, so nothing said so."* The bake-off multipliers are the same disease
in a second organ. **The replacement is the next recalibration.** Without a render
step, keeping the documents in agreement stays a chore that fails quietly, and it
will fail across more numbers at once than it did here.

That todo already names candidate mechanisms for the render step. This is one job,
not two — solve it there and the bake-off inherits the fix.

### The two significant figures

Published cells need enough precision to support the ratios readers will build from
them. `0.014` is two significant figures; anything divided by it inherits about ±4%
before fold variation is counted. Either print more digits or — better, and see the
derived number above — publish the ratio itself.

### The unrecorded machine

Ratios travel between machines; seconds do not. `bakeoff.json` records the machine as
`macOS-26.5.2-arm64` and `python 3.14.5` — no CPU model, no timer method, no
statement of what else was running. Absolute seconds are unreproducible off this
laptop, while a ratio largely cancels the hardware. `detect_x_realtime` is already
computed and is the better-normalised figure of the two. Headline the ratio or the
realtime factor, keep seconds as provenance, and record the machine well enough that
a rerun elsewhere is comparable.

### The ranking that already broke

**Name the axes held fixed, and show the ranking's sensitivity to the one already
known to move it.** `docs/forks.md` measured the detectors across a background grid
and found per-detector F1 spreads from 0.092 to 0.307 — against the bake-off's top
gap of 0.017. The published ordering is *known* to be fragile to a parameter the
bench holds constant, and the bake-off does not say so where the ordering is
presented. A new bench that repeats that is not an improvement on this one.

### The caveat below the table

**Say what the sample cannot separate before the numbers, not after.** Four folds,
eight seeds, two per fold; seed variance within a fold was never measured. The README
does disclose this — beneath the table, after the ranking has been read. If the
replacement still cannot separate its top few detectors, that belongs above the
table, in the same breath as the ordering it undermines.

## The through-line

The first three blocking criteria are one defect seen from three sides: **the bench
computes more than it publishes, publishes more than it can defend, and the gap
between those is where a human invents a number.** That gap is the thing to close;
the individual figures will move on their own.

## Two things this does not do

**The README is not corrected here.** [`README.md`](../../README.md) still says
"eighteen times faster than LoCo" where four other documents say seventeen. That is a
real inconsistency and it is deliberately left alone: the replacement supersedes the
value, and editing it now spends a murderboard pass on a number with a known expiry.
If the replacement slips, the one-word fix stands on its own — and the direction is
settled by something other than arithmetic, because ⚠ **seventeen is reportedly
already in circulation outside the repo, on résumé and application text that has been
sent** (Tony, 2026-08-27). That could not be verified from here: the multipliers
appear in neither `syncytium2-profile` nor `tonydefazio.com`, and the documents in
question are not in the estate. If it holds, standardising on seventeen costs one word
and standardising on eighteen retroactively falsifies documents already in strangers'
hands.

**Do not sweep on the string.** `docs/forks.md` contains an `18×` in its
background-grid table that has nothing to do with speed — it is CoactDetect's F1
spread divided by the bake-off's top gap. The `15×` in the row below it is the same
kind of quantity. A search-and-replace across the multipliers corrupts both.

## Where the numbers here came from

Every quantity above is recomputed from `docs/learned/bakeoff.json` at full
precision, rather than read off a rendered table — which is the practice the first
blocking criterion is asking the bench to make unnecessary.
