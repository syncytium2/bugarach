# Murderboard run — the rigid-shift look note and its six figures

## The problem this run was for

The rigid-shift look is an exploratory note, `docs/learned/rigid_shift_look/README.md`, with six
figures. It asks whether rigid shift can serve as the negative class for a label-free
coordinated-event detector. Rigid shift moves each ROI's whole onset train by one random offset
within ±*J*. To serve, it has to pass three tests:
- **Hide:** a classifier that cannot see coordination cannot tell the shifted copy from the real
  recording.
- **Remove:** it destroys planted coordination.
- **Keep counts:** occupied frames are unchanged.

The note went to Tony and onto `main` without review. Tony saw the legend laid over the
uniform-dither bars in Figure 1 and asked whether the report and figures had been murderboarded.
They had not. This run is that review, done late: the note was already public.

## What was found

**The note's conclusions do not survive as written, and edits cannot repair them. Two instruments
need new measurements first.** Two blocking findings were each found independently by more than
one role.

**The rising "leak" at large displacements is probably not a leak** (Reviewer 2, RTFM). The leak
classifier sees per-ROI statistics pooled over ROIs: spread, minimum and maximum. These respond
when ROIs that rise and fall together within a 60 s window are shifted apart. The classifier is
therefore not blind to cross-ROI structure once *J* is a sizeable share of the window. The
decisive check, run by RTFM on the real recordings, shifts every ROI of a recording by **one
shared offset**. That moves each ROI's drift in time exactly as rigid shift does, but keeps all
cross-ROI structure (3 surrogate draws × 3 fold seeds per cell):

| cell | independent offset per ROI (rigid shift) | one offset shared by all ROIs |
|---|---|---|
| slow stream, 44.8 s | 0.558 (shipped run 0.563) | 0.502 |
| slow stream, 22.4 s | 0.539 (shipped run 0.549) | 0.502 |
| Cossart, 40 s | 0.589 (shipped run 0.604) | 0.517 |
| Cossart, 10 s | 0.560 (shipped run 0.581) | 0.500 |
| fast stream, 40 s | 0.506 | 0.510 |

- **What the check rules out:** drift moved in time is not what the classifier detects. It
  detects that shared co-modulation within ±*J* was removed.
- **What rests on the wrong reading:**
  - the note's "slow drift moved in time" explanation;
  - its narrow slow window;
  - "Cossart only near 5 s";
  - "larger shifts leak".
- **The fast stream is unaffected** (0.506 against 0.510).
- **Synthetic twins agree:** Reviewer 2's check reads planted 0.80 against unplanted 0.45 at
  44.8 s, lab-sized.

**The Cossart destruction result could not have failed** (Reviewer 2, RTFM, Prove It,
Cross-Examiner). An event in 283 ROIs spread over ±*J* puts about 283/(2*J*) ROIs in each 1 s bin.
That is below K = 55 ROIs for every *J* of 2.6 s or more, so every such cell had to read 0, and
did. The Cossart events that matter are smaller still: `learned/cossart_transfer` measured about
28 of 566 ROIs per event (8.1 %), and Cossart's coactivity excess peaks at K = 12 ROIs. Both are
below every K this run scanned. The pre-registration's graded control, `freeze_half`, was not run.

**The remaining findings, found by several roles each:**
- **Uncredited data.** The Cossart data are DANDI:000219 (Dard, Picardo & Cossart), licensed
  CC-BY-4.0, from Dard et al. 2022, *eLife* 11:e78116 (DOI or Die, blocking). The note showed
  derived figures publicly with no credit.
- **Answer and decisions omit Cossart.** The Cossart result never reached the note's answer or
  its decisions (Start With the Problem, blocking).
- **The slow window crosses its own line.** The recommended window at 11.2 s has an upper bound
  of 0.551 over mice, which crosses 0.55. The same crossing is flagged for Cossart and not here
  (five roles).
- **The slow leak is not "almost entirely" in DI.** MALE reads 0.593 at 44.8 s (0.557–0.633),
  and group cannot be separated from imaging day (five roles).
- **Two withdrawn claims were repeated.**
  - The screen's review said the destruction measure could not register removal on Cossart; the
    blind pre-registration round corrected that.
  - The note says K of 3–8 counts chance coincidences on Cossart; the 2026-08-29 transfer handoff
    measured otherwise.
