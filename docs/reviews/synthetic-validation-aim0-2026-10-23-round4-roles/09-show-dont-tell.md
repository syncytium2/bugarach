GRANT 9 MISMATCH — missing none; holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill, ToolSearch, SubagentHandback, Claude Docs MCP (batch, guide, update), plus deferred tools (WebFetch, WebSearch, Dropbox, Gmail and others) beyond the grant of Read, Grep, Glob, Bash

**Run finding (about the run, not the artifact):** this role was spawned through the inline general-purpose fallback, not the named agent. It held editing tools that no reviewer may have. I used none of them on the artifact. I wrote only to `_scratch/r4-role-09/` (the counting scripts `count.py` and `share.py`). The run record's `roles:` line must say this review took a fallback path.

**Blindness:** I opened only `_scratch/r4_extract.md`, `_scratch/r4_common.txt`, my role file, the four PNGs, and the tail of `docs/GLOSSARY.md`. I checked that `docs/reviews/synthetic-validation-aim0_2026-10-23.md` exists by path only (it does).

## Method and thresholds
- **Unit:** one "page" is one section of the GitHub-rendered Markdown, taken from extract lines 1–390 and 392–444. Locations below are page line numbers (extract line +15 up to extract 390; +45 after that).
- **Words:** counted by script. Largest block means one paragraph, bullet, caption or table.
- **Figure share:** no figure sets a width in the source (plain `![]()`). Every PNG (1430–1690 px wide) is wider than GitHub's content column (I assumed about 880 px). GitHub styles images `max-width:100%`, so each one renders at the full column width with **no side margins**. Rendered height is then 880 × h/w: Figure 1 551 px, Figure 2 517, Figure 3 384, Figure 4 341.
  - Text height was **estimated, not rendered**: 16 px font, 24 px lines, about 112 characters per line, 16 px block gaps, table rows wrapped by character count. Error is probably ±20%. I had no browser render of GitHub.
  - Share = figure height ÷ section height.
- **Thresholds (conventions, tuned):**
  - The 40-words-per-slide limit flags every section of a reference page, so I reported it but did not flag on it.
  - I applied: any block over 60 words (31 of 73 blocks); any results or methods section without a figure; two or more consecutive prose-only sections; figure share under 50%.

## Count table
| page lines | section | words (≈) | largest block | figure | figure share |
|---|---|---|---|---|---|
| 16–37 | Where it stands | 260 | 87 (l.23, status bullet) | n | 0% |
| 38–68 | Symbols and tools | 352 | 175 (table); prose 65 (l.55) | n | 0% |
| 69–112 | Aim 1a | 644 | 169 (l.85 bullet); caption 134 | y (Figure 1) | 40% |
| 113–199 | Aim 0 predictions | 1244 | 265 (l.180 "What it rests on") | y (Figure 2) | 23% |
| 200–233 | Checked by two more sessions | 382 | 114 (l.202) | n | 0% |
| 234–263 | Membership | 346 | 105 (Figure 3 caption l.252) | y (Figure 3) | 41% |
| 264–349 | Order | 1242 | 191 (Kreuz table); prose 153 (l.310) | y (Figure 4) | 16% |
| 350–357 | Generator | 66 | 62 | n | 0% |
| 358–376 | Settled | 445 | 445 (table) | n | 0% |
| 377–405 | Tried and dropped | 354 | 56 | n | 0% |
| 437–489 | Plan, Aim 0 item | 593 | 114 (l.467 item 5) | n | 0% |

The new GLOSSARY section has 488 words of definitions. Prose is the right form there, so it is not flagged.

## Findings
Columns: location · issue · severity · suggested fix · could I verify it against a source.

1. **l.140–150 and Figure 2 A/E** · The headline claim ("participants predicted to within about 0.01"; residual shrinking from 0.05 to 0.007–0.016 with the at-most-one-event term) cannot be seen in its figure. The A/E axes run 0.3–2.5, so a 0.01 residual is smaller than a marker. The sign-test and SE-null detail (l.140–150, 168–174; 77 + 93 + 112 words) is typed out instead. · **major** · **Replace with a residual panel:** (measured − predicted) ÷ planted against predicted, y axis about ±0.06, coloured points for the full prediction and grey for the Poisson train, one row per background. It shows the shrink, the slightly-high direction (34 and 31 of 48 below) and the rate/share asymmetry (43 and 41 of 48 above at 0.01 Hz) in one picture. The bullets keep only the assertion and the medians; the SE-null and sign-test detail moves to `theory.py` or the folder README. · yes (records exist; numbers not rechecked: not this role)

2. **l.310–318, "With few events…" (153 words)** · The result that matters most for the lab's data has no figure: the detection limit at the lab's scale (about 3 templates at 10 events of 7 cells; about 80 at 140 events of 13) and the no-order F at 10 and 140 events. Figure 4 C covers n̄ 2–68 at 10 cells per event only. · **major** · **Add a detectability chart (for example Figure 4 D):** the largest M whose signal clears the null by 2 SD, against events per recording, one line for 7 and one for 13 cells per event, with the lab's 10–25 events shaded. The prose keeps the assertion; the ± values move to a note or point to `order_limit.json`. · partly (numbers would come from `order_limit.json`, not opened)

