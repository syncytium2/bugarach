# Handoff — the rigid-shift rule as code, first of four pieces on the branch

> **Branch `unsup/rule-as-code`.** Working material for sessions in this tree.
> Goal page: [`goals/unsupervised-learning.md`](../goals/unsupervised-learning.md). The root
> `HANDOFF.md` belongs to the MAHICE/loop thread; do not edit it for this work.

## Why this exists

The rigid-shift pre-registration was signed, reviewed, amended and blind-reviewed on 2026-09-14,
and still could not be executed from its prose: results overlapped, gates could not fail, one
exclusion inverted its purpose
([blind-round record](../reviews/2026-09-14-preregistration-is-rigid-shift-usable_2026-09-14-round2.md)).
Offered a choice between writing the rule as tested code and stopping the goal, Tony chose code.
**Nothing reads a real recording until Tony signs the committed code and tests.**

## Done

- **`src/bugarach/confirm/rule.py`** takes gate readings in and returns verdicts and one outcome.
  It uses no data and no randomness.
- **`tests/test_confirm_rule.py`** has 35 tests: every gate boundary, every stream combination,
  and a 20,000-run property test that better evidence never gives a worse outcome.
  Mutation-checked: four reverted rules each fail the suite.
- **The property test found a defect no reviewer had.** Reading Cossart at the single smallest
  passing displacement let one more passing cell turn VIABLE into NARROWED. Cossart and group
  exclusion are now read over every passing position.

## Choices in `rule.py` that are the implementation's, not signed

Tony adopts these by signing. Each is marked ⚠ in its docstring.
- **Visibility floor:** the quantity is named as planted-minus-unplanted excess, in ROI·events
  per minute.
- **Group rule:** uses the lower bound at 0.05/3/4, not a point estimate.
- **Cossart reading and group exclusion:** read over every passing position.
- **FAILED_ON_COUNT:** a separate outcome, not STOPPED, for when some displacement passed leak and
  destruction but failed only on count.

## Next, in order

1. **Leak instrument** (`src/bugarach/confirm/leak.py`):
   - interior windows: whole 60 s windows from the generation-window start, trailing part
     dropped, first and last excluded;
   - features **without the edge-band columns**, since the blind round showed they see
     coordination under rigid shift;
   - a public no-permutation CV scorer promoted from `tools/measure_recording_identity.cv_correct`;
   - a refitting mouse bootstrap with a fresh fold seed per resample, and a test that fold
     assignment varies;
   - a 20-seed negative control with its pairing permuted per seed;
   - seeds masked to 31 bits;
   - synthetic tests: a leak-free rigid shift passes, uniform dither fails, and coordination
     alone does not make rigid shift read as leaking.
2. **Count instrument:**
   - occupied frames per ROI per interior window;
   - an equivalence interval over mice, with one weighting for statistic and margin;
   - `edge_thinning` at *J* = 5 s as the control.
3. **Destruction instrument:**
   - in `surrogate_stats.destruction`, add `bin_sec`, assessor seed parameters, per-draw values,
     and a twin index in the surrogate, twin and freeze-half keys. The defaults must reproduce
     today's output, with a test that says so;
   - 20 twins;
   - the half-frozen homogeneous-resample control;
   - synthetic tests: a surrogate that leaves coordination FAILs, and homogeneous resample
     PASSes.
4. **Runner and salting:**
   - a runner under `tools/` that builds `rule` readings;
   - **a baseline guard (Tony asked, 2026-09-14, for confirmation that only baseline is
     tested).** For the lab folder the runner refuses any recording whose window source is not
     a baseline region, so the loader's whole-recording fallback can never reach it. It also
     refuses any window that overlaps a non-baseline region. A test must fail if either guard
     is removed. On 2026-09-14 all 84 lab recordings took the baseline path, each window 17–20
     minutes long, none outside its baseline region, and none overlapping TTX, senktide, high K+,
     SB222200 or wash. The Cossart folder declares no regions (untreated awake pups), so it is
     read whole, and the runner labels it that way rather than calling it baseline;
   - run tag `confirm-2026-09-14` salted into every seed, with a test that records every seed
     passed to `RandomState` and asserts none matches the exploratory set;
   - a `--limit` smoke run on synthetic folders only.

Then a short page for Tony pointing at the commit, to be signed. Then the run.

## Traps

- **Worktree tests:** run with `PYTHONPATH=$PWD/src`, or the shared venv imports the primary
  checkout.
- **Heredocs:** the repo hook blocks heredocs that write source; use the editor tools.
- **Contamination:** the overnight run's rigid-shift outcomes at the declared displacements must
  not be read.
- **Personal paths:** verbatim reports containing machine-local paths are blocked by SAP004;
  scrub them before committing.
