GRANT 5 ok — Read, Grep, Glob

**Constructions list used:** the role-5 banned-constructions list in `docs/doc_review_process.md`, lines 567–572, plus `docs/writing_conventions.md` for American spelling, dates and naming. `murderboard_prose.sh` is not vendored, so I searched the diff `go_diff_r2.patch` with Grep instead.

**Search 1: banned words and phrases.** Pattern: `(?i)not just|it's not about|it is not about|worth noting|delve|leverag|robust|seamless|crucial|landscape|tapestry|in today's`
```
No matches found
```
**Search 2: added lines containing a dash**, checking for an em-dash pivot into an uplifting close.
```
24:+  107(2):517–531, doi:10.1152/jn.00633.2011. LoCo's `maxlt` mode takes the
28:+  IEEE T-AES AES-16(1):115–118, doi:10.1109/TAES.1980.308885. **Where greatest-of
54:+on 2026-08-24 identified the family of every lineage row — `rate_detect` is
68:+- **greatest-of (GO) / ordered-statistic (OS) selection** — combination rules for the
84:+> and its percentile-of-pool is kin to OS-CFAR — so §4's argument that three of these
93:+| LoCo, `maxlt` | ... 115–118 | 1980 **read in full**; Hansen 1973 **not read** |
105:+at `<darkroom>/bugarach/lit/radar/` with a read-status entry each — Tony supplied
120:+*"Constant-false-alarm-rate processing in search radars"*, given at *Radar —
122:+(IEE, the British body, not the IEEE), 23–25 October 1973, and published in its
143:+  report, which it paginates 1–8. So the talk covered more than greatest-of.
153:+  source we hold for its page range, 325–332, and it names the venue as an IEEE
```
All of these are page ranges, a title, or a dash that introduces a list or a clause. None is a pivot into an uplifting close.

**Search 3: spelling.** Pattern: `^\+.*(?i)(analyz|analys|centre|center|acknowledg)`. It found `analyzed` (line 158) and `acknowledgment` (line 138), both American. The `centred` on the CoactDetect row is in an unchanged line, so it is out of scope.

**Hand checks.** No rhythm-built three-item lists: the three libraries and the three detector lineages are real lists of three. No "In today's" openers.

**Result: 0 banned-construction hits.**

---

## Counts and passage test, per changed block

I counted words by hand, so treat them as ±5%.

| block | words | sentences | the one sentence it exists to deliver | what the other words buy |
|---|---|---|---|---|
| README, LoCo bullet (patch 24–32) | ~80 | 4 | "`maxlt` is greatest-of selection, and where greatest-of began is not established." | The Hansen & Sawyers citation is useful. "This README used to cite ° Hansen 1973" is the document's own history (git already has it), and it keeps a paper nobody has read in a citation list. "in radar" repeats the sentence before it. |
| README, ° legend | shorter by one clause | 1 | Unchanged | A clean cut. |
| GLOSSARY, CFAR paragraph (changed part) | ~120 | 4, one of them ~76 words | "The mechanisms are CFAR's; where greatest-of began is not established." | The ~76-word second sentence was already there. The edit made it longer by writing out `loco_detect`'s twice and defining GO and OS, which the bullet below defines again. |
| GLOSSARY, GO/OS bullet | ~20 | 1 | Unchanged | Adds the abbreviations. This is the right place for them; the paragraph above is the redundant copy. |
| detector_history, Revised note flag (patch 82–84) | ~13 inserted | inserted into 1 | "Origin not established, see §4." | Nothing to cut. The insertion splits a clause (see finding 9). |
| §4 table row, LoCo `maxlt` | ~35 in the two cells | table | "Attribution not established; Hansen & Sawyers 1980 is the loss analysis." | "at the end of this section" repeats what the paragraph after the table says ("below"). |
| Paragraph after the table (patch 104–110) | ~91 | 4 | "Four of the table's papers are on the shelf and read; the 1973 Hansen paper is not." | Sentences 3–4 correct an old claim about how quotations were checked. They are true, but they are a second point in this block and they repeat the Sources entry. The payload comes first, which is right. |
| *Where greatest-of began*, opening paragraph | ~138 | 7 | Not written anywhere: "The one paper this document credited is unread, and the sources we hold credit two different people." | The venue, the ISBN and the list of failed searches describe the attempt, which the brief asks for. The garbled "cited … as Hansen" clause and the separate Xplore author-record sentence are thoroughness. |
| "What the sources we hold say", 4 bullets | ~245 | 10 | Gandhi & Kassam credit Hansen; Rohling credits Moore & Lawrence; Hansen & Sawyers cite a 1972 Hughes memo. | The patent bullet (~38 words) bears on what else the 1973 paper covered, not on who began greatest-of. It also drags in one sentence in the paragraph after the table and one clause in Sources. The Hansen & Sawyers acknowledgment sentence never says what it implies. |
| "What we do not know", 4 bullets | ~70 | 5 | "Whether the 1973 paper introduced greatest-of or analyzed something already in use." | Bullet 2 states a known fact (who credits whom) and mostly restates bullet 1. Bullet 4 introduces two papers without citing them. |
| §7 item 2, ⚠ line | ~25 | 2 | "One attribution did not survive; see §4." | Fine at this length, but it contradicts the sentence right before it (finding 3). |
| Sources entry | ~28 added | 1 | "Every radar quotation is from the shelf except one from a patent." | Repeats sentence 4 of the paragraph after the table. |
| cfar_scope.html, lede | ~20 | 1 | Unchanged mapping pointer | The origin note repeats the table row just below it, and the clause is hard to parse. |
| cfar_scope.html, row and `VARIANTS` cite | ~8 | — | "origin not established" | See finding 12. |

