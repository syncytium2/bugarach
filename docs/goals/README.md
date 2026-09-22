# Goals — one page per thing we are trying to achieve

## The current program — set by Tony on 2026-09-17, and not final

**Read this before any goal page.** Tony, 2026-09-17: *"we're experiencing a lot of drift in goals
across sessions."* Three goals are current, and five decisions hold for all of them **until Tony
changes them**. **None of this is final** (Tony, the same day): *"we're still troubleshooting and
figuring out what models/detectors to keep."* So no result under this program is a final result
yet, and a detector or model that is in scope today may be dropped. A goal page or handoff that
disagrees with this section is out of date. Fix it in the same change as whatever you were doing.

| # | goal | page | machine |
|---|---|---|---|
| 1 | **Full tuning of the coded detectors: every knob**, all six | [`coded-detector-optimization.md`](coded-detector-optimization.md) | WSMIP065 |
| 2 | **A fair comparison of the coded detectors against the nets** | [`learned-model-family.md`](learned-model-family.md) | WSMIP064 |
| 3 | **"Final" supervised-learning results on the current best simulation** | [`learned-model-family.md`](learned-model-family.md) | WSMIP064 |
| 4 | **One stream for coordination**, fast and slow together, with each call naming the events it recruited from each — **added 2026-09-22, not started, no machine** | [`combined-stream-coordination.md`](combined-stream-coordination.md) | — |

**Goals 2 and 3 have their first result** (2026-09-19). Both runs finished with no errors on
disjoint draws, and each report was murderboarded in three blind rounds. **Under the shared
false-alarm budget CoactDetect is ahead of every net in every fold of both draws.** Chosen on F1
alone the two are nearly tied and the sign is not settled: the merge gap was tuned for the coded side
only, and margins are at the limit of what the scoring resolves — the replicate measured the
between-draw move at 0.010 F1 for the nets. The numbers, what the rounds changed and where the
reports live are in [`learned-model-family.md`](learned-model-family.md), *The weekend's two runs*.

Goal 2 depends on goal 1. A comparison against coded detectors that were tuned on a few knobs is
not fair, and that was the objection to the untuned bake-off in the first place.

**The five decisions (Tony, 2026-09-17):**

1. **Superseded 2026-09-21 — the folder is now `dataset.default()`**, which is
   `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED` (84 recordings) and is confirmed by the
   person at the start of every session. Tony, 2026-09-21: one default data folder, confirmed each
   session; `steps_and_pins_excluded` is it. `steps_excluded` is now an **archive** role — it
   declares a contamination and `dataset.current()` refuses it. The bench is still measured on it
   (`bench.MEASURED_ROLE`), and `tools/check_scored_dataset.py` flags that at session start until
   the bench is re-measured. The ruling as it stood on 2026-09-17, kept for the record:
   **One folder of real data: `dataset.current("steps_excluded")`**
   (`2026-09-03_revised_2v_long_STEPS_EXCLUDED`, 84 recordings). Tony: *"you should only work from
   the steps excluded folder. it is terrifying that you might use other data."* The senktide and
   TTX recordings are **inside** that folder. The separately declared roles `senktide` and `ttx`,
   the `.mat` stores, `default` and `pensub` are **not** used for this program.
2. **Train on the baseline, run on the full slice — but this run is baseline only.** Tony:
   *"our original goal was to train on the baseline and run on the full slice."* Simulation
   parameters come from the folder's **baseline** windows only (FOUNDATIONS §9). Running on the
   full extent — baseline, treatment and everything else in `regions.csv` — is the goal and is
   **held**: Tony, 2026-09-17, *"for this training run use only baseline."* So nothing in the
   current program scores a treatment window, and the full-slice run waits for his word.
   **A baseline window shorter than 15 minutes is not measured at all** (`bench.MIN_BASELINE_SEC`;
   Tony, 2026-09-17: *"baselines shorter than 15 minutes should be ignored. they probably should
   not have been exported."*). Nothing in today's folder is affected — its shortest baseline is
   17.0 minutes — so it is a guard against the next folder, and the right place for it is the
   exporter rather than here.
   **What `regions.csv` is:** the folder's table of periods, one row per period of each recording.
   interface2's `generate_export_folder.m` wrote it (`PROVENANCE.md` in the folder). It holds a
   period's label, when the period began and ended (`start_sec`/`end_sec`: the raw, untrimmed period
   from the lab's db4 record), and the part to score (`analysis_start_sec`/`analysis_end_sec`: the
   `long_window_20` windows Tony chose at export). Rules: [`export_folder_spec.md`](../export_folder_spec.md),
   `regions.csv`; the windowing regime:
   [`exports/2026-09-03_handoff_from_interface2_draft_final_run.md`](../exports/2026-09-03_handoff_from_interface2_draft_final_run.md) §2.
3. **The simulation is the bench's fitted field** (`bench.BENCH_RECORDING` and its two `REGIMES`),
   for all three goals. `docs/learned/generator_spec.json` (the "home spec", derived from the closed
   `.mat` store and marked superseded in [`MILESTONES.md`](../MILESTONES.md)) is **retired for this
   program**. WSMIP064's tuning run on its branch (`tune-learned-vs-coact`) relaunched at 12:42 on
   2026-09-17 as a **GPU shakedown on the home spec, not a result**. It is not stopped by this, and it
   gives way when the next comparison needs the GPU. The switch applies to what the nets are tuned on
   next. ⚠ The
   bench's own measured values do not yet come from `steps_excluded` either. `MEASURED_RATE_SHAPE` and
   `MEASURED_BURST_SHAPE` were fitted by `tools/fit_background_shape.py` on the `.mat` archive, and
   `MEASURED_PROVENANCE` is a MATLAB summary over 84 baseline windows. Re-deriving them from the folder
   is goal 1's first step.
