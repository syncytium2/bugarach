GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**What I checked first.** I read the method's code: `tools/measure_coordination_rates.py` (factorial_cumulants, population_cumulants, shifted, excess_cumulants, solve, pooled_ratio, per_recording, truth, _sim, calibrate, CAL_NO_PROBE). I read the generator in `src/bugarach/simulate.py` (background clumping, the hot stretch with its ramp, distractors, planting) and `src/bugarach/bench.py` (BENCH_RECORDING, REGIMES, ELEVATED_RATE_RECORDING, make_recording, the spacing note). I also read `tools/fit_background_shape.py` (its floors), `docs/learned/runs/2026-09-25-real-intervals/README.md`, the explainer script and `numbers.json`. For the literature I looked up Ehm, Staude & Rotter 2007 (arXiv 0711.1965), the Staude, Grün & Rotter 2010 Frontiers abstract and the Pipa 2008 bibliographic record.

I re-derived the algebra by hand:
- The compound-Poisson factorial cumulants are f₂ = λw·E[k(k−1)] and f₃ = λw·E[k(k−1)(k−2)].
- The fixed-model bias for sizes 10/6/3 is −14% on the share, +38% on k and −37% on λ. The measured values are −18%, +26–33% and −33–37%. The difference is consistent with window-edge loss.
- For one size of 6, the binomial model's bias is +21%. The measured value is +17%.

I recomputed every percentage in the README against `numbers.json`. All match.

