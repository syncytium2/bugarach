# The performance table

**No detector is declared the winner, and that is the design.** The table reports what
each one measured and which requirements it failed. Nothing orders them.

> **Provenance.** Numbers below are **re-derived** — recomputed from
> `docs/learned/bakeoff.json` and the code, with the commands in §6 — unless marked
> ⚠ **inherited**, which means they come from
> [the ranking brief](handoffs/2026-08-30-ranking-the-detectors.md) and were not
> recomputed here.

Implemented in [`bugarach.performance`](../src/bugarach/performance.py).

---

## 1. Why there is no ranking

Sweep two detectors across the seven background levels at twelve seeds, then repeat with
the *next* twelve seeds. Same code, same grid. **The winner changes at two of the seven
levels.**

| background (Hz/ROI) | seeds 1–12 gap | winner | seeds 13–24 gap | winner | |
|---|---|---|---|---|---|
| 0.0026 | +0.0515 | CoactDetect | +0.0774 | CoactDetect | |
| 0.0052 | +0.0372 | CoactDetect | +0.0451 | CoactDetect | |
| 0.0080 | −0.0102 | LoCo | −0.0345 | LoCo | |
| **0.0120** | **+0.0032** | CoactDetect | **−0.0011** | LoCo | **flips** |
| 0.0190 | −0.0088 | LoCo | −0.0411 | LoCo | |
| **0.0280** | **−0.0411** | LoCo | **+0.0006** | CoactDetect | **flips** |
| 0.0400 | −0.0444 | LoCo | −0.0397 | LoCo | |

*Gap is mean F1, CoactDetect minus LoCo. Neither wins the axis: CoactDetect takes three
of seven in both blocks. **Each flip has a gap under 0.004 on at least one side** —
0.0032 against 0.0011, and 0.0411 against 0.0006 — and no level clearing 0.02 in **both**
blocks changes its winner. The largest between-block swing is 0.042, about the whole
spread separating the top four detectors.*

An ordering built on that produces a different ordering next week. **So the table prints
the fold range and lets the reader see the overlap.** That is not a weaker result than a
ranking; it is the accurate one.

> ⚠ The brief reports a stronger version — CoactDetect winning all seven levels on seeds
> 1–12 — and **it does not reproduce on `main`**, where it takes three of seven; varying
> the match tolerance does not recover it. Those numbers were most likely measured on the
> branch carrying a fitted background shape. Worth reconciling before that figure is
> quoted again.

## 2. What the table shows

```
8 seeds, 4 folds — fold range shown; no ordering claimed
detector                  F1     fold range  recall   prec  probe/min  ceiling  gate  distr       xRT
-----------------------------------------------------------------------------------------------------
tube                   0.681   0.629-0.744     0.92   0.54       2.05        —  none   0.96    302841
tube_guard             0.673   0.600-0.747     0.81   0.58       0.48        —  none   0.94    316537
CoactDetect            0.651   0.606-0.711     0.77   0.57       0.12        1  pass   0.94    114554
LoCo                   0.638   0.567-0.696     0.73   0.57       0.25        1  pass   0.94     28439
rate+context           0.571   0.463-0.647     0.70   0.49       3.47        2  FAIL   1.00   1444570
sixth                  0.541   0.472-0.627     0.74   0.45      21.48       25  pass   0.98     60366
tube_ratio             0.503   0.422-0.562     0.65   0.43       0.00        —  none   0.71    304976
tube_ratio_guard       0.471   0.424-0.545     0.58   0.41       0.00        —  none   0.71    301093
binned SCE             0.420   0.308-0.487     0.48   0.38       5.92        9  pass   0.56    602699
SPIKE-synch            0.254   0.205-0.341     0.17   0.54       0.88        1  pass   0.38     74893
tiny                   0.125   0.125-0.125     0.07   1.00       0.00        —  none   1.00     30937
trace                  0.118   0.095-0.125     0.07   0.79       0.00        —  none   0.98    318776

distr is REPORTED, NOT GATED — it counts span coverage, not firing; see the module docstring.
```

*Verbatim output of the command in §6, not retyped.* **Rows are sorted by F1 for
readability and that is not a ranking** — the top four ranges overlap, which is the point
of printing them. A **fold** is one held-out block of recording seeds; a detector's F1 is
its mean over folds and the range is the min and max across them.

⚠ **`sixth` is a stale display name for locust**, carried by the viewer's title map since
the 2026-08-24 rename. The table prints what the code prints rather than quietly
correcting it — filed as
[the title map still says sixth](todo/2026-08-30-the-title-map-still-calls-locust-sixth.md).

The overlap the table reports in numbers, drawn:

![Mean F1 per detector as bars, with each of the four held-out folds drawn as a dot on top. The four leftmost detectors have means from 0.638 to 0.681 and their fold clouds overlap almost completely.](learned/bakeoff.png)

*Panel A of the bake-off figure — every fold drawn on its mean. This panel exists for the
defect this document is about: its generator's docstring says "the previous report ranked
seven detectors over an F1 spread of 0.011 and called it an ordering". **Note the bars
descend left to right** — the figure still invites the ordering the table declines to
make. Panel B is the cost plane and is not argued from here. Re-derived: every bar matches
the per-fold means in `bakeoff.json`.*

