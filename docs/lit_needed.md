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
holds 29 papers.

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

- [ ] **Amarasingham A, Harrison MT, Hatsopoulos NG & Geman S (2012).** Conditional modeling and
      the jitter method of spike resampling. *J Neurophysiol* 107(2):517–531.
      doi:10.1152/jn.00633.2011. **PMC3349623** (PMID 22031767).
      → Interval/window jitter, and the conditional-inference framing — *what the resampling
      conditions on is the null hypothesis*. **Already cited in this repo's own README** for LoCo
      and CoactDetect's null, and read by nobody here. Also gates a correct statement of what our
      existing detectors' null actually means.
      *Blocked:* same PMC bot-check; publisher copy is paywalled.

- [ ] **Elsayed GF & Cunningham JP (2017).** Structure in neural population recordings: an expected
      byproduct of simpler phenomena? *Nat Neurosci* 20:1310–1318. **PMC5577566** (PMID 28783140).
      → The canonical statement of the thesis this project keeps re-deriving: a surrogate preserving
      a specified feature set can only test whether structure exceeds what that feature set implies.
      *Blocked:* PMC bot-check; Nature paywalled; no author copy found at the Columbia lab page.

- [ ] **Hansen VG (1973).** Constant false alarm rate processing in search radars. Proc. IEE
      International Radar Conference, IEE Conf. Publ. **105**, 325–332.
      → ⚠ **Settles a live dispute in this repo.** `GLOSSARY.md` and `README.md` cite Hansen 1973 as
      the origin of GO-CFAR; `detector_history.md` §4 puts **Hansen & Sawyers 1980** in a column
      headed *origin* and marks it read-in-full. Two murderboard roles came out on opposite sides.
      The shelf holds the 1980 paper and not this one, so the question cannot be closed from what we
      have. A 1973 IEE conference publication is genuinely hard to get — this may need a library.

- [ ] **Date A, Bienenstock E & Geman S (1998).** On the temporal resolution of neural activity.
      Technical Report, Division of Applied Mathematics, Brown University.
      → The root of the dithering lineage, cited by Louis et al. 2010. Confirmed to exist by
      citation; no open copy located. Lowest priority — Louis et al. and Harrison & Geman supersede
      it operationally — but this project's attribution rule is to trace to the origin, and right
      now that trace stops one step short.

## Fetched 2026-09-10, on the shelf

Recorded so nobody re-fetches them, and so the failures above are legible as failures rather than
as an absence of effort.

| paper | where |
|---|---|
| Harrison & Geman 2009, *Neural Comput* 21(5):1244–1258 | `surrogates/harrison_geman_2009_pattern_jitter.pdf` — **fetched by Tony** |
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
