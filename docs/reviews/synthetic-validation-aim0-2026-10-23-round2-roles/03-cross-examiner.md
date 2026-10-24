GRANT 3 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), Bash, PowerShell, Agent, Artifact, Skill, Claude Docs, Dropbox, Gmail MCP tools (general-purpose inline fallback, not the named agent). I edited nothing and wrote no files. I used Bash only to read the JSON records and recompute medians in memory. This is a finding about the run: the `roles:` line must say role 3 ran through the fallback path.

**Role 03, Cross-Examiner: finding list** (location · issue · severity · suggested fix · verified against a source?)

1. **GLOSSARY.md:468–476 (jitter entry, next to the new "Two measures of one spread" note) and goal page lines 38–39.** The glossary quotes "0.105 s fast, 0.131 s slow, 0.150 s combined" as "the half-width of the correlogram's peak". These are not half-widths. They are the tool's *calibrated generator σ*: `runs/2026-09-23-jitter-correlogram-senktide-ttx/jitter_correlogram.json` has `hwhm.real_sec = 0.186` but `hwhm.jitter_sec = 0.105`, and `bench_measured.json` sets the bench's `jitter_sec` to 0.105. The goal page says "the glossary's correlogram half-width is a different measure of the same spread", and the new note says half-width ≈ 1.67 σ. A reader following both will divide 0.105 by 1.67 and get a σ of about 0.063 s, which is wrong: σ is 0.105. · **Major** · Relabel the glossary values as "σ (`jitter_sec`) calibrated from the half-width; raw half-width 0.186 s fast". Fix the page parenthesis to match. · yes

2. **Page line 119, "5-cell events (jitter off by up to 2×)".** `summary()`'s own statistic in `theory_check.json` (median of condition medians, k = 5) gives σ̂/σ = 1.99, 0.61, 1.00, 0.94 at 0.01 Hz and 0.10 (at the search bound), 2.65, 0.99, 1.85 at 0.05 Hz. The worst outside the frame scale is 2.65×, and at 0.05 s it is 10× low. · **Major** · Say "off by up to 2.7× (10× at 0.05 s, at the bound)". · yes

3. **Page lines 73–74, "K = 6 cells misses most 5-cell events (B, 0.3 at 1 s jitter)".** The 0.3 in Figure 1 B is a median pooled over 5-, 10- and 20-cell events. In `aim1_one_source.json` at 1 s jitter and 0.01 Hz, K = 6 reads 0.0 for 5-cell, 0.3 for 10-cell and 1.0 for 20-cell events. So the 0.3 is the 10-cell value, and 5-cell events are missed entirely. · **Major** · Either "misses all 5-cell and most 10-cell events at 1 s jitter", or drop the figure reading. · yes

4. **Page line 66–67, "within about 25 % of planted in every condition at the 2 and 4 s windows".** The page defines a condition as one grid point (line 42), but the claim only holds for Figure 1's pooled medians. Per condition, 12 condition-windows fall outside 25 %, all 5-cell or 0.05 Hz (for example 3.58, 1.84 and 0.09 at 4 s). This is the same N on two counting bases. · Moderate · Say "in every panel point (pooled over participation and event count)" or "for events of 10 or more cells". · yes

5. **Page lines 115–117, "participants and rate within 4 %".** This is a median of condition medians per (background, σ); the maximum is 4.2 %. The underlying condition medians reach 14 % (k) and 27 % (rate, 0.05 Hz, σ 1 s). The sentence before it uses median/worst, so the basis changes inside one bullet without saying so. · Minor · Add "median over conditions" or give the worst case. · yes

6. **Page line 210, "0.22 to 0.61 across 15–100 cells".** In `order_limit.json` `c_by_field`, the score-sort range is 0.216–0.507 and the local-search range is 0.314–0.6015. The maximum rounds to 0.60, not 0.61, and the quoted range silently spans both sorts. · Minor · Use "0.22–0.51 (score sort), 0.31–0.60 (local search)". · yes

