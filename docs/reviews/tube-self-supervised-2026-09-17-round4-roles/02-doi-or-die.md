GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)

The missing tools didn't limit the check. I did the same searches through Bash.

# DOI or Die: blind review of `<worktree>/docs/learned/tube_self_supervised/README.md` at f2278da

**Bottom line:** all 29 references exist, and none of the bibliographic data were made up. Every volume, page range and DOI I resolved matches Crossref, DataCite or a scan of the paper. The problems are about who gets credit. The report stops tracing too early in two lineages, gets one implementation wrong, and leaves out the closest prior art for its training objective, even though that prior art is on the project's own shelf.

## Findings

| Location | Issue | Severity | Suggested fix | Verified against a source? |
|---|---|---|---|---|
| *Other labs' detectors in Figure 3*, sentence on Cecchini et al. 2021 | **The report credits the wrong paper for the Kreuz group's event detection.** Cecchini 2021 does filter by SPIKE-synchronization (it drops spikes not matched in at least three quarters of the other trains) and does threshold the mean calcium signal (Fig. 2C). But it credits the event framework to its ref. [23], **Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J Phys* 19:043028, doi:10.1088/1367-2630/aa68c3**. That 2017 paper already sets a threshold on the SPIKE-synchronization profile to keep only global events (C_thr = 0.7). It did so on fast calcium imaging of **acute CA3 hippocampal slices from juvenile mice** (data from the Bonn epileptology department, Beck lab), which is much closer to this lab's preparation than Cecchini's awake wide-field cortex. In Cecchini, the "spikes" are threshold crossings of wide-field pixels, not cells. The last author of both papers is Kreuz (CNR Institute for Complex Systems, Florence), so "Kreuz group" is correct for both. | high | Cite Kreuz et al. 2017 as the origin of thresholding the SPIKE-synchronization profile to isolate events, noting it was on hippocampal-slice calcium imaging. Keep Cecchini 2021 for the added mean-signal threshold, and say its units are pixels. Add Kreuz 2017 to the reference list. | yes: both papers are open access and I read them (Cecchini §Results and Fig. 2 caption; Kreuz 2017 §2 and §3.2) |
| *The published lineage*, "The trail stops at Pipa, Riehle & Grün 2007" | **The trail has further leads, and one is in a paper already on the shelf.** Pipa et al. 2008 cites NeuroXidence as "(Pipa 2003; Pipa et al. 2006)". The 2006 entry is the 2007 Neurocomputing paper, still in press (same DOI). "Pipa 2003" is **German patent application DE10008251A1** (inventor Gordon Pipa, filed 2000-02-23, published 2001-08-30). There is also **Pipa & Grün 2003, *Neurocomputing* 52–54:31–37, "Non-parametric significance estimation of joint-spike events by shuffling and resampling"** (doi:10.1016/S0925-2312(02)00823-8), cited by both Pipa 2008 and Stella 2022. The report names neither. Stella 2022 credits the invention to Pipa et al. 2008 ("introduced dithering of the entire spike train"). | medium | Say where the trail really stops: "verified to Pipa, Riehle & Grün 2007, unread; earlier leads Pipa & Grün 2003 (closed access, unread) and patent DE10008251A1 (seen only through an automated summary of its Google Patents page, which describes a jitter-window coincidence detector, not a surrogate)". Add Stella's credit to Pipa 2008. | partly: citations yes (shelf PDFs, Crossref); the patent only through an automated summary; Pipa & Grün 2003 not read (closed, no abstract available) |
| *Other labs' detectors*, "as implemented in PySpike (Mulansky & Kreuz 2016)" | **Wrong implementation.** `src/bugarach/detectors/sync.py` is a native port of interface2's **cSPIKE** stack (`AdaptiveSPIKESynchroProfile` → `SpikyDetect3`). PySpike is only a cross-check (it is imported in `tools/synfire_scan.py`, not in the detector). The τ-cap is also this project's own, per `docs/detector_history.md` Tier 2. | medium | "wraps a τ-capped SPIKE-synchronization profile (Kreuz, Mulansky & Bozanic 2015), ported from cSPIKE and checked against PySpike (Mulansky & Kreuz 2016)". | yes: the code and detector_history |
| *Learning against a surrogate or a constraint*; *What is this project's own*; the "literature search" bullet | **Close prior art on the shelf is missing.** The report says contrastive learning was not covered "beyond the two papers named below". But `<darkroom>/lit/ml/README.md` lists roughly 20 self-supervised-learning papers as "read 2026-09-12". Two of them are the nearest precedents for training a network to score real data above a temporally broken copy:<br>• **Hyvärinen & Morioka 2017** (AISTATS, PMLR 54): logistic regression trained to tell real windows from time-permuted ones. It extends noise-contrastive estimation, the same lineage the report cites.<br>• **Chau et al. 2025** (Population Transformer, ICLR 2025): a channel-wise objective that detects channels whose activity was swapped for activity from a random time.<br>Neither is cited. | medium | Cite both as the nearest self-supervised precedents, and say how rigid shift differs (it shifts each ROI's own train). Restate the coverage line to reflect what the shelf holds. | yes: shelf PDFs and README entries |
| *Learning against a surrogate*: C2ST, NCE and Neyman–Pearson credits | The report cites later restatements as if they were the origins:<br>• Lopez-Paz & Oquab 2017 say the reduction of two-sample testing to classification "was introduced in (Friedman, 2003)" (SLAC report; OSTI record doi:10.2172/826696).<br>• Gutmann & Hyvärinen 2012, footnote 1: preliminary versions appeared at **AISTATS 2010**.<br>• Scott & Nowak 2005 say NP classification theory was "apparently first studied by **Cannon, Howse, Hush & Scovel**" (LANL LA-UR 02-2951, 2002). | low–medium | Cite the root beside each modern restatement: Friedman 2003; Gutmann & Hyvärinen 2010; Cannon et al. 2002. | yes for what each paper credits (texts read); the three root works themselves not fetched |
| *Other labs' detectors*, "(Kreuz, personal communication, April 2026)" | Dated to the month only. The rule is a checkable, dated citation. The report paraphrases and does not quote, which is correct for a public repo. | low | Give the full date. | no: the correspondence is off-limits in this blind review |
| *The published lineage*, "the forms … Stella et al. prefer both wrap" | Stella 2022 never says TR-SHIFT wraps. The wrap is in Elephant 1.2.1's `_trial_shifting` (`np.remainder` over the trial). For Louis et al. the wrap is in their text (p. 367: "we actually roll the spike train"). | low | Attribute Stella's wrap to Elephant's `trial_shifting` implementation. | yes: Elephant v1.2.1 source from GitHub; Stella full text |
| *The published lineage*, "Harrison & Geman 2009 call closely related" | They say this only for the limiting case R = ∞, "the entire spike train is a single pattern". | low | Add "(when the pattern spans the whole train)". | yes: shelf PDF |
| Figure 3 table, "hand-written here" for CoactDetect, LoCo and rate+context; the `count_excess` definition | These rows claim authorship with no pointer to the recorded lineage. detector_history §4 records rate+context as cell-averaging CFAR and LoCo's `maxlt` as greatest-of combination, origin not established. `count_excess` (share active minus its 30 s mean) is the same subtractive local-background shape. Only binned SCE and `tube` get a lineage. | low | Point to detector_history §4 from the table or the lineage section. | yes: detector_history |
| *References*, minor gaps (none are errors) | • Hamon et al. 2026: title missing ("CICADA: A unified framework for NWB-based neurophysiological data analysis"; openRxiv DOI verified).<br>• Zhu, Li, Zhang 2023: no initials (Yunrong, Yang, Qiming).<br>• Jarabo-Amores 2009: 57(11):4175–4181; title missing.<br>• Wang 2019: ICASSP pp. 31–35, doi:10.1109/ICASSP.2019.8682847.<br>• Louis 2010: pp. 359–382, doi:10.1007/978-1-4419-5675-0_17.<br>• Grün 1996: a PhD thesis (Ruhr-Universität Bochum); subtitle "Detection, Significance, and Interpretation"; published in Thun/Frankfurt.<br>• Denis 2020: the DOI is the version DOI for v1.0.3; the concept DOI is 10.5281/zenodo.10041433.<br>• Elephant is cited only by RRID (resolves to Elephant, SCR_003833).<br>• SPADE has no reference.<br>• The dataset "this project also uses" is unnamed: it is DANDI:000219, whose DANDI record links it to Dard 2022. | low | Fill these in. | yes: Crossref, DataCite, DANDI API, SciCrunch |

