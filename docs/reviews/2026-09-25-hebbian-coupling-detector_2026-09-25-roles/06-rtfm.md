GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I also hold SubagentHandback. I have no Edit, Write or NotebookEdit. Scratch dir `<scratchpad>` was created but nothing was written to it. The repo's heredoc hook blocked the scratch script, so the numbers below come from inline `python3 -c`.)

# Role 6 (Methods / RTFM): findings on `docs/proposals/2026-09-25-hebbian-coupling-detector.md`

**What I grounded in:**
- `clamor:clamor/malsburg1986.py`: `coactivity`, `control`, `modulate`, the `S_MIN`/`S_MAX` constants and `selftest`, all read in full. I re-ran the kernel and control logic line by line in pure Python; no numpy or torch is installed on this machine.
- `clamor:lit/malsburg-1986.md`.
- `src/bugarach/graph.py`: `sttc`, `sttc_matrix`, `modularity_vs_null`.
- `src/bugarach/assess.py`: `circular_shift_trains`.
- `tools/modularity_null.py`.
- `docs/learned/runs/2026-09-22-jitter-correlogram/README.md`.
- `current_export.toml` and `pyproject.toml`.
- Outside sources: Cutts & Eglen 2014 (STTC and its Δt), Ahn, Bagrow & Lehmann 2010 (link communities), Aicher, Jacobs & Clauset 2015 (weighted SBM).

**Lit-cache:** I could not get the 1986 PDF. It is closed access, gitignored in clamor and not on this machine, and `fetch_paper.py` is deliberately not vendored here. So on eqs 7 and 8 I checked the proposal against clamor's transcription only, not against the paper. **--need: von der Malsburg & Schneider 1986, *Biol Cybern* 54:29–40, DOI 10.1007/BF00337113**.

## Findings (location · issue · severity · suggested fix · verified against a source?)

