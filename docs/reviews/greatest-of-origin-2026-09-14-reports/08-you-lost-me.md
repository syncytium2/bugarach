GRANT 8 ok — Read, Grep, Glob

# Role 8, naive-reader accessibility: round 1 findings for the greatest-of attribution change

I read the diff and the passages around each unit in the worktree. I kept track of what a reader has already been told before reaching each unit.
- **detector_history.md:** §3 has defined CFAR, reference cells, cell under test and guard cells. The table defines CA-CFAR. The revision-note block (unit 3) comes *before* §3, so a reader has not had those definitions there.
- **README.md:** CFAR is never spelled out, and `maxlt` is never explained.
- **GLOSSARY.md:** the paragraph comes before the bullets that define its terms.

**What I checked and found nothing on:**
- **Swerling:** the term does not appear in any of the five units.
- **Figures:** none are in scope, so the chart-type and panel-readability checks do not apply.
- **Illustration:** the new text is about who did what and when, not how a mechanism works, so no picture is needed. Figure `cfar_map.png` panel B already shows the half-windows.
- **Tone:** the only capitals are inside a quoted memo title and the published term LOG/CFAR, so tone is fine.

## Per-unit verdict

| # | Unit | Terms and identifiers first used here | Defined here? | Can a cold reader follow? |
|---|---|---|---|---|
| 1 | §4 table row "LoCo, `maxlt`" | `maxlt`; CAGO-CFAR; "not established"; "loss analysis"; "1973" (held? column) | `maxlt`: yes, the mechanism column explains it. CAGO: no (CA is expanded one row up, GO never is). "loss": no. "1973": no, it only gets a meaning in the passage below. | **Blocking.** Three undefined: CAGO, loss, 1973. The sentence straight after the table says "All four primaries are now held and read", which contradicts "1973 no copy found" to a reader who has not counted the rows. |
| 2 | §4 "Where greatest-of began, we could not establish." to "reads *not established*." | greatest-of (as a noun); IEE Conference Publication; IEEE Xplore vs IEE; "usually credited"; detectability loss; "lagging" (the table says "trailing"); mean level; 'Split'; Hughes Aircraft; clutter transition; Siebert detector; Dicke-Fix detector; LOG/CFAR receiver; Moore & Lawrence 1980; `maxlt` | IEE: no. "Usually credited": no (by whom?). Detectability loss, mean level, Split: no (all inside quotes, none glossed). Siebert, Dicke-Fix, LOG/CFAR: no. Clutter transition: close enough to §3's "clutter edges". Greatest-of: only via the table. The paragraph that explains `maxlt` comes after this passage. | **Blocking.** At least six undefined, and three of them (Siebert, Dicke-Fix, LOG/CFAR) are names a reader does not need. The chain of reasoning is easy to follow; the vocabulary is what loses the reader. |
| 3 | Inline ⚠ in the "Revised 2026-08-24" note | `loco_detect`, `maxlt` (first appearance in the document), GO-CFAR, OS-CFAR, "greatest-of" (new), percentile-of-pool | None. This note sits above §3, so even CFAR has not been spelled out yet. GO is never linked to "greatest-of". | **Blocking** by count. Only "greatest-of" is new in this change; the rest was already there. The parenthesis still opens with "Hansen 1973", which reads as an attribution before the ⚠ takes it back. |
| 4 | GLOSSARY CFAR vocabulary paragraph | `rate_detect`, `loco_detect`, `maxlt`, GO-CFAR, OS-CFAR, percentile-of-pool, greatest-of | CFAR and greatest-of are defined in the bullets *below*. GO and OS are never spelled out. Code identifiers are more acceptable in a glossary. | **No.** "Closed every lineage row" and "could not be established" contradict each other within one sentence. The long new parenthesis leaves "its percentile-of-pool" without a clear owner. |
| 5 | README "LoCo and CoactDetect" bullet | `maxlt`; greatest-of CFAR; CFAR; detectability cost; IEEE T-AES; IEE Conf. Publ.; "the same split detector"; "the 1980 paper"; "the 1973" (resolves fine) | `maxlt`: no. Greatest-of: no. CFAR: never spelled out in the README. Detectability cost: no (cost compared with what?). "Split": no, and nothing says greatest-of is a split detector. IEE: no. "The 1980 paper" and "Hansen (1973)" both resolve. | **Blocking.** At least five undefined. The intro above the list says the shelf "holds only Finn & Johnson", but the bullet says Hansen & Sawyers "**is** on this project's shelf". |

