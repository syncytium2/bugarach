GRANT 5 ok — Read, Grep, Glob

# Role 5, line editor: round 1 findings on the greatest-of origin passages

The passages are accurate and they follow the brief: none of them replaces the old origin with a new one. The weak spots are length and one closing recap. The one sentence meant to describe the search is also vague, and four places word the same fact differently. The README bullet uses one term an outside reader cannot decode. Nothing is blocking.

## Construction search (done by hand; `murderboard_prose.sh` is not vendored)

**List used:** the role-5 banned-constructions list from `doc_review_process.md`, as given in my checklist. I ran it over the `+` lines of `go_diff.patch`. Two Grep patterns were used:
- `^\+.*(not (just|only|merely)\b.*\bbut\b|it'?s not about|is not about|worth noting|\bdelve|\bleverag|\brobust|\bseamless|\bcrucial|\blandscape|\btapestry|in today's|—)`, case-insensitive.
- A second pass for British spellings, because `writing_conventions.md` requires American English.

Pasted hits:

| patch line | construction | kind |
|---|---|---|
| 45 | `GO-CFAR (Hansen 1973 — ⚠ *2026-09-14: ...` | em-dash leading into a caveat, not an uplifting close. Not a defect. |
| 54 | `**not established** — see *Where greatest-of began* below` | em-dash leading into a cross-reference. Not a defect. |
| 62 | `*Radar — present and future*` | dash inside a title. Not a defect. |
| 18 | `already analysed` (README) | British spelling. **Defect** (F9). |
| 89 | `or analysed a technique` (detector_history) | British spelling. **Defect** (F9). |

- **Banned words:** none found (delve, leverage, robust, seamless, crucial, landscape, tapestry).
- **Other banned forms:** no *not just X but Y*, no *it's not about*, no *worth noting*, no *In today's*.
- **Lists:** none built for rhythm. Both new lists have four real items.
- **Existing text in the reviewed Glossary paragraph** (not introduced by this change) contains the banned forms: *"That argument is no longer a reading — it is the attribution"* and *"name what these detectors are, not what they resemble"*. See F13.

## Word and sentence counts per changed block (counted by hand)

| block | words | sentences |
|---|---|---|
| Table row, attribution cell + held? cell | 19 + 8 = 27 | 2 + 1 fragment |
| Inline ⚠ flag (Revised 2026-08-24 note) | 22 | 1 (a bracketed aside inside a sentence that is already long) |
| Opening paragraph of *Where greatest-of began* | 75 | 5 |
| "What the papers we hold say about it:" | 8 | 1 |
| ↳ bullet: Hansen's own 1980 paper | 48 | 2 |
| ↳ bullet: the 1972 Sawyers memo | 57 | 4 |
| ↳ bullet: Gandhi & Kassam 1988 | 45 | 2 |
| ↳ bullet: Rohling 1983 | 20 | 1 |
| "What we do not know:" + 4 items | 5 + 62 | 1 + 5 |
| Closing "That is why the attribution cell…" | 16 | 1 |
| **Whole new passage** | **~336** | **22** |
| Glossary: inserted aside / sentence that holds it / whole paragraph | 18 / ~87 / ~140 | aside / 1 / 4 |
| README: changed text in the LoCo bullet | 81 | 5 |

## Passage test (one sentence each block delivers; what the rest buys)

- **Whole passage.** The point: *the usually credited 1973 paper could not be found, and an unseen 1972 memo had already analyzed the split detector, so whether 1973 introduced greatest-of is unknown.*
  - That point sits in the "What we do not know" list (its second item) and at the end of the Sawyers bullet, near the bottom.
  - **Evidence a sceptic would ask for:** the full citation, the 1980 quote, the Sawyers memo and its date, Gandhi & Kassam's word "proposed", and Rohling not citing 1973.
  - **Thoroughness for its own sake:** the calendar dates of the search, the contents-listing sentence, the page-range source sentence, unknown items 1 and 3 (they repeat "no copy" and "not seen"), and the closing recap.
  - Cutting those takes about 60–80 words out, leaving roughly 260. Details in F1–F7.
