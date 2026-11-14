GRANT 2 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, and the Claude Docs, Dropbox and Gmail write tools

(This is a finding about the run: the harness gave this reviewer more tools than its grant allows. I edited nothing in the repository. All my scratch files are under <scratch>/mb3/role02/.)

# Role 2 "DOI or Die": chapter-1-aim0.md (blob faa8e320)

## How I checked
- **Live resolution.** I resolved every DOI in the reference list, plus the five arXiv DOIs, through the doi.org handle API. Each DOI was also checked for correction or retraction notices with the Crossref `updates:` filter. All 51 identifiers resolve (responseCode 1). There are no corrections or retractions; the only update notice is PLOS's own versioning record on Cecchini 2021.
- **Metadata.** I matched author, year, journal, volume and pages through Crossref bibliographic search. All agree with the reference list. Year differences between online-first and print issues are normal: Peyrache and CuBIC are 2009 online and 2010 in print; Wang is 2023 online and 2024 in print.
- **References without DOIs.** Each was reached by a second route:
  - Finn 1967 and Finn & Johnson 1968: open-access scans of RCA Review at worldradiohistory.com, contents pages checked. Finn & Johnson run 414–464; the next article starts on p. 465.
  - Kish 1995: Statistics Sweden's JOS archive lists it in vol 11(1), March 1995.
  - Shah & Wainwright: the jmlr.org page gives 18(199):1–38.
  - Williams 2020: listed in the NeurIPS 2020 proceedings.
  - Books (Daley & Vere-Jones, Møller & Waagepetersen, Glaz et al.): DOIs resolved through Crossref.
  - Cramér 1946, Diggle 1983, Kish 1965: confirmed only by book reviews of the time that are indexed in Crossref.
- **Claims checked against the text** (library copies in <01-lit>, plus the OA Finn 1967 scan):
  - Kreuz 2017: the quote is in sec. 3.1 and the binomial-null rejection in sec. 2.5, both verbatim.
  - Kish 1995: p. 63 has "a synthetic but useful 'ratio of homogeneity'" and roh = (deft² − 1)/(n/a − 1); p. 64 has deft² = 1 + roh(n_c/a − 1).
  - Kruskal 1958: sec. 4 gives the τ relation for the bivariate normal from the quadrant formula, citing Cramér p. 290, and credits the quadrant measure to Sheppard 1899.
  - Louis, Borgelt & Grün 2010: Fig. 6 matches (two groups clear, three less so), and so does "increasingly difficult to disentangle as their sizes converge".
  - Rohling 1983: Fig. 3(b) shows "two guard cells directly adjacent to the test cell".
  - Finn & Johnson 1968: the masking statement is in their abstract, and they describe the earlier CFAR regulated by receiver noise.
  - Waagepetersen 2007: Eq. 7 gives the Thomas K-function in closed form.
  - Mariani 2025: the "disentangle global events with overlap" wording is there.
  - Perkel 1967: uses "cross-correlation histogram".
  - Cossart 2003: threshold from interval-reshuffled surrogates.
  - Diggle & Gratton 1984: the example is a pairwise-interaction process.
  - Thomas 1949: quadrat counts only.
  - Durbin 1951: the journal name "Br J Psychol Stat Sect" is correct; the masthead reads "Statistical Section, The British Journal of Psychology".
- **Literatures searched:** Crossref/doi.org; the RCA Review archive; the JOS archive; JMLR; NeurIPS; a web search on the origin of the arcsine relation; a web search for later Grün-lab work on reading group size and jitter across bin widths.
- **Not searched:** IEEE Xplore full text (the fetch was refused); radar literature before 1966 (Hansen 1965 and others); the history of the τ–ρ relation beyond secondary sources.

## Findings
Each finding gives location · issue · severity · suggested fix · whether I could verify it against a source.

1. **§1.2.3, line 151; References, line 1750 · Finn 1967 has no ⚠, but it was never on the shelf.** <repo>/docs/methods/coordination_pipeline_methods_cover_memo.md:119 says "Finn (1967) [is] not on the shelf". The 01-lit radar README records it only as a lead taken from Hansen's reference list. That contradicts the chapter's header line, "every other source was read against the claim it supports".
   - I read it now, from the OA scan of RCA Review 28(4), Dec 1967, p. 653 ff. at worldradiohistory.com. It does support the claim: the threshold is made "proportional to an updated maximum-likelihood estimate of the output variance", using "the N resolution cells surrounding the cell under test".
   - The claim stands; only its status is wrong.
   - Severity: medium.
   - Fix: file the OA scan in 01-lit/bugarach/radar, update the README, and cite the page.
   - Verified: yes.

2. **§1.2.3, line 151 (origin) · The trace stops one step short.** Finn 1967 does not develop the spatially sampled estimate itself; it refers it to its Reference 1: H. M. Finn, "Adaptive Detection in Clutter", Proc. Natl Electronics Conf. XXII:562, 1966.
   - Finn & Johnson 1968 also cite that 1966 paper (their ref. 3), along with an Allerton 1967 paper.
   - Crossref holds the 1966 paper as Finn H, "Adaptive detection in clutter", Fifth Symposium on Adaptive Processes (1966), pp. 562–567, doi:10.1109/sap.1966.271149. It resolves; it is paywalled (IEEE).
   - "Finn (1967) set it instead…" therefore credits the second step, not the first.
   - Severity: medium.
   - Fix: credit Finn 1966, or say "verified to Finn 1967; its root, Finn 1966, not held".
   - **Paper needed: doi:10.1109/sap.1966.271149.**
   - Verified: partly (the chain is verified; the root is not read).

