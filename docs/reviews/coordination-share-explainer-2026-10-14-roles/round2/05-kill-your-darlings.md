GRANT 5 ok — Read, Grep, Glob

(SubagentHandback is only how this report gets back to you. It is not an editing tool. I hold no Edit, Write or NotebookEdit.)

**Artifact:** `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md` (281 lines). House rules read: CLAUDE.md "Writing for a human reader" and `docs/writing_conventions.md`.

## Tool status
`murderboard_prose.sh` is not available on this machine, so the "count first" step was **not run as specified**. In its place I ran Grep searches against the artifact. The word and sentence counts per block below are **my estimates**, not tool output.

**Lists run:**
- **(a) The murderboard banned list from doc_review_process.md role 5:**
  - not just / not only
  - it's not about
  - worth noting
  - delve, leverag, robust, seamless, crucial, landscape, tapestr
  - in today's
  - em-dash
- **(b) House additions from CLAUDE.md:**
  - fire / fires / fired / firing (SAP017)
  - data is / was / has / shows / itself (SAP015)
  - British spellings: centre, -our, -ise, analys, round, grey, labelled
- **(c) A "not … but" pivot regex**, plus "X, not Y" contrasts.

## Hits table (pasted from Grep)

| line | construction | kind |
|---|---|---|
| — | list (a): **no matches** | banned list clean |
| — | fire*/data-singular: **no matches** | house rules clean |
| 11, 15, 19 | "grey" | British spelling (house: American) |
| 83 | "wrapping round" | British idiom |
| 101 | "it analyses together" (verb) | British spelling |
| 182 | "It is how fast the rate changes that matters, not how long…" | cleft contrast, close cousin of "it's not about A, it's about B" |
| 62, 79, 139, 204 | "X, not Y" headings and sentences | contrast form; allowed, noted for density only |

**Other mechanical counts:**
- "bench": 22 uses (first at line 11), **never defined**.
- "Tony": lines 226 and 232.
- "events" in the sense of shared moments: lines 145, 222 and 230.

## Findings
Columns: location · issue · severity · fix · verified against a source.

1. **11 onward (22 uses) · "the bench" is never defined.** It carries most of the argument from line 118 onward, for a reader the brief says is not math-oriented. **High.** Add a Terms entry: "Bench: the project's set of simulated recordings with known planted moments, used to check detectors." **Verified: yes** (Grep).

2. **3–19 against 45–58 · symbols are used before they are defined.** The captions use *X*, *f*₂, *f*₃, "shifted copy", "pass band", "fixed/binomial model", "busy background" and "stretch". All are defined only further down. The layout ADR puts figures first, so the conflict is structural. **Medium.** Either gloss each in its caption ("*f*₂, pairs beyond chance") or add one caption line: "symbols: see Terms." **Verified: yes.** Boundary: roles 8 and 10 may also flag this.

3. **One quantity has several names:**
   - *k* is also "cells per moment" (96), "participants per moment" (157, 165, Fig. 4B) and "moment size" (128).
   - λ is also "how often" (55, 97) and "moments per minute" (158, 165).

   "Participants per moment" and "moments per minute" are never tied to *k* and λ. **Medium.** Pick one plain name for each, and put it beside the symbol in Terms. **Verified: yes.**

4. **145, 222, 230 · "events" means shared moments here.** Line 48 makes an event a single cell's calcium event, and "events 2 s apart" or "about 7 events per 45 minutes" reads as per-cell events. **Medium.** Use "moments". **Verified: yes.**

5. **86 · ambiguity.** "every cell has the same number of ticks" can be read as "all cells have equal counts". **Medium.** Fix: "each cell keeps the number of ticks it had in Figure 1B". **Verified: yes.**

6. **83–84 · unclear phrasing.** "with every two cells' amounts at least two windows apart" does not parse easily. **Medium.** Fix: "no two cells are slid by amounts within two windows of each other". **Verified: no** (wording only).

7. **147–148 · the text contradicts itself.** "each recording in a set carries 2 pairs of moments closer together" is false for the mixed set, which has 4 pairs (lines 226–229 say so). **Medium.** Fix: "carries 2 pairs (the mixed set, 4) of moments closer together". **Verified: yes,** against the doc's own lines 226–229.

8. **144–146 · compressed inference.** "measured after merging any two events less than 2 s apart. So the closest moments real recordings hold are the ones the bench never plants." The "So" skips a step. **Medium.** Fix: "Because events under 2 s apart were merged before measuring, no interval shorter than 2 s can be drawn, so the bench never plants the closest moments real recordings hold." **Verified: no.**

