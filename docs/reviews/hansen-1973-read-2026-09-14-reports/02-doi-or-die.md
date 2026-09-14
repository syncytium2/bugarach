GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

## Answers to the four questions

1. **"It describes greatest-of selection, but it neither cites a source for it nor presents it as new."** This holds for all the text I could read. The greatest-of passage on p. 326 has no reference, and neither do the captions of Figs. 5, 6 and 7. The only reference in the non-stationary-noise section is [13] (Nathanson & Reilly), and it supports the claim that clutter power varies with range, not greatest-of. The passage calls it "a technique which can be used" and "this technique". The paper calls itself "a survey of available results" (Conclusions). One limit: the OCR is garbled from mid-p. 327 through the Fig. 7 discussion, so a dropped bracket there can't be ruled out from the text alone.
2. **"…seven years before Moore & Lawrence's talk."** The dates are right, but the sentence is an origin argument. Its only job in that bullet is to rebut Rohling's "proposed". Details in row 1.
3. **"The paper itself does not say it is proposing the technique."** Accurate. The paper does use that word elsewhere: on p. 328 it writes "the proposed class of generalized CFAR processors … [19]", citing Hansen's own 1972 abstract. It uses no such wording for greatest-of.
4. **Tracing back through the reference list.** Nothing in the reference list (21 entries) is cited for split windows or greatest-of, in the text or in any figure caption. The cell-averaging CFAR it builds on is cited to [2–7]: Hall 1962–63, Hansen 1965, Finn 1967, Finn & Johnson 1968, Steenson 1968, Hansen & Ward 1972. I stopped there. Of those, only Finn & Johnson is on the shelf and read. For Steenson 1968 and Hansen & Ward 1972 I read only the abstracts, and neither mentions greatest-of, which settles nothing. I did not reach Hall, Hansen 1965 or Finn 1967.

## Findings

