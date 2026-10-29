GRANT 5 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update (none of these were used; this review used only Read and Grep)

**Note on the run:** the brief said my grant has no shell. That is not true for this session: Bash and PowerShell were both present. I did not use them. The prose receipt below is the main thread's run, not mine. Record this as a fallback-path spawn: the role did not run as a named agent with its declared grant.

# Role 5: Line editor ("Kill Your Darlings"). Chapter 1, blind verify, round 2

Artifact: `docs/dissertation/chapter-1-aim0.md` (hash cdc8fbf6…). Banned lists run: `.claude/agents/murderboard/05-kill-your-darlings.md` and `docs/writing_conventions.md` (plural *data*; no *fire*; no *modality*; American spelling; name things rather than index them).

## Receipt: `murderboard_prose.sh`, run by the main thread (upstream copy), verbatim from `<scratchpad>/mb/prose_r2.txt`

```
docs/dissertation/chapter-1-aim0.md
  line   construction                       kind   context
  838    robust                             word   in: - Shah NB, Wainwright MJ (2018). Simple, robust and optimal 

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1         19 words    1 sentences
  3         23 words    1 sentences
  6          3 words    1 sentences
  8          3 words    1 sentences
  10        82 words    4 sentences
  17        99 words    3 sentences
  25        31 words    2 sentences
  28         5 words    1 sentences
  30        52 words    3 sentences
  35         2 words    1 sentences
  37       111 words    6 sentences
  45       141 words    4 sentences   << over 120
  54        17 words    2 sentences
  56         6 words    1 sentences
  58        43 words    1 sentences
  62        93 words    4 sentences
  69         2 words    1 sentences
  71       204 words   14 sentences   << over 120
  87        46 words    2 sentences
  91         3 words    1 sentences
  93         8 words    1 sentences
  95       126 words    5 sentences   << over 120
  104      154 words    6 sentences   << over 120
  115        3 words    1 sentences
  117      189 words    1 sentences   << over 120
  131        4 words    1 sentences
  133        2 words    1 sentences
  135      205 words   10 sentences   << over 120
  148       24 words    2 sentences
  151      190 words    7 sentences   << over 120
  165       32 words    1 sentences
  168       20 words    1 sentences
  171        4 words    1 sentences
  173      151 words    7 sentences   << over 120
  185       80 words    3 sentences
  191      112 words    5 sentences
  200       34 words    3 sentences
  204       81 words    5 sentences
  211       11 words    1 sentences
  213      131 words    4 sentences   << over 120
  222       77 words    3 sentences
  228       76 words    3 sentences
  234        8 words    1 sentences
  236        4 words    1 sentences
  238       23 words    1 sentences
  241        9 words    1 sentences
  243       27 words    1 sentences
  246       10 words    1 sentences
  248       51 words    3 sentences
  253       88 words    5 sentences
  259        2 words    1 sentences
  261      133 words    6 sentences   << over 120
  270        6 words    1 sentences
  272       66 words    2 sentences
  277       10 words    1 sentences
  279       17 words    1 sentences
  281       79 words    4 sentences
  288        9 words    1 sentences
  290       27 words    1 sentences
  293        8 words    1 sentences
  295       68 words    3 sentences
  300        4 words    1 sentences
  302        2 words    1 sentences
  304       69 words    5 sentences
  310       61 words    2 sentences
  315      113 words    5 sentences
  323       39 words    3 sentences
  327       11 words    1 sentences
  329       72 words    4 sentences
  336       16 words    1 sentences
  338      113 words    5 sentences
  346      138 words    5 sentences   << over 120
  355        9 words    1 sentences
  357       79 words    4 sentences
  363      106 words    4 sentences
  371       79 words    4 sentences
  377       32 words    3 sentences
  381      149 words    1 sentences   << over 120
  392      119 words    6 sentences
  400        8 words    1 sentences
  402       33 words    1 sentences
  405        8 words    1 sentences
  407       36 words    1 sentences
  410        7 words    1 sentences
  412        2 words    1 sentences
  414      136 words    8 sentences   << over 120
  423      157 words    7 sentences   << over 120
  433       54 words    3 sentences
  438       40 words    3 sentences
  442        8 words    1 sentences
  444       37 words    2 sentences
  448        8 words    1 sentences
  450       51 words    1 sentences
  455        5 words    1 sentences
  457       70 words    5 sentences
  462       75 words    3 sentences
  468        2 words    1 sentences
  470      102 words    6 sentences
  478      101 words    4 sentences
  485       11 words    1 sentences
  487       51 words    2 sentences
  492       82 words    4 sentences
  498        2 words    1 sentences
  500       89 words    8 sentences
  507      239 words   12 sentences   << over 120
  523       53 words    2 sentences
  527       55 words    3 sentences
  532        2 words    1 sentences
  534      155 words    7 sentences   << over 120
  544       21 words    3 sentences
  547      156 words    1 sentences   << over 120
  558       89 words    4 sentences
  564       41 words    2 sentences
  568       89 words    1 sentences
  575      138 words    6 sentences   << over 120
  586        8 words    1 sentences
  588       61 words    3 sentences
  594        2 words    1 sentences
  596      145 words    6 sentences   << over 120
  606      235 words    8 sentences   << over 120
  620        2 words    1 sentences
  622       82 words    6 sentences
  628       11 words    1 sentences
  630      102 words    3 sentences
  638       77 words    3 sentences
  645        2 words    1 sentences
  647      129 words    5 sentences   << over 120
  656       78 words    4 sentences
  662        3 words    1 sentences
  664        9 words    1 sentences
  666      385 words    4 sentences   << over 120
  683      100 words    4 sentences
  692        4 words    1 sentences
  694      119 words    7 sentences
  703        7 words    1 sentences
  705       47 words    2 sentences
  709      125 words    4 sentences   << over 120
  718       37 words    2 sentences
  724        3 words    1 sentences
  726      127 words   11 sentences   << over 120
  740        4 words    1 sentences
  742       99 words    8 sentences
  750       61 words    1 sentences
  755        3 words    1 sentences
  757      127 words    5 sentences   << over 120
  766        4 words    1 sentences
  768      117 words    4 sentences
  779        4 words    1 sentences
  781        6 words    1 sentences
  783       55 words    1 sentences
  798       19 words    2 sentences
  803        2 words    1 sentences
  805       10 words    1 sentences
  807      733 words  116 sentences   << over 120
  26 block(s) over 120 words — for each, name its payload sentence and where it sits
```

