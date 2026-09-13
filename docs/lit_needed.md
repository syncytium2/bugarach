# Papers this project needs and could not fetch

**A session that needs a paper it cannot download adds a line here and tells Tony.** He can get
any of these; grab the PDF, drop it on the shelf under the naming convention below, and tick the
box. Modelled on `murderboard-lit/_NEEDED.md`, which has had this mechanism since 2026-08-22.

> **Why this file did not exist until 2026-09-10.** The murderboard's paper-fetch tool writes that
> list automatically when a fetch fails, and it is **deliberately not vendored here** — it hardcodes
> a personal library path, which sapper SAP004 blocks from a public repo
> ([the todo](todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md)). Dropping the tool was
> right. Dropping the *channel* with it was not, and it cost something real: a proposal was drafted
> on 2026-09-10 whose central mechanism had been characterised as unsound in a literature this
> project holds none of, and nobody asked for the papers because there was nowhere to ask.
> Tony, 2026-09-10: *"you're supposed to ask me for pdfs you can't get."*

> ## ⚠ RESOLVE EVERY PMCID FROM NCBI. NEVER WRITE ONE FROM MEMORY.
>
> The first version of this file, written on 2026-09-10 **immediately after an eleven-role
> adversarial review**, carried **three fabricated PMCIDs**. Each was plausible — right shape, right
> era, and one of them landed on a *different paper in the same journal and the same year*:
>
> | written | what it actually is |
> |---|---|
> | PMC3289479 → Amarasingham 2012 | Hsieh TH, mechanomyography and paired-pulse TMS, *J Neurophysiol* 2012 |
> | PMC5763468 → Elsayed & Cunningham 2017 | Ji Z, linear programming for phosphoproteomics, *BMC Syst Biol* |
> | PMC5873297 → Platkiewicz 2017 | Sin MLY, urinary RNA sequencing, *Clin Cancer Res* |
>
> **Every identifier supplied by a murderboard role was correct; every one generated from memory was
> wrong.** It cost Tony a download of the wrong paper before he caught it —
> *"PMC3289479 is a different paper"* (2026-09-10). A wrong accession number is a **fabricated
> citation**, the exact defect role 2 of the murderboard exists to catch, and it got in here because
> this file was written after the review rather than inside it.
>
> Resolve them, don't recall them. The legacy `pmc/utils/idconv` endpoint is retired; use eutils:
>
> ```
> esearch.fcgi?db=pubmed&term=<title>[Title]        # title -> PMID
> elink.fcgi?dbfrom=pubmed&db=pmc&id=<pmid>         # PMID  -> PMCID (FIRST linkset; the long
>                                                   #          second list is "cited by")
> esummary.fcgi?db=pmc&id=<pmcid>                   # PMCID -> title + first author, to confirm
> ```
>
> And confirm the file after download: `pdftotext -f 1 -l 1 <pdf> -` prints the title page.
> `pdftotext` is installed on this machine (`/opt/homebrew/bin/pdftotext`).

## Where the shelf is

`<darkroom>/bugarach/lit/<topic>/<first-author>_<year>_<slug>.pdf` — resolve the darkroom with
`bugarach.paths.darkroom()` or `python -m bugarach.paths`. **Never hardcode it**: the path carries
a person's name and this repo is public (SAP004).

Topics in use: `radar/`, `coordination/`, `DL/`, `surrogates/`, `ml/`. As of 2026-09-10 the shelf
holds 37 files — nine of them papers on surrogate methods, a topic the shelf held nothing on before this date.

⚠ **There is no master library.** Checked 2026-09-10: `murderboard-lit/` is its own repo of 206
papers but on a different subject entirely — agentic reproducibility, paper-code consistency —
and `draughtsman/lit` and `clamor/lit` hold one and two papers respectively (von der Malsburg, on
binding). Nothing is shared, nothing is indexed across them, and no project can see another's
shelf. Filed as an open question rather than fixed unilaterally, since three of those four
locations belong to other projects.

---

## Open

- [x] ~~**Harrison MT & Geman S (2009).** A rate and history-preserving resampling algorithm for
      neural spike trains. *Neural Computation* 21(5):1244–1258. PMC3065177.~~
      **Tony fetched it 2026-09-10** → `surrogates/harrison_geman_2009_pattern_jitter.pdf`.
      *Pattern jitter*, the leading candidate to replace the surrogate the murderboard killed, and
      a dynamic program that cannot be implemented from a secondary description.

