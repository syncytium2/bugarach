GRANT 1 ok — Read, Grep, Glob, Bash

Blind pass. I did not open anything under `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`, and I edited nothing. I pulled the shelf PDFs' text with `pdftotext` in both `-layout` and plain modes, and pulled the patent's text out of the saved Google Patents page with a small script.

## Claim ledger

| # | Quoted claim (location) | Cited source | What the source says | Verdict |
|---|---|---|---|---|
| 1 | The 1973 conference was *Radar — present and future*, London, 23–25 October 1973, IEE Conf. Publ. 105 (detector_history §4) | Proc. IEE contents notice (`iee_conf_105_1973_CONTENTS_ONLY.pdf`) | "IEE CONFERENCE PUBLICATION 105 / Radar--present and future (23rd-25th October 1973, Savoy Place, London, England)" | match |
| 2 | Proc. IEE 120(11), November 1973, p. 1391; ISBN 0 85296 114 6; confirms author and title | same | Page footer reads "PROC.IEE, Vol.120, No. 11, NOVEMBER 1973 1391"; ISBN 0 85296 114 6; "GREGERS HANSEN, V.: Constant-false-alarm-rate processing in search radars" | match |
| 3 | Hansen's IEEE Xplore record lists nothing between 1972 and 1974 | `gregers_hansen_AUTHOR_PROFILE_ieee.pdf` | 19 items. The last 1972 entry is Hansen & Ward; the next is the 1974 multilevel quantization paper; no 1973 entry | match |
| 4 | Earlier CFAR papers with Zottl (1971) and Ward (1972); neither on the shelf | profile; shelf listing | Hansen & Zottl, AES-7(4) 1971; Hansen & Ward, AES-8(5) 1972; neither PDF is in `lit/radar/` | match (but see finding F6) |
| 5 | IEEE Xplore, the IET Digital Library and HathiTrust refused automated searches; OpenAlex and Semantic Scholar hold records without text; no library request recorded | none cited | A handoff (`docs/handoffs/2026-09-10-the-surrogate-is-the-design.md`) records IEEE Xplore answering with HTTP 418 / CAPTCHA. Nothing I was allowed to open covers IET, HathiTrust, OpenAlex, Semantic Scholar, or the absence of a library request | partly supported; rest unverifiable |
| 6 | Hansen & Sawyers cite 1973 for *"a simple rule for determining the detectability loss"*, *"based on a simplified analysis and simulation results of limited accuracy"* | H&S 1980 p.115 | Verbatim; [1] is the 1973 IEE paper | match |
| 7 | Internal Hughes memo by J.H. Sawyers, 15 Feb 1972, title as quoted, is the exact analysis the greatest-of curves were prepared from | H&S 1980 refs and intro | [2] "Detection losses of the 'Conventional' and 'Split' mean level threshold detectors," Internal memo, Hughes Aircraft Co., Feb. 15, 1972. The intro says "exact analysis contained in [2]" and "graphs … were prepared from [2]" | match |
| 8 | Acknowledgment: *"are derived from independent work performed by the two authors"* | H&S 1980 p.118 | Verbatim | match |
| 9 | H&S doi:10.1109/TAES.1980.308885; AES-16(1):115–118 (README) | PDF metadata and page footers | Metadata holds `10.1109/TAES.1980.308885`; footers show pages 115–118, Vol. AES-16 No. 1, January 1980 | match |
| 10 | US 4,318,101: Nippon Electric, filed 1980, granted 1982 | saved Google Patents page | Original assignee Nippon Electric Co Ltd; US filing 1980-03-11; published 1982-03-02; priority JP 1979-03-14 | match |
| 11 | Patent says Hansen *"proposed another CFAR processor for the Weibull clutter in general"*, and gives the report as pages 1–8 | same | "Hansen solely proposed another CFAR processor for the Weibull clutter in general in his report that was made public at International Conference on Radar-Present and Future, 23-25 October 1973. The report of Hansen is paged 1-8". The fragment is exact; "solely" is left out of the quote without harm. The patent never mentions greatest-of or maximum selection | match |
| 12 | Rohling: *"Moore et al. [3] proposed a different estimation method. The CAGO CFAR applies the maximum of two arithmetic means"*; [3] is Moore & Lawrence, 1980 IEEE International Radar Conference | Rohling 1983 p.609 and refs | Verbatim; [3] = Moore, J.D. & Lawrence, N.B. (1980), presented at the IEEE International Radar Conference, Washington, D.C. | match |
| 13 | Rohling: *"Hansen et al. [2] have investigated CAGO CFAR"*, [2] = H&S 1980; Rohling does not cite 1973 | Rohling refs | Verbatim; [2] = H&S 1980. The only 1973 string in Rohling's text is not a Hansen citation | match |
| 14 | Gandhi & Kassam: *"Hansen [9] has proposed … greatest of (GO) the sums in the leading and lagging windows"*, [9] = the 1973 paper | G&K 1988 p.428 and refs | Verbatim. Counting the reference list, the 9th entry is Hansen, V.G. (1973) | match |
| 15 | G&K is the only held source giving pages 325–332, and it names the venue as an IEEE conference | all shelf PDFs and the patent | G&K: "Proceedings of the IEEE 1973 International Radar Conference, London. 1973, pp. 325-332." H&S gives no pages; Rohling and Weinberg do not cite 1973; the patent gives pages 1–8 | match |
| 16 | `maxlt` takes the larger of the trailing and leading background estimates (README, GLOSSARY, table) | `src/bugarach/detectors/loco.py` | `thr_a[ai] = max(tl, tr)`, where `tl`/`tr` are percentile thresholds of the surrogate pool for each half-context; this is the default mode | match (the "CAGO" label is a different matter, F4) |
| 17 | `tools/verify_quotes.py` traces some quotations automatically and is not yet a gate | the tool; `.githooks`, `tests`, `.github` | The docstring says "PROVISIONAL — a reporting aid, not a gate, and deliberately not wired into CI"; grep finds no reference in hooks, tests or CI | match |
| 18 | The four papers marked *read in full* are held, each with a read-status entry; Tony supplied the two IEEE papers on 2026-08-22 | shelf `README.md`; PDF stamps | All four are present with "read in full" entries. H&S and G&K carry an "August 22, 2026" download stamp | match |
| 19 | GLOSSARY: "the four radar primaries were retrieved and read on 2026-08-22" | shelf README, file timestamps | README dated 2026-08-22; Finn & Johnson and Rohling saved 09:13, the IEEE pair 16:18, same day | match |
| 20 | Every radar quotation in the document comes from a shelf PDF except the patent (Sources) | shelf | Every new radar quotation checks out against a shelf PDF or the patent, as rows 6–14 show | match |
| 21 | Sources: the shelf README carries "read status per work and the two outstanding library orders" | shelf README | That README now says both orders were "delivered 2026-08-22". It has no entry for the 1973 paper, the IEE contents PDF or the author-profile PDF | **mismatch** (F5) |
| 22 | Hansen & Sawyers 1980 is on the shelf and read (README drops "shelf holds only Finn & Johnson") | shelf | The old sentence contradicted the old README's own "**is** on this project's shelf". Dropping it is correct | match |
| 23 | detector_history.html is rebuilt from the markdown | the html | Every new passage is present. `~~Hansen 1973~~` shows as literal tildes, because the converter outputs no strikethrough | match in content; rendering defect (F3) |