- **The count test cannot see how rigid shift loses onsets.** It drops onsets pushed past the
  ends of the recording, which the interior windows exclude by construction. A 20-minute
  synthetic recording loses 2.07 % at 44.8 s (Reviewer 2).
- **Wrong preparation.** The Cossart recordings are in vivo imaging of awake pups, P5–P12, not
  slices (DOI or Die).
- **Uncredited prior art.** Rigid shift is published as whole-train shifting (Pipa, Riehle & Grün
  2007; Pipa et al. 2008; Louis, Borgelt & Grün 2010). The published form wraps, and this run
  does not.
- **The figures:**
  - The fix that drew controls on top now hides four of five rigid-shift lines on Cossart.
  - Displacement is distinguished only by dash pattern in a 7 pt legend.
  - The reference lines are unlabelled, the panels unlettered, and the leak y-limits unshared.
  - Points where planted participants are fewer than K are plotted as if meaningful.
- **Darkroom delivery was broken.** The Cossart outputs and the updated note were copied to a
  doubled path, `<darkroom>/bugarach/bugarach/…`. The folder Tony opens still holds the old note
  and the pre-fix figures (Reinventing the Wheel, Prove It).

## What was done

- **A correction banner** opens the note. It names the two readings that do not hold, the
  corrected numbers, the dataset credit and the published lineage. The goal page line that
  repeats the note's claims carries a matching flag.
- **Nothing else** in the note was rewritten. Its conclusions wait on new measurements, and a
  rewrite before them would send a blind round to review conclusions nobody yet knows.

**The banner is itself unreviewed.** It is an edit made after round 1, and no blind pass has read
it.

## What would validate a rewrite

1. **Leak:** the shared-offset control beside every leak cell, on both folders.
2. **Removal on Cossart:** destruction at Cossart's measured participation (about 8 % of ROIs)
   and at K near 12 ROIs, plus the graded `freeze_half` control.
3. **Counts:** the whole-recording dropped share of onsets at each *J*.
4. **The note itself:** a rewrite on those results, then a blind round.

These are new runs, and whether to spend them is Tony's decision.

## How this generalises

A classifier is only blind to the structure a surrogate removes if its features cannot see that
structure. Removing the edge-band features after the pre-registration's blind round fixed one path.
Pooled spread over ROIs is another, and the only way to find these paths is a control that keeps
coordination while moving everything else. A leak test without that control cannot tell "the
surrogate leaks" from "the surrogate works".

---

## Appendix — run header and role ledger

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/rigid_shift_look/README.md (3fc1f4d9089d35e0a11ce48840a273a12f33c4c7 -> 00a2e9ed1be72dd2c93baad281a0d5bad9ba979d, the correction banner only; figures unchanged at 616f124)
- roles:     11 of 11 run (fallback grants: spawned by name, 7 of 11 declared MISMATCH on Grep and Glob)
- reports:   rigid-shift-look-2026-09-15-roles/
- rounds:    1 of the process's 3 — unconverged; stopped after round 1 and escalated, because the blocking findings need new measurements, not edits

Mode: standard

The artifact is the note and the six PNGs it embeds, as built at commit 616f124 on
`unsup/rigid-shift-look-figures`. The generator, `tools/make_rigid_shift_look_figure.py`, and the
runner, `tools/look_rigid_shift.py`, were reviewed under RTFM and Reinventing the Wheel.

The role reports were extracted verbatim from each reviewer's transcript as it arrived, before
synthesis. Machine-local absolute paths were then replaced with `<worktree>`, `<scratchpad>` and
`<darkroom>` placeholders (sapper SAP004; the repository is public), and nothing else changed. The
archive name has no underscore because `murderboard_roster.sh` strips underscores from the
`reports:` path.

**Grants.** Seven roles declared MISMATCH because they did not hold Grep and Glob: Prove It, DOI or
Die, Reviewer 2, RTFM, Reinventing the Wheel, Show Don't Tell and Ship It. Each searched with `grep`
and `find` through Bash instead. No role held an editing tool, and no role reports touching the
repository. Several wrote intermediates to the scratchpad.

