# The ruling queue — every decision waiting on Tony, in one place

**This is the queue, not the content.** Each item says what must be decided, what it is
holding up, where the evidence is, and what this repository would do absent a ruling. The
linked file wins over the summary here, exactly as [`INDEX.md`](INDEX.md) does.

**Why it exists.** When this page was filed on 2026-09-22 there were nine live rulings, spread
across a cover memo, two root handoffs, an open pull request's body and a document in the
darkroom. It grows: a ruling that arises goes here rather than into a tenth place. No session could see
the set, so each one rediscovered a subset and several restarted work that a ruling had
already parked. The two rulings that *were* visible were visible because they use the
mechanized channel: a todo carrying `status: waiting-on-tony`, which the session briefing
prints first and loudly on every machine. This page is what that channel points at, so the
briefing stays one item longer rather than nine — it sits about 8.1 KB against a spill
threshold measured between 8,768 B and 10,186 B (`tools/hook_spill_census.sh`), and nine
items would silence it.

**How it is maintained.** A ruling that is made **leaves this page in the same commit as the
place the work reads it** — a bench constant, a goal page, a contract, a handoff. A page that
accumulates settled items is a page nobody reads twice. The queue entry is
[`todo/2026-09-22-the-decision-queue.md`](todo/2026-09-22-the-decision-queue.md); delete this
file's last item and that todo goes with it.

**Not murderboarded** — working material for sessions in this tree. Every number below names
the file it came from. Nothing here is for an outside reader.

---

## 1. Pinning — CLOSED 2026-09-22, the producer answered