## Findings

**F1 · major · verifiable: yes.** Location: `docs/proposals/2026-09-10-coordination-without-labels.html`, line 848 (footer).
- **Issue:** The retraction missed a copy. This public file still says: "the constant-false-alarm-rate family from the radar literature (Finn & Johnson 1968; Hansen 1973; Rohling 1983)". That is the same attribution being withdrawn in README, GLOSSARY, detector_history and cfar_scope. The file is not in the diff. A grep of the tree (excluding the blind-pass folders) finds no other live copy.
- **Fix:** Apply the same change in this PR: cite Hansen & Sawyers 1980 for the analysis, or drop Hansen, and link to "Where greatest-of began". If the proposal is a frozen dated artifact, add a dated correction note rather than leaving it silent.

**F2 · major · verifiable: yes.** Location: detector_history §4, "What we do not know", the bullet "who proposed it: Rohling credits Moore & Lawrence, and Gandhi & Kassam credit Hansen".
- **Issue:** The bullet weighs the two credits as equal. The held sources do not support that.
  - Hansen & Sawyers, which Rohling himself cites as [2], place greatest-of analysis in a February 1972 memo ("the 'Split' mean level threshold detector") and in the 1973 paper. Both are years before Moore & Lawrence's 1980 talk.
  - Gandhi & Kassam cite Moore & Lawrence [6] only for showing that "a minor increase can be expected in the false alarm rate of the GO-CFAR processor" during clutter transitions. That is analysis of an existing technique, and the talk's own title is "Comparison of two CFAR methods…".
  - So Rohling's "proposed" cannot mean *first* proposed. The open question is narrower than the bullet says: whether greatest-of started with the 1972 memo, the 1973 paper, or earlier.
- **Why this is not a new origin claim:** Stating this names no origin, so the owner's brief ("do not replace the old origin claim with a new one") still holds. The brief does ask for "what we know", and this is known from the held papers.
- **Fix:** Add one sentence along these lines: "Moore & Lawrence's 1980 talk is later than both the 1972 memo and the 1973 paper that Hansen & Sawyers cite for greatest-of analysis, and Gandhi & Kassam cite it as an analysis, so Rohling's 'proposed' cannot mean first." Keep the bullet as the unknown between the 1972–73 work and anything earlier.

