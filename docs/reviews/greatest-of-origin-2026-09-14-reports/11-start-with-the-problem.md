GRANT 11 ok — Read, Grep, Glob

## Spine: the new passage (docs/detector_history.md lines 483–519)

1. **P1 (problem and search):** We cannot say where greatest-of began. The paper usually credited, Hansen 1973, is known only from a contents listing, and a four-day search found no copy.
2. **Lead-in (line 491):** What follows is what the papers we hold say. This is a signpost, not a claim.
3. **Known 1:** Hansen's 1980 paper says the 1973 paper gave a loss rule for greatest-of selection, so the 1973 paper dealt with greatest-of.
4. **Known 2:** A 1972 Hughes memo by Sawyers analysed the "split" detector 20 months before the conference, and the 1980 paper builds on it. We have not seen it.
5. **Known 3:** Gandhi & Kassam 1988 say Hansen 1973 proposed a CFAR (constant false alarm rate) procedure for clutter transitions. Theirs is our only source for the page range.
6. **Known 4:** Rohling 1983 credits greatest-of to two 1980 papers and does not cite 1973.
7. **Unknown:** We don't know what the 1973 paper contains, whether it introduced greatest-of or analysed something already in use, what the memo contains, or whether Hansen's earlier papers from 1971 and 1972 bear on it.
8. **Consequence:** That is why the table cell reads *not established*.

**Arc used:** problem, then the search, then what we know, then what we don't, then what it means for the table. This is the brief's own arc. The passage follows it exactly, and its first sentence is the problem. Within the passage, the order is sound.

## Spine: §4 as it now stands (for placement)

1. The manuscript's 2×2 rests on two axes, and the locality axis is CFAR's.
2. Table: each detector matched to a CFAR variant with its attribution. The `maxlt` cell says *not established* and *1973 no copy found*.
3. "All four primaries are now held and read."
4. Correction: the censoring fix is older than Gandhi & Kassam.
5. **[new]** Where greatest-of began is not established (37 lines).
6. `maxlt` matches greatest-of's combination rule. Taking the larger half means a clutter edge, such as a drug-onset ramp, cannot lower the bar.
7. Verdict: this is a convergent rediscovery. The cell was empty only in the calcium-imaging literature, and in detection theory "it has been occupied for a long time".

## Findings

