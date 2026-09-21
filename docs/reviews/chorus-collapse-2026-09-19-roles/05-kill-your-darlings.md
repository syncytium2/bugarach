GRANT 5 ok — Read, Grep, Glob
(I also hold SubagentHandback. It is the channel for handing this report back, not an editing tool. I hold no Edit, Write or NotebookEdit.)

**Artifact:** `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`. This is the built page. I did not open the generator. The page is 315 lines. Lines 98, 139, 163, 174, 195, 200 and 212 hold inline SVG figures, so I pulled their captions, tables and `<text>` labels out with Grep.

## 1. Banned-construction search

**The tool was not available.** `murderboard_prose.sh` is not in this repo, so I cannot paste its output. What follows is a Grep of the built HTML. Its search terms are the process file's list, the house convention, unedited:
- not just X, but Y
- it's not about A, it's about B
- it's worth noting
- delve, leverage, robust, seamless, crucial, landscape, tapestry
- a rhythmic three-item list
- an em-dash pivot into an uplifting close
- "In today's ___"

| line | construction | kind |
|---|---|---|
| — | `not (just\|only\|merely) … but`, `it's not about`, `worth noting/mentioning`, `delv`, `leverag`, `robust`, `seamless`, `crucial`, `landscape`, `tapestr`, `in today's` | 0 hits |
| 139 ×3 | `—` | table-cell placeholder in Table 1 ("no configuration of that shape"). Not a pivot. Not a defect. |
| — | rhythmic three-item list | 0 found, by reading. Every triple counts real things: the three pooled statistics, the three step-length pairs, seed shares 34%/32%/38%, and the three open repairs. |

I also searched for British spellings (-ise/-our/centre/labelled/whilst/amongst/grey…) and for singular "data". Both came back with 0 hits.

## 2. Findings

Each row gives: location · issue · severity · suggested fix · verified.

1. **Lines 50–52, 64, 72, 106–108, 290 ("run" means three things)** · The subtitle says "the two runs of the project's fair comparison" and then "14 training runs were replayed from the runs' own starting points". Box bullet 1 says "both runs of goal 2", and bullet 3 says "In the second run". Line 106 adopts "draws" and later uses "run" for a single training run: "6 of 7 distinct runs", "8 distinct collapsed runs". The reader cannot tell a replicate from one training run, and "the runs' own starting points" is unreadable. · **major** · Say "draw" from the subtitle on, defined once there. Keep "run" for one training run only. · yes

2. **Line 201–202 ("7 other lr-0.03 configurations") and the Figure 7 caption ("each of the other lr-0.03 configurations")** · Table 2 has 8 rows from 8 configurations. Its first row, 2736f584 seed 1, is **Figure 1's own configuration** at another seed. The replay filenames show this: Figure 1 is `2736f584…_s0` and `_s2`. So "other" is false for that row, and 7 does not match the table's 8. The totals on the page (11 − 8 = 3 left out; "8 distinct collapsed runs" in Limits; "6 of 7 other collapsed runs" in the box) only add up once the reader has spotted this. · **major** · Write "one collapsed fit from each of 8 lr-0.03 configurations: Figure 1's own at another seed, and 7 others". Mark that row in Table 2. · yes (replay filenames in `replays/`)

3. **Lines 175–180 (the "Round 1 of this page's review" paragraph)** · This is review history in the shipped text. Its payload is one reason: GELU's negative dip carries signal, so "never goes positive" is the wrong test and would have counted a working fit. Everything else is process narrative. The last sentence says "§6 says what is known about them", but Limits says it is "not established". · **major** · Replace with about 2 sentences: "Silent is defined by variation, not sign: GELU's negative dip carries signal, and a never-positive test counts a working fit whose output varies normally. What flattens the 24 collapsed chorus_gain_norm fits without a silent layer is not known (Limits)." · yes

4. **Line 222–223 (Sokar et al. "define such 'dormant' units by a threshold on their activity, as this page does")** · The page's own rule is a threshold on **variation**: standard deviation under 0.001. Lines 175–178 reject an activity threshold. So "as this page does" contradicts §3 of the page. · **major** · Write "…by a threshold on their activity; this page thresholds variation instead (§3)", or drop "as this page does". · yes on the internal contradiction; no on Sokar's exact definition (paper not fetched; role 4)

