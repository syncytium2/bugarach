GRANT 4 MISMATCH — missing none; holds Edit, Write, NotebookEdit (also Agent, Artifact, PowerShell, Skill, Claude Docs MCP write tools). This was a fallback spawn as a general-purpose agent. I used only Read, Grep, Glob and Bash, wrote nothing outside `_scratch/r3-role-04/` (I created the empty folder and nothing else), and respected the blindness rule.

**Reviewer 2 (role 04): findings.** Columns: location · issue · severity · suggested fix · verified against a source (yes/no)

1. **Fig 1 D, the bullet "The assessor cannot measure jitter", the Fig 1 caption ("only the joint fit tracks jitter") and the Settled row.**
   - **Issue:** the picture refutes the unconditional claim. At 0.01 Hz the assessor tracks planted jitter up to 0.5 s. K=4 medians are 0.085, 0.23, 0.48 and 0.68 s for planted 0.05, 0.2, 0.5 and 1.0 s; K=3 reads 0.18, 0.27, 0.47 and 0.69 s (from `aim1_one_source.json`).
   - **Why:** the failure is real only at 0.05 Hz, plus the ~0.7 s cap at 1 s. The Settled table carries the overreach forward.
   - **Severity:** blocking, because it is a Settled claim that will feed later reports.
   - **Fix:** say "cannot measure jitter at 0.05 Hz, or above ~0.7 s; at 0.01 Hz it tracks 0.05–0.5 s". Restate the caption and the Settled row to match.
   - **Verified:** yes.

2. **Joint-fit headline ("jitter from 0.2 s up") against the lab's own jitter.**
   - **Issue:** the GLOSSARY gives the lab's measured σ as 0.105 s fast and 0.131 s slow. That sits exactly in the gap between 0.05 s (not resolved) and 0.2 s (resolved), and the grid has no point there.
   - **Why:** the page never says that the real data's jitter falls outside the validated range.
   - **Severity:** major.
   - **Fix:** state it beside the headline and in Settled. Add σ = 0.1–0.15 s to the grid, or a narrower window, before the fit is used on real data.
   - **Verified:** yes.

3. **"7 and 10 of 48 condition-windows sit beyond 2 SE where about 2 are expected" ("not to within noise").**
   - **Issue:** the SE is 1.2533·SD/√5, with the SD from 5 recordings and ddof=0. That statistic is t-like with heavy tails. Under a true null I simulated P(|z|>2) = 0.117, so about 5.6 of 48 are expected, not 2.2.
   - **Why:** 7 at 0.01 Hz is null-level; 10 at 0.05 Hz is only mildly high. The three windows also reuse the same recordings, so the 48 are not independent.
   - **Severity:** major.
   - **Fix:** recompute the expectation (t with 4 df, or simulate). Soften the claim to "consistent with noise at 0.01 Hz, mildly beyond it at 0.05 Hz". State how the SE is defined.
   - **Verified:** yes.

4. **"Event rate and share … biased one way."**
   - **Issue:** only 0.01 Hz is reported (43 and 41 of 48). At 0.05 Hz, measured exceeds predicted in 30 (rate) and 29 (share) of 48, which is no consistent direction.
   - **Severity:** major (selective reporting).
   - **Fix:** report both backgrounds and confine "one way" to 0.01 Hz.
   - **Verified:** yes (`theory.summary`).

5. **"worst ratio 5.6 of planted" (5-cell events, 0.05 Hz).**
   - **Issue:** 5.608 is the worst |measured − predicted| residual, not a ratio. The worst ratio to planted is 6.32 (2 s window).
   - **Severity:** minor.
   - **Fix:** correct the label or the number.
   - **Verified:** yes.

6. **Chance clusters, "All within their 95 % intervals", and Fig 2 D.**
   - **Issue:** the K=6, 0.01 Hz arm expects 0.2 clusters in 4500 min, so 0 or 1 observed passes whatever the true rate. That check cannot fail, yet it is counted as agreement.
   - **Inconsistency:** the page quotes the prediction as 0.0001/min, the figure as 5e-05/min, and the code gives 5.1e-5/min.
   - **Severity:** major for the power problem, minor for the number.
   - **Fix:** say "not testable at this size" for that arm, and use 5e-5 everywhere.
   - **Verified:** yes.

7. **"Both follow from the event floor … 6 cells at 0.01 Hz and 12 at 0.05 Hz."**
   - **Issue, the floor:** the ADR-0008 floor counts in a sliding 2 s window against a budget of one chance call per hour. The assessor's own rule (1 s bins, merge 2, `theory.chance_clusters_per_min`) reaches one chance cluster per hour at K=5 (0.01 Hz) and K=8 (0.05 Hz), not 6 and 12.
   - **Issue, the 5-cell events:** K=6 missing 5-cell events is k<K, true by construction, not the floor.
   - **Unmentioned:** K=6 also misses 10-cell events at 1 s jitter (rate 0.13–0.40 of planted), which the floor cannot explain. That is the drop to 0.3 in Fig 1 B.
   - **Severity:** major.
   - **Fix:** use the assessor's own chance rate for its threshold, call the k<K case trivial, and add the bin-versus-jitter loss.
   - **Verified:** yes.

8. **Fig 1 pools across participation.**
   - **Issue:** the claims are split by k (5-cell versus 10+), but the panels pool k. The text admits the K=6 evidence is "inside the pooled points of B".
   - **Severity:** major (results not broken down by a design variable).
   - **Fix:** split by k (marker or panel), or add a per-k table.
   - **Verified:** yes.

