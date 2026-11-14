GRANT 4 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, Monitor and MCP doc/Dropbox and Gmail tools (Edit and Write are editing tools no reviewer may hold; none of them was used, and nothing in the repository was changed. Scratch work is only in <scratch>/mb2/role04/)

# Reviewer 2 (role 4): adversarial review of chapter-1-aim0.md (blob 0acfccbb)

Scope: I read the whole chapter. I opened Figures 1.1, 1.2, 1.4, 1.9, 1.12 and 1.16 as images. I read ch1_intro_figures.py and its log, src/bugarach/event_floor.py, the simulate_coordination docstring, ch1_followups/dependence_null.py (header) and membership_repeat.txt. I also re-ran the chapter's own `detector_runs` under three controls (script: <scratch>/mb2/role04/cfar_ctrl.py, 60 draws per arm, 40 for the separation sweep). I did not open anything under docs/reviews/.

Control results, used below. Rows are the share of draws in which each detector found the event:

| arm | fixed bins | sliding window | CFAR |
|---|---|---|---|
| baseline, event 2 / event 5 | 0.33 / 0.47 | 1.00 / 0.65 | 0.38 / 0.53 |
| events 1 and 3 removed, event 2 / event 5 | 0.33 / 0.52 | 1.00 / 0.65 | **0.98** / 0.57 |
| busier stretch set to 0.0096 Hz, event 2 / event 5 | 0.42 / 0.45 | 1.00 / 0.52 | 0.38 / **0.60** |
| situation 3 at 4 s apart, both found | 0.00 | 0.00 | 0.00 |
| situation 3 at 5 s apart, both found | 0.875 | 0.25 | 0.30 |

## Findings

Each finding gives: location · issue · severity · suggested fix · verified against a source.

**1. 1.2.4 situation 3 heading, 1.2.4 closing paragraph ("The merge gap must be shorter than the gap between events, or it joins them"), and 1.10 ("a merge gap shorter than the interval between events")**
- **Issue:** The stated design rule is false, and the chapter's own example refutes it.
  - In situation 3 the merge gap (3 s) is *shorter* than the separation (4 s; `DET` events at 81.0 and 85.0 s), yet every detector merges the pair in every draw.
  - The heading "A merge gap longer than the gap between events joins them" therefore misdescribes the planted case. The body sentence ("the runs of called counts are less than 3 s apart") shows that what matters is the gap between calls, which the bin or window width extends.
  - In my control, at 5 s separation the sliding window still merges 75 % of pairs and CFAR 70 %.
  - Section 1.7 itself puts the count detector's half-point at (m + ½) bin widths ≈ 5 s, and Figure 1.16 A shows the count detector reporting two in 0 % of pairs at 4 s.
  - The rule is repeated as a conclusion in 1.10.
- **Severity:** major (a wrong rule repeated in the Conclusion).
- **Fix:** Restate the rule as "the merge gap plus the bin or window width must be shorter than the separation," or cite 1.7's (m + ½)-bin result. Retitle situation 3, for example: "A merge gap joins events whose calls, widened by the window, fall within it."
- **Verified:** yes (script `DET`, my control, Figure 1.16).

**2. 1.7 opening: "Situation 3 of Figure 1.2 showed two events 3 s apart"**
- **Issue:** They are 4 s apart (1.2.4, Figure 1.2 caption, `DET`).
- **Severity:** minor (factual).
- **Fix:** Change to 4 s.
- **Verified:** yes.

**3. 1.6.1 "This explains the third failure of *1.4*" and 1.6.2 "This is the second failure of *1.4*"**
- **Issue:** The numbers are swapped. In the 1.4 list, failure 2 is the fixed threshold and chance clusters, which 1.6.1 explains, and failure 3 is the flat jitter reading, which 1.6.2 explains.
- **Severity:** minor (cross-reference error).
- **Fix:** Swap "third" and "second".
- **Verified:** yes (1.4 list).

**4. 1.3.4: "A threshold high enough to sit far above chance therefore misses most jittered events."**
- **Issue:** This overreaches, because it rests on an arbitrary K = 8.
  - The chapter's own safe threshold for 1 s bins at this background is K = 4–5 (1.6.1). At K = 5, 442 of 450 jittered events still reach threshold (log line 28).
  - So "far above chance" here means three cells above the one-per-hour floor, chosen without justification.
  - `events_reaching` also counts background cells within ±1.5 s, not only the event's participants, so "put at least 8 cells" is not exactly what was counted.
- **Severity:** major (an overreaching inference on an unjustified constant).
- **Fix:** Tie the claim to the safe threshold, or state why K = 8. Say that the count includes background cells.
- **Verified:** yes (log, script).

