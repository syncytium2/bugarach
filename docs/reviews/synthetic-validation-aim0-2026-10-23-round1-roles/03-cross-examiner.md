GRANT 3 MISMATCH — missing none; holds forbidden tools: Edit, Write, NotebookEdit (deferred), Bash, PowerShell, Agent, Artifact, Skill, Claude Docs batch/update (write-capable MCP), WebFetch/WebSearch (deferred). Spawned through the inline general-purpose fallback, so the run record's `roles:` line must say this review took a fallback path. I used Read, Grep and Glob only. I edited nothing, ran no code and wrote no scratch files.

# Role 3 (Cross-Examiner): findings on Aim 0, synthetic-validation.md

Every finding row is: location · issue · severity · suggested fix · verified against a source (yes/no). "Doc" means `docs/goals/synthetic-validation.md`, and line numbers are its lines.

**Counting basis.** Every number below uses the basis `theory_check.json` uses: one row per (background, jitter, k, event count, window). A row's value is the median over 5 recordings of recovered ÷ planted. There are 72 rows per background. The doc never states this basis. It also uses the word "cell" for both a grid condition and an ROI (see finding 9).

## A. Numbers in the text that the record contradicts

1. **L37 vs L51–53.** L37 says the predicted participants "match the measured median within about 0.03 in every cell" at 0.01 Hz. L52 says "within a median 0.011 (worst 0.06)" for the same comparison. The json agrees with L52. Examples at 0.01 Hz:
   - σ 0.2 s, k 5 cells, 15 events, 2 s window: predicted 0.937, measured 0.880 (difference 0.057).
   - σ 1.0 s, k 5 cells, 15 events, 1 s window: difference 0.046.
   - σ 0.5 s, k 5 cells, 15 events, 1 s window: difference 0.040.
   
   Neither line gives a unit. Both are differences in recovered ÷ planted, but L52's "of the planted value" reads as if it were a fraction of k. · **High** · Make L37 agree with L52 (median 0.011, worst 0.06) and name the unit ("in recovered ÷ planted"). · yes

2. **L47 vs L52 vs json: which conditions are "not predicted" is stated two ways.** L47 limits it to "5 cells per event, 15 events, 0.05 Hz". L52 drops every 5-cell condition at 0.05 Hz ("events of 10 or more cells"). The json shows that 5 cells with 45 events at 0.05 Hz also miss badly:
   - σ 0.2 s, 4 s window: k 0.66 measured vs 0.83 predicted; rate 2.80 vs 1.32.
   - σ 1.0 s, 1 s window: k 0.76 vs 0.55.
   - σ 0.5 s, 1 s window: share 1.11 vs 0.75.
   
   · **Medium** · Make L47 say "5 cells per event at 0.05 Hz, either event count", which matches L52. · yes

3. **L41–42: "0.17, 0.48 and 1.0 s at both backgrounds" holds only at 0.01 Hz.** The json jitter medians are 0.166, 0.471 and 0.975 s at 0.01 Hz, and 0.147, 0.496 and 0.936 s at 0.05 Hz. Figure 1's purple series shows the same split (about 0.83× vs 0.73× at 0.2 s).
   - L43's "0.05 s reads about 0.02 s" is 0.025 s at 0.01 Hz but 0.007 s at 0.05 Hz.
   - The same "about 0.17 s" repeats at L91–92.
   - Only 25–27 of 30 recordings are usable at 0.05 Hz, which the text does not say.
   
   · **Medium** · Give both backgrounds (0.17/0.47/0.98 s and 0.15/0.50/0.94 s) and state the usable count. · yes

4. **L44–45: "within about 10 % at every K and background" understates the worst cases.** From the json, predicted (chance + planted) against measured:
   - 0.01 Hz, K = 6, 45 events: 1.000 vs 0.867 per min (15 %).
   - 0.05 Hz, K = 3, 45 events: 8.97 vs 8.03 per min (12 %).
   - 0.05 Hz, K = 6, 15 events: 0.617 vs 0.556 per min (11 %).
   
   · **Low–Medium** · Say "within about 15 %", or name the K = 6 exceptions. · yes

5. **L34–39 headline "predicted exactly" vs L98–99 "open residuals … neither is explained".**
   - The heading covers all of the tool's outputs, but only participants are checked in the text.
   - The json's rate and share columns miss by much more than participants do, even at 0.01 Hz. For σ 0.2 s, k 5 cells, 15 events, 4 s window: rate 1.075 predicted vs 0.783 measured, share 1.00 vs 0.71. For σ 1.0 s, k 10 cells, 4 s window: rate 1.12 vs 1.30.
   - L38's "5–15 %" Poisson residual is for participants only. The rate residual reaches about 34 % (σ 0.05 s, k 5 cells, 45 events, 4 s window: 0.995 vs 1.335).
   
   · **High** · Limit "exactly" to the pair and triple cumulants and participants. Report the rate and share agreement, or say they are not yet matched, and connect this to L98–99. · yes