5. **Lines 164, 172–173 (§3, third paragraph)** · Opens with a preview: "This is the test that separates this failure from the earlier one." The payload is the last sentence: "The encoder still hears the events; the head does not pass them on." · **major** · Promote the last sentence to the first. Cut the preview. · yes

6. **"goal 2", 8 times (lines 51, 64, 86, 89, 101, 106, 245, 249)** · This is an internal index number used as a name, which breaks the house rule "name things, don't index them". An outside reader of a public page has to hold it in their head. · **major** · Write "the fair comparison". Keep "(goal 2)" once in the subtitle as a lookup key. · yes

7. **Lines 109–114 against 130–136** · The heading "Which fits collapse is not repeatable" (§1) seems to contradict §2's "The training seed does [decide], p = 0.001". The page never reconciles them: the seed matters within a draw, but it does not carry across draws. · **major** · Add one clause to lines 112–113: "…a fit that collapses in one draw is no likelier to collapse in the other, though within a draw the seed matters (§2)." · no (reconciliation is inferred; role 4)

8. **Lines 102–105 ("Inside each outer fold … 432 per net per run")** · 24 configurations × 3 seeds × 6 pairs = 432. That reads as one outer fold per draw, yet the sentence says "each outer fold", and Table 3's note says 40 default refits per net "in every fold". The reader cannot tell whether 432 counts one outer fold or one draw. · major · State the number of outer folds, and whether inner selection runs in each. · no (role 4 to check against source)

9. **Line 104–105 ("The configuration tuning picks is then trained afresh") and the Table 3 header "refits of configurations tuning chose"** · Garden path: "configuration tuning" parses as a compound noun. · minor · Write "The configuration that tuning picks…" and "configurations that tuning chose". · yes

10. **Lines 161 against 98** · The threshold is given as "(0.0001)" with no unit. Figure 1 draws the same threshold as "−9.2" on a logit axis. · minor · Write "(probability 0.0001, a logit of −9.2)". · yes (logit(10⁻⁴) = −9.21)

11. **Counts with no unit (house rule)** · Line 112 "111.5"; line 113 "38 observed, 39.6 expected"; line 218 "8 early, 0 late, 3 recovered"; line 243 "the second draw's 3; all 3". · minor · Add "fits" or "refits" to each. · yes

12. **Line 163 (Figure 3 caption and axis) "SD"** · The abbreviation is never defined. The prose always spells it out. · minor · Write "standard deviation (SD)" at first use in the caption. · yes

13. **Line 145 "GELU"; line 147 "β1 0.9 and β2 0.999"; lines 84 and 164 "PR"; line 286 "GPU"** · GELU is expanded only in the reference list. β1 and β2 are symbols used before they are defined, and β2 is reused in 2/(1 − β2). PR is not defined for an outside reader. · minor · Write "a Gaussian error linear unit (GELU)"; "Adam's moment-decay rates β1 = 0.9 and β2 = 0.999"; "pull request (PR) #596". · yes

14. **§ cross-references: lines 83 "(§4)", 89 "(§5)", 98 "replayed in §4", 180 "§6 says"** · Section numbers used as names. Figures on this page carry names; sections do not. · minor · Use the heading: "(When it happens, and what prevents it)". · yes

15. **Line 164 "PR #596 found plain chorus's encoder…" and Table 2 "the same run as 2736f584's, stopped earlier"** · A lookup key used as the subject of a sentence, and a hash used as a name. The box does this correctly: "the failure found earlier in plain chorus (PR #596)". · minor · "The earlier diagnosis of plain chorus (PR #596) found…" and "the same run as the first row's". · yes

16. **Line 193–194 ("the replay with a 50-step warm-up stays flat…")** · Forward reference: warm-up is introduced only in the next paragraph (196–199). · minor · Move the clause after line 199, or introduce the warm-up replays first. · yes

