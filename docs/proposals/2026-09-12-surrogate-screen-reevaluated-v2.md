# The surrogate screen: what the night bought, what it did not, and what to run next

**Status: draft, unreviewed.** Replaces
[`2026-09-12-surrogate-screen-reevaluated.md`](2026-09-12-surrogate-screen-reevaluated.md),
withdrawn the same day after its own murderboard: four of its conclusions rested on probe
numbers where production numbers existed. Every figure here is from the 2026-09-11 production
run unless the table says otherwise.

## The bottom line

The overnight run could not have produced a corrected flag at any setting, and that was
derivable from the plan before it started. Correcting within each reporting group instead of
across all of them cuts the required sample four- to fivefold — but it does **not** rescue the
night's data, which stays below the line either way. Only a new run can flag.

A rerun of the cells the night dropped costs **53,432 core-hours at 19 draws per cell** and
**278,409 at the plan's 99** — both from the run's own projections. I do not recommend buying
the joint-ISI half of that yet, for reasons in *What to run next*, and I am **withdrawing** the
previous draft's claim that its square-root axis is a no-op: it is not.

## What needs your call

| # | decision | options | what it costs | my recommendation |
|---|---|---|---|---|
| 1 | Does the joint-ISI family stay in the screen? | keep all radii · keep the affordable radii · drop the family | 53,432 core-hours at 19 draws, 278,409 at 99; 46 further cells unpriced | **Keep, but only the radii already measured.** It runs on 47 of 144 slow cells today. Dropping it revisits your 2026-09-10 ruling, and nothing here forces that. |
| 2 | `coverage` — redefine, or add a column? | redefine · add `scored_share` | redefining changes what every 2026-09-11 number means | **Add a column.** Keep `coverage` as shipped and publish the excluded count beside it. |
| 3 | Does the fast discriminator tier come back? | reinstate · leave void · rebuild the control | rebuilding needs a multi-seed control and a power fix | **Rebuild the control first.** Reinstating now would rest on a flag that is an artefact (below). |

## Where every number comes from

| source | path |
|---|---|
| production run | `<darkroom>/bugarach/2026-09-11-surrogate-screen/` — `cells.csv`, `stats.csv`, `destruction.csv`, `yardsticks.csv`, `meta.json`, `discriminator/` |
| probe (instrument only) | `<darkroom>/bugarach/probe-surrogate-screen/` — `stage2_*` 259 splits/519 draws, `stage2b_*` 260/520, `stage4_*` discriminator |
| code | branch `surrogate-screen-overnight`, commit `0dc6356`: `surrogate_stats.correction_reach`/`smallest_n`/`score_cell`, `surrogates.py`, `surrogate_discriminator.py`, `tools/probe_discriminator.py` |
| review of the withdrawn draft | `docs/reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md` |

The probe is used **only** for the question it was sized for — can the instrument answer — on
two recordings at three draws. Every cost, destruction and capability figure below is from
production. That distinction is what the withdrawn draft got wrong.

## Terms

| term | meaning here |
|---|---|
| *J* | jitter radius: how far a surrogate may move one onset (seconds on `steps_excluded`, frames on Cossart) |
| draws | surrogate draws per grid cell. **Not** *K* — the glossary reserves *K* for the coactivity floor |
| *K* | coactivity floor: co-active ROIs the assessor requires before it counts an event |
| scope | one reporting group. `steps_excluded` has five: the four mouse groups plus the pooled `all` |
| family | the checks Holm corrects together within one grid cell |
| band / paired | the two yardsticks: real-vs-real across mouse-grouped half splits; and the real value ranked among its own surrogate draws |
| twin | a matched synthetic pair, one with planted coordinated events and one without |
| destruction / retained | whether a surrogate removes planted coordination; `retained` is the share still visible (1 = all kept, 0 = all removed) |
| saturated | so many ROIs remain inside the assessor's coincidence bin that retention cannot fall, whatever the surrogate does |

## The problem, unchanged

A detector trained without labels learns to tell a real recording from a surrogate of itself, so
whatever it learns is coordination — but only if the surrogate differs in cross-ROI timing and
nothing else. Uniform per-onset dither fails that: it manufactures within-ROI intervals shorter
than any real one, a defect Gerstein (2004) described and Stella et al. (2022) corroborated. The
screen exists to find a replacement, and shortlists nothing by design.

## What the night could not do, per folder

Holm multiplies the smallest attainable *P* by the family size, so past α no corrected test can
fire — for any candidate, the known-bad control included. This is Tarone's (1990) testability
argument applied to a Monte-Carlo floor; the floor itself is Phipson & Smyth (2010), and the
correction is Holm (1979).

