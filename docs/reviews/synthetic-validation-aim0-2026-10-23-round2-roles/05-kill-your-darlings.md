GRANT 5 MISMATCH — missing none; holds Bash, PowerShell, Edit, Write, Agent, Artifact, Skill, ToolSearch, Claude Docs MCP tools (update, batch, guide), plus deferred NotebookEdit, SendMessage, WebFetch/WebSearch, Gmail, Dropbox MCP and others. I was spawned through the inline general-purpose fallback. I used only Read and Grep, and I edited nothing.

**Role 5: Line editor ("Kill Your Darlings").** I reviewed `docs/goals/synthetic-validation.md` lines 16–241 and 286–311, and the new `docs/GLOSSARY.md` entries (lines 473–476, 656–672). All locations below are **goal-page line numbers**: the tool's extract lines plus 15 for extract lines 1–226, plus 58 for extract lines 228 onward. Banned list run: the house list in `05-kill-your-darlings.md`, unedited.

### Tool output (verbatim, `_scratch/r2_prose_report.txt`, run by the main thread)
```
_scratch/r2_extract.md
  line   construction                       kind   context
  — no banned construction found

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1          4 words    1 sentences
  3        191 words   11 sentences   << over 120
  20         6 words    1 sentences
  22       102 words    2 sentences
  29        77 words    3 sentences
  36        11 words    1 sentences
  38         2 words    1 sentences
  40        95 words    3 sentences
  47        43 words    2 sentences
  51       217 words    7 sentences   << over 120
  65        12 words    1 sentences
  67        42 words    3 sentences
  72       109 words    5 sentences
  80         2 words    1 sentences
  82        58 words    2 sentences
  88       354 words   10 sentences   << over 120
  111        9 words    1 sentences
  113      132 words    5 sentences   << over 120
  124      165 words    1 sentences   << over 120
  132      151 words    2 sentences   << over 120
  142       32 words    2 sentences
  146       13 words    1 sentences
  148       88 words    6 sentences
  155        2 words    1 sentences
  157       62 words    3 sentences
  163      108 words    6 sentences
  171        2 words    1 sentences
  173      64 words    4 sentences
  178      111 words    6 sentences
  187      293 words   11 sentences   << over 120
  210       61 words    2 sentences
  215        4 words    1 sentences
  217      124 words    6 sentences   << over 120
  228      296 words   20 sentences   << over 120
  9 block(s) over 120 words — for each, name its payload sentence and where it sits
```
The tool reports no banned construction. My own search of the extract for each banned word, em-dashes, "not just", "worth noting" and "In today" found nothing. There is no rhythm-built three-item list: each list I found counts real items. **"Data" plural:** the word "data" does not appear in the extract at all, so this check is clean. I also read for a match split across a line break and found none.

