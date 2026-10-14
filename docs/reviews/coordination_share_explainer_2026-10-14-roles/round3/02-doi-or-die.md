GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

Role 2, "DOI or Die": citation and reference check on `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`. I edited nothing and created no files (the scratch folder `...\scratchpad\mb-r3\role2\` exists and is empty). I did not read the earlier rounds' role-2 reports, so this pass is blind.

## Metadata check: all seven external references are correct
I resolved each one by DOI through Crossref. None is fabricated or guessed.
- Ehm, Staude & Rotter 2007, *Electron J Stat* 1:473–495, 10.1214/07-EJS095. The abstract estimates the "jump measure" (how often joint events happen and how big they are) from the population count alone, so "by a different estimator" is fair.
- Staude, Rotter & Grün 2010, *J Comput Neurosci* 29:327–350, 10.1007/s10827-009-0195-x (online 2009-10-28). This is CuBIC; I checked it against the PMC2940040 text.
- Kuhn, Aertsen & Rotter 2003, *Neural Comput* 15:67–101, 10.1162/089976603321043702. CuBIC calls SIP/MIP "special cases" of the compound Poisson process (CPP), so "binomial = MIP" is correct.
- Pipa, Wheeler, Singer & Nikolić 2008, *J Comput Neurosci* 25:64–88, 10.1007/s10827-007-0065-3. Checked against the PMC2758673 text.
- Staude, Rotter & Grün 2008, *Neural Comput* 20:1973–1999, 10.1162/neco.2008.06-07-550.
- Staude, Grün & Rotter 2010, *Front Comput Neurosci* 4:16, 10.3389/fncom.2010.00016. Crossref lists only Staude, but the publisher page lists all three authors. It does correct CuBIC for shared rate changes, which supports the page's line 230.
- Reimer, Staude, Ehm & Rotter 2012, *J Neurosci Methods* 208:18–33, 10.1016/j.jneumeth.2012.04.015.

## Findings
(location · issue · severity · suggested fix · verified against a source)

1. **Lines 281–284** · "after the multiple-shift method of Grün and colleagues" has no year, so a reader cannot check it, and the lineage is wrong. Pipa 2008 does describe the multiple-shift method (Grün et al. 1999) as shifting "entire spike trains in relation to one another". But it presents its random, independent whole-train shifts as an *alternative* to that method, which tries every combination of shifts and does not scale. The multiple-shift method is a coincidence counter, not a surrogate. The project's own reading log already records this correction (`docs/learned/recombination_nulls_reading_log.md` line 222: "the multiple-shift method is a coincidence **detector**"), and the page repeats the old claim. The two papers also come from different labs: Grün 1999's last author is Aertsen; Pipa 2008's is Nikolić, in Singer's group. · **Medium** · Either drop the clause, or write "(Pipa et al. 2008, who contrast it with the exhaustive multiple-shift coincidence count of Grün, Diesmann, Grammont, Riehle & Aertsen 1999, *J Neurosci Methods* 94:67, 10.1016/S0165-0270(99)00126-0)". · **yes**

2. **Lines 291–293, "What is this project's: a two-number shortcut"** · The cited CuBIC paper already reads event size from low-order cumulants of the population count. Its main text says κ1 and κ2 are fixed by the carrier rate and the first two moments of the amplitude distribution, and that their ratio ρ "equals the Fano Factor of the population spike count". The project's construction is a real step beyond that: it uses excess *factorial* cumulants with surrogate subtraction, takes f₃/f₂, and closes with the fixed or binomial model. But calling the "two-number shortcut" ours, without naming CuBIC's own two-moment ratio, overstates novelty on a public page. · **Medium** · Reword to something like "a variant of CuBIC's moment ratio: excess factorial cumulants f₂, f₃ closed by one of two models". Keep the other items in the list. · **yes** (from the prose; the equations are images and did not render, and Appendix B was not read in full)

3. **Lines 293–295, ⚠ residual on factorial cumulants outside neuroscience** · Keeping the residual is correct, but it should name what is still unsearched, and the strongest candidate is concrete. Qian & Elson 1990, "Distribution of molecular aggregation by analysis of fluctuation moments", *PNAS* 87:5479–5483, 10.1073/pnas.87.14.5479, estimate the distribution of aggregate sizes from the higher moments of fluctuation counts. That is the same inverse problem as moments of k cells. A patent citing it says they used "the first three cumulants". Its companion is Qian & Elson 1990, *Biophys J* 57:375. Two related fields are also unsearched: number-and-brightness analysis, and method-of-moments estimation for compound Poisson / Neyman Type A distributions. · **Medium** (a public claim of what is ours) · Name these in the ⚠, e.g. "fluorescence fluctuation moment analysis (Qian & Elson 1990) and compound-Poisson method-of-moments in statistics were not searched", or read Qian & Elson before keeping the claim. · **partly**: the paper exists and I read the abstract; whether it uses a third-to-second cumulant ratio is not verified, because only the abstract and page images were available.

4. **Lines 281–284 and 293 (the ladder of slides; applying it to calcium onsets)** · Shifting each cell's train by its own circular offset is the standard null in calcium imaging, the field these data come from. The project's own reading log, rows 217 and 283–284, lists CICADA (Zenodo 10.5281/zenodo.10041434), Dard et al. 2022 and Bocchio et al. 2020. The page credits only spike-train sources. The claim that the ladder is ours, where "the published ones are random", holds for Pipa 2008 and for CICADA. · **Low** · Add one clause naming the calcium-imaging use of per-cell circular shifts. · **partly**: I confirmed this from the reading log only and did not reopen those papers.

5. **Lines 286–289, forward trace** · The same group's next step applied the cumulant method to a signal that is not spikes: Reimer, Staude, Boucsein & Rotter 2013, "A new method to infer higher-order spike correlations from membrane potentials" (CuBICm), *J Comput Neurosci* 35:169–186, 10.1007/s10827-013-0446-8. That is the nearest forward prior art to "applying it to calcium-event onsets". One search for CuBIC or cumulant methods applied to calcium imaging found nothing, which is a residual, not proof of absence. · **Low** · Cite CuBICm beside the 2012 paper, and say that an application to calcium imaging was searched once and not found. · **yes** for the 2013 metadata; the search is not exhaustive.

6. **Lines 286–287, "the same authors addressed … rate changes shared across cells"** · Staude, Rotter & Grün 2008 decomposes the *pairwise* cross-correlation of doubly stochastic processes; it does not use population cumulants. The 2010 Frontiers paper is the population-level correction. The sentence is accurate as written but may read as if both apply to this measure. · **Info** · Optionally: "(pairwise, Staude et al. 2008; for the population count, Staude et al. 2010)". · **yes**

7. **Backward trace, where I stopped** · CuBIC credits Holgate 1964 (bivariate Poisson), Johnson & Goodman 2008, Snyder & Miller 1991, and Daley & Vere-Jones 2005 for the compound/marked Poisson construction, and Ehm 2007 as the earlier estimator applied to spike trains. I stopped at Ehm 2007 and Kuhn 2003 because the page's sentence ("not new") does not claim a root. I did not open Holgate 1964 or Johnson & Goodman 2008. · **Info** · No change needed. · **yes** (from CuBIC's references)

8. **Lines 294–295, correspondence** · Nobody has asked Rotter, Staude, Grün or Ehm about the shortcut, and I found no correspondence in the repo on this topic (I searched `docs/` excluding reviews). That is correctly a residual ⚠. The page quotes no third party, so the public-repo rule on other people's words is satisfied. The reading log (line 396) already names writing to the Grün group as the cheapest open check on a different question; one letter could cover both. Whether to write is Tony's call. · **Info** · Keep the ⚠. · **yes** (repo grep)

## Project-internal attributions: checked, no findings
- ADR-0017 point 4 does name this measure as the first confirmed exception (Tony, 2026-10-14).
- `CAL_NO_PROBE` does record "share +43% FAIL" with the probe stretch in.
- `CAL_TOL = 0.25` has no stated reason anywhere in the tree outside the reviews, so "the tool does not say why 25%" is correct.
- The `ADOPTED_MODEL` comment gives the reason the page reports.
- The docstring (lines 36 and 175) does say the two models "bracket" the answer.
- `CAL_JITTER` is 0.106 s for the fast stream.

## Literatures searched
- Searched: neuroscience compound Poisson / cumulant methods (Crossref; CuBIC full text and its references; the Frontiers 2010 page); spike-train surrogate lineage (Pipa 2008 full text; Grün 1999 metadata); fluorescence fluctuation moment analysis (one search, abstract level); CuBIC applied to calcium imaging (one search, nothing found).
- Not searched (residual ⚠): statistics on compound-Poisson / Neyman Type A method of moments; high-energy-physics and photon-counting factorial cumulants beyond Qian & Elson; the bodies of papers citing CuBIC, Ehm 2007 or CuBICm; prior art for a deterministic offset ladder.

Sources:
- [Crossref API](https://api.crossref.org)
- [CuBIC, PMC2940040](https://pmc.ncbi.nlm.nih.gov/articles/PMC2940040)
- [NeuroXidence, PMC2758673](https://pmc.ncbi.nlm.nih.gov/articles/PMC2758673)
- [Staude, Grün & Rotter 2010, Frontiers](https://www.frontiersin.org/articles/10.3389/fncom.2010.00016/full)
- [Qian & Elson 1990, PMC54348](https://pmc.ncbi.nlm.nih.gov/articles/PMC54348)
- [CuBICm, Springer](https://link.springer.com/article/10.1007/s10827-013-0446-8)
- [Elephant CuBIC documentation](https://elephant.readthedocs.io/en/v0.8.0/reference/cubic.html)
