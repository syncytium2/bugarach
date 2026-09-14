GRANT 11 ok — Read, Grep, Glob

## 1. Spine of the new §4 passage, "Where greatest-of began is not established"

**Opening paragraph**
1. Where greatest-of selection began is not established.
2. This document used to credit Hansen's 1973 paper (IEE Conference Publication 105, London, 23–25 October 1973), with the full bibliographic details.
3. Nobody on this project has read that paper.
4. A notice in *Proc. IEE* confirms the paper exists: author, title and ISBN.
5. The search failed: Hansen's IEEE Xplore record is empty for 1972–74, three databases refused automated searches, two others hold records with no text, and no library request is recorded.

**"What the sources we hold say, oldest first"**
6. Hansen & Sawyers 1980 cite the 1973 paper for a loss rule for greatest-of, so the 1973 paper treated greatest-of. They also cite a 1972 Sawyers memo and describe the two authors' work as independent.
7. The patent says Hansen proposed a Weibull-clutter CFAR processor in 1973, so the talk covered more than greatest-of.
8. Rohling 1983 says Moore & Lawrence proposed greatest-of and doesn't cite the 1973 paper.
9. Gandhi & Kassam 1988 say Hansen 1973 proposed it, and they are our only source for its pages. They call the venue an IEEE conference.

**"What we do not know"**
10. Whether the 1973 paper introduced greatest-of or analyzed something already in use.
11. Who proposed it: Rohling and Gandhi & Kassam disagree.
12. What the 1973 paper and the 1972 memo contain.
13. Whether Hansen's 1971 and 1972 papers bear on it.

**The arc I judged against.** The brief's arc: status, then what used to be claimed, then the search, then what we know, then what we don't. That is the default arc minus "the fix". The passage follows it with one gap: it never says **what depends on the answer**, which is the "what it costs" step. Findings F2 and F1 cover the gap and a related problem.

**Does it open on the problem?** Partly. The bold opening sentence is the status, which is right. But the reason for that status is that the sources we hold **disagree about who proposed it** (points 8, 9 and 11). That reason doesn't show up until point 8 of 13 and isn't named until point 11. The first paragraph only gives "nobody has read it", so a reader can finish it thinking the only problem is access, and that Gandhi & Kassam's "Hansen has proposed" settles the question.

**Spine of the whole of §4, for placement:**
- **S1.** The manuscript rests on a 2×2 taxonomy with one "empty" cell.
- **S2.** The locality axis is CFAR's.
- **S3.** The table maps each mechanism to a named CFAR variant.
- **S4.** The papers read in full are on the shelf; the 1973 paper isn't ("below").
- **S5.** A correction: the censoring fix is Weiss's and Rickard & Dillard's.
- **S6.** `maxlt` matches greatest-of in how it combines the two windows, not in how it estimates each one.
- **S7.** It is a convergent rediscovery: the cell is only empty in calcium imaging.
- **S8.** The new passage.

Putting S8 at the end is defensible. If its 47 lines sat next to S5 (the other provenance correction), they would bury S6 and S7, which are the argument. The pointers in S3 (table cell) and S4 (paragraph after the table) come right where a reader first meets the greatest-of row, so they arrive when needed.

## 2. Findings