**5. 1.2.4 situation 4: CFAR "makes 0.03 false alarms per minute (1.5 per hour), above the one-per-hour allowance … four of the five false alarms fall within 13 s of its ends"**
- **Issue:** The statistic is fragile.
  - It rests on 5 events in 200 min. The exact Poisson 95 % interval for 5 counts is 1.6–11.7, or about 0.5–3.5 per hour, so "above the allowance" is not established.
  - The edge attribution rests on 4 of 5 events and was not tested by a control.
  - "CFAR raises its threshold to 10–12 cells in that stretch" comes from the one draw shown (log line 17), not from the 200 draws.
- **Severity:** moderate.
- **Fix:** Give the interval and say "consistent with the allowance; too few to tell." Report the threshold range over all draws, or mark it as the draw shown.
- **Verified:** yes (log).

**6. 1.2.4 situation 5: CFAR finds event 5 in 49 % because "event 5 sits just after the busier stretch, whose onsets still fall in its reference stretches, so its threshold there is 6 cells in 119 draws and 7 or more in 67"**
- **Issue:** The causal attribution is not supported.
  - A threshold of 6 is simply the analytic floor at the true 0.0096 Hz (1.2.3), not an elevation.
  - In my control, setting the busier stretch to 0.0096 Hz moved CFAR's event-5 recall only from 0.53 to 0.60 (n = 60, within noise).
  - By contrast, the situation-2 masking claim does hold: removing events 1 and 3 lifts CFAR's event-2 recall from 0.38 to 0.98. The chapter could cite that as its evidence for masking, which it currently only asserts.
