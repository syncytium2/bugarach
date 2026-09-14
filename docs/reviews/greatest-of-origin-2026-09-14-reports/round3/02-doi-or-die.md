GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2 (citations and references): findings, round 3 blind pass

The attribution holds up. Every quotation, date, volume, page range, DOI, patent fact and HathiTrust ISBN I checked in the changed text matches its source. There is one claim about the search that the sources contradict, one sentence that rules out an origin, one omitted identifier fact, and two residual `⚠` gaps (a place nobody searched, and no record of anyone being asked). Nothing is blocking.

## Findings

Format: location · issue · severity · suggested fix · verifiable against a source

1. **detector_history.md §4.1, Gandhi & Kassam bullet** · The doc says *"Their reference list is our only source for the 1973 paper's pages, 325–332."* That is false. The OpenAlex record the search says it consulted (W2416657781) gives volume 105, pages 325–332. It links to a CiNii Research record (NAID 10011821161, CRID 1573668924726035968) with the same pages, the venue "Radar-present and future" and the publisher "IEEE Conference Publication". Both records look like they were built from citing papers, so neither is independent of the volume. Also unmentioned: 325–332 and the patent's "1–8" are both eight pages long. · **major** · Suggested wording: "The pages 325–332 come from their reference list and from citation-derived catalogue records (OpenAlex, CiNii). The patent gives 1–8, also eight pages. Neither comes from the volume itself." · yes

2. **detector_history.md §4.1, Rohling bullet, last sentence** · *"so his 'proposed' cannot mean first"* rules out an origin (Moore & Lawrence). It rests on the memo's date and content, and on what the 1973 paper covered, all known only second-hand (Hansen & Sawyers; Gandhi & Kassam). The brief says nothing may assert an origin, positive or negative. · **major** · Suggested wording: "Moore & Lawrence's talk is later than both the memo and the 1973 paper, so on the 1980 and 1988 accounts his 'proposed' does not settle who was first." · yes