6. **L140 (order table) vs `order_limit.py`: the formula in the table does not produce the number in the table.**
   - For M > 1 the script's prediction is `hypot(pred_many, no-order bias)`.
   - The printed formula alone gives 0.081 at M = 64 and τ = 2.5. The "0.086" in the table is the value with the bias added in quadrature (bias ≈ 0.375/√170.5 ≈ 0.029).
   - The check's settings are also not given: τ = 2.5, 2000 events, σ 0.2 s for this row; 200 events for the one-template row; 25–800 events for the no-order row.
   
   · **Medium** · Write the row as √(formula² + (0.375/√n̄)²), and state E and τ for each check. · yes

7. **L132: "the indicator F the share of pair agreements with that sort" contradicts the code and the table's own null.**
   - A share of agreements would sit at 0.5 with no order present.
   - The code's F is Σ n_ij D_ij / Σ n_ij, which is agreements minus disagreements. It goes to 0 with no order, which is what the "no order" row (0.375/√n̄ → 0) assumes.
   
   · **Medium** · Say "the net agreement (agreeing minus disagreeing pair co-participations) as a share of all of them". · yes

8. **L143–147: an explanation the page itself withdraws.**
   - L147 uses 0.375/√n̄ to explain why the August control median "sat at 0.10".
   - L154–156 says PySpike's ISI-adaptive windows and normalisation "change the constants, and the scaling laws are the claim, not the numbers". The 0.10 is exactly such a number. n̄ for that control is never computed either.
   - The quote also keeps fast ρ −0.75 and drops slow ρ −0.40 from the same sentence of `2026-08-19-synfire-measured-and-what-it-cost.md` L71. That todo correlates the indicator with spike count, not events per pair; the doc puts its own reading in place of the todo's.
   
   · **Medium** · Call the 0.10 consistent in direction only, give both ρ values, and label the per-pair reading as the doc's own interpretation. · yes (todo text); no (n̄)

## B. Terminology against GLOSSARY.md and CLAUDE.md

9. **"Cell" means two things.** It names a grid condition in "in every cell" (L37), "every cell at one background" (L77) and "the weakest cells" (L47). It names an ROI in "5 cells per event" (same L47 sentence), "within one cell" (L86) and "33 cells". L47 uses both meanings in one parenthesis. · **Medium** · Use "condition" (or "grid point") for the grid and keep "cell" for an ROI. · yes

10. **The assessor goes by three names: "the assessment", `assess`, and the glossary's "the assessor".**
    - The doc says "the assessment" at L23, L44, L82, L177, L180 and L184.
    - Figure 1's legend says "assess, K = 3 cells".
    - GLOSSARY L205–207 names the machine half "the assessor" and says: *Never "the assessment says"*.
    
    · **Medium** · Use "the assessor" (`assess_coactivity`) in the prose, and match the legend or explain it. · yes

11. **"Chance floor" for the ADR-0008 floor** (L85 "The ADR-0008 chance floor", L117 "the chance floor"). GLOSSARY L477–482 says pages meaning this one say "event floor" or "the floor (ADR-0008)". The handoff L64 has the same drift. · **Low–Medium** · Write "event floor (ADR-0008)". · yes

12. **Retired words "spacing" and "timing".** GLOSSARY L456–458 says "spacing" and "timing" are retired in favour of **intervals** and **jitter** (Tony, 2026-09-28).
    - The Aim 0 text uses "clustered spacing" (L253), "how tightly timed" (L117) and "participation and timing (k, σ)" (L160).
    - The rest of the page does the same: L9, L205, L261, L267–268, L287.
    
    · **Low–Medium** · Replace with "intervals" and "jitter". · yes

13. **Bare "adaptive" (retired).** "rather than adaptive windows" (L135) and "its adaptive coincidence windows" (L155) refer to PySpike's window. The glossary's term for it is **ISI-adaptive**. · **Low** · Write "ISI-adaptive". · yes

