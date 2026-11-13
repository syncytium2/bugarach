GRANT 3 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update (plus deferred NotebookEdit and others reachable through ToolSearch)

This is a finding about the run, not the artifact: the role took a fallback path and was given editing tools. I used only Read, Grep and Glob, and edited no file.

# Cross-Examiner report: Chapter 1 (chapter-1-aim0.md, blob 14d63527)

**What I checked.** I read the whole chapter (1,669 lines). I opened Figures 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.9, 1.11, 1.12, 1.13, 1.14, 1.17 and 1.19 as images. Figures 1.7, 1.8, 1.10, 1.15, 1.16 and 1.18 were not opened. I checked the chapter against:
- every line of intro_figs.log;
- ch1_intro_figures.py (the chance and CFAR code, DET, PROBLEM, SETS, the scoring code and Figure 1.3 panel E);
- the GLOSSARY sections on two axes, K, MAHICE, bench and simulation, and synthetic validation;
- the docstrings of theory_floor.py and assessor_jitter.py.

I also checked:
- every section and table cross-reference inside the chapter;
- every table against the text and figures (Tables 1.1, 1.3, 1.4, 1.5, 1.6 and 1.7 against Figures 1.11, 1.12, 1.14 and 1.19);
- by hand: the worked F example (+3, +5, −3, −5; F = 0.67), c = 0.376, C = 0.65, g₂ = ½ at 2.08σ, the HWHM factor of 1.67, the sign-test p = 0.007 for 24 of 32, and the chance floor of 6 cells at 0.0096 Hz from the 1.2.3 formula.

Most numbers reconcile. The findings are below.

Each finding gives its location, the issue, a severity, a suggested fix, and whether I could verify it against a source.

## A. Contradictions inside the chapter

**A1. Contribution 3 (l.664–666), the summary of 1.5 (l.692–693), 1.5.6 (l.902) and 1.5.7 (l.959) overstate where the joint fit works.**
- **Issue:** These passages say the joint fit "recovers jitter … for events of 10 or more cells and jitter of 0.2 s or more", and l.959 calls 0.2 s a "resolved" column. Figure 1.12 and its caption (l.973–975) say otherwise. 10 cells at 0.2 s is resolved on the first experiment only (held-out 0.98–1.36). "On both records … the 10-cell row [is resolved] from 0.5 s." The chapter's own rule (l.632–633) is that the held-out value is the one to trust. So the claim holds for 20 cells from 0.2 s and for 10 cells from 0.5 s.
- **Severity:** Major. This is a headline contribution.
- **Fix:** Restate the claim as "20 cells from 0.2 s, 10 cells from 0.5 s (both records)". At l.959, say the 0.2 s column is resolved only at 20 cells.
- **Verified:** Yes (figure, caption and text).

**A2. 1.8.2, l.1344–1345: the median recording window is described three ways.**
- **Issue:** This line says "the median recording window holds one to three (*1.3.1*)". Section 1.3.1 gives medians of 1 (fast) and 2 (slow). The rest of the chapter says "1–2 events" (l.644), "one or two events" (l.1070) and "one fast or two slow" (l.1002).
- **Severity:** Moderate.
- **Fix:** Change it to "one or two".
- **Verified:** Yes.

**A3. 1.3.4, l.415–419 against Figure 1.3 E: two different bases for "chance".**
- **Issue:** The text defines chance as "background alone … rate b" (0.0096 Hz), then quotes "chance puts at least 8 cells in a 1 s bin in a share 2 × 10⁻⁸". The script (l.550–552) and the log (l.28–30) compute that chance at the sets' mean onset rate, 0.0147 Hz, which includes the coordinated onsets. The panel legend says so too. At b = 0.0096 Hz the share would be about 10⁻⁹. The Figure 1.3 caption says only "chance level for independent cells".
- **Severity:** Moderate. One quantity is counted on two bases.
- **Fix:** Say in the text and caption that chance is taken at the mean onset rate (0.0147 Hz), or recompute it at b.
- **Verified:** Yes (script and log).

**A4. 1.3.3, l.367–369: measured shares quoted as if they were g₂.**
- **Issue:** The sentence introduces g₂, then says "a 0.2 s window holds 0.48 … 1 s 0.87; jittered 0.10 and 0.47". Those are the measured excess-pair shares, which include the hard-core term. The g₂ values in the log are 0.49 and 0.89, and 0.11 and 0.49.
- **Severity:** Minor.
- **Fix:** Label the numbers as "measured", or quote g₂.
- **Verified:** Yes (log l.21–27).