9. **Membership answer to Tony ("Under the assumptions below, yes") and GLOSSARY "exchangeable limit".**
   - **Issue:** convergence to random holds only when total events E is fixed while M grows. If each new source brings its own events (E = M·e), the ratio 1 + (Me − 1)/M tends to 1 + e and never reaches random.
   - **Contrast:** the order signal does fall as 1/√M either way, so "assemblies and templates both converge" is too general.
   - **Severity:** major.
   - **Fix:** put "at fixed total events" in the answer sentence and in the glossary, and give the per-source case.
   - **Verified:** yes (derived from the page's own formula).

10. **"At the lab's scale the order signal may sit below the bias" (about 4 or more templates).**
    - **Issue, fit range:** c = 0.38 was fitted over n̄ = 2–68 at k = 10 (Fig 4 C), but the claim applies it at n̄ = 1–4.5 and k = 7–13. c itself varies from 0.26 to 0.51 with k (`order_limit.json`).
    - **Issue, the threshold:** "about 4 templates" holds only at n̄ ≈ 1. At n̄ = 4.5 (bias ≈ 0.18) the signal stays above the bias until about 13–16 templates.
    - **Issue, the yardstick:** a mean bias is removed by a calibrated relabel null, so detectability depends on the null's spread, not its mean.
    - **Not reconciled:** the August verdicts (29 % and 54 % against an 8 % false-positive rate on the control) are never squared with this.
    - **Severity:** major.
    - **Fix:** give the range ~4–16, mark it as an extrapolation, and compare the signal with the null SD. Reconcile with the August verdicts.
    - **Verified:** yes.

11. **Kreuz comparison and Tony's speed question.**
    - **Issue:** the page offers the score sort as the fast alternative, with no timing and no power comparison against a search or annealing on the same trains. Lower bias alone does not establish that it can replace annealing.
    - **Severity:** minor/major.
    - **Fix:** add a timing and power comparison to plan item 1, and say "not measured" now.
    - **Verified:** yes.

12. **Numbers resting on reviewers' computations with no record in the folder.**
    - **Issue:** "+33 % coincidences (a reviewer's test)", "about 1 % of the pair count (a reviewer)", and the g_2 rounding numbers in `theory.py`'s `s_eff` docstring. None has a script or output in `docs/learned/synthetic_validation/`.
    - **Severity:** minor.
    - **Fix:** keep those scripts and outputs beside the others, or mark the numbers unverified.
    - **Verified:** no (they live in the blinded run record).

13. **Fig 2 caption, "The at-most-one-event term closes the participant residual".**
    - **Issue:** it contradicts the text's "not to within noise" (though see finding 3).
    - **Severity:** minor.
    - **Fix:** make the two agree.
    - **Verified:** yes.

14. **"A latency template … reads as extra jitter" (bold claim, and in the GLOSSARY).**
    - **Issue:** this is derived only. Plan item 3 says it is still owed by simulation, and it holds in expectation only under random membership.
    - **Severity:** minor.
    - **Fix:** mark it "derived, not simulated; random membership".
    - **Verified:** yes.

15. **Settled rows for Aim 0 ("derived and checked").**
    - **Issue:** they lack the "(one generator)" scope the Aim 1a row carries. The fit assumes fixed k, Gaussian jitter and the 20 s minimum separation. Blind A's caveat that "real data will need a mixture over k" is dropped.
    - **Severity:** major.
    - **Fix:** add the scope and the assumptions to each row.
    - **Verified:** yes.

16. **Figures 1–4, panel titles.**
    - **Issue:** panels carry letters only, and no panel states why its result matters.
    - **Severity:** minor.
    - **Fix:** add inferential titles.
    - **Verified:** yes.

17. **Fig 3 A.**
    - **Issue:** all 7 simulated points sit 1–2 % below the prediction. They share one 400-recording random baseline, so the errors are correlated, and the log axis hides it.
    - **Severity:** minor.
    - **Fix:** note it, or give a per-point baseline.
    - **Verified:** yes.

18. **"Two causes, neither tested here" (why the assessor's jitter saturates).**
    - **Issue:** both blind passes modelled the chance/event mixture; B reports a 2 % median error on assessor jitter. The sentence under-reports existing evidence.
    - **Severity:** minor.
    - **Fix:** cite B's check.
    - **Verified:** yes.

19. **"Where it stands": "For events of 10 or more cells and jitter from 0.2 s up, the … output is predicted".**
    - **Issue:** this conflates two results. The participant prediction holds at all jitters; the 0.2 s limit is the joint fit's.
    - **Severity:** minor.
    - **Fix:** separate the two.
    - **Verified:** yes.

**Checked and clean:**
- **Joint-fit, residual and chance numbers:** all match `theory.summary()`. These are the joint-fit medians and ranges, the participant, rate and share residual medians and worsts, the share and participant ranges per window, the 17 of 720 refusals, the chance rates, the assessor jitter ranges at 0.05 Hz, and K=6's condition medians of 0–0.27.
- **Membership:** the verdict numbers (100 %, 83 %, 27 %, 3/60) match `membership_limit.json`.
- **Order:** the numbers (0.503, 0.753, 0.176, M=16 about 10 % high, c across fields) match `order_limit.json`.
- **August todo:** its figures (0.101, 0.036, 0.099, ρ −0.75 and −0.40) match.
- **Blind passes:** the comparison table's attributions match both blind reports.
- **Commit timing:** `git show d495ab0e` (15:40) already holds the at-most-one-event term, and the blind agents worked at c442014a, so "committed before either blind report" is plausible.

**Relevant files:**
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\goals\synthetic-validation.md`
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\learned\synthetic_validation\aim1_one_source.json`
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\learned\synthetic_validation\theory.py`
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\learned\synthetic_validation\order_limit.json`
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\learned\synthetic_validation\membership_limit.json`
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\docs\GLOSSARY.md`
