GRANT 2 MISMATCH — missing none (WebSearch and WebFetch arrived deferred and I loaded them); holds forbidden Edit, Write, NotebookEdit (deferred), plus PowerShell, Agent, Artifact, Skill, and MCP Docs, Dropbox, Gmail, PubMed tools. This is a run-level finding: the role was spawned through the inline fallback, so the run record's `roles:` line must say fallback path. I edited no tracked file. My scratch is only `_scratch/r3-role-02/lit/` (downloaded OA papers and their text). I did not open `docs/reviews/` or any other `_scratch/` file.

Locations below are page lines of `docs/goals/synthetic-validation.md`. For lines 16–329 the extract line is the page line minus 15.

## Findings (location · issue · severity · suggested fix · verified against source?)

1. **L112–114 ("What is added here: g_n for Gaussian jitter… and the joint fit") and Settled row L306.**
   - Issue: close prior art for the joint fit is missing, from the same lab the page already cites. Louis & Grün 2009 (CNS*2009 poster, *BMC Neurosci* 10(Suppl 1):P253, doi:10.1186/1471-2202-10-S1-P253, full abstract read) derive the population complexity distribution analytically for arbitrary rate, jitter and bin width. They then infer **group size and jitter together by following the distribution across bin widths**. That is the joint fit's idea, using the complexity distribution instead of pair and triple cumulants, uniform ±j jitter, and non-overlapping groups. It was followed by Louis, Borgelt & Grün 2010, *Neural Netw* 23(6):705–712, doi:10.1016/j.neunet.2010.05.004 (abstract only). That abstract says the method reliably extracts the size and temporal precision of synchronous groups even under strong rate covariation. The lab is Grün's (last author, RIKEN BSI), the same group as CuBIC and Pazienti.
   - Also missing: Grün et al. 1999 itself (§6, read) concludes that both of its methods "allow to detect the temporal scatter" of near-coincidences from how detection changes with analysis width. So a jitter estimate from a window sweep goes back to 1999 for pairs.
   - Severity: **high**. This is a novelty and attribution claim that will feed later reports.
   - Fix: cite Louis & Grün 2009 and Louis, Borgelt & Grün 2010 as the population-count precedent for estimating size and jitter across windows. Narrow "what is added" to: Gaussian jitter, cumulant (pair and triple) form, the at-most-one-event term, and fitting the event rate jointly. Mark Louis 2010 "⚠ abstract only".
   - Verified: yes (2009 full abstract; 2010 abstract only).