- [x] ~~**Amarasingham A, Harrison MT, Hatsopoulos NG & Geman S (2012).** Conditional modeling and
      the jitter method of spike resampling. *J Neurophysiol* 107(2):517–531.~~
      **Tony fetched it 2026-09-10**, publisher version →
      `surrogates/amarasingham_2012_jitter_method.pdf`. Interval/window jitter and the
      conditional-inference framing — *what the resampling conditions on is the null hypothesis*.
      **Was already cited in this repo's own README** for LoCo and CoactDetect's null, and read by
      nobody in it until now.

- [x] ~~**Elsayed GF & Cunningham JP (2017).** Structure in neural population recordings: an
      expected byproduct of simpler phenomena? *Nat Neurosci* 20:1310–1318.~~
      **Tony fetched it 2026-09-10** → `surrogates/elsayed_cunningham_2017_byproduct.pdf`. The
      canonical statement of the thesis this project keeps re-deriving: a surrogate preserving a
      specified feature set can only test whether structure exceeds what that feature set implies.

- [ ] **Gregers Hansen, V. (1973).** Constant-false-alarm-rate processing in search radars. Proc.
      IEE International Radar Conference *Radar — present and future*, 23–25 October 1973, Savoy
      Place, London. IEE Conf. Publ. **105**.
      → **PARTIALLY RESOLVED 2026-09-10: the citation is confirmed, the origin question is not.**
      Tony found the volume's
      contents listing (`radar/iee_conf_105_1973_CONTENTS_ONLY.pdf` — the listing, **not** the
      paper). It reads:
      > GREGERS HANSEN,V.: Constant-false-alarm-rate processing in search radars

      So the paper is real and the title is confirmed. **The surname is `Gregers Hansen`.**
      IEEE's own authority record agrees — Tony saved it as
      `radar/gregers_hansen_AUTHOR_PROFILE_ieee.pdf`, and it reads:
      > **V. Gregers Hansen** — Also published under: Vilhelm Gregers Hansen, V. Hansen, V. G. Hansen
      > · Affiliation: Raytheon Company, Wayland, MA

      ⚠ **A correction to the first version of this entry, which said we had been citing the name
      "wrong".** That was too strong. IEEE lists *V. G. Hansen* as a form he genuinely published
      under, so `Hansen VG` is a documented variant rather than an error. What is true is narrower:
      the **canonical form is Gregers Hansen**, treating `Hansen` as the surname inverts a compound
      one, and a repo that cares about attribution should use the canonical form. Same correction
      applies to the 1980 paper on this shelf — cite it as **Gregers Hansen & Sawyers**.

      ⚠ **Still open, and it is the half that matters:** whether this paper is the ORIGIN of
      greatest-of CFAR. The contents listing gives no abstract, no pages and no text, so it cannot
      settle `detector_history.md` §4 putting **Hansen & Sawyers 1980** in a column headed *origin*.
      Our claimed page range **325–332 remains unverified** — it appears in no source we hold.

      **The chronology is evidence and not proof, and it leans one way.** From the IEEE profile and
      OpenAlex, his CFAR thread runs: 1971 *Siebert and Dicke-Fix CFAR Radar Detectors* → 1972 *Cell
      Averaging LOG/CFAR Receiver* → **1973 the paper in question** → 1980 *Detectability Loss Due to
      "Greatest Of" Selection in a Cell-Averaging CFAR*. A 1980 title that costs a technique
      presupposes the technique already exists, which is consistent with 1973 introducing it — the
      reading murderboard role 2 argued for. It is also consistent with GO originating in the 1971 or
      1972 papers, which we do not hold either. **Titles are not papers; this does not close it.**

      ⚠ **IEEE Xplore is exhausted as a route.** The 1973 paper is an **IEE** (British) conference
      publication and Xplore does not index it — the profile jumps 1972 → 1974. What remains is a
      library holding IEE Conf. Publ. 105 itself.

