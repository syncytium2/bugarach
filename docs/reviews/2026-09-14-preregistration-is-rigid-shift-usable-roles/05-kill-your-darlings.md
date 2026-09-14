GRANT 5 ok — Read, Grep, Glob

# Role 5, line editor: pre-registration "is rigid shift usable"

**Artifact:** `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`

## What I checked
- **Prose tool:** the main thread ran `murderboard_prose.sh` (upstream syncytium2/murderboard @ 81a0927). I hold no shell and did not run it myself. Its output, as the main thread pasted it:
  ```
  — no banned construction found
  blocks: 1 12w/1s · 3 134w/6s <<over 120 · … · 90 119w/7s · … · 119 195w/10s <<over 120 · … · 165 106w/7s · … · 184 68w/1s · …
  2 block(s) over 120 words
  ```
- **Banned list:** I ran the one in my role file (the process file's role 5). I also read by hand for the forms the tool cannot search:
  - A rhythm triple is a three-item list written for cadence rather than because there are three things. Line 13's "rule first, then one small run, then read the result once" names three real steps. So does line 29's list of three streams.
  - No sentence pivots on an em-dash into an uplifting close.
  - Nothing opens with "In today's ___".
  - **Result:** no hits.
- **House conventions:** I read `docs/writing_conventions.md` and `docs/GLOSSARY.md` (its sections on surrogates, MAHICE and K).
- **Terms checked against the code:**
  - `surrogates.rigid_shift`
  - `surrogate_stats.destruction` and `coact_excess`
  - `surrogate_discriminator.forced_choice`
  - `assess.assess_coactivity`'s default bin width
- **The earlier plan's J grid:** `proposals/2026-09-10-surrogate-evaluation-overnight.md`.

## Passage test: the two blocks over 120 words, plus the two just under

| block | words | payload sentence | where it sits | what the other words buy | verdict |
|---|---|---|---|---|---|
| 3–13 (signed blockquote) | 134 | Two jobs share one block. Status: "Everything above the sign-off line is frozen." Why: "rule first, then one small run, then read the result once." | Status is second. Why is **last**. | The diagnosis ("the verdict rule was written afterwards, so every rule was post-hoc") is evidence a sceptic needs. The date "2026-09-12" and the goal link are lookup keys. | The block is fine as a record. Promote the why-payload if the page is ever reissued. Frozen. |
| 119–131 (destruction bullets) | 195 | "Pass at a *J*: retained share at most 0.25, at every K where the planted events are visible…" | **Second of five** bullets | These words are execution rules, not padding: the bin width, the controls, saturation, the Cossart exclusion. | Keep the length. But three of the bullets are ambiguous about what the run must do (see the findings on lines 119–122, 125–127 and 128–129). |
| 90–97 (leak pass and controls) | 119 | "the upper 98.3 % bound on accuracy is below 0.55" | First | The binomial odds of 7.5 % and 1.6 % justify choosing 4 seeds over 3 (checked: correct at α = 0.05). | Keep. The sentence about three or more seeds never says 3 was the rejected threshold. |
| 165–173 (build list) | 106 | "A runner… calling the three instruments above with fresh seeds." | First | The cost sentence ("hours on the Mac") is vague but harmless. | Keep. |

## Findings

Severity: **H** means the sentence is ambiguous about what the run must do or how its result is read, so it is a candidate for a dated amendment. **M** means a reader will likely misread it, so it is a residual flag. **L** means style, or a typo-class fix that may be applied above the sign-off line.

| # | location | issue | sev | suggested fix | verified against a source? |
|---|---|---|---|---|---|
| 1 | Outcome table, "Cossart leak at the passing *J*" (l.141) | Cossart's displacements are in frames (4, 8, 16) and the lab streams' are in seconds. Fast and slow can also pass at *different* J values, or at several. "The passing *J*" does not say which Cossart J to read. It could mean the same position on the list, the one equal in seconds, or any of them. | **H** | Amendment: name the rule. For example, "Cossart passes if its leak gate passes at the same position in its list (4, 8 or 16 frames) as any J at which both lab streams passed." | yes (table l.67–71) |
| 2 | Outcome table (l.141–146) | The table has no rows for VOID. PASS/VOID, FAIL/VOID and VOID/VOID have no outcome. The row "PASS on one stream, FAIL on the other" also leaves the Cossart column blank. | **H** | Amendment: add the VOID rows, or state "any VOID stream: nothing is read until it is fixed and rerun". | yes |
| 3 | l.73 "every bound below is Bonferroni-widened" and l.123 "retained share at most 0.25" | The destruction pass states no bound. It can be read as the point estimate `(E_planted − E_unplanted) after / before` computed over draws, or, by l.73, as the upper 98.3 % bound on that share. These give different verdicts. The number of destruction draws is also never stated. | **H** | Amendment: say "point estimate over N draws" or "upper 98.3 % bound over N draws". | yes (`surrogate_stats.destruction` computes a mean ratio with no interval) |
| 4 | l.119–122 destruction bin "1.0 s" | The old bin is described as "±2-frame (0.5 s)", which is 2·2+1 = 5 frames. 1.0 s is 10 frames, and a bin of 2h+1 frames cannot be 10. "The bin as a parameter" (l.167) does not say whether it is a full width or a half-width. The assessor's docstring also calls 1.0 s "the MATLAB default for the **faster** stream". "The assessor's own definition" is therefore not established for the slow stream. | **H** | Amendment: "bin_width_sec = 1.0 s full width, on both streams", or name the half-width in frames. | yes (`assess.py` l.394, `surrogate_stats.py` l.93, l.1193) |
| 5 | l.125–127 destruction controls | The leak and count gates both say what a failed control does ("void"). The destruction controls do not. Both controls are independent of J, so it is also unclear whether a failure voids one J or the whole stream, and at which K and participation it must hold. | **H** | Amendment: "if either control fails at any K and participation, the stream is void for destruction". | yes |
| 6 | l.116–117 "Retained = excess the planted twin keeps after the surrogate, as a share of what it had before" | This misstates the unchanged instrument. The code divides the planted-minus-unplanted difference after the surrogate by the same difference before. The prose drops the subtraction of the unplanted twin, so a reader computing from the sentence gets a different number. | M | Residual flag: "retained = (planted − unplanted excess) after ÷ the same before". | yes (`surrogate_stats.py` l.1211–1213, l.1247–1249) |
| 7 | l.128–129 "Saturation" | "The expected number of co-active ROIs still inside the bin" does not say expected over what (analytic or over draws), or which ROIs (the planted participants). The page does not say how a saturated J combines with "at every K where the planted events are visible". "Saturation" is not in the glossary. | M | Define the computation in one sentence. | partly (not in glossary; no code exists yet) |
| 8 | Displacements table, slow row (l.70) "the same logic on the slow grid" | False as written. The overnight plan's slow grid is 0.7, 1.4, **2.5**, 2.8, 5.6, 11.2 s. By the fast row's logic, the next step after 1.4 s is 2.5 s, not 2.8 s. The values 1.4, 2.8, 5.6 are straight doubling. The signed values stand; the stated reason does not match them. | M | Residual flag: "1.4 s, then doubled twice". | yes (`2026-09-10-surrogate-evaluation-overnight.md` l.249) |
| 9 | l.123 "every K" and l.117 "the assessor's K scan" | K is used and never defined. The glossary defines K as a **percentage** set by a person during MAHICE and records that "a scan, not a setting" was retired on 2026-09-03. Here K is an absolute ROI count (`DEFAULT_MIN_ROIS`). | M | Residual flag: "K, the minimum number of co-active ROIs, over the assessor's default range (`DEFAULT_MIN_ROIS`); not the glossary's percentage K". | yes (GLOSSARY l.127–146, l.195–203) |
| 10 | l.56–57 "The share of ROIs that rigid shift cannot change" | Two readings. It could mean zero-event ROIs, which cannot change. Or it could mean ROIs whose drawn offset rounded to 0 frames, which did not change in that draw. They are different numbers to report. | M | Residual flag: "the share of zero-event ROIs". | no |
| 11 | l.107 "±2 % of the mean real count" | Mean over what is not stated: per ROI per analysis window, pooled over mice or within each mouse, per stream or per group. | M | Residual flag: name the aggregation. | no |
| 12 | l.97 "No single seed can void anything — that was the defect" | "Anything" overclaims. The positive, count and destruction controls give no seed count, so a single seed could still void them. "That" points back to "the seed-0 defect", 65 lines earlier. | M | "No single real-against-real seed can void a stream; one seed doing so was the seed-0 defect." | yes |
| 13 | l.139 "VOID… the instrument is broken, which is fixed and rerun rather than read" | The page does not say whether the rerun is judged by this same frozen rule or needs an amendment. The sentence also calls a gate that fails its control "the instrument". | M | Residual flag: "rerun under this page unchanged; any change to a gate is an amendment". | no |
| 14 | l.44–46 "A VIABLE result is therefore 'held up…', not 'replicated…'" | Only VIABLE is bound to this caveat. NARROWED rests on the same reused recordings. | M | Residual flag: "A VIABLE or NARROWED result". | yes |
| 15 | l.31 "Its fast accuracies there were 0.495–0.524, though every fast row was voided by the seed-0 defect" | One sentence asserts two things, and the second undoes the first: the fast stream has no valid leak evidence. That is the most important fact in the block, and it sits inside a subordinate clause. "Seed-0 defect" is not explained until l.97. | M | Split into two sentences and state the consequence: "so the choice rests on slow and Cossart". | yes (line text) |
| 16 | One instrument, five names | "Per-ROI leak test" (l.28), "coordination-blind classifier" (l.18), `forced_choice` (l.84), "the discriminator" (l.166), "the test" (l.94). Likewise one run carries four names: "the surrogate screen" (l.9), "the 2026-09-11 overnight run" (l.27), "the exploratory run" (l.37), "the screen" (l.90). | L | Name each once and keep the name. | yes |
| 17 | l.36 "STOP" and l.146 "STOPPED" / l.139 "FAIL" | Outcome labels drift. "A STOP on rigid shift" matches no defined outcome, since a FAIL on one stream gives NARROWED. | L | "A STOPPED outcome stops the goal". | yes |
| 18 | l.21–23 "If yes… If no…" | The question promises a yes/no answer, but the outcome section has four outcomes plus VOID. | L | Residual only; the outcome section governs. | yes |
| 19 | Undefined jargon | These terms appear with no definition and no glossary entry: "edge-band counts" (l.85), "symmetric statistics" (l.86), "free win" (l.102), "motion-pinned" (l.59), "four groups" (l.52), "survivors" (l.33), "homogeneous resample" (l.126), "visible" (l.123; it means excess before the surrogate > 0), "twins" (l.113; as written, each twin has both variants), "same key" (l.115), `tube` (l.150), "ROI axis" (l.149), "quiet → busy transfer penalty" and "treated-window number" (l.151), "band statistics" (l.158), "ROI swap" (l.160), "credited" (l.65), "prices it" (l.172). "Leak", "destruction", "floor" and *J* are in the glossary and are fine. | L | Residual flags. Define on reissue. | yes (checked GLOSSARY) |
| 20 | Undefined abbreviations and symbols | ROI (never expanded), ISI in "Joint-ISI" (l.34), α (l.96), K (see the K finding above). MAHICE is not spelled out, and the glossary requires that "on first use" in anything outward-facing (l.160). | L | Expand on first use. | yes (GLOSSARY l.167) |
| 21 | Units | Cossart's J is given in frames with no frame interval, and the house rule asks for the conversion wherever units differ. "566 median ROIs" (l.130) is garbled. "Participation 0.2 and 0.5" never says it is a fraction of ROIs. | L | "a median of 566 ROIs per recording"; give Cossart's frame interval. | yes (CLAUDE.md units rule) |
| 22 | American English | "labelled" (l.27), "analysed" (l.53), "normalise" (l.149). | L | **Typo class, so it can be applied above the line:** labeled, analyzed, normalize. | yes (`writing_conventions.md` l.115–117) |
| 23 | l.53, l.56 "FOUNDATIONS §9" | A bare section index; the conventions list "§6bis" as a failing example. | L | "FOUNDATIONS §9 (baseline windows only; zero-event ROIs stay in)". | yes (`writing_conventions.md` l.13) |
| 24 | l.9–10 "the screen was designed to measure everything and design its verdict rule *afterwards*" | The parallel verbs make the screen the one designing its own rule. | L | "the screen measured everything and left its verdict rule to be written afterwards". | yes |
| 25 | l.121–122 "**Scored at 1.0 s**, the assessor's own definition, and report 0.5 s beside it." | Mixed mood: a participle, then an imperative. | L | **Typo class:** "Score at 1.0 s…". | yes |
| 26 | l.73 "Three displacements are a family of three" | Says nothing. The content is the family size and the base α it widens. | L | "The three J values per stream are one family: every interval is 98.3 % (1 − 0.05/3)." | yes |
| 27 | l.80 "Each gate states how it can fail, and each has a control that shows it can." | A preview of the section, and the destruction gate's controls give no failure consequence (see the destruction-controls finding), so the claim is not true of every gate. | L | Cut, or make it true with the amendment for the destruction controls. | yes |
| 28 | Seven "(accepted)" / "— accepted" tags (l.63, 90, 96, 107, 119, 123, 124) | These repeat the sign-off. | L | Residual; frozen. | yes |
| 29 | l.149–150 "normalise the count across ROIs away" | Garbled. | L | "or normalize away count differences across ROIs". | yes |

## What to do with these
- **Amendment candidates:** five findings are ambiguous about what the run must do.
  - Which Cossart J counts as "the passing J".
  - The missing VOID rows in the outcome table.
  - Whether the retained share is a point estimate or a bound, and how many draws.
  - Whether the 1.0 s bin is a full width or a half-width, and whether it applies to the slow stream.
  - What a failed destruction control voids.
- **Typo class, applicable above the line:** the three British spellings and the mixed-mood "Scored at 1.0 s" sentence.
- **Residual flags:** everything else.
