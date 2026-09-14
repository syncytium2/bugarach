GRANT 1 ok — Read, Grep, Glob, Bash

# Claim ledger: Hansen 1973 update (role 1, "Prove It")

**Result: no blocking findings.** Every number, quotation, page, citation and attribution in the change matches its source. There is one major finding: the copy of the document that readers open, in the darkroom (the shared Dropbox output folder), has not been rebuilt. The minor findings are about wording and a few leftover inconsistencies.

## What I checked, and how

- **The shelf PDF, rendered.** The PDF has no text layer I could use, and pypdfium2 and fitz are not installed. I pulled the scanned page images out of the PDF and decoded them with PIL. I read these pages as images: the cover (p. i), the copyright page (p. ii), pp. 325, 326 and 327, the reference list (the bottom of p. 329 and the top of p. 330), and the figure page (p. 331).
- **The other sources.**
  - The text extractions of Hansen & Sawyers 1980, Gandhi & Kassam 1988, Rohling 1983, the patent and the Proc. IEE contents notice.
  - The HathiTrust catalogue, queried live.
  - The shelf README, `docs/SESSIONS.md` on origin/main, and the local session board.
  - The rebuilt HTML, in both the repo and the darkroom.
- **Not opened:** `docs/reviews/`.

## Claim ledger

