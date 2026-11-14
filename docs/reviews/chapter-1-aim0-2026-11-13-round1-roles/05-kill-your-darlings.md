GRANT 5 MISMATCH — missing none; holds Bash, PowerShell, Edit, Write, Agent, Artifact, Skill, ToolSearch, SubagentHandback, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update, mcp__claude_ai_Claude_Docs__guide (plus deferred NotebookEdit, WebFetch, Dropbox, Gmail and others available through ToolSearch)

# Murderboard role 5: line editor ("Kill Your Darlings")

**Artifact:** `<repo>\docs\dissertation\chapter-1-aim0.md` (blob 14d63527), 1,669 lines, read in full.

## Run notes

- **The grant mismatch is a finding about the run, not about the chapter.** This role came up on a fallback path that gave it editing and shell tools. It used only Read, Grep and Glob, and it edited nothing. The run record's `roles:` line should say the review took a fallback path.
- **`murderboard_prose.sh` was not run, and that counts as a failure.** The file is not in this worktree: Glob for `**/murderboard_prose*` found nothing. Even if it were there, running it needs Bash, which is outside this role's grant. So the "line · construction · kind" and "block · words · sentences" table is missing. Every count below came from Grep, and every block length is an estimate (lines × about 16 words), not a count.
- **Banned list used:** the role file's default list (*not just X, but Y* · *it's not about A* · *it's worth noting* · delve, leverage, robust, seamless, crucial, landscape, tapestry · "In today's"). I added three house rules: plural *data*, no *fire/firing*, and the owner's ban on "toy".

## Mechanical search results (Grep output, pasted)

- **Banned words, "toy", "fire" in any form:** one hit, and it is exempt. Line 1657 is a reference title: "Simple, robust and optimal ranking…" (Shah & Wainwright).
- **Singular *data*** (pattern: determiner + data + is/was/has/does/shows/itself, or "this data"): no matches.
- **Every use of *data*:** lines 48, 207, 212, 380 ("the data themselves", correct), 1230, 1295 (quoted text), 1398, 1486, 1508, 1630 (reference). None breaks the rule.
- **Em dashes:** 0. So there are no em-dash pivots.
- **British spellings** (centre, labelled, modelling, analyse, behaviour, colour, neighbour, favour): no real hits. Line 1072 has "per cent"; American usage is "percent".
- **Three-item lists built for rhythm:** none found on reading.

## Findings

Each row gives: location · issue · severity · suggested fix · verifiable against a source.

### Term collisions and undefined terms (the owner's "define every term at first use" brief)

