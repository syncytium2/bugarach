GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

Role 2 (DOI or Die): the coordination-share explainer
Artifact: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`

**Summary.** All five cited works exist, and their metadata on the page are correct. One overclaim matters: the "What is this project's" paragraph says solving for *k* and λ is the project's own, but Ehm et al. 2007, already on the page, estimates both from the same population count. The paragraph also gives CuBIC credit for more than it does. No third-party private correspondence appears on the page.

## Metadata check (all resolved through PubMed eutils, Europe PMC full text or arXiv; none from memory)

| Citation on page | Resolved | Status |
|---|---|---|
| Staude, Rotter & Grün 2010, *J Comput Neurosci* 29:327 (CuBIC) | PMID 19862611, doi:10.1007/s10827-009-0195-x, PMC2940040, pp. 327–350. Full text read. | correct |
| Ehm, Staude & Rotter 2007, *Electron J Stat* 1:473 | doi:10.1214/07-EJS095, arXiv 0711.1965, pp. 473–495. Full text read. | correct |
| Kuhn, Aertsen & Rotter 2003, *Neural Comput* 15:67 | PMID 12590820, doi:10.1162/089976603321043702, pp. 67–101. Full text read (Freiburg lab's own copy). | correct |
| Pipa, Wheeler, Singer & Nikolić 2008, *J Comput Neurosci* 25:64 | PMID 18219568, doi:10.1007/s10827-007-0065-3, PMC2758673. Full text read. | correct |
| Staude, Grün & Rotter 2010, *Front Comput Neurosci* 4:16 | PMID 20725510, doi:10.3389/fncom.2010.00016, PMC2906200. Full text read. | correct |

## Findings

**1. "What is this project's" claims the *k* and λ solve (README lines 248–249)**
- **Issue:** The paragraph claims "using factorial cumulants and solving them for *k* and λ" as the project's own.
  - Ehm et al. 2007, already cited two lines up as background, estimates the size distribution of shared events and their rate from the population count. Its abstract: "estimating [the jump measure] from a single, equidistantly sampled trajectory".
  - The CuBIC paper describes Ehm 2007 the same way: "'empirical de-Poissonization' presented by Ehm et al. (2007) thus directly estimates the orders of correlation in the data".
  - Ehm's estimator differs (it inverts the empirical characteristic function rather than using cumulants), but the solve itself is prior art.
  - The fixed model's moment solve, *k* = *f*₃/*f*₂ + 2, is the method of moments for a compound Poisson count with one fixed event size. That is a standard statistics move: Ehm 2007 cites the "decompounding" literature (Buchmann & Grübel 2003, *Ann Statist* 31:1054).
  - Using *factorial* rather than ordinary cumulants is the only part I could not find in neuroscience (see the searches at the end). It is standard in physics counting statistics.
- **Severity:** high. This is a novelty claim on a public portfolio page, and the contradicting work is already on the page.
- **Suggested fix:** Say that Ehm et al. 2007 already estimate the rate and size of shared events from the population count, by a different estimator. Narrow "ours" to: the factorial-cumulant moment solve under a fixed-size model, the share of events, the ladder of offsets, the use on calcium-event onsets, and the checks. Keep the factorial-cumulant point with a ⚠ (see the searches at the end).
- **Verified:** yes, for Ehm 2007 and CuBIC. The physics counting-statistics literature was searched shallowly.

**2. What CuBIC infers is overstated (lines 239–241)**
- **Issue:** The page says CuBIC uses cumulants "to infer how many neurons take part in coordinated events". CuBIC infers a **lower bound** on the order of correlation. Its text: "The outcome of CuBIC is a lower bound on the order of correlation".
- **Severity:** medium.
- **Suggested fix:** "...to infer a lower bound on how many neurons take part..."
- **Verified:** yes, from the full text.

**3. "The fixed model is the same family" is misattributed (lines 243–244)**
- **Issue:** The sentence reads as if the fixed model belongs to Kuhn's MIP family. MIP is binomial thinning of one shared Poisson process; Kuhn 2003 §2.2 confirms it. The family that holds both MIP and a fixed-size model is the **compound Poisson process** (CPP):
  - Ehm et al. 2007 use it.
  - Staude, Rotter & Grün 2010 state: "The SIP/MIP models presented in Kuhn et al. (2003) are special cases of this more general model".
  - Kuhn's own fixed-size model is the SIP (single interaction process), where every cell joins every event, so *k* = *N*.
  - Brette 2009 (*Neural Comput* 21:188–215, doi:10.1162/neco.2008.12-07-657) also builds models of this kind.
- **Severity:** medium.
- **Suggested fix:** "Both are compound Poisson models (Ehm et al. 2007; Staude et al. 2010): binomial is Kuhn et al.'s MIP, and fixed has one event size (Kuhn et al.'s SIP is the case where every cell joins)."
- **Verified:** yes.

**4. MIP's first appearance is earlier (line 243)**
- **Issue:** The thinning construction first appears, unnamed, in Kuhn, Rotter & Aertsen 2002, *Neurocomputing* 44–46:121–126 (read; Fig. 1 there). Kuhn 2003 says "Preliminary results have been presented elsewhere (Kuhn, Rotter, & Aertsen, 2002)" and is where the name "multiple interaction process" first appears.
- **Severity:** low. Citing 2003 for the name is correct.
- **Suggested fix:** None needed, or add "(construction first in Kuhn et al. 2002)".
- **Verified:** yes.

**5. The shift's origin and the glossary pointer (lines 244–246)**
- **Issue, part 1 (origin):** Pipa 2008 does shift whole trains ("each complete spike train is jittered on a timescale given by τr"). It is not the root, though. The repo's own trace (`docs/learned/tube_self_supervised/README.md` lines 738–750, and GLOSSARY "rigid shift") reaches back past it:
  - Pipa, Riehle & Grün 2007 (closed access, unread);
  - Pipa & Grün 2003;
  - the multiple-shift method of Grün et al. 1999, which Pipa 2008 itself credits.
- **Issue, part 2 (the pointer):** The glossary's rigid-shift entry says the **published** form *wraps* the train and this project's rigid shift does not. This tool's `shifted` does wrap. So "which this tool's shift is not" invites the wrong reading, that the tool departs from Pipa by wrapping. Its real departure is the offsets: a shuffled ladder of distinct offsets at least two windows apart, not independent random jitter within ±τr.
- **Issue, part 3 (missing literature):** Per-cell circular shift is also a standard null in calcium imaging (Dard et al. 2022, already cited in the glossary), and the page does not mention it.
- **Severity:** low–medium.
- **Suggested fix:** "...shifting surrogate (Pipa et al. 2008, after Grün et al.'s 1999 multiple-shift method), here with offsets on a shuffled ladder rather than random." State the ⚠ from the repo's trace: it stops at Pipa, Riehle & Grün 2007, unread.
- **Verified:** yes for Pipa 2008, from the full text. The root is not verified (Pipa, Riehle & Grün 2007 is unread).

**6. Missing: the same authors' paper on Figure 5's exact problem (lines 250–252)**
- **Issue:** Staude, Rotter & Grün 2008, "Can spike coordination be differentiated from rate covariation?", *Neural Comput* 20:1973–1999, doi:10.1162/neco.2008.06-07-550 (PMID 18336077). It is the direct predecessor of the cited Front 2010 paper, which cites it. The repo's own `docs/learned/recombination_nulls_reading_log.md` line 265 already lists it (abstract only).
- **Severity:** medium. This is the closest prior art for the "What else it counts" section.
- **Suggested fix:** Cite it next to Front 2010.
- **Verified:** existence yes. Content checked from the abstract only, as recorded in the repo's reading log.

**7. Missing: forward trace on cells' own clumping (step 2, lines 81–91; Figure 5C)**
- **Issue:** Reimer, Staude, Ehm & Rotter 2012, "Modeling and analyzing higher-order correlations in non-Poissonian spike trains", *J Neurosci Methods* 208:18–33, doi:10.1016/j.jneumeth.2012.04.015 (PMID 22561088). By its abstract it tests how non-Poisson (clumped) single-cell statistics bias the estimate of event rate and size from the population count. That is the problem the page's shifted copies address.
- **Severity:** medium. It is the authors' own next step on this exact weakness.
- **Suggested fix:** Cite it as related work on single-cell clumping.
- **Verified:** existence and abstract, yes. Full text not read (Elsevier, closed access).

**8. Front 2010 citation (lines 250–252)**
- **Finding:** No defect. Its abstract says it adapts CuBIC "to time-varying firing rates" and "corrects for false positive inference of correlations in data with pure rate co-variation", which matches the page.
- **Severity:** none.
- **Verified:** yes, from the full text.

**9. Private correspondence (CLAUDE.md rule)**
- **Finding:** No defect. The page quotes nobody outside the project. "(Tony, 2026-10-14)" is the user's own ruling.
- **Severity:** none.
- **Verified:** yes.

**10. Nobody has been asked**
- **Issue:** I found no record anywhere in the repo of contact with the Rotter group (Freiburg, last author on Ehm 2007, Kuhn 2003 and Front 2010) or with Grün (last author on CuBIC, then at RIKEN BSI; her group maintains the CuBIC code in the Elephant toolbox). A 2026-09-14 role-2 review raised the same question for Grün's group about shifting, and it was never answered.
- **Severity:** residual ⚠.
- **Suggested fix:** Ask Tony whether anyone has asked Rotter, Staude or Grün about a moment solve for *k* and λ with fixed-size events. If someone has, cite it as [archive note: the reviewer named the standard citation form for a private conversation here — the name, the words for a private conversation, and the date — paraphrased and not quoted. Reworded on archiving because `tools/check_quotes.py` reads that phrase beside this report's quotations of published papers as quoted correspondence; nothing in this report is private correspondence.]
- **Verified:** no. Only the repo was searched.

## Where the backward trace stopped, and why

- **CuBIC → Ehm 2007 → Buchmann & Grübel 2003 and Holgate 1964.** Stopped at the last two: not fetched. One step short of the statistics root.
- **MIP → Kuhn 2002.** That is the root (read).
- **Shift → Pipa 2008 → Grün et al. 1999 and Pipa, Riehle & Grün 2007.** Stopped at the last two: closed access, unread here (the repo's own earlier trace stopped at the same place).

## Literatures searched

- **Searched:** the spike-train higher-order-correlation literature (the CuBIC, de-Poissonization and MIP/SIP line, plus its forward trace: Front 2010, Reimer 2012 and 2013, Elephant).
- **Searched:** statistics on estimating compound Poisson and Neyman Type A distributions (decompounding, method of moments). One shallow search, plus Ehm's reference list.
- **Searched:** physics counting statistics with factorial cumulants (one search). The tool exists there.
- **Searched:** calcium imaging × CuBIC (one search). No application found.
- **NOT searched (⚠):** quantum-optics photon counting (Mandel Q, factorial moments), cosmology and ecology counts-in-cells, particle-physics multiplicity factorial moments, and the calcium-imaging "population event and ensemble size" literature in depth.

Files written: downloaded papers and text extracts in `C:\Users\defazio\AppData\Local\Temp\claude\c--Users-defazio-bugarach-bugarach\8f7e79d0-c19b-4389-819d-be7bbbbd9efc\scratchpad\mb-r2\` (PMC2940040, PMC2906200 and PMC2758673 as .xml and .txt; ehm, kuhn2002 and kuhn2003 as .txt; the PDFs in `dl\`). Nothing was edited. The lit shelf (`<darkroom>/bugarach/archive/2026-08/lit/`) holds only Pipa 2008 of the cited papers; the others were fetched from open-access sources and are not shelved.
