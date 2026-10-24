GRANT 5 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update (MCP write tools), plus other deferred MCP tools

The review took a fallback path: I was spawned as a general-purpose agent, not the named role. I used only Read and Grep.

**Run note, blindness breach (accidental), for the ledger.** One Grep over `docs/` was meant to skip `docs/reviews/` with the glob `!reviews/**`, but the exclusion did not work. Two lines from earlier-round files came back:
- `docs/reviews/synthetic-validation-aim0_2026-10-23-round3-roles/08-you-lost-me.md:27`: the Settled table, "circularity column", "run status mirrors per §8".
- `.../05-kill-your-darlings.md:155`: "circularity column" is undefined jargon.

I was already searching for those two phrases because I had flagged them myself, so F17 and F18 were found independently. They are still tainted by what I saw, so weight them that way. I opened nothing else under that prefix.

**Lists I ran.** The banned list and the "data is plural" rule are the ones in `.claude/agents/murderboard/05-kill-your-darlings.md` (generated from `doc_review_process.md`):
- not just X but Y / it's not about A, it's about B / it's worth noting / delve, leverage, robust, seamless, crucial, landscape, tapestry / rhythm triplet / em-dash uplifting close / "In today's ___".
- The data-plural form: determiner + *data* + singular verb.

## Tool output (verbatim, `_scratch/r4_prose_report.txt`, extract line numbers)

```
_scratch/r4_extract.md
  line   construction                       kind   context
  — no banned construction found

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1          4 words    1 sentences
  3        244 words   15 sentences   << over 120
  23         6 words    1 sentences
  25       213 words    1 sentences   << over 120
  40       168 words    8 sentences   << over 120
  54        11 words    1 sentences
  56         2 words    1 sentences
  58       134 words    7 sentences   << over 120
  68       445 words   16 sentences   << over 120
  98        11 words    1 sentences
  100       71 words    5 sentences
  108      107 words    5 sentences
  116        2 words    1 sentences
  118       82 words    4 sentences
  125      609 words   21 sentences   << over 120
  165      265 words   11 sentences   << over 120
  185        9 words    1 sentences
  187      114 words    5 sentences
  197      134 words    1 sentences   << over 120
  205      109 words    1 sentences
  216       32 words    1 sentences
  219       12 words    1 sentences
  221       76 words    4 sentences
  227      100 words    5 sentences
  235        2 words    1 sentences
  237      105 words    5 sentences
  245       52 words    2 sentences
  249       12 words    1 sentences
  251       49 words    3 sentences
  257       50 words    3 sentences
  262      114 words    6 sentences
  271        2 words    1 sentences
  273       89 words    5 sentences
  280      215 words   11 sentences   << over 120
  295      153 words    5 sentences   << over 120
  305       44 words    1 sentences
  310      204 words    5 sentences   << over 120
  317      242 words   13 sentences   << over 120
  335        9 words    1 sentences
  337       62 words    2 sentences
  343        2 words    1 sentences
  345      464 words   12 sentences   << over 120
  362        4 words    1 sentences
  364      340 words   17 sentences   << over 120
  392        7 words    1 sentences
  394       60 words    3 sentences
  400      230 words   13 sentences   << over 120
  420        3 words    1 sentences
  422      227 words   14 sentences   << over 120
  442       27 words    1 sentences
  16 block(s) over 120 words — for each, name its payload sentence and where it sits
```

**Mechanical checks I added by hand:**
- **Data plural.** I grepped `\bdata\b` across the extract, including matches split across a line break: page 32 "on the same data", page 167 "real data will need", page 368 inside a quotation. No agreement errors.
- **Glossary entries.** I read the revised jitter entry (GLOSSARY 468–479) and "## Synthetic-validation vocabulary" (659–698) by eye. No banned construction, no singular "data".

## Judgment columns for the 16 blocks over 120 words (page lines)