1. **"Participation" means two different things.** · Line 40 defines it as "how many cells join an event", a count. Table 1.2 (l. 252) and GLOSSARY l. 481 define it as a share ("participation 0.15, 0.3, 0.6"). Line 202 ("threshold must sit below the participation") and l. 1240 ("blended participation") use the count sense. · **High** · At l. 40, write "**participation** (the share of cells that join an event; k cells of N)". Use "participants" or "k" wherever a count is meant. · Yes (GLOSSARY).
2. **"Cell" has three meanings in §1.2.3.** · The radar terms "reference cells", "cell under test" and "guard cells" (l. 129–134) sit in the same paragraph as "N cells" (biological cells). GLOSSARY l. 667–668 flags this third sense; the chapter never does. A naive reader will read "guard cells next to the cell under test" as neurons. · **High** · Add one sentence: "In radar a *cell* is a stretch of range or time; here the cell under test is the instant being tested, and the reference cells are the 30 s on either side." · Yes.
3. **"Window" covers four scales, and "recording window" adds a fifth use.** · The word means the counting window *w* (1–4 s), the sliding 2 s window, the CFAR reference windows (30 s), and the "recording window" (20 min, l. 225 onward). The 20-minute one is exactly what a reader will mix up with *w* in sentences like "participants can be read from one window" (l. 610). · **Medium** · Rename the 20-minute unit, for example "baseline segment" or "analysis period", and keep "window" for counting. · Yes.
4. **"Baseline" has three senses.** · The title's "analytical baseline" means a reference method. Lines 51, 225, 1078, 1509 and 1526 mean the pre-treatment recording period. Line 1261's "simulated random baseline" means a reference value. "Baseline" in the recording sense is never defined for a naive reader. · **Medium** · Define it at l. 51 ("baseline, before any treatment"), and change the title word, for example "an analytical reference". · Yes.
5. **"Calcium event" is used before it is defined, and never defined.** · Line 12 uses "calcium events" and l. 13 "multichannel stream"; "channel" is first explained at l. 214. A reader outside the field gets no "a brief rise in a cell's fluorescence". · **Medium** · In l. 19–23, add a half-sentence defining a calcium event. Say "channel = cell" at the first use, or drop "multichannel" from l. 13. · Yes.
6. **"Poisson" is never defined in prose.** · Line 239 ("independent Poisson background onsets") and l. 343 use it bare. §1.2.3 described the same thing in plain words but never named it. · **Low** · At l. 112, add "(a **Poisson** process)" after "at random at rate b". · Yes.
7. **Terms are used before their definitions.** · "the repository's assessor" (l. 192) is defined only at l. 428. "the score sort and F" in the Figure 1.4 caption (l. 407–411) are defined at §1.8.2. Table 1.2's column "values in the first experiment" comes before the first experiment is introduced (§1.4). · **Medium** · At l. 192, say "the repository's assessor (*1.3.4*), a cell-counting tool". In the Figure 1.4 C caption, give one clause each for the score sort and F, or point forward explicitly. · Yes.
8. **"Chance floor", "event floor" and "smallest threshold under the budget" are three names for close relatives.** · At 0.0096 Hz they give 6 cells (§1.2.3, 2 s sliding) and 4–5 cells (§1.6.1, 1 s bins). §1.6.1 never says why its answer differs from §1.2.3's. · **Medium** · Add one sentence in §1.6.1: "Lower than the 6 cells of *1.2.3* because the assessor counts 1 s bins, not a 2 s sliding window, and starts at most one cluster per run of bins." · Yes.

### Ambiguous or imprecise sentences

9. **Line 61:** "needs three things … gives them in that order". The three things are never named, so "that order" has nothing to point to. · **Medium** · Name them ("why simple detectors fail, the tools that measure coordination, and the question those tools raise") or cut the sentence. · Yes.
10. **Line 385–386:** "independent random shifts were tried and lost planted pairs". The mechanism is missing, so the reader cannot tell why the shifts lost pairs. · **Medium** · State it ("…because a shift shorter than the event spacing re-aligned…"), or cut the clause. · No (needs the record).
11. **Line 388–389:** "Per recording it reports participants from f₃/f₂ pooled across all the recordings it is given." "Per recording" and "pooled across recordings" contradict each other. · **Medium** · "It reports one participant estimate for all the recordings it is given, from f₃/f₂ pooled across them, and per-recording rates from that." · Yes (l. 618–619 agree with this reading).
12. **Line 772–773:** "the surrogate's own pair count 4–15 times the independent value". Which pair count, and which value, is unclear: the coordinated part, or all of it? · **Low** · Name the quantity: "the surrogate's coordinated pair excess". · No.
13. **Line 801:** "rather than the 2.2 of a normal error" is garbled. · **Low** · "rather than the 2.2 expected if the errors were normal". · Yes.
14. **Line 895:** "When σ is *not* identifiable has not been derived" reads as a garden path. · **Low** · "The condition under which σ cannot be identified has not been derived." · Yes.
15. **Lines 1062–1064:** the sentence starting "Predicted 0.256 and 0.019 per minute…" is a fragment with no subject. · **Low** · "The formula predicts 0.256 and …". · Yes.
16. **Line 1154:** "At σ = 1 s the event part runs high". It could mean the reading or the model. · **Low** · "the mixture's event part over-predicts". · Yes.
17. **Line 1186:** "The model as first stated" leaves the reader asking which model, and stated where. · **Low** · "The separation model as first run". · Yes.
18. **Lines 1430–1431 (§1.9.1):** "The threshold that worked, CFAR's". CFAR missed event 2 in 56 % of draws and event 5 in 58 % (Table 1.1). It "worked" only for situation 4. · **Medium** · "The threshold that held in the busier background, CFAR's, …". · Yes (Table 1.1).
19. **Line 1435:** in the list of things the theory "does not predict", the item "clustered intervals" is not a quantity. · **Low** · "the effect of clustered intervals between events". · Yes.
20. **Merge rule is stated two ways.** Line 92–93 says "gap … at most a merge gap, 3 s". Lines 157 and 436–437 say "less than 3 s apart". · **Low** · Pick one, and say it the same way all three times. · Yes.
21. **The median events per recording window is given inconsistently.** Line 1344–1345 says the median window "holds one to three". Lines 226–227 and 644 say median 1 (fast) and 2 (slow), and l. 1000 and 1069 say "one or two". · **Medium** · "one or two". · Yes.
22. **"obvious" appears at lines 61, 96, 546 and 1177.** To a reader outside the field it reads as "you should already know this". · **Low** · Use "simplest", "first", or cut. · Yes.
23. **Voice shifts to "we" only in §1.6.1** (l. 1067 "We accept", l. 1072 "we recommend"). Elsewhere the chapter writes "This chapter allows" (l. 120). · **Low** · Use one voice. · Yes.
24. **Line 1072:** "per cent". · **Low** · "percent" (house rule: American English). · Yes.