| folder | statistics | scopes | family, as run | band floor after Holm | paired floor after Holm | reaches α? |
|---|---|---|---|---|---|---|
| `steps_excluded` | 13 | 5 | 65 | 0.644 | 1.000 | no |
| `steps_excluded`, within scope | 13 | 5 | 13 | 0.129 | 0.260 | **still no** |
| `cossart` | 11 | 1 | 11 | 0.109 | 0.537 | no |

At the night's 100 mouse splits and 99 draws (Cossart: 40), **nothing flags under either rule**.
The scope change buys a smaller requirement, not a rescue:

| folder | family within scope | splits needed | draws needed |
|---|---|---|---|
| `steps_excluded` | 13 | 260 | 520 |
| `cossart` | 11 | 220 | 440 |

## What the probe established about the instrument

Run at 260 splits and 520 draws on the fast stream, uniform dither — the known-bad control — is
flagged under Holm in **every scope**; at 259/519 it is flagged in none.

| scope | checks | band raw → Holm | paired raw → Holm | smallest adjusted *P* |
|---|---|---|---|---|
| DI | 13 | 7 → 7 | 10 → 10 | 0.0498 / 0.0499 |
| MALE | 13 | 7 → 6 | 11 → 11 | 0.0498 / 0.0499 |
| ORX | 13 | 7 → 7 | 9 → 8 | 0.0498 / 0.0499 |
| OVX | 13 | 7 → 7 | 10 → 10 | 0.0498 / 0.0499 |
| all | 13 | 7 → 7 | 11 → 11 | 0.0498 / 0.0499 |
| **at 259/519, every scope** | 13 | 7 → **0** | 9–11 → **0** | 0.0500 / 0.0500 |

⚠ **Read this as resolution, not effect size.** Every flag sits on the attainable floor — band
1/261, paired 2/521 — so a check flags only when **no draw of 520** is as extreme as the real
value. One discordant draw lifts the adjusted *P* to 0.0998 and the flag vanishes. The design
has no margin: sizing for one is roughly 480 splits and 960 draws. Do-nothing stays at 0 of 13
throughout, which is the control behaving.

## What production says, and where the withdrawn draft was wrong

| claim in the withdrawn draft | production says |
|---|---|
| "the square root is a provable no-op, so half those cells are duplicates" | **False.** 23 sqrt/nosqrt cell pairs carry statistics and differ on 5–7 of 13. Elephant applies the square root before smoothing and before the cumulative is normalised, so normalisation cannot undo it. **Recommendation withdrawn.** |
| "joint-ISI is about six times uniform dither" | fast: 47.6 ms vs 0.159 ms per ROI per draw — **~300×**. slow: 4.14 ms vs 0.152 ms — **~27×**. The 6× was a probe artefact |
| "joint-ISI runs on `steps_excluded` only at the largest *J*" | it runs on **47 of 144 slow cells** (joint-ISI 24, ISI dither 23) and 2 of 144 fast |
| "the three generators exclude a third to a half of their ROIs" | **47.9–69.5%**: 1,261–1,827 of 2,630 ROIs |
| "3 of 6 fast radii are saturated" | the fast sweep has **7** radii; 3 of the 6 candidate radii saturate at the top floor, excluding the 20-second shipped-dither radius |
| "uniform dither moves 0.63 → 0.05" | that pair is the **20% participation** arm. At 50%: 0.948 → 0.424 (medians over 6 cells) |

## Destruction, from production and per participation arm

`steps_excluded` ran destruction at 19 draws and 200 assessor surrogates. Medians, fast stream:

| generator | 50%: floor 3 → 8 | 20%: floor 3 → 8 |
|---|---|---|
| do-nothing (must keep) | 1.000 → 1.000 | 1.000 → *no value at floor 8* |
| freeze-half (graded) | 0.465 → 0.187 | 0.377 → *no value at floor 8* |
| homogeneous resample | 0.003 → 0.000 | −0.016 → *no value at floor 8* |
| circular shift | 0.005 → 0.000 | −0.004 → *no value at floor 8* |
| uniform dither | 0.948 → 0.424 | 0.654 → *no value at floor 8* |

⚠ Two cautions the withdrawn draft lacked. **Neither zero-reader is a test**: the circular shift
*is* the assessor's own null, and homogeneous resample places onsets uniformly over the window —
the distribution that null is invariant under. Both read zero by construction; they calibrate the
zero point and cannot fail. And **Cossart's production destruction ran at 5 draws and 20 assessor
surrogates**, a tenth of the shipped ensemble, where the estimator is that ensemble's median — so
its numbers are not comparable with the table above.

## The discriminator, with the power stated correctly

