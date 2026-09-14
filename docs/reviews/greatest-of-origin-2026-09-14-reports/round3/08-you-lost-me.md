GRANT 8 ok — Read, Grep, Glob

I read all 8 units cold, in the worktree `<worktree>`, alongside the diff `...\scratchpad\go_diff_r3.patch`. For each unit I counted only what the document had defined before that point. In `detector_history.md` that means the top revision notes, §3 (which defines CFAR, reference cells, cell under test, guard cells and clutter edges) and §4. I opened nothing under `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`.

**Figure checks:** none of the units contains a chart or panel, so the misleading-look-alike-chart check and the per-panel "what a stranger sees" check had nothing to act on. One edited string outside the units does show up in a rendered panel (finding F20). I have no rendering tool, so I traced it through the page's JavaScript instead of looking at it.

**Blocking rule:** I applied it literally. A unit where three or more undefined terms first appear is blocking. The Origin column says whether this change caused that, so you can decide.

## Verdict for each unit

| # | Unit | Terms and identifiers first used here | Defined here? | Can a stranger follow it? | Origin |
|---|---|---|---|---|---|
| 1 | §4 table row "LoCo, `maxlt`" | "greatest-of (GO) selection"; "loss analysis"; "the cell-averaging form"; *IEEE T-AES* | GO yes, through the mechanism column. "Loss" no: its first definition in the document is §5.1, later. "Cell-averaging form" has no referent. *T-AES* no, but it is only a citation. | **No (major).** Two undefined terms, and it is unclear what "read in full" refers to. | "Loss analysis", "cell-averaging form" and the unclear "held?" cell are new. *T-AES* was already there. |
| 2 | Paragraph after the table ("Four of the table's papers…") | "shelf"; `<darkroom>`; "read-status entry"; `tools/verify_quotes.py`; "traces"; "does not block anything"; "Tony" | None of them | **Blocking.** Seven undefined. | The `verify_quotes.py` sentence is new. Shelf, darkroom, read-status and Tony were already there. |
| 3 | §4.1 Where greatest-of began | "the IEE's notice" (used before it is explained); "search-only scan"; "IET Digital Library" (IET's link to IEE is not given); "detectability loss"; "'Conventional' and 'Split' mean level threshold detectors"; "loss curves"; "Weibull clutter"; "Goldstein's 1973 Weibull processor"; "CAGO CFAR"; "lagging windows" | IEE yes. The "notice" is explained one paragraph later. The rest no. | **Blocking.** About ten undefined. Two inferences depend on steps the text never states: why the memo counts as a treatment of greatest-of, and why the acknowledgment is quoted. | All new |
| 4a | ⚠ sentence in the "Revised 2026-08-24" note | "greatest-of", its first appearance in the document; the sentence before it says "GO-CFAR" | No. Nothing tells the reader that GO means greatest-of. | **Mostly.** The switch in wording breaks the link to the claim it corrects. | New |
| 4b | ⚠ sentence in §7 item 2 | "this check"; "the 1980 loss analysis"; "could not tell the two apart" | "This check" and the 1980 paper yes, from the item. "Could not tell the two apart" has no clear subject or meaning. | **No (major).** | New |
| 5 | GLOSSARY, CFAR vocabulary paragraph | "a reading"; "lineage row"; "OS-CFAR" and "greatest-of selection" (both before the list defines them); "percentile-of-pool"; "this project's own priority is closed"; `rate_detect`, `loco_detect`, `maxlt` | GO and OS are defined in the list below. Lineage row, percentile-of-pool and "priority is closed" are not. | **Blocking.** Three undefined, plus a contradiction a stranger will notice (F12). | The contradiction and "own priority" are new. Lineage row, percentile-of-pool and the jump ahead of the list were already there. |
| 6 | README, LoCo and CoactDetect bullet | `maxlt`; "half-window" (half of which window?); "detection loss"; "plain cell-averaging"; *IEEE T-AES* | CFAR is expanded here, and greatest-of is explained in the text. The other four are not defined. | **Blocking.** Four undefined. | "Half-window" and "detection loss" are new. `maxlt`, cell-averaging (undefined in the bullet above too) and *T-AES* were already there. |
| 7 | `cfar_scope.html` intro above the table, and the "LoCo · maxlt" row | "LoCo"; "maxlt"; "origin" (the page has never claimed one); "loss:" | "Loss" has a referent in the card above (Hansen & Sawyers' extra loss). LoCo and maxlt are never defined on the page. | **Blocking**, but because of material already there (LoCo, maxlt, and the other detector names in the table). The change adds only minor issues. | "Origin" in the intro and "origin/loss" in the source column are new. The detector names were already there. |
| 8 | Proposal footer correction | "greatest-of selection" (the body says "greatest-of CFAR"); the path "docs/detector_history.md §4.1" | Mostly yes | **Yes, with minor issues** | New |

## Findings

Columns: location · issue · severity · suggested fix · checkable against a source?

**Blocking**

- **F1.** detector_history §4.1, Hansen & Sawyers bullet · **Blocking** · Checkable: yes (Hansen & Sawyers 1980 text on the shelf)
  - **Issue:** The text calls the 1972 Sawyers memo "the earliest dated treatment of greatest-of in the sources we hold". The memo's title only says "'Conventional' and 'Split' mean level threshold detectors". Nothing tells a stranger that "mean level" means cell-averaging or that "split" means greatest-of, so they cannot see why the memo is about greatest-of. The claim that most affects the origin question rests on a step the text leaves out.
  - **Fix:** Add one clause with a source, for example: "(Hansen & Sawyers use 'split' for greatest-of selection and 'conventional' for plain cell-averaging)". If the paper does not say that, remove the "earliest dated treatment" sentence.
- **F2.** detector_history §4.1, whole subsection · **Blocking** · Checkable: yes
  - **Issue:** About ten radar or library terms appear once and are never defined: detectability loss, loss curves, Weibull clutter, Goldstein's Weibull processor, CAGO CFAR, lagging windows, search-only scan, IET, and the IEE "notice" (used before it is explained).
  - **Fix:**
    - Add short glosses: detectability loss is how much stronger a target must be to be detected as reliably as with a perfectly known background; CAGO is cell-averaging with greatest-of; lagging means trailing; Weibull clutter is background whose amplitude follows a Weibull distribution; IET is the successor to the IEE.
    - Change "the IEE's notice" to "a notice in the IEE's journal (below)".
    - Change "search-only scan" to "scanned, searchable but not viewable".
    - Either cite Goldstein 1973 or drop the name.
- **F3.** detector_history paragraph after the §4 table · **Blocking** · Checkable: no
  - **Issue:** "`tools/verify_quotes.py` traces some of them automatically and does not block anything" puts a code path in reader-facing prose and uses two jargon verbs, "traces" and "block", without saying block what. The paragraph also uses shelf, `<darkroom>` and read-status entry, which were already undefined.
  - **Fix:** Write "a script matches some of them to the PDF text automatically; a mismatch is reported but does not stop a change from being merged." Give "shelf" one gloss on first use, for example "the project's collection of retrieved papers".
- **F4.** README LoCo and CoactDetect bullet · **Blocking** (by count) · Checkable: yes
  - **Issue:** "Two local thresholds, one from the trailing and one from the leading half-window" never says what the window is. "Detection loss" and "plain cell-averaging" are undefined. `maxlt` is a code name in a citation block read by outsiders.
  - **Fix:**
    - Write "the context window before and after the moment being tested".
    - Write "detection loss (how much stronger an event must be to be found equally often)".
    - Write "plain cell-averaging (averaging the whole window)".
    - Name the option once in plain words, for example "LoCo's split-window mode (`maxlt`)".
- **F5.** GLOSSARY CFAR vocabulary paragraph · **Blocking** (by count; mostly already there) · Checkable: no
  - **Issue:** "Lineage row", "percentile-of-pool" and "this project's own priority is closed" are undefined. The added word "own" makes "priority" read like task ranking rather than scientific priority.
  - **Fix:** Write "which detector traces to which published method", "its 99.9th-percentile threshold on the pooled surrogate null" and "the question of who got there first is settled".

**Major**

- **F6.** §4 table, LoCo `maxlt` row, attribution cell · **Major** · Checkable: yes
  - **Issue:** "Loss analysis of the cell-averaging form" has no referent. It reads as an analysis of plain CA-CFAR, which is the previous row, when the paper analyses cell-averaging with greatest-of. The change removed the old "CAGO" label that at least pointed at the right thing. "Loss" is not defined until §5.1.
  - **Fix:** Write "detection-loss analysis of greatest-of with averaged halves".
- **F7.** §4 table, same row, "held?" cell · **Major** · Checkable: yes
  - **Issue:** The attribution cell now names two things, an origin that is "not established" and the 1980 paper. "Read in full" in the next cell reads as if it covers both.
  - **Fix:** Write "Hansen & Sawyers: read in full; origin: —".
- **F8.** §7 item 2 ⚠ sentence · **Major** · Checkable: no
  - **Issue:** In "…and could not tell the two apart", the subject and meaning are unclear. It could mean the papers are indistinguishable, or that the check confused them. It also comes straight after the unqualified "All four primaries are read."
  - **Fix:** Write "the check read the 1980 loss analysis and counted it as confirming the 1973 credit, which it cannot do: the 1980 paper cites the 1973 one but is not it."
- **F9.** Revision note ⚠ (4a) · **Major** · Checkable: no
  - **Issue:** The sentence being corrected says "GO-CFAR (Hansen 1973)", and the correction switches to "greatest-of". A reader at the top of the document, before §3 and §4, has no way to connect the two. The note also still ends by saying the CFAR mapping has "become the attribution", and the ⚠ does not say whether that conclusion survives.
  - **Fix:** Write "the Hansen 1973 credit for GO (greatest-of) CFAR is withdrawn…". Add "the mechanism mapping stands; this one origin credit does not."
- **F10.** §4.1 Hansen & Sawyers bullet, acknowledgment sentence · **Major** · Checkable: yes
  - **Issue:** The quote "derived from independent work performed by the two authors" is given with no statement of what it bears on. A stranger cannot tell why it is there, and may fill the gap with an origin story the brief forbids.
  - **Fix:** Say in one neutral clause what it shows, for example that the paper describes its results as coming from separate work by each author. Otherwise remove it.
- **F11.** §4.1 search paragraph · **Major** · Checkable: yes
  - **Issue:**
    - The two ISBNs are reported with no reason given for why the mismatch matters.
    - Neither the IET's link to the IEE nor the reason a stranger would look there is given.
    - "This project's automated tools" is vague.
  - **Fix:** Add "the IET, the IEE's successor, which holds its archive". Say what the ISBN mismatch affects, for example ordering the right volume through a library. Name the limitation, for example "blocked to scripted access".
- **F12.** GLOSSARY paragraph logic as read · **Major** · Checkable: no
  - **Issue:** It says the old "flagged unverified" wording "stopped being true" because the mechanisms were identified. It then ends by saying greatest-of's origin is not established, which is an unverified attribution again. A stranger reads a contradiction. The change caused this by replacing "closed every lineage row" with "identified the mechanism", which no longer supports "stopped being true".
  - **Fix:** Separate the two claims: "the mechanisms are now identified; the attributions are verified except one, where greatest-of began (§4.1)."

**Minor**

- **F13.** §4.1 first paragraph · **Minor** · Checkable: yes
  - **Issue:** A two-line aside about the author's name ("GREGERS HANSEN, V.", V.G. Hansen) sits between "a 1973 paper by" and the title. It does not say why the name matters.
  - **Fix:** Move the aside after the title, or into the search paragraph, with its reason: it affects catalogue searches.
- **F14.** §4.1 "What the sources we hold say" · **Minor** · Checkable: yes
  - **Issue:** The list includes the patent, which the bullet itself says is not on the shelf, so "sources we hold" is wrong for one item.
  - **Fix:** Write "What the sources we have read say".
- **F15.** §4.1 Gandhi & Kassam bullet · **Minor** · Checkable: yes
  - **Issue:** "Lagging" is used where §4 says "trailing". The point of "names the venue as an IEEE conference" (it conflicts with the IEE venue stated above) is left for the reader to work out.
  - **Fix:** Write "leading and lagging (trailing) windows". Add "unlike the IEE notice".
- **F16.** Paragraph after the table · **Minor** · Checkable: yes
  - **Issue:** "Radar quotations are checked … against text extracted from those PDFs", but §4.1 now quotes a patent from Google Patents. The Sources entry mentions that exception; this paragraph does not.
  - **Fix:** Add "(except the patent quotations in §4.1)".
- **F17.** README bullet · **Minor** · Checkable: no
  - **Issue:** "This README no longer cites…" addresses someone who read an earlier version. A first-time reader has no referent for "no longer".
  - **Fix:** Write "Earlier versions of this README cited a 1973 Hansen conference paper as the origin; that credit is withdrawn."
- **F18.** cfar_scope.html intro · **Minor** · Checkable: no
  - **Issue:** "§4.1 records that greatest-of's origin is not established" appears on a page that never claimed an origin. The "source" column still lists Finn & Johnson 1968 and Rohling 1983 as if they were origins, so the clause raises a question it does not answer. The file path is plain bold text, not a link (this was already the case).
  - **Fix:** Write "the source column names papers that describe each variant; where greatest-of began is not established (detector_history §4.1)". Make the path a link.
- **F19.** cfar_scope.html LoCo · maxlt row · **Minor** · Checkable: no
  - **Issue:** "origin not established; loss: Hansen & Sawyers 1980" is too terse. "Loss:" works only for a reader who remembers the card above, and the cell mixes origin and analysis inside a column headed "source".
  - **Fix:** Write "origin unknown · extra-loss measurement: Hansen & Sawyers 1980".
- **F20.** cfar_scope.html line 382 (`VARIANTS` GO `cite`), outside the units · **Minor** (caused by this change) · Checkable: no (not rendered)
  - **Issue:** The new text "loss analysis: Hansen & Sawyers 1980" is drawn under the GO mini-panel (line 823). It also appears in the tooltip on the GO button. The mini-panels sit in the "Five bars over one record" section, above the card that first mentions a loss, so the reader has no referent for "loss" there. The CA panel beside it shows a bare citation, which reads as an origin, so the two captions imply different things.
  - **Fix:** Use the same wording as F19, or define the loss in the caption.
- **F21.** Proposal footer · **Minor** · Checkable: no
  - **Issue:** The original sentence credits Hansen 1973 for "the constant-false-alarm-rate family" and never says the credit was for greatest-of, so the correction's switch to "greatest-of selection" asks the reader to make the link. The body calls it "greatest-of CFAR". "docs/detector_history.md §4.1" is a repository path with no link, and a reader of the proposal cannot follow it.
  - **Fix:** Write "the credit to Hansen 1973 for greatest-of CFAR is withdrawn as unverified…". Link the path to the public repository URL.
- **F22.** §4 table rows compared · **Minor** (partly caused by this change) · Checkable: no
  - **Issue:** Neighbouring rows say "(CA-CFAR)" and "(OS-CFAR)", but this row now says "greatest-of (GO) selection". A stranger may wonder whether it is a different kind of thing. How the rows should match across files is agent 3's territory; I am noting only that a reader may stumble here.
  - **Fix:** Write "greatest-of (GO-CFAR)".

**Already there before this change:** F3's shelf and darkroom terms, F4's `maxlt` and cell-averaging, F5's lineage row and percentile-of-pool, F7-era "Tony", and F18's unlinked path. The undefined detector names on `cfar_scope.html` (LoCo, maxlt, rate+context, CoactDetect, binned SCE, CICADA) are what make unit 7 blocking, and they predate this change. "CFAR", "GO-CFAR" and "OS-CFAR" are also used in `detector_history.md`'s revision notes and the GLOSSARY paragraph before they are defined.

**Tone:** sentence case is consistent in every unit. "GREGERS HANSEN, V." is in capitals because it is quoted, and I did not flag it. No list items are packed into a title or legend.