| # | Quoted claim (location) | Source checked | What the source says | Verdict |
|---|---|---|---|---|
| 1 | Title, author, IEE Conf. Publ. 105, *Radar — present and future*, London, 23–25 Oct 1973 (§4.1) | Cover, p. 325, Hansen & Sawyers ref [1], contents notice | Title and author are on p. 325; dates and venue on the cover. The number "105" is **not printed** anywhere in the loan copy; it comes from the Proc. IEE notice and from Hansen & Sawyers | match |
| 2 | pp. 325–332 (§4.1, table, lit_needed) | Page numbers on the scans | The paper starts on p. 325 and its figures end on p. 332 | match |
| 3 | The volume prints ISBN 0 85296 112 X; the notice prints 114 6 | Copyright page image; contents notice line 73; HathiTrust (ISBN-13 9780852961124) | 112 X is on the copyright page; 114 6 is in the notice. HathiTrust's ISBN-13 is the same number as 112 X | match |
| 4 | HathiTrust search-only scan, record 001618382, supplied the loan copy | PDF stamp (item mdp.39015000988512, HathiTrust Resource Sharing, generated 2026-09-14 19:22 GMT); HathiTrust API | The item belongs to record 001618382 and is listed as "Limited (search-only)" | match |
| 5 | p. 326 quotation: "A technique which can be used … to normalize the output" | p. 326 image | Word for word | match |
| 6 | "a survey of available results" (Conclusions) | p. 329 text | The words are there. The sentence limits the survey to CFAR loss in stationary Gaussian noise, though (see finding 3) | match, but paraphrase stretched |
| 7 | Fig. 6 is a cell-averaging CFAR "using 'greatest-of' selection" | p. 326 text; p. 331 caption | The quoted words come from the **body text on p. 326**. The caption reads "Conventional cell averaging CFAR processor with 'Greatest-Of' selection" | match (wording from the text, not the caption) |
| 8 | Fig. 5 case: 32 reference cells, linear envelope detection, Pf 10⁻⁵, 20 dB step | p. 326 image; Fig. 5 label "N = 32" | "N=32 and using linear envelope detection", "Pf = 10⁻⁵", a 20 dB step starting in cell 10 | match |
| 9 | Expected false alarms: 0.15 for cell-averaging, 0.0008 for greatest-of | p. 326 (0.15), p. 327 (0.0008), Fig. 5 labels | Same values in the text and on the figure | match |
| 10 | p. 327 loss rule: divide the number of reference samples by √2 | p. 327 image | "divided by √2" (the OCR drops the radical). Recomputed from the paper's own worked example: 5/32 = 0.156 for plain cell-averaging, and 5/(32/√2) = 0.221 against the printed 0.22 for greatest-of (1.1 dB) | match |
| 11 | None of these passages or figure captions carries a reference | Images of pp. 326, 327 and the Fig. 5–7 captions on p. 331 | No bracketed reference in any of them. The nearest, [13], belongs to the paragraph before, about clutter power varying with range | match |
| 12 | "neither attributes it to anyone nor presents it as new" | pp. 325–327 | It is introduced as "A technique which can be used…"; the results come from "Numerical computations have shown" and "it was found". Nothing claims novelty. By contrast, the paper does say "proposed" for generalized CFAR (Fig. 10, ref [19]) | match |
| 13 | Cell-averaging cited to earlier work, among it Finn & Johnson 1968 and Steenson 1968 | p. 325 "[2-7]"; refs 5 and 6 | Present | match |
| 14 | Cell-averaging citations: Hall 1962–63, Hansen 1965, Finn 1967, Steenson 1968, Hansen & Ward 1972 | Refs 2, 3, 4, 6 and 7 (images) | All present. The list **leaves out ref 5, Finn & Johnson** (see finding 4) | match, list incomplete |
| 15 | Zottl 1971; 1972 generalized-CFAR abstract | Ref 12 (Siebert/Dicke-fix detectors, AES-7, July 1971); ref 19 (1972 ISIT, Asilomar, abstracts) | Present. Ref 12 is cited for coherent CFAR, i.e. for another purpose | match |
| 16 | The Weibull CFAR's general structure is cited to Hansen's own 1972 abstract | p. 328 "…as shown in Fig. 10 [19]"; Fig. 13 is the Weibull CFAR | Present | match |
| 17 | The 1973 paper does not cite the Sawyers memo | Refs 1–21 | No Sawyers entry | match |
| 18 | Hansen & Sawyers' co-authors were made aware of each other's work "by a third party" | Their acknowledgment | They thank David Shanks of Technology Service Corporation "for informing each of the other's work" | match |
| 19 | Patent: "proposed another CFAR processor for the Weibull clutter in general", paginated 1–8, no discussion of greatest-of; filed 1980, granted 1982 | patent.txt | "Hansen solely proposed another CFAR processor…"; "paged 1-8"; zero hits for "greatest"; filed 1980, published 1982-03-02 | match |
| 20 | Gandhi & Kassam: pp. 325–332 match the volume; they call the venue an IEEE conference | Their reference list | "Proceedings of the IEEE 1973 International Radar Conference, London, pp. 325-332" | match |
| 21 | Two later sources credit different people with proposing it | Rohling ("Moore et al. [3] proposed"); Gandhi & Kassam ("Hansen [9] has proposed") | Both present | match |
| 22 | "Five of the table's papers are held and read in full" | Table rows; shelf listing | Finn & Johnson, Hansen 1973, Hansen & Sawyers, Rohling and Gandhi & Kassam are all on the shelf. Weiss and Rickard & Dillard are cited only through Rohling | match (read status taken on trust) |
| 23 | Shelf README entry: ISBN, record, private-study limit, OCR reliable up to p. 326 | README lines 177–206; PDF cover sheet | All consistent. The header count ("five read in full … one read in part, plus two evidence files") also matches | match |
| 24 | Todo: Finn 1967 as Hansen cites it: vol. 29, pp. 653–676, Dec. 1967; Hansen gives Finn & Johnson as vol. 30 | Refs 4 and 5 (image) | Numbers match. Hansen prints the author as **"H. H. Finn"**; the todo and README write "H. M. Finn" | numbers match; author initials differ |
| 25 | "the journal's contents page says 29" | Only the repo table (29(3)); the Finn & Johnson PDF was not text-extracted | Not checked against the journal | unverifiable here |
| 26 | lit_needed: "Nobody will read it" and "the talk" are earlier readings in the entry | lit_needed lines 122 and 127–139 | Both present | match |
| 27 | Todo: "the darkroom rebuild and the shelf README rows … are claimed on docs/SESSIONS.md" | origin/main `docs/SESSIONS.md` | Claim WSMIP065/shelve-hansen-1973 is active and covers `lit/radar/` and `detector_history.html`. The branch's own copy of the board does not have it yet | match (on main) |
| 28 | The built `docs/learned/detector_history.html` is rebuilt | Repo HTML | Contains "attributed to no one" and "divided by √2" | match |
| 29 | Proc. IEE 120(11), Nov 1973, p. 1391 notice | The contents file has no volume or page header I could tie to 120(11) p. 1391 | — | unverifiable |
| 30 | "IEEE Xplore / IET refused automated queries; OpenAlex / Semantic Scholar hold records without text; no correspondence recorded" | No record available to me | — | unverifiable (a record of the process) |

## Findings

