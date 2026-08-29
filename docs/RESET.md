# The reset — what bugarach is, what it may say, and what it must not say yet

> **This is the lead document.** Tony stopped the work on 2026-08-24 and reset it. Where
> this page contradicts a planning note, a todo or a commit message, **this page wins**;
> where it contradicts [`FOUNDATIONS.md`](FOUNDATIONS.md), the sections it would amend are
> named in the last part and folding them in is Tony's call, not a session's.
>
> It exists because the project's understanding of its own central instrument changed, and
> because a reader could otherwise assemble a confident and wrong picture from a large
> backlog of todos written before that change.
>
> **How this page stays true, since two status documents in this repo have already gone
> stale while looking current.** It holds **decisions and constraints**, which age slowly,
> and deliberately holds **no counts of open pull requests, worktrees or claims** — those
> were wrong within the hour it took to draft this, and the commands that produce them are
> named in part 9 instead. Vocabulary is in [`GLOSSARY.md`](GLOSSARY.md); this page defines
> only the handful of terms its own argument turns on.
>
> **Operationally blocking as of the reset: CI failed on every pull request**, and `main`
> would go red on the next merge. Diagnosis in part 9. ✅ **Fixed since — and fixed the way
> part 9 prescribed**: `tests/test_site_dates.py` now reads the stamp date from the viewer
> page's own history rather than from `HEAD`. Pull requests have been going green since;
> #375 passed 3/3 on 2026-08-28.

> **Landed 2026-08-28, four days after it was written, unchanged in argument.** This page sat
> on an unproposed branch while every session reconstructed its part 7 from `HANDOFF.md`'s
> table. What was corrected on the way in: the CI banner above and its twin in part 9, both
> now false; the status of part 7 steps 0–2, which have since been done; and #270, which has
> merged. **Nothing in parts 1–6, 8 or 10 was touched** — those are the decisions, and they
> are the reason the page exists.

---

## 1 · The decision that forced the reset

Tony, 2026-08-24:

> *"The assessor should be machine and human working together to find coordination.
> There's no ground truth and I shouldn't have allowed the idea of an independent
> assessor."*

Everything below follows from taking that seriously.

**There is no autonomous assessor.** The instrument is a person and a program together. A
coordination number produced without anybody having looked at the recording is not a weaker
result of the same kind — it is not a result. The August plan for a human review surface
was scoped as *"a feature to add at some stage"*; that scoping is withdrawn.

**There is no ground truth about a real recording.** The phrase remains correct for
**planted** events in a simulation, where it means *known by construction* — `simulate.py`
and `score.py` use it properly. It is not available for anything the assessor, a detector,
or a person says about tissue.

**Three consequences that are not stylistic.**

- An assessment is a **record containing a judgement**, not a number with a caveat beside
  it. **K** — the number of ROIs that must be co-active before a moment counts as
  coordinated — is a convention, not a measurement, and it moves the headline by an order of
  magnitude across the range the assessor scans. Today the CLI correctly refuses to choose
  it — *"K is a scan, not a choice … nothing here has turned a measurement into a setting —
  that needs somebody who has looked at the recording"* — and the browser holds *"the K a
  person accepted"* in a variable that dies with the tab. Neither writes the decision down.
- **The view is part of the judgement.** A human call is a property of
  (recording × rendering × observer), not of the recording. If a person's look is
  constitutive rather than confirmatory, the rendering they looked at belongs in the record.
  The browser currently lets a caller rescale time continuously without recording where
  they were.
- **The obvious validation test is circular and must not be written as written.** Asking
  the assessor to recover planted events is the convention agreeing with itself, because
  the simulation is parameterised from the assessor. What survives is the **null**: plant
  nothing, and the excess must read zero. A rate-matched null that leaks is a defect in the
  arithmetic whatever convention sits on top, and every generator spec derived afterwards
  inherits it.

**What this does not touch.** The machine half is still held to 1e-9 against
`measure_coordination_timescale.m`; parity is faithfulness of arithmetic and does not
depend on who reads the output. And the assessor still does the job it was introduced for
— it stops the benchmark being a restatement of whichever detector measured it. It simply
is not an oracle while doing it.

---

## 2 · What the product is

Tony's own statement of the loop, 2026-08-24, with the three places reality differs marked:

> *"The user shares a folder with a series of recordings. They want to quantify
> coordination and whether it changes with a treatment. They give the times of treatments
> and the analysis windows.* ⚠¹ *The app assesses their recordings to establish parameters
> for a simulated data set with ground truth.* ⚠² *After user evaluation of the simulated
> data to ensure it bears resemblance to their data, the app optimizes six detectors and
> trains tube variants.* ⚠³ *The optimized/trained detectors are then tested on another
> batch of simulated data and compared quantitatively on their performance. Then the user
> runs the detectors on the original data set and hits publish."* ⚠⁴

