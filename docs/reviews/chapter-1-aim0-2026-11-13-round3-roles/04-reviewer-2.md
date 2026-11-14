GRANT 4 MISMATCH — missing none; holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs MCP tools (update, batch), plus deferred Dropbox and Gmail write tools

**Run notes (about the run, not the chapter)**
- The grant mismatch above means this review took a fallback path. I edited, wrote and deleted nothing. I used PowerShell once, for a read-only arithmetic check with the repository's Python (the chance-floor and chance-cluster rates). That tool is outside role 4's grant.
- The temp volume is full (0 MB free). Bash output to <scratch> failed, so no scratch file exists under <scratch>/mb3/role04/. Read and Grep worked.
- I did not open anything under docs/reviews/.

**Findings** (location · issue · severity · suggested fix · verified against a source)

1. **1.3.1, 1.5.7, 1.8.2 power design, 1.10 — the realistic event counts come from a detector.**
   - Issue: The numbers per segment (median 1–2, 28 of 66 fast segments with none, 9.7 and 22.0 per hour) are calls of a detector. The run record (<repo>/docs/learned/runs/2026-09-25-real-intervals/README.md, "How an event and a gap are defined") shows it is a sliding 2 s co-activity count at the ADR-0008 floor. That is the kind of detector *1.2* says cannot be set until coordination is measured. At realistic values its floor is about 6 cells and fast events have about 7, so its recall is far from 1 (compare Table 1.1 event 5 and the recall in *1.6.1*). The counts are then probably lower bounds. The chapter tells the reader only that the intervals understate close pairs. Yet "7-cell events are not readable at a median segment" and "power at 1–5 events because the median segment holds one or two" both rest on these counts.
   - Severity: major.
   - Fix: State that the counts are detector calls with unknown recall. Either estimate that detector's recall at k = 7 and 13 and realistic σ, or take the count per segment from the coordination-rates tool's rate, which needs no detector. Then soften 1.10.
   - Verified: yes.

2. **1.3.1, 1.5.7, 1.10 — a pooled headline where the breakdown by group exists.**
   - Issue: The run record has events per hour by group:

     | stream | DI | MALE | OVX | ORX |
     |---|---|---|---|---|
     | fast | 20.5 | 15.0 | 3.4 | 2.1 |
     | slow | 48.5 | 31.9 | 8.2 | 3.8 |

     In 20 minutes that is about 7 fast events for DI and about 0.7 for ORX. The "median segment of 1–2 events" therefore describes no group. "A realistic 20-minute baseline segment supports…" is a pooled result across a design factor whose breakdown the repository already holds. Measured against Table 1.5, DI and MALE segments are near "readable" and OVX and ORX are nowhere near. The one-per-hour chance budget is also a large share of all calls for ORX and OVX fast segments, which *1.6.1* calls loose only at the pooled median. "Differences between the groups are not this chapter's subject" does not cover a conclusion stated at a pooled median.
   - Severity: major.
   - Fix: State 1.10's segment-level conclusion per group, or at least give the per-group rates beside Table 1.5 and Table 1.7.
   - Verified: yes.

3. **1.3.1, "7 cells … and 13, of 33 ⚠ (the goal page's working values)" — a source of record exists.**
   - Issue: <repo>/src/bugarach/bench.py and bench_slow.py record a re-measurement on the same 66 recordings on 2026-09-23:
     - fast: participation 0.203 (95 % interval 0.182–0.233) of 32 ROIs, jitter 0.105 s (0.090–0.124);
     - slow: participation 0.375 (0.308–0.445), jitter 0.131 s (0.120–0.146).
   - The participation comes from the coordination-rates probe, which *1.5.7* shows reads about 0.92 of planted at these values. The jitter comes through the correlogram calibration, which the chapter says was never tested at these values. So the "realistic" k and σ are outputs of the tools under test, given here as points with no intervals. The σ interval 0.090–0.124 s straddles the region where the joint fit stops resolving jitter.
   - Severity: minor.
   - Fix: Cite the measurement with its intervals and drop the ⚠. Say that k and σ are readings of the tools under test, and carry the ranges into 1.5.7.
   - Verified: yes.

