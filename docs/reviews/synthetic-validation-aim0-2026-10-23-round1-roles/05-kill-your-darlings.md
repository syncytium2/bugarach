GRANT 5 MISMATCH — missing none; holds forbidden tools Edit, Write, NotebookEdit (plus Bash, PowerShell, Agent, Artifact, MCP connectors). I was spawned as a general-purpose agent through the inline fallback. I used only Read and Grep, and I created, edited and deleted nothing. Record this as a fallback-path run on the `roles:` line.

**Surface checked:** goal page lines 25–163 (through the extract `_scratch/aim0_sections.md`) and the plan bullet at lines 234–255. Rules applied: CLAUDE.md "Writing for a human reader", the data-plural and "fire" rules, and `docs/writing_conventions.md` (American English, units on every table column, the agreement-between-methods rule).

**Banned-construction list run:** the one in the role file. It contains *not just X, but Y* · *it's not about A, it's about B* · *it's worth noting* · delve, leverage, robust, seamless, crucial, landscape, tapestry · rhythm triads · an em-dash pivot into an uplifting close · an opener of the form *"In today's ___"*. The project adds two rules on top: "data" is plural, and calcium events do not "fire".

## Tool output, pasted verbatim (`_scratch/prose_report.txt`, run by the main thread)
```
_scratch/aim0_sections.md
  line   construction                       kind   context
  — no banned construction found

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1         14 words    1 sentences
  3         47 words    3 sentences
  8        256 words   11 sentences   << over 120
  26        58 words    2 sentences
  31         6 words    1 sentences
  33        62 words    3 sentences
  38         8 words    1 sentences
  40       154 words    1 sentences   << over 120
  49       313 words   15 sentences   << over 120
  74        29 words    3 sentences
  77        50 words    2 sentences
  82        15 words    1 sentences
  84        47 words    4 sentences
  89        11 words    1 sentences
  91        69 words    1 sentences
  97       111 words    5 sentences
  105       92 words    4 sentences
  113       88 words    1 sentences
  119       82 words    4 sentences
  127       84 words    3 sentences
  134       79 words    3 sentences
  3 block(s) over 120 words — for each, name its payload sentence and where it sits
```
Block line numbers are in the extract. Goal-page line = extract line + 24.

## Passage test on the three over-length blocks (the judgment columns)

| block | payload sentence | where it sits | what the other words buy |
|---|---|---|---|
| ext 8 (goal 32–48), first-result bullets, 256 words | "At 0.01 Hz background the predicted participants match the measured median within about 0.03 in every cell." A second payload: "That turns jitter from Aim 1a's weakest parameter into one of its best." | Mid-bullet, in bullets 2 and 3. Neither is a bullet's lead. | **Evidence:** the jitter numbers, the K-cluster tail and "Not predicted" (this names what the doc does not know, so keep it). **Satisfaction:** the Poisson-residual sentence (ext 13–15) explains a route not taken. Cut it to a clause or drop it. The g_n definition (ext 9) is reference material. "g_2 has a closed form" asserts something without giving the form or a pointer. Fix: lead bullets 2 and 3 with their payloads. |
| ext 40 (goal 64–72), agreement table, 154 words | The header "All three reached the same core answer independently." | Top. Correct. | The table is evidence and earns its length. Two gaps: "stated" (rows 5–6) is never defined (asserted without derivation?), and the bare "—" in row 6 does not say whether B tried and failed or never tried. |
| ext 49 (goal 73–96), "What only the blind passes found", 313 words | "Errors in Figure 1 were correlated across each row … **Fixed** … The 0.05 Hz rows now sit on the prediction." | The first bullet, which is the right place. But it is buried among six peers of much lower consequence. | **Satisfaction / duplication:** the "joint fit … Adopt it" bullet and the "Routes not yet taken" bullet repeat the plan bullets at goal 242–244. "Better than this session's one-parameter fit, which reads 0.2 s as about 0.17 s" repeats ext 17–18. Fix: promote the design flaw out of the list (it is a correction to Aim 1a, not a theory result), and cut the two plan-duplicate bullets to a pointer to the plan. |

## Findings
Columns: location · issue · severity · suggested fix · verifiable against a source.

