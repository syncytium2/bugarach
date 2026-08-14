# HANDOFF — `docs/generator.md` is mid-review

**Branch:** `rewrite-generator-doc` (pushed). No PR open, deliberately: by the
murderboard's own standard the artifact is not "done" while a blind round is
unclean, and the current version has never been seen by eight of the eleven
roles.

**Read `docs/FOUNDATIONS.md` first.** The SessionStart hook prints its §9; if it
did not fire, read the file. A session that skipped it spent a day building on
the assumption that TTX silences the field, which this project's data refutes.

---

## Your first action

Run the **full eleven roles** against `docs/generator.md` as it now stands:

```
/murderboard docs/generator.md
```

or by hand per `docs/doc_review_process.md` if the skill is unavailable.

**Run all eleven. Do not select a subset.** That is the mistake that made the
last two blind rounds useless: I ran only roles 1, 3 and 10 (claims, consistency,
craft), so both rounds came back as lists of numbers — and a verbless fragment
sat in the opening sentence through both of them. The process says it outright:
*"what scales to stakes is how you run them, never which ones you run."*

The document has been substantially rewritten since the eleven last ran, and the
cold open — a real-vs-generated comparison figure — has never been reviewed by
any role.

### Then

Update `docs/reviews/generator_2026-08-14.md` (the run record) with the round,
and re-gate:

```
bash tools/murderboard_roster.sh check docs/reviews/generator_2026-08-14.md
```

It currently passes at 11 of 11. Keep it passing.

---

## What is in flight

`docs/generator.md` documents `bugarach.simulate`'s coordination generator. Over
this session it was recalibrated three times — invented values → measured values
→ baseline-only regimes — and rewritten once against an eleven-role review.

**Committed and green on this branch:** 344 tests pass, sapper clear, all ten
figures regenerate, every reference resolves.

### The finding that matters most

Leading with real data (Tony's instruction) surfaced the largest gap, and it is
not a parameter:

| | real slice | generated |
|---|---|---|
| spread of per-ROI rates (CV) | 2.04 | 0.24 |
| busiest ROI's share of all events | 28.1% | 4.4% |
| clumping in time (CV per minute) | 0.78 | 0.25 |

The generator draws homogeneous Poisson at one rate per ROI; a real field is
clumpy in both ROI and time. Every detector counts *distinct ROIs coactive*, so
this changes the effective population and the circular-shift null. LoCo finds 5
coordinated events in the real recording and 10 in the generated one — **the
synthetic is the easier problem.** Filed:
`docs/todo/2026-08-14-generator-background-model-is-flat.md`.

---

## Residual ⚠ — decisions for Tony, not for a session

1. **`jitter_sec = 0.36 s` is calibrated to a near-null statistic.** Its own
   circular-shift surrogate null is 0.42 s; the source marks it "flagged-soft";
   and it does not round-trip (build at 0.36, re-measure ~0.64). `span_med` /
   `width_med` are not null-dominated and are the obvious candidates. **Needs a
   decision on what tightness should be calibrated to.**
2. **`bg_rate_hz` is a background rate; the measured value is a total rate.**
   Realized totals are 3.0× nominal in the quiet regime — so the regime named for
   baseline's p25 is busier than baseline's median. Correcting it means solving
   for the background that makes the realized total match, which moves every
   number again.
3. **The background-model gap above.** Fixing it is a recalibration, not a tweak.
4. **The bench has never been scored against a real recording.**

---

## Open todos created this session

- `2026-08-14-generator-background-model-is-flat.md` — the finding above
- `2026-08-14-generator-doc-numbers-are-transcribed.md` — ~60 quantities are
  hand-copied from a bench that keeps moving; three review passes produced three
  different tallies of the same sweep. **The cheap fix is a test that re-derives
  every quoted number**, turning drift into a red test instead of a review
  finding. Probably worth doing *before* the next murderboard round, since it
  removes a whole class of findings.
- `2026-08-13-hookspath-is-opt-in-per-clone.md` — commit gates are per-clone
- `2026-08-13-sap005-cannot-see-past-one-line.md` (sapper_feedback) — SAP005
  cannot check a doctype-first HTML literal

---

## Machine-local state you may need

- `BUGARACH_DATA_ROOT` — real stores. Set it to reach the archived slices:
  `export BUGARACH_DATA_ROOT=~/Dropbox-UniversityofMichigan/"Richard DeFazio"/data`
  The reality-check figure needs it; everything else runs without it.
- `BUGARACH_DARKROOM` — must point at `<darkroom>/bugarach`, **not** the darkroom
  root. Pointing it at the root scatters output into other projects' folders.
- interface2 checkout at `~/Developer/interface2`; global foundations at
  `~/Developer/foundations` (PR #5 open there, unmerged — the coordination-under-
  treatment section).

## Verify the branch is sound

```
.venv/bin/python -m pytest -q                      # 344 passed, 1 skipped
.venv/bin/python tools/sapper.py --all             # clear
bash tools/murderboard_roster.sh check docs/reviews/generator_2026-08-14.md
.venv/bin/python tools/make_generator_figures.py --out docs/generator
```

Delete this file when `docs/generator.md` lands.
