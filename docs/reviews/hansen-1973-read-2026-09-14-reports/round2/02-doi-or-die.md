GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**Role 2, citation and reference check: findings on the hansen-1973-read change (r2 patch)**

**Scope.** I reviewed the r2 patch you named. The worktree kept changing while I worked: `git diff origin/main` now differs from r2 in GLOSSARY, detector_history §4 and §4.1, §7 item 2, lit_needed, the proposal footer and the follow-ups todo. Findings on the current text are marked **[live]**. I edited nothing. I did not open `docs/reviews/`. To see the scan's page images I installed pypdfium2 into the scratchpad only (`r2role2/`).

## Findings

| # | Location | Issue | Severity | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 1 | **[live]** `todo/2026-09-14-greatest-of-follow-ups.md`, the Finn 1967 bullet | The new text guesses "the year, not the volume, is likely wrong, and this may be a December 1968 paper". That is false. The RCA Review December 1967 issue (Volume XXVIII, No. 4) lists "Adaptive Detection with Regulated Error Probabilities … 653, H. M. FINN" on its contents page, and the next article starts on p. 679. So the year Hansen printed is right. His volume (29 for 28), his end page (676) and his initial ("H. H.") are wrong. Guessing metadata like this is not allowed. | **blocking** | Replace with: H. M. Finn, RCA Review **28**(4), Dec. 1967, pp. 653–678 (checked against the issue, worldradiohistory.com scan). Hansen misprints the volume as 29, the end page as 676 and the initial as "H. H." The r2 wording ("volume number is unverified") can now be resolved the same way. | yes |
| 2 | detector_history §4.1, "What we do not know", 3rd bullet | **Narrows.** "That covers its citations for cell-averaging … and Hansen's papers with Zottl … and on generalized CFAR" names a subset and reads as if it were the whole list. Left out are pre-1973 works the paper cites: [13] Nathanson & Reilly 1968, cited in the same Non-stationary Noise section, one paragraph before the greatest-of passage; [11] Carpentier, *Radars: New Concepts*, 1968; [1] Croney 1956; [8] Mitchell & Walker 1971; [9] Siebert 1958; [10] Bello & Higgins 1961; [14] Trunk & George 1970; [16] Dillard & Antoniak 1970. The bullet on main covered "Hansen's other papers". The new one drops his uncited pre-1973 papers, e.g. "Performance of the Analog Moving Window Detector", AES-6(2), 1970 (from the IEEE author record on the shelf). | major | Say "any of the paper's 21 references, or Hansen's other pre-1973 papers", then give examples. At minimum add [13] and [11]. | yes |
| 3 | §4.1, "What we do not know", last bullet | **Unsearched fields are left out.** Only "patent and technical-report literature" is named. Nobody searched pre-1973 radar textbooks and handbooks (the 1973 paper itself cites one, Carpentier 1968), non-English radar literature, or pre-1973 conference proceedings other than this volume. Each of these is an open question, not evidence that there is no earlier work. | major | Name those fields as not searched. | yes (by inspection) |
| 4 | §4.1, "What we do not know", 1st bullet (r2 and [live]) | "…or earlier work" rules out work by others in the same period (1972–73) that is not earlier. Dropping Moore & Lawrence 1980 is justified, since the 1973 paper predates it. | minor | "…or other work". | yes |
| 5 | §4.1, "What the 1973 paper says", first two sentences | "Its conclusions call it 'a survey of available results' on CFAR losses. Alongside that survey…" The full clause is "A survey of available results indicating the CFAR loss … against stationary Gaussian noise has been presented" (p. 329). The √2 loss rule on p. 327 is itself a stationary-Gaussian loss result, so it falls inside that survey, not beside it. | minor | Quote the clause to "stationary Gaussian noise" and drop "Alongside". | yes |
| 6 | §4.1, Fig. 6 bullet | The quote *"using 'greatest-of' selection"* comes from the p. 326 body text. The Fig. 6 caption actually reads "Conventional cell averaging CFAR processor with 'Greatest-Of' selection". | minor | Quote the caption, or give the quote as p. 326 text. | yes |
| 7 | §4.1, Gandhi & Kassam bullet, and "The IEE is … not the IEEE" | The volume's title page says the conference was organised by the IEE "in association with the … Institute of Electrical and Electronics Engineers (United Kingdom and Republic of Ireland Section)" and four other bodies. Calling it an IEEE conference names the wrong publisher, but it has some basis. | minor | "published by the IEE; the IEEE's UK and Ireland Section was one of five associated bodies". | yes |
| 8 | Proposal footer (r2) | The original footer listed Hansen 1973 as lineage for "the constant-false-alarm-rate family", next to Finn & Johnson and Rohling. It never said "origin". The r2 correction quietly reverses the earlier "withdrawn as unverified" without saying so, and "a source for greatest-of CFAR" can be read as "the source". **[live]** fixes both: it quotes the first version and says the paper "stays cited above as a source that describes greatest-of CFAR". | minor (resolved in live) | Keep the live wording. | yes |
| 9 | **[live]** §4.1, first paragraph | Two new sentences. (a) "It is the earliest *published* description of greatest-of this project has found." This is true as limited, but ranking by priority comes close to what Tony's brief forbids. (b) "An unpublished Hughes Aircraft memo from February 1972 is earlier." Hansen & Sawyers only say their greatest-of loss curves were "prepared from" an "exact analysis contained in" the memo. They do not quote the memo describing the technique. | major (a question about the brief) | Ask Tony whether (a) is allowed. For (b), attribute it: "which, per Hansen & Sawyers, contains an exact loss analysis of greatest-of". | yes |
| 10 | **[live]** lit_needed, "presents computations of its own" | The paper says "Numerical computations have shown" and "it was found", and never says whose computations they were. The r2 wording, "reports computed results without attributing them", matched the text. | minor | Go back to the r2 wording. | yes |
| 11 | lit_needed entry heading (unchanged in this diff) | The title is still the hyphenated form from the Proc. IEE notice, with the venue "Proc. IEE International Radar Conference". The paper prints "Constant False Alarm Rate Processing in Search Radars", and the volume is IEE Conf. Publ. 105, not Proc. IEE. | minor | Follow the paper now that we hold it. | yes |
| 12 | lit_needed, table row "Rohling 1983" (in the changed file, text unchanged) | "credits greatest-of (CAGO) to Hansen & Sawyers 1980 and Moore & Lawrence 1980" overstates. Rohling says Moore et al. "proposed" it and Hansen et al. "have investigated" it. §4.1 has this right. | minor | Match §4.1. | yes |
| 13 | Outside the diff: `todo/2026-08-25-the-attribution-table-credits-the-wrong-hansen-paper.md` | The file has a closure banner, but its body still says "The origin is V. G. Hansen, 'Constant False Alarm…'" (line 23) and "Hansen 1973 is not on the shelf" (line 48). The 2026-09-10 handoff still says "One paper outstanding". | minor | Add a one-line "superseded by §4.1" note, or leave them and record it. | yes |
| 14 | Outside the diff: proposal footer and detector_history table, Finn & Johnson 1968 for cell-averaging | Same shape as the greatest-of problem. The 1973 paper cites cell-averaging to [2–7], which includes Hall 1962–63, Hansen 1965 and Finn 1967, all earlier than Finn & Johnson. The live todo notes that the priority question was closed on 2026-08-24. | minor (open question, ⚠) | Note it; no change within this scope. | yes |
| 15 | Correspondence | No record of anyone contacting the IET archives, V. Gregers Hansen, or David Shanks / Technology Service Corporation. Hansen & Sawyers thank Shanks by name for telling each author of the other's work. **"Nobody was asked" is an open question, not a clean result.** | minor (open question, ⚠) | Ask Tony the question already in the follow-ups todo, and record the answer with its date. | no (only Tony knows) |

