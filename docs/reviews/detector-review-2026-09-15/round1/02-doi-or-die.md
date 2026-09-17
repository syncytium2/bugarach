> **Public copy.** Lines that concern real treatment recordings are removed (5 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2: citations and references ("DOI or Die") for `detector_review.html`

**Result:** 2 blocking, 5 major and 9 minor findings. I edited nothing and wrote only to `...\scratchpad\mb_scratch\role02\`.

Almost every error is one the project's own record had already fixed. The page drops those corrections.

## Findings

| # | location | issue | severity | suggested fix | verified against a source? |
|---|---|---|---|---|---|
| 1 | §12, CoactDetect/LoCo paragraph | **"Resampling by shifting follows Amarasingham et al. 2012" credits the wrong paper.** That paper is about jitter resampling. I extracted its full text from the shelf copy and the word "shift" never appears. Whole-spike-train random shifting is credited to Pipa et al. 2008 by Stella et al. 2022 (read in full on the shelf). The per-cell circular shift used for calcium-event thresholds is in Bocchio 2020 and Dard 2022 (both Methods read). | **blocking** | "Shift surrogates: Pipa, Wheeler, Singer & Nikolić 2008, *J Comput Neurosci* 25:64–88, doi:10.1007/s10827-007-0065-3. In calcium imaging: Bocchio et al. 2020, *Nat Commun* 11:4559; Dard et al. 2022, *eLife* 11:e78116." Drop Amarasingham, or cite it only as related conditional resampling. | yes |
| 2 | §12, SPIKE-synch: "The calling rule on top is ours." | **A novelty claim the project's own record withdrew.** `detector_history.md` (2026-08-29 header, "Tier 2" section) says the rule is not novel and is ordinary hysteresis thresholding. The 2026-08-31 site review removed the same claim. The measure's authors use SPIKE-Synchronization to pick out events in calcium imaging: Cecchini et al. 2021 keep only spikes coincident with at least 3/4 of the other trains, with one-spike-per-pixel matching. Kreuz's April 2026 email describes the rest of their rule; the Kreuz todo has it in paraphrase. | **blocking** | "The calling rule was written here. It is a standard hysteresis threshold, and the measure's authors use comparable event rules on the same profile (Cecchini et al. 2021, *PLoS Comput Biol* 17:e1008963; T. Kreuz, personal communication, 2026-04-23)." Cite, don't quote. | partly: Cecchini read through a summarising fetch of the open-access HTML, not the PDF |
| 3 | §12, binned SCE: "follows the rule in the Methods of Cossart 2003, which reshuffled intervals where this code shifts" | **The page names one divergence, but the threshold rule itself also differs.** I read the 2003 primary (PDF hosted by the Yuste lab). Its threshold is *"the number of coactive cells exceeded in a single frame in only 5% of these histograms"*: a maximum per surrogate at P<0.05, per 0.9–1.6 s frame, 1,000 reshufflings, with manual rejection. binned SCE takes the 99th percentile pooled over all bins, with 10 s bins and 200 shifts. The pooled 99th-percentile circular-shift form is Dard 2022 (CICADA; 300 shifts, 99th percentile). That fits the project's record that binned SCE was "based on ideas in CICADA". The 2003 paper also credits the reshuffling to **Mao et al. 2001** (its reference 12), which the page leaves out. The 2026-08-31 site review fixed that exact omission. | **major** | "binned SCE uses the circular-shift, pooled-percentile threshold used with CICADA (Dard et al. 2022; Bocchio et al. 2020). The surrogate-threshold idea goes back to Mao et al. 2001, *Neuron* 32:883–898, and was applied by Cossart, Aronov & Yuste 2003 with interval reshuffling and a per-surrogate maximum at P<0.05." In §4.4, "two decades" becomes "about 25 years". | yes (Cossart 2003 full text; Dard and Bocchio Methods) |
| 4 | §12, last bullet: "All six … were first written in MATLAB in the same lab" | **False for locust.** It was first written in Python by the Cossart lab. interface2's MATLAB version is a transliteration of it (`detector_history.md` §6.3). For SPIKE-synch, the Python measure is checked against cSPIKE, the Kreuz group's code (docstring of `tests/test_webapp_sync_detect_parity.py`), not against code from "the same lab". locust's 1e-9 match is against interface2's transliteration; nothing has ever been compared with CICADA. Placed next to the CICADA credit, the sentence reads as validation against CICADA. The tolerance figures themselves are role 1's to check. | **major** | "Five were first written in MATLAB by the same author. locust's MATLAB version was a transliteration of CICADA. Each Python version matches its MATLAB predecessor to 1e-9; no output has been compared against CICADA itself." | yes (project record, test files) |
| 5 | §4.5 and §10: "Close to a published, widely used tool" | **Overstates CICADA.** It has no method paper (shelf README). The framework paper, Hamon et al. 2026 (bioRxiv 10.64898/2026.07.03.736318), is a preprint, and its text states no SCE rule. The GitLab repo has 7 stars and 1 fork. Its listed uses are Cossart-lab and collaborator papers. §6.3 of the history says locust stands "near, not for" CICADA, and interface2 had shelved the upstream function for over-detecting on this preparation. | **major** | "Adapted from openly released Cossart-lab software used in that lab's published analyses (e.g., Dard et al. 2022)." | yes |
| 6 | §5 and §12: "The learned detectors, the simulator, and the tuning procedure were built in this project" | **No prior art for outside reviewers, and the simulator is a port.** Learned event detectors are an established genre: DOSED (Chambon et al. 2019, *J Neurosci Methods* 321:64–78), cnn-ripple (Navas-Olive et al. 2022, *eLife* 11:e77772), SEED (Tapia-Rivas et al. 2024, *Sci Rep*; DOI not resolved). Simulated benchmarks with planted ground truth exist for calcium imaging (Mölter, Avitan & Goodhill 2018, *BMC Biol* 16:143). The simulator and scorer were first written in MATLAB in interface2 (`generate_synth_coord.m`, `score_coord_detection.m`; todo 2026-08-12). The 2026-08-31 site review also named SpindleNet and DeepWonder. | **major** | "…built by this project's author (simulator and scoring first in MATLAB), on established practice: learned event detectors (DOSED, cnn-ripple, SEED) and planted-ground-truth benchmarks (Mölter et al. 2018)." | yes (shelf first pages, Crossref); SpindleNet and DeepWonder not re-checked |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 8 | §12, Grün 2002 | **Two papers merged under one title.** They are "…: I. Detection and significance", 14(1):43–80, doi:10.1162/089976602753284455, and "…: II. Nonstationary data", 14(1):81–119, doi:10.1162/089976602753284464. Part II introduces moving-window UE, the closest neuroscience precedent for the rolling local null in CoactDetect and LoCo, and the page could say so. The README marks both ° (not read here). | minor | Give both titles and DOIs. | abstracts only |
| 9 | §12, SPIKE-synch | **Root omitted.** The adaptive coincidence window (the "smaller half-gap") comes from event synchronization. Kreuz et al. 2022 say it was "originally introduced for the bivariate measure event synchronization". | minor | Add Quian Quiroga, Kreuz & Grassberger 2002, *Phys Rev E* 66:041904. | yes (arXiv full text) |
| 10 | §12, CICADA: "Zenodo, doi:…10041434, MIT license" | **License attached to the wrong object.** The Zenodo record is CC-BY-4.0. The GitLab source is MIT. The rest of the metadata checks out: authors Denis, Dard, Quiroli, Cossart, Picardo; v1.0.3; 2020-07-20. "Cossart lab" is backed by the GitLab namespace and the copyright notice. | minor | "…Zenodo doi:10.5281/zenodo.10041434; source gitlab.com/cossartlab/cicada, MIT." | yes |
| 11 | §12, all references | **Only CICADA has a DOI, and Hansen & Sawyers and Rohling have no titles.** Everything else resolves in Crossref: Kreuz 2015 10.1152/jn.00848.2014; PySpike 10.1016/j.softx.2016.07.006; Cossart 2003 10.1038/nature01614; Malvache 2016 10.1126/science.aaf3319; Hansen & Sawyers 10.1109/TAES.1980.308885; Rohling 10.1109/TAES.1983.309350; Amarasingham 10.1152/jn.00633.2011; Mao 2001 10.1016/S0896-6273(01)00518-9. Finn & Johnson's RCA Review details match the shelf PDF. | minor | Add DOIs and titles. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 13 | §1: KNDy description | The acronym is never expanded and the brain region is never named. The description itself is consistent with Lehman, Coolen & Goodman 2010, *Endocrinology* 151:3479–3489 (arcuate nucleus of the hypothalamus; controls GnRH secretion). | minor | "KNDy (kisspeptin/neurokinin B/dynorphin) neurons of the hypothalamic arcuate nucleus (Lehman et al. 2010)". | abstract |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 15 | §4.2 and §4.3 weaknesses | Published analyses exist for three stated weaknesses. Self-masking and mutual masking: Finn & Johnson 1968; Gandhi & Kassam 1988. Events split across bin edges: the multiple-shift method, Grün et al. 1999, *J Neurosci Methods* 94:67–79. | minor | Optional citations. | yes (Crossref, Grün 2010 chapter) |
| 16 | §12, rate+context | Neuroscience lineage not searched: thresholding the pooled rate or PSTH (Kreuz's email suggests Mainen & Sejnowski 1995, hedged; unread). The body of Cotterill 2016 on the shelf is also unread. | minor (⚠ residual) | Leave a note or search. | no |

**Checked and fine:**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Finn & Johnson, Rohling, Hansen & Sawyers and Malvache metadata match the shelf PDFs.
- "Where that rule began has not been established" (greatest-of) matches history §4.1.
- Cossart 2003 is correctly left without a lab label; it is from the Yuste lab at Columbia, confirmed in the PDF.

## Where I stopped, and why
- **binned SCE root:** stopped one step short at Mao 2001. cell.com returned 403 and I found no open copy. An earlier review notes that Abeles & Gerstein 1988 may sit behind it; not checked.
- **Shift surrogates:** stopped at Pipa 2008, which I only searched with grep, not read. Earlier uses are not traced.
- **Unitary Events:** abstracts only. Earlier roots (Grün 1996 thesis, Riehle 1997) not traced.
- **SPIKY 2015:** metadata only. The claim that it introduced SPIKE-Synchronization rests on Kreuz 2022's own citation.
- **Kreuz 2022:** the arXiv text gets its spikes from threshold crossings and defers event identification to its refs [10, 11]. So `detector_history.md:169` would be better supported by citing Cecchini 2021 than Kreuz 2022. That is a finding about the internal record, not about this page.

## Forward traces
- **CICADA authors:** Hamon 2026 preprint, Dard 2022, Leprince 2023/2026.
- **Kreuz group:** Cecchini 2021, Kreuz 2022, a 2025 *J Neurosci Methods* follow-up on overlapping events, and a 2026 *Biological Cybernetics* review. The last two I found in search and did not read; either could contain further event rules.
- **Grün group:** Stella 2022.

## Literatures searched and not searched
- **Searched:**
  - radar CFAR (shelf primaries)
  - spike-train surrogates and Unitary Events (surrogates shelf, PubMed)
  - calcium-imaging SCE (Cossart 2003, Dard, Bocchio, Malvache, CICADA source and Zenodo)
  - spike synchrony (Kreuz 2022 full text, Cecchini 2021, Crossref)
  - learned event detection (shelf first pages)
  - neuroendocrine background (Europe PMC abstracts)
- **Not searched (⚠ residual):**
  - ecology's torus-translation and toroidal-shift tests, and geoscience surrogate data (both plausible roots for circular-shift surrogates)
  - seismological STA/LTA, genomics peak calling, adaptive image thresholding, changepoint detection
  - MEA burst detection
  - injection-recovery practice in physics
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Correspondence (I cannot ask anyone directly, so these go to the main thread)
- **Known:** Kreuz to Tony, 2026-04-23. It supports finding 2, and must be cited, not quoted. His 2026-09-02 clearance covers only the PySpike PR.
- **⚠ Nobody was asked:** no correspondence with the Cossart lab (Picardo or Dard) is recorded. That is the cheapest check on findings 5 and 7. None with the Yuste lab about Mao 2001.
- **Question for Tony:** has anyone written to CICADA's authors about the port?

## Fetched but not shelved
The main thread should shelve these; Cossart 2003 is cited as a root and was missing from the shelf. All are in `...\scratchpad\mb_scratch\role02\`:
- `cossart2003.pdf` (Yuste-lab copy)
- `kreuz_2022_latency.pdf` (arXiv 2205.09855)
- `sce_desc.py` (CICADA SCE plugin source)

Sources:
- [Zenodo 10041434 (CICADA)](https://zenodo.org/records/10041434)
- [Cossart 2003 PDF (Yuste lab)](https://blogs.cuit.columbia.edu/rmy5/files/2017/06/cossart.nature.03.pdf)
- [Cecchini et al. 2021](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008963)
- [Kreuz et al. 2022, arXiv](https://arxiv.org/abs/2205.09855)
- [Mao et al. 2001, PubMed](https://pubmed.ncbi.nlm.nih.gov/11738033/)
- [Grün 2002, PubMed search](https://pubmed.ncbi.nlm.nih.gov/?term=Gr%C3%BCn+Diesmann+Aertsen+2002+unitary+events+Neural+Computation)
- [Kreuz 2022, JNM vol. 381](https://www.sciencedirect.com/journal/journal-of-neuroscience-methods/vol/381/suppl/C)
- [CICADA GitLab](https://gitlab.com/cossartlab/cicada)
- Crossref API and Europe PMC API, for the DOIs and abstracts above