## Every reference: exists, says what's quoted, is the origin

- **Cecchini 2021** (PLoS Comput Biol 17(5):e1008963): exists; supports the mean-signal threshold; not the origin (Kreuz 2017 is, see findings).
- **Cossart, Aronov & Yuste 2003** (Nature 423:283–288): exists. Methods confirm interval reshuffling, 1,000 surrogates and a 5 % threshold, crediting Mao et al. 2001 (ref. 12). Lab: Yuste (last author), Columbia.
- **Mao et al. 2001** (Neuron 32(5):883–898, doi:10.1016/S0896-6273(01)00518-9): exists; metadata correct. **Not reached:** Cell Press returns 403 to automated fetches. Unpaywall lists it as free on the publisher's site, so a browser should work.
- **Dard 2022** (eLife 11:e78116): exists. Methods confirm an independent per-cell circular shift, 300 surrogates and the 99th percentile. Last author Picardo, INMED.
- **Denis et al. 2020, CICADA** (Zenodo): exists; creators and year match DataCite.
- **Hamon et al. 2026**: exists. The PDF confirms the corresponding and last author is Dard, at EPFL's Laboratory of Sensory Processing, with INMED co-authors (Denis, Filippi, Cossart, Picardo).
- **Diskin et al. 2024** (Signal Processing 223:109543; arXiv 2208.02474): exists; checked from the abstract only.
- **Finn 1967** (RCA Review 28(4):653–678): exists. Checked in a scan of the December 1967 issue: title, "Harold M. Finn", pp. 653–678. The threshold is proportional to a maximum-likelihood estimate of clutter level. Finn & Johnson's footnote prints "Vol. 29", which is their typo; the report's 28 is right.
- **Finn & Johnson 1968** (29(3):414–464): exists; pages confirmed from the shelf scan. Finn 1966 (Proc. National Electronics Conference, 22:562) was not reached, as the report says.
- **Grün 1996**: exists (Reihe Physik 60, Harri Deutsch; confirmed by the Grün 1999 abstract).
- **Grün, Diesmann & Aertsen 2002** (Neural Comput 14(1):43–80): exists. Clipping confirmed through the same authors' 2010 chapter on the shelf, not the 2002 paper.
- **Grün et al. 1999** (J Neurosci Methods 94(1):67–79): exists. The abstract confirms the multiple-shift method is a coincidence detector, not a null.
- **Gutmann & Hyvärinen 2012**, **Lopez-Paz & Oquab 2017**, **Scott & Nowak 2005** (51(11):3806–3819): exist and say what is cited; origin gaps are in the findings.
- **Harrison & Geman 2009** (21(5):1244–1258): exists; the quote is accurate, with the R = ∞ nuance.
- **Jarabo-Amores 2009**, **Zhu 2023**: exist; titles match the cited claims; texts not read.
- **Kreuz 2015 SPIKY** (113(9):3432–3445): exists and is the right origin for the profile. It builds on Quian Quiroga, Kreuz & Grassberger 2002 (event synchronization), which could be cited as its ancestor.
- **Mulansky & Kreuz 2016** (SoftwareX 5:183–189): exists; misapplied (see findings).
- **Louis, Borgelt & Grün 2010**: exists. All three claims check out: they recommend spike-train dithering, credit Pipa 2008 and Harrison & Geman 2009, and roll the train at the ends because "start and end rates are the same".
- **McFee et al. 2018** (26(11):2180–2193): exists. It does evaluate time-localized predictions with segment-based metrics, which supports the report's claim.
- **Nadeau & Bengio 2003** (52(3):239–281): exists; text not opened.
- **Pipa, Riehle & Grün 2007**: metadata and DOI match Crossref. **Not reached** (closed access).
- **Pipa et al. 2008** (25(1):64–88): exists; describes whole-train shifting in full (§2.4).
- **Stella et al. 2022**: exists. It calls TR-SHIFT "the most robust surrogate method", recommends it as "the surrogate method of choice for the SPADE analysis", and uses a 25 ms dither.
- **Wang, Li & Metze 2019**: exists; focuses on localization.

