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

## 1. Pinning — ASKED 2026-09-22, waiting on the producer

**The ask is sent**, on Tony's instruction, as
[syncytium2/interface2#1](https://github.com/syncytium2/interface2/issues/1) — the geometric
check (`tools/check_roi_pinning.m`, pinned pixels against ROI masks) on `20250926_237`,
`20260629_314` and `20260630_325`, and nothing else. It carries our answers to the three
questions their 2026-09-18 note asked, including the two that are ours to own: nothing here
reads their pinning manifest, and our earlier leave-one-out was quoted as an estimate of the
artifact's share when it is only an upper bound. **Sent as a GitHub issue rather than a
darkroom note** — their first since the migration — so the thread has a public, permanent
address either side can cite.

**Nothing is owed by this repository until they answer.** What is left here is the decision
below, if their answer turns out to need one.

**Rewritten 2026-09-22, and the rewrite is the point.** Tony asked whether this had been
checked before. **It has — three separate ways — and the answer has been in the darkroom
since 2026-09-18.** What was wrong was this repository's copy of it.

**Decide, once they answer:** whether the residual risk needs anything held.

**What was already done, so nobody screens it a fourth time:**

| when | who | what |
|---|---|---|
| 2026-09-02 | interface2 | a blind whole-frame scan, knowing nothing about the ROI census, ranking `20250926_237`, `20260629_314` and `20260630_325` beside the four known pinned slices |
| by 2026-09-18 | interface2 | the per-ROI trace-derivative detector over **all 85 archive slices** — 14 ROIs across 6 slices flagged, 12 across 4 strong |
| 2026-09-18 | Tony | the trace panels by eye, one per pinned ROI, raw fluorescence against the frame minimum, `20260630_325` among them |
| 2026-09-17/18 | bugarach | the whole rigid-shift chain re-run on the de-pinned export; every conclusion survived (`ba6f90c`) |

**What the producer actually said**, in the same-day correction inside
`<darkroom>/bugarach/2026-09-18-pinned-rois-answer/README.md`: all three candidates were
inside the 85-slice sweep. `20260630_325` came back **marginal** and is in the census (ROI 10,
3.6 s). `20250926_237` and `20260629_314` came back with **no ROI flagged**. Their note
corrects an earlier sentence of their own that said the detector had not been run on them.

**Why this repository kept saying otherwise.** The correction never reached
`current_export.toml`, and everything downstream re-derives from that note: the cover memo,
the round-3 review's finding 3, this item as first written. The round-**2** review caught it
(`reviews/coordination-pipeline-methods-2026-09-22-roles-r2/01-prove-it.md`, F3) and said the
producer should fix the pointer; nobody did, so round 3 read the pointer and restated the
withdrawn claim. All the live copies are corrected as of this change; the verbatim morning
summary and the review records keep their text, because they are the record of what was
believed when.

**What is genuinely open, and it is narrow: sensitivity, not coverage.** The census tests
manually selected hROIs only, so a flooded patch holding no hROI leaves it silent while the
frame is still corrupted — exactly what a whole-frame scan sees and it cannot. `20260629_314`
is the most exposed case at 14 ROIs, the fewest of any DI slice. The settling test is
geometric — pinned pixels against ROI masks, interface2's `tools/check_roi_pinning.m` — and
**that** has not been run on these three.

**Recommendation, as sent:** the geometric test on those three slices and nothing else. The
producer's own reading is that the residual cuts in our favour, because a whole-frame artifact
where no ROI sits cannot reach our event table at all. Do **not** arm the contamination stop
for this: the folder addresses what was found, and the open part is a sensitivity limit rather
than a declared contamination the data do not mark. Three of the ten DI mice would be affected
in every recording if the candidates are real, which is why it was worth asking at all.

**What went back with it**, four days late and now sent. Their question about the re-run is
answered by the rigid-shift chain above and by the by-group figures (DI slow 1.82 pooled, 1.76
[1.20, 2.50] per slice, against the 1.49 the leave-one-out predicted). Their question about the
manifest has the answer nobody had sent: **nothing in this tree reads
`moco_pinned_excluded.tsv`** — the only manifest reader, `tools/make_group_raster_summary.py`,
names the field-step files — and the manifest is still the right shape, because the windows are
what a null would mask across. Their question about the shared gaps is answered honestly as
untested, with the observation that **the gap outlives the fix**: clipping removes the events
and leaves a stretch shared across ROIs, so a whole-trace circular shift can still manufacture
or destroy coincidence at the offset. That last one is now open work here, not a question for
them.

⚠ **One thing shipped ahead of its own page.** The by-group numbers went to the producer while
`docs/learned/slow_comodulation/README.md` still shows the superseded run (item 9). The issue
says so and tells them to cite it rather than the page — but the page is now the thing that
disagrees with what another team has been told, which moves item 9 up.

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

⚠ **Check one thing before ruling this, added 2026-09-22 on Tony's question — what else did the
simulations absorb, and was it measured carefully?** The jitter is not a lone bad constant.
`tools/remeasure_bench.py` takes `n_roi`, `jitter_sec` **and `participation`** from a single
`assess_coactivity` call at K = 4, and inside it the jitter and the participation come out of
the **same `_clusters(...)` invocation at the same 1.0 s bin**. A wider bin sweeps more distinct
ROIs into a cluster, so participation is mechanically bin-dependent in the way the jitter turned
out to be — and it has never been swept. It is also the constant with the most riding on it:
064's own finding is that **slow participation, 0.38, is the value the whole slow bench turns
on**, and 0.18 → 0.19 is already queued for fast. Two further asymmetries: the instrument
computes `jit_null` and `jit_excess` and **the bench absorbed the uncorrected `jit_obs`**; and
participation has **no null counterpart at all** to check against. The sweep machinery exists —
`tools/measure_slow_bench.py` already carries `BINS = (0.5, 1.0, 2.0, 3.0, 5.0)`, which is how
the jitter was caught, while `remeasure_bench.py` is still single-bin. Full audit of every
constant the bench absorbs, graded by how it was measured:
[`todo/2026-09-22-what-else-came-from-the-clustering-instrument.md`](todo/2026-09-22-what-else-came-from-the-clustering-instrument.md).

**Recommendation:** sweep participation across those bins first — it is minutes on a machine
with the data — then rule the jitter and move both constants in the same overnight pass as the
0.19 change, since all three move the same bench. Adopting a corrected jitter while leaving an
uncorrected participation fixes half a bench and leaves the half with more riding on it. Until
it is ruled, treat every operating point chosen this month as provisional — that is the honest
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

## Under check — claims that are not rulings yet

**These are not decisions.** They are things somebody noticed that would change a result if
true, filed here so they are visible beside the rulings rather than in a todo nobody opens. An
item leaves this section when it is confirmed or dismissed — and if confirming it produces a
decision, that decision joins the numbered list above.

- **CoactDetect's event times are bin edges, so they cannot line up with chorus or with the
  data** (Tony, 2026-09-22, by eye). A mechanism that produces exactly that is in the code:
  `coact.py:278` takes a call's onset from the **left edge of its bin**, quantised to the shipped
  `int_win_sec` of 2.0 s, while the nets decode at frame resolution and the data are event
  onsets. `emit.py` writes that bin-edge onset into `detections.csv`, which is what the rasters,
  the figures and fireflies read. ⚠ **It does not automatically invalidate goal 2** — scoring
  matches within a tolerance, and a tolerance wider than a bin absorbs the offset, which would
  explain why F1 never showed it. Check that first. Full write-up, what to measure, and the fix
  that is already half-built by #698:
  [`todo/2026-09-22-coactdetect-onsets-are-bin-edges.md`](todo/2026-09-22-coactdetect-onsets-are-bin-edges.md).
  **Needs a real recording**, so it belongs on 064 or 065.

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