**Stopping reason.** After round 1, escalated to Tony. The blocking findings concern what the leak
and destruction instruments can see, and they are answered by new runs, not edits. This is not a
converged run and must not be read as one.

**Calibration.** This review found defects and fixed none of the note's conclusions. It is not a
correctness proof. A clean run would measure how quickly reviewers stopped finding things, not
whether anything remains.

**Findings by severity, round 1** (raw counts as graded by each role, before deduplication):

| role | blocking | major | minor |
|---|---|---|---|
| 1 · Prove It | 0 | 7 | 10 |
| 2 · DOI or Die | 1 | 4 | 11 |
| 3 · Cross-Examiner | 0 | 7 | 15 |
| 4 · Reviewer 2 | 2 | 8 | 5 |
| 5 · Kill Your Darlings | 0 | 7 | 24 |
| 6 · RTFM | 1 | 2 | 6 |
| 7 · Reinventing the Wheel | 0 | 1 | 10 |
| 8 · You Lost Me | 6 (four of them blocking by the three-undefined-terms count) | 11 | 8 |
| 9 · Show, Don't Tell | 0 | 6 | 2 |
| 10 · Ship It | 0 | 7 | 8 |
| 11 · Start With the Problem | 1 | 4 | 5 |

### Role ledger

**1 · Prove It** — GRANT 1 MISMATCH — missing Grep, Glob; holds Read, Bash (no forbidden editing tools)
Recomputed every number from the run outputs; nearly all match. Wrong: DI "almost entirely" (DI supplies 49–56 % of the above-chance answers, MALE 23–38 %); the 11.2 s slow upper bound crosses 0.55; two withdrawn claims repeated (Cossart destruction could not register; K 3–8 counts chance coincidences); stale scope, dates, branch pointer; darkroom copy old and at a doubled path. Minor: 84–100 % not 84–99 %, 5.6 s not 5 s, −4.8 % fast control, 31.5 ROI median, 10 Cossart twins, no Cossart leak table.

**2 · DOI or Die** — GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)
Blocking: DANDI:000219 (Dard, Picardo & Cossart; CC-BY-4.0; Dard et al. 2022) used without credit. Major: Cossart recordings are in vivo pups, not slices; rigid shift's lineage (Pipa, Riehle & Grün 2007 → Pipa 2008 → Louis 2010 → Stella 2022) uncredited, and the published form wraps; "the second review" cited while its finding on interior windows is omitted; the withdrawn Cossart destruction claim. Minor: interface2 commit f76e7b1b is private; Dard 2022 already used per-cell circular shifts on these data; dither, count, classifier test and resample lack citations; 59 of 62 sessions; DeepCINAC inference; movement epochs as a nonstationarity. Residual ⚠: nobody asked Grün's, Pipa's or Dard's groups.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Counts, K scaling and most values consistent. Major: slow value 0.60 is at 5.6 s; the 11.2 s crossing is flagged on Cossart but not slow; DI and MALE both leak; absolute K contradicts the glossary's percentage K; no Cossart leak table; Cossart events measured at 8.1 % (≈28 ROIs), below the smallest scaled K; goal page stale. Minor: 84–99 % basis, −4.6 % vs −4.8 %, dashed vs shaded band, interval widths, slice vs recording, stream name, occupied frames vs onsets, *J* wording, new terms missing from the glossary, group order, 31 vs 32 ROIs, unlinked references, stale header, Cossart window source.

**4 · Reviewer 2** — GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)
Blocking: the leak classifier's pooled count features see coordination under rigid shift once *J* is a sizeable share of the window (synthetic: planted 0.80 vs unplanted 0.45 at 44.8 s); Cossart destruction at *J* ≥ 5 s cannot fail at K ≥ 55. Major: the count test cannot see end-of-recording drops (2.07 % at 44.8 s); the destruction headline follows from K ≥ 3 and one-frame events; points with participants below K; slow 11.2 s crossing; the group story is untested and partly contradicted; pooled across design groups; baseline-only scope missing from the answer; dither has no power against rigid shift's failure modes. Minor: 60 s window unjustified, 1.67–98.33 % basis, bar definitions, figure titles, jitter source.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
`murderboard_prose.sh` is not vendored and the role has no shell, so the house banned-construction list was run by Grep: no hits except one em-dash in the title (not a pivot) and one "not only" that carries content. Major: header scope false; "narrow" hedges that no slow displacement clears both lines; slow displacements misnamed; DI, MALE, ORX, OVX undefined; ordinal references ("the second review") unlinked; "hide" undefined; the Cossart reading's caveat follows its conclusion. 24 minor line edits.

