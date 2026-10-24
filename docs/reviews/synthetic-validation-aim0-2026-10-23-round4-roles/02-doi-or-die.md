GRANT 2 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), plus Agent, Artifact, PowerShell, Skill, ToolSearch, SendMessage, Claude Docs batch, update and create, Dropbox and Gmail write tools (deferred). I was spawned through the inline fallback as a general-purpose agent. I used only Read, Grep, Glob, Bash, WebSearch and WebFetch, plus ToolSearch to load the two web tools. I edited no tracked file. Scratch is under `_scratch/r4-role-02/` only. This mismatch is a finding about the run: the `roles:` line must say the review took a fallback path.

Blindness: I opened nothing under `docs/reviews/`. I checked that `docs/reviews/synthetic-validation-aim0_2026-10-23.md` exists, by path only. From `_scratch/` I read only `r4_common.txt` and `r4_extract.md`.

## Findings (location · issue · severity · suggested fix · verified against a source?)

1. **Extract lines 178–180 ("Spatial statistics fits a Thomas process … by minimum contrast … (Diggle, Besag & Gleaves 1976; Waagepetersen 2007)")** · Wrong root for minimum contrast. Diggle, Besag & Gleaves 1976 (Biometrics 32:659) is about distance methods. spatstat's `thomas.estK` page lists it but does not tie it to minimum contrast. spatstat's `mincontrast` page credits the method to Pfanzagl 1969 (Metrika 14:249) and Diggle & Gratton 1984 (JRSS B 46:193; DOI 10.1111/j.2517-6161.1984.tb01290.x, which resolves). So the software documentation the page says it read does not support the attribution. · **medium** · Cite Diggle & Gratton 1984 (and Pfanzagl 1969) for minimum contrast. Keep Waagepetersen 2007 (Biometrics 63:252, verified) for the Neyman–Scott estimating-function form. Drop DBG 1976 or say why it is cited. Keep the ⚠ papers-not-read flag. · yes (both spatstat help pages read; Crossref metadata).

2. **Lines 329–331 ("Kreuz's lab has replaced annealing with direct pairwise estimates for latency correction … (Kreuz et al. 2022 …; Mariani et al. 2025 …)")** · Kreuz 2022 is the annealing paper. Its abstract says the matched spikes are aligned by simulated annealing, and the first-row or first-diagonal direct shift appears only as the simple case. The replacement of annealing by a fast extrapolation direct shift is Mariani 2025. The 9.7 s against 861.8 s figure on 183 trains (MATLAB, M1, MEX-compiled annealing) is verified in Mariani's arXiv v2 (2410.15018), footnote 3. · low · Reword to: Kreuz et al. 2022 introduced latency correction by annealing, with direct shift as a simple alternative; Mariani et al. 2025 replaced annealing with an extrapolation direct shift (9.7 s against 861.8 s). Note that the timing was read from the arXiv version. · yes (arXiv 2205.09855 and 2410.15018 full text).

3. **Line 332 ("*Biol Cybern* 120(3):21, 2026")** · The DOI 10.1007/s00422-026-01045-5 resolves: Kreuz, "Quantifying spike train synchrony and directionality: Measures and Applications". Crossref gives issue **3-4**, article 21, online 2026-07-13. Kreuz's own publications page lists 120(3):21. The "still sorts by annealing" claim is verified in arXiv 2510.07140v2: the review restates the annealing sort of the 2017 paper and proposes no other sort. · low · Write 120(3–4):21, or cite by DOI. · yes.

4. **Order section (lines 254–333) and the Synfire Indicator comparison: the forward trace of Kreuz's own applied papers is incomplete** · Kreuz's lab has applied SPIKE-order and spike train order to calcium imaging: Cecchini et al. 2021, PLoS Comput Biol 17:e1008963 (Kreuz last author; DOI verified), on wide-field GCaMP propagation before and after stroke. The 2026 review lists it with Tomlinson et al. 2019 (Epilepsia 60:898) as the framework's later applications. The page cites Kreuz 2022 only for latency correction and does not mention Cecchini 2021. It is the closest prior art for "an order indicator on calcium-imaging events", and the repo already knows it (`docs/detector_history.md:169`, `docs/methods/coordination_pipeline_methods.md`). · medium · Cite Cecchini et al. 2021 as the lab's own application of the Synfire Indicator to calcium imaging (wide-field, not cellular), and say whether it reports event counts or the few-events bias. I did not read the paper itself; only the review's description and the metadata. · partly (metadata and the review's description; paper not opened).

