GRANT 4 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch (which can load NotebookEdit and the Dropbox and Gmail write tools), mcp__claude_ai_Claude_Docs__batch / __update / __guide

(I held editing tools that no reviewer may have. I used none of them. All my work was Read, Grep, Bash and Python scripts in my scratch folder. The run record should note that this role came in by a fallback path.)

# Role 4, Reviewer 2: Chapter 1 (blob 14d63527)

**Scope.** I read the whole chapter. I spent most of the effort on the material this revision added: sections 1.1 to 1.4, Figures 1.1 to 1.3 and Table 1.1. I opened all three new PNGs and read `ch1_intro_figures.py` and its log. I re-ran parts of the script under new conditions to test claims; the scripts are in `<scratch>\mb\role04\` (chk1.py, chk2.py, chk3.py).

I checked the radar citations against `01-lit/bugarach/radar/README.md`; it supports the Finn & Johnson masking claim and Rohling's "guard cells by 1983". I spot-checked the revision note's "no number changed": every number in the 5c3605a9 version still appears in this one.

Each finding is: location · issue · severity · suggested fix · verified against a source (yes/no).

## Blocking / high

**1. §1.2.4 situation 3 ("No count separates two events 3 s apart"), Table 1.1 column 3, §1.9.1 · high · verified: yes**
- **Issue:** Figure 1.2 D contradicts this heading. The sliding count shows two separate peaks (12 and 11 cells) with a dip to near zero between them. I re-ran the 200 draws: the sliding count forms two runs at or above 6 cells, separated by a dip below 6, in **200 of 200**.
- What joins them is the detector's settings, not the count:
  - the merge gap of 3 s, which equals the planted separation;
  - `runs_to_calls` and `count_sliding_detect` extend each call's span back by the 2 s window;
  - for fixed bins, event 3a (80 s) sits on a bin border.
- The vignette therefore shows a merge-gap setting, which §1.2.4's closing paragraph and §1.10 themselves list as a failure mode ("a merge gap longer than the interval between events"). It does not show a property of counting. The heading's "because their counts overlap" is false for the sliding count.
- **Fix:** Retitle it, e.g. "A merge gap as long as the separation joins two events". Say that the sliding count itself resolves the pair (Fig. 1.2 D), and that §1.7 derives the tools' limit as (m + ½) bin widths, set by the merge rule.

**2. §1.2.4 situation 5 ("An event smaller than the chance floor cannot be told from chance … Counting alone cannot distinguish it from background") · high · verified: yes**
- **Issue:** The chapter's own chance-floor formula refutes this. Running `chance_floor` from `ch1_intro_figures.py` at 0.0096 Hz gives a floor of **4 cells for a 0.2 s window** and 4 cells for a 0.5 s window. The 6-cell floor belongs to the 2 s window.
- Event 5 has σ = 0.05 s, so its 5 onsets fit in a 0.2 s window. It is above the floor of a counting window matched to its jitter.
- The chapter states the window/jitter trade-off one paragraph later but does not apply it here. The chance floor depends on the window; "counting alone" does not set it.
- **Fix:** Restrict the claim to the 2 s window. State that a narrower window lowers the floor, and that this is a trade against splitting jittered events (situation 2).

**3. Table 1.1 column 5, situation 5 text, Figure 1.2 caption ("2, … centered on a border between two fixed bins") · high · verified: yes**
- **Issue:** An undisclosed confound. Events 3a (80 s), 4 (150 s) and **5 (210 s)** also sit on 2 s fixed-bin borders, but the caption names only event 2. The text says fixed bins find event 5 less often because the sliding window "catches more background". That is wrong as stated.
- Moving event 5 by +1 s to mid-bin, with everything else unchanged over the same 200 seeds, raises the fixed-bin rate from **0.21 to 0.41**. Fig. 1.2 C shows event 5 split as 2 and 5 cells across the border.
- **Fix:** Move events 3a, 4 and 5 off the borders, or disclose that they sit on borders. Then restate the explanation for situation 5.

**4. Figure 1.3 C and §1.3.2 ("That level, the same at every lag, is chance"; "The dotted line at 1 is chance"; jittered HWHM "5 % narrower than predicted") · high · verified: yes**
- **Issue:** In the figure, every off-peak point for both sets sits well below the dotted chance line. I measured the mean ratio at |lag| ≥ 2 s as **0.857 (sharp) and 0.902 (jittered)**.
- This is the hard-core train: no other event within 20 s depletes cross-event coordinated pairs. It is the same mechanism §1.3.3 invokes for windows, but the correlogram text and its prediction (C₀ + …, drawn at 1 off-peak) omit it.
- Taking the HWHM against the measured baseline gives 0.815 s for the jittered set, against 0.835 predicted. The bootstrap SE over recordings is 0.015 s. Part of the reported "5 % narrower" is therefore this baseline offset, and the rest is about 1.3 SE.
- The text reports the 5 % miss with no uncertainty and no explanation. A reader takes it as a model failure.
- **Fix:** Add the hard-core depletion to C(τ), or say the baseline sits below 1 and why. Report the HWHM against the actual baseline, with a bootstrap SE. Put uncertainty on the Fig. 1.3 C and D comparisons.

**5. §1.2.3 / §1.2.4 situations 2 and 5, §1.9.1 ("The threshold that worked, CFAR's, was itself a prediction") · high · verified: yes**
- **Issue:** The CFAR rates in Table 1.1 come from this crowded design, not from CFAR in general.
- Over 200 draws, CFAR's local background estimate in the quiet stretches has a median of **0.0212 Hz, 2.2× the true 0.0096 Hz**. The design packs 6 events into 4 minutes (about 90 per hour, against the realistic 9.7–22), and the busy stretch leaks into the reference windows. Fig. 1.2 D shows the violet threshold at 7–9 cells through almost all of the quiet stretches, not at 6.
- CFAR's threshold at event 5 (210 s) is 7 in 56 % of draws and 8 in 10 % (6 in 32 %). So "five cells are one fewer than the threshold" is false for CFAR in most draws. CFAR's 42 % on event 5 goes unexplained; its reference window (175–205 s) overlaps the busy stretch.
- "Worked" is an overreach: CFAR finds events 2 and 5 in only 44 % and 42 % of draws. It wins only on false calls.
- **Fix:** Add a caveat that the CFAR rates are specific to this event density, and report the bias in CFAR's estimate. Explain CFAR's result on event 5. Change "worked" to "kept false calls near its budget".

**6. §1.4 "answer in brief" ("jitter cannot be read from one window at all") and §1.10 ("by any tool tested") · high · verified: yes**
- **Issue:** Only the joint fit was tested at realistic values and in 20-minute windows (`window_counts.py`, `realistic_counts.py`). The correlogram tool never was; the ch1_followups README runs it only on the 240-recording grid.
- The chapter's own Table 1.3 makes the correlogram the better per-recording estimator at small jitter: 0.97 [0.94, 1.02] at 0.2 s and 1.06 at 0.05 s, at 0.01 Hz. Realistic jitter (0.105–0.131 s) falls in exactly that range.
- "Unreadable" is asserted for a tool that was not run.
- **Fix:** Restrict the claim to the joint fit, or run the correlogram tool on the realistic-values recordings and the 20-minute windows.

## Medium

**7. §1.2.4 situation 2 ("their onsets raise its threshold near event 2 to 7 or 8 cells in most draws") · medium · verified: yes**
- **Issue:** Over the 200 draws, the CFAR threshold at 46 s is 8 in 158, 9 in 36 and 7 in 6. The accurate statement is "8 or 9". The script does not print this number, although its docstring says "Every number the chapter quotes from these figures is printed by this script".
- **Fix:** Correct to "8 (9 in about a fifth of draws)", and print the distribution in the script.

**8. Table 1.1, false calls per hour in the quiet background · medium · verified: yes**
- **Issue:** A fragile statistic. Each draw has 3 quiet minutes, so 200 draws give 10 hours in all. Then 0.10/h is **one** false call, 0.50/h is five and 0.00/h is none.
- This is the only empirical check in §1.2 that the 6-cell floor meets one call per hour (the formula predicts 0.33/h for the sliding window). The counts and intervals are not shown.
- **Fix:** Give the counts and the observation time (e.g. "5 in 10 h; 95 % interval 0.16–1.17/h"), or simulate more quiet time.

**9. Table 1.1 column 4 and situation 4 ("The fixed-threshold detectors find event 4") · medium · verified: no**
- **Issue:** A check that cannot fail. In the busy stretch the fixed detectors make 1.78 and 3.60 false calls per minute. Each call spans at least 2 s and scoring adds ±1 s, so a chance call near 150 s scores as "found". A 1.00 hit rate there cannot show that the detector responds to the event.
- **Fix:** Report the hit rate with event 4 removed (the chance-hit rate) beside 1.00, or score hits only by calls whose members are mostly the event's cells.

**10. §1.4 "The question, and the answer in brief" ("For one source, mostly yes") · medium · verified: yes, against the chapter's own §1.5.4 and §1.5.5**
- **Issue:** The summary omits two results:
  - on the held-out record the participant prediction is rejected as exact: 17 of 48 condition-windows lie beyond 2 SE, p = 0.0005–0.002;
  - the slow-stream residual of up to 3.3 SE is unexplained.
- These appear only in §1.9.4. A reader of §1.4 gets the 1–2 % median without the rejection.
- **Fix:** Add one sentence to the summary.

**11. §1.1 premise ("a recording mixes two or more sources") · medium · verified: yes**
- **Issue:** This is asserted without evidence. DeFazio et al. 2026 gives two event *types*, which the chapter analyzes as separate streams; that is not two sources within a stream. §1.5.3 then shows that the chapter's count tools cannot tell two sources from one, so as things stand the premise cannot be tested with this toolset.
- **Fix:** Label it a working hypothesis, or cite evidence for several sources within one stream.

**12. Unjustified constants in §1.2 · medium · verified: yes**
- **Issue:** None of these is justified for the reader:
  - merge gap of 3 s ("one event can spill into the next bin" justifies a gap of 0, adjacency, not 3 s);
  - CFAR reference window of 30 s and guard band of 5 s;
  - scoring tolerance of ±1 s;
  - the 2 s window/bin, whose only grounding is that it is the repository's (ADR-0008) and the lab's interval lists.
- Situations 3 and 5 hinge on two of these: the merge gap and the 2 s window.
- **Fix:** One clause each saying why, or that the value is illustrative.

## Low

**13. §1.3.4 ("A threshold that would catch every sharp event therefore misses most jittered ones") · low · verified: yes**
- **Issue:** The share of bins with at least 8 cells is 0.0147 against about 0.0167 bins per event, roughly 88 %, not "every". A bin share is also not a per-event detection rate.
- **Fix:** Say "most sharp events", or compute the per-event rate.

**14. §1.2.3 / §1.9.1, agreement of the analytic floor with the repository's simulated floor · low · verified: yes**
- **Issue:** Both are computed on flat Poisson backgrounds (`blind_a/theory_floor.py` checks the formula against `event_floor` on Poisson trains). The agreement is a consistency check of the up-crossing approximation, not validation on real backgrounds.
- **Fix:** Say so.

**15. §1.2.4 situation 2 ("Jitter defeats fixed bins") · low · verified: no**
- **Issue:** The 0.34 is conditional on the event being placed on a border, the worst case. At random placement fixed bins would do better. The table header discloses the border; the heading generalizes.
- **Fix:** "Jitter across a bin border defeats fixed bins".

**16. §1.10 ("A window shorter than about six times the jitter undercounts participants") · low · verified: yes**
- **Issue:** The source (§1.5.2) is for 10-cell events, with "undercount" meaning below 0.9. The conclusion drops both qualifiers.
- **Fix:** Restore them.

**17. Figures 1.1 to 1.3 · no findings on the pictures beyond 1, 3, 4 and 5 above**
- Figure 1.1 matches its caption: 190 + 40 onsets and four events.
- Figure 1.3 D and E match the log.
- The picture-level findings are: Fig. 1.2 D refutes situation 3 (finding 1); Fig. 1.2 C shows event 5 split across a border (finding 3); Fig. 1.2 D shows CFAR running high in the quiet stretches (finding 5); and Fig. 1.3 C shows the off-peak points below "chance" (finding 4).