14. **"Jitter" is defined differently in the glossary and on this page.** GLOSSARY L468–472 defines jitter as measured by the half-width of the onset correlogram's peak (0.105 s fast). Aim 0 and Figure 1 use jitter as the Gaussian SD σ of the onsets ("jitter, SD (s)"). The two differ by a factor, since a pair's lag has SD σ√2. · **Medium** · Add the SD definition (the generator's `jitter_sec`) to the glossary entry and give the conversion. · yes

15. **New terms with no glossary entry.** The house rule is that a new term is added to the glossary in the same change. None of these is in GLOSSARY.md (searched):
    - **source**: the goal's central word. It also overlaps the stream axis, since the handoff L40 says "fast and slow are one example of two sources".
    - assembly, membership, the coordination-rates tool, window sharing g_n, chance clusters, the synfire indicator / SPIKE-order, score sort, the exchangeable limit.
    
    · **Medium** · Add the entries, and say how "source" relates to "stream". · yes

16. **Bare counts and missing units (CLAUDE.md "every number carries its unit").** Examples:
    - "6 at 0.01 Hz and 12 at 0.05 Hz" (L87, should say cells).
    - "M = 10/45/1000" (assemblies).
    - "K = 3 or 4" (cells; Figure 1's legend says "cells", the text does not).
    - "within about 0.03" and "0.011 (worst 0.06)" (see finding 1).
    
    Symbols used before they are defined: q (L69), f3 (L98), N and λ (L36). · **Low** · Add units, and define each symbol at first use. · yes

17. **Figure 1 is referred to by number only.** CLAUDE.md requires number and name in prose. L50, L76, L243 and L284 say just "Figure 1". The prose name at L170 ("recovery against planted jitter") does not match the caption's title ("Aim 1a, one source, random membership"). · **Low** · Use one name in both places and attach it to each reference. · yes

## C. Aim 0 against the rest of the page and the companion docs

18. **The event-floor capability edge is stated too narrowly (L86–87).** The floor is 12 cells at 0.05 Hz (blind_b `theory_floor.txt`), so 10-cell events (participation 0.3) can never pass it at 0.05 Hz either, not only 5-cell events. · **Low–Medium** · Say "below 6 cells at 0.01 Hz and below 12 cells at 0.05 Hz, i.e. 5- and 10-cell events at 0.05 Hz". · yes

19. **Aim 1a bullets still say jitter is the weak parameter (L184–188), while Aim 0 L42 says it is now one of the best.**
    - The L166–168 caveat covers only the reseeding, not the fact that Aim 0 superseded this.
    - L187 still moves the correlogram tool "up the list" on grounds Aim 0 removed.
    - L174 says share is within "about 20 %" at every jitter and window. Figure 1 shows about 0.73 for the 1 s window at 1 s jitter (0.01 Hz), which is about 27 % off.
    
    · **Medium** · Add a pointer to the Aim 0 jitter fit, and revise the 20 % figure. · yes (figure)

20. **"Where it stands" (L18–23) is stale against the Aim 0 sections.** It does not record:
    - the blind replication;
    - that Aim 1a was rerun with a seed per recording;
    - the membership and order pass.
    
    Separately, "Open work a session can do without a ruling" (L284–291) leaves out every "Next" item in the Aim 0 plan (L237–254): the PySpike check, moving blind A's joint fit into `theory.py`, Cramér–Rao, the random-matrix threshold. · **Medium** · Add the dated status bullets, and either list the Aim 0 items in Open work or cross-reference them. · yes

21. **Claims with no saved output behind them.** The scripts exist, but no output file was kept for:
    - blind A's joint fit "within about 5 % from 0.2 s" (`invert_cr.py`), which is also why L92 says "Adopt it";
    - B's "f3 5–7 % below prediction over 60 seeds" (`check_f3.py`; the 60 seeds are confirmed in the code);
    - A's "rate 3–5 % above";
    - the membership checks (44.5 vs 45.0 and so on);
    - the order checks (0.503/0.500, 0.747/0.758, 0.461/0.460, 0.084/0.086, ±0.01).
    
    The predicted values I could recompute from the formulas all match. Separately, the blind numbers come from the shared-seed record (blind_README L7), and the doc does not say so beside them. · **Medium** · Commit the `.out`/`.txt` outputs beside the scripts as blind_b does, and mark the blind numbers as from the first record. · no (measured values); yes (predicted values)

22. **README.md wording.** The `theory_check.json` row ("its record") comes after `order_limit.py`, so "its" reads as if it were order_limit's. The file is theory.py's record. · **Low** · Move the row under `theory.py`, or say "theory.py's record". · yes

## Checked and consistent (no finding)

- **Run sizes:** 240 recordings (48 conditions × 5 seeds), 33 cells, 45 min, min_sep 20 s, frame 0.1 s, windows 1/2/4 s, K = 3/4/6.
- **Seeding:** the per-recording seed fix is in `aim1_one_source.py`.
- **Formulas:** the closed forms in L32–33 and L67 match the `theory.py` docstring. The 60 q (1 − q)² per-minute chance-cluster rate matches.
- **Floor:** 6 and 12 cells, and "exact or within one cell" against `window_floor` (blind_b `theory_floor.txt`).
- **Count detector:** "about 0.03 recall in most conditions" (blind_b `theory_count_detector.txt`).
- **Truncated Gaussian:** a 1 s Gaussian cut at ±1.5 s has SD 0.74 s.
- **Membership:** 1 + (E − 1)/M gives 45, 5.4, 1.98 and 1.04 at M = 1, 10, 45 and 1000.
- **Order:** (2/π)arctan τ gives 0.500 at τ = 1 and 0.758 at τ = 2.5.
- **August todos:** 0.101 control median, ρ −0.75, the event-preserving null, and "the generator plants no order".
- **Figure 1 vs Aim 1a text:** 8–16× at K = 3/4 and 0.05 Hz, 0.4× at the 1 s window and 1 s jitter, and the caption's 240 recordings, 33 cells and 45 min all match.
- **Rest of the page:** the Settled detector list matches the plan bullet. Compute WSMIP065 matches the handoff.
- **Not applicable:** group order (no groups in Aim 0); "fire" and "modality" are not used, and "spike count" appears only inside a quotation; "data" plural is respected.