- [x] ~~**Date A, Bienenstock E & Geman S (1998).** On the temporal resolution of neural
      activity. Technical Report, Division of Applied Mathematics, Brown University.~~
      **Tony fetched it 2026-09-10** from Geman's Brown page →
      `surrogates/date_1998_temporal_resolution.pdf`, dated 21 May 1998. **The root of the dithering
      lineage, and the trace no longer stops short of it.** Note the acknowledgements: the
      multi-electrode data came from Hatsopoulos, Ojakangas & Donoghue — the same Hatsopoulos who is
      a co-author on the 2012 jitter paper, so the lineage from this report to the method we intend
      to use is one continuous group.

- [x] ~~**Louis S, Borgelt C & Grün S (2010).** Generation and selection of surrogate methods for
      correlation analysis. In Grün S & Rotter S (eds), *Analysis of Parallel Spike Trains*,
      Springer, chapter 17, pp. 359–382. doi:10.1007/978-1-4419-5675-0_17.~~
      **Read 2026-09-12 from the G-Node advanced-course portal copy** →
      `surrogates/louis_2010_surrogate_methods_chapter17.pdf` (typeset; page numbers match). Springer
      itself now returns a bot-check page, so the publisher PDF is still not held — see the deep-dive
      list below. Chapter 10 of the same book came from the same portal.

- [x] ~~**Grün S, Borgelt C, Gerstein GL, Louis S & Diesmann M (2010).** Selecting appropriate
      surrogate methods for spike correlation analysis. *BMC Neuroscience* 11(Suppl 1):O15.~~
      On the shelf since 2026-09-12 → `surrogates/grun_2010_selecting_surrogate_methods.pdf`.

- [x] ~~**Gerstein (2004)**, *Acta Neurobiologiae Experimentalis* 64(2):203–207.~~ On the shelf since
      2026-09-12 → `surrogates/gerstein_2004_searching_for_significance.pdf`.

- [x] ~~**Pipa et al. (2008)**, *Journal of Computational Neuroscience* 25:64–88.~~ On the shelf since
      2026-09-12 → `surrogates/pipa_2008_neuroxidence.pdf` (Springer served it that day; it served
      nothing later the same day).

- [ ] **Pazienti A, Diesmann M & Grün S (2007)**, *LNCS* pp. 428–437, doi:10.1007/978-3-540-75555-5_41,
      and **Pazienti A, Maldonado PE, Diesmann M & Grün S (2008)**, *Brain Res* 1225:39–46,
      doi:10.1016/j.brainres.2008.04.073 (both resolved by Crossref 2026-09-12). The bounds on how far
      dithering can destroy precise coincidences, which is the surrogate screen's destruction test.
      → **Tony ask.** Springer bot-checks the 2007 chapter; the 2008 paper's Universidad de Chile
      repository copy sits behind a proof-of-work bot page.

**Added 2026-09-12 by the ROI-swap proposal's murderboard**
([`proposals/2026-09-12-the-roi-swap-null.md`](proposals/2026-09-12-the-roi-swap-null.md)).
The proposal cites all four as not held; until they are read, the claims resting on them are not
admissible there.

- [x] ~~**Perkel DH, Gerstein GL & Moore GP (1967).** Neuronal spike trains and stochastic point
      processes. **II. Simultaneous spike trains.** *Biophys J* 7(4):419–440. PMID 4292792,
      PMC1368069, doi:10.1016/S0006-3495(67)86597-4.~~
      **Read 2026-09-12** from Europe PMC's scan of the published pages, which
      `https://europepmc.org/articles/PMC1368069?pdf=render` serves even though `fullTextXML` is empty →
      `surrogates/perkel_1967_simultaneous_spike_trains.pdf`. The same route served Gerstein & Perkel
      1972. The shuffle construction is on p. 436. The shift predictor's construction. ⚠ Not Part I, *The single spike train*,
      same authors, same issue — a bare "(1967)" does not distinguish them. Whether *"shift
      predictor"* is their term is unresolved: Amarasingham 2012 calls it the shuffle predictor and
      Pipa 2008 credits the name to König (1994).