## Literatures searched and not searched
- **Searched:**
  - spike-train surrogates: Harrison & Geman, Louis, Pipa, Stella, Grün, and the Elephant source
  - calcium-imaging synchronous calcium event (SCE) detection: Yuste and Cossart/Dard groups, forward to Hamon 2026
  - SPIKE-synchronization: Kreuz group, forward to Cecchini 2021, back to Kreuz 2017
  - radar CFAR primaries
  - Neyman–Pearson learning
  - noise-contrastive estimation and classifier two-sample tests
  - weakly supervised sound-event pooling
  - the shelf's self-supervised-learning papers on neural data
  - two web searches for learned detectors trained against spike or calcium surrogates (nothing closer found)
- **Not searched (still ⚠):**
  - time-shift surrogates in nonlinear time-series analysis (Andrzejak, Kraskov, Stögbauer, Mormann & Kreuz 2003, *Phys Rev E* 68:066202 exists and is an unexamined lead, with a Kreuz co-author)
  - toroidal-shift nulls in ecology
  - anomaly and change-point detection
  - EEG burst detection
  - astronomical and seismic transients
  - learned or differentiable CFAR beyond CFARnet and Zhu 2023
  - Grün and Pipa work before 2003
  - the Kreuz group after 2022

## Couldn't reach
Pipa, Riehle & Grün 2007; Pipa & Grün 2003; Mao 2001; Finn 1966; Grün 1996 (a book); Cannon et al. 2002; Friedman 2003; Gutmann & Hyvärinen 2010. The text of DE10008251A1 is seen only through an automated summary.