9. **182 · the bold payload contradicts the numbers in its own bullet.** "how long the change lasts" does not matter, yet the share falls from 8% to 3% to 1.2% as length grows, and Figure 5A is plotted by length. It also uses the near-banned cleft form. **High.** Fix: "What is counted is the switching on and off; a longer stretch spreads that over more onsets, so its share is smaller." **Verified: yes** (lines 180–182).

10. **116 and 137 · the same statement twice, 21 lines apart.** "The tool adopts the fixed model" appears at both, with the reason only at the second. **Medium.** Put the reason (137–139) at 116 and delete it at 137.

11. **132–133 and 139–140 · the same claim twice.** "How low it reads depends on how much moment sizes vary…" is restated as "by an amount that depends on how much the moment sizes vary". **Low.** Keep one, the closing instruction at 139.

12. **167–168 · misplaced sentence.** The binomial-model result for the share is stranded at the end of a paragraph about *k* and λ. **Low.** Move it to the end of the "share hardly moves" bullet (151).

13. **38–39 · ambiguity.** "the share … that are coordinated, against the overall event rate" could mean the share is computed relative to the rate or plotted against it. **Medium.** Say which. **Verified: no.**

14. **38 · undefined term.** "`fireflies`" means nothing to an outside reader. **Medium.** Fix: "the project's group-comparison analysis (`fireflies`)".

15. **226, 231–232 · names and dates used as lookup keys.** "(Tony, 2026-10-14)" and "waiting on Tony" in a public explainer give an outside reader a name and a date without meaning; this breaks the writing_conventions rule "Shas and dates are lookup keys". Line 144 has the same problem with "since 2026-10-07". **Low.** Fix: "chosen for this page"; "awaits a decision on the revised bench"; "the current bench". **Verified: yes** (writing_conventions.md lines 30–42).

16. **256–263 · internal jargon.**
    - "default export", "`senktide_ttx`", "contamination stop", "producer" are undefined.
    - The payload, "Pinned cells show events at the same moments, which is exactly what this measure counts," sits at line 261, sixth of eight lines.

    **Medium.** Lead with the payload, and replace "producer" with "the lab's export pipeline". **Verified: no.**

17. **239, 248 · undefined terms.** "cumulants" and "factorial cumulants" are not defined for this audience. **Medium.** Fix: "*f*₂ and *f*₃ are what statisticians call factorial cumulants". **Verified: no.**

18. **246 · definition by negation.** "which this tool's shift is not" tells the reader what the shift is not, and not how it differs. **Low.** Fix: one clause ("…is not: there all cells move together"), if that is the distinction. **Verified: no.**

19. **198–199 · throat-clearing.** "Figure 6, how far one recording strays, shows how far that answer can be from the truth, for one recording" repeats the heading three times over. **Low.** Cut to "The tool reports a share for each recording; Figure 6 shows how far it can miss."

20. **208–209 · same phrase, two meanings in one bullet.** "on its own" first means "alone" (a lower rate on its own) and then means "each recording's own ratio" (0.74 to 0.95 on its own). **Low.** Change the second to "each recording's own ratio".

21. **201 · the bold claim overstates.** "Fewer shared moments, more spread": the 80% range is 0.39 wide with 6 moments and 0.33 with 3, so spread does not keep rising. **Low.** Soften to "With few shared moments, much more spread". **Verified: yes,** against the doc's own numbers. Accuracy belongs to role 4.

22. **212–214 · the block asserts nothing the reader needs.** It says the eligibility limits did not apply. "shorter than 300 s, with fewer than 20 onsets or fewer than 5 cells" is also ambiguous between and/or. **Low.** Move it to For developers (next to `shape_usable`) or cut it.

23. **176–177 · confusing arithmetic.** "0.1334 onsets per second … about 27 times the quiet background, so 28 times in all" makes the reader do the sum, and 4 significant figures is false precision for this reader. **Low.** Fix: "every cell's rate rises to about 28 times the quiet background". Line 177 also overruns the wrap width.

24. **183 · undefined term.** "30 s ramps" is used without definition, and it contrasts silently with "switches on and off sharply" (177). **Low.** Add: "rising and falling over 30 s, unlike panel A's sharp switch".

25. **218–221 · one sentence of about 60 words with four semicolons.** "(0.0169)" has no unit (CLAUDE.md: every number carries its unit). **Low.** Split it into 3 sentences and add "onsets per second per cell".