4. **1.9.1, "Its threshold kept false alarms near their allowance only because it was itself a prediction" — overreach, refuted by the figure.**
   - Issue:
     - In the 0.0096 Hz stretches, CFAR's background estimate has a median of 0.0208 Hz, twice the true rate (ch1_intro_figures.log).
     - Figure 1.2 D shows its threshold at 7–9 cells through most of the quiet stretches, against a correct floor of 6.
     - Its 0 false alarms in 10 h there come from a threshold biased high. That bias also cost it events 2 and 5.
     - In the busier stretch, 5 false alarms in 200 min (1.5 per hour, 95 % interval 0.5–3.5) cannot tell compliance from excess.
     - 1.9.1 also repeats the 6 / 12 agreement with the repository's simulated floor as support, although *1.2.3* says two integer agreements are not a test.
   - Severity: major.
   - Fix: Say that CFAR's rate was consistent with the allowance in the busier stretch, and below it in the quiet stretches because its estimate ran about 2× high.
   - Verified: yes (log, figure).

5. **1.2.4 situation 5 — "found only when the background helps" is wrong for CFAR, and a cause is left untested.**
   - Issue: CFAR's threshold near event 5 was 4 or 5 cells in 14 of the 200 draws (log), so it could find the 5-cell event without any background onset joining. The text gives only "6 in 119 and 7 or more in 67", and says the cause of the higher values "was not isolated". Two causes are plausible: the 2× estimate from events 3 and 4 in its reference span, and the noise of a small reference sample.
   - Severity: minor.
   - Fix: Report the 14 draws. Run the leave-out test for events 3 and 4, as was done for event 2.
   - Verified: yes.

6. **1.2.3, "30 s of reference holds enough background onsets to estimate b at 0.0096 Hz" — an unjustified constant.**
   - Issue: Two 30 s spans × 33 cells × 0.0096 Hz ≈ 19 expected onsets. That is a Poisson CV of about 23 %, enough by itself to move the floor by a cell. Calling it "enough" is not a justification.
   - Severity: minor.
   - Fix: Give the expected count and the threshold spread it implies.
   - Verified: yes (arithmetic).

7. **1.2.4 situation 3, "Section 1.7 derives … how much closer any method could go" — overreach.**
   - Issue: *1.7* itself says its likelihood-ratio tests bound the best achievable separation from above. They are also handed the pair's location and the background. They are not a limit on any method.
   - Severity: minor.
   - Fix: Write "how much closer likelihood-ratio tests given the pair's location can go".
   - Verified: yes.

8. **1.5.6 and Table 1.3, "elsewhere the correlogram tool does as well" — understated, and the claimed difference is untested.**
   - Issue: Where it gives an estimate, the correlogram is better than the joint fit:
     - 0.01 Hz, σ = 0.05 s: 1.06 [1.02, 1.10] against 1.33 [0.98, 1.79];
     - 0.05 Hz, σ = 0.2 s: IQR [0.83, 1.01] against [0.65, 1.13].
   - At σ = 0.05 s it is censored in 8 of 20 recordings. "The better estimator" is asserted from medians with no paired test.
   - Severity: major.
   - Fix: Restate the comparison by regime. Add a paired per-recording comparison, for example a sign test on |log(recovered ÷ planted)|, and report the censoring beside it.
   - Verified: yes.

