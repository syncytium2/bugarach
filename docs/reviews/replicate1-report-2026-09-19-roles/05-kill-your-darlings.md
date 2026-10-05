GRANT 5 ok — Read, Grep, Glob

**Role 5, line editor ("Kill Your Darlings"): blind verify, round 3 of 3**
Artifact: `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (hash 9a99a7a4). I read it by line offsets and Grep: every paragraph, list item, callout, figure caption, the Figure 1 key, table titles and cells, table notes, and the text inside the SVG figures. I checked one generated sentence against `tools/make_replicate_report.py`. I opened no earlier review reports.

## 0. The count tool did not run (a finding about the run)

- **Where:** the process, not the page.
- **Issue:** `murderboard_prose.sh` does not exist. I globbed for `murderboard_*` in both trees and found only `murderboard_agents.py`, `_freshness.sh`, `_revendor.py` and `_roster.sh`. My grant has no shell, so I could not have run it anyway. Under the checklist, "not run" is a failure, not a clean result. There is no pasted tool output below.
- **Substitute:**
  - I searched for the banned constructions with Grep, and the results are real.
  - The block word and sentence counts in section 2 are my hand estimates, labeled that way.
- **Severity:** major, for the run record.
- **Fix:** vendor or restore the script, or take the "run the tool" clause out of role 5's checklist. The run record's `roles:` line should say role 5's count step was done by hand.
- **Verified against a source:** yes (Glob).

## 1. Banned constructions

I ran the list exactly as it stands in the process file, unedited.

- **Clean:** delve, leverage, robust, seamless, crucial, landscape, tapestry, "worth noting", "not just / not only", "it's not about", "In today's". Zero hits.
- **Em dashes:** 17 hits. None pivots into an uplifting close. All are parentheticals or appositives (lines 83, 175–176, 191–192, 230, 237, 323–324, 396, 418–419), plus SVG tooltip text on line 263.
- **Three-item lists:** each lists three real things: the three reasons on line 80, the three pooled statistics on line 174, and the three scope limits on line 44.
- **Near-miss "X, not Y":** 6 instances, on lines 88, 124, 147, 169, 224 and 336. Each states a true contrast, so all stay.
- **British spellings:** none found (colour, favour, -ise, grey and similar).
- **"data" plural:** line 372, "the data say", is correct.

## 2. Hand counts and passage test (my estimates, not tool output)

Each block below gives its size, the one sentence it exists to deliver, and what the rest of the words buy.

- **"Why this report exists" (lines 46–51), ~100 words, 5 sentences.**
  - Payload: "one run cannot tell a lead of ~0.01 F1 from recording luck, so it was run twice." It sits in the middle.
  - The last sentence is a roadmap. The house voice bans previews.
  - The block also duplicates section 6 (see findings 6 and 13).
- **Figure 1 caption (line 85), ~140 words, 7 sentences.** Earns its length: every sentence is needed to read the figure. Two phrases are decoration (finding 16).
- **F1 paragraph (lines 117–124), ~115 words.** The payload ("practical ceiling 0.83, and a long merge can pass it") is at the end, where it is also ambiguous (finding 2).
- **Origins paragraph (lines 141–149), ~135 words.**
  - Payload never stated: "three coded detectors descend from published methods; three were designed here."
  - Fix: open with that sentence.
- **Reference paragraph (lines 150–160), ~150 words.** Earns its length. The merge setting is buried in a sentence about the guard interval (finding 18).
- **Section 4 inner fits (lines 194–203), ~150 words, 7 sentences.** Its counts contradict each other at the surface (finding 3).
- **Section 6 (lines 228–236), ~165 words.**
  - Payload is last: "the two runs differ only in seeds and draw number."
  - The first sentence repeats the intro and section 9.
  - Fix: promote the payload and cut the repeat.
- **Section 9, first paragraph (lines 290–301), ~190 words, 6 sentences.** Three points in one block:
  - the typical move between draws;
  - the rehearsal's lead is within that move;
  - the moves are correlated: the second draw favors the nets by 0.018.

  The third point is the one a reader loses. Fix: split it into its own paragraph.
- **"Where the as-run gap is" (lines 341–352), ~160 words.** The payload comes first ("It is in precision.") — good. The last sentence explains the internals of a score-file field (finding 20).
- **Blocks that pass:**
  - Section 10's limits bullets. The simulator-defect bullet is ~110 words and earns them.
  - Section 7 (lines 239–246), apart from finding 21.
  - Section 8: training, searches, held-out budget checks, and grid tops.
  - Matched merge, both paragraphs (lines 319–338).
  - The headline gap (lines 304–312). It is exemplary, and "which is what agreement should look like but not proof of it" is dry humour that is also true.

## 3. Findings

Format: location · issue · severity · suggested fix · verified against a source.

### Major

1. **Section 2, list item on line 106: "A dense stretch of 300 s (20–25 minutes)"**
   - Issue: two lines up, "2700 s (45 minutes)" is a unit conversion. So this one reads as "300 s = 20–25 minutes", when it means *from minute 20 to minute 25*.
   - Severity: major.
   - Fix: "of 300 s, from minute 20 to minute 25,".
   - Verified: yes (lines 96, 106).

2. **Section 2, lines 122–124: "as in Figure 1, so a long merge can pass that figure"**
   - Issue: "figure" means the number 0.83, right after "Figure 1". The reader parses it as the figure.
   - Severity: major.
   - Fix: "…so a long merge can score above 0.83; it is a practical ceiling…". Also give Figure 1 its name, per the house rule.
   - Verified: yes.

3. **Section 4, lines 194–197: the inner-fit counts contradict each other**
   - Issue:
     - "each trained on two of the training folds and scored on a third" is followed by "each fit is scored on the two folds outside its pair".
     - The text says "6 pairs of folds", while Figure 3 says "× 3 fold pairs".
     - All are true from different viewpoints, but none is named.
   - Severity: major.
   - Fix: "Each inner fit trains on two folds and is scored on the other two. For any one held-out fold that leaves 3 pairs (Figure 3); across the draw there are 6, so a net has 432 inner fits (24 × 3 × 6)."
   - Verified: yes (line 196 against the Figure 3 SVG text).

4. **Section 3, the tube bullet (lines 167–170)**
   - Issue, part a: "the gains are about the tuning budget" collides with the defined term **budget** (the false-alarm cap).
   - Issue, part b: the tube control is set up and never cashed. Section 9's "Tuning" subsection covers only line_length and chorus_norm, and never says what tuning did to tube. Table 1 shows it did almost nothing: 0.629/0.651 untuned against 0.631/0.646 on F1 alone.
   - Severity: major.
   - Fix: say "the amount of tuning" instead of "tuning budget", and add one sentence to "Tuning" giving the tube result.
   - Verified: yes (Table 1 cells, line 247).
   - Boundary: role 11 owns section order. This is a missing payoff inside a section, so I file it here.

5. **Answer box, bullet 2 (lines 59–61): "the closest by two to three times the typical move, in every fold of both draws"**
   - Issue: the sentence reads as "trailed by 2–3× the typical move in every fold". The body says the trailing holds in every fold (Figure 9), but 2–3× is a statement about means. The second draw's fold standard deviation is 0.018 around 0.025, so some folds trail by less.
   - Severity: major.
   - Fix: "every learned model trailed CoactDetect in every fold of both draws; the closest, on average, by two to three times the typical move."
   - Verified: yes (lines 305–307).

6. **Section 6 (lines 228–230) against section 9 (lines 295–296)**
   - Issue: section 6 lists five ways the rehearsal differed: simulator, coded tuning on three settings, older budget, fold defect, and no limit on the context window. Section 9 says "four things changed at once (simulator, coded tuning, budget and the fold defect)".
   - Severity: major.
   - Fix: make the two lists match. Either count five, or fold the context window into "coded tuning" in both places.
   - Verified: yes.

7. **Table 2 title (line 262): "made exactly one call on every held-out recording of both folds they were scored on"**
   - Issue: section 4 defines **held out**, in bold, as the outer fold. Inner fits are scored on training folds.
   - Severity: major, because it contradicts a defined term.
   - Fix: "…one call on every recording of both folds it was scored on."
   - Verified: yes.

### Minor

8. **Line 1755 of the generator, rendered at line 349 of the report: "chorus_gain_norm, line_length show that pattern"**
   - Issue:
     - `', '.join(pattern)` has no "and", and gives "show" with a single item.
     - It restates the previous sentence's subject.
     - chorus_norm drops out silently.
   - Severity: minor.
   - Fix: join with "and", make the verb agree with the count, write "line_length shows the same pattern", and say what chorus_norm does.
   - Verified: yes (generator lines 1119–1122 and 1755).

9. **Line 345: "where its extra false alarms fall: fewer than CoactDetect's in the dense stretch"**
   - Issue: extra false alarms cannot be fewer.
   - Severity: minor.
   - Fix: "It makes fewer false alarms than CoactDetect in the dense stretch and more outside it (…)".
   - Verified: yes.

10. **Line 341: "found as many planted events as CoactDetect (recall 0.90 and 0.85 against 0.86 and 0.84)"**
    - Issue: 0.90 against 0.86 is more, not "as many". The pairs also do not say which number belongs to which draw. The same problem is on lines 346–348.
    - Severity: minor.
    - Fix: "at least as many … (first draw 0.90 against 0.86, second 0.85 against 0.84)", and label the draws on lines 346–348 the same way.
    - Verified: yes.

11. **Answer box, bullet 3 (line 65): "by half to three-quarters as much"**
    - Issue:
      - The body's numbers leave 43%–72% of the gap (28%–57% closes), so the low end is below half.
      - "the closest learned model" also shifts meaning: at the matched 2 s merge, chorus_norm in the second draw sits at −0.004 (Table 5), closer than chorus_gain_norm.
    - Severity: minor.
    - Fix: "chorus_gain_norm still trailed … by roughly 40–70% of its as-run gap".
    - Verified: yes (lines 330–332, Table 5).

12. **Lines 330–331: "its gap is 0.014, 0.015 …"**
    - Issue: the text gives unsigned numbers while Table 5 prints the same quantities as negatives.
    - Severity: minor.
    - Fix: "it trails by 0.014, 0.015…".
    - Verified: yes.

13. **"Why this report exists" (line 51) and section 6 (line 228)**
    - Issue:
      - The last sentence of "Why this report exists" is a section roadmap.
      - "on a simulator since retired" appears in both places.
      - The intro's "so it was run a second time" follows from "which the project says is not yet final", not from the actual reason, which is that one run cannot measure luck.
    - Severity: minor.
    - Fix: cut the roadmap sentence (or keep it as navigation and say why it stays). Tie "so" to the measurement reason. Remove the repeat from section 6.
    - Verified: yes.

14. **Title subline, line 40: "a hundredth of F1"**
    - Issue: F1 is used before it is defined on line 55.
    - Severity: minor.
    - Fix: "a hundredth of F1 (a 0–1 detection score)".
    - Verified: yes.

15. **Box (lines 60, 65): "cap"**
    - Issue: the body calls the same thing "budget" and "ceilings".
    - Severity: minor.
    - Fix: "one shared cap on false alarms (the budget, section 5)".
    - Verified: yes.

16. **Figure 1 caption and key**
    - Issue:
      - "The top strip is the lane" is house jargon.
      - "nothing drawn over it" states a house rule, not information for the reader.
      - "one mark per event" leaves "event" ambiguous between a calcium event and a coordinated event.
      - The key's "distractor: … scored as a false alarm" and line 104's "scored as false alarms" are imprecise: the distractor is not scored; a call on it is.
    - Severity: minor.
    - Fix: "The top strip holds the answer key and CoactDetect's calls"; drop "nothing drawn over it"; write "one mark per calcium event"; write "a call on one counts as a false alarm".
    - Verified: yes.

17. **Section 2, line 120: "the two backgrounds' F1 are averaged"**
    - Severity: minor.
    - Fix: "F1 scores are averaged".
    - Verified: yes.

18. **Section 3, the reference paragraph (lines 154–156): "…so an event cannot raise its own threshold, and calls within 8 s are joined"**
    - Issue: the merge setting hangs off the guard-interval sentence.
    - Severity: minor.
    - Fix: split it into its own sentence. Also gloss "null" at first use (line 152): "the circularly shifted copies (the null)".
    - Verified: yes.

19. **Section 3, detector descriptions**
    - Issue:
      - rate+context, "a window centered on it": "it" has no clear referent.
      - line_length uses "the field" and "vote" before chorus_norm defines votes.
      - tube, "within a pool of about a second": "window" is the plain word.
    - Severity: minor.
    - Fix: "a longer window around the same moment"; "the share of imaged cells active"; "within a window of about a second".
    - Verified: yes.

20. **Line 350: "their distractor field counts distractors touched by any call, matched ones included, so it cannot be subtracted…"**
    - Issue: this is score-file internals and the author's debugging history. The reader needs only that the split is unknown.
    - Severity: minor.
    - Fix: "The score files do not record which of those fell on distractors."
    - Verified: yes.

21. **Section 7 (line 239)**
    - Issue: it opens with a figure pointer rather than the finding, and the section titled "Results of each draw" never says how the nets did.
    - Severity: minor.
    - Fix: open with "CoactDetect scores 0.748 in both draws…" and add one sentence on where the nets' means fall.
    - Verified: yes.
    - Boundary: role 11 owns the order.

22. **Lines 313–316: "were within 0.029 of CoactDetect as run. Untuned, chorus_norm was −0.012 and +0.006."**
    - Issue: "within" hides the sign. The untuned figures do not say which draw each belongs to or what they are measured against.
    - Severity: minor.
    - Fix: give signed values per draw, "against CoactDetect, first and second draw".
    - Verified: yes.

23. **Section 9, "Tuning" (line 356): "raised … by +0.032 and +0.029"**
    - Issue: a double sign.
    - Severity: minor.
    - Fix: "by 0.032 and 0.029".
    - Verified: yes.

24. **Section 5 (lines 211–216)**
    - Issue:
      - "Each detector and net is chosen two ways", but the nets also have an untuned entry.
      - "each pairing is an entry" does not say pairing of what.
      - The sentence carries two colons.
    - Severity: minor.
    - Fix: "each detector–selection pair is an entry", and move the list of the three ceilings into its own sentence.
    - Verified: yes.

25. **Line 223: "(CoactDetect 2–6)"**
    - Issue: no unit. Line 222: "is reported only" should read "is only reported".
    - Severity: minor.
    - Fix: "(CoactDetect 2–6 per hour)".
    - Verified: yes.

26. **Line 275: "Two things could do it"**
    - Issue: vague. The first cause, the threshold carried onto refits, applies to nets only, yet CoactDetect is named as an overrun in the same sentence.
    - Severity: minor.
    - Fix: "Two causes are possible for the nets, and neither was measured: …; for CoactDetect, only chance."
    - Verified: yes.

27. **Line 207: "unless every outer fold fits its own"**
    - Issue: "its own" what?
    - Severity: minor.
    - Fix: "…trains its own models on its own recordings".
    - Verified: yes.

28. **Line 190: "(24 recordings, one per background)"**
    - Issue: reads as one recording per background.
    - Severity: minor.
    - Fix: "(24 recordings: each seed at both backgrounds)".
    - Verified: yes.

29. **Line 200: "(40–60 refits per net per draw)"**
    - Issue: the range is unexplained.
    - Severity: minor.
    - Fix: add "fewer when two selections pick the same configuration", or drop the count.
    - Verified: no (I did not check the cause).

30. **Line 229: "tuned on three settings"; line 232: "prompted this replicate"**
    - Issue: "three settings" of what is unclear, and "replicate" as a noun is jargon.
    - Severity: minor.
    - Fix: name the settings; use "rerun" for "replicate".
    - Verified: no (I did not open the rehearsal's notes).

31. **Lines 302 and 209: redundant closing sentences in captions**
    - Issue: Figure 8's "It shows the scale a between-draw difference has to beat." repeats the body and has a vague "It". Figure 3's "The whole of it repeats with each fold held out." repeats the figure's own bottom line.
    - Severity: minor.
    - Fix: cut both sentences.
    - Verified: yes.

32. **Figure 11 caption (line 354)**
    - Issue:
      - "Held-out false alarms per recording, chosen under the budget" is a dangling modifier: false alarms are not chosen.
      - "the two coded detectors that count cells the same way" does not say the same way as what.
      - "at each entry's chosen threshold" does not fit coded detectors, which have settings, not thresholds.
    - Severity: minor.
    - Fix: "…for entries chosen under the budget"; "that, like the nets' pooling, count distinct cells"; "at each entry's chosen threshold or setting".
    - Verified: yes.

33. **Figure 7 caption (line 263): "trains at all 5"**
    - Severity: minor.
    - Fix: "trains normally at all 5 refits".
    - Verified: yes.

34. **Section 10**
    - Issue:
      - Line 365: "moves the opposite way" does not say what moves.
      - Line 371: "in both folders" is ambiguous.
      - Line 388: "the one real-recording figure quoted" repeats the figure/number collision from finding 2.
    - Severity: minor.
    - Fix: name the quantity; write "on both exports"; write "the one real-recording number".
    - Verified: yes.

35. **Table 7, rows "tuning before this comparison" and "the budget"**
    - Issue: the coded-detector column describes CoactDetect only, but the row heading implies all six.
    - Severity: minor.
    - Fix: label those cells "CoactDetect:" and say what applies to the other five.
    - Verified: yes.

36. **Figure 2 (line 185)**
    - Issue: a numbered figure that is empty, and the placeholder says "to come" twice.
    - Severity: minor for my role; delivery of the drawing belongs to roles 9 and 10.
    - Fix: say "to come" once.
    - Verified: yes.

37. **Line 401: "among others"**
    - Issue: vague.
    - Severity: minor.
    - Fix: name the other branches or cut the phrase.
    - Verified: yes.

38. **Prose references without names**
    - Issue: line 123 has "as in Figure 1" with no name, against the house rule of number plus name.
    - Severity: minor.
    - Fix: "Figure 1, a simulated recording".
    - Verified: yes.
    - Boundary: role 10 owns the mechanical sweep.

## Checked and clean

- House voice across section 8 ("Training that failed", "Searches that found no admissible setting", "Settings at the top of their grid"), the headline-gap paragraph, and both matched-merge paragraphs. Each asserts its payload first, uses concrete numbers with units, and names unknowns instead of hedging ("the output itself is not examined here"; "neither was measured"; "how the headline depends on any of them is untested").
- No throat-clearing openers and no recap closer. The References and section 11 lists are functional.
- Glossary use is consistent. "Distractor", "promiscuity probe" and "contaminated null" are used as `docs/GLOSSARY.md` defines them, and the banned word "modality" is absent.
