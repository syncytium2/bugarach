# Ranking the detectors — what was measured, and the five decisions that are Tony's

> ⚠ **Not murderboarded**, on a context budget rather than a ruling. Review scope: a
> **role-1 claim check** — every number below was produced or re-derived in the
> session that wrote this, and the command is given wherever it is not a file path.
> **If any of it reaches an outside reader, murderboard that artifact first.**

> **Nothing is built.** This is a design brief. No ranking code was written, no test
> was re-baselined, and no operating point moved.

**The ask.** Tony, 2026-08-30: *"lets figure out a solid foundation for ranking the
detectors, assuming that another data set (cossart dandiset) might completely destroy
what we decide."* And on why it cannot be patched: *"all of this is flaky. i think we
have enough experience now, and the freedom at this moment, to rationalize this
performance ranking."*

---

## 1. Why the current ranking cannot be repaired in place

**F1 does not separate the detectors it is being used to separate.** Three
independent demonstrations, all from 2026-08-30:

| comparison | F1 | spread | verdict |
|---|---|---|---|
| learned `tube` vs `coact` | 0.681 vs 0.651 | fold ranges **0.63–0.74** and **0.61–0.71** | overlapping |
| `coact` vs `loco` | 0.651 vs 0.638 | ±0.044, ±0.053; coact takes **3 of 4 folds** | inside spread |
| background axis, 12 seeds | coact wins all 7 grid points | **by 0.0011** at the busy endpoint | a tie |
| background axis, seeds **13–24** | **loco takes the busy half** | endpoints disagree | **the ordering flips with the seed block** |

That last row is the one that settles it. The same code, the same grid, a different
block of twelve seeds, and the winner changes. **Any scheme that must produce a strict
order will produce a different one next week**, and re-baselining the three
`test_background_curve` asserts to today's numbers would encode a coin flip as a
finding.

⚠ **`SEEDS = (1, 2, 3)`** in `tests/test_background_curve.py` is the count this
bench's own author called noise-dominated one file over —
`HANDOFF-bench-background.md`: *"Use 12 seeds, not 3."* Two other probes inherit it,
including `tools/probe_three_scoring_rules.py`, whose 0/7 and 6/7 headline counts are
3-seed argmax comparisons with no spread reported.

## 2. What is actually instrumented — four failure modes, not two

`BenchResult` already carries more than the ranking uses:

| failure | field | needs planted truth |
|---|---|---|
| missed a real coordinated event | `recall`, and **`by_frac`** — recall *by participation level* | yes |
| fired where nothing was planted | `precision`, `n_fa` | yes |
| fired in a block with **nothing planted** | `hot_fa`, `hot_fa_per_min` — the promiscuity probe | **no** |
| fired on a **real coincidence that is not coordination** | **`distractor_hits`** | yes |
| fired near an event but not on it | absorbed into `tol_sec`, never reported | yes |

**`distractor_hits` has never entered a ranking and probably should.** `score.py:44`
calls the distractors *"genuine coincidence that is not coordination"* and says they
are tracked separately because *"'should a burst count?' is a live question."* That
question is still open and it is decision **D3** below.

**`by_frac` is the difficulty axis** — recall at 30% / 18% / 10% participation. A
detector that only finds large events is a different instrument from one that finds
small ones, and a single recall number hides it.

## 3. The probe is a real axis, and its name is wrong

Measured 2026-08-30, 12 detectors: **r(precision, probe) = −0.32**. Weak, and the
pairs settle it — `coact` 0.572 precision / **1.25** firings/min against `tube` 0.543
/ **20.5**. Near-identical precision, **17× the firings**. Precision is a *ratio*
measured on data containing events, so a trigger-happy detector collects true
positives that dilute its false ones; remove the events and there is nothing to
dilute with.

⚠ **But "false positives on empty data" is wrong, and the correction matters.** The
probe block is **not empty**: 591 spikes across 33 ROIs in five minutes, each ROI
drawn independently. Independent draws still coincide. Measured over 12 seeds, within
the planted jitter (0.36 s):

| ROIs coinciding | by chance |
|---|---|
| 3 (the participation floor) | **12.4 / min** |
| 4 | 2.97 / min |
| 5 | 0.57 / min |
| 6 (the median planted event) | **0.10 / min** |
| 7 | 0.02 / min |
| ≥8 | **0.00** |

About 4× fewer per extra ROI. **So a detector firing on a 3-ROI cluster there is
detecting something real.** What the probe measures is not "fires at nothing" but
*calls a chance coincidence coordination* — and read across that curve, each
detector's probe rate implies the cluster size it is consistent with: locust ≈2–3,
binned SCE ≈3–4, rate ≈5, sync ≈5–6, LoCo ≈6, coact below the floor.

⚠ That read-across is an **inference**: the detectors threshold their own statistic,
they do not count ROIs in a window. And `coact`'s 0.0 cannot be distinguished from
"never fires at all" by this measurement.

## 4. The constraint that should drive the design — and the thing I got wrong first

