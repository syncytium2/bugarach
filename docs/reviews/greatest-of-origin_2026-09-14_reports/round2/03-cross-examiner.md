GRANT 3 ok — Read, Grep, Glob

**Findings: Cross-Examiner (role 3), blind pass**

What I checked: the patch; the worktree copies of `docs/detector_history.md` (all of it), README "Licensing & citations", GLOSSARY's radar vocabulary section, `docs/learned/cfar_scope.html` (the text sections and VARIANTS), `docs/learned/detector_history.html` compared with the markdown, `docs/INDEX.md`, `docs/MILESTONES.md`, `docs/forks.md`, and `tools/verify_quotes.py`. I also grepped the tree (excluding reviews/, todo/ and lit_needed.md) for Hansen, greatest-of, GO-CFAR, CAGO, 1973 and Gregers. That grep turned up `docs/handoffs/2026-09-10-the-surrogate-is-the-design.md`, `docs/SESSIONS.md` and `docs/proposals/2026-09-10-coordination-without-labels.html`, so I read them too.

Each row: location · issue · severity · suggested fix · verifiable against a source.

1. **`docs/proposals/2026-09-10-coordination-without-labels.html:848`** · This public page still credits the radar family to "(Finn & Johnson 1968; **Hansen 1973**; Rohling 1983)". It is the one companion still naming the origin that the change withdraws everywhere else. · **major** · Take Hansen 1973 out of that list, or cite Hansen & Sawyers 1980 for the analysis and point at detector_history §4. Don't name a new origin. · yes (grep)

2. **detector_history.md §4, "V. Gregers Hansen, cited here … as Hansen"; README "Hansen V.G."** · The new text treats *Hansen* as the surname and *Gregers* as a middle name. `docs/handoffs/2026-09-10-the-surrogate-is-the-design.md:150-153` says the opposite: "`Gregers Hansen` is the canonical surname", confirmed by the IEE volume's contents listing and IEEE's authority record. It lists GLOSSARY, README and detector_history as using a variant, and says the 1980 paper is "Gregers Hansen & Sawyers". So the change settles a naming question in the direction a companion says is not canonical. · **major** · Reconcile with the handoff. Either give the name as the sources print it and say both forms occur, or state that the surname form is itself unresolved. · no (the evidence PDFs are on the darkroom shelf)

3. **detector_history.md Sources, radar-shelf bullet (edited in this change)** · It still says the shelf README carries "**the two outstanding library orders**". Three other passages disagree: §4 says "No library request for the printed volume is recorded", §4 and §7.2 say all four papers are held and read, and SESSIONS.md:890 shows the two orders were Hansen & Sawyers and Gandhi & Kassam, both since supplied. A reader will take one of the "outstanding orders" to be Hansen 1973. · **major** · Drop "the two outstanding library orders" or mark it historical. Keep the §4 sentence as the single statement about a library request. · yes (in-document plus SESSIONS.md)

4. **detector_history.md §7 item 2, "All four primaries are read; nothing on this item is outstanding."** followed by the new ⚠ line · The item is "Verify §4's CFAR attributions against primary sources", struck through as Done. The ⚠ line says one attribution did not survive, and §4 says its primary was never read. "Nothing outstanding" and "not established" now sit next to each other. · **major** · Qualify "nothing on this item is outstanding", for example "…except that the 1973 paper has not been read (§4)". That records a fact without making an origin claim. · yes

5. **§4 "No library request for the printed volume is recorded"** · The handoff (lines 142-144 and 193) records Hansen 1973 as "a library job", filed as a todo. SESSIONS.md:2211 says "one paper, and it needs a library", pointing at lit_needed.md. The need is recorded; what is missing is a placed request. As written, a reader may think nobody noted it. · minor · "A library request is noted as needed but has not been placed." · yes (handoff, SESSIONS)

6. **§4 "What the sources we hold say"** · Two things leave this incomplete. The radar shelf holds `iee_conf_105_1973_CONTENTS_ONLY.pdf` and `gregers_hansen_AUTHOR_PROFILE_ieee.pdf` (SESSIONS.md:2209-2210), but §4 cites a *Proc. IEE* notice and "Hansen's IEEE Xplore author record" without saying whether those are the shelf files. Separately, the list includes the patent, which the paragraph above calls "outside the shelf". · minor · Name where the notice and author-record evidence live. Call the list "sources consulted" or tag the patent. · no