3. **Table 1.9 (line 1569) and §1.8.2; References, line 1781 · Sheppard 1899 has no ⚠ but appears to have been read only through Kruskal.** There is no copy in 01-lit, and the repository's note (synthetic_validation/README.md:104) cites it only through Kruskal. It should carry ⚠ "cited through Kruskal 1958", as Cramér does.
   - Upstream lineage is also left out. Secondary sources (Wikipedia, citing Lindskog, McNeil & Schmock) trace τ = (2/π) arcsin ρ to Stieltjes 1889, Sheppard 1898 and Greiner 1909, and name it for Greiner. Sheppard 1898 is Proc R Soc 62:170–173, doi:10.1098/rspl.1897.0090, which resolves.
   - I have not read Stieltjes, Sheppard 1898 or Greiner, so the lineage is a residual ⚠.
   - Severity: low.
   - Fix: add the ⚠, or obtain Sheppard 1899 (doi:10.1098/rsta.1899.0003; probably free at royalsocietypublishing.org).
   - Verified: partly.

4. **Table 1.9, line 1556 · "Grün 1996, not held" is named as the root of the fission probability but is missing from the References.** Severity: low. Fix: add a reference entry marked ⚠ (not held). Verified: yes (it is absent from the list).

5. **§1.8.2 (line 1415) and Table 1.9 · The Copeland wording slightly overstates the identity.** Shah & Wainwright's Copeland counting ranks items "by the number of pairwise comparisons won". They describe it as a special case of the Borda count and cite Copeland 1951 and de Borda 1781. The score sort uses wins minus losses with unequal co-participation, and the two orders differ when pairs are compared unequally often.
   - Severity: low.
   - Fix: "a net-wins variant of what Shah & Wainwright call Copeland counting (Copeland 1951)".
   - Verified: yes (S&W sec. 2.3).

6. **Table 1.9 and §1.4 "Prior work" · An earlier statement of the method is uncited.** Louis & Grün 2009 (BMC Neurosci 10(Suppl 1):P253, doi:10.1186/1471-2202-10-S1-P253, open access, resolves) states the bin-width tracking of the second maximum before the 2010 paper. It is listed as needed in <01-lit>/_NEEDED.md but is not cited.
   - Severity: low.
   - Fix: cite it as the first statement of the method, or note it as not read.
   - Verified: yes (existence and abstract).

7. **§1.9.2, lines 1580–1581 · The enquiry to the Kreuz group is cheaper than the chapter implies.** The chapter correctly says the enquiry to Kreuz has not been sent. But a working mail channel with Thomas Kreuz already exists (docs/kreuz_note.md, kreuz_note_2_apology.md, kreuz_note_3_thanks.md, Aug–Sep 2026). Question for Tony: did any of Kreuz's replies touch on ordering, annealing versus ranking, or the finite-size bias? If so, it is a citable personal communication (with permission, given the PR#89 lesson). If not, the ask costs one mail. "Nobody was asked" stays a residual ⚠ for both the Kreuz and Grün enquiries.
   - Severity: low.
   - Fix: ask Tony, then either quote and date the reply or keep the residual ⚠.
   - Verified: no (I did not read private mail).

8. **Informational, no change to the artifact.** <01-lit>/Kish-SamplingOrganizationsGroups-1965.pdf is Kish 1965, Am Sociol Rev 30:564–572 ("Sampling organizations and groups of unequal sizes"). It is not the cited *Survey Sampling* (1965). Watch for the two being confused. Finn & Johnson 1968 misprint Finn 1967 as vol. 29; the chapter's vol. 28(4) is correct. Cossart 2003 credits interval reshuffling to Mao et al. 2001 (their ref. 12), which is not held. The chapter cites Cossart only as an example of practice, so no change is needed. Verified: yes.

## Residuals ⚠
- **Claims not checked against the text** (existence and metadata only):
  - Grün 1999 eq. 5 (the fission function is present; the equation number was not checked)
  - Pazienti 2008 ("at a single tolerated spread")
  - CuBIC eq. 3
  - Müller 2004 and Wu & Müller 2005
  - Tomlinson 2019 (net count; partly seen)
  - Silva 2015, Coppersmith, Skillings & Mack, Kendall & Babington Smith, Neyman & Scott
  - Malvache 2016 (window-count detection)
  - Williams 2020, Wang 2024, Schrader 2008, Peyrache 2010, Lopes-dos-Santos 2011
  - DeFazio 2026, Cecchini 2021, Kreuz 2022, Kreuz 2026
- **Already marked ⚠ in the chapter:** Reimer 2012 (abstract only); Trunk 1978 (not held, doi:10.1109/taes.1978.308625).
- **Forward trace:**
  - Kreuz group: covered by the chapter (2021, 2022, 2025, 2026).
  - Grün group: checked only to Louis & Grün 2009/2010 by web search. SPADE and ASSET are named in the repository's prior-art record but were not re-searched here.

## Papers needed
- Finn HM 1966, "Adaptive detection in clutter", doi:10.1109/sap.1966.271149 (IEEE, paywalled)
- Finn 1967 is free: worldradiohistory.com/ARCHIVE-RCA/RCA-Review/RCA-Review-1967-12.pdf (pp. 653–678)

unreached: 0
