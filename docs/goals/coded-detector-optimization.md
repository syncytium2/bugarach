# Goal: every hand-written detector runs at a setting this bench chose

> **The goal page for this work — start here.** The tree calls the same goal *the re-fit*, *the
> retune*, *best parameters*, *calibration* and *the optimization of the program detectors*; they are
> one goal. This page holds the goal, what is settled about it, what was tried and dropped, and what
> is waiting on Tony, with a link beside every line. **The linked file wins** where the two disagree,
> and a line found wrong is fixed in the same change as whatever you were doing.
>
> **Working material, not murderboarded** — same standing as [`pipeline.md`](../pipeline.md). No tree
> counts; measured numbers are content and carry their source. How the page stays true is at the
> bottom; the convention is in [`README.md`](README.md).
>
> **Written 2026-09-16** against `origin/main` at `a7fe2f8` and the open branches.
>
> ⚠ **Goal 1 of the program Tony set on 2026-09-17**: *full tuning of the coded detectors, every
> knob*. Five decisions bind it (one data folder, `steps_excluded`; train on the baseline and run on
> the full slice; the bench's fitted field as the simulation; fast stream first; every parameter
> except the data's own). They are in [`README.md`](README.md), *The current program*. The working
> plan, owned by WSMIP065, is [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md). Where
> this page and those two disagree, those two win until this page is brought up to date.

---

## The goal

Six hand-written detectors ship at one stored setting each, and a reader deciding whether to trust a
number has to be able to ask where that setting came from and get an answer better than *the function
signature*. Tony, 2026-09-16, on the review document's tuning figure:

> i can't release these data in the current state. it looks unfinished and no polish can hide that.

The goal is that every one of the six runs at a value **this** bench chose, under the false-alarm
budgets this project declares, across the parameters that actually move the answer — not one knob
each while thirteen others sit at whatever they were written with.

Abbreviations used below: **F1**, the harmonic mean of recall and precision; **ROI**, region of
interest (one imaged cell); **FA**, false alarm. *Held-out* means chosen on one set of bench
recordings and re-scored on a set the search never saw.

## Where it stands

**2026-09-24, evening: the rulings for final parameters are made, and the night is planned.**
[ADR-0009](../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)
answers #793's two questions and three more (R1–R5):
- the elevated-rate test gets a recording of its own;
- planted events under the floor are "don't care";
- ADR-0008 sets SPIKE-synch's `min_n`;
- the budgets stand;
- no context longer than 120 s is searched.

The runbook for the night is [`HANDOFF-overnight-final-parameters.md`](../../HANDOFF-overnight-final-parameters.md).
Every tuned number below is pre-ADR-0008 and is re-searched, not adopted.

**2026-09-24, the 3 × 3** ([run record](../learned/runs/2026-09-24-cross-stream-3x3/README.md)):
every stream's version of every detector, scored on all three benches with bootstrap intervals.
The diagonal reproduces last night's numbers exactly.
- The tops of the leaderboards sit inside each other's intervals.
- LoCo tuned on combined beats fast's own LoCo on the fast bench (0.791 [0.779, 0.803] against
  0.746 [0.733, 0.760]).
- SCE's slow proposal beats the shipped SCE on fast and on combined.

Where the search moved nothing, it may have stopped short of the best available setting.

**2026-09-24, overnight: CoactDetect searched on all three benches retuned to the 66-recording
default**, under the stop-gap floor (`min_rois` never below 3, *pre-ADR-0008*;
[run record](../learned/runs/2026-09-24-overnight-coact-chorus/README.md)). Fast proposes sliding
at alpha 1e-5, a 120 s context and an 8 s merge gap: +0.037 held-out mean F1 [+0.026, +0.045],
+0.021 on fresh seeds (0.726 → 0.747; without decoy calls 0.855 → 0.874). Slow and combined moved
nothing. **Not adopted**: the proposal waits on Tony, and ADR-0008's per-window floor waits on the
two bench questions in #793. **The other five were searched the same night**
([run record](../learned/runs/2026-09-24-overnight-rest-of-suite/README.md)). There are proposals
for rate+context, SPIKE-synch and locust on fast, and for SCE, rate+context and locust on slow, and
each holds on fresh seeds inside its detector's budget. Combined moved nothing. ⚠ Fast SPIKE-synch's
`dt` and `C_min` stopped at the search's extension cap, unbracketed. None is adopted.
**Run on the 66 recordings** at those settings
([detection run](../learned/runs/2026-09-24-detect-66-floors/README.md)), every window scored under
its own ADR-0008 floor and under its baseline floor. Senktide raises the floor most in OVX and ORX
(fast median 6 → 24 and 4 → 26 co-active ROIs), and there the two floors give very different call
rates. The paragraphs below are from 2026-09-16/17 and predate the slow and combined benches.