- [ ] **Grün S, Diesmann M, Grammont F, Riehle A & Aertsen A (1999).** Detecting unitary events
      without discretization of time. *J Neurosci Methods* 94:67–79.
      → The multiple-shift method, which Pipa 2008 credits as the antecedent of whole-train shifting.
      Known only from Pipa's reference list; **whether it is itself the root is unverified** — the
      trace stopped here, one paper short of certain, the same shape as the Gerstein-to-Date correction
      recorded on the shelf. Its abstract, read 2026-09-12, describes the multiple-shift method as a
      coincidence **detector**, not a surrogate null. Still not held (closed access per OpenAlex).

- [ ] **Stella A, Quaglio P, Torre E & Grün S (2019).** 3d-SPADE: Significance evaluation of
      spatio-temporal patterns of various temporal extents. *Biosystems* 185:104022.
      doi:10.1016/j.biosystems.2019.104022, PMID 31449837.
      → The closest named prior art for what the screen does. **Still not held** — ScienceDirect 403, and
      the ETH repository is a JavaScript shell. ⚠ **Correction 2026-09-12:** this entry used to say
      `INM-6/SPADE_surrogates` accompanies a *different* 2021 paper. Crossref says the 2021 bioRxiv
      (doi:10.1101/2021.08.24.457480) carries the same title and authors and **is the preprint of**
      Stella, Bouss, Palm & Grün 2022, *eNeuro* — already on the shelf. The harness is not missed by a
      2022 citation set.

- [x] ~~**Cunningham JP & Yu BM (2014).** Dimensionality reduction for large-scale neural recordings.
      *Nat Neurosci* 17:1500–1509. doi:10.1038/nn.3776.~~
      **Read 2026-09-12 in the PMC author manuscript, and it does not support the claim.** "pseudo",
      "shuffl" and "noise correlation" do not appear in its body. For "shuffling trials removes noise
      correlations", cite Averbeck, Latham & Pouget 2006 (p. 359, p. 362), now at
      `recombination/averbeck_2006_neural_correlations.pdf`. The publisher PDF of Cunningham & Yu is still
      not held, and is not needed for this.

## Added 2026-09-12 by the recombination-nulls deep dive — no publisher PDF

From [`learned/recombination_nulls_reading_log.md`](learned/recombination_nulls_reading_log.md). Every
identifier was resolved from Crossref, OpenAlex, PubMed or Europe PMC. A second pass then tried each DOI
again through OpenAlex's publisher locations and the publisher URL patterns that serve `curl`. That pass
found five more publisher PDFs, now shelved; everything below is what remained.

**What failed, so the next session does not re-try it:** Springer returned a 3 KB "Client Challenge" page
for **every** request on 2026-09-12, including `/content/pdf/` — the route `INDEX.md` recorded as working.
Elsevier, Cell Press, Wiley, OUP, APS journals (*J Neurophysiol*), *J Neurosci*, PNAS, MIT Press, Annual
Reviews, the Royal Society, APS physics, AIP and MDPI all returned 403. nature.com returns an HTML paywall
page for subscription titles. Open access that worked: Frontiers, PLOS, eLife's CDN, *Nature
Communications*, *Scientific Reports*, NeurIPS proceedings, PMLR.

### Tony asks — nothing held beyond the abstract, and the paper bears on an answer

- [ ] **Brody CD (1998).** Slow covariations in neuronal resting potentials can lead to artefactually fast
      cross-correlations in their spike trains. *J Neurophysiol* 80(6):3345–3351.
      doi:10.1152/jn.1998.80.6.3345. → The slow-state version of Brody 1999, and the closest to slow
      slice-level drift. Journal 403.
- [ ] **Grün S, Riehle A & Diesmann M (2003).** Effect of cross-trial nonstationarity on joint-spike
      events. *Biol Cybern* 88(5):335–351. doi:10.1007/s00422-002-0386-2. → Rate states covarying across
      trials as the generator of shuffle false positives. Springer bot page; MPG repositories 403.
- [ ] **Malvache A, Reichinnek S, Villette V, Haimerl C & Cossart R (2016)**, *Science* 353:1280–1283 —
      **the supplementary materials only**; the main text is on the shelf. → Where its SCE significance
      test is defined. science.org 403; HAL bot page; the Zenodo record is deleted (410).