| # | Location | Issue | Severity | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| 1 | detector_history.md §4, placement of lines 483–519 | **The passage uses ideas before §4 explains them.** Known 3's evidence is that Hansen "proposed a CFAR procedure to regulate false alarm rate in the region of clutter transition". That links to greatest-of only if you already know greatest-of exists for clutter edges, and §4 says so only at lines 526–528, *after* the passage. Likewise, "split" in the memo title (line 498) is only tied to the two half-windows by the table's one-line mechanism; the full explanation is in §5.4 (line 653). Where it sits now, the passage also pushes the section's actual case (the match and the verdict, spine items 6–7) below a 37-line side trip into sources. | major | Move the passage to the **end of §4**, after the "convergent rediscovery" paragraph and before the `---`. By then the reader knows what greatest-of does and why, so every quote in the passage can be judged. The link also reads naturally: "occupied for a long time" leads into "where it began, we could not establish". Change the table pointer to "see *Where greatest-of began*, end of this section". Putting it straight under the table would be no better (still before the mechanism). Putting it after the `maxlt` paragraph would split the mechanism from its verdict. | yes (lines 466, 483–530) |
| 2 | detector_history.md line 473, between the table and the passage | **A contradiction comes before its explanation.** The table cell says "1973 **no copy found**", and the next paragraph opens "**All four primaries are now held and read**". Until the explanation arrives, the reader holds a contradiction. §7 item 2 (line 984) also still says "nothing on this item is outstanding". | major | Make line 473 say which four it means, e.g. "All four primaries the table rests on are held and read; the one work no copy was found of is taken up in *Where greatest-of began*." Whether §7 item 2 needs a matching note is Tony's call under the "leave it at that" brief. I am flagging it, not asking for a new to-do. | yes (lines 466, 473, 984) |
| 3 | README.md lines 655–661, order of the caveat sentences | **The order implies a new origin, which the brief forbids.** The bullet goes: not established, then the 1973 paper could not be found, then "a 1972 internal memo … already analysed the same split detector", then the pointer. It ends on the one fact that reads as a rival origin, and drops everything that balances it: Hansen's own 1980 description, "we have not seen the memo", and the unknowns. The history doc gets the order right. The README summary reverses its weight. | major | Put the pointer straight after the bold sentence: "**Where greatest-of began is not established**; `docs/detector_history.md` §4 sets out what is known and what is not." Then either drop the memo sentence, or follow it with what is not known ("… a 1972 memo, which we have not seen, analysed it earlier"), so the bullet does not end on an implied answer. | yes |
| 4 | README.md line 659, "the same split detector" | **An undefined term arrives before the reader can judge it.** Nothing earlier in the README defines "split detector", and "the same" has nothing to refer back to (the text before says "greatest-of CFAR"). | minor | Say "greatest-of's two-half-window detector", or drop the phrase (see #3). | yes |
| 5 | detector_history.md lines 493–507, order of the four "known" bullets | **The list has no stated order.** It runs 1980 author, then 1972 memo, then 1988, then 1983. The piece of evidence that complicates the story (the memo) sits between two that support the usual credit, so the reader cannot tell whether the order is meant to argue something. | minor | Pick one order and keep to it: Hansen's own account first, then his co-author's memo, then later citers by date (Rohling 1983 before Gandhi & Kassam 1988). This only swaps the last two bullets, and the order then carries no hint of a verdict. | yes |
| 6 | detector_history.md lines 514–516, last "unknown" bullet | **Two new sources first appear inside the unknowns list.** Hansen & Zottl 1971 and Hansen & Ward 1972 were not set up among the known facts, and the passage never says why earlier papers might matter (that Hansen already had CFAR work before 1973). The reader meets the question before its reason. | minor | Add one clause giving the reason, e.g. "Hansen had published on CFAR receivers before 1973 (Hansen & Zottl 1971; Hansen & Ward 1972), and neither is on the shelf." Or cut the bullet down to the question alone. | yes |
| 7 | detector_history.md lines 197–206, inline flag in the 2026-08-24 revision note | **Correct placement.** The correction appears exactly where the old claim ("Hansen 1973") is read, and its pointer to §4 is a proper forward reference. One cost: this is a 3-line aside in the middle of the sentence, and it leaves the lead claim "closed every lineage row" (line 198) sounding unqualified until the aside. Identity (`maxlt` is GO-CFAR) is still closed; only origin is open, so this is tolerable. | minor | Optional: move the ⚠ to the end of the sentence, after "become the attribution", so the 08-24 sentence reads whole and the flag follows it. | yes |
| 8 | GLOSSARY.md lines 262–265, CFAR vocabulary paragraph | **The pointer arrives at the right moment**, beside the attribution it qualifies and before the vocabulary list relies on it. But the parenthetical sits between "GO-CFAR" and "and its percentile-of-pool", so "its" now seems to refer back to `detector_history.md` or to greatest-of rather than to `loco_detect`. | minor | Move the parenthetical after "GO-CFAR" to the end of the sentence as its own sentence ("Where greatest-of began could not be established; `detector_history.md` §4 …"). Or repeat the subject: "and `loco_detect`'s percentile-of-pool …". | yes |

**Answers to the three questions:**
1. The passage opens on the problem and follows the brief's order. No finding about its internal order, apart from #5 and #6.
2. Its current place is defensible, since it sits with the other attribution correction and the table points "below" to it. But it asks the reader to judge clutter-transition and "split" evidence before §4 has explained greatest-of's purpose. End of §4 is the better place (#1), and the "All four primaries" paragraph needs fixing whichever place is chosen (#2).
3. GLOSSARY: the pointer arrives when the reader needs it. README: the pointer comes last, after a sentence the reader can't judge that also points to an answer (#3, #4).

No boundary notes. #2 and the §7 item overlap with factual consistency, which belongs to other roles. I filed them here only for where the sentence sits relative to the cell it contradicts.

Files: `<worktree>\docs\detector_history.md`, `<worktree>\README.md`, `<worktree>\docs\GLOSSARY.md`
