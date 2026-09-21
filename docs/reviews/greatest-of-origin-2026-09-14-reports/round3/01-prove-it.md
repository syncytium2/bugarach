GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): claim check of the greatest-of origin change, blind pass

**Verdict:** every quotation and number in the new text matches its source, but two sentences get the record of the original error wrong. The shelf papers, patent and catalogue records support §4.1's quotations and bibliographic details. The two problem sentences are the ⚠ in the "Revised 2026-08-24" note and the ⚠ in §7 item 2. Both describe how the Hansen 1973 credit got in, and both describe it wrongly. Two major findings and seven minor ones; nothing blocking.

## Claim ledger

| # | Location | Quoted claim | Source checked | What the source says | Result |
|---|---|---|---|---|---|
| 1 | §4.1 ¶1 | The IEE notice lists the author as "GREGERS HANSEN, V." with title "Constant-false-alarm-rate processing in search radars" | `iee_conf_105_1973_CONTENTS_ONLY.pdf` | Same author and title (the title is hyphenated across a line) | match |
| 2 | §4.1 ¶1 | Other authors cite him as V.G. Hansen | Hansen & Sawyers 1980 refs [1], [3], [4]; Gandhi & Kassam ref [9] | "V.G. Hansen" | match |
| 3 | §4.1 ¶1 | *Radar — present and future*, IEE Conference Publication 105, London, 23–25 October 1973 | Proc. IEE notice; HathiTrust record 001618382 (series field: no. 105, venue London) | same | match |
| 4 | §4.1 ¶2 | Notice appears in *Proc. IEE* 120(11), November 1973, p. 1391 | notice footer | "PROC.IEE, Vol.120, No. 11, NOVEMBER 1973 1391" | match |
| 5 | §4.1 ¶2 | The notice gives ISBN 0 85296 114 6 | notice | same | match |
| 6 | §4.1 ¶2 | HathiTrust record 001618382 gives 0 85296 112 X | catalogue API | ISBN field 085296112X | match (both check digits valid) |
| 7 | §4.1 ¶2 | HathiTrust holds "a search-only scan of a US university library's copy" | API items | [a US university library] item, "Limited (search-only)". Record 011456921 also has a search-only Illinois item labelled "no.103-105(1973)" | match, but incomplete (F4) |
| 8 | §4.1 ¶2 | OpenAlex holds a catalogue record without text | OpenAlex API, queried just now | W2416657781: no full text, no DOI. It does list pages 325–332 | match (the page listing matters for F5) |
| 9 | §4.1 ¶2 | IEEE Xplore and the IET Digital Library could not be queried; no library request recorded | none I can open; HathiTrust search-inside returned HTTP 403 to me | — | unverifiable |
| 10 | §4.1, H&S bullet | "a simple rule for determining the detectability loss" and "based on a simplified analysis and simulation results of limited accuracy", both cited to [1] = the 1973 paper | `hansen_sawyers_1980_go_cfar_loss.pdf` p. 115 | verbatim; [1] is IEE Conf. Publ. 105, Oct. 23–25, 1973 | match |
| 11 | §4.1, H&S bullet | Sawyers memo, Hughes Aircraft, 15 Feb 1972, "Detection losses of the 'Conventional' and 'Split' mean level threshold detectors", is the exact analysis the curves are prepared from | H&S p. 115, ref [2] | "exact analysis contained in [2]"; curves "were prepared from [2]"; dated Feb. 15, 1972 | match |
| 12 | §4.1, H&S bullet | Acknowledgment: results "are derived from independent work performed by the two authors" | H&S p. 118 | verbatim | match |
| 13 | §4.1, patent bullet | Nippon Electric; filed 1980; granted 1982 | patent text | filed 1980-03-11 (Japanese priority 1979-03-14); granted 1982-03-02; assignee Nippon Electric Co. | match |
| 14 | §4.1, patent bullet | Hansen "proposed another CFAR processor for the Weibull clutter in general", "another" meaning besides Goldstein's 1973 processor; pages 1–8 | patent text | "Hansen solely proposed another CFAR processor for the Weibull clutter in general…", right after Goldstein AES-9(1) 1973; "paged 1-8" | match (the fragment starts after "solely", which is acceptable) |
| 15 | §4.1, patent bullet | The processor "as disclosed in the Hansen report" averages reference cells on both sides; the patent never mentions greatest-of | patent text | shift register stages −H…H; the average is taken over every stage except the centre. No match for greatest, greater, larger or maximum | match |
| 16 | §4.1, Rohling bullet | "Moore et al. [3] proposed a different estimation method. The CAGO CFAR applies the maximum of two arithmetic means" | `rohling_1983_os_cfar.pdf` | verbatim; [3] is Moore & Lawrence, IEEE International Radar Conference, Washington DC, 1980 | match |
| 17 | §4.1, Rohling bullet | "Hansen et al. [2] have investigated CAGO CFAR"; Rohling does not cite the 1973 paper | Rohling text and reference list | verbatim; [2] is H&S 1980; no 1973 Hansen entry | match |
| 18 | §4.1, G&K bullet | "Hansen [9] has proposed … leading and lagging windows", with [9] the 1973 paper | `gandhi_kassam_1988_cfar_nonhomogeneous.pdf` | verbatim; counting the reference list puts the 1973 paper at [9], H&S 1980 at [10] and Moore & Lawrence at [6], which matches the in-text numbers | match |
| 19 | §4.1, G&K bullet | "proposed and analyzed in [9, 10]"; pages 325–332; venue named as an IEEE conference | G&K | "proposed and analyzed in [9, 10]"; "Proceedings of the IEEE 1973 International Radar Conference, London, pp. 325-332" | match |
| 20 | §4.1, not known | Hansen & Zottl, *IEEE T-AES* AES-7(4), 1971; Hansen & Ward, AES-8(5), 1972, 648–652; both have CFAR in the title | `gregers_hansen_AUTHOR_PROFILE_ieee.pdf`; H&S ref [4]; patent | Zottl: "…Siebert and Dicke-Fix CFAR Radar Detectors", AES-7 issue 4, 1971. Ward: "…Cell Averaging LOG/CFAR Receiver", AES-8 issue 5, Sept 1972, pp. 648–652 | match |
| 21 | §4.1 ¶1 | "The sources we do hold describe work on greatest-of from 1972 onward" | all shelf texts; Finn & Johnson 1968 checked for a split window or maximum rule | Finn & Johnson analyse edge effects but have no greatest-of rule; the earliest dated item is the 1972 memo | match |
| 22 | §4 table and paragraph after it | Four papers held and read in full: Finn & Johnson, H&S, Rohling, G&K | shelf `README.md` | all four marked read in full | match |
| 23 | Paragraph after table | Tony supplied H&S and G&K on 2026-08-22, closing item 2 of §7 | shelf README; H&S download stamp (Aug 22, 2026); §7 item 2 text | consistent | match |
| 24 | Paragraph after table | `tools/verify_quotes.py` traces some quotations and blocks nothing | the tool, run just now | reports 15 of 64 quotations traced; its docstring says it is not wired into CI; nothing in the repo invokes it | match |
| 25 | Sources entry | The two library orders listed on the shelf README were delivered the same day; every radar quotation is from a shelf PDF except the patent's | shelf README; I hand-checked the §4.1 quotations the tool missed | consistent; every §4.1 quotation is genuine | match |
| 26 | README | H&S 1980, AES-16(1):115–118, doi:10.1109/TAES.1980.308885 | Crossref | 308885 is H&S, pp. 115–118 (308887 would be a Nitzberg paper) | match |
| 27 | README | `maxlt` takes the larger of a trailing and a leading half-window threshold | `src/bugarach/detectors/loco.py` lines 506–518 | `thr_a[ai] = max(tl, tr)`; `maxlt` is the default | match |
| 28 | README | Greatest-of's added loss over plain cell-averaging is computed in H&S | H&S p. 116 | loss "relative to the basic cell-averaging CFAR" | match |
| 29 | ⚠ in the "Revised 2026-08-24" note | "For greatest-of the audit identified the mechanism, not where it began" | interface2 commit 9d9710a4 (the audit) | "maxlt IS GO-CFAR (Hansen 1973)"; its code comment says "[introduces GO-CFAR]". interface2 commit 3b8b0683: "Hansen 1973 introduces the rule" | **mismatch** (F1) |
| 30 | ⚠ in §7 item 2 | The 2026-08-22 check "read the 1980 loss analysis, not the 1973 paper the greatest-of attribution named, and could not tell the two apart" | `git log -S` on detector_history.md | The check (commits 9a3da1c, 1a51bd3, 2026-08-22) verified an attribution to H&S 1980, and that is the paper it read. "Hansen 1973" first entered in 8ec8d92, 2026-08-24 | **mismatch** (F2) |
| 31 | README ° legend | ° marks a work carried from the audit and "not read here" | `<darkroom>/bugarach/lit/surrogates/README.md` | Amarasingham et al. 2012 is on the shelf, marked "read in part 2026-09-12", yet README still gives it a ° | **mismatch** (F3) |
| 32 | GLOSSARY | An interface2 audit on 2026-08-24 | interface2 commit 9d9710a4 | authored 2026-08-21; bugarach's reply is dated 2026-08-24 | date refers to receipt, not the audit (F8) |
| 33 | `detector_history.html` | Rebuilt from the markdown | reran `tools/md_to_page.py` into scratch and diffed | identical | match |

