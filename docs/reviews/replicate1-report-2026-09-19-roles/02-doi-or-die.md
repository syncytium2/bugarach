GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**Role 2, citations and references ("DOI or Die"). Blind verify, round 3 of 3.**

I reviewed `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. Its hash is 9a99a7a4209b11b7bb285c260a43ea31aabda1d3, which matches the build you named. I read the text extracted from that HTML. I did not open any earlier review reports, and I wrote nothing into any repository. My scratch files are in the session scratchpad.

**Headline:** All 8 references exist, and no metadata is fabricated. The problems are about origins and completeness:
- **Two major findings, both in section 3:**
  - The paper cited for the Kreuz lab's thresholding is an application, not the lab's own method paper.
  - The wording hands a Yuste-lab paper to the Cossart lab by implication.
- **Seven minor findings.**
- **No private correspondence is quoted.**

## Findings

Format: location · issue · severity · suggested fix · verified against a source.

**1.** §3, the SPIKE-synch sentence ("the Kreuz lab has published threshold detection on that measure itself (Cecchini and colleagues, 2021)"), and the References.
- **Issue:** Cecchini 2021 is an application, not the root. Its Methods filter spikes by SPIKE-Synchronization ("coincident with spikes in at least three quarters of the other spike trains"), and it credits that framework to its ref [23]. Ref [23] is the lab's method paper: Kreuz T, Satuvuori E, Pofahl M, Mulansky M (2017), *Leaders and followers: quantifying consistency in spatio-temporal propagation patterns*, New Journal of Physics 19(4):043028, doi:10.1088/1367-2630/aa68c3. Its §2.2 introduces a threshold C_thr on the SPIKE-synchronization profile ("only spikes with a coincidence value higher than this parameter C_thr are taken into account"). This is also the forward trace from the 2015 measure paper: the same author's next paper is where the thresholding lives.
- **Severity:** major.
- **Fix:** Cite Kreuz et al. 2017 as the origin, and keep Cecchini 2021 as a later application. For example: "...has published threshold detection on that measure itself (Kreuz and colleagues, 2017; applied by Cecchini and colleagues, 2021)". Add the 2017 entry to References.
- **Verified:** yes. Crossref for both DOIs; WebFetch of the PLoS page and the IOP page.
  - ⚠ Both passages came back through WebFetch's summarizing model. I did not read either PDF end to end.

**2.** §3, "Binned SCE descends from Cossart, Aronov and Yuste (2003) … the circular-shift null is the Cossart lab's later form".
- **Issue:** Wrong-lab implication. "The Cossart lab's later form" tells the reader that the 2003 form was also the Cossart lab's. It was not. Cossart was first author, the last author is Yuste, and the affiliation is the Department of Biological Sciences, Columbia (I checked the paper's author block). `docs/detector_history.md` makes this point in so many words: "Cossart 2003, from **Yuste's** lab" and "a **Yuste-lab** method that travelled to Marseille with its first author".
- **Severity:** major (the checklist treats crediting a method to the wrong laboratory as a research-integrity issue).
- **Fix:** "…Cossart, Aronov and Yuste (2003), from Rafael Yuste's laboratory, who tested…; the circular-shift null is the form the Cossart lab later adopted in its own laboratory, in their CICADA software…".
- **Verified:** yes. I read the Yuste-lab-hosted PDF (blogs.cuit.columbia.edu/rmy5/files/2017/06/cossart.nature.03.pdf) and Crossref.

**3.** §3, the same Cossart 2003 attribution.
- **Issue:** The trace stops one step short of the root. The report's description of the 2003 method is exactly right. The 2003 Methods say "we used interval reshuffling (randomly reordering of intervals between events for each cell)", done 1,000 times, with the threshold at P < 0.05. But the 2003 paper credits the surrogate method to its ref 12: Mao BQ, Hamzei-Sichani F, Aronov D, Froemke RC, Yuste R (2001), *Dynamics of spontaneous activity in neocortical slices*, Neuron 32:883–898, doi:10.1016/S0896-6273(01)00518-9. That is the same lab and shares a co-author. I could not get the Mao 2001 text: cell.com returned 403, and the Yuste-lab mirror returned 404. So whether Mao 2001 already tested coactive-cell counts, or only introduced the reshuffle, is unverified. `detector_history.md` records the same gap ("Mao 2001, which nobody has reached").
- **Severity:** minor (the report's wording is supported by the 2003 text).
- **Fix:** Either add "building on Mao and colleagues (2001)" with a flag, or leave the text and carry the residual below.
- **Verified:** yes for the 2003 text and its reference 12. No for Mao 2001.

**4.** References, the Cecchini entry.
- **Issue:** The title is missing. This is the only entry without one, and "Cecchini G and colleagues, with Kreuz T as last author" is not a citation format. Crossref gives:
  - **Title:** *Cortical propagation tracks functional recovery after stroke*
  - **Authors:** Cecchini G, Scaglione A, Allegra Mascaro AL, Checcucci C, Conti E, Adam I, Fanelli D, Livi R, Pavone FS, Kreuz T.
  - Volume/issue/article number (17(5):e1008963) and the DOI are correct as printed.
- **Severity:** minor.
- **Fix:** Give the full entry: "Cecchini G, Scaglione A, Allegra Mascaro AL, Checcucci C, Conti E, Adam I, Fanelli D, Livi R, Pavone FS, Kreuz T (2021). Cortical propagation tracks functional recovery after stroke. PLoS Comput Biol 17(5):e1008963."
- **Verified:** yes (Crossref).

**5.** References and §3, the CICADA entry.
- **Issue:** No year, version or title, and the only source given for "the Cossart lab's circular-shift null" is software.
  - Zenodo 10.5281/zenodo.10041434 is titled "CICADA stands for Calcium Imaging Complete Automated Data Analysis", version 1.0.3, publication date 2020-07-20. The five creators exactly match the report (Denis, Dard, Quiroli, Cossart, Picardo).
  - Forward trace, published statement: Dard et al. 2022, eLife 11:e78116, doi:10.7554/eLife.78116 (last author Picardo; Cossart second to last). Its Methods, "SCE detection … launched from CICADA", say "an independent circular shift was applied to each cell to obtain 300 surrogate raster plots … 99th percentile".
  - Forward trace, framework paper: Hamon et al. 2026, bioRxiv doi:10.64898/2026.07.03.736318. The DOI resolves. According to the project's literature shelf (in the darkroom's `lit/` folder), it states no SCE null, so it does not replace the software record.
- **Severity:** minor.
- **Fix:** "Denis J, Dard R, Quiroli E, Cossart R, Picardo M (2020). CICADA: Calcium Imaging Complete Automated Data Analysis, v1.0.3 [software]. Zenodo. doi:10.5281/zenodo.10041434". Add Dard et al. 2022 as the published source for the circular-shift form.
- **Verified:** yes. Zenodo API, Crossref, and the Dard 2022 PDF on the literature shelf (Methods read). Hamon 2026: DOI and author list only.

**6.** §9, "the folds share training data, so both p-values are optimistic (Bengio and Grandvalet, 2004)".
- **Issue:** The citation exists and supports the claim. The JMLR abstract says naive estimators "that don't take into account the error correlations due to the overlap between training and test sets … grossly underestimate variance". It is not the origin, though. The root is Dietterich TG (1998), *Approximate statistical tests for comparing supervised classification learning algorithms*, Neural Computation 10(7):1895–1923, doi:10.1162/089976698300017197. The standard correction is Nadeau C, Bengio Y (2003), *Inference for the generalization error*, Machine Learning 52(3):239–281, doi:10.1023/A:1024068626366. Separately, the entry has no URL; JMLR has no DOI.
- **Severity:** minor.
- **Fix:** Cite Dietterich 1998 as the origin, and optionally Nadeau and Bengio 2003. Add https://www.jmlr.org/papers/v5/grandvalet04a.html to the Bengio and Grandvalet entry.
- **Verified:** yes (JMLR page; Crossref for the two suggested papers).

**7.** §3, "is the Deep Sets construction (Zaheer and colleagues, 2017), also used by PointNet (Qi and colleagues, 2017)".
- **Issue:** The metadata for both is correct. The ordering implied by "also used by" is wrong: PointNet was posted first (arXiv 1612.00593, December 2016), and Deep Sets second (1703.06114, March 2017). The shelf's own note says PointNet reached the construction independently. The shape is also older than both:
  - Edwards and Storkey, *Towards a Neural Statistician*, arXiv 1606.02185 (June 2016)
  - Ravanbakhsh, Schneider and Póczos, *Deep Learning with Sets and Point Clouds*, arXiv 1611.04500 (November 2016)
- **Severity:** minor.
- **Fix:** "…the construction formalized as Deep Sets (Zaheer and colleagues, 2017) and reached independently by PointNet (Qi and colleagues, 2017)".
- **Verified:** yes (arXiv API for all four).
- **Side note, outside the artifact:** the shelf index `darkroom/bugarach/lit/DL/README.md` lists the second Deep Sets author as "Kumar". It is Kottur. The report has it right.

**8.** §11, "its matched-merge re-decode is docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/merge_gap.json".
- **Issue:** No branch is given, and the file is not on main or in this worktree. It exists only on `origin/nets/fair-comparison-report`. Every other branch-only path in §11 names its branch.
- **Severity:** minor.
- **Fix:** Add "(branch nets/fair-comparison-report)".
- **Verified:** yes (`git ls-tree` on origin/main, the worktree and all related branches).

**9.** §3 ("chose these values on 96 other bench recordings (seeds 1–96)") and Table 7 (same wording).
- **Issue:** The cited source says goal 1 chose on half of those and held out the rest. `HANDOFF-coded-detectors.md` on opt-every-knob-run says "choose on recordings 1–48, score on 49–96" and "Held out on 48 recordings the search never saw". The point the sentence makes (seeds disjoint from this run's) still holds. The origin of the values themselves is confirmed: both runs' meta.json record `coded_base.source` as "goal 1's every-knob sliding values, WSMIP065, branch opt-every-knob-run @ 6fe09ab".
- **Severity:** minor.
- **Fix:** "…chose these values on bench recordings 1–48 and checked them on 49–96…".
- **Verified:** yes.

**10.** §3, two claims that section 11 does not source.
- **Issue:**
  - "untuned, it tied CoactDetect in an earlier comparison" (tube). The source is `HANDOFF-workstation-tuning.md` on tune-bench-comparison: "It ties CoactDetect untuned". That was on the retired home spec.
  - "which the project says is not yet final" (in the intro). The sources are `docs/goals/README.md` ("set by Tony on 2026-09-17, and not final") and `docs/goals/learned-model-family.md`, "Which models and detectors to keep".
  - The page says its hand-written sections "cite their sources".
- **Severity:** minor.
- **Fix:** Add both to §11's list of sources, and say that the tube tie was on the retired simulator.
- **Verified:** yes.

**11.** §3 and §10, the "30–36%" figure, sourced to `docs/forks.md §14` (tune-bench-comparison).
- **Issue:** The figure is supported: 64% of LoCo's calls kept and 70% of CoactDetect's, "on three real TTX baselines". But forks.md is itself second-hand. It cites `docs/todo/2026-09-07-detector-calls-move-with-the-grid.md`, which is on main and holds the measurement. That todo measured on the `2026-09-03_…STEPS_EXCLUDED_TTX` export, the same export whose pinned-ROI defect §10 discusses.
- **Severity:** minor.
- **Fix:** Cite the todo as the measurement. Consider noting which export it came from.
- **Verified:** yes.

## Checked and clean

**Every reference exists, and its authors, title, venue, year and DOI/arXiv id are correct except where noted above:**
- **Bengio and Grandvalet 2004:** JMLR 5:1089–1105; checked on the JMLR page.
- **Cossart, Aronov and Yuste 2003:** Nature 423:283–288, doi:10.1038/nature01614; checked on Crossref and in the PDF.
- **CICADA:** creators and DOI checked through the Zenodo API.
- **Finn and Johnson 1968:** title and RCA Review 29(3):414–464; checked in the shelf PDF, where page 414 opens the article and the author line reads "H. M. Finn and R. S. Johnson".
- **Kreuz, Mulansky and Bozanic 2015:** J Neurophysiol 113(9):3432–3445, doi:10.1152/jn.00848.2014; checked on Crossref and Europe PMC. This is the right origin for the measure. Its abstract introduces SPIKE-synchronization as "an improved and simplified extension of event synchronization". I stopped the backward trace there.
- **Qi et al. 2017 and Zaheer et al. 2017:** checked through the arXiv API. The author lists are exact, including Kottur and Póczos.
- **Cecchini 2021:** DOI checked; the last author is Kreuz.

**In-text citations and the reference list match one to one.** Every cited work is listed, and every listed work is cited.

**Finn and Johnson's role:** it is the CA-CFAR primary ("CA" is cell-averaging, "CFAR" is constant false-alarm rate). The claim "by the author's account they resemble … without having been derived from it" matches the author's own account recorded in `detector_history.md` on 2026-08-29 ("They blindly reconstructed elements of CFAR, I was totally unaware"). Tony is the project author, not a third party.

**Every internal path exists where the report says it is,** and the content supports the claim it is cited for:
- `docs/detector_history.md` (main): the lineage in §3, and locust as a modified port.
- `docs/todo/2026-09-17-two-bake-off-folds-train-the-same-model.md` (main): the fold defect in the rehearsal (called the "GPU shakedown" there).
- `docs/goals/README.md` (main): baseline only, fast stream first.
- `docs/FOUNDATIONS.md` §9 (main): under TTX (a sodium channel blocker), the fast stream falls to a median 0.46 of baseline and the slow stream rises to 2.50.
- `HANDOFF-workstation-tuning.md` (tune-bench-comparison):
  - the 1.6 margin "derived from binned CoactDetect's ratio"
  - the constants on the corrected export, measured on both machines, with participation at 0.18 against 0.1905
  - the rehearsal's +0.011 and +0.016, corrected on 2026-09-19
- `docs/forks.md` §14 (tune-bench-comparison): the 30–36% figure.
- `docs/learned/tuned_vs_coact/shakedown_home_spec/README.md` (tune-bench-comparison): retired home spec, three knobs, a 240 s context, "nothing should quote it as a comparison".
- `HANDOFF-slow-comodulation-on-the-de-pinned-export.md` (main): decision 3, "`bench.MEASURED_ROLE` still points at the contaminated folder", 0.03% of events.
- `docs/goals/coded-detector-optimization.md` and `HANDOFF-coded-detectors.md` (opt-every-knob-run): α 1e-5, context 120 s, merge 8 s, guard 1 s; the crowded-recording check with events 6 s apart; "an 8 s merge fuses neighbours".
- `docs/GLOSSARY.md`: "promiscuity probe".
- `tools/fair_comparison_evidence.py merge-gap` (nets/fair-comparison-report): the subcommand exists.
- `--replicate` in `tools/tune_learned_vs_coact.py` (replicate-run): the option exists.
- The chorus models are absent from main and present on replicate-run.

**"By the branch history their code differs only in the option that sets the draw":** the two runs' `started.git.commit` values are e8764aa and 7a95e8a. The diff between them touches three files: the tuning tool, its test and the handoff. The one commit in between that changes code is "--replicate R". This matches the claim.

**Private correspondence:** I found no quotation of a third party. The quoted strings in the text are project terms ("coded", "nets", "norm", "chorus", "gain"). There is no personal-communication citation. The Kreuz correspondence of April 2026 that `detector_history.md` records is correctly left out, and a published paper is cited instead. `check_quotes.py --all` in the worktree printed "clear", but it probably scans only tracked files and this report is untracked, so my manual scan is the real check here.

## Residual ⚠ (for the ledger)

- **Mao et al. 2001 is unread.** It is paywalled (403). The binned SCE root is verified one step short of it.
- **Kreuz 2017 and Cecchini 2021 were read only through WebFetch's summarizer.** Before the new citation ships, the passages in finding 1 should be checked against the PDFs. Both are open access.
- **Priority of rate+context, CoactDetect and LoCo.** The report's "designed here" is an authorship claim and is accurate. `detector_history.md` records that four literatures that could hold prior art have never been searched. That residual carries over into this page.
- **"The three statistics are this project's choice" (the chorus pooling).** This is not phrased as a novelty claim. If it is ever read as one:
  - **Searched:** set learning (Deep Sets, PointNet, Neural Statistician, Ravanbakhsh 2016) and graph pooling. Multi-aggregator pooling of mean, max, min and std is in Corso et al. 2020, *Principal Neighbourhood Aggregation*, NeurIPS, arXiv 2004.05718.
  - **Not searched:** multiple-instance-learning or sound-event-detection pooling beyond what is on the shelf, and statistics pooling in speaker embeddings.
  - **Nobody was asked:** I know of no correspondence on it.

Sources:
- [Cecchini et al. 2021, PLoS Comput Biol](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008963)
- [Kreuz et al. 2017, New J Phys](https://iopscience.iop.org/article/10.1088/1367-2630/aa68c3)
- [Cossart, Aronov & Yuste 2003 (Yuste lab PDF)](https://blogs.cuit.columbia.edu/rmy5/files/2017/06/cossart.nature.03.pdf)
- [Cossart 2003, Nature](https://www.nature.com/articles/nature01614)
- [Mao et al. 2001, Neuron (403 to me)](https://www.cell.com/fulltext/S0896-6273(01)00518-9)
- [Bengio & Grandvalet 2004, JMLR](https://www.jmlr.org/papers/v5/grandvalet04a.html)
- Zenodo record 10041434, Crossref, arXiv and Europe PMC APIs (queried directly)
