# Goal: a learned architecture that beats the hand-written detectors, and is known to

> **The goal page for this work — start here.** The tree calls the same goal *the model track*, *the
> learned detectors*, *the net design proposal*, *the field-size candidates* and *the bake-off*; they
> are one goal. This page holds the goal, what is settled about it, what was tried and dropped, and
> what is waiting on Tony, with a link beside every line. **The linked file wins** where the two
> disagree, and a line found wrong is fixed in the same change as whatever you were doing.
>
> **Not the label-free goal.** Training *without labels* against a surrogate negative is a different
> thread with its own page — [`unsupervised-learning.md`](unsupervised-learning.md). This page is
> about the **architectures**: what shapes exist, which of them can learn, and what they score when a
> simulator supplies the answer key. The two meet at stage 5 of the route below, and the tuned weights
> from this goal are meant to be that one's starting point later.
>
> **Working material, not murderboarded** — same standing as [`pipeline.md`](../pipeline.md). No tree
> counts; measured numbers are content and carry their source. How the page stays true is at the
> bottom; the convention is in [`README.md`](README.md).
>
> **Written 2026-09-16** against `origin/main` at `a7fe2f8` and the open branches.
>
> ⚠ **Goals 2 and 3 of the program Tony set on 2026-09-17**, both owned by WSMIP064: *a fair
> comparison of the coded detectors against the nets*, and *"final" supervised-learning results on the
> current best simulation*. Five decisions bind them, in [`README.md`](README.md), *The current
> program*. None of it is final. Two of them change the *next* comparison, not the run going now:
> **the simulation becomes the bench's fitted field**, with the home spec `generator_spec.json`
> retired for this program, and **fast stream first**. What that comparison needs from goal 1
> (WSMIP065) is in
> [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) §4. Where this page and those two
> disagree, those two win until this page is brought up to date.

---

## The goal

Six hand-written detectors set the bar, and the best of them sit within a few hundredths of F1 of each
other, which is inside the spread. A learned detector earns its place only by clearing that bar
**separably** — by a margin the fold-to-fold variation cannot explain — and by being understood well
enough that its margin can be attributed to its shape rather than to its tuning budget. So the goal
has two halves that have to move together: **expand the family** with architectures that test a
specific idea about what coordination looks like, and **tune both sides fairly** so a win is about
architecture and not about who got more knobs turned.

Abbreviations used below: **F1**, the harmonic mean of recall and precision; **ROI**, region of
interest (one imaged cell); ***t***, the paired *t* statistic over folds; **FA**, false alarm; **CV**,
cross-validation.

## Where it stands

**2026-09-24, the context span** ([run record](../learned/runs/2026-09-24-chorus-context-span/README.md)):
the chorus models were trained on 409.6 s crops but run on whole recordings, so the same weights
were run both ways: over the whole recording, and over consecutive 409.6 s pieces.
- On its own bench, the span moves F1 beyond seed noise in 1 of 12 cells (−0.015).
- Off its own stream, chorus_norm loses up to 0.090 F1 over the whole recording, all of it recall.
- The piece edge adds stretch calls, but only 0.003 F1 (median).
- On the 66 recordings, 87–98% of calls match between the two modes.

Measurement only; nothing is adopted.

**2026-09-24, the 3 × 3** ([run record](../learned/runs/2026-09-24-cross-stream-3x3/README.md)):
the picked chorus checkpoints were scored on all three benches, and run as saved, since every bench
recording has the same shape and encoding. The fast-trained chorus_norm transfers best:
- 0.789 on fast;
- 0.824 on slow;
- 0.802 on combined, where it ties the combined-trained one (0.799) and LoCo (0.802) at the top.

The slow-trained checkpoints lose 0.11 on fast.

**2026-09-24, overnight: chorus_norm and chorus_gain_norm trained on all three benches retuned to
the 66-recording default**, 5 seeds each, lr 0.01, on the GPU in 11–19 s a fit
([run record](../learned/runs/2026-09-24-overnight-coact-chorus/README.md)). **None of the 30 fits
collapsed.** On fresh seeds nothing chose on, the picked chorus_norm leads CoactDetect on fast
(0.789 against 0.747) and combined (0.799 against 0.785) and trails on slow (0.844 against 0.869),
with fewer calls on the empty recording on all three. Without decoy calls: fast 0.941 against 0.874,
combined 0.945 against 0.913, slow 0.994 against 0.999. The picked checkpoints are in the run's
darkroom folder. **On the 66 recordings** ([detection run](../learned/runs/2026-09-24-detect-66-floors/README.md))
they ran in every window, with each call kept or not under ADR-0008's per-window floor and under
the baseline floor, by the ROIs with an onset inside it. chorus_norm moves the same way as
CoactDetect between the two floors everywhere.