**The swept knobs are done; everything else has never been searched.** All six were retuned together
on 2026-09-16 ([PR #597](https://github.com/syncytium2/bugarach/pull/597)), and
[`bench.py`](../../src/bugarach/bench.py)'s `RETUNE` constant states the rule that chose them. Three
values moved, three were already best or inside the noise. That closed the *one knob per detector*
question and opened the larger one: `bench.py` says in terms that **only the one swept knob per
detector was searched; every other parameter is as it was**.

**A search over every *declared* setting finished** on 2026-09-16 at 17:02, into
`<darkroom>/bugarach/2026-09-16-full-search/`. It was a **measurement, not an adoption**. Its handoff, now
[`docs/handoffs/2026-09-17-evaluate-sliding-detectors.md`](../handoffs/2026-09-17-evaluate-sliding-detectors.md)
(`full-search` has landed; the file left the root on 2026-09-21), is **superseded** by
[`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md), which also corrects four of its
readings. Two of them are in the table below.

**Sliding LoCo and CoactDetect are built and not landed.** Branch `sliding-loco-coact`, also
unmerged: at their binned-tuned values they call more and break the empty-recording budget, so the
search has to hand them admissible values before they can merge.

**Next, 2026-09-17:** re-derive the bench from `steps_excluded`, fast stream, baseline windows. Then
search every parameter (not just the declared ones) with grids that extend until bracketed, and land
sliding at the chosen values. WSMIP064's tuning run (goals 2 and 3) is running and does not wait on
these. Its next comparison uses them. None of it is final: Tony is still deciding which detectors
and models to keep.

## What is settled

**Strength** follows [`MILESTONES.md`](../MILESTONES.md): *measured* is a number from a run, *decided*
is a ruling, *argued* is reasoning nobody has measured.

| finding | strength | source |
|---|---|---|
| **All six swept knobs were retuned together against the bench as it now stands** — 48 bench recordings per point on both backgrounds and on the empty recording, grids widened until no optimum sat on an edge, candidates limited to values under **both** false-alarm budgets, best by F1 averaged over the two backgrounds, and a stored value moved **only** where the gain's 95 % bootstrap interval excludes zero | measured | the `RETUNE` constant and each detector's `source` string in [`bench.py`](../../src/bugarach/bench.py) |
| **Three moved**: binned SCE 99 → 98 (mean F1 0.490 → 0.525), LoCo 99.9 → 99.5 (0.669 → 0.686), rate+context 5.0 → 4.5 Hz (0.606 → 0.630) | measured | the `source` strings in [`bench.py`](../../src/bugarach/bench.py); figure in `<darkroom>/bugarach/2026-09-16-best-parameters/` |
| **Three did not**: CoactDetect's alpha was already the best value inside both budgets; SPIKE-synch's every looser value fires over the busy-background limit; locust's 99.99 scores +0.010 mean F1 on an interval spanning zero, so 99.999 stays | measured | same `source` strings |
| **Only one knob per detector has ever been swept.** Every other parameter in each stored operating point is as its function was written | measured from the code, and stated in the code | [`bench.py`](../../src/bugarach/bench.py); [the wall this makes](../todo/2026-08-27-one-knob-per-detector-is-the-next-wall.md) |
| **Half the stored table is a code or viewer default rather than a calibration.** rate+context and binned SCE carry their function's defaults; SPIKE-synch and CoactDetect carry viewer FAST points; LoCo, locust and CoactDetect's alpha are the tuned ones | measured from the code | the `source` strings; `docs/todo/2026-09-16-three-detectors-run-at-code-defaults.md` ⚠ **on branch `detector-review-doc`, not on `main`** |
| **The bench's measured values hold on `steps_excluded`**, fast stream, baseline analysis windows (2026-09-17): 7 of 8 inside their 95% bootstrap intervals over 84 recordings. `participation` 0.18 sits 0.0018 below its interval, a rounding of 6/33, waiting on Tony. A test now fails if the pointer, the record and the bench stop agreeing | measured; one value waiting | [`bench_measured.json`](../learned/bench_measured.json), `tools/remeasure_bench.py`, `tests/test_bench_is_measured_on_the_declared_folder.py` |
| **Sliding LoCo and CoactDetect have calibrated values, chosen in that mode — and the switch is NOT on yet** (2026-09-17). It moves the viewer's calibrated defaults while the browser still runs both detectors binned, and moves the calls a slow-comodulation analysis is pinned to; it waits on those two. The values, held out on recordings the search never saw, against the binned points they would replace: LoCo mean F1 0.737 against 0.699, 1.7 calls/hour on the empty recording against a limit of 3 (sliding at the binned values was 4.0 and over), crowded 0.827 against 0.816; CoactDetect 0.746 against 0.702, 5.8 calls/hour against a limit of 7 (was 7.7 and over), crowded 0.818 against 0.808 | measured, held out | the `source` strings in [`bench.py`](../../src/bugarach/bench.py); run in `<darkroom>/bugarach/2026-09-17-full-search/sliding5/` |
| **A search maximising F1 under the three false-alarm budgets proposes an artifact, and a fourth budget is what refuses it.** The first every-knob run gained 0.11–0.31 held-out F1 for four of six detectors by running merge gaps out to about a minute, and lost 0.25–0.32 on crowded recordings where events sit 6 s apart. **The other budgets cannot see it**: merging makes a detector call less, so the artifact looks *cleaner* on every false-alarm measure | measured, one run | `bench.MAX_CROWDED_DROP`; run in `<darkroom>/bugarach/2026-09-17-full-search/` |
| **A context window wider than the planted spacing is rewarded for contaminating its own null**: the null sits high, the detector calls less, precision and F1 rise. The search chose 240 s on a bench that plants events 120 s apart, under all four budgets, until the rule went in front of it | measured | `bench.context_fits_the_null`; `tests/test_bench.py::test_the_bench_recording_keeps_the_null_clean` |
| **Sliding and binned disagree on real recordings only as `forks.md` §14 predicts** (2026-09-17, the 84 baseline analysis windows of `steps_excluded`, fast stream, at the binned-tuned settings): sliding calls more (LoCo 598 → 923 calls, CoactDetect 436 → 583) and never fewer for LoCo; a median 1.00 of binned calls survive within 2.5 s; CoactDetect's shared onsets move a median +0.30 s where LoCo's move 0.00 s, the bin edge becoming the first participating event. **Nothing unexplained blocks landing sliding** | measured, one run | `tools/compare_sliding_vs_binned.py`; run, figures and note in `<darkroom>/bugarach/2026-09-17-sliding-vs-binned/` |
| **The refusal machinery exists and is tested.** `pick_operating_point` refuses an optimum on the edge of its grid, a sweep where every value scores alike, and a winner that fires too often where nothing was planted, rather than reporting them | built | [`bench.py`](../../src/bugarach/bench.py), `tests/test_bench.py` |
| **The empty-recording false-alarm budget moved where a calibration can see it** — `MAX_FALSE_POSITIVES_PER_HOUR` and `false_positives_per_hour`, landed with the retune | built | [`bench.py`](../../src/bugarach/bench.py) |
| **With LoCo retuned, CoactDetect's lead is 0.003 F1**, and the background-curve tests say so with a tie margin rather than asserting an order the spread does not support | measured | `tests/test_background_curve.py` |
| **Two corrections landed immediately before the retune and moved every curve it reads**: locust holds each cell for the event's own width instead of a fixed second, and binned SCE's calls are scored over the bins they were made on | measured | [PR #594](https://github.com/syncytium2/bugarach/pull/594), [PR #593](https://github.com/syncytium2/bugarach/pull/593) |
| **A long context wins held-out and loses on crowded recordings.** The 240 s contexts that lead the overnight search's held-out column cost LoCo 0.044 and CoactDetect 0.022 mean F1 on the crowded check — the bench plants events at least 120 s apart, and a window-shaped setting can learn that spacing. ⚠ Corrected 2026-09-17: the LoCo winner also carries an 8 s merge gap, the top of its grid, which fuses crowded events planted 6 s apart. Part of the loss may be that, not the context | measured, one run | [`docs/handoffs/2026-09-17-evaluate-sliding-detectors.md`](../handoffs/2026-09-17-evaluate-sliding-detectors.md), now on `main`; correction in [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) §2 |
| **locust's minimum distance climbed to 12.8 s (128 frames), +0.119 held-out mean F1 and +0.149 crowded, and was still climbing.** ⚠ Corrected 2026-09-17: 128 frames is where the search's extension cap (`MAX_EXTENSIONS = 3`) stopped it, silently, so it is an unbracketed edge and not an optimum. A score that rises as repeat calls are suppressed points at the anchor question below | measured, one run; unbracketed | same; correction in [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) §2 |

## Tried and dropped — do not re-propose without new evidence

- **Stepped LoCo and CoactDetect in the search.** The first overnight run was stopped mid-stage on
  2026-09-16 because LoCo was chasing a smaller and smaller threshold step — a binned detector
  approximating a slide. Tony: *"the loco and coact should slide not step"*, which had been filed
  nine days earlier ([the todo](../todo/2026-09-07-detector-calls-move-with-the-grid.md)). The
  stopped run's files are kept beside the live one in the darkroom folder.
- **Running the next bake-off in the app** (Tony, 2026-08-28). Reversed 2026-09-16 — *"i believe
  these big runs need scripting and not in-app"* — on the grounds that the earlier ruling assumed
  the project was further along than it was. Recorded in
  [the bake-off gate todo](../todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md) and in
  `HANDOFF-workstation-tuning.md` on branch `tune-learned-vs-coact`.
- **Judging a setting on F1 alone.** The first version of the optimization handoff did, and never
  mentioned the promiscuity gate. Re-run through the picker the same sweeps said something else:
  binned SCE's apparent sacrifice was mostly the credit a detector gets for calling more bins, and
  four selection rounds it had called honest took picks the gate refuses.

## Waiting on Tony

Each is a decision, not a task, and nothing below it can be settled by a session.

| decision | why it gates the goal | filed |
|---|---|---|
| **Binned SCE at 98 or at 75** — 98 gives mean F1 0.525 at 3.4 calls an hour on an empty recording; 75 gives 0.665 at 41.8, against a declared limit of 6. The F1 optimum is excluded by the budget, not by noise | Decides whether the budget or the score is the binding constraint, for every detector and not only this one | [todo](../todo/2026-09-16-binned-sce-trades-false-alarms-for-f1.md) |
| **How the promiscuity probe enters the score** — two live rules pick opposite winners for the rate detector | [`MILESTONES.md`](../MILESTONES.md) lists it as blocking the re-fit; waiting since 2026-08-25 | [todo](../todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md) |
| **locust's anchor** — the half-rise in Python, the peak in the browser, and the width now painted forward from it | Two surfaces answer the same question differently, and the retune's locust numbers rest on one of them | [todo](../todo/2026-09-16-locust-anchor-and-the-panel-viewer.md) |
| **rate+context at 4.5 Hz**, given the gain is entirely on the quiet background and busy is slightly worse with more false alarms | A setting that helps one end of the difficulty axis and hurts the other is a choice about which recordings matter | the `source` string in [`bench.py`](../../src/bugarach/bench.py); the table in `HANDOFF-full-search.md` ⚠ **not on `main`** |
| **Whether the 24-seed bake-off is promoted** or stays beside the 8-seed run | [`MILESTONES.md`](../MILESTONES.md) holds the row: do not promote, the input data may be revised | [todo](../todo/2026-08-31-two-overnight-results-need-a-ruling.md) |

## Open work a session can do without a ruling

- **Land sliding LoCo and CoactDetect**, taking admissible values from the search — held-out and
  under all three budgets — and setting them in `OPERATING_POINTS` before merging. The learned-model
  tuning (WSMIP064) already runs this sliding code. Its next comparison needs the **values**: [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) §4.
  Branch `sliding-loco-coact`.
- **The browser still runs both of them binned** — `loco.js` and `coact.js`. Owed the moment the
  sliding versions land, or the two surfaces disagree about what a call is.
- **[`RESET.md`](../RESET.md) §7 step 5 is stale.** It says no tool in this repo runs a campaign and
  that the walk over every detector × regime is still upstream MATLAB. That has been false since
  `tools/refit.py`, and twice over since `tools/retune_operating_points.py`. The same sentence is in
  [`handoffs/2026-09-04-walk-the-loop-end-to-end.md`](../handoffs/2026-09-04-walk-the-loop-end-to-end.md).
- **A citation in `main` resolves only off `main`.**
  [`tools/retune_operating_points.py`](../../tools/retune_operating_points.py) sends a reader to
  *"the 2026-09-16 optimization handoff, §4"* for the parameters that were never varied. That
  section is real and is called *What has never been optimized at all* — in
  `HANDOFF-detector-optimization.md` on branch `detector-review-doc`, which has not merged. Either
  land the handoff or point the docstring at something a reader on `main` can open.
- **Viewer defaults against calibrated operating points**, field by field, with the caveats already
  written — and explicitly not a bulk adoption.
  [Todo](../todo/2026-08-12-reconcile-detector-defaults.md).
- **The bake-off hands `pick_threshold` its own training recordings back.**
  [Todo](../todo/2026-08-27-the-threshold-is-picked-on-the-recordings-it-trained-on.md), and the
  same defect in the tube ablation
  ([todo](../todo/2026-08-28-the-ablation-still-picks-thresholds-on-its-fitting-data.md)).
- **An edge-of-grid optimum is a refusal on the hand-written path and a warning on the learned one.**
  [Todo](../todo/2026-09-09-an-edge-of-grid-threshold-refuses-on-one-branch-and-warns-on-the-other.md).
- **Whether the overnight search closes the MATLAB port.** `tools/search_all_settings.py` is the
  first thing here that walks every detector against every declared setting, which is what
  [the port todo](../todo/2026-08-12-port-coordination-benchmark.md) was filed for. Decide whether
  that todo is answered, narrowed, or still owed for the simulator half.

## Where the work lives

| what | where |
|---|---|
| The stored settings, and why each one is what it is | [`bench.py`](../../src/bugarach/bench.py) — `OPERATING_POINTS`, `RETUNE`, and each detector's `source` string. It is the one place that changes when a calibration does |
| The rule that picks a setting | `bench.sweep`, `bench.pick_operating_point`, `bench.MAX_PROBE_PER_MIN`, `bench.MAX_FALSE_POSITIVES_PER_HOUR` in the same file |
| The retune that used it | [`tools/retune_operating_points.py`](../../tools/retune_operating_points.py) — its module docstring is the statement of what *best* means here, written to be argued with |
| The search over every declared setting | `tools/search_all_settings.py` on branch `full-search` ⚠ **not on `main`** |
| Sliding LoCo and CoactDetect | `src/bugarach/detectors/sliding.py` and the `window_mode` branches on branch `sliding-loco-coact` ⚠ **not on `main`**; the binned versions stay as the MATLAB ports and their parity tests are untouched |
| Where the argument for the whole thread is written down | `HANDOFF-detector-optimization.md` on branch `detector-review-doc` ⚠ **not on `main`** — what is solid, where each detector stands, what has never been optimized, and what finishing costs |
| Run outputs | `<darkroom>/bugarach/2026-09-16-best-parameters/` and `<darkroom>/bugarach/2026-09-16-full-search/` — resolve with `bugarach.paths.darkroom()` |
| The ordering argument this thread sits inside | [`RESET.md`](../RESET.md) §7 — mechanism, then benchmark, then calibration ⚠ its step 5 is stale, above |

## Keeping this page true

- **A result toward this goal updates this page in the same PR.** A decision moves from *Waiting on
  Tony* to *What is settled* with its date. A dropped approach moves to *Tried and dropped* with its
  reason.
- **A session working on this goal says so on its board claim** (`Goal: coded-detector-optimization`)
  and names its branch `opt/<slug>`. Branches stay short-lived and land on `main`; the page, not a
  branch, is what holds the goal together.
- **Every ⚠ branch-only marker above is a debt.** When that branch lands, the marker comes off in the
  same PR. A goal page whose sources a reader on `main` cannot open is the condition this folder
  exists to end.
