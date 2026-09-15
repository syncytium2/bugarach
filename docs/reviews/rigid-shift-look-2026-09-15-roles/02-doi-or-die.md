GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)

The missing tools didn't limit the check, because `grep` and `find` through Bash covered the same ground. I edited nothing in the repo. Intermediates (extracted shelf text, the Dard 2022 XML) are in `<scratchpad>/mb_scratch/role02/`.

# Role 2, citations and references: `docs/learned/rigid_shift_look/README.md` and its six figures

**What the note cites:** no external work at all. It names three methods (rigid shift, uniform dither, the circular-shift null), one dataset ("Cossart"), one outside commit (interface2) and four internal sources ("the recording-identity run", "the second review", "the screen's review", "the thresholds he signed"). None of them is linked or cited.

## Findings

**1. The Cossart data are used without citing their authors, under a licence that requires it** · **blocking** (public repo) · verified yes
- **Location:** the Cossart section heading, lines 93–131; Figures 5 and 6.
- **Issue:**
  - The folder is DANDI:000219, "Two photon calcium imaging in the CA1 region of the hippocampus in neonatal mice", licensed CC-BY-4.0 (DANDI API). DANDI's own citation reads "Dard, Robin; Picardo, Michel; Cossart, Rosa".
  - DANDI lists the paper as Dard et al. 2022, *eLife* 11:e78116, doi:10.7554/eLife.78116 (Crossref). The last author is Picardo and the second-to-last is Cossart, both at INMED U1249, Aix-Marseille.
  - The folder's own `PROVENANCE.md` says "Cite the authors, not this folder." The note shows figures derived from these data on a public page and credits no one. "The Cossart dataset" names neither the first author nor the co-senior author.
- **Fix:** at first mention, write "DANDI:000219 (Dard, Picardo & Cossart; CC-BY-4.0), from Dard et al. 2022, *eLife* 11:e78116". Put the same short credit in the captions of Figures 5 and 6.

**2. The Cossart recordings are called "slices", but they are in vivo recordings from awake pups** · major · verified yes
- **Location:** line 109 ("The ranges over slices match those over mice"); the Figure 5 axis labels ("32 mice, 59 slices" and "(59 slices)"); the thin-bar legend ("same, over slices").
- **Issue:**
  - `PROVENANCE.md` and `tools/import_dandi.py` both say "in vivo two-photon calcium imaging of CA1 in mouse pups (P5–P12)". Dard 2022 says the same.
  - "slice" comes from the export contract's `slice_id` column name. As written, the note misdescribes another group's preparation and implies it matches this lab's slices.
- **Fix:** use "recordings" or "sessions" for the Cossart folder, in the text and in the figure labels, and state once that it is in vivo imaging in awake P5–P12 pups.

**3. Rigid shift is published prior art, and the note credits none of it or says which variant it ran** · major · verified yes (shelf PDFs, installed Elephant 1.2.1 source, Crossref)
- **Location:** lines 12, 31 ("moves each ROI's whole train by one random offset within ±*J*"), and the title.
- **Lineage, traced backward:**
  - **Elephant 1.2.1:** `dither_spike_train`, which `rigid_shift` calls (`src/bugarach/surrogates.py:368-386`), calls this "spike train shifting". The module cites Gerstein 2004 and Louis 2010.
  - **Louis, Borgelt & Grün 2010**, *Analysis of Parallel Spike Trains* ch. 17, pp. 359–382, doi:10.1007/978-1-4419-5675-0_17. They call it "spike train dithering (tr-di)" and credit "Pipa et al. 2008; Harrison and Geman 2009". **Their implementation wraps on purpose** (p. 367): "in order to conserve the net time overlap … and thus not to underestimate the expected coincidence count, we actually roll the spike train."
  - **Pipa, Wheeler, Singer & Nikolić 2008**, *J Comput Neurosci* 25:64–88, doi:10.1007/s10827-007-0065-3, §2.4: "the jittering is equivalent to random shifts of an entire spike train". The authors are at FIAS / MPI for Brain Research, Frankfurt, with Nikolić as last author.
  - **Harrison & Geman 2009** (p. 1250) credit the method instead to **Pipa, Riehle & Grün 2007**, *Neurocomputing* 70:2064–2068, doi:10.1016/j.neucom.2006.10.142, where Grün is last author. So the method was carried between labs by its first author, Pipa. Crediting 2008 alone credits Frankfurt; the 2007 paper credits Grün's group.
  - **Stella, Bouss, Palm & Grün 2022**, *eNeuro* 9(3), doi:10.1523/ENEURO.0505-21.2022. They credit "dithering of the entire spike train" to Pipa 2008, run it per trial as TR-SHIFT, and rank it the most robust surrogate.
