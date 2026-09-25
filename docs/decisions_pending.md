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

**Cleared 2026-09-25, Tony approving:**
- **Items 3 (the nets on the slow bench), 8 (the tuning branch, #642) and 10 (the combined-stream
  goal) were overtaken by [ADR-0010](adr/0010-tune-train-and-review-against-the-data-as-they-are.md)'s
  full-panel night.** It trains every learned family on the slow and combined realistic benches,
  with the `--bench` switch #642 was the only home for, now on `main`. #642 is closed as superseded.
- **"Two scorers, two winners"** was settled by [ADR-0009](adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)
  decision 1: the elevated-rate test is scored on a recording of its own, against its own budget,
  and never enters precision.
- **"Run-record naming"** is not ready for a ruling: its prior-art pass has not been run. It is
  an open todo until it has.

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

## 1b. The probe basis — RULED and ADOPTED 2026-09-22, background end to end

**Tony, ~21:45 EDT: background, end to end.** Quiet, busy and both `hot_rate_hz` probes, on
both streams, are raw minus the coordinated share.

The substance now lives where the work reads it — the two `REGIMES` docstrings and the two
`hot_rate_hz` provenances, which carry the numbers, the recording set and the calibration
caveat — which is why this item is a stub rather than a section.

⚠ **Two findings reversed on the new axis and are listed for Tony** in the run record: no
detector is a steady leader across the whole grid any more, and the fitted-versus-flat
contrast is gone. Both follow from SPIKE-synch's flatness, already ruled a result (#738).

**Why it was asked, and it was worth asking.** The 21:00 ruling
([#747](https://github.com/syncytium2/bugarach/pull/747)) quoted fast's **raw** probe and
slow's **background** one in the same sentence — *"fast 0.06 → 0.128 Hz, slow to its measured
value (about −9%)"*. On fast those differ by 0.6%; on slow they straddle the old 0.032, so its
probe would have risen 42% or fallen 9% depending on which was meant. The orchestrator
confirmed the raw figure was its own relay.

Evidence: [`learned/runs/2026-09-23-coordination-rates/`](learned/runs/2026-09-23-coordination-rates/README.md).

## 2. The jitter constant — RULED 2026-09-22, the benches carry the measurement

**Tony, 2026-09-22 evening: adopt the measured values**, with participation 0.18 → 0.19 in the
same pass. `bench.BENCH_RECORDING["jitter_sec"]` is **0.106 s** and `bench_slow`'s is
**0.135 s**, against 0.36 s and 0.30 s before; both benches were planting events about three
times looser than the recordings they are fitted to. Both re-measures ran on the default folder
and every constant landed inside its interval.

The substance now lives where the work reads it — the two `BENCH_RECORDING` docstrings,
`docs/learned/bench_measured.json` and `bench_measured_slow.json` — which is why this item is a
stub rather than a section. The measurement itself is
`docs/learned/runs/2026-09-22-jitter-correlogram/` ([#718](https://github.com/syncytium2/bugarach/pull/718)).

**Two follow-ups were taken rather than dropped**, neither a blocker: the participation sweep
stops at a 3 s bin where the bins run to 5 s, and the bench absorbs `jit_obs` rather than
`jit_excess` though the distinction is now known to matter —
[`todo/2026-09-22-what-else-came-from-the-clustering-instrument.md`](todo/2026-09-22-what-else-came-from-the-clustering-instrument.md).
**What the ruling does not settle:** the operating points. The re-searches propose settings on
the new bench; adopting any of them is still Tony's, as it was for the slow reference.

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

## 9. Slow comodulation: the page and the held review round — DEFERRED 2026-09-23 by Tony

**Decide:** the round-3 role reports held in the darkroom, and who finishes the page.

**Blocking:** nothing computational — the measurement finished on the de-pinned export and the
numbers barely moved, which is the correct outcome for 83 events out of 264,075 and is itself
worth stating. The page still carries the superseded run's numbers **and a stop notice that is
no longer true**.

**Evidence:** `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, and the held reports in
`<darkroom>/bugarach/2026-09-17-slow-comodulation/round3-roles-held/`.

**Recommendation:** finish it on any machine with the data; it is done work that never shipped,
and a stale stop notice teaches sessions to ignore stop notices.

**Deferred, 2026-09-23 (Tony):** *"keep the co-modulation story in our backpocket for now. flag
for followup as important but off target for today's goals."* The three-stream re-run is #768. For
the scoring design, minute-scale shared change is treated as **background**, a working choice and
not a finding:
[`todo/2026-09-23-minute-scale-shared-change-is-background-for-now.md`](todo/2026-09-23-minute-scale-shared-change-is-background-for-now.md).

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
