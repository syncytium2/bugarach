GRANT 2 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred; loadable), plus Agent, Artifact, PowerShell, Skill, ToolSearch, Claude Docs MCP (batch/update), and deferred Dropbox, Gmail/Docs write tools

This is a finding about the run, not about the artifact. I was spawned through the inline general-purpose fallback, so the run record's `roles:` line must say the review took a fallback path. I used none of the editing tools. I made no tracked-file edits, wrote nothing to Dropbox and committed nothing. Scratch is limited to `_scratch/role-02/`: PDFs copied for text extraction, plus `njp.txt`, `k2022.txt` and `gruen.txt`.

## Sources actually opened (text read, not remembered)
- **Kreuz, Satuvuori, Pofahl & Mulansky 2017**, *New J Phys* 19:043028, doi:10.1088/1367-2630/aa68c3. Read from the lab copy in `01-lit` (read-only), §§2.4–2.5, 3.1 and 4.
- **Kreuz et al. 2022**, *J Neurosci Methods* 381:109703 (arXiv 2205.09855). Full text.
- **Mariani et al. 2025**, *J Neurosci Methods* 416:110378 (arXiv 2410.15018v2). Read via the HTML, in two passes.
- **Kreuz 2026**, *Biol Cybern* 120(3):21, doi:10.1007/s00422-026-01045-5 (arXiv 2510.07140v1). Read via the HTML.
- **thomaskreuz.org** journal-article list, 2017 onward.
- **Grün, Diesmann, Grammont, Riehle & Aertsen 1999**, *J Neurosci Methods* 94:67–79. Full text. Note that its page-1 header prints "93"; PubMed and the running heads give 94(1).
- **CuBIC: Staude, Rotter & Grün**, *J Comput Neurosci* 29:327–350, doi:10.1007/s10827-009-0195-x. Read the first half of the PMC text. The year is listed as 2009 online and 2010 in print.

## Sources confirmed by metadata only (existence and venue, text not read)
- Ehm, Staude & Rotter 2007, *Electron J Stat* 1:473–495, doi:10.1214/07-EJS095.
- Coppersmith, Fleischer & Rudra 2010, *ACM Trans Algorithms* 6(3):55.
- Shah & Wainwright 2018, *JMLR* 18(199):1–38. The JMLR version calls the method "Borda counting"; the arXiv version calls it "Copeland".
- Williams, Degleris, Wang & Linderman 2020, *NeurIPS*, arXiv 2010.04875.
- Bair, Zohary & Newsome 2001, *J Neurosci* 21(5):1676–1697.
- Greiner's relation (Greiner 1909; Kruskal 1958), via secondary sources.

## Findings
Columns: location · issue · severity · suggested fix · verified against a source?

1. **L119, L129–135, plan L240 · SPIKE-order and the Synfire Indicator are never cited on the goal page.** "The published method" has no reference. `order_limit.py` says only "Kreuz et al. 2017", with no venue. **Medium.** Cite Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J Phys* 19:043028, doi:10.1088/1367-2630/aa68c3, at first mention. I confirmed the NJP paper itself defines the Synfire Indicator (§2.4, eqs 11 and 14). That also closes the ⚠ left open in `todo/2026-08-18-synfire-order-is-not-the-assembly-question.md` L66–69. **Yes.**

2. **L131–134, L141 · The indicator is normalised differently from the paper it claims to follow.** The page says it scores order "the way SPIKE-order does", with F as the share of realised pair agreements, Σ n_ij D_ij / Σ n_ij. NJP eq. 14 is F = 2D< / ((N−1)M), normalised by all *possible* coincidences, with M the pooled spike count. Its ceiling is therefore SPIKE-synchronization C (stated in Kreuz 2022). With 10 of 33 cells per event, Kreuz's F would sit roughly a factor C ≈ 9/32 below the page's F. The ⚠ at L154–156 concedes that "normalisation change[s] the constants". But the no-order law at L141 is then tied to the August PySpike numbers (ρ −0.75, median 0.10), which carry Kreuz's normalisation. **Medium.** Name the normalisation difference where the method is introduced, and either rescale by C or say the 0.10 comparison is qualitative only. Boundary: whether the scaling claim survives the rescaling belongs to the technical roles. **Yes.**

3. **L141–149 · The null bias is presented as found here, but Kreuz 2017 already states it.** The page treats "the optimisation's own bias, falling with events per pair" as its own explanation. Kreuz 2017 §3.1 already says that non-zero sorted F on Poisson trains is a finite-size effect that converges to zero with more spikes. §2.5 also notes that the null would be binomial and analytic if coincident pairs were independent, and that pairs within one event are not. **Medium.** Credit Kreuz 2017 for the qualitative effect and for naming the obstacle. Claim only the 1/√n̄ form and its constant. Related: L153 calls the null bias a "closed form", but 0.375 is a constant fitted by simulation at N = 33 under the score sort. Say "fitted constant". The closest theory is random tournaments and the feedback arc set problem (Erdős–Moon, Spencer), which I did not open (⚠). **Yes** for the Kreuz content.

