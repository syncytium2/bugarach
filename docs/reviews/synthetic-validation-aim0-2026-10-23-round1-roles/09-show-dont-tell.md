GRANT 9 MISMATCH — missing none; holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill, and MCP write tools (Docs, Dropbox, Gmail)

None of the three Aim 0 result sections shows a picture. The only figure is Figure 1, and it is named but never embedded. The two results with the clearest shape, membership and order, have no figure at all. Their numbers exist only as typed rows, though the scripts print 7- and 18-row tables that are plainly curves.

## How I measured
- **Run-time finding:** this run took a fallback path. I am a general-purpose agent and hold editing tools that no reviewer may have. I edited nothing; my only writes are under `_scratch/role-09/`.
- **What I looked at:** the four sections at doc lines 25–54, 55–105, 106–163 and 234–255 of `docs/goals/synthetic-validation.md`, each treated as a "page". I also opened the Figure 1 PNG, read the top of `theory_check.json` and ran `membership_limit.py` and `order_limit.py`; both printed tables that match the doc's numbers.
- **Word counts:** counted with a script (`_scratch/role-09/count.py`). A "block" is a paragraph or a list item, and table words count toward the total but are not a block.
- **Figure share:** this is Markdown on GitHub, so there is no fixed canvas. If an image is embedded with `![...](...)`, GitHub draws it at full column width, so the share would be roughly 100% of the width. Searching the whole doc for `![` finds nothing. Figure 1 is only named: as text in Aim 0, and as a plain filename in backticks under Aim 1a. So the measured share is 0% in every section.
- **Thresholds used:** these are the project's tunable conventions. Flag a page over 40 words; a block over 60 words; a results page with no figure; two or more prose-only pages in a row; a figure under ~50% of the page. A doc section is far longer than a slide, so the 40-word limit flags everything. I treated it as context and relied on the other four tests.

| page | total words | largest block | figure (y/n) | figure share |
|---|---|---|---|---|
| Aim 0, first result (25–54) | 375 | 85 ("coordination-rates tool is predicted exactly") | n (Figure 1 named in text) | 0% |
| Aim 0, replicated blind (55–105) | 622 (incl. one 6×4 ✓ table) | 83 ("design flaw in Aim 1a") | n | 0% |
| Aim 0, membership and order (106–163) | 678 (incl. two tables) | 111 ("Membership" paragraph) | n | 0% |
| Plan, Aim 0 bullet (234–255) | 256 | 47 | n | 0% |

All three result sections are prose-only and come one after another. The Aim 1a section that follows also has no embedded figure.

## Findings
Each row: location · issue · severity · fix, with a named replacement figure · could I verify it against a source.

1. **Membership paragraph, lines 121–127** · This result has no figure. A 111-word block carries a curve as typed pairs ("44.5 against 45.0 at M = 1, 5.30 against 5.40 …"), and `membership_limit.py` prints 7 rows of measured against predicted. · **high** · Use a log–log plot: measured dispersion ratio (points) against E/M, with the predicted line 1 + (E − 1)/M drawn over the 7 points. It shows "converges to random as 1/M, set by E/M" in one look. Move the background-cells and missed-members caveat to the caption or a footnote. · yes (script output matches the doc)

2. **Order paragraph and prediction table, lines 129–141** · This result has no figure. A 3-row table compresses 18 printed rows from `order_limit.py` into two spot checks per case. · **high** · Use a three-panel figure: (a) F against τ, 5 points, with the line (2/π) arctan τ; (b) F against M on log–log axes, 7 points, with the predicted 1/√M line; (c) F against n̄ on log–log axes, 6 points, with the line 0.375/√n̄ (slope −½). Keep the formulas as a one-line caption under each panel. The 92-word description of the method is a sequence, so give it a small schematic (pair lead signs → score sort → F) and move the "two changes from the published method" to notes. · yes

3. **"The last row matters for the real data", lines 143–149** · An 82-word block makes the section's most important claim, linking the no-order bias to the August ρ = −0.75 and the 0.10 control median, and shows none of it. · **high** · Put the August order-free control values on panel (c) of finding 2, drawn against the 0.375/√n̄ curve. That picture is the claim. Keep the link to the todo as provenance in the caption. · partly (the August numbers come from the todo; I did not re-derive them)

