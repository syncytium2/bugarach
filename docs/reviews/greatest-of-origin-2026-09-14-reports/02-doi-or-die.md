GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2 (citation and reference validator), round 1: how greatest-of CFAR began

**Summary:** Everything the new passage quotes is real and matches the page. The main problems are gaps:
- **F1:** It misreports who Rohling 1983 credits.
- **F2:** It leaves out two shelf facts that bear on the origin question.
- **F3:** It misses a third source that describes what the 1973 paper contained.
- **F4:** It says more about how hard we searched than the record shows.

None of these needs a new origin claim, so Tony's brief still holds.

## Findings

**F1 · detector_history.md §4, the Rohling 1983 bullet · major · verifiable: yes**
- **Issue:** The passage says Rohling "credits greatest-of to the 1980 paper and to Moore & Lawrence 1980". Rohling actually gives a *proposer* and an *investigator*: *"Moore et al. [3] proposed a different estimation method. The CAGO CFAR applies the maximum of two arithmetic means…"* and, separately, *"Hansen et al. [2] have investigated CAGO CFAR"*. His [3] is Moore & Lawrence, IEEE International Radar Conference, 1980.
- **Why it matters:** That is a third, conflicting proposer on our own shelf. Its date also shows it is late: Hansen & Sawyers was received August 1979 and published January 1980, and the Sawyers memo is from 1972.
- **Two smaller problems:** "the 1980 paper" is ambiguous in this bullet, because Moore & Lawrence is also 1980. And the passage's lead phrase "the work usually credited" is not supported by the shelf, where Gandhi & Kassam and Rohling name different proposers.
- **Fix:** "Rohling 1983 says Moore & Lawrence (1980) *proposed* greatest-of, cites Hansen & Sawyers 1980 as having *investigated* it, and does not cite the 1973 paper." Replace "usually credited" with "credited by Gandhi & Kassam 1988".
- Moore & Lawrence exists: OpenAlex W3010182914 and ADS 1980inra.conf..403M. Gandhi & Kassam give pp. 403–409.

**F2 · §4, the two Hansen & Sawyers bullets and the "What we do not know" list · major · verifiable: yes**
The "what we know" section understates what the 1980 paper says, in three ways:
1. **More than one sentence describes the 1973 rule.** The next sentence adds *"This rule is based on a simplified analysis and simulation results of limited accuracy."* The following paragraph says its loss is *"somewhat larger than predicted from an exact analysis contained in [2]"*. So "its author's one-sentence description" is wrong.
2. **The Acknowledgment is left out.** It says the results *"are derived from independent work performed by the two authors"*, who learned of each other's work through David Shanks of Technology Service Corporation. So two people at two companies (Raytheon and Hughes Aircraft) worked on greatest-of independently. That bears directly on "introduced, or analysed a technique already in use".
3. **"Hansen's own 1980 paper" is inaccurate.** The paper is joint, and its exact analysis is Sawyers'.

**Fix:** Say "Hansen & Sawyers 1980". Quote both sentences about [1]. Add the independent-work acknowledgment as a known fact. Also:
- Change "The same paragraph cites an earlier analysis" to "the next paragraph". The memo [2] first appears in §I's second paragraph.
- Give a source for "it was not published": the Conclusions call the results *"previously unpublished"*, and the reference calls the memo an *"Internal memo"*.

**F3 · §4, "no other route produced text" and "what the 1973 paper contains" · major · verifiable: yes (checked verbatim from the Google Patents text)**
- **The source:** US patent 4,318,101, NEC (Nippon Electric), priority 1979-03-14, filed 1980-03-11, granted 1982-03-02. It describes the 1973 report's content:
  - *"Hansen solely proposed another CFAR processor for the Weibull clutter in general in his report that was made public at International Conference on Radar-Present and Future, 23-25 October 1973. The report of Hansen is paged 1-8…"*
  - The processor converts Weibull clutter to *"a new variate z … that follows a simple exponential distribution"*.
  - Its FIG. 2 ("as disclosed in the Hansen report") averages all reference stages except the centre one. No greatest-of step is described.
- **What this changes:**
  - The 1973 talk evidently covered Weibull-clutter CFAR, not only greatest-of.
  - A second pagination ("1-8", probably preprint numbering) sits against Gandhi & Kassam's 325–332.
- **Limit:** A patent's reading of a paper is itself second-hand.
- **Fix:** Add a bullet naming the patent as a dated secondary description of the talk's content (Weibull-clutter CFAR), noting its "1-8" pagination. Keep "that reference list is our only source for 325–332".

