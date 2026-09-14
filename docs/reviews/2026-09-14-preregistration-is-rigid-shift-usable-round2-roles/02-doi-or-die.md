GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)

The missing tools didn't block anything. I searched with `grep`/`git grep` through Bash instead.

# Role 2, citations and references ("DOI or Die"), blind pass on blob 2c9813d

The page contains almost no formal citations. These findings cover the attributions behind it: the methods the amendments adopt, the internal sources it links, and the exploratory numbers it quotes.

**What I was exposed to.** I opened the rigid-shift and joint-ISI rows of `<darkroom>/bugarach/2026-09-11-surrogate-screen/discriminator/*/discriminator.csv` to check the numbers the page quotes. Where a finding below mentions another exploratory outcome, the page or a todo it links already implies it. I opened no `docs/reviews/` file.

## Findings

**1. The leak bootstrap is credited to a function that does something different** · major · verified yes
- **Location:** the signed text, lines 87–88 ("the recording-identity run's `mouse_bootstrap`"), and the amendment's "The bootstrap refits", lines 263–266.
- **Issue:**
  - `mouse_bootstrap` (`tools/measure_recording_identity.py:189`) gives a two-sided 95 % percentile interval. It resamples mice over per-pair correctness from a single fixed cross-validation fit. It never refits.
  - The amendment specifies a different method: refit per resample, a duplicated mouse kept inside one fold, a fresh fold seed each time.
  - That method is **bootstrap case cross-validation**, applied at the mouse level: Jiang, Varma & Simon 2008, *Stat Appl Genet Mol Biol*, doi:10.2202/1544-6115.1322. I read their text. It says the method modifies Fu, Carroll & Wang 2005, *Bioinformatics* 21:1979–1986. I took that citation from Jiang's reference list and did not open the paper.
  - The page cites neither paper, and the build list (lines 165–170) does not include this bootstrap.
- **Fix:** a dated amendment that names the method and cites Jiang 2008. It should also retire the `mouse_bootstrap` pointer and add the refitting bootstrap to the build list, with a test.

**2. The adopted method's documented bias pushes toward PASS, and no control would detect it** · major · verified yes (text); the consequence is my reasoning, not a measurement
- **Location:** the leak gate amendments, lines 259–269.
- **Issue:**
  - Jiang 2008 says each resample trains on only about 0.632(n−1) distinct units, which "leads to an overestimation on the true prediction error" and so to conservative intervals.
  - That is conservative when you want to claim a classifier works. This gate claims the opposite, that the classifier fails, so the same bias pulls accuracy toward 0.5 and toward PASS. The wider interval pulls the other way, and the net effect is not measured.
  - Neither control is sensitive to it. Uniform dither sits far above 0.55, and the can-pass check has a true accuracy of 0.5.
- **Fix (the statistics role owns the remedy):** report the full-data cross-validated accuracy beside the bootstrap percentile and require both to be below 0.55. Alternatively, add a planted leak near the margin as a graded positive control.

**3. The same data were used to choose the displacement and to test it** · major · metadata verified; only abstracts read for these papers
- **Location:** line 43 ("What protects this run is a fixed rule and fresh randomness") and lines 328–329 (how a result may be reported).
- **Issue:**
  - The smallest *J* in each stream was chosen by the leak criterion on these same recordings. The page's line 325 and the join todo already imply that every other declared slow and Cossart displacement leaked in the exploratory run.
  - So a leak PASS will most likely come from exactly the selected cell. There the test is not independent of the selection: Kriegeskorte et al. 2009, *Nat Neurosci* 12:535–540, doi:10.1038/nn.2303.
  - Fresh seeds and folds protect against a lucky seed, not against selection.
  - The literature on pre-registering analyses of existing data supports the disclosure the page already makes: Nosek et al. 2018, *PNAS*, doi:10.1073/pnas.1708274114; Weston et al. 2019, *AMPPS* 2:214–227, doi:10.1177/2515245919848684.
- **Fix:** the reporting sentence should add "at a displacement selected on these recordings by the same leak criterion", with those citations.

**4. The stated reason for the slow displacements does not match the grid** · minor · verified yes
- **Location:** line 70, "the same logic on the slow grid".
- **Issue:**
  - The slow grid is (0.7, 1.4, 2.5, 2.8, 5.6, 11.2), per `tools/build_surrogate_screen.py:62-63`. The next step after 1.4 s is 2.5 s, not 2.8 s; 2.8 s is double 1.4 s.
  - The fast set (1.6, 2.5, 5.0) and the Cossart set (4, 8, 16 frames) do follow the stated logic.
- **Fix:** a dated amendment that corrects the reason. The displacements themselves stay as signed.

**5. A quoted accuracy range is narrowed wrongly** · minor · verified yes
- **Location:** line 31, "Its fast accuracies there were 0.495–0.524".
- **Issue:** the source todo (`126-fast-candidates-were-voided…`) gives that range across all six fast displacements. The 0.524 comes from 2.5 s, which is outside "to 1.6 s", so the word "there" is wrong.
- **Fix:** say "across all six fast displacements".