- [ ] **Stella A, Quaglio P, Torre E & Grün S (2019)**, 3d-SPADE — already listed above.
- [ ] **Lopes-dos-Santos V, Ribeiro S & Tort ABL (2013).** Detecting cell assemblies in large neuronal
      populations. *J Neurosci Methods* 220(2):149–166. doi:10.1016/j.jneumeth.2013.04.010. → The per-neuron
      circular-shift assembly null, known here only through Mölter 2018's description.
- [ ] **Cossart R, Aronov D & Yuste R (2003).** Attractor dynamics of network UP states in the neocortex.
      *Nature* 423:283–288. doi:10.1038/nature01614. → A slice calcium-imaging root; its null was not read.
- [ ] **Shahbazi F, Ewald A, Ziehe A & Nolte G (2010).** Constructing surrogate data to control for
      artifacts of volume conduction for functional connectivity measures. IFMBE Proceedings vol. 28,
      pp. 207–210. doi:10.1007/978-3-642-12197-5_46. → A surrogate that keeps shared mixing while
      destroying source dependence — the EEG analogue of keeping shared drive. Springer bot page.
- [ ] **Lancaster G, Iatsenko D, Pidde A, Ticcinelli V & Stefanovska A (2018).** Surrogate data for
      hypothesis testing of physical systems. *Physics Reports* 748:1–60. doi:10.1016/j.physrep.2018.06.001.
      → Whether the major surrogate review covers inter-subject surrogates is unverified.
- [ ] **Aarts E, Verhage M, Veenvliet JV, Dolan CV & van der Sluis S (2014).** A solution to dependency:
      using multilevel analysis to accommodate nested data. *Nat Neurosci* 17:491–496. doi:10.1038/nn.3648.
      → Type I error from nested data, abstract only.
- [ ] **Miklós I & Podani J (2004).** Randomization of presence–absence matrices: comments and new
      algorithms. *Ecology* 85:86–92. doi:10.1890/03-0101. → The swap algorithm samples unevenly.
- [ ] **Fayle TM & Manica A (2010).** Reducing over-reporting of deterministic co-occurrence patterns in
      biotic communities. *Ecol Modelling* 221:2237–2242. doi:10.1016/j.ecolmodel.2010.06.013. → Sequential
      swap false-rejection above 30% on large random matrices; known only through Gotelli & Ulrich 2011.
- [ ] **Hasson U, Nir Y, Levy I, Fuhrmann G & Malach R (2004).** Intersubject synchronization of cortical
      activity during natural vision. *Science* 303:1634–1640. doi:10.1126/science.1089506. → The origin of
      cross-subject recombination in fMRI.
- [ ] **Price AL et al. (2006).** Principal components analysis corrects for stratification in genome-wide
      association studies. *Nat Genet* 38:904–909. doi:10.1038/ng1847. → Population structure as the
      confound of permutation across individuals.
- [ ] **Churchill GA & Doerge RW (1994).** Empirical threshold values for quantitative trait mapping.
      *Genetics* 138:963–971. doi:10.1093/genetics/138.3.963. → Permutation across individuals, valid under
      equal relatedness. OUP 403; Europe PMC has no text for this scan.

⚠ Author lists above that go past the first author were resolved from Crossref for this entry; titles for
Brody 1998, Grün 2003, Lopes-dos-Santos 2013, Cossart 2003, Aarts 2014, Miklós 2004, Fayle 2010, Hasson 2004,
Price 2006 and Churchill 1994 are Crossref's. **Check the downloaded title page before shelving**, as the
section on PMCIDs above says.

### Tony asks — lower priority, metadata or abstract only