**A5. 1.3.3, l.370–371: "At 4 s and 8 s the measured share turns down" is true only for the sharp set.**
- **Issue:** The sharp set goes 0.91 → 0.90 → 0.84. The jittered set is flat at 0.81 and 0.81 (log l.25; Figure 1.3 D).
- **Severity:** Minor.
- **Fix:** Say "turns down (sharp) or levels off (jittered) instead of approaching 1".
- **Verified:** Yes.

**A6. Merge-gap rule, l.92–93 against l.157 and l.437.**
- **Issue:** 1.2.1 joins calls when the gap is "at most … 3 s", as does the script's `runs_to_calls` (`<= merge_gap`). The Figure 1.2 caption and 1.3.4 say "less than 3 s apart". This does not matter with 2 s bins, but the rule is stated two ways.
- **Severity:** Minor.
- **Fix:** Use one wording.
- **Verified:** Yes.

**A7. 1.1, l.61–62: the 1.2 roadmap names the wrong recording.**
- **Issue:** "Section 1.2 tries the obvious detectors on Figure 1.1's problem". Section 1.2 actually runs them on a different, designed recording (Figure 1.2: 4 min, 0.0096 Hz with a 0.05 Hz stretch). Figure 1.1 is 2 min at a uniform 0.05 Hz.
- **Severity:** Minor.
- **Fix:** Say "on a recording like Figure 1.1's, built to show…".
- **Verified:** Yes (PROBLEM and DET in the script).

**A8. 1.5.7, l.999–1000: two thresholds for "readable".**
- **Issue:** For the joint fit, "from two events" means 39–40 of 40 in the band. But the tool's 1 s estimate "from one" event includes slow 13 at E = 1, which is 35 of 40 (Table 1.5).
- **Severity:** Minor.
- **Fix:** State one threshold, or qualify the slow-stream case.
- **Verified:** Yes.

**A9. Table 1.4 note (l.989) and the l.1311 area: the bound applies only to the fast stream.**
- **Issue:** The note says "A jitter ratio of 0.05 is the fit's lower bound". That holds only for the fast stream. For the slow stream the bound is 0.005/0.131 = 0.038, and Figure 1.11 C draws the slow-stream bound points there.
- **Severity:** Minor.
- **Fix:** Write "0.05 (fast) or 0.04 (slow)".
- **Verified:** Yes (figure).

## B. Stale cross-references (left over from the renumbering)

**B1. "Reproducing this chapter", l.1585: `blind_a/theory_floor.py # event floor, 1.5.1`.**
- **Issue:** The event floor is now in 1.6.1, and 1.5.1 is "The undercount". The script's docstring calls itself the "ADR-0008 chance floor, analytic: up-crossing rate of the sliding-window … count", which is the 1.2.3 formula.
- **Severity:** Moderate.
- **Fix:** Change the label to "1.2.3, 1.6.1".
- **Verified:** Yes.

**B2. Same section, l.1596: `assessor_jitter.py # 1.5.2, Table 1.6`.**
- **Issue:** The assessor jitter reading is now 1.6.2, and 1.5.2 is window sharing.
- **Severity:** Moderate.
- **Fix:** Change it to 1.6.2.
- **Verified:** Yes.

**B3. Same section, l.1583: `theory.py --from-record # prints 1.1 and 1.4 numbers`.**
- **Issue:** Under the new numbering 1.1 is the introduction, which quotes no first-experiment numbers. This label is almost certainly stale (probably 1.4 and 1.6 now). theory.py has no section labels to confirm it against.
- **Severity:** Moderate.
- **Fix:** Check the label and update it.
- **Verified:** Partly (stale by structure; the target is not confirmed).

**B4. Companion file `ch1_followups/assessor_jitter.py`, docstring l.40: "pooled the way Figure 1.1 D/H".**
- **Issue:** That figure is now Figure 1.6 D/H. This is out of the artifact's scope, but the chapter points readers to that script.
- **Severity:** Minor.
- **Fix:** Update the docstring when the scripts are next touched.
- **Verified:** Yes.

**B5. 1.6.1, l.1089 and 1.9.1, l.1434: "π_K … derived exactly in *1.7*".**
- **Issue:** Section 1.7 states that the plateau π_K² "is derived exactly", but gives no π_K formula and no pointer to one. A reader following the cross-reference finds a claim, not the derivation.
- **Severity:** Minor.
- **Fix:** Point to the separation record, or give the formula.
- **Verified:** Yes.

