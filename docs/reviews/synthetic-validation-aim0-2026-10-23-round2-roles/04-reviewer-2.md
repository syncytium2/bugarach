GRANT 4 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update/guide (and, through ToolSearch, deferred NotebookEdit, Dropbox and Gmail write tools)

Run note: I was spawned through the inline fallback as a general-purpose agent, so I held editing tools that no reviewer may have. I did not use them. Everything I wrote went through Bash heredocs into `_scratch/r2-role-04/` (s.py, a.py, n.py, which only read `theory_check.json` and `aim1_one_source.json`). I edited no tracked file and reran no figure script. I opened none of the blinded paths. I opened all four figures and read each picture.

# Reviewer 2 findings (role 04)

Each row: location · issue · severity · suggested fix · could I verify it against a source.

1. **Order is not invisible to the population count.** Location: "Membership and order", ¶1: "Membership and order are invisible to every population-count tool, at any number of sources" (also the glossary "exchangeable limit").
   - This holds for membership but not for order. Take a latency template with spread s, random membership and jitter σ. The lag between two participants is then distributed N(0, 2(s²+σ²)).
   - So g_2 and g_3 see the template exactly as extra jitter, σ_eff = √(s²+σ²). The count is sensitive to order but cannot tell it from jitter.
   - Consequence: the joint fit, which "does measure" jitter, would report template spread plus jitter on any recording that has order.
   - Severity: **blocking**.
   - Fix: change "invisible" to "indistinguishable from jitter". Add the caveat to the joint-fit and Figure 1 jitter claims ("in the absence of a latency template"). Optionally, a one-line simulation with s > 0 through `predict_solve`.
   - Verified: yes (derivation from the generator model in `order_limit.py` and `theory.py`; not simulated).

2. **"In every condition" is true only of pooled medians.** Location: Figure 1 bullets, "within about 25 % of planted in every condition at the 2 and 4 s windows" and "the 4 s window stays within about 30 %".
   - These are medians pooled over participation and event count.
   - Per condition (condition medians from `theory_check.json`), the coordinated share at 0.05 Hz runs 0.53–1.53 at 2 s and 0.09–3.58 at 4 s. Participants at 4 s and 0.05 Hz run 0.66–3.2.
   - Only the 0.01 Hz rows roughly hold (share 0.71–1.18).
   - Severity: **major**.
   - Fix: say "pooled median". Give per-condition ranges, or exclude the 5-cell events at 0.05 Hz explicitly, as the Aim 0 section already does.
   - Verified: yes.

3. **The "0.3" is not the 5-cell detection rate.** Location: Figure 1 bullet, "K = 6 cells misses most 5-cell events (B, 0.3 at 1 s jitter)".
   - 0.3 is the pooled median over 5-, 10- and 20-cell events.
   - The 5-cell K=6 rate ratio at 0.01 Hz, per condition, is 0.27, 0.16, 0.07, 0.13, 0.07, 0.04, 0, 0.
   - In the picture, the red K=6 bars in B reach down to ~0.07 at every jitter. That is the 5-cell rows hiding inside the pooled bar.
   - Severity: major.
   - Fix: quote the 5-cell rows (0–0.27), or break panel B down by participation.
   - Verified: yes.

4. **"16× and 8× the planted rate" is not a property of K.** Location: Figure 1 bullet, "16× and 8× the planted rate (F)".
   - The multiple is the chance rate divided by the planted rate. Per condition it runs 7.7–24.5× for K=3 and 4.1–12.7× for K=4, depending mostly on 15 against 45 events.
   - Severity: minor.
   - Fix: state the chance rate in clusters per minute (7.97 and 3.86 per min, already derived), not as a pooled multiple.
   - Verified: yes.

5. **Figure 1's violet jitter points pool the 5-cell events.** Location: Figure 1 violet joint-fit points, and the text "Aim 0's joint fit (violet) does measure it".
   - `aim1_figure.py` fits every row, so the points include the 5-cell events that the text excludes. The text quotes k ≥ 10 only.
   - The 5-cell rows are off badly: 1.85 s at 1 s planted and 0.005 s (the search bound) at 0.05 s, both at 0.05 Hz.
   - In the picture, H at 0.05 s reads 0.55× with an IQR spanning 0.1–1.7.
   - The figure therefore neither matches the quoted numbers nor shows the failure the text admits.
   - Severity: major.
   - Fix: plot violet for k ≥ 10 only (or by participation) and say so in the caption.
   - Verified: yes.