**The whole passage runs about 450 words across §4.** The brief says "leave it at that" and makes brevity part of it. The cuts proposed below come to about 120–150 words, and none of them removes anything a sceptic would ask for.

---

## Findings

| # | location | issue | severity | suggested fix | verifiable against a source |
|---|---|---|---|---|---|
| 1 | detector_history §4, *Where greatest-of began*, sentence 2: "cited here and in the papers below as Hansen" | The clause means nothing ("cited as Hansen") and is false for one of the papers below: the Rohling bullet says "He does not cite the 1973 paper." | major | Cut the clause. | yes (the passage contradicts itself) |
| 2 | Same sentence: "This document used to credit a 1973 paper by V. Gregers Hansen" | "Credit" has no object. The reader is not told what was credited to the paper. | minor | "This document used to credit greatest-of selection to a 1973 paper by V. Gregers Hansen, …" | yes |
| 3 | detector_history §7 item 2, the ⚠ line against the unchanged sentence before it: "All four primaries are read; nothing on this item is outstanding." | The next line says an attribution on this item did not survive, so "nothing … is outstanding" is now contradicted two lines apart. "All four primaries" also reads as if Hansen 1973 was never a primary. | major | Change the sentence before it to "The four primaries on the shelf are read," and let the ⚠ line say the origin attribution is open. Or strike "nothing on this item is outstanding". | yes |
| 4 | *Where greatest-of began*, whole passage | The payload is never stated. The first sentence gives the verdict. The reason (the sources credit different people, and the credited paper is unread) is buried in the second "do not know" bullet. | major | After "…is not established." add one sentence: "The paper this document credited has not been read, and the sources we hold credit two different people: Gandhi & Kassam credit Hansen, Rohling credits Moore & Lawrence." Then drop the second "do not know" bullet (finding 7). | yes |
| 5 | "What the sources we hold say", patent bullet, plus the paragraph after the table ("The one quotation from outside the shelf, from a patent, is marked as such") and the Sources edit | The patent shows only that the 1973 paper covered Weibull clutter too. It has no bearing on who began greatest-of. Keeping it costs about 60 words across three places and is the only reason for the quotation caveat twice over. | major (brevity is in the brief) | Cut the bullet, the post-table sentence and the Sources clause. If it stays, say in the bullet what it bears on. | yes |
| 6 | Same section: "paper" / "talk" / "report" | One object gets three nouns. "So the talk covered…" uses a noun never introduced, and "the 1973 report, which it paginates 1–8" makes a reader wonder whether the report is a different document from the paper at 325–332. | minor | Use "paper" throughout. If the patent bullet stays, write "paginates it 1–8". | yes |
| 7 | "What we do not know", bullets 1–2 | Bullet 2 ("who proposed it: Rohling credits…, Gandhi & Kassam credit…") restates bullet 1, and its second half is something we *do* know, sitting under the "do not know" heading. | minor | Merge into bullet 1, or move the credit split into the payload sentence from finding 4. | yes |
| 8 | "What we do not know", bullet 4: "Hansen's earlier CFAR papers, with Zottl in 1971 and with Ward in 1972 … Neither is on the shelf." | Two papers appear here for the first time with no citation, so a reader cannot find them. The second sentence also breaks the list's lower-case fragment style. It may clash with "author record lists nothing between 1972 and 1974" (is the 1972 Ward paper inside that range?). | minor | Give venue and year for both papers, or cut the bullet. Change the Xplore sentence to "lists nothing dated 1973". | yes |
| 9 | Revised 2026-08-24 note: "`maxlt` is GO-CFAR (~~Hansen 1973~~; ⚠ *2026-09-14: origin not established, see §4,* Where greatest-of began) and its percentile-of-pool…" | A 13-word insertion separates the subject from "and its percentile-of-pool". The italics are also reversed: everywhere else the section name is the italic part, here it is the only roman part. | minor | Put the flag after the sentence: "…become the attribution. ⚠ *2026-09-14:* the Hansen 1973 origin is struck; see §4, *Where greatest-of began*." | yes |
| 10 | Paragraph after the table, sentence 1: "The four papers the table marks *read in full* are held and read" | Circular: papers marked "read" are read. "The two IEEE papers" is also ambiguous, because three papers in the table are IEEE T-AES (Hansen & Sawyers, Rohling, Gandhi & Kassam). | minor | "Four of the table's papers are on the shelf at `<darkroom>/bugarach/lit/radar/`, each read in full with a read-status entry; Tony supplied Hansen & Sawyers and Gandhi & Kassam on 2026-08-22." | yes |
| 11 | Paragraph after the table, sentence 3: "Radar quotations are checked by hand…; `tools/verify_quotes.py` traces some of them automatically and is not yet a gate." | Passive with no actor or time ("are checked" by whom, and when?). "Some" is a hedge where a count is possible. "Gate" is in-house jargon for an outside reader. The Sources entry repeats the claim. | minor | "Each radar quotation was checked by hand against the PDF text in this revision; a script checks N of them, and nothing runs it automatically." Keep this claim in one place only. | yes |
| 12 | cfar_scope.html `VARIANTS` GO `cite: "Hansen & Sawyers 1980; origin not established"` | It renders under the rule and in the tooltip in the same format as `"Weiss 1982; Rickard & Dillard"`, where the semicolon separates two sources. A reader parses "origin not established" as a second source. It also drops the "loss analysis" qualifier the table row keeps. | minor | `cite:"Hansen & Sawyers 1980 (loss analysis; origin not established)"`, matching the row. | yes |
| 13 | cfar_scope.html lede: "…§4, which also records that where greatest-of began is not established." | "that where … is not" is a garden path: the reader expects "where" to lead to a place. The table row two lines down already carries the caveat. | minor | Cut the clause: "The mapping is **docs/detector_history.md** §4." Or: "…§4, which also records that greatest-of's origin is unknown." | yes |
| 14 | README LoCo bullet: "This README used to cite ° Hansen V.G. (1973)… as the origin" | A record of the document's own past edit, in a citation list for people citing the tool. It keeps a full unread citation where a copier will pick it up. "in radar" in the sentence before repeats "radar detection". | minor | "…Hansen & Sawyers (1980)…. **Where greatest-of began is not established**; see [`docs/detector_history.md`] §4, *Where greatest-of began*." Drop the retired citation. | yes |
| 15 | *Where greatest-of began*, sentences 5–7 (Xplore author record; three libraries refused automated searches, OpenAlex and Semantic Scholar hold records without text; no library request recorded) | This is the attempt the brief wants, but in three sentences where one would do, and the author-record sentence adds little. | minor | "Searches of IEEE Xplore, the IET Digital Library and HathiTrust were refused, OpenAlex and Semantic Scholar hold only records, and no library request has been made." | yes |
| 16 | "What the sources we hold say", Hansen & Sawyers bullet: "as the exact analysis the paper's greatest-of curves are prepared from" | "Exact" reads as an intensifier ("the very analysis") when it means exact as opposed to the 1973 "simplified analysis". The passive ending is awkward. The acknowledgment sentence after it never says what it implies. | minor | "…as the source of the exact (not simplified) analysis behind the paper's greatest-of curves." Cut the acknowledgment sentence or state what it bears on. | yes |
| 17 | Sources entry: "except the patent quoted in §4" | Category slip: a patent is not a quotation. It also repeats sentence 4 of the paragraph after the table. | minor | "except the quotation from US patent 4,318,101 in §4, *Where greatest-of began* (Google Patents text)". Or cut, per finding 5. | yes |
| 18 | GLOSSARY CFAR paragraph, sentence 2 | About 76 words in one sentence. The edit made it longer: `loco_detect`'s is written out twice, and GO and OS are defined here and again in the bullet below. | minor | Restore "its percentile-of-pool" and drop "(GO)" and "(OS)" here, leaving them to the bullet. Split at the colon. | yes |

**No blocking findings.** None of these corrections brings back an origin claim. The prose stays within the brief: it describes the attempt and says what is and isn't known. The majors are one false clause (1), one contradiction with neighboring text (3), a payload that is never stated (4), and one bullet that isn't about where greatest-of began (5).

Files reviewed:
- <worktree>\docs\detector_history.md
- <worktree>\docs\GLOSSARY.md (from the diff)
- <worktree>\README.md (from the diff)
- <worktree>\docs\learned\cfar_scope.html
- <scratchpad>\go_diff_r2.patch
