GRANT 1 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch (which can load the deferred NotebookEdit), and mcp__claude_ai_Claude_Docs__batch/update/guide

(This is a finding about the run, not about the artifact. The harness gave this reviewer editing tools that the role forbids, so the record should say the review took a fallback path. I used none of them. All scratch files are under ...\scratchpad\mb\role01\.)

# Role 1, "Prove It": claim ledger for chapter-1-aim0.md (blob 14d63527)

## What I checked
- **The revision note's claim that "no number … changed".** I diffed the chapter against the previous version, 5c3605a9. The only numbers that appear in the old version and not the new one are section numbers (1.4.x, 1.7.x, 1.8.x). I also remapped every old figure, table and section reference to the new numbering and diffed sections 1.5 to the end: they match apart from added prose and the stale references in finding 7.
- **The opening figures' numbers.** I re-ran `ch1_intro_figures.py --out <scratch>`. Its printed output is identical to intro_figs.log, line for line apart from the PNG paths. So every number in Table 1.1 and sections 1.1–1.3 reproduces.
- **Extra checks I ran:**
  - The CFAR threshold near event 2 over all 200 draws.
  - How each detector handled event 3 in every draw.
  - The correlogram's baseline away from zero lag.
  - The unrounded f₂ shares.
  - The share of events reaching K cells in some 1 s bin.
  - The analytic chance floors, the point where g₂ = ½, and the binomial chance tails.
- **Code read:** `count_detect`, `count_sliding_detect`, `merge_runs`, `measure_coordination_rates` (cumulants, `shifted`), and the `simulate_coordination` participation rule (k fixed at 10).
- **Run records read:** 2026-09-25-real-intervals README and blind_a/REPORT.md §4 (the Monte Carlo floor).
- **Papers read in 01-lit:** Finn & Johnson 1968, Rohling 1983, Malvache 2016, Perkel 1967, Thomas 1949.
- **Record of which recordings are in or out:** the export folder is the source of record (CLAUDE.md, "the export folder is the input"). The 66 real windows came from the `…STEPS_AND_PINS_EXCLUDED` export, which matches. The chapter makes no group-level claim.

## Findings
Columns: location · issue · severity · suggested fix · verified against a source?

1. **§1.3.2 and Fig 1.3 C · The correlogram model omits the hard-core deficit.**
   - C(τ) = C₀ + peak predicts chance (1) at every lag away from the peak. The measured correlogram instead sits at **0.857 (sharp) and 0.902 (jittered) of chance at |lag| ≥ 2 s**; the points are visibly below the dotted "chance" line.
   - The cause is the same one the chapter gives for f₂: events are held at least 20 s apart, so coordinated onsets from different events never pair at short lags.
   - The HWHM is taken relative to 1, not to the actual baseline. That explains part of the "5 % narrower" jittered width: measured against the baseline, the width is 0.815 s, not 0.796 s.
   - **Medium.** Fix: state the deficit, or take the width above the local baseline, and attribute the narrowing. · yes

2. **§1.3.4 · "chance puts at least 8 cells in a 1 s bin in a share 2 × 10⁻⁸".**
   - The sentence before it defines chance as background alone: 1 − e^(−bB) with b = 0.0096. At that rate the share is **7.8 × 10⁻¹⁰**.
   - The 2.07 × 10⁻⁸ comes from the sets' total mean onset rate, 0.0147 Hz, which includes the coordinated onsets (as the figure legend says).
   - **Medium-low.** Fix: say "at the sets' mean onset rate", or quote 8 × 10⁻¹⁰. · yes

3. **§1.3.4 · "A threshold that would catch every sharp event therefore misses most jittered ones."**
   - At the K = 8 being discussed, only **397/450 (88 %)** of sharp events reach 8 cells in any 1 s bin; 119/450 (26 %) of jittered events do.
   - The threshold that does catch every sharp event is K = 5 (450/450), and it catches **442/450** jittered events.
   - The sentence as written is not true.
   - **Medium.** Fix: "a threshold of 8 cells catches 88 % of sharp events but 26 % of jittered ones." · yes

4. **Fig 1.2 caption, "All three detectors join calls less than 3 s apart", and Table 1.1.**
   - `count_detect` and `count_sliding_detect` (via `merge_runs`) join gaps ≤ 3 s ("at most", not "less than").
   - The script's CFAR (`runs_to_calls`) measures the gap from the next run's start minus w, so it **joins runs up to 5 s apart**.
   - CFAR call spans also run from the run start minus 2 s to the run end, while the sliding detector's span runs from first onset to last. CFAR is therefore scored with a wider ±1 s target.
   - The table compares detectors whose merge and scoring rules differ.
   - **Low-medium.** Fix: give CFAR the same merge and span rule as `count_sliding_detect`, or disclose the difference. · yes

5. **§1.3.3 · "measured shares lie within 0.02 of the full prediction at every window for both sets".**
   - Unrounded, the jittered set is +0.0194 at 4 s and **+0.0214 at 8 s**.
   - **Low.** Fix: "within about 0.02". · yes

6. **§1.3.3 · "At 4 s and 8 s the measured share turns down".**
   - True for the sharp set (0.911 → 0.903 → 0.840).
   - The jittered set is flat (0.685 → 0.807 → 0.807). Only its prediction turns down.
   - **Low.** Fix: restrict the claim to the sharp set. · yes

7. **"Reproducing this chapter" comments carry stale section numbers.**
   - `theory.py --from-record` "prints 1.1 and 1.4 numbers": now 1.4 and 1.5.
   - `theory_floor.py` "event floor, 1.5.1": now 1.6.1.
   - `assessor_jitter.py` "1.5.2": now 1.6.2.
   - Table numbers in these comments were updated; section numbers were not.
   - **Low-medium,** because these lines are the provenance pointers. Fix: renumber them. · yes