| stream | control | pairs | ICC | design effect | effective n | required mice | mice | verdict |
|---|---|---|---|---|---|---|---|---|
| fast | positive | 1,669 | 0.112 | 5.14 | **324** | 89 | 44 | detected, underpowered |
| fast | negative | 830 | 0.000 | 1.00 | 830 | 35 | 44 | not flagged |
| slow | positive | 1,669 | 0.109 | 5.03 | **332** | 87 | 44 | detected, underpowered |
| events | positive | 1,375 | 0.004 | 1.16 | 1,184 | 18 | 32 | detected, powered |
| events | negative | 671 | 0.011 | 1.22 | 548 | **39** | 32 | not flagged, **underpowered** |

The test needs 654 independent pairs. Against effective n the `steps_excluded` positive controls
have about half of that. ⚠ **The `powered` flag is computed from the data it judges**: the ICC is
measured on the same correctness vector the test just produced, so a control that detects nothing
gets ICC ≈ 0, design effect 1, and reads "powered". The fast negative control reads powered for
exactly that reason. It cannot be used as evidence that a non-detection is meaningful.

The fast tier's voiding also rests on **one** draw: its 248 candidate rows carry a single distinct
void reason, stamped on 126, because the negative control is derived from the real features alone
and is identical for every candidate in a stream. Re-run at five seeds it flags once — but the
flagging run is the discovery run, so that is 0 of 4 fresh seeds, and five seeds cannot separate
α from 10α.

## What to run next

| # | step | why | cost |
|---|---|---|---|
| 0 | correct the shipped report | it still tells a reader the fast discriminator tier is void, and never shows the excluded-ROI count | minutes |
| 1 | fix the joint-ISI bin width | it is *J*/2, giving a 5-point lattice, where Stella bin at 1 ms | code only |
| 2 | rebuild the discriminator's negative control | multi-seed, and size on a pre-declared ICC rather than the observed one | code only |
| 3 | rerun the **cheap** class at 260 splits / 520 draws (Cossart 220/440) | the only sample that can flag; the gate now refuses less | measured per generator in `cells.csv` |
| 4 | destruction at the unsaturated radii, both participation arms | the 20% arm is missing a floor and was never reported | code + a short run |
| 5 | decide the joint-ISI radii to buy | see decision 1 | 53,432 core-h at 19 draws; 278,409 at 99 |

**Do not** buy the joint-ISI radii before step 1: the bin width is wrong in every one of those
cells. That is the whole of the "don't spend it yet" argument — the square-root duplication claim
that previously carried it is withdrawn.

## Residual ⚠

- The keystone is one candidate at one radius on one stream, every flag at the floor.
- `coverage` runs opposite to the exclusion it reports: 1.000 for generators excluding half their
  ROIs, 0.505 for those excluding none, because excluded ROIs leave numerator and denominator
  together. No verdict rule reads it today; one that did would prefer whichever generator
  discarded the most data.
- Saturation is computed at 50% participation only (`recruited = 0.5 * n_roi` is hardcoded), so
  every saturation verdict is about that arm.
- Fractional *K* is not a universal fix: at 10% it rescues Cossart (57 against 42.9 expected at
  *J* = 16 frames) and makes the fast stream worse (3 against 4.6 at *J* = 0.8 s).
- 46 of the 358 dropped cells carry no cost projection, so both core-hour totals are lower bounds.
- Three of the plan's own residuals are still open and bear on this: the circular shift's root was
  never searched, nobody has asked the producer about τ or Grün's group about surrogate selection,
  and Elephant's defects are unfiled.
- Louis, Borgelt & Grün (2010, ch. 17) is the published form of this screen's premise and is still
  unread — paywalled, on `docs/lit_needed.md`.
- The review behind this document is itself unconverged: no third blind round, and five of eleven
  roles never saw the rebuilt artifact.

## Sources

Holm 1979, *Scand J Statist* 6(2):65–70 · Tarone 1990, *Biometrics* 46:515–522 · Phipson & Smyth
2010, *SAGMB* 9(1):39 · Gerstein 2004, *Acta Neurobiol Exp* 64(2):203–207 · Stella, Bouss, Palm &
Grün 2022, *eNeuro* 9(3) ENEURO.0505-21.2022 · Amarasingham et al. 2012 (conditional jitter
framing) · Friedman 2003; Lopez-Paz & Oquab, arXiv:1610.06545 (classifier two-sample test) ·
Elephant 1.2.1, doi:10.5281/zenodo.1186602, RRID:SCR_003833 · Dard, Picardo & Cossart,
DANDI:000219; Dard et al. 2022, *eLife* 11:e78116.