**F4 · §4, "IEEE Xplore does not index this IEE volume, and no other route produced text" · major · verifiable: partly**
- **Xplore:** The recorded basis (the closed todo and lit_needed) is only that Hansen's Xplore author profile jumps from 1972 to 1974, plus 418/CAPTCHA refusals. An author profile with nothing listed does not prove the volume isn't indexed.
- **"No other route":** Only two routes are recorded: Xplore and OpenAlex.
- **Routes I tried today:** HathiTrust (403), Open Library (no record), Google Books API (quota error), IET Digital Library search (403). Patents worked (F3).
- **Circular sources:** Web searches now return this repo's own public PR #521 as the source for "Xplore does not index it". That result cannot be cited as independent.
- **Fix:** Say what was actually established: "Xplore's author record for Hansen lists nothing between 1972 and 1974, and Xplore refused direct searches". List the routes tried and the ones not tried.

**F5 · §4 opening, "The volume's contents listing" · minor · verifiable: yes**
- **Issue:** The shelf PDF is not the volume's own contents page. It is a notice printed in *Proc. IEE* **120**(11), November 1973, p. 1391. It also gives "437 pp., 68 papers" and ISBN 0 85296 114 6.
- **Fix:** Cite it as that notice and include the ISBN, which is the key for any library route.

**F6 · §4, Gandhi & Kassam bullet · minor · verifiable: yes**
- **Checked:** The quote matches. [9] really is Hansen 1973 (I counted their reference list: [6] Moore & Lawrence, [7] Weiss, [9] Hansen 1973, [10] Hansen & Sawyers, [13] Rohling). The pages are 325–332.
- **Issue:** Their entry names the venue *"Proceedings of the IEEE 1973 International Radar Conference, London"*, but it was an IEE conference. They also say greatest-of was *"proposed and analyzed in [9, 10]"*. Both weaken our only source for the page range. lit_needed.md records this; the passage doesn't.
- **Fix:** Add a clause: "their entry misnames the venue as IEEE".

**F7 · README.md, LoCo bullet · minor · verifiable: yes**
- **Wording:** "Hansen V.G. (1973) … could not be found" reads as if the paper might not exist. Its existence is confirmed; only a copy is missing. Fix: "no copy could be found; only a published listing of the volume confirms it".
- **Degree mark:** The 1973 citation lost its ° ("not read here") mark, though it is still unread.
- **Stale legend:** The legend above still says "this project's shelf holds only Finn & Johnson", which contradicts "which **is** on this project's shelf" in this same bullet.
- **Vague reference:** "Already analysed the same split detector": same as what? Say "a 1972 internal Hughes Aircraft memo, which the 1980 paper cites as the source of its exact greatest-of analysis".
- **DOI:** Add doi:10.1109/TAES.1980.308885. I checked it on Crossref: the title, AES-16 and pp. 115–118 match.

**F8 · §4, just after the table ("Every radar quotation in this document is matched mechanically against a PDF") · minor · verifiable: yes**
- **Issue:** `tools/verify_quotes.py` reports both new quotes as misses: *"a simple rule for determining…"* and *"Hansen [9] has proposed…"*. I checked both by hand against `pdftotext -layout` and both are genuine; the misses come from a line-end hyphen and quote-mark differences.
- **Why it matters:** The tool calls itself provisional and not a gate, so the sentence overstates what was checked. "All four primaries are now held and read" also sits awkwardly now that the greatest-of row names no primary.
- **Fix:** "checked by hand against `pdftotext -layout`; the matcher is a provisional aid."

**F9 · GLOSSARY.md CFAR paragraph · minor · verifiable: yes**
- **Checked:** The edit is accurate.
- **Wording:** "closed every lineage row" still stands two clauses before "where greatest-of began could not be established". The audit closed that `maxlt` *is* greatest-of, not where greatest-of began.
- **Fix:** Optional: say "identified the family of every lineage row".

**F10 · detector_history.md, the inline ⚠ in the "Revised 2026-08-24" note · no defect · verifiable: yes**
The flag is accurate and dated. As a historical note, keeping "(Hansen 1973 — ⚠ …)" is acceptable.