4. **Aim 0 first result, the four claim bullets and the closing paragraph, lines 32–53** · The core claim is "the exact form matches the measured median, and removes the 5–15% Poisson residual". It sits in an 85-word bullet plus a paragraph of median and worst-case numbers. The only figure is Figure 1, which is not embedded. In Figure 1 the dashed prediction lines sit almost exactly under the solid lines, so the comparison the text describes is unreadable there. · **medium-high** · Draw a new figure from `theory_check.json`: predicted against measured, one point per cell, with the identity line. Use two marker sets: Poisson in grey (showing the 5–15% offset) and exact in colour (on the line). Facet by background and by the quantity (k, λ, share). Embed Figure 1 here as well, at full width, with `![Figure 1](../learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png)`. The Figure 1 reflow is to move the dashed predictions to their own figure (this scatter) and leave Figure 1 as measured-only. · yes (I opened the PNG; the JSON holds `poisson`, `exact` and `meas` for each cell)

5. **The "window sharing" and "jitter from the pair count" bullets, lines 32–33 and 40–43** · The mechanism g_n(w, σ) and the "window must exceed jitter" behaviour are explained only as formulas. · **medium** · Plot k̂/k = (2 + (k−2)g₃/g₂)/k against σ/w as a single theory curve, with the Aim 1a cells collapsed onto it. This is the dimensionless re-plot the plan itself asks for (line 243), so it serves both. For window sharing, add a small schematic: n jittered onsets, range R_n, window w. · yes (claim in the doc; curve not drawn)

6. **Replicated blind, ✓ table, lines 62–70** · **Prose (a table) is right here, no figure needed.** The table shows which of three methods agreed on six categorical results. A grid of checkmarks is the right form, and a chart would add nothing. · — · No change. · yes

7. **Replicated blind, "what only the blind passes found" and the open residuals, lines 73–99** · 622 words, the longest page, mostly provenance and work not yet done ("Routes not yet taken", the open residuals, how the agents were briefed). The one result on the page, the seed-sharing design flaw (83 words), is itself visual: errors ran together across each row and the 0.05 Hz rows ran low. · **medium** · For the seed flaw: a before/after strip of Figure 1's 0.05 Hz participants row, from `aim1_one_source_shared_seeds.json` against the rerun, on the same axes as the prediction. **Move, don't delete:** "Routes not yet taken", the open residuals and the agent-briefing details go to `blind_README.md`, which already exists. Leave a one-line pointer here. · yes

8. **"Against the brute force", lines 151–156** · 84 words. The runtime contrast is "about 20 s" against annealing, but no annealing time is given. · **low** · Prose is acceptable for a two-number comparison, and a two-bar runtime chart only helps once there is a measured `synfire_scan.py` time. The PySpike ⚠ caveat should stay on the page as one line, because it limits what the section claims. · yes (I timed both scripts at about 20 s; I did not time the annealing)

9. **"Three properties" table, lines 113–119** · **Prose (a table) is right here.** It maps property to the tool that sees it to the tool blind to it. That is a lookup, and the table form works. · — · No change. · yes

10. **Plan, Aim 0 bullet, lines 234–255** · **Prose is right here.** It is a to-do list for future work, with no result to show. Every item is under 60 words. · — · No change. · yes

11. **Doc-wide: three or more prose-only sections in a row (lines 25–189)** · Aim 0 ×3 and Aim 1a carry no embedded image. The house rule says "render it before writing about it", but the doc writes about four results and shows none of them. · **high** · Embed figures in this order: Figure 1 once at full width (the Aim 1a section is its natural home, with Aim 0 pointing to it), then the predicted-against-measured scatter (finding 4), the membership curve (finding 1) and the order three-panel (findings 2–3). After that, each results section's opening paragraph becomes a standfirst of two or three lines above its figure. · yes

Boundary note: I judged Figure 1 itself only on whether it can carry the Aim 0 claim. Its overplotting, eight-entry legend and labels are mechanical checks, and they belong to agent 10.