**6. The joint-ISI correction is right, but the fast rows were voided and the todo it corrects is still wrong** · minor · verified yes
- **Location:** lines 345–346.
- **Issue:**
  - `discriminator.csv` confirms the amendment: 12 rows at fast 2.5 s and 24 at slow 5.6 s and 11.2 s, all flagged.
  - The fast rows carry the same seed-0 void that the page notes for rigid shift. The amendment does not say so.
  - The linked todo `docs/todo/2026-09-12-joint-isi-dithering-is-unmeasured-not-failed.md` still says every cell was skipped.
- **Fix:** add "fast rows voided by the seed-0 defect", and correct the todo in the same commit.

**7. Rigid shift has no cited origin, and the page runs a different variant from the published one** · minor · verified yes (shelf PDFs and installed Elephant 1.2.1 source)
- **Location:** lines 17–18 and 25–38.
- **Issue:**
  - **Code matches the description.** Elephant 1.2.1 `dither_spike_train` with `edges=True` drops onsets pushed outside the range. With `edges=False` it clamps them to the range ends; neither setting wraps. `rigid_shift` (`src/bugarach/surrogates.py:368`) uses `edges=True`, so "nothing wrapped" is accurate.
  - **Lineage, traced backward.**
    - Stella et al. 2022 credit whole-train dithering to Pipa et al. 2008.
    - Pipa 2008 credits the multiple-shift method to Grün et al. 1999. I did not get that paper, so the trace stops one step short of the root.
    - Louis, Borgelt & Grün 2010 (chapter 17 of *Analysis of Parallel Spike Trains*) describe the same method as "spike train dithering". Their implementation **wraps on purpose**, "to conserve the net time overlap … and thus not to underestimate the expected coincidence count".
  - So the count loss this page gates on is the published reason for wrapping, and the page runs Elephant's non-wrapping default instead.
- **Fix:** one sentence of lineage citing Pipa 2008 and Louis, Borgelt & Grün 2010, saying the published version wraps to preserve counts and this run does not.

**8. The 1 s bin is a code default, not a definition of "coordinated"** · minor · verified yes
- **Location:** lines 119–122 ("the assessor's own definition") and line 290.
- **Issue:**
  - The 2 s slow default (`measure_coordination_timescale.m:33`) is correct.
  - Traced back in interface2: the 2 s slow bin arrived in commit bf0ca990 (2026-07-21), commented "coarse coactivity bin (SLOW is seconds-scale)". The 1 s fast bin arrived in f76e7b1b (2026-07-22), commented "finer bin for the faster stream". Neither has a measurement or citation behind it, and the trace stops there.
  - The Python port calls 1.0 s "a convention" (`src/bugarach/assess.py:394`).
  - Commit f76e7b1b also measured real onset jitter at a median of 1.04 s on the fast stream (90th percentile 1.53 s). The destruction twins plant 1-frame jitter instead. That is a design question for the destruction role.
- **Fix:** call it "the assessor's default bin, a convention" rather than a definition.

**9. "Uniform dither is known to leak" has no source** · minor · partly verified
- **Location:** line 34, and the positive control's rationale.
- **Issue:** sources exist and none is cited:
  - Stella et al. 2022 (on the shelf): onsets lost when dithered times are binned, and altered interval distributions.
  - Gerstein 2004: dither adds short intervals. The shelf README records only its title and abstract as read; I did not open it.
  - The project's own exploratory positive control.
- **Fix:** cite these.

**10. The classifier two-sample test is uncited on the page** · minor · verified yes for Lopez-Paz & Oquab; Kim metadata only; Friedman not retrieved
- **Location:** lines 84–86 and 333–334.
- **Issue:**
  - The module docstring cites Friedman 2003 and Lopez-Paz & Oquab 2017; the page cites neither.
  - Lopez-Paz & Oquab (shelf copy) name Friedman 2003 as the origin. They also note that generators of different quality can reach the same C2ST (classifier two-sample test) score. That supports the page's narrow claim for a PASS.
  - Traced forward: Kim, Ramdas, Singh & Wasserman 2021, *Ann Stat* 49(1):411–434, doi:10.1214/20-AOS1962.
  - The backward trace stops at Friedman 2003, which I did not retrieve.
- **Fix:** cite Lopez-Paz & Oquab 2017 in the "What a PASS may claim" leak line.

**11. The equivalence test is described correctly but uncited** · minor · metadata and abstract verified
- **Location:** line 280, "equivalence by two one-sided tests at 0.05/3 each".
- **Issue:**
  - The correspondence is right: two one-sided tests at α are equivalent to a (1−2α) interval, which here gives 96.67 %. The reference is Schuirmann 1987, *J Pharmacokinet Biopharm* 15:657–680, doi:10.1007/BF01068419.
  - One caveat for the statistics role: the ±2 % margin is estimated from the data, while the standard test assumes a fixed margin.
- **Fix:** cite Schuirmann 1987.