5. **Line 254 (the page's sentence on Tony expecting Kreuz's method to be brute force and slow) and the whole Kreuz comparison: correspondence not used, nobody asked** · The repo has an open, friendly mail thread with Kreuz. He replied 2026-04-23 and again around 2026-08-31 and 2026-09-02 (`docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`; `docs/kreuz_note_3_thanks.md`, which records that he pointed to Fig. 11 of Mariani et al. 2025). None of it asked about a fast or closed-form sort, the Synfire Indicator's no-order bias with few events, or comparing across recordings. Several of the page's open points could be settled in one question to him: the speed expectation, whether the lab has a closed-form null, and the normalization difference. · medium (residual ⚠) · Add a ⚠ saying nobody has asked Kreuz. If the question is sent, cite the answer as a paraphrased, dated personal communication, per the CLAUDE.md rule on correspondence. Mariani Fig. 11 is relevant to plan item 3 (`max_tau`); consider citing it there. · yes (repo correspondence files read; no correspondence quoted here).

6. **Lines 172–176 (the joint-fit prior art: Grün 1999, Pazienti 2008, Louis & Grün 2009, Louis, Borgelt & Grün 2010)** ·
   - **Grün et al. 1999** (JNM 94:67-79, DOI verified; full text from the Freiburg brainworks PDF): "fission probability" (Eq. 5) for two trains with uniform jitter is verified. So is reading the coincidence width from the analysis width at best detection (Fig. 10, §5.2).
   - **Back-trace stopped one step short:** the paper credits the loss of sensitivity under jitter to Grün 1996, a PhD thesis I did not open.
   - **Louis & Grün 2009** (BMC Neurosci 10(Suppl 1):P253, RIKEN BSI, Grün group): verified in full. They follow the second maximum of the complexity distribution across bin widths and infer group size and jitter together.
   - **Louis, Borgelt & Grün 2010** (Neural Netw 23:705-712): metadata and abstract verified. The abstract does not mention bin widths, so the ⚠ stays.
   - **Pazienti et al. 2008** (Brain Res 1225:39-46): the abstract supports the claim (detection decays with dither width; precision found from a single tolerated-spread setting).
   - **Missing root:** both Louis papers build on Grün, Abeles & Diesmann 2008 (LNCS 5286:96-114, DOI 10.1007/978-3-540-88853-6_8), which is where the complexity distribution comes from. The page omits it. · low · Add Grün, Abeles & Diesmann 2008 as the complexity-distribution root. Note "Grün 1996 thesis not opened". Upgrade Louis & Grün 2009 to read in full. · yes, except Grün 1996 and the full text of Louis 2010 and Pazienti 2008.

7. **Line 323 (the quote from Kreuz 2017 §3.1) and lines 292–293, 307, 314, 319 (sec. 2.5, sec. 3.1, eq. 14, binomial null, surrogates)** · All verified against the lab-library PDF (`01-lit/kreuz 2017 leaders and followers spike-order njp.pdf`):
   - the quoted sentence is exact (§3.1, pp. 11–12);
   - eq. 14 is F = 2D</((N−1)M), with M = all spikes;
   - §2.5 says the null would be binomial if pairs were independent;
   - the surrogates swap order values while keeping coincidence structure;
   - the finite-size effect is in §3.1;
   - the sort is simulated annealing with neighbour swaps.

   Also confirmed: PySpike's annealer imports `rand` from libc.stdlib (`pyspike/cython/cython_simulated_annealing.pyx`); 0.9.0 is the current PyPI release; PySpike PR #89 is still open and unmerged. · none · none · yes.

8. **Line 340 (PP-Seq, NeurIPS 2020) and line 433 (Wang, Degleris, Williams & Linderman, JASA 119:2382, 2024)** · PP-Seq is verified from arXiv 2010.04875: the authors and Stanford affiliation are right, it is a Neyman–Scott process with per-neuron offsets, and the number of sequence types R is chosen by cross-validation (§4.1). The JASA paper's DOI 10.1080/01621459.2023.2257896 resolves: 119:2382-2395, online 2023. · none · none · yes.

9. **Lines 326–329 (Coppersmith, Fleischer & Rudra 2010; Shah & Wainwright 2018)** ·
   - **Coppersmith:** the factor-5 approximation under w_uv + w_vu = 1 is verified (ECCC and IBM abstracts). The conference original is SODA 2006, pp. 776-782.
   - **Coppersmith metadata:** TALG volume 6, issue 3, 2010 is verified. Article number 55 is **not** confirmed: Crossref carries no article number and the ACM DL returned 403.
   - **Shah & Wainwright:** JMLR 18(199):1-38 (2018) is verified, and the abstract supports "Borda counting optimal up to constant factors". Their guarantee is for top-k set recovery, which is narrower than full-order recovery. · low · Optionally cite the SODA 2006 original. Confirm article 55. Optionally scope Shah & Wainwright to top-k recovery. · mostly.