**F1**
- **Location:** detector_history.md §4, opening paragraph of the new passage.
- **Issue:** The reason the origin is "not established" (the sources we hold credit different people) comes last, in points 8–11. The opening paragraph gives only "nobody has read it", which reads as an access problem that Gandhi & Kassam's explicit credit would settle.
- **Severity:** major.
- **Fix:** After "Nobody on this project has read it", add one sentence stating what we know: the sources we hold do not agree on who proposed it (Rohling 1983 credits Moore & Lawrence; Gandhi & Kassam 1988 credit Hansen). This introduces no new origin claim.
- **Verifiable:** yes (the passage's own bullets).

**F2**
- **Location:** detector_history.md §4, where S7 ("occupied for a long time") meets S8.
- **Issue:** A bold "…is not established" directly follows the section's conclusion, and nothing says whether it takes back S6 or S7. Readers arriving from the README, GLOSSARY or cfar_scope pointers land here without §4's context. The passage never says what does and doesn't depend on its question.
- **Severity:** major.
- **Fix:** Add one sentence saying the mechanism match (S6) and §5.4 do not depend on who began greatest-of, and that greatest-of is in print in Hansen & Sawyers 1980, which is read in full. That states a lower bound we hold, not an origin. Have role 4 check the wording.
- **Verifiable:** yes.

**F3**
- **Location:** docs/learned/cfar_scope.html, map table, `LoCo · maxlt` row.
- **Issue:** Word order implies a new origin. In a column headed "source", where the sibling rows (Finn & Johnson 1968, Rohling 1983) are origins, the cell leads with "Hansen & Sawyers 1980" and only then adds "(loss analysis; origin not established)". detector_history's table puts the two in the opposite, correct order.
- **Severity:** major.
- **Fix:** Match detector_history: "origin not established; loss analysis: Hansen &amp; Sawyers 1980".
- **Verifiable:** yes.

**F4**
- **Location:** cfar_scope.html, `VARIANTS` GO entry, `cite:` field (line 382).
- **Issue:** Same problem, worse. Lines 813 and 823 render this string under the GO mini-plot and in its hover text, next to "Trunk 1978", "Rohling 1983" and "Weiss 1982". It reads "Hansen & Sawyers 1980; origin not established": a name in the origin slot, contradicted in the same breath, with no "loss analysis" label.
- **Severity:** major.
- **Fix:** Use "origin not established" alone, or "origin not established; loss: Hansen & Sawyers 1980".
- **Verifiable:** yes.

**F5**
- **Location:** GLOSSARY.md, CFAR paragraph.
- **Issue:** The inserted sentence ends with the pointer. The next bold sentence is "None of it is a problem — priority is closed (Tony, 2026-08-24)". Placed right after "not established", "priority is closed" can read as closing the greatest-of origin question, which the brief forbids. It actually refers to bugarach's own claim to have been first.
- **Severity:** minor.
- **Fix:** Move the greatest-of sentence and its pointer after "…sets out." at the end of the paragraph, or write "bugarach's priority is closed".
- **Verifiable:** yes.

**F6**
- **Location:** GLOSSARY.md, same paragraph.
- **Issue:** "the four radar primaries were retrieved and read" comes before the `maxlt` clause. A reader will assume one of the four is the greatest-of source. detector_history was reworded to "the four papers the table marks *read in full*" to avoid exactly this.
- **Severity:** minor.
- **Fix:** "four radar papers", or name them.
- **Verifiable:** yes.

**F7**
- **Location:** detector_history.md, revision note dated 2026-08-24 (lines 204–208).
- **Issue:** The ⚠ flag sits in the middle of the sentence, and the sentence goes on to say §4's argument "has … become the attribution". Read in order, the conclusion outlasts the flag. This note is the first mention of greatest-of a cold reader meets.
- **Severity:** minor.
- **Fix:** Move the ⚠ to the end of the sentence, scoped: "⚠ 2026-09-14: the mechanisms are CFAR's; where greatest-of began is not established (§4)".
- **Verifiable:** yes.

**F8**
- **Location:** detector_history.md §7 item 2.
- **Issue:** The ⚠ comes 23 lines after "~~Verify…~~ **Done**" and straight after "nothing on this item is outstanding". Someone scanning §7 reads "Done" and moves on. "One attribution did not survive" also leans toward "refuted", which is more than the passage establishes.
- **Severity:** minor.
- **Fix:** Put the ⚠ on the line after "**Done 2026-08-22**", worded as "one attribution is withdrawn: where greatest-of began is not established (§4)".
- **Verifiable:** yes.

**F9**
- **Location:** detector_history.md §4, paragraph after the table.
- **Issue:** "The one quotation from outside the shelf, from a patent, is marked as such" announces a patent 25 lines before the reader meets it, with no pointer. The patent bullet in the passage doesn't say it's off the shelf either; only the Sources entry does.
- **Severity:** minor.
- **Fix:** Add "(*Where greatest-of began*, below)", and mark the patent bullet itself as off the shelf.
- **Verifiable:** yes.

**F10**
- **Location:** detector_history.md §4 table, `maxlt` "held?" cell.
- **Issue:** "Hansen 1973 **not read**" names a work the attribution cell beside it doesn't name. It is defined 37 lines later.
- **Severity:** minor.
- **Fix:** Drop it from the held cell (the passage covers it), or add "formerly credited: Hansen 1973" to the attribution cell.
- **Verifiable:** yes.

**F11**
- **Location:** new passage, opening paragraph vs point 9.
- **Issue:** The aside "(IEE, the British body, not the IEEE)" comes long before its use. It only matters at point 9, where Gandhi & Kassam call the venue an IEEE conference, and point 9 doesn't refer back to it.
- **Severity:** minor.
- **Fix:** In point 9, add "(the *Proc. IEE* notice above names the IEE)", or move the aside there.
- **Verifiable:** yes.

**F12**
- **Location:** new passage, point 13 vs point 5.
- **Issue:** Hansen's 1971 (with Zottl) and 1972 (with Ward) papers first appear in the "do not know" list. They belong with the search in point 5, which reports that his author record is empty for 1972–74. A reader can't square the two from where each sits.
- **Severity:** minor.
- **Fix:** Name both papers in the search paragraph and keep point 13 as the open question.
- **Verifiable:** yes.

**F13**
- **Location:** detector_history.md; all four pointers.
- **Issue:** Every pointer cites "§4, *Where greatest-of began*", but that is a bold opening sentence, not a heading. It has no link anchor, so README and GLOSSARY readers land at the top of a 1,000-line file and have to find it. A heading would also mark it as a coda rather than a retraction of S7, which helps F2.
- **Severity:** minor.
- **Fix:** Make it `### Where greatest-of began`, and link the README and GLOSSARY pointers to that anchor.
- **Verifiable:** yes.

**F14**
- **Location:** README.md, LoCo bullet in the citation list.
- **Issue:** The order within the bullet is sound: the citable cost paper, then the status, then the history, then the pointer. But the history sentence repeats the retired reference in full citation form (author, year, italic title, venue) inside a list headed "Cite in any publication…", where a skimmer copying references will pick it up.
- **Severity:** minor.
- **Fix:** Shorten to "This README used to cite a 1973 Hansen conference paper as the origin", and leave the full details to §4.
- **Verifiable:** yes.

**F15**
- **Location:** cfar_scope.html lede.
- **Issue:** The caveat about one row becomes the closing clause of the section's lede, before the table. The row cell repeats it six lines later.
- **Severity:** minor.
- **Fix:** Optional: keep the caveat only in the row (once F3 is fixed) and end the lede at "§4".
- **Verifiable:** yes.

**Checked, no findings:**
- The "oldest first" order of the sources. It is stated openly, and it happens to put the two conflicting credits (points 8 and 9) side by side.
- The table cell's own order: "not established" before "loss analysis". That is correct.
- The Sources entry.
- The GLOSSARY term entry for greatest-of carries no origin note. That is consistent, because no term entry in that list carries one.
- The passage adds no follow-up action to §7, which is consistent with "leave it at that".

Files: `<worktree>\docs\detector_history.md`, `...\docs\GLOSSARY.md`, `...\README.md`, `...\docs\learned\cfar_scope.html`
