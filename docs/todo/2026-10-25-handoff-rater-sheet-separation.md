---
status: done
closed: 2026-10-25
filed: 2026-10-25
---

# Handoff: a separation test on the human rater sheet

**Done 2026-10-25** by the rater-sheet session: [PR #916](https://github.com/syncytium2/bugarach/pull/916) (rows r11–r14, a separation score; pairs record their realized separation as well as the planned one).

**For a new session.** Tony, 2026-10-25: *"add this to the human test sheet. What is the limit of
human detection of separation"*. "This" is the minimum separation of two coordinated events: how
close in time two events can be before people mark them as one. The sheet is
[`tools/rater_sheet/`](../../tools/rater_sheet/README.md) (a synthetic-only Qualtrics pilot, #903),
with its todo [`2026-10-23-the-human-rater-sheet.md`](2026-10-23-the-human-rater-sheet.md).

The sister handoff
[`2026-10-25-handoff-minimum-separation-theory.md`](2026-10-25-handoff-minimum-separation-theory.md)
derives the same limit for the detectors; the human curve and the detector curves are meant to go
on one plot.

**Claim a block on the machine-local board before the first write.** The original rater-sheet
session (`065/rater-sheet`) still holds the darkroom folder
`bugarach/2026-10-23-rater-sheet-pilot/` and is not running. Do not write into that folder: build
into scratch with `make_pilot.py --out`, or claim a new darkroom folder in `docs/SESSIONS.md`.
Synthetic rows only (FOUNDATIONS §5).

## What to add

**Separation rows.**
- **Length and layout:** the same 15-minute rows of 32 ROIs as the pilot.
- **Planted pairs:** each row plants pairs of coordinated events at set separations, Δ = 0.5, 1,
  2, 3, 5 and 8 s (onset to onset).
- **Controls:** single events, so "one where there were two" and "two where there was one" can
  both be scored.
- **Spacing between pairs:** wide enough that the pairs never interact.
- **Conditions:** the pilot's two timings, tight (0.105 s) and wide (0.5 s), on the quiet and busy
  backgrounds (`bench.REGIMES`). Fix participation at one level, say 20 %, so separation is the
  only thing varying.
- **About four rows.** Leave the existing 10 rows unchanged.
- **The generator:** `simulate_coordination` holds events apart (`min_sep_sec`), so plant the pairs
  by hand, or override it for these rows.

**The instruction.** The raters already mark events. These rows need the sentence: *if you see two
events close together, mark both.* Zoom matters here. 0.5 s is a few pixels at full width, so
whether people zoom is part of the result; log zoom depth if the glue allows it.

**Scoring** (`score_export.py`). The pilot's hit rule matches within `bugarach.score.TOL_SEC`
(2.5 s), which cannot resolve a 0.5 s pair. Add a separation score:
- **Per pair:** count the marks inside [first − 2.5 s, second + 2.5 s]. "Resolved" means two marks
  or more, matched one to one by nearest onset.
- **Per single:** a single counts as split if it got two marks or more.
- **Report:** P(resolved) against Δ for each condition, with the split rate on singles as the false
  alarm. Then fit the Δ at which P(resolved) = 0.5, or 0.75 after correcting for the singles' split
  rate.

**The key** records each pair's two onsets and Δ.

**Tests and docs.** Extend `tests/test_rater_sheet.py` (the rows build, the key holds the pairs, the
scorer scores a synthetic export correctly). Add the separation rows to the tool README and the
todo. Rebuild the preview and check it end to end in Chromium, as the pilot was.

## What the answer will be compared with

- **The data's own limit:** two Gaussian onset clouds stop being bimodal below Δ = 2σ. That is
  0.2 s at tight timing and 1 s at wide.
- **The assessor's floor,** about 3 s (1 s bins, merge within 2 bins, gather ±1.5 s).
- **Real event intervals:** the 5th percentile gap is 3.8 s on the fast stream and 7.1 s on the
  slow, and 7.5 % of fast gaps are under 5 s (`learned/runs/2026-09-25-real-intervals/gaps.csv`).

If people resolve pairs the assessor merges, people's marks are the better reference for close
events. If not, the assessor's floor is no worse than human eyes.

## Done when

The separation rows are in the pilot build, the scorer reports the human separation curve, the
tests pass, and the README and todo say how to read the result. Tony runs the survey; the session
does not.