3. **detector_history.md §4.1, "The search" paragraph (ISBN)** · Both ISBNs are quoted correctly and both check digits are valid. But HathiTrust record 011456921, which the brief lists and the doc omits, assigns 0 85296 114 6 (the notice's number) to **IEE Conference Publication 103**, *Conference on the Use of Digital Computers in Measurement*, York, 24–27 September 1973. So the conflict the doc leaves open has a checkable explanation. · minor · State the fact without deciding it: "HathiTrust record 011456921 gives 0 85296 114 6 to Conference Publication 103." · yes

4. **detector_history.md §4.1, "HathiTrust holds a search-only scan of a US university library's copy"** · There are two search-only scans, not one. Record 001618382 has the standalone copy (item mdp.39015000988512). Record 011456921 has a bound volume at another US university, labelled "no.103-105(1973)" (uiug.30112007966838), which appears to contain No. 105. The standalone scan comes from the same library whose licence stamp is on the shelf copy of Hansen & Sawyers. That makes a print request or in-volume search there a cheap next step. I tried the in-volume search (see Coverage below) and was blocked. · minor · Say "two search-only scans" and give both item IDs. Do not name the library in public text if that is being avoided. · yes

5. **detector_history.md, paragraph after the §4 table, and the Sources entry** · *"Radar quotations are checked by hand against text extracted from those PDFs"* covers only the four papers. But §4.1 also quotes the IEE notice ("GREGERS HANSEN, V.") and the patent. The notice PDF and the IEEE author-profile PDF are on the shelf, but the shelf README has **no entry** for either. The shelf's own rule says a PDF with no entry is indistinguishable from one "someone downloaded and forgot". The Sources entry says the shelf has "read status per work". · minor · Add entries for both PDFs to the shelf README. Change the sentence to say quotations are checked against the shelf PDFs (four papers plus the IEE notice) and the patent text. · yes

6. **detector_history.md §7 item 2, ⚠ sentence** · *"All four primaries are read"* is still there. The GO row's "primary" was the 1980 loss analysis, which is not the origin, so "primaries" now overstates. *"…and could not tell the two apart"* has no clear referent, and nothing on the shelf or the page supports it. · minor · Change to "All four papers are read." Replace the second clause with "it read the 1980 loss analysis, not the 1973 paper the attribution named." · no (process claim)

7. **detector_history.md §4 table, `LoCo, maxlt` row** · The "held?" cell says **read in full** next to an attribution cell that opens "origin **not established**". A reader can take "read in full" to mean the origin was read. · minor · Change the held cell to "Hansen & Sawyers read in full; 1973 paper not held". · yes

8. **GLOSSARY.md CFAR paragraph** · (a) *"four radar papers were retrieved and read on 2026-08-22"*: the shelf README records five works saved that day, four read in full plus Weinberg 2017 read in part. (b) *"an interface2 audit … identified the mechanism of every lineage row"* cannot be checked from anything I was allowed to open. · minor · Change (a) to "four radar papers were read in full". Leave (b), but note the source. · (a) yes, (b) no

9. **GLOSSARY.md CFAR paragraph (edited in this diff), and the §4 table / cfar_scope.html by the same pattern** · Outside the GO brief, but in the edited paragraph. *"`rate_detect` is cell-averaging CFAR (Finn & Johnson 1968)"* keeps the "(author year)" origin form the diff just withdrew for GO. A held source contradicts it: Gandhi & Kassam's own reference [2] is Steenson B.O., *"Detection performance of a mean-level threshold"*, IEEE T-AES AES-4, **July 1968**, 529–534. That is earlier than Finn & Johnson (September 1968). The Sawyers memo's title ("mean level threshold detectors") uses the same vocabulary. The CA-CFAR origin has the same untraced shape as the Hansen 1973 credit. · major (adjacent, not blocking this deliverable) · File it separately. Don't fix it silently in this PR. · yes

10. **README.md LoCo/CoactDetect bullet** · The Hansen & Sawyers citation has no title, while every other entry in the list has one. The metadata is correct (Crossref: *Detectability Loss Due to "Greatest Of" Selection in a Cell-Averaging CFAR*, AES-16(1), 115–118, January 1980, doi:10.1109/TAES.1980.308885). · minor · Add the title in italics. · yes

11. **§4.1 "What we do not know" (residual ⚠: unsearched literatures)** · The search names databases (HathiTrust, Xplore, IET, OpenAlex, Semantic Scholar) but not these literatures:
    - radar textbooks and handbooks from before and around 1973;
    - pre-1973 patents on split-gate or greatest-of CFAR circuits;
    - the mean-level-detector line (Steenson 1968, Dillard 1974, both in Gandhi & Kassam's list);
    - the Japanese Weibull-clutter literature that cites the 1973 paper. The CiNii record lists two citing papers, including *"Detection of Aircraft Embedded in Ground Clutter by Means of Non-Doppler Radar"*. The NEC patent comes from that group.

    None of this is evidence of earlier work. It is where nobody has looked. · minor · Add one sentence: "not searched: radar textbooks and handbooks, pre-1973 patents, the mean-level-detector papers, the Japanese literature citing the 1973 paper." · no

12. **§4.1 (residual ⚠: nobody asked)** · The section doesn't say whether anyone has been asked, for example a radar colleague, IEEE AESS history contacts, or anyone connected to either author or to the Sawyers memo. "Nobody was asked" is itself a residual. · minor · Record it either way: *No correspondence has been sought*, or cite who was asked and the date as personal communication (paraphrased, not quoted). · no

## Verified as written, no change needed

- **IEE notice (Proc. IEE 120(11), November 1973, p. 1391):**
  - author listed as "GREGERS HANSEN, V."
  - title "Constant-false-alarm-rate processing in search radars"
  - 23rd–25th October 1973, Savoy Place, London
  - Conference Publication 105
  - ISBN 0 85296 114 6
- **HathiTrust 001618382:** ISBN 085296112X, 437 pp., IEE conference publication no. 105.
- **Hansen & Sawyers 1980:**
  - The three quotations are exact: "a simple rule for determining the detectability loss", "based on a simplified analysis and simulation results of limited accuracy", "are derived from independent work performed by the two authors".
  - Reference [1] (IEE Conf. Publ. No. 105, 23–25 Oct 1973, no pages given) matches.
  - The Sawyers memo title and its date, 15 February 1972, match.
  - "graphs … were prepared from [2]" matches.
  - Pages 115–118 are correct; the paper ends on 118.
  - The DOI resolves on Crossref to the right metadata.
- **US 4,318,101:**
  - Original assignee Nippon Electric; filed 1980-03-11; granted 1982-03-02.
  - "proposed another CFAR processor for the Weibull clutter in general" is exact (the source has "solely" before it), and Goldstein's AES-9(1), January 1973 processor comes immediately before it.
  - "paged 1-8" and "as disclosed in the Hansen report" match.
  - The first average calculator uses every register stage except the centre, so it does average both sides.
  - The words "greatest", "larger of" and "maximum of" do not appear.
- **Rohling 1983:** both quotations are exact. [2] is Hansen & Sawyers 1980. [3] is Moore & Lawrence, IEEE International Radar Conference, Washington DC, 1980. No 1973 Hansen citation.
- **Gandhi & Kassam 1988:** both quotations are exact. [9] is Hansen 1973, "Proceedings of the IEEE 1973 International Radar Conference, London", pp. 325–332. [10] is Hansen & Sawyers 1980. The reference-list order confirms the numbering.
- **Zottl and Ward papers:** Zottl AES-7(4) 1971 and Ward AES-8(5) 1972 match the IEEE author-profile PDF; Ward's pages 648–652 match Hansen & Sawyers' reference [4] and the patent. Neither is on the shelf.
- **Finn & Johnson 1968 and Weinberg 2017 (both on the shelf):** neither mentions greatest-of selection, so "sources we hold describe work on greatest-of from 1972 onward" stands. Weinberg cites Hansen & Sawyers only as one of several example works, with no claim about who was first.
- **Mechanism and tooling:** the `loco.py` docstring and code confirm `maxlt` takes the max of the trailing and leading half-context thresholds, as the README says. `tools/verify_quotes.py` describes itself as provisional and not a gate, and nothing in tests, hooks or CI calls it, which matches "does not block anything".
- **Shelf README:** confirms the two library orders (Hansen & Sawyers, Gandhi & Kassam) were delivered on 2026-08-22.
- **Anchor:** `#41-where-greatest-of-began` matches the heading.
- **Other pages:** the cfar_scope.html and proposal-footer corrections are consistent with §4.1, and neither states a new origin.

## Coverage

**Searched:**
- all seven PDFs on the radar shelf, with both extraction modes;
- the Google Patents text;
- the HathiTrust catalogue API, both records;
- Crossref (the DOI, plus a title search);
- OpenAlex;
- CiNii Research;
- two general web searches.

**Tried and blocked:**
- HathiTrust in-volume full-text search on both scans (bot challenge, then HTTP 403);
- Semantic Scholar (HTTP 429). The doc's claim about Semantic Scholar is therefore unverified by me.

**Not searched:** IEEE Xplore, IET Digital Library, radar textbooks and handbooks, pre-1973 patents, the mean-level-detector and Japanese Weibull-CFAR literatures, and correspondence.

**Where I stopped on origin:** one step short. The 1973 paper and the 1972 memo are both unread, and no text of either was reachable from here.

Files reviewed (in the worktree `greatest-of-origin-not-established`): `docs/detector_history.md`, `docs/GLOSSARY.md`, `README.md`, `docs/learned/cfar_scope.html`, `docs/proposals/2026-09-10-coordination-without-labels.html`, `docs/INDEX.md` (changed in the diff but not in the brief; no findings), `src/bugarach/detectors/loco.py`, `tools/verify_quotes.py`, and `<darkroom>/bugarach/lit/radar/README.md`.

Sources:
- [US4318101 (USPTO)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4318101)
- [OpenAlex W2416657781](https://openalex.org/W2416657781)
- [CiNii Research record](https://cir.nii.ac.jp/crid/1573668924726035968)
- [HathiTrust catalogue record 001618382](https://catalog.hathitrust.org/api/volumes/full/recordnumber/001618382.json)
- [HathiTrust catalogue record 011456921](https://catalog.hathitrust.org/api/volumes/full/recordnumber/011456921.json)
- [Crossref 10.1109/TAES.1980.308885](https://api.crossref.org/works/10.1109/TAES.1980.308885)
- [Weinberg, arXiv:1709.09786](https://arxiv.org/pdf/1709.09786)
