GRANT 2 MISMATCH — missing none (WebSearch and WebFetch arrived deferred and were loaded through ToolSearch); holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch / __update (both can write), and deferred Dropbox and Gmail write tools

I used none of the forbidden tools on the repository. My only writes were scratch files under …\scratchpad\mb\role02\ (text extractions, Crossref dumps, and the downloaded RCA Review issue in dl_rca\), all made through Bash. This mismatch is a finding about the run, not the artifact: the run record's `roles:` line should say role 2 ran on a fallback path with an over-broad grant.

**Artifact checked:** `docs/dissertation/chapter-1-aim0.md`. Its blob hash on disk, 14d63527d4d1…, matches the brief.

## What I checked

- **References new in this revision (Finn & Johnson 1968, Rohling 1983, Perkel, Gerstein & Moore 1967, Malvache et al. 2016).** I read each one from the library PDF (pymupdf extraction) against every sentence in the chapter that cites it: §1.2.3, §1.2.4 item 2, §1.3.2 and §1.3.6.
- **Identifiers for all 51 entries.**
  - Crossref bibliographic match for every entry.
  - Live `doi.org` resolution (curl, HTTP 302 with the target recorded) for the 46 that have a DOI, plus the arXiv DataCite DOIs for the five "read as arXiv" entries.
  - Non-DOI works checked by their own route:
    - RCA Review: September 1968 issue fetched live from worldradiohistory.com; its contents page reads Vol. 29 No. 3, Finn & Johnson p. 414.
    - JMLR: the jmlr.org abstract page gives 18(199):1–38, 2018.
    - NeurIPS 2020: proceedings PDF and virtual pages, via web search.
    - Greiner 1909: zbMATH API (JFM).
    - Kish 1995: the held scan only. Web search found no publisher page; this is a gap in the route, not a failure.
- **Text spot-checks of older references whose wording carries a load-bearing claim.**
  - Kruskal 1958 for the τ–arcsin relation and the Cramér credit.
  - Shah & Wainwright for "Copeland counting".
- **Lab attribution for the "same group" claims** (Cecchini 2021, Kreuz 2022, Mariani 2025), by last author from Crossref.
- **Forward search** of the Kreuz group's work after the 2026 review.
- **Records consulted:** the prior-art record, `radar/README.md`, `coordination/README.md`, and the Kreuz correspondence todo.
- **Not re-verified this round:** the claims attached to the references carried over from 5c3605a9. Their metadata was checked; their claims were not re-read, apart from the Kruskal and Shah spot-checks above.

## Findings

Each finding gives location · issue · severity · suggested fix · verified against a source (yes/no).

1. **§1.2.3 ("Finn & Johnson (1968) set a radar's detection threshold… The family of methods built on that idea is called CFAR") and §1.3.6.**
   - **Issue:** this credits CFAR's name, and implicitly the idea, to Finn & Johnson. Their own §II says otherwise: *"This conventional system, the constant false-alarm-rate regulation system (CFAR) was designed to adapt to changes in the variance of the detector output…"*. That earlier CFAR sampled noise in the radar's dead time. Finn & Johnson extended it to estimates from the cells surrounding the cell under test.
   - **Origin traced back:** the paper cites its precursors.
     - Finn 1966, "Adaptive detection in clutter": Fifth Symposium on Adaptive Processes / Proc. NEC XXII, pp. 562–567, doi:10.1109/sap.1966.271149, resolved.
     - Finn, Dec. 1967, *RCA Rev* 28(4):653–678, per the library README's check of the contents page. Finn & Johnson themselves misprint it as "Vol. 29".
     - Steenson, July 1968, "Detection performance of a mean-level threshold", *IEEE Trans AES* 4(4):529–534, doi:10.1109/taes.1968.5409020, resolved.
     - I stopped at Finn 1966, the earliest paper the chain reaches. Its text is not held.
   - **Severity:** medium (origin and attribution).
   - **Fix:** "CFAR, first a threshold set from receiver noise, was extended to an estimate from the cells around the cell under test by Finn (1966, 1967) and Finn & Johnson (1968; see also Steenson 1968)". Alternatively, keep Finn & Johnson as the standard citation and drop "built on that idea is called CFAR".
   - **Verified:** yes.

2. **§1.3.6 ("with the cell under test and its neighbors left out, is cell-averaging CFAR (Finn & Johnson 1968)").**
   - **Issue:** Finn & Johnson leave out only the cell under test. Their Fig. 2 reads "excluding cell under test", and the paper has no guard band. §1.2.3 already has this right ("routine by 1983 (Rohling 1983)"), so §1.3.6 contradicts it. The library's radar README records the same correction.
   - **Severity:** medium (one primary credited with something it does not contain).
   - **Fix:** "…with the cell under test left out, is cell-averaging CFAR (Finn & Johnson 1968); leaving out its neighbors too (guard cells) was routine by Rohling (1983)".
   - **Verified:** yes.