**Other sources checked:**
- **Weinberg 2017** is on the shelf and cites H&S 1980 only in a general group of references. It says nothing about who originated greatest-of, so leaving it out of §4.1 loses nothing.
- **The rest of the tree** still names Hansen 1973 in only three places:
  - the proposal footer, which now carries the correction;
  - `docs/forks.md`, which mentions H&S only;
  - a dated handoff record.
- **Source of record:** this deliverable has no experimental units. The equivalent record is the shelf's read-status README, which I located and checked (F6).

## Findings

**F1: major.**
- **Where:** `docs/detector_history.md`, the ⚠ sentence in the "Revised 2026-08-24" note.
- **Issue:** "For greatest-of the audit identified the mechanism, not where it began" is false about the audit. The audit did name an origin: Hansen 1973, labelled "introduces GO-CFAR". That origin claim is exactly what is now being withdrawn. As written, the correction makes the original error look smaller than it was, which cuts against Tony's brief to describe the attempt as it happened.
- **Fix:** "The audit named Hansen 1973 as greatest-of's origin; nobody here or there had read that paper, and the credit is withdrawn as unverified (§4.1)."
- **Verifiable:** yes (interface2 commits 9d9710a4 and 3b8b0683).

**F2: major.**
- **Where:** `docs/detector_history.md` §7 item 2, the ⚠ sentence.
- **Issue:** the chronology is wrong. On 2026-08-22 the attribution under check *was* H&S 1980, and the check read that paper. The 1973 credit arrived two days later, on 2026-08-24, from the audit. The check's real gap was that it confirmed a citation without asking whether the paper was the origin. "Could not tell the two apart" also asserts something no source records.
- **Fix:** "This check verified the attribution as it then stood, Hansen & Sawyers 1980, which it read, but did not ask whether that paper was greatest-of's origin. The 2026-08-24 audit replaced it with Hansen 1973, which nobody read; that credit is withdrawn (§4.1)."
- **Verifiable:** yes (`git log -S "Hansen 1973"` and `-S "(CAGO-CFAR) | Hansen & Sawyers"`).