- **Table row.** Delivers "origin not established; the 1980 paper is the loss analysis." It carries a sentence where the other rows hold a single citation. That is acceptable.
- **Inline flag.** Delivers "the Hansen 1973 credit is withdrawn; see §4." The date is the one thing that separates it from the note it sits in, so it earns its place. The rest is fine apart from F10.
- **Glossary aside.** Delivers "origin not established." The rest (the link and "sets out what is known and what is not") belongs in `detector_history.md`, not in a vocabulary file. See F11.
- **README.** Delivers "greatest-of CFAR; origin not established; see detector_history." One 39-word sentence carries two separate facts, and one of them uses undefined jargon. See F8.

## Findings

| # | location | issue | severity | suggested fix | verifiable against a source |
|---|---|---|---|---|---|
| F1 | detector_history.md, closing line of *Where greatest-of began* ("That is why the attribution cell … reads *not established*.") | A closing recap, which the house voice bans. The table already points here, so this line only points back. | major | Delete the sentence. | yes (table row 466 already has the cross-reference) |
| F2 | detector_history.md, opening paragraph: "and no other route produced text" | The brief says "describe our attempt", and this is the only sentence about the attempt. It hedges where it should name the routes. A reader cannot tell whether "other route" means an interlibrary loan request or one web search. | major | Name the routes tried (for example IET Digital Library, British Library, interlibrary loan), in one short clause. Or say plainly that only the contents listing and Xplore were tried. | no (the routes tried are not recorded in the diff) |
| F3 | detector_history.md, whole new passage | About 336 words for a brief that asks for brevity. The neighboring correction paragraph above it is about 45 words. | major (as a total; the itemized cuts are F1, F4–F7) | Apply F1, F4, F5, F6 and F7. Target about 250 words. | yes (the counts above) |
| F4 | opening paragraph: "We looked for it from 2026-09-10 to 2026-09-14" | Calendar dates standing in for a duration (writing_conventions: "drop the calendar date that merely encodes it"). | minor | "We spent five days looking for it and found no copy." Or drop the time span and name the routes (F2). | yes |
| F5 | opening paragraph: "The volume's contents listing confirms the author and title and nothing more." | The listing is not named, so the reader cannot check it. The sentence also stands alone for what could be a clause. | minor | Fold it into the previous sentence and name where the listing is: "…found no copy; the volume's contents listing (in <catalog>) confirms only author and title." | no |
| F6 | "What we do not know", items 1 and 3 | They repeat "found no copy" and "We have not seen the memo" from earlier. The real unknown, item 2 ("introduced … or analysed"), sits second. | minor | Put item 2 first. Merge items 1 and 3 into it or cut them. | yes |
| F7 | Gandhi & Kassam bullet: "That reference list is our only source for the page range." | An 11-word sentence about bibliographic housekeeping. | minor | "…and give its pages as 325–332, our only source for them." | yes |
| F8 | README.md LoCo bullet: "a 1972 internal memo cited in the 1980 paper already analysed the same split detector" | "split detector" is undefined anywhere in the README; its only other meaning there is event streams. "the same" has no detector to refer back to, because the sentence before named a paper. One 39-word sentence also carries two facts (not found; memo earlier). | major (README is the outside-reader surface) | Split it: "The work usually credited, Hansen (1973), … could not be found. A 1972 internal memo, cited in the 1980 paper, had already analyzed greatest-of." | yes (detector_history: "The 1980 paper derives greatest-of's detection performance from it") |
| F9 | README.md line 658 "analysed"; detector_history.md line 512 "analysed" | House convention is American English. | minor | "analyzed" in both places. | yes (writing_conventions.md, "American English") |
| F10 | detector_history.md line 204–206, inline flag | (a) It says "§4 says what is known" and drops "and what is not", the half the brief emphasizes. The README and Glossary both keep it. (b) The aside sits inside a sentence with another dash and a later "and its percentile-of-pool…", so the reader loses that thread. Line 206 is a stub reading "> known*) and". | minor | "(Hansen 1973; ⚠ *added 2026-09-14: no copy found and origin not established, see* Where greatest-of began *in §4*)". Re-wrap the lines. | yes |
| F11 | GLOSSARY.md aside inside "That argument is no longer a reading" | The other two bracketed asides in that sentence are citations (Finn & Johnson 1968, Rohling 1983). This one is an 18-word clause with a semicolon and a link, which breaks the pattern. Placed right after "closed every lineage row", it also reads as if this row were reopened, when only the origin is open, not the family. | minor | "`maxlt` is GO-CFAR (origin not established; see [*Where greatest-of began*](detector_history.md))". | yes |
| F12 | detector_history.md bullet 1 "Hansen's own 1980 paper" and bullet 2 "J.H. Sawyers wrote an internal memo" | The reader is not told that Sawyers is the 1980 co-author, although the table says "Hansen & Sawyers". The second bullet's bold lead-in is a claim, while the other three bold lead-ins are source names, and bullets 1 and 2 are the same paper. The gloss "So the 1973 paper dealt with greatest-of selection" uses a vague verb for what the quote actually says: it gave a loss rule. | minor | Bold "**Hansen & Sawyers 1980**" in bullet 1. Open bullet 2 with "**Sawyers's 1972 memo, via the same paragraph.**" Change the gloss to "So the 1973 paper gave a rule for greatest-of's detectability loss." | yes (quote at line 493–496) |
| F13 | GLOSSARY.md, reviewed paragraph, existing text: "That argument is no longer a reading — it is the attribution." / "what these detectors are, not what they resemble" | Banned *not A, it's B* forms. They are not introduced by this diff, but they sit in a paragraph under review. | minor (existing) | Leave for this change unless the author wants them fixed. If fixing: "**That argument is now the attribution.**" | yes |
| F14 | Same fact worded four ways: "we could not establish" (detector_history lead-in), "is not established" (README, flag), "could not be established" (Glossary), "not established" (table) | One fact in four wordings invites a reader to look for a difference that is not there. | minor | Pick one: "not established" (it matches the table cell) everywhere except the bold lead-in, which works as the passage's name. | yes |
| F15 | The 1973 title: README "*Constant false alarm rate processing in search radars*" vs detector_history "*"Constant-false-alarm-rate processing in search radars"*" | The same title is written two ways, so at least one is not verbatim. | minor | Use the contents-listing form in both files. | no (listing not accessible to me) |
| F16 | Pointers "§4" in README, Glossary and the flag | §4 is long. The passage already has a name the table uses (*Where greatest-of began*), and writing_conventions says "name things; don't index them". | minor | Point at the name, or "§4, *Where greatest-of began*". | yes |
| F17 | "What we do not know", item 4 | It is a fragment ending in ";", followed by a full sentence inside the same item, which breaks the list's grammar. "LOG/CFAR" is an abbreviation never defined (LOG presumably logarithmic). | minor | "…whether Hansen's earlier CFAR papers bear on it: Hansen & Zottl 1971 (Siebert and Dicke-Fix detectors) and Hansen & Ward 1972 (cell-averaging logarithmic-receiver CFAR), neither on the shelf." | partly (the meaning of LOG needs the source) |
| F18 | Rohling bullet: "Moore & Lawrence 1980" | Named without a citation anywhere in the passage, so a reader cannot look it up. | minor | Add venue and year as Rohling's reference list gives them. | yes (Rohling 1983 reference list, on the darkroom shelf; not opened by me) |

**Not flagged:**
- The date in the inline flag marks a later amendment inside a dated note, so it carries meaning.
- "twenty months" is correct: 15 February 1972 to 23 October 1973.
- The fronted bold lead-in "Where greatest-of began, we could not establish." also serves as the passage's name, so the unusual word order does a job.
- Keeping the Gandhi & Kassam quote exact matters: the doc says quotations are matched mechanically against PDFs, so F12 and F17 leave all quotes untouched.

**Files:**
- `<worktree>\docs\detector_history.md`
- `<worktree>\docs\GLOSSARY.md`
- `<worktree>\README.md`
- `<repo>\docs\writing_conventions.md`
