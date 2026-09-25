GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
(SubagentHandback is also present. It is the delivery channel, not an editing tool. No Edit, Write or NotebookEdit.)

# Role 2, DOI or Die: methods_one_page (HTML text; the PDF is its render)

I edited no repo file. Scratch files are in `<scratch>/mb/` (a copy of RCA Review 29(3) and a text extraction of it).

## The five references on page 2

| Ref | Exists | Metadata | Says what the text uses it for | Origin |
|---|---|---|---|---|
| Efron 1979 | yes (Crossref) | correct: *Ann. Statist.* 7(1):1–26, doi:10.1214/aos/1176344552 | yes for the bootstrap (abstract read). Full text not reached: Project Euclid PDF blocked | origin of the bootstrap; see finding 5 for the percentile interval |
| Finn & Johnson 1968 | yes | correct: I read the Sept 1968 issue's own contents page. The paper starts at p. 414 and the next item at p. 465, so 414–464 holds. No DOI exists (RCA Review predates DOIs). | yes for cell-averaging CFAR. The body text says the threshold is set from "the outputs of the resolution cells that surround the cell under test", with that cell excluded (Fig. 2) | the standard citation, but see finding 1b |
| Kingma & Ba 2015 | yes (arXiv 1412.6980) | correct (3rd ICLR, San Diego, 2015) | yes | origin |
| Yu & Koltun 2016 | yes (arXiv 1511.07122) | correct (ICLR 2016) | yes | Their §2 credits the operator to the algorithme à trous (Holschneider et al. 1987; Shensa 1992) and prior CNN use to Chen et al. 2015. Citing Y&K for a dilated-convolution architecture is conventional. No action needed. |
| Zaheer et al. 2017 | yes (arXiv 1703.06114, NIPS 2017) | correct. All six authors verified. | yes: Theorem 2 gives ρ(Σφ(x)) and handles sets of varying size | not the only origin; see finding 4 |

Every in-text citation has an entry and every entry is cited. Grün 2002 and Amarasingham 2012 (decisions_pending item 7, unread) are correctly **not** cited. There is no quoted or private correspondence, and no "personal communication", on the page. The CLAUDE.md private-correspondence rule is satisfied.

## Findings

**1. CoactDetect paragraph: "The method is a cell-averaging constant-false-alarm-rate (CFAR) test (Finn & Johnson, 1968)."** Severity: **major**.
- **Issue (a): it overclaims identity and drops the independence statement.**
  - The repo's own map (docs/detector_history.md §4 table) lists CoactDetect's analogue as "cell-averaging, per-cell test" and leaves the attribution column empty. Finn & Johnson is attributed there to rate+context.
  - CoactDetect differs from Finn & Johnson's test:
    - its statistic is a distinct-ROI count;
    - its null is a circular-shift surrogate;
    - its threshold is mean + z·SD, where Finn & Johnson use a threshold proportional to the estimate;
    - its guard is optional, and when the guard is narrower than the window the test window's own onsets sit in the null pool.
  - Finn & Johnson exclude the cell under test and have **no guard band**. The repo's correction in detector_history §5.1 says guard bands are "standard by 1983". Putting "is a CA-CFAR test (F&J)" right after the guard band implies F&J have one.
  - Tony's ruling (detector_history, 2026-08-24 and 2026-08-29) is to "acknowledge the origins, say we arrived independently". Tony has also said: *"They blindly reconstructed elements of CFAR, I was totally unaware when I designed them"*. The commit timeline supports this: the detector was built 2026-07-14 and the CFAR literature was found 2026-08-22. As written, the sentence reads as derivation, which puts the credit in the wrong place.
- **Issue (b): the trace stops one step short of the root.** Finn & Johnson's §I cites three earlier Finn papers:
  - "Adaptive Detection in Clutter", *Proc. Natl. Electronics Conf.* XXII:562, 1966;
  - the Allerton conference paper of Oct 1967;
  - *RCA Review* Dec 1967, which they misprint as vol. 29.

  §II also calls their method "a generalization" of a "conventional" thermal-noise CFAR system. None of these was retrieved. Keep F&J 1968 as the standard citation for the cell-averaging form, but do not call it where CFAR began.
- **Suggested fix (net length ≈ 0):** "It resembles cell-averaging constant-false-alarm-rate (CFAR) detection (Finn & Johnson, 1968), which it arrived at independently."
- **Verified:** yes. I checked the repo lineage, and read F&J's abstract, §I–II and Fig. 2 in the scanned issue. The 1966–67 Finn papers are unverified.

