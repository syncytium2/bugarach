GRANT 5 MISMATCH — missing none; holds Bash, PowerShell, Edit, Write, Agent, Artifact, Skill, and deferred NotebookEdit among others (the role grants Read, Grep, Glob only)

**Note on the run:** I was told this grant "has no shell", but the session handed me a full fallback toolset that includes a shell and editing tools. The `roles:` line for this run should record a fallback path, not a named-agent grant. I used only Read and Grep. I edited nothing and wrote nothing to the repo, 01-lit, or my scratch folder.

# Role 5: Line editor, "Kill Your Darlings". Chapter 1 (Aim 0)

Artifact: `<worktree>/docs/dissertation/chapter-1-aim0.md` (hash a3d06b04…)
Banned list I ran: the one in `.claude/agents/murderboard/05-kill-your-darlings.md`, plus `docs/writing_conventions.md` (plural "data", no "fire", no "modality", American spelling, name things rather than index them).

## Receipt: murderboard_prose.sh

The main thread ran the upstream copy on the artifact. I did not run it myself. Output verbatim from `<scratchpad>/mb/prose_r1.txt`:

```
docs/dissertation/chapter-1-aim0.md
  line   construction                       kind   context
  688    robust                             word   in: - Shah NB, Wainwright MJ (2018). Simple, robust and optimal 

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1         19 words    1 sentences
  3        116 words    4 sentences
  13         3 words    1 sentences
  15        82 words    4 sentences
  22        96 words    3 sentences
  29        91 words    4 sentences
  37        54 words    2 sentences
  42       156 words    5 sentences   << over 120
  53         2 words    1 sentences
  55       268 words   15 sentences   << over 120
  76        97 words    4 sentences
  83         3 words    1 sentences
  85         8 words    1 sentences
  87        39 words    3 sentences
  91       162 words    6 sentences   << over 120
  102        5 words    1 sentences
  104        3 words    1 sentences
  106      182 words    1 sentences   << over 120
  120        4 words    1 sentences
  122       16 words    1 sentences
  124      154 words    6 sentences   << over 120
  136       51 words    2 sentences
  141        4 words    1 sentences
  143      217 words    9 sentences   << over 120
  158       98 words    4 sentences
  166       31 words    3 sentences
  170       77 words    5 sentences
  176        6 words    1 sentences
  178        4 words    1 sentences
  180       23 words    1 sentences
  183        9 words    1 sentences
  185       27 words    1 sentences
  188       10 words    1 sentences
  190      162 words    6 sentences   << over 120
  200        6 words    1 sentences
  202       57 words    2 sentences
  207       26 words    1 sentences
  210       69 words    2 sentences
  216        9 words    1 sentences
  218       27 words    1 sentences
  221        8 words    1 sentences
  223       41 words    2 sentences
  227        6 words    1 sentences
  229       92 words    4 sentences
  238        5 words    1 sentences
  240      147 words    6 sentences   << over 120
  251        6 words    1 sentences
  253       26 words    1 sentences
  256        8 words    1 sentences
  258       24 words    1 sentences
  261        7 words    1 sentences
  263       47 words    2 sentences
  267        5 words    1 sentences
  269        5 words    1 sentences
  271       90 words    3 sentences
  278       55 words    2 sentences
  283        3 words    1 sentences
  285       45 words    2 sentences
  290        6 words    1 sentences
  292        2 words    1 sentences
  294       82 words    6 sentences
  301        6 words    1 sentences
  303      113 words    4 sentences
  311       44 words    1 sentences
  315        5 words    1 sentences
  317        2 words    1 sentences
  319       72 words    4 sentences
  325      119 words    4 sentences
  334      131 words    4 sentences   << over 120
  343      105 words    3 sentences
  350       44 words    2 sentences
  354       62 words    2 sentences
  359        8 words    1 sentences
  361       44 words    3 sentences
  365        8 words    1 sentences
  367       51 words    1 sentences
  372        5 words    1 sentences
  374       68 words    4 sentences
  379       77 words    3 sentences
  385        2 words    1 sentences
  387       80 words    4 sentences
  394       61 words    3 sentences
  399       12 words    1 sentences
  401       61 words    3 sentences
  406       50 words    2 sentences
  410       81 words    4 sentences
  416        2 words    1 sentences
  418       66 words    5 sentences
  423      201 words   10 sentences   << over 120
  436       50 words    3 sentences
  440       28 words    2 sentences
  443       71 words    1 sentences
  449       35 words    1 sentences
  452      207 words    6 sentences   << over 120
  468        8 words    1 sentences
  470       25 words    2 sentences
  474      236 words    9 sentences   << over 120
  489        2 words    1 sentences
  491       81 words    6 sentences
  497        2 words    1 sentences
  499       51 words    3 sentences
  503        5 words    1 sentences
  505       13 words    1 sentences
  507       33 words    2 sentences
  511      141 words    5 sentences   << over 120
  521       66 words    3 sentences
  528        9 words    1 sentences
  530      265 words    1 sentences   << over 120
  545       47 words    3 sentences
  550        3 words    1 sentences
  552        9 words    1 sentences
  554       83 words    3 sentences
  561       72 words    3 sentences
  567        8 words    1 sentences
  569      128 words    6 sentences   << over 120
  578        3 words    1 sentences
  580      136 words    7 sentences   << over 120
  590        2 words    1 sentences
  592      218 words   15 sentences   << over 120
  611        3 words    1 sentences
  613        8 words    1 sentences
  615      155 words   10 sentences   << over 120
  628       63 words    1 sentences
  634        3 words    1 sentences
  636      179 words    6 sentences   << over 120
  649        4 words    1 sentences
  651        4 words    1 sentences
  653       28 words    1 sentences
  662       11 words    1 sentences
  665        2 words    1 sentences
  667      436 words   75 sentences   << over 120
  697       47 words    5 sentences
  20 block(s) over 120 words — for each, name its payload sentence and where it sits
```