- **Issue:** the note runs a variant none of these papers tested: a single segment, no wrap, onsets pushed out of the window dropped (`edges=True`). A reader cannot tell that the evaluated surrogate is an established method, or that the published version wraps precisely to protect the counts this note measures.
- **Fix:** add one sentence of lineage to "What was measured": Pipa, Riehle & Grün 2007; Pipa et al. 2008; Louis, Borgelt & Grün 2010. Say that the published form wraps and this run does not.

**4. Two of the note's own conclusions are stated in Pipa 2008 and uncredited** · minor · verified yes (Pipa 2008 text)
- **Location:** line 140, "Shifting by 10–20 s removes all cross-ROI structure faster than that"; and the paragraph "The K scaling makes removal easy" (lines 126–131).
- **Issue:**
  - Pipa 2008 §2.4 says whole-train shifts destroy "fine temporal cross-structure on timescales faster than τr, but preserve auto-structures on all timescales". Its η = τr/τc trade-off (2–5) is exactly the timescale decision the note hands to Tony.
  - The same section says "the probability that jittering destroys JSEs increases exponentially with the complexity" (JSEs are joint-spike events). That is the K-scaling observation.
- **Fix:** cite Pipa 2008 beside both.

**5. The note cites "the second review" for one finding and leaves out another finding from the same reviewer that bears directly on its headline** · major · verified yes
- **Location:** lines 33–34, "the second review showed they see coordination under a shift".
- **What the source says:**
  - The source is the blind round of the pre-registration review, Reviewer 2: `docs/reviews/2026-09-14-preregistration-is-rigid-shift-usable-round2-roles/04-reviewer-2.md`, finding 1.
  - It is one reviewer's synthetic check (0.578–0.617 with the edge-band features, about 0.50 without) and was not reproduced. The claim is quoted accurately.
- **What is left out:** finding 6 of the same file (severity high). On interior windows, "rigid shift changes per-ROI features and occupied-frame counts only when onsets cross window boundaries … Both gates are close to guaranteed passes by construction". The look uses exactly those interior windows for "looks usable" and for the ±0.14 % count result.
- **Fix:** link the review by name. Say the edge-band result was one reviewer's synthetic check. Cite finding 6 in "What this cannot say". The statistics role owns what that finding means for the conclusion.

**6. "The screen's review found the destruction measure could not register removal on Cossart" relies on a claim a later review contradicted** · major · verified yes
- **Location:** lines 129–131.
- **Issue:**
  - The claim is traceable to `docs/reviews/report_steps_excluded_2026-09-11.md:24`.
  - The blind round's Prove It role (`…round2-roles/01-prove-it.md`, row at line 53 and finding 6) checked Cossart `destruction.csv` and found a **mismatch**. At the old settings the controls did read removal: homogeneous resample about 0, freeze-half 0.27–0.48, do-nothing 1.00.
  - The run record repeats this: "Cossart's destruction measure does register removal, contrary to the signed text."
  - "With K scaled … so here it can" therefore sets the new result against a claim that was already corrected.
- **Fix:** cite both reviews and drop the contrast, or restate it as "the earlier claim that it could not was corrected in the blind round".

**7. Uncheckable outside citation, "an interface2 commit measured real fast onset jitter at about 1 s"** · minor · verified yes
- **Location:** line 136.
- **Issue:**
  - This is interface2 commit `f76e7b1b` (2026-07-22). Its message reads "FAST (real, 85 slices): onset jitter median 1.04 s (p90 1.53) … FAST and SLOW coordination JITTER are similar (~1 s)", so the number is right.
  - interface2 is private: an unauthenticated GitLab API request returns 404. A reader of this public repo cannot follow the reference.
  - The source also says slow jitter is about 1 s, and it measured an older store of 85 slices, not the 84-recording folder.
- **Fix:** name the commit and file (`measure_coordination_timescale.m`, interface2 `f76e7b1b`) and say the repo is private. Say "both streams, about 1 s (median 1.04 s fast, 90th percentile 1.53 s)".

**8. Neither the circular-shift null nor its use on this very dataset is credited** · minor · verified yes (Dard 2022 full-text XML)
- **Location:** line 41, "above its circular-shift null"; the Cossart section.
- **Issue:**
  - Dard 2022 Methods, SCE (synchronous calcium event) detection: "an independent circular shift was applied to each cell to obtain 300 surrogate raster plots … 99th percentile". For its movement-locked histograms, "the activity of each imaged cell was translated by a randomly selected integer (between 1 and the total number of frames)".
  - So the dataset's own authors already applied per-cell whole-train shifts (wrapping, across the whole recording) to these recordings. That is the closest prior art for the Cossart run.
  - The repo's `docs/detector_history.md` traces the rule back to Cossart, Aronov & Yuste 2003, which used interval reshuffling rather than a circular shift. I did not re-read that paper.
- **Fix:** one clause, "the per-ROI circular shift that Dard et al. 2022 also used on these recordings".

