> **Public copy.** Lines that concern real treatment recordings are removed (13 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 5 ok — Read, Grep, Glob

# Role 5 (line editor) review: detector_review

**Tool provenance.** The main thread ran `murderboard_prose.sh` from the upstream syncytium2/murderboard clone at 81a0927, and I read its output. The script is **not vendored** in bugarach, so this run cannot be reproduced from the repo alone. It used upstream's default banned list: *not just X but Y* · *it's not about A, it's about B* · *it's worth noting* · delve / leverage / robust / seamless / crucial / landscape / tapestry · *In today's ___*. The lists built for rhythm and the em-dash pivots can't be found by search, so I checked those by hand.

## Scan output, pasted verbatim

```
<scratchpad>/review/detector_review_plain.txt
  line   construction                       kind   context
  — no banned construction found

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1          2 words    1 sentences
  3          2 words    1 sentences
  5         24 words    1 sentences
  7         64 words    5 sentences
  9         67 words    5 sentences
  11         1 words    1 sentences
  13         2 words    1 sentences
  15         5 words    1 sentences
  17         5 words    1 sentences
  19         4 words    1 sentences
  21         4 words    1 sentences
  23         8 words    1 sentences
  25         7 words    1 sentences
  27         4 words    1 sentences
  29         8 words    1 sentences
  31         6 words    1 sentences
  33         6 words    1 sentences
  35         5 words    1 sentences
  37         3 words    1 sentences
  39        58 words    4 sentences
  41        33 words    3 sentences
  43        48 words    5 sentences
  45        50 words    5 sentences
  47       117 words   10 sentences
  49         6 words    1 sentences
  51         4 words    1 sentences
  53        21 words    2 sentences
  55         1 words    1 sentences
  57        27 words    2 sentences
  59         1 words    1 sentences
  61        30 words    2 sentences
  63         1 words    1 sentences
  65        20 words    2 sentences
  67         1 words    1 sentences
  69        22 words    2 sentences
  71         2 words    1 sentences
  73        14 words    1 sentences
  75         1 words    1 sentences
  77        17 words    2 sentences
  79         1 words    1 sentences
  81        22 words    2 sentences
  83         1 words    1 sentences
  85        25 words    2 sentences
  87         2 words    1 sentences
  89        18 words    1 sentences
  91         4 words    1 sentences
  93        28 words    3 sentences
  95         4 words    1 sentences
  97        45 words    5 sentences
  99         1 words    1 sentences
  101       26 words    2 sentences
  103        2 words    1 sentences
  105       31 words    2 sentences
  107        3 words    1 sentences
  109       43 words    4 sentences
  111        6 words    1 sentences
  113       41 words    4 sentences
  115       65 words    5 sentences
  117        7 words    1 sentences
  119       33 words    3 sentences
  121       50 words    5 sentences
  123       18 words    2 sentences
  125      290 words   21 sentences   << over 120
  127       97 words    7 sentences
  129        5 words    1 sentences
  131       60 words    4 sentences
  133       15 words    1 sentences
  135       26 words    2 sentences
  137       83 words    5 sentences
  139       10 words    1 sentences
  141       26 words    1 sentences
  143       36 words    1 sentences
  145       32 words    1 sentences
  147       30 words    1 sentences
  149       35 words    1 sentences
  151       37 words    1 sentences
  153        2 words    1 sentences
  155       59 words    5 sentences
  157       90 words    6 sentences
  159        1 words    1 sentences
  161       19 words    3 sentences
  163        1 words    1 sentences
  165       38 words    2 sentences
  167        2 words    1 sentences
  169      101 words    6 sentences
  171      110 words    8 sentences
  173        1 words    1 sentences
  175       26 words    2 sentences
  177        1 words    1 sentences
  179       47 words    3 sentences
  181        2 words    1 sentences
  183       88 words    7 sentences
  185       60 words    6 sentences
  187        1 words    1 sentences
  189       33 words    3 sentences
  191        1 words    1 sentences
  193       38 words    3 sentences
  195        3 words    1 sentences
  197       65 words    6 sentences
  199       91 words    7 sentences
  201        1 words    1 sentences
  203       34 words    3 sentences
  205        1 words    1 sentences
  207       32 words    2 sentences
  209        2 words    1 sentences
  211      102 words    6 sentences
  213       58 words    4 sentences
  215       67 words    5 sentences
  217        1 words    1 sentences
  219       27 words    3 sentences
  221        1 words    1 sentences
  223       36 words    2 sentences
  225        2 words    1 sentences
  227      112 words    7 sentences
  229       89 words    7 sentences
  231        1 words    1 sentences
  233       28 words    2 sentences
  235        1 words    1 sentences
  237       60 words    3 sentences
  239        5 words    1 sentences
  241       85 words    5 sentences
  243       21 words    1 sentences
  245        5 words    1 sentences
  247       27 words    2 sentences
  249       38 words    2 sentences
  251       47 words    3 sentences
  253       28 words    2 sentences
  255       27 words    1 sentences
  257       29 words    1 sentences
  259       21 words    1 sentences
  261        3 words    1 sentences
  263        6 words    1 sentences
  265       86 words    7 sentences
  267      134 words   11 sentences   << over 120
  269        1 words    1 sentences
  271       25 words    3 sentences
  273        1 words    1 sentences
  275       59 words    4 sentences
  277        9 words    1 sentences
  279       45 words    3 sentences
  281       54 words    4 sentences
  283       55 words    4 sentences
  285       35 words    3 sentences
  287       32 words    4 sentences
  289       86 words    4 sentences
  291      232 words   16 sentences   << over 120
  293       80 words    5 sentences
  295        8 words    1 sentences
  297        4 words    1 sentences
  299      100 words    7 sentences
  301       45 words    2 sentences
  303        6 words    1 sentences
  305      120 words    7 sentences
  307       34 words    3 sentences
  309        9 words    1 sentences
  311       72 words    4 sentences
  313      110 words   14 sentences
  315        5 words    1 sentences
  317       21 words    2 sentences
  319       62 words    4 sentences
  321       79 words    6 sentences
  323       33 words    2 sentences
  325      109 words    7 sentences
  327       11 words    1 sentences
  329       69 words    3 sentences
  331       41 words    3 sentences
  333       19 words    1 sentences
  335       50 words    4 sentences
  337       32 words    3 sentences
  339      118 words   10 sentences
  341       22 words    1 sentences
  343        3 words    1 sentences
  345        1 words    1 sentences
  347        1 words    1 sentences
  349        1 words    1 sentences
  351        2 words    1 sentences
  353        1 words    1 sentences
  355        1 words    1 sentences
  357        2 words    1 sentences
  359        2 words    1 sentences
  361        2 words    1 sentences
  363        2 words    1 sentences
  365        2 words    1 sentences
  367        2 words    1 sentences
  369       81 words    6 sentences
  371        9 words    1 sentences
  373       36 words    4 sentences
  375       99 words    4 sentences
  377       97 words    4 sentences
  379       59 words    4 sentences
  381       75 words    5 sentences
  383      116 words    7 sentences
  385       67 words    6 sentences
  387      121 words    8 sentences   << over 120
  389       38 words    4 sentences
  391      102 words    5 sentences
  393        7 words    1 sentences
  395        8 words    1 sentences
  397       38 words    1 sentences
  399       40 words    1 sentences
  401       45 words    1 sentences
  403       38 words    1 sentences
  405       40 words    1 sentences
  407       37 words    1 sentences
  409       43 words    1 sentences
  411       33 words    1 sentences
  413       16 words    1 sentences
  415       22 words    1 sentences
  417       24 words    2 sentences
  419        7 words    1 sentences
  421       19 words    3 sentences
  423       51 words    3 sentences
  425       30 words    3 sentences
  427       23 words    3 sentences
  429       27 words    2 sentences
  431        6 words    1 sentences
  433       41 words    4 sentences
  435      121 words   15 sentences   << over 120
  437       46 words    7 sentences
  439       34 words    4 sentences
  441       42 words    6 sentences
  443       43 words    2 sentences
  445       27 words    1 sentences
  5 block(s) over 120 words — for each, name its payload sentence and where it sits
```

**Artefacts in the scan.** Sentence counts at lines 433–441 are inflated by author initials ("H.M.", "J Neurophysiol"). The Table 1 rows (345–367) have their cells run together, so their word counts mean nothing.

**Checks I did by hand, which the script can't do:**
- **Three-item lists.** Lines 5, 119, 131 and 311 each list three things that really exist. None is built for rhythm.
- **Em-dash pivots.** None; the plain text has no em-dash pivots at all.
- **Verdict.** No banned-construction defects.

## Passage test: the five blocks over 120 words, plus two near the limit

| block | payload sentence | where it sits | what the other words buy | verdict |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| **267**, Figure 9 caption (134 words) | "B: all four tube models find the planted event; trace and tiny do not. C: … the two ratio models make 0 and 0." | The last two sentences | Legend | Length is earned. Fix the wording of "near zero" (see the findings). |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| **435**, Section 12 citations (121 words) | "CoactDetect and LoCo test for more lineups than a rate-keeping chance model allows" | First sentence | Citations, which a reader would demand | Length is fine. The jargon is not (finding M10). |
| **305** (120 words, near the limit) | "A fair test must not choose the setting on the same recordings it is scored on" | Sentence 3 | The procedure | Fine. Line 307 then repeats sentence 4 (finding L2). |
| **339** (118 words), **383** (116 words) | Legend, and "most detectors call at many of the same moments" | — | Legend and counts | Fine. |

## Findings

Line numbers refer to `detector_review_plain.txt`. Where I found the matching line in `tools/detector_review_template.html`, it is given as T###.

### High

| # | location | issue | fix (proposed rewrite) | verify |
|---|---|---|---|---|
| H1 | 275 (T204) | "Each was trained once, so we do not know how much a second training run would change them." This contradicts line 305 ("We trained each learned detector three times"), line 335, the line 339 caption ("three dots per round, one per training run") and table rows 409–415 ("varies between training runs"). | Replace with: "Their scores change from one training run to the next (Section 8)." | yes |
| H2 | 271 | "The fastest detectors here once trained." Table 1 disagrees: tube_ratio is the slowest of all twelve at 9,786 times real time (line 337), and rate+context (536,163) and locust (517,797) are faster than every learned model. Line 397 also calls rate+context "Fastest by far". | Cut the sentence, or write: "Fast once trained, though slower than rate+context and locust." | yes |
| H3 | 299 | "a detector may not exceed its own limit (Section 7.3)". Line 333 says "nothing stopped rate+context from choosing a setting that breaks its busy-block limit". Line 325 says it breaks the limit, and line 311 says learned detectors have no limit. | "Each hand-written detector has a limit on that rate (Section 7.3). The tuning does not enforce it." | yes |
| H4 | 255–261 | "The three variations each change one thing:" followed by "tube_ratio_guard does both." The sentence contradicts itself. | "tube_guard and tube_ratio each change one thing, and tube_ratio_guard makes both changes:" | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| H6 | 387 (T271/273) | The caption names SPIKE-synch (269 calls) among the detectors that call densely. It then says "This matches their behavior in the simulated busy block (Figures 3, 6 and 7)". But SPIKE-synch made 0 calls in the simulated busy block (line 229), is not a one-bar detector, and is not in Figures 3, 6 or 7. The example does not fit the explanation offered for it. | "locust, binned SCE and rate+context call many times in the busy stretch, as they did in the simulated busy block (Figures 3, 6 and 7). SPIKE-synch did not call in the simulated block, so its 269 calls here have another cause." The author should either name that cause or state that it is unknown. | yes (line 229) |

### Medium

| # | location | issue | fix | verify |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M2 | 377 (first use), 383, 417 | "analysis window" is never defined. | At line 377: "…inside each analysis window, a stretch of the recording the lab marks for scoring…" The author must confirm this definition. | no |
| M3 | 57, plus 47, where "fast stream" appears before it is defined | The "Stream" entry says events are reported "two ways" but never says what separates fast from slow. A 6th grader cannot use the term. GLOSSARY.md does not define it either. | State the difference in one sentence. If no one can yet, write that down rather than leave it implied. In Figure 1, drop "fast stream" or add "(Section 2)". | no |
| M4 | 39 | "KNDy" is never spelled out, and "neurons" is not a 6th-grade word. | "The cells are KNDy neurons (said "candy"), nerve cells named for three chemicals they make: kisspeptin, neurokinin B and dynorphin." | no (domain fact, no source opened) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M6 | 251, 265 | "time filters" and "tiny filters each cell's row" are never defined. | "…using four pairs of sliding averages: a short one for the center and a longer one for the surround." Check this against learn/nets.py. | no |
| M7 | 227 | "the smaller half-gap" is never defined. "continues while it stays above 0.1 with gaps shorter than 0.5 seconds" doesn't say what the gaps are gaps in. | "Each event's window reaches halfway to its cell's previous and next events. Two events are close if they fall inside the smaller of their two windows, and never more than 0.25 seconds apart." And: "A call continues while the average stays above 0.1, allowing dips shorter than 0.5 seconds." | no |
| M8 | 183 (T144), 189, 401 | "stops the bar from dropping just as the recording gets busier." A bar does not drop when activity rises. The failure this rule prevents is a bar that lags behind, still low, as a busy stretch starts. | "Taking the higher side raises the bar before a busy stretch starts and keeps it up until the stretch ends." | no |
| M9 | 119 vs 125/127 | Line 119 says a shuffle "destroys … its bursts, its quiet stretches". Figure 2 then shows the shuffle making clumps and gaps. The two read as a contradiction. | Line 119: "This throws away each cell's own spacing and puts random spacing in its place." | yes |
| M10 | 433–437 (T307–308) | Terms beyond a 6th grader: "rate-keeping chance model", "Resampling", "greatest-of rule", "its loss". In line 433, "cell-averaging detector" uses radar's *range cell*, which collides with this document's "cell". "with an added rather than multiplied bar" is opaque. "Where that rule began has not been established" is a passive hedge. "which reshuffled intervals where this code shifts" is ambiguous. "Synchronous calcium events in hippocampus: Malvache…" is a fragment with no stated link to the detector. | Line 433: "…the radar detector that compares each point with the average of its neighbors. rate+context adds a fixed amount to that average where radar multiplies it." Line 435: "Scrambling by circular shift follows…"; "LoCo's take-the-higher-side rule comes from radar, where its cost in missed targets is analyzed in…"; "We have not found who first proposed it." Line 437: "Cossart et al. shuffled the gaps between events; this code uses circular shifts instead. Malvache et al. (2016) applied the same idea to the hippocampus." | no |
| M11 | 125 | Beyond the passage test above, "(0.35% against 0.40%)" doesn't say which figure is the shuffle and which the shift. "The three calls outside the block that both bars make are planted events" is hard to parse. | "…the two agree more closely (shuffle 0.35%, shift 0.40%)." And: "Outside the block, both bars make the same three calls, and all three are planted events." | yes (the order needs checking against the figure) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M13 | 289 vs 241, 305 | "The standard test recording, which we call the bench" is singular, but the tuning uses 24 simulated recordings and training uses 18. The document never says how one recording becomes 24. | "We make 24 bench recordings, each from a different random start." The author must confirm. | yes (the inconsistency); no (the fix) |
| M14 | 311 | "F1 alone can reward a detector that fires often" gives no reason. The reason is in line 299: calls in the busy block are kept out of precision. The list "1 per minute for CoactDetect, 1 for LoCo, 1 for SPIKE-synch" repeats itself. | "Calls in the busy block are kept out of precision, so F1 cannot see them. So each hand-written detector has a limit: 1 call per minute for CoactDetect, LoCo and SPIKE-synch, 2 for rate+context, 9 for binned SCE, 25 for locust." | yes |
| M15 | 325, 331, 211, 133/135 | Numbers without units, against writing_conventions. Line 325: "(0.17)", "(0.31)", "(1.40)", "(1.01)", "(0.01 and 0.02)", "(1.05 against 1)". Line 331: "0.005" doesn't say what it measures. Line 211: "4 frames". Lines 133/135: "s" is an abbreviation a reader has to decode. | Write "0.17 calls per minute" at first use in each sentence, "a bar of 0.005", "4 frames (0.4 seconds)", and "(seconds 400 to 580)". | yes |
| M16 | 241, 253, 257, 267, 275 | The learned detectors' threshold goes by four names: "output level", "chosen level", "call level" and "bar". | Use "call level" everywhere. Line 257 can keep "bar" only if it says the surround sets the call level. | yes |
| M17 | 369 (T256) | "not a confidence interval" brings in an undefined term only to deny it. | "It is only the lowest and highest score we saw." | yes |
| M18 | 199 | "19 bins in this window pass it". Window B is 180 seconds long (line 135) and the bins are 10 seconds (line 197), which gives 18 whole bins. Either partial bins at the edges are counted or the count is wrong. | Say which. Role 4 owns the number itself. | yes |
| M19 | 319 vs 429 | Line 319 says the rounds differ "by more than these five differ from each other". Line 429 says "about as much as". Table 1 supports "more than": CoactDetect runs 0.71–0.76, while the five means run 0.71–0.74. | Line 429: "…differ by more than the top detectors differ from each other…" | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

### Low

| # | location | issue | fix | verify |
|---|---|---|---|---|
| L1 | 101 (T85) | "operating point" is defined and never used again (grep finds it only at line 101). | Cut the sentence. | yes |
| L2 | 127, 307, 327 | Preview sentences: "Figure 2 makes two points." and "Section 7.3 explains why that matters." Section 7.3 doesn't explain it; line 333 does. The first sentence of line 307 repeats line 305. Line 327 says "flaws we can see in Figure 11C", but 11C shows only the quiet background (line 313), and the busy-background half of flaw 2 isn't in it. | Cut the preview in line 127 and start with "First, real cells…". Merge line 307 into line 305 as "The rule looks at F1 alone and ignores the busy block." Line 327: "The tuning has three flaws." | yes |
| L3 | 337 | "about 9,786 times", "about 536,163 times": "about" with four or more significant figures is false precision. | "about 10,000 times" and "about 540,000 times". | yes |
| L4 | 155 | "Nearby calls closer than 3 seconds" says the same thing twice. | "Calls less than 3 seconds apart are joined into one." | yes |
| L5 | 157 | "the average rises, and so does the bar, but by a fixed amount" is ambiguous. | "the average rises, and the bar rises with it, staying 5 events per second above it." | yes |
| L6 | 73 | "The count a detector's measure must pass": for rate+context, SPIKE-synch and tube, the measure is a rate or a score, not a count. | "The value a detector's measure must pass…" | yes |
| L7 | 131 | "more lineup right now" uses "lineup" as a mass noun. | "are more cells lining up right now than chance explains?" | yes |
| L8 | 151 | "a fixed level (0.1) on the average over each 0.1-second bin": two different 0.1s side by side. | "an average score above 0.1 in a 0.1-second bin". | yes |
| L9 | 169 | "measured in units of how much the surrogate counts vary" is the hardest phrase in Section 4.2. | "…and compares that distance with how far surrogate counts usually stray from their own average." | no |
| L10 | 179 | "candidate bin" is never defined. | "for every bin with at least 3 ROIs". | yes |
| L11 | 197, 211 | "pools" is jargon. Line 211 describes a circular shift without using that name. | Line 197: "puts the counts from every bin of every surrogate into one list". Line 211: "makes 100 circular shifts, counting in frames". | yes |
| L12 | 203 | "goes back two decades", but 2003 was 23 years ago. "tolerant of" is abstract. | "more than two decades"; "Its wide bins still catch events whose cells start a few seconds apart." | yes |
| L13 | 213 | "should not be read as CICADA's" is passive. CICADA is not spelled out until line 439. | "Do not read its results as CICADA's." Spell out CICADA here. | yes |
| L14 | 237 | "(Section 7)": the finding that SPIKE-synch's setting barely matters is at line 331, in Section 8. | "(Section 8)" | yes |
| L15 | 279 | "the lab's pipeline"; line 57 calls it "the lab's event-finding program". | Use one name. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| L17 | 283 | "spread … by a random amount of about 0.36 seconds" sits beside "within about a second" (line 47), "about a third of a second" (line 229) and "span 1.2 seconds" (line 291). The document never says what 0.36 is. | "each cell's start is moved by a random amount, typically 0.36 seconds, so the whole group can span a second or more." The author must confirm. | no |
| L18 | 287 | "These are real lineups": everywhere else, "real" means recorded from tissue. The sentence also opens with a numeral ("6 times"). | "Six times… These are true lineups that the answer key leaves out on purpose." | yes |
| L19 | 289 | "taken only from untreated baselines" is repeated by the last sentence of the block. "25th and 75th percentiles of real baselines" doesn't say what quantity (rate per ROI? a recording's average?). | Cut the phrase and name the quantity. | no |
| L20 | 299 | "so one call cannot take an event that another call sat closer to" is hard to parse. | "so each planted event goes to its nearest call." | yes |
| L21 | 325 | "about as often as the limit CoactDetect and LoCo meet" compares a rate with a limit. | "about once a minute, the limit set for CoactDetect and LoCo." | yes |
| L22 | 329 | "binned SCE chose the lowest value … in 3 of 4 rounds, and LoCo did so in 3 of 4" repeats itself. | "binned SCE and LoCo each chose the lowest value on their lists in 3 of 4 rounds." | yes |
| L23 | 331 | "the other two rules in Section 4.6": that section has three candidate rules (the 0.25-second cap, the 0.5-second gaps, at least 3 events). | Name the two. | yes |
| L24 | 335 | "Training alone changes the learned detectors" is ambiguous. | "Training the same network again, from a new random start, changes its score." | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| L27 | 381, 383, 385 | "black rule" (line 381), "the whole field" (line 383), "the useful detectors" (line 385, an undefined set). | "black line"; "every cell in view"; "the detectors other than trace and tiny". | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| L29 | 407 | "(recall 2% at 10% of ROIs)" puts two percentages with different meanings side by side. "for this data" breaks the house rule that "data" is plural. | "finds 2% of events joined by 10% of ROIs"; "for these data". | yes |
| L30 | 9 | "what each detector calls": "call" is used as a verb before line 77 defines it. | "where each detector marks an event". | yes |
| L31 | 115 | "We make hundreds of surrogates". Lines 169, 183, 197 and 211 give 100 to 200. | "We make 100 or more surrogates". | yes |
| L32 | 105 | "not chosen by a person but adjusted by the computer" is not in positive form. "This process is called training" is passive. | "A detector whose inner numbers the computer adjusts, over many examples, until its answers match the planted events. That adjusting is called training." | yes |
| L33 | 373, 379, 387, 391, 421 (and 9, 45) | The "no answer key" warning appears seven times. The copies at lines 9, 45, 373 and 421 are in the right places. The clause in line 387 is decoration. | Cut the last clause of line 387 (see also H6). | yes |
| L34 | 445 | A fragment joined to a clause by a semicolon. | "We built this document with the project's own tools. One run produced the bench recordings, the rounds, every number in the text and the figures." | yes |

**Handed to other roles, not filed here:**
- The comparison table in Section 4 has no number, while Section 8's table is "Table 1". Numbering is a mechanical check (role 10).
- Orange means "shuffle" in Figure 2B and "whole-recording shift" in Figure 2C. That color clash is for role 8 or 10.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Whether 5.2 and 19 mHz are the right percentiles is also role 4's.

Files:
- `<scratchpad>\review\detector_review_plain.txt`
- `<scratchpad>\review\prose_scan.txt`
- `<worktree>\tools\detector_review_template.html`
- `<worktree>\docs\writing_conventions.md`