**⚠¹ The treatment times are the producer's, not the user's.** They arrive in the folder as
region labels and the app never learns which one is the drug — `emit.py` keeps *"No
privileged region and no protocol vocabulary."* The **analysis windows** are the user's.
Both halves are right; they come from different places.

**⚠² Not ground truth — parameters.** Per part 1.

**⚠³ Tube variants do not exist.** There is one tube, trained only under `bugarach lab`.

**⚠⁴ There is no publish, and the question in the first sentence is never answered.**
The app writes `detections.csv` and `run.json` and stops. **No function anywhere in `src/`
puts two regions side by side** — no contrast, no ratio, no paired statistic. The user
opens the table in something else and does the science by hand. The loop as drawn ends one
analysis short of the question it opens with.

---

## 3 · What is actually built

| stage | in the browser | in Python |
|---|---|---|
| open a folder, check it conforms | ✅ | ✅ `bugarach check` |
| draw the rasters, windows, ROI ordering | ✅ | ✅ `bugarach.ui.app` |
| assess coordination without a detector | ✅ parity-tested against the Python | ✅ `bugarach assess` |
| simulate a folder from that assessment | ✅ writes a conforming folder | ✅ `simulate.py` + `adapt.py` |
| put the simulation's statistics beside the real folder's | ✅ | ⚠️ split across `tools/` |
| optimise the six, folds and pooled scoring | ✅ all six | ✅ `tools/fair_bakeoff.py` |
| train the tube | ⚠️ only under `bugarach lab` | ✅ `learn.train` (PyTorch) |
| compare every detector on one split | ⚠️ built, hidden, copy unreviewed | ✅ `docs/learned/bakeoff.json` |
| detect over the real folder and write files | ✅ | ✅ `bugarach detect` |
| **compare two regions** | ❌ | ❌ |
| **record the human's judgement** | ❌ | ❌ |

The suite is green — 1,181 passed, 2 skipped — and that number says nothing about the two
❌ rows, because nothing tests what does not exist.

---

## 4 · What may be said, and what may not

**May be said.** Six MATLAB detectors are ported and match their originals to 1e-9 on
committed fixtures. A lab can open a folder, measure coordination without choosing a
detector, generate a matched simulation, tune against planted events, and detect — in a
browser, with no install and no upload. That is the deliverable and it substantially works.

**May not be said, each for a recorded reason.**

- **That any detector is right about a real slice.** Everything measured is simulated and
  no real slice has an answer key. This is the sentence that must survive every rewrite.
- **That the tube leads.** The tube is the learned detector — a centre-minus-surround
  filter, 1,149 parameters, the only model here that is trained rather than configured. It
  **ties**: 0.668 ± 0.061 against CoactDetect's 0.651 ± 0.044, four folds, **one training
  run per fold and no seed replication anywhere**. What it demonstrably wins on is cost —
  5.6 s to fit, 0.014 s to scan a fold. It also transfers worse than two of the six from a
  quiet background to a busy one, which is a negative result about its own central claim.
  ⚠ **And both numbers were computed at a calibration that has since been superseded** —
  see part 5. They are the best published figures and they are not current ones.
- **That the comparison reaches the state of the art.** It contains **no published learned
  method** and **none of the assembly-detection family**. SPIKE-synch's profile (Kreuz
  lab) is published and locust derives from published work — but locust is a modified
  partial port whose numbers are its own, not CICADA's (`detector_history.md` §6.3), so
  **no published method runs here in its authors' form.** The accurate claim is narrower
  than the first version of it and wider than the second.
- **SPIKE-synch's 0.254 is not its accuracy.** Its swept knob is not binding — `C_min` sits
  pinned above most of the grid and the profile is quantised — so on a default simulation
  every value on the grid returns the same result. It is the score of a sweep that could
  not choose. **Correcting this is a published-table fix and does not wait for any
  campaign.**

---

## 5 · What is stale, and it does not look stale

**Everything in `docs/learned/` was computed before the difficulty axis was corrected.**
`bench.REGIMES` moved on 2026-08-20 (0.0038 → 0.0052 quiet, 0.0175 → 0.0190 busy) and
locust's FAST percentile was retuned in the same change. Nothing has been regenerated. The
figures render identically; only the numbers underneath moved. **Nothing will fail, and
somebody will quote them.**

**The bake-off's data set was measured off the `.mat` store, not the approved folder.**
`generator_spec.json` records `"store": "event_store_onset_revised_2v_alive_rescued"` and an
IQR of [0.0037, 0.0185] — the superseded axis, from the source the export-folder rule
closed. The assessment behind it, `assessment_real.json`, carries `background: null`: it
predates the shape fitter, so re-deriving from it today falls back to a reference constant.

