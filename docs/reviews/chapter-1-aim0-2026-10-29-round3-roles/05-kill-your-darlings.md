GRANT 5 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs update/batch, plus Read, Grep, Glob

(Run finding, not an artifact finding: this role came up on a general harness with editing tools. None were used on the repository or on 01-lit. I only read files and ran searches. The run record's `roles:` line should say the review took a fallback path.)

# Role 5: Line editor ("Kill Your Darlings"). Blind verify, round 3

Artifact: `docs/dissertation/chapter-1-aim0.md` (hash a4fbb30e…). Read in full, lines 1–1135.
Banned lists used: the list in `.claude/agents/murderboard/05-kill-your-darlings.md` and the house rules in `docs/writing_conventions.md`: plural "data", no "fire/firing", no "modality", American spelling, percentages say what they are of, name things rather than index them.

## Receipt: `murderboard_prose.sh`

**Who ran it:** the main thread, using the upstream copy (it is not vendored in this worktree). The verbatim output is at `<scratchpad>/mb/prose_r3.txt`. Pasted unchanged:

```

docs/dissertation/chapter-1-aim0.md
  line   construction                       kind   context
  1123   robust                             word   in: - Shah NB, Wainwright MJ (2018). Simple, robust and optimal 

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1         19 words    1 sentences
  3         74 words    3 sentences
  9          3 words    1 sentences
  11         3 words    1 sentences
  13        82 words    4 sentences
  20        99 words    3 sentences
  28        31 words    2 sentences
  31         5 words    1 sentences
  33       128 words    6 sentences   << over 120
  42         2 words    1 sentences
  44       124 words    6 sentences   << over 120
  53       167 words   10 sentences   << over 120
  65        17 words    2 sentences
  67         6 words    1 sentences
  69        43 words    1 sentences
  73       127 words    6 sentences   << over 120
  82        44 words    3 sentences
  86         2 words    1 sentences
  88        18 words    1 sentences
  91       270 words   13 sentences   << over 120
  114       32 words    2 sentences
  117        3 words    1 sentences
  119        8 words    1 sentences
  121       92 words    4 sentences
  128      113 words    2 sentences
  138      154 words    6 sentences   << over 120
  149        3 words    1 sentences
  151      191 words    1 sentences   << over 120
  165        4 words    1 sentences
  167        2 words    1 sentences
  169      205 words   10 sentences   << over 120
  182       24 words    2 sentences
  185      295 words   14 sentences   << over 120
  205       48 words    2 sentences
  210        2 words    1 sentences
  212      286 words   13 sentences   << over 120
  229        4 words    1 sentences
  231      152 words    7 sentences   << over 120
  243      180 words    7 sentences   << over 120
  256      152 words    7 sentences   << over 120
  268       61 words    6 sentences
  273      170 words   10 sentences   << over 120
  286       72 words    2 sentences
  292       11 words    1 sentences
  294      131 words    4 sentences   << over 120
  303      110 words    4 sentences
  311       77 words    3 sentences
  317      116 words    4 sentences
  325        2 words    1 sentences
  327      190 words    8 sentences   << over 120
  340      115 words    4 sentences
  349        8 words    1 sentences
  351        4 words    1 sentences
  353       77 words    2 sentences
  359        8 words    1 sentences
  361       11 words    1 sentences
  363        4 words    1 sentences
  365       23 words    1 sentences
  368        9 words    1 sentences
  370       27 words    1 sentences
  373       10 words    1 sentences
  375       51 words    3 sentences
  380       88 words    5 sentences
  386       46 words    2 sentences
  390        2 words    1 sentences
  392      135 words    6 sentences   << over 120
  402        6 words    1 sentences
  404      104 words    3 sentences
  412       10 words    1 sentences
  414       17 words    1 sentences
  416       72 words    3 sentences
  422        4 words    1 sentences
  424        2 words    1 sentences
  426       69 words    5 sentences
  432       61 words    2 sentences
  437      140 words    6 sentences   << over 120
  447        2 words    1 sentences
  449      148 words    7 sentences   << over 120
  459       43 words    3 sentences
  463       11 words    1 sentences
  465       95 words    5 sentences
  474       16 words    1 sentences
  476      115 words    5 sentences
  484      109 words    4 sentences
  492      123 words    5 sentences   << over 120
  501        9 words    1 sentences
  503      172 words    6 sentences   << over 120
  514      106 words    4 sentences
  522      170 words    6 sentences   << over 120
  533        2 words    1 sentences
  535      215 words   11 sentences   << over 120
  550       63 words    4 sentences
  556      240 words    1 sentences   << over 120
  567       33 words    1 sentences
  570      110 words    1 sentences
  577       91 words    5 sentences
  583      146 words    6 sentences   << over 120
  593        7 words    1 sentences
  595        7 words    1 sentences
  597       33 words    1 sentences
  600        8 words    1 sentences
  602       24 words    1 sentences
  605        7 words    1 sentences
  607        2 words    1 sentences
  609      138 words    7 sentences   << over 120
  618       75 words    4 sentences
  623      127 words    6 sentences   << over 120
  631       66 words    3 sentences
  636       40 words    3 sentences
  640        5 words    1 sentences
  642      108 words    5 sentences
  649       10 words    1 sentences
  651       98 words    1 sentences
  658       34 words    2 sentences
  661       33 words    2 sentences
  664      108 words    1 sentences
  671      246 words    8 sentences   << over 120
  687        8 words    1 sentences
  689       90 words    5 sentences
  697      141 words    6 sentences   << over 120
  706        2 words    1 sentences
  708      173 words    8 sentences   << over 120
  719      329 words   10 sentences   << over 120
  740        2 words    1 sentences
  742      126 words    7 sentences   << over 120
  751        8 words    1 sentences
  753       65 words    3 sentences
  759        9 words    1 sentences
  761       51 words    1 sentences
  766        5 words    1 sentences
  768       70 words    5 sentences
  773       75 words    3 sentences
  779       91 words    4 sentences
  786        2 words    1 sentences
  788      102 words    6 sentences
  796       82 words    3 sentences
  802       11 words    1 sentences
  804       78 words    5 sentences
  811       51 words    2 sentences
  816       99 words    4 sentences
  823        2 words    1 sentences
  825       89 words    8 sentences
  832      320 words   16 sentences   << over 120
  853       53 words    2 sentences
  857       86 words    4 sentences
  864        2 words    1 sentences
  866      117 words    5 sentences
  874       21 words    3 sentences
  877      156 words    1 sentences   << over 120
  888       66 words    3 sentences
  893      138 words    4 sentences   << over 120
  901       14 words    1 sentences
  903        7 words    1 sentences
  905      119 words    1 sentences
  912      129 words    5 sentences   << over 120
  922        3 words    1 sentences
  924       11 words    1 sentences
  926       49 words    2 sentences
  931       81 words    3 sentences
  938       68 words    4 sentences
  944        9 words    1 sentences
  946        7 words    1 sentences
  948      450 words    5 sentences   << over 120
  968       74 words    3 sentences
  975        4 words    1 sentences
  977      123 words    7 sentences   << over 120
  986        3 words    1 sentences
  988      255 words   17 sentences   << over 120
  1010       4 words    1 sentences
  1012     115 words    8 sentences
  1022      60 words    1 sentences
  1027       3 words    1 sentences
  1029      85 words    3 sentences
  1036       4 words    1 sentences
  1038     126 words    5 sentences   << over 120
  1050       4 words    1 sentences
  1052       6 words    1 sentences
  1054      79 words    1 sentences
  1073      19 words    2 sentences
  1078       2 words    1 sentences
  1080      10 words    1 sentences
  1082    1096 words  168 sentences   << over 120
  41 block(s) over 120 words — for each, name its payload sentence and where it sits
```

**Banned-construction hits: one, exempt.** Line 1123, "robust", is in the title of Shah & Wainwright's paper in the reference list. A cited title cannot be reworded, so it stays.

**My own searches, beyond the script:**
- "fire/fires/fired/firing": no hits.
- "modality", "centre", "this data", "the data is/was/has": no hits.
- Singular "data" split across a line break: none. The four uses of "data" (lines 119, 584, 745, 989) all agree with the plural.
- "spike" appears only in names and quotations from the spike-train literature, which are not house prose.
- No *not just X but Y*, no *it's worth noting*, no *In today's*, and no em-dash pivots.
- The contribution and limitation lists hold seven and six items because there are that many things, not three items built for rhythm.

## Passage test: the 41 blocks over 120 words

Tables, list blocks and the reference list are marked n/a. The script counts them as blocks, but they have no single payload.

| block | what it is | payload sentence, and where it sits | what the other words buy | verdict |
|---|---|---|---|---|
| 33 | 1.1 "What brute force found" | "The experiment found three failures it could not explain" (5 of 6) | First definitions of both tools. Needed. | Keep. Could promote. |
| 44 | Fig 1.1 caption | the title (first) | how to read the panels | Keep |
| 53 | the three failures | the bold lead of each item | the evidence | Keep |
| 73 | "For one source, mostly yes" | first | one mechanism per failure; last sentence has a word error (finding 9) | Keep |
| 91 | Contributions | list | — | n/a; duplication noted in finding 10 |
| 138 | generative model | "a cluster process of the Neyman–Scott type" (first) plus "Two departures…" (last) | The Thomas (1949) aside buys a correct attribution and nothing else. | Keep (footnote candidate) |
| 151 | Table 1.1 | — | — | n/a |
| 169 | Fig 1.2 caption | title | Last sentence admits the minute was picked, which buys honesty. | Keep |
| 185 | tools list | each bullet front-loaded | needed definitions | Keep |
| 212 | Fig 1.3 caption | title | the worked example in C earns its length | Keep |
| 231 | prior work, bin widths | "uniform jitter" (mid) | precedents | Keep |
| 243 | prior work, cumulants | "That is the joint fit's construction…" (**last**) | precedents; the Ehm/Reimer sentence rests on two unread sources | Promote the last sentence |
| 256 | prior work, cluster processes | list of precedents | — | Keep |
| 268–273 | prior work, assemblies and order | — | Assemblies paragraph: see finding 12 | — |
| 294 | first experiment | first | Last sentence (rerun with fresh seeds) is evidence. | Keep |
| 327 | Fig 1.4 caption | title; the real finding, "only the 20-cell row is resolved from 0.2 s up", is sentence 7 | — | Minor: move it to the title |
| 392 | Fig 1.5 caption | title | — | Keep |
| 437 | 1.4.4 residual counts | "the hard-core form overpredicts participants by about 1 %" (**last**) | the counting argument | Promote (finding 5) |
| 449 | Fig 1.7 caption | title | — | Keep |
| 492 | slow-stream miss | "This residual is unexplained." (last) | Ending here works. | Keep |
| 503 | joint-fit setup | first two sentences | honest limits | Keep |
| 522 | correlogram vs joint fit | bold sentence 6 of 7 | last sentence is off-topic | Promote and cut (finding 4) |
| 535 | Fig 1.8 caption | title | — | Keep |
| 556 | Table 1.2 | — | — | n/a |
| 583 | true event train | "it matters little if the analyst assumes the 20 s hard core" (3 of 6) | — | Keep |
| 609 | Fig 1.9 caption | title | — | Keep |
| 623 | chance-cluster budget | "A threshold therefore has to be set per recording from its own background." (5 of 6) | Holds the 7–16 vs 1–8 clash (finding 1). | Promote |
| 671 | 1.5.2 bullets | each bullet front-loaded | — | Keep; one number clash (finding 7) |
| 697 | "The two sides are not given the same information" | first | — | Keep |
| 708 | Fig 1.10 caption | title | — | Keep |
| 719 | separation bullets | the bold leads | — | Keep |
| 742 | Fig 1.11 caption | title | One clause says the same thing twice. | Minor trim |
| 832 | closed-form bullets | "No order" bullet: "the mean of F is exact for every N, k and E" (first) | Six precedent sentences repeat Table 1.6. | Cut (finding 6) |
| 877 | Table 1.4 | — | — | n/a |
| 893 | frame rounding | "Rounding does not cost power at realistic jitter" (3 of 4) | — | Keep; number clash (finding 8) |
| 912 | Copeland | "found no ranking sort and no analytical null" (last) | Two optimality results that do not apply buy nothing for the argument. | Cut to one clause (finding 13) |
| 948 | Table 1.6 | — | — | n/a |
| 977 | 1.8.3 two sources | "may therefore need higher orders…" (5 of 7) | — | Keep; the first sentence repeats 1.7 (finding 10) |
| 988 | Limitations | list | — | Keep |
| 1038 | About this chapter | — | — | Keep |
| 1082 | References | — | — | n/a |

## Findings

Columns: location · issue · severity · suggested fix · verified against a source (yes/no).

1. **1.2.1, "1–8 coordinated events per recording window"; 1.5.1, "against the 7–16 coordinated events a realistic recording holds"; 1.7.2, "a realistic recording window holds 1–8"; 1.8.1, "at 7–16 events" and "One to three events of 7 cells"; 1.8.3, "than a realistic recording window often holds".** · Two counts are each called what "a realistic recording" holds, and they differ by a factor of five. "Recording window" is never defined or set apart from the 45-minute recording. The chapter's two practical verdicts, that participants can be read and that order cannot, rest on these two different sizes. A reader cannot tell whether one real recording supports the first verdict, the second, or both. · **major** · Define "recording window" once in 1.2.1: its duration, and why it is shorter than 45 minutes. Then use one phrase per quantity in every place listed. In 1.5.1, say which count the one-per-hour budget is set against. · no (the goal page does not contain the phrase "recording window", so it could not be traced)

2. **One prediction under two names:** "full prediction" (Fig 1.5 caption, Fig 1.6 title and caption, Fig 1.7 caption) and "hard-core form" (1.4.4 last sentence, 1.4.5, Fig 1.8 caption). · The first time the hard-core form is named as a prediction is the last sentence of 1.4.4, where it shows up without definition as the subject of the key result. Figure 1.6 also contrasts the "full prediction" with "a Poisson event train". A cold reader has three labels for two things. · **major** · At 1.4.3, name it once: "the hard-core form (with the at-most-one-event term)". Replace "full prediction" everywhere, including the figure titles, which are regenerated from `ch1_new_figures.py`. · no

3. **1.9 Conclusion.** · It recaps the three grid failures, almost word for word from 1.1 ("The question, and the answer") and line 65 ("A grid can find such failures…"). Its last sentence repeats the end of 1.8.3. The house voice bans a closing recap. Worse, it recaps the wrong thing: it leaves out the result that matters most for the rest of the dissertation. At realistic values, participants can be read from one recording, jitter on the fast stream cannot, and an order test needs more events than a recording window holds (1.8.1). · **major** · Either cut 1.9, or replace it with the one thing the chapter changes for Chapter 2: what realistic recordings can and cannot support, with the numbers. Drop the restated failures. · no

4. **1.4.6, block 522, "Against the correlogram tool…".** · The payload, "per recording, the joint fit is the better estimator at the busier background from 0.5 s up", sits sixth of seven sentences, after three qualifications that switch between per-recording, pooled and Gaussian use. "Reads 0.05–0.2 s jitter as well as the joint fit or better, though at 0.05 s often only as 'below the curve'" contradicts itself: a width below the calibration curve yields no estimate (Table 1.2: 8 and 15 recordings). The last sentence, about the assessor, is off-topic. · minor · Open with the bold verdict. Say "at 0.05 s it often gives no estimate (width below the curve)". Move the assessor sentence to 1.5.2, where it is already stated. · yes (Table 1.2 in the chapter)

5. **1.4.4, block 437, "The prediction is close but not exact…".** · The finding, a 1 % overprediction with sign test p = 0.007, comes last, after a mid-sentence aside ("not the 2.4 a normal error would give, because…") that reads at first as if 2.4 were the expected count. · minor · First sentence: "The hard-core form overpredicts participants by about 1 % (24 of 32 conditions below, p = 0.007)." Then give the beyond-2-SE counts, with the heavy-tails point as its own sentence. · no

6. **1.7.2, "No order" bullet (lines 839–851).** · About 240 words in one bullet, with the line break broken at line 850, which is far over length. After the exact-mean result it runs through Kendall's W, Durbin and Skillings–Mack, Kreuz's rejected null, and Silva et al. Every one of those is repeated in Table 1.6, and Silva et al. appears for the third time (1.2.3, here, and Table 1.6). The sentence that matters, "Only the mean is derived, not the spread, which is what detection depends on", is buried in the second-to-last position. · minor · Keep the result, the asymptote, the 33-of-33 check and the only-the-mean caveat. Move the lineage to Table 1.6, which already holds it, keeping at most the Kreuz sentence because it explains why an exact mean is worth having. Fix the line break. · yes (Table 1.6 rows "exact no-order mean" and "score sort")

7. **1.5.2: predicted chance share "0.89–0.96 at K = 3 and 0.79–0.92 at K = 4" vs the bullet's "85–93 % of clusters are chance clusters".** · Two ranges for what reads as the same quantity, with no label saying which is predicted and which is measured. · minor · Label the bullet "measured" (or "predicted") and give K. · no

8. **1.7.2, frame rounding: "power rises from 0.91 to 0.99" vs Table 1.4's 0.89 (13 cells, 3 events, r = 2.5).** · The same condition has two power values in the text. The 0.91 is 0.909 from the rounding run's 2,000 recordings. The 0.89 is the table's 300 recordings. Both are correct, but the chapter never reconciles them. In the same paragraph, "falls by 5.2 % (SE 0.08 %)" is a relative change that is not labeled as one, which breaks the house rule that a percentage says what it is a percentage of. · minor · Add "(2,000 recordings; Table 1.4's 0.89 is from 300)". Write "falls by 5.2 % of its value". · yes (`docs/learned/synthetic_validation/ch1_followups/order_rounding.txt` line 2; `order_power.txt` lines 21–22)

