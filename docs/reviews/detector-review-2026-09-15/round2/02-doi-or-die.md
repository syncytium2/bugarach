> **Public copy.** Lines that concern real treatment recordings are removed (2 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2, DOI or Die: citations and attributions (blind pass, round 2)

**Artifact:** `detector_review.html`, read through `detector_review_plain.txt`, built from `tools/detector_review_template.html`.

**What I checked:** every reference in Section 11 and every named attribution in Sections 1, 3.5, 3.6, 4 and 8. I resolved all DOIs against Crossref, checked the claims against the cached primary texts in the scratch folder, and pulled CICADA's metadata from Zenodo and GitLab. I also downloaded the PySpike paper (arXiv 1603.03293) and checked when `max_tau` entered PySpike's git history. The figures carry no attributions; I checked Figure 7.

**Result:** 2 blocking, 3 major and 13 minor findings. Twenty-two references and attributions checked out clean; they are listed after the findings.

---

## Blocking

**B1. Section 11, locust/CICADA: the version cited does not contain the method that was ported.**
- **Issue:** The page cites "CICADA … v1.0.3, Zenodo, doi:10.5281/zenodo.10041434". That release has no SCE detection code.
  - The GitLab tag `1.0.3` is dated 2019-08-30. Its tree has 343 files and none matches `sce`.
  - `sce_stats_utils.py`, which holds `get_sce_threshold` and `detect_sce` (the functions locust is derived from), was first committed on 2020-03-26.
  - It first appears in a tagged release at `1.1.0` (2024-05-21). It is now at `src/cicada/utils/stats/sce_stats_utils.py` in `2.2.0` (2025-11-23).
  - The project's own record says the transliteration was checked against upstream **`master`** on 2026-08-21, not against v1.0.3 (`docs/detector_history.md` §6.3, around line 876).
  - A reader who follows the citation cannot find the method it names.
- **Also wrong in the same entry:**
  - The Zenodo record was *created* 2023-10-26, even though its `publication_date` field says 2020-07-20.
  - Zenodo's title is "CICADA stands for Calcium Imaging Complete Automated Data Analysis".
- **Evidence:**
  - https://zenodo.org/api/records/10041434 (version 1.0.3, concept DOI 10.5281/zenodo.10041433)
  - `https://gitlab.com/api/v4/projects/14048984/repository/tags`
  - `…/repository/tree?ref=1.0.3&recursive=true`
  - `…/repository/commits?path=src/cicada/utils/stats/sce_stats_utils.py`
- **Fix:** Cite the GitLab repository at the commit that was read (record the hash from interface2's `coordination_method_provenance.md` §5). For the software in general, cite the Zenodo *concept* DOI 10.5281/zenodo.10041433. Say the SCE functions are not in v1.0.3.
- **Verified against a source:** yes.

**B2. Section 11, SPIKE-synch: the window cap is credited to a paper and a tool that do not supply it.**
- **Issue:** The page says "Our implementation follows Mulansky M., Kreuz T. (2016), PySpike, SoftwareX 5:183–189 … whose cap on the window we use." That is wrong three ways:
  1. **The paper never mentions a cap.** Its Appendix A.3 defines τ as half the smallest of the four neighbouring inter-spike intervals, with no upper bound (arXiv 1603.03293).
  2. **The cap exists only in the software.** `max_tau` was added in commit `4366f30` on 2015-04-02, but this project's own records say it has done nothing since PySpike 0.8.0 (2023): `docs/FOUNDATIONS.md` line 81, `docs/pyspike_max_tau.patch`, and `docs/exports/pyspike_pr_body_2026-08-31.md`.
  3. **The project's own history says the cap is its own code.** `docs/detector_history.md` lines 340–343 say bugarach computes its own τ and the cap is its own.

  So the sentence credits a feature to a paper that lacks it and to a library where it is inert.
- **Evidence:**
  - https://arxiv.org/pdf/1603.03293 (Appendix A.3)
  - PySpike git log: `git log -S max_tau` in github.com/mariomulansky/PySpike
- **Fix:** Cite PySpike 2016 for the SPIKE-synchronization definition only. Add something like: "The 0.25-second cap is applied in our own code. PySpike has a `max_tau` option meant to do the same thing, which has had no effect since version 0.8.0 (reported upstream)."
- **Verified against a source:** yes.

---

## Major

**M1. Section 2, "Why the shift and not the shuffle": the mechanism is already published and is not cited.**
- **Issue:** The page argues from its own measurement that a shuffle puts two events from one cell in the same bin, where they count once. That makes the surrogate counts too low, the bar too low, and chance lineups fire more often.
  - Stella, Bouss, Palm & Grün (2022) report the same failure for uniform dithering: an overestimate of significance, which means false positives.
  - Their recommended fix is to shift whole trains, which is what this project does.
  - An external reviewer from the spike-statistics field will expect this citation.
- **Evidence:**
  - Stella A., Bouss P., Palm G., Grün S. (2022). *Comparing surrogates to evaluate precisely timed higher-order spike correlations.* eNeuro 9(3):ENEURO.0505-21.2022, doi:10.1523/ENEURO.0505-21.2022 (abstract read in the cached copy).
  - Louis S., Borgelt C., Grün S. (2010). *Generation and selection of surrogate methods for correlation analysis.* In *Analysis of Parallel Spike Trains*, pp. 359–382, doi:10.1007/978-1-4419-5675-0_17 (resolved only; not read).
- **Fix:** Add Stella 2022 to Section 11 beside the surrogate entry. Say this project's measurement agrees with it.
- **Verified against a source:** yes for Stella; no for Louis 2010.

**M2. Sections 2 and 11, "Where the surrogate comes from matters too": the local-surrogate literature is missing.**
- **Issue:** The headline finding is that surrogates drawn from the nearby seconds follow slow rate changes and whole-recording surrogates do not. That is the central point of the jitter and conditional-resampling literature. None of it is cited.
- **Evidence:**
  - Harrison M.T., Geman S. (2009). *A rate and history-preserving resampling algorithm for neural spike trains.* Neural Computation 21(5):1244–1258, doi:10.1162/neco.2008.03-08-730 (resolved).
  - Amarasingham A., Harrison M.T., Hatsopoulos N.G., Geman S. (2012). *Conditional modeling and the jitter method of spike resampling.* J Neurophysiol 107:517–531, doi:10.1152/jn.00633.2011 (cached text read).
  - Grün S. (2009). *Data-driven significance estimation for precise spike correlation.* J Neurophysiol 101(3):1126–1140, doi:10.1152/jn.00093.2008 (resolved).
- **Fix:** Cite Amarasingham 2012 or Harrison & Geman 2009 where CoactDetect's and LoCo's local window is introduced. Stella 2022 already credits trial shifting to Pipa 2008 *and* Harrison & Geman 2009.
- **Verified against a source:** partly. Amarasingham was read; the other two were resolved only.

**M3. Section 11, LoCo: "We have not found who first proposed [greatest-of]." A standard origin exists.**
- **Issue:** Greatest-of CFAR is routinely credited to Hansen V.G. (1973), *Constant false alarm rate processing in search radars*, IEE Conf. Publ. 105, *Radar — Present and Future*, London, pp. 325–332.
  - The cited Hansen & Sawyers (1980) paper itself says its loss rule "is given in [1]".
  - That reference list was cut off in the cached text, so I could not read [1] directly.
  - Rohling (1983) cites Hansen & Sawyers and Moore & Lawrence for greatest-of, not an earlier root.
- **Where I stopped:** one step short. Hansen 1973 is a conference paper that is not online, and reference [1] of the 1980 paper is not legible in the cache.
- **Evidence:** https://www.semanticscholar.org/paper/Constant-false-alarm-rate-processing-in-search-Hansen/b9f381e35d0cc467d022f6661a4b477f0ba78d8f
- **Fix:** Replace the sentence with "Greatest-of selection is usually credited to Hansen (1973)", cite it, and keep Hansen & Sawyers 1980 for the loss analysis. Better still, get the IEEE PDF of Hansen & Sawyers and confirm what reference [1] is.
- **Verified against a source:** no. This is a residual ⚠.

---

## Minor

**m1. Section 11, CICADA license.** "Under the MIT license" is correct for the GitLab repository: `LICENSE.txt` is MIT, "Copyright (c) 2019 cossart lab". But the Zenodo deposit the page cites is licensed **CC-BY-4.0**. Name the license with the source it belongs to. *Verified: yes.*

**m2. Sections 3.5 and 11, forward trace on CICADA.**
- A paper describing the current CICADA now exists: Hamon M., Lebert J., … Cossart R., Picardo M.A., Dard R.F. (2026). *CICADA: A unified framework for NWB-based neurophysiological data analysis.* bioRxiv, doi:10.64898/2026.07.03.736318 (resolves to bioRxiv).
- Its corresponding and last author is at EPFL, in the Laboratory of Sensory Processing. Cossart and Picardo (INMED, Marseille) are co-authors.
- Every commit to `sce_stats_utils.py` since 2022 is by Robin Dard.
- "Released by the Cossart lab" is still accurate for the repository namespace and license holder. An external reader would still expect the preprint cited as the current description.
- *Verified: yes, from the preprint text and GitLab commits.*

**m3. Section 11, Cecchini 2021 "in comparable ways".**
- **What the paper says:** Cecchini et al. keep only spikes coincident with spikes in at least three-quarters of the other trains, which is a per-spike cut on SPIKE-synchronization. They then pair spikes using SPIKE-order. The rest of the method is in their S1 Appendix, which I did not read.
- **What the correspondence adds:** it is correctly cited, not quoted, and dated 2026-04-23, matching `docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`. Paraphrased, it says their detector also required a condition on the calcium signal itself, which an event-times-only detector cannot apply.
- **Problem:** "Comparable" hides both differences.
- **Fix:** Something like "…select events by thresholding the same measure, per spike rather than per bin, together with a condition on the calcium signal (Cecchini et al. 2021; T. Kreuz, personal communication, 2026-04-23)."
- *Verified: yes for Cecchini's main text (https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008963); no for S1.*

**m4. Section 11, Mao 2001: only verified one step short.**
- The bibliographic details are correct.
- The claim that surrogate thresholding "goes back to" Mao rests on Cossart, Aronov & Yuste 2003 citing Mao (their ref. 12) for interval-reshuffling surrogates. I checked that in the 2003 Methods.
- I could not read Mao's own Methods: the Cell Press full text returned 403. So I have not confirmed that Mao thresholded coactive-cell counts, or whom Mao cites.
- Both papers are from the Yuste lab (Columbia; Yuste is last author on both). Cossart is first author of the 2003 paper and later ran her own lab in Marseille. The page does not conflate the two labs.
- *Verified: no. Residual ⚠.*

**m5. Section 11, Pipa 2008 "Shifting whole spike trains".**
- NeuroXidence jitters complete trains by a small bounded amount within trials, with no wrap-around (Pipa et al. 2008, Fig. 1(e)). Stella 2022 credits whole-train dithering to Pipa 2008 and Harrison & Geman 2009.
- The attribution is right for the idea. The wrap-around circular shift used here is a variant, not Pipa's construction.
- **Fix:** Add "(bounded shifts; the wrap-around form is used in Bocchio 2020 and Dard 2022)" and add Harrison & Geman 2009.
- *Verified: yes.*

**m6. Section 11, rate+context lineage.**
- **Radar root:** Finn & Johnson (1968) cite earlier Finn papers on adaptive detection, including H.M. Finn, *Adaptive detection in clutter*, Proc. Natl. Electronics Conf. XXII:562 (1966). I stopped there, unretrieved. The 1968 citation is still the standard one.
- **Neuroscience lineage (bigger gap):** thresholding a population rate (PSTH) against a running baseline is common practice, and the correspondence (paraphrased) pointed there too. The project already holds Cotterill et al. 2016, a burst-detector comparison that `docs/detector_history.md` §2 calls half-read. A neuroscience reviewer will expect a neuroscience citation beside the radar one.
- *Verified: no. Residual ⚠: that literature was not searched.*

**m7. Section 11, formatting.** Nine references have no DOI, although every one resolves. Titles are also missing for most of them. Add these DOIs and make all DOIs links:
- Bocchio 2020: 10.1038/s41467-020-18432-6
- Dard 2022: 10.7554/eLife.78116
- Cecchini 2021: 10.1371/journal.pcbi.1008963
- DOSED: 10.1016/j.jneumeth.2019.03.017
- cnn-ripple: 10.7554/eLife.77772
- Mölter 2018: 10.1186/s12915-018-0606-4
- Lehman 2010: 10.1210/en.2010-0022, issue 151(8)
- Navarro 2009: 10.1523/JNEUROSCI.1569-09.2009, issue 29(38)
- Quian Quiroga 2002: 10.1103/PhysRevE.66.041904

*Verified: yes.*

**m8. Section 1, Lehman 2010.** Correct, but it is a review. The term "KNDy" also appears earlier the same year from the same group: Cheng G., Coolen L.M., Padmanabhan V., Goodman R.L., Lehman M.N. (2010), Endocrinology 151(1):301–311. I did not read it to check who coined the term. Optional. *Verified: no.*

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**m10. Sections 8 and 11, attributions with no name.**
- "First written in MATLAB by the same author": no author is named anywhere in the document.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Neither can be checked by an outside reader. Name the person, or point to a citable record.
- *Verified: no.*

**m11. Out of scope, but it feeds this page: `docs/detector_history.md` misdescribes Cossart 2003.**
- Around line 387 it says the 2003 method used a "pooled histogram, percentile cut".
- The 2003 Methods instead set the threshold as the number of coactive cells "exceeded in a single frame in only 5% of these histograms" across 1,000 surrogates. That is a per-surrogate maximum.
- The artifact's wording ("took a per-surrogate maximum") matches the primary. The history note is the one that is wrong.
- *Verified: yes, cached Cossart 2003 Methods.*

**m12. Section 11, forward trace on Kreuz.** Kreuz's publication page (https://www.thomaskreuz.org/publications/journal-articles) lists two later items I did not read:
- Mariani et al. (2025), J Neurosci Methods 416:110378.
- Kreuz (2025), *Quantifying spike train synchrony and directionality: Measures and Applications*, Biol Cybern (in press; arXiv:2510.07140).

Per the correspondence (paraphrased), the Mariani paper allows at most one spike per train in each event. That bears on a known SPIKE-synch weakness recorded in the repo: its `min_n` floor can count one ROI more than once. Consider citing the review as the modern restatement. *Verified: no.*

**m13. Section 4.1, tube-guard.** Blanking the surround near the scored moment is the CFAR "guard cell" idea. Section 11 cites radar only for rate+context and LoCo, so a one-line cross-reference would close the gap. *Verified: yes, as a construction.*

---

## Verified clean

Crossref metadata, and where noted the text, matches the page for each of these:
- **Grün, Diesmann & Aertsen (2002), Unitary Events I:** Neural Computation 14(1):43–80, doi:10.1162/089976602753284455.
- **Unitary Events II:** 14(1):81–119, doi:10.1162/089976602753284464. "Moving window" is backed by the sliding-window description in Grün et al.'s 2010 chapter; I did not open the 2002 paper itself.
- **Pipa, Wheeler, Singer & Nikolić (2008):** J Comput Neurosci 25(1):64–88, doi:10.1007/s10827-007-0065-3.
- **Hansen & Sawyers (1980):** AES-16(1):115–118, doi:10.1109/TAES.1980.308885. It does analyze the extra loss from greatest-of selection.
- **Rohling (1983):** AES-19(4):608–621, doi:10.1109/TAES.1983.309350. Order-statistic CFAR, so "related to" is fair.
- **Finn & Johnson (1968):** RCA Review 29, September 1968, pp. 414 onward. The threshold is proportional to an estimate of the clutter level, so "radar multiplies" is correct.
- **Mao et al. (2001):** Neuron 32(5):883–898, doi:10.1016/S0896-6273(01)00518-9.
- **Cossart, Aronov & Yuste (2003):** Nature 423:283–288, doi:10.1038/nature01614. Interval reshuffling, 1,000 surrogates, per-surrogate maximum: all confirmed in the Methods.
- **Malvache et al. (2016):** Science 353(6305):1280–1283, doi:10.1126/science.aaf3319. Introduces "synchronous calcium events (SCEs)" in awake CA1.
- **Bocchio et al. (2020):** Nat Commun 11:4559. Circular shift of each cell, 1,000 surrogates, 99th percentile of the pooled sum, 200 ms bins.
- **Dard et al. (2022):** eLife 11:e78116. Circular shift of each cell, 300 surrogates, 99th percentile, run through CICADA's "SCE description" analysis. Together with Bocchio, this backs "like the one in".
- **Kreuz, Mulansky & Bozanic (2015):** J Neurophysiol 113(9):3432–3445, doi:10.1152/jn.00848.2014. Its abstract introduces SPIKE-synchronization as an extension of event synchronization.
- **Quian Quiroga, Kreuz & Grassberger (2002):** Phys Rev E 66:041904.
- **Mulansky & Kreuz (2016):** SoftwareX 5:183–189, doi:10.1016/j.softx.2016.07.006. The bibliographic details are right; only the cap claim fails (B2). The four-gap window definition matches Section 3.6.
- **Cecchini et al. (2021):** PLoS Comput Biol 17(5):e1008963. It is ref. 45 on Kreuz's own publication list.
- **Chambon et al. (2019), DOSED:** J Neurosci Methods 321:64–78.
- **Navas-Olive et al. (2022), cnn-ripple:** eLife 11:e77772.
- **Mölter, Avitan & Goodhill (2018):** BMC Biol 16:143.
- **Lehman, Coolen & Goodman (2010):** Endocrinology 151(8):3479–3489.
- **Navarro et al. (2009):** J Neurosci 29(38):11859–11866.
- **CICADA authors on Zenodo:** Denis, Dard, Quiroli, Cossart, Picardo, as the page lists.
- **Private correspondence:** the Kreuz exchange is cited and dated, not quoted, which complies with the repository rule.

## Literatures searched, and what is still open (⚠)

- **Searched:**
  - spike-train surrogate statistics (Grün lab, Pipa, jitter methods)
  - the calcium-imaging SCE lineage (Yuste, then Cossart, then CICADA)
  - SPIKE-synchronization (the Kreuz group, backward and forward)
  - radar CFAR (CA, GO, OS)
  - the learned-detector and benchmark papers the page cites (existence and content only)
- **Not searched:**
  - multi-electrode-array network-burst and PSTH-threshold detection (m6)
  - circular or toroidal-shift surrogates in ecology and time-series analysis, which could predate Pipa for the wrap-around form
  - who first proposed hysteresis (two-level) thresholding
  - the neuroendocrinology literature beyond the two background citations
- **Stopped one step short:**
  - Hansen 1973 (M3)
  - Mao 2001's Methods (m4)
  - Finn 1966 (m6)
  - Cecchini 2021 S1 Appendix (m3)
- **Correspondence:** the Kreuz exchange exists and is cited properly. The repo has no record of anyone asking the CICADA authors about the locust port or its v1.0.3 citation. **Nobody asked:** residual ⚠. The page already says no output has been compared against CICADA itself.