## C. Terminology and reserved words (against the GLOSSARY)

**C1. "quiet background" and "busy" are reserved terms (l.125–126, l.169 Table 1.1 header, l.184; "busier", "quieter" throughout).**
- **Issue:** The glossary's **background** entry fixes *quiet* = 0.0052 and *busy* = 0.019 Hz, and says "'the quiet background' always means this". The **Aim 1a backgrounds** entry warns that 0.01 and 0.05 Hz "are not the bench's quiet and busy regimes". The chapter uses "quiet" for 0.0096 Hz and "busy" for 0.05 Hz.
- **Severity:** Moderate.
- **Fix:** Use "the 0.0096 Hz background" and "the 0.05 Hz stretch", or a pair of terms the glossary does not reserve (for example "lower" and "higher").
- **Verified:** Yes.

**C2. New terms that are not in the glossary.**
- **Issue:** The chapter introduces these terms in bold or as defined terms: **chance floor**, **false call**, **recording window**, **hard-core form**, **general form**, **held-out record**, **cluster-start factor**, **refused**, **sharp set** and **jittered set**. A grep finds none of them in the GLOSSARY. The checklist rule is that a new term is added in the same change. Two of them also collide with existing words:
  - "false call" sits beside the glossary's "false alarm" (glossary l.383, l.428), and the chapter itself uses "false alarm" in 1.2.3 and 1.7.
  - "chance floor" sits beside "event floor" (ADR-0008), and theory_floor.py calls ADR-0008's floor the "chance floor".
- **Severity:** Moderate.
- **Fix:** Add the entries. Settle "false call" against "false alarm", and "chance floor" against "event floor".
- **Verified:** Yes.

**C3. "window" carries too many meanings; "recording-windows" (l.623) collides with "recording window" (l.225).**
- **Issue:** "Refused in 17 of 720 recording-windows" means recording × tool window (240 × 3). Section 1.3.1 defines **recording window** as the lab's 20-minute baseline stretch, and 1.5.7 uses both senses within lines of each other ("one 20-minute window", "1 s window"). Reference windows and sliding windows add two more senses.
- **Severity:** Moderate.
- **Fix:** Use "recording × window pairs" (or "condition-windows" style) at l.623 and nearby, and keep "recording window" for the 20-minute stretch only.
- **Verified:** Yes.

**C4. Symbols p, w and K are reused (l.113–118 against Table 1.2, l.256 and l.259).**
- **Issue:**
  - In 1.2.3, p = 1 − e^(−bw), the chance one cell is active. Table 1.2 defines p = λw, events per window. p is also used for p-values.
  - In 1.2, w and K are the 2 s detector window and detector threshold. Table 1.2 defines w as the coordination-rates tool's window and K as the assessor's threshold.
  - B (bin width, l.416) and h (lag bin, l.295) are missing from Table 1.2, and B is also a panel letter.
- **Severity:** Moderate. The defects are p and B.
- **Fix:** Rename the 1.2.3 probability (for example p₁ or a), widen the Table 1.2 rows for w and K, and add h and B.
- **Verified:** Yes.

**C5. "cell" in its radar sense inside a section about cells (1.2.3, l.129–137).**
- **Issue:** "Reference cells", "cell under test" and "guard cells" sit in a paragraph whose cells are ROIs. The glossary flags this as a third sense of "cell". The chapter never says that, here, a "cell" is a stretch of time.
- **Severity:** Minor.
- **Fix:** Add one clause: "(in radar, a 'cell' is a stretch of range or time, here of time)".
- **Verified:** Yes.

**C6. Bare "settings" (l.64; also l.546).**
- **Issue:** The glossary retires bare "settings". At l.64, "every detector needs settings" does not say which kind. At l.200 the context does say which.
- **Severity:** Minor.
- **Fix:** Write "detector settings".
- **Verified:** Yes.

**C7. The GLOSSARY entry "coordinated onset rate per cell" disagrees with the figures.**
- **Issue:** The entry says the quantity is "labeled 'coordinated share' in the Chapter 1 figures". Figure 1.6 C/G labels it "coordinated onset rate recovered ÷ planted". This is the companion doc going stale, not the chapter. I did not open Figure 1.8.
- **Severity:** Minor.
- **Fix:** Update the glossary.
- **Verified:** Yes (Figure 1.6).

## D. Figures against text, and order across figures