| block (extract → page) | words | payload sentence | where it sits | what the other words buy |
|---|---|---|---|---|
| 3 → 18 | 244 | one headline per dated bullet (in bold) | start of each bullet | status log, so this is fine. Weak spot: bullet 1's last fragment (F1) |
| 25 → 40 | 213 | symbols table, not prose | n/a | definitions a cold reader needs; keep |
| 40 → 55 | 168 | a definition per bullet | start | definitions; keep |
| 58 → 73 | 134 | "A fixed K fails at the higher background (F), and there the assessor's jitter is flat (H)." | sentence 5 of 7 | how to read the panels; earned. Could move the finding up to sentence 2 |
| 68 → 83 | 445 | bold lead of each bullet | start, good | bullet 1 (~150 w) holds three points, and its real conclusion (set K per recording) is the last sentence (F2, F3, F4) |
| 125 → 140 | 609 | bold leads (participants within 0.01; chance clusters 60q(1−q)²; joint fit from 0.2 s; rate and share worse) | start of each bullet, except the jitter bullet (see next column) | the SE and sign-test detail is skeptic evidence; keep. The jitter bullet's 18-word bold lead holds no result; its payload (from 0.2 s up, lab's 0.10–0.15 s untested) sits mid-bullet at p.164 (F7) |
| 165 → 180 | 265 | "What is added here: g_n for Gaussian jitter and n onsets, the pair-and-triple form, the at-most-one-event term, and the event rate in the same fit." | sentence 9 of 11 (p.195), near the end | the prior-art chain a skeptic asks for, but written in research order. Promote the novelty sentence (F9) |
| 197 → 212 | 134 | table | n/a | keep |
| 280 → 295 | 215 | bold lead per bullet | start | keep; small ambiguities (F11) |
| 295 → 310 | 153 | "With few events the no-order bias is large, and raw indicators are not comparable across recordings." | sentence 1, good | numbers back it; the last sentences name what is unknown (good voice), but see F12 |
| 310 → 325 | 204 | "F differs from … in four ways" plus the table | intro, then table | the "coincidences" and "null" cells each hold 3 sentences of evidence (~60 w) that a table cell should not carry (F13) |
| 317 → 332 | 242 | bullet 1 "consistent with the no-order bias, but untested"; bullet 2 has no stated payload | start / none | bullet 2 is a citation run; its point (net-wins sorting has bounded guarantees, and Kreuz's lab still anneals) is never stated (F14) |
| 345 → 360 | 464 | table rows | n/a | rows F17, F18 |
| 364 → 379 | 340 | each bullet: what was dropped and why | start | good form; F19 |
| 400 → 445 | 230 | item 3's payload "before any explanation of the August result is claimed" | mid-item 3 | item 3 bundles 4 tasks and a docstring criticism (F21) |
| 422 → 467 | 227 | item 5: "derive the detectability threshold … low-rank structure against sampling noise" | start | the PCA lineage (Peyrache 2009/2010, Chapin & Nicolelis, Lopes-dos-Santos 2011/2013) is thoroughness, not something a plan item needs (F22) |

## Findings

Each row: location (page line) · issue · severity · suggested fix · could I verify it against a source.

- **F1** · p.21–22 · "Rerun the same day with a seed per recording." has no subject and no reason (the shared-background flaw). A cold reader cannot tell why it matters · low · "Rerun the same day with a seed per recording, after the first run's recordings were found to share backgrounds." · yes (p.381–383)
- **F2** · p.100 vs p.93/105 · "B" is used for blind session B ("B reports a 2 % median error") in the same bullet list where "(B)" means Figure 1 panel B (p.93, p.105) · **medium** · write "blind B" every time "B" means the session · yes
- **F3** · p.90, p.99 · "both blind passes" is used in Aim 1a before the blind passes are introduced (p.200) · medium · on first use: "both blind passes (the two extra sessions, *Aim 0, checked by two more sessions*)" · yes
- **F4** · p.93 · "That is the case for a threshold set per recording" can read as "that is the situation for" as well as "that is the argument for". It is also the bullet's conclusion, placed last · medium · "So the threshold should be set per recording from its own null, as ADR-0008's floor is set per window," and move it up to follow the bold lead · yes
- **F5** · p.89 · "against the same budget": the budget (≤ 1 chance cluster per hour) is only implied by the previous sentence · low · "against the same one-per-hour budget" · yes
- **F6** · p.98 · "a 1 s Gaussian cut there has SD 0.74 s" is compressed for the PI · low · "a Gaussian of SD 1 s, truncated at ±1.5 s, has SD 0.74 s" · yes
- **F7** · p.158–167 · the jitter bullet's 18-word bold lead names the method, not the result. The result is buried mid-bullet · medium · lead: "**The joint fit recovers jitter from 0.2 s up; 0.05 s is not resolved and the lab's 0.10–0.15 s is untested.**" Then numbers, then assumptions · yes
- **F8** · p.151, p.158 · "Chance clusters at K: the first failure." / "…: the second failure." reads as if the *prediction* failed. It means "explains Aim 1a's first failure" · **medium** · "Chance clusters at K (explains Aim 1a's first failure)" · yes (p.116)
- **F9** · p.195 · the block's payload, the novelty claim, sits at sentence 9 of 11 · medium · open the block with "What is new here: …", then "The rest is prior art:" and the chain · yes
- **F10** · p.187 · "window loss" for Grün 1999, where the page and glossary call the concept "window sharing" (g_n). That is two names for one thing · low · "the two-onset, uniform-jitter case of window sharing (their 'fission probability')" · yes (GLOSSARY 685)
- **F11** · p.298 · "sits on it at r = 1 to 2.5 (0.503, 0.753)": two values against a range; the reader has to guess the pairing. "(its own misorders)" is terse · low · "at r = 1 and 2.5 (0.503 and 0.753)"; "2 % below at r = 5, where the sort itself misorders cells" · yes
- **F12** · p.171 · "in 30 and 29 at 0.05 Hz, which is no consistent direction": "which" can attach to the whole sentence, but it applies only to 0.05 Hz. The header then claims "measured high at 0.01 Hz", so the split must be read · low · "…at 0.01 Hz; at 0.05 Hz, 30 and 29 of 48, so no consistent direction there" · yes
- **F12b** · p.173 · "found that term of the right sign and size": no "term" has been named, only a dependence · low · "found the dependence contributes a term of the right sign and size" · yes
- **F12c** · p.317–318 · "its median intervals of 25–41 s imply more": the number is left out, though it is one division away · low · "imply 86–142" (59 min ÷ 25–41 s), or say why the two disagree (the glossary's interval/rate note) · yes (GLOSSARY 460–465)
- **F13** · p.327, p.330 · Kreuz table cells carry multi-sentence evidence (review agent's PySpike test; the August null description) · low · keep one clause per cell; move the PySpike numbers and the August-null contrast to a bullet below the table · yes
- **F14** · p.340–348 · the "Prior art for the fast sort" bullet never states its conclusion. "9.7 s against 861.8 s" does not say which method is which · medium · lead: "Sorting by net wins has known guarantees, and Kreuz's lab has dropped annealing elsewhere but not for the sort." Then: "(direct pairwise 9.7 s, annealing 861.8 s)" · no (Mariani 2025 not opened; which number is which is inferred)
- **F15** · p.336 · source line is unwrapped (~140 chars, "spikes and cross-event…") where the rest wraps at about 100 · low (cosmetic, diff noise) · rewrap · yes
- **F16** · p.238 · "the excess over random" is used before "excess" is defined (the variance ratio, p.242–245) · low · "the excess pair co-participation variance over random" · yes
- **F17** · p.362 · "the circularity column" is undefined jargon. Contaminated by the breach (see the run note) · medium · "an out-of-sample test: score on the generator you did not tune on" · yes (no glossary entry)
- **F18** · p.365 · "Run status mirrors per windows_workstation_setup.md §8" reads as a broken verb phrase. "Status mirror" is a project noun, but the sentence has no verb. Contaminated by the breach · medium · "Run-status mirroring is set up per … §8" · yes (docs/handoffs/2026-09-21-slow-bench.md uses "status mirror" as a noun)
- **F19** · p.400 · "Scoped to 0.05 Hz and the 0.7 s ceiling" comes straight after "it can against the quieter background", so a cold reader takes 0.05 Hz as where it *works*. It is where the old claim still holds · **medium** · "The claim now holds only at 0.05 Hz and above about 0.7 s." · yes (p.95–98)
- **F20** · p.441–443 · the parenthetical about page structure ("This page adds *What the tree has* and *The plan* …") sits inside the Aim 0 plan item. It is about the page, not the aim · low · move it to the top of "The plan" or into a page-structure note · yes
- **F21** · p.454–461 · plan item 3 bundles comparing against PySpike, an order-free `synfire_scan` run, a library writer, a `max_tau` flag/PR #89, and a docstring correction. "which `synfire_scan.py`'s docstring overstates" has an unclear antecedent (it overstates reproducibility) · medium · split into 3a (compare), 3b (August control), and a "needs:" sub-list; "the docstring claims reruns reproduce; they do only in the same call order and C runtime" · yes
- **F22** · p.470–476 · item 5 spends ~70 words on the PCA method's citation lineage, more than the plan needs · medium · keep "`bugarach.assembly` notes Marchenko–Pastur is unavailable with fewer events than cells, and `assembly_report.md` found PCA flags every simulated recording (method: Lopes-dos-Santos et al. 2013)"; the lineage can go to the script or glossary · yes
- **F23** · p.162 · "1 and 4 of 20 fits at the 0.005 s search bound": the 20 (conditions × recordings?) is unexplained · low · "of the 20 recordings at 0.05 s" · no (the denominator is inferred: 4 conditions × 5)

**Clean, with what I checked:**
- Banned constructions: none in the page extract (per the tool) or in the reviewed glossary entries (by eye).
- No rhythm triplets: the three-item "⚠ Not searched" list (p.196–197) names three real fields.
- No throat-clearing openers, no recap closers.
- Data plural: clean.
- Glossary entries read clearly. The one consistency note is F10, where they name window sharing and the page uses another term.

**Severity count:** 0 blocking; medium F2, F3, F4, F7, F8, F9, F14, F17, F18, F19, F21, F22; the rest low.
