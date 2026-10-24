GRANT 4 MISMATCH — missing none; holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs MCP (batch/update), plus deferred Dropbox, Gmail/etc. (I used none of the editing or writing tools on tracked files. The only files I wrote are in `_scratch/role-04/`.)

Run note for the ledger: this reviewer was spawned through the inline general-purpose fallback, not the named agent. The `roles:` line must say the review took a fallback path.

# Reviewer 2: findings on Aim 0 (synthetic-validation.md L25–163, plan L234–255, Figure 1)

Each row gives the location, the issue, its severity, a suggested fix, and whether I could check it against a source.

**1. L34–39, "predicted exactly … within about 0.03 in every cell"**
- **Issue:** False in both records. In `theory_check.json` (the reseeded run) the 0.01 Hz participant residual reaches 0.057, and 10 of 72 cells are over 0.03. In the shared-seeds record the worst is 0.086, with 9 cells over 0.03. L51–53 then gives different numbers (median 0.011, worst 0.06), so one page carries two inconsistent claims. The L34–43 bullets were written in commit d495ab0e, before the reseed, and were never updated.
- Each cell is a median of only 5 seeds. The per-cell seed SD of k̂/k is 0.014 at 0.01 Hz and 0.038 at 0.05 Hz (k ≥ 10). A median residual of 0.011–0.016 is therefore about 1–2 sampling SEs: "consistent within 5-seed noise" is supported, "exactly" is not.
- Blind B, over 60 seeds, saw f3 5–7 % below prediction at 0.05 Hz, and A saw rate 3–5 % above (L98–99). Both are unexplained residuals at exactly the level "exact" claims.
- The event-rate and share predictions are much looser. At 0.01 Hz the rate residual has median 0.039 and max 0.29, which the heading also covers.
- **Severity:** major.
- **Fix:** Retitle to "predicted to within sampling noise (5 seeds per cell)". Delete the stale "0.03 in every cell". Give separate residuals for participants, rate and share, and state the unexplained 60-seed residuals beside the headline.
- **Verified:** yes.

**2. L47–48 and L52, the "Not predicted" exclusion**
- **Issue:** The excluded set is wider than stated. The 0.05 Hz claim filters to k ≥ 10, which drops every 5-cell cell, the 45-event ones included. At 0.05 Hz the 5-cell, 45-event cells also miss: 0.843 predicted against 0.672 measured at w = 4, and 0.831 against 0.659.
- **Severity:** minor.
- **Fix:** Say "all 5-cell cells at 0.05 Hz", or report them.
- **Verified:** yes.

**3. L40–43, the jitter fit ("0.17, 0.48, 1.0 at both backgrounds … floors near the 0.1 s frame … one of its best")**
- **Values are stale.** In the reseeded record 0.05 Hz gives 0.147, 0.496 and 0.936, so 0.2 s reads about 0.15 s (IQR 0.10–0.19), not 0.17 s.
- **The floor is not the frame.** The median at planted 0.05 s, 0.05 Hz, is 0.0074 s. That is exactly the optimiser's lower bound: grid 0.01 × e^−0.3 in `jitter_from_windows`. Up to 9 of 10 recordings per cell sit on that bound, and 3 of 10 do so even at planted 0.2 s (0.05 Hz, k = 10).
- **Undisclosed failures.** The pooled figure hides 3–5 of 30 unusable (NaN) recordings at 0.05 Hz. For k = 5 at 0.05 Hz, 4–5 of 10 are NaN, with IQRs such as 0.42–1.78 s.
- **Severity:** major.
- **Fix:**
  - Replace the numbers from the current `theory_check.json`.
  - Report the bound-hit and NaN counts.
  - Break the result down by participation.
  - Drop "one of its best" (the coordinated share is within about 20 % everywhere; this is not).
  - Note that the fit uses the Poisson g₂ while participants needed the exact form, which is a candidate source of its −15 % bias.
- **Verified:** yes (recomputed per k).