**What is correct.** The formulas, the 90/720 ordered pairs and triples, k = f₃/f₂ + 2, the half-window second count, 20 copies and 2-window spacing, "at most about half a minute" (offsets reach ±32 s), the per-cell clumping, the floors 300 s / 20 onsets / 5 cells, quiet 0.0049 and busy 0.0169, the 41 s median gap (41.3 s), the 0.106 s jitter (CAL_JITTER, not the bench's 0.105) and the citation volumes and pages. Figure 3C is exactly the shipped calibration: mcr._sim, 48 recordings, N_SURR = 20, default realistic spacing, pooled over the 48.

**Two runs I did, scratch only, no files written.**
- 6 null recordings each with a sharp stretch at +0.1334 onsets/s, 1 s window. The share of raw f₂ the shifted copies remove is 16% at 10 s, 66% at 60 s, 92% at 300 s and 97% at 900 s. The excess pairs per recording are 143, 358, 373 and 292.
- The 24 quiet and 24 busy no-moment runs, pooled. Pooled f₃ is −0.0009 (quiet) and −0.0078 (busy), so there is no answer. f₃ is positive in 10 of 24 and 11 of 24 recordings.

## Findings

1. **README l.175–182 (Figure 5A text): the length dependence is attributed to the wrong cause.**
   - **Issue.** "So it is counted most when it is short … 8% … 3.0% for 5 minutes and 1.2% for 15 minutes." For stretches of a minute or more, the spurious excess is roughly the same at every length: about 360 excess pairs per recording at 60 s and 300 s, and 290 at 900 s. The share of onsets × total onsets per cell is about constant (8.2% × 21.2 ≈ 174, 3.0% × 53.2 ≈ 162, 1.2% × 133 ≈ 155). The share falls only because a longer stretch adds more onsets to the denominator. The 10 s point (3.7%) is *lower* than the 30 s point, because a stretch shorter than the ±32 s slide span is not yet saturated. The bold sentence "how fast the rate changes … not how long" is right about the count; the "counted most when short" sentence is wrong about why the share moves.
   - **Severity.** Medium.
   - **Fix.** Say that the edges add about the same false coordination at every length from about a minute up. A longer stretch adds more real onsets, so the same false part is a smaller share. Below the slide span (about a minute) the whole stretch is counted, which is why 10 s reads lower than 30 s.
   - **Verified.** Yes: my run plus arithmetic on `numbers.json`.

2. **README l.273 (For developers, "the elevated-rate note is CAL_NO_PROBE") against l.177–178: the page points at a tool note that says the opposite.**
   - **Issue.** The README says the shifted copies "remove most of it". CAL_NO_PROBE (tool l.259–260) says "The surrogates cannot subtract it either: per-cell circular shifts … break the joint rise up rather than preserving it." My run backs the README: 92% removed at 300 s. A developer following the pointer meets a contradicting mechanism. The tool's own module docstring (l.30–31, modulation slower than the span survives) agrees with the README, so the tool contradicts itself.
   - **Severity.** Medium. This is a defect in the tool that the page inherits through its pointer.
   - **Fix.** Add one sentence beside the pointer saying that CAL_NO_PROBE's account of the surrogates is superseded by Figure 5A. File a todo to correct CAL_NO_PROBE. The page is not the place to edit the tool.
   - **Verified.** Yes.

3. **README l.183 and Figure 5B x-label "the bench's 30 s ramps": the stretch has one ramp, not two.**
   - **Issue.** `simulate.py` l.911–913 thins with `rf = min(1, (ct-h0)/ramp_sec)`, so it ramps in only and switches off sharply. The bench docstring says "30 s ramps" too, and the page inherited it. This matters for the reader's inference: 5B at 28× (2.8%) nearly equals 5A's sharp 5-minute stretch (3.0%), and with both edges assumed ramped a reader concludes that ramps don't help. In fact one sharp edge remains, and a 30 s ramp is shorter than the ±32 s slide span anyway.
   - **Severity.** Medium.
   - **Fix.** Write "ramping in over 30 s and switching off sharply (the bench's elevated-rate stretch)" in the text and the axis label. Optionally file the bench docstring error.
   - **Verified.** Yes, from the code.

4. **README l.19 and l.170–194 (Figure 5 shares): the k behind every Figure 5A/5B number is borrowed from planted recordings, and the page does not say so.**
   - **Issue.** `in_run` computes each null or stretch recording's share with f₃/f₂ pooled over the 24 quiet recordings carrying 15 planted moments, plus that one recording. That reasonably mimics the tool pooling over a whole folder. But the reported share depends on that choice: a run of stretch recordings alone would pool its own edge-driven f₃/f₂ and give different numbers. A methods reader cannot reproduce or interpret 5A/5B without knowing it.
   - **Severity.** Medium.
   - **Fix.** Add a clause to the caption or the text: "each recording's share is worked out as one recording in a run alongside the 24 quiet recordings with planted moments, so its participants per moment come from them, as the tool pools over a folder."
   - **Verified.** Yes, from the code (`in_run`, `figure5`).

5. **README l.193–194: "If every recording in a run has no shared moments at all, the pooled triples are not above zero and the tool gives no answer." This is stated as a rule but is a coin flip.**
   - **Issue.** Excess f₃ is zero only in expectation. In my runs it was positive in 10 of 24 and 11 of 24 recordings, and the pooled sum happened to be negative both times. Another set of seeds can pool slightly positive. pooled_ratio then returns a small positive k − 2, and the tool reports a share driven by leftover f₂.
   - **Severity.** Low to medium.
   - **Fix.** "On these runs the pooled triples came out below zero and the tool gave no answer; with no shared moments they are as likely to come out just above zero, and then it gives a small, meaningless answer."
   - **Verified.** Yes: my run plus the pooled_ratio code.

6. **README l.229–230 and Figure 3C: the right answer counts the decoys as coordinated, and the page does not say so.**
   - **Issue.** The tool's `truth()` sums sizes over `gt.events + gt.distractors`. The bench plants 6 decoys of 6 cells each (distractor_frac 0.18). That is close to the number of real moments under realistic spacing (about 7). The page describes decoys as "near-coincidences it plants to test detectors", which a reader takes as negatives. So 3C's "planted share" includes them, and the moment sizes there are 10, 6, 6 (decoys) and 3, not three sizes.
   - **Severity.** Medium.
   - **Fix.** Add: "the tool's check counts the decoys (6 per recording, 6 cells each) as coordinated, since this measure cannot tell them apart; they are a fourth moment size."
   - **Verified.** Yes, from the code (`truth`, BENCH_RECORDING, simulate distractors).

7. **README l.248–250: the priority claim "What is this project's: using factorial cumulants and solving them for k and λ" overstates.**
   - **Issue.** Recovering how often joint events happen and how big they are (the jump measure ν = λ × size distribution) from the population count alone is the subject of Ehm, Staude & Rotter 2007, which the page cites one sentence earlier. It does so in full, by empirical de-Poissonization. That a compound Poisson count's r-th factorial cumulant equals λ·E[(k)ᵣ] is textbook. What is this project's own is the two-cumulant shortcut under a fixed-size or binomial closure, the share-of-events framing, the surrogate design and the application to calcium onsets.
   - **Severity.** Medium. This is a portfolio page read by outside reviewers.
   - **Fix.** "What is this project's: a two-cumulant shortcut (pairs and triples, closed by assuming every moment the same size) to what Ehm et al. estimate in full; reporting it as a share of events; …"
   - **Verified.** Partly. I confirmed Ehm 2007 estimates the jump measure from population counts. I could not confirm whether it uses factorial cumulants specifically.

8. **README l.239–241: what CuBIC infers.**
   - **Issue.** "use cumulants of the population count to infer how many neurons take part in coordinated events". CuBIC infers a lower bound on the order of correlation (the largest group whose joint events must be present), by hypothesis tests on cumulants. It does not estimate participants per event.
   - **Severity.** Low.
   - **Fix.** "…to infer the smallest group size that must be taking part in coordinated events".
   - **Verified.** No. This is from the method's documented purpose; I did not open the paper.

9. **README l.96 and Figure 2B: "≈ 8.1 cells per moment" is shown without its right answer.**
   - **Issue.** That recording planted moments of 10, 6 and 3 cells (mean 6.3). A first-time reader takes 8.1 as the correct reading. The size bias that explains it is only reached in Figure 3's section.
   - **Severity.** Low.
   - **Fix.** Add "(planted: 10, 6 and 3 cells, mean 6.3; why it reads high is under Figure 3)".
   - **Verified.** Yes: SIZES, the figure2 code and numbers.json k = 8.05.

10. **README l.86: "Figure 1D … every cell has the same number of ticks" is false of the figure as drawn.**
    - **Issue.** The shift preserves each cell's count over the whole 45 minutes. The 5-minute view in 1D shows a different stretch of each cell's train than 1B does, so per-cell tick counts in view differ.
    - **Severity.** Low.
    - **Fix.** "…every cell keeps the same number of onsets over the whole recording (not within these 5 minutes, since each train has slid)".
    - **Verified.** Yes, from the code (figure1 draws `sur` over t0–t1; `shifted` is circular by up to ±32 s).

11. **README l.190 (Figure 5C, "Each cell's own clumping is removed … the steady rows"): the quiet steady row does not show it.**
    - **Issue.** In that row raw f₂ is 0.0030 and excess 0.0014, so 52% is removed (`numbers.json`). Both are at noise level, so there is nothing visible to remove. The claim holds for the 13× row (99.4%) only.
    - **Severity.** Low.
    - **Fix.** Write "(Figure 5C, the steady 13× row; at the quiet background there is too little clumping to see)".
    - **Verified.** Yes.

12. **README l.187–188: "removes 99% of it" (the slow rise).**
    - **Issue.** The 99.0% in numbers.json is the share of the *whole* raw f₂ removed in the rising 13× row, not of the part the rise added. The rise adds about 0.186 (0.593 − 0.407), and the excess grows by about 0.0035, so about 98% of the rise is removed. The conclusion still holds; the quantity named does not.
    - **Severity.** Low.
    - **Fix.** "removes about 98% of what the rise adds" or "leaves 1% of f₂".
    - **Verified.** Yes, arithmetic on numbers.json.

13. **The tool's docstring claims, outside this page, that the two models "bracket the answer" (tool l.36 and l.175). The page's own data refute it.**
    - **Issue.** In Figure 3A and 3C both models read low: fixed −18% and −16%, binomial −8% and −2%. Fig 4 shows the binomial model also reads low on every set. The page itself does not repeat the claim; it describes the models correctly. This is noted for the record because a reader following the "For developers" link will meet it.
    - **Severity.** Low for the page; medium for the tool.
    - **Fix.** File a todo against the tool docstring. Optionally add one sentence: "the two models do not bracket the answer: in Figure 3A both read low."
    - **Verified.** Yes.

14. **README l.245–246: Pipa et al. 2008 as the source of the "spike-train shifting surrogate".**
    - **Issue.** The citation is correct (NeuroXidence, J Comput Neurosci 25:64–88). I could not confirm from an accessible source that the paper's surrogate is whole-train shifting. As I recall it, NeuroXidence shifts trains against each other by small amounts, which is far from this tool's ±32 s circular ladder. The page already hedges through the GLOSSARY.
    - **Severity.** Low.
    - **Fix.** Confirm the surrogate against the paper; if it is small-shift, say "(by small amounts; this tool's are up to half a minute and wrap round)".
    - **Verified.** No.

No paper needed `--need`. I fetched no PDFs. The scratch directory holds only an empty `mb-r2/role6/` folder (a heredoc write was blocked by the repo hook, and the checks ran inline instead).

**Paths.**
- Artifact: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`
- Figure script: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\explain_coordination_share.py`
- Numbers: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json`
- Tool (CAL_NO_PROBE at l.245–272, solve docstring at l.169–181): `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py`
- One-sided ramp at l.911–913: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\simulate.py`
- ELEVATED_RATE_RECORDING at l.1561 and BENCH_RECORDING distractors at l.1023: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\bench.py`

Sources:
- [Ehm, Staude & Rotter 2007, arXiv 0711.1965](https://arxiv.org/abs/0711.1965)
- [Ehm, Staude & Rotter 2007, Electronic Journal of Statistics](https://projecteuclid.org/euclid.ejs/1195051631)
- [Staude, Grün & Rotter 2010, PMC2906200](https://pmc.ncbi.nlm.nih.gov/articles/PMC2906200)
- [Staude, Grün & Rotter 2010, Frontiers](https://www.frontiersin.org/articles/10.3389/fncom.2010.00016/text)
- [Elephant CuBIC reference](https://elephant.readthedocs.io/en/v0.12.0/reference/cubic.html)
- [NeuroXidence (Pipa et al. 2008)](https://www.epistemio.com/p/Xd4R46GB)
- [dblp record](https://dblp.uni-trier.de/pid/91/133.html)
