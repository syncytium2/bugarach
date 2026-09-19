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

Goal 2 depends on goal 1. A comparison against coded detectors that were tuned on a few knobs is
not fair, and that was the objection to the untuned bake-off in the first place.

**The five decisions (Tony, 2026-09-17):**

1. **One folder of real data: `dataset.current("steps_excluded")`**
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

**Division of labour.** WSMIP065 owns goal 1. It lands sliding LoCo and CoactDetect, re-derives the
bench from the folder, and supplies the every-knob reference grids. WSMIP064 owns goals 2 and 3: the
nested tuning (a GPU shakedown on the home spec since 12:42 on 2026-09-17; the real run waits on goal 1) and the fair comparison. WSMIP065 runs no net fits. The machines
share nothing but `origin`, so **everything one needs from the other goes through `main`**: this
section, the goal pages, and the handoff files at the root.

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