### Redundancy and preview (house voice: no preview of what a section will say, no recap)

25. **§1.1 "How the chapter proceeds" (l. 60–74) is a roadmap.** It also states the Aim 0 question word for word, and the same question appears again at l. 592–594. · **Medium** · Keep the question in one place (§1.4). Cut the roadmap to two sentences. Boundary: role 11 owns whether a roadmap belongs here at all; this row is only about length and duplication. · Yes.
26. **The section openings of §1.5 (l. 687–694) and §1.6 (l. 1029–1033) are previews.** §1.5's "In short:" repeats §1.4's "answer in brief" and Contribution 1–3. · **Medium** · Cut §1.5's paragraph to its first sentence. Keep §1.6's, which is short, or cut it too. · Yes.
27. **The first two paragraphs of §1.1 (l. 12–17 and l. 19–25) each describe turning a recording into lists of onset times.** · **Medium** · Merge them. Lead with the definition paragraph and end on the payload: "Downstream analysis rests on knowing which onsets belong to which event." · Yes.
28. **§1.3.5 (l. 458–465) exists to say "introduced where they are analyzed".** · **Low** · Fold its two definitions into §1.8's opening and delete the subsection, or keep one sentence at the end of §1.3.4. · Yes.
29. **Window sharing is explained twice.** §1.3.3 (l. 358–378) and §1.5.1–1.5.2 (l. 698–735) both do it, and "rounding changes nothing because windows sit on the frame grid" appears at l. 628–629 and l. 723–724. · **Low** · In §1.5.2, refer back to §1.3.3 instead of re-deriving the motivation. Keep the rounding remark once. · Yes.
30. **"6 and 12 cells, same as the repository's floor" is stated three times:** l. 123–125, l. 1074–1076 and l. 1430–1431. · **Low** · Keep l. 123. Make l. 1074–1076 a back-reference and cut l. 1431's restatement. · Yes.
31. **Figure captions repeat the text's results.** The set definition is at l. 267–270 and again in the Figure 1.3 caption (l. 274–278). The text and caption of Figure 1.7 repeat each other (l. 732–734 and 747–749). The Figure 1.9 caption repeats l. 792–805. The Figure 1.17 caption repeats l. 1273–1274. The Figure 1.19 caption's last three sentences are repeated almost verbatim at l. 1380–1383. · **Medium** · Captions should say what is drawn; the result belongs in the text, once. Cut l. 1380–1383 outright. · Yes.
32. **The Kruskal/Cramér/Greiner attribution chain appears twice:** l. 1324–1327 and Table 1.9. · **Low** · Keep the full chain in Table 1.9. In the text, keep "the classical arcsine relation (Kruskal 1958)". · Yes.
33. **Thomas (1949) aside at l. 237–239:** "although Thomas gave only the count distribution… with no scatter law". It is a scholarly darling that gives a naive reader nothing. · **Low** · Cut it, or move it to §1.3.6. · Yes.
34. **Kish's "synthetic but useful" quotation and the deft²/roh/n/a symbol mapping (l. 1282–1285)** are decoration in the main line. · **Low** · Keep "has the form of Kish's design effect (Kish 1995)" and drop the quotation. · Yes.

