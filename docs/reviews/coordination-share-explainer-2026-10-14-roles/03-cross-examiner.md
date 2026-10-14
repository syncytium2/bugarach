GRANT 3 ok — Read, Grep, Glob

Role 3 (Cross-Examiner), round 1. Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md, plus figures 1 to 5 (all five PNGs opened), checked against numbers.json, explain_coordination_share.py, tools/measure_coordination_rates.py, src/bugarach/bench.py, docs/GLOSSARY.md, docs/INDEX.md (line 88), the 2026-10-14 explainer todo, the 2026-10-08 stack-ceiling todo, the 2026-10-05 pinning todo and correlogram_explainer/README.md.

Seventeen findings: 1 blocking, 7 major, 9 minor.

## Findings
Columns: location · issue · severity · suggested fix · verified against a source.

1. **README "The simulated recordings" (lines 61–74) and "How we know it works" (lines 210–214)** · The page says "The bench keeps its moments at least 120 s apart" and that it copies the bench's "15 planted shared moments". That has not been true since 2026-10-07.
   - `bench.py` sets `DEFAULT_SPACING = "realistic"` (lines 1174–1188, ADR-0010 ruling 2, Tony "switch now").
   - Under it, planted gaps are drawn from measured real gaps, with events under 2 s apart merged first (median 41.3 s fast per the glossary).
   - Under it, fast plants about 7 events per 45 minutes, not 15 (`realistic_counts`, `seed_factor` docstring).
   - The old 120 s placement survives only as the named spacing `"bench"`.
   - `make_recording` applies `spacing_overrides`, so the tool's own calibration runs on realistic gaps. "On the bench's own recordings the check is part of every run" therefore describes recordings unlike this page's.
   - The page's framing ("What is new here is the spacing… Real recordings have shared moments closer than that") rests on the stale claim.
   - The tool docstring line 42 ("120 s spacing floor") is stale in the same way, and it is probably the source.
   · **blocking** · Describe the bench as it is: realistic gaps by default since 2026-10-07, with sub-2 s events merged, and about 7 fast events per 45 min. Say this page uses the old 120 s placement plus its own close and medium pairs. Recheck which part is actually new (close pairs under 2 s). File the tool docstring's staleness separately. · yes

2. **README "What it cannot see", bullets 2–3 (lines 183–191), against Figure 5A labels and numbers.json** · The text treats the two rows as different outcomes. It says the steady row "gives no answer at all, not a small one… so `solve` declines" and the rising row "is reported as no coordination". numbers.json records the same thing for both: `answered: 0` of 24, median null. In both cases the pooled f3/f2 is not positive and the tool returns NaN. Figure 5A labels both rows "no coordination reported in any of 24 recordings", which contradicts the text's "no answer at all" for the steady row. · **major** · Pick one wording for "the tool returned no answer" and use it for both rows, in the figure label and the text. For example: "no answer (excess triples not above zero) in any of 24 recordings". Then rewrite the rising-background bullet: it is not "reported as no coordination", it gets no answer. · yes

3. **README lines 196–201 (background lowered) against Figure 5B and numbers.json** · Fig 5B's 15-moment set at the quiet background has a pooled median of 81% (`15 moments.pooled_median` 0.814). The next sentence gives "79% at the quiet level" for what reads as the same condition (`1.0x quiet` 0.790). The generator explains the gap:
   - `low = run_set(pool, dict(), …)` takes the defaults `n_close=2, n_medium=2`, so the lowered-background sets use the **mixed** gap schedule.
   - Fig 5B's sets are all 120 s singles.
   - Yet the text immediately says "Figure 5B's recordings are all at the quiet background, with every moment 120 s or more from the next", which implies the lowered sets match.
   - The conclusion "a lower event rate on its own does not make the answer noisy" compares pooled medians. Fig 5B measures noise as the spread of each recording's own answer, and that spread is not computed for the lowered sets.
   · **major** · Either run the lowered-background sets on 120 s singles (`n_close=0, n_medium=0`), or state that they use the mixed schedule. Report each recording's own 10th-to-90th-percentile range so the "noisy" claim is compared like with like. · yes

