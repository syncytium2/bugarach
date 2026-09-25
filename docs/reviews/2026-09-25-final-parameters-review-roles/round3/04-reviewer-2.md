GRANT 4 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback, which is the harness hand-off tool, not an editing tool. I hold no Edit, Write or NotebookEdit.)

# Reviewer 2 (adversarial), blind round 3: the final-parameters night report

**Artifact:** `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md` at 0638de5. I also reviewed its four PNGs (opened and read as images), `adoption.json` and `adoption_table.md`.

**Sources I checked against:**
- `<darkroom>/bugarach/2026-09-25-final-parameters/065/report-inputs/real_data.md`
- `.../064/phase3-3x3/review_checks.json`
- `src/bugarach/score.py` (the matching code)
- `src/bugarach/bench_combined.py`, `bench_slow.py`, `detectors/cicada.py`
- `docs/adr/0008-...md`
- `docs/handoffs/2026-09-21-slow-bench.md`

I did not open the earlier review reports.

**Summary:** 2 blocking, 8 major, 4 minor.

## Findings

Each finding gives location · issue · severity · fix · whether I verified it.

### 1. Decision 1, "What the gain is made of: mostly fewer calls on decoys" — BLOCKING
**Issue:** The report's own data contradict this.
- `adoption.json` → `cross_stream.rows`, diagonal, `by_background`, shipped → proposal decoy calls:
  - fast binned SCE: 124→117 (quiet), 97→76 (busy)
  - combined binned SCE: 131→131, 106→89
  - combined rate+context: 125→115, 126→114
  - combined SPIKE-synch: 121→118, 98→94
- Busy precision rises a lot: 0.56→0.66, 0.58→0.64, 0.40→0.585 and 0.57→0.64. So the gain is mostly fewer *non-decoy* false alarms on busy. About 115 decoy calls per background remain, and they are what holds F1 near 0.78.
- Table 1 disagrees with the sentence too. Without decoys, gains are +0.028, +0.010, +0.123 and +0.029. For rate+context and SPIKE-synch that is larger than the as-scored gain. If decoys were the source, these would be near 0.
- "…near 1 … for the shipped points too" is false for combined rate+context: 0.855 without decoys.
- Recall also *falls* under several proposals, which "Recall is near 1" hides:
  - fast binned SCE quiet: 0.996→0.971
  - combined binned SCE busy: 0.962→0.930
  - combined SPIKE-synch quiet: 1.000→0.983

**Fix:** Rewrite the bullet from the per-background precision, recall and decoy-call counts. Say that the gain is fewer non-decoy false alarms on busy, paid for with some recall on counted events.

**Verified:** yes (adoption.json and Table 1).

### 2. Decision 5, fast and slow locust (`sce_min_distance_frames` 4 → 128 / 256 frames) — BLOCKING
**Issue:** The page says these five proposals are held back "only because" of a limit, and that "if a limit counts, all five are" adoptable. That drops an earlier stop.
- `docs/handoffs/2026-09-21-slow-bench.md:296-298` says this exact climb (256 frames = 25.6 s) "is not a setting to ship until the anchor is settled".
- `bench_combined.py:282` carries the same ⚠ for 128 frames (12.8 s).
- The page never gives these values in seconds. At 0.1 s per frame they are 12.8 s and 25.6 s.

**Fix:**
- Carry the earlier "not a setting to ship" flag into Decision 5.
- Say whether the anchor question has been settled.
- Give the frame counts in seconds.
- Remove fast and slow locust from "all five … making nine" unless the flag has been cleared.

**Verified:** yes (both quotes are in the tree).

### 3. Decision 5 / Table 2, slow locust passes the elevated-rate budget by construction — MAJOR
**Issue:** The budget cannot fail for this proposal.
- A minimum of 25.6 s between SCE peaks caps calls at 60/25.6 = 2.34 per minute. The limit is 4.0 per minute.
- The proposal "fixes" the shipped failure (7.2/min) by rate-limiting itself, not by rejecting rate-driven co-activity.
- "Each of the five passes every budget that was checked" treats a pass that could not have gone the other way as evidence.

**Fix:** State the rate ceiling beside the pass, and mark this budget "no power for this proposal".

**Verified:** arithmetic yes. That the minimum distance applies to calls follows from the docstring at `cicada.py:62`; I did not run it.

### 4. The close-events test has little power — MAJOR
**Issue:** It is used as a gate (Decision 6; Table 2), but it barely moves.
- Locust proposals that cannot make two calls within 12.8 s or 25.6 s still pass a test on events "as little as 6 s apart". Held-out losses: slow −0.0068, combined −0.0007 to −0.0068.
- A detector that is structurally blind to the case this test exists for loses under 0.007 F1. So close pairs must be a small share of the scored events.
- Slow binned SCE at 0.0207 vs 0.02 (Decision 6) is being decided against an instrument whose power is not shown.