**9. Uniform dither has no citation, and neither does its role as "what a leak looks like"** · minor · verified yes
- **Location:** lines 35–36; the Figure 1 legend.
- **Issue:**
  - Louis 2010 ch. 17 (p. 367): spike dithering "was introduced in (Date et al. 1998)". Date, Bienenstock & Geman 1998 is a Brown technical report on the shelf.
  - Stella 2022 (abstract): uniform dither "fails as an appropriate surrogate because it leads to a loss of spikes in the context of binning and clipping".
- **Fix:** cite Date et al. 1998 for the method and Stella 2022 for the leak.

**10. The count measure is Stella's finding, uncredited** · minor · verified yes
- **Location:** line 44, "Occupied frames per ROI per window".
- **Issue:** a count taken after binning and clipping is the binarisation Stella 2022 shows uniform dither fails on and TR-SHIFT preserves. The repo's own todo (`…count-preservation-after-encoding-is-the-gate-stella-actually-found.md`) says so.
- **Fix:** cite Stella 2022.

**11. The leak classifier is a classifier two-sample test, uncited** · minor · verified yes (shelf copy of Lopez-Paz & Oquab; docstring)
- **Location:** lines 12–13 and 31–34.
- **Issue:** `surrogate_discriminator.py` credits Friedman 2003 and Lopez-Paz & Oquab, "Revisiting Classifier Two-Sample Tests", ICLR 2017, arXiv:1610.06545. The note cites neither. Their point that the result depends on the classifier backs the note's "not detected here is not undetectable".
- **Fix:** cite Lopez-Paz & Oquab 2017.

**12. "Homogeneous resample" has a published name** · minor · verified yes
- **Location:** line 42.
- **Issue:** it is Elephant's `randomise_spikes` (`surrogates.py:764`), which is Louis 2010's "spike time randomization (sp-rnd)".
- **Fix:** give the published name in parentheses.

**13. The Cossart folder is not the whole dataset, and neither the note nor the folder says which version or why** · minor · verified yes
- **Location:** line 96, "59 recordings from 32 mice".
- **Issue:**
  - DANDI:000219 version 0.260826.1155 holds 62 assets from 35 subjects. Dard 2022 reports "62 imaging sessions, 35 mouse pups".
  - Three sessions are missing from the raw `manifest.csv`: `sub-210226-210307-1 …a000`, `sub-210226-210308-1 …a000` and `sub-200108-200117-1 …a001`, all behavior+image+ophys.
  - `PROVENANCE.md` records no DANDI version and no reason for the gap.
  - Under the export-folder rule this is a question for the producer, not a filter to add. For citation purposes, "the Cossart dataset" overstates what was read.
