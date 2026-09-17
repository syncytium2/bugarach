GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash, WebSearch, WebFetch)

This is a finding about the run, not about the page. I ran every search with `grep`, `git grep` and `find` through Bash, so the checks still happened, but the run record should say the review used a fallback grant.

# Citation and reference review: `docs/learned/slow_comodulation/README.md`, round 1

Artifact: `<worktree>/docs/learned/slow_comodulation/README.md` (commit 8ba5f57 on `unsup/slow-comodulation`), with `fig3_recordings.png` and `summary.json` opened.

**Headline:** the page cites no published work at all. Its central points are old and well documented: shared rate change raises coincidences near zero lag, a linear trend gives a flat elevated correlogram, and a whole-train shift smooths rates on the scale of its width. Several of those papers are already shelved and read in this repo. The page never claims novelty in words, but its naming (a coined statistic, "shoulder", "block control") and its "What this changes" section read as a first discovery. It also plots and tabulates a third-party CC-BY dataset without crediting its authors.

## Findings

**1. The Cossart folder is used without crediting the data's authors.**
- **Location:** Figure 3 caption, the recordings table, panel C header ("C. Cossart folder · 59 recordings, 32 mice"), "Cossart's shoulder" paragraph.
- **Issue:** the page and figure use DANDI:000219, which is licensed CC-BY-4.0. The repo's own importer writes into PROVENANCE.md: *"Cite the authors, not this folder."* Neither the page nor `summary.json` names the authors, the paper or the dandiset.
- **Severity:** blocking. The repo is public, and CC-BY requires attribution.
- **Fix:** at first mention, write something like "in vivo two-photon imaging of CA1 in neonatal mice (P5–P12) from Dard et al. 2022, *eLife* 11:e78116, doi:10.7554/eLife.78116; data DANDI:000219 (Dard, Picardo & Cossart), CC-BY-4.0". Put the short credit in the Figure 3 caption too.
- **Verified:** yes. I checked the DANDI API record (licence, contributors, "IsPublishedIn" eLife 78116), the eLife page (authors, volume, article number, DOI, 2022-07-20), and `tools/import_dandi.py` lines 186–191.