17. **Line 188 cites Figure 6 before Figure 5 (line 192)** · The figures render 5 then 6, so the prose reads out of sequence. · minor · Cite Figure 5 first, or reorder the sentences. (The mechanical side of figure order is role 10's.) · yes

18. **Line 224 "Why it helps Adam is argued"** · "Argued" is ambiguous: disputed, or demonstrated? · minor · "Why it helps Adam is disputed". · yes

19. **Line 220–221 ("Units that stop responding … are a long-standing observation")** · Category error: units are not an observation. · minor · "That units stop responding under too large a step size is long observed…". · yes

20. **Line 251 heading "A collapse can be caught when it happens"** · The body says "a check at the end of training". The heading claims more than the body delivers. · minor · "A collapse can be caught before it is scored." · yes

21. **Line 240 (four refits listed one by one, three words repeating)** · Redundant. · minor · "chorus_norm: 2, both second draw at lr 0.01; chorus_gain_norm: 2, one per draw, at lr 0.03." · yes

22. **Line 255–256 against 264–265** · The one-recording caveat is stated twice. · minor · Keep it in Limits only, or in §5 only. · yes

23. **Line 50–51 subtitle** · "the saved fits of the two runs of the project's fair comparison of coded detectors against learned nets": five chained "of"s. · minor · "A diagnosis from the saved fits of both draws of the fair comparison between coded detectors and learned nets (goal 2)." · yes

24. **Box bullet 4, lines 77–83** · About 100 words. Sentences 2–3 (flat start at replay, 220 steps, head silent later) are §4's evidence repeated in a summary box. · minor · Two sentences: "A collapsed fit never leaves the flat output every fit starts with; ramping lr up over the first 200 steps lets it train, and 6 of 7 other collapsed runs too. This is a known failure of too large a step size, and warm-up is its standard remedy." · yes

25. **Terminology drift: "dead" (lines 88, 175, 232), "silent", "dormant", "flat"** · Four words for overlapping ideas. "Dead models" (88, 232) means collapsed fits, while "dead" (175) meant a layer. · minor · Use "collapsed fits" for models and "silent" for layers, and quote "dormant" only as Sokar's term. · yes

26. **Sentences opening with a numeral: lines 137 "5 pairs…", 179 "24 collapsed…", 217 "0 fits collapsed…", 271 "24 collapsed…"** · Style. · minor · Recast, or spell the number out. · yes

27. **Line 66–67 box ("each called every recording it was scored on as a single event, which matches one of the 15 planted events, F1 0.125")** · "15 planted events" is Figure 1's recording, but the sentence applies it to every recording. · minor · "…as a single event; on Figure 1's recording, with 15 planted events, that scores F1 0.125." · no (whether every scoring recording has 15 events is unchecked)

28. **Table 2 header "configuration's collapse share"** · The cells are counts ("33 of 36 fits"), not shares. · minor · Rename it "collapsed fits in the configuration". · yes

## 3. Passage test, block by block

Word counts are hand counts, approximate, because the tool was unavailable. Sentence counts are exact.

| block | words / sentences | the one sentence it delivers | where it sits | what the rest buys |
|---|---|---|---|---|
| Subtitle 50–53 | ≈45 / 3 | "The runs' results were not changed; 14 training runs were replayed from the runs' own starting points to watch the failure happen" | middle | Scope and provenance. Earns its place. Finding 23 (the "of" chain) and finding 1 ("runs"). |
| Intro 55–60 | ≈85 / 3 | what chorus_norm is and how a call is scored | throughout | The definitions (ROI, logit, F1) a cold reader needs. Keep. |
| Answer box 62–90 | ≈330 / 17 | tuning's top rate (lr 0.03) makes chorus_norm fits stay flat from the start; warm-up fixes it; tuning stepped around it | bullets 2, 4, 6 | A top-of-page summary, not a recap. Bullet 4 carries §4's evidence and can be cut (finding 24). |
| §1 p1 93–97 | ≈80 / 4 | "The collapsed fit's output barely moves … so the whole recording is one call" | last | Seed and threshold context for Figure 1. Keep; could promote. |
| How the fits are organized 99–108 | ≈130 / 5 | definitions of configuration, inner fit, refit, draw | throughout | A glossary the page needs. Finding 8 (the outer-fold count) and finding 9 (garden path). |
| Not repeatable 109–114 | ≈75 / 3 | the bold heading, restated at line 112 | first (heading) | The overlap arithmetic, which a sceptic would demand. It collides with the seed result (finding 7). |
| §2 p1 117–124 | ≈95 / 4 | "For chorus_norm the learning rate separates the configurations almost completely" | first | Shape, plus step length disclosed as untested. Keep. |
| §2 p2 125–129 | ≈40 / 2 | chorus_gain_norm's 4 × 6 encoder collapses at both upper rates | throughout | Tight. |
| §2 p3 130–138 | ≈115 / 5 | "The training seed does [decide], for chorus_norm (p = 0.001)" | **second, after the null result** | Promote the seed finding ahead of the fold-pair null. The pooled-seed and twin-exclusion sentences are method notes; fold them into the test's parenthesis. |
| §3 p1 142–148 | ≈105 / 3 | the head is 8 untuned GELU layers trained by Adam at up to 30 times its default step size | last clause | The GELU dip is needed later (by the round-1 paragraph). Keep. Finding 13 (β). |
| §3 p2 149–162 | ≈140 / 6 | 142 of 153 collapsed chorus_norm fits have a silent head layer; 0 of 279 working ones do | middle, after definitions | Definitions first is correct here. Finding 10 (threshold unit). |
| §3 p3 164–173 | ≈100 / 6 | "The encoder still hears the events; the head does not pass them on." | **last, after a preview** | Promote it (finding 5). |
| Round 1 175–180 | ≈80 / 5 | why silent is defined by variation, not sign | buried in the middle | Review history, which satisfies the author and no reader. Cut to 2 sentences (finding 3). |
| §4 p1 183–194 | ≈150 / 7 | "the silent head marks a fit that never left its flat start, and does not begin the failure" | **sentence 7 of 7** | The timing detail (step 230, 135 of 158) is evidence for Figure 5 and earns its place. Promote the payload to open the paragraph. Finding 16 (forward reference). |
| §4 p2 196–199 | ≈65 / 3 | only the start matters: 200 warm-up steps are enough, 50 are not | spread over sentences 2–3 | Tight. |
| §4 p3 201–211 | ≈110 / 5 | a 200-step warm-up trains 6 of 7 distinct collapsed runs where chance predicts 1.4 | middle | The selection disclosure (3 left out, and why) is what a sceptic demands. Keep. The count wording is wrong (finding 2). |
| Settled early 213–219 | ≈70 / 3 | 60 of 62 chorus_norm collapses were already there at the shorter length, and none recovered | first | The list of step-length pairs is noise. The notable fact, that 3 chorus_gain_norm fits recovered, is buried in a parenthesis. Surface it or cut it. |
| Known failure 220–226 | ≈95 / 4 | the bold heading | heading | The citations and the 2,000-step rule of thumb (which bears on e86433df) earn their place. Findings 4, 18, 19. |
| §5 228–258 | ≈380 / 5 bullets | "chorus_norm was in effect tuned over a smaller grid than the one the fair-comparison report declares" | end of bullet 1 | The repair options are three real things. Findings 20, 21, 22. |
| Limits 260–276 | ≈130 / 6 bullets | the census is one recording from one draw; the warm-up was tried on chorus_norm only | throughout | Each bullet is a distinct limit. Keep. |
| Where everything is 278–296 | ≈150 | — | — | Lookup section, where hashes and paths belong. Exempt. |

**Overall:** there is no throat-clearing opener, no recap close, and no decorative humor. The prose is mostly short and concrete. The recurring defect is order: in §2 p3, §3 p3 and §4 p1, the block's point is its last or buried sentence, because each was written in the order it was thought. Promoting fixes more than trimming does, except for the round-1 paragraph, which should be cut.

**Out of my lane, passed on without judging:**
- Finding 8 (the outer-fold count) is for role 4 to check against the source.
- Sokar's exact definition (finding 4) was not fetched.
- Whether §1's "not repeatable" paragraph belongs in §2 is section order, which is role 11's.