9. **1.1, "For cell-by-cell structure it derives two means, the excess variance that reused cell groups add and the order indicator's mean".** · A variance ratio is not a mean, so the sentence does not say exactly one true thing. · minor · "derives two quantities: the excess variance… and the order indicator's mean…" · no

10. **Repetition across sections.**
    - The two-source claim appears almost verbatim in 1.7 (line 753) and 1.8.3 (line 978).
    - "invisible to the population-count tools by construction" appears at lines 755 and 776–777.
    - "No human has reviewed" and "exercise" appear in the front note, in 1.8.4 item 6 and in *About this chapter*.
    - Each contribution's standing appears three times: in the italic tags under Contributions, in 1.2.3, and in Table 1.6.

    · minor · State each once. 1.7 can point to 1.8.3. Keep the Contributions tags to a few words and let Table 1.6 hold the precedents. · no

11. **Symbols reused with different meanings.**
    - g is the within-cell minimum interval (1.6), and g₂, g₃, g_n are window sharing.
    - e is "planted events per minute" in the same sentence as e^(−3b) (1.5.2, lines 654–655), and e is also "events per assembly" (1.7.1).
    - c is the chance-cluster rate (1.5.2) and also the constant c(N, k) (1.7.2).
    - Kish's b̄ sits beside the background rate b.

    · minor · Rename the minimum interval (for example d_min, and not "refractory", which brings in a spike prior) and the events-per-minute rate (for example λ_min, since λ is already the event rate). Add both to Table 1.1. · no

