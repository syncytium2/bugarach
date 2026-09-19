GRANT 11 ok: Read, Grep, Glob
(The harness also gave me SubagentHandback, which is only the channel this report travels on. I held no Edit, Write, NotebookEdit or Bash.)

Artifact read: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`, the built page. Line numbers below refer to that file. The file is 612 KB because the figures are inlined, so I read the prose in full and the figure and table captions by searching. I judged only the order of the page.

## Spine: one claim per element, in page order

0. **Title and subtitle (L49–53).** A third of chorus_norm's fits do not train. The finding comes from the saved fits of goal 2's two runs plus 14 exact replays, on simulated recordings only.
1. **Intro paragraph (L55–60).** chorus_norm and chorus_gain_norm read one row per ROI and output a logit per frame. A threshold turns the logits into calls, and the calls are scored by F1.
2. **Answer box (L62–90), six claims:**
   - (a) 146 and 153 of 432 inner fits collapse to one call per recording, which gives F1 0.125.
   - (b) For chorus_norm the cause is lr 0.03. For chorus_gain_norm the encoder's shape matters as much.
   - (c) The signal stops in the head: 142 of 153 collapsed fits have a silent head layer, and 0 of 279 working fits do.
   - (d) A collapsed fit never leaves its flat start, and a 200-step warm-up prevents that.
   - (e) This is not PR #596's failure.
   - (f) Tuning stepped around it. 11 of 24 configurations dropped out of contention, 2 refits collapsed, and the repair is goal 2's decision.
3. **§1 paragraph 1 (L93–97).** A collapsed fit's output barely moves and sits above its threshold, so the whole recording becomes one call.
4. **Figure 1 (L98).** A collapsed fit calls a held-out recording one event. A working fit of the same configuration makes 23 calls.
5. **"How the fits are organized" (L99–108).** Definitions: configuration, the 24-configuration grid, inner fit (432 per net per run), refit, draw.
6. **"Which fits collapse is not repeatable; how many is" (L109–114).** The overlap between draws (111 observed, 111.5 expected) says the configuration sets the collapse rate, not which fits collapse.
7. **§2 paragraph 1 (L117–124).** For chorus_norm the learning rate separates configurations almost completely. Within lr 0.03, shape shifts the share, and training length is tangled with depth.
8. **§2 paragraph 2 (L125–129).** chorus_gain_norm follows encoder shape: 4 × 6 collapses at 78% at lr 0.03 and still at 25% at lr 0.01.
9. **§2 paragraph 3 (L130–138).** Within a configuration the fold pair does not matter (p 0.94). The training seed does for chorus_norm (p 0.001).
10. **Figure 2 (L139).** For chorus_norm, lr 0.03 is where fits collapse, shown per configuration.
11. **Table 1 (L139).** Collapsed inner fits by learning rate and encoder shape.
12. **§3 paragraph 1 (L142–148).** Architecture: encoder, three pooled statistics, and an 8 × 8 GELU head that was never tuned. lr 0.03 is 30× Adam's suggested default.
13. **§3 paragraph 2 (L149–162).** Defines the census and "silent". Collapsed fits have silent head layers and flat outputs; working fits have neither. Every collapsed threshold sits at the grid floor.
14. **Figure 3 (L163).** Every collapsed fit has a flat output and most have a silent head layer. No working fit has either.
15. **§3 paragraph 3 (L164–173).** The PR #596 discriminating test. The head's input still separates events (d 1.84 against 2.60); the output does not (0.13 against 4.29).
16. **Figure 4 (L174).** The head's input separates events in collapsed fits and their output does not.
17. **"Round 1 of this page's review…" (L175–180).** An earlier sign-test definition of a dead layer miscounted, so the page uses a variance rule. 24 collapsed chorus_gain_norm fits have no silent layer (points to §6).
18. **§4 paragraph 1 (L183–194).** Exact replays: both fits start flat. The working fit's loss falls below 1.0 by step 220 and the collapsed fit's never leaves its start. The collapsed fit's head goes silent at step 230, after the stall, so silence is a consequence and not the start of the failure.
19. **Figure 5 (L195).** The collapsed fit's head goes silent after its loss has stalled; the working fit's never does.
20. **§4 paragraph 2 (L196–199).** The same collapsed fit trains at lr 0.003, at lr 0.01, and at lr 0.03 with a 200-step warm-up. A 50-step warm-up is not enough.
21. **Figure 6 (L200).** The same fit trains at a lower learning rate or with a slower start. This figure also holds the as-run loss curves that answer the when question.
22. **§4 paragraph 3 and Figure 7 (L201–212).** The 200-step warm-up lets 6 of 7 other collapsed runs train, against 1.4 expected by chance.
23. **Table 2 (L212).** Warm-up results, fit by fit.
24. **"Settled early, mostly" (L213–219).** Twin configurations that differ only in step count show that 60 of 62 collapses are fixed by the shorter length.
25. **"A known failure, with a standard remedy" (L220–226).** Dormant units at large step sizes are documented, and warm-up is the standard remedy.
26. **§5 bullet 1 (L230–236).** For chorus_norm, tuning chose no lr-0.03 configuration. In effect it tuned over a smaller grid than the declared one.
27. **§5 bullet 2 (L237–238).** For chorus_gain_norm, tuning chose lr 0.03 for 30 refits, and its collapsed refits are among them.
28. **§5 bullet 3 (L239–244).** 4 refits collapsed across the two draws, and they match the replicate report's † flags.
29. **§5 bullet 4 (L245–250).** Three repairs are open: drop lr 0.03, add warm-up to the shared trainer, or change the head. Each needs both draws rerun.
30. **§5 bullet 5 (L251–256).** A guard could catch a collapse: output SD is at most 0.132 in collapsed fits and at least 0.803 in working ones, measured on one recording.
31. **Table 3 (L258).** What tuning chose: refits by learning rate.
32. **§6 Limits (L260–276).** Residual risk: simulated recordings only; one census recording; counterfactual replays judged by loss; warm-up tried on chorus_norm only; 24 unexplained chorus_gain_norm collapses; seed effect not explained.
33. **§7 and References (L278–314).** Appendix: data, tool, upstream reports, PR #596 provenance, citations.

## Arc I judged against

This is a diagnosis, so I adapted the default analysis arc:

**the problem (what it looks like) → what it costs → what separates collapsed from working fits (configuration axes) → the mechanism: where the signal stops, then when → the fix and its evidence → the decision it leaves → residual risk**

The request's own order (PR #596 → tabulate → compare outputs → loss curve → repair) fits inside that arc.

The page mostly follows the arc, and some of it follows it well:
- The page opens on the problem: the title, then box bullet (a) with a link to Figure 1.
- The PR #596 check sits at §3, the first place it can be judged, because it needs the encoder and head described first. Putting it there rather than first, where the request listed it, is right.
- Limits come last, before the appendix.

The departures from the arc are below.

## Cold open

**What the reader sees first:** the title, which states the problem, then a provenance subtitle, a paragraph of definitions, and the six-claim answer box, whose first bullet states the problem in words.

**The picture of the problem, Figure 1, is the fourth thing on the page.** It comes below a box whose five later claims use vocabulary the page has not yet given (inner fit, configuration, refit, encoder, head, pooled statistics). So the problem does come first, but only in words; the picture of it arrives late.

## Findings

Format: location · issue · severity · suggested fix · verified

1. **Answer box (L62–90) against the §1 definitions (L99–108)** · The box uses "inner fits", "configurations", "refits", "encoder", "head" and "lr 0.03" before they are defined. The configuration and fit definitions come in §1, and the encoder and head only in §3. Four of the six box claims arrive before the reader can judge them. · **major** · Move the "How the fits are organized" paragraph above the box, or give each term a short inline gloss in the box. Name the learning-rate grid (0.003, 0.01, 0.03) in bullet (b). · verified: yes

2. **Figure 1 (L98), placed after the box** · The one figure that shows what a collapse looks like sits after a definitions paragraph and a six-bullet summary. The problem is first in words, not in the picture. · **major** · Put Figure 1 directly under the intro paragraph, before the box or as its first element, so the reader sees the collapse before reading its diagnosis. · verified: yes

3. **§1 "Which fits collapse is not repeatable; how many is" (L109–114)** · This analytical claim ("the configuration decides how often a fit collapses") sits inside "The problem". It arrives before §2 shows that configurations differ in collapse rate (Figure 2, Table 1), which its "expected at configurations' own rates" figure depends on. It also splits the seed question: §1 says the overlap says nothing about which fits collapse, and §2 paragraph 3 then shows the training seed does matter within a configuration. · **major** · Move the paragraph into §2, after the lr and shape results and next to the fold and seed test (L130–138). Present the two together: the rate is set by configuration, and within a configuration the seed decides. · verified: yes

4. **§5 bullets 1–3 and Table 3 (L230–244, L258): the cost to goal 2** · What the collapse cost goal 2 is the second step of the arc. Here it arrives in the second-to-last section, bundled with the repair decision. That includes the most serious consequence: chorus_gain_norm's collapsed refits went into its held-out scores. Box bullet (f) mentions only the chorus_norm side. The cost claims can be understood as soon as §2 establishes lr 0.03 as the collapse rate. The page does not say why it holds the cost back. · **major** · Move §5 bullets 1–3 and Table 3 into a short "What it cost goal 2" section right after §2. Leave §5 as the decision and the guard. Add the chorus_gain_norm held-out consequence to box bullet (f). · verified: yes

5. **§3 heading and paragraph 2 against §4 paragraph 1 (L141, L149–162, L183–194); box (c) against (d)** · §3, "Where the signal stops", and box bullet (c), "The signal stops in the head", present the silent head as the mechanism. One section later, §4 shows the head goes silent only after the loss has stalled, so it marks the failure rather than starting it. The reader carries a causal reading for a whole section before the page takes it back, and nothing warns them. For a PI who asked specifically for the mechanism, this is the page's main argument, and it arrives in the wrong order. §3 has to stay first, because §4 needs "silent" defined. · **major** · Keep the order but state the deviation. In §3's opening, and in box bullet (c), say this is where a collapsed fit ends up, and that §4 shows the silence comes after the fit has already stalled. Alternatively, retitle §3 as the symptom and discriminating test ("What a collapsed fit looks like inside"). · verified: yes

6. **§4 paragraph 1, Figures 5 and 6 (L183–200)** · The loss curve that answers the request's when question (initialization or during training) is in Figure 6. That figure's headline claim is about the fix, and it is placed after both Figure 5 and the counterfactual paragraph. The text cites Figure 6 before Figure 5, so the numbering runs against the order of citation. · **major** · Split Figure 6. The as-run loss curves go directly after the "loss falls below 1.0 by step 220" sentence and take the lower number. The counterfactual curves stay after paragraph 2. Then Figure 5, the silent-layer onset, follows the curve it is timed against. · verified: yes

7. **§4 paragraph 1, last sentence (L193–194)** · "The replay with a 50-step warm-up stays flat without a silent layer" uses a counterfactual replay before the page has introduced counterfactual replays (paragraph 2, L196–199). It is half of the evidence that silence is a consequence. · **minor** · Move the sentence to the end of paragraph 2, where the 50-step ramp is introduced, and make the consequence claim there. · verified: yes

8. **"Settled early, mostly" (L213–219)** · This is population-level evidence on when a collapse is decided, which supports §4 paragraph 1. It arrives after the prevention argument (paragraphs 2–3, Figure 7, Table 2), so §4 runs when → prevention → when. · **minor** · Move it directly after §4 paragraph 1 and Figure 5, so the when argument is complete before the fix begins. · verified: yes

9. **"Round 1 of this page's review…" (L175–180)** · This is revision history in the middle of the case. It justifies the silent-layer definition, but it comes two paragraphs and a figure after that definition (L151) and after the PR #596 test. Its job is methodological, not a step in the argument. · **minor** · Compress it to one clause at the definition ("a variance rule, not a sign test, because GELU's negative dip carries signal") and move the history and counts to §6 or an appendix note. · verified: yes

10. **§5 bullet 4 against bullet 5 (L245–256)** · The decision bullet says "Three are open", and then a fourth option arrives: a guard that refuses a flat-output fit. The list of choices reads as closed before its last member appears. · **minor** · Put the guard in the options bullet and say it is a guard rather than a repair ("a fourth, which catches rather than prevents"), or put it before the three repairs. · verified: yes

11. **Figure 2 and Table 1 (L139), placed at the end of §2** · Both are cited in paragraph 1 but sit after paragraphs 2 and 3. Paragraph 3 (fold and seed tests) is not about either one. Evidence does follow its claims, but at a distance. Table 3 (L258) likewise comes after all five §5 bullets while only bullet 1 cites it. · **minor** · Put Figure 2 and Table 1 after §2 paragraph 1 (or 2). Put Table 3 after its bullet, or with the moved cost section (finding 4). · verified: yes

## Order checks with no finding

- Intro definitions before the problem (L55–60): these are needed to read "F1 0.125" and "one call", and the paragraph is short. It earns its place.
- PR #596 test placed in §3 (L164–173): this is the earliest position where it can be judged. It earns its place.
- Literature paragraph after the warm-up evidence (L220–226): evidence comes first and context follows. It earns its place.
- §6 Limits and §7 Where everything is: residual risk, then the appendix. Both are placed correctly.

Every section has a job in the spine. None needs to move to an appendix wholesale. The problems are misplaced paragraphs and figures within sections (findings 3, 4, 6, 8, 9), not whole misplaced sections.