(The tool's line numbers are block starts. Its hit at "line 838" is the Shah & Wainwright reference.)

**Banned-construction result.** There is one hit: *robust*, inside a cited paper's title ("Simple, robust and optimal ranking…"). That is someone else's words and it stays, so it is not a defect. I also searched by hand with Grep and found none of the following: em-dashes, *it's worth noting*, *not just/not only*, *In today's*, singular *data* (including matches split across lines, read for), *fire/firing*, *modality*, British spellings (centre, labell-, modell-, analyse, colour). Line 616 has a plural *data* that misparses; see F9.

## Passage test: the 26 flagged blocks

Five flagged blocks are tables or reference lists, not prose: 117 (Table 1.1), 381 (Table 1.2), 547 (Table 1.3), 666 (prior-art table) and 807 (references). The word count does not apply to them.

| block | payload sentence | where it sits | what the other words buy | verdict |
|---|---|---|---|---|
| 45 | the two bold leads ("A fixed threshold does not transfer…"; "…reads jitter only at the quieter background") | first, in each bullet | the numbers a skeptic would ask for | keep |
| 71 | the bold lead of each contribution | first, in each item | definitions | keep; see F12 on item 2 |
| 95 | "They serve only to choose where to simulate; no statement in this chapter is about the recordings themselves." | middle | the realistic values, which are needed | keep; see F7 ("bench") |
| 104 | "Two departures from the textbook process matter: …fixed, not Poisson… hard-core train" | last | the Thomas (1949) aside buys pedantry, not evidence | trim (F11) |
| 135 | "A 1 s window border splits event 1 into 4 and 6, while event 2 falls inside one window at every width." | middle | instructions for reading the panels | acceptable for a caption; "(σ is its SD)" repeats Table 1.1, so cut it |
| 151 | one sentence per tool, defining what it counts | first, in each bullet | the parenthetical about how the figures label the share is a patch over a naming problem | F1 |
| 173 | "Louis, Borgelt & Grün (2010)… gave the full distribution of the population count for groups with uniform jitter" | middle | the lineage, which a committee needs | keep |
| 213 | "it was rerun with a seed per recording, and every number here is from the rerun" | last | the grid definition | keep; the payload could lead |
| 261 | "B: participants reported over planted… from k̂ = 2 + (k − 2) g₃/g₂" | middle | the caption uses "at-most-one-event term" before 1.4.2 defines it | F10 |
| 346 | "The general form predicts the tool to within 0.01–0.04 at every window." | middle | the setup; "These recordings" has no antecedent | F4, F8 |
| 414 | "one fixed threshold cannot serve both backgrounds" | late | repeats block 423 almost word for word | F3 |
| 423 | "This explains the first failure." | middle, after five numbers | the evidence, which is needed | promote: "The formula explains the first failure: predicted 0.256…" |
| 507 | per bullet: F = (2/π) arctan r; signal ∝ 1/√M; the exact no-order mean | first, in each bullet | the lineage (Kendall–Babington Smith, Durbin, Skillings–Mack) duplicates the 1.9.1 table and buries "Only the mean is derived, not the spread, which is what detection depends on" | F6 |
| 534 | "two templates need more than five" (the figure title) | title | the caption body restates Table 1.3 and the paragraph after it | F3, F2 |
| 575 | "Kreuz et al. … describe the finite-size effect… they do not give a formula for it." | first | the optimality caveats, which are needed; "Copeland ranking" repeats 1.6.2 | minor trim |
| 596 | the 80%/50% separation markers against cells per event | first | the legend | acceptable caption |
| 606 | "So between about 0.5 and 2.5 s the tools merge pairs the tests could separate." | **last, as a third bullet** | the evidence | promote it to the section's opening sentence (F9) |
| 647 | "For one source, theory predicts the coordination-rates tool, the assessor's chance clusters, and what each window can and cannot read." | first | — | keep, but see F3 on 1.1/1.8/1.10 |
| 709 | "a consistency check, not independent review" | middle | the list of what the rederivations added, which is fine | keep |
| 726 | numbered limitations | — | — | keep |
| 757 | the Chapter 2 hand-off (last sentence) | last | a recap of 1.1 and 1.8 | F3 |

## Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| F1 | 1.2.2, l.155–157: "the coordinated share, the rate of coordinated onsets per cell, λk/N. (As a ratio to planted, that share is the same as the fraction…)" | A "share" defined as a rate in Hz. The parenthetical admits that the word and the figure labels mean different things. The term recurs in 1.1, 1.4.4 and the Figure 1.1 caption ("coordinated share"). | major | Name the quantity for what it is: *coordinated rate per cell, λk/N*. Or define the share as the coordinated fraction of onsets and label the figures to match. Then delete the parenthetical. | yes (the chapter's own text) |
| F2 | 1.6.2, l.560: "one template is detected at three events when r ≥ 2.5, and two need five or more" | This contradicts the Figure 1.8 title ("two templates need more than five") and Table 1.3, where the best two-template power at 5 events is 0.77, below 0.8. "Five or more" says five suffices. | major | "…and two templates are not detected reliably at any count up to five." | yes (Table 1.3 in the chapter) |
| F3 | 1.1 "The question, and the answer" (l.62–67); 1.8 (l.630–660); 1.10 (l.757–764) | The same three-part claim is stated three times: the two failures explained, k̂ to 1–2%, the joint fit better from 0.5 s, and "the tools, not the data, limit…". The house voice forbids a closing recap. The same pattern recurs at small scale: the Figure 1.5 caption repeats l.426–429 (safe threshold 5 and 8, "one fixed threshold cannot serve both"), and the Figure 1.8 caption repeats Table 1.3 and l.558–560 ("at one event no test has power" appears twice). | major | Keep 1.8 as the argument. Cut 1.10 to its first and last sentences: the brute-force line and the Chapter 2 hand-off. Cut the results sentences from the Figure 1.5 and 1.8 captions, or from the body; each claim should be made once. | yes |
| F4 | 1.4.5, l.349: "0.0099 Hz, which makes these trains denser than the hard-core trains above" | As written this is false for the 45-event arm (45/2700 s = 0.0167 Hz > 0.0099 Hz). What is presumably meant is that the trains contain intervals shorter than 20 s. | major | "…0.0099 Hz; unlike the hard-core trains, these allow intervals shorter than 20 s, so two events can share a window." | yes (arithmetic from the chapter's Table 1.1) |
| F5 | 1.4.6, l.374: "The joint fit is the better estimator from about 0.5 s up, and at the busier background." | Overstates Table 1.2. At 0.05 Hz and 0.2 s, the joint fit's IQR [0.65, 1.13] is wider than the correlogram's [0.83, 1.01]. | minor | "…from about 0.5 s up at either background." | yes (Table 1.2) |
| F6 | 1.6.2 "No order" bullet, l.513–521 | The bullet makes four claims and gives three lineages. The limitation that matters most ("Only the mean is derived, not the spread, which is what detection depends on") is the second-to-last sentence. The Kendall-W, Durbin and Skillings–Mack lineage is already in the 1.9.1 table. | minor | Move the lineage to 1.9.1. Lead the bullet with "The mean of F under no order is exact…; its spread is not derived." | yes |
| F7 | 1.2.1, l.101–102 "the bench's middle participation levels"; 1.8 caption l.651 "fast and slow bench levels"; 1.3 "shipped windows"; 1.8 "two of the six ported detectors"; 1.8 "Nbw" | Undefined jargon: "bench", "ported", "shipped", the six detectors, and the dimensionless group Nbw are never introduced. A committee member has no way to decode them. | minor | Define "bench" once, or replace it with "the lab's mid-range participation levels". Say what the six detectors are and where they were ported from, or drop the count. Gloss Nbw as "expected background onsets per window across the field". | yes |
| F8 | 1.4.5, l.346–347: "On event trains with realistic intervals the difference is large. These recordings were simulated…" | "These recordings" has no antecedent. | minor | "Recordings with realistic trains were simulated with renewal trains…" | yes |
| F9 | 1.7, l.616: "The data set only the plateau, π_K²" | Garden path: "data set" reads as the noun *dataset*. Separately, the section's payload ("between about 0.5 and 2.5 s the tools merge pairs the tests could separate") sits last, as a bullet of its own. It also omits the count detector's 5 s. | minor | "Only the plateau, π_K², depends on the data." Open 1.7 with the payload sentence, adding "(5 s for the count detector)". | yes |
| F10 | Figure 1.3 caption, l.267: "the full prediction, which adds the at-most-one-event term" | A forward reference: the term is defined in 1.4.2, after the figure. | minor | Add "(1.4.2)", or define it in a clause: "the correction for no two events sharing a window". | yes |
| F11 | 1.2.1, l.105–107: "although Thomas (1949) gave only the count distribution… with no spatial scatter law" | A historical aside that adds nothing a reader needs in order to follow the model. | minor | Move it to a footnote or the reference annotation, or cut it. | yes (the chapter's own text; Thomas not reopened) |
| F12 | 1.1 Contributions, item 2: "including the dependence of the tool's surrogates on the event train" | Opaque at first reading: surrogates are not defined until 1.2.2. | minor | "…including the way the tool's time-shifted surrogates still carry part of the event train". | yes |
| F13 | 1.4.4, l.315–317: "about 6 of the 48… would sit beyond 2 standard errors, because the standard error of a median of 5 values is heavy-tailed" | Elliptical. The reader has to infer that 6 is the corrected expectation in place of roughly 2.4 under normality. | minor | "…would sit beyond 2 standard errors, not the 2–3 a normal error gives, because…" | yes |
| F14 | 1.4.5, l.338: "The 1 % overprediction goes as a direction" | An unclear idiom. | minor | "The 1 % overprediction no longer has a consistent sign:" | yes |
| F15 | 1.3, l.226: "the medians exclude those, and the predictions cannot" | Ambiguous: cannot exclude them, or cannot refuse? | minor | "…the medians exclude them; the predictions, computed per setting, include every recording." (The author should confirm which is meant.) | no (intent unclear) |
| F16 | 1.6.2, l.560–562 ("The earlier record's power at 10 and 25 events… it is not quoted here") and l.564 ("An earlier analysis of real recordings found…") | Record-keeping that a committee reader cannot place. The first explains why a number is absent. The second cites an analysis with no reference. | minor | Cut the first, or move it to *About this chapter*. Give the second a citation or file path, or cut it. | no (source not identified) |
| F17 | l.3: "How it was made, and what it does not claim, is in the note at the end." | A preview, which the house voice forbids. The end note also says little about what the chapter does not claim; that is 1.8 and 1.9.4. | minor | Cut the second sentence, or point it to 1.9.4. | yes |

## What I would need before signing off

- **Must fix:** F1, F2, F3 and F4. Each is either a sentence that asserts something false or ambiguous, or the same claim made three times.
- **Should fix:** the remaining minors. They are mostly one-line repairs.

On style, the chapter's sentences are short, concrete and largely clean. The banned list and the house conventions are clear apart from the one quoted title. The cost is in repetition between sections and in payloads buried mid-block (1.5 l.426, 1.7 l.618), not in padding within sentences.