**Banned-construction result.** The tool had one hit: "robust" at line 688. It is inside a cited paper's title (Shah & Wainwright 2018) and must stay as published, so it is not a defect.

I also searched by hand with Grep and read the text:
- No "fire/firing", no "modality", no British spellings, no singular "data", no em-dashes in the body, no "In today's".
- One rhetorical *not A but B* pivot the tool cannot catch, at line 42 (finding 9).

## Passage test: the 20 blocks over 120 words

Three of the 20 are not prose: Table 1.1 (line 106), the 1.9 table (line 530) and the references (line 667). No finding on those.

| block | payload sentence, and where it sits | what the other words buy | verdict |
|---|---|---|---|
| 42, 1.1 "The answer, developed below" | Sentence 1: "theory … tells it where to look" (top) | A full preview of results, which the Contributions list repeats right after it | Cut to 1–2 sentences (finding 1) |
| 55, Contributions | The list itself | Item 6 packs three results (one-template form, null mean, power) into one item | Split item 6. Fix "exact" (finding 3) |
| 91, 1.2.1 generative model | "Each cell carries … Two departures … matter below" (end) | The 45-word sentence on who named the Thomas process. That is the author's satisfaction, not evidence | Move to a footnote or cut |
| 124, 1.2.2 tools | One tool per bullet | All of it earns its place | Keep |
| 143, 1.2.3 Louis et al. | "This is the closest precedent for the joint fit, and it differs in three ways" (sentence 5 of 6) | The setup before it | Promote the payload to first. See finding 2 for the repetition |
| 190, 1.3.1 uniform vs Gaussian | "Gaussian jitter has no such edge, so g_n stays smooth in w, which is what lets the joint fit … read σ" (middle) | Restates the Grün and Louis priors from 1.2.3, plus a parenthetical on the history of the dropped frame-rounding term | Cut the restatement. Move the history to 1.8 |
| 240, 1.3.5 joint fit | Sentences 2–3 (top) | Third telling of the Louis comparison, plus the history of the "earlier one-parameter fit" | Cut both |
| 334, 1.5.4 chance clusters | "a threshold has to be set per recording from its own background" (middle) | The last sentence (spread-out events lost at K = 6) is a separate result | Split into two paragraphs |
| 423, 1.6.2 three bullets | One closed form per bullet | Evidence a skeptic would ask for | Keep. Fix "exact" (finding 3) |
| 452, 1.6.2 against Synfire | "consistent with the no-order bias, but not tested" (sentence 4) | The Borda/Copeland/Shah–Wainwright prior art (about 70 words), which belongs in 1.2.3 Order or in 1.9 | Promote the payload. Move the prior art |
| 474, 1.7 bullets | Third bullet: the tools merge pairs the data could separate, and on the lab's gaps that costs little (end, correctly placed for a "so") | Evidence | Keep. Fix the numbers (finding 5) |
| 511, 1.8 rederivation | "This is a consistency check, not independent review." (sentence 4) | The method description | Promote to first |
| 569, 1.10 lab's regime | Sentence 1 (top) | Evidence | Keep. Fix the jitter range (finding 6) |
| 580, 1.10 two sources | Sentence 2, "a prediction and no test" (top) | Evidence | Keep |
| 592, Limitations | One limitation per item | Item 5 is not a limitation: every source is now held. It is a review record | Cut item 5 or move it to 1.8 |
| 615, Next steps | One step per item | Item 2 repeats Louis Fig. 6 almost word for word from 1.10 "Two sources" | Shorten item 2 to "test with the full count distribution (*1.10*)" |
| 636, 1.11 Conclusion | Sentence 1 plus the new-results sentence | A recap of 1.10. Also "sobering" (decoration) and "Reading the prior work sharpened the claims" (process story) | Trim to about 3 sentences of what is new and what is open |