7. **Page line 143, blind B "read 0.2 s 5–15 % high".** `blind_b/REPORT.md` §5 table gives σ̂/σ = 1.08–1.15 at 0.2 s, which is 8–15 % high. · Minor · Change to 8–15 %. · yes

8. **Page lines 157–158, B's triple count "3–19 % below prediction at 0.05 Hz (40 seeds)".** This matches `sim_cumulant_check.txt` (40 seeds; 0.813/0.838 up to 2.158/2.675). But B's verbatim REPORT, which the page links as the attribution source, says "f3 is 5–7 % below prediction (60 seeds, about 4σ)". A reader checking the link finds a different number. · Minor · Name both: the report's 5–7 % (60 seeds) and the txt's 3–19 % (40 seeds, per window). · yes

9. **"Exact" still in use.** Line 30 says the murderboard found "exact" stretched past participants, yet the Figure 2 legend reads "exact prediction, 5/10/20 cells per event" for all three estimates, including rate and share, which line 108 calls "predicted less well". Line 135 ("This session's exact term"), README line 10 ("the exact excess cumulants") and the `theory_check.json` key `exact` do the same. · Moderate · Relabel the figure legend "with the at-most-one-event term" and fix line 135 and the README. The JSON key can stay, with a note. · yes

10. **"Where it stands" lines 24–27 against the body.** "A fit across its three windows recovers jitter … for events of 10 or more cells": the body (line 118) says jitter at 0.05 s is not resolved. "Membership and order have closed forms too": the body says the no-order constant is "fitted, not derived" (line 209) and that membership assumes perfect readout (line 183). · Moderate · Add "above the frame scale" and "except the no-order constant". · yes

11. **Page lines 180–182, "8 % at 0.04".** `membership_limit.json` has reuse 0.045 and detected 0.085. · Minor · "8.5 % at 0.045". · yes

12. **Figure 3 caption and legend, "95 % range of a single random recording".** `aim0_figures.py:132` draws `axhspan(1, random_p95)`: the band runs from the random mean (1) to the one-sided 95th percentile. It is not a 95 % range. `membership_limit.py` itself says "95th percentile". · Minor · "grey band, 1 to the 95th percentile of random participation". · yes

13. **Figure 2 D, "K = 6: none predicted, none measured".** The prediction is 5.1 × 10⁻⁵ per min (`theory_check.json`) and the page says "0". It is off-scale, not none. · Minor · "K = 6: predicted 5 × 10⁻⁵/min, none measured". · yes

14. **Run-record link, page line 29 (also the `theory.py` docstring).** `docs/reviews/synthetic-validation-aim0_2026-10-23.md` does not exist in this worktree (checked by Glob on the name only, not opened). Several quoted numbers rest only on it: "about 1 % of the pair count, murderboard role 6" (line 110) and "0.28 at 10 of 33 cells" (line 206, also only in the `order_limit.py` docstring). It may be deliberately withheld for blindness. · Moderate (if truly missing) · Confirm the file is present before shipping, and put the role-6 numbers in a record (`order_limit.json` / `theory_check.json`). · no (I could not verify the numbers)

15. **"cell" as a term.** The new glossary entry for condition says *Never "cell", which is an ROI*. Two clashes:
    - The glossary's own radar section (lines 276–281: "cell under test", "reference cells", "guard cells") uses cell for a time bin, so the file now gives "cell" two meanings.
    - README line 13 ("whose cells shared five backgrounds") uses "cells" for conditions, which the new rule forbids. Goal page line 325 ("every cell", Aim 2) does the same.

    · Minor · Change the README and line 325 to "conditions". Qualify the glossary note ("in this goal's vocabulary; the radar 'cell' is a bin"). · yes