**F3: minor.**
- **Where:** README "Licensing & citations", the ° legend, which this diff rewrote.
- **Issue:** without its old qualifier, the legend still makes a false claim about one entry. Amarasingham et al. 2012 is on the surrogates shelf, marked read in part, but still carries "° … not read here". Separately, Cossart, Aronov & Yuste 2003 came from the audit and has no °, but no shelf entry for it turned up. Whether it was read here cannot be confirmed.
- **Fix:** remove the ° from Amarasingham 2012, and either shelve Cossart 2003 or mark it °.
- **Verifiable:** yes for Amarasingham; no for Cossart 2003.

**F4: minor.**
- **Where:** §4.1, the search paragraph.
- **Issue:** the paragraph leaves out two facts the catalogue already shows:
  - Record 011456921 is IEE Conference Publication **no. 103** (Digital Computers in Measurement, York, Sept 1973), and it carries ISBN 0 85296 114 6. That is the ISBN the Proc. IEE notice prints for no. 105, so the conflict has a likely explanation (a misprint in the notice or a cataloguing error) that goes unstated.
  - That record's Illinois search-only item is labelled "no.103-105(1973)", which suggests a second scan that may contain no. 105. The text says only "a search-only scan".
- **Fix:** add one sentence on each. Whether the Illinois volume really contains no. 105 remains unknown, and the text should say so.
- **Verifiable:** yes (HathiTrust API); what the Illinois volume contains is not.

