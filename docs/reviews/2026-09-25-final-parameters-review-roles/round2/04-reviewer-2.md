GRANT 4 ok — Read, Grep, Glob, Bash (also holds SubagentHandback, the hand-off channel, not an editing tool; no file edited)

# Role 4 — Reviewer 2: findings on `docs/learned/runs/2026-09-25-final-parameters/README.md`

**Checked:** the whole page; all four figures read as images; `adoption.json` (`rows`, `cross_stream`, per-background metrics, `under_floor`); ADR-0009; `src/bugarach/bench.py` constants and seed offsets; the real-data write-up and floor probe in `<darkroom>/bugarach/2026-09-25-final-parameters/065/report-inputs/`. Every number quoted below comes from `adoption.json` or that write-up.

**Summary:** 3 blocking, 10 major, 7 minor. The page is careful about held-out selection bias. What it does not show is **what the F1 gains are made of** (almost entirely fewer decoy calls), **what they cost** (calls on real planted events below the floor, which the metric cannot see), and **whether its checks could have failed** (the elevated-rate test partly measures the floor by construction).

Format: location · issue · severity · suggested fix · verified against a source.

## Blocking

**B1 · Decision 1 / Decision 7 — the harm lives in the set the metric does not score.**
- ADR-0009 R2 removes below-floor planted events from recall and precision, so F1 cannot register their loss.
- `adoption.json` records calls on those events for shipped and proposal (`under_floor…calls_on_under_floor`), and the adoptable proposals call far fewer of them:
  - fast binned SCE: lowest level quiet 22 → 5 of 120; busy 23 → 6; middle level busy 60 → 49 of 85;
  - combined rate+context: lowest level quiet 34 → 2 of 120; busy 41 → 11;
  - combined SPIKE-synch: lowest busy 41 → 20;
  - combined binned SCE: lowest quiet 36 → 24.
- So some of the "held-out gain" may be bought by giving up sensitivity to real, weak coordination the bench planted. The page treats Decision 7 (much of the bench sits under the floor) as a bench question and never connects it to the four proposals it asks Tony to adopt, and "pass every budget checked" plus "gain above zero" cannot detect this loss.

· **blocking** · In Decision 1, add calls on under-floor events, shipped → proposal, by level and background; state that F1 is blind to them and that ADR-0008 calls them "don't care". Whether losing them is acceptable is Tony's ruling, and he needs the numbers to make it. · verified yes (`adoption.json`).

**B2 · Decision 1, the "combined's budgets" bullet, and Figure 3 — the elevated-rate test partly cannot fail for floored detectors.**
- ADR-0009 Consequences: the test "partly measures the floor … a detector that honours the floor makes few calls there by construction". Figure 4 shows why: the elevated-rate recording's floor is 16–20 co-active ROIs, and that floor becomes `min_rois`/`min_n` for CoactDetect, LoCo, binned SCE and SPIKE-synch (`bench.FLOORED_SETTING`).
- The page says the four proposals "pass them by wide margins, so no verdict here depends on that", and never repeats the ADR's caveat.
- Direct evidence the test does not respond:
  - combined SPIKE-synch measures exactly 0.2 calls/min inside the stretch (limit 16), identical for shipped and proposal on the selection, held-out and fresh seeds — different recordings;
  - combined binned SCE's in-stretch value is identical for shipped and proposal on every seed set (5.742 / 5.721 / 5.75), although its threshold changed.
- The outside-stretch rate is taken in the same recording, so it has the same raised floor.
- The test does have power for rate+context and locust, which carry no participation minimum.

· **blocking** (a pass is offered as reassurance for exactly the proposals where the check cannot move) · State ADR-0009's caveat on the page; mark which detectors' passes are uninformative; delete "no verdict here depends on that" or restrict it to rate+context; name the test that would have power (e.g. the no-coordination recording at its own ~4–6 floor). · verified yes (`adoption.json` budget values; ADR-0009; `bench.py` L58–61; Figure 4 visual).

**B3 · Decision 8 omission — the strongest cross-stream counterexample is about an adoptable proposal.**
- On the combined bench, the fast-tuned binned SCE proposal scores 0.788 [0.774, 0.802], while combined's own proposal — which Decision 1 asks Tony to adopt — scores 0.764 [0.748, 0.781].
- Decision 8's table lists only combined-tuned wins and frames the ruling in one direction.
- Other omitted reversals: fast-tuned CoactDetect on combined 0.811 vs 0.803; combined-tuned rate+context on fast 0.736 vs fast's shipped 0.703.
- Tony cannot decide on combined binned SCE without this.