12. **1.2.3, Assemblies paragraph.** · Seven citations, five marked ⚠, on PCA assembly detection with a Marčenko–Pastur null. The chapter's assembly test is a shuffle test on the membership matrix. The PCA line becomes relevant only in a "Further out" item in 1.8.5, and the paragraph never says why it is here. · minor · Cut it to one sentence tied to that next step, or say how the PCA method relates to the margin-preserving null. · no

13. **1.7.2, block 912, Coppersmith/Shah sentence.** · Two optimality results are introduced only to say they do not apply. The words buy thoroughness, not evidence. · minor · "No optimality result covers net-win ranking with unequal co-participation and dependent within-event signs (Coppersmith et al. 2006; Shah & Wainwright 2018)." · no

14. **Small precision and grammar fixes.**
    - 1.3, "added the joint fit, the per-estimate noise and when the tool refuses, …": the list items do not parse. Use semicolons, or "the conditions under which the tool refuses".
    - 1.3: "k̂" is listed as a result before 1.4.1 defines it.
    - 1.4.6, "On data that law is unknown": write "On a real recording the interval law is unknown…".
    - 1.6, "Three derivations answer it": the likelihood-ratio separations are fitted tests checked against simulated nulls, not derivations. Write "Three analyses".
    - 1.6: "These are the power of particular tests" should be "These are separations reached by particular tests".
    - 1.6, "scored by the separation at which they report a pair as two half as often as they ever will": write "at which the chance of reporting the pair as two reaches half its plateau".
    - 1.8.1: "Nbw" is undefined. Say it is the expected background onsets per window.
    - "isolated-pair prediction" (1.8.1) vs "isolated-event prediction π_K" (1.8.5): pick one.
    - The table after line 567 has no number or caption, so the order runs Table 1.2, an unlabeled table, Table 1.3. Number it and put the caption above it. (Boundary: role 10 owns the mechanical table check. This is the prose side only.)

    · minor · as listed · no

## Verdict

**Not ready to sign off yet, but close.** The house banned list is clean: one hit, and it is exempt as a cited title. Line by line the prose is in the house voice: short, concrete, and willing to say what it does not know (for example, "This residual is unexplained"; "was not run"). I would sign once findings 1–3 are fixed:
- the two undefined counts of what "a recording" holds, which carry the chapter's practical verdicts;
- one prediction under two names;
- a conclusion that recaps the grid failures instead of stating what realistic recordings support.

Findings 4–6 are payload-promotion edits, each a few minutes' work. Everything else is minor.

What I checked:
- the whole chapter, every block over 120 words, every list, and the captions;
- the agent's banned list and the house rules in `docs/writing_conventions.md`;
- the source lines behind findings 6 and 8.

I did not open anything under `docs/reviews/` or the git history.