4. **Fast stream first, then slow.** All three goals are finished on the **fast** stream before any
   of them is repeated for slow. The bench's measured values are fast-stream values already. Every
   result names its stream (FOUNDATIONS §9: under TTX the streams move in opposite directions).
5. **Every knob means every parameter** a detector accepts, **except the data's own**: the events,
   the time range, the frame interval, stream and column names, and seeds. That includes `min_rois`
   and the merge gaps, which the 2026-09-16 search deliberately left out. `min_rois` is reported with
   a warning that it can learn the simulation's planted participation level. The full inventory, and
   the parameters whose status is still an open reading, are in the goal 1 handoff
   [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md).

**Division of labour.** WSMIP065 owns goal 1: it lands sliding LoCo and CoactDetect, re-derives the
bench from the folder, and supplies the every-knob reference grids. WSMIP064 owns goals 2 and 3. The machines
share nothing but `origin`, so **everything one needs from the other goes through `main`**: this
section, the goal pages, and the handoff files at the root.

**Both GPUs are running goal 2's comparison this weekend, and that is deliberate** (Tony, 2026-09-18).
This paragraph used to say WSMIP064's tuning was a shakedown waiting on goal 1, and that **WSMIP065
runs no net fits**. Both were true when they were written and neither is now. The shakedown finished at
02:35 on 2026-09-18 and the real comparison launched the same afternoon at 16:14 on WSMIP064. WSMIP065
then launched **the same comparison on a disjoint draw of recordings** — `--replicate 1`, seeds
2000–2047 against WSMIP064's 1000–1047, sharing no recording — because once both sides are tuned the
shakedown's margin was +0.011 F1 and **variance binds**. The 24 configurations, the training seeds and
the grids are held fixed, so a difference between the two runs is a difference between draws of data.
`--replicate 0` declares byte for byte what WSMIP064 is already running, so that run stays resumable.

Both runs write a `progress.json` mirrored about once a minute into the darkroom —
`bugarach/2026-09-18-fair-comparison-run/` and `bugarach/2026-09-18-replicate-run-status/`. **An `at`
more than a few minutes old means the run has stopped**, and `STATUS.txt` beside it says the age in
words, so the answer is readable from any machine rather than from the one the run is on
(`tools/mirror_run_status.py`).

**Not among the three.** [`unsupervised-learning.md`](unsupervised-learning.md) and
[`detector-review-document.md`](detector-review-document.md) are not stopped by this section, and
they are not the current program either. Tony ranks them against it.

---

**Why this folder exists.** By 2026-09-14 the work toward a label-free detector was spread across two
handoffs, several proposals and review records, a long tail of todos, a draft branch and two darkroom
run folders. Every piece was findable, but nothing said what the goal was, what was settled, what was
dropped and what was waiting on a decision, so sessions and Tony both lost the thread. A long-lived
goal branch was considered and rejected: sessions start from `main`, the briefing and
[`INDEX.md`](../INDEX.md) read `main`, and a branch holds commits, not a summary.

**A goal page holds**, in this order: the goal in a paragraph; where it stands; what is settled, with
strength and source; what was tried and dropped, and why; what is waiting on Tony; open work a session
can do without a ruling; where the work lives; how the page stays true.

**How it differs from its neighbours.** [`MILESTONES.md`](../MILESTONES.md) is the whole project's
established record, one row per result. [`INDEX.md`](../INDEX.md) is keywords to files. A handoff is one
session's state at a stop and is deleted or archived when spent. A goal page lives as long as the goal
does and is the first thing a session reads when it picks that goal up.

**Conventions**

- A result, ruling or dropped approach toward a goal **updates its page in the same PR**.
- A session working toward a goal puts `Goal: <page name>` on its board claim and names its branches
  `<prefix>/<slug>`, so `git branch --list '<prefix>/*'` shows what is in flight.
- No tree counts. Every restated number links to the file that owns it, and the linked file wins.
- When a goal is reached or stopped, the page says which at the top and stays as the record.

| goal (the three current ones are numbered in the section above) | page | branch prefix |
|---|---|---|
| A coordinated-event detector that learns without labels | [`unsupervised-learning.md`](unsupervised-learning.md) | `unsup/` |
| Every hand-written detector at a setting this bench chose | [`coded-detector-optimization.md`](coded-detector-optimization.md) | `opt/` |
| A learned architecture that beats the hand-written detectors, separably | [`learned-model-family.md`](learned-model-family.md) | `nets/` |
| A document about the detectors an outside reader can judge | [`detector-review-document.md`](detector-review-document.md) | `review/` |

**Three of these four were written on 2026-09-16, and writing them is what found the problem they
fix.** Asked where four goals stood, two independent searches of `main` reported that the detector
review document did not exist and that detector optimization had nothing in flight. Both were reading
the tree correctly: the work, and the only summary of it, sat together on unmerged branches. A goal
whose account of itself lives on the branch it describes disappears the moment that branch lands — or,
until then, is invisible to every session that starts from `main`, which is every session.

**So a page may point at a branch, and it must say so.** Each of the three carries a ⚠ marker on every
source that is not on `main` yet, and taking a marker off is part of landing the branch it names.