16. **Reserved symbol K (page line 40).** The glossary reserves K for a percentage of ROIs (lines 128–132, 196–204) and says an absolute K "must never be transplanted". The page reuses K as an absolute count. It flags this, but the glossary's own rule forbids reusing a reserved word for a different concept. · Minor · Use a distinct symbol (for example K_abs or "threshold of K cells"), or add the absolute-K usage to the glossary K entry. · yes

17. **New terms missing from the glossary** (rule: a new term is added in the same change):
    - order indicator F
    - the at-most-one-event term
    - score sort / local search
    - reuse E/M
    - joint fit
    - no-order constant
    - n̄

    Also, τ is used for both template spread ÷ jitter and Kendall's τ in one sentence (line 197–198). τ, F, n̄, q and s are absent from the page's symbol list (lines 37–42). · Minor · Add the entries and rename Kendall's τ (for example τ_K). · yes

18. **GLOSSARY.md:656, placement.** The "Synthetic-validation vocabulary" block is a bold paragraph inside `## Surrogate vocabulary`, so source, condition and membership are filed under surrogates. · Minor · Give it its own `##` heading. · yes

19. **Figure colours across figures.**
    - The palette that means 1/2/4 s windows in Figure 1 (blue/orange/green) is reassigned to 10/5/20 cells in Figure 2.
    - Violet means the joint fit in Figure 1, chance clusters in Figure 2 D/H, and detection rate in Figure 3 B.
    - The row and panel order (participants, rate, share; 0.01 above 0.05) is consistent.

    · Minor · Give the participation levels a palette that does not collide with the windows. · yes

20. **Page lines 152–155 (from B).** "Count-detector recall within about 0.03 in 20 of 24 conditions": B's 24 rows (`theory_count_detector.txt`) are a k × σ × b × K grid, not conditions in the glossary sense (no event count; K is a detector setting). The count is 19–20 of 24 depending on 0.031. Separately, "chance joiners lift a 5-cell event past 6 about a third of the time": the source is K = 6 recall 0.33–0.34 at σ = 0.2 only (0.08 at σ = 1), and the event is *reaching* 6, not passing it. · Minor · "in 20 of B's 24 settings"; "to 6 … at 0.2 s jitter". · yes

21. **"Where the work lives" table (lines 362–363).** It says "Aim 1 scripts and records", but the folder also holds Aim 0's. It lists figures as darkroom-only, but they are also in the repo and embedded. · Minor · Update both rows. · yes

**Checked clean, against `aim1_one_source.json`, `theory_check.json`, `membership_limit.json`, `order_limit.json`, both blind REPORTs and their txt files, all four figures, both READMEs and the glossary:**
- Aim 1a setup: 240 recordings = 48 conditions × 5, 4 jitters, 2 backgrounds, 33 cells, 45 min, events 20 s apart; 720 recording-windows, 17 refusals, all at 0.05 Hz; 10 background-only recordings per background.
- Aim 0 residuals: all medians and worsts (0.009/0.056, 0.015/0.11, ~0.05 without the term, rate 0.03–0.06 / 0.18–0.38, share 0.02 / 0.07–0.28, 5.6).
- Joint fit: σ readings 0.22/0.49/1.01 and 0.20/0.52/1.01; 0.07 and 0.03 s; 3 and 7 of 20 fits at the bound.
- Chance clusters: 0.26/0.02/0 and 7.97/3.86/0.28 predicted; 0.27/0.04/0 and 7.94/3.96/0.22 measured.
- Membership: 1 + (E − 1)/M; 63 % at 0.3 uses; 400 simulations.
- Order: 0.38 and 0.50; (2/π) arctan τ; 1/√M; Figure 4's 200 and 2000 events and τ = 2.5.
- Blind passes: each one's cumulant forms (1/N and 1/N² omissions), 60 q(1 − q)², the floor of 6 and 12, A's rate 3–5 % high.
- Context: the August ρ −0.75/−0.40; every cross-referenced file exists except the run record; the plan's numbered items agree with the body and with "Open work" (items 1 and 3–7); the glossary's σ√2 → 1.67 σ arithmetic.