1. **ext 13 vs ext 27–29 (goal 37 vs 51–53)** · The two passages contradict each other. Ext 13 says the prediction is "within about 0.03 in every cell". Ext 27–29 says "worst 0.06", and "worst 0.11" at 0.05 Hz. The first number is pre-reseed and says so nowhere. · **High** · Date-stamp the 0.03 as the first run, or replace it with the post-reseed numbers. · yes (`theory_check.json`)
2. **ext 27–28** · The sentence is garbled: "the exact form matches the measured median participants within a median 0.011 … of the planted value". Three quantities (prediction, measurement, planted value), one comparison. Is the 0.011 prediction against measurement, or measurement against planted? It also has no unit (a fraction? participants per event?). · **High** · State the comparison and the unit, e.g. "prediction minus measured median, as a fraction of cells". · yes (`theory_check.json`)
3. **"cell" is overloaded throughout** (ext 13 "every cell", 23 "weakest cells (5 cells per event …)", 50–51 "every cell at one background rate", 62 "At 33 cells", 61 "within one cell") · The word means both a grid condition and an imaged cell, sometimes in the same sentence (ext 23). · **High** · Call the grid unit a "condition" or "grid cell" everywhere in Aim 0. · no
4. **ext 77–80 (goal 101–104)** · There is a logical slip. The heading says "not the only solution", but the body says the other routes reach "the same quantities … not competing answers". So the answer is unique and only the route is not. The phrasing ("not the only solution, but one answer reached three ways") is also close to the banned *not X, but Y* form. It is kept because it answers Tony's literal question, but it answers it ambiguously. · **Med** · "One answer, reached three ways; other routes lead to the same quantities." · no
5. **ext 38 / 40 "independently"** · This overstates what agreement shows, by the house rule "Agreement between methods rules out one thing". Three agents on the same model, with the same question and the same code pointers, rule out one session's slip. They do not rule out a shared misreading of the generator. · **Med** · Add one sentence naming what the agreement excludes and what it leaves. · no
6. **Symbols and abbreviations used before they are defined (Aim 0 sits above Aim 1a, and neither defines them):**
   - σ, w, n, R_n and the "+" positive part (ext 9)
   - k, λ, N (ext 12)
   - K and "the assessment" (ext 20; "the assessment" is never named as a tool anywhere on the page)
   - k_hat and g_3/g_2 (ext 43)
   - q (ext 45)
   - SD (ext 60)
   - ADR-0008 (ext 61): an index, not a name, against "Name things; don't index them"
   - "Count detector" (ext 64)
   - b (ext 72)
   - f3 (ext 74; the prose elsewhere calls it the "triple cumulant")
   - "fast ρ" (ext 121)
   - Kreuz / SPIKE-order (ext 86, 95), with no citation
   - SCE, CoactDetect, LoCo in the plan bullet (SCE is expanded only at goal 196, below its use at goal 250)

   **Med** · Add a one-line symbol key at the top of Aim 0, and expand ADR-0008 by name. · yes (code and ADR files)
7. **Numbers without units, or without saying what of:**
   - ext 13 "0.03"
   - ext 14 "5–15 %" (of what?)
   - ext 21 "within about 10 %"
   - ext 62 "it is 6 … and 12" (cells?)
   - ext 74 "rate 3–5 % above" (which rate?)
   - "0.01 Hz / 0.05 Hz background" throughout: Aim 1a says "Hz per cell", Aim 0 drops the "per cell"
   - the order table's "check" column, which needs "(dimensionless)" in its header, per writing_conventions §units

   **Med** · Add the units and the per-cell qualifier. · yes
8. **ext 101–102 and the ext 115–116 table, "44.5 against 45.0", "0.503 against 0.500"** · The pairs never say which number is the measurement and which is the prediction. · **Med** · Put "measured X against predicted Y" once, or use the column headers "measured" and "predicted". · yes (`membership_limit.py`, `order_limit.py` output)
9. **ext 116–117** · The "M templates" check does not state the τ it was run at. "Constant to ±0.01 from 25 to 800 events" does not say what is constant (F·√n̄?). · **Med** · Name the quantity and the τ. · yes
10. **ext 99–100** · "converges to random as 1/M, and what sets it is … E/M, not M alone" reads as self-contradicting unless E is held fixed. "Dispersion" is also undefined (variance-to-mean?). · **Med** · Say "at fixed E, as 1/M", and define dispersion. · yes
11. **ext 102–103** · "Membership is read perfectly here" sounds like a result, but it is a simulation assumption. "By a factor blind pass B derived" gives no factor and no pointer. · **Low-Med** · "Here the simulation assumes members are seen without error; B's correction factor is in <file>." · yes
12. **ext 107–108** · The sentence is missing a verb: "the indicator F the share of pair agreements with that sort". · **Low** · "…and F is the share of pairs that agree with that sort." · no
13. **ext 27 "After the reseeding below"** · Section 1's closing paragraph depends on a fix that is only explained in section 2. · **Low** · Say "after reseeding (each recording now has its own seed)" inline. Section order is role 11's call. · no
14. **American English:**
    - ext 43 "behaviour"
    - ext 84 "generalises"
    - ext 120 "optimisation"
    - ext 131 "normalisation"

    **Low** · Use behavior, generalizes, optimization, normalization. · yes
15. **ext 50 "`1000 + seed` in every cell"** · "seed" is defined in terms of itself. · **Low** · Name the loop variable (e.g. "replicate index"). · yes (code)
16. **Labels for which blind pass found what are inconsistent** · ext 50 and 69 say "(both)"; the other bullets say "(A and B)". · **Low** · Pick one. · no
17. **Plan bullet, goal 236–254** · "Next, in order:" introduces a mix of three kinds of item:
    - imperatives ("check", "move")
    - noun phrases ("the detectability threshold", "Cramér–Rao bounds")
    - claims stated as results ("two sources: their cumulants add … predicted before it is run"; "a shared slow rate change adds pair excess…")

    The last bullet ("…stay simulated") is a scope statement, not a next step. · **Low-Med** · Make every item a task, and move the scope line out of the ordered list. · no
18. **ext 1 header "not reviewed"** · This goes stale once this murderboard lands. · **Low** · Update it at step 5. · no

**Clean:**
- No banned constructions (the tool found none, and I confirmed by reading).
- No singular "data": the only use, ext 119 "the real data", has no verb.
- No "fire" or "firing".
- The spike-count wording at ext 121 is inside a quotation, so it is exempt.

**Out of scope, noted only:** goal 174, in Aim 1a, uses "robust", which is a banned word.