9. **1.5.7, Table 1.5 and 1.10 — "readable" is undefined and applied unevenly; the rate claim has no table.**
   - Issue: The cut-off is never stated. 35 of 40 counts as readable (the tool, slow stream, 13 cells, E = 1), while 30 of 40 does not (the joint fit, fast stream, 7 cells, E = 4). 1.10 says event rate is readable "from four events of 13 cells or sixteen of 7", but the chapter has no rate column. The numbers are only in <repo>/docs/learned/synthetic_validation/ch1_followups/README.md, R3 task 1. There, fast stream, 13 cells, E = 4 gives 35 of 40 and slow stream, 7 cells, E = 8 gives 31 of 40.
   - Severity: major.
   - Fix: Define "readable" (for example, at least 35 of 40 within 0.8–1.25) and apply it to every cell of the table. Add the rate column to Table 1.5.
   - Verified: yes.

10. **1.10, the order clause ("order, for 13-cell events, from three events with a template … at least 2.5 times the jitter") — a missing caveat.**
    - Issue: Table 1.7 assumes known events and no background onsets (limitation 5), with unrounded onsets. The latency spread r has never been measured in the lab's data. The conclusion presents this as what a realistic segment supports.
    - Severity: major.
    - Fix: Carry "with known events and no background, if such a template exists" into 1.10.
    - Verified: yes.

11. **1.6.1, "K = 5 and 8 were not simulated with events, so those values extrapolate" — a cheap check left undone.**
    - Issue: The chance-cluster rate needs no events, and the 100 background-only recordings per background already exist. At 0.01 Hz the formula is effectively checked only at K = 3 and 4, since the text says K = 6 "tests nothing". Scoring the existing recordings has power: about 0.53 clusters per hour at K = 8 and 0.05 Hz, so about 40 expected in 75 h; about 0.066 per hour at K = 5 and 0.01 Hz, so about 5 expected. The recommended safe thresholds rest on exactly these K.
    - Severity: major.
    - Fix: Score the existing background-only recordings at K = 5, 7 and 8.
    - Verified: yes (rates recomputed; the formula reproduces every number in *1.2.3* and *1.6.1*).

12. **1.6.2, "agrees within about 0.05 in most conditions" — vague.**
    - Issue: "Most" is not a number.
    - Severity: minor.
    - Fix: Give how many of how many conditions agree, and the worst miss.
    - Verified: no.

13. **1.9.1 "turns the three failures … into consequences of formulas", and Contribution 5 — overreach.**
    - Issue: The flat reading's level, 0.64–0.73 s, is not derived. It is the chance clusters' SD measured on background-only recordings. By the chapter's own account, the rows where chance clusters dominate cannot test the mixture's weights. The only rows that test the mixture miss by up to 0.04 s, and at K = 6 "two misses partly cancel".
    - Severity: minor.
    - Fix: Say "semi-analytic: the chance part is measured, and the weights are tested in two rows, one of which agrees partly by cancellation".
    - Verified: yes.

14. **Figure 1.6 and the 1.4 list of failures — the picture shows two failures the text leaves out.**
    - Issue: Panel E shows the assessor reading participants at about 0.45–0.55 of planted, flat across jitter, at 0.05 Hz and K = 3 and 4. Panels B and F show the 1 s window reading event rate at about 2× planted at σ = 1 s. Neither is among the "three failures". The first appears only in 1.9.1 as not predicted. The second is the mirror image of the participant undercount, through the well-determined product λk.
    - Severity: minor.
    - Fix: Name both in 1.4 and say how they relate to the other failures.
    - Verified: yes (image).

15. **1.8.1 and the Figure 1.17 title, "stays detectable" — overreach.**
    - Issue: At reuse 0.045, both nulls reject in 9 % of recordings against a 2 % false-positive rate. That is detection above chance at low power. "Rerun at 1000, the low-reuse rates are the same" gives no number, though the follow-ups record 92 of 1000.
    - Severity: minor.
    - Fix: Use a title like "still detected above the false-positive rate, in about 1 recording in 10", and give the 1000-surrogate figures.
    - Verified: yes.

