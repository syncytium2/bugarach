GRANT 9 MISMATCH — missing none; holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill, Claude Docs MCP tools (batch, update; others deferred), plus Read, Grep, Glob, Bash
(Spawned through the inline fallback as a general-purpose agent. I held editing tools and used none of them on tracked files. The only file I wrote is my own measuring script, `_scratch/r3-role-09/measure.py`. The run record's `roles:` line should say this role took the fallback path.)

## How I measured

- **Unit.** Each `##`/`###` section of `_scratch/r3_extract.md` counts as one page, and the plan item is its own page.
- **Words.** Counted by script, with markdown syntax and link targets stripped. A "block" is one paragraph, one list item or one table cell.
- **Figure share.** The share is the figure's rendered height divided by the section's estimated rendered height. I did not render the page in a browser.
  - All four PNGs are wider than GitHub's content column (1430–1690 px wide, 130 dpi). GitHub's `max-width:100%` scales each to the full column width, about 880 px, so no figure has any side margin.
  - Rendered figure height = 880 × aspect ratio: Figure 1 0.61, Figure 2 0.57, Figure 3 0.42, Figure 4 0.37.
  - Text height assumes a 16 px font, 24 px line height, about 105 characters per line and 16 px paragraph margins. Table rows are wrapped with equal column widths.
  - The estimate is good to about ±25%.
- **Thresholds** (conventions, not optima):
  - A text block over 60 words.
  - A results section with no figure.
  - Two or more consecutive prose-only results sections.
  - A figure-bearing section where the figure is under 50% of the section.
- **The 40-words-per-slide rule does not fit a goal page that is mostly reference material.** I report the counts but do not flag on them.

## Count table

| section (extract lines) | total words | largest block | figure | figure share |
|---|---|---|---|---|
| Where it stands (1–15) | 150 | 85 (L7 status entry) | n | 0% |
| Symbols and tools (17–39) | 227 | 64 (L32 tool description) | n | 0% |
| Aim 1a, first result (41–73) | 411 | 104 (L56 "fixed K") | y, Fig 1 | **44%** |
| Aim 0, the predictions (75–137) | 738 | **143** (L90 "What it rests on") | y, Fig 2 | **28%** |
| Aim 0, checked by two sessions (139–174) | 377 | 114 (L141 intro) | n | 0% |
| Aim 0, membership (176–200) | 238 | 120 (L192) | y, Fig 3 | **44%** |
| Aim 0, order (202–268) | **819** | 121 (L210 Fig 4 caption) | y, Fig 4 | **16%** |
| What membership and order change (270–276) | 60 | 60 | n | 0% |
| Settled (278–295) | 346 | 40 (table cell) | n | 0% |
| Tried and dropped (297–313) | 193 | 42 | n | 0% |
| Plan item "Aim 0" (316–350) | 417 | 85 (L330 item 5) | n | 0% |
| GLOSSARY new section (GLOSSARY.md 659–691) | 396 | — | n | n/a |

- **Whole reviewed span:** about 1,730 px of figure in about 11,350 px of page, or **15%**.
- **Blocks over 60 words: 19.** They start at lines 90, 192, 210, 141, 119, 261, 56, 252, 45, 83, 7, 330, 133, 229, 126, 62, 185, 32 and 104 (excluding 104, the next is 67 at 63 words, then 222 at 63).
- **Every figure-bearing section is under 50%.**

## Findings

Each finding gives location · issue · severity · fix · whether I could verify it against a source.

1. **Aim 0, order (L202–268): 819 words carried by one figure at 16% of the section.** · **major** · verify: yes (measured).
   - The section holds three separate arguments: the closed forms, the lab-scale warning and the Kreuz comparison (table, August result, prior art).
   - Reflow: split it in two.
     - "Order, closed forms" keeps Figure 4 and the three bullets. That alone takes the figure to about 40–50% of its section.
     - "Order, against Kreuz" holds the table and the August bullet.
   - Relocate, don't delete: "Prior art for the fast sort" (L261, 105 words) and the PySpike `rand()` and +33%-coincidence test details in the table cells go to `docs/learned/synthetic_validation/README.md` or an appendix. Leave a one-line pointer.

2. **"At the lab's scale the order signal may sit below the bias" (L235–238) is a key quantitative conclusion with no figure.** · **major** · verify: yes (the numbers are in the text and in Fig 4B).
   - Replacement figure: in Figure 4B, add a horizontal shaded band at F = 0.18–0.35, labelled "no-order bias at the lab's n̄ ≈ 1–4.5".
   - The reader then sees the crossing at M ≈ 4 instead of being told it. The paragraph shrinks to one sentence.

3. **The core prediction (L83–88) is the mechanism under the whole page, and it is told, not shown.** · **major** · verify: partly (the formula is in the text; I did not rerun `theory.py`).
   - Figure 2 shows only predicted-against-measured ratios, never the curve itself.
   - Replacement figure, two parts:
     - **Schematic:** one event's Gaussian onset spread (σ) under windows of width w, with the "all n in one window" probability g_n shaded.
     - **Line plot:** k̂/k against σ/w for k = 10 and 20, prediction curves with Aim 1a's measured points.
   - This is also plan item 9 (dimensionless axes), so it could be built once and serve both.

4. **Aim 0, the predictions (L75–137): figure at 28% of the section; the 143-word block at L90 ("What it rests on") is provenance on the face of the page.** · **major** · verify: yes (measured).
   - Relocate the lineage paragraph (Neyman–Scott, CuBIC, Grün 1999, Pazienti 2008, the ⚠ prior-art gaps) to a "Prior art" appendix or the folder README. Keep one sentence: what is new is g_n for Gaussian n-onset loss, the at-most-one-event term and the joint fit.
   - The residual bullets (L115–132) type out a grid of numbers: quantity × background × median/worst. Turn them into a 3 × 2 table (participants, rate, share by 0.01 / 0.05 Hz, each "median (worst)") or a residual dot plot.
   - Move the 43/48 and 41/48 one-way-bias counts and the surrogate-dependence hypothesis to notes under the table.

5. **Aim 1a (L41–73): figure at 44%; the bullets repeat values Figure 1 already carries.** · **minor** · verify: yes (checked against the Figure 1 image: F shows K = 3/4 at about 16× and 8×; D/H show the joint fit on the identity line).
   - Each bullet should be its assertion plus a panel letter. Specific numbers go in a small table, or stay as one figure each.
   - The ⚠ shared-seed paragraph (L52–54) duplicates *Tried and dropped* L301–302. Move it there and leave a footnote marker.
   - Candidate added panel: event floor against background (6 cells at 0.01 Hz, 12 at 0.05 Hz), with planted k = 5/10/20 and K = 3/4/6 marked. It shows why a fixed K fails, which L56–61 argues in 104 words.

6. **Aim 0, membership (L176–200): figure at 44%; the 120-word paragraph at L192 restates panel B and the figure's own annotation.** · **minor** · verify: yes (checked against the Figure 3 image).
   - Panel B already plots 83% at reuse 0.3 and 27% at 0.045. The "M = 1 reads uniform-only" note is already printed on the figure.
   - Keep the assumptions and the formula 1 + (E − 1)/M on the face. Move the Kish analogy (⚠ not opened) and the unequal-use Σp_m² variant to notes.

7. **Figure 4 caption (L210–216, 119 words) carries the definition of F, which the body repeats at L218–221.** · **minor** · verify: yes.
   - A caption says what the figure shows and why it matters. Keep the panel key and the last two sentences.
   - Move "F is the net agreement…" into the body only, where it already appears.
   - The other three captions (63–90 words) state what is shown and why, and are acceptable.

8. **Aim 0, checked by two sessions (L139–174): a results section with no figure.** · **no change needed; prose and table are right here.** · verify: yes.
   - What it compares is categorical (which derivation each session reached), and the 5-row table is the right display.
   - Relocation only: the 114-word intro's account of what the sessions shared (prompt, repo, model) can go to `blind_README.md`, leaving the bold assertion and one sentence.
   - Optional: show the two open residuals (L173–174) as blind-pass markers in Figure 2 rather than as prose.

9. **Two consecutive prose-only sections at the top (Where it stands, then Symbols and tools).** · **minor** · verify: no (judgment).
   - The status log and the symbols table are right as prose and table.
   - The two tool descriptions (L32–39) are mechanisms the PI must hold for every later figure. Replacement: one schematic pipeline for each tool.
     - **Coordination-rates tool:** onsets → windows → pair/triple counts vs time-shifted surrogates → excess → k̂, rate, share.
     - **Assessor:** 1 s bins → cluster ≥ K → ±1.5 s gather.
   - The ±1.5 s gather panel would also show the jitter-ceiling mechanism of L62–66: a 1 s Gaussian cut at ±1.5 s gives SD 0.74 s.

10. **Settled, Tried and dropped, the plan item, the generator paragraph and the GLOSSARY section: no figure flag.** · **no change needed** · verify: yes.
    - These are decision logs, plans and definitions, so prose and tables are correct.
    - Relocation only: the citations in plan item 5 (L330–336, 85 words) go to a references note.

## No findings on

- **Side margins:** none of the four figures has empty side margins, since all scale to the full column on GitHub.
- **Geometry and legibility:** I did not judge figure geometry or legibility at the roughly 54% downscale Figure 1 gets; those belong to agent 10.