· **blocking** (bears directly on Decision 1) · List every off-diagonal cell that beats the diagonal, in both directions, with intervals; cross-reference combined binned SCE from Decision 1; note that with 48 off-diagonal cells some wins are expected from noise. · verified yes (`adoption.json` `cross_stream`).

## Major

**M1 · Decision 1 / Table 1 / Definitions — what the F1 gain is made of is never said.** Recall is ~0.95–1.0 almost everywhere, precision ~0.63–0.78, and F1 without decoy calls ~0.95–1.0, so nearly all the headroom, and nearly all the gain, is fewer calls on decoys. For fast CoactDetect (0.981 → 0.956) and combined CoactDetect (1.000 → 0.978), F1 without decoy calls *falls* under the proposal: on events that count those proposals are worse, and they win only on decoy rejection. · major · One sentence in "How to read them" saying the gain is mostly decoy rejection, pointing at the without-decoys column and flagging the two CoactDetect rows. · verified yes.

**M2 · Decision 3 — "the precision swing may be the floor's doing" is testable with data in hand, and the data show two different mechanisms.**
- **Fast rate+context shipped:** recall is 1.0 on both backgrounds and decoy calls are ~equal (136 quiet vs 134 busy). Busy counts 155 events vs 240 on quiet (fewer true positives), which takes precision from ~0.635 to ~0.57; the rest of the drop to 0.460 comes from ~46 extra busy calls that are neither decoys nor planted events. So the floor explains part of the swing, not all.
- **Fast SPIKE-synch shipped:** the swing runs the other way — busy precision 0.847 vs quiet 0.699 — because busy's higher floor, as `min_n`, cuts decoy calls from 84 to 23. That is the floor acting as a detector setting, not as the scorer setting events aside, which is the only mechanism the page offers.

(Both are arithmetic from `adoption.json`, assuming one matched call per event.) · major · Replace "may be" with this decomposition (or compute it properly), and give the sign of each swing. · verified yes (with that assumption).

**M3 · Decision 4 — "Fast CoactDetect does not fail the close-events test" rests on an unrecorded number and is treated inconsistently.**
- The 0.0165 "re-run in review" is in no run record (neither the darkroom folder nor `adoption.json` contains it).
- It is a point estimate on 12 recordings per background, 0.0035 inside the allowance, declared a flat pass — while slow binned SCE at 0.0207 (0.0007 outside) is called "at the allowance within noise … Tony's call".
- The fresh seeds do not run the close-events test at all.

· major · Record the re-run (script, seeds, output) in the darkroom and cite it; give both rows the same wording ("within noise of the allowance"), or better, an interval. · verified yes (grep: no record).

**M4 · Table 2 — "pass" printed for budgets never measured.** The held-out column shows "pass" for fast rate+context, fast SPIKE-synch and combined rate+context shipped, although their failing budget (the precision swing) is `null` there ("not recorded in the search's held-out rows"). The fresh column shows "pass" where the close-events test was not run. The caption says "not checked" marks a missing check, but the cells read "pass". · major (a reader sees the swing failures "pass" on held-out) · Generator: "pass (precision swing not recorded)" / "pass (close-events not run)". · verified yes (`adoption.json` `held_out.precision_swing.ok: null`).

**M5 · Decision 1 — the paired fresh-seed gain is not computed, and one interval is misdescribed.** Combined binned SCE and combined SPIKE-synch rest on overlapping, unpaired intervals; the per-recording scores exist, so a paired bootstrap on the fresh seeds is cheap and is the only independent test of the gain. "Combined rate+context's barely touch" is wrong: shipped [0.642, 0.726] vs proposal [0.748, 0.793] are 0.022 apart, while fast binned SCE's gap is 0.004. · major · Compute and show the paired fresh-seed gain with its interval for all four; correct "barely touch". · verified yes (intervals).

**M6 · The strict rule (Decisions 1–2) has no minimum effect size, and the budgets are anchored to the shipped point.** "Interval above zero" admits slow rate+context at +0.005 F1 (fresh 0.830 → 0.834) and combined binned SCE at +0.015. The budgets are ceilings over what the shipped point measured (`bench.py` `MAX_PRECISION_DROP`: "measured: 0.01" → limit 0.10), with inconsistent, unjustified headroom (binned SCE 0.46 measured → 0.50 limit; SPIKE-synch in-stretch 0.2 measured → 16/min). "Passes every budget" therefore means "no worse than a shipped-derived ceiling", and several ceilings cannot realistically bind. · major · State the anchoring in Decision 1; ask Tony for a minimum practical gain; list the budgets whose limit is >10× the measured value. · verified yes (`bench.py` 2082–2088; `adoption.json`).