**F5: minor.**
- **Where:** §4.1, G&K bullet.
- **Issue:** calling Gandhi & Kassam's reference list "our only source for the 1973 paper's pages, 325–332 (the patent gives 1–8)" contradicts itself. The patent is also a page source. OpenAlex, which the paragraph says was consulted, also lists 325–332, though probably taken from later citations rather than independently. Both ranges are 8 pages long, which is worth saying.
- **Fix:** "the only source we hold that gives 325–332 (OpenAlex repeats it); the patent gives 1–8, the same length."
- **Verifiable:** yes.

**F6: minor.**
- **Where:** §4.1 evidence; §7 item 2 ("a read-status entry per work"); the Sources entry ("read status per work").
- **Issue:** two PDFs that §4.1 relies on have no entry in the radar shelf README: `iee_conf_105_1973_CONTENTS_ONLY.pdf` and `gregers_hansen_AUTHOR_PROFILE_ieee.pdf`. Neither appears in Sources. The shelf README's own rule says a PDF with no entry cannot be told apart from one downloaded and forgotten, and its header still says two works are "not read".
- **Fix:** name both files in Sources. Filing entries on the shelf README is a separate action for the main thread.
- **Verifiable:** yes.

**F7: minor.**
- **Where:** §4 table, `maxlt` row; §7 item 2.
- **Issue:** the status cell "read in full" now sits next to "origin **not established**", so it reads as if the origin was read in full. §7 still says "All four primaries are read" right before the ⚠. That is the old framing, since H&S is no longer a primary source for greatest-of.
- **Fix:** tie the status to H&S explicitly, e.g. "H&S read in full; origin paper not read". In §7, "all four papers are read".
- **Verifiable:** yes.

**F8: minor.**
- **Where:** `docs/GLOSSARY.md`, CFAR paragraph (rewritten in this diff).
- **Issue:** *an interface2 audit on 2026-08-24*. The audit commit is dated 2026-08-21; 2026-08-24 is when bugarach replied to it.
- **Fix:** "an interface2 audit (received 2026-08-24)".
- **Verifiable:** yes.

**F9: minor.**
- **Where:** §4.1 search paragraph, "IEEE Xplore and the IET Digital Library could not be queried".
- **Issue:** nothing I was allowed to open records this. A dated handoff, `docs/handoffs/2026-09-10-the-surrogate-is-the-design.md`, reports HTTP 418 or a CAPTCHA from IEEE Xplore, which partly supports it. Nothing covers the IET library.
- **Fix:** cite the handoff, or record the IET attempt.
- **Verifiable:** no.

I opened nothing under `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`. My scratch text extractions and the rebuilt page are in the session scratchpad only.