### The weekend's two runs: CoactDetect holds under the budget, and the rest is inside the noise

**Both runs finished 2026-09-19 with no errors** — WSMIP064 on recording seeds 1000–1047 at 05:58
EDT, WSMIP065's disjoint replicate on 2000–2047 at 07:47. Each machine wrote a report for a reader
new to the project and murderboarded it in **three blind rounds** plus a finding-driven pass. The
reports are committed at [`tuned_vs_coact/fair_comparison_2026_09_18/report.html`](../learned/tuned_vs_coact/fair_comparison_2026_09_18/report.html)
and [`tuned_vs_coact/replicate1/report.html`](../learned/tuned_vs_coact/replicate1/report.html); the
four architectures are drawn through draughtsman in `<darkroom>/bugarach/2026-09-19-comparison-architectures/`.

**Under the shared false-alarm budget the answer is clean and it survived every round.** Held to
1.6 times CoactDetect's own rates, **CoactDetect is ahead of every net in every fold of both
draws**. That is the selection with a stated operating constraint, and it is the one that replicated.

**Chosen on F1 alone the two are nearly tied, and the sign is not settled.** Counting every training
of every net, CoactDetect is ahead on average in both draws. But in WSMIP064's run the best net moves
ahead once both sides use the same **merge gap** — a setting only the coded side was allowed to tune —
and in the replicate it is ahead in most folds, its average pulled down by two trainings that failed.
**Margins this small are at the limit of what the scoring resolves**, and the matched-gap leads carry
*t* of only −1.5 to −2.1.

**The scale that makes those claims checkable.** The replicate measured what moves when only the
recordings change, configurations and training seeds held fixed: the nets by a median of **0.010 F1**,
the coded detectors by **0.003**. The shakedown's leads of +0.011 and +0.016 were exactly that size,
so a single run could never have told them from the draw. That is what the second draw was for.

**Three things the rounds established that a single pass would have missed:**

1. **The earlier +0.103 lead is gone even for the untuned nets.** So it was not lost to tuning them.
   The simulator and CoactDetect's own tuning changed together, and this run cannot separate them.
2. **The two sides win in different places.** On F1 alone the chorus nets find more of the faintest
   events — those joined by a tenth of the cells — when background firing is high; CoactDetect finds
   more of them when it is low. A pooled F1 hides that entirely.
3. **The nets are handicapped by construction.** Each fits only **10 of the 72** training recordings
   and picks its threshold on 2, while a coded setting is scored on all 72. Tuning moved the nets by
   a few hundredths at most, and not always upward.

**Among the coded detectors, binned SCE beats CoactDetect under the budget in a few folds**, by a few
hundredths of F1 — admissible there, in 3 of 4 replicate folds. Its *F1-alone* first place is a
different matter and does not stand: a 30 s merge gap it moved to in 8 of 8 folds, failing the
crowded-recording check in 7 of 8.

**The chorus nets often fail to train, and the failures are inside these averages.** About a third of
`chorus_norm`'s 432 inner fits per draw make one call per recording — F1 exactly 0.125 — and a sixth
of `chorus_gain_norm`'s. Two failed refits carry a whole fold's margin in the replicate.

