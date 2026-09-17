# Murderboard run — the slow shared modulation explainer

## What was at stake

The page exists to answer a question the label-free detector thread had been working around: a model
trained to score a recording above a **rigid shift** of itself is paid for whatever the shift
destroys, and if the recordings hold slow shared change in firing rate that the shift leaves alone,
the models were never graded on it. Getting that wrong in either direction has a cost. Say the slow
change is real when it is an artifact of the measurement, and the next detector is built to chase
it; say it is absent when it is there, and the same failure repeats silently.

Three blind rounds found, between them, that the page was wrong about what its own numbers meant
more often than it was wrong about the numbers. The arithmetic held up: an independent rerun matched
the shipped `summary.json` exactly, and every one of the 39 cells behind Figures 4 and 5 reproduced.
What did not hold were the readings laid over it — a null that did not match its arm, a detrending
step described as a trend test, a cross-dataset comparison whose denominator counted silent cells, a
headline that contradicted its own section, and a central claim that was true by construction and
therefore could not have failed.

**The run ends unconverged.** Round 3 returned blocking findings, the process caps the review at
three rounds, and the fixes made after it — including the one that changed a measurement — are
themselves unreviewed. What follows separates what was reviewed from what was not.

### The finding that changed a number

The arms that delete CoactDetect's episodes were divided by a null that did not share their holes.
Deleting every onset inside an episode cuts gaps **shared across ROIs**; the null circularly shifted
the already-deleted trains, scattering each ROI's gaps to its own phase, so the shared gaps were
scored as shared change. The adversarial reviewer found it, reran the slow stream with its own
correction — shift the full trains, then cut the same episodes — and reported the pooled 1-minute
ratio falling from 2.06 to 1.26, which would have removed the slow stream's result.

That correction is right about the defect and wrong about the fix: it matches the holes but not the
counts. Removal takes onsets where they are dense, while cutting the same windows out of a shifted
train takes them in proportion to time, so the null ends up holding more onsets than the arm and the
ratio is pushed **down**. On a synthetic case built so that what survives removal is independent by
construction — truth 1.00 — that construction reads **0.41**.

The null now shifts each ROI circularly **inside the stretches no episode covers**, which keeps both
its onset count and the shared gaps. On the same known-truth case it reads **1.00**, and the old
mismatched null reads 1.25, confirming the reviewer's direction. On the real data the correction is
small: lab fast **2.42 → 2.37**, lab slow **2.17 → 2.13** at 1-minute bins. Both nulls are kept in
the tool so the difference can be read rather than asserted, and two tests now fail if either
property is lost.

### The claim that could not fail

"A rigid shift leaves change over a minute or more in place" was the page's central consequence, and
a shift of at most *J* cannot move onsets between bins many times wider than *J*. No recording could
have refuted it. It is now marked **argued**, and a new arm supplies the part that can fail: delete
the episodes first, *then* rigid-shift. It leaves 2.52 of 2.56 on the fast stream and 2.39 of 2.55
on the slow — so what survives is not merely events landing in the same bin.

## Header

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  `docs/learned/slow_comodulation/README.md` (first draft 8ba5f57 → `2abe5be` at 369b5ca)
- roles:     11 of 11 run (agents spawned by name, on a fallback grant: 7 of 11 were never issued
  Grep and Glob, and worked around it through Bash)
- reports:   slow-comodulation-2026-09-17-round3-roles/
- rounds ran: all 11 roles in each of the three rounds, and 7 of 11 reported a grant mismatch in
  every round — see the ledger and the calibration line below
- earlier archives: slow-comodulation-2026-09-17-roles/ and
  slow-comodulation-2026-09-17-round2-roles/, 11 of 11 reports each
- ⚠ the round-3 archive holds **10 of 11**: the citation reviewer's report is held out of the tree
  (below), so the roster gate fails on it
- rounds:    3 blind rounds, **not clean at the cap**

### The held report

`check_quotes` refuses the round-3 citation review. It fires on a line that says an author "wrote"
with a quotation beside it — but the quotation is of this page's own opening box, and the words
discussed are Perkel, Gerstein & Moore 1967, published. It is a misfire of a gate that exists for
private correspondence, not a leak. The gate's own instruction is to **ask Tony rather than edit the
check or its exemption list**, and that question has not been put, so the report is not in the tree.
It is intact in the darkroom under `2026-09-17-slow-comodulation/round3-roles-held/`. Consequence,
stated rather than worked around: `murderboard_roster.sh check --require-reports` fails on the
missing role, and a `--no-verify` commit was not used to get past a publication gate.

## Severity by round

| round | blocking | major | medium | minor / low | what it cost |
|---|---|---|---|---|---|
| 1 | 3 | 14 | 9 | 25 | The measurement was rebuilt: zero lag was double-counted, the benchmark generator was described as shoulder-free when its planted block is shared drift, and a cited "91 % of the excess" was an artifact of the lag range. |
| 2 | 2 | 11 | 12 | 26 | The removal arms were given their own null (the version corrected again in round 3), the slow stream moved to the project's calibrated detector point, and the detrended column stopped being read as a trend. |
| 3 | 2 | 12 | 10 | 27 | The null's holes, the by-construction claim, the per-pair denominator, the chance references, and the page's whole argument order. |

