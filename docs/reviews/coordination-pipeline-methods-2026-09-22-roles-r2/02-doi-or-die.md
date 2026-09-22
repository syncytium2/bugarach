# Role 2 — DOI or Die (round 2, blind pass, verbatim as returned)

GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I also hold SubagentHandback, the channel for this report. I hold no editing tool. Nothing in the repo was modified. The papers I fetched are in `<scratchpad>\mb2r2\`.)

# Role 2, DOI or Die. Round 2, blind pass
Artifact: `docs\methods\coordination_pipeline_methods.md` at commit 464d995.

## Summary
- **Metadata is clean.** All 16 reference-list entries exist. I resolved the 12 DOIs through Crossref and checked the other 4 separately: Zenodo API for CICADA, the shelf PDF for Finn & Johnson, and the arXiv abstract pages for Adam and Deep Sets. Authors, year, title, venue, volume, issue and pages all match, apart from the CICADA title in F10.
- **In-text and list are consistent.** Every in-text citation is in the list and every list entry is cited.
- **The problems are in what the text says the sources say, and in who it credits.** Six attribution claims need changing: F1, F2, F3, F4, F5, F7.

## Findings
Format: location · issue · severity · suggested fix · verified against a source.

**F1. L177–178: SPIKE-synch, the sentence crediting the measure's authors with a detection step of the same form (Cecchini et al., 2021, plus the personal-communication citation). · High**
- **Issue.** This overstates the source. Cecchini 2021, S1 Appendix "Event detection", which I read, detects events this way:
  - the adaptive coincidence window capped at 2.5 s;
  - one threshold, C_thr = 0.75, on each spike's SPIKE-synchronization;
  - event boundaries taken from jumps in the SPIKE-Order profile;
  - a maximum gap of 0.15 s between consecutive spikes;
  - a first filter keeping only spikes within 1 s of a peak in the mean calcium trace.
- It has no second (sustain) level, no hysteresis scan of the coincidence profile, and no minimum-events rule.
- The repo's own paraphrase of the April correspondence (`docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`) says the same: a profile threshold, **and** a condition on the mean calcium signal, plus a maximum gap. That is two of our components out of three, plus one this pipeline cannot apply.
- **Fix.** Say that the measure's authors have detected events with a threshold on the same coincidence measure and a maximum gap between an event's spikes, together with a condition on the mean fluorescence signal that an event-based pipeline cannot apply; cite Cecchini et al. (2021) and the personal communication.
- **Verified:** yes (Cecchini S1 Appendix, `pcbi.1008963.s008`).

**F2. L173: the coincidence window "is capped at a maximum (Kreuz et al., 2017)" · Medium (origin)**
- **Issue.** The cap starts earlier. Quian Quiroga, Kreuz & Grassberger 2002, just after Eq. 4, already give the capped window, τ′ᵢⱼ = min{τ, τᵢⱼ}, as an option.
- Kreuz 2017 NJP (read, §2.1) brings it back as τ_max for SPIKE-synchronization, and Cecchini 2021 uses it (2.5 s).
- **Fix.** "…and is capped at a maximum, an option noted with the adaptive window itself (Quian Quiroga et al., 2002) and used with SPIKE-synchronization by Kreuz et al. (2017)."
- **Verified:** yes, against the arXiv preprint nlin/0202065v1, not the PRE version of record (paywalled). The trace stops there.
- ⚠ Not verified: the climate event-synchronization literature (Malik et al. 2010, cited by Kreuz 2017; Boers et al. 2014) may also use a τ_max. The Malik PDF text came out garbled and I did not settle it.

**F3. L161–162: the description of Cossart, Aronov & Yuste 2003 · Medium**
- **Issue 1, wording.** "thresholded each movie's largest single-frame count at P < 0.05" reads as if the observed movie's maximum was tested. In the Methods paragraph the repo carries (the todo `2026-08-24-the-methods-are-not-ours…`, lines 43–48), the threshold is the coactive-cell count exceeded in a single frame in only 5% of 1,000 interval-reshuffled surrogate histograms.
  - **Fix:** "who reshuffled each cell's inter-event intervals (1,000 surrogates per movie) and called frames whose coactive-cell count exceeded the count reached in only 5% of surrogates (P < 0.05)".
- **Issue 2, where the trace stops.** 2003 credits the technique to Mao, Hamzei-Sichani, Aronov, Froemke & Yuste 2001, *Neuron* 32(5):883–898, doi:10.1016/S0896-6273(01)00518-9 (Crossref-verified). The artifact does not cite Mao.
  - I could not get Mao: cell.com returns 403, and ScienceDirect is blocked by the UMich network (certificate intercept).
  - 2003 is not on the shelf either, and it is paywalled (Unpaywall: not open access). The 2003 wording is therefore second-hand, carried from interface2's session.
- **Stopped at:** one step short at 2003, two steps short of the root at Mao 2001.
- **Fix:** add "(technique credited there to Mao et al., 2001)", or say plainly that 2003 is the root reached.
- **Verified:** no, second-hand only.
- Related, low: per `docs/detector_history.md` (2026-08-29 header), the author says binned SCE was "based on ideas in CICADA" before the port. The text's "descends from 2003" skips the route it actually took. That rests on the author's memory and no source.

**F4. L331–332: the Nadeau–Bengio correction "carries over to k-fold cross-validation only as a heuristic (Bouckaert and Frank, 2004)" · Medium (misattribution)**
- **Issue.** Bouckaert & Frank (read, §3.3) do not say that. They apply the same correction to repeated k-fold because "cross-validation is a special case of random subsampling". They use "heuristic" only once, in general, for the corrected t-tests ("Several heuristic versions of the t-test…[5,6]").
- Nadeau & Bengio, as quoted in B&F, expect "normal usage" with n₁ 5–10 times larger than n₂. Here n₁/n₂ = 3 for the coded detectors, and it is below 1 for the learned refits (10 recordings trained, 24 tested).
- **Fix.** "…was derived for random train/test splits; Bouckaert and Frank (2004) apply it to k-fold cross-validation by treating it as a special case of random subsampling, and it assumes training sets several times larger than test sets (Nadeau and Bengio, 2003), which holds for neither ratio here."
- **Verified:** yes (Waikato PDF).
- **Boundary note, not mine to judge:** `docs/MILESTONES.md` has an open row, "two bake-off folds train the same model". It undercuts the fold independence this correction assumes. That goes to the statistics role.

**F5. L168–170 and L163–164: locust and CICADA · Medium (origin and forward trace)**
- **(a) The CICADA algorithm has a paper; cite it for locust.** Dard et al. 2022 (eLife, "SCE detection", read) describe CICADA's "SCE description" analysis:
  - an independent circular shift per cell, 300 surrogates;
  - a threshold at the 99th percentile;
  - peaks at least 5 frames apart.
  - That is the algorithm locust ports. Bocchio 2020 (read) uses the same form: 1,000 circular-shift surrogates, 99th percentile, peaks ≥ 1 s apart.
  - The text cites both only under binned SCE, whose rule (10 s bins, pooled 98th percentile, no peak spacing) is further from them. The repo's attribution ledger already lists "Denis 2020 (Zenodo); Dard 2022" for locust.
  - **Fix:** "…a partial, modified port of CICADA (Denis et al., 2020; algorithm as described in Dard et al., 2022)". Keep Bocchio and Dard under binned SCE only for "the circular-shift form".
- **(b) Forward trace: the authors' own later paper is uncited.** Hamon M, Lebert J, Denis J, Filippi C, Renard A, Bech P, Pulin M, Bisi A, Molinuevo Gomez D, Priestley JB, Crochet S, Petersen CCH, Cossart R, Picardo MA, Dard RF (2026). *CICADA: A unified framework for NWB-based neurophysiological data analysis.* bioRxiv, doi:10.64898/2026.07.03.736318.
  - Crossref-verified. On the shelf as `coordination/hamon_2026_cicada_preprint.pdf`.
  - It describes a refactored, modular CICADA (cicada-nwb, cicada-analysis, cicada-gui).
  - It cites the original tool as "Cossart Lab / CICADA, 2019, GitLab".
  - **Lab attribution:** its last and corresponding author, Dard, is at EPFL (Laboratory of Sensory Processing, Petersen). Cossart and Picardo (INMED, Marseille) are co-authors. So "the Cossart lab's CICADA", the GLOSSARY wording, describes the 2019–2020 tool and not the 2026 framework.
  - **Fix:** cite the Zenodo record for the version that was ported. Optionally add Hamon 2026 as the framework paper, stating that the port predates the refactor.
- **Verified:** yes for all of F5.
- **Lab check for Bocchio and Dard.** Bocchio 2020: last author Cossart, INMED. Dard 2022: co-corresponding Cossart and Picardo, INMED. "Cossart laboratory" is acceptable. "INMED (Cossart and Picardo)" would be more exact for Dard.

**F6. L140–158: CoactDetect and LoCo have no attribution · Medium**
- **Issue.** rate+context gets a lineage sentence: designed independently, with the structure of cell-averaging CFAR (constant false-alarm rate). CoactDetect and LoCo get none.
  - The repo records that all three were designed here and converge on CFAR (`detector_history.md`). CoactDetect's "context" and "guard" are CFAR's reference and guard cells.
  - The attribution ledger lists "Grün 2002a,b; Amarasingham 2012" as the family for excess coincidence against a rate-preserving null.
- **Metadata, Crossref-verified:**
  - Grün S, Diesmann M, Aertsen A (2002) Neural Comput 14(1):43–80, doi:10.1162/089976602753284455.
  - Same authors (2002) Neural Comput 14(1):81–119, doi:10.1162/089976602753284464.
  - Amarasingham A, Harrison MT, Hatsopoulos NG, Geman S (2012) J Neurophysiol 107(2):517–531, doi:10.1152/jn.00633.2011.
- **Fix.** Add one sentence stating that all three were designed in this laboratory, and give their CFAR and Unitary-Events correspondences. **But** the README marks Grün and Amarasingham ° (not read here). They must be read before any content claim is attached to them. `surrogates/amarasingham_2012_jitter_method.pdf` is on the shelf, and so is a Grün 2010 chapter.
- **Verified:** metadata yes, content no.

**F7. L183: cSPIKE is named without a citation · Low**
- **Fix.** Cite Satuvuori et al. 2017 (already in the list), which announces cSPIKE and which Cecchini 2021 cites as "the cSPIKE-implementation". Add the URL and the version used.
- **Verified:** yes (Satuvuori, PMC5508708).
- The MRTS claim at L174 checks out too: Satuvuori 2017 introduces the minimum relevant time scale as threshold T for A-SPIKE-synchronization. This had been marked "nobody here has read it"; it is now read.

**F8. L21 (MATLAB `findpeaks`), L180–185 (MATLAB, Python, PySpike): no releases or versions · Low**
- **Fix.** Give the MATLAB release plus Signal Processing Toolbox version, The MathWorks, Natick MA; the PySpike version the cross-check used (PyPI has 0.1 to 0.9.0); cSPIKE's version; and the Python and deep-learning framework versions for the learned detectors (none is named).
- The "no effect since version 0.8.0" claim is the repo's own finding. Citing it as upstream PR mariomulansky/PySpike#89 (open, 2026-09-01; verified with gh) would make it checkable.
- **Verified:** partly.

**F9. L178: the personal communication · Low**
- **Issue.** It is dated by month and year only; CLAUDE.md gives the full date, 2026-04-23.
- **Fix.** Give the full date. Keep it a citation, never a quote: the repo is public and the rule applies. Many journals also want written permission from the person cited (see Q1).
- **Verified:** date from repo records only.

**F10. L406–407: CICADA reference details · Low**
- The Zenodo record title is "CICADA stands for Calcium Imaging Complete Automated Data Analysis". It is version 1.0.3, dated 2020-07-20. Creators: Denis, Dard, Quiroli, Cossart, Picardo, which matches the list.
- doi:10.5281/zenodo.10041434 is the version DOI. The concept DOI is 10.5281/zenodo.10041433. Keep the version DOI if 1.0.3 is what was ported (see Q2).
- Upstream spells the expansion two ways: the 2026 preprint says "Completely Automated".
- **Fix:** reproduce the record title, or keep the parenthetical form knowingly.
- **Verified:** yes (Zenodo API).

**F11. L147–148: Finn & Johnson 1968 · Low (where the trace stops)**
- Metadata is right. From the shelf PDF: RCA Review, September 1968, pp. 414–464 (51 pages). Issue 3 is inferred from the September issue date; no issue number was read.
- The paper cites Finn's own earlier work: Proc. Nat. Electronics Conf. XXII:562, 1966; Allerton 1967; RCA Review Dec. 1967, pp. 653–678.
- Tony ruled the CFAR priority question closed (2026-08-24), so this is a record, not a request.
- **Stopped at:** 1968, read; Finn 1966 and 1967 not read.
- **Verified:** yes.

**F12. L274–277 and L281: learned-detector components · Low / info**
- Deep Sets citation checks out (shelf PDF). Zaheer et al. themselves say "the idea of pooling a function across set-members is not new". PointNet is concurrent: Qi CR, Su H, Mo K, Guibas LJ, CVPR 2017, pp. 77–85, doi:10.1109/CVPR.2017.16. Adding it is optional.
- Adam: Kingma & Ba, ICLR 2015, arXiv:1412.6980. Verified.
- The dilated convolutions, the difference-of-Gaussians filters and the hysteresis scan have no citations. That is optional under the house rule; if hysteresis is cited, Canny 1986, IEEE TPAMI PAMI-8(6):679–698, doi:10.1109/TPAMI.1986.4767851 has verified metadata, but I did not establish it as the origin of hysteresis thresholding.

**Verified clean, no change needed:**
- NoRMCorre (Pnevmatikakis & Giovannucci 2017, JNM 291:83–94).
- Kreuz et al. 2015 as the source of SPIKE-synchronization. Checked through Kreuz 2017 [27] and Satuvuori 2017; the paper itself was not read (PMC full text not retrievable).
- Quian Quiroga 2002 as the origin of the adaptive window (Eq. 4, read).
- Mulansky & Kreuz 2016.
- Nadeau & Bengio 2003 metadata, and the √(3/7) and ≈0.31 factors (recomputed).
- Bocchio 2020, Dard 2022 and Cecchini 2021 metadata and full author lists.

## Where each trace stopped
- **Binned SCE:** at Cossart 2003, which is paywalled, not shelved, and known only from a second-hand quote. Mao 2001 was not reached (403 and network block).
- **CA-CFAR:** at Finn & Johnson 1968 (read). Finn 1966 and 1967 not read.
- **Adaptive window and cap:** at Quian Quiroga 2002 (arXiv v1).
- **SPIKE-synch detection:**
  - Backward: Cecchini 2021 plus its S1 and S2 appendices (read).
  - Forward: Kreuz et al. 2022, Mariani et al. 2025 (JNM 416:110378, doi:10.1016/j.jneumeth.2025.110378, arXiv 2410.15018, read) and Kreuz 2025 (Biol Cybern, in press, arXiv 2510.07140, read).
  - None of the later papers has a detector beyond a threshold and maximum-gap preprocessing.
  - Kreuz's publication page gives Mariani's title as "…with event overlap". Crossref has "…with overlapping global events".
- **CICADA:** backward to Zenodo v1.0.3, forward to Hamon 2026. Ratsifandrihamanana et al. 2023 (STAR Protocols) was checked and does not describe SCE detection.
- **Unitary Events and jitter family:** metadata only. Not read.

## Fields searched, and what was not
- **Searched:** the SPIKE-synchronization literature (the Kreuz lab, backward and forward), the Cossart and INMED CICADA literature, radar CFAR (shelf), and ML model-comparison statistics (Nadeau–Bengio, Bouckaert–Frank).
- **Not searched (⚠):**
  - climate event synchronization, for the τ_max antecedent;
  - genomics peak calling, seismological STA/LTA (short-term/long-term average), adaptive image thresholding and changepoint detection, for the three in-house detectors, as the README already records;
  - the SCE literature before 2001.

## Questions for the humans
1. **Kreuz.** Has he agreed to be cited as a personal communication? Is the April reply the relevant one? Does anything he wrote describe a two-level (hysteresis) scan, or only a threshold plus a maximum gap, which is what the repo's paraphrase says?
2. **CICADA.** Which CICADA version or commit did interface2 port from? Is it Zenodo v1.0.3? Has anyone at INMED, or Dard at EPFL, been told about the port and the rename to locust? "Nobody was asked" is a residual ⚠.
3. **Missing PDFs.** Can Tony fetch Cossart et al. 2003 (Nature) and Mao et al. 2001 (Neuron) for `lit/coordination/`? That would close F3 first-hand.
4. **Versions.** Which MATLAB release did the producer's `findpeaks` run on, and which PySpike and cSPIKE versions did the parity checks use?
5. **CoactDetect and LoCo lineage.** Does Tony want the Unitary-Events and jitter lineage cited for these two? If so, someone must read Grün 2002 and Amarasingham 2012 first.

Sources used:
- [Zenodo CICADA record](https://zenodo.org/records/10041434)
- [Cossart Lab CICADA on GitLab](https://gitlab.com/cossartlab/cicada)
- [Kreuz journal-article list](https://www.thomaskreuz.org/publications/journal-articles)
- [Mariani et al., arXiv 2410.15018](https://arxiv.org/abs/2410.15018)
- [Kreuz 2025 review, arXiv 2510.07140](https://arxiv.org/pdf/2510.07140)
- [Bouckaert & Frank 2004 PDF](https://ml.cms.waikato.ac.nz/publications/2004/bouckaert-frank.pdf)
- [Adam, arXiv 1412.6980](https://arxiv.org/abs/1412.6980)
- [Malik et al. 2010, NPG](https://npg.copernicus.org/articles/17/371/2010/)
- Crossref API for every DOI listed
- Europe PMC: PMC5508708 (Satuvuori 2017) and PMC10701450 (Ratsifandrihamanana 2023)
- PLoS CB supplements for Cecchini 2021 (s008, s009)
- IOP PDF of Kreuz 2017
- arXiv nlin/0202065 (Quian Quiroga 2002)

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004). In F1, F9 and Q1 the quoted citation strings for the personal communication were paraphrased (tools/check_quotes.py); the substance of each row is unchanged.*