**The fold range is the observed min and max, not an interval estimate**, and it is
deliberately not dressed as one. It exists so a reader can see that 0.651 (0.606–0.711)
and 0.638 (0.567–0.696) are not distinguishable here, without anyone choosing a threshold
on their behalf.

Four things it says:

- **rate+context fails its gate** — 3.47 firings/min against its own 2.0 ceiling. This is
  the one verdict in the table, and it is a pass/fail against a declared number, not a
  comparison with another detector. It ships that way because the bake-off picks each
  fold's knob by raw argmax with no probe gate.
- **The learned models read `none`, which is not `pass`.** No ceiling has been declared
  for any of them, so the table cannot say anything about them on that axis — while
  `tube` fires at 2.05/min, above the 2.0 that rate+context just failed on.
- **`distr` is reported and not gated**, because the measure is broken — §4.
- **`xRT` is platform-bound.** Raw seconds move with hardware and thread count; the
  normalised multiple gates at realtime and never ranks. A detector is not better science
  for having run on a faster machine.

## 3. Gates are requirements, not comparisons

A gate asks *is this detector doing something disqualifying*, answered against a declared
number. That question survives the removal of the ordering untouched, and it survives a
change of data set — which a preference about how much one failure outweighs another does
not.

**A gate is a column, not a removal.** A failing detector stays in the table with its
verdict beside it, because the table's job is to report. The earlier design dropped gated
detectors out of the ranking entirely; with no ranking there is nothing to drop out of.

Two of the three gates need no ground truth — the probe and the timing ratio — so they
still work on recordings with no coordination ground truth. Worth keeping in view when
this points at another lab's data.

## 4. The distractor column is broken

A **distractor** is a planted correlated burst: real cross-ROI coincidence that is not a
coordinated event. It is the most meaningful false positive this bench measures, and
*"should a burst count?"* has been open since the scoring module was written.

**The number does not mean what its name says.** One detector makes two detections in an
entire fold, matches a planted event with both — precision 1.000 — and is scored as
hitting twelve of twelve distractors. What is computed is *how many distractors are
covered by the union of the detection spans*: it scales with span width, has no
opportunity denominator, and unlike the probe count twenty lines above it in the same
function is not restricted to unmatched detections, so a correct detection is charged as a
distractor hit too.

So it reports and does not gate. Repair, evidence and ownership:
[the write-up](todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md).

## 5. What was considered and rejected

Comparing several algorithms across several data sets is a solved problem in statistics:
the **Friedman test with a Nemenyi post-hoc**, drawn as a critical-difference diagram,
which yields exactly the cliques an ordering would want and **derives them from the data**
rather than from a chosen number (Demšar, *Statistical Comparisons of Classifiers over
Multiple Data Sets*, JMLR 7:1–30, 2006).

**It is the wrong tool here**, for a reason specific to this bench. The mean-ranks
post-hoc compares two algorithms through a statistic that depends on *every other
algorithm in the pool*, so its verdict on A-vs-B changes when unrelated C, D, E are added
or removed. Benavoli, Corani & Mangili (*Should We Really Use Post-Hoc Tests Based on
Mean-Ranks?*, JMLR 17:1–10, 2016) measure the cost: on one pair the sign test has power
**0.94** where the mean-ranks test has **0.046**, and the critical value is inflated by
`sqrt(m(m+1)/6)` relative to a pairwise test — about **5×** at twelve detectors.

This bench **deliberately ships poor learned nets as controls**. Under a mean-ranks test
those controls would not sit harmlessly at the bottom of the table; they would inflate the
variance of every comparison made in their presence, so the detectors the controls exist
to anchor would get *harder* to tell apart the more carefully the controls were chosen.

If an ordering is ever wanted, the route is **pairwise** — Wilcoxon signed-rank or the
sign test, with Holm — because its verdict does not depend on who else is in the room.

## 6. Reproducing

```
# the table
python -c "from bugarach.performance import *; from bugarach.ui.app import TITLES; \
  print(performance_table(fold_scores_from_bakeoff('docs/learned/bakeoff.json')).render(TITLES))"

# the seed-block flip in §1 — runs in seconds
python -c "
from bugarach.bench import evaluate_background_curve as ebc, BACKGROUND_GRID
for lo in (1, 13):
    seeds = tuple(range(lo, lo + 12))
    c, l = ebc('coact','baseline_quiet',seeds), ebc('loco','baseline_quiet',seeds)
    print(seeds[0], [round(c[r].f1 - l[r].f1, 4) for r in BACKGROUND_GRID])"
```

Run pytest with `PYTHONPATH=$PWD/src` from a worktree, or it tests the primary checkout's
sources and fails toward green.

## 7. Open

- **The bake-off is 8 seeds in 4 folds.** Every F1 above rests on it. A 24-seed re-run
  would put the table on firmer ground and would re-quote every published number.
- **No probe ceilings for the learned models** — the `none` column. Setting them is a
  measurement, not a default.
- **The distractor measure** — §4.
- **The calibration loop** picks knobs by raw argmax with no probe gate, which is why
  rate+context ships over its ceiling. Fixing it re-quotes published numbers.