- **Severity:** moderate.
- **Fix:** Drop or soften the busier-stretch explanation for event 5. Add the events-removed control as the evidence for masking at event 2.
- **Verified:** yes (my re-run of the chapter's functions).

**7. Figure 1.2 panel A and caption ("The draw shown is one of 200 …"); text below Table 1.1**
- **Issue:** The single draw presents near coin-flip outcomes as verdicts.
  - Three of the shown marks are "most common" outcomes at 0.41 (fixed bins, event 5), 0.45 (CFAR, event 2) and 0.49 (CFAR, event 5). A reader sees a firm red "missed".
  - The shown draw is also one of only 7 of 200 that are typical on every outcome. The text discloses that, but the figure does not.
- **Severity:** moderate.
- **Fix:** Mark outcomes whose share lies within 0.35–0.65 in panel A (for example, a hollow marker), or print each share beside its mark.
- **Verified:** yes (log, picture).

**8. 1.2.3: CFAR estimates b "from the onsets in the 30 s on either side of each instant, leaving out the 5 s nearest it"; 1.2.4: "CFAR's 70 s reference span"**
- **Issue:** The quantity is defined ambiguously, and the constants are unjustified.
  - The code uses 30 s *beyond* a 5 s guard, so the reference runs 5–35 s on each side (`local_rate`). The sentence reads as 25 s of reference per side. Only the code makes the "70 s span" consistent.
  - Neither 30 s nor 5 s is justified, yet events 1 and 3 sit 31–35 s from event 2, inside the reference, by design. That placement drives the situation-2 result.
  - The ±1 s scoring tolerance and the 3 s merge gap ("the repository's setting") are also given without a reason.
- **Severity:** moderate.
- **Fix:** Say "30 s beyond a 5 s guard". State why each constant was chosen, and say that the event placement was chosen to put events 1 and 3 in event 2's reference.
- **Verified:** yes (script lines 179–190, 279–286).

**9. 1.5.4 and 1.9.4 limitation 2: "On held-out recordings the participant residuals exceed sampling noise"; "The hard-core form overpredicts participants by about 1 %"**
- **Issue:** The test cannot separate theory error from estimator bias.
  - The null in dependence_null.py centres the per-recording distribution on the prediction, which is k̂ evaluated at the *expected* counts.
  - k̂ = 2 + f₃/f₂ is a ratio estimator, so even an exact theory of f₂ and f₃ leaves E[k̂] ≠ k̂(E[f]). A systematic per-condition offset of that kind produces exactly the 24/32 sign pattern and the excess of 2-SE points.
  - The chapter checks this nonlinearity gap only for *rate* (±0.008). For participants it offers the pooled path (≤ 0.004 change). Pooling 5 recordings removes roughly 4/5 of a 1/n ratio bias, so that suggests a per-recording bias of about 0.005, which is comparable to the 0.007–0.012 median residuals being attributed to the theory.
- **Severity:** major. A check that cannot fail in the direction tested: the residual is assigned to the theory without a null that includes the estimator's own bias.
- **Fix:** Simulate per-recording k̂ under the exact moments, or apply a delta-method bias correction, and re-centre the null. Report how much of the 1 % survives.
- **Verified:** partly (dependence_null.py header; the bias magnitude is my inference).

**10. 1.6.1 "Real backgrounds are not flat … does not change (0.99 per hour …), because coincidences across cells depend only on each cell's rate per bin"**
- **Issue:** The alarm cannot ring.
  - The per-cell burstiness simulated is independent across cells. By the chapter's own explanation it cannot change a cross-cell coincidence rate, so the check is unable to register the harm.
  - The harm that matters, bursts shared across cells, was not modelled. The sentence still reads as reassurance about real backgrounds.
  - The draft's own "because …" is the confession.
- **Severity:** major.
- **Fix:** Restate as "independent per-cell burstiness leaves it unchanged by construction; shared modulation, the case that would raise it, is untested." Move that sentence before the reassurance.
- **Verified:** yes (text logic; generator docstring: burst gamma drawn per ROI).

**11. 1.8.1 Detection: "still in 13 % at reuse 0.045 (… 8 of 60, binomial 95 % interval about 6–25 %)"**
- **Issue:** The headline uses the small sample when the chapter's own record holds a far more precise one.
  - membership_repeat.txt gives, at M = 1000, 1000 recordings: 0.094 [0.077, 0.114] at 200 surrogates and 0.092 at 1000.
  - The text quotes those same 1000-recording subgroups (14 %, 26 %, 2 %) one sentence later, so the headline and its breakdown come from different runs.
- **Severity:** moderate.
- **Fix:** Quote 9 % [8–11 %] from the 1000-recording run and keep the subgroup numbers with it.
- **Verified:** yes (membership_repeat.txt).

**12. 1.3.2 and Figure 1.4 C: the off-peak level is reported only at 5–10 s lag**
- **Issue:** The log shows structure the text does not mention.
  - For the sharp set the level at 2–3 s lag is 0.859, against 0.891 at 5–10 s and a predicted 0.887 (log line 19).
  - The hard-core deficit should be flat out to 20 s. By my rough count of about 13,000 expected pairs, the gap is roughly 3–4 Poisson SE; correlated pairs would lower that.
  - The jittered set's 2–3 s level matches its Gaussian tail.
  - The correlogram tool subtracts the 5–10 s level, so a lower near-peak floor would bias the HWHM.
- **Severity:** minor to moderate.
- **Fix:** Report the 2–3 s level and either explain it or show it is noise, for example with a bootstrap over recordings.
- **Verified:** yes (log); the significance is my estimate.

**13. 1.10 Conclusion: "event rate from four events of 13 cells or sixteen of 7"; 1.5.7 "Rate needs at least four events with 13 cells and sixteen with 7"**
- **Issue:** The evidence is not shown. Table 1.5 gives participants only, so a conclusion-level claim rests on numbers the reader cannot see.
- **Severity:** moderate.
- **Fix:** Add a rate row or column to Table 1.5, as in-band counts by E.
- **Verified:** no (window_counts.txt not reconciled).

**14. 1.2.3 and 1.9.1: the analytic chance floor "gives the same 6 and 12 cells as the repository's simulated floor"; CFAR "kept false alarms near their allowance only because it was itself a prediction"**
- **Issue:** The agreement is weaker evidence than the text implies, and the check guarding it cannot fail.
  - The floors are coarse integers. The repository floor (event_floor.py) uses a different rule: the first K meeting the budget, against the chapter's "every larger K also".
  - The script's `assert chance_floor(0.01) == 6 and chance_floor(0.05) == 12` compares the analytic floor with hard-coded constants, not with `event_floor.window_floor`. It cannot detect drift in the repository's floor.
  - "Near their allowance" rests on 0 in 10 h and 5 in 200 min (finding 5).
- **Severity:** minor.
- **Fix:** Call the agreement integer-level agreement at two points, and make the assert call the repository floor on a flat Poisson background.
- **Verified:** yes (script line 722, event_floor.py).

**15. Figure 1.1 caption and the opening of 1.1**
- **Issue:** The figure's background (0.05 Hz) is five times the lab's 0.0096 Hz, and the caption does not say so. A reader outside the field will take the "noisy background" as representative. Separately, the 1.1 claim that a tool reports about 0.7 s "whatever the true jitter is" holds at K = 3–4 only; at K = 6 the reading moves (Table 1.6).
- **Severity:** minor.
- **Fix:** Add "(about five times the lab's typical rate, chosen to make the point)". Qualify the 0.7 s claim by threshold.
- **Verified:** yes.

**16. 1.2.4 closing: "The repository's more elaborate detectors … belong to the same families."**
- **Issue:** This is asserted with no support.
- **Severity:** minor.
- **Fix:** Name the detectors and the family each belongs to, or drop the sentence.
- **Verified:** no.

## What held up under attack

- The masking explanation for situation 2: removing events 1 and 3 restores CFAR's recall from 0.38 to 0.98.
- The analytic chance-call rate: I recomputed 0.33 per hour at K = 6, b = 0.0096 Hz, 2 s.
- The CFAR threshold distributions quoted for events 2 and 5 (196 of 200; 119 / 67).
- The correlogram HWHM agreement within about 1 SE.
- The situation-4 chance-hit control: the chapter already demands and shows the "found by luck" rate.

## Run note

The grant mismatch above (editing tools held) is a finding about the run, not about the chapter. The run record should say this role took a fallback path.