4. **README Terms, "Share of events coordinated" (lines 56–57), and section 3 (lines 123–125)** · The page defines it as "of all a cell's onsets, the fraction…" and says each cell's coordinated rate is divided by "the cell's event rate". The tool computes a population quantity:
   - `share = λk/N` is the same for every cell.
   - It is divided by `raw = r["rate"]`, the recording's mean per-cell rate.
   - `coordinated_share_of_rate = nanmedian(shares / raw)` is a median over recordings.
   - The planted truth in the generator is also population-wide: `n_pl / (n_bg + n_pl)`.

   So the measure is the fraction of all onsets in the recording, not any one cell's fraction. · **major** · Redefine it as "of all onsets in a recording, over all cells, the fraction that belong to a shared moment (the tool reports the median over recordings)". Change "the cell's event rate" to "the mean event rate per cell". · yes

5. **README Figure 2 caption (line 7): "one rigidly shifted copy"** · "Rigid shift" is a reserved glossary term (GLOSSARY lines 549–555): offsets drawn in ±J of 10–20 s, and "the published form wraps the train; **this project's does not**". The tool's `shifted` wraps circularly and uses distinct offsets two windows apart. The README body itself says "wrapping round the end". The reserved word is reused for a different surrogate, and the caption contradicts the body. The commissioning todo (item 2, "shifted rigidly") carries the same slip. · **major** · Say "one shifted copy (each cell's train slid by its own amount, wrapping round)" or name it after the function (`shifted`). Do not use "rigid". · yes

6. **README line 67, "the spacing of the moments", and the "gap schedule" vocabulary throughout** · GLOSSARY lines 456–467 name "intervals" as the only term for the time between coordinated events, and retire "spacing" and "timing" for it. The page uses "spacing" (line 67) and an unglossed family: "gaps", "gap schedule", "close pair", "medium pair", "single moment". · **major** · Replace "spacing" with "intervals". Either add "gap schedule / close pair / medium pair" to the glossary in this change, or rephrase in terms of intervals. · yes

7. **New terms not in the glossary: "shared moment", "share of events coordinated", "fixed model" / "binomial model", "factorial cumulant"** · None of these has a GLOSSARY entry. "Shared moment" is the page's central noun, and it overlaps the glossary's "coordinated event". The sister correlogram page uses it as well. The checklist requires a new term to be added in the same change. "Share of events coordinated" also has three other names across companions: "coordinated share" (INDEX line 88, tool), "coordinated fraction" / "fraction of events coordinated" (INDEX line 190, ADR-0017 row), and "fraction of events that are coordinated" (todo). · **major** · Add glossary entries in this PR: shared moment (and how it differs from a coordinated event), the share or coordinated fraction (pick one canonical name and list the others as aliases), the fixed and binomial models, and factorial cumulant. · yes

8. **README "What it cannot see", bullet 1 (line 178): "0.127 onsets per second (the bench's elevated-rate level)"** · The bench's elevated-rate level is now 0.1334 Hz (`ELEVATED_RATE_RECORDING.hot_rate_hz`, `bench.py` line 1565; the table at line 1065 records 0.1271 moving to 0.1334). 0.127 is the value in `CAL_NO_PROBE`'s 2026-09-22 note, which is history. · **major** · Either say "0.127 onsets per second, the level in the tool's `CAL_NO_PROBE` note", or plant 0.1334 and call it the bench's current level. · yes

9. **README section 5, the "Medium pairs… change nothing at any window" bullet against "close pairs move them by about 3 percentage points at most" (lines 165–170)** · Against the 120 s-only set, numbers.json gives these medium-pair shifts:
   - at 4 s: share −2.7 pp, k +2.2 pp, λ −3.3 pp;
   - at 1 s: k +2.7 pp, λ −2.4 pp.

   The text calls a shift of that size "nothing" for medium pairs and "about 3 points" for close pairs at 1–2 s. · minor · Give both the same yardstick: "medium pairs move every number by no more than about 3 points, the same as the differences between sets at 1 and 2 s". · yes

10. **README section 4 (line 148): "every fixed-model share here reads low by about a fifth"** · Figure 4A and numbers.json put the fixed-model error between −10% and −21% across schedules and windows. About a fifth is the worst case (mixed at 1 s), not every case. · minor · "reads low by 10 to 21% (about a fifth at the primary 1 s window)". · yes

11. **README lines 125 and 191: "`solve` does exactly this" and "so `solve` declines"** · The reported numbers go through `pooled_ratio` and `per_recording`, not `solve`. The pooled path returns NaN when the pooled f3 or f2 is not positive. `solve` is used only for Fig 5B's per-recording "own" answers. · minor · Name `per_recording` (with `pooled_ratio`) for the pooled answer, and `solve` only for a single recording on its own. · yes

