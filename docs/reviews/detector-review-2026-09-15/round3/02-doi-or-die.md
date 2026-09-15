> **Public copy.** Lines that concern real treatment recordings are removed (1 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2: citation and reference check, round 3 (blind pass)

**Verdict:** None of the metadata is fabricated. All 22 journal DOIs resolve, and authors, titles, volumes, pages and years match Crossref. The CICADA software DOI and the bioRxiv DOI resolve too. There are no blocking findings. Five major findings concern whether each cited work says what the page says, and whether it is really where the idea started.

Everything below is from sources I fetched in this session, unless the row says otherwise. I did not read `docs/reviews/detector_review_2026-09-15*` or `_round1/`.

## Major

**M1. Section 11, LoCo paragraph: Hansen 1973 is marked "(not read)", and "usually credited" overstates.**
- **The problem:** the project did read this paper. The loan copy is on the lit shelf (`darkroom/bugarach/lit/radar/gregers_hansen_1973_cfar_search_radars.pdf`, marked read in full on 2026-09-14). `docs/detector_history.md` §4.1 records the reading.
- **I checked it myself:** page 326 of the scan describes greatest-of selection ("use the greatest of these two estimates to normalize the output"). The paper gives no source for it and does not claim it as new.
- **Later sources disagree on who gets the credit.** Gandhi & Kassam 1988 credit Hansen 1973. Rohling 1983 credits Moore & Lawrence 1980. Hansen & Sawyers 1980 point to an unpublished Hughes Aircraft memo by Sawyers (1972). Two sources out of three is not "usually".
- **Fix:** replace the clause with something like: "greatest-of selection; its earliest published description we found is Hansen V.G. (1973) … pp. 325–332, which does not cite an earlier source; where it began is not established." Remove "(not read)".
- **Verified against source:** yes.

**M2. Section 2 (last paragraph of "Why the shift and not the shuffle"): the Stella et al. 2022 citation says more than the paper does.**
- **What the page says:** others measured "the same failure for random scrambles" and "recommend shifting whole rows instead".
- **What Stella tested was not the page's shuffle.** They tested uniform dithering: each spike moves a small amount (±D, with D = 25 ms). The page's shuffle sends each event to any time in the recording.
- **The mechanism does match.** Binning and clipping lose spikes, which inflates significance.
- **The recommendation is also not "whole rows".** Stella recommend trial shifting: each trial's spike train moves by one small random amount, and there is no wrap-around. They also accept four other surrogates (UDD, JISI-D, ISI-D and WIN-SHUFF). The paper is at doi:10.1523/ENEURO.0505-21.2022, abstract and Discussion.
- **Fix:** "Stella et al. (2022) found that moving each spike on its own loses spikes to the same one-count-per-bin rule and inflates significance. They recommend shifting each trial's spike train as a whole by one small random amount."
- **Possible added citation:** the evidence against randomizing the whole recording is Louis, Borgelt & Grün 2010 (chapter 17 of *Analysis of Parallel Spike Trains*). It is on the shelf.
- **Verified against source:** yes.

**M3. Section 11, SPIKE-synch paragraph: the source that started picking out events by SPIKE-synchronization score is not cited.**
- **What the page cites:** Cecchini et al. 2021 for how "the measure's authors pick out events on the same scores".
- **That description of Cecchini is accurate.** They drop every spike that is not coincident with spikes in at least three quarters of the other trains, and they add a threshold on the average calcium signal. (PLoS Comput Biol 17:e1008963, Results, "Event identification", and the Fig 2C legend.) Kreuz is last author, at CNR/ISC Florence.
- **Cecchini is not the origin.** Cecchini's reference [23] is Kreuz, Satuvuori, Pofahl & Mulansky 2017, "Leaders and followers: quantifying consistency in spatio-temporal propagation patterns", *New J Phys* 19:043028, doi:10.1088/1367-2630/aa68c3 (open access).
  - Kreuz 2017 introduces a threshold on each spike's SPIKE-synchronization value, to keep "truly global events".
  - It applies that threshold at 0.7 to calcium-imaging giant depolarizing potentials (GDPs) (Fig. 12).
- **Fix:** cite Kreuz et al. 2017 as the origin, and keep Cecchini 2021 as the calcium-imaging application that adds the signal condition.
- **The personal communication is handled correctly.** It is paraphrased, cited, and dated 2026-04-23, with nothing quoted.
- **Verified against source:** yes.

**M4. Sections 3.5 and 11, CICADA: checking forward shows the upstream code has moved, and one of the four stated differences is now partly gone.**

What checks out:
- **SCE code is not in Zenodo 1.0.3.** I downloaded `cicada-1.0.3.tar.gz` from zenodo.org/records/10041434 and it contains no SCE code.
- **The code first appeared in 2020.** In GitLab project 14048984, the first commit touching `src/cicada/utils/stats/sce_stats_utils.py` is dated 2020-03-26. The file is absent from tags 1.0.3 and 1.0.6.
- **The upstream rule matches the page.** `get_sce_threshold` uses np.roll per cell, pools the counts, takes a percentile (95th by default) and uses 100 surrogates.

What the page misses:
- **No branch is called "main".** The default branch is `master`.
- **That repository has declared itself superseded since 2026-07-14.** Robin Dard's commit 19862ecb put a banner at the top of its README: "UPDATED VERSION AVAILABLE … This is an old version". It points to `cossartlab/cicada_analysis`, `cicada_nwb` and `cicada_gui`. The page says the port was checked "as read in August 2026", which is after the banner went up.
- **The current code reads event times directly.** `cicada_analysis/cicada_tools/imaging/detect_population_burst.py` (commit 0db65793, 2026-06-28) adds `detect_sce_from_spike_times` and `detect_sce_rolling`.
  - They detect SCEs straight from lists of event times.
  - They use a sliding coincidence window, a threshold from pooled circular-shift percentiles (99th by default), and peak picking.
- **So one difference is now out of date.** Section 3.5 says locust differs from CICADA because "we feed it our own list of events". That was true of the code that was ported. It is no longer true of the software the page cites as "current" (Hamon et al. 2026).
- **Fix:**
  - Say "master" instead of "main".
  - Say that the ported repository is the superseded one, and name `gitlab.com/cossartlab/cicada_analysis` as the current home.
  - In Section 3.5, qualify the difference: "…instead of letting CICADA find them (the version we ported required its own event detection; the current version also accepts event times, which we have not compared)".
- **Verified against source:** yes.

**M5. Section 11, binned SCE paragraph: Mao et al. 2001 was verified only one step short of the root.**
- **What I confirmed:** Cossart 2003 cites its reference 12 for "interval reshuffling", and reference 12 is Mao et al. 2001 (Neuron 32:883).
- **What I could not do:** open Mao 2001. OpenAlex lists it as a free copy on cell.com, but cell.com returned 403 / Cloudflare to curl and WebFetch. The earlier attempt in `mb_scratch/role02/mao_try.pdf` is the same Cloudflare page. It is not on the lit shelf.
- **What stays unconfirmed:** whether Mao 2001 thresholds coactive cells against surrogates, or only supplies the reshuffling. This is my open ⚠.
- **Fix:** get the PDF through a browser. Until then, write "Cossart et al. 2003 (reshuffling method from Mao et al. 2001)" rather than "goes back to Mao 2001".
- **Verified against source:** no.

## Minor

| # | Location | Issue | Fix | Verified |
|---|---|---|---|---|
| m1 | §11 LoCo: Hansen & Sawyers 1980 cited for "its cost in missed targets" | The paper measures the extra sensitivity loss of greatest-of in a *uniform* background (0.1–0.3 dB). The weakness §3.3 describes, a second event hiding the first, is multiple-target masking. Rohling 1983 analyses that, and so does Gandhi & Kassam 1988 (*IEEE T-AES* 24(4):427–445, doi:10.1109/7.7185, on the shelf, not cited). | Say "its small loss of sensitivity in a uniform background", and cite Rohling / Gandhi & Kassam for masking. | yes |
| m2 | §11: "The wrap-around form for calcium events: Bocchio 2020; Dard 2022" | Reads as an origin. Circular shifts on calcium data are older: Mölter 2018, which the page already cites, uses them. So do Romano et al. 2017 (PLoS Comput Biol 13:e1005526) and the CICADA code (March 2020). Bocchio's description matches (1,000 surrogates, 99th percentile), and so does Dard's (300 surrogates, 99th). | "used for calcium events by, among others, …" | yes |
| m3 | §11: Pipa 2008 "(small shifts, without wrapping around)" | "Small shifts of the entire train" is supported (§2.4). "Without wrapping" is not stated; the paper only zero-pads the ends of trains (Appendix 1). | Drop "without wrapping around", or mark it as inferred. | yes |
| m4 | §2 and §11: Harrison & Geman 2009 and Amarasingham 2012 for an "old idea" | These are a 2009 algorithm and a 2012 review. The lineage starts with Date, Bienenstock & Geman 1998 (Brown Univ. tech report), which Amarasingham cites and the shelf calls the root. Hatsopoulos et al. 2003 (Neurocomputing 52–54:25–29) is also earlier. | Add Date et al. 1998 as the root. | yes |
| m5 | §11 SPIKE-synch: PySpike cap "has had no effect since its version 0.8.0" | In v0.9.0 `get_tau`, `max_tau` fills only the neighbour slots that are missing. It still limits the window at a train's first or last spike when MRTS = 0; it has no effect for spikes with neighbours on both sides. The 0.7.0 code applied it everywhere. Fix filed upstream as PR #89 (open, 2026-09-01). | "…has had no effect on events with neighbours on both sides since 0.8.0". | yes |
| m6 | §11: CICADA reference | No year given. DataCite says issued 2020-07-20, deposited 2023-10-26. The Zenodo record metadata says CC-BY-4.0, but the `LICENSE.txt` inside the tarball is MIT (© 2019 cossart lab). | Add "(2020)". Write "record metadata CC-BY-4.0; code MIT". | yes |
| m7 | §11: Cossart 2003 "set the bar from the highest count in each surrogate" | This is a fair reading of "the number of coactive cells exceeded in a single frame in only 5% of these histograms" (1,000 reshufflings, P < 0.05), but the sentence is ambiguous. `docs/detector_history.md` line 386 reads it the other way ("pooled histogram"). The page's reading fits the text better, so the record should be corrected. | Add "P < 0.05, 1,000 reshufflings". Fix detector_history. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m9 | §11: format | DOIs are plain text, not links. Titles are given for some references (Grün, Harrison, Stella) and left out of others (Bocchio, Dard, Mao, Malvache, Cecchini, Hamon). | Link the DOIs and use one style. | yes |

## Citations an outside reviewer would expect but won't find (residual ⚠)

- **Kreuz et al. 2017** (M3). Also **Date et al. 1998** (m4) and **Gandhi & Kassam 1988** (m1). All three are on the shelf or open access.
- **Neural-network CFAR detectors:** for example Diskin, Beer, Okun & Wiesel 2024, "CFARnet", *Signal Processing* 223:109543, doi:10.1016/j.sigpro.2024.109543. Section 4 frames the tube models in radar terms (guard cells, center against surround), so a radar reviewer will look for this. I only spot-checked this literature; I did not search it.
- **autoMEA** (Hernandes et al. 2024, *Front Neurosci* 18:1446578, doi:10.3389/fnins.2024.1446578). It is on the shelf, where the notes call it the learned detectors' "architecturally our nearest neighbour". It is not cited.
- **rate+context:** the page says the neuroscience literature was not searched. Network-burst detection on multi-electrode arrays (MEA) is the obvious place to look. Not searched by me either.

## What I checked

- **Metadata:** Crossref for all 22 journal DOIs, plus DataCite and the Zenodo record page for CICADA (10041433 and 10041434). doi.org resolved the bioRxiv DOI 10.64898/2026.07.03.736318 (Hamon et al., posted 2026-07-08; first author Hamon, last author Dard at EPFL).
- **Source text:**
  - Cached copies of Stella, Pipa, Cossart 2003, Amarasingham, Bocchio, Dard, Mölter, Hansen & Sawyers, Finn & Johnson, Grün 2010, Hamon and Kreuz 2022.
  - Copies I fetched: Cecchini 2021 and Kreuz 2017.
  - The Hansen 1973 scan on the shelf.
- **Code:** GitLab `cossartlab/cicada` and `cicada_analysis`, and GitHub `mariomulansky/PySpike` at tags 0.7.0, 0.8.0 and v0.9.0.
- **Accepted without reading:** Grün 2002 I/II. Its moving window is confirmed through Grün 2010. Also Quian Quiroga 2002, Kreuz 2015, Mulansky & Kreuz 2016, Rohling 1983 (cached, header checked), Malvache 2016 and the learned-detector references. For these I checked metadata only; what the page says about them is general.

**Not searched:** Mao 2001 (blocked); where greatest-of began before 1973; where the term "SCE" first appeared; MEA network-burst detection; neural-network CFAR beyond one search.

**Nobody asked (⚠):** there is no record of anyone contacting the CICADA authors (Dard, Picardo, Cossart) about the port, the superseded repository, or the new event-time functions. Ask Tony before calling locust's differences settled.

**Private correspondence:** the page cites one item (Kreuz, 2026-04-23), paraphrased and dated. It contains no quoted correspondence.

## Files

- Built page reviewed: `<scratchpad>\review\detector_review_plain.txt`
- Evidence I fetched (in the same scratchpad): `scratchpad\r2lit\` holds `cicada-1.0.3.tar.gz`, `sce_stats_utils.py`, `dpb.py` (current upstream code), `cecchini2021.pdf/.txt`, `kreuz2017.pdf/.txt`, and `pb070.py`, `pb080.py`, `pb090.py` (PySpike backends).
- Project record that contradicts the page on Hansen 1973: `<worktree>\docs\detector_history.md` (§4.1; line 386 for the Cossart 2003 reading)

Sources:
- [Mao et al. 2001, Neuron (cell.com, blocked)](https://www.cell.com/fulltext/S0896-6273(01)00518-9)
- [PubMed 11738033](https://pubmed.ncbi.nlm.nih.gov/11738033/)
- [CICADA Zenodo record](https://zenodo.org/records/10041434)
- [gitlab.com/cossartlab/cicada](https://gitlab.com/cossartlab/cicada) and [cicada_analysis](https://gitlab.com/cossartlab/cicada_analysis)
- [PySpike](https://github.com/mariomulansky/PySpike)
- [Cecchini et al. 2021](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008963)
- [Kreuz et al. 2017, NJP](https://iopscience.iop.org/article/10.1088/1367-2630/aa68c3)
- [CFARnet (arXiv 2208.02474)](https://arxiv.org/abs/2208.02474)
- [CFARnet, Signal Processing](https://www.sciencedirect.com/science/article/abs/pii/S0165168424001622)