**2. Participation floor: the rigid-shift null has no citation.** Severity: **major**.
- **Issue:** shifting each ROI's whole train by its own random offset is a published surrogate. The repo's own glossary (docs/GLOSSARY.md, "rigid shift") credits it as whole-train shifting to Pipa, Riehle & Grün 2007; Pipa et al. 2008; Louis, Borgelt & Grün 2010. ADR-0008 says the write-up cites ADR-0006's definition of chance.
- **The published form wraps the train; this project's form drops onsets pushed past the window's end** (glossary ⚠). So "after" is the honest verb, not "is".
- **Which lab.** The first author is shared but the laboratories are not:
  - Pipa et al. 2008 (NeuroXidence), last author Nikolić: Max Planck Institute for Brain Research / Frankfurt Institute for Advanced Studies, Singer's group.
  - Pipa, Riehle & Grün 2007, last author Grün: RIKEN / BCCN Berlin.
  - I looked up both affiliations in OpenAlex.
- **Where the trace stops:** an earlier role-2 report in this repo (slow-comodulation round 2) says Pipa 2008 p. 68 names Grün et al. 1999's multiple-shift method as the predecessor. Grün 1999 and Pipa 2007 are closed-access and unread, so the trace is verified to one step short of the root.
- **Suggested fix:** change "(a rigid shift)" to "(whole-train shifting, after Pipa et al., 2008)". Add to page 2:
  - Pipa G, Wheeler DW, Singer W, Nikolić D (2008). NeuroXidence: reliable and efficient analysis of an excess or deficiency of joint-spike events. *J Comput Neurosci* 25(1):64–88. doi:10.1007/s10827-007-0065-3
  - Optional review citation: Louis S, Borgelt C, Grün S (2010). Generation and selection of surrogate methods for correlation analysis. In *Analysis of Parallel Spike Trains*, Springer, 359–382. doi:10.1007/978-1-4419-5675-0_17
  - Page 2 holds only five entries, so the page-1 cost is about 30 characters.
- **Verified:** metadata yes (Crossref, and the Pipa 2008 abstract via OpenAlex). The wrap claim for the published method is second-hand, from the repo glossary.

**3. Parameters: "the cross-ROI onset correlogram" has no citation.** Severity: **major**.
- **Issue:** the tool this sentence describes, tools/measure_jitter_correlogram.py, says in its own docstring that the statistic is "(Perkel, Gerstein & Moore 1967)". The page credits no one.
- **Suggested fix:** "…onset correlogram (Perkel et al., 1967)…". Add: Perkel DH, Gerstein GL, Moore GP (1967). Neuronal spike trains and stochastic point processes. II. Simultaneous spike trains. *Biophys J* 7(4):419–440. doi:10.1016/S0006-3495(67)86597-4
- **Verified:** metadata yes (Crossref). Text not read, so whether PGM 1967 has this exact normalisation (the count expected under independence) is unverified.

**4. Chorus: "(Zaheer et al., 2017)" as the sole credit for symmetric pooling across ROIs.** Severity: **minor**.
- **Issue:** Deep Sets is not the only origin, and not the earliest. PointNet (a shared per-element network plus a symmetric pool) was posted in Dec 2016, before Deep Sets (Mar 2017). The repo's own docstring (src/bugarach/learn/nets/chorus.py) cites both. Ravanbakhsh, Schneider & Póczos (arXiv 1611.04500, 2016) is earlier still and comes from Deep Sets' own group.
- **Suggested fix:** "(Qi et al., 2017; Zaheer et al., 2017)". Add: Qi CR, Su H, Mo K, Guibas LJ (2017). PointNet: deep learning on point sets for 3D classification and segmentation. *CVPR*, 652–660 (CVF pagination; IEEE Xplore gives 77–85). doi:10.1109/CVPR.2017.16. arXiv:1612.00593
- **Verified:** yes (arXiv and Crossref). Crossref's author field for PointNet is garbled, so use the names above.

**5. "95% bootstrap interval … (Efron, 1979)".** Severity: **minor**.
- **Issue:** the code (tools/score_cross_stream.py) takes the 2.5 and 97.5 percentiles, i.e. a percentile interval. Efron 1979 is the origin of the bootstrap. The percentile interval is usually credited to Efron B (1981), Nonparametric standard errors and confidence intervals, *Can J Stat* 9(2):139–158, doi:10.2307/3314608 (Crossref-verified).
- **Suggested fix:** keep Efron 1979. Adding Efron 1981 is optional. If you add nothing, leave the text as it is.
- **Verified:** partly. The 1979 full text was blocked, so I could not confirm whether it already describes percentile intervals.