## Findings

Columns: location · issue · severity · suggested fix · checked against a source

1. **1.1 lines 42–51, Contributions lines 55–74, lines 76–81, 1.9, 1.10 "What theory replaces", 1.11.** The chapter tells its results six times. Lines 76–81 open with "What is old and what is new is set out in *1.9*. In short…", which is the banned preview form. · **major** · Keep the Contributions list and the 1.9 table. Cut lines 42–51 to one or two sentences. Delete lines 76–81. Cut the first paragraph of 1.10 (lines 554–559), which repeats 1.5.4's explanations, down to its last sentence. · yes (internal)

2. **The Louis, Borgelt & Grün (2010) comparison** appears at lines 143–156, 192–194, 242–246, 1.9 (three rows), 583–585, 619–621 and 643–646. Each time it says "slope-change rule, uniform jitter, no event rate", and Fig. 6 is told twice almost word for word. · **major** · Say it once, in full, at 1.2.3. Elsewhere use a cross-reference ("unlike the uniform-jitter rule of *1.2.3*"). · yes (internal)

3. **Contribution 6 (line 70), the 1.9 row "The exact no-order mean of F, c/√n̄", and 1.6.2 line 428** · The exact mean and c/√n̄ are two different results. `kendall_w/derivation.md` §3 gives the exact formula ("exact for every N, k and E", computed by FFT). §4 gives c/√n̄ as the large-E limit, within 0.003 of exact only for n̄ ≳ 1. Contribution 6 and 1.9 call c/√n̄ "exact", so each states two things and one of them is false. · **major** · Write "its exact no-order mean, whose large-E limit is c/√n̄ …" in both places. · yes (`kendall_w/derivation.md` lines 4–6, 51, 84, 200–202)

4. **Undefined jargon a committee reader meets cold.**
   - "fast stream", "slow stream" (first used line 26, never defined); "combined stream" (line 450)
   - "baseline window" (449, 574, 587, 642)
   - "event floor" (338, 518, 565)
   - "Palm train/form" (235, 596)
   - "hard-core" (first used 230, not named where the 20 s spacing is introduced at line 99)
   - "merge rule" (479), "shipped" (356, 485), "August recordings" (625), "correlogram tool" (616)
   - "CoactDetect and LoCo" (562). The "six coordination detectors" of line 29 are never named.
   - "Aim 1" (162, before it is introduced)

   **major** · Define the streams and the baseline window in 1.1 or 1.2.1, one clause each. Add "(a hard-core train)" at line 99. Define or cut the rest at first use. · yes (GLOSSARY defines most of these; the chapter does not)

5. **1.7 line 483, "between about 0.6 and 2.5 s"** · The data's floor was just given as 0.26–0.76 s (line 474), and line 51 says "under 1 s". "0.6" is tied to neither. The source (`separation/floor/derivation.md` line 454) says "between about 0.6 s and 3 s". · **major** · State one figure for the floor and reuse it: "between the data's floor (under about 0.8 s) and the assessor's 2.5 s". · yes