### Passage test: the 9 blocks over 120 words
| block (extract → page) | words | payload sentence | where it sits | what the rest buys |
|---|---|---|---|---|
| 3 → 18 (Where it stands) | 191 | "Both faults are fixed and every number below is recomputed." | last | It is a dated log, so the length is mostly earned. The murderboard bullet's list of findings repeats "Tried and dropped". Keep. |
| 51 → 66 (Aim 1a bullets) | 217 | "A fixed K does not transfer across backgrounds" and "the assessor cannot measure jitter" (the two in "Where it stands") | bullets 3–4 of 4 | These are evidence, so they are earned. Move the two headline bullets first; the share and participants bullets are lesser results. |
| 88 → 103 (Aim 0 predictions) | 354 | "Participants are predicted to within seed noise, and jitter by the joint fit, for events of 10+ cells; rate and share less well; 5-cell events at 0.05 Hz not at all." | nowhere: it is spread over 5 bold leads | It is mostly evidence. Add that one sentence as a lead. The refusal sentence (L112) applies to the whole section but sits inside one bullet. |
| 113 → 128 (two more sessions) | 132 | "This is a consistency check, not independent review." | middle, after a bold headline that says more | Put the caveat in the headline. "The other routes lead to the same quantities" says nothing a reader can pin down. Cut it. |
| 124 → 139 (table) | 165 | (tabular; the tool's "1 sentence" is an artifact of the table) | n/a | Earned. See the "no 1/N factor" finding below. |
| 132 → 147 (what only blind passes found) | 151 | "At 33 cells the event floor is 6 cells at 0.01 Hz and 12 at 0.05 Hz, so 5- and 10-cell events cannot pass it at 0.05 Hz…" | last, after a ~100-word one-sentence list | This is the most consequential sentence in the section, and it is buried. Promote it to its own line. Break the semicolon list into bullets. |
| 187 → 202 (against Kreuz) | 293 | "Against Kreuz's synfire measure, the comparison is not yet made." | first (good) | Bullets 1–2 are earned. Bullet 3 (prior art for the fast sort) does not follow from "So:" and belongs with the Order paragraph. |
| 217 → 232 (Tried and dropped) | 124 | Each bullet is its own payload. | n/a | Two bullets restate earlier text; see the redundancy findings. |
| 228 → 286 (plan item) | 296 | "Derive what the tools should return from the planted parameters, then simulate to test the prediction and measure what is left over." | first (good) | It is a numbered list, so the length is earned. See the item-level findings. |

### Findings
Columns: location · issue · severity · suggested fix · verified against source (yes/no)

1. **L103–108 and L118–119 · Undefined symbols.** g_n and the k̂ formula's g_3/g_2 (L92, L142) are not in the symbols block. g_n is defined only in the glossary. n̄ (L191, L212, also L339) is never defined on the page. · major · Add g_n ("the chance that n onsets of one event share a counting window") and n̄ to "Symbols and tools used below". · yes (Grep of the page and glossary)
2. **L197 · τ collision.** "F = (2/π) arctan τ (A), which is the population Kendall τ…" uses τ for two quantities in one sentence: spread ÷ jitter (L189) and Kendall's τ. · major · Rename one of them, e.g. "Kendall's τ_K" or "ρ = spread ÷ jitter". · yes
3. **L32, L84, L99, L106, L193 · One idea, four names.** "at-most-one-event term", "the term for at most one event per window", "hard-core bias" and "(a Poisson event train)" all name one idea. The term is first used at L32 but explained only at L106. · major · Define it once, at first use or in the symbols block ("events ≥ 20 s apart, so a window holds at most one"), and use only that name afterwards. · yes
4. **L147–154 · Run-on sentence.** "What only the blind passes found" is one ~100-word sentence of six semicolon items, with the event-floor consequence last. · major · Turn the six items into bullets and promote the event-floor sentence (see the passage table). · yes
5. **L128–130 · Headline overclaims its own caveat.** The bold headline "One answer, reached three ways; the other routes lead to the same quantities" is undercut two sentences later by "⚠ This is a consistency check, not independent review". "The other routes" has no referent. · major · Headline: "Same core derivation in all three sessions; a consistency check, not independent review." Cut the second clause. · yes
6. **L135 · Undefined term.** "This session's exact term was committed before…": which term? "Exact" is the word the last review flagged as stretched. · minor · "This session's at-most-one-event term was committed before…" · yes
7. **L141 (table row 1) · Ambiguous cells.** "no 1/N factor" and "no 1/N² factor in the triple term" do not say whether the blind result is wrong, uses a different convention, or is an approximation. · minor · Say which, e.g. "same leading terms; drops the 1/N correction". · no (would need `blind_a/REPORT.md` and `blind_b/REPORT.md`)
8. **L69, L74 · Unitless numbers.** "reads 0.4 at 1 s jitter" and "(B, 0.3 at 1 s jitter)" are ratios to planted only by inference from the figure axes. L66's "down to 0.74" sits beside L78's unrelated "SD 0.74 s". · minor · Write "0.4 of planted" and "0.3 of planted". · yes
9. **L76 · Misplaced modifier.** "It reads about 0.66 s whatever was planted at 0.05 Hz" reads as if 0.05 Hz were what was planted. · minor · "At 0.05 Hz it reads about 0.66 s whatever jitter was planted (H)". · yes
10. **L104–105, L108–109 · Imprecise statistics.** It does not say whether "median residual" is signed or absolute. The ranges "0.03–0.06", "0.18–0.38" and "0.07–0.28" do not say what they span (windows? backgrounds?). · major (the numbers feed later reports) · State the statistic, e.g. "median |measured − predicted|/planted", and name the range's axis. · no (would need `theory_check.json`)
11. **L111 · "Off by 5.6" is ambiguous.** It could mean a factor or a difference in the ratio. · minor · "worst ratio 5.6× planted" (or whatever it is). · no
12. **L112–114 · Misplaced sentence.** The refusal sentence (17 of 720 recording-windows, medians exclude them) sits inside the 5-cell bullet but governs every median in the section. It does not say whether all 17 are 5-cell. "Now passes through" is change-log voice. · minor · Move it to a lead sentence for the section, say which conditions the 17 are, and drop "now". · no
13. **L110, L207 · Internal citation.** "murderboard role 6" is cited as a source. A cold reader (Tony, a later session) cannot resolve it from the page. · minor · Cite the run record or the script and number it rests on. · yes
14. **L110 · Bridge not made.** "The surrogate's own correlations" is the page's first use of "surrogate". L46 called these "time-shifted copies". · minor · "the time-shifted copies' (surrogates') own correlations". · yes
15. **L152, L295 · Undefined term.** "count-detector" / "count detector" is used but not defined on the page or under that name in the glossary. · minor · Name the code object, or define it in the tools list at L44–49. · yes (Grep)
16. **L153 · Redundant.** "matches the simulated floor exactly or within one cell" means the same as "within one cell". · nit · "within one cell of the simulated floor". · yes
17. **L157–159 · Two "above"s.** "A the rate 3–5 % above. The surrogate correlation above…" uses two senses of "above" in one line; the second points back 50 lines. · nit · "…3–5 % high. The surrogate correlation (Event rate bullet) may…" · yes
18. **L161 heading · Ambiguous heading.** "(checked on membership and order alone)" does not say what was checked on what. · minor · e.g. "(simulated with membership or order as the only structure)". · no
19. **L180–181 · Wrong attachment, unclear condition.** "two events share an assembly with probability 1/M, the survey-sampling design effect" attaches "design effect" to the probability; the design effect is the ratio. "While each assembly is used at least once" is ambiguous: it most likely means mean use E/M ≥ 1. · minor · "the ratio is 1 + (E − 1)/M, Kish's design effect: two events share…" and "while reuse E/M is at least 1". · no
20. **L206–207 · "Less with it" is ambiguous.** It could mean a smaller factor (more shrinkage) or less shrinkage. · minor · State the direction with a number. · no
21. **L209 · Bold lead says less than it means.** "The no-order constant is not the annealed one" is then followed by a value "under a local search that stands in for annealing". · minor · "The no-order constant here is fitted, and is not Kreuz's annealed value." · yes
22. **L218–223 · Off-topic bullet.** Bullet 3 (fast-sort prior art) is not a consequence of the "So:" sentence. "9.7 s against 861.8 s" does not say what was timed or on what. · minor · Move it to the Order paragraph (L193–200) and say "runtime on <data>". · no
23. **L90, L198, L221, L226 · Four reading-status markers.** "⚠ not opened", "⚠ secondary sources only", "both from metadata" (no ⚠) and "abstract read" (no ⚠). · minor · Use one ⚠ form throughout. · yes
24. **L226 · Symbol collision.** "spread s" collides with the unit s used everywhere on the page. · nit · Use another letter, or "template spread" in words. · yes
25. **L62–64, L35, L234–235 · One fact, three places.** The shared-background flaw is stated in the L21–22 log, the ⚠ block at L62 and "Tried and dropped" L234. The Poisson residual appears as "about 0.05" at L105 and "5 %" at L232. · nit · Keep the ⚠ block and the dropped entry. Make the units match (0.05 vs 5 %). · yes
26. **L37–42 · Incomplete grid.** The symbols block lists the k grid but not the σ grid (0.05, 0.2, 0.5, 1.0 s, inferred from L116–119). The grid appears only scattered through the bullets. · nit · Add σ values (and b, E) to the "condition" sentence. · no
27. **L292–293 (plan 2) · Double "ask".** "Ask whether anyone has asked Kreuz" is awkward. · nit · "Ask Tony whether the lab has already contacted Kreuz or Mulansky about…". · yes
28. **L301 (plan 4) · Unconnected sentence.** "Lopes-dos-Santos et al. 2013 is the classical instrument" is appended with no link to the item; "instrument" is vague. · nit · "…the classical method to test against". · yes
29. **L304–306 (plan 6) · Term unexplained.** "slow-comodulation" is first used on the page here. It is a glossary term (glossary L582; `decisions_pending.md` §9) but the page does not link it. · nit · Link the glossary entry. · yes
30. **L309–310 · Unclear clause.** "CoactDetect and LoCo (rolling context, merge gaps), clustered intervals and per-cell burstiness stay simulated." It is unclear what "stay simulated" means and what the parenthesis attaches to. · minor · "No closed form is planned for CoactDetect's and LoCo's rolling context and merge gaps, clustered intervals, or per-cell burstiness; these are checked by simulation only." · yes
31. **GLOSSARY L473–476 · No finding.** Clear; it closes with "Say which one you quote." · none · n/a · yes
32. **GLOSSARY L656–672 · No finding.** Short and precise. "Never 'cell', which is an ROI" is right, though the goal page writes "cells" for ROIs throughout where the glossary writes ROIs. That is a consistency note for role 8/10, not a defect here. · none · n/a · yes

**Open for the main thread:**
- **Fixes and rewordings:** findings 7, 10, 11, 12 and 18–20 need the JSON and report files checked before rewording. I did not open them; my role is reading for clarity.
- **The grant line:** it is a MISMATCH because of the fallback. The run record's `roles:` line must say the review took a fallback path.