**F1 · "Equation 8, the bound" (l.47–50), with "How the code arrives" (l.163) · HIGH.** The 80 % bound is not enforced by `control()`. It comes from the clamp to `S_MIN`/`S_MAX` inside `modulate()`, which the proposal does not copy.
- q(s) is only zero at s₀(1 ± s_d). A finite step overshoots that edge, and past it q turns negative. Measured: q(s₀ + q₀) = −0.00085.
- At the paper's q₀ = 0.01, one Co = +1 step at rest takes s from 0.012 to 0.022, which is above S_MAX = 0.0216. clamor's `Q0_OVER_HALF_RANGE = 1.04` records exactly this.
- With the clamp, the edges are absorbing: q = 0 there, so the entry never moves again. clamor's own comment says "a single coincident burst puts a resting synapse ON the clamp … it can never move again".
- So at q₀ = 0.01, each entry of D is set by the sign of the **first** in-window onset pair and then frozen. That is the opposite of "a stray episode of false synchrony cannot move a coupling far".
- Derived: the bound holds without the clamp absorbing only if q₀ < ½·s₀·s_d = 0.0048. Proof sketch: in x = (s−s₀)/(s₀s_d) the step is r(1−x²) with r = q₀/(s₀s_d), and it overshoots x = 1 iff r(1+x) > 1.
- The paper's 0.01 is above that limit, so is the "one between" if it is set above 0.0048, and q₀/12 is below it (it takes 125 coincidences to approach the edge).
- **Fix:** name the clamp and copy it (or `modulate`'s clamp line) along with the two functions. State the 0.0048 limit. Say that at q₀ = 0.01 the rule is a first-event latch, and consider dropping 0.01 from the stage-1 sweep or labelling it as that.
- Verified: yes, against clamor code plus arithmetic.

**F2 · "Pairs" (l.62–64) and "The kernel" (l.68–72) · HIGH.** The proposal does not mention `coactivity`'s wrap. With period 2w, `coactivity` wraps Δt modulo 2w into (−w, w]. Measured with w = 0.3: Co(0.45) = 0, Co(0.6) = **+1**, Co(0.9) = −1, Co(1.2) = **+1**.
- In clamor the gate that stops this is in `modulate()` (`seen = … dt.abs() <= period + burst/2`), and that is not being copied.
- If the implementation does not gate |Δt| ≤ w **before** calling `coactivity`, an onset pair 2w apart counts as a perfect coincidence.
- **Fix:** say explicitly that pairs are gated to |Δt| ≤ w (in integer frame lags) before the kernel, because the copied function wraps. Add a test at Δt = 2w.
- Verified: yes.

**F3 · "On the frame grid, the ends count half" (l.80–84) and "The width" (l.85–91) · HIGH.**
- The trapezoid algebra is correct. The plain lag sum from −K to K is −1 for every K and the trapezoid gives 0 (checked for K = 2..5). The −1 comes from the extra −K term on top of a full period of roots of unity.
- **But the argument needs w to be a whole number of frames, and the proposed widths are not.** Two, three or four jitters give fast w = 0.212, 0.318, 0.424 s (2.12, 3.18, 4.24 frames) and slow w = 0.270, 0.405, 0.540 s (2.70, 4.05, 5.40 frames).
- At those widths there is no lag at ±w, so "end lags" is undefined. The uniform-null lag sum is −0.79, −0.66, −0.53 (fast) and **+0.42**, −0.90, −0.20 (slow). The drift sign depends on the fractional part of w/frame, not on "longer or shorter".
- **Fix:** round w to an integer number of frames K for each recording's own frame grid, work in integer lags (this also avoids float-equality trouble at the end lags), then apply the trapezoid.
- Verified: yes, arithmetic. The claim that onsets sit on the 0.1 s grid comes from the jitter README; I could not check it against the data (no export folder on this machine).

**F4 · "The width" (l.85–91) · HIGH.** The width is set from the wrong quantity, and the low end of the sweep carries almost no signal.
- The jitter README's 0.106 / 0.135 s is **σ, each participant's scatter around the shared time**. Pair lags, which are what the kernel sees, have SD σ√2 (README: "pair lags scatter with SD σ√2").
- The kernel's zero crossing is at w/2. At w = 2σ that is 0.7 SD of the pair-lag spread.
- Expected Co for a truly coordinated pair (Gaussian pair lag, rounded to 0.1 s frames):

  | stream | w = 2σ | w = 3σ | w = 4σ |
  |---|---|---|---|
  | fast | 0.08 | 0.33 | 0.53 |
  | slow | 0.18 | 0.34 | 0.54 |

  In the continuous limit this is roughly exp(−π²/m²).
- 17–30 % of coordinated pairs land in the negative lobe. At 2σ a real assembly member gains about 0.08 per coincidence, which is nearly indistinguishable from the null.
- **Fix:** write w in terms of pair-lag spread (σ√2) and show E[Co | coordinated] for each sweep value. Consider dropping 2σ, or add 5–6σ.
- Also: the README has a ⚠ saying it was measured on the 2026-09-17 folder and "the data have since changed". The proposal cites the numbers without carrying that forward.
- Verified: yes (README plus arithmetic).

**F5 · "Why that point and no other: it is rate-neutral" (l.73–79) and stage 1 (l.143) · MEDIUM.** The proposal treats "zero expected update" as if it meant "rate-neutral". It is not.
- The expected increment is zero, and before the clamp it is exactly zero (a martingale), not just "to first order".
- But the **spread** of D grows with the number of in-window onset pairs, which is roughly the product of the two rates. Under independence, |D_ij| and ‖D‖_F are larger for busy pairs.
- Readout 1 survives this because the circular shift preserves each ROI's rate.
- Readout 3 does not: busy pairs get large random-sign weights in E(t).
- The stage-1 check "D should stay at s₀ within surrogate spread" has a typo (D = W − s₀ should stay at **0**) and cannot detect the problem, because the surrogate spread scales the same way.
- **Fix:** say "mean-neutral, not variance-neutral". In stage 1, measure var(D_ij) against the rate product under independence, and normalise E(t) or D by the null SD.
- Verified: yes (derivation).

**F6 · "Any other window length breaks it" (l.77–78) and "How the code arrives" (l.171–173) · MEDIUM.**
- "Any other" is false as written. Because of the wrap, the continuous integral is 2w/π·sin(πW/w), which is also zero at W = 2w, 3w and so on.
- The two sections also contradict each other. l.72 says the interpolated (judgement-call) branch of `coactivity` "is never exercised". l.172 says stage 1 "sweeps w against the window, where the interpolated form is exercised".
- The interpolated branch runs only when burst ≠ period/2. With period 2w and burst w it is never exercised, whatever the window.
- **Fix:** drop the l.172 justification, or state which sweep calls `coactivity` with burst ≠ period/2.
- Verified: yes (code).

**F7 · "Pairs" (l.62–63) · LOW–MEDIUM.**
- "On each onset of ROI i, every onset of every other ROI j within ±w contributes one update to W_ij and W_ji" visits each onset pair twice, once from i and once from j. That doubles the effective q₀, which matters given the 0.0048 limit in F1.
- "Walk … in time order" cannot see an onset of j that comes later but is still within w when i's onset is processed.
- **Fix:** define the update once per unordered onset pair, applied when the later onset arrives.
- Verified: yes (reading).

**F8 · Check B (l.129–135) · MEDIUM.** The comparison is not well posed as stated.
- (a) STTC at `dt = w` counts every |Δt| ≤ w as coincident (tiles are ±dt, per Cutts & Eglen and `graph._tile_fraction`). The kernel counts w/2 < |Δt| ≤ w *against* the pair. The STTC matching the positive lobe is `dt = w/2`.
- (b) STTC is NaN for an ROI with no events in the window (`graph.sttc`). D is exactly 0 for such pairs, and for any pair with no in-window onset pair. The proposal does not say how NaNs and the mass of tied zeros enter the rank correlation.
- (c) At q₀ = 0.01, D is effectively three-valued {−0.0096, 0, +0.0096} (F1), so Spearman ρ mostly measures ties.
- (d) At small q₀, D scales like a count (it grows with rate) while STTC is rate-normalised. So ρ < 0.9 could come from normalisation alone and would not show that the negative lobe adds anything.
- **Fix:** compare on pairs where both are defined, and use a tie-aware statistic (Kendall τ-b). Compare against STTC at both w/2 and w, and against the unbounded signed kernel sum, which isolates the bound's contribution from the lobe's.
- Verified: yes (code plus Cutts & Eglen 2014).

**F9 · Check A (l.122–127) · MEDIUM.**
- (a) "The existing STTC matrices" are not stored anywhere. `tools/modularity_null.py` writes only meanSTTC and Q. The only STTC ever computed here used `dt = 2.0 s`, about 5–10× the proposed w, and a ±20 s jitter null (`modularity_vs_null`), not the circular shift. A Check A run at dt = 2 s tests a different timescale than the rule, and its stop rule would not carry over to D. Name the dt, ideally w or w/2.
- (b) `sttc_matrix` puts 1.0 on the diagonal and NaN rows for silent ROIs. Both must be removed before any eigen-decomposition, or the diagonal inflates λ₁.
- (c) The statistic is ill-posed. "Share of off-diagonal variance left after the leading eigenvector, against the same share on surrogates" compares against a noise matrix whose share is near 1 whatever the structure. A rank-1-plus-modules matrix and a pure rank-1 matrix both read below the null, so "at null level" does not mean "nothing beyond the core". Test λ₂ (or the largest eigenvalue of the residual after rank 1) against the surrogate distribution of λ₁ of the surrogate matrices.
- Verified: yes (code).

**F10 · Readout 1 (l.99–102) · LOW.**
- "Leading eigenvalue" of a signed symmetric D needs to say whether it means the largest algebraic or the largest absolute value.
- Using the circular shift as a null for a statistic of the learned matrix is valid if, and only if, the full rule (including clamp and ordering) is **re-run** on each surrogate, which the text says. `circular_shift_trains` expects onset times relative to the window start and wraps them; the text should say it is applied per window.
- Known limit: the shift destroys shared slow rate co-modulation as well as timing. The zero-mean kernel mostly cancels modulation much slower than w, but only if F3 is fixed.
- Verified: yes (`assess.py`).

**F11 · Readout 3 (l.107–110) · HIGH.**
- "Threshold set on the circular-shift surrogates" is ambiguous. If the real-data D is applied to shifted trains, the null is too low: D was learned on the same frames it now scores, so in-sample frames score high by construction and there is no matching surrogate.
- **Fix:** relearn D on each surrogate and score that surrogate with its own D, or learn D on a held-out part of the baseline. Also, E(t) sums over |A|² pairs, so it scales with the active count squared. Say how that differs from CoactDetect beyond the rank-1 remark.
- Verified: yes (reading).

**F12 · Readout 2 (l.103–106) · MEDIUM.**
- Mixed-membership SBM (Airoldi et al. 2008) is defined for binary adjacency. The positive part of D needs a weighted variant (e.g. the weighted SBM of Aicher, Jacobs & Clauset 2015, which also handles signed weights without thresholding). Link communities (Ahn, Bagrow & Lehmann 2010) accept non-negative weights.
- Taking the positive part throws away the negative lobe, which Check B names as the rule's contribution.
- Every overlapping-community method returns communities on noise. The readout needs its own surrogate test, as the modularity work had.
- Per recording there are about 32 ROIs (2,109 ROIs / 66 recordings in `current_export.toml`), which is very little data for a mixed-membership fit.
- **Fix:** name the method and variant, and add the null test.
- Verified: partially. I checked Ahn and Aicher; MMSB is from memory.

**F13 · "Equation 7, the kernel" (l.42–45) and "The kernel" (l.68–71) · none (confirmed correct).**
- Co = +1 / 0 / −1 at 0, w/2, w with period 2w and burst w reduces to cos(πΔt/w). The selftest pins this at period 6 and burst 3 for Δt from −3 to 3 against cos(2πΔt/T) (tolerance 1e-6), plus the three points for burst 1–5.
- `control()` matches q₀(1 − ((s−s₀)/(s₀s_d))²). s_d = 0.8 gives [0.2 s₀, 1.8 s₀], "within 80 %", as clamor's notes say.
- One wording point: "checked in clamor's selftest()" is accurate, but the selftest checks the arithmetic only. It does not check the clamp or the wrap gate, which are what F1 and F2 depend on.
- Verified: against the transcription yes; against the paper no (--need above).

**F14 · "How the code arrives" (l.168–169) · none.** torch is in the `dev` and `dl` extras (`pyproject.toml` l.28, l.33), and CI installs `dl` (`ci.yml` l.73). Verified: yes.

Sources:
- [Cutts & Eglen 2014, J Neurosci (PubMed)](https://pubmed.ncbi.nlm.nih.gov/25339742/)
- [Ahn, Bagrow & Lehmann 2010, Nature](https://www.nature.com/articles/nature09182)
- [Aicher, Jacobs & Clauset, weighted SBM (arXiv 1404.0431)](https://arxiv.org/abs/1404.0431)
