GRANT 5 ok — Read, Grep, Glob (the harness also provides SubagentHandback, which is only for handing this report back. I hold no Edit, Write or NotebookEdit.)

# Role 5, Kill Your Darlings, round 1
Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`, the built page. Every quote below comes from the HTML, not from the f-string in `tools/diagnose_chorus_collapse.py`.

## Mechanical search
`murderboard_prose.sh` is not vendored here, so the script did not run. I ran the process file's banned-construction list by hand with Grep on the built HTML. The list is the house convention from `doc_review_process.md`, role 5, as restated in the task. I added the house-rule checks from CLAUDE.md and `writing_conventions.md`.

| construction | pattern run | hits |
|---|---|---|
| not just X, but Y | `not just`, `not only` | 0 |
| it's not about A, it's about B | `it'?s not about`, `it is not about` | 0 |
| it's worth noting | `worth noting` | 0 |
| delve / leverage / robust / seamless / crucial / landscape / tapestry | word stems | 0 |
| In today's ___ | `in today'?s` | 0 |
| em-dash pivot into an uplifting close | `—`, `&mdash;`, `&#8212;`, ` -- ` | 2 (lines 73 and 74). Both are one parenthetical pair inside §1. Neither is a pivot and neither closes anything. **Not a hit**, but see the §1 row: they sit inside a 62-word sentence. |
| rhythmic three-item list | read by hand | 0. Every list of three (the §5 repairs, the §6 limits) names three real, distinct things. |
| singular "data" (house) | `data (is\|was\|has\|does\|itself)`, `this data` | 0 |
| British spelling (house) | centre, colour, behaviour, modelling, labelled, analyse, favour, -ise | 0 |
| 8-hex configuration hashes | `\b[0-9a-f]{8}\b` | on 5 lines. Visible prose: line 123 (`2736f584`) and line 136 (`e86433df`). Table 2 at line 140 carries 8 of them. The rest are SVG tooltips (lines 91 and 120). |

Block sizes. I counted these by hand because the tool was unavailable, so they are approximate:

| block | words (approx.) | sentences |
|---|---|---|
| subtitle | 22 words | 2 sentences |
| answer box (4 bullets) | 180 words | 8 sentences |
| §1 paragraph | 140 words | 4 sentences |
| §2 paragraph | 120 words | 5 sentences |
| §3 paragraph 1 | 190 words | 7 sentences |
| §3 paragraph 2 | 75 words | 4 sentences |
| §4 paragraph | 215 words | 9 sentences |
| §5 (4 bullets) | 250 words | 11 sentences |
| §6 limits | 100 words | 6 sentences |

## Passage test
For each block: the one sentence it exists to deliver, where that sentence sits, and what the other words buy.

