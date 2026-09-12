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

Topics in use: `radar/`, `coordination/`, `DL/`, `surrogates/`, `ml/`. As of 2026-09-12 the shelf
holds **40 PDFs** — twelve of them papers on surrogate methods, a topic the shelf held nothing on
before 2026-09-10.

**Check the shelf before fetching, and shelve what you fetch.** Both halves, because on 2026-09-12
only the first half was running: a single blind review round had two roles hunting the same unshelved
paper — one reached Gerstein 2004 open-access and read it, the other could not and marked the claim
unverified. Both had correctly checked the shelf first. Neither shelved it, and neither should have:
the judgment roles cannot write, and the shell-holding roles are asked to keep to a scratch path that
a shared cross-machine shelf is not. **Carrying a review's fetches onto the shelf is part of applying
its findings**, and it is the adjudicating thread's job. `surrogates/README.md` and `ml/README.md`
were themselves missing until 2026-09-12, so fourteen PDFs sat in the state the shelf's own top-level
README calls "indistinguishable from a PDF someone downloaded and forgot".

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

- [ ] **Louis S, Borgelt C & Grün S (2010).** Generation and selection of surrogate methods for
      correlation analysis. In Grün S & Rotter S (eds), *Analysis of Parallel Spike Trains*,
      Springer, chapter 17, pp. 359–382. doi:10.1007/978-1-4419-5675-0_17.
      → **Still not shelved, but NOT unreachable — the "paywalled" label was wrong.** An open full
      text of chapter 17 is served at `portal.g-node.org/advanced-course-2019/`, which a 2026-09-12
      blind review fetched and read; pp. 359–382 confirmed from the PDF's own running heads. Its
      abstract is the surrogate screen's premise almost verbatim: surrogates must destroy "the
      feature of interest (temporal coordination of spikes)" while "other features of the data are
      preserved. The latter aspect is the most demanding." **Fetch from G-Node and shelve.** Any
      document still citing this as unread-because-paywalled is wrong as written. (Stella 2022 cites
      it as "Louis 2010b".)

- [x] ~~**Grün S, Borgelt C, Gerstein GL, Louis S & Diesmann M (2010).** Selecting appropriate
      surrogate methods for spike correlation analysis. *BMC Neuroscience* 11(Suppl 1):O15.
      doi:10.1186/1471-2202-11-S1-O15; PMC3090783.~~ **Fetched 2026-09-12** from biomedcentral →
      `surrogates/grun_2010_selecting_surrogate_methods.pdf`. Two pages, CNS*2010 abstract, and the
      free form of the chapter-17 premise above. Europe PMC's `fullTextPDF` endpoint returned 0
      bytes; the publisher's `/counter/pdf/` URL served it.

- [x] ~~**Gerstein (2004)**, *Acta Neurobiologiae Experimentalis* 64(2):203–207, PMID 15366253.~~
      **Fetched 2026-09-12** from ane.pl (open access, CC-BY) →
      `surrogates/gerstein_2004_searching_for_significance.pdf`, 5 pp., pages 203–207 confirmed off
      the title page. ⚠ **Two corrections it forces.** Its abstract calls its own method "a novel
      variant of the *dither surrogate* (Date et al. 1998)" — so the dithering root is Date 1998,
      already on this shelf, and a trace stopping at Gerstein stops one paper short. And he says flat
      dither "does change the original IH by **adding** short intervals and lowering the peak"; he
      does **not** claim intervals shorter than any real one. That stronger claim is bugarach's own
      measurement and must not be attributed to him.

- [x] ~~**Pipa et al. (2008)**, *Journal of Computational Neuroscience* 25:64–88, PMID 18219568,
      PMC2758673 — whole-train shifting, the origin Stella credit for trial shifting.~~
      **Fetched 2026-09-12** → `surrogates/pipa_2008_neuroxidence.pdf`, 25 pp. The paper is
      *NeuroXidence*, Pipa, Wheeler, Singer & Nikolić — the identifier in this entry was correct.
      Route: Springer `link.springer.com/content/pdf/10.1007/s10827-007-0065-3.pdf`; Europe PMC's
      `fullTextPDF` gave 0 bytes and its `fullTextXML` gave usable metadata but not a shelf-able file.

- [ ] **Stella A, Quaglio P, Torre E & Grün S (2019).** 3d-SPADE: significance evaluation of
      spatio-temporal patterns of various temporal extents. *Biosystems* 185:104022.
      doi:10.1016/j.biosystems.2019.104022. → **Named by a 2026-09-12 review as the closest prior art
      for what the surrogate screen does** — the applied paper in which Grün's group selected
      joint-ISI dithering as SPADE's surrogate. Their released harnesses `INM-6/SPADE_surrogates` and
      `INM-6/SPADE_applications` run substantially the comparison this screen runs. The screen is not
      wrong to exist, but it is currently unsituated against this. Shelve under `surrogates/`.

- [ ] **Pazienti, Diesmann & Grün (2007)** and **Pazienti et al. (2008)**, *Brain Research*
      1225:39–46 — the bounds on how far dithering can destroy precise coincidences, which is the
      surrogate screen's destruction test. Known only from Stella's reference list; identifiers
      not yet resolved.

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
| Gerstein 2004, *Acta Neurobiol Exp* 64(2):203–207 | `surrogates/gerstein_2004_searching_for_significance.pdf` — **fetched 2026-09-12**, ane.pl, open access |
| Grün, Borgelt, Gerstein, Louis & Diesmann 2010, *BMC Neurosci* 11(Suppl 1):O15 | `surrogates/grun_2010_selecting_surrogate_methods.pdf` — **fetched 2026-09-12**, biomedcentral |
| Pipa, Wheeler, Singer & Nikolic 2008, *J Comput Neurosci* 25(1):64–88 | `surrogates/pipa_2008_neuroxidence.pdf` — **fetched 2026-09-12**, Springer |
| Platkiewicz, Stark & Amarasingham 2017, *Neural Comput* 29(3):783–803 | `surrogates/platkiewicz_2017_spike_centered_jitter.pdf` |
| Gutmann & Hyvärinen 2012, *JMLR* 13:307–361 | `ml/gutmann_hyvarinen_2012_nce.pdf` |
| Lopez-Paz & Oquab 2017, ICLR | `ml/lopezpaz_oquab_2017_c2st.pdf` |
| Ilse, Tomczak & Welling 2018, ICML | `ml/ilse_2018_attention_mil.pdf` |
| Jain & Wallace 2019, NAACL | `ml/jain_wallace_2019_attention_not_expl.pdf` |
| Wang, Li & Metze 2019, ICASSP | `ml/wang_2019_mil_pooling_sed.pdf` |

**Frontiers, eNeuro, JMLR, PMLR, ACL Anthology, arXiv and MIT Press Direct all served a PDF to
`curl`. Every PMC link returned a bot-check page.** So the pattern for a future session: try the
publisher before PMC, and when PMC is the only route, it is a Tony ask rather than a dead end.