**12. The two-level destruction bootstrap is uncited** · minor · verified yes
- **Location:** lines 296–297.
- **Issue:** Saravanan, Berman & Sober 2020 (on the shelf, arXiv:2007.07797) is the neuroscience reference for resampling at both levels. With only 5 twins at the top level, its discussion of few subjects applies.
- **Fix:** cite it.

**13. The Cossart data are not cited** · minor · verified yes
- **Location:** line 55.
- **Issue:**
  - DANDI:000219 comes from Dard et al. 2022, *eLife* 11:e78116, doi:10.7554/eLife.78116.
  - The corresponding authors, listed last, are Cossart and Picardo, at INMED Marseille. So calling it the Cossart lab's data holds, though Picardo shares that position.
  - `tools/import_dandi.py` records the licence as CC-BY-4.0, so attribution is needed before any result reaches an outside reader.
- **Fix:** cite the dataset and the paper.

**14. One option attributed to the tube todo is not in it** · minor · verified yes
- **Location:** line 150.
- **Issue:** "or normalise the count across ROIs away" does not appear in the tube todo. The todo offers keeping the cell axis, or an explicit argument that collapsing it is safe. The amendment's requirement for an aggregate-channel leak test (lines 347–348) does match the todo.
- **Fix:** mark the normalisation option as this page's own, or drop it.

**Checked and clean:**
- The one-sided Bonferroni percentiles (0.05/3 gives the 1.67th and 98.33rd).
- The negative-control odds: 7.5 % for three or more of 20 seeds, 1.6 % for four or more. This assumes the seeds are independent, but they share windows; that is for the statistics role.
- The leak margin: `MIN_EFFECT = 0.55` in the code.
- The edge-thinning control: at 5 s it loses J/(2W) = 4.2 % of onsets. It is generated per analysis window, so interior windows see the loss.
- FOUNDATIONS §9 does cover baseline-only data and keeping zero-event ROIs.
- The K = 4 used by the freeze-half control is in the default scan (3, 4, 6, 8).
- The claim that exploratory results existed at every declared cell except fast 5.0 s.

**Freeze-half, a note on its origin:** it comes from `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md:227`. The exploratory run applied it to circular shift (`build_surrogate_screen.py:120-126`). The amendment moves it onto homogeneous resample, so the 0.10–0.90 band was set without an exploratory value. I found no external source for it.

**For another role (not verified):** "interior" is defined against the recording (line 219), but surrogates are generated over `rec.window` (`surrogate_stats.py:966`). If that window is the baseline region, the edge loss sits at the region's edges, not the recording's.

## Literatures searched and not searched
- **Searched:**
  - The shelf's surrogate papers (Pipa 2008, Louis chapter 17, Stella 2022), the ML shelf (Lopez-Paz & Oquab), and the recombination shelf (Saravanan).
  - On the web: equivalence testing, bootstrap cross-validation intervals, theory of classifier-based two-sample tests, pre-registration of existing data, circular analysis, and the DANDI record.
- **Not searched, or not retrieved (residual):**
  - Ecology null-model benchmarking, which may be prior art for a graded control.
  - Shuffle practice in the calcium-imaging literature.
  - Small-cluster bootstrap in econometrics (44 mice).
  - The non-inferiority trial literature beyond Schuirmann.
  - Specific papers not obtained: Grün 1999, Friedman 2003 and Fu 2005. The Bates, Hastie & Tibshirani text was not read.

## Residual: nobody was asked
- The Elephant and Grün group were never asked about the non-wrapping variant and its count loss; `docs/todo/2026-09-11-elephant-surrogate-defects-are-not-filed-upstream.md` is still unfiled.
- No statistician was consulted about using bootstrap case cross-validation to show non-separability.
- The Cossart and Dard group were not contacted.
- I found no record that anyone asked. The main thread should ask Tony whether any correspondence exists, and cite it rather than quote it.

Sources:
- [Schuirmann 1987](https://link.springer.com/article/10.1007/BF01068419)
- [Jiang, Varma & Simon 2008](https://www.degruyterbrill.com/document/doi/10.2202/1544-6115.1322/html?lang=en), [NCI report copy](https://brb.nci.nih.gov/techreport/conflimbiosubmission0107.pdf)
- [Bates, Hastie & Tibshirani](https://arxiv.org/abs/2104.00673)
- [Kim, Ramdas, Singh & Wasserman 2021](https://projecteuclid.org/journals/annals-of-statistics/volume-49/issue-1/Classification-accuracy-as-a-proxy-for-two-sample-testing/10.1214/20-AOS1962.full)
- [Nosek et al. 2018](https://www.pnas.org/doi/10.1073/pnas.1708274114)
- [Weston et al. 2019](https://journals.sagepub.com/doi/full/10.1177/2515245919848684)
- [Kriegeskorte et al. 2009](https://www.nature.com/articles/nn.2303)
- [DANDI 000219 API record](https://api.dandiarchive.org/api/dandisets/000219/)