**Fix:**
- Report how many planted pairs in the close-events recordings are closer than 12.8 s and 25.6 s.
- Score recall on those pairs alone, as a paired per-pair check.
- Until then, say the test is "not able to detect loss of close events at the shares planted".

**Verified:** numbers yes (adoption.json). Mechanism is inferred; I did not count the pairs.

### 5. Budgets with no power are not named per proposal — MAJOR
**Issue:** "Other gaps" says generically that some ceilings "cannot bind". The strict rule's "every budget passes" still counts these passes.

What `adoption.json` shows:
- **No-coordination recording, detectors whose minimum the floor sets.** The floor is defined as the size the recording's own null reaches at most once per hour. So on a recording with nothing planted, calls per hour are held low by construction for detectors counting in ≤2 s windows. SPIKE-synch and LoCo read 0.
- **Limits far above measured values:**
  - fast CoactDetect no-coordination: 0.11 against 7 per hour
  - combined CoactDetect: 0.1–0.3 against 10
  - combined SPIKE-synch elevated-rate, in the stretch: 0.2 against 16 per minute
  - combined locust: 3.2 against 68
  - fast locust: 3 against 48
- **The elevated-rate recording's floor (16–20 co-active ROIs) is set for the whole recording.** Figure 3's bottom row shows every floor-set detector at 0 outside the stretch. So the outside-the-stretch budget is likely powerless for them too, not only the inside one the page names.

**Fix:** For each of the four adoptable proposals, list which budgets could actually have failed. From the data this looks like: precision swing, close-events (not run on fresh seeds), and no-coordination for rate+context only.

**Verified:** values yes. The outside-the-stretch mechanism is inferred from Figure 3 and the floor definition.

### 6. Decision 1 pools quiet and busy — MAJOR
**Issue:** The headline gains hide that they come almost entirely from the busy background.
- Per-background F1, computed from the recall and precision in `adoption.json`:
  - combined binned SCE quiet: about 0.772 → 0.771 (no gain); busy: about 0.724 → 0.757
  - fast binned SCE quiet: about 0.785 → 0.790
- Busy is also the background where most events are under the floor (fast middle level: 85 of 120). The gain and the "don't care" region coincide.

**Fix:** Give the paired fresh-seed gain per background, in its own column or panel.

**Verified:** yes (recomputed from adoption.json recall and precision).

### 7. "Those events are 'don't care' … losing them costs nothing in F1" (Decision 1; Definitions) — MAJOR
**Issue:** This is half the mechanism, and the other half offers another explanation for "the proposals call far fewer of them".
- In `score.py:260-304`, the one-to-one match runs over *all* planted events before the don't-care mask is applied. So an event under the floor can take the nearest call away from a counted event, turning it into a miss.
- Duplicate calls on an event under the floor stay in the false alarms (`dup_times`, `n_fa`); only the single matched call is removed.
- So calling events under the floor is not free. The search is actively *rewarded* for going blind to them, and more so on busy (see finding 6).
- This also means the Definitions entry ("a call matched to it is left out of precision") is incomplete.

**Fix:**
- Say this in Decision 1 and in the Definitions.
- Report duplicates and stolen matches near events under the floor, shipped vs proposal.
- Consider moving the don't-care mask to before matching.

**Verified:** code yes; magnitude not measured.

### 8. Combined binned SCE's adoption case is thin — MAJOR
**Issue:** The evidence for this one proposal is weak on every axis, and it is presented as one of four equally adoptable proposals.
- Fresh paired lower bound is +0.001, across four simultaneous intervals with no multiplicity statement.
- The winner changed with the held-out choice (it trailed by 0.0003 on the selection seeds).
- Quiet gain is about 0 (finding 6).
- Fast's version scores higher on the same fresh seeds (Decision 2).

**Fix:** Put these four facts together in Decision 1's row for combined binned SCE.

**Verified:** yes.

### 9. Decision 2 asks Tony to choose a version by its fresh-seed score — MAJOR
**Issue:** The prompt ("fast's proposal is at least as good on combined") asks Tony to choose on seeds 6000–6023, the only set nothing has chosen on yet. Doing so spends that set, and no untouched evaluation would remain.

**Fix:** Say so. If a choice is made on fresh seeds, name a new untouched seed set for confirming it.

