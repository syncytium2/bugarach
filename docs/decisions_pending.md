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

## 1. Pinning is not closed for three analyzed recordings

**Decide:** whether this is a known contamination, which by your own rule stops the work and
goes to the producer the same day — and, if it is, whether the pointer's note is amended so
`dataset.refuse_if_contaminated()` arms for it.

**Blocking:** every number measured on the default folder, including the methods section that
landed yesterday and the full-cohort run. The stop is **not** armed today: the note for
`steps_and_pins_excluded` says the folder *addresses* its contamination, and these three sit
in the residual paragraph below that sentence, so analyses keep running over them right now.

**Evidence:** `current_export.toml`, the `steps_and_pins_excluded` note — `20260702_338`
(1 ROI, 13 exceeding frames) and `20260630_325` (1 ROI, 10) sit below the census cut of 100
exceeding frames, against 515 to 2,195 frames for the four that were cleaned; `20260629_314`
is absent from the census altogether and the pinning detector has never been run over it, with
an interface2 todo from 2026-09-02 ranking it beside the known four on a blind whole-frame
scan. The producer's 2026-09-18 answer lists `20250926_237` and `20260630_325` as candidates
under open challenge. All three are in the 67 first-treatment recordings, all three are
diestrus females, and each is the second recording of a mouse that already has a pinned one —
[`reviews/coordination-pipeline-methods-2026-09-22-roles-r3/01-prove-it.md`](reviews/coordination-pipeline-methods-2026-09-22-roles-r3/01-prove-it.md),
finding 3.

**Recommendation:** ask the producer today. It is one message, the rule has no exception for
"probably small", and this is now the fourth review to raise it. Two of the three are already
in the producer's own open review, so the question is narrow: has `20260629_314` been screened,
and what is the verdict on the other two.

## 2. The jitter constant is about three times too loose on both benches

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

**Recommendation:** rule the number, then run fast and slow together in one overnight pass with
the participation change in item 11, since all three move the same constants. Until it is
ruled, treat every operating point chosen this month as provisional — that is the honest
statement, and it is cheaper to say now than to withdraw later.

## 3. The nets on the slow bench — run, re-pilot, or drop

**Decide:** whether step C runs at all, and on which bench.

**Blocking:** the last step of the slow-stream job. 064 correctly stopped rather than guessing.

**Evidence:** `HANDOFF-slow-bench.md`, step C, and
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
the detector axis's second stream, what `bench_slow.py` and the whole of `HANDOFF-slow-bench.md`
are about. **Slow comodulation** is minute-scale shared modulation, measured on *both* streams,
where "slow" names the timescale of the modulation rather than a channel. [`GLOSSARY.md`](GLOSSARY.md)
should say so in two lines.
