# Murderboard run — docs/learned/report.html

- upstream:  syncytium2/murderboard @ f43a07b
- vendored:  f43a07b
- freshness: current (`murderboard_freshness.sh --refresh --verbose`, exit 0)
- artifact:  `docs/learned/report.html` (`fa29612` → `43f89d5` → `34e9788` → `5ebfe44`, rebuilt after the last fix)
- roles:     11 of 11 run, **each on two models** (Claude Opus 5 and Claude Sonnet 5)
- rounds:    2 (round 1 on the inherited page; round 2 blind, on the rebuilt page)

Requested as "murderboard the deep learning report with the two models", so every
role ran twice on independent models rather than once. Round 1 fired 22 role-runs
(11 × 2); round 2 fired 16 (all 11 on Opus, plus roles 1, 4, 6, 8 and 10 repeated
on Sonnet, the roles whose round-1 findings had diverged most between models).

**The artifact is the built page**, not its source. `report.src.html` +
`architecture.svg` + the two result JSONs are inputs; `tools/build_learned_report.py`
resolves them into `report.html`, which is what ships and what was reviewed.

---

## What this review actually did

It did not correct a report. It **retracted the report's conclusion three times**,
and the last retraction is the deliverable.

| round | the page claimed | what measurement showed |
|---|---|---|
| inherited | the learned model beats the best hand-written detector, 0.68 to 0.64 | the two numbers came from different background regimes; on a matched regime a hand-written detector won in both |
| after fix 1 | the model leads at the participant floor | measured, it does not — swept, `rate+context` reaches 0.60 floor recall where the model reaches 0.40 at the same precision |
| after fix 2 | the model transfers better than the six | the collapse it was measured against is an artifact of re-calibration; at its shipped setting `rate+context` loses 0.009, not 0.49 |
| now | the model is level with the six on a benchmark too small to separate them, **and the transfer test falsifies its architectural claim** | stated as such |

The final position, in one line: **a 1,149-parameter model specified in a sentence
and trained for five seconds is level with six hand-calibrated detectors, and the
one experiment designed to test what makes it different says it does not work.**
Deploying upward it loses a third of its precision — second-worst of five, where
rate invariance by construction predicted a flat line. That is a real result and a
publishable one; it is not the result the page was written to report.

Each retraction was produced by fixing a defect the previous round found, which is
the process working — but it means **the page has never once survived a round
unchanged**, and that is the single most important thing to carry forward.

---

## Role ledger — round 1 (inherited page, hash `fa29612`)

| # | role | opus | sonnet | outcome |
|---|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 69-row ledger, 4 blocking | 26-row ledger, 2 blocking | both found the regime-basis mismatch and the geometric-ladder contradiction independently |
| 2 | Citation & reference validator — "DOI or Die." | 10 findings, 1 blocking | 2 findings, 1 blocking | **the six are ports of third-party work and the public page credited none of them** (CICADA/Cossart lab MIT, SPIKE-synchronization/Kreuz lab) |
| 3 | Consistency auditor — "Cross-Examiner." | 22 findings, 3 blocking | 7 findings, 2 blocking | isolated **three** counting bases on one page, not two |
| 4 | Adversarial reviewer — "Reviewer 2." | 15 findings, 6 blocking | 8 findings, 2 blocking | the "no precision collapse" null had no power; the participant-floor breakdown existed and was discarded |
| 5 | Line editor — "Kill Your Darlings." | 68 findings, 4 blocking | 15 findings, 2 major | found the initialisation claim contradicted by the table beneath it |
| 6 | Methods / domain expert — "RTFM." | 17 findings, 5 blocking | 3 findings, 2 blocking | **ran the code**: the two regimes do not plant identical events; the two sides were scored under different precision rules |
| 7 | Reuse auditor — "Reinventing the Wheel." | 15 findings, 2 blocking | 2 findings, 1 blocking | the lead figure's three "moments that are not events" are the generator's own planted distractors, unmarked |
| 8 | Naive-reader accessibility — "You Lost Me." | 15 findings, per-section table | per-section table, 6 blocking rows | at 3× zoom the events *are* visible under three of five triangles the caption says are indistinguishable |
| 9 | Density & figure-first — "Show, Don't Tell." | per-section table, 9 findings | per-section table, 9 findings | 63% running text; the argumentative core had no picture in 2,698 px |
| 10 | Build & craft gate — "Ship It." | 21-row table, 13 defects | 21-row table, 6 defects | **no doctype, charset, viewport or lang** — quirks mode, unusable on a phone; learned/hand colours at contrast 1.00 |
| 11 | Argument order — "Start With the Problem." | 9 findings, 1 blocking | 6 findings, 1 blocking | the handoff's own #1 next step (multi-seed) was absent from the page |

## Role ledger — round 2 (blind, rebuilt page)

Blind per the process: the round-2 agents were given the artifact and its sources
and **nothing about round 1** — no finding list, no note of what had been touched.