### Passage test (does a block say more than its last sentence?)

35. **Frame-rounding paragraph, l. 1385–1398, about 220 words (estimated).** Its point is: *rounding creates ties that pull the no-order null down more than the signal, so power rises, and a recorded-data test needs a null rounded the same way.* That point sits in the last sentence. · **Medium** · Promote it to the first sentence. Keep the 0.06→0.66 example and the tie-corrected mean's match (0.004); the other numbers can go. · Yes.
36. **§1.4 "How the predictions are tested", l. 615–625, about 170 words.** Its point (*residual = median recovered minus predicted; refusals bias the 5-cell, 0.05 Hz medians*) is split between the first and last sentences. The middle (the gap between pooled and median path, the ±0.008 nonlinearity) is evidence for methods readers. · **Low** · Move the middle to a footnote or a parenthesis. · Yes.
37. **§1.5.6 opening, l. 890–900, about 180 words.** The block mixes the definition of the fit with its known defects. The defects are listed again in Limitation 3. · **Low** · Keep the definition and the identifiability sentence here, and leave the defects to §1.9.4. · Yes.
38. **Long captions (estimated words):** Fig 1.4 about 300, Fig 1.9 about 260, Fig 1.5 about 260, Fig 1.2 about 250, Fig 1.12 about 240, Fig 1.11 about 230, Fig 1.10 about 220. Each carries results, which overlaps with #31. · **Medium** · Cut each to what is drawn plus one sentence of result. Fig 1.12's "Two points are resolved on the first experiment only…" belongs in §1.5.7. · Yes (line counts).
39. **Long sentences:** l. 1179–1181 (about 55 words, the likelihood-ratio test set-up), l. 328–331 (about 65 words, the correlogram tool's calibration), l. 646–650 (about 60 words). · **Low** · Split each at its "because" or "and". · Yes.

### House-rule items (boundary noted)

40. **Several table headers lack units, and dimensionless values are not labeled.** The house rule says units go in the header, not the caption. Table 1.1's share columns have no "(share of draws)". Tables 1.3 and 1.4 say "jitter" or "participants" where the values are fitted ÷ planted ratios. Table 1.6's "(s)" is in the caption only. Table 1.7's power is not marked dimensionless. · **Medium** · Add the unit or "(ratio)" to each header. Boundary: a mechanical check that role 10 may also table; filed here once because writing_conventions.md names the line editor as its enforcer. · Yes (`docs/writing_conventions.md`, "Every table column carries its units").
41. **The "Reproducing" section's comments carry section numbers from before the renumbering.** Line 1585: "event floor, 1.5.1" should be §1.6.1. Line 1596: "1.5.2, Table 1.6" should be §1.6.2. Line 1583: "prints 1.1 and 1.4 numbers" is probably stale too. · **Medium** · Update these to the current numbers. · Yes for 1585 and 1596; no for 1583.
42. **List with no blank line before it (l. 640–641).** Pandoc markdown will not parse a list without a blank line before it, so the .docx deliverable will show literal "- " dashes. · **Low** · Insert a blank line. Boundary: rendering is role 10's; noted because the deliverable goes through pandoc. · Yes (source text).

### Conclusion and recap

43. **§1.10 is a recap, and the house voice says no recap paragraph.** A dissertation chapter conventionally ends with one, so I am not asking for it to go. Two of its claims are vaguer than the body. "Event rate with a few more events than that" stands for 4 (13 cells) and 16 (7 cells), which for 7 cells is double, not "a few more". "A window shorter than about six times the jitter undercounts participants" drops the 0.9 criterion it rests on. · **Low** · Give the numbers: "rate from four events of 13 cells, sixteen of 7", and "below 0.9 of planted once the window is under about six times the jitter". · Yes (§1.5.7, §1.5.2).

## What holds up

- The banned constructions are absent.
- *Data* is plural everywhere, and "fire" and "toy" are absent.
- The figure-led opening and the five numbered "situations" read cleanly.
- Most sentences are short and concrete.

The main line-level costs are duplication between captions and text, sections that preview themselves, and four overloaded terms (participation, cell, window, baseline). The overloaded terms matter most to the naive reader the owner asked for.
