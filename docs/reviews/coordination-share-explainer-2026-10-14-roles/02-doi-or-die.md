GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I hold no Edit, Write or NotebookEdit. The only thing I wrote was one downloaded copy of Kuhn 2003, as a PDF and its extracted text, in scratchpad\mb-r1\role2-dl\.)

# Role 2 — Citation & reference validator: findings on coordination_share_explainer/README.md

Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md

**Bottom line:** both references in the tool's docstring are real and correctly described, though one ("the same cumulant route") overstates the match. The README names no literature at all while explaining the method step by step, so attribution is owed. One of its claims also drops a qualifier its source states.

## Findings
Each finding gives location · issue · severity · suggested fix · verified.

**F1 · Whole README, mainly "How the measure works" §1–§4 (lines 82–150) · major · verified yes (the sources exist and the lineage is confirmed below)**
- **Issue:** The page explains the population-count cumulant method, the fixed and binomial participation models, and the rigid-shift surrogate in detail, and cites none of them. A reader of a public portfolio repo would reasonably read the method as the project's own.
- **Precedent and gap:** The tool's docstring cites two papers. The sister explainer (`learned/correlogram_explainer/README.md`, line 96) has a "Reference for the method" line for Perkel, Gerstein & Moore 1967. This page drops the convention.
- **Fix:** Add a short "Where the method comes from" paragraph at the end of the text, written in plain words for this audience:
  - (a) Inferring shared events from the cumulants of the population count: Staude, Rotter & Grün 2010 (CuBIC), and before it Ehm, Staude & Rotter 2007.
  - (b) The binomial model is the multiple-interaction process (MIP) of Kuhn, Aertsen & Rotter 2003. The fixed model is a compound Poisson process whose moment size is always *k* (Staude et al.'s framework). It reduces to Kuhn's single-interaction process (SIP) when *k* = *N*.
  - (c) Whole-train shifting as a surrogate: Pipa et al. 2008, and Louis, Borgelt & Grün 2010. These are already in `docs/GLOSSARY.md` under "rigid shift" (lines 549–555); cite them or link that entry.
  - (d) Then say what is this project's own: factorial rather than ordinary cumulants, solving *f*₃/*f*₂ for *k* and λ, the share-of-rate output, distinct per-cell offsets at least two windows apart, and calibration on the bench.

**F2 · Tool docstring line 23 ("Staude, Rotter & Grün (2010) … use the same cumulant route"), to be carried into the README · minor · verified yes (full text read)**
- **Issue:** "The same" overstates the match. CuBIC works on **ordinary** cumulants κ_m of the population count, estimated with k-statistics. It tests for the **minimum correlation order** that can explain κ₃ under a compound Poisson model. The paper never mentions factorial cumulants, and it does not solve for moment size and rate.
- **Fix:** When the README cites it, write "builds on the population-count cumulant approach of" rather than "uses the same route". Leave the docstring to whoever owns the tool; this is a note, not a change for this PR.

**F3 · Line 100 ("For cells with independent onsets, both are zero on average, whatever each cell's rate") · minor · verified yes (against the source)**
- **Issue:** The source says something narrower. The tool's own `factorial_cumulants` docstring (line 119) reads "Zero in expectation for independent **Poisson** counts". The module docstring says "independently **at constant rates**". For independent cells that are not Poisson within a window (refractoriness, regular cells, at most one onset per window), *f*₂ per cell is Var − mean, which is not zero. The README dropped that qualifier.
- **Why it is minor:** the shifted copies keep each cell's own count statistics, so the excess is still right. The point is that the README's sentence is stronger than its source, and §2's "chance is measured, not assumed" is what actually rescues it.
- **Fix:** "For cells with independent onsets at steady rates, both are close to zero, and the shifted copies (step 2) remove what is left."
- **Boundary:** the mathematical consequence belongs to the claims/maths role. I file it here only as "the README misstates its source".

**F4 · Line 67 "(Tony, 2026-10-14)"; line 73 "still waiting on Tony" · no issue · verified yes**
- Internal ruling attributions, dated, with no quoted words.
- No third-party correspondence appears anywhere on the page, so the "Other people's words" rule is satisfied.

**F5 · Line 189 ("The todo that commissioned this page had this backwards; the tool's own docstring has it right") · no issue · verified yes**
- The todo's item 5 does say slower shared changes "survive into the surrogate and are counted as coordination".
- The docstring (lines 27–31) and `shifted` (lines 152–154) say such changes survive into the surrogate and are **subtracted**.
- The README's statement is accurate.

**F6 · Lines 144–146 (the reason for `ADOPTED_MODEL`) and lines 181–182 (`CAL_NO_PROBE`) · no issue · verified yes**
- Lines 144–146 paraphrase the comment at tool lines 274–277 faithfully.
- Lines 181–182 say "may be large on the slow stream". The note says "not obviously small" for slow (share 35.9% at the probe). That is a fair paraphrase.

**F7 · No location; residual for the run · ⚠ residual · verified no**
- **Issue:** Nobody has been asked whether anyone has corresponded with Staude, Rotter or Grün (or the Elephant maintainers) about using CuBIC-style cumulants on calcium-imaging onsets. The repo's reading log (`docs/learned/recombination_nulls_reading_log.md`, around line 396) records an outstanding, *different* question to the Grün group, and nothing on this one.
- **Fix:** Ask Tony. Until then, "nobody was asked" stands as a residual ⚠.

**F8 · Literature coverage behind any novelty claim · ⚠ residual · verified partly**
- **Issue:** This construction is general enough to have been invented elsewhere, and it was. In high-energy physics, factorial cumulants ("Mueller coefficients") of particle multiplicity vanish for uncorrelated (Poisson) emission. The "clan" model there is a compound Poisson of independently produced clusters, which is exactly this page's shared moments of size *k*. I confirmed this only from secondary review abstracts (arXiv hep-ph/0405251, hep-ph/0101016), not from Mueller 1971 or Giovannini & Van Hove themselves.
- **Fix:** If the README says anything like "the measure is ours", phrase it as "the calcium-imaging application and calibration are ours" and not the statistic. The current draft makes no explicit novelty claim, so this is a guardrail, not a defect.

## Bibliographic verification
- **Staude B, Rotter S, Grün S (2010).** "CuBIC: cumulant based inference of higher-order correlations in massively parallel spike trains." *J Comput Neurosci* 29(1–2):327–350, doi:10.1007/s10827-009-0195-x. Online 2009, print 2010.
  - Verified by reading the full text (Europe PMC, PMC2940040).
  - **Lab:** the last author is Grün, at the Unit of Statistical Neuroscience, RIKEN Brain Science Institute (Wako, Japan), and BCCN Berlin. Staude (first and corresponding author) is at both RIKEN BSI and BCCN Freiburg / Albert-Ludwig University. Rotter is at Freiburg.
  - So CuBIC is Grün's RIKEN group working with Freiburg. It is **not** "the Rotter lab"; a shared author is not a shared lab.
- **Kuhn A, Aertsen A, Rotter S (2003).** "Higher-order statistics of input ensembles and the response of simple model neurons." *Neural Comput* 15(1):67–101, doi:10.1162/089976603321043702.
  - Verified from the PDF text. All three authors are at Neurobiology & Biophysics, Freiburg. The last author is Rotter, so this is Freiburg.
  - **SIP:** one Poisson realisation is copied into all *N* trains, plus independent background.
  - **MIP:** each train is an independent thinning of one Poisson "mother" process, so the size of a cluster is binomial. The paper states this directly: "the number n follows a binomial distribution".
  - So the tool's "binomial" model is MIP, as the docstring says, and the attribution is correct.
  - SIP is credited to Deppisch et al. 1993 and Bohte et al. 2000 (the latter as the motivation for SIP); I did not open either.

## Where the backward trace stopped, and why
- **(a) Cumulants of the population count.** Followed CuBIC → Ehm, Staude & Rotter 2007, *Electron J Stat* 1:473–495, doi:10.1214/07-EJS095 ("empirical de-Poissonization"; existence verified, arXiv 0711.1965, text not read).
  - CuBIC credits the "insertion of additional coincident events" to Holgate 1964 (bivariate Poisson), with Snyder & Miller 1991 and Daley & Vere-Jones 2005 for compound Poisson theory.
  - **Stopped there:** these are statistics papers and textbooks, not opened, and none is free online in this session. So this lineage is verified to one step short of its root.
  - The identity actually used, κ₍r₎ = λ·w·E[k(k−1)…(k−r+1)] for a compound Poisson, is classical. I checked its algebra and the README's *f*₂ and *f*₃ definitions by hand, and both are correct.
- **(b) The participation models.** Kuhn 2003 is the origin of the MIP/SIP names and is correctly cited. CuBIC says plainly that the SIP and MIP models are "special cases" of its compound Poisson model. The fixed model is that compound Poisson with a single moment size.
- **(c) The rigid-shift surrogate.**
  - Pipa, Wheeler, Singer & Nikolić 2008, *J Comput Neurosci* 25:64–88, doi:10.1007/s10827-007-0065-3: existence verified from the record. A Frontiers paper (Louis et al. 2010) credits it with the "spike train shifting" surrogate; I did not read Pipa 2008's own text.
  - Pipa, Riehle & Grün 2007 and Louis, Borgelt & Grün 2010: as recorded in the repo's GLOSSARY and reading log, not re-fetched.
  - The tool's variant (circular, offsets a permutation of multiples of two windows) has no prior art searched. ⚠

## Forward trace
- **Staude, Grün & Rotter 2010,** *Front Comput Neurosci* 4:16, doi:10.3389/fncom.2010.00016 (existence and abstract verified).
  - This is CuBIC extended to non-stationary rates. It uses the law of total cumulance to absorb population-wide rate changes, and in simulation it removes false positives from pure rate co-variation.
  - **This bears directly on the README's main blind spot (lines 177–182: a busy stretch reads as coordination).** The README should at least name it as the published route to that limit, and it is a candidate fix for the tool.
- **Elephant** (the NeuralEnsemble analysis toolkit) ships `cubic()`: verified from its documentation.
- Not opened: Reimer, Staude, Ehm & Rotter 2012 (non-Poisson extension), cited from memory only, so unverified. Forward citations of Kuhn 2003 beyond CuBIC were not traced.

## Literatures searched, and not searched
- **Searched:** computational neuroscience on higher-order spike correlation (CuBIC, de-Poissonization, MIP/SIP, Elephant); spike-train surrogates (through the repo's own reading log, plus a NeuroXidence lookup); high-energy physics multiplicity statistics (factorial cumulants, clan model; secondary sources only); one search for factorial cumulants or CuBIC applied to calcium imaging, which found nothing.
- **Not searched (residual ⚠, not absence):**
  - quantum-optics photon counting (factorial moments);
  - ecology and epidemiology clustered-count models (Neyman Type A, compound Poisson);
  - seismology cluster processes;
  - the slice calcium-imaging assembly literature (Cossart, Yuste, Ikegaya, Bonifazi), including circular-shift surrogates there;
  - statistics references (Johnson, Kemp & Kotz);
  - correspondence (F7).

Sources:
- [CuBIC full text, Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2940040/fullTextXML)
- [Kuhn, Aertsen & Rotter 2003 PDF](https://brainworks.biologie.uni-freiburg.de/2003/journal%20papers/NECO15.1-Kuhn.pdf)
- [Ehm, Staude & Rotter 2007, arXiv](https://arxiv.org/pdf/0711.1965)
- [Staude, Grün & Rotter 2010, Frontiers](https://www.frontiersin.org/articles/10.3389/fncom.2010.00016/text)
- [Elephant CuBIC documentation](https://elephant.readthedocs.io/en/latest/reference/cubic.html)
- [NeuroXidence record](https://publikationen.ub.uni-frankfurt.de/opus4/frontdoor/index/index/year/2009/docId/7070)
- [Clan structure review, arXiv hep-ph/0405251](https://arxiv.org/pdf/hep-ph/0405251)
- [Correlations and fluctuations, arXiv hep-ph/0101016](https://arxiv.org/pdf/hep-ph/0101016)