4. **L147–149 · The relabel null has prior art in Kreuz's own surrogate.** The page says "the null that todo had to build", i.e. permuting which cell owns each onset while keeping the onsets. Kreuz 2017 §2.5 already gives an event-preserving order surrogate: it keeps every spike's SPIKE-synchronization value and swaps the order of coincident pairs. The relabel null is a variant of that, not a new construction. **Low–Medium.** Add "a variant of Kreuz et al.'s (2017, §2.5) order surrogates". **Yes.**

5. **L132–134, L151–153, plan L240–241 · The "score sort instead of annealing" has prior art, including from Kreuz's own lab.**
   - **Forward trace, Kreuz lab.** Kreuz 2017 uses annealing for the sort, and Kreuz 2022 and the 2026 review still do. No Kreuz paper through 2026 replaces annealing in the *sort*. The same lab did replace annealing with a deterministic O(N²) estimate from pairwise matrices for *latency correction*:
     - Kreuz 2022 introduced the "direct shift".
     - Mariani et al. 2025 added an extrapolated direct shift, giving column averages of the spike-time-difference matrix. They report 9.7 s against 861.8 s for annealing.
     - The repo already knows Mariani 2025: Tony's draft reply to Kreuz cites its Fig. 11.
   - **Ranking literature.** Sorting by net wins is Borda/Copeland counting. Coppersmith, Fleischer & Rudra 2010 show weighted-wins ordering 5-approximates the feedback arc set problem. Shah & Wainwright 2018 show Borda counting is optimal up to constants for recovering a ranking from noisy pairwise comparisons.
   - **The template model.** Latent latency plus Gaussian jitter is Thurstone's Case V model (Thurstone 1927; not opened, ⚠). L152, "the optimal order is the score order in expectation", is the standard consistency result for that model class.

   **Medium.** Before "offer it as the fast route", cite Mariani 2025 and Kreuz 2022 as the lab's own deterministic alternative, and Coppersmith 2010 and Shah & Wainwright 2018 for the score sort. Also say that maximising the Synfire Indicator is the linear-ordering (Kemeny / feedback arc set) problem: Kreuz compares it to the travelling salesman problem. **Yes** for Kreuz and Mariani; metadata only for the two ranking papers.

6. **L139–140 · Both order formulas are classical identities presented as derived here.**
   - **Arctan form.** The one-template F is (2/π) arctan τ = (2/π) arcsin(τ/√(1+τ²)). That is Greiner's relation (Greiner 1909; Kruskal 1958): Kendall's τ for a bivariate normal with ρ = s/√(s²+σ²), via Sheppard's orthant probability. So the one-template F is the population Kendall τ between template and observed latencies, which is a more checkable statement.
   - **Arcsin form.** It is the same identity at ρ = τ²/(1+τ²), multiplied by the half-normal mean √(2/π).

   **Low–Medium.** Name the identities and cite Greiner/Kruskal and Sheppard. I checked these only through secondary sources (Lindskog et al.; the Bayesian Kendall-τ paper, arXiv 1703.01805). Sources disagree on whether Sheppard is 1898 or 1899. The originals were not opened: verify before citing. **Partial.**

7. **L123–126 · The membership formula 1 + (E − 1)/M is the survey-sampling design effect.** It is Kish's 1 + (m − 1)ρ with intraclass correlation ρ = 1/M: two events share an assembly with probability 1/M. My algebra reproduces it exactly for one pair. The page presents it as derived. **Low.** Name it as the design effect (Kish 1965, *Survey Sampling*; book not opened, ⚠). Also note that `bugarach.assembly.stat_dispersion` already uses pair-count dispersion (variance, not variance/mean), so this predicts an existing statistic rather than introducing one. **Partial** (algebra yes; book no).

8. **L34–39, L66–67 · The cumulant route has prior art that the page does not mention.** "The coordination-rates tool is predicted exactly" and the replication table read as three independent discoveries. `tools/measure_coordination_rates.py` L23–24 already cites Staude, Rotter & Grün (CuBIC) for the cumulant route and Kuhn, Aertsen & Rotter 2003 for the model; the goal page cites neither. Also uncited:
   - Ehm, Staude & Rotter 2007: inverting population counts for the participation ("amplitude") distribution of a compound Poisson process, i.e. k from cumulants.
   - CuBIC's own null variances of its cumulant estimators (k-statistics), which are prior art for "the noise of each estimate" (L79–81). Charlier-polynomial orthogonality under the Poisson distribution is textbook (Charlier 1905; Szegő): cite it, don't present it as found.

   **Medium.** One sentence: "the cumulant route is CuBIC's (Staude et al. 2010) and Ehm et al. 2007's; what is new here is the window-sharing factor g_n and the at-most-one-event term." I found no prior art for the at-most-one-event term in what I read; I did not read CuBIC §5.3.3 on jitter (⚠). **Yes** for CuBIC, metadata only for Ehm.