## Questions only the humans can answer
1. **Kreuz email:** what is its exact date? Did Kreuz point to Cecchini 2021 or to the 2017 paper? Did anyone ask whether his group has thresholded SPIKE-synchronization on other hippocampal-slice calcium data?
2. **Pipa or Grün:** has anyone asked them where whole-train random shifting started? Pipa & Grün 2003 and the 2000 patent are the open steps.
3. **Dard (EPFL) or the Cossart lab:** has anyone asked whether they have trained, or plan to train, learned synchronous-event detectors against circular-shift surrogates? That forward step is the closest possible prior art for the report's "our own" claim.
4. **Papers Tony could fetch:** Pipa, Riehle & Grün 2007 and Pipa & Grün 2003 (Neurocomputing, closed access), and Mao 2001 (free on cell.com in a browser).

Scratch files are under `<scratchpad>/mb4/role02/` (fetched PDFs and their text dumps). Nothing in the repository was edited.

Sources:
- [Cecchini et al. 2021, PLoS Comput Biol](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008963)
- [Kreuz et al. 2017, New J Phys](https://iopscience.iop.org/article/10.1088/1367-2630/aa68c3)
- [Cossart, Aronov & Yuste 2003 (Columbia copy)](https://blogs.cuit.columbia.edu/rmy5/files/2017/06/cossart.nature.03.pdf)
- [RCA Review, December 1967 (worldradiohistory)](https://worldradiohistory.com/ARCHIVE-RCA/RCA-Review/RCA-Review-1967-12.pdf)
- [DE10008251A1, Google Patents](https://patents.google.com/patent/DE10008251A1/en)
- [Scott & Nowak 2005 (author copy)](https://www.stat.rice.edu/~cscott/pubs/np.pdf)
- [CFARnet, arXiv 2208.02474](https://arxiv.org/abs/2208.02474)
- [McFee, Salamon & Bello, arXiv 1804.10070](https://arxiv.org/abs/1804.10070)
- [Elephant v1.2.1 surrogates source](https://raw.githubusercontent.com/NeuralEnsemble/elephant/v1.2.1/elephant/spike_train_surrogates.py)
- [Grün et al. 1999, PubMed](https://pubmed.ncbi.nlm.nih.gov/10638816/)
- [Grün 1996 thesis, dblp](https://dblp.org/rec/phd/dnb/Grun96.html)
- [Mao et al. 2001, PubMed](https://pubmed.ncbi.nlm.nih.gov/11738033/)
- [DANDI:000219](https://dandiarchive.org/dandiset/000219/draft)
- [Seizure event detection, Stern et al. 2024, PubMed (checked, not Kreuz group)](https://pubmed.ncbi.nlm.nih.gov/38274784/)
