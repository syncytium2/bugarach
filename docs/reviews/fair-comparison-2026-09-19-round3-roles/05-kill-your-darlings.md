<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 5 ok — Read, Grep, Glob

(SubagentHandback is the delivery channel, not an editing tool. I hold no Edit, Write or NotebookEdit. I have no Bash, so the caller ran the mechanical search.)

**Banned list used:** the list parsed from bugarach `docs/doc_review_process.md` by `murderboard_prose.sh` (syncytium2/murderboard @ 08f5ddb), as the caller reported.

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` (hash-object 5c0ccbb)

## Tool output, pasted from `...\scratchpad\mb\prose_tool_output_round3.txt`

```
  line   construction                       kind   context
  — no banned construction found

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1          6 words    1 sentences
  7        101 words    3 sentences
  32       477 words   23 sentences   << over 120
  68       455 words   23 sentences   << over 120
  88       454 words   20 sentences   << over 120
  116      743 words   14 sentences   << over 120
  129      696 words   31 sentences   << over 120
  166      389 words   15 sentences   << over 120
  182      373 words   15 sentences   << over 120
  200      356 words   14 sentences   << over 120
  221      224 words    8 sentences   << over 120
  240      127 words    5 sentences   << over 120
  252      441 words   16 sentences   << over 120
  260      236 words   11 sentences   << over 120
  282      206 words    8 sentences   << over 120
  285      934 words   40 sentences   << over 120
  326      287 words   16 sentences   << over 120
  341        5 words    1 sentences
  343      371 words   17 sentences   << over 120
  373      340 words    4 sentences   << over 120
  376      719 words   25 sentences   << over 120
  409        2 words    1 sentences
  411      626 words   31 sentences   << over 120
  456        4 words    1 sentences
  458      340 words   16 sentences   << over 120
  498       19 words    2 sentences
  20 block(s) over 120 words — for each, name its payload sentence and where it sits