**6 · RTFM** — GRANT 6 MISMATCH — missing Grep, Glob; holds none (no Edit, Write or NotebookEdit)
Blocking: pooled cross-ROI statistics detect removed shared co-modulation; the shared-offset control on the real data reads chance (table above), so the large-*J* "leak" on slow and Cossart is not drift. Major: DI and MALE both above chance at 44.8 s; controls at 0 and 1 do not show Cossart destruction can register partial removal. Minor: points below K; intervals sit about 0.01 below the point and the point depends on fold seed; 95 % bars misdescribed; unstated settings; 84–99 % and 5.6 s; count statistic differs from the pre-registered one. Sound: the wrapper is an exact rigid shift, interior windows avoid edge loss, edge-thinning tiles align, the feature mask works, mouse grouping holds.

**7 · Reinventing the Wheel** — GRANT 7 MISMATCH — missing Grep, Glob; holds Read, Bash and no forbidden tools
Major: neither tool defaults to `darkroom()`, and the Cossart outputs landed at a doubled darkroom path while the real folder kept a stale note and pre-fix figures. Minor: a third copy of the forced-choice scorer without the drift assertion; `excess`, `destruction_task`, `k_scan`, twin sizing and window tiling duplicate production code, each with a named difference (bin width, missing `freeze_half`, rounding and a switch at 62 ROIs, `or 1` instead of a refusal, a lost guard); the visibility floor is `before > 0`, not the signed 1.0; thresholds are hardcoded, and 1.67 % stayed frozen for 4 and 5 displacements; the baseline guard uses a string prefix; the leak runs skip the real-against-real negative control.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
Blocking: the purpose (a surrogate negative class for a detector) is never stated; group codes undefined; occupied frames and the edge-thinning control undefined; leak and destruction bullets each introduce three or more undefined terms; the limitations section likewise. Major: no schematic of rigid shift against dither; the mechanism behind the destruction curves comes after all four figures that need it; the DI finding has no figure; the 0.55, ±2 % and 0.25 lines unexplained; slow displacements unexplained; K scaling rule unstated against the glossary; "events" reads as a quantity; 10 s and 40 s line styles indistinguishable. Minor: the control reads as a fourth displacement; dodged bars; Cossart citation; wording.

**9 · Show, Don't Tell** — GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash)
Major: the answer has no figure (proposes a trade-off grid of leak and retained share against *J* with the passing band shaded); the per-group claim has no figure; the K-scaling argument is arithmetic about a picture; the displacement trend is split across two figure pairs; destruction figures run along K while captions read along *J*; no methods schematic. Minor: the legend strip takes 19 % of each destruction figure; leak panels give the space to the dither reference. Prose is right for provenance, limits and decisions.

**10 · Ship It** — GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)
All six PNGs are current and reproduce pixel for pixel; no overlap or clipping remains. Major: the controls now drawn on top hide four of five Cossart rigid-shift lines, and the caption says the reverse; *J* shown only by dash pattern, with 20 s and 40 s identical; 7 pt legend displays near 7.6 px; the 0.25 line is unlabelled and shares a dash style with a *J*; the 0.5, 0.55, 0 and ±2 % marks are not in the legend; leak y-limits are not shared; no panel letters. Minor: Cossart dither bars hidden behind markers; empty K = 146 slot; 10 not 20 Cossart twins; band vs dashed; no unit on "displacement J"; fraction vs percent; tick crowding; two control glyphs.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
Spine reduced to one claim per section; judged against problem → cost → method → what it gets wrong → fix → evidence → residual risk, with answer-first allowed. Blocking: the Cossart result never reaches the answer or the decisions, though it decides viable against narrowed. Major: the scope line is contradicted halfway down; the K-scaling limit arrives after the result it limits; the best-case caveat never meets the 84–99 % headline; the cold open is process, not the problem. Minor: half the reason for the follow-up; mechanism before context; method detail before the figures; sections follow the order of work; decisions do not say what each answer unlocks.
