GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2 findings: where greatest-of CFAR began (blind pass)

I found three major problems and nothing blocking. The biggest one is a wrong-looking identifier: library catalogues give the 1973 volume a different ISBN from the one the text states. The same catalogue search also turned up a scan of the volume held by the [a US university library], which the search narrative doesn't mention. Nothing in the changed text credits a new origin for greatest-of.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verifiable against a source |
|---|---|---|---|---|---|
| 1 | `docs/detector_history.md` §4, *Where greatest-of began*: "gives the volume's ISBN, 0 85296 114 6" (same text in `docs/learned/detector_history.html` line 758) | The notice on the shelf does print 114 6, but only in its OCR text layer. I could not render the page image to confirm it. Two library catalogues disagree with it. The Library of Congress record for *International Conference on Radar—Present and Future, 23–25 October 1973*, IEE Conf. Publ. no. 105, 437 pp. (LCCN 74169985, OCLC 952520, HathiTrust 001618382) gives **0 85296 112 X**, and Open Library agrees. Catalogue records put 0 85296 114 6 on **Conf. Publ. 103**, the York conference on digital computers in measurement (HathiTrust 011456921). A library request using 114 6 could bring back the wrong book. | major | Check the page image. Then write: "the notice prints ISBN 0 85296 114 6; the Library of Congress and HathiTrust catalogues give 0 85296 112 X for this volume and attach 114 6 to Conf. Publ. 103." Do not choose between them silently. | yes |
| 2 | Same passage: "IEEE Xplore, the IET Digital Library and HathiTrust refused automated searches … No library request for the printed volume is recorded." | **(a)** "HathiTrust refused" is only partly true. Its full-text search returned a Cloudflare 403 for me, but its catalogue API answered at once. It shows the volume was scanned from the **[a US university library]'s** copy (`mdp.39015000988512`, search-only). The print copy sits in [the library]'s Buhr storage (C 580398). The shelf's IEEE PDFs were licensed through that same library. In a browser, HathiTrust's search-only mode shows which pages match a term such as "greatest", without anyone needing the full text. **(b)** None of the attempts are dated. **(c)** I could only check "not recorded" against the shelf README and this document. The brief ruled out `docs/todo/` and `docs/lit_needed.md`, and `lit_needed.md` has changes in this worktree. | major | Date the attempts. Say "HathiTrust full-text search refused; its catalogue shows a search-only [the library] scan (001618382) and a [the library] print copy." The main thread should check `lit_needed.md` and the todos before keeping "no library request is recorded". | partly |
| 3 | §7 item 2: "All four primaries are read; nothing on this item is outstanding." followed by "⚠ 2026-09-14: one attribution did not survive." | "Nothing outstanding" now contradicts §4, which leaves the 1973 paper unread. The struck-through "Verify §4's CFAR attributions … Done" also still stands. "Did not survive" can be read as *Hansen 1973 is not the origin*, which is a negative origin claim the brief forbids. | major | Use "the attribution to Hansen 1973 as origin is withdrawn as unverified; the paper is unread and outstanding (§4)". Remove "nothing on this item is outstanding", or limit it to the four papers. | yes |
| 4 | The paragraph after the §4 table: "The one quotation from outside the shelf, from a patent, is marked as such." | The §4 bullet names the patent but never says it is off the shelf. Only the Sources entry says that. The quote also comes from Google Patents' OCR text, not the USPTO page image. The quote is accurate as a substring; the patent reads "Hansen solely proposed another CFAR processor …". | minor | In the bullet, add "(not on the shelf; Google Patents text)". Or check it against the USPTO PDF and say so. | yes |
| 5 | Sources entry for the radar shelf: "with read status per work and the two outstanding library orders" | That clause is stale. The shelf README says those two orders were delivered on 2026-08-22. The two PDFs added 2026-09-10 (`iee_conf_105_1973_CONTENTS_ONLY.pdf` and `gregers_hansen_AUTHOR_PROFILE_ieee.pdf`) have no README entry. §4's evidence for the ISBN, title and publication gap rests on those two files. | minor | Change to "…with read status per work". Tell the main thread that the shelf README needs entries for the two September additions. The darkroom is not a file under review. | yes |
| 6 | §4 passage: "Hansen's IEEE Xplore author record lists nothing between 1972 and 1974" next to "IEEE Xplore … refused automated searches" | Both statements are true: the record lists four 1972 items, then a 1974 one. But read together they suggest Xplore could not be searched, while the shelf holds a manual Xplore capture made with [a US university library] access. | minor | Separate them: "a manual Xplore author-record capture (2026-09-10) is on the shelf; automated queries were refused (date)." | yes |
| 7 | `README.md`, the ° legend: "° marks a work … **not read here**" | Removing the old "shelf holds only Finn & Johnson" clause was right; that clause was already false. But Amarasingham et al. 2012 still carries a °. The surrogates shelf records it as "read in part 2026-09-12 (role 6, pdftotext)". | minor | Change the legend to "not read in full here", or remove the ° from Amarasingham 2012. | yes |
| 8 | Revised-2026-08-24 note: "(~~Hansen 1973~~; ⚠ …) … has stopped being a reading of the design space and become the attribution" | Now that the GO origin is struck, "become the attribution" overstates. The GLOSSARY already softened the same sentence to "the mechanisms are CFAR's". | minor | Use the GLOSSARY wording, or add "(except where greatest-of began, §4)". | yes |
| 9 | §4 bullets: "So the 1973 paper treated greatest-of." and "So the talk covered more than greatest-of." | Both inferences hold. Hansen, the 1973 author, describes the rule in the 1980 paper. The patent describes the Hansen processor as a Weibull processor that uses averages of logs and of squared logs over both sides of the cell. Two small problems: the patent calls it a "report" and paginates it 1–8, so "talk" is loose; and the first inference rests on the author's own later description. | minor | Use "per its author's 1980 description, the 1973 paper treated greatest-of" and "the paper covered more than greatest-of". | yes |
| 10 | README: "This README used to cite ° Hansen V.G. (1973), *Constant-false-alarm-rate processing in search radars*, IEE Conf. Publ. 105" | The old README actually cited the title without hyphens, gave the venue as "Proc. IEE Int. Radar Conf." and gave pp. 325–332. Hyphenating the title is correct, but it misquotes what the README used to say. | minor | Quote the old citation as it was, or say "cited Hansen's 1973 paper (IEE Conf. Publ. 105) as the origin". | yes |