```

I also ran my own Grep for the banned words, "worth noting", "not just", "In today" and word-dash-word em-dash pivots. I found 0 hits. I read every prose sentence and found no three-item list built only for rhythm.

## Passage test: the 20 blocks over 120 words

| block (line) | payload sentence | where it sits | what the other words buy |
|---|---|---|---|
| 32 (terms, question, answer) | "Held to a shared limit on false alarms, CoactDetect is ahead of every net on average…" | About 60% of the way in, after a 180-word Terms box and the question | The Terms box defines words before the reader knows why they matter. The answer paragraph itself says "The sections below explain every term in this paragraph". So the box can come after the question and answer (finding F1). "The sections below explain…" is a preview; keep only the pointer to sections 6 to 8. |
| 68 (sec 1 + Figure 1 caption) | "A detector has to find the few real events without calling either." Then the distractor ceiling of 0.71. | End of paragraph 1; ceiling in the middle of paragraph 2 | The example and the ceiling are evidence. Keep. |
| 88 (sec 2 + Figure 2) | "…every planted event is known." | Sentence 2. Good. | The scoring rules are needed. But one subordinate clause undercuts the headline (F2). |
| 116 (sec 3 + Table 1) | "The difference between the nets that matters most is where each stops treating ROIs separately." | Opens paragraph 2. Good. | The Table 1 citation cell is repeated word for word three times (F9). |
| 129 (sec 4.1 + Figure 3 + four folds) | "…every candidate setting is judged on the other three folds alone, and the winner is scored once on the held-out fold." In the sub-block: "So the corrected values rank how consistent a difference is; they are not tests." | First is early. The sub-block's payload is second to last. | The Bouckaert/Frank and Bengio/Grandvalet citations are what a sceptic would ask for, so keep them. But put the payload first (F12). |
| 166 (sec 4.2 + Figure 4) | "Four outer folds would then have been fewer than four independent fits." | End of paragraph 1 | Paragraph 2, the fix and its check, earns its place. "'Not the same' is not 'independent'" earns its place. |
| 182 (sec 4.3 + Figure 5 + reference settings) | "The reference CoactDetect below therefore uses goal 1's settings…" | Paragraph 2. Paragraph 1 opens on a sentence that uses "counting mode" before defining it. | Reorder (F13). |
| 200 (sec 4.4) | "So every contestant was chosen twice…" | Sentence 2. Good. | The budget details are needed. One sentence is ambiguous (F16). |
| 221 (sec 4.5) | The crowded-recording rule | Sentence 2. Good. | "the check sees gaps wider than about 6 s" is opaque (F15). |
| 240 (sec 5) | "So a second workstation ran the same comparison on a disjoint set of recordings" | Sentence 2. Good. | Clean. |
| 252 + 260 (sec 6, Table 2, bullets) | "So on F1 alone the two draws disagree about who is ahead, by less than 0.01 F1…; under the budget they agree." | The last bullet, at the very end | This is the section's conclusion and it arrives last, written in the order the author worked it out. Promote it to lead the list (F11). |
| 282 (Figure 8 caption) | "Each mark is one outer fold: the net's held-out F1…minus CoactDetect's" | Early | Dense but each sentence is a reading instruction. Keep. |
| 285 (sec 7, 934 words, the longest block) | "With the gap matched on F1 alone, chorus_norm is ahead…That reverses the order in point estimate, and is not distinguishable from a tie…Under the budget, matching does not change the order." | Paragraph 4 of 5, about 70% of the way in | Paragraphs 1 to 3 explain the mechanism before the result. The GPU-versus-CPU reproduction sentence is sceptic evidence but belongs in the Figure 9 caption or a note. Promote the result to open the section (F10). |
| 326 (sec 8 + Figure 11) | "What separates them is the faintest events, joined by 10% of the ROIs." | Middle. The first sentence carries the claim in general form. | Acceptable. The last sentence ("paid for in precision") is a second payload and earns its place. |
| 343 (sec 9 bullets) | Each bold lead-in is a payload | The start of each bullet. Good. | Bullet 3's second half, on why the numbers differ from goal 1's published ones, answers a question this reader cannot ask (F21). |
| 373 (Table 3) | Caption | — | Fine. |
| 376 (sec 10) | "Tuning moved the nets by little, and not always up" / "Failure is a property of the nets, at about 1% of refits…" | Paragraph starts. Good. | About 120 words of verbatim repeated parentheticals (F8). |
| 411 (sec 11 limits) | The bold lead-ins | The start of each bullet. Good. | Individual sentences are opaque (F17, F18, F19). |
| 458 (sec 12) | Reference list | — | The code-trap sentence about `build_chorus_norm()` is a developer warning in a newcomer report (F22). |

## Findings

Each finding gives location · issue · severity · suggested fix · verified (yes/no).

**F1** · Opening block, lines 36–48 · The Terms box comes before the question and answer. It uses "coded detectors", "CoactDetect" and "LoCo" before paragraph 2 introduces them, and the payload arrives about 290 words in. · medium · Put the question and answer first and the Terms box after them. Or drop the Terms box's use of CoactDetect/LoCo until they are introduced. · verified yes

**F2** · Line 105–107, sec 2 · "…the scorer's own documentation says to read the order of its rows, not their third decimal place" sits inside a subordinate clause. The headline margins are in the third decimal (0.007, 0.009, 0.010), and the Figure 8 caption reports margins of 0.0001 and 0.0004. The report makes the warning, then reads past it, and never connects the two. · high · Give it its own sentence and tie it to the margins: "The headline margins below, 0.007 to 0.010 F1, are at the resolution the scorer warns against." · verified yes (internal)

**F3** · Answer paragraph, lines 58–61 · One sentence carries three clauses and an appositive: "which one is ahead changes with a setting only the coded side was allowed to tune, how close two calls must be before they are merged into one, and with which recordings were drawn". "How close two calls must be…" reads as a second list item, not as a definition of the setting. · medium · Split it: "Which one is ahead changes with two things: the merge gap (how close two calls must be before they are merged into one), which only the coded side could tune; and which recordings were drawn." · verified yes

**F4** · Answer, lines 57–59 · "its merge gap", "refits that failed to train" and "both draws of recordings" are used before they are defined. "Merge gap" is paraphrased only in the next sentence, without its name. · medium · Name the merge gap at first use with its gloss. Say "training runs that failed" instead of "refits". Say "in both independent sets of recordings". · verified yes

**F5** · Figure 1 caption (line 85) · "at about 12 times the quiet background's rate and 3 times the busy one's". The ratios fit only the probe's added 0.06/s: 0.06/0.0052 = 11.5 and 0.06/0.019 = 3.2. Against the total rate they are 12.5 and 4.2. A reader will take "rate" to mean the total. · medium · "its added rate is about 12 times the quiet background and 3 times the busy one". · verified yes (arithmetic from the report's own numbers)

**F6** · Terms (line 36–37), Table 1 SPIKE-synch row, sec 11 contamination bullet · "event" means two things. Terms defines a per-cell **firing** as "one entry in its event list", then uses "event" for coordinated events. SPIKE-synch "local gaps between each ROI's events" and "called events on the steps… about 0.03% of events" both mean firings. · medium · Use "firing" wherever a single cell is meant. Keep "event" for coordinated or planted events. · verified yes

**F7** · Throughout (Terms line 41; Table 1 "5 settings"; 4.1 line 146 "3 or 4 settings of its own architecture"; line 147 "moved one setting at a time") · "setting" means three things: a whole configuration, a single knob, and one value of a knob. · medium · Keep "setting" for a knob and "value" for one point on its grid. Use "configuration" for the whole candidate, as the net rows already do. · verified yes

**F8** · Sec 10, lines 389 and 392 · The gloss "(the failed-training signature: one long call per recording, so a hit or two at perfect precision and almost no recall)" appears 4 times word for word. "(no calls at all at the single threshold its selection chose on the inner fits; an F1 with no calls counts as 0)" appears 3 times. Also, line 389 nests parentheses: "(… inner fits (0.9983); …)". · medium · Define "the failed-training signature" and "no calls" once, above the lists, and make each bullet one line. This cuts about 120 words. · verified yes

**F9** · Table 1, "where it comes from" column · The Deep Sets citation cell appears three times in full. · low · Write "as chorus_norm" in rows 2 and 3. · verified yes

**F10** · Sec 7, lines 285–323 · At 934 words this is the longest block, and its result (the matched-gap comparison, lines 311–320) sits in paragraph 4 of 5. · medium · Open the section with the two-sentence result, then give the mechanism. Move the reproduction check ("coded detectors exactly and the nets within 0.0015 F1…") into the Figure 9 caption. · verified yes

**F11** · Sec 6 bullets, lines 260–281 · The conclusion is the last bullet, and it restates the two bullets above it. · low–medium · Make it the first bullet, or the paragraph that leads into the list. Cut the restatement from the other two. · verified yes

**F12** · Sec 4.1 "What four folds can and cannot show", lines 152–163 · The payload ("the corrected values rank how consistent a difference is; they are not tests") is second to last. "a two-sided 5% test would need 3.18" is elliptical: the test needs |t| ≥ 3.18. Also, "Varma and Simon 2006, …, measure how much the shortcut flatters" (line 132) leaves a verb stranded inside a citation, and "the shortcut" has no named referent. · low–medium · Lead with the payload. Write "would need |t| of at least 3.18". Write "(Varma and Simon, 2006, BMC Bioinformatics 7:91, measured how much choosing and scoring on the same recordings flatters a result)". · verified yes

**F13** · Sec 4.3, line 183–185 · The first sentence uses "weaker counting mode" before binned and sliding modes are defined in the next sentence, and its "so… instead" logic is hard to follow. · medium · Define the two modes first. Then write: "Goal 1 found sliding mode better; the project's current defaults still use binned mode; so every setting the searches did not vary was held at goal 1's values." · verified yes

**F14** · Table 2 caption, line 258 · Broken parallel: "a coded choice that fails the crowded-recording check, or under the budget is not admissible (section 4.5), gets its difference and no t." · medium · "a coded choice that fails the crowded-recording check, or that is not admissible under the budget (section 4.5), gets its difference and no t." · verified yes

**F15** · Sec 4.5, line 230–231 · "so the check sees gaps wider than about 6 s": it is unclear what "sees" means or whose gaps. · medium · "so the check can only penalize merge gaps wider than about 6 s". · verified no (meaning inferred)

**F16** · Sec 4.4, line 211–212 · "The budget never drops below one false alarm in the time measured, a floor no fold reached" is ambiguous: did no fold's budget fall to the floor, or did no fold's false-alarm count reach it? · low · "The budget has a floor of one false alarm in the time measured; no fold's budget was low enough to hit it." · verified no

**F17** · Sec 11, participation bullet, lines 422–425 · The heading says the value "sits just outside its own measured interval". The body gives a lower end of 18.18% = 6 of 33, which is the ROI count the bench plants. A reader cannot tell what is outside what, or why a rounding would "move every bench number". · medium · State both numbers in the same form: "the bench plants 18.00%; the interval's lower end is 18.18% (6 of 33)". Say what changing it would change. · verified no

**F18** · Sec 11, last bullet, line 450–452 · "what retraining elsewhere would move was measured only confounded, by an earlier cross-machine check…" is ungrammatical and opaque. Also, "processors" (here and on lines 296, 300, 494) means CPUs, but a GPU is also a processor. · medium · "Only one earlier check compared training on two machines, and the second machine had uncommitted changes, so its difference of up to about 0.02 F1 per fold mixes machine and code." Say "CPU" and define it once. · verified yes

**F19** · Sec 11, contamination bullet, lines 414–421 · Undefined for a new reader: "export folder", `steps_excluded` (an index, not a name) and "bootstrap interval". The last sentence ("lists the contamination as a limit because the project lead asked for exactly that…") is process talk; only its final clause is information. · low–medium · Gloss the export folder in a few words and drop the code name here, since sec 12 carries the records. Keep "listing it does not show that the effect is negligible." · verified yes

**F20** · Sec 9, bullet 2, lines 350–359 · The heading says "4 coded detectors have no admissible result in any fold", and the next sentence names four detectors: binned SCE, LoCo, SPIKE-synch and rate+context. But binned SCE passes in fold 4 under the budget (bullet 1; Table 3, 1 of 4). The four with none are LoCo, SPIKE-synch, rate+context and locust. · medium · Name the four in the heading, and introduce binned SCE separately as "also over the budget at its start". · verified yes (against Tables 2 and 3)

**F21** · Sec 9, bullet 3, lines 363–365 · The second half, on why the crowded numbers differ from goal 1's published numbers (seeds 49–60 versus 1–12), answers a comparison this reader never sees. · low · Move it to the Table 3 caption, or cut it. · verified yes

**F22** · Sec 9, bullet 4, line 366 · "switched off the window its credit is for" is obscure: "its credit" points back at a Table 1 citation. · medium · "Under the budget, SPIKE-synch dropped the local-gap coincidence window that defines SPIKE-synchronization, and used a fixed window in 4 of 4 folds." · verified yes

**F23** · Undefined jargon, scattered: "threshold picker" (lines 294, 393); "cell-averaging structure" and "guard" in Table 1 (the guard is defined only in 4.3); "circularly shifted", "shifted in time" and "rolled in time" in Table 1 (the reader cannot tell whether these are one operation); "bracketed" (line 444); "vendored" (line 465); "liberal operating point" (line 406); "min_rois… can learn the bench's planted participation levels" (a setting does not learn; tuning fits it). · low–medium · Define each at first use or replace it. Use one name for the shift. For min_rois: "tuning min_rois can fit it to the bench's planted participation levels". · verified yes

**F24** · Small items · (a) Figure 1 caption, "nothing is drawn on it": a house convention that means nothing to this reader. Cut it. (b) Line 336, "+0.000": write "0.000" or "no difference". (c) Line 403, "differs by up to 106 per hour": write "106 false alarms per hour" (the house rule that counts carry units). (d) The text calls itself both "this page" and "this report"; pick one. (e) Line 64, "The sections below explain every term in this paragraph" is a preview; keep only "sections 6 to 8 give the numbers". · low · as stated · verified yes

**F25** · Repetition across sections · "The earlier +0.103 lead is gone… three things changed at once" appears in the Answer and again in sec 10 (lines 381–383), and there it is off the section's topic (tuning, failed refits, overruns). · low · Keep it in the Answer and sec 10, but make sec 10 list the three changes by name and cut the rest of the restatement. · verified yes

## Checked clean
- No banned constructions (tool output plus my own Grep).
- American spelling: 0 British forms found by Grep.
- "Data" is plural: 0 singular uses found.
- Abbreviations defined at first use: ROI, F1, SCE, GPU and P. CPU is the exception (F18).
- No throat-clearing openers and no recap closer. Provenance is metadata only.

I did not open any review record or run record.