## Checked against sources and correct (r2)
- **The p. 326 quote.** It matches the page image word for word.
- **Fig. 5.** N = 32, linear envelope detection, Pf = 10⁻⁵, a 20 dB step at cell 10, N_FA = 0.15 and 0.0008. All match.
- **The √2 rule on p. 327.**
  - The OCR drops the radical, but the page image shows "divided by √2".
  - The worked numbers agree: x/N = 0.156 for plain cell-averaging and 0.22 for greatest-of, since 5/(32/√2) = 0.221.
- **"None of these passages or figure captions carries a reference."**
  - I checked this on the page images of pp. 326–327 and the Fig. 5–7 captions on p. 331.
  - Cell-averaging is cited to [2–7].
  - None of the 21 references is the Sawyers memo.
- **Hansen & Sawyers 1980.**
  - All three quotes match.
  - Reference [2] is the 15 Feb 1972 Hughes memo.
  - The acknowledgment's "third party" is David Shanks of TSC, so the r2 paraphrase is accurate.
  - Hansen was at Raytheon, Wayland; Sawyers at Hughes Aircraft, Fullerton. That is two companies, not one lab.
- **US 4,318,101.**
  - The details check out: NEC, filed 11 Mar 1980, granted 2 Mar 1982.
  - The quote is a substring that leaves out the preceding "solely", which is harmless. The pages are given as "paged 1-8".
  - "greatest" and "maximum of" do not appear anywhere in the patent.
  - The 1973 paper does cite the generalized CFAR structure to [19], Hansen's 1972 ISIT abstract.