## Checked and correct

**Hansen & Sawyers 1980 (shelf PDF, and Crossref for the DOI):**
- Volume, pages and date are correct: AES-16(1), January 1980, pp. 115–118.
- doi:10.1109/TAES.1980.308885 resolves to this paper.
- All three quotations match the text.
- Reference [1] is Hansen's 1973 paper, IEE Conf. Publ. No. 105, 23–25 October 1973.
- Reference [2], the Sawyers memo, matches: title with 'Conventional' and 'Split', Hughes Aircraft internal memo, 15 February 1972. The paper says its curves "were prepared from [2]", an "exact analysis".
- The acknowledgment quotation matches.

**The Proc. IEE notice:**
- It appears in *Proc. IEE* vol. 120, no. 11, November 1973, p. 1391.
- Author ("GREGERS HANSEN, V."), title and dates match.
- The venue was Savoy Place, London. The Library of Congress record confirms the organiser: the Electronics Division of the IEE, with the Italian electrotechnical association (AEI) and others. "A London conference of the IEE" holds.

**Hansen's Xplore author record:** there is a gap between 1972 and 1974. The Hansen & Zottl 1971 and Hansen & Ward 1972 CFAR papers are listed there. Neither is on the shelf.

**US 4,318,101:**
- Assignee is Nippon Electric.
- Filed 1980-03-11, granted 1982-03-02. It also claims Japanese priority from 1979-03-14; the text leaves that out, which is harmless.
- The quotation and the pagination "1–8" match.

**Rohling 1983:**
- Both quotations match.
- Reference [2] is Hansen & Sawyers 1980.
- Reference [3] is Moore & Lawrence, presented at the IEEE International Radar Conference, Washington DC, 1980.
- None of the paper's 12 references is the 1973 paper.

**Gandhi & Kassam 1988:**
- The quotation matches.
- I counted the reference list: [9] is Hansen 1973, "Proceedings of the IEEE 1973 International Radar Conference, London … pp. 325–332". The "IEEE conference" statement and the page range hold.
- They also write "proposed and analyzed in [9, 10]", which is consistent with "credit Hansen".

**Other checks:**
- OpenAlex has a record with no full text (W2416657781, vol. 105, pp. 325–332, venue wrongly assigned). Semantic Scholar has a record too; my API call was rate-limited, so I only saw it through web search.
- `tools/verify_quotes.py` exists, calls itself provisional, and nothing in `.githooks/` or `.github/workflows/` uses it, so "not yet a gate" holds.
- I matched every quotation in §§3–5 against the shelf text (plus the saved patent page). Every quotation in the new §4 passage matched.
- The `cfar_scope.html` row, the VARIANTS entry and the lede match §4.
- **Nothing in the changed text credits greatest-of to anyone.** "What we do not know" reports Rohling's credit and Gandhi & Kassam's credit side by side without choosing.

## What I searched, and what I did not

- **Searched:** the radar shelf (all six named PDFs plus Finn & Johnson), the saved patent page, the surrogates and coordination shelf READMEs, Crossref, OpenAlex, HathiTrust's catalogue API, Open Library, and web searches for the exact title, the conference and the ISBN. HathiTrust full-text search and the IET Digital Library both returned 403 to me.
- **Not searched (open ⚠ items):**
  - The 1973 paper itself, and the HathiTrust page-level search of the [the library] scan.
  - Hansen's later paper "Clutter suppression in search radars" (1977 IEEE Conference on Decision and Control), which appears on his own author record. §4 does not list it among the unknowns.
  - Textbooks: Nathanson 1969, Skolnik's *Radar Handbook*, Barton.
  - Moore & Lawrence 1980, which is not on the shelf.
- **Not opened:** `docs/todo/`, `docs/reviews/`, `docs/lit_needed.md` (the brief ruled them out).
- **Nobody asked (open ⚠):** the text doesn't say whether anyone wrote to Rohling, Kassam or Hansen. Ask Tony whether any such letter exists. If one does, cite it as a dated personal communication and don't quote it.

Files: `<worktree>\docs\detector_history.md`, `...\README.md`, `...\docs\GLOSSARY.md`, `...\docs\learned\cfar_scope.html`, `...\docs\learned\detector_history.html`. Shelf: `<darkroom>\bugarach\lit\radar\`.

Sources:
- [HathiTrust record 001618382 (Radar—Present and Future, 1973)](https://catalog.hathitrust.org/Record/001618382)
- [HathiTrust record 011456921 (Conf. Publ. 103, the record carrying ISBN 0852961146)](https://catalog.hathitrust.org/Record/011456921)
- [Crossref: 10.1109/TAES.1980.308885](https://api.crossref.org/works/10.1109/TAES.1980.308885)
- [OpenAlex W2416657781](https://openalex.org/W2416657781)
- [Semantic Scholar record](https://www.semanticscholar.org/paper/Constant-false-alarm-rate-processing-in-search-Hansen/b9f381e35d0cc467d022f6661a4b477f0ba78d8f)
- [USPTO image of US 4,318,101](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4318101)