Named in the reading log but not load-bearing for any answer: Aertsen, Gerstein, Habib & Palm 1989
(*J Neurophysiol*, doi:10.1152/jn.1989.61.5.900); König 1994 (doi:10.1016/0165-0270(94)90157-0); Staude,
Rotter & Grün 2008 (doi:10.1162/neco.2008.06-07-550); Ben-Shaul et al. 2001
(doi:10.1016/S0165-0270(01)00389-2); chapters 5, 6, 8, 12 and 18 of *Analysis of Parallel Spike Trains*
(doi prefix 10.1007/978-1-4419-5675-0_); Anderson, Sanderson & Sheinberg 2007
(doi:10.1007/s00221-006-0594-4); Franco et al. 2004 (doi:10.1007/s00221-003-1737-5); Averbeck & Lee 2006
(doi:10.1152/jn.00919.2005); Panzeri et al. 2022 (doi:10.1038/s41583-022-00606-4); Cowley et al. 2020
(doi:10.1016/j.neuron.2020.07.021); Theiler et al. 1992 (doi:10.1016/0167-2789(92)90102-s); Andrzejak et
al. 2003 (doi:10.1103/physreve.68.066202); Barnes et al. 2024 (doi:10.1063/5.0202865); Toledo et al. 2002
(doi:10.1016/s1350-4533(01)00114-x); Schwartz et al. 2022 (doi:10.1016/j.neuroimage.2022.119677); Reindl et
al. 2018 (doi:10.1016/j.neuroimage.2018.05.060); Moreau & Dumas 2021 (doi:10.1016/j.tics.2021.02.011);
Zhang & Yartsev 2019 (doi:10.1016/j.cell.2019.05.023); Bernieri, Reznick & Rosenthal 1988
(doi:10.1037/0022-3514.54.2.243); Ramseyer & Tschacher 2010 (doi:10.1007/978-3-642-12397-9_15); Connor &
Simberloff 1979 (doi:10.2307/1936961); Diamond & Gilpin 1982 (doi:10.1007/BF00349013); Ulrich & Gotelli
2007, *Ecology* (doi:10.1890/06-1208.1); Fayle & Manica 2011 (doi:10.1016/j.ecolmodel.2011.01.010); Wilson
1995 (doi:10.2307/3546047); Peres-Neto et al. 2001 (doi:10.1034/j.1600-0706.2001.930112.x); Gotelli &
Graves 1996, *Null Models in Ecology* (a book); Perkel 1964, RAND RM-4234-NIH (identifier unresolved);
Peyrache et al. 2009 (doi:10.1038/nn.2337); Robinson et al. 2021, *Can contrastive learning avoid shortcut
solutions?*; Kostas & Rudzicz 2020, DN3; Liu, Azabou et al. 2021, *Drop, swap, and generate* (bioRxiv
doi:10.1101/2021.07.21.453285).

### Read, but only from a non-publisher copy

The text was read. A publisher PDF matters only if one of these is cited in a document for outside readers,
where the page numbers must be checked against the version of record.