**D1. Cell order on the raster axes differs between figures.**
- **Issue:** Figures 1.1, 1.2 and 1.3 A/B put cell 1 at the bottom and 33 at the top. Figure 1.5 A puts cell 1 at the top and 33 at the bottom, and Figure 1.4 A/B lists cell 1 first at the top.
- **Severity:** Minor.
- **Fix:** Use one orientation for all rasters.
- **Verified:** Yes.

**D2. Figure 1.4 A caption (l.398–399), 1.3.3 (l.384) and the figure's axis note: the offsets are not multiples of two windows.**
- **Issue:** The offsets are "distinct multiples of two windows … here −6, −2, +2 and +6 s for a 2 s window". Two windows is 4 s, and none of these is a multiple of 4. The figure's own note says "centered", which explains it, but the caption and text leave that out.
- **Severity:** Minor.
- **Fix:** Write "distinct multiples of two windows, centered on zero (so half-multiples when N is even)".
- **Verified:** Yes.

**D3. Figure 1.3 E against l.419: the quoted value cannot be seen.**
- **Issue:** The text quotes the chance share at ≥ 8 cells, 2 × 10⁻⁸. The panel's axis stops at 10⁻⁷, and the chance line leaves it at about K = 7.5. This is also tied to A3.
- **Severity:** Minor.
- **Fix:** Extend the y-axis to 10⁻⁹, or quote K = 7.
- **Verified:** Yes.

**D4. 1.2.4 situation 2 (l.183): numbers that the log does not print.**
- **Issue:** "Raise its threshold near event 2 to 7 or 8 cells in most draws (8 and 9 in the one drawn)". The log prints only the ranges for the quiet and busy stretches. The "8 and 9" match Figure 1.2 D by eye. The "7 or 8 in most draws" figure is printed nowhere, though the script's docstring promises "Every number the chapter quotes from these figures is printed by this script".
- **Severity:** Minor.
- **Fix:** Print it, or drop it.
- **Verified:** No ("8 and 9" is checked by eye only).

**D5. Figure 1.14 caption (l.1134) against l.1141–1142: two numbers for the event-only ceiling.**
- **Issue:** The caption says the event-only curve "levels off near 0.74 s". The text gives a ceiling of 0.743 s at σ = 1. In panels B–D the curve keeps rising past σ = 1, to about 0.8.
- **Severity:** Minor.
- **Fix:** Write "0.74 s at σ = 1 s".
- **Verified:** Yes.

## E. Items checked that reconcile (no action)

- **Figure 1.1:** 190 + 40 onsets; 4 events × 10 cells.
- **Table 1.1:** matches the log exactly, including "17 of 200" and seed 1011.
- **Draw shown in Figure 1.2:** the found, missed and false-call marks match the log (fixed 3 of 6 found, 2 false calls; sliding 5 of 6, 3; CFAR 3 of 6, 0). CFAR is 9–12 cells in the 0.05 Hz stretch. Peak bin counts are 13, 4, 10, 11 and 5.
- **Chance floor:** 6 and 12 cells, also asserted in the script at 0.01 Hz.
- **Correlogram:** 18.2/18.5 and 0.176/0.174/0.167 s; 4.6/4.8 and 0.796/0.835 s (5 % narrower).
- **Bin shares:** 0.015, 0.0044, 0.017 and 0.019.
- **Sign tests and residual counts (Figure 1.9):** 7/17 and 10/10 beyond 2 SE; 12 + 12 of 16 below predicted.
- **Table 1.3 against Figure 1.11 A/B:** off-curve counts 8, 15, 15, 2 and 3/5.
- **Table 1.4 against Figure 1.11 C and Figure 1.12:** at the bound 21/11/4/1; in band 2/8/18/16.
- **Figure 1.12 ranges against 1.5.6:** 0.88–1.13 and 0.86–1.36.
- **Table 1.6 against the l.1140–1153 claims:** within 0.015 s, 0.006 s, 0.02 s and 0.03/0.036 s, as stated.
- **Figure 1.13** labels against 1.6.1; **Figure 1.17** against 1.8.1 (72 %, 13 %, 1 and 3 of 60, ratio 1.04).
- **Table 1.7 against Figure 1.19:** all 48 values match.
- **Pooled rates:** 9.7/22.0 per hour ↔ 7.3/16.5 per recording ↔ 3.2/7.3 per window; the 25.5 and 53.6 runs ≈ 3.5× and 3.3×.
- **Fraction of chance clusters:** 0.33 ÷ 1.33 = a quarter.
- **Figure 1.6 D/H** against the l.575–578 readings.
- **Section and table cross-references** in the body (as opposed to "Reproducing") all resolve, apart from B5.