| # | location | issue | severity | suggested fix | verifiable |
|---|---|---|---|---|---|
| 1 | detector_history.md §4.1, Rohling bullet: "The 1973 paper describes greatest-of seven years before Moore & Lawrence's talk." | This argues against Rohling's attribution, which the brief rules out. It is also loose: October 1973 to April 1980 is about 6.5 years. And Moore & Lawrence was not just a talk; it is a published proceedings paper, pp. 403–409 (Rohling: "Presented at"). The list is already oldest-first, so readers can see the dates anyway. | major | Delete the sentence. | yes |
| 2 | §4.1 "What we do not know", bullet 1: "or earlier work that neither of them cites" | (a) It claims to know what the 1972 memo cites, but the memo is unread (bullet 2 admits this). (b) It leaves out earlier work the 1973 paper *does* cite for other things ([2–7], [12], [19]), almost none of which is read. That narrows the candidate origins beyond what the evidence supports. | major | "…the 1973 paper, or earlier work." | yes |
| 3 | §4.1 closing line: "The 1973 paper cites Hansen's earlier CFAR papers (with Zottl, 1971; with Ward, 1972) for other results, not for greatest-of." | True as a statement about citations, but it replaces the old unknown ("whether Hansen's other papers bear on it … Neither is on the shelf"). A citation pattern now stands in for content nobody has read. It is also incomplete: the paper also cites Hansen 1965 [3] and Hansen 1972 [19], "Generalized constant false alarm rate processing…". Hansen's 1970 "Performance of the Analog Moving Window Detector" is not cited at all and is unread. | major | Restore it as an unknown: whether the earlier works the paper cites for other results describe greatest-of. None is read except Finn & Johnson. | yes |
| 4 | §4 prose after the table (line 474: "Four of the table's papers are held and read in full"; line 479: "…copy on the same shelf"); Sources (line 1083: "Every radar quotation … from a PDF on that shelf") | (a) The count is now five, going by the table's own "both read in full". (b) Seen from this machine, the 1973 PDF is **not** on `<darkroom>/bugarach/lit/radar/`. The shelf holds 7 files, none of them the 1973 paper, and `README.md` has no read-status entry for it. `lit_needed.md` says both were to be done. Could be Dropbox sync lag, but as it stands the provenance claim can't be checked. | major | Shelve the PDF and add the README entry before merging, or say where the copy is. Fix the count. Outside my role, but worth flagging: the loan notice limits the copy to private study, so check that a shared Dropbox shelf fits that. | yes |
| 5 | `docs/learned/detector_history.html` (tracked) | Still has the pre-read §4.1: "is not among them", "whether Hansen's other papers bear on it", and the old table cell. Anyone opening the page sees the old attribution. | major | Rebuild it in the same change. | yes |
| 6 | §4.1 opening and "What the 1973 paper says"; §4 table "both read in full" | The absence-of-citation claim, and "read in full", rest on OCR that is garbled from mid-p. 327 to p. 332. | minor, open ⚠ | Check pp. 327–328 against the page images and say that was done. If only the OCR was read, "read in full" overstates. | partly |
| 7 | §4.1: "On p. 327 it gives a rule for greatest-of's added loss" | The rule gives greatest-of's *total* CFAR loss, read off Fig. 3 with an adjusted N; the added loss follows by subtraction. Also, the OCR reads "divided by 2", but the worked example (x/N = 0.22 at 32 cells, Pf = 10⁻⁵, where plain cell-averaging gives 0.156) implies N ≈ 22.6 = 32/√2. So the divisor is probably √2, with the radical lost. | minor | "gives a rule for greatest-of's CFAR loss in stationary noise". Check the page image before anyone quotes the rule. | yes (inference) |
| 8 | §4.1: "It reviews CFAR processor designs and their losses" | Next to "nor presents it as new", this nudges readers toward "greatest-of came before this paper", a negative origin by implication. The paper's greatest-of computations (Figs. 5 and 7, the loss rule) are also unreferenced, as if they were its own work. | minor | Use the paper's own words ("a survey of available results", Conclusions), or drop the characterization. | yes |
| 9 | §4 table cell: "described without citation in Hansen, IEE Conf. Publ. 105…" | "Without citation" is ambiguous: it can read as *we* cite it without a citation. Title is missing. `lit_needed.md`'s own ruling is to use the canonical surname "Gregers Hansen". | minor | "described, citing no source, in Gregers Hansen, *Constant false alarm rate processing in search radars*, IEE Conf. Publ. 105, 1973, pp. 325–332" | yes |
| 10 | §4.1, Gandhi & Kassam bullet | The verified venue error was removed. G&K give "Proceedings of the IEEE 1973 International Radar Conference, London". "Matches the volume" now reads as approval of the whole reference. | minor | "Their page range matches the volume; their venue (IEEE) does not." | yes |
| 11 | proposal footer correction | The footer acknowledges lineage "(Finn & Johnson 1968; Hansen 1973; Rohling 1983)" and never said "origin". Withdrawing the credit outright, now that the paper is read and does describe greatest-of, clashes with the §4 table, which cites it. It can also read as "not a source for greatest-of". | minor | "[Correction, 14 September 2026: Hansen 1973 was credited here as where greatest-of selection began. That paper describes it without citing a source or claiming it; where it began is not established.]" | yes |
| 12 | `docs/lit_needed.md` (changed in the worktree but **missing from the supplied diff**; two todo files also differ from origin/main and I did not open them) | Line 130, "Rohling 1983 credits greatest-of (CAGO) to Hansen & Sawyers 1980 and Moore & Lawrence 1980", misstates Rohling: Hansen et al. "investigated", Moore et al. "proposed". Lines 136–137 ("the only [page-range source] found … Hansen's own citation gives no pages") are overtaken by the volume but not marked as such. Line 176 says the PDF is shelved (see row 4). Line 97's "Proc. IEE International Radar Conference" mixes up the journal that carried the notice with the conference volume. | minor | Correct these. Widen the review diff to cover every changed file. | yes |
| 13 | §4.1: "No correspondence about the paper is recorded." | Nobody has asked Gregers Hansen, Sawyers, or anyone who might know. Under my checklist that is an open ⚠, not a clean result. I can't ask Tony, so the main thread should ask whether anyone has written to anyone about this. | minor, open ⚠ | Ask. If nobody was asked, record it as open. | no |
| 14 | §4.1 "What we do not know" (not searched) | Pre-1973 patents are an unsearched field, and it bears on "earlier work". A spot check found US 3,946,382 (Kossiakoff & Austin, assigned to the US Navy). It was filed 27 Oct 1972 as a continuation-in-part of an application filed 28 Jan 1970. Google Patents text: the six-cell average is used "if the six cell average is greater than the twenty cell average". As far as I could read, that compares a short and a long window, not leading and lagging halves. I did not read it in full. **This is not a proposed origin.** It shows only that the question is live in a field nobody has searched. | minor, open ⚠ | Say in the doc that patent literature was not searched. Name no origin. | partly |