- **Fix:** write "59 of the 62 published sessions". Ask the producer (the importer's author) to add the version and the reason to `PROVENANCE.md`.

**14. On Cossart, "onsets" and "occupied frames" are the authors' inferred activity, not raw events** · minor · verified yes (Dard 2022 text; Crossref)
- **Location:** lines 95–110.
- **Issue:**
  - Dard 2022: "Activity inference was done using DeepCINAC classifiers (Denis et al., 2020) … a 0.5 threshold … considering a neuron as active from the onset to the peak of a calcium transient".
  - DeepCINAC is Denis, Dard, Quiroli, Cossart & Picardo 2020, *eNeuro* 7(4), doi:10.1523/ENEURO.0038-20.2020.
  - `tools/import_dandi.py` still says "Which step, this importer does not claim to know". The paper answers that.
- **Fix:** one clause in the note, "active frames as inferred by DeepCINAC (Denis et al. 2020)". Correct the importer's docstring in its own PR.

**15. The untested guess about Cossart leaving out a cause the dataset's own paper documents** · minor · verified yes (text); what it does to the leak is not measured
- **Location:** lines 121–124, "One untested guess … slow drift is moved in time".
- **Issue:** Dard 2022 reports movement-locked activation in pups younger than P9 ("both pyramidal cells … and interneurons … were activated during movement"). These are awake, behaving animals, so behavioural state is a documented source of nonstationarity within a recording, alongside drift.
- **Fix:** name movement epochs (Dard 2022) beside drift as a candidate cause.

**16. Internal attributions are unlinked; one misstates who decided what** · minor · verified yes
- **Checked and correct:**
  - "The recording-identity run" is `docs/learned/recording_identity.md:161-162`, which says "DI baselines are the least stationary" in slow. That matches, but it is not linked.
  - "The thresholds he signed" is `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`, not linked.
  - "Tony asked whether it works on the Cossart dataset" matches the board: *"Does it work on the cossart dandiset?"*
- **Misstated:** line 3, "Tony set the pre-registration machinery aside for one figure he reads himself". The board (`docs/SESSIONS.md`, the rigid-shift-look block) records that the session **offered** one exploratory figure instead, and Tony answered *"Yep. Overnight run."* I found nothing on record for "he reads himself".
- **Fix:** link all four sources. Write "offered one exploratory figure in place of the pre-registration; Tony agreed (2026-09-14)".

## Where the backward traces stopped
- **Rigid shift:** at Pipa, Riehle & Grün 2007 and Pipa & Grün 2003, *Neurocomputing* 52–54:31–37, doi:10.1016/S0925-2312(02)00823-8. Both are closed access. OpenAlex has no abstract and ScienceDirect returned 403. So the 2007 attribution rests on Harrison & Geman's secondary reading, one step short of the root.
- **Uniform dither:** at Date et al. 1998, which is held; I read only the passage Louis quotes.
- **Circular shift in calcium imaging:** at Dard 2022, read. The 2003 Yuste-lab root comes from the repo's own trace and I did not re-read it.
- **Classifier two-sample test:** at Lopez-Paz & Oquab 2017, read. Friedman 2003 was not re-read this round.

## Literatures searched, and not searched
- **Searched:**
  - Spike-train surrogates: Louis ch. 17, Pipa 2008, Harrison & Geman 2009, Stella 2022, Date 1998 and the Elephant source.
  - The DANDI record and Dard 2022 full text, including forward to DeepCINAC.
  - Classifier two-sample tests (shelf).
  - A web search for later Grün-lab applied work with trial shifting. It found only SPADE 2017 and Stella 2022 / its bioRxiv preprint, so "no later applied paper" is **not** established.
  - A web search on circular-shift nulls in calcium imaging. It found Huang et al. 2026, *eNeuro* 13(1), doi:10.1523/ENEURO.0378-25.2025, which mentions circshift but not drift. I saw only a summary of it.
- **Not searched (residual ⚠):**
  - Pipa's own later work after 2008.
  - Pazienti et al. 2007 and 2008 on how dithering destroys coincidences. This bears on "looser events are harder to remove", and neither paper is held.
  - Surrogate testing in nonlinear dynamics (Theiler 1992 onward).
  - Toroidal-shift nulls in ecology.
  - Harris 2021 on nonsense correlations (on the recombination shelf, unread for this note), for the drift explanation.
  - Real-versus-synthetic discriminator scores in time-series generative modelling.

## Residual ⚠: nobody was asked
I found no correspondence with Grün's or Pipa's groups about whole-train shifting without wrap on trial-less recordings; `docs/todo/2026-09-11-elephant-surrogate-defects-are-not-filed-upstream.md` is still open. I found none with Dard, Picardo or Cossart about the three sessions missing from the import or about the surrogate they used. **The main thread should ask Tony whether any of these conversations exist**, and cite them as dated personal communications rather than quoting them.

## Outside this artifact, for the main thread
- `docs/learned/recombination_nulls_reading_log.md:197-198` still says rigid shift is "what Louis 2010 recommends and what Stella et al. 2022 found most robust". Both of those endorse the wrapped or per-trial variants. Round 1 of the pre-registration review flagged this line, and it has not been corrected.
- For the counting role: the note gives the typical Cossart recording as 12,634 frames, but the raw manifest's median is 12,500 frames. I did not work out which definition the note used.

Sources:
- [DANDI:000219 API record](https://api.dandiarchive.org/api/dandisets/000219/)
- [Dard et al. 2022, eLife 11:e78116](https://elifesciences.org/articles/78116) ([JATS XML](https://cdn.elifesciences.org/articles/78116/elife-78116-v2.xml))
- [Stella et al. 2022, eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0505-21.2022), [PMC9186111](https://pmc.ncbi.nlm.nih.gov/articles/PMC9186111/), [bioRxiv](https://www.biorxiv.org/content/10.1101/2021.08.24.457480v1.full)
- [SPADE, Quaglio et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5443150/)
- [Huang et al., eNeuro ENEURO.0378-25.2025](https://www.eneuro.org/content/13/1/ENEURO.0378-25.2025)
- [Circular shift method figure (ResearchGate)](https://www.researchgate.net/figure/Circular-shift-method-A-B-To-create-a-null-distribution-the-neural-data-is_fig3_347273052)
- Crossref records for doi:10.7554/eLife.78116, 10.1523/ENEURO.0038-20.2020, 10.1016/j.neucom.2006.10.142, 10.1016/S0925-2312(02)00823-8, 10.1007/s10827-007-0065-3, 10.1523/ENEURO.0505-21.2022, 10.1007/978-1-4419-5675-0_17
- Shelf PDFs under `<darkroom>/bugarach/lit/surrogates/` (Louis ch. 17, Pipa 2008, Harrison & Geman 2009, Stella 2022, Date 1998) and `lit/ml/lopezpaz_oquab_2017_c2st.pdf`