**F11 · Companion record `docs/reviews/2026-09-10-coordination-without-labels-roles-1-6.md`, table row 4 and F4 · major (for the record, not the artifact) · verifiable: yes**
- **What it claimed:** The earlier role 2 said it "confirmed independently that Hansen 1973 introduces GO selection" and marked "is the origin: yes", with pages 325–332.
- **What it rested on:** It names no source. On that date no held source gave 325–332; the Hansen 1973 todo said so in terms. The 1972 memo that contradicts it had been on the shelf since 2026-08-22, in the paper that row cited.
- **Verdict:** It was an unsupported claim of verification, and it helped drive the wrong direction later closed in `2026-08-25-the-attribution-table-credits-the-wrong-hansen-paper.md`.
- **Fix:** Note in the closed Hansen 1973 todo or the run ledger that the 2026-09-10 claim was unsupported. The review record itself is not to be edited.

## Checks against the brief

- **The 1972 Hughes memo:** The passage's account of it is correct. Author J.H. Sawyers; title *"Detection losses of the 'Conventional' and 'Split' mean level threshold detectors"*; Internal memo, Hughes Aircraft Co., Feb. 15, 1972. It is the 1980 paper's source for GO detection performance ("derived as follows [2]"; graphs "prepared from [2]"). The twenty-month gap before 23 October 1973 is correct.
- **Moore & Lawrence 1980:** The passage gets what Rohling says about it wrong (F1).
- **Hansen & Ward 1972:** AES-8, 648–652, as given in the 1980 reference list.
- **Hansen & Zottl 1971:** Only the IEEE profile supports it (AES-7(4)); its pages are unverified. The passage gives none.

## What I searched, and what I didn't

**Searched:**
- The shelf PDFs, read with `pdftotext -layout`: Hansen & Sawyers §I, the Acknowledgment and the references; the Rohling and Gandhi & Kassam passages and reference lists; the contents notice and the author profile. Weinberg 2017 cites only the 1980 paper.
- Semantic Scholar (CorpusId 63449050: no venue, no abstract).
- OpenAlex.
- Google Patents: US 4,318,101 and US 4,101,889 (Hughes, no mention of Hansen).
- Crossref.
- Tried and blocked: IET Digital Library (403), ADS (CAPTCHA), HathiTrust (403), Google Books (quota), Open Library (nothing).

**Not searched (⚠):**
- **Library holdings for the volume:** IET Archives at Savoy Place, British Library, WorldCat.
- **Books by snippet:** HathiTrust or Google Books full-text search inside the volume.
- **Patents before 1973** on split or greatest-of range gates. My one query returned only later patents. This is the likeliest place for an earlier practitioner origin.
- **The Hughes "mean-level threshold" literature:** Steenson 1968, AES-4:529–534, which shares the memo's term.
- **Forward from the author:** Hansen's 1974–1982 papers and the Radar Handbook chapters. Shrader & Gregers-Hansen wrote the MTI chapter; the automatic-detection/CFAR chapter may carry a greatest-of attribution.

**Not established:** Hansen's affiliation in 1973. Raytheon in 1980 does not settle 1973.

## For the main thread to ask Tony

- Has anyone written to the IET Library/Archives, or asked V. Gregers-Hansen himself? He co-authored the Radar Handbook 3rd-edition MTI chapter (2008).
- Has anyone asked Technology Service Corporation, the firm credited in the 1980 Acknowledgment?

If nobody has, "nobody was asked" is a residual ⚠ and the passage should say so. It is the cheapest route not yet tried.

## Files
- Artifact: <worktree>\docs\detector_history.md, …\docs\GLOSSARY.md, …\README.md
- Companion records: <worktree>\docs\lit_needed.md, …\docs\todo\2026-09-10-nobody-has-read-hansen-1973.md, …\docs\reviews\2026-09-10-coordination-without-labels-roles-1-6.md, …\tools\verify_quotes.py
- Shelf: <darkroom>\bugarach\lit\radar\
- Patent page saved: <scratchpad>\us4318101.html

Sources:
- [US4318101A, Google Patents](https://patents.google.com/patent/US4318101A/en)
- [US4101889A, Google Patents](https://patents.google.com/patent/US4101889A/en)
- [Semantic Scholar record, Hansen 1973](https://www.semanticscholar.org/paper/Constant-false-alarm-rate-processing-in-search-Hansen/b9f381e35d0cc467d022f6661a4b477f0ba78d8f)
- [ADS record, Moore & Lawrence 1980](https://ui.adsabs.harvard.edu/abs/1980inra.conf..403M/abstract)
- [Crossref, doi:10.1109/TAES.1980.308885](https://api.crossref.org/works/10.1109/TAES.1980.308885)
- [Radar Handbook ch. 15, Shrader & Gregers-Hansen](https://helitavia.com/skolnik/Skolnik_chapter_15.pdf)
- [bugarach PR #521 (circular search hit, not a source)](https://github.com/syncytium2/bugarach/pull/521)