12. **README line 71, "close pairs only, and medium pairs only", against Figure 4's caption ("with close pairs", "with medium pairs") and legend ("close pairs", "medium pairs")** · Those sets are 2 close pairs plus 11 singles, and 2 medium pairs plus 11 singles (numbers.json `schedules`). They are not "only" pairs, and the body and the caption name them differently. · minor · Use "with close pairs (2 close pairs, 11 singles)" and "with medium pairs" in the body, matching the caption. · yes

13. **README line 76: "chosen as the stretch where a close pair and a medium pair are both in view"** · Figure 1 shows **two** close pairs (about 35m25s and 37m55s) and one medium pair. · minor · "where both close pairs and a medium pair are in view". · yes

14. **README Terms, λ (line 53): "the figures give it per minute"** · No figure shows λ per minute. Figure 4C plots relative error, as a percentage, of "moments per minute". · minor · "the tool reports it per minute; Figure 4C shows its error". · yes

15. **Figure references without names** · CLAUDE.md requires number plus name. These references carry the number only:
   - line 112: Figure 2B
   - lines 142, 157, 162: Figures 4A, 4B, 4C
   - line 179: Figure 5A, middle row
   - line 190: Figure 5A, top row
   - line 193: Figure 5B
   - lines 211–212: "Figure 3 is that check" and "Figure 4A carries it"

   Lines 85, 92, 137, 154 and 174 do it correctly. · minor · Add the short name to each: "Figure 2B, the wider spread", "Figure 4A, window size and gaps", "Figure 5A, what it cannot see", and so on. · yes

16. **Companion GLOSSARY "background" entry (line 421) and "jitter" entry (line 470)** · The glossary gives quiet 0.0052 and busy 0.019, but `bench.REGIMES` and the page give 0.0049 and 0.0169. The glossary gives fast jitter 0.105 s, but the tool's `CAL_JITTER` and the page give 0.106 s (the sister page says 0.11 s). The page matches the code, so the glossary is stale, but a reader cross-checking finds three values. · minor · Update the glossary's background and jitter values in this change, or have the page note which source each number comes from. · yes

17. **README Terms, "Onset" (line 46): "so it is fixed before coordination is asked about"** · "Fixed" is also the name of the adopted model, five sections later. Copied from the sister page. · minor · "so it is settled before…" · yes

## Checked and consistent
- **Counts:** 48 recordings (24 seeds × 2 backgrounds), 24 per Fig 5 row, 20 shifted copies (`N_SURR`), 32 cells, 45 min.
- **Planted moments:** 5 each at 10/6/3 cells (levels 0.3, 0.203, 0.1 × 32, rounded). The mixed schedule has 2 close + 2 medium + 7 singles = 15 everywhere: README, the generator docstring, numbers.json and the todo note.
- **Window and recording numbers:** Fig 1's window is 2110–2470 s (35m10s–41m10s), seed 10, quiet. Fig 2 is seed 3, busy.
- **Fig 2:** means 0.47/0.47; excesses 0.214 and 1.369 (raw minus the shifted mean); "5 to 11 onsets" matches the histogram.
- **Fig 3 / Fig 4:** −21% and −11%; the fixed range −10 to −21%; the binomial range +1 to −11%; k 56% vs 28%; λ −47% vs −30%. The "about 3 pp" at 1–2 s is right (maximum 3.3).
- **Fig 5:** 3.7% and 5.7%; own ranges 78–84, 73–91, 69–105%; pooled 81–83%.
- **Tool constants:** two offsets of half a window; spacing of 2 windows; about 64 s for 32 cells; `CAL_TOL` 0.25; `ADOPTED_MODEL` fixed and its reason; `PRIMARY_W` 1 s.
- **Companion docs:** the INDEX row (line 88) agrees with the page; the todo's note on item 5 being backwards matches the tool docstring; the 66-recording `senktide_ttx` stop matches the 2026-10-05 todo.
- **Category order:** colour roles hold across Figs 1 and 4 (blue close, orange medium, green "aqua" single / 120 s only, black mixed). No DI/OVX/MALE/ORX grouping appears.
- **Banned words:** none in the README ("modality", "fire").