6. **Lab jitter is given four ways.** "0.105 s fast, 0.131 s slow" (lines 25–26, 476); "0.105–0.150 s" (569); "0.10–0.15 s" (595); "σ = 0.1 and 0.15 s" (615). The 0.150 is the combined stream (GLOSSARY line 472), which the chapter never introduces. · minor · Give fast, slow and combined once in 1.1, then use those numbers everywhere. · yes (GLOSSARY)

7. **The word "floor" means two things.** "The repository's event floor" (338) is a threshold. "The data's floor" and "the tools' floor" (474–479, 1.6 caption, 576, 643) are a minimum separation. Line 576 "the data's own floor" sits a page after the event-floor sense. · minor · Call the separation one "separation floor" or "resolution limit". · yes (internal)

8. **Line 481, "The data set only the plateau, f²"** · On first reading this parses as the noun "data set", and the sentence fails to parse. · minor · "The data determine only the plateau, f²…" · yes

9. **Line 42, "theory does not replace simulation but tells it where to look"** · A *not A but B* pivot. It also contradicts the 1.10 heading "What theory replaces, and what it does not", which says theory does replace part of simulation. · minor · Line 42: "theory tells simulation where to look, and replaces it for one source's population counts." · yes (internal)

10. **Symbol collisions.**
    - s = σ√2 (line 185) vs jitter ±s (line 152)
    - "the top k items" (line 463) vs k = participants
    - K = threshold vs "K-function" (line 159)
    - b = background vs Kish's b̄ (line 375)

    minor · Rename the line-152 symbol. Change "top k" to "top few". Write "Ripley's K-function". The b̄ case is handled in the text and can stay. · yes

11. **Line 210, "The second terms are the at-most-one-event term"** · The plural does not match the singular. f₃ has three terms, and it is unclear which one or two the sentence means. · minor · "In each line, the term in p² is the at-most-one-event correction…" (role 4 should confirm which terms are meant). · no (did not rederive)

12. **Process history inside results.** The frame-rounding parenthetical (197–198), "an earlier one-parameter fit … its readings were partly model error" (246–248), Limitation 5, and "Reading the prior work sharpened the claims" (643). The shared-backgrounds rerun (278–281) is a real disclosure and should stay. · minor · Move the rest to 1.8, where review corrections already live. · yes

13. **Line 505, "Three kinds of check were made, and their limits should be stated plainly."** · Throat-clearing (house voice). · minor · Delete it. The three bold headers do the job. · yes

14. **Line 461, "the textbook Borda or Copeland ranking"** · "or" hedges between two different rules. · minor · Name the one that net lead count is (Copeland, wins minus losses). Say Borda is equivalent only when every pair is compared. · no (did not check Coppersmith's definitions)

15. **Lines 311–313, "Two smaller regularities"** · No payload. The reader is not told why the numbers are there. · minor · Tie them to k̂ ("the 1 s window's undercount at σ = 1 s is what *1.3.3* predicts") or cut them. · yes (internal)

16. **Smaller precision points.**
    - Line 330, "a possible small high bias": the bias of what? The prediction runs high against the measurement.
    - Line 348, "5-cell events read 0.1 to 3.6 times planted": which estimate?
    - Line 357: χ² of what?
    - Line 436: ± what (SD, SE)?
    - Line 425, "sits on it": colloquial.
    - Line 223, "and it predicts": "it" has no clear antecedent.

    minor · Name the subject in each. · yes (internal)

17. **Line 641, "sobering"** · Evaluative decoration. · minor · Delete it. The number makes the point. · yes

## What must change before I would sign off

Findings 1–5. The chapter tells its claims too many times. It calls an asymptotic result "exact". It never defines the streams and windows that every lab-regime number depends on. And it gives one quantity (the separation floor) three different values. The minor findings are a single editing pass.

Fixing finding 1 alone would shorten the chapter by about 600–800 words without losing a result.

---
*Archivist's note (main thread, 2026-10-29): for this public repository (sapper SAP004), the review worktree's absolute path became `<worktree>/`; the session scratch folder's absolute path became `<scratchpad>/`. Nothing else in the report was changed by this pass.*