| paper | what was read instead |
|---|---|
| Brody 1999a and 1999b, *Neural Comput* 11(7) | CaltechAUTHORS typeset copies (shelved) |
| Ventura, Cai & Kass 2005a, 2005b; Kass, Ventura & Brown 2005; Kass & Ventura 2006 | publisher typesets on the Kass lab site (shelved) |
| Harrison, Amarasingham & Kass 2013, *Spike Timing* (CRC) | author manuscript (shelved) |
| Albert et al. 2016, *Neural Comput* 28(11) | HAL author version (shelved) |
| Louis, Borgelt & Grün 2010 and Grün, Diesmann & Aertsen 2010, *Analysis of Parallel Spike Trains* chs. 17 and 10 | G-Node course-portal copies (shelved) |
| Perkel, Gerstein & Moore 1967; Gerstein & Perkel 1972, *Biophys J* | Europe PMC scans of the published pages (shelved) |
| Grün 2009, *J Neurophysiol* 101:1126–1140; Vinci et al. 2016, *Neural Comput* 28:849–881 | PMC full-text HTML |
| Larry & Joshua 2023, *J Neurophysiol* 129:843–861; Yuan & Shou, *eLife* 10.7554/eLife.103703 | bioRxiv full text |
| Peyrache et al. 2010, *J Comput Neurosci* 29:309–325 | UvA-DARE repository copy (shelved) |
| Romano et al. 2015, *Neuron* 85; Ratsifandrihamanana et al. 2023, *STAR Protoc* 4:102760 | Europe PMC XML |
| Cunningham & Yu 2014, *Nat Neurosci*; Kohn et al. 2016, *Annu Rev Neurosci*; Moreno-Bote et al. 2014, *Nat Neurosci*; Stefanini et al. 2020, *Neuron*; Ebitz & Hayden 2021, *Neuron* | PMC author manuscripts |
| Averbeck, Latham & Pouget 2006, *Nat Rev Neurosci* 7:358–366 | typeset PDF on Latham's Gatsby page (shelved) |
| Gallego et al. 2020, *Nat Neurosci* 23:260–270 | Europe PMC author manuscript |
| Meyers et al. 2008, *J Neurophysiol*; Latham & Nirenberg 2005, *J Neurosci*; Nogueira et al. 2020, *J Neurosci*; Leavitt et al. 2017, *PNAS*; Mozumder & Constantinidis 2023, *J Neurophysiol* | PMC full text |
| Mozumder et al. 2025, *Cell Rep* 45:116764; Deitch, Rubin & Ziv 2021, *Curr Biol* 31; Zhang et al. 2026, *Neuron* 114 | bioRxiv preprints (shelved) |
| Tyrcha et al. 2013, *J Stat Mech*; Saravanan, Berman & Sober 2020 (journal DOI unresolved) | arXiv (shelved) |
| Pandarinath et al. 2018, LFADS, *Nat Methods* 15:805–815 | CSHL author manuscript (shelved) |
| Ye & Pandarinath 2021, *Neurons, Behavior, Data analysis and Theory* | arXiv (the journal PDF came back 0 bytes twice) |
| Banville et al. 2021, *J Neural Eng* 18:046020; Geirhos et al. 2020, *Nat Mach Intell* 2:665–673 | arXiv (shelved) |
| Arora et al. 2025, NuCLR, NeurIPS; Chen, Luo & Li 2021, NeurIPS; Chau et al. 2025, Population Transformer, ICLR | arXiv (shelved); proceedings or OpenReview not reached |
| Liu, Tang & Goldwater 2023, *Interspeech*; Rivière et al. 2020, *ICASSP*; Doersch, Gupta & Efros 2015, *ICCV* | arXiv, or the CVF open-access copy for Doersch (shelved) |
| Hamilton 2021, *Neuron* 109:404–407 | PsyArXiv preprint, whose title differs (shelved) |
| Holroyd 2022, *Trends Neurosci* 45:346–357 | Ghent author manuscript (shelved) |
| Kingsbury et al. 2019, *Cell* 178:429–446; Moulder et al. 2018, *Psychol Methods* 23:757–773 | PMC author manuscripts |
| Reindl et al. 2022, *NeuroImage* 251:118982 | bioRxiv preprint (shelved) |
| Zimmermann et al. 2024, *Imaging Neurosci*; Zamm et al. 2024, *SCAN*; Ayrolles et al. 2021, *SCAN*; Gugnowska et al. 2022, *Cereb Cortex*; Kayhan et al. 2022 and Marriott Haresign et al. 2022, *Dev Cogn Neurosci*; Nguyen et al. 2021, *Sensors*; Pérez et al. 2021, *MethodsX* | Europe PMC full text |
| Hakim et al. 2023, *NeuroImage* 280; Sheppard et al. 2012, *Phys Rev E*; Iatsenko et al. 2013, *Phil Trans R Soc A* | typeset repository copies (UCL; Lancaster eprints) (shelved) |
| Prichard & Theiler 1994, *PRL*; Pereda et al. 2005, *Prog Neurobiol* | arXiv (shelved) |
| Finn et al. 2015, *Nat Neurosci*; Nastase et al. 2019, *SCAN*; Winkler et al. 2015, *NeuroImage*; Ahrends et al. 2022, *NeuroImage*; Molina & Stone 2020, *Ecology* | Europe PMC full text |
| Chen et al. 2016, *NeuroImage* 142, and its corrigendum | PMC page text, **figures not seen** |
| Winkler et al. 2014, *NeuroImage* 92; Hindriks et al. 2016, *NeuroImage* 127 | Warwick and KU Leuven typeset repository copies (shelved) |
| Liégeois et al. 2017, *NeuroImage* 163; Bari et al. 2019, *NeuroImage* 202; Abney 2015, *Genet Epidemiol* 39 | bioRxiv or arXiv (shelved) |
| Gotelli 2000, *Ecology* 81; Ulrich & Gotelli 2007, *Oikos* 116; Gotelli & Ulrich 2011, *Ecol Modelling* 222; Gotelli & Ulrich 2012, *Oikos* 121 | typeset copies on Gotelli's UVM site (shelved) |
| Colwell & Winkler 1984, in *Ecological Communities* (Princeton UP) | a scan on Colwell's website, noisy OCR (shelved) |
| Rupprecht et al. 2021, CASCADE, *Nat Neurosci* 24 | the shelf copy is a Europe PMC author manuscript, unchanged |
| Lopez-Paz & Oquab 2017, ICLR | the shelf copy is arXiv v4, unchanged |