3. **§1.3.6 ("Rohling (1983) set out the family's variants, including an ordered-statistic estimate…").**
   - **Issue:** slightly overstated. Rohling recalls two variants (cell-averaging, and cell-averaging with greatest-of selection, citing Hansen & Sawyers 1980 and Moore & Lawrence 1980) and proposes the ordered-statistic one. He credits trimming the largest reference cells to Weiss (1982) and Rickard & Dillard (1977). The ordered-statistic resistance to a second target in the reference cells is supported (abstract and Fig. 3).
   - **Severity:** low.
   - **Fix:** "Rohling (1983) compared cell-averaging with its greatest-of variant and introduced an ordered-statistic estimate that resists…".
   - **Verified:** yes.

4. **§1.7 and Table 1.9, last row ("no wider search (super-resolution and radar resolution are the obvious fields)").**
   - **Issue:** the paper added in this revision already analyses exactly this. Finn & Johnson's abstract: *"Target pair resolution capabilities of these adaptive detection modes are also analyzed."* Rohling cites Trunk 1978, "Range resolution of targets using automatic detectors", *IEEE Trans AES* 14:750–755. The radar-resolution precedent is now on the shelf and unused, while the table still calls that field unsearched.
   - **Severity:** medium (the closest precedent is absent from the comparison).
   - **Fix:** read Finn & Johnson's target-pair section (held) and state how §1.7 relates to it. List Trunk 1978 as a needed paper.
   - **Verified:** yes for presence in Finn & Johnson. Not checked against §1.7's content.

5. **§1.2.3 and §1.2.4 item 2 ("Finn & Johnson also named the method's weakness: a second target in the reference cells raises the estimate and hides the first (masking)").**
   - **Issue:** supported. Abstract: *"The introduction of a second target in one of the threshold control cells introduces a masking effect equivalent to a 1-dB loss…"*. One nuance: Finn & Johnson quantify the effect as small (1 dB worst case with 100 cells). Masking that drives the threshold up sharply, as in Figure 1.2 D, is Rohling's Fig. 3.
   - **Severity:** low.
   - **Fix:** optionally cite Rohling beside Finn & Johnson for the severe form.
   - **Verified:** yes.

6. **§1.3.2 (Perkel, Gerstein & Moore 1967 call the two-cell version the cross-correlation histogram) and §1.3.6.**
   - **Issue:** supported (p. 422: "(b) The cross-correlation histogram. We select spikes in train A and construct a histogram of the times to all spikes in train B, both forward and backward…"). Metadata is correct: *Biophys J* 7(4):419–440, doi:10.1016/S0006-3495(67)86597-4, resolved. The paper is the source of the name, not of cross-correlating spike trains: it cites Gerstein & Clark 1964 and Moore, Perkel & Segundo 1966. The chapter claims only the name, which is fine.
   - **Severity:** none.
   - **Verified:** yes.

7. **§1.3.6 ("Counting the cells active together in a short window, against a threshold, is how synchronous calcium events are found… (Malvache et al. 2016)").**
   - **Issue:** the main text supports this. Fig. 1A shows "summed activity of cells (over a 200-ms window). Red dashed line indicates significance threshold for synchronous activity detection (five cells in this example)", with P < 0.01 per the supplementary methods. Metadata is correct: *Science* 353(6305):1280–1283, doi:10.1126/science.aaf3319, resolved.
     - The detection rule itself is in the Materials and Methods supplement, which is not held (`coordination/README.md` says so). The surrogate behind the threshold is unverified.
     - Malvache 2016 is an instance, not the origin. The root of window-count detection in calcium imaging was not traced.
   - **Severity:** low.
   - **Fix:** none needed for the claim as worded. Add the supplement to the needed list if the chapter ever describes how the threshold is set.
   - **Verified:** yes for the main text. The supplement is paywalled.

8. **References: Greiner R (1909), "*Z Math Phys* 57. ⚠ (not opened; pages unverified)".**
   - **Issue:** placeholder metadata. zbMATH/JFM 40.0284.02, resolved live, gives the full record: Greiner R (1909), "Über das Fehlersystem der Kollektivmaßlehre", *Z Math Phys* 57:121–158, 225–260, 337–373. Whether it holds the τ–arcsin relation remains unverified, so the ⚠ on the content claim stays.
   - **Severity:** low.
   - **Fix:** complete the entry from the JFM record and keep "⚠ not opened".
   - **Verified:** yes (bibliographic only).

9. **§1.8.2 and Table 1.9 ("Kruskal (1958, sec. 4) derives from the quadrant-probability relation as stated by Cramér").**
   - **Issue:** the claim checks. In §4 Kruskal gives ρ = sin[(π/2)τ] "a direct consequence of the analogous formula for [the quadrant measure]", and §3 credits that formula to "Cramér [12, p. 290]". Cramér is a named attribution with no entry in the reference list.
   - **Severity:** low.
   - **Fix:** add "Cramér H (1946). *Mathematical Methods of Statistics*. Princeton University Press, p. 290 ⚠ (not opened; via Kruskal)", or write "via Kruskal's citation of Cramér".
   - **Verified:** yes.