7. **§4 "cited here and in the papers below as Hansen"** · One of "the papers below", Rohling 1983, does not cite the 1973 paper, as the same passage says a few lines later. · minor · "…and in the papers below that cite it". · yes

8. **§4, "IEEE Xplore author record lists nothing between 1972 and 1974" vs "IEEE Xplore … refused automated searches" vs "with Ward in 1972"** · A reader cannot tell how the author record was read if Xplore refused searches. It is also unclear whether "between 1972 and 1974" excludes the 1972 Ward paper, and nothing says where the Zottl 1971 and Ward 1972 references came from. · minor · Say how the record was obtained (the shelf PDF?), write "nothing dated 1973", and give a source for the Zottl and Ward citations. · no

9. **Same passage: "paper" / "report" / "talk" for the 1973 item** · The patent bullet says "report" and then "the talk". The talk is inferred; what the sources quote is the written paper. · minor · Use "paper" throughout, or say "the published paper". · yes

10. **2026-08-24 revision note, the new flag** · Emphasis runs the other way from every other reference to the passage: `*2026-09-14: … see §4,* Where greatest-of began`. README, GLOSSARY, the §4 table and §7.2 all italicise *Where greatest-of began*. Also, in `detector_history.html:440-441` the `~~Hansen 1973~~` strikethrough spans a line break and renders as **literal tildes**, so the struck citation shows unstruck. The renderer does the same at §7 items 2 and 3, where the ordered list also collapses into one `<p>` holding the new ⚠ line (html 1188-1233). Checking the rendered output mechanically is role 10's job; I am filing it once because the brief asked me whether the HTML matches the markdown. · minor · Put the reference in the same italics as the others. Avoid `~~` across a line break, or write "formerly cited as Hansen 1973". · yes

11. **README, GLOSSARY and cfar_scope point at "§4, *Where greatest-of began*"** · No passage has that title. The target is a bold lead-in, "**Where greatest-of began is not established.**", with no heading or anchor, so the reference can't be linked or searched for under its cited name. · minor · Match the cited name to the lead-in exactly, or make the passage a sub-heading. · yes

12. **GLOSSARY (edited) "the four radar primaries were retrieved and read" vs §4 (edited) "The four papers the table marks read in full"** · The change moved §4 from "primaries" to "papers", which fits, since Hansen & Sawyers is now a loss analysis and Gandhi & Kassam "the standard analysis, not the origin". GLOSSARY (just edited) and §7.2 still say "four primaries". · minor · Use one term. "Four papers" fits the new framing. · yes

13. **GLOSSARY "an interface2 audit on 2026-08-24 identified the family of every lineage row" vs the detector_history 2026-08-24 note "closed every lineage row … become the attribution"** · GLOSSARY softened its wording ("the mechanisms are CFAR's"). The source note it summarises still says "closed" and "become the attribution", and the new flag sits inside that sentence. · minor · Leave the dated note as it is, but add "(for GO, the family, not the origin)" beside the flag, or soften GLOSSARY less. · yes

14. **2026-08-22 revision note, "the other two are confirmed from Rohling's printed reference list"** · This predates the change but is a claim about the radar primaries. The other two were Hansen & Sawyers 1980 and Gandhi & Kassam 1988 (SESSIONS.md:890-892). A 1983 paper cannot list a 1988 one. The note also says "§7.2 says … how to get them", which §7.2 no longer does. · minor · Add a bracketed correction to the note. · yes (date arithmetic)

15. **§4 paragraph, "Tony supplied the two IEEE papers on 2026-08-22"** · Kept through the rewrite. Three of the four read-in-full papers are IEEE T-AES (Hansen & Sawyers, Rohling, Gandhi & Kassam), so "the two IEEE papers" doesn't say which. · minor · Name them: "Hansen & Sawyers 1980 and Gandhi & Kassam 1988". · yes

16. **§4 table, censoring row, marked "read in full"** · The cell lists Weiss 1982, Rickard & Dillard and Gandhi & Kassam, but only Gandhi & Kassam is read (the other two are "per Rohling"). The "four papers" count is right only if the reader knows that. · minor · "Gandhi & Kassam **read in full**; Weiss, Rickard & Dillard not read", matching the new style of the LoCo row. · yes