### No publisher version exists — not an ask

Preprint-only or arXiv-only works, where the preprint **is** the version of record: van den Oord, Li &
Vinyals 2018 (CPC); Cheng et al. 2020; Azabou et al. 2021 (MYOW); Jude et al. 2022; Harris 2021 (bioRxiv
v3); Posani 2026; Xu et al. 2026 (CalM); Lin, Wu & Jung 2026; Zare et al. 2026; Fayle 2020; Hamon et al. 2026
(CICADA); Amarasingham et al. 2011 (the jitter supplement on arXiv).

## Fetched 2026-09-10, on the shelf

Recorded so nobody re-fetches them, and so the failures above are legible as failures rather than
as an absence of effort.

| paper | where |
|---|---|
| Date, Bienenstock & Geman 1998, Brown Univ. tech. report | `surrogates/date_1998_temporal_resolution.pdf` — **fetched by Tony**, the root of the lineage |
| Harrison & Geman 2009, *Neural Comput* 21(5):1244–1258 | `surrogates/harrison_geman_2009_pattern_jitter.pdf` — **fetched by Tony**. ⚠ **Replaced 2026-09-10** with the published version; the file was briefly the NIH author manuscript |
| Hatsopoulos, Geman, Amarasingham & Bienenstock 2003, *Neurocomputing* 52–54:25–29 | `surrogates/hatsopoulos_2003_what_time_scale.pdf` — *"At what time scale does the nervous system operate?"*, which is the *J* question by another name |
| Amarasingham, Geman & Harrison 2015, *PNAS* | `surrogates/amarasingham_2015_ambiguity_nonidentifiability.pdf` — what a surrogate test can and cannot conclude |
| Paradiso et al. 2019, *Front Integr Neurosci* 12:63 | `coordination/paradiso_2019_transsaccadic_v1_lfp.pdf` — swept up from the same page; not on the ask list, filed rather than discarded |
| Amarasingham, Harrison, Hatsopoulos & Geman 2012, *J Neurophysiol* 107:517–531 | `surrogates/amarasingham_2012_jitter_method.pdf` — **fetched by Tony**, publisher version |
| Elsayed & Cunningham 2017, *Nat Neurosci* 20:1310–1318 | `surrogates/elsayed_cunningham_2017_byproduct.pdf` — **fetched by Tony**, publisher version |
| Louis, Gerstein, Grün & Diesmann 2010, *Front Comput Neurosci* 4:127 | `surrogates/louis_2010_operational_time_dither.pdf` |
| Stella, Bouss, Palm & Grün 2022, *eNeuro* 9(3) | `surrogates/stella_2022_comparing_surrogates.pdf` |
| Platkiewicz, Stark & Amarasingham 2017, *Neural Comput* 29(3):783–803 | `surrogates/platkiewicz_2017_spike_centered_jitter.pdf` |
| Gutmann & Hyvärinen 2012, *JMLR* 13:307–361 | `ml/gutmann_hyvarinen_2012_nce.pdf` |
| Lopez-Paz & Oquab 2017, ICLR | `ml/lopezpaz_oquab_2017_c2st.pdf` |
| Ilse, Tomczak & Welling 2018, ICML | `ml/ilse_2018_attention_mil.pdf` |
| Jain & Wallace 2019, NAACL | `ml/jain_wallace_2019_attention_not_expl.pdf` |
| Wang, Li & Metze 2019, ICASSP | `ml/wang_2019_mil_pooling_sed.pdf` |

**Frontiers, eNeuro, JMLR, PMLR, ACL Anthology, arXiv and MIT Press Direct all served a PDF to
`curl`. Every PMC link returned a bot-check page.** So the pattern for a future session: try the
publisher before PMC, and when PMC is the only route, it is a Tony ask rather than a dead end.