**So the first step of any re-fit is not code.** It is a fresh `assess` over the approved
export folder, and a person choosing K — which `derive_spec` requires explicitly, and which
part 1 now makes constitutive rather than procedural.

**Regenerate in one pass.** A half-regenerated `docs/learned/` mixes two calibrations with
nothing saying which is which, and is worse than a consistently stale one. The README table
and the site's report come last, because they are what a stranger reads.

---

## 6 · Three confounds that bind any result

**The detectors are steeply background-sensitive and nothing reports it.** On the same 120
events, CoactDetect recalls **0.817** at the quiet endpoint and **0.560** at the busy one —
**0.26** of recall, **0.32** at the measured real participation, across a 3.7-fold rate
change that is only the interquartile spread of *untreated* slices. Operating points are
chosen at one point on that axis and quoted as though they held across it. For scale:
crowding costs 0.144, the best mechanism change measured buys 0.050, and the guard buys
nothing. ⚠ Those three come from **different runs on different recordings** and are not
strictly commensurable — the ordering is indicative, not a tested comparison. What is not
in doubt is that background sensitivity is the largest of them and the only one nothing
reports.

**Changing the background's shape reorders the detectors outright**, and this one is
already drawn — [`docs/learned/two_decisions.png`](learned/two_decisions.png), panels A
and B:

![Panel A, a histogram of per-ROI background rate: the bench's flat field is a single red spike at 5.2 mHz with no silent ROIs, against the fitted field's long blue tail with 34% of ROIs silent and a median of 1.1 mHz. Panel B, every detector's F1 at its shipped operating point under both fields, joined by a line: binned SCE 0.155 to 0.107, locust 0.296 to 0.265, SPIKE-synch 0.367 to 0.500, rate+context 0.636 to 0.547, LoCo 0.674 to 0.703, CoactDetect 0.703 to 0.736 — every score moves and they move in both directions](learned/two_decisions.png)

Panel A is the difference: the real recordings leave **35% of ROIs silent** across 81
baseline windows and 2,643 ROIs, and the bench's flat field leaves **none**. Panel B is
what it costs — every score moves, in both directions, and `rate+context` and `SPIKE-synch`
close from 0.269 apart to **0.047**. Shape is not a bigger version of level, and the
reassurance from the endpoint move does not transfer to it.

⚠ **Panel C of that same figure carries a claim the project has already withdrawn** — that
the ranking is unchanged from 0.4 s to 2.0 s. True of the archived sweep, **not** true at
the shipped operating points, where two detectors swap between 0.4 s and 0.5 s. Cite A and
B; do not cite C until the figure is regenerated.

**Therefore the treatment contrast, once built, measures two things at once.** The
simulation is parameterised from **baseline** — by rule, and the rule is right. The
detectors are optimised against it and then run across treatment windows whose background
differs. A change in detections is a change in coordination **plus** a change in the
instrument's sensitivity, with nothing separating them. This is not hypothetical: under TTX
coordination splits by stream, FAST at 0.46 of its own baseline and SLOW at 2.50 with 44%
of slices at or above it. **A result running in opposite directions in two streams is
exactly the shape a sensitivity artifact could manufacture, and exactly the shape it could
hide.**

The instrument for all three is the same, it is already proven on a different variable, and
the case for it is [`revise the bench recording before the re-fit`](todo/2026-08-23-revise-the-bench-recording-before-the-refit.md):
the matching tolerance used to be a hidden constant and is now a **curve**, with
`describe_curve` refusing a bare F1 when the score still depends on the axis. Do that to
the background. Then a contrast can report coordination here, coordination there, and how
much of the difference the detector's own sensitivity accounts for.

**Build the contrast on the assessor before the detectors.** Its null is a per-ROI circular
shift that holds each ROI's own rate and burstiness, so it is the one rate-controlled
instrument in the stack. Safer, not immune: its excess is an absolute per-minute magnitude
and whether two windows at different rates yield comparable excesses is established
nowhere.

---

## 7 · What the reset changes about the order of work

The previous plan was **mechanism → benchmark → calibration**, and that ordering is still
right: re-fitting a detector whose mechanism is wrong bakes the defect into the new
operating point at full price. The reset inserts a step in front of it.

**Status as of 2026-08-28**, added when this page landed — the steps, not the argument:

0. ✅ **The assessor becomes a pair.** The screen that shows the scan, takes the decision, and
   **records the decision and the view beside the data set it produced.** Nothing
   downstream is reproducible until this exists, because today the one input everything
   derives from is a number a person agreed to in a tab that has since closed.
   *Landed 2026-08-24; #270, which carries the decision, merged 2026-08-28.*
1. ✅ **The null test.** Plant nothing, expect zero. *It leaked; corrected in #303.*
2. ✅ **The background axis becomes a reported curve**, not a point. *Nothing is flat.*
3. ⛔ **Fresh assessment of the approved folder, and a K decision**, which unblocks a re-derived
   generator spec. *Tony's.*
4. **Mechanism, behind flags defaulting to current behaviour** — parity is the product, so
   every mechanism change lands as a named alternative and never as a redefinition —
   [`forks.md`](forks.md) records each such choice and how to go back. Four tube candidates
   are written up with the evidence for each in
   [`the four variants`](todo/2026-08-23-four-variants-of-the-tube.md): the
   ratio-of-Gaussians is the only one with positive evidence anywhere, the guard is
   unsupported rather than refuted, and a censored surround is the prescribed remedy nobody
   has run.
5. **Then the re-fit**, then the regeneration of everything that quotes an operating point,
   in one pass. ⚠ *Two things stand in front of it that are not steps 3 and 4. The scoring
   question — how the promiscuity probe enters the score — is under measurement rather than
   open: `bench.py` has kept the probe out of F1 and gated on it at selection since
   2026-08-22, which is the third form
   [the todo](todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md) names. And
   **no tool in this repo runs a campaign** — `bench.sweep()` builds a curve and
   `pick_operating_point()` chooses on one, but the walk over every detector × regime is
   still `optimize_detectors.m` in interface2
   ([port it](todo/2026-08-12-port-coordination-benchmark.md)).*
6. **Then the contrast** — [`the question nothing computes`](todo/2026-08-23-the-treatment-contrast-is-the-question-nothing-computes.md)
   — and only then does the loop answer the question it opens with.

---

## 8 · Decisions only Tony can make

1. **Does this document get folded into `FOUNDATIONS.md`?** It would amend §1 (the two
   deliverables do not mention the assessor, which parts 1 and 6 make load-bearing) and §2
   (parity is the product — still true, and now explicitly a claim about the *machine half*).
   Nothing here edits FOUNDATIONS; a session should not.
2. **Is the assessor decision an ADR?** It reverses a premise and constrains vocabulary
   repo-wide. It is currently recorded in
   [`the human-in-the-loop todo`](todo/2026-08-16-assessment-needs-a-human-in-the-loop.md)
   because that is where the subject already lived.
3. **K, on the approved folder** — the fresh assessment is blocked on it, and everything
   downstream is blocked on that.
4. **Are mechanism changes in scope, or only settings?** Settings-only makes the campaign
   smaller and guarantees it repeats.
5. **The publish step.** Export, report, or figure — it has no referent today.
6. **Multi-seed training**, which is real compute and is the only way the tie at the top
   becomes a measurement rather than a coin.

---

## 9 · What was in flight when the work stopped

**No counts here, deliberately** — every one I wrote while drafting this was wrong by the
time I checked it, because other sessions were still landing work. Read the state, do not
quote it from this page:

```bash
gh pr list --state open                                    # what is open
grep -c 'Status:\*\* ACTIVE' ../bugarach-worktrees/SESSIONS.md   # who is working
git worktree list                                          # where
grep -l 'status: open' docs/todo/*.md | wc -l              # the backlog
```

The durable parts: **PR #270** carries the assessor decision and was blocked by the CI
failure below, not by review — *it merged on 2026-08-28*. **#53** and **#50** are proposals
aimed at other teams rather than webapp work, and both are still open. The todo backlog is
large and **most of it was written before part 1** — read it in that light rather than as a
queue.

**CI was broken for every pull request, and `main` would go red on the next merge.** ✅
*Fixed since, as prescribed here.* `test_the_stamp_prefix_is_the_one_the_viewer_page_writes_by_hand`
compared the viewer page's hand-written date stamp against `_stamp_dates(HEAD)`; on a pull
request, HEAD is GitHub's ephemeral merge commit, dated *now*. The page said one day, CI
computed another. The fix was one line — read the date from the page's own history
(`git log -1 --format=%cs -- docs/site/raster_viewer.html`) rather than from HEAD, which is
also what the commit that last touched this claimed to be doing. It was left unfixed at the
stop because `tools/build_site.py` and `tests/test_site_dates.py` were claimed by a session
that was still ACTIVE. `tests/test_site_dates.py` now reads the page's own history, and pull
requests have been going green since.

---

## 10 · Vocabulary, so the reset is not undone by a word

- **Ground truth** — planted events in a simulation, and nothing else.
- **The assessor** — a person and a program. Never "the assessment says", always with the
  judgement and the view attached.
- **The bench** is three different things and they must be named apart: the **hardcoded**
  recording in `bench.py` that the probes run on and that reads no external file; the
  **spec-derived** data set the bake-off and the tube were fitted on; and the **user's**
  simulated folder the browser generates live. Only the third is derived from anybody's
  folder.
- **Detections, not events.** The app may say *these are the detections*; it may not say
  *these are the events*.