10. **Lines 165–171 (Neyman & Scott 1952, 1958; Thomas 1949; CuBIC; Kuhn, Aertsen & Rotter 2003)** ·
    - **Metadata:** all resolve.
      - Neyman & Scott: ApJ 116:144 (DOI 10.1086/145599) and JRSS B 20:1-29.
      - Thomas: Biometrika 36:18-25.
      - CuBIC: JCNS 29:327-350 (PMC2940040).
      - Kuhn, Aertsen & Rotter: Neural Comput 15:67-101; the page gives no journal for this one.
    - **CuBIC content** (full text): it names the SIP and MIP models of Kuhn et al. 2003 as special cases of its compound-Poisson model. It uses ordinary cumulants (the word "factorial" never appears), so "factorial rather than ordinary" is a fair contrast. It derives the variance of its test statistic analytically, which supports "CuBIC gives its own estimators' noise".
    - **Thomas and Neyman–Scott content:** not opened by me either, so the page's ⚠ flags stand. · low · Add the journal for Kuhn 2003. · yes (metadata and CuBIC text).

11. **Lines 423–431 (Baik & Silverstein 2006; Baik, Ben Arous & Péché 2005; Peyrache 2009 and 2010; Chapin & Nicolelis 1999; Lopes-dos-Santos 2011 and 2013)** ·
    - **Metadata:** all resolve as written.
      - Baik & Silverstein: JMVA 97:1382-1408.
      - Baik, Ben Arous & Péché: Ann Probab 33:1643-1697.
      - Peyrache 2009: Nat Neurosci 12:919-926.
      - Peyrache 2010: JCNS 29:309-325.
      - Chapin & Nicolelis: JNM 94:121-140.
      - Lopes-dos-Santos 2011: PLoS ONE 6:e20996.
      - Lopes-dos-Santos 2013: JNM 220:149-166.
    - **Origin claim:** the Lopes-dos-Santos 2011 full text credits Peyrache et al. with introducing the Marchenko–Pastur null, which supports "that method comes from Peyrache".
    - **Not opened:** the Baik papers stay ⚠. · none · none · yes for metadata and the Peyrache origin.

12. **Line 437 (Staude, Rotter & Grün 2008, Neural Comput 20:1973-1999)** · Verified from the abstract: they decompose the cross-correlation so as to correct for rate effects, and show coordination and rate covariation are separable over a wide range of parameters, but not identifiable at extreme ones. · low · Optionally add "except at extreme parameters". · yes.

13. **Line 282 (Greiner via Kruskal 1958) and line 232 (Kish 1965)** · Kruskal 1958 resolves (JASA 53:814-861). Neither book nor paper was opened by me, so the page's ⚠ flags stand. Kish's design effect for unequal weights is commonly also cited to Kish 1992 (J Off Stat); I did not verify that. · low · none beyond the existing ⚠ · no.

14. **Order section: unsearched literatures for the order indicator and its no-order bias** · The page searched CS ranking (feedback arc set, Borda) and the Kreuz lab. It did not search the neuroscience sequence and replay literature, where per-event rank-order correlation against a template, shuffle nulls and few-cell or few-event bias are standard. Candidates, metadata verified, papers not read:
    - Lee & Wilson 2002, Neuron 36:1183;
    - Luczak et al. 2007, PNAS 104:347;
    - seqNMF and related methods (not checked).

    Neither the page nor I can claim there is no prior art for the fast sort or the bias here. · medium (residual ⚠) · Add "⚠ Not searched: hippocampal replay and cortical sequence rank-order methods". · no.

15. **Internal citations used as sources (lines 252–253, 316–321; plan items 3 and 5)** · The 2026-08-19 synfire todo matches: ρ −0.75 and −0.40; 23 of 80, 44 of 82 and 3 of 40; medians 0.036, 0.099 and 0.101. `FOUNDATIONS.md` has the `max_tau` item (line 81). `docs/assembly_report.md` exists. · none · none · yes.

16. **`docs/GLOSSARY.md`, the new vocabulary section (lines 659 onward) and the revised jitter entry** · They contain no literature references. The Kreuz mentions there (SPIKE-order; the Synfire Indicator normalized by all spikes) are consistent with Kreuz 2017 eq. 14. · none · none · yes.

## What I checked and where I stopped
- **Checked:** every named attribution in extract lines 1–390 and 392 onward, and in the new glossary entries. Metadata came from Crossref, dblp (failed), Europe PMC, JMLR, ECCC, IBM and Kreuz's publications page. Full text came from Kreuz 2017 (lab library); Grün 1999 (Freiburg PDF); Louis & Grün 2009, CuBIC and Lopes-dos-Santos 2011 (open access); and from arXiv for Kreuz 2022, Mariani 2025, the Kreuz 2026 review and PP-Seq. Code came from the PySpike GitHub source and PR #89's status.
- **Stopped short:**
  - Grün 1996 thesis (not obtained);
  - Thomas 1949, Neyman & Scott, Kish, Kruskal and the Baik papers (not opened);
  - Louis 2010 and Pazienti 2008 (abstract only);
  - Coppersmith's article number (ACM DL returned 403);
  - Cecchini 2021 (not read in full).
- **Lab library:** `01-lit` holds only Kreuz 2017 and PySpike 2016 of the cited works. No fabricated reference found; every DOI resolves.