**6. Output: the width/amplitude measurement has no provenance.** Severity: **minor**.
- **Issue:** src/bugarach/call_measure.py and docs/INDEX.md record that it was "built from interface2's concept, not ported" (Tony, 2026-07-22 and 2026-09-21). interface2's `characterize_coord_window.m` did it first. This is the same lab and the same PI, so no literature citation is owed. A methods reader might still want "adapted from the laboratory's earlier analysis".
- **Suggested fix:** optional. Adjudicator's call, and only if it fits in the length.
- **Verified:** yes, against repo text.

**7. CoactDetect's circular-shift null within a context window has no citation.** Severity: **minor**.
- **Issue:** circular-shift surrogates over coactivity are standard. The earlier methods document cites Bocchio et al. 2020 and Dard et al. 2022 for that form, and Cossart, Aronov & Yuste 2003 for the SCE rule it descends from (they used interval reshuffling). The one-page draft cites none of them. Finding 1's wording probably covers this adequately for one page.
- **Suggested fix:** none required if finding 1 is applied. ⚠ The origin of the circular-shift coactivity null was not traced in this pass.
- **Verified:** no.

**8. Cosmetic:** "Deep sets" in the reference list; the published title is "Deep Sets" (the earlier methods doc uses that). Severity: **minor**. Match the house style.

**Checked, no finding:**
- **One-to-one scoring:** the scoring code (src/bugarach/score.py) uses greedy nearest-first matching within a tolerance. That is ordinary practice and owes no citation.
- **F1:** F1 as the harmonic mean, Gamma rate factors and coordinate search likewise need no citation on one page.
- **Adam hyperparameters:** stated, and they need no extra citation.

## Residual ⚠
- ⚠ **Unread roots:** the 1966–67 Finn papers (CFAR), Grün et al. 1999 and Pipa, Riehle & Grün 2007 (whole-train shift), and the full text of Perkel 1967 were not read.
- ⚠ **Unsearched literatures:**
  - seismology's STA/LTA adaptive triggers, a likely further independent ancestor of rolling-context thresholds;
  - sonar and other non-radar CFAR literature;
  - burst-detection literature beyond what the repo holds;
  - event-detection scoring and matching literature;
  - the forward trace of Zaheer/Póczos's and Pipa's later applied papers for neural-population uses;
  - the population-event detection literature in calcium imaging beyond one shallow web search.
- ⚠ **Nobody asked:** no one has been asked (for example the Grün lab) about the whole-train-shift lineage. This is recorded as a residual, not as an absence of prior art. For the CFAR convergence, the human evidence exists and is on file: Tony's recollection (2026-08-29), plus the commit timeline in detector_history.md. It supports finding 1's "arrived independently".

## Literatures searched
- **Radar CFAR:** the Finn & Johnson primary, read in the scanned RCA Review Sept 1968 issue, plus the repo's radar lineage.
- **Spike-train surrogates and coincidence:** Pipa 2007/2008 and Louis 2010, metadata and affiliations via Crossref and OpenAlex, plus the repo's earlier reviews.
- **Spike-train correlograms:** Perkel 1967, metadata only.
- **Machine learning:** Deep Sets, PointNet, dilated convolutions, Adam, via arXiv/ar5iv.
- **Statistics:** Efron 1979 and 1981, metadata and abstract.
- **Cross-field web searches:** "CFAR + calcium coactivity" and "permutation-invariant networks + calcium imaging". Neither turned up close prior art, but both were shallow.

Sources:
- [RCA Review Sept 1968 (Finn & Johnson, p. 414)](https://www.worldradiohistory.com/ARCHIVE-RCA/RCA-Review/RCA-Review-1968-09.pdf)
- [Efron 1979, Project Euclid](https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.full)
- [Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980)
- [Yu & Koltun, arXiv:1511.07122](https://ar5iv.labs.arxiv.org/html/1511.07122)
- [Zaheer et al., arXiv:1703.06114](https://ar5iv.labs.arxiv.org/html/1703.06114)
- [scispace record for Finn & Johnson](https://scispace.com/papers/adaptive-detection-mode-with-threshold-control-as-a-function-5d5m9eoan0)
- Crossref and OpenAlex API records for the DOIs above