2. **L98 (unsearched list) and L112–114.**
   - Issue: the unsearched spatial point-process field holds a direct analogue of the joint fit. The Thomas process (the page's own named model) is routinely fitted by **minimum contrast on the K-function**. Its pair-count-versus-scale curve has the closed form K(r)=πr²+(1/κ)(1−exp(−r²/4σ²)), which gives parent intensity κ and scatter σ, with offspring per parent μ from the intensity. Those correspond to λ, σ and k. Sources: spatstat `thomas.estK` docs, citing Diggle, Besag & Gleaves 1976, Møller & Waagepetersen 2003 pp. 61–62, Waagepetersen 2007. I read the docs, not the books.
   - Severity: **high** (prior art inside a field the page itself marked ⚠).
   - Fix: cite minimum-contrast Thomas-process fitting as the pair-only analogue. The residual novelty is the triple term and the held-apart (non-Poisson) parents. Keep the ⚠ on quadrat-variance ecology and physics counting statistics, which I also did not search.
   - Verified: partly (software docs only).

3. **L90–91 ("Gaussian scatter…; Neyman & Scott 1958, Thomas 1949").**
   - Issue: misattribution and a non-root citation.
     - Thomas 1949 (*Biometrika* 36:18–25, doi:10.1093/biomet/36.1-2.18; the author is Marjorie Thomas) is a quadrat-count model: Poisson parents, each with a Poisson number of offspring. It has no Gaussian displacement law. "Thomas process" for the Gaussian-scatter case is a later naming convention.
     - The Neyman–Scott cluster model's root is Neyman & Scott 1952, *ApJ* 116:144. A secondary review says it has a Gaussian within-cluster density; I read the abstract only. The 1958 *JRSS B* 20:1 paper exists and is the one PP-Seq cites, but it is the later, statistical restatement.
   - Severity: medium.
   - Fix: write "Neyman & Scott 1952 (restated 1958); the Gaussian-scatter case is now called the Thomas process (after Thomas 1949)". Add ⚠: 1952 abstract only, 1949 abstract via secondary source.
   - Verified: partly.

4. **L96–97 (Pazienti et al. 2008, "used coincidence detection against window width to estimate synchronization precision").**
   - Issue: the paraphrase is wrong. The abstract (PubMed 18547547, doi:10.1016/j.brainres.2008.04.073) says detection probability decays with the applied **dither interval**, and precision is estimated "for a single setting of tolerated temporal spread", meaning a fixed window. The same wording sits in `theory.py` L18–19 ("against window width").
   - Severity: medium.
   - Fix: "used how coincidence detection decays with dither width, at one fixed window, to estimate synchronization precision". Keep ⚠ abstract only. Full text was not obtainable: the FU-Berlin PDF link returns 404, and Pazienti's dissertation does not contain this study.
   - Verified: yes, against the abstract.

5. **L94 (CuBIC citation).**
   - Bibliography is correct: 29(1-2):327–350, doi:10.1007/s10827-009-0195-x. Its MIP link to Kuhn et al. 2003 is confirmed in the CuBIC text.
   - Worth adding: CuBIC states that its sensitivity to jittered coincidences "remains to be assessed systematically", and cites Pazienti 2008 for jitter small against bin size. That supports the page's gap claim once item 1 is fixed.
   - Severity: low.
   - Verified: yes (PMC2940040 full text).

6. **L95–96 (Grün et al. 1999).**
   - Verified: uniform jitter over 2s+1 positions, two trains, Eq. 5 "fission probability", read in full. Lab: Aertsen is last author (Freiburg).
   - Note: the publisher PDF header prints vol. 93; PubMed gives 94(1):67–79, doi:10.1016/S0165-0270(99)00126-0. Keep 94 and add the DOI. I stopped tracing at this paper. Its own predecessors (Grün's 1996 thesis, Riehle et al. 1997) were not opened.
   - Severity: low.
   - Verified: yes.

7. **L349–351 (assembly method "originates in Lopes-dos-Santos et al. 2011 (*PLoS ONE* 6:e20996) and Peyrache et al., restated in Lopes-dos-Santos et al. 2013").**
   - Issue: the order is wrong and one reference is incomplete. Lopes-dos-Santos 2011 (full text read, PMC3115970) credits Peyrache et al. with introducing the Marčenko–Pastur null. That is Peyrache et al. 2010, *J Comput Neurosci* 29:309–325, and Peyrache et al. 2009, *Nat Neurosci* 12:919. Lopes-dos-Santos calls its own method an extension of Chapin & Nicolelis 1999 (*J Neurosci Methods* 94:121) and Nicolelis et al. 1995. "Peyrache et al." has no year or venue, although `docs/assembly_report.md` L457 already lists Peyrache 2010.
   - Severity: medium (crediting the wrong origin).
   - Fix: "originates in Peyrache et al. 2009/2010 (Battaglia lab; PCA of ensembles from Chapin & Nicolelis 1999), extended by Lopes-dos-Santos et al. 2011 (Tort lab), restated 2013 (*J Neurosci Methods* 220:149)".
   - Verified: yes.

8. **L278–281 (Coppersmith, Fleischer & Rudra 2010).**
   - Bibliography is correct: *ACM Trans Algorithms* 6(3):55, SODA 2006.
   - Issue: the factor-5 guarantee holds under probability constraints (w_uv+w_vu=1). It bounds the **feedback-arc-set (backward-weight) cost**, not net agreement F. F also weights pairs by co-participation count, so "approximates the best order within a factor of 5" does not carry over to F as written.
   - Severity: low–medium.
   - Fix: say the 5-approximation is for the disagreement (feedback arc set) objective with per-pair normalized weights. Optionally name the problem: linear ordering / feedback arc set in tournaments, NP-hard (Ailon, Charikar & Newman). Kreuz 2017 compares the search to the travelling-salesman problem instead.
   - Verified: yes (abstract and DBLP).

9. **L279–280 (Shah & Wainwright 2018).**
   - Verified: *JMLR* 18(199):1–38. The abstract calls it "Borda counting" and "optimal … up to constant factors". Correct.
   - Verified: yes.

10. **L281–283 (Kreuz et al. 2022; Mariani et al. 2025; "9.7 s against 861.8 s on one 183-train dataset"; 2026 review).**
    - Verified:
      - Kreuz 2022: *JNM* 381:109703, PMID 36075286.
      - Mariani 2025: *JNM* 416:110378, PMID 39894257. The arXiv 2410.15018v2 footnote 3 gives 861.8 s (MEX-compiled annealing) against 9.7 s (direct shift) on 183 trains, about 13 spikes each. The speedup is for latency correction, not sorting. Correct.
      - The review is Kreuz T (single author), *Biol Cybern* 120(3):21, 2026, arXiv:2510.07140. It says sorting "in [12] is performed using simulated annealing". "Still sorts by annealing" is a fair reading.
    - Fix: cite the review as "Kreuz 2026, *Biol Cybern* 120(3):21" (it lacks the article number and the author now).
    - Severity: low.
    - Verified: yes.

11. **L247–249, L255–266, L272–273 (Kreuz, Satuvuori, Pofahl & Mulansky 2017).**
    - Verified against the lab-library PDF:
      - eq. 14 is F = 2D</((N−1)M), normalized by all spikes;
      - §2.5 says the null would be strictly binomial if coincident pairs were independent, and its surrogates swap order values while keeping spike times;
      - §3.1 describes the finite-size effect;
      - the quoted sentence matches.
      - F_Kreuz = F·(k−1)/(N−1) follows from eq. 14 with known events and no background.
      - PySpike's annealer uses C `rand()` with no `srand` (source read).
    - Issue, minor: L272 says "warn that F is…", but on this page "F" is the page's own indicator. The quote is about Kreuz's Synfire Indicator.
    - Fix: "warn that the Synfire Indicator is…".
    - Severity: low.
    - Verified: yes.

12. **L237–239 (Greiner's relation via Kruskal 1958).**
    - Kruskal 1958 (*JASA* 53:814–861) is cited elsewhere as the source of Greiner's relation τ=(2/π)·arcsin ρ. The page's (2/π)·arctan r is the same thing with ρ=r/√(1+r²).
    - Not opened: Kruskal 1958 and Greiner 1909, so the existing ⚠ stands.
    - Fix: add the arcsin form so a reader can match it to the literature.
    - Severity: low.
    - Verified: partly (secondary sources).

13. **L288–290 (PP-Seq).**
    - Verified (arXiv 2010.04875): Williams, Degleris, Wang & Linderman, NeurIPS 2020. It is a Neyman–Scott process with per-neuron offsets, and R is chosen by cross-validation. Correct.
    - Verified: yes.

14. **Plan L367–368 (Wang, Degleris, Williams & Linderman "2023, *JASA*", "likelihood inference").**
    - Issue: the published issue is *JASA* 119(547):2382–2395 (2024; online 2023), doi:10.1080/01621459.2023.2257896. Its inference is Bayesian (collapsed Gibbs / MCMC), not frequentist likelihood.
    - Not searched: the composite and Palm likelihood literature for Neyman–Scott processes (e.g. Guan 2006; Tanaka, Ogata & Stoyan 2008; Waagepetersen 2007). That is a residual ⚠ for a step that names composite likelihood.
    - Fix: correct the year and volume, and say "Bayesian inference".
    - Severity: low.
    - Verified: yes (metadata).

15. **Plan L362–364 (Baik & Silverstein 2006; Baik, Ben Arous & Péché 2005).**
    - Both exist: *J Multivariate Anal* 97:1382–1408 and *Ann Probab* 33:1643–1697. BBP is for complex Wishart matrices; Baik–Silverstein gives general almost-sure limits. The ⚠ "neither opened" is honest.
    - Fix: add the venues.
    - Severity: low.
    - Verified: metadata via citing papers.

16. **Plan L372 (Staude, Rotter & Grün 2008, *Neural Comput* 20:1973).**
    - Verified: 20(8):1973–1999. The abstract matches "separate coordination from rate covariation".
    - Verified: yes.

17. **L211 (Kish 1965 design effect).**
    - Analogy only; the book was not opened, and the existing ⚠ is adequate. I did not search for an earlier origin of 1+(m−1)ρ. The intraclass-correlation variance inflation predates Kish (Hansen, Hurwitz & Madow 1953 is likely), so this is a residual ⚠.
    - Severity: low.
    - Verified: no.

18. **Waiting on Tony L422–427 and Plan item 2 (correspondence).**
    - I read all repo correspondence, in paraphrase:
      - April 2026: Kreuz's letter on SPIKE-synch detection.
      - 2026-08-28: the τmax note was sent.
      - 2026-08-31: Kreuz's reply endorsing the fix, Mulansky cc'd, pointing to the review and the two latency-correction papers.
      - 2026-09-01/02: the apology and Kreuz's clearance, which covers only the PR material.
    - None of it touches a fast sort, an analytical null or the finite-size bias. The page's claim "does not cover it" is accurate.
    - Issue: the page cites only the April letter. It should also name the August/September thread (`docs/kreuz_note*.md`, `docs/todo/2026-08-11-file-pyspike-max-tau-issue.md`) as checked. The Sep 2 thread is where Kreuz himself pointed to Mariani et al. 2025 (Fig. 11), and the page now cites that paper.
    - "Has anyone asked Kreuz or Mulansky about a fast sort or analytical null" remains a **residual ⚠: nobody asked**, correctly routed to Tony. Nobody has asked the Grün lab about the joint fit either (new, given item 1).
    - Severity: low (record completeness).
    - Verified: yes (repo files).

19. **Internal references.**
    - ADR-0006, 0008 and 0019 exist, as do every linked file and the run record (by path).
    - The August todo's numbers check out: ρ −0.75/−0.40, and control median 0.101 against 0.036/0.099 over 40 recordings.
    - MAHICE is a glossary-defined house coinage.
    - The GLOSSARY entries (the revised jitter entry and the new vocabulary section) carry no external citations beyond the Synfire Indicator normalization, which I verified.
    - No findings.

## Literatures searched / where I stopped
- **Searched:**
  - the spike-synchrony and unitary-event line (Grün/Aertsen/Rotter/Staude/Pazienti/Louis), traced forward from CuBIC to Louis 2009/2010;
  - the Kreuz line: 2017 → 2022 → 2025 → 2026 review, his publication page, and the Cecchini 2021 application, which has nothing on a null or a fast sort;
  - tournament ranking in CS;
  - Bayesian point-process ML (Linderman);
  - PCA assembly detection.
- **Touched only:** spatial point-process statistics (minimum contrast; item 2).
- **Not searched (residual ⚠):** quadrat-variance ecology (Greig-Smith-style block-size variance is the obvious analogue), physics counting statistics (Fano factor or variance against counting window for cluster processes), composite and Palm likelihood for Neyman–Scott processes, and the origin of the design effect.
- **Roots stopped short:** Grün 1999's own predecessors, Greiner 1909, and the Neyman & Scott 1952 full text were not opened. Pazienti 2008 and Louis 2010 are abstract only, because of paywalls or dead OA links.