**2. "Cossart" names one principal investigator, not the laboratory or the authors.**
- **Location:** throughout the page and Figure 3.
- **Issue:** the lab is the last author plus the affiliation. The paper's last author is **Michel A. Picardo** and Cossart is second to last. Both are at INMED (INSERM U1249, Aix-Marseille). The dandiset lists Dard, Picardo and Cossart.
- **Severity:** minor ("Cossart folder" is the repo's internal folder name).
- **Fix:** keep the folder name for the code, but on the page write "the Dard et al. 2022 dataset (INMED)" or "DANDI:000219".
- **Verified:** yes (eLife author list and affiliations, DANDI contributors).

**3. The page compares folders without saying they are different preparations and different event landmarks.**
- **Location:** "Every folder has both a peak and a shoulder"; "on Cossart it takes about 3 s to fall to zero".
- **Issue:** the importer's PROVENANCE says DANDI:000219 is in vivo neonatal CA1. Its `time_sec` is "the first frame of an inferred active run — NOT a `t50rise`", and it warns that timing agreement between the two corpora "is not available". The page compares peak widths and dips across folders without either caveat. The published paper also ties this activity to self-motion; its title is about disengaging "from self-motion". That is a documented candidate source of shared slow structure in this folder, which the page's drift-source paragraph (written only for slices) leaves out.
- **Severity:** major.
- **Fix:** add one sentence on the preparation and the landmark difference. Limit Cossart-versus-lab comparisons to shape, not lag in seconds. In the "where the drift comes from" paragraph, note that in the Dard data, behaviour is a published candidate.
- **Verified:** yes for the PROVENANCE text. For the self-motion link, only the title and abstract level.

**4. The recording count omits three sessions.**
- **Location:** "The Cossart folder: 59 recordings".
- **Issue:** the 2026-09-15 citation review of the rigid-shift look found 59 of the 62 published sessions. This page does not mention the three missing sessions.
- **Severity:** minor.
- **Fix:** write "59 of the 62 published sessions", as that review recommended.
- **Verified:** no. I took this from the prior review record (`docs/reviews/rigid-shift-look-2026-09-15-roles/02-doi-or-die.md`, line 106) and did not recount.

**5. The central phenomenon is uncited: shared rate change inflates coincidences.**
- **Location:** "The problem", "How to read the measurement", Figure 1 prose ("Shared modulation creates sub-second coincidences too"), the "shoulder" bullets, "a trend across the whole window reads as a shoulder".
- **Issue:** these are well documented, and the page gives no source for any of them:
  - **Perkel, Gerstein & Moore 1967**, p. 428: shared rate changes of otherwise independent neurons give "an elevation above its 'null' level (that expected for independent cells)" around the origin. The same page says "Linear trends result in a uniformly elevated cross correlation, which remains flat". That is exactly the page's "shoulder not yet fallen at 5 minutes".
  - **Amarasingham et al. 2012**: "slow and common fluctuations also produce similar zero-lag counts".
  - **Brody 1999a**: covariation in excitability produces correlogram peaks that look like synchrony.
  - **Yule 1926**, restated for neuroscience by **Harris 2021**: shared slow trends produce "nonsense correlations".
  - The repo already holds this lineage. The reading log calls a shared within-recording time course "the single best-documented way recombination nulls lie (Perkel p. 428; Harris; Tyrcha et al. 2013)".
- **Severity:** major.
- **Fix:** add a short "Published lineage" section:
  - Perkel, Gerstein & Moore 1967, *Biophys J* 7:419–440, doi:10.1016/S0006-3495(67)86597-4, p. 428 and Fig. 4
  - Brody 1999a, *Neural Comput* 11:1537–1551, doi:10.1162/089976699300016133
  - Amarasingham, Harrison, Hatsopoulos & Geman 2012, *J Neurophysiol* 107:517–531, doi:10.1152/jn.00633.2011
  - Harris 2021, bioRxiv doi:10.1101/2020.11.29.402719 (a preprint)
  
  Say plainly that what is new here is the measurement on these recordings, not the phenomenon.
- **Verified:** yes. I read the passages in the shelved PDFs and checked the DOIs on Crossref. Yule 1926 (*J R Stat Soc* 89:1–63) is verified only through Harris's reference list, not read.

**6. The "excess coincidence" statistic is a standard normalised cross-correlogram, presented as a coined term.**
- **Location:** "How to read the measurement".
- **Issue:** dividing the observed count by the count expected under independence at each ROI's observed total is Perkel et al.'s "null level … predicted expected level for stationary independent processes, based upon observed mean firing rates" (their Equation 3). The page gives the construction a new name and no origin.
- **Severity:** minor.
- **Fix:** "the cross-correlogram normalised by its independence level (Perkel, Gerstein & Moore 1967)". Keep the house name only as a label.
- **Verified:** partly. I read the p. 428 text and the Fig. 4 caption that refer to Equation 3, not Equation 3 itself.

**7. Rigid shift is used without attribution, and one of its "facts" is already published.**
- **Location:** "The problem" (definition), Figure 2 prose, and the second bullet ("Rigid shift removes modulation only on timescales shorter than about *J*").
- **Issue:** no attribution. Louis, Borgelt & Grün 2010, §17.3.3 ("spike train dithering"), state: "Interspike intervals are fully maintained, and firing rates are smoothed on the timescale of the dither width". That is the page's second fact. Louis et al. credit Pipa et al. 2008 and Harrison & Geman 2009. Harrison & Geman 2009 (p. 1250) relate it to "the resampling method in Pipa, Riehle, and Grün (2007), which can be sampled by uniformly jittering each spike by the same amount". Stella et al. 2022 call it trial shifting and rank it most robust, at a 25 ms dither.
- **Severity:** major.
- **Fix:** attribute rigid shift to that chain and cite Louis 2010 for the smoothing property. Say that the page's use differs from the published form in two ways:
  - it drops and trims where Louis et al. roll the train;
  - it shifts a whole recording by 10–20 s where the published regime is 25 ms.
- **Verified:** yes for Louis, Harrison & Geman and Stella (shelved PDFs). Pipa, Riehle & Grün 2007 and the multiple-shift paper by Grün et al. 1999 are closed access and unread, so the trace stops one step short of the root.

**8. The 2-minute block control is presented as a new design, and its lineage goes unmentioned, including the detector the page uses.**
- **Location:** the Figure 2 caption, the ⚠ paragraph below it, and the table rows.
- **Issue:**
  - **Published lineage.** Holding each ROI's count fixed within fixed windows and randomising timing inside them is the idea behind interval (window) jitter: Date, Bienenstock & Geman 1998; Amarasingham et al. 2012. Harrison & Geman 2009 condition on coarse-window counts in the same way. Their reading, that a rejection means structure faster than the window, is the page's own interpretation of the block control.
  - **In-repo precedent.** **CoactDetect's own null** is "circular-shift each ROI's events WITHIN a rolling context window centred on the bin". Per `src/bugarach/detectors/coact.py` lines 7–11, that window is 60 s on the fast stream and 120 s on the slow. The block control is a fixed-block version of the null inside the detector whose episodes the page removes. By design, CoactDetect does not call structure that its local null already contains. That is a reason, which the page never states, why "unchanged by removing CoactDetect's episodes" is expected for drift slower than the context window.
- **Severity:** major.
- **Fix:** cite interval jitter (Date et al. 1998, a Brown University technical report; Amarasingham et al. 2012) as the conceptual origin. Name CoactDetect's rolling local circular shift as the same construction, and note the by-design reading next to the removal result.
- **Verified:** yes (`coact.py` docstring, `interface2/explore_sce.m` lines 1145–1149 at 80951ced, the Amarasingham 2012 text). Date 1998 is shelved; I did not read it this round.

**9. The circular-shift null is used without attribution, including the Dard dataset's own use of it.**
- **Location:** Figure 2 caption and the legend in Figure 3.
- **Issue:** no attribution. Dard et al. 2022 detect synchronous events in this very dataset with "an independent circular shift … applied to each cell to obtain 300 surrogate raster plots", thresholded at the 99th percentile. Separately, Harris 2021 shows that circular shifting gives false positives under slow drift. That is the mechanism by which the page's shoulder sits above the circular curve, so the page should say so rather than simply calling it "the null".
- **Severity:** minor.
- **Fix:** cite Dard et al. 2022 (Methods, "SCE detection"). Add one clause: under drift, circular shift is the null for "no relation", not for "no shared trend" (Harris 2021).
- **Verified:** yes (PMC full-text Methods; Harris 2021 abstract in the shelved PDF).

**10. The refractory explanation of the dip misstates its in-repo source and merges two folders.**
- **Location:** "The lab slow stream has a dip".
- **Issue:**
  - **Wrong mechanism.** The source for the floor (`docs/reviews/2026-09-10-coordination-without-labels_2026-09-10.md`, line 28) attributes it to the **event extractor**: "An event extractor cannot emit two onsets from one cell inside a single calcium transient". That is not physiological refractoriness. Stella et al. 2022 draw exactly this distinction ("a dead-time may be introduced by spike sorting. Further, the biological absolute refractory period…").
  - **Merged folders.** 3.20 s is the senktide-baseline subset. For `steps_excluded`, the folder this page analyses, the floor is **2.80 s** (`docs/proposals/2026-09-10-surrogate-evaluation-overnight.md`, line 79).
  - **Missing caveat.** The goal page's row is marked "measured by a review role — reproduce before building on it", and the page drops that.
  - **Reach.** A 2.80 s floor does not by itself reach the 5.2 s edge of the dip. Flagged for the reasoning roles.
- **Severity:** major.
- **Fix:** "the same-ROI dead time, which the source attributes to the extractor's inability to split one transient (2.80 s on this folder; measured by a review role, not reproduced)". Drop "refractory" unless the lab confirms it (FOUNDATIONS §9).
- **Verified:** yes.

**11. The "10–45 s" question is attributed to the goal page, which does not contain it.**
- **Location:** "The decision is narrower than it was framed. The goal page asks whether *shared modulation on timescales of 10–45 s* counts as coordination."
- **Issue:** the goal page has no "10–45 s" in this worktree, on `main` or on the report branch. The question is item 2 of "What waits on Tony" in `docs/learned/tube_self_supervised/README.md`, and the goal page says that report "has not been re-reviewed, so none of its numbers are quotable yet".
- **Severity:** major. It misattributes an in-repo source to a report flagged as not quotable.
- **Fix:** point to the rigid-shift report's "What waits on Tony" and carry its "not yet quotable" status.
- **Verified:** yes (grep of all three versions).

**12. The "independently confirmed" attribution cannot be checked on `main`, and the independence is not shown.**
- **Location:** "The session running the rigid-shift report confirmed this independently on synthetic recordings, 2026-09-17".
- **Issue:** the only durable record is commit 65285fa on the unmerged `origin/unsup/rigid-shift-report-residuals` (`tools/check_small_j_mixes_events.py`). It measures something else: a 10 s `slow_modulation` scorer at AUC 0.669 on events-only synthetic recordings against 0.522 on shared modulation alone. It credits the argument to an unnamed "reviewing session". If that session was this page's, the check tests this page's hypothesis and does not confirm it independently.
- **Severity:** minor.
- **Fix:** cite the commit and tool and the two AUCs, and drop "independently" unless the arguing session is named.
- **Verified:** partly (commit and docstring read; the session's identity is not established).

**13. `count_excess` is defined only on an unmerged branch.**
- **Location:** "Removing a local background removes drift".
- **Issue:** the definition ("that share minus its own 30 s moving mean", 301 frames) exists only on `unsup/rigid-shift-report-residuals`, in `tools/tube_self_supervised.py` line 514 and its GLOSSARY. It is not in this worktree's copy of that tool (which the page's own measurement imports) and not on `main`.
- **Severity:** minor.
- **Fix:** land after PR #603, or cite the branch and commit.
- **Verified:** yes.

**14. The page ignores the repo's own earlier writing on the same problem.**
- **Location:** "The benchmark has never contained any of this" and the Figure 1 prose on the simulator.
- **Issue:** `docs/todo/2026-09-12-evidence-before-more-effort-on-the-roi-swap.md` (line 62) already lists "Slow drift shared by every ROI across a whole recording; bleaching; field steps" as absent from the simulator. The reading log (lines 193–196) already calls a shared within-recording time course the best-documented failure. The page cites neither.
- **Severity:** minor.
- **Fix:** link both. The page's contribution is the measurement, and the prior framing belongs beside it.
- **Verified:** yes.

**15. "This page does not measure the count's variance" understates what the literature supplies.**
- **Location:** "Pairs, not counts" and "Cossart's shoulder … (argued)".
- **Issue:** the conversion from correlogram to count covariance is published. Brody 1999a gives it as eq. 3.6 and rule of thumb 3: the covariogram integral is proportional to the count covariance. Kass & Ventura 2006 show count correlation grows with window length under shared slow variation, which is the page's "the shoulder holds most of the excess".
- **Severity:** minor.
- **Fix:** cite both, and say the count variance is derivable from the pooled correlograms even though the page does not compute it.
- **Verified:** yes for Brody (trial-based setting) and Kass & Ventura 2006 (doi:10.1162/neco.2006.18.11.2583). For continuous recordings, the usual source for the triangle-weighted form is Bair, Zohary & Newsome 2001, *J Neurosci* 21:1676–1697, which I found by search but **did not read**.

**16. The "explore_sce viewer's slow settings" point to a private repository.**
- **Location:** "CoactDetect removal is partial by construction".
- **Issue:** the values are correct: 1 s bins, 120 s context, α = 1e-6, min_rois 3 (default and slider). But the viewer lives in the private interface2 repository, so a public reader cannot check them. The page also never gives the fast stream's point (2 s / 60 s / 1e-4, `bench.OPERATING_POINTS['coact']`).
- **Severity:** minor.
- **Fix:** cite `src/bugarach/detectors/coact.py` (docstring lines 84–87) and `src/bugarach/bench.py` (the `coact` entry), and state both streams' settings.
- **Verified:** yes (`explore_sce.m` lines 1145–1149, `coact.py`, `bench.py`, `summary.json` `coact_params`).

**17. The FOUNDATIONS §9 paraphrase is loose.**
- **Location:** "FOUNDATIONS §9 sends such questions to the lab".
- **Issue:** §9 says preparation facts "are not bugarach's to derive" and names global `syncytium2/foundations` §15 as the authority. Questions about extraction (baseline F estimate, thresholds) belong to the producer under the export-folder rule in CLAUDE.md.
- **Severity:** minor.
- **Fix:** "preparation questions go to global FOUNDATIONS §15 (§9 here); extraction questions are a conversation with the producer".
- **Verified:** yes.

**18. Checked and correct.** No change needed for these:
- **Simulator quote:** "a busy stretch belongs to a cell, not to the whole field" appears at `src/bugarach/simulate.py` lines 762–763 (a comment split over two lines), and the file has no shared-modulation option.
- **Rigid shift as described:** matches `rigid_frames` (`tools/tube_self_supervised.py` lines 97–104).
- **Three-ROI floor:** CoactDetect's `min_rois=3`.
- **Group and imaging day:** the INDEX ROI-swap row says group is nested in imaging day (42 dates, none with more than one group), consistent with `recording_identity.md` line 87.
- **Goal page floor values:** the goal page does record both 2.80 s and 3.20 s (see the refractory finding for the merge).
- **Verified:** yes.

**19. Outside this artifact: an error in the rigid-shift report the page may copy.**
- **Location:** `docs/learned/tube_self_supervised/README.md`, lines 415–416.
- **Issue:** it says "no source reached attributes train shifting to" Pipa, Riehle & Grün 2007. The shelved and read Harrison & Geman 2009 (p. 1250) does relate uniform whole-train jitter to that paper. The 2026-09-15 citation review reported this too. It matters here if the lineage section asked for above is copied from that report.
- **Severity:** minor for this page; it belongs to that report's review.
- **Fix:** do not copy that sentence. Correct it in the report's own thread.
- **Verified:** yes.

## Where each origin trace stopped
- **Shared rate change inflating the correlogram:** the root is Perkel, Gerstein & Moore 1967, p. 428, read. I did not follow its "details will be presented elsewhere" onward.
- **Nonsense correlations:** stopped at Harris 2021 (read). Yule 1926 is verified only from Harris's reference list (unread), and the econometrics sources he names (Granger & Newbold 1974 and others) were not traced.
- **Whole-train shift:** stopped one step short of the root. Pipa, Riehle & Grün 2007, and Grün et al. 1999 are closed access and unread.
- **Interval jitter:** Date, Bienenstock & Geman 1998 is shelved but I did not reread it.
- **Circular shift in calcium imaging:** stopped at Dard 2022 (read). Earlier INMED uses and the CICADA code were not traced.
- **Forward trace:** checked Harris 2021 forward to Harris 2020, arXiv:2012.06862, "A Shift Test for Independence in Generic Time Series". Its linear shift of one series within a central segment is the closest published relative of this page's trimmed, non-wrapping rigid shift. I did not trace Stella 2022 forward into Elephant's later surrogates. The tube report says Elephant's `dither_spike_train` does not wrap; I did not check that.

## Literatures searched
- **Searched:**
  - Spike-train correlation and surrogate methods, from shelved PDFs in `<darkroom>/bugarach/lit/surrogates/`: Perkel 1967, Brody 1999a, Kass & Ventura 2006, Amarasingham 2012, Harrison & Geman 2009, Louis 2010 chapter 17, Stella 2022.
  - Time-series nonsense correlations: Harris 2021 and 2020.
  - Calcium-imaging synchronous-event detection: Dard 2022 Methods.
  - Calcium-imaging signal contamination: Gauthier et al. 2022, *Nat Methods* 19:470–478, doi:10.1038/s41592-022-01422-5. Abstract only. It concerns fluorescence misattributed between cells, a possible measurement-side source of shared events, and is not cited as support.
- **Not searched (⚠ residual):**
  - Cortical-state and shared-gain work on slow shared variability (for example Goris, Movshon & Simoncelli 2014; Ecker et al. 2014; Okun et al. 2015 on population coupling). These are named from memory and unverified; do not cite them without fetching.
  - Refractoriness after network bursts in slices, cultures and developing hippocampus, which bears on the dip.
  - Drift in functional connectivity and the global signal in fMRI.
  - Econometric cointegration and spurious regression.
  - Block-permutation and exchangeability-block designs in statistics. Winkler 2014 is shelved in `lit/recombination/` and was not opened.

## What people might already know (⚠ residual)
- **The producer:** I found no record in the tree that anyone asked the lab whether shared drift over minutes could come from the measurement: focus or slice-position change, bleaching, or the baseline-F estimate. Earlier docs only list those as possibilities.
- **The Dard dataset:** no record of anyone asking Dard, Picardo or Cossart about slow drift in DANDI:000219 (the 2026-09-15 review found the same).
- **Tony:** ask him whether either conversation has happened off the record. If it has, cite it as "*name*, personal communication, *date*" and do not quote it.

Scratch files (paper text extracts only) are in `<scratchpad>/review/lit/`. I did not edit anything in the repo.

Sources:
- [DANDI:000219 metadata](https://api.dandiarchive.org/api/dandisets/000219/versions/draft/info/)
- [Dard et al. 2022, eLife 11:e78116](https://elifesciences.org/articles/78116)
- [Dard et al. 2022, PMC full text](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9363116/)
- [Harris 2020, arXiv:2012.06862](https://arxiv.org/abs/2012.06862)
- [Harris, Nonsense correlations in neuroscience, bioRxiv](https://www.biorxiv.org/content/10.1101/2020.11.29.402719v3)
- [Gauthier et al. 2022, Nature Methods](https://www.nature.com/articles/s41592-022-01422-5)
- [Bair, Zohary & Newsome 2001, J Neurosci (search result only, not read)](https://www.jneurosci.org/content/21/5/1676)
- [Crossref API](https://api.crossref.org/works) (DOI checks: Perkel 1967 part II, Brody 1999a and 1999b, Kass & Ventura 2006, Amarasingham 2012)