**4. L44–46, "Chance clusters … within about 10 % at every K and background"**
- **Issue:** The 10 % holds only for medians pooled over participation and jitter. Per design cell, 43 of 144 miss by more than 10 %. At 0.01 Hz, K = 6, k = 5, the measured rate is 0.00–0.16 of predicted, and K = 6, k = 10, σ = 1 s gives 0.29–0.33.
- The check's prediction is chance + *all* planted events. It assumes every planted event yields one cluster, so it can only pass where chance dominates (0.05 Hz, K = 3 or 4) or detection is near-certain. Blind B's `theory_assess.py` modelled per-event detection (D) and this check did not.
- Figure 1 shows the miss: in the top row's event-rate panel the green K = 6 curve falls to 0.3× at 1 s jitter while its dashed prediction stays at 1.
- **Severity:** major.
- **Fix:** Restate as "the chance term is predicted within about 10 % where chance dominates". Either add a detection term (B's D) or say planted detection is not predicted. Show the per-cell breakdown.
- **Verified:** yes.

**5. L55–104, "replicated blind … All three reached the same core answer independently … one answer reached three ways"**
- **The shared inputs.** The blind agents had the same prompt (Tony's question), the same repo at `main` (c442014a), the same Aim 1a record (the shared-seeds one) and the same tools, and were presumably the same model.
- **The agreement was largely forced by the shared inputs:**
  - The tool under prediction is defined by factorial cumulants, and its docstring cites the Kuhn–Aertsen–Rotter cumulant route. Predicting it is necessarily a cumulant calculation, so "the cumulant route is the one all three found first" is close to forced.
  - Row 2 ("window must exceed jitter") was already stated in bold on `main`'s goal page (L31–33 at c442014a), which the agents read.
  - Row 4 (the binomial tail) is the obvious model for `_clusters`.
- **Same route, different results.** On jitter the three disagree in sign: this session reads 0.2 s as about 0.17 s, while B's w1/4 ratio reads it 1.05–1.15× high. The table ticks all three as agreeing.
- **Untested row.** Row 5 (two equal-jitter sources not identifiable) was simulated by no one, yet it is counted as agreement.
- **Timing.** The record does not show whether the first session's "second try" at the exact term (d495ab0e, 15:40) came before or after any blind output (blind README at 15:54).
- **Severity:** major.
- **Fix:** Call it "a consistency check by agents sharing prompt, repo, record and tool definitions, not independent replication". Mark row 5 as asserted, not tested. Show the jitter disagreement. Log the timing of the second try against the blind runs.
- **Verified:** yes (git history and B's `.txt` files).

**6. L86–87, "The ADR-0008 chance floor … 6 at 0.01 Hz … so a 5-cell event can never pass it"**
- **Issue:** Contradicted by blind B's own count-detector table. At k = 5, K = 6, 0.01 Hz, σ = 0.2, recall is 0.344 (sim 0.330). Chance joiners inside the window lift a 5-cell event over 6 a third of the time.
- The floor's constants (WINDOW_SEC, J_SEC, FA_PER_HOUR) are not stated on the page.
- **Severity:** major.
- **Fix:** Say "a 5-cell event passes only via chance joiners (about 1/3 at 0.01 Hz)". State the floor's window and false-alarm budget.
- **Verified:** yes.

**7. L141, "no order: F ≈ 0.375/√n̄", and L152–153, "the indicator and its null bias are closed forms"**
- **Issue:** 0.375 is an empirical constant fitted from simulation at N = 33 and k = 10, not derived. Rerunning the script's own statistic (`_scratch/role-04/order_probe.py`):
  - N = 15, k = 5: c ≈ 0.43
  - N = 100, k = 10: c ≈ 0.21
  - N = 100, k = 30: c ≈ 0.37
- So it is not a closed form, and it does not transfer across field sizes.
- **Severity:** major.
- **Fix:** Call it "an empirical constant, about 0.375 at N = 33, k = 10; depends on N and k". Derive it or tabulate it.
- **Verified:** yes (ran it).

**8. L132–134 and L152, "the sort is a score sort … Under the template model the optimal order is the score order in expectation"**
- **Issue:** Never tested against an optimiser. An insertion hill-climb starting from the score sort (a stand-in for the annealing) raises the no-order indicator by about 35 %: c goes from 0.37 to 0.50 at N = 33, and the same direction holds at every N and k tried. `synfire_scan.py` also keeps the best of `--restarts` anneals, which raises the bias further.
- So the score sort's null bias is not the brute-force method's null bias. With order present the gap is small (+0.01–0.02 at τ = 0.25–2.5).
- "Optimal in expectation" is asserted without proof. The table's M-template "prediction" also adds a *simulated* null bias in quadrature (`np.hypot(pred_many, bias)`, with bias measured) without saying so.
- **Severity:** major.
- **Fix:**
  - Drop or prove "optimal in expectation".
  - Say the closed forms are for the score-sort statistic, not SPIKE-order's annealed optimum.
  - Say the M-row includes a measured bias term.
- **Verified:** yes (ran it).

**9. L143–149, "That is the August finding … anti-correlated with spike count (ρ −0.75) … and why the order-free control's median sat at 0.10"**
- **Issue:** Unsupported leap. Nothing was run on the real trains or with PySpike.
- August reports order *present*: 29 % and 54 % of recordings beat the null. "With no order present, the indicator is the optimisation's own bias" therefore cannot by itself be "the August finding" on real data.
- PySpike's indicator averages over all spikes, including non-coincident ones and empty trains (`synfire_scan.py` L70). Its normalisation differs, the annealing plus best-of-restarts bias is larger (finding 8), and c depends on N (finding 7).
- The 0.10 control median was never reproduced from the control's parameters.
- The slow stream's ρ −0.40 is not addressed.
- The ⚠ at L154 says "the scaling laws are the claim", but L143–147 asserts the explanation.
- **Severity:** blocking. The draft's own caveat concedes that the constants change, and the explanation depends on them.
- **Fix:** Restate as a hypothesis: "a 1/√n̄ bias would produce this anti-correlation; untested on the August trains." The test with power: run `synfire_scan` (PySpike) on order-free simulations matched to the August recordings' N and spike counts, and check that F·√n̄ is constant and that it reproduces the 0.10 median and ρ.
- **Verified:** yes (August todo, `synfire_scan.py`).

**10. L121–127, the membership law and "perfect readout"**
- **The caveat is buried.** "Membership is read perfectly here" is one sentence after the numbers, yet the conclusion "an assembly converges to random as 1/M" is drawn without it.
- **Wrong citation.** "A factor blind pass B derived" for chance joiners and missed members: the blind passes predate the membership question. The only related item in `blind_b` is the assessment's gathered count, k + (N−k)(1−e^(−3b)), which is not a shrink factor for pair-dispersion excess, and missed members are not covered at all.
- **Convergence is stated for means only.** I checked the noise: a single recording's D ratio has SD 0.11 under random membership (95th percentile 1.19). Detection is 100 % at M = 45, about 68 % at M = 150, and about 12 % at M = 1000 (5 % is chance).
- **Severity:** major.
- **Fix:**
  - Put "perfect readout" in the claim sentence.
  - Fix or remove the B citation.
  - Give the per-recording SD and the detectability against M.
- **Verified:** yes (ran it, and grepped `blind_*`).

**11. L118, the table row "which cells: seen by `bugarach.assembly`"**
- **Issue:** `bugarach.assembly` was not run in Aim 0. Its seeing membership is asserted from its purpose.
- **Severity:** minor.
- **Fix:** Mark it as untested (Aim 1b).
- **Verified:** no.

**12. Figure 1 (read as an image)**
- **Pooling hides the failures.** Points pool over participation (0.15, 0.3, 0.6) and event count (15, 45), so the k = 5 failures (NaN jitter, the K = 6 misses) are invisible.
- **Two visible contradictions with the text:**
  - The top-row event-rate panel: K = 6 at 1 s jitter is 0.3× against a dashed 1×.
  - The jitter panel: the fitted jitter at 0.05 s has bars from about 0.15× to 1.1× and medians of 0.5× and 0.15×, which is the bound artefact, not "floors near the frame".
- **Scale.** The log y-axis (0.1–30) cannot show the 0.01-level agreement that "exact" claims.
- **Titles.** Panel titles name quantities, not why they matter.
- **Severity:** major.
- **Fix:** Add a per-participation breakdown (panels or markers by k), and a residual panel (measured − predicted) on a linear scale. Mark NaN and bound-hit counts.
- **Verified:** yes.

**13. Constants undefined or unjustified on the page**
- K is never defined in Aim 0 (cells per 1 s bin).
- k = 5, 10, 20 are not stated (they come from 0.15, 0.3, 0.6 of 33).
- The merge rule behind (1−q)² (merge_bins = 2) and the gather ±1.5 s (wm_factor 1.5 × the 1 s bin) are given without a reason.
- The 0.375 constant (finding 7), the 20 s min_sep (only in parentheses), and the ADR-0008 window and false-alarm budget (finding 6).
- "Within about 0.03" never says it is a fraction of planted (ratio units).
- The jitter search bounds (0.01–5 s, ±0.3 in log) are undocumented and actually bind.
- **Severity:** minor (finding 7's constant is major).
- **Fix:** Define each one where it is first used, and say why.
- **Verified:** yes.

**14. L246–247 (plan), "with equal jitters only a combined participation term is identifiable (Aim 1c's answer, predicted before it is run)"**
- **Issue:** Stated as an answer. It is an untested claim from second- and third-order cumulants only: spacing or rate differences, or higher cumulants, are not ruled out.
- **Severity:** minor.
- **Fix:** "predicted from pair and triple cumulants; to be tested in Aim 1c".
- **Verified:** no.

**15. L77–78, "The 0.05 Hz rows now sit on the prediction" after the reseed**
- **Issue:** Supported for k ≥ 10. The signed median residual moved from −0.040 to −0.005, but the worst is still 0.106 and there are only 5 seeds.
- **Severity:** minor.
- **Fix:** Add "(k ≥ 10, median of 5 seeds; worst 0.11)".
- **Verified:** yes.

## Checked and fine
- The truncated-Gaussian 0.74 s figure.
- The seed fix: per-recording seeds in `aim1_one_source.py`.
- The membership numbers, which reproduce.
- The one-template order values at τ = 1 and τ = 2.5, which reproduce from `order_limit.py`.
- B's floor table, which matches `window_floor`.

## Scratch
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\role-04\order_probe.py`
- `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\role-04\theory_check.json` (from rerunning `check()` on the shared-seeds record)