6. **"Within seed-to-seed noise" is asserted, not tested.** Location: Aim 0 predictions, "Participants: predicted to within seed-to-seed noise".
   - My crude test used z = (median measured − predicted) / (1.25·SD/√n) on condition medians, k ≥ 10. Beyond 2 SE: 6 of 48 at 0.01 Hz and 11 of 48 at 0.05 Hz, where about 2–3 are expected.
   - The test is crude: the SD comes from only 5 recordings.
   - Severity: major.
   - Fix: run the test properly (per-condition SE, or pooled z) and report it. Otherwise say "small, median 0.009", not "within noise".
   - Verified: yes (crude test; scripts in `_scratch/r2-role-04/`).

7. **The rate and share residuals are a one-sided bias.** Location: "Event rate and share: predicted less well".
   - At 0.01 Hz, measured exceeds predicted in 43 of 48 conditions for rate and 42 of 48 for share. 16 and 18 of 48 lie beyond 2 SE.
   - The page offers the unmodelled surrogate correlation (~1 % of f2) as a possible cause. That cause is unquantified. A 1 % f2 error could move λ̂ by ~3 %, so it is neither excluded nor shown.
   - Severity: major.
   - Fix: state the sign and frequency. Either quantify the surrogate term's effect on λ̂ or mark the explanation "untested".
   - Verified: yes.

8. **Figure 2 still calls the prediction "exact".** Location: Figure 2 legend, "exact prediction, 5/10/20 cells per event".
   - The run record names "'exact' stretched past participants" as an overclaim. The legend still applies the word to the rate and share panels, where the worst residual is 0.38, and to 5-cell events, where it is 5.6.
   - Severity: major.
   - Fix: relabel as "with the at-most-one-event term".
   - Verified: yes.

9. **One chance-cluster prediction misses by 2×, another by 22 %, and the text is silent.** Location: Aim 0 "Chance clusters at K" (predicted 0.02 against measured 0.04 at K = 4, 0.01 Hz) and Figure 2 D.
   - The K=4 point in D visibly sits above the diagonal.
   - Pooled counts, K=4 at 0.01 Hz: 16 clusters measured against 8.6 expected (Poisson p ≈ 0.015).
   - K=6 at 0.05 Hz: 105 measured against 128 expected (about 2 SD low).
   - The quoted "measured" values are medians of per-recording counts of 0–2 clusters, a coarse statistic.
   - Severity: major.
   - Fix: report pooled rates with Poisson CIs and state the misses. The q(1−q)² cluster-start approximation is the suspect.
   - Verified: yes.

10. **The joint fit's "within 4 %" is a median of medians.** Location: joint fit, "participants and rate within 4 %"; "Where it stands" also claims it "recovers jitter … for events of 10 or more cells".
    - Per-condition medians for k ≥ 10 run 0.94–1.14 for participants and 0.73–1.14 for rate.
    - Jitter at 0.05 s is not recovered: 3 and 7 of 20 fits sit at the bound, and one condition's median is the bound.
    - The headline omits the jitter range.
    - Severity: major.
    - Fix: give per-condition ranges, and say "for jitter ≥ 0.2 s" in "Where it stands".
    - Verified: yes.

11. **Figure 2 does not say which conditions are off scale.** Location: Figure 2 panels E–G, "3/4/2 conditions off scale".
    - The largest misses are hidden and the caption does not say they are the 5-cell events at 0.05 Hz.
    - Severity: minor.
    - Fix: name them in the caption, or extend the axis.
    - Verified: yes.