8. **§1.3.6 · "with the cell under test and its neighbors left out, is cell-averaging CFAR (Finn & Johnson 1968)".**
   - Finn & Johnson's text excludes the cell under test ("must exclude the cell under test", p. 422). The text layer contains no guard cells or neighbors; figure text was not checked.
   - Guard cells are in Rohling 1983 ("two cells (guard cells) directly adjacent … usually also done").
   - §1.2.3 itself attributes guard cells correctly to Rohling 1983, so §1.3.6 contradicts it.
   - **Low.** Fix: drop "and its neighbors" from the Finn & Johnson attribution. · yes

9. **§1.9.1, new text: "Each failure in Table 1.1 is a setting that does not match a property of the coordination … The threshold that worked, CFAR's".**
   - CFAR finds event 2 in only 44 % of draws and event 5 in 42 %. §1.2.4 item 2 itself attributes the event-2 failure to masking by nearby events, which is not a setting mismatch.
   - The fixed-bin failure on event 2 is a bin border, not "a bin narrower than the spread".
   - CFAR "worked" only on false calls and event 4.
   - **Low-medium.** Fix: narrow the claim to false calls, and name masking as a separate failure. · yes

10. **Fig 1.3 caption · "the thick horizontal bars span the peak's HWHM".**
    - The bars are drawn from −HWHM to +HWHM, which is the full width at half maximum.
    - **Low.** Fix: "extend one HWHM either side of zero". · yes

11. **"About this chapter", revision note.**
    - It says sections 1.1–1.4 were written new and "the rest was renumbered". New prose with new claims was also added to the openings of 1.5, 1.6 and 1.7, and to 1.9.1, 1.9.3, 1.9.5 and 1.10; finding 9 is one of those claims.
    - Fig 1.4's PNG was also regenerated; only its wording changed.
    - "No number … changed" holds.
    - **Low.** Fix: list the other sections that gained text. · yes

## Claims verified (matched)
**Fig 1.1 and the model**
- 190 background and 40 event onsets; 4 events × 10 cells; σ 0.2 s; b 0.05; 120 s.
- Event times 17/46/78/104 s, at least 20 s apart, consistent with "chosen by hand" under the hard-core model.

**Fig 1.2, Table 1.1 and §1.2**
- All 15 detection shares and all 6 false-call rates in Table 1.1 match the script output.
- Seed 1011, "17 of 200" draws typical; per-detector hits and false calls in the draw shown.
- Event parameters (12/0.05, 7/0.5 at 45.95 s on a bin border, 10+10/0.1 at 80 and 83 s, 12/0.1 in the busy stretch, 5/0.05); busy stretch 2–3 min.
- Event 3: in all 200 draws, every detector found exactly one of the pair and missed the other, so "called as one event in every draw" holds.
- CFAR threshold near event 2: its minimum is 7 or 8 in 198/200 draws, and (8, 9) in draw 1011. The text's "7 or 8 … (8 and 9 in the one drawn)" holds with "threshold" read as the window minimum.
- CFAR threshold in the busy stretch 9–12; false calls 1.78, 3.60 and 0.02 per minute.
- Chance floors: 6 cells at 0.0096 and 0.01 Hz, 12 at 0.05 Hz (0.334/h at K = 6, 0.0096 Hz). The repository's Monte Carlo floor gives 6 and 12 at 0.01 and 0.05 Hz (REPORT §4).
- Fixed-bin merge semantics (≤ 3 s, at most one uncalled bin); distinct-cell counting; the sliding window (t − 2, t].
- CFAR reference 30 s and guard 5 s; ADR-0008's one call per hour.

**§1.3**
- C₀ formula; 2√(ln 2) σ = 1.665σ; peak 18.2 measured against 18.53 predicted (sharp); 4.6 against 4.76 (jittered); HWHM 0.176/0.174/0.167 and 0.796/0.835 s; 0.796/0.835 = 4.7 % narrower.
- g₂ = ½ at w = 2.079σ; g₂ values; measured shares 0.48/0.87 (sharp) and 0.10/0.47 (jittered).
- f₂ and f₃ formulas match `factorial_cumulants`; two window offsets (0, w/2).
- Surrogate offsets are a permutation × 2w, spanning (N − 1)·2w = 64 s at w = 1 s; the "independent shifts lost pairs" claim holds (35 %, per the code's docstring).
- Fig 1.4 A shifts −6/−2/+2/+6 s and the 4/1 onset counts; B row and column sums; C net leads +3/+5/−3/−5, order 2-1-3-4, 12 pairs, F = 0.67.
- Bin shares 0.0147 and 0.0044 at K = 8, 0.017 and 0.019 at K = 5; 45/2700 = 0.017.
- Table 1.2: 15/2700 = 0.0056, 45/2700 = 0.0167, k/N = 0.15/0.30/0.61.
- §1.3.1 realistic event counts: 212/66 = 3.2, 481/66 = 7.3, 9.7 and 22.0 per hour (run record).

**Attributions**
- Finn & Johnson: masking by a second target in the threshold-control cells; cell under test excluded.
- Rohling: guard cells routine; ordered statistic resists interfering targets.
- Malvache: summed-activity threshold in a 200 ms window.
- Perkel: "cross-correlation histogram".
- Thomas 1949: quadrat counts of clustered plants, no scatter law.

## Not verifiable
- Glaz, Naus & Wallenstein 2001 is marked ⚠ (not opened) in the chapter itself; I did not open it either.

unreached: 0