17. **Terminology, §4 table "greatest-of (CAGO-CFAR)"** · GLOSSARY (edited in this change) defines only "greatest-of (GO)". cfar_scope uses GO and GO-CFAR, and the history's own revision note uses GO-CFAR. CAGO appears only inside Rohling quotations and is not in the glossary. Two abbreviations for one reserved term. · minor · Use "GO-CFAR" in the table, or add "CAGO (Rohling's name)" to the GLOSSARY bullet in this change. · yes

18. **§7 item 4, "Rohling 1983 is a rate-local rolling null with a greatest-of combination rule and an order-statistic estimator"** · The new §4 text reports Rohling crediting CAGO to Moore et al. and Hansen et al. as prior work while he proposes OS. §5.5 presents greatest-of combined with an order-statistic estimator as a cheap untried experiment. The three statements don't line up. · minor · Check against Rohling. If he does not combine them, rewrite item 4 as "…names both greatest-of and ordered-statistic CFAR". · no (PDF not accessible)

19. **cfar_scope.html map table vs detector_history §4 table** · The row order differs: cfar_scope has rate+context, LoCo×3, CoactDetect, SCE; the history has rate+context, CoactDetect, LoCo×2, 99.9th percentile, … The last row reads "binned SCE, **CICADA**" in cfar_scope and "binned SCE, **locust**" in the history, and locust is the project name for the port. This predates the change. · minor · Match the history's row order and write "locust". · yes

20. **README citations vs GLOSSARY and history** · GLOSSARY and §4 attribute LoCo's percentile-of-pool to OS-CFAR (Rohling 1983). README's "Cite in any publication" list cites Finn & Johnson and Hansen & Sawyers but has no Rohling. This predates the change, but the LoCo bullet was rewritten in it. · minor · Add Rohling 1983 to the LoCo bullet, or note that it is omitted on purpose. · yes

21. **detector_history.md §3, "`radar`, `CFAR` … return nothing across interface2 and bugarach" / "not cited anywhere in either repository"** · The present tense is now false against the README citations block and this document. This predates the change. · minor · Mark it as "true when written (2026-08-22)". · yes

22. **`docs/handoffs/2026-09-10-the-surrogate-is-the-design.md:154-156`** · It says "Do not change the column until someone has read the 1973 paper" and calls the column *origin*, but the table header is *attribution*. The change does edit that column's content (to "not established"), which fits Tony's brief. The handoff also still describes the column wrongly. · minor (ledger note) · Record in the run record that Tony's brief overrides the handoff instruction. Update or retire that handoff bullet. · yes

23. **`docs/INDEX.md:87`** · The provenance row's keywords (authorship, provenance, lineage, CFAR, radar) have nothing for this passage. "greatest-of", "GO-CFAR", "Hansen 1973" and "origin" would all miss. · minor · Add those keywords to row 87 in this change. · yes

**Checked and consistent:**
- `detector_history.html` text matches the markdown for every changed passage.
- The "four papers … read in full" count matches the table's four marked rows.
- Dates run oldest first (1980, 1980/82, 1983, 1988), and the 2026-09-14 flags match today's date.
- Hansen & Sawyers AES-16(1), Jan 1980, 115–118 is the same in README, the table and SESSIONS.
- Gandhi & Kassam 24(4) 427–445 is the same across documents.
- The 1973 title's hyphenation is now the same in README and history.
- J.H. Sawyers is named the same way in README and history.
- The description of `tools/verify_quotes.py` ("not yet a gate") matches its docstring and forks.md:347.
- Weinberg is on the radar shelf (SESSIONS.md:888), so "the one quotation from outside the shelf, from a patent" holds.
- MILESTONES.md has no CFAR row to reconcile.
- forks.md §8 cites no 1973 origin.

Files referenced:
- `<worktree>\docs\detector_history.md`
- `<worktree>\docs\learned\detector_history.html`
- `<worktree>\docs\learned\cfar_scope.html`
- `<worktree>\docs\GLOSSARY.md`
- `<worktree>\README.md`
- `<worktree>\docs\proposals\2026-09-10-coordination-without-labels.html`
- `<worktree>\docs\handoffs\2026-09-10-the-surrogate-is-the-design.md`
- `<worktree>\docs\SESSIONS.md`
- `<worktree>\docs\INDEX.md`
