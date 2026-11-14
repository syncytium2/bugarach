GRANT 2 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch and Claude Docs, cloud-storage and Gmail MCP tools. I also hold everything in my grant: Read, Grep, Glob, Bash, WebSearch, WebFetch (the last two loaded through ToolSearch).

I used none of the forbidden tools. I wrote only to `scratchpad/mb/work-r3-2/` (two page renders and a text extraction).

**Blindness breach, to record in the ledger.** I ran a repo-wide Grep for "Kreuz 2026 / Biol Cybern". Its glob filter did not exclude directories, so it printed about five matching lines from `docs/reviews/chapter-1-aim0_2026-10-29-roles/02-doi-or-die.md` and `...-round2-roles/02-doi-or-die.md`, plus one table row from `...-round2-followup.md`. I saw only those lines, opened none of the files, and relied on nothing in them. Finding 6 below rests on `docs/learned/synthetic_validation/README.md` l. 99 and `kreuz_sort/literature_report.md`. Weigh finding 6 and the Grün 1996 residual with that exposure in mind. I had found the Grün 1996 root independently in the Grün 1999 text (abstract and p. 68).

Artifact checked: `docs/dissertation/chapter-1-aim0.md`, hash a4fbb30e… (matches).

## Verdict

No blocking or major citation defects. Every unmarked reference exists in the library (`01-lit/bugarach/synthetic_validation/` or `coordination/`), and the claims I checked against the texts are supported. What remains is minor: wording that goes slightly beyond a source, notation attributed to the wrong edition, ⚠ marks that do not match the repository's own reading record, and roots verified one step short. I would sign off once the minor items are fixed or acknowledged.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | §1.2.3 "averaged over a displacement of up to ±j time steps" | Grün et al. 1999 write the displacement as **s** (uniform over ±s, p_s = 1/(2s+1); Eq. 5 is F(s,b)). The symbol j is Pazienti et al. 2008's jitter. The fission probability is also for one fixed spike and one jittered replica, not a symmetric near-coincidence. | minor | Write "±s time steps (one spike of the pair displaced uniformly)". | yes (Grün 1999 text, Eqs. 4–6, Fig. 1) |
| 2 | §1.2.3 "their spatial example is a hard-core inhibition process" | Diggle & Gratton 1984 §6 fit a pairwise-interaction inhibition process (Eq. 6.2): a hard core δ plus a soft interaction range ρ. They note that the pure hard-core class (δ = ρ) "turns out to be inadequate to describe the cell data". | minor | Write "a pairwise-interaction inhibition process (a hard core plus soft repulsion)". The not-a-cluster-process point stands. | yes (D&G 1984 pp. 208–209) |
| 3 | §1.7.1 "deft² = 1 + roh(b̄ − 1), with b̄ the mean cluster size … (Kish 1995, pp. 63–64; it is the intraclass correlation)" | On those pages Kish writes roh = (deft² − 1)/(n/a − 1), calling it "a synthetic but useful 'ratio of homogeneity'" (p. 63), and deft² = 1 + roh(n_c/a − 1) (p. 64). b̄ is not his 1995 notation, and he does not equate roh with the intraclass correlation there; "synthetic" signals that it is not exactly the ICC. | minor | Use Kish's n/a, or attribute b̄ to Kish 1965 ⚠. Change "it is the intraclass correlation" to "a synthetic analogue of the intraclass correlation". | yes (rendered pp. 63–64 of the scan) |
| 4 | §1.8.3 "Louis, Borgelt & Grün (2010, Fig. 6) separated two and three groups of different sizes" | Fig. 6(a): two groups "are reliably distinguished". Fig. 6(b): for three groups of various jitters, correct identification "is not as obvious". The "converge" remark is quoted correctly. | minor | Write "separated two groups reliably and three less clearly". | yes (Louis 2010 text, p. 708) |
| 5 | References, Durbin 1951 "*Br J Stat Psychol* 4:85–90" | The scan's masthead reads "The British Journal of Psychology, Statistical Section, Vol. IV, Part II, June 1951". The journal took the *Br J Stat Psychol* title later; the DOI indexes it under the later name. | minor | Either form is defensible; for accuracy use "*Br J Psychol Stat Sect* 4:85–90 (now *Br J Stat Psychol*)". | yes (scan masthead) |
| 6 | §1.2.3 "(Kreuz 2026 ⚠)"; References "Kreuz T (2026) … *Biol Cybern* 120:21. ⚠"; also "Grün, Abeles & Diesmann (2008 ⚠)" | The ⚠ marks do not match the repository's own reading record. **(a)** `docs/learned/synthetic_validation/kreuz_sort/literature_report.md` §5 read the review as arXiv 2510.07140v2 and quotes it: "the sorting is performed using simulated annealing", which supports "still orders trains by annealing". `docs/learned/synthetic_validation/README.md` l. 99 gives issue 120(3–4) and doi 10.1007/s00422-026-01045-5, both missing from the entry. **(b)** `prior_art/grun_literature.md` lists Grün, Abeles & Diesmann 2008 as "Full text", and Louis 2010's reference list confirms its metadata (LNCS 5286:96–114). The ⚠ marks are conservative but misdescribe what was read. | minor | Kreuz 2026: drop ⚠ and add "Read as arXiv 2510.07140v2", the issue and the DOI. G-A-D 2008: drop ⚠ or say why it is kept. Also add the PDFs to the shelf. Note: the review says annealing switches "any two" trains, which conflicts with the 2017 paper's neighbor swaps. This does not affect the chapter's claim. | yes (repo records; Louis 2010 refs). I did not open the review myself. |
| 7 | §1.7.2 "a relation usually credited to Greiner (1909 ⚠)"; References "Greiner R (1909) … *Z Math Phys* 57. ⚠" | The trace stops at Kruskal 1958, which credits the quadrant relation to Cramér (p. 290) and does not cite Greiner. A web search could not confirm the Greiner entry, and the entry has no pages. The attribution "usually credited" has no source behind it in the chapter. | minor | Cite the secondary source that credits Greiner, add verified pages, or keep ⚠ and list it for Tony to pull. Do not complete pages from memory. | partly (Kruskal yes; Greiner no) |
| 8 | References, "Copeland AH (1951) … Unpublished seminar notes. ⚠" | The entry has no venue or institution. Shah & Wainwright cite it as [Cop51], but in my text extraction the bibliography entry is garbled and could not be read. | minor | Fill in the venue from a source that is actually opened (e.g., the Shah & Wainwright PDF bibliography), or leave the entry as is with ⚠. | no |

