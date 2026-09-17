GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)

I searched with `grep` and `git grep` through Bash instead, so the missing tools cost no coverage. I did not open this page's round-one role-2 record (`<worktree>/docs/reviews/slow_comodulation_2026-09-17-roles/02-doi-or-die.md`), so this pass stayed blind.

## Findings

Each finding gives: **location** · issue · severity · suggested fix · verified against a source?

**Missing credit for methods the page uses**

1. **The count-variance ratio has no lineage anywhere on the page (Figure 1, the numbers table, "Published lineage")** · medium-high
   - **Issue:** The page's ratio is Schluter's variance ratio. Schluter 1984 (*Ecology* 65:998–1005, doi:10.2307/1938071, p. 999, Eq. 3) defines V = s_T²/Σσ_i²: the variance of the total count across samples divided by the sum of each species' variance. It equals 1 when nothing covaries, and Schluter credits Robson 1972 for the test. Map time bins to samples and ROIs to species and it is the page's ratio; the page just gets its denominator from a circular shift. Gotelli 2000 (*Ecology* 81:2606) notes that V > 1 comes from differences among samples, which is the page's own point about drift. In neuroscience the same construction is the Golomb–Rinzel synchrony measure χ². "What is new here is the measurement on these recordings" still holds, but the ratio reads as the page's own.
   - **Fix:** Credit Schluter 1984 (and Robson 1972, via Schluter) in the lineage section. Mention χ² as the neuroscience form.
   - **Verified:** Yes for Schluter (I read p. 999 from the author's own reprint) and Gotelli 2000 (on the shelf). χ² is from a web search only.

2. **"This page drops what leaves the window and trims, where Louis et al. roll the train" (lineage section; Figure 4 caption)** · medium
   - **Issue:** Shift, discard what falls outside, and score only a central segment trimmed by the maximum shift is Harris's "linear shift" method. It is set out in the Harris preprint the page already cites (the linear-shift section) and credited there to Harris 2020, "A Shift Test for Independence in Generic Time Series" (arXiv:2012.06862). The page presents the trimming as its own departure. Harris also shows that circular shift assumes cyclo-stationarity, and the page uses circular shift as its zero reference. That is consistent with what the page measures, but one clause should say so.
   - **Fix:** Credit Harris's linear shift for drop-and-trim, and add the clause about circular shift.
   - **Verified:** Yes for the preprint (shelved copy, posted 19 June 2021). The arXiv paper is cited from Harris's reference list; I did not open it.

3. **"who credit Pipa et al. 2008 and Harrison & Geman 2009" (lineage section)** · medium
   - **Issue:** The trace stops one step short. Harrison & Geman 2009 (pp. 1250–1251) credit the whole-train shift to Pipa, Riehle & Grün 2007 (*Neurocomputing* 70:2064–2068, doi:10.1016/j.neucom.2006.10.142). Pipa 2008 (p. 68) names Grün et al. 1999's multiple-shift method as its predecessor.
   - **Knock-on:** The rigid-shift report on the unmerged branch `unsup/rigid-shift-report-residuals` says "no source reached attributes train shifting to" Pipa, Riehle & Grün 2007. The shelved Harrison & Geman 2009 contradicts that.
   - **Fix:** Add the 2007 paper. Say the trace stopped at Grün et al. 1999, which is closed-access and unread.
   - **Verified:** Yes for Harrison & Geman 2009 and Pipa 2008 (both read). Pipa 2007 and Grün 1999 are checked by metadata only (Crossref).

**Citations that don't say what the page claims**

4. **Brody 1999 cited for "summed over all lags … zero by construction" (the ⚠ paragraph after Figure 2) and for "the correlogram integrates to the count covariance" (lineage section)** · medium
   - **Issue:** Brody's rule of thumb 3 (p. 1548; Eq. 3.6, p. 1546) is about the trial-shuffle-corrected covariogram: its sum equals the covariance of spike counts across trials. His "excitability covariations" are also across trials. The page's zero sum is plain arithmetic: its expected count comes from the same window's totals, and the raw correlogram summed over all lags equals n₁n₂. That identity is only a step in Brody's proof.
   - **Fix:** Say "by construction, because chance is set from the window's own totals". If Brody stays, write "(cf. Brody 1999, rule of thumb 3, for the across-trial version)" and add "over trials" to the lineage sentence.
   - **Verified:** Yes.

5. **Perkel, Gerstein & Moore 1967, "p. 428" (lineage section)** · low
   - **Issue:** The section heading starts on p. 428, but both claims (the elevation near zero lag from shared rate changes, and the flat elevation from a linear trend) are on p. 429.
   - **Fix:** Change to pp. 428–429.
   - **Verified:** Yes (checked page breaks in the scan).

6. **"Holding each train's count fixed in fixed windows … is interval jitter (Date, Bienenstock & Geman 1998 …)" (lineage section)** · low
   - **Issue:**
     - No venue given. Harrison & Geman 2009 cite it as a Tech. Rep., Division of Applied Mathematics, Brown University, May 1998 (the shelved copy is dated 21 May 1998). Amarasingham 2012 cites it instead as *Soc Neurosci Abstr* 25:1411, 1999.
     - Date et al. re-place spikes uniformly inside each interval. The block control circularly shifts inside each block, so it keeps within-block spacing.
   - **Fix:** Add the venue. Call the block control "a variant of interval jitter".
   - **Verified:** Yes.

7. **Named works without full references: Pipa et al. 2008, Harrison & Geman 2009, Stella et al. 2022, the Louis chapter** · low
   - **Issue:** The metadata resolve on Crossref:
     - Pipa 2008: *J Comput Neurosci* 25:64–88, doi:10.1007/s10827-007-0065-3
     - Harrison & Geman 2009: *Neural Comput* 21:1244–1258, doi:10.1162/neco.2008.03-08-730
     - Stella 2022: *eNeuro* 9(3), doi:10.1523/ENEURO.0505-21.2022
     - Louis chapter: pp. 359–382, eds Grün & Rotter, doi:10.1007/978-1-4419-5675-0_17

     "The ranking in Stella et al. 2022" is never explained. They call trial shifting "the most robust surrogate method" for SPADE (spatiotemporal spike-pattern) analysis at D = 25 ms.
   - **Fix:** Add full references, and say what the ranking was.
   - **Verified:** Yes. The quote "firing rates are smoothed on the timescale of the dither width" and the wrap-around in §17.3.3 are confirmed.

8. **Harris 2021 citation** · low
   - **Issue:** The DOI is the 2020 posting; the year comes from the version posted 19 June 2021. I found no peer-reviewed version.
   - **Fix:** Name that version.
   - **Verified:** Yes.

**The Dard et al. dataset and its lab**

9. **"the authors tie the activity to the animals' own movement, which is a published candidate" (decision section)** · medium
   - **Issue:** This overstates the paper.
     - Dard et al. 2022 link activity within 2 s of a movement onset (in 4 s windows). The sign depends on age: activity rises after movement from P5 to P8 and falls after movement from P10 on. They never discuss drift over minutes.
     - The paper also says "Neuronal activity was stable over the duration of the recording (… median change: 0.08 transients/minute, N = 31)" (p. 4). That bears directly on the page's reading of this dataset and is missing.
     - The paper says "non-anesthetized" and reports twitches during active sleep. "Awake" is DANDI's wording.
   - **Fix:** Describe the movement link at its real timescale and age range, add the stability statement, and say "non-anaesthetised".
   - **Verified:** Yes (paper read).

10. **Forward trace of the Cossart/Picardo group** · medium
    - **Issue:** The group's own protocol for these recordings, Ratsifandrihamanana et al. 2023 (*STAR Protocols*, doi:10.1016/j.xpro.2023.102760, last author Picardo), excludes recordings with a "strong change in baseline fluorescence" or z-motion artefacts. That speaks to the page's measurement-side explanations for drift. Leprince et al. (bioRxiv 2025.11.27.690943, last author Cossart; appears to be in *Current Biology* 2026) uses new P20–27 recordings, so it is not prior art for this dataset.
    - **Fix:** Cite the protocol next to the list of measurement-side explanations for drift.
    - **Verified:** Partly. I read the protocol through a PMC summary, not in full, and Leprince et al. only from part of the bioRxiv text.

11. **"its onset is the first frame of an inferred active run" (the settle-list item comparing the two folders)** · low-medium
    - **Issue:** The paper's Methods ("Activity inference") name the inference: DeepCINAC (Denis et al. 2020, *eNeuro* 7:ENEURO.0038-20.2020), thresholded at 0.5, with a cell counted active "from the onset to the peak of a calcium transient". Its NWB section says that inference is what went into the DANDI files. `<worktree>/tools/import_dandi.py` still says it "does not claim to know which step"; the paper answers that.
    - **Fix:** Credit DeepCINAC. Note that an "active run" ends at the transient's peak, which also matters for what `width_sec` means.
    - **Verified:** Yes for the paper. I did not open the NWB files themselves.

12. **The DANDI:000219 citation** · low
    - **Issue:**
      - Contributors (Dard, Picardo, Cossart) and the CC-BY-4.0 licence check out against the DANDI API.
      - No version is cited. The only published version is 0.260826.1155 (doi:10.48324/dandi.000219/0.260826.1155), published 2026-08-26. The importer landed 2026-08-28, and nothing records which version was downloaded; `<worktree>/tools/build_surrogate_report.py` already says so.
      - The licence is named but not linked.
      - Lab check: last author Picardo, co-corresponding Cossart; INMED U1249 (Inserm, Aix-Marseille University). Picardo works in Cossart's team, so "Cossart lab" elsewhere in the tree is correct.
    - **Fix:** Use DANDI's own citation string, plus a note that the downloaded version is unrecorded and a licence link.
    - **Verified:** Yes.

13. **`summary.json`** · low
    - **Issue:** It holds no commit, export version, dataset version or licence; the dataset appears only as `cossart/events`.
    - **Fix:** Add a provenance block, or have the page say where provenance lives.
    - **Verified:** Yes.

**In-repo attributions**

14. **"item 2 of *What waits on Tony* in the rigid-shift report … itself not yet re-reviewed" (the opening box)** · medium
    - **Issue:** This is accurate for the report in this tree, but the unmerged branch the page already cites (commits `65285fa` and `ef9fdc3`) has moved on:
      - The decision is now item 1 and reads "over tens of seconds", not "10–45 s".
      - "Absent on the lab fast stream" is retracted.
      - A third review round exists (`tube-self-supervised-2026-09-17-round3.md`).

      The page therefore cites two versions of the report, and a bare item number, which breaks the house writing rule, will be wrong whichever branch merges first.
    - **Fix:** Name the decision, pin the commit being cited, and say the report is being revised on that branch.
    - **Verified:** Yes.

15. **"Their expansions … are not written down in this repository" (Figure 6 text)** · medium
    - **Issue:** False. `<worktree>/docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` (line 88) and `<worktree>/tools/build_surrogate_report.py` (lines 1357–1358) spell them out, and FOUNDATIONS §9 says "diestrus" and "male". None of them cites the producer, and the export contract doesn't define the labels.
    - **Fix:** "Written down in this repository without a producer source (those two files); the export contract does not define them."
    - **Verified:** Yes.

16. **Extractor dead time: "the source attributes it to the extractor"** · low
    - **Issue:** That source is this repo's own reasoning, and the producer has never been asked: `<worktree>/docs/todo/2026-09-10-the-dead-time-floor-is-the-producers-number.md` is still open. The 2.80 s figure and its "measured by a review role" label match the goal page.
    - **Fix:** "This repository attributes it to the extractor; the producer has not been asked" and link the todo.
    - **Verified:** Yes.

17. **A relevant producer caveat is missing from the drift explanations (decision section)** · low-medium
    - **Issue:** `<worktree>/docs/todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md` records the producer's note that motion correction pinned 12 ROIs to the frame floor in four recordings, flagged in no column. That is a known cross-ROI measurement artefact of the "slice-position change" kind the page lists.
    - **Fix:** Cite it next to that explanation.
    - **Verified:** Yes.

18. **CoactDetect has no lineage pointer** · low
    - **Issue:** The main README places it in the Unitary Events / jitter family. `<worktree>/docs/detector_history.md` records that nobody has checked whether its rolling, rate-local null is published.
    - **Fix:** Link `detector_history.md` where CoactDetect is defined (Figure 5 caption).
    - **Verified:** Yes.

**Other in-repo attributions that checked out:**
- the operating points: fast 2 s / 60 s / α = 1e-4 in `bench.OPERATING_POINTS`; slow 1 s / 120 s / 1e-6 in the `coact_detect` docstring
- the generator spec: 0.0097 onsets per ROI per second, 3,525 s, 15 events, `hot_window` 1,200–1,500 s at 0.06
- the export spec's 0.3 s and 2 s peak lags
- MILESTONES on the ±2 s field-step exclusion
- `recording_identity.md` on group being nested in imaging date
- FOUNDATIONS §9 deferring to §15, and its rule against pooled numbers
- 0.669 and 0.522 in `results.json` at `ef9fdc3` (these are `share_real_higher`, not AUC)
- the sinusoidal modulation (40 s period, 0.9 depth)
- `count_excess`'s 30 s moving mean
- "no record in this tree" of anyone asking the producer or the Dard authors about drift

**Residual ⚠**

19. **Literatures I searched and did not search**
    - **Searched:**
      - spike-train statistics: correlograms, jitter and dither surrogates (the shelf, read)
      - ecology co-occurrence null models (Schluter, Gotelli)
      - time-series nonsense correlation (Harris)
      - Cossart/Picardo forward work
    - **Search results only, not read:**
      - neural synchrony measures (Golomb–Rinzel)
      - shared gain / state-fluctuation variability, e.g. Goris, Movshon & Simoncelli 2014, *Nat Neurosci* 17:858. The lineage section omits this whole field, which studies slow excitability changes shared across neurons.
    - **Not searched:**
      - variance-time, Fano and Allan-factor analysis of counts across window sizes (the page's 1 s / 10 s / 1-minute sweep)
      - econometric spurious regression beyond Harris
      - fMRI/EEG surrogate literature (on the shelf, unopened)
      - slice-imaging baseline drift and bleaching

20. **What the humans hold**
    - I can't ask Tony, so this stays open. Nothing in the tree shows the producer or the Dard/Picardo/Cossart group was asked about slow drift. Nothing shows whether anyone asked the producer how the fluorescence baseline is estimated, which could move every ROI's threshold together.
    - Question for Tony: has anyone already asked either of them, in any form?

## Files
- Artifact: `<worktree>/docs/learned/slow_comodulation/README.md`, `summary.json`
- Sources read (text extracts): `<scratchpad>/review2/r2/*.txt`; Schluter page render `<scratchpad>/review2/r2/schluter-2.png`; DANDI metadata `<scratchpad>/review2/r2/dandi_219_pub.json`
- In-repo files I checked against: `<worktree>/docs/learned/tube_self_supervised/README.md`, `<worktree>/docs/goals/unsupervised-learning.md`, `<worktree>/docs/todo/2026-09-10-the-dead-time-floor-is-the-producers-number.md`, `<worktree>/docs/todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md`, `<worktree>/docs/proposals/2026-09-10-surrogate-evaluation-overnight.md`, `<worktree>/tools/build_surrogate_report.py`, `<worktree>/tools/import_dandi.py`, `<worktree>/docs/detector_history.md`

Sources:
- [Schluter 1984 reprint](https://www.zoology.ubc.ca/~schluter/reprints/schluter%201984%20ecology%20variance%20test.pdf)
- [Schluter 1984, Wiley](https://esajournals.onlinelibrary.wiley.com/doi/abs/10.2307/1938071)
- [Neuronal synchrony measures, Scholarpedia](http://www.scholarpedia.org/article/Neuronal_synchrony_measures)
- [Goris et al. 2014, Nature Neuroscience](https://www.nature.com/articles/nn.3711)
- [Pipa, Riehle & Grün 2007, ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0925231206004504)
- [Harris, Nonsense correlations, bioRxiv v3](https://www.biorxiv.org/content/10.1101/2020.11.29.402719v3)
- [Ratsifandrihamanana et al. 2023, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10701450/)
- [Leprince et al., bioRxiv](https://www.biorxiv.org/content/10.1101/2025.11.27.690943v1.full)
- [Leprince et al., Current Biology](https://www.cell.com/current-biology/abstract/S0960-9822(26)00523-3?rss=yes)
- [INMED team page](https://www.inmed.fr/en/developpement-des-microcircuits-gabaergiques-corticaux-en)
- [Dard et al. 2022, eLife](https://elifesciences.org/articles/78116)
- [DANDI:000219 API](https://api.dandiarchive.org/api/dandisets/000219/)
