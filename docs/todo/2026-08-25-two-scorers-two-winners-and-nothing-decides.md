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

---

# MEASURED, 2026-08-28 — the third form is not a proposal. It is in `bench.py`, it is the default, and it does not pick the winner.

`tools/probe_three_scoring_rules.py`. Decision 1 above lists a gate as a *third form* to
consider. **It exists.** `pick_operating_point(max_probe_per_min=-1.0)` looks the detector
up in `MAX_PROBE_PER_MIN` and raises `TooPromiscuous` rather than taking the runner-up
silently, and that dict's own docstring — landed **2026-08-22, three days before this file
was filed** — already gives the reasoning as a decision:

> *"the probe stays **out of F1**. Folding it in makes the headline measure how hard the
> probe was set … The fix for "the alarm cannot ring" is to give the probe a gate at
> **selection time**, not to corrupt the score."*

So the open question is narrower than *"two rules and nothing decides."* It is whether
that third rule, already running, is sufficient. **Measured — and the answer is not the
one the probe was written expecting.**

![Every candidate on both mechanisms' sweeps, placed by how often it fires in a block with nothing planted, one row per background rate. The dashed rule is the 2/min ceiling and hollow markers are refused: additive spreads from 0 to 6.1 with 31 of 56 hollow, while multiplicative sits on zero at every background with none refused](../learned/three_scoring_rules.png)

Same runs feed all three rules, pooled through `bench.pool_scores` — hand-pooling is the
specific defect this file is about, so the probe imports it rather than becoming a fourth
fork. `baseline_quiet`, 3 seeds, tol 1.5 s, each mechanism swept over its own knob.

**Which mechanism each rule picks, over the seven background points:**

| rule | precision | probe | multiplicative wins |
|---|---|---|---|
| 1 · probe-blind | `n_hit / n_scored` | excluded | **0 / 7** |
| 2 · probe-inclusive | `n_hit / n_detected` | in F1 | **6 / 7** |
| 3 · gate (shipped) | `n_hit / n_scored` | eligibility only | **0 / 7** |

**The gate sides with rule 1 on the mechanism, not with rule 2.** It does not break that
tie, and nothing here says it does.

**What it does do is refuse the thing this file objects to.** The complaint was that the
probe-blind rule *"picks additive thresholds firing 8 to 92 times in a block with nothing
planted, and its F1 cannot see that."* The gate sees it: **31 of 56 additive candidates are
refused** at rate's 2.0/min ceiling, and additive's own operating point moves — on the
quietest background from F1 **0.827 at knob 2** (5.5 firings/min) down to **0.689 at knob
4**. Half the sweep is ineligible at every background point.

**And the asymmetry this file already found gets sharper.** Multiplicative's F1 is not
merely the same under both rules — it never approaches the ceiling: **0 of 70 candidates
refused, maximum 0.2 firings/min**, against additive's maximum of 6.1. It is not that the
rules cannot disagree about multiplicative; it is that multiplicative never does the thing
the probe looks for.

## What this settles, and what it does not

- **Decision 1 has a live default with a written rationale**, so the question is *"is the
  gate enough?"* rather than *"pick one of two."* That is a smaller decision.
- **It does not choose a mechanism.** Additive's best *eligible* F1 still beats
  multiplicative's at all seven points, so forks §3's reason for leaving the default alone
  is untouched.
- **It does not validate the ceiling.** `MAX_PROBE_PER_MIN["rate"] = 2.0` against a
  measured 0.6 is a budget somebody set; every number above moves if it moves.
- **One detector, one regime, 3 seeds, no seed spread reported.** `baseline_quiet` only,
  and the mechanism-winner column is an argmax comparison, not a test.
- **The numbers differ slightly from the figure above** — 0/7 and 6/7 here against this
  file's 1/7 and 5/7, which came from `make_rate_bar_axis_figure.py` on its own grids. The
  pattern reproduces; the exact counts are grid-dependent and neither is the other's
  correction.
- **`probe_rate_mechanism.py` is untouched**, per this file's own instruction.

`--selftest` runs the gate at an infinite ceiling and requires it to reproduce the
probe-blind pick exactly on all 14 sweeps, refusing nothing. Without it the gate column
could differ for a reason that is not the gate. It passes.