| # | role | opus | sonnet | what the blind pass caught that round 1 could not |
|---|---|---|---|---|
| 1 | Prove It | 69-row ledger, 2 blocking | 9 findings, 2 blocking | a `{{N:...}}` token resolving cleanly while pointing at the wrong grid index — the new defect class the token system introduced |
| 2 | DOI or Die | — | 2 findings | the page's own tests and figures were uncommitted, so "in PR #52" was not yet true |
| 3 | Cross-Examiner | 25 findings, 4 blocking | — | **I had used the word "silent" for zero-event ROIs, which FOUNDATIONS §9 forbids in terms** |
| 4 | Reviewer 2 | 17 findings, 7 blocking | 10 findings, 3 blocking | **the promiscuity probe is a test that cannot fail** — firings leave numerator and denominator both |
| 5 | Kill Your Darlings | 68 findings, 2 blocking | — | two hand-typed numbers ("half", "0.011") contradicting the tokens beside them |
| 6 | RTFM | 8 findings, 3 blocking | 6 findings, 2 major | **`pick_threshold` still pooled by hand** — I fixed the two tools and missed the picker; and the transfer collapse is a calibration artifact |
| 7 | Reinventing the Wheel | 8 findings, 1 blocking | — | the round-trip recording silently dropped the probe and distractors it claimed to inherit |
| 8 | You Lost Me | 17 findings, 13 blocking rows | 9 findings, 3 blocking rows | overlapping markers rendering as a phantom third symbol; the knob column shipping raw parameter identifiers |
| 9 | Show, Don't Tell | 9 findings, 1 blocking | — | the section the page calls its strongest result had **zero figures** while the section saying "it does not win" had six |
| 10 | Ship It | 13 defects, 1 blocking | 5 defects, 1 blocking | my redrawn schematic clipped its own caption's first letter and struck through two labels |
| 11 | Start With the Problem | 9 findings, 1 blocking | — | the strongest result sits at 61% of page height with no summary above it |

---

## What was fixed

**Code — because the document could not be made true without it.**

- `bugarach.bench.pool_scores` extracted, and `evaluate` rebuilt on it. Both figure
  tools and the transfer tool now pool through one rule. Verified behaviour-preserving:
  `evaluate("rate", "baseline_busy")` reproduces its cached F1 to all digits.
- `learn.train.pick_threshold` now pools the same way. It had been selecting the
  operating point under a metric that counts probe firings and reporting it under
  one that does not — worth 0.08 of F1.
- `tools/regime_shift.py` gained the matched transfer test for the six (calibrate on
  one background, carry the knob over) and calibrates it on **held-out** seeds, so
  both halves of that comparison are chosen off the recordings they are graded on.
- `tools/build_learned_report.py` emits a real document head, and resolves every
  quoted number from the JSONs at build time via `{{N:...}}` tokens. A stale path
  fails the build.
- `tests/test_learn_nets.py` added (11 tests) and a pooling-parity test in
  `tests/test_bench.py`. `nets.py` and `train.py` — the two modules every number
  comes from — previously had no tests while the footer said they did.

**Figures.** Schematic redrawn for the right architecture and its clipping and
label collisions fixed; lead figure extended to include the probe it stopped short
of, with distractors marked and markers separated; participant-floor and
precision-recall figures added; loss figure given its third colour; detector
identity carried by dash pattern because colour carries class; learned/hand colours
separated in luminance; panel letters, axis units, headroom, legend placement.

**Prose.** Third-party attribution restored; parity claim narrowed to its real
scope; the initialisation, footprint, count and ratio errors corrected; the probe's
inability to penalise stated; the interval matching rule stated; the single-seed
caveat extended to every comparison rather than only learned-vs-learned.

---

## ⚠ Residual — this page is not done

1. **⚠ It has never survived a round unchanged.** Round 2 found blocking defects in
   round 1's repairs, several of them mine. A third blind round should be assumed
   to find more, and should be run before this is shown to anyone outside.
2. **⚠ One seed.** Every learned number is a single training run. With 45 planted
   events one event is 0.022 of recall, and the entire spread across the top three
   detectors is half an event. Nothing here is a measured difference.
3. **⚠ The architecture conclusion is not controlled.** The winning model trained at
   ten times the learning rate of the two it is contrasted with, and the project's
   own diagnostic ranks the positive-class weight and batch size as the leading
   untested causes of their failure to descend.
4. **⚠ The probe cannot fail.** Inherited from the bench, not introduced here, but it
   means the page's most severe-looking negative control constrains nothing. Worth a
   `docs/todo/` item against `bench.py` rather than a wording change.
5. **⚠ The transfer table's row selection.** Round 2 found it showed each detector's
   worse direction while the learned model got both. Rewritten against the re-run,
   but the re-run's numbers had not themselves been through a blind pass at the time
   this record was written.
6. **⚠ The bench's background is flat.** The fitted heterogeneous model is documented
   in `bench.py` as not wired in; real recordings leave 35% of ROIs with no events in
   a baseline window against 2% here.
7. **⚠ The generator revision is in flight** and moves the distribution everything
   here is fitted to.
8. **⚠ No citations for centre-surround or dilated convolutions.** Both are named
   techniques from a literature and the page cites neither; `fetch_paper.py` is
   deliberately not vendored in this repo (SAP004), so no citation could be verified
   during this run.
9. **⚠ The "2-second calibrated SCE bin"** claim could not be sourced anywhere in this
   tree; it refers to an upstream campaign this repo does not vendor.

---

## Cross-document corrections made in the same pass

- `docs/SESSIONS.md` — the `learned-detectors-framework` claim still asserted the
  model "does NOT converge" and quoted CoactDetect at 0.66, both superseded; and
  recorded a darkroom copy that never happened because `$BUGARACH_DARKROOM` is unset
  on this machine. Both marked.
- `docs/todo/2026-08-16-learned-detectors-handoff.md` still carries the retracted
  "the regime-shift guard does not reproduce the failure it exists to catch", plus
  four stale numbers. **Not yet corrected — flagged for the next session.**