3. **All four figure sections (40, 23, 41, 16%)** · Every figure-bearing section is under 50% figure share; Order (16%) and Predictions (23%) are worst. There is no width or margin defect: each figure fills the column. The text around them is the problem. · **major** · GitHub Markdown has no columns, so **reflow by relocation**:
   - Move "What it rests on" (l.180–198, 265 words, the largest block on the page) and "Prior art for the fast sort" (l.340–348, 121 words) into a collapsed `<details><summary>Prior art</summary>` block, or into `learned/synthetic_validation/README.md` behind a one-line link.
   - Move the PySpike test details out of the Kreuz table's "coincidences" cell (l.327) into a footnote under the table.
   - In Order, put Figure 4 right after "The question" (l.266) rather than after three paragraphs.
   - Estimated effect: Predictions rises to about 29% and Order to about 22%. Relocation alone cannot reach 50% on a reference page. The rest of the gap closes only when findings 1, 2, 5 and 8 draw numbers that are now typed. **Relocate, don't delete:** every caveat and citation stays reachable.
   
   · yes (measured, method above)

4. **Captions: Figure 1 l.73–81 (134 words), Figure 3 l.252–258 (105), Figure 4 l.288–293 (89), Figure 2 l.133–138 (82)** · Captions carry argument and provenance.
   - Figure 1: "A fixed K fails at the higher background (F), and there the assessor's jitter is flat (H)" repeats l.85/95. "Each recording has its own seed; the first run's shared backgrounds…" duplicates l.381.
   - Figure 3: the surrogate counts (200, package default 1000) and the definitions of the two nulls are methods text.
   - Figure 4: "an asymptotic form that at M = 2 already sits well below…" is the claim at l.300.
   
   · minor · Cut each caption to what is plotted and why it matters. Move the result sentences to the bullets (already there), the seeding note to Tried and dropped (already there), and the null definitions to the Membership text at l.242 or l.260. · yes

5. **l.95–101 and l.158–167 (119 + 155 words)** · Two key limits are typed as lists of numbers, not drawn: the assessor's 0.74 s ceiling from the ±1.5 s gather, and the lab's jitter (0.105–0.150 s) sitting in the untested gap. · minor · **Annotate Figure 1 D and H:** a shaded vertical band at 0.105–0.15 s labelled "lab's jitter, untested", and a horizontal line at 0.74 s labelled "±1.5 s gather ceiling". The jitter readings in l.96–98 and l.159–161 then shrink to "(D, H)". · yes (values stated on the page)

6. **l.85–94, "A fixed K does not transfer" (169 words, the longest bullet in Aim 1a)** · The K at which chance falls to one cluster per hour (5 versus 8 by the assessor's rule; 6 versus 12 for ADR-0008's floor) is the picture of "does not transfer", and it is typed. Figure 2 D/H shows only K = 3, 4 and 6, predicted against measured. · minor · **Draw chance clusters per hour against K (3–12):** one line per background, the predicted 60 q(1 − q)² curve, a 1-per-hour budget line, and markers at the ADR floor values. It could replace Figure 2 D/H or sit beside Figure 1 F. · partly

7. **l.237–239 (Membership)** · The section's answer to Tony is a contrast between two regimes. Only one is drawn: Figure 3 A shows fixed E. The other ("E = M e: the excess stays near e and never reaches random") is text only. · minor · Add the second regime as a second curve in Figure 3 A, so the converge / don't-converge contrast is visible. · yes (follows from the stated 1 + (E − 1)/M)

8. **l.123–129, "The core prediction" (107 words)** · A mechanism given as prose. · minor (optional) · **Add a schematic:** one event's Gaussian onsets on a time axis tiled by windows of width w, showing a caught pair and a split triple, with an inset of g_3/g_2 (and so k̂) against σ/w. This connects to plan item 8's dimensionless axes. Prose is acceptable if left as is, because the formula carries the argument. · n/a

9. **Prose-only runs: l.16–68 and l.350–489** · Two figure-free sections open the page (about 1,280 px of text before Figure 1), and four close it.
   - Judgment: prose or tables are the right form for Where it stands (status log), Symbols (table), Settled (decision ledger), Tried and dropped (log) and Plan (to-do list), so those are not flagged on form.
   - Fix for the run-up: the tool-definition bullets at l.55–67 repeat the new GLOSSARY entries (population-count tool, assembly, latency template). Replace them with a link to shorten the text before Figure 1.
   - The Generator paragraph (l.350–356) could later become a source-model diagram (source → k, σ, intervals, membership, δ) for Aim 1c; it is optional at 62 words.
   
   · minor · as stated · yes

10. **l.332–339, August-fall bullet (121 words)** · Six numbers in a sentence: medians 0.101, 0.036 and 0.099; significant counts 23/80, 44/82 and 3/40. · minor · A 3-row table (stream · median indicator · significant/total), not a figure. The Kreuz et al. quotation and the "dilution" mechanism stay as prose. · yes (the todo is cited; not opened)

11. **Plan items 3 (l.454, 100 words) and 5 (l.467, 114 words)** · Item 5 is mostly prior-art citations (Baik, Peyrache, Lopes-dos-Santos). · note · Move the citations to the prior-art block from finding 3 and keep the action line. Prose is right for a to-do list. · yes

12. **Boundary hand-off to agent 10 (not my finding to own)** · Figures 1 and 2 render at about 52–54% of their native pixels in an 880 px column, so tick and legend text comes out at roughly 8 px. Whether that is legible is a mechanical check. · note · Refer to Ship It. · no (estimated, not rendered)

**What I checked:** all 11 sections of extract lines 1–444, block-level word counts, the four PNGs (their pixel sizes and what they show against the claims in the text), and the new GLOSSARY section (definitions; prose right).