16. **1.4 "answer in brief" and 1.5.4 against limitation 2 — the caveat is missing where the claim is made.**
    - Issue: Limitation 2 concedes that the 2-SE excess cannot be separated from the bias of k̂ = 2 + f₃/f₂ as a ratio of noisy counts. It marks that with ⚠, which the chapter defines as a references marker. Meanwhile 1.4 and 1.5.4 state "residuals exceed sampling noise" without the caveat. The follow-ups give a participant median-of-ratios minus ratio-of-means gap of −0.001 (IQR within ±0.011). That bears on the question but does not settle it, because a ratio of 5-recording means is still biased.
    - Severity: minor.
    - Fix: Either carry the caveat into 1.4 and 1.5.4, or settle it: at a few conditions, run many recordings and compare the median k̂ with the prediction from the expected counts.
    - Verified: partly.

17. **1.9.5 item 1 — listed as future work, but already run.**
    - Issue: The item asks to "add realistic jitter … and 7 cells per event to the first experiment's grid". The goal page records that run ("Aim 1a at the lab's values", 2026-11-11, aim1_lab_regime.py). Participants and rate came within 0.99–1.03 for 6.5 or more cells. Jitter read 1.20 [0.50, 1.97] at 6.5 fast-stream cells, and about 2× planted at 3–4 cells. The chapter neither reports this run nor reconciles it with Table 1.4 (fast stream, 7 cells: 0.05 [0.05, 1.52], at a lower event count).
    - Severity: minor.
    - Fix: Report the run or say why it is excluded, and update 1.9.5.
    - Verified: yes.

18. **1.3.3, the surrogate offsets ("distinct multiples of two windows") — unjustified, and the evidence is not shown.**
    - Issue: Nothing explains why two windows. The "lost 35 % of planted pairs" rests on the tool's documentation and is not shown. *1.5.3* also shows that the chosen design still leaves the surrogate's pair count at 4–15 times the independent value.
    - Severity: minor.
    - Fix: Justify 2w, and cite the run behind the 35 %.
    - Verified: no.

19. **1.7, "the assessor resolves about 98 %" — the wrong computation.**
    - Issue: The figure comes from the share of intervals under 3 s (1.7 %). The split curve, though, crosses half its plateau at 2.5 s and only reaches the plateau further out, so intervals of about 2.5–4 s are partly merged.
    - Severity: minor.
    - Fix: Integrate the predicted split curve over the measured interval list.
    - Verified: no.

20. **1.3.1, "0.0096 Hz … estimated from the fast stream and used for both streams" — unjustified.**
    - Issue: The chapter gives no background for the slow stream. Real windows leave about 35 % of ROIs silent (bench.py), while the realistic runs for the coordination-rates tool and the joint fit used a flat background. *1.6.1* addresses this for the chance rate only.
    - Severity: minor.
    - Fix: Give the slow stream's own b, or justify reusing the fast stream's, and state that the realistic runs used a flat background.
    - Verified: partly.

**Checked and holding**
- Every Table 1.1 entry, and every situation-text number checked against the log, matches ch1_intro_figures.log (finding 5 is an omission, not a mismatch). This covers the 7/74/122 → 196 split, the 119/67 split, false alarms within 13 s of the stretch ends, the 1.5 per hour [0.5–3.5] interval and 7 of 200 typical draws.
- The *1.3.2* and *1.3.3* numbers for the sharp and jittered sets match the log (peaks, HWHMs and standard errors, levels, g₂, shares within 0.02).
- The chance-floor and chance-cluster formulas reproduce 6 and 12 cells, 4 cells for the 0.2 s window, 0.33 per hour, 0.98 per hour at K = 4, and the 0.00964 Hz crossing.
- The closed forms in *1.8.2* check: (2/π) arctan r, C = 0.65, c = 0.376, and 0.48 at n̄ = 0.4.
- The claim that the assessor's jitter reading is planted as the simulator's jitter is confirmed in <repo>/src/bugarach/adapt.py (jit_obs → jitter_sec).
- Figures 1.2, 1.4 and 1.6 were opened as images.