Counts are of distinct findings after merging duplicates across roles; the per-role reports carry
the originals.

## Role ledger

Grant lines are quoted from each report's first line. Every role ran in every round.

| role | round 3 grant, verbatim | round 3 findings |
|---|---|---|
| 1 Prove It | GRANT 1 MISMATCH — missing Grep, Glob; holds Read, Bash (no editing tools held) | 14 — reran the whole measurement; `summary.json` matched exactly, 39 of 39 table cells verified; found the four flagged recordings are all DI, and the synthetic-intervals claim false |
| 2 DOI or Die | GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash, WebSearch, WebFetch) | 11 — the Grün 1999 trace is wrong, the variance ratio's origin is Pielou 1972, χ² and Zohary 1994 uncredited, FOUNDATIONS §5 misquoted, the DANDI credit incomplete. **Report held out of the tree, above.** |
| 3 Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 8 — the dip claim holds only at *J* ≥ 10 s; the short answer contradicted its own group section; two measurement bases mixed in one sentence |
| 4 Reviewer 2 | GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only) | 21 — the null's holes (blocking), the timescale the arms cannot isolate, detrending as a trend test, untested group differences, the by-construction claim |
| 5 Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 30 — one quantity under six names, definitions duplicated, the bolded conclusion arriving last, "baseline" meaning three things |
| 6 RTFM | GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 11 — the per-pair denominator counted silent ROIs, detrending calibrated against a stationary world, the leave-five-out weighted by the wrong null, the one-draw chance reference noisy |
| 7 Reinventing the Wheel | GRANT 7 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash) | 9 — the planted-event world still avoided its switched-off probe's time span; four near-copies of existing helpers; CoactDetect reuse verified against the canonical path on 24 recordings |
| 8 You Lost Me | GRANT 8 ok — Read, Grep, Glob | 28 — six terms used before definition in the summary alone; the unsigned log lag axis never explained; episode removal drawn nowhere |
| 9 Show, Don't Tell | GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 12 — the headline had no picture of its own; prose carrying what a panel should |
| 10 Ship It | GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read and Bash) | 12 — y-labels overrunning, an x-label cut off, ▼ carrying three meanings, group colours a pastel pair |
| 11 Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 12 — the page opened with citations rather than the worry, and never said the question had moved from 10–45 s to a minute or more |

**Calibration.** Seven of eleven roles reported a grant mismatch, in every round: Grep and Glob were
not granted, and each role worked around it with `grep` through Bash, so no check was skipped. No
role held an editing tool. The mismatch is a property of this harness, not of the roles.

## What was fixed after round 3 — unreviewed

Every item here postdates the last blind pass:

- the removal null (above), with two new tests and the mismatched null kept for comparison;
- the post-removal rigid-shift arm, in the measurement, in Figure 4 and in the page;
- the with-and-without view of the four producer-flagged recordings, read from the producer's own
  note in `current_export.toml` rather than retyped;
- the per-pair comparison moved to active ROIs and reported as a correlation — which reverses the
  page's earlier cross-dataset reading: per pair the Dard et al. dataset is the **weakest** of the
  three (0.024 against 0.077 and 0.157), not the equal of the lab;
- multi-draw chance references, per-arm Kish sizes and leave-five-out weights;
- Figure 1 rebuilt to show the problem, Figure 2 given an episode-removal panel, Figure 4 given the
  new arm, and the block-control schematic redrawn without a chance alignment of its own;
- the page rewritten in the order role 11 asked for, with the change of question stated at the top.

## Residual ⚠, for Tony

1. **The held report** needs a ruling: is `check_quotes` firing on published words a misfire to be
   recorded, or does the report need rewording before it enters the tree?
2. **Nobody has asked the producer** about shared slow change, or about the four flagged recordings;
   nobody has asked the Dard et al. authors either.
3. **The timescale and the carrier are unresolved.** A 17–25 minute window cannot resolve "a minute
   or more" into a timescale, and the 1-minute ratio counts from lag 0 upward.
4. **The 10–45 s band the rigid-shift report actually asked about is still open** — it is the part a
   rigid shift removes, and this page does not separate it from events the shift spreads.
5. **The intervals are probably a little narrow**: 7.7–17.5 effective mice under the correlogram
   weighting, and percentile bootstraps under-cover at that few clusters.
6. **FOUNDATIONS §5 needs an adjudication.** The committed figures and the per-recording table are
   aggregates of real data; the precedent they rest on is the overnight proposal's, not §5's own
   words, which are stricter than this page's practice.
7. **No group difference is tested**, and group is confounded with imaging day on this export.

## Gates

```
bash tools/murderboard_roster.sh check --require-reports docs/reviews/slow-comodulation-2026-09-17.md
python3 tools/murderboard_agents.py --process docs/doc_review_process.md verify docs/reviews/slow-comodulation-2026-09-17.md
```

Their results are reported in the delivery message, failures included.
