GRANT 4 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, SubagentHandback, mcp__claude_ai_Claude_Docs__batch, update, guide (editing tools no reviewer may have; spawned general-purpose through the inline fallback). None of the editing tools were used. The only file I wrote is the scratch script `_scratch/r4-role-04/power.py`.

**Role 04, Reviewer 2: finding list.** "Extract" line numbers refer to `_scratch/r4_extract.md`. I ran `theory.py --from-record` and opened all four figures. I also ran my own simulation (`_scratch/r4-role-04/power.py`, 300 reps per point, using `order_limit.py`'s functions).

Each row: location · issue · severity · suggested fix · verified against a source.

1. **Extract 299–301, order at the lab's scale.** The page says "a template signal clears that null by 2 SD up to about 3 templates at 10 events of 7 cells, and up to about 80 at 140 events of 13 cells".
   - No script or record produces this. It is computed from the asymptotic F_M with the bias added in quadrature, below the event counts where either was checked. That is the same extrapolation the *Tried and dropped* entry says was "replaced by direct simulation"; only the null side was simulated.
   - My direct simulation, 10 events of 7 cells: the null is 0.484 ± 0.065. At M = 3 the mean F is 0.567, below the null's mean + 2 SD (0.614). Only 23 % of runs exceed it, and power is 38 % against the null's 95th percentile. The crossing is at M ≈ 2 (0.616).
   - At 140 events of 13 cells, M = 80 gives 0.116 against a threshold of 0.119: 41 % exceed it, power 52 %.
   - "Mean clears the null's mean + 2 SD" is roughly 50 % power, not detection.
   - Severity: **blocking**. Fix: simulate the signal at these event counts, report power at α = 0.05, and correct "about 3" to "about 2". Verified: yes (by simulation).

2. **Extract 287–288 ("the no-order bias adds in quadrature"); glossary "falls as 1/√M either way".**
   - Quadrature was tested only where the bias F₀ is 0.03–0.09 (2000 and 200 events).
   - Where the bias is large it fails. At 10 events of 7 cells with M = 1, quadrature predicts 0.899 and the measured F is 0.754.
   - 1/√M was simulated only at a fixed E = 2000. Nothing supports "either way" (fixed E, or E = M·e).
   - Severity: major. Fix: scope both to "many events per template, small F₀". Verified: yes.

3. **Extract 132–135, the sign test.**
   - p = 0.006 and 0.06 treat 48 condition-windows as independent, but the page itself says the three windows reuse the same recordings.
   - Collapsing to the 16 conditions (my computation from `theory_check.json`): 12 of 16 are below prediction at 0.01 Hz (p = 0.08) and 9 of 16 at 0.05 Hz (p = 0.80). So "the direction is consistent" does not hold at 0.05 Hz.
   - The page also omits that 10 of 48 beyond 2 SE against 5.7 expected has binomial P = 0.05; the script prints it.
   - Severity: major. Fix: test per condition, or say "described, not tested". Verified: yes.

4. **The backgrounds 0.01 and 0.05 Hz (symbols table; every Aim 1a claim; Settled row 354) are never justified.**
   - `docs/generator.md:92` gives the lab's measured background as **0.0096 Hz/ROI**. It lists 0.05 Hz as the retired default, "assumed 5× busier". The bench uses 0.0052 and 0.0190 Hz.
   - So "a fixed K does not transfer" and "the assessor's jitter is flat" (F, H) are results at a background about 5× the lab's. The 0.01 Hz arm, the one where the assessor works, is the lab-like one.
   - The page never tells Tony this, and it is the most important fact for interpreting Aim 1a.
   - Severity: major. Fix: state which arm matches the lab and why 0.05 Hz was kept. Verified: yes.

5. **Participation regime (headlines "events of 10 or more cells").**
   - The glossary gives participation of 0.20 fast, 0.38 slow and 0.25 combined, which is about 6.6, 12.5 and 8.3 of 33 cells. The fast stream sits nearest the 5-cell arm.
   - That arm is where the joint fit fails, even at 0.01 Hz: jitter 0.37–2.47 times planted, and planted 0.2 s reads 0.127 s.
   - The lab's regime is untested or failing on participation as well as on jitter, and the page flags only jitter.
   - Severity: major. Fix: add the participation caveat next to the jitter one, in *Where it stands* and in Settled. Verified: yes.

6. **Extract 101, "For this generator, mostly yes" (replace brute force?).** This overreaches.
   - Not predicted:
     - whether a planted event reaches K (the assessor's recall and event rate);
     - the assessor's participants and jitter (modelled only by the blind passes);
     - 5-cell events at 0.05 Hz;
     - CoactDetect and LoCo (extract 442);
     - two sources (untested, and inseparable even in theory).
   - Aim 0 is itself "predict first, simulate to check", which is not replacement.
   - Severity: major. Fix: answer directly. Something like: "Not replace. It predicts the coordination-rates tool and chance clusters for one source, and says where simulation must look." Verified: yes.

7. **Membership "Yes" (extract 14–16, 221–225; Figure 3 filename "converge-to-random").**
   - With E fixed, M → ∞ converges to assemblies that are never reused, which is random participation by construction. That makes the "yes" close to a tautology.
   - The substantive case, where each source brings its own events (E = M·e), is "No", and it is **not simulated**: `membership_limit.py` fixes E = 45. Yet the section header says "simulated".
   - The picture undercuts "converges". In Figure 3B the repository's assembly test still flags 83 % (either null) and 72 % (both) at E/M = 0.3, and 27 % / 13 % at E/M = 0.045, where the variance ratio is only 1.04. Under random participation the rates are 5 % and 1.7 %. A single repeated assembly stays detectable long after the variance has converged.
   - Severity: major. Fix: lead with the condition; label the E = M·e case "derived, not simulated"; state the E/M at which detection reaches the false-positive rate. Verified: yes.

8. **Figure 3B and its text: the false-positive rate is reported only for "both nulls".** The "either null" rate under random participation is 3 of 60 (5 %; `random_flagged` in the json), and the dashed "either" curve has no baseline. Severity: minor. Fix: add that baseline. Verified: yes.

9. **Extract 224–225, "Membership is invisible to every population-count tool at any number of sources".**
   - This is derived by construction, not tested.
   - It is also not exact for the coordination-rates tool. The shift-surrogate term (pk)²(1 − 1/N) assumes equal per-cell coordinated rates, and assemblies make them unequal. At M = 1, Σ_{i≠j} λ_iλ_j is 90 λ² against 97 λ².
   - That changes the at-most-one-event term, the term credited with moving the residual from 0.05 to 0.01. My estimate is about 0.5 % of f2 at 45 events and a 4 s window, comparable to the 0.007 precision claimed.
   - Severity: minor. Fix: say "derived; exact only for equal per-cell rates". Verified: no (derivation only).

10. **Extract 9–10 and the Settled row, "participants predicted to within about 0.01 at every jitter".** At 0.05 Hz the per-jitter medians are 0.011–0.020, and the worst single conditions are 0.106 (σ = 0.2 s) and 0.093 (σ = 0.5 s). Severity: minor. Fix: quote the median and the worst; drop "at every jitter". Verified: yes.

11. **Extract 6, 80–83 and Settled 354, "the assessor reads jitter only up to about 0.7 s".**
    - The wording is ambiguous: 0.74 s is the readout ceiling, while the planted range read correctly is only up to 0.5 s, with nothing simulated between 0.5 and 1 s.
    - The claim also depends on K:
      - K = 3 reads 0.16 s for planted 0.05 s at 0.01 Hz;
      - K = 6 has jitter defined in only 15–16 of 20 recordings;
      - at 0.05 Hz, K = 6 reads 0.43 → 0.68 s as the planted value rises, so "whatever was planted" overstates.
    - Severity: minor. Fix: write "accurate to a planted 0.5 s at K ≥ 4; readout saturates near 0.74 s". Verified: yes.

12. **Figure 1 pools over design variables.**
    - Each point pools participation (10 and 20 cells) and event count (15 and 45), so the interquartile bars mix factors.
    - Panel E shows structure the text never mentions: at 0.05 Hz the assessor's participants read 0.45–0.55 of planted at K = 3 and 4, and about 1.1 at K = 6.
    - Severity: minor. Fix: split by k, and add one sentence on E. Verified: yes.

13. **Quoted review-agent numbers that are "not kept here".**
    - The numbers: 1 % of f2 / 3 % in rate (extract 157–159); the 9 % F loss from ties (268–269); 8 % and 35 % fit bias (374–375); +36 % and +44 % coincidences and 23 % below (table, 312).
    - They are load-bearing and cannot be reproduced from the repo.
    - They also contradict each other: `theory.py`'s `s_eff` docstring gives the same dropped frame term as "about 18 % low at 0.05 s", against the page's 8 % / 35 %.
    - Severity: major. Fix: keep the scripts and outputs in `docs/learned/`, or mark the numbers unverified; reconcile 18 % with 8 % / 35 %. Verified: yes for the contradiction.

14. **Blind-pass numbers rest on the shared-seed record (`blind_README.md`).**
    - "B reports a 2 % median error" (85–86), the count-detector recall within 0.03 (213) and the open residuals (216–217) are quoted without that caveat.
    - This contradicts line 21: "Every number below was recomputed after the fixes".
    - Severity: major. Fix: caveat each blind number, or scope line 21. Verified: yes.

15. **The Kreuz comparison and speed (Tony's "Synfire is very slow").**
    - Nothing here measures any runtime. Mariani's 9.7 s against 861.8 s is for latency correction, a different task.
    - Not said: `synfire_scan.py`'s cost is the sort multiplied by surrogates × restarts, so a faster sort changes the unit cost, not the null's multiplier.
    - Not said either: Figure 4C shows a stronger search raises the no-order constant (0.38 → 0.50). That implies annealing carries a larger finite-size bias than the score sort. Tony should hear both points.
    - Severity: minor. Fix: one sentence "no timing measured", plus the two points above. Verified: yes.

16. **Extract 16, "An order indicator has closed forms".**
    - Only one form is exact (one template). The M-template form is asymptotic and runs up to 10 % high.
    - The no-order term, the one that matters at the lab's event counts, is fitted, with c varying 0.22–0.60 by field size.
    - Severity: minor. Fix: reword. Verified: yes.

17. **Extract 314, "F_Kreuz = F (k − 1)/(N − 1), 0.28 at 10 of 33 cells".** 0.28 is the factor, but it reads as a value of the indicator. Severity: minor. Fix: write "a factor of 0.28". Verified: yes.

18. **Figures 2–4 caption titles name the quantity, not the finding.** Figure 1 does state its finding. Severity: minor. Fix: put each figure's finding in its title. Verified: yes.

19. **Extract 298–299, "a calibrated null such as … relabelling removes the mean bias".**
    - This holds only for random membership. The bias depends on how pair co-participations are distributed, and relabelling randomizes that distribution.
    - Under assemblies the bias is likely lower in the observed recording than in the null, so the null would be conservative. Untested.
    - Severity: minor. Fix: scope to random membership. Verified: no.

**Checked and clean:**
- The chance-cluster formula 60 q(1 − q)² matches `assess._clusters`'s merge rule (merge_bins = 2).
- The joint fit uses no planted values except N.
- The ±1.5 s truncation gives an SD of 0.743 s.
- "From K = 5 at 0.01 Hz and K = 8 at 0.05 Hz" reproduces.
- Every other quoted Aim 0 and Aim 1a number matches `theory.py --from-record`.
- The membership and order json values match the text.
- Blindness held: blind A worked from `main` at c442014a, and `theory.py`'s first commit, d495ab0e, is not on `main`.
- The run-record file exists (checked by path only, not opened).
- `_scratch/r4_prose_report.txt`, which my brief also allowed, was not opened.