26. **11, 15, 19; 83; 101 · American English house rule.** "grey" should be "gray" (it may also need changing in the figure generator; see the conventions' figure-label note), "wrapping round" should be "wrapping around", and "analyses" (verb) should be "analyzes". **Low.** **Verified: yes** (writing_conventions.md "American English").

27. **234 · axis notation in prose.** "30m to 35m" is axis-label shorthand. **Low.** Fix: "minutes 30 to 35".

28. **33 · throat-clearing.** "What it does count as coordination, implicitly, is this:" **Low.** Fix: "Implicitly, it counts as coordination:"

29. **279–280 · will go stale.** "(written when the review finishes)" will be false the day the review lands. **Low.** Remove it when the record is linked.

30. **3 · inconsistent caption punctuation.** "A, the lane…" against "B:", "C:", "D:". **Low.** Use "A:" throughout.

## Passage test, per block
Columns: block · ~words / sentences (my estimate) · payload · where the payload sits · what the rest buys.

- **Captions 3–23** · 40–90 words each · legends · not applicable · they are legends; see finding 2.
- **31–36** · ~85 / 4 · bold implicit definition · middle · the opening question earns its place; "What it does count…is this:" does not (finding 28).
- **38–40** · ~45 / 2 · fireflies will use it; baseline only for now · start · fine apart from findings 13 and 14.
- **42–43** · 2 sentences · all simulated · start · fine.
- **Terms 45–58** · fine; missing bench, participants per moment and moments per minute (findings 1 and 3).
- **64–66** · ~45 / 2 · X is the count per window · start · the half-window detail earns its place because line 131 relies on it.
- **68–71** · ~60 / 4 · sharing shows as spread · middle · the Figure 2A numbers are the evidence; keep.
- **73–77** · ~75 / 3 · f₂ and f₃ measure the excess · start · the 90-vs-720 example is good and earns its place.
- **81–86** · ~95 / 6 · the slide keeps each cell's rhythm and destroys same-time onsets · middle · fine; fix findings 5 and 6.
- **88–91** · ~50 / 3 · subtract; the excess is left · end · fine.
- **95–98** · ~65 / 4 · the share comes from k, λ and rate · end, bolded · fine.
- **100–102** · ~45 / 3 · the ratio is pooled · middle · fine.
- **108–110** · fine.
- **112–116** · ~65 / 5 · cannot tell the models apart; fixed is adopted · end · weakened by finding 10.
- **118–126** · bullets · fine.
- **128–135** · ~120 / 7 · "fixed reads low by an unknown amount that depends on size variation" · middle and again in the next block · the two mechanisms are evidence; the restatement is padding (finding 11).
- **137–140** · ~60 / 3 · payload at the end (read as an underestimate) · end · merge into 112–116.
- **144–149** · ~90 / 4 · the new sets plant the close spacings the bench lacks · second sentence · the date and the 41 s median are context a sceptic might want; fix findings 7, 8 and 15.
- **151–156** · ~95 / 4 · the share is stable unless moments are closer than a window · start, bolded · the long inventory sentence at 151–153 is thoroughness; it could be "14–19% low for all but sub-window pairs".
- **157–161** · ~75 / 4 · k and λ move a lot · start · the mechanism earns its place.
- **162–163, 165–168** · see finding 12.
- **175–182** · ~125 / 6 · "a field-wide rise is counted at its switch-on and switch-off" · start; the closing bold sentence contradicts it (finding 9) · the 8 / 3 / 1.2% evidence earns its place.
- **183–185, 186–189, 190, 191–194** · fine, with findings 23 and 24.
- **198–199** · padding (finding 19).
- **201–210** · bullets · fine, with findings 20 and 21.
- **212–214** · ~45 / 2 · no payload for the reader (finding 22).
- **218–224** · ~105 / 2 · how the simulations are built · fine content; split (finding 25).
- **226–232** · ~95 / 4 · the mixed set's layout · start · the Tony references are internal (finding 15).
- **234–235** · fine.
- **239–246** · ~110 / 4 · the method is CuBIC-family · start · citations are evidence; keep.
- **248–252** · ~65 / 2 · what is new here · start · fine.
- **256–263** · ~115 / 5 · numbers withheld because pinned cells mimic coordination · **sixth of eight lines; promote it** (finding 16).
- **264–265** · fine.
- **For developers** · fine.

**Highest-value repairs:**
- the undefined "bench" (finding 1)
- the closing sentence of Figure 5's first bullet, which contradicts its own numbers (finding 9)
- the k/λ name drift (finding 3)
- the false "2 pairs" claim at line 148 (finding 7)
