# HANDOFF — slow shared modulation, re-measured on the producer's de-pinned export

**State: the measurement is done and the page is not.** The overnight run finished; the
explainer still carries the superseded run's numbers and a stop notice that is no longer
true. Everything needed to finish is below; nothing needs re-running.

Filed 2026-09-17, late. Branch `unsup/pins-excluded-run` (this file lands with it).

---

## What changed today, in one paragraph

The producer answered the question about the moco floor-pinned ROIs by shipping a new
export, `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, which removes every event
inside a pinned window and ships a manifest. That cleared the contamination stop for the new
folder, the measurement was re-run on it overnight, and **the numbers barely moved** — which
is the correct outcome for 83 events out of 264,075, and is itself worth stating on the page.

## Where everything is

| what | where |
|---|---|
| the run | `<darkroom>/bugarach/2026-09-17-slow-comodulation-pins-excluded/` — `results.json`, `summary.json`, six figures, `one_recording.png` |
| the superseded run | `<darkroom>/bugarach/2026-09-17-slow-comodulation/` — keep it; the page's current text belongs to it |
| the page | `docs/learned/slow_comodulation/README.md` — **still the old run**, with a stop notice at the top |
| the figures in the repo | **deliberately still the old run's**, so page and figures agree. The new ones are in the darkroom |
| the murderboard record | `docs/reviews/slow-comodulation-2026-09-17.md` — describes the old run, three blind rounds, delivered unconverged |
| the held role report | `<darkroom>/bugarach/2026-09-17-slow-comodulation/round3-roles-held/` — waits on Tony |

Reproduce: `python tools/measure_slow_comodulation.py --jobs 12 --draws 32 --boot 4000`,
then `python tools/make_slow_comodulation_figure.py --run <that folder> --also
docs/learned/slow_comodulation`. The run took 686 s on a free machine.

## The numbers to write the page from

Pooled 1-minute count-variance ratio, 95 % interval over mice, then after removing a
straight line. **Contaminated run → de-pinned run**, so the reader can see what the
producer's change did:

| dataset, arm | contaminated | de-pinned |
|---|---|---|
| lab fast, as recorded | 3.21 | **3.14** [2.42, 3.94] · 2.42 |
| lab fast, episodes removed + block control | 2.37 | **2.36** [1.83, 2.93] · 1.65 |
| lab fast, episodes removed + rigid shift *J* 20 s | 2.52 | **2.50** [1.92, 3.09] · 1.79 |
| lab slow, as recorded | 11.37 | **11.79** [7.89, 15.51] · 7.42 |
| lab slow, episodes removed + block control | 2.13 | **2.11** [1.55, 2.76] · 1.38 |
| lab slow, episodes removed + rigid shift *J* 20 s | 2.39 | **2.36** [1.75, 3.07] · 1.67 |
| Dard et al., as recorded | 15.23 | **15.12** [12.24, 18.04] · 13.11 |

Per recording, after removal and the block control: fast median 1.26, above 1 in 71 %; slow
median 1.22, above 1 in 62 %.

**The Dard et al. folder is byte-identical between the two runs** — only the draw count
changed, 8 → 32. It moved 15.23 → 15.12, **0.7 %**. That is the surrogate-draw noise floor
measured rather than guessed, and it closes a murderboard residual that had estimated ~5 %
from a reseed. Quote it: differences under about 1 % are not readable.

## The group result, which is what Tony asked for next

**Slices are effectively independent here, so use them as the unit.** Measured on the
per-recording ratio after removal and the block control: ICC between mice **0.018** (fast)
and **0.000** (slow), design effect 1.02 and 1.00, so 84 slices are worth ~83 and ~84.
Resampling mice and resampling slices give the same interval (fast [1.45, 2.05] against
[1.44, 2.04]). Tony asked why slices could not be treated as independent; the answer is that
they can, and the earlier mouse-only framing was more cautious than the data warrant.

Per-slice ratio after removal and the block control, slices as independent units:

| group | fast | slow |
|---|---|---|
| **DI** (17 slices, 10 mice) | **2.47** [1.79, 3.24] | 1.76 [1.20, 2.50] |
| MALE (22, 12) | 1.71 [1.23, 2.30] | **2.46** [1.37, 3.87] |
| ORX (25, 12) | 1.23 [1.05, 1.46] | 1.38 [1.10, 1.71] |
| OVX (20, 10) | 1.70 [1.10, 2.62] | 1.32 [1.09, 1.58] |

**DI − rest, fast stream: +0.95 [+0.19, +1.81], excluding zero.** Slow: +0.04
[−0.71, +0.86], nowhere near it. Pooled (pair-weighted) by group, de-pinned, for the same
arm: fast DI 2.67, MALE 1.96, ORX 1.65, OVX 2.62; slow DI 1.82, MALE 2.92, ORX 1.89,
OVX 1.50.

⚠ **The day confound is untouched by any of this.** 84 recordings, 48 imaging dates, no date
holding more than one group, so group and imaging day are perfectly aliased. A tighter
interval is an interval around (group + day). More slices cannot separate them; only a day
holding two groups can. Every group figure needs that sentence beside it.

## Two lessons from today that belong in the page, not just here

- **A leave-them-out is an upper bound on an artifact's contribution, not an estimate.**
  Dropping the four contaminated recordings predicted DI's slow figure would fall to 1.49.
  Actually de-pinning them — removing 83 events and keeping the rest of those recordings —
  gives **1.82**. The page quoted the leave-out as though it estimated the artifact's share;
  it does not, and the same caution applies to the heaviest-five checks.
- **DI's height survives the real removal.** Fast 2.73 → 2.67, its 5–30 s shoulder unchanged
  at +0.108 against +0.040 to +0.053 for the other three groups. So the contamination was
  never what produced the group ordering — which is a stronger statement than the page's
  current "trust the by-group reading least", and should replace it.

## What is left to do, in order

1. **Rewrite the page on the de-pinned numbers.** Replace the stop notice with what actually
   happened: the folder declared a contamination, work stopped, the producer removed it, the
   run was repeated, and the numbers moved by less than a percent. That sequence is the most
   useful thing the page now records.
2. **Rebuild the group section** on slices as the unit, with the intervals above and the DI
   contrast, and the day confound stated beside it.
3. **Copy the new figures into the repo** (`--also docs/learned/slow_comodulation`) *in the
   same commit as the new text*. They were deliberately left at the old run's version so the
   page and its figures never disagree on `main`.
4. **Update `summary.json` beside the page** from the new run, and the goal-page pointer
   (`docs/goals/unsupervised-learning.md`), which also carries a stop notice.
5. **Decide whether this needs a fresh murderboard.** The last one ended unconverged at the
   round cap; the numbers have changed by under 1 % but the argument has changed more.
6. **Release the board claims** — `docs/SESSIONS.md` (darkroom, ACTIVE) and the machine-local
   board — when the page lands.

## Decisions waiting on Tony

1. **The held role report.** `check_quotes` refuses the round-3 citation review because it
   quotes published words (Perkel 1967) beside a line saying an author "wrote". A misfire,
   not a leak, but the check says ask rather than edit it or its exemption list. It sits in
   the darkroom under `round3-roles-held/`, and `murderboard_roster.sh --require-reports`
   fails until it is resolved.
2. **FOUNDATIONS §5.** The committed figures and the per-recording table are aggregates of
   real data, resting on the overnight proposal's precedent rather than §5's own stricter
   words.
3. **`bench.MEASURED_ROLE` still points at the contaminated folder.** The simulator's
   background shapes and rates are fitted to data containing the pinned ROIs — 0.03 % of
   events, so the effect is small, but "small" is the argument we agreed not to accept alone.
   Moving it is a decision like moving `default`, and it turns the suite red until the bench
   is re-measured. Untouched.
4. **The decision the page sets up**, unchanged: is shared change over a minute or more
   coordination, background to subtract, or the producer's to explain?

## Traps a fresh session will otherwise walk into

- **`dataset.current("steps_excluded")` refuses**, on purpose. That folder is still
  contaminated. New analysis reads `steps_and_pins_excluded`. The override is
  `BUGARACH_ACK_CONTAMINATION='<why this analysis is unaffected>'` and it echoes the reason.
- **Do not recognise the lab folder by its role name.** Three tools did; when the role name
  changed today, two crashed and one guard — the refusal of non-baseline windows — went
  silent. Ask the folder what it has. Filed:
  `docs/todo/2026-09-17-tools-that-name-the-lab-folder-instead-of-asking-it.md`, which names
  the one instance still standing (`build_surrogate_report.py:1991`).
- **`tests/test_build_surrogate_screen.py::test_a_worker_past_its_cap_is_killed_and_recorded`
  fails on `main` locally**, both parametrizations, on a clean tree. Pre-existing, not from
  today's work, unfixed.
- **`elephant==1.2.1` was installed into the primary checkout's `.venv` today** by the
  neighbouring session — the pin `pyproject.toml` has declared since 2026-09-11, which that
  venv predated.
- **The primary checkout is not always on `main`.** Another session works in it on its own
  branch; check before assuming, and do not `git pull` it out from under them.

## The other session

`Mac unsupervised` is running the rigid-shift chain overnight from a pinned checkout, and is
holding branch `use-the-steps-and-pins-export` until this branch's pointer lands, because its
defaults name the `steps_and_pins_excluded` role. Its first result: the per-ROI classifier
still reads rigid shift as chance on the de-pinned folder (0.489–0.506, against 0.486–0.505
before), so de-pinning opened no per-ROI leak. Two independent measures agreeing that the
producer's change did what it claimed and nothing more.