## Findings

Format: location · issue · severity · suggested fix · checkable against a source.

1. **detector_history.md:466 (unit 1), held? cell "1973 **no copy found**"**
   - **Issue:** "1973" has no referent in the row. The attribution cell names no 1973 work, so the reader meets a year with nothing attached.
   - **Severity:** major
   - **Fix:** "Hansen 1973 (see below): **no copy found**".
   - **Checkable:** yes (the table itself)

2. **detector_history.md:466 (unit 1), "The loss analysis is Hansen & Sawyers"**
   - **Issue:** "loss" is undefined at this point (a loss of what?). "CFAR loss" is not defined until §5.1, around line 578.
   - **Severity:** minor
   - **Fix:** "The analysis of what greatest-of costs in sensitivity is Hansen & Sawyers…"
   - **Checkable:** yes

3. **detector_history.md:466 (unit 1), "CAGO-CFAR"**
   - **Issue:** GO is never spelled out. A reader has to guess CA + GO from the row above.
   - **Severity:** minor (it was already there, but it counts toward this row's blocking verdict)
   - **Fix:** "greatest-of (cell-averaging greatest-of, CAGO-CFAR)".
   - **Checkable:** yes

4. **detector_history.md:473, "All four primaries are now held and read"**, right after unit 1
   - **Issue:** A cold reader has just seen "1973 no copy found" and "not established". "All four … held" now reads as a contradiction, because nothing says which four. The sentence is outside the diff, but the new row is what makes it contradictory.
   - **Severity:** major
   - **Fix:** Name the four (Finn & Johnson, Hansen & Sawyers, Rohling, Gandhi & Kassam) and add "the 1973 Hansen paper is not among them; see below".
   - **Checkable:** yes

5. **detector_history.md:483–484 (unit 2), "The work usually credited is…"**
   - **Issue:** "Usually" names no one who does the crediting. The bullets underneath show one source crediting Hansen with a CFAR procedure (Gandhi & Kassam) and one that does not cite the 1973 paper (Rohling). A reader will take "usually credited" as settled consensus, which the passage does not show and the brief tells us not to assert. Whether the evidence is enough is agent 4's call; mine is that the word has no referent.
   - **Severity:** major
   - **Fix:** "The work this document previously credited, following the interface2 audit, is…" or "The work Gandhi & Kassam 1988 cite for it is…"
   - **Checkable:** yes

6. **detector_history.md:483 (unit 2), lead sentence**
   - **Issue:** "Greatest-of" is used as a noun before the paragraph that explains it ("`maxlt` is greatest-of selection", line 521), which comes after this passage.
   - **Severity:** minor
   - **Fix:** Add a clause: "Where greatest-of selection (taking the larger of the two half-window background estimates) began…". Or move this passage below the `maxlt` paragraph.
   - **Checkable:** yes

7. **detector_history.md:485, 488 (unit 2), "IEE Conference Publication" and "IEEE Xplore does not index this IEE volume"**
   - **Issue:** Putting IEE right next to IEEE makes it look like a typo. Nothing says IEE is a different body.
   - **Severity:** major for this audience, because a careful reader will "correct" it.
   - **Fix:** At first use: "the Institution of Electrical Engineers (IEE, the UK body, now the IET; not the IEEE)".
   - **Checkable:** yes (external)

8. **detector_history.md:494–496 (unit 2), quoted "detectability loss" and "leading and lagging sets of reference cells"**
   - **Issue:** "Detectability loss" is undefined. "Lagging" is the source's word, but the table on line 466 says "trailing", so a reader may think two different things are meant.
   - **Severity:** minor
   - **Fix:** Add a gloss after the quote: "(the extra signal strength greatest-of needs to detect as well as plain cell-averaging; 'lagging' is the table's trailing half-window)".
   - **Checkable:** yes

9. **detector_history.md:498–499 (unit 2), memo title "'Conventional' and 'Split' mean level threshold detectors"**
   - **Issue:** "Mean level" and "Split" are undefined. The bullet's whole point is that a split mean-level detector *is* the greatest-of structure, but the text never says so. It only says the 1980 paper "derives greatest-of's detection performance from it". A cold reader cannot see why a 1972 memo on "split" detectors matters.
   - **Severity:** major
   - **Fix:** Add one sentence: "A split detector averages the leading and trailing halves separately, which is the structure greatest-of selection chooses between; 'mean level' is the radar term for a background estimate built by averaging."
   - **Checkable:** yes (against the 1980 paper, §I)

10. **detector_history.md:514–516 (unit 2), "Siebert and Dicke-Fix detectors", "LOG/CFAR receiver"**
    - **Issue:** Three technical names that are never defined and not needed. The point is only that Hansen had earlier CFAR papers nobody here has read. The names add three undefined terms and nothing else.
    - **Severity:** minor (they push this unit's undefined count up)
    - **Fix:** Drop the subject clauses ("Hansen's two earlier CFAR papers, with Zottl in 1971 and with Ward in 1972, neither on the shelf"), or gloss each one briefly.
    - **Checkable:** yes

11. **detector_history.md:491, 511 (unit 2), "What the papers we hold say about it" and "its author's one-sentence description"**
    - **Issue:** "It" could mean the 1973 paper or the question of where greatest-of began. The Rohling bullet is about the second. "Its author's one-sentence description" makes the reader connect Hansen with the 1980 bullet themselves.
    - **Severity:** minor
    - **Fix:** "What the papers we hold say about the 1973 paper and about greatest-of's origin". And "beyond Hansen's own one-sentence description of it in 1980".
    - **Checkable:** yes

12. **detector_history.md:518 (unit 2), "the attribution cell for `maxlt`"**
    - **Issue:** A code identifier in reader-facing prose.
    - **Severity:** minor
    - **Fix:** "the attribution cell for LoCo's greatest-of rule".
    - **Checkable:** yes

13. **detector_history.md:204–206 (unit 3), "GO-CFAR (Hansen 1973 — ⚠ *2026-09-14: no copy …*)"**
    - **Issue:** The parenthesis still starts with a citation that reads as the origin, and only then takes it back, inside nested dash, flag, date and italics. A skimming reader keeps "Hansen 1973". GO is never linked to "greatest-of". This is also the first appearance of `maxlt` and `loco_detect` in the document, and CFAR has not been spelled out yet.
    - **Severity:** major for the flag's structure; the undefined identifiers were already there.
    - **Fix:** Strike through the old citation in the dated note, as the document does elsewhere with ~~ ~~, e.g. "GO-CFAR (greatest-of CFAR; ~~Hansen 1973~~ ⚠ 2026-09-14: origin not established, §4)". Optionally add a first-use gloss: "LoCo's greatest-of rule (`maxlt`)".
    - **Checkable:** yes

14. **GLOSSARY.md:260–265 (unit 4), "an interface2 audit … closed every lineage row — … `maxlt` is GO-CFAR (where greatest-of began could not be established …)"**
    - **Issue:** The same sentence says every row was closed and then that one could not be established. A cold reader stops at the contradiction.
    - **Severity:** major
    - **Fix:** "closed every lineage row except the origin of greatest-of, which could not be established (detector_history.md §4)".
    - **Checkable:** yes

15. **GLOSSARY.md:262–265 (unit 4), new parenthesis breaks the list pattern**
    - **Issue:** The three items read cited name, sentence, cited name. "And its percentile-of-pool" now sits about 30 words after "`loco_detect`'s `maxlt`", so "its" could mean LoCo, `maxlt` or GO-CFAR.
    - **Severity:** minor
    - **Fix:** Move the not-established note to its own sentence after the list, and use "LoCo's percentile-of-pool" instead of "its".
    - **Checkable:** yes

16. **GLOSSARY.md:262, 265 (unit 4), "GO-CFAR" and "OS-CFAR"**
    - **Issue:** GO and OS are never spelled out anywhere in the glossary. The bullet on line 296 defines "greatest-of / ordered-statistic" but never connects them to the abbreviations.
    - **Severity:** minor (already there)
    - **Fix:** Change the bullet to "**greatest-of (GO) / ordered-statistic (OS) selection**".
    - **Checkable:** yes

17. **README.md:653 (unit 5), "LoCo's `maxlt` is greatest-of CFAR."**
    - **Issue:** A code identifier the README never explains. "Greatest-of" is undefined, and CFAR is never spelled out in the README (line 641 says "constant-false-alarm property" but never connects it to the abbreviation). The audience is hiring and grant readers.
    - **Severity:** major (already there, but this unit is under review and its new sentences depend on it)
    - **Fix:** "LoCo's rule of taking the larger of its trailing and leading background estimates is greatest-of selection in constant false alarm rate (CFAR) detection."
    - **Checkable:** yes

18. **README.md:654 (unit 5), "Its detectability cost"**
    - **Issue:** A relative word with no referent: cost compared with what, and in what?
    - **Severity:** minor
    - **Fix:** "Its small sensitivity cost relative to plain cell-averaging is measured in…"
    - **Checkable:** yes (against the 1980 paper)

19. **README.md:658–659 (unit 5), "a 1972 internal memo … already analysed the same split detector"**
    - **Issue:** "Split detector" is undefined, and "the same" points at nothing. The README never said greatest-of is a split detector. The memo's author and organisation are left out, which the reader may need for a follow-up search.
    - **Severity:** major (new in this change)
    - **Fix:** "a 1972 internal Hughes Aircraft memo by Sawyers, cited in the 1980 paper, already analysed a detector that splits the reference window into leading and trailing halves".
    - **Checkable:** yes

20. **README.md:657 (unit 5), "IEE Conf. Publ. 105"** right after "IEEE T-AES"
    - **Issue:** Reads as a typo to a cold reader.
    - **Severity:** minor
    - **Fix:** "Institution of Electrical Engineers (IEE) Conf. Publ. 105".
    - **Checkable:** yes (external)

21. **README.md:634–636 against 655 (unit 5), shelf contradiction**
    - **Issue:** The intro to the list says "this project's shelf holds only Finn & Johnson of the works below", but the bullet says Hansen & Sawyers "**is** on this project's shelf". The 1973 paper is not held yet carries no ° mark, so a reader cannot tell whether a missing ° means "read here". Mostly already there, but unit 5 is where the reader runs into it.
    - **Severity:** major
    - **Fix:** Change the intro to "holds only Finn & Johnson and Hansen & Sawyers". Either give the 1973 entry a ° or say in the ° legend that unmarked-but-unfound works are called out in the text.
    - **Checkable:** yes

22. **README.md:646–661 (unit 5), a citation list with no citation instruction for greatest-of**
    - **Issue:** This section opens "Cite in any publication…". Someone skimming for what to cite now reads "not established" and gets no guidance, so they are left without an answer.
    - **Severity:** minor
    - **Fix:** One clause that makes no claim about origin: "for greatest-of, cite the 1980 analysis; no origin can be cited".
    - **Checkable:** no (editorial)

## Where these need adjudication

- **Rows 3 and 4 of the verdict table** reach "blocking" mostly on terms that were already in the text. The terms this change adds are "greatest-of" (unit 3) and "could not be established" against "closed every lineage row" (unit 4). The smallest fixes within the change are findings 13 and 14.
- **Rows 1, 2 and 5** are blocking mainly because of text this change adds: the "1973" and "loss" referents in the table, the IEE/split/mean-level/Siebert vocabulary in §4, and "split detector" in the README. Each fix is a clause, and none of them adds a new claim about where greatest-of began.

Files read:
- <worktree>\docs\detector_history.md
- <worktree>\docs\GLOSSARY.md
- <worktree>\README.md
- <scratchpad>\go_diff.patch