**Answered the same afternoon it was asked**, in
[syncytium2/interface2#1](https://github.com/syncytium2/interface2/issues/1). The geometric test
ran on all three candidates — `tools/check_roi_pinning.m`, pinned pixels against ROI masks and
penumbra rings, 4,000 frames sampled each, read-only on the turbo `complete/main set/` files.
**The frames pin; the ROIs do not.** `20250926_237` shows no pinned frames at all;
`20260629_314` pins in 44 frames and `20260630_325` in one, and in both the flooded patch sits
where **no ROI or penumbra** is, so it cannot reach an extracted trace or this repository's event
table. The known-pinned control fired as expected, 2 of 21 ROIs touched.

**So the group-level scenario does not hold**: mice 68, 82 and 83 are not affected in every
recording at the ROI level, and nothing in the de-pinned export needs to change. The
fast-stream DI result does not depend on those three slices hiding pinned ROIs.

**Their caveat, which they volunteered and which belongs with the conclusion:** the geometric
test undercounts — on the control it caught 2 of the 4 census ROIs, because its mask keeps only
pixels at the frame minimum in more than half the pinned frames. A clean result is therefore not
proof on its own. What carries it is **two tests sharing no code agreeing**: the per-ROI trace
detector and the geometry. They also note 400 samples is too sparse to clear a slice; the table
uses 4,000.

The substance now lives where the work reads it — the note in `current_export.toml` and the row
in [`MILESTONES.md`](MILESTONES.md) — which is why this item is a stub rather than a section.
**Still ours and untouched by this:** group and imaging day are perfectly aliased in this
corpus, which they say plainly they have not checked and which is not theirs to check.

## 1b. The probe basis — is the background axis a raw rate or a coordination-subtracted one?

**ASKED 2026-09-22 23:30 EDT, blocking the adoption PR. WSMIP064 is holding and will not pick.**

**Decide:** whether `REGIMES` quiet/busy and `hot_rate_hz` are all **raw** rates, all
**background** rates (raw minus the coordinated share), or a mixture.

**Why it is open.** The 21:00 ruling recorded in
[#747](https://github.com/syncytium2/bugarach/pull/747) says *"The probe moves to the measured
99th percentile of 5-minute baseline stretches — fast 0.06 → **0.128 Hz**, slow to its measured
value (**about −9%**)"*. Those two examples name **different quantities**, and on slow they point
in opposite directions:

| stream | bench now | raw 99th | background 99th |
|---|---|---|---|
| fast | 0.060 | **0.12781** (+113%) | 0.12708 (+112%) |
| slow | 0.032 | **0.04531** (+42%) | **0.02906** (−9%) |

`0.128` is fast's **raw** value (background 0.127 — a 0.6% difference, immaterial). `−9%` is
slow's **background** value; raw is **+42%**. So slow's probe either rises 42% or falls 9%, and
the two straddle the current 0.032. The `−9%` may have come from WSMIP064's own #743 summary,
which framed slow's probe as background.

**What pulls each way.** The ruling's stated reason — so the methods statement's *"99th
percentile of the baseline frequency"* is true of the bench — argues for **raw**, that statement
being about baseline frequency. But quiet and busy are explicitly going to **background** values,
and a probe that is raw while quiet and busy are background makes the axis **two different
quantities at different points along it**.

**And the size of the whole adoption turns on it.** On the bench's own `shape_usable` set the
**raw** quiet/busy already reproduce `bench.REGIMES` to within 3% (fast −3.0% and +0.2%, slow
+0.6% and +0.3%). The 13–22% quiet/busy change exists **only** on the background reading; go raw
throughout and the adoption is essentially probe-only.

**Evidence:** [`learned/runs/2026-09-23-coordination-rates/`](learned/runs/2026-09-23-coordination-rates/README.md)
(#743), Figure 1 panel B.

**Two flags for whoever writes it up.** Slow's ungated calibration terms are the weakest in that
run (moment rate −22.8%), and slow's probe is the one carrying a 35.9% coordination correction —
so a raw probe sidesteps that weakness rather than resting on it. And #744 puts slow's per-group
correlogram width borderline at p = 0.054 against fast's flat p = 0.71: three runs now say slow
is the stream to be slowest about.

**Recommendation:** pick one quantity and use it end to end. Absent a reason to mix, **background
throughout** is self-consistent and matches the `−9%` actually quoted; if the methods sentence is
the point, say so and take **raw throughout**, accepting that quiet/busy then barely move.

**Sequencing, so nobody waits on the wrong thing:** the adoption is blocked on
[#738](https://github.com/syncytium2/bugarach/pull/738) regardless — it is still a draft — so
there is no time pressure from WSMIP064's side.

## 2. The jitter constant is about three times too loose on both benches

> **RULED 2026-09-22 evening (Tony): adopt the measured values**, fast 0.106 s and slow 0.135 s,
> in both benches, with participation 0.18 → 0.19 in the same pass, and rerun. Being implemented
> overnight — [`HANDOFF-overnight-2026-09-22.md`](../HANDOFF-overnight-2026-09-22.md). This item
> leaves the page in the PR that changes the constants.

**Decide:** whether the measured onset jitter replaces the bench constants, and when the
re-measure and re-search run.

**Blocking:** every tuned number on **both** streams, the slow adoption that has already
happened, and the constants the methods section describes. It also decides whether step C
below has a stable bench to train on.

**Evidence:** [#718](https://github.com/syncytium2/bugarach/pull/718), merged 2026-09-22
(`05769ce`); its run record is `docs/learned/runs/2026-09-22-jitter-correlogram/`.
Read off the half-width of the cross-ROI
onset correlogram at 0.1 s lags rather than from a within-cluster spread: **fast 0.106 s
[0.091, 0.120] and slow 0.135 s [0.126, 0.149], against benches of 0.36 s and 0.30 s**, with
theory giving 0.110 s and 0.138 s. Both old values tracked bin ÷ √12 — bugarach's and the
MATLAB summary's alike. Slow's peak carries a tail one jitter does not make, and a shared
same-frame artefact would read the same way. **The measurement landed; no bench constant moved
with it**, which is what makes this a ruling rather than a change already made.
Related: the slow bench's own 0.30 s already rested on an analogy that step A disproved, where
the MATLAB summary gives 0.46 s for slow and that move alone costs locust −0.098 and
SPIKE-synch −0.082 mean F1 (`docs/learned/runs/2026-09-21-slow-step-a/README.md`).

⚠ **Check one thing before ruling this, added 2026-09-22 on Tony's question — what else did the
simulations absorb, and was it measured carefully?** The jitter is not a lone bad constant.
`tools/remeasure_bench.py` takes `n_roi`, `jitter_sec` **and `participation`** from a single
`assess_coactivity` call at K = 4, and inside it the jitter and the participation come out of
the **same `_clusters(...)` invocation at the same 1.0 s bin**, so both are coupled to that bin
by construction. **Participation was swept and held** — `tools/measure_slow_bench.py`'s `BINS`
docstring records the 2026-09-21 result: the jitter tracks bin ÷ √12 from 0.5 s to 5 s on both
streams while participation stays at fast 0.19 at every bin and slow 0.37–0.38 from 0.5 s to
3 s. So the bench's recruitment constant survives the test its timing constant failed.

Three residuals, none of them a reason to delay the ruling: the quoted flat range **stops at
3 s** where the bins run to 5 s, and at `wm_factor` 1.5 a 5 s bin gathers participants within
±7.5 s of a cluster centre; participation has **no null counterpart** (`jit_obs` at least has
`jit_null` and `jit_excess` — which **the bench does not use**, it absorbed the uncorrected
observation); and the flatness is empirical rather than structural, unlike `rate_shape`, which
predicts the 35% silent-ROI figure it was never fitted to. Full audit, graded by how each
constant was measured:
[`todo/2026-09-22-what-else-came-from-the-clustering-instrument.md`](todo/2026-09-22-what-else-came-from-the-clustering-instrument.md).

**Recommendation:** rule the jitter. The audit that was meant to precede it is done and it came
back clean for participation, so there is nothing left to wait for. Move the constant in one
overnight pass with the 0.19 change, and take the two residuals as follow-ups rather than
blockers: extend the participation sweep to the top of the bin range, and decide whether the
bench should absorb `jit_excess` rather than `jit_obs` now that the distinction is known to
matter. Until it is ruled, every operating point chosen this month stays provisional.

## 3. The nets on the slow bench — run, re-pilot, or drop

**Decide:** whether step C runs at all, and on which bench.

**Blocking:** the last step of the slow-stream job. 064 correctly stopped rather than guessing.

**Evidence:** `docs/handoffs/2026-09-21-slow-bench.md`, step C, and
`docs/learned/runs/2026-09-21-slow-pilot/README.md`. Two untuned nets at three seeds against
the slow reference land everything within **0.827–0.859 mean F1**, the nets 0.016 to 0.032
below CoactDetect, against 0.29 of spread on fast. Fits take 5 to 16 s on the GPU, so a full
slow comparison is hours rather than the fast run's roughly 14 hours — the cost argument is
weaker than it looked, and the bench's own stability is the real question.

**Recommendation:** hold until item 2 is ruled, then re-pilot rather than re-run: a bench where
every detector scores above 0.8 separates nets from coded detectors less well, and the slow
participation of 0.38 is the value the whole slow bench turns on.

## 4. The export contract fireflies proposes

**Decide:** accept the column change, and answer three questions only this repository can
answer.

**Blocking:** fireflies is frozen — it sets no axis ranges from today's widths or amplitudes
until this is agreed.

**Evidence:** `FORMAT_CHANGE_from_fireflies.md` in
`<darkroom>/bugarach/2026-09-21-full-cohort-default/` (fireflies, 2026-09-22). The proposal:
`strength` and `width_sec` go back to the detector's own values; the call measure ships as its
own named columns (`amplitude`, `core_span_sec`, `core_n_roi`, `core_n_events`) in each
`04_detect_<cohort>/detections.csv`; a `measure_version` column is added; their adapter reads
by name with no fallback. On the 09-21 export the values are identical, so this renames columns
rather than re-exporting anything.

The three questions, paraphrased from that document:

1. **Zero width.** 443 calls have `core_span_sec == 0` while `amplitude` computes as though the
   width were one frame — 2 cells at a 0.1 s frame interval gives 20 cells/s. Amplitude says
   "at least one frame" and the width column says zero. Which is the rule?
2. **Missing values.** 609 calls have `amplitude` NA, 326 of them with `core_span_sec` NA too.
   Does NA mean no core, a call too small to measure, or something else?
3. **Which file is canonical** for fireflies to read: the per-cohort `detections.csv` with the
   scored windows in `run.json`, or `detect/calls_measured.csv` with the windows applied by
   them.

**Recommendation:** accept A, B and D as proposed, and adopt the version column **before** the
`core_span_sec` change lands rather than after. On question 3, keep the per-cohort file:
windows are ours, which is their own 2026-09-14 scope stop. Questions 1 and 2 are one line each
from you and I will write the reply.

## 5. Five code defects the methods review found

**Decide:** which are fixed before any of their numbers ship, and in what order.

**Blocking:** every reported number for LoCo, locust and binned SCE on recorded data.

**Evidence:** [`methods/coordination_pipeline_methods_cover_memo.md`](methods/coordination_pipeline_methods_cover_memo.md)
and the morning summary beside it. The methods describe the intended rule; the code does
something else:

| defect | size |
|---|---|
| LoCo and locust count calls whose onset falls outside the analysis window | 212 LoCo calls and 234 locust calls, fast stream |
| Binned SCE measures width and amplitude over the wrong interval | measuring over the whole bin changes 27% of its calls |
| `measure_calls` overwrites the detectors' own cell-count column with its own count | every call |
| locust uses one threshold for a whole recording, baseline and treatments pooled | a treatment that raises the rate also shifts the baseline threshold |
| the stored defaults for CoactDetect and LoCo are still the binned ones | the run's actual settings are committed as `methods/recorded_data_detector_settings.csv` |

**Recommendation:** the first two first — they silently change published numbers. The
cell-count overwrite is also item 4's business, because it is the column fireflies is about to
read by name.

## 6. "Amplitude" keeps its name, or gets a better one

**Decide:** the name, and whether the methods section states the consequence.

**Evidence:** the cover memo. Reviewers asked to rename it in all three rounds, and round 3
found it mostly tracks 1 ÷ width. It is defined as cells ÷ width
(`src/bugarach/call_measure.py`).

**Recommendation:** whichever name you pick, the section should say in one sentence that the
measure is dominated by width — a reader who plots it against width will see that immediately
and conclude it was hidden.

## 7. Two citations nobody here has read

**Decide:** who reads Grün et al. 2002 and Amarasingham et al. 2012, or whether the claim they
support comes out.

**Evidence:** the repository README asks for both for CoactDetect and LoCo; the methods section
ships uncited because nobody in this tree has read them.

**Recommendation:** they go on the literature shelf and someone reads them before the section
reaches an outside reader. An uncited method claim is the kind of thing a referee opens with.

## 8. The tuning branch's fate

**Decide:** whether [#642](https://github.com/syncytium2/bugarach/pull/642) lands, and who adds
its `--bench fast|slow` seam.

**Blocking:** step C in item 3 — the tool is on that draft branch and nowhere else, and without
the seam a slow run trains on fast recordings and stamps them slow.

**Recommendation:** rule item 3 first. If step C is held indefinitely, the branch should still
land for the run it already produced; a tool that exists only on a draft branch is a tool the
next session will rebuild.

## 9. Slow comodulation: the page and the held review round

**Decide:** the round-3 role reports held in the darkroom, and who finishes the page.

**Blocking:** nothing computational — the measurement finished on the de-pinned export and the
numbers barely moved, which is the correct outcome for 83 events out of 264,075 and is itself
worth stating. The page still carries the superseded run's numbers **and a stop notice that is
no longer true**.

**Evidence:** `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, and the held reports in
`<darkroom>/bugarach/2026-09-17-slow-comodulation/round3-roles-held/`.

**Recommendation:** finish it on any machine with the data; it is done work that never shipped,
and a stale stop notice teaches sessions to ignore stop notices.

---

## 10. The combined-stream goal: when it starts, and what shape it takes

**Decide:** whether goal 4 starts before or after the jitter ruling and the slow stream's
last step, and whether a combined stream **replaces** the two passes or sits beside them.

**Blocking:** nothing today — the goal is new and nothing is built. It is here because two of
its three open questions are yours and one is the producer's, and because the order matters:
it would inherit benches that items 2 and 3 are about to move.

**Evidence:** [`goals/combined-stream-coordination.md`](goals/combined-stream-coordination.md),
set by Tony 2026-09-22. Fast and slow are detected one stream at a time today, so an event
recruiting three fast cells and two slow ones is two small calls or none. The concern he
raised with it — that the two streams may draw from **one pool of events** — is real and
half-answered: the export contract settles that only the *width* rule differs between them
and that the detection is methodically identical, but it says nothing about what assigns an
event to a stream or whether one transient can appear in both. **That part is a producer
question**, by the same rule as item 1.

**Recommendation:** ask the producer the membership question in the same message as item 1's
pinning question — they go to the same people and one of them is already overdue. Then run
the one cheap measurement that does not wait on anybody: per ROI, the gap from each slow
onset to the nearest fast onset, against the frame interval. A mass at zero is a shared pool.
Start the build after items 2 and 3, and after the one-stream-aware bench rebuild — a third
copy of the scoring path is the strongest argument yet for that refactor landing first.

## Under check — claims that are not rulings yet

**These are not decisions.** They are things somebody noticed that would change a result if
true, filed here so they are visible beside the rulings rather than in a todo nobody opens. An
item leaves this section when it is confirmed or dismissed — and if confirming it produces a
decision, that decision joins the numbered list above.

- **RESOLVED 2026-09-22 — the detections on the full-cohort rasters are drawn where the file says,
  and no number moves.** Tony saw, by eye, that the marks did not line up with the events or with
  each other. Measured against the run's own files: CoactDetect ran **sliding** there, and its
  onsets sit on member events (median offset 0.00 s). Two detectors *do* float and neither was in
  that figure — **binned SCE** by a median 3.5 s, which is its 10 s bin edge, and **locust** by
  +0.5 s fast and +1.1 s slow, which is peak versus half-rise. What looked like inconsistency
  between the two lanes is **chorus firing where coact does not** (19 calls against 12 on one
  panel); where both fire they agree to a few tenths of a second, sub-pixel at that zoom. The page
  reads correctly once its x-axis is taken as **minutes from senktide onset**, which it does not
  say. Findings, and the three misreadings this cost on the way:
  [`todo/2026-09-22-what-the-full-cohort-rasters-show.md`](todo/2026-09-22-what-the-full-cohort-rasters-show.md).
  Left open there: label the axis origin, distinguish paired from unpaired marks, and decide
  whether the emitted onset should come from the call measure the way width and amplitude already
  do (#698) — which is also what the fireflies contract asks for.

## Already in the queue, listed so this page is the whole of it

- **Two scorers, two winners, and nothing decides between them** —
  [`todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md`](todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md).
  The re-fit cannot start until the elevated-rate test's place in the score is chosen.
- **Run-record naming, four decisions** —
  [`todo/2026-08-31-run-record-naming-decisions.md`](todo/2026-08-31-run-record-naming-decisions.md).
  They amend ADR-0005 and land in a contract two other teams read.
- **Bench participation 0.18 → 0.19**, already scheduled for after the 2026-09-22 meeting —
  [`todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md`](todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md).
  Not a ruling; listed because it moves the same constants as item 2 and the two reruns should
  be scheduled together.

## One vocabulary fix, which is nobody's ruling

**The slow stream and slow comodulation are different things wearing one word**, and the
confusion has now cost a conversation. The **slow stream** is the export's slow event channel —
the detector axis's second stream, what `bench_slow.py` and the whole of `docs/handoffs/2026-09-21-slow-bench.md`
are about. **Slow comodulation** is minute-scale shared modulation, measured on *both* streams,
where "slow" names the timescale of the modulation rather than a channel. [`GLOSSARY.md`](GLOSSARY.md)
should say so in two lines.