- **Rohling and Gandhi & Kassam.**
  - All quotes match.
  - In Gandhi & Kassam, [9] is the 1973 paper and [10] is the 1980 paper, with pp. 325–332 and "Proceedings of the IEEE 1973 International Radar Conference".
- **Proc. IEE notice.** 120(11), Nov. 1973, p. 1391, with ISBN 0 85296 114 6.
- **The volume.** The copyright page prints "ISBN: 0 85296112 X".
- **HathiTrust record 001618382.**
  - Its only item is mdp.39015000988512, the same handle printed on the loan cover sheet.
  - OCLC 952520, IEE Conf. Publ. no. 105.
- **HathiTrust record 011456921.** It is Conf. Publ. 103 (ISBN-13 978-0-85296-114-8, bound as no. 103–105), so "the notice's 114 6 was the error" holds.
- **The loan copy.** The cover sheet shows the [a US university library] interlibrary loan, generated 2026-09-14 19:22 GMT. The scan has all of pp. 325–332.

## What I searched, and what I did not
- **Searched:**
  - The 1973 scan: page images of pp. 325–327 and 329–331 plus the whole OCR text.
  - Shelf texts for Hansen & Sawyers, Rohling and Gandhi & Kassam.
  - Weinberg 2017 and Finn & Johnson 1968, by keyword only.
  - The Proc. IEE notice and Hansen's IEEE author record.
  - The Google Patents text of US 4,318,101.
  - The HathiTrust catalogue API (two records).
  - The RCA Review December 1967 issue.
    - A keyword skim of Finn 1967 finds it uses the *maximum of per-cell clutter-level estimates* to decide how many second-step transmissions to send (pp. 660–662).
    - Its threshold is proportional to the variance estimate of the cell under test.
    - In that skim I saw no leading/lagging greatest-of normalisation, but I did not read it in full.
- **Not searched:**
  - Hall 1962–63, Hansen 1965, Steenson 1968, Hansen & Ward 1972, Hansen & Zottl 1971, Nathanson & Reilly 1968, Carpentier 1968, and Hansen's 1972 ISIT abstract.
  - Moore & Lawrence 1980, and the Sawyers memo, which is unobtainable.
  - Pre-1973 patents, DTIC technical reports, radar textbooks and handbooks, and non-English literature.
  - Hansen's later work after 1980.

Sources:
- [HathiTrust record 001618382 (API)](https://catalog.hathitrust.org/api/volumes/full/recordnumber/001618382.json)
- [HathiTrust record 011456921 (API)](https://catalog.hathitrust.org/api/volumes/full/recordnumber/011456921.json)
- [US 4,318,101, Google Patents](https://patents.google.com/patent/US4318101A/en)
- [RCA Review, December 1967 (worldradiohistory.com)](https://worldradiohistory.com/ARCHIVE-RCA/RCA-Review/RCA-Review-1967-12.pdf)

Files: `<darkroom>/bugarach/lit/radar/gregers_hansen_1973_cfar_search_radars.pdf`, `<darkroom>/bugarach/lit/radar/README.md`, and in the worktree `docs/detector_history.md`, `docs/lit_needed.md`, `docs/todo/2026-09-14-greatest-of-follow-ups.md`, `docs/proposals/2026-09-10-coordination-without-labels.html`. The page images, the RCA Review text and the live-vs-r2 diff are in the scratchpad under `r2role2/`.