- **Answer box.**
  - Payload: "chorus_norm fits collapse at the top learning rate: the head's layers die in the first steps, and a lower learning rate or a 200-step warm-up prevents it."
  - The payload is spread over bullets 1 to 3, which is fine for a summary.
  - Missing: what the collapse did to goal 2's result. Tuning never chose a learning rate (lr) of 0.03, so chorus_norm was in effect tuned over 13 of its 24 configurations. That consequence sits at the bottom of §5, bullet 1.
  - Missing: the generalization evidence. The warm-up rescued 7 of 8 other collapsed fits.
  - Bullet 4 (PR #596) buys disambiguation that a reader of the earlier diagnosis needs. Keep it.
- **§1.**
  - Payload: "In both draws about a third of chorus_norm's inner fits collapsed to one call per recording, mostly the same fits, so the collapse follows the configuration and starting weights rather than the recordings."
  - It sits at sentence 3 of 4. The fold/seed arithmetic in sentence 1 buys the 432 denominator, which a sceptic needs.
  - The last sentence ("It matters because chorus_norm's scores mix a working model with one that never trained") is the one §5 then contradicts (see findings).
- **§2.**
  - Payload: "The learning rate separates collapsing configurations almost completely: 42% to 92% of fits at 0.03, 7 of 468 below it." It sits first. Good.
  - The width/depth breakdown and the seed/fold shares are evidence a sceptic asks for. Keep them, but they read as a data dump (see findings).
- **§3 paragraph 1.**
  - Payload: "152 of 153 collapsed chorus_norm fits have a dead head layer against 1 of 279 working fits, which flattens the output until the whole recording is one call." It sits mid-paragraph, after about 70 words of architecture.
  - The architecture and the definition of GELU (the activation function) are both needed to define "dead" and the "negative residue". They buy something.
  - The two exception sentences at the end are the evidence a sceptic demands. Keep them.
- **§3 paragraph 2.**
  - Payload: "In chorus_gain_norm, 15 of 75 collapses have no dead layer and are spread across learning rates: a second route this page does not explain." It sits last.
  - The vote-gain sentence buys a clue with no interpretation attached (see findings).
- **§4.**
  - Payload: "Replayed exactly, the collapsed fit's head starts dying by step 30. The same fit trains at a lower learning rate or with a 200-step warm-up, and that warm-up rescued 7 of 8 other collapsed fits."
  - It is split, with the general half at the very end, after about 180 words on one example.
  - "Reproduced its saved checkpoint to the last bit" and "both start with an output that barely varies" are evidence. Keep them.
  - The configuration hashes buy nothing for the reader.
- **§5 bullet 1.**
  - Payload: "chorus_norm was in effect tuned over 13 of its 24 configurations." It sits last.
  - "Did not put dead models into … scores wholesale" is a hedge. Bullet 2 has the exact number.
- **§5 bullets 2 to 4.** Each one's payload is its bold lead. Good.
- **§6 and §7.** These are lists of limits and pointers. They deliver what they say.

## Findings
Format: location · issue · severity · suggested fix · verified

1. **§1, last sentence, against §5 bullet 1** · issue: §1 says "It matters because chorus_norm's scores mix a working model with one that never trained." §5 then says tuning never picked an lr-0.03 configuration, so dead models did *not* reach the held-out scores wholesale: 2 of 95 chorus_norm refits collapsed. The page states its own stakes and then withdraws them · severity: **major** · fix: rewrite the §1 close to the true consequence: "It matters because a collapsed fit scores badly in tuning, so the collapse decides which configurations chorus_norm can be tuned over." Then cut "wholesale" in §5 and give the number: "2 of its 95 refits collapsed". · verified: yes (lines 77–78 and 146–155 of the built page).

2. **Answer box** · issue: the box gives the mechanism but not the consequence for goal 2, which is what the PI reads the box for. The consequence (lr 0.03 was never chosen, so the effective grid was 13 of 24 configurations) and the fact that collapse is detectable (output spread at most 0.13 in collapsed fits against at least 0.80 in working ones) are buried in §5. This is a within-block promotion. Section order is role 11's · severity: **major** · fix: add a fifth bullet: "**What it did to goal 2:** tuning stepped around it: no lr-0.03 configuration was chosen, so chorus_norm was tuned over 13 of its 24 configurations. A spread check at the end of training would catch a collapse." · verified: yes.

3. **Answer box, bullet 2** · issue: the denominator changes without warning. Bullet 1 reports "292 of its 396 inner fits" (both draws). Bullet 2 then reports "152 of 153 collapsed chorus_norm fits" and "1 of the 279 working fits" (second draw only). A reader cannot reconcile 292 with 153 · severity: **major** · fix: "in the second draw, 152 of 153 collapsed chorus_norm fits…" · verified: yes (lines 53–58).

4. **Answer box, first use of "collapses"** · issue: the box uses "collapses" before the page defines it. §1 defines it as one call covering the whole recording, and the box is often the only thing read · severity: **minor** · fix: bullet 1: "chorus_norm collapses (outputs the whole recording as one call) in 292 of…" · verified: yes.

5. **Answer box, bullet 3** · issue: "a collapsed fit's head starts losing whole layers by step 30" reads as a general law. It rests on one replayed fit. The box also leaves out the 7 of 8 other fits the warm-up rescued, which is the part that generalizes · severity: **minor** (role 4 owns whether the claim is supported; this row is about the wording) · fix: "Replayed exactly, the one collapsed fit we traced loses whole head layers by step 30 … a 200-step warm-up also rescued 7 of 8 other collapsed fits." · verified: yes (lines 59–62 against 123–136).

6. **Answer box, bullet 4; §7** · issue: "PR #596" is a lookup key, and "starting deaf" is jargon the page never defines · severity: **minor** · fix: name the failure and push the key into parentheses: "This is not the silent-encoder failure fixed earlier (PR #596), where plain chorus's per-cell encoder produced no signal at any learning rate." · verified: yes.

7. **Subtitle** · issue: "reloaded and replayed; nothing in the runs was retrained" contradicts §4. §4 retrains fits, replayed and with changes, 11 training runs in all. "Draws" and "goal 2" are also both undefined at this point. goal 2's name, from `docs/goals/README.md`, is "a fair comparison of the coded detectors against the nets" · severity: **minor** · fix: "A diagnosis from the saved fits of the two runs (draws) of the fair comparison of coded detectors against nets. The runs' results were not changed; a handful of fits were retrained from their saved starting weights to watch the collapse. Simulated recordings only." · verified: yes.

8. **§1, sentence 2 (lines 71–76)** · issue: one 62-word sentence carries four facts: the two counts, what a collapse is, its F1, and the 111 repeat fits. Inside it sits an em-dash parenthetical holding the page's only definition of "collapse" · severity: **minor** · fix: split it into two sentences. Put the definition first: "A collapsed fit makes one call covering the whole recording, which matches one of 15 planted events (F1 0.125)." Then the counts. · verified: yes.

9. **§1, "each pair of 4 folds"; "goal 2's comparison"** · issue: "each pair of 4 folds" is ambiguous; it means each of the 6 pairs drawn from 4 folds. "goal 2" is an index where a name belongs · severity: **minor** · fix: "on each of the 6 pairs of folds drawn from 4"; name the comparison at first use. · verified: yes.

10. **§2, "chorus_gain_norm shows the same pattern, milder."** · issue: Figure 1B shows a different pattern. At lr 0.03, 9 of its 12 configurations collapse in 0 to 10 of 36 fits and 3 collapse in 23 to 31. At lr 0.01, several collapse in 5 to 12 of 36. §3 then says 15 of its collapses take a second route, not concentrated at lr 0.03. So the sentence says something vaguer than the figure beside it · severity: **major** · fix: "chorus_gain_norm is different: at lr 0.03 three of its 12 configurations collapse in most fits and the rest rarely, and it also collapses at lr 0.01 (§3)." · verified: yes (from the figure's own tooltips, lines 91 and 111–118).

11. **§2, width/depth sentence (lines 84–86)** · issue: a telegraphic dump: "by width, 4 units 80% (172 of 216 fits); 8 units 67% …". The reader has to parse four percentages to reach a point the sentence never states · severity: **minor** · fix: state the direction first: "Within lr 0.03, narrower and deeper encoders collapse more: 80% of fits at width 4 against 67% at width 8; 85% at depth 6 against 60% at depth 4." · verified: yes (172 + 120 = 292 and 108 + 184 = 292, both consistent).

12. **§5 bullet 2 and §6 bullet 1, "census"** · issue: an undefined term used four times. "The census" first appears at §5 ("were in the census"). §3 describes the reload-and-run but never names it. The name exists only in the anchor id `fig-census`, which a reader never sees · severity: **major** · fix: name it where it is done, in §3: "Every second-draw inner fit of both chorus_norm and chorus_gain_norm was reloaded and run on one recording; call this the census." · verified: yes (Grep: the visible uses are at lines 156, 163, 171 and 173; lines 103 and 120 are an href and an id).

13. **§3, "Every second-draw chorus inner fit"** · issue: "chorus" is ambiguous here, because the page also uses it for plain chorus, a different net. The sentence means chorus_norm and chorus_gain_norm · severity: **minor** · fix: name both nets. · verified: yes.

14. **§3 and Figure 2 caption, "bench recording", "seed 2000", "threshold falls to the bottom of its grid"** · issue: two undefined terms and one lookup key. "Bench recording" and the threshold grid are never defined; "seed 2000" means nothing to the reader · severity: **minor** · fix: "one held-out simulated recording with a quiet background (simulation seed 2000)"; "the fit's detection threshold, chosen from a fixed grid, falls to its lowest value". · verified: yes.

15. **§3 and §5, output spreads 0.0055 / 5.20 / 0.047 / 0.13 / 0.80; Table 2 "final loss"** · issue: these numbers carry no unit and no "dimensionless" (house rule). The logit spread is in logit units, and the loss type is never named · severity: **minor** · fix: "(standard deviation of the output logit, in logits)"; set the Table 2 header to `final loss (cross-entropy, dimensionless)` or whatever the loss actually is. · verified: partly. The numbers are unitless on the page; I did not check the loss type in code.

16. **§3 paragraph 2, the vote-gain sentence (lines 116–118)** · issue: "end a median 3% from where they started, against 13% in working fits" is a clue with no stated meaning, so the reader has to guess what it suggests · severity: **minor** · fix: add the reading and name the uncertainty: "…so in these fits the gains barely learned; whether that is cause or symptom is not established." Otherwise cut it. · verified: yes.

17. **§4 prose (lines 123 and 136) and Table 2, configuration hashes** · issue: `2736f584` and `e86433df` in prose, and 8 hashes as the only identifier in Table 2's "fit" column, are lookup keys. The prose already has the property that matters for `e86433df` ("collapsed in 31 of its 36 fits"). The reader can only tie Table 2's first row to Figure 3 by matching `2736f584` across two places · severity: **major** (the house rule is explicit, and the page is written for outside readers) · fix:
    - Name each fit by what distinguishes it: its encoder width and depth, and how many of its configuration's 36 fits collapsed. For example: "a width-4, depth-6 configuration that collapsed in 33 of 36 fits (2736f584)".
    - Move each hash into parentheses, or into a last Table 2 column for lookup.
    - Mark the Figure 3 configuration's row "(Figure 3's configuration)".
    - Add width and depth to the Figure 1 tooltips so the figure and the prose share a name. The hashes can stay in the tooltips for lookup.
    · verified: yes.

18. **§4, §5 bullet 3 and §6 bullet 4, warm-up counts** · issue: the page counts the same experiment two ways. §4 and §5 say "7 of 8 fits tried"; §6 says "Warm-up was tried on 9 collapsed fits". Both are true (8 others plus the Figure 3 fit), but a reader sees two denominators for one test · severity: **minor** · fix: use one count everywhere: "a 200-step warm-up rescued 8 of the 9 collapsed fits it was tried on (the Figure 3 fit and 8 others)". · verified: yes.

19. **§4, payload placement and voice** · issue: 215 words, in which the general result (7 of 8 rescued) arrives in the last two sentences, after about 180 words on one fit. "4 of its 8 at the end" is elliptical, and "the end" has no step count. The run of passives ("was then replayed", "was then applied") is off the house voice · severity: **minor** · fix: open with the general result, then give the traced example. Write "4 of its 8 head layers dead at step N". Make the verbs active ("Replaying the collapsed fit with one change: …"). · verified: yes.

20. **§5 bullet 2 (lines 154–157)** · issue: a sentence opens with a numeral ("4 refits collapsed"). The parenthetical list of four near-identical tuples is prose doing a table's job. "The second draw's 3 were in the census, and 3 of them have a dead head layer" is roundabout. The bullet also skips the notable fact that chorus_norm's two collapsed refits are at lr 0.01, not at 0.03 · severity: **minor** · fix: "Four refits collapsed: chorus_norm's two, both in the second draw at lr 0.01, and chorus_gain_norm's two, one per draw at lr 0.03. All 3 from the second draw have a dead head layer; the first-draw one was not examined." · verified: yes.

21. **§5 bullet 1, "a lr-0.03 configuration"** · issue: grammar. "lr" is read as "ell-arr", so the article is "an" · severity: **minor** · fix: "an lr-0.03 configuration". · verified: yes.

22. **Whole page, "lr" and "F1"** · issue: abbreviations used without definition (house rule). "lr" first appears in Figure 1's labels and Table 1's headers; "F1" appears in §1 · severity: **minor** · fix: "learning rate (lr)" at its first prose use, in answer-box bullet 1; "F1 (the harmonic mean of precision and recall)" in §1. · verified: yes.

23. **§5 bullet 3, "Three follow from the evidence"** · issue: the third option, changing the head, "was not tested here", so it does not follow from the evidence · severity: **minor** · fix: "Three are open: …" · verified: yes.

24. **§6 bullet 1** · issue: three facts chained with semicolons · severity: **minor** · fix: split into sentences. · verified: yes.

## Checked and clean
- None of the process list's banned constructions appear.
- There is no throat-clearing, no section preview, and no closing recap.
- §3 paragraph 2 ("this page does not establish what it is") and the §6 limits name what the page does not know instead of hedging around it.
- "Data" is never used with a singular verb, and I found no British spellings.
- Figure references carry both a number and a name ("Figure 1, collapse by configuration").

## Summary
There are 24 findings: 6 major (rows 1, 2, 3, 10, 12 and 17) and 18 minor. None is blocking.