9. **L32–33, L40–43, L67–68 · Window sharing and reading jitter from the window have prior art.** g_2 is the continuous, Gaussian-jitter form of Grün et al. 1999's "fission probability" F(s, b): the share of jittered coincidences split by a bin border, with surviving count p_c(1 − F) (their eq. 6, uniform jitter on a grid). Their whole paper is built on the bin-versus-jitter loss, which is the page's "the window must exceed the jitter". Estimating a correlation timescale from how counts depend on the window is also standard (Bair, Zohary & Newsome 2001; window method not opened, ⚠). **Medium.** Cite Grün et al. 1999 for the window-loss factor and claim only the Gaussian closed form and the three-window fit. **Yes** for Grün 1999.

10. **L158–162, plan L245–247 · The proposed generator, and Aim 1c's multi-source question, have direct prior art.** The proposal is several sources, each with membership, jitter and a per-cell latency template, plus Poisson background. That is the PP-Seq model of Williams, Degleris, Wang & Linderman (NeurIPS 2020, arXiv 2010.04875): a Neyman–Scott process whose latent events of several types evoke spikes at per-neuron offsets and widths, fitted by Bayesian inference including how many types there are. The current generator is itself a Neyman–Scott / Thomas cluster process (Gaussian displacement) with a regularised parent train, and the page never names it. **Medium–High.** Weight for later reports: Aim 1c's "separation below which the tools report one source" is a question PP-Seq answers by model fit. Name the generator's class, cite Williams et al. 2020 as the published model of the proposed generator, and consider it as a comparison method. **Partial** (abstract and metadata; full text not read).

11. **Plan L237–239 · The random-matrix threshold is unattributed, and the repo has already hit its limits.** "Random-matrix theory has a sharp threshold" cites nothing; the spiked-covariance (BBP) transition is Baik, Ben Arous & Péché 2005 (not opened, ⚠). The repo's own records are relevant:
    - `bugarach.assembly` docstring: Marchenko–Pastur becomes unavailable when there are fewer events than ROIs.
    - `docs/assembly_report.md` L340–343: PCA against a Marchenko–Pastur bound flags every simulated recording, because coordinated events violate its null.
    - The classical assembly instrument is Lopes-dos-Santos et al. 2011/2013 and Peyrache et al. 2010, already cited in the repo.

    **Medium.** Cite BBP and Lopes-dos-Santos 2013, and link both internal findings. Without them the next session will rediscover the rank-deficiency problem. **Yes** for the internal records; BBP not opened.

12. **L93–95, L102, plan L244 · Cramér–Rao bounds and scan statistics are named as routes with no roots.** **Low.** When they are taken, cite scan statistics (Naus 1965; Glaz, Naus & Wallenstein 2001). Expect that Fisher information for Neyman–Scott processes is not tractable in closed form; the usual route there is composite or Palm likelihood (Tanaka, Ogata & Stoyan 2008; Guan 2006). None of these were opened (⚠). **No.**

13. **L44–46, L85–87 · The binomial chance tail and ADR-0008 floor are standard or internal; no citation needed.** No finding. **n/a.**

14. **L110–111, L151 · Tony's "brute force" characterisation is handled correctly.** Kreuz 2017 says brute force over N! orders is infeasible and uses annealing. The page correctly says "simulated annealing over N! orders". No Kreuz correspondence is quoted, consistent with the CLAUDE.md rule. No finding. **Yes.**

## Residuals and ⚠
- **Nobody was asked (⚠).** The repo's correspondence with Kreuz (`kreuz_note*.md`, the April todo) covers max_tau, C versus E, the detection layers and Mariani's Fig. 11. Nothing in it touches a fast sort or an analytical Synfire null. Before claiming the score sort or the null law as new, ask Tony whether anyone has asked Kreuz (or Mulansky). In 2026-08 Kreuz pointed to his own applied papers on exactly the construction then being claimed as ours (`doc_review_process.md` L1463), and the same pattern is plausible here.
- **Literatures searched:**
  - Kreuz lab output 2017–2026, traced forward from NJP 2017.
  - Unitary-event and coincidence analysis (Grün 1999).
  - Population-count cumulants (CuBIC; Ehm 2007).
  - Ranking from tournaments and pairwise comparisons (Coppersmith 2010; Shah & Wainwright 2018).
  - Rank correlation under normality (Greiner / Kendall / Sheppard).
  - Neural sequence and point-process models (PP-Seq).
- **Not searched (⚠):**
  - Synfire-chain and sequence detection beyond PP-Seq (Abeles & Gerstein; Schrader et al. 2008; SPADE; seqNMF; SPOTDis).
  - Random-tournament and linear-ordering theory for the 0.375 constant.
  - Survey sampling beyond Kish.
  - Point-process estimation theory, scan statistics, spiked random matrices, and Thurstone's original paper.
  - Ecology and seismology cluster-process literature.
- **Not opened (⚠):** Kish 1965, BBP 2005, Thurstone 1927, Greiner 1909, Sheppard 1898/99, Charlier 1905, the Ehm 2007 text, the PP-Seq full text, the Bair 2001 methods, and CuBIC §5.3.3 (jitter versus bin). Verify each before citing.
- **Out of scope here:** the Scholarpedia SPIKE-order article was not checked; NJP itself suffices.