| # | Location | Issue | Severity | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 1 | `<darkroom>/bugarach/detector_history.html` | The copy a reader opens is **dated 2026-08-29**. It is 258 KB against the repo's 277 KB, has none of the new text, and does not even carry the earlier "not established" wording (0 hits). Only the repo copy was rebuilt. The todo records the darkroom rebuild as claimed, not done. | major (delivery) | Rebuild the darkroom copy before calling this delivered, and diff it against the repo HTML. | yes |
| 2 | §4.1, Fig. 6 bullet | The quoted words *"using 'greatest-of' selection"* come from the p. 326 body text, not the Fig. 6 caption. The next paragraph talks about "figure captions", so a reader will take the quotation as the caption. Figs. 5 and 6 (p. 331) also have no page number. | minor | Add "(p. 326)" after the quotation, or quote the caption itself ("Conventional cell averaging CFAR processor with 'Greatest-Of' selection", p. 331). | yes |
| 3 | §4.1, "Its conclusions call it *'a survey of available results'* on CFAR losses" | The Conclusions call only one part of the paper a survey: CFAR loss in stationary Gaussian noise. Non-stationarity, where the greatest-of material sits, is "discussed in detail" separately. Saying "call it" (the whole paper) goes further than that. | minor | "Its conclusions describe its treatment of CFAR loss in stationary noise as *'a survey of available results'*". | yes |
| 4 | §4.1, "What we do not know", third bullet | The list of cell-averaging citations leaves out Finn & Johnson 1968 (ref 5), then says "Of its cell-averaging citations, only Finn & Johnson 1968 is on the shelf". The document says only that Finn & Johnson "say nothing about where greatest-of began". It never says they do not describe greatest-of, so dropping them from this open question has no stated basis. | minor | Put Finn & Johnson in the list. Or state that it was read and does not describe greatest-of, if that is what the reading found. | partly (the reference list yes; the content of Finn & Johnson not checked) |
| 5 | Follow-ups todo, Finn lead; shelf README "Also a lead" | "H. M. Finn … (as Hansen cites it …)": Hansen prints "H. H. Finn". The volume warning could also be sharper. If the journal numbers Sept 1968 as vol. 29 on one volume per year, Dec 1967 cannot also be vol. 29. The paper's own evidence already points to a different volume. | minor | Write "H. H. [sic] Finn" or drop "as Hansen cites it" from the author. Add that the vol. 29 / Dec 1967 pairing clashes with the journal's own numbering. | yes (initials); no (actual volume) |
| 6 | `docs/lit_needed.md`, heading of the now-ticked Hansen entry | The heading keeps the notice's form, "Constant-false-alarm-rate processing … Proc. IEE International Radar Conference". The paper's title has no hyphens, and the volume is titled "International Conference on Radar — Present and Future". §4.1 now uses the paper's form, so the two files disagree. | minor | Take the title and volume name from the paper, which is now in hand. | yes |
| 7 | `docs/lit_needed.md` line 130 (same entry, unchanged) | The table row says Rohling "credits greatest-of (CAGO) to Hansen & Sawyers 1980 and Moore & Lawrence 1980". §4.1 says Rohling has Moore et al. "proposed" it and Hansen et al. "investigated" it. The new closing paragraph lists only two earlier readings as superseded, so this looser one still stands in a file being edited. | minor | Name it as superseded too, or align it with §4.1's wording. | yes |
| 8 | §7 item 2 | "All four papers are read" now sits right beside a ⚠ reporting that a fifth paper was read. It is accurate for item 2's own scope, but reads as a contradiction. | minor | "All four papers named here are read". | yes |
| 9 | Run note, not about the artifact | Comparing the branch with origin/main also shows `docs/site/raster_viewer.html`, `docs/site/viewer.template.html` and `tests/test_webapp_annotate.py`. The branch is behind main, and its copy of `docs/SESSIONS.md` lacks the darkroom claim that main has. The patch I reviewed leaves these out, but a reviewer working from the raw diff would see unrelated changes. | minor | Merge origin/main into the branch before the PR. | yes |

## Brief compliance, factual side only

Nothing in the changed text names a replacement origin. The "What we do not know" bullets list the 1972 memo, the 1973 paper and "earlier work" as open possibilities only. Moore & Lawrence 1980 was correctly dropped from that list, since it is later than 1973.

## Relevant files

- Repo (worktree `hansen-1973-read`): `docs/detector_history.md` (§4.1, §7), `docs/lit_needed.md`, `docs/todo/2026-09-14-greatest-of-follow-ups.md`, `docs/learned/detector_history.html`, `docs/SESSIONS.md` on origin/main
- Darkroom: `<darkroom>/bugarach/lit/radar/gregers_hansen_1973_cfar_search_radars.pdf`, `<darkroom>/bugarach/lit/radar/README.md`, `<darkroom>/bugarach/detector_history.html` (stale)
- Decoded page images, in this session's scratchpad: `p1r_imgs/small02.png`–`small08.png` (pp. 325–331) and `p329_bottom.png` / `p330_top.png` (reference list)
