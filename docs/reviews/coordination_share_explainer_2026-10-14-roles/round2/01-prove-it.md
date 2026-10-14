GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1, claim and data verifier: coordinated-share explainer, round 2

**Artifact:** `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`, the six PNGs beside it, and `numbers.json`.

**Reproducibility:** I re-ran the generator with `--out` pointed at scratch (`...\scratchpad\mb-r2\role1\`; `--also` was not passed). All six PNGs and `numbers.json` came out byte-identical to the committed copies. Every quoted number therefore traces to code that reproduces exactly.

I also wrote extra checks and passed them inline with `python -c`, because the repo's hook blocks heredocs: tick counts in Figure 1, the pooled ratio on the no-planted set, and the bench's decoys.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| 1 | Line 38, "It is the measure `fireflies` will read treatment results through" | **Wrong attribution.** ADR-0017 point 4 makes measuring the coordinated fraction under treatment *bugarach's* job, as the first confirmed exception to the fireflies default. The same ADR says "Fireflies' export from bugarach is unchanged". The explainer's own todo (lines 39–41) says the same. | major | "bugarach will report treatment results through this measure (ADR-0017, the first exception to fireflies' default)". | yes |
| 2 | Line 42, "No real recording is shown or quoted", against line 145, "median 41 s on the fast stream" | **The page quotes a real-data statistic.** The 41 s (`p50` = 41.25 s) comes from `docs/learned/runs/2026-09-25-real-intervals/summary.json`. That run measured the default `senktide_ttx` folder (66 recordings): the export under the contamination stop since 2026-10-05, including the four DI (diestrus) recordings with pinned cells. It is also pooled across DI, OVX, MALE and ORX. Pinned cells make same-moment events, so they can shorten measured intervals. Figure 3C's bench recordings draw their gaps from that same pool. | major | Either drop the 41 s, or say it comes from the stopped export and is pooled over groups. Change line 42 to "No real recording is shown; the bench's gap schedule is drawn from the default export". | yes |
| 3 | Lines 191–194, "If every recording in a run has no shared moments at all, the pooled triples are not above zero and the tool gives no answer" | **Stated as a rule, but in fact it is chance.** With nothing planted, expected *f*₃ is zero and its sign is noise. On the page's own 24 no-planted quiet recordings, pooled Σ*f*₃ is −0.0009 at 1 s (no answer) and −0.12 at 4 s (no answer), but **+0.029 at 2 s**. There `pooled_ratio` = 1.00, so the tool *does* answer, with *k* = 3. | major | "...the pooled triples may come out at or below zero, and then the tool gives no answer. When they come out slightly positive, it reports a small share." | yes (recomputed) |
| 4 | Lines 180–182, "So it is counted most when it is short" and the bold "It is how fast the rate changes that matters, not how long the change lasts" | **Figure 5A's own numbers refute both.** The shortest stretch (10 s) reads a median 3.7%, below 30 s (7.9%), 1 min (8.2%) and 2 min (5.8%). The six stretches all have the same sharp edges, yet the reported share varies from 1.2% to 8.2% with length alone. So length does matter for the reported share, because the excess from the edges is divided by a total that grows with the stretch. | major | Say the excess comes from the edges, and the reported share peaks for stretches of 30 s to 2 min and falls for longer ones as the stretch's own onsets dilute it. Quote the 10 s point. Drop or reword the bold sentence. | yes |
| 5 | Line 190, "Each cell's own clumping is removed in the same way (Figure 5C, the steady rows)" | At the quiet background the subtraction removes **52%** of *f*₂ (`numbers.json` 5C "steady, quiet": raw 0.0030, after 0.0014, `removed` 0.523). The 99% figure holds only at 13× quiet. The residual is consistent with the +0.1% median in the no-stretch nulls. | major | "...removed almost entirely at 13 times quiet (99%), about half at the quiet background, where it is tiny to begin with (Figure 5C)". | yes |
| 6 | Line 86, "every cell has the same number of ticks" (Figure 1D against 1B) | It is true over the whole recording but **false in the 5 minutes shown**. I recomputed for seed 13, 30m–35m: 9 of 32 cells have a different tick count, and the totals are 102 onsets in B against 96 in D. A reader counting ticks in the figure will find it wrong. | major | "...and every cell keeps the same number of ticks over the whole recording (a 5-minute view can gain or lose a few at its edges)". | yes (recomputed) |
| 7 | Lines 122, 229–231 and the Figure 3 caption ("the bench's own recordings ... and the decoys on") | **Figure 3C's "planted share" counts the decoys as coordinated.** `truth()` in `measure_coordination_rates.py` sums over `gt.events + gt.distractors`. In a bench recording (quiet, seed 1) that is 7 events plus 6 decoys of 6 cells, so decoys are **45% of planted coordinated onsets**. The page calls decoys "near-coincidences it plants to test detectors", which reads as negatives. 3C also defines the planted share differently from 3A and 3B (λ·Σ*k*/(*N*·*T*) ÷ measured rate, against frame-deduplicated planted onsets ÷ all onsets). | major | Say in the caption and at line 231 that in 3C the right answer counts the bench's decoys as shared moments, as the tool's own check does. | yes (recomputed) |
| 8 | Lines 133–134, "On these simulations it ranges from 5% (one size) to 18% (three sizes)" | Figure 4 on the same page has the fixed model reading 21% low (close pairs at 4 s) and 22–23% low (very close pairs). As written, the range understates. | minor | Scope it: "from moment-size variation alone ... 5% to 18%; window splitting of close pairs adds more (up to 23%, Figure 4A)". | yes |
| 9 | Lines 165–166, "33% to 55% low" | The smallest magnitude for moments per minute is −0.3354 (120 s only, 2 s window), which rounds to **34%**. The 55% matches (−0.5468). | minor | "34% to 55%". | yes |
| 10 | Lines 187–188, "removes 99% of it" ("it" being the change) | 99.0% is the share of the *total* raw *f*₂ removed. The part the rise adds is 0.593 − 0.407 = 0.186, and what is left of it is 0.0059 − 0.0024 = 0.0035, so **98%** of the change is removed. | minor | "about 98% of it", or "99% of the pairs beyond chance". | yes |
| 11 | Line 183, "the bench's 30 s ramps" (Figure 5B axis label too) | `simulate.py` (lines 911–913) ramps only **in**, with `rf = min(1, (ct-h0)/ramp_sec)`. The stretch switches off sharply. "Ramps" suggests both edges are soft. | minor | "the bench's 30 s ramp in (it ends sharply)". | yes |
| 12 | Line 185, "three quarters of all the recording's onsets fall inside the stretch" | `share_of_onsets_in_stretch` is a formula, `added·span/(added·span + QUIET·T)` = 0.75. It counts only the *added* onsets and ignores the ramp. Counting background inside the stretch gives about 0.78, and allowing for the ramp about 0.74. "About three quarters" survives, but the JSON field name misdescribes what it holds. | minor | Rename the field to `share_of_onsets_added_by_stretch`; the prose can stay "about three quarters". | yes |
| 13 | Lines 259–260, "four recordings from the diestrus (DI) group await review cell by cell" | The stop todo says `_312` has been reviewed ROI by ROI. Three (`_309`, `_316`, `_235`) have not. All four need corrected sets before the stop clears. | minor | "three await review cell by cell, and all four (all DI) need corrected cell sets". | yes |
| 14 | Line 212, "Every simulated recording gave an answer" | `numbers.json` records `no_answer` only for Figure 6's per-recording solve. `q()` drops non-finite values silently, so Figures 3, 4 and 5 leave no record of missing answers. With planted moments in every pooled set, the pooled ratio is very likely positive, but the record does not show it. | minor | Record a `no_answer` count per figure, or scope the sentence to Figure 6. | no (inferred, not counted) |
| 15 | Line 279, link to the review record | `docs/reviews/coordination_share_explainer_2026-10-14.md` does not exist yet. The text admits it ("written when the review finishes"). | minor | Make sure it lands in the same PR. | yes |
| 16 | Line 248, "What is this project's: using factorial cumulants" | It is a novelty claim against Ehm, Staude and Rotter (2007) "de-Poissonization". I cannot check from the tree whether that paper already uses factorial cumulants. | minor | Verify against the paper, or soften to "the solve for *k* and λ under the two models ...". | no |

## Claim ledger

Format: quoted value · source · recomputed · verdict.

### Figure 1
- 32 cells · `BENCH_RECORDING n_roi` · 32 · match
- 5 minutes, 30m–35m, quiet recording 13 · `numbers.json` 1 · window 1800–2100 s, seed 13 · match
- close pair 2 s apart, medium pair 10–20 s · `SCHEDULES`, `MEDIUM_GAPS` · same · match
- "every cell has the same number of ticks" · recomputed · 9 of 32 differ in view (102 vs 96 onsets) · **mismatch** (finding 6)

### Figure 2 and steps 1–3
- 0.44 onsets per window, both recording and copy · `mean_real` / `mean_shifted` 0.4385 · match
- windows holding 6 to 11, recording only · max 11 real, 5 shifted · match
- 20 copies · `N_SURR` = 20 · match
- copies' *f*₂ 0.03 · 0.0283 · match
- excess 0.20 and 1.21 · 0.1998 and 1.2092 · match
- *k* ≈ 8.1 · 1.2092 / 0.1998 + 2 = 8.05 · match
- 90 ordered pairs, 720 ordered triples · 10·9, 10·9·8 · match
- slides at least two windows apart · `shifted(..., 2*wf)` · match
- slides "at most about half a minute" · max |offset| over 200 draws = 31 s · match
- windows counted twice, the second at half a window · `population_cumulants` offsets (0, wf//2) · match
- formulas for *f*₂, *f*₃ and λ*wk*(*k*−1) · `factorial_cumulants` and `solve` · match

### Figure 3
- pass band ±25% · `CAL_TOL` = 0.25 · match
- 48 recordings per panel · 24 seeds × 2 backgrounds · match
- 3A: fixed 18% low, binomial 8% low · −17.66%, −7.51% · match
- 3B: fixed 5% low, binomial 17% high · −5.09%, +17.03% · match
- 3C: fixed 16% low, binomial 2% low · −15.59%, −2.25% · match
- single recordings 0.67 to 1.12 · min 0.671 (3C), max 1.121 (3B) · match
- adopted model fixed · `ADOPTED_MODEL` · match
- bench about 7 events per 45 minutes · `realistic_counts`: 9.72 per hour × 0.75 h = 7.3, and recording seed 1 has 7 · match
- decoys on in 3C · 6 decoys of 6 cells · match, but undisclosed in the right answer (finding 7)
- 10, 6 and 3 cells · 0.30, 0.203, 0.10 × 32, rounded · match
- jitter 0.106 s · `CAL_JITTER` · match (the bench's own value is 0.105)
- quiet 0.0049, busy 0.0169 · `bench.REGIMES` via the generator · match

### Figure 4
- 14% to 19% low (120 s only, medium, mixed, and close pairs at 1 and 2 s) · 13.6–18.6% · match
- close pairs at 4 s 21% low, against 14% · −21.2%, −13.6% · match
- very close pairs 22% to 23% low · −21.7, −23.2, −23.4% · match
- *k* 56% high against 33% · 0.560, 0.332 · match
- λ 49% low against 35% · −0.495, −0.351 · match
- very close pairs 50–69% high and 48–55% low · 0.497–0.690 and −0.477 to −0.547 · match
- medium pairs within about 5 points of the 120 s set · max difference 5.3 points (*k* at 2 s) · match
- 26–69% high · 0.2645–0.690 · match
- 33–55% low · 33.5–54.7%, rounding to 34–55 · **minor mismatch** (finding 9)
- binomial 3–17% low · 3.3–17.4% · match
- a 2 s pair shares a 4 s window about half the time · 1 − 2/4 · match

### Figure 5
- 0.1334 onsets per second, the bench's elevated level · `ELEVATED_RATE_RECORDING` · match
- the rate is added, not set · `simulate.py` line 914 extends the trains · match
- 27× the background, 28× in all · 27.2 and 28.2 · match
- 8% for a 30 s to 1 minute stretch · 7.9%, 8.2% · match
- 3.0% at 5 minutes · 3.05% · match
- 1.2% at 15 minutes · 1.17% · match
- 10 s stretch · 3.7%, not quoted · contradicts "most when short" (finding 4)
- 2× reads 0.14%, the same as none · 0.144% against 0.134% · match
- 10× reads 1.0% · 0.97% · match
- 28× reads 2.8% · 2.82% · match
- three quarters of onsets in the stretch · 0.75 from a formula · approximately right (finding 12)
- 99% removed at 13× · 99.0% of raw (98% of the rise) · minor (finding 10)
- steady rows removed · 52% at quiet · **mismatch** (finding 5)
- no-stretch median 0.1%, range −0.4% to +0.6% · 0.134%, −0.437%, +0.585% · match
- 5-minute stretch · `hot_window` 1200–1500 s · match
- 30 s ramps · ramp in only · minor (finding 11)

### Figure 6
- 15 moments: 0.78–0.86 · 0.781–0.864 · match
- 6 moments: 0.59–0.98 · 0.590–0.977 · match
- 3 moments: 0.69–1.02, single recordings 0.55–1.09 · 0.693–1.022, 0.547–1.090 · match
- ¼ quiet: 0.77–0.87 · 0.773–0.868 · match
- busy: 0.76–0.92, and 0.74–0.95 on its own · 0.755–0.921, 0.736–0.952 · match
- wider with 6 moments when pooled · width 0.39 against 0.28 · match
- 24 per group, no answer 0 · match (Figure 6 only)

### Limits and spacing
- 300 s / 20 onsets / 5 cells · `fit_background_shape` `MIN_*` · match
- every simulated recording clears the limits · the lowest is ¼ quiet at about 188 onsets · match
- spacing realistic since 2026-10-07 · `bench.py` line 1179 · match
- median 41 s, merged under 2 s · `summary.json` p50 = 41.25 s, merge rule 2.0 s · match, but the source is the stopped, group-pooled export (finding 2)

### What waits
- 66 recordings, `senktide_ttx` · `current_export.toml` · match
- stop since 2026-10-05 · same file · match
- "four await review" · stop todo says three · **mismatch** (finding 13)
- `fireflies` will read through it · ADR-0017 · **mismatch** (finding 1)

### Developer names and citations
- `shifted`, `solve`, `per_recording`, `pooled_ratio`, `ADOPTED_MODEL`, `CAL_TOL`, `shape_usable`, `CAL_NO_PROBE`, `coordinated_share_of_rate` · all present in the tool · match
- GLOSSARY "rigid shift" entry, and this tool's shift is not one · glossary lines 514 and 573 · match
- Citations: Staude, Rotter and Grün 2010 *J Comput Neurosci* 29:327; Ehm, Staude and Rotter 2007 *Electron J Stat* 1:473; Kuhn, Aertsen and Rotter 2003 *Neural Comput* 15:67; Pipa et al. 2008 *J Comput Neurosci* 25:64; Staude, Grün and Rotter 2010 *Front Comput Neurosci* 4:16 · match my recall of the literature, but there is no source in the tree · unverifiable

## Group membership and older-version checks

- **Group membership:** none of the page's own figures use real data, so group and withdrawal membership does not apply to them. It does apply to the two real-data inputs, the 41 s gap median and the bench's gap pool. Those carry the group-pooling and contamination point in finding 2.
- **Comparison with the round-1 draft (e3c2e5a4):** Figure 3A's fixed-model median moved from −20.7% to −17.7%, and the "pooling pulls each set back" claim was replaced. Both moves come with generator changes: the planted share is now counted from frame-deduplicated onsets, the set definitions changed, and Figure 6 is new. The replacement claim about pooling is consistent with the new numbers. The round-1 draft was never a delivered artifact, so I am not counting this as a regression.

**Files:**
- Artifact: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`
- Recomputation output: `C:\Users\defazio\AppData\Local\Temp\claude\c--Users-defazio-bugarach-bugarach\8f7e79d0-c19b-4389-819d-be7bbbbd9efc\scratchpad\mb-r2\role1\`
- Sources behind the main findings:
  - `...\coordination-share-explainer\docs\adr\0017-group-and-treatment-comparisons-default-to-fireflies.md`
  - `...\coordination-share-explainer\docs\learned\runs\2026-09-25-real-intervals\summary.json`
  - `...\coordination-share-explainer\tools\measure_coordination_rates.py` (`truth()`)
  - `...\coordination-share-explainer\src\bugarach\simulate.py` (lines 903–914)