12. **The convergence result is close to true by construction.** Location: Membership claim, "assembled participation converges to random. It does".
    - Assemblies are drawn as random k-sets, with uniform choice and perfect readout. As M grows, every event gets a fresh random set, which is the random case.
    - The non-trivial content is the 1/M rate. That rate assumes uniform usage: with unequal usage the share probability is Σp_m², so the "effective M" is smaller.
    - Overlapping, nested or unequally sized assemblies are not covered.
    - Severity: major (it answers the PI's question).
    - Fix: state the assumptions (random, equal-size, uniformly used assemblies) next to "It does", and give the Σp_m² generalization.
    - Verified: yes (`membership_limit.py`).

13. **Several Figure 3 descriptions are wrong or loose.** Location: Figure 3 caption, "grey band, the 95 % range of a single random recording", and the text "detected every time while each assembly is used at least once … 8 % at 0.04 (5 % by chance)".
    - The band is drawn from 1.0 (the mean) to the 95th percentile (`axhspan(1, p95)`). It is a one-sided band, not a 95 % range.
    - At E/M = 1, on average each assembly is used once, and about 37 % are unused. "Each assembly used at least once" is false; the condition is reuse ≥ 1.
    - The realised null rate at M = 10000 is 2.75 %, not 5 %. The p95 is in-sample, and every ratio shares one baseline mean, so the errors are correlated (measured below predicted at all 7 points).
    - Severity: minor.
    - Fix: relabel the band. Say "reuse E/M ≥ 1". Use an out-of-sample null and report the realised null rate.
    - Verified: yes.

14. **The "closed forms" for order are partly fitted, and the line is stitched.** Location: Order, "With M templates the signal term falls as 1/√M"; Figure 4 B; and "Membership and order have closed forms too".
    - The M-template prefactor √(2/π)·√((2/π)arcsin(τ²/(1+τ²))) is stated but not derived anywhere.
    - At M = 1 it gives 0.65 against the one-template 0.758, so the code special-cases M = 1. The solid line in B kinks at M = 2.
    - Simulation sits 6–9 % below the prediction at M = 2–16. This is visible in the picture and not mentioned.
    - F_0 in B is simulated, not derived, and C is a fit.
    - Severity: major.
    - Fix: derive or cite the prefactor. Say it is asymptotic and report the mid-M shortfall. Retitle Figure 4 from "closed forms" to "closed forms and fits".
    - Verified: yes.

15. **Figure 4 A's low-τ mismatch is not explained.** Location: Figure 4 A and "Under one template F = (2/π) arctan τ".
    - At τ = 0.25 simulation reads 0.176 against 0.156 predicted, and at 0.5 it reads 0.314 against 0.295. This is the F_0 bias at 200 events: √(0.156² + 0.092²) = 0.18 matches.
    - Severity: minor.
    - Fix: draw √(F_1² + F_0²) in A as well, or state the bias.
    - Verified: yes.

16. **At the lab's event counts the order signal may sit below the bias.** Location: Figure 4 B and C regime against the lab.
    - B runs at 2000 events and C reaches n̄ = 70.
    - At the lab's scale (33 cells, ~25–45 events, participation 0.2–0.38), n̄ ≈ 1–4. There F_0 ≈ 0.2–0.4, which exceeds the M-template signal for M ≳ 4–8. The page never says this.
    - That is the result's significance for the PI's question.
    - Severity: major.
    - Fix: add the lab's n̄ to C and state where signal meets bias at realistic event counts.
    - Verified: yes (arithmetic from `order_limit.py` nbar and the GLOSSARY interval and participation values).

17. **The August record already has an order-free control, and the page omits it.** Location: Kreuz bullet, "August anti-correlation … consistent with this bias but untested. The test: run synfire_scan.py on order-free simulations".
    - The August todo already reports 40 generated order-free recordings with a median indicator of 0.101. That is higher than fast (0.036) and equal to slow (0.099).
    - This is the most relevant evidence for the bias question, and part of the proposed test already exists.
    - Severity: major.
    - Fix: cite it, and say what is missing (matching on cells and spike counts).
    - Verified: yes (`docs/todo/2026-08-19-…`, table).

18. **The PI's "brute force / very slow" remark gets no direct answer.** Location: Kreuz comparison against the PI's remark ("Pretty sure his is brute force. Synfire is very slow").
    - The page never measures where synfire's time goes: the annealed sort, the ISI-adaptive SPIKE-order matrix, or `--restarts`. Nor does it time the score sort.
    - "O(N²) with no search" implies a speed-up for Kreuz's pipeline that is not shown, because F is not SPIKE-order.
    - The Mariani 9.7 s against 861.8 s figure is for latency correction, not the sort, and a reader may take it as the synfire speed-up.
    - Severity: major.
    - Fix: answer directly. Kreuz's sort is simulated annealing, which is search; the indicator itself is not. Report `synfire_scan` `elapsed_sec` from the August JSON against the score sort's time on the same trains.
    - Verified: partly. The annealing is confirmed in `tools/synfire_scan.py`; the August timing JSON is in the darkroom and I did not open it.

19. **The field-size range mixes two sorts, and the novelty claim is weak.** Location: Kreuz bullet, "changes with field size (0.22 to 0.61 …)" and "what is new here is the 1/√n̄ form".
    - 0.22 is a score-sort value and 0.61 a local-search value, so the range mixes two estimators. Per sort: score 0.22–0.51, search 0.31–0.60.
    - A 1/√n̄ scaling is the generic CLT rate for a sum of random signs, and it was checked at only one field size (33 cells, 10 per event).
    - Severity: minor.
    - Fix: report per-sort ranges and soften the novelty claim.
    - Verified: yes.

20. **Local search does not bound annealing.** Location: `order_limit.py` docstring, the local search "standing in for the simulated annealing … which can only do as well or better".
    - Stochastic annealing is not guaranteed to match a local search started from a good point.
    - Severity: minor.
    - Fix: say "typically finds orders at least as good", or measure it.
    - Verified: yes (by reasoning).

21. **"One answer, reached three ways" is stronger than the caveat under it.** Location: blind-pass heading, "One answer, reached three ways".
    - The paragraph itself calls it a consistency check with shared inputs, and the table shows each pass differs in a 1/N term.
    - The claim that the exact term was committed before the blind reports checks out: d495ab0e (15:40) holds the (1 − 1/N) terms, and bc0a1f80 (15:54) adds the blind reports.
    - Severity: minor.
    - Fix: lead with the consistency-check caveat, not the bold claim.
    - Verified: yes.

22. **The assessor-jitter explanation is untested.** Location: Figure 1 bullet, "tops out near 0.7 s … because it gathers onsets within ±1.5 s (a 1 s Gaussian cut at ±1.5 s has SD 0.74 s)".
    - The arithmetic is right (truncated SD 0.743), and ±1.5 s is `wm_factor` 1.5 × the 1 s bin, which the page does not say.
    - But at 0.05 Hz it reads 0.66 s even at 0.05 s planted (H, 14×). That is chance onsets within the gather window, not truncation of the event's own spread.
    - The stated cause is one of two, and neither is tested.
    - Severity: minor.
    - Fix: name both causes (truncation at high σ, background contamination at low σ), and cite `wm_factor`.
    - Verified: yes (`assess.py`, `wm_factor` = 1.5).

23. **Figure 1 omits the tool's own rate bias.** Location: Figure 1 B and F, the picture against the text.
    - The coordination-rates tool's event rate at the 1 s window climbs to 1.7× (B) and 2.1× (F) at 1 s jitter. No bullet mentions it.
    - Severity: minor.
    - Fix: add a bullet. Aim 0 predicts it (exact 1.6–2.3), which is a point in its favour.
    - Verified: yes.

24. **The residual statistic is not defined.** Location: "Measured minus predicted, as a ratio to planted: median 0.009 (worst 0.056)".
    - The reader is not told it is |condition-median ratio − predicted ratio|, taken over 72 condition-windows (48 for k ≥ 10).
    - Severity: minor.
    - Fix: one clause defining it.
    - Verified: yes (`theory.summary`).

25. **The glossary equates the convergence limit with the August null.** Location: GLOSSARY "exchangeable limit … it is the null that keeps every onset time and permutes which ROI owns it".
    - The August relabel null permutes ownership of every spike, background included, across the whole recording. The exchangeable limit only permutes cells within events.
    - The goal page says "variant"; the glossary says "is".
    - Severity: minor.
    - Fix: change "is" to "is approximated by" and name the difference.
    - Verified: yes (todo 2026-08-19, `synfire_scan._relabel`).

# What I checked and found sound
- All quoted Aim 0 numbers reproduce from `theory.summary(theory_check.json)`: residuals, 17 of 720 refusals, the joint-fit σ values and bound counts, and the chance-cluster values.
- The membership and order JSONs match the text.
- The glossary 1.67σ conversion is right.
- The blind-pass caveat is adequate in body text.

The scratch scripts are `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r2-role-04\s.py`, `a.py` and `n.py`.