**Why, diagnosed on WSMIP065: at a learning rate of 0.03 the head is never woken.** Across both draws
292 of 396 inner fits at that rate collapse, against 7 of 468 below it. Every collapsed inner fit has
a head layer that passes nothing varying — 153 of 153 for `chorus_norm`, 75 of 75 for
`chorus_gain_norm` — and no working fit does. Replayed bit-exactly against its checkpoint, the same
collapsed fit trains at 0.01 or 0.003, or at 0.03 behind a 200-step warm-up. Tuning chose no
lr-0.03 configuration for `chorus_norm` under either selection, so the cost to goal 2 is a smaller
effective grid rather than a wrong answer; `chorus_gain_norm` is the exception, picking that rate in
6 of 8 folds on F1 alone. The repair is filed as a decision, not made. Source:
[PR #667](https://github.com/syncytium2/bugarach/pull/667), ⚠ **landed at Tony's call with four open
murderboard findings and its round-2 repairs not blind-verified**. Its readout
[`chorus_collapse/`](../learned/chorus_collapse/index.html) and its
[todo](../todo/2026-09-19-chorus-norm-does-not-train-at-lr-0.03.md) are on `main` with it.

⚠ **A claim this page carried is withdrawn.** It read the **111** inner fits that collapse in *both*
draws as the same fits failing twice, and called the failure deterministic given configuration, seed
and fold pair. It is not evidence of that. Draws share their configurations, seeds and fold pairs and
differ only in recordings, so the per-configuration collapse rates predict an overlap of **111.5** on
their own — against the 111 observed, and 39.6 against 38 for `chorus_gain_norm`. The overlap is what
chance gives. Whether a collapse is reproducible is a question the replay tool can answer and nobody
has asked. Found by round 2 of the chorus-collapse murderboard; the same misreading in the replicate
report is in the todo above.

### The nets' merge gap, tuned like any other setting: it does not change the answer

**The setting only the coded side had been allowed to tune is now tuned for both, and no verdict
moves.** Each net's gap is re-selected on the inner fits of its training folds, as the run selected
every other setting: on F1 alone the gap is a configuration setting and each fit still picks its own
threshold at that gap; under the budget threshold and gap are chosen together among admissible pairs.
The search starts from the run's 2 s and moves only for 0.002 inner F1, goal 1's step, and only if the
move passes goal 1's crowded-recording check. **It needs no retraining** — a merge gap is applied when
a net's per-frame output is decoded, after the network has run, so the gaps are re-selected from the
saved fits (`tools/tune_net_merge_gap.py`, whose output records exactly that). At 2 s the re-decoding
reproduces both runs: all 3,881 fits' picked thresholds, rows and empty-recording counts, and both
selections' inner and held-out F1. **Both draws**: WSMIP064's fits and WSMIP065's, re-decoded by the
same tool on one machine.

**Under the budget CoactDetect still wins**, on average against every net in both draws and in 29 of
32 net-folds. Tuning closes 0.009 to 0.014 F1 of the chorus nets' shortfall: in this draw
`chorus_norm` −0.032 → **−0.018** (*t* corrected −1.19) and `chorus_gain_norm` −0.030 → **−0.017**;
in the replicate −0.092 → −0.083 and −0.025 → −0.015. The mechanism is not the obvious one: the
chosen threshold is **unchanged in 26 of the 32 gated choices**, so the gain comes from merging at
the same threshold, not from buying a lower one.

**On F1 alone the sign depends on two accounting choices, and the gap is worth about one noise unit
either way.** Scored the same way on both sides — the report's under-0.2-F1 refits set aside on the
baseline as well as the tuned choice — `chorus_norm` goes +0.005 → **+0.015** in the replicate and
−0.007 → **+0.004** here; `chorus_gain_norm` +0.003 → **+0.013** and −0.015 → −0.007. So the nets
that end ahead **were already ahead before the gap moved**, and on this selection the gap itself buys
0.008 to 0.011 F1, about the 0.010 F1 between-draw scale. ⚠ That scale's own source measures a **systematic +0.015 F1
shift in the nets' favour in the replicate's draw**, which is the size of the lead there, and the two
draws differ in machine as well as recordings.

**The long-gap inflation is not specific to the coded side.** In all 64 choices of both draws the
inner fits preferred a wider gap and the crowded-recording check refused it — 30 s for every net. This
is the veto that took binned SCE's F1-alone first place, now applied to the nets for the first time.
Two things it does not settle. ⚠ The settings it **accepted** lose a median 0.012 F1 on the crowded
recordings themselves, the same size as the gain, and two of them fail the check outright when it is
re-measured on the outer refits (`chorus_gain_norm` on F1 alone here, fold 3, by 0.063; the same net
under the budget in the replicate, fold 2, by 0.024). ⚠ And held-out F1 is largest at the **top of the
grid in all 64 folds**, so every chosen gap is a boundary the check imposed rather than an optimum —
as CoactDetect's 8 s is the top of its own grid. The two landing together is not agreement.

⚠ **The check is not the same test on both sides.** CoactDetect's reference in the run already carries
its 8 s gap, so its crowded check had nothing to refuse; the nets' compares a wider gap against their
as-run 2 s. And the 0.02 allowance that decides every gap here is still unsigned.

Source: [`net_merge_gap.json`](../learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.json)
and `replicate_net_merge_gap.json` beside it, and the page
[`net_merge_gap.html`](../learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.html) —
WSMIP064's draw (seeds 1000–1047) and WSMIP065's (2000–2047), both re-decoded on WSMIP064.
Murderboarded in one round of all eleven roles plus a blind verify round,
[`net-merge-gap-2026-09-19.md`](../reviews/net-merge-gap-2026-09-19.md); what the review changed is
listed there and in the page builder's docstring.

⚠ **The bench's values were re-measured on the de-pinned export** on 2026-09-17 by both workstations,
every value inside its own bootstrap interval — commit `2120516` on `tune-bench-comparison`, **not on
`main`**. Moving `MEASURED_ROLE` to the corrected folder is still undecided.

**There is a built route, and it is the best-organised thing in this goal.**
[`pipelines/learned-model-evaluation.md`](../pipelines/learned-model-evaluation.md) walks a new
architecture from registration to murderboard in eight stages, each with the gate it has to pass and
the incident that put the gate there. Use it when a new architecture exists and someone needs a
number for it; `tools/check_pipelines.py` keeps it honest.

**The family doubled this week, on branches.** The registry is the folder — every module in
`src/bugarach/learn/nets/` is imported and registers itself, so there is no name list to go stale.
On `main` that folder holds **tube** and its three variants, **line** and its one-sensor ablation,
and two controls, **trace** and **tiny**. Branch `tune-learned-vs-coact` ⚠ **unmerged** adds
**gauge**, **tube_no_bypass**, and five **chorus** variants.

**Two repaired chorus variants lead CoactDetect, and that margin is exactly what is under test.**
On the home spec, `chorus_norm` beats CoactDetect by 0.103 F1 (*t* 6.5) and `chorus_gain_norm` by
0.084 (*t* 10.2), paired over folds. But every learned model in that table ran at **one untuned
setting** while CoactDetect had been tuned on one knob — so the margins might be about the tuning
budget rather than the architecture.

**The run that settles it was lost, and is running again.** The workstation tuning run gives both
sides a declared budget under nested cross-validation. Gate 1 passed on 2026-09-16: the
`chorus_gain_norm` stop was ruled a low seed draw. The run launched under WSL on WSMIP064 at 21:52 and
was **lost at 01:57 on 2026-09-17**, when the university's privilege manager signed the user out
(armory `FINDINGS.md` §20). Tony's rulings: WSL is a dead route there. Go native, and train on the GPU
(`train(device=...)`, built the same day). Its status line is in `HANDOFF-workstation-tuning.md` on
branch `tune-learned-vs-coact` ⚠ **not on `main`**. **Relaunched at 12:42 on 2026-09-17 as a GPU
shakedown, not a result** (Tony: *"launch it"*, after choosing between waiting for goal 1 and running
a stale test). Nothing had run between the loss and then. It runs on the retired home spec as declared
on that branch, from Task Scheduler on the GPU (`--device cuda --gpu-jobs 2`), resumable. Its purposes:
prove a long unattended GPU run on that machine before the one that matters, and show which of the
nets' settings ever win. **It finished on 2026-09-18 at 02:35**: 2,089 jobs, no errors, and no
readout planned. Its summary is in `docs/learned/tuned_vs_coact/shakedown_home_spec/` on
`tune-bench-comparison` ⚠ **not on `main`**. The real comparison launched the same afternoon (below,
*Four more, before the run launched*). Before relaunching, a GPU correctness check agreed with the CPU and the
Mac: over three seeds each model's mean F1 is within 0.004 to 0.023 of the Mac's. The simulation change
and goal 1's every-knob grids apply to the next comparison, not to this run:
[`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) §4. The untuned home-spec table above
stays as the record.

## What is settled

**Strength** follows [`MILESTONES.md`](../MILESTONES.md): *measured* is a number from a run, *decided*
is a ruling, *argued* is reasoning nobody has measured.

### How the next comparison runs on the bench (decided, Tony, 2026-09-17)

Four rulings for goal 2's tuning run, taken one at a time with Tony. The rest of its design carries
over from `HANDOFF-workstation-tuning.md` on `tune-learned-vs-coact`: nested cross-validation, two
selections (F1 alone, and F1 under a shared false-alarm budget), three training seeds, and the GPU.

| # | question | decided | why |
|---|---|---|---|
| 1 | **The bench's two backgrounds** (quiet 0.0052 Hz and busy 0.0190 Hz per ROI, `bench.REGIMES`) | **The same as goal 1.** Every recording seed is simulated at both rates, and a model is scored on the mean of the two backgrounds' pooled F1. A third, typical-rate background was considered and set aside *"for now"*: it would mean changing goal 1's search mid-course and re-choosing the shipped settings | both sides are then chosen on the same objective, which is what makes the comparison fair |
| 2 | **What a net trains on** | **Mixed:** half quiet and half busy recordings for training, and one of each for picking the threshold | a net scored on both backgrounds should learn from both |
| 3 | **Where the shared false-alarm budget is measured** | **The bench's own instruments:** the probe (the 5-minute stretch at 0.06 Hz inside every recording), counted in both backgrounds' recordings, and `bench.make_null_recording` (a whole recording at the quiet rate, nothing planted). **Reported, never used to select:** a no-event recording at the busy rate. **Dropped:** the home spec's 0.25× stress twin, which describes no real recording | the budget then measures what `MAX_PROBE_PER_MIN` and `MAX_FALSE_POSITIVES_PER_HOUR` measure. On the home spec the quiet twin was already this rate (0.54 × 0.0097 = 0.0052 Hz) |
| 4 | **What the budget is anchored to** | **CoactDetect at the settings goal 1's every-knob search lands**, times the declared margin (1.6), with the exact values written into the run's declaration before it starts | it is the CoactDetect that will ship, and the run waits on goal 1's bench and grids anyway |

### Four more, before the run launched (decided, Tony, 2026-09-18)

| # | question | decided | why |
|---|---|---|---|
| 5 | **The fold defect** ([todo](../todo/2026-09-17-two-bake-off-folds-train-the-same-model.md)) | **Fixed before any launch**, in the tuning tool. Training seeds are dealt round-robin across the training folds, starting after the held-out one; the run replays `train`'s and `pick_threshold`'s own draws and refuses to start unless every outer fold has its own fitting set and threshold pair. `meta.json` records the check | the tuning tool had it too: in the shakedown, two of the four outer folds fitted the same ten recordings at seed 0. A paired test over folds assumes distinct fits, so more folds would have bought degrees of freedom the harness could not deliver |
| 6 | **Sliding or binned for the coded side** | **Sliding, and said so.** `bench.OPERATING_POINTS` still ships CoactDetect and LoCo binned (goal 1 held the switch for the viewer's sake), so the tool lays goal 1's chosen sliding values under every coded setting it scores and records each detector's window mode in `meta.json` | searching binned would put the coded side at a configuration goal 1 already measured as inferior: the unfairness goal 2 exists to remove, in different clothes |
| 7 | **What the rest of the weekend buys** | **Twelve seeds per fold instead of six**, everything else as declared. Not eight folds: that is about 45–50 hours, and the back half of the weekend stays free | at a tuned margin of +0.011 F1 (the shakedown), variance binds; each fold's held-out F1 now pools 24 recordings instead of 12 |
| 8 | **GPU workers** | **One** (`--gpu-jobs 1`) | measured on the tool's own fit path: `chorus_norm` 309 fits per hour at one process, 264–274 at two to six. Processes contend on one GPU under Windows' display driver |

**Launched 2026-09-18 at 16:14** on WSMIP064 from branch `tune-bench-comparison` @ `e8764aa`, from
Task Scheduler, into `%USERPROFILE%\runs\fair-comparison-2026-09-18\`. All four nets and all six coded
detectors, fast stream, bench simulation. Its `progress.json` is mirrored about once a minute to
`<darkroom>/bugarach/2026-09-18-fair-comparison-run/`. An `at` there more than a few minutes old means
the run has stopped. Training floor 11.7 GPU-hours, so it should finish early on 2026-09-19. Status
and readout plan: `HANDOFF-workstation-tuning.md` on that branch ⚠ **not on `main`**.

### The family

| finding | strength | source |
|---|---|---|
| **The folder is the registry.** Every module in `src/bugarach/learn/nets/` is imported by `pkgutil` and registers itself through `@register`, so to enumerate the family you list the folder. Nothing carries a hand-written name list that can drift | built | [`learn/nets/__init__.py`](../../src/bugarach/learn/nets/__init__.py) |
| **On `main`: tube, tube_guard, tube_ratio, tube_ratio_guard, tube_no_bypass, line, line_length, line_bound, trace, tiny, gauge, chorus, chorus_gain, chorus_gain_norm, chorus_line, chorus_norm.** The four tube variants are the mechanism candidates; trace and tiny are controls; plain `chorus` is the failed control its four repairs are measured against. Every one is in the lab server's capabilities and the browser's model picker, because the registry is the picker's only source | built | the folder; [`lab.py`](../../src/bugarach/lab.py) `_architectures()` |
| **gauge, tube_no_bypass and the five chorus nets landed on `main` on 2026-09-21**, code only, from branch `tune-bench-comparison`; their run output stays on that branch and in the darkroom | built | #680 |
| **`line` counts how many ROIs are lit and judges that count against its own background.** It takes the top mean F1 in the supervised bake-off (0.713) but **not separably from CoactDetect** (+0.063, *t*(3) = 1.31), and its one-sensor ablation is indistinguishable from CoactDetect (+0.005, *t*(3) = 0.34) | measured, held | [`MILESTONES.md`](../MILESTONES.md) section C; [`line.py`](../../src/bugarach/learn/nets/line.py) |
| **`tube` reproduces its shipped 24-recording F1 of 0.656 exactly** after the bypass flag was added, so `tube_no_bypass` is a controlled ablation and not a redefinition | measured | [PR #596](https://github.com/syncytium2/bugarach/pull/596) |

### What the models score

All of these are on **simulated recordings** — the simulator is the only place an answer key exists.
The home spec is 32 ROIs, four folds of six recordings, two torch training seeds.

| finding | strength | source |
|---|---|---|
| **chorus_norm +0.103 F1 over CoactDetect (*t* 6.5) and chorus_gain_norm +0.084 (*t* 10.2)**, seed-averaged, paired over four folds, both at fewer busy-window false alarms than CoactDetect | measured, two seeds, untuned | `docs/learned/field_size_candidates/README.md` and `learned_vs_coact.json` beside it ⚠ **on branch `tune-learned-vs-coact`, not on `main`** |
| **line_length +0.052 (*t* 4.5); tube +0.000 (*t* 0.0)** against CoactDetect's 0.645. `tube` is the tuning-inflation control: it ties CoactDetect untuned, so if tuning lifts *it* clear too, the leaders' margins are about budget | measured, two seeds | same readout ⚠ **not on `main`** |
| **gauge is the only learned model that carries to a larger field, and it is the worst of them at home.** On the 566-ROI Cossart spec it scores 0.67 / 0.59 where tube reaches 0.14 / 0.24 and line 0.005 / 0.15 — but on the home spec it scores 0.53 / 0.51 against CoactDetect's 0.65, and on an emptying field it fires 57 to 77 times an hour with nothing planted, where tube and CoactDetect fire less than once | measured, one run per seed | [PR #596](https://github.com/syncytium2/bugarach/pull/596) |
| **gauge still trails CoactDetect on Cossart** by 0.11 to 0.19 F1. Carrying is not winning | measured | same |
| **Every learned model was trained at one learning rate, 1e-2, on purpose**, while CoactDetect was tuned on one knob. That asymmetry is the reason the tuning run exists, and it is why none of the margins above can yet be attributed to architecture | measured from the code | [`tools/fair_bakeoff.py`](../../tools/fair_bakeoff.py) |

### What fails to train, and why it matters

| finding | strength | source |
|---|---|---|
| **`chorus` as first built does not train**: F1 0.125 flat, every fold, both seeds, threshold pinned to the grid floor. Diagnosed — its per-cell encoder **starts deaf**, at any learning rate — and repaired four ways, all of which now train | measured, then repaired | [PR #596](https://github.com/syncytium2/bugarach/pull/596); [`why_chorus.txt`](../learned/field_size_candidates/why_chorus.txt), landed alone because `chorus.py` cites it — the rest of that folder is still on the PR's branch |
| **`trace` and `tiny` show the same signature and were never diagnosed.** Their thresholds pin to the grid floor on three and four folds of four, so "detect everything" beat every stricter setting. The filed todo names those two; chorus makes it three, and chorus is the one that turned out to be a fixable defect rather than a property of the shape | measured | [the todo](../todo/2026-08-28-two-architectures-have-no-operating-point.md) |
| **A model that starts deaf is a bug, not a verdict on the architecture.** That is the general lesson, and it is why a failed-training result now has to be diagnosed before it is reported as a finding about a shape | argued, from the chorus repair | the same readout ⚠ **not on `main`** |

### gauge and chorus stay in the model picker (decided, Tony, 2026-09-22)

They reached it with #680, which landed their code and therefore registered them: the registry is the
picker's only source. That was the question PR #596 had held open — a model in the picker is one a
colleague can run on their own recordings, and these have seen simulation only, with `gauge` firing
freely on an empty field. **Ruled: leave them there**, each carrying its registration note (`gauge`:
*SIMULATION ONLY*; `chorus`: *DOES NOT TRAIN*).

### Where the label-free half stands

| finding | strength | source |
|---|---|---|
| **Four architectures trained with rigid shift as their only negative do not beat random initialisation** at the label-free threshold, reaching 0.34–0.49 F1 against 0.65–0.70 supervised | measured, held | [`MILESTONES.md`](../MILESTONES.md) section C; the goal page is [`unsupervised-learning.md`](unsupervised-learning.md) |

## Tried and dropped — do not re-propose without new evidence

- **`quorum`**, the third architecture in the original proposal. Built and drawn, then dropped from
  the tuning branch: with one field size on the bench its exponent cannot be identified, so the bench
  cannot tell the shape from a constant. It survives only on branch
  `claude/net-design-proposal-hw8rve`. Bringing it back means giving the bench more than one field
  size first.
- **The field-size proposal as written.** Held back and owed a rewrite: it was drafted without knowing
  `line` already existed — one of its three proposed nets largely duplicates it — and it rested on a
  per-cell rate taken as a median of medians, which comes out about six times below the range
  FOUNDATIONS §9 gives for the same quantity. [Todo](../todo/2026-09-16-the-field-size-proposal-must-be-rewritten-around-line.md).
- **Running the tuning in the app.** The 2026-08-28 ruling that the next bake-off would run in the app
  was reversed on 2026-09-16 — *"i believe these big runs need scripting and not in-app"* — on the
  grounds that it had assumed the project was further along than it was.
- **Integer stride shifts for gauge's null.** The first stride was 7 frames, inside the 9-frame
  widening, and left 6.25 % of cell pairs aligned at 32 ROIs. Replaced by irrational phases
  ([PR #596](https://github.com/syncytium2/bugarach/pull/596)).

## Waiting on Tony

Each is a decision, not a task, and nothing below it can be settled by a session.

| decision | why it gates the goal | filed |
|---|---|---|
| **Which models and detectors to keep** (Tony, 2026-09-17: *"we're still troubleshooting and figuring out what models/detectors to keep"*) | Decides what the next comparison, on the bench and against every-knob coded detectors, includes. (The Gate 1 step-3 stop that stood here was ruled on 2026-09-16: a low seed draw, not a defect) | [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) §4; `docs/learned/tuned_vs_coact/gate1/README.md` ⚠ **not on `main`** |
| **Whether [PR #596](https://github.com/syncytium2/bugarach/pull/596)'s run output lands.** Its registration question is ruled (see *gauge and chorus stay in the model picker*); what remains is its results folder and tools | Decides whether the field-size readout is citable from `main` or only from the branch | the PR, deliberately not set to auto-merge |
| **Bake-off promotion**, for `line` and for anything the tuning run returns | [`MILESTONES.md`](../MILESTONES.md) reserves it; the `line` row is `held` | [`MILESTONES.md`](../MILESTONES.md) section C |
| **Whether `trace` and `tiny` get the chorus treatment** — diagnosed as possibly-deaf, or recorded as shapes that cannot learn this task | Decides whether the no-operating-point todo is a bug report or a result | [todo](../todo/2026-08-28-two-architectures-have-no-operating-point.md) |

## Open work a session can do without a ruling

- **Diagnose `trace` and `tiny`** with the probe that caught chorus, before either is written up as an
  architecture that cannot learn. The tool is `tools/probe_untrained_response.py` on branch
  `tune-learned-vs-coact` — the gate a model should pass before anyone spends compute training it.
- **[`model_track.md`](../model_track.md) has fallen behind the family it describes.** It never names
  `line`, `chorus` or `gauge`, and its account of where the model stands is centre−surround.
  [`MILESTONES.md`](../MILESTONES.md) section C is more current. Either bring it up to date or point
  it here.
- **The four tube variants still owe the controlled rate-step test** that would say which of them is
  doing what. [Todo](../todo/2026-08-23-four-variants-of-the-tube.md).
- **`build_tube`'s docstring asserts two guarantees the model does not deliver.**
  [Todo](../todo/2026-08-27-the-model-does-not-do-what-its-docstring-says.md).
- **The bake-off picks a threshold on the recordings it fitted on**, in the bake-off
  ([todo](../todo/2026-08-27-the-threshold-is-picked-on-the-recordings-it-trained-on.md)) and in the
  tube ablation ([todo](../todo/2026-08-28-the-ablation-still-picks-thresholds-on-its-fitting-data.md)).
- **The learned models have never seen a real recording in training**, and a published route for
  fixing that is filed. [Todo](../todo/2026-08-17-pretrain-on-the-six-then-fine-tune.md).
- **The bake-off page transcribes numbers a token could substitute**, and it is stale.
  [Todo](../todo/2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md).

⚠ **Out of scope on Tony's word, 2026-09-16:** Cossart transfer — *"it's ok if the learned detectors
don't automaticly work on cossart. don't get distracted"* — and, for the tuning run specifically, real
recordings, label-free training, new architectures, and any edit to `bench.OPERATING_POINTS`. The
operating points belong to [`coded-detector-optimization.md`](coded-detector-optimization.md).

## Where the work lives

| what | where |
|---|---|
| The route from a new architecture to a number | [`pipelines/learned-model-evaluation.md`](../pipelines/learned-model-evaluation.md) — eight stages, each with its gate |
| The architectures | [`src/bugarach/learn/nets/`](../../src/bugarach/learn/) — the folder is the registry |
| The bake-off | [`tools/fair_bakeoff.py`](../../tools/fair_bakeoff.py) — `--learned`, `--null-rates`, `--skip-hand-written`, `--train-seed` |
| The tuning run's specification, and Tony's decisions of 2026-09-16 | `HANDOFF-workstation-tuning.md` on branch `tune-bench-comparison` ([PR #642](https://github.com/syncytium2/bugarach/pull/642)) ⚠ **not on `main`**. The copy on `tune-learned-vs-coact`, which this row named until 2026-09-20, is the shakedown's and stops 192 lines earlier |
| What the two readouts left open, and why the tool behind them is not on `main` | [the 2026-09-20 handoff](../handoffs/2026-09-20-the-readouts-landed-the-code-behind-them-did-not.md), retired 2026-09-22; its header says where each item went |
| The current scoreboard | `docs/learned/field_size_candidates/README.md` on that branch ⚠ **not on `main`** |
| Gate 1, and the stop | `docs/learned/tuned_vs_coact/gate1/README.md` on that branch ⚠ **not on `main`** |
| The proposal the three new shapes came from, and `quorum` | branch `claude/net-design-proposal-hw8rve` ⚠ **not on `main`**; its tip is an ancestor of `main` but the files were stripped back out before it merged |
| Architecture diagrams | drawn by `syncytium2/draughtsman`; `line` beside `tube` at one scale is its queue item 13 |
| Run outputs | `<darkroom>/bugarach/field-size-candidates/` and `<darkroom>/bugarach/2026-09-16-net-design/` — resolve with `bugarach.paths.darkroom()`. ⚠ Both notes in the net-design folder are partly wrong and the folder has no third note saying so |

## Keeping this page true

- **A result toward this goal updates this page in the same PR.** A decision moves from *Waiting on
  Tony* to *What is settled* with its date. A dropped approach moves to *Tried and dropped* with its
  reason.
- **A session working on this goal says so on its board claim** (`Goal: learned-model-family`) and
  names its branch `nets/<slug>`. Branches stay short-lived and land on `main`; the page, not a
  branch, is what holds the goal together.
- **Every ⚠ branch-only marker above is a debt.** When that branch lands, the marker comes off in the
  same PR. Most of this goal's evidence currently lives where a reader on `main` cannot open it, which
  is the condition this folder exists to end.