## Checked and correct

- **The 1973 quotation:** word-for-word on p. 326. Also correct: "using 'greatest-of' selection", Fig. 6, and 0.15 → 0.0008 across a 20 dB step (Fig. 5).
- **Fig. 2 citations:** [2–7] includes Finn & Johnson and Steenson.
- **Sawyers memo:** absent from the 1973 reference list.
- **Weibull processor:** the paper does present one, in its non-Gaussian-noise section.
- **Volume details:** the volume's ISBN is 0 85296 112 X, and the Proc. IEE notice gives 0 85296 114 6. HathiTrust record 001618382 holds item mdp.39015000988512, which is the item the loan copy came from. Record 011456921, which has ISBN 0 85296 114 6, is Conference Publication 103.
- **Hansen & Sawyers 1980:** both quotations, the memo's details and the acknowledgment match the text.
- **Rohling 1983:** both quotations, ref [3] and ref [2] match the text.
- **Gandhi & Kassam 1988:** both quotations and pp. 325–332 match the text.
- **US 4,318,101:** the supplied `patent.txt` is **0 bytes**, so I checked against Google Patents instead. "Hansen solely proposed another CFAR processor for the Weibull clutter in general" and "is paged 1-8" are both there; NEC, filed 1980-03-11, granted 1982-03-02.

## What I searched, and what I did not

**Searched:**
- the whole 1973 paper (both extractions, reference list, all figure captions)
- Hansen & Sawyers 1980, Rohling 1983 and Gandhi & Kassam 1988 in the extractions; Weinberg 2017 by keyword only (no mention of Hansen, Moore or greatest-of)
- the Proc. IEE notice and Hansen's IEEE author profile, for his later work
- HathiTrust records 001618382 and 011456921
- US 4,318,101
- Moore & Lawrence metadata, via ADS
- abstracts only of Steenson 1968 and Hansen & Ward 1972
- a patent spot check: US 3,995,270, US 3,633,173 and US 3,631,486 (none describes greatest-of); US 3,946,382 (row 14)

**Not searched:**
- Hall 1962–63, Hansen 1965, Finn 1967
- Hansen 1970 (moving-window detector), Hansen 1977 ("Clutter suppression in search radars"), Hansen 1974 (importance sampling)
- the 1972 Sawyers memo; the other papers in Conf. Publ. 105
- Moore & Lawrence's full text
- systematic pre-1973 patent or report literature (DTIC and similar)
- the page images of pp. 327–332
- the humans: nobody asked

Sources:
- [HathiTrust record 001618382](https://catalog.hathitrust.org/Record/001618382)
- [HathiTrust record 011456921](https://catalog.hathitrust.org/Record/011456921)
- [US 4,318,101 (Google Patents)](https://patents.google.com/patent/US4318101A/en)
- [Moore & Lawrence 1980 (ADS)](https://ui.adsabs.harvard.edu/abs/1980inra.conf..403M/abstract)
- [Hansen & Ward 1972 (IEEE Xplore)](https://ieeexplore.ieee.org/document/4103022)
- [Steenson 1968 (IEEE Xplore)](https://ieeexplore.ieee.org/document/5409020/)
- [US 3,995,270](https://patents.google.com/patent/US3995270A/en)
- [US 3,633,173](https://patents.google.com/patent/US3633173A/en)
- [US 3,631,486](https://patents.google.com/patent/US3631486A/en)
- [US 3,946,382](https://patents.google.com/patent/US3946382A/en)
