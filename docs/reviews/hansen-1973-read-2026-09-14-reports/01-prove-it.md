GRANT 1 ok — Read, Grep, Glob, Bash

**Summary.** Almost everything checks out against the sources: the quotations, page and figure numbers, both false-alarm counts, the 20 dB step, the ISBNs, what each paper is cited for, and the Weibull processor. There are two major problems. The shelf does not hold the 1973 paper, although the document says it does. And a count of papers read in full, right next to the changed table, is now wrong. The rest are minor.

**What I checked.** Every changed sentence in the diff, against:
- the 1973 paper's text (both extraction modes);
- the Hansen & Sawyers 1980, Rohling 1983, Gandhi & Kassam 1988 and patent texts;
- the notice in *Proc. IEE* (the institution's journal);
- the HathiTrust record 001618382, fetched live, including its full catalogue entry;
- the lines around the change in the worktree's `docs/detector_history.md`;
- the shelf folder `<darkroom>/bugarach/lit/radar/` and its `README.md`. This folder is the project's own record of what is held and read. The diff does not cite it for this change, so I checked it separately.

I did not open `docs/reviews/` or `docs/todo/`.

## Claim ledger

| # | Quoted value / claim | Cited source | Recomputed / found | Result |
|---|---|---|---|---|
| 1 | Title "Constant false alarm rate processing in search radars" | 1973 paper | Page header reads the same; the *Proc. IEE* notice hyphenates it | match |
| 2 | IEE Conference Publication 105, *Radar — present and future*, London, 23–25 Oct 1973 | volume; HathiTrust | Scan: organised by the IEE, Savoy Place, 23–25 Oct 1973. Catalogue entry: "IEE conference publication; no. 105" | match |
| 3 | pp. 325–332 | volume | Paper starts on p. 325; Fig. 15 is on p. 332. Gandhi & Kassam give 325–332. The patent's "1–8" is also 8 pages | match |
| 4 | Quotation "A technique which can be used … to normalize the output" (p. 326) | 1973 paper | Word for word after stripping punctuation; falls between the p. 326 and p. 327 page markers | match |
| 5 | "using 'greatest-of' selection" … (Fig. 6) | 1973 paper | "such a cell-averaging CFAR using 'greatest-of' selection is shown in Fig. 6"; Fig. 6 is a block diagram | match |
| 6 | 20 dB step; expected false alarms 0.15 → 0.0008 (Fig. 5) | 1973 paper | Text: 20 dB step at range cell 10, 0.15 without greatest-of and 0.0008 with it. The Fig. 5 legend matches. Conditions: 32 reference cells, linear envelope detector, false-alarm probability 10⁻⁵ | match |
| 7 | p. 327 gives a rule for greatest-of's added loss in stationary noise | 1973 paper | p. 327: loss "determined from Fig. 3 if N is taken as the total number of reference noise observations divided by 2" | match |
| 8 | "No reference is attached to any of this" | 1973 paper | p. 326 and the Fig. 5/6 captions carry no citation. The p. 327 text is garbled right after "divided by 2" | match on p. 326; **cannot be verified from the extracted text for p. 327** |
| 9 | Cell-averaging CFAR cited to earlier work, among it Finn & Johnson 1968 and Steenson 1968 | 1973 paper | Fig. 2 is cited "[2-7]"; ref 5 is Finn & Johnson (Sept 1968), ref 6 is Steenson (July 1968) | match |
| 10 | Paper "reviews CFAR processor designs and their losses" | 1973 paper | Conclusions: "A survey of available results indicating the CFAR loss … has been presented" | match |
| 11 | Neither cites a source for greatest-of nor presents it as new | 1973 paper | Wording is "A technique which can be used…". No novelty language in the introduction or conclusions. By contrast, the paper says "proposed" and cites [19] for its own generalized CFAR | match (p. 327 as in row 8) |
| 12 | 1973 paper does not cite the 1972 Sawyers memo | 1973 paper refs 1–21 | Reference list is cleanly extracted; no Sawyers entry | match |
| 13 | Cites Zottl 1971 and Ward 1972 "for other results, not for greatest-of" | 1973 paper | Ref 12 (Hansen & Zottl) is cited for analysis of the Siebert and Dicke-fix detectors. Ref 7 (Hansen & Ward) is cited for cell-averaging, its loss, and log/CFAR loss. Neither is cited for greatest-of | match (list incomplete, see F6) |
| 14 | Paper presents a Weibull CFAR processor in its non-Gaussian noise section | 1973 paper | NON-GAUSSIAN NOISE section: "resulting design of a Weibull CFAR is shown in Fig. 13", before the conclusions | match |
| 15 | Patent: "proposed another CFAR processor for the Weibull clutter in general"; pages 1–8; filed 1980, granted 1982 | patent text | Quotation present; "paged 1-8"; filed 1980-03-11, published 1982-03-02, Nippon Electric | match |
| 16 | *Proc. IEE* 120(11), Nov 1973, p. 1391 confirms author and title | contents notice | "GREGERS HANSEN, V.: Constant-false-alarm-rate processing in search radars"; footer reads PROC. IEE Vol. 120 No. 11 NOVEMBER 1973, 1391 | match |
| 17 | Notice ISBN 0 85296 114 6; volume ISBN 0 85296 112 X | notice; scan p. ii | Notice: 0 85296 114 6. Scan: "0 85296112 X". Catalogue: 9780852961124, the same number as 0852961124. Both check digits are valid | match |
| 18 | HathiTrust search-only scan in record 001618382; loan copy supplied from it | HathiTrust API | Item mdp.39015000988512 is "Limited (search-only)". The loan cover links that same item and says "Generated … through HathiTrust Resource Sharing on 2026-09-14" | match |
| 19 | Read on 2026-09-14 / "read later that day" | loan cover | Loan generated 2026-09-14 19:22 GMT | consistent |
| 20 | Hansen & Sawyers cite the 1973 paper for "a simple rule…" | H&S text | Present; their ref [1] is the 1973 paper | match |
| 21 | Rohling: Moore et al. [3]; Moore & Lawrence at the 1980 IEEE International Radar Conference; "Hansen et al. [2]" is the 1980 paper | Rohling text | All present | match |
| 22 | "seven years before Moore & Lawrence's talk" | 1973 paper; Rohling | 1980 − 1973 = 7 (Oct 1973 to a 1980 conference) | match |
| 23 | Gandhi & Kassam: "Hansen [9] has proposed…", "proposed and analyzed in [9, 10]", pages 325–332 | G&K text | All present; their [9] gives pp. 325–332 | match |
| 24 | "That paper was unobtainable online" | none | A search-only online scan exists, and the loan was generated from it electronically | overstated (F4) |
| 25 | Loan copy is "on the same shelf" | shelf | No 1973 paper PDF on the shelf; no README entry | **mismatch (F1)** |
| 26 | Table row "both read in full" vs. "**Four** of the table's papers are held and read in full" | the document itself | The table now marks five papers read in full | **mismatch (F2)** |
| 27 | IEEE Xplore and the IET Digital Library refused queries; OpenAlex and Semantic Scholar have no text; no correspondence recorded | none supplied | Not in any source I was given | unverifiable |

## Findings

**F1: the shelf does not hold the 1973 paper.**
- **Location:** `docs/detector_history.md`, the paragraph after the §4 table ("from an interlibrary-loan copy on the same shelf"). Also the Sources section, whose unchanged line says "Every radar quotation in this document is from a PDF on that shelf".
- **Issue:** The shelf holds the other radar PDFs plus `iee_conf_105_1973_CONTENTS_ONLY.pdf` and an author-profile PDF. It has no 1973 paper. Its `README.md` has no entry for the paper at all: no read status, no source. So the new p. 326 quotation does not come from a PDF on that shelf, and the paragraph's "each with a read-status entry" does not hold for it. The only extracted text sits in a temporary session folder. The loan cover also limits the copy to "private study, scholarship, or research". Whether a shared shelf is a suitable place for it is for the main thread to decide; the README already labels some files "personal reading copies".
- **Severity:** major.
- **Fix:** File the PDF and a read-status entry on the shelf before shipping, or stop saying it is on the shelf.
- **Verifiable:** yes.

**F2: the "Four papers" count is now wrong.**
- **Location:** `docs/detector_history.md` §4, the unchanged sentence "**Four of the table's papers are held and read in full** — Finn & Johnson, Hansen & Sawyers, Rohling, and Gandhi & Kassam".
- **Issue:** Two lines above it, the changed table row now marks Hansen 1973 "read in full" too. That makes five, and the count contradicts the table.
- **Severity:** major.
- **Fix:** Change it to "Five" and add Hansen 1973, or add a separate sentence for the 1973 paper.
- **Verifiable:** yes.

**F3: the "no reference" claim is not yet checked for p. 327.**
- **Location:** §4.1, "No reference is attached to any of this". The table row's "read in full" depends on the same pages.
- **Issue:** This holds for p. 326 and the Fig. 5/6 captions. On p. 327 the extracted text drops brackets and full stops (for example "Fig 7" with no period). It has a gap right after "divided by 2", exactly where the added-loss rule would carry a citation. One point in the claim's favour: references are numbered by first appearance. [13] appears on p. 326 and [14] first appears on p. 328, so a citation on p. 327 could only point to refs 1–13, and none of those titles is about greatest-of. Still, "no reference" is not proven from the text we have.
- **Severity:** minor.
- **Fix:** Check the p. 327 page image of the loan scan, or limit the sentence to p. 326 and the figures.
- **Verifiable:** partly.

**F4: "unobtainable online" is overstated.**
- **Location:** §4.1, "That paper was unobtainable online."
- **Issue:** HathiTrust holds an online scan (search-only). The loan copy was generated electronically from it through HathiTrust Resource Sharing. IEEE Xplore and the IET library refusing this project's automated queries does not show the paper is absent there.
- **Severity:** minor.
- **Fix:** "This project could not obtain it online; the loan copy came from HathiTrust's search-only scan."
- **Verifiable:** yes.

**F5: "follows" puts the Fig. 5 example in the wrong order.**
- **Location:** §4.1, "A block diagram … follows (Fig. 6), and a computed example across a 20 dB clutter step…".
- **Issue:** In the paper, the example and its 0.15 result for plain cell-averaging come *before* the greatest-of passage. Only the 0.0008 result comes after it.
- **Severity:** minor.
- **Fix:** Reword the order. Optionally add the example's conditions: 32 reference cells, linear envelope detector, false-alarm probability 10⁻⁵.
- **Verifiable:** yes.

**F6: the list of Hansen's earlier papers reads as complete but is not.**
- **Location:** §4.1, last line: "cites Hansen's earlier CFAR papers (with Zottl, 1971; with Ward, 1972)".
- **Issue:** The paper also cites:
  - Hansen 1965 [3], inside the cell-averaging range [2-7];
  - Hansen 1972 [19], *"Generalized constant false alarm rate processing and an application to the Weibull distribution"*, a CFAR paper with CFAR in its title, cited for the Weibull and generalized CFAR;
  - Hansen's nonparametric-detection papers [15], [17] and [18].

  None of them is cited for greatest-of, so the conclusion stands. The list is just not complete.
- **Severity:** minor.
- **Fix:** "cites Hansen's earlier papers, among them …, for other results; none for greatest-of."
- **Verifiable:** yes.

**F7: an open question was closed without evidence.**
- **Location:** §4.1, "What we do not know".
- **Issue:** The old list included "whether Hansen's other papers [Zottl 1971, Ward 1972] bear on it … Neither is on the shelf." The new text replaces that with a fact about how the 1973 paper cites them. How a paper cites something does not show what the cited paper contains, and neither paper has been read. The item was dropped on an inference. Also, "earlier work that neither of them cites" assumes we know what the 1972 memo cites, and the memo is unread.
- **Severity:** minor.
- **Fix:** Keep "whether Hansen's earlier papers (unread) describe greatest-of" as an unknown. Change "that neither of them cites" to "not cited in the 1973 paper".
- **Verifiable:** yes.

**F8: the footer correction gives a reason that does not match the credit.**
- **Location:** `docs/proposals/2026-09-10-coordination-without-labels.html`, footer correction.
- **Issue:** The footer credits Hansen 1973 as a source for "the constant-false-alarm-rate family from the radar literature". It never called the paper the origin of greatest-of. The correction withdraws that credit because the paper does not cite or claim greatest-of, which is an origin argument. The paper, now read, does describe cell-averaging and greatest-of CFAR, which supports the credit as printed.
- **Severity:** minor (for the main thread to decide).
- **Fix:** Either say the withdrawal concerns the audit's claim that the paper is the origin, or keep Hansen 1973 as a family source and correct only the origin implication.
- **Verifiable:** yes.

**F9: a citation error inside Hansen 1973 (no action needed).**
- **Location:** 1973 paper, ref 5.
- **Issue:** Hansen gives Finn & Johnson as *RCA Review* vol. 30, pp. 414–465. The document's table has 29(3), 414–464, from the paper itself, which the document says was read in full. The document is right; Hansen's reference is wrong.
- **Severity:** minor.
- **Fix:** No change. Just don't copy Hansen's version of the citation.
- **Verifiable:** yes.

**Retraction check.** The withdrawal of "Hansen 1973 as the origin" is carried the same way in all five places: the table row, the paragraph after the table, the "Revised 2026-08-24" note, §7 item 2, and GLOSSARY. I checked the replacement claim ("describes it without citing or claiming it") as hard as the original. It holds, apart from F3 on p. 327. No replacement origin is named anywhere, as Tony's brief asked.

**Files referenced:**
- `docs/detector_history.md`, `docs/GLOSSARY.md` and `docs/proposals/2026-09-10-coordination-without-labels.html` in the `hansen-1973-read` worktree
- the shelf: `<darkroom>/bugarach/lit/radar/` and its `README.md`
- the scratchpad `r2txt/` text files and the diff patch named in the task
