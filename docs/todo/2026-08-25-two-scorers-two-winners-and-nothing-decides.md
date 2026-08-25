---
status: waiting-on-tony
filed: 2026-08-25
---

# Two scorers, two winners, and nothing decides between them

waiting: Decide how the promiscuity probe enters the score. Two rules are live in the tree, they pick opposite winners for the rate detector, and the re-fit cannot start until one is chosen.

> **Not murderboarded** — a finding for sessions in this tree. Every number is
> reproducible from `tools/make_rate_bar_axis_figure.py`. **If any of it reaches an
> outside reader, murderboard that artifact first.**

Went looking for whether the multiplicative bar (forks §3) holds across the
background axis, now that ADR-0003 makes mechanism changes ordinary work. Found
something in front of that question.

![Panel A, F1 against background rate for both mechanisms under both scoring rules: the additive curves separate widely between rules while the multiplicative pair lies exactly on top of itself. Panel B, firings in a block with nothing planted at the knob the probe-blind rule chose, log scale: additive between 8 and 92, multiplicative flat at zero](../learned/rate_bar_across_background.png)

## The two rules

| | precision is | the promiscuity probe |
|---|---|---|
| `BenchResult.precision` (`bench.evaluate`) | `n_hit / n_scored` | **excluded** |
| `tools/probe_rate_mechanism.py` | `n_hit / n_detected` | **included** |

Both are defensible and both are in the tree. `BenchResult.precision` excludes the
probe for a documented reason — it is severe enough that folding it in *"stops
measuring the detector and starts measuring how hard the probe was set"*, and
CICADA reads F1 0.09 one way against 0.68 the other. The probe tool includes it
because promiscuity is the thing item 8 predicts and it ought to cost something.

**The probe tool's docstring says it is *"mirroring `bench.evaluate`'s pooling"*.
It is not.** That is the exact fork `pool_scores`' own docstring was written to
stop:

> *"A review on 2026-08-16 found the learned models pooled by hand in two tools as
> `n_hit / n_detected`, while the six went through `evaluate` … the rule for what
> counts forked in silence. Import this."*

`probe_rate_mechanism.py` was written **after** that review, and re-forked it.

## What it costs, measured

Both mechanisms swept over their own knob at every point on `BACKGROUND_GRID`,
3 seeds, so neither is credited a sweep the other did not get:

**Multiplicative wins 1 of 7 points with the probe excluded, and 5 of 7 with it
included.** Same runs, same seeds, same grids.

The probe-blind rule picks additive thresholds firing **8 to 92 times in a block
with nothing planted in it**, and its F1 cannot see that
([the probe cannot fail](2026-08-16-promiscuity-probe-cannot-fail.md)). The
probe-inclusive rule hands the headline to how hard the probe was set.

## Why this blocks the re-fit rather than just annoying us

The revision plan already said so, in Phase 2, and this is what walking into it
looks like:

> *"**Make the promiscuity probe able to fail.** … **This must land before the
> re-fit**, or the campaign re-selects operating points against a score that cannot
> see promiscuity, which is the very thing items 7–9 are about."*

An operating-point campaign is a maximisation over a score. Two scores that
disagree about the winner will produce two different sets of shipped settings, and
whichever runs first will look authoritative.

## One asymmetry survives the open question

Multiplicative's F1 is **the same number under both rules** — it never fires in the
empty block, so the rules cannot disagree about it. Additive's differ by up to
0.256 depending on which rule is used.

That is weaker than *"multiplicative wins"* and much more robust: whichever way the
promiscuity question is settled, the multiplicative bar's score does not move.

## What this does not settle

- **Which rule is right.** Not a session's call: it decides what every published
  score in this project means.
- **Whether the multiplicative bar should be the default.** Its best α ranges 4×
  across the grid, so it is not background-invariant here and there is no single α
  to calibrate. Forks §3's reason for leaving the default alone — *"switching
  before Phase 4 would ship an uncalibrated operating point"* — is untouched by
  ADR-0003 and still holds.
- **Whether `probe_rate_mechanism.py` should be repaired or retired.** It informs a
  recorded fork, so silently changing its numbers is worse than leaving them with
  this file beside them.

## Decisions this needs

1. **How does the promiscuity probe enter the score?** Excluded (today's
   `bench.evaluate`), included, or a third form — a separate gate that a candidate
   must pass rather than a term in F1, which is what `hot_fa` already looks like.
2. **Does the re-fit wait for it?** The revision plan says yes.