## Checked and supported (no finding)

- **Grün 1999 / Pazienti 2008 / Louis 2010.** Fission probability, Eq. 5. Pazienti derives the dither × jitter interaction and estimates precision from the decay. Louis 2010: binomial count given the overlap, Max2 change in slope, two straight-line fit, built on Grün, Abeles & Diesmann 2008.
- **CuBIC.** Eq. 3 is "the central equation", with a Poisson carrier. Kuhn et al. 2003 SIP/MIP are "special cases".
- **Kreuz 2022.** The first-row and diagonal "simple shift" beside annealing ("introduced a direct shift beside annealing" holds). **Mariani 2025.** Extrapolation direct shift; "overlapping global events" is in the title.
- **Kreuz 2017.** The sec. 3.1 quote is verbatim. The sec. 2.5 binomial null is rejected because pairwise orders are not independent.
- **Cecchini 2021.** Wide-field calcium imaging.
- **Thomas 1949.** Whole clusters are counted per quadrat, with no scatter law, as the chapter says.
- **Waagepetersen 2007.** Thomas K-function, Eq. 7.
- **Kruskal 1958.** Sec. 4 derives τ via the q relation, citing Cramér.
- **Coppersmith 2006.** 5-approximation; w_uv + w_vu = 1; pp. 776–782.
- **Shah & Wainwright.** Copeland counting, top-k, comparisons independent across pairs.
- **Tomlinson 2019, Silva 2015, Schrader 2008, Müller 2004, Wu & Müller 2005, Staude-Grün-Rotter 2010.** Per the shelf README.
- **DeFazio 2026.** 10 Hz frames, two event types, 38(11):e70298, author list matches.
- **Wang 2024.** JASA 119(547):2382–2395 (RePEc).
- **Reimer 2012.** Exists, JNM 208:18–33; Bernstein Center Freiburg with Rotter as last author ("from Rotter's group" holds). Content claim is abstract-only, as marked.
- **Peyrache 2010 and Lopes-dos-Santos 2011.** Held on the `coordination/` shelf.
- **Header claim.** "Every other source was read" holds: every unmarked reference is in the library.

## Residuals (⚠)

- **Origin of the fission probability, one step short.** Grün 1999 cites Grün 1996 (*Unitary Joint-Events in Multiple-Neuron Spiking Activity*, Reihe Physik 60, Harri Deutsch) for the loss of sensitivity to jitter under binning. The book is not held, so whether F(s,b) is older than 1999 is unverified.
- **Papers to pull:** Grün 1996; Reimer et al. 2012 (JNM 208:18); Greiner 1909; Kish 1965; Diggle 1978 and 1983; Rodriguez-Iturbe, Cox & Isham 1987; the Kreuz 2026 journal PDF.
- **Correspondence.** The chapter itself records two enquiries that have not been sent: the Grün lab on a Gaussian or formal-fit version, and Kreuz on annealing versus ranking. "Nobody was asked" stands as a residual until they are.
- **Literatures searched.** I did not run my own novelty search; I relied on `prior_art/` (Grün group, order, cross-field survey). The chapter's own ⚠ list of unsearched fields stands: point-process counting theory beyond textbooks, hydrology, the normal range distribution, and super-resolution/radar for §1.6.

*(Archivist's note: one connector name in the GRANT line was replaced with "cloud-storage" to pass the repository's path scrub; nothing else is changed.)*