**F3 · minor · verifiable: yes** (the rendering itself is role 10's to check). Location: `docs/learned/detector_history.html`, line 440.
- **Issue:** The strikethrough on the retracted citation does not render. The page shows "GO-CFAR (~~Hansen 1973~~; ⚠ …". A reader of the built page sees the withdrawn citation in plain type with stray tildes. The page contains 4 literal `~~` and no `<del>` or `<s>` tags.
- **Fix:** Have `tools/md_to_page.py` render `~~…~~` as `<del>`, or reword the markdown so the withdrawn citation is named in words rather than by strikethrough.

**F4 · minor · verifiable: yes.** Location: detector_history §4 table, row "LoCo, `maxlt`", CFAR analogue column "greatest-of (CAGO-CFAR)". This text predates the diff but sits in a row the diff changed.
- **Issue:** The label is itself a claim. "CA" in CAGO means cell-averaging, but `loco.py` takes the max of two percentile thresholds of a surrogate pool (`max(tl, tr)`), not two cell means. The paragraph right under the table says so ("its estimator is a percentile … rather than a mean").
- **Fix:** Change the label to "greatest-of (GO) selection", matching GLOSSARY and cfar_scope, or add "combination rule only".

**F5 · minor · verifiable: yes.** Location: detector_history, Sources entry for `<darkroom>/bugarach/lit/radar/README.md`.
- **Issue:** The entry says the shelf README holds "the two outstanding library orders", but that README records both as delivered. It also has no entry for the 1973 paper that is now outstanding, or for the two evidence PDFs the new §4 passage relies on (the IEE contents page and the IEEE author profile). The shelf's own rule is that "a PDF with no entry is indistinguishable from a PDF someone downloaded and forgot."
- **Fix:** Correct the Sources wording. Separately, the shelf README needs entries for the two evidence files and the unread 1973 paper. That is outside this repo, so hand it to the main thread.

**F6 · minor · verifiable: yes.** Location: detector_history §4, last "do not know" bullet ("Hansen's earlier CFAR papers, with Zottl in 1971 and with Ward in 1972").
- **Issue:** The list reads as complete but is selective. The same author record lists other pre-1973 detection papers bearing on constant false alarm: nonparametric rank tests (1970), a generalized sign test with Olsen (1971), and the analog moving-window detector (1970). Distribution-free detectors are a CFAR route.
- **Fix:** Write "including those with Zottl (1971) and Ward (1972)", or list all of them.

**F7 · minor · verifiable: no.** Location: detector_history §4, the sentence beginning "IEEE Xplore, the IET Digital Library and HathiTrust refused automated searches…".
- **Issue:** These are claims about the search, and nothing is cited for them. Only the IEEE Xplore refusal is backed by a record I was allowed to open (the 2026-09-10 handoff). IET, HathiTrust, OpenAlex, Semantic Scholar and "no library request is recorded" cannot be checked by an outside reader.
- **Fix:** Cite where the search log lives (for example, the todo that records it) so each statement has a source.

**F8 · minor · verifiable: yes.** Location: detector_history §4, "Hansen's IEEE Xplore author record lists nothing between 1972 and 1974".
- **Issue:** The statement is true, but a reader may take it as evidence about the paper. IEEE Xplore indexes IEEE publications, and the paragraph itself has just said the volume is an IEE one (the handoff also says Xplore does not index it). An empty 1973 is expected, not informative.
- **Fix:** Add "as expected, since the IEE volume is not an IEEE publication", or cut the sentence.

**F9 · minor · verifiable: yes.** Location: detector_history §7 item 2.
- **Issue:** The item still says "nothing on this item is outstanding", and the new ⚠ line directly under it says an attribution did not survive. The table in §4 now marks the 1973 paper "not read".
- **Fix:** Qualify the sentence, for example "nothing outstanding except the 1973 paper (§4, *Where greatest-of began*)", or strike it and let the ⚠ line stand.

**F10 · minor · verifiable: partly.** Location: GLOSSARY CFAR paragraph ("`rate_detect` is cell-averaging CFAR (Finn & Johnson 1968)") and `cfar_scope.html` VARIANTS (SO → "Trunk 1978", TM → "Weiss 1982; Rickard & Dillard").
- **Issue:** These are citations of the same kind as the one just retracted, and the diff did not recheck them. Trunk, Weiss and Rickard & Dillard are not on the shelf and are cited second-hand through Rohling and G&K. G&K's reference list also has Steenson 1968, "Detection performance of a mean-level threshold", in the same year as Finn & Johnson. No mismatch was found; they are simply unchecked.
- **Fix:** Out of scope for this brief. Record it as a follow-up so the next attribution change does not rediscover the same problem.

**No mismatch found:** every quotation in the changed passages is verbatim in its source (Hansen & Sawyers, Rohling, Gandhi & Kassam, the patent). Bibliographic details, dates, the ISBN, the DOI, the page ranges and the code behaviour were all recomputed from the sources, and all match.

**Files relevant to these findings:**
- `<worktree>\docs\proposals\2026-09-10-coordination-without-labels.html`
- `<worktree>\docs\detector_history.md`
- `<worktree>\docs\learned\detector_history.html`
- `<worktree>\src\bugarach\detectors\loco.py`
- `<darkroom>\bugarach\lit\radar\README.md`