**Cossart's DANDI:000219 is a binary raster with no coordination ground truth.** So
`recall`, `precision`, `distractor_hits` and `by_frac` are not *degraded* there — they
are **absent**.

**But that does not sink the design, because the transfer path already exists and does
not score on their raster.** `tools/import_dandi.py` → export folder →
`docs/learned/assessment_cossart.json` → a **generator spec derived from their
statistics** → simulation *with* planted ground truth →
`fair_bakeoff.py --score-spec`, which fits on one spec and scores on another
(`f3c22bf`, mutation-tested both ways).

> **You transfer the statistics, not the data.** Every ground-truth measure therefore
> *does* survive to another lab's corpus.

This session asserted the opposite out loud before finding the importer, which is why
`docs/INDEX.md` now exists. **Read the INDEX before designing around a constraint.**

⚠ What does **not** transfer: timing comparisons. Their `time_sec` is the rising edge
of an inferred active run; ours is a `t50rise`. `import_dandi.py` — *"Rankings and
rates are safe; a claim that two labs' events coincide to within a tolerance is not."*

## 5. The shape I would propose — not a decision

1. **Split measures by what they require**, not by what they mean: ground-truth-needing
   (recall, precision, distractors, by_frac) vs available-anywhere (probe, timing,
   cross-detector agreement). You then always know which half you still have.
2. **Gates before scores.** A gate encodes a *requirement* and survives a dataset
   change; a weight encodes a *preference* and does not. `MAX_PROBE_PER_MIN` already
   works this way and is the model.
3. **Paired comparison, not marginal means.** Every detector runs the same folds and
   seeds. `coact` beat `loco` on **3 of 4 folds** — comparing `0.651 ± 0.044` to
   `0.638 ± 0.053` throws that pairing away.
4. **Output tiers, not a strict order.** Two detectors tie unless one wins a stated
   majority of folds by more than a stated margin. *"coact and loco are tier 1"* is a
   legitimate result that does not flip when the seeds change.
5. **The rule and the result live apart.** The rule is a decision, written once. The
   result is regenerated per corpus. **Cossart can destroy the result without touching
   the rule** — which is the only form of robustness the ask actually describes.

## 6. The decisions, all Tony's

| | decision | why it cannot be defaulted |
|---|---|---|
| **D1** | **Which measures rank, and which only report?** | Ranking on everything is a weighted sum in disguise, and the weights are a scientific claim |
| **D2** | **Is the probe a gate, a ranked score, or both?** | It is a gate today. Making it a score changes what "best" means; folding it into F1 was already rejected (`MAX_PROBE_PER_MIN` docstring: *"the probe stays out of F1"*) |
| **D3** | **Does `distractor_hits` enter at all?** | *"Should a burst count?"* — open since `score.py` was written. It is the most scientifically meaningful false positive and it is currently invisible |
| **D4** | **What counts as a tie?** | Needs a stated margin and a stated seed count. Anything smaller than ~0.02 F1 on this bench is noise |
| **D5** | **Platform-dependent measures — rank, report, or exclude?** | `detect_sec` and `calibrate_sec` move with hardware and thread count. `detect_x_realtime` already exists as the normalised form. The learned models' numbers are **platform-bound** (macOS arm64 vs Linux x86_64), which `test_lab_server.py` documents at length |

## 7. Do not do these

- **Do not re-baseline the three `test_background_curve` asserts to today's numbers.**
  They encode a claim — *"you cannot quote an F1 without saying what background it was
  measured at"* — and flipping `>` to `==` silently publishes the opposite scientific
  position. Their author left them red on purpose and said so.
- **Do not fold the probe into F1.** Rejected 2026-08-22 with a written rationale;
  CICADA reads F1 0.09 one way against 0.68 the other.
- **Do not rank on 3 seeds.** Use 12 or state why not.
- **Do not build a ranking that needs planted ground truth and then claim it transfers**
  without going through `--score-spec`.

## 8. Reproducing the numbers

```
# background axis at 12 seeds, both seed blocks
evaluate_background_curve(name, "baseline_quiet", tuple(range(1, 13)))
evaluate_background_curve(name, "baseline_quiet", tuple(range(13, 25)))

# chance coincidence in the probe block: count distinct ROIs in a sliding
# 0.36 s window inside BENCH_RECORDING["hot_window"], 12 seeds

# per-fold F1, the paired comparison
docs/learned/bakeoff.json -> hand_written[name]["per_fold"]
```

⚠ **Run pytest from a worktree with `PYTHONPATH=$PWD/src`** or it tests the primary
checkout's `src` and fails toward green — `2026-08-28-the-worktree-src-fix-nobody-has-chosen.md`.

## 9. State when this was written

`main` at `0188362`. Open: **#415** (index + briefing spill fix), **#414**
(`detector_history.md`), **#413** (handover todos), **#412** (site derives from data).
`bench-background-is-not-flat` is pushed at `f0f9b94`, **four tests red**, no PR,
waiting on the item-4 ruling — which is decision **D4** wearing a different hat.