**M7 · Decision 7 — "about one ROI above" is false for slow, and "the last three rows" is wrong.** In Figure 4, slow's no-coordination floor is ~3–4 ROIs against 6–7 for the planted quiet recording (~+3); fast and combined are ~+1. The 25/40, 20/40 and 15/40 are fast busy, combined busy and slow busy — the page table's rows 2, 4 and 5, not the last three. · major (it misreads the figure and understates the self-defining-null effect on slow) · Give per-stream offsets and name the rows. · verified yes (Figure 4 visual).

**M8 · Figure 4 / Decision 7 — structure the text never mentions.** The elevated-rate recording's floor is 16–20 ROIs on fast and combined (~8–10 on slow), far above every planted level. The page never mentions it, although it is what makes B2 true. · major · One bullet under Figure 4 linking it to the elevated-rate caveat. · verified yes (Figure 4 visual; `bench.py` L1071).

**M9 · Real data — a design-variable breakdown is cherry-picked.**
- "Under senktide on fast, OVX +17, ORX +20" omits DI (+1) and MALE (+1) from the same table (`065/report-inputs/real_data.md`).
- That contrast is the result, even descriptively: the floor rises with senktide only in the gonadectomised groups, and the page's wording lets the pattern read as general.
- The consequence is unstated: a per-window floor can absorb exactly the treatment-associated co-activity the project studies (OVX senktide flips 29 of 72 cells; ORX flips 43 of 88).

· major · Give all four groups in DI, OVX, MALE, ORX order, and one sentence that the floor's rise under treatment is itself something Tony must rule on (still descriptive, FOUNDATIONS §9). · verified yes (`real_data.md` L44–59).

**M10 · Definitions / Figure 1 — "mean F1" pools backgrounds scored on different event sets.** On fast, busy F1 is computed over 155 events and quiet over 240; averaging the two F1s hides this, and background is a design variable (e.g. fast rate+context shipped: quiet 0.777 vs busy 0.630). · major (moderate) · For the four adoptable rows, give per-background F1, precision and recall in Decision 1 (they are in `adoption.json` `by_background`), and state the counted-event denominators. · verified yes.

## Minor

**m1 · Decision 8, row 3 — no interval, and the "win" is inside noise:** combined-tuned CoactDetect on fast is 0.827 [0.810, 0.845] vs fast's 0.809 [0.791, 0.831], heavily overlapping, yet the row reads "beats"; rows 1–2 are unpaired comparisons. Fix: add the intervals, or soften to "scores higher, not tested". · verified yes.

**m2 · Real data — "2,696 cells" counts one window-level fact eight times.** Floors are set per window × stream, not per detector, so "in 2,696 cells the two floors differ" multiplies window-level facts by 8 detectors. Fix: also give the window count (of 128 × 3). · verified partly (structure from `real_data.md`).

**m3 · Decision 6 — "no result on this page changes" is asserted from the proposals alone.** Invalid 8 s guard settings were walked; they could have consumed extensions or changed bracketing records (e.g. `guard_sec (limit)` on slow LoCo). Fix: "no proposal changes; bracketing not re-checked", or re-check. · verified no.

**m4 · What ran — "re-derived independently in review, with no mismatch".** The method is not stated. If it used the same `Evaluator`/`make_admissible`, it is a reproducibility check (the same pattern the page labels correctly for the 3 × 3), not independent. Fix: say how. · verified no.

**m5 · Unjustified constants:** the 400-resample bootstrap (a 95% interval then rests on ~10 samples per tail), the quarter-of-context guard cap, the 6-extension cap (`--max-extensions 6`), the 6 s close-events spacing and the 2.5 s match tolerance are named but not justified on the page beyond ADR pointers. Fix: one clause each, or a pointer to where each is justified. · verified yes (absence).

**m6 · Figure 2 — the colour scale compresses the differences.** The colorbar is 0.4–0.9 while every cell lies in 0.67–0.87, so the differences Decision 8 relies on (~0.02–0.03) are invisible in colour. Fix: narrow the range, or show the difference from the diagonal. · verified yes (visual).

**m7 · Figure titles name the quantity, not why it matters** (e.g. "Figure 3. The elevated-rate recording…"). Fix: state the inference (Figure 3: which detectors can fail this test, and which proposals pass it). · verified yes.

**Figures, read as pictures:**
- Figure 1 agrees with Table 1.
- In Figure 3, the combined rate+context proposal busy point (~1.3/h, above its bar) matches the text; the shipped combined SPIKE-synch busy point also sits above its bar (~1.6/h), ungated and unmentioned.
- Figure 4 undermines "about one ROI" for slow (M7) and shows the 16–20 elevated-rate floors (M8).