**Verified:** yes (the page's own seed-set definitions).

### 10. Decision 3, "a new ruling, not a loosened limit" — MAJOR
**Issue:** Both options offered for the failing budgets loosen them in effect.
- Re-measuring the ceilings at the shipped points that now fail puts the new limits above the failure.
- Making decoys under the floor "don't care" deletes the failing swing.
- "The gate takes the absolute swing, although the budget was written for precision falling" reads as advocacy for passing.

**Fix:** Say plainly that either option would turn today's failures into passes. Frame the ask as "change the budget definition", with that consequence stated.

**Verified:** yes.

### 11. Real data section — MAJOR
**Issue:** The section picks one cut, leaves out its settings, and states one reading of a finding that has two.
- **One cut shown.** It gives fast × senktide only.
- **Same pattern elsewhere.** `real_data.md` shows it in high K⁺: OVX +9, ORX +12 on fast; +10 and +14.5 on combined. It also says all 291 flips in the OVX/ORX senktide and high-K⁺ rows go "calls only at the baseline floor". That means the per-window floor removes *every* call in those cells.
- **TTX is omitted.** It goes the other way: own floor −3 to +1, and 73 of 82 flips are calls only at the window's own floor. That bears on FOUNDATIONS §9.
- **Settings not stated.** The run used each stream's *proposal* where one existed: settings not yet adopted, including fixed-window SPIKE-synch and the 25.6 s locust. A reader will assume shipped settings.
- **Required caveat missing.** ADR-0008 says a write-up states that group is nested in imaging day. The section does not.
- **One interpretation offered.** "A per-window floor can absorb the treatment-window co-activity" is one reading. ADR-0008 decision 4 intends the other: the floor difference measures how much of an apparent change is a change in rate. Nothing here tells the two apart.
- **Untested comparison.** "Mainly in the gonadectomized groups" is a group comparison. It is untested, with n = 6–15 windows per cell.

**Fix:**
- Show the whole table, or name the high-K⁺ and TTX rows.
- State the settings used.
- Add the nesting caveat.
- Give both readings.
- Consider making "per-window vs baseline floor" an explicit decision. As written, the one real-data result bearing on whether ADR-0008 erases the effect under study has no decision attached, while nine decisions ask to adopt settings tuned under that floor.

**Verified:** yes (`real_data.md`; ADR-0008 lines 70–77 and 106–107).

### 12. Locust `sce_percentile` 99.99995 (fast, combined) — MINOR
**Issue:** This is a single-extreme threshold. The detector pools frames across 100 surrogates (`cicada.py:58`, 179). At that percentile the threshold is within about 1–2 samples of the pooled maximum for recordings of about 45 minutes at 0.1 s. It is a max, not a percentile, and the grid can go no further in any meaningful way.

**Fix:** State the number of pooled samples and the rank the percentile resolves to. Treat it as an effective limit.

**Verified:** partly. The pooling and 100 surrogates are in the code; I did not check the planted recordings' length.

### 13. Decision 1 / Figure 3, combined SPIKE-synch "exactly 0.2 calls per minute … on every seed set" — MINOR
**Issue:** 0.2/min × 5 min is exactly one call per recording, whatever the settings. That looks like a structural artifact (for example, the step at the stretch edge), not a response to rate.

**Fix:** Say what that one call is.

**Verified:** arithmetic yes; the cause is not checked.

### 14. Slow chorus_norm fails the elevated-rate test on fresh seeds — MINOR
**Issue:** This appears only in Table 2. No prose mentions it.

**Fix:** One line in Decision 3.

**Verified:** yes.

### 15. Held-out gain intervals use 400 resamples — MINOR
**Issue:** That is thin for 95% tails when an interval's closeness to zero is the adoption criterion.

**Fix:** Note it, or recompute with 2,000.

**Verified:** yes (as stated on the page).

## What I checked
- **Report text:** every section and all nine decisions.
- **Figures:** all four, looked at as images.
  - Figure 3 matches the text for combined rate+context outside the stretch on busy.
  - Figure 4 matches Table 3 and the ~1 ROI (fast, combined) and ~3 ROI (slow) floor offsets.
  - Figure 2 cell values are consistent with "about 14 higher off the diagonal".
- **adoption.json:** budgets, and precision, recall and decoy calls per background.
- **review_checks.json:** paired gains.
- **real_data.md:** all three stream tables.
- **score.py:** the matching and don't-care logic.
- **ADR-0008:** decision 4 and its consequences.
- **Locust provenance:** the earlier "not to ship" flag, in the slow-bench handoff and `bench_combined.py`.
- **Not checked:** decoy counts per recording, the number of close pairs in the close-events recordings, the planted recordings' frame counts, and whether the "anchor question" was settled after 2026-09-21.