10. **Reference list: incomplete page ranges.**
    - Staude, Rotter & Grün 2010, CuBIC: "29:327" should be **29:327–350**.
    - Silva, Feng & Foster 2015: "18:1772" should be **18:1772–1779**.
    - Neyman & Scott 1952: "116:144" gives the first page only (Crossref has no end page).
    - **Severity:** low.
    - **Fix:** complete the two ranges from Crossref.
    - **Verified:** yes.

11. **Reference list: Daley & Vere-Jones 2003.**
    - **Issue:** no DOI or ISBN is given. doi:10.1007/b97277 (Springer, 2003, vol. I, 2nd ed.) resolves.
    - **Severity:** low.
    - **Fix:** optionally add the DOI.
    - **Verified:** yes.

12. **All other references: existence and metadata.**
    - All 46 DOIs resolve at doi.org. The five arXiv DOIs resolve. Authors, year, journal, volume and pages match Crossref, apart from item 10.
    - Online-first years differ from print years: Crossref gives 2009 for Peyrache 2010 and CuBIC 2010, and 2023 for Wang 2024. The chapter's print years are correct.
    - DeFazio 2026: e70298 is vol. 38, issue 11. Kreuz 2026: article 21 in 120(3–4).
    - No Crossref update-to relation (correction or retraction) was found for DeFazio 2026. I did not sweep update relations for the others.
    - **Severity:** none.
    - **Verified:** yes.

13. **Lab attribution: "The same group applied it…" (Cecchini 2021, Kreuz 2022, Mariani 2025).**
    - **Issue:** the claim holds. Kreuz is last author of Cecchini 2021 and Mariani 2025 and first author of Kreuz 2022. I checked authorship from the Crossref author list only. Crossref carries no affiliations for these papers, so the affiliation was not looked up.
    - **Severity:** none.
    - **Verified:** yes (authorship only).

14. **Correspondence (⚠ residual, §1.3.6 Detectors and §1.9.2).**
    - **Issue:** the repository records that Kreuz answered Tony's SPIKE-synch questions by email in April 2026 (`docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`). In paraphrase: his group detects events with a SPIKE-synchronization criterion together with a threshold on the mean calcium signal, plus a maximum-gap rule. He named thresholding the peri-stimulus time histogram (PSTH) as the common approach elsewhere, with Mainen & Sejnowski 1995 as a hedged earliest use. That bears on the origin of the window-count detector, and the chapter does not use it.
      - The chapter's statement that the two enquiries (Grün's lab, and Kreuz on annealing versus ranking) "have not been sent" is accurate for those specific questions.
    - **Severity:** low.
    - **Fix:** cite as "Kreuz, personal communication, April 2026" if used, without quoting, per CLAUDE.md. List Mainen & Sejnowski 1995 (doi:10.1126/science.7770778, not resolved in this review) as a lead for the detector's origin.
    - **Verified:** the record yes; the email itself was not seen.

15. **Unsearched fields (⚠ residual, Table 1.9: "The at-most-one-event term… not found").**
    - **Issue:** the chapter lists "point-process counting theory beyond the textbooks" as unsearched. Counter dead time (non-paralysable dead-time corrections in particle counting) and Matérn hard-core processes are the obvious places a hard-core counting correction would already exist. Neither was searched, and the prior-art record does not show them searched either.
    - **Severity:** low (an unsearched field, not an absence of prior art).
    - **Fix:** name dead-time counting and hard-core point processes among the fields not searched.
    - **Verified:** no.

16. **Forward trace.**
    - For the Kreuz tools, the 2026 review is the latest found. A web search for later SPIKE-order or Synfire Indicator papers found nothing newer.
    - For CFAR, the Gregers Hansen, Hansen & Sawyers, Gandhi & Kassam and Weinberg papers on the shelf cover the field's later work. The chapter correctly makes no novelty claim for CFAR.
    - **Severity:** none.
    - **Verified:** yes.

## Papers needed (not in the library)

- Trunk 1978, "Range resolution of targets using automatic detectors", *IEEE Trans AES* 14:750–755. DOI not looked up.
- Finn 1966, doi:10.1109/sap.1966.271149 (IEEE, paywalled).
- Steenson 1968, doi:10.1109/taes.1968.5409020 (paywalled).
- Malvache et al. 2016, Materials and Methods supplement (Science, paywalled).
- Grün 1996 (named in the chapter as not held).

## Sources

- https://zbmath.org/2637044
- https://www.jmlr.org/papers/v18/16-206.html
- https://www.worldradiohistory.com/ARCHIVE-RCA/RCA-Review/RCA-Review-1968-09.pdf
- https://papers.neurips.cc/paper_files/paper/2020/file/a5481cd6d7517aa3fc6476dc7d9019ab-Paper.pdf
- https://neurips.cc/virtual/2020/oral/18888
- https://arxiv.org/pdf/2510.07140

unreached: 0
