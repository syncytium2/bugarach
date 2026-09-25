GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 — Prove It: claim check of the final-parameters morning report

**Artifact:** `<worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md`

**Result:** the adoption table is numerically correct end to end. The report makes one false statement about how proposals were chosen, one mechanism claim its own search numbers contradict, and several understatements.

**What was checked:**
- All 24 rows were recomputed independently from the three `candidates.json` files, each `search.json`, `selection_budgets.json` and the budget constants in `src/bugarach/bench*.py`. This covers fresh F1 (recomputed as the quiet/busy mean), both budget sets on selection, held-out and fresh seeds, bracketing, changed settings, chorus picks and under-floor counts. Every stored selection-seed check was re-derived from its raw values, with no disagreement.
- The repo copy and the darkroom `report/` copy are byte-identical (so are `adoption.json` and all four figures). The table block inside README.md differs from `adoption_table.md` only in line endings. `figure3` is byte-identical to `065/report-inputs/figure3_elevated_rate.png`.

## Findings (location · issue · severity · suggested fix · verified against a source?)

1. **Line 36–37, "seeds 49–96, which nothing was chosen on" · HIGH · verified: yes.**
   - **Issue:** this is false. `tools/score_bench_candidates.py::proposal()` picks each proposal as the held-out candidate with the highest held-out `mean_f1` among those with `lo > 0`.
   - **Where it changed the outcome:** combined binned SCE, which the report calls adoptable. On the selection seeds the pair candidate was best (0.7519 vs rounds 0.7516), but the held-out seeds picked rounds (0.7669; the pair's `lo` is −0.0077). That row's "+0.015 [+0.006, +0.024]" is therefore measured after selecting on those same seeds. For fast and slow LoCo the held-out pick happens to agree with the selection-seed pick.
   - **Fix:** say that the held-out seeds chose among candidates and gated whether a proposal exists, and point to fresh seeds 6000–6023 as the independent check (combined SCE there: 0.748 → 0.764).

2. **"What waits on Tony" item 2, "Measured on" column · MEDIUM · verified: yes.** It understates:
   - Shipped slow locust also fails the probe on held-out (6.85 calls/min) and fresh (7.23 calls/min quiet; limit 4.0); the table says "selection seeds" only.
   - Shipped combined rate+context also fails the precision swing on fresh (0.257; limit 0.15).
   - The table has no row showing the shipped budgets of a detector that has a proposal, so these two failures appear nowhere on the page.
   - **Fix:** list selection, held-out and fresh for both rows.

3. **Item 3, "With the floor setting `min_rois`, the detector's own significance threshold stops binding" · MEDIUM · verified: yes (contradicted).**
   - **Issue:** no run record makes this claim, and the search histories refute it: changing `alpha` alone in round 1 moved selection F1 from 0.769 to 0.800 (fast) and from 0.778 to 0.791 (combined). A threshold that does not bind would change nothing.
   - **Fix:** delete the mechanism, or replace it with the measured fact ("lowering alpha alone gained +0.031 on fast and +0.013 on combined on the selection seeds").

4. **Combined CoactDetect row, "no: alpha (cap)" · LOW–MEDIUM · verified: yes.**
   - **Issue:** the search added 240 s to the combined CoactDetect (and combined rate+context) context grid, but `valid()` / `context_fits_the_null` refuses anything over 120 s, so 240 was never evaluated. The proposal's 120 s context counts as interior only because of a grid value nobody scored.
   - **Inconsistency:** slow LoCo, sitting at the same 120 s ceiling (ADR-0009 R5), is flagged `context_win_sec (edge)`.
   - **Adoption:** unchanged, since combined CoactDetect is already held back; the combined rate+context proposal is at 60 s and unaffected.
   - **Fix:** list `context_win_sec` as an open axis for combined CoactDetect, or note the inconsistency.

5. **Item 4 (fast LoCo) · LOW · verified: yes.**
   - "`threshold_pctile` at the cap": all 6 extensions went down the low end (94, 88, 76, 52, 4, 1). The top end (99.99) was never extended; it is "cap" only because the axis's extension allowance was used up going down. Say so.
   - Combined LoCo's context grid was also extended below 20 s (to 5 and 10 s). Its search produced no proposal, but the item implies fast LoCo is the only case.

6. **"What ran" table · LOW · verified: yes.**
   - The phase 0 PR lists include #811 (score-candidates-benches), #812 (cross-stream-candidates) and #813 (detect-with-floors-microscope), which are phase 3 tooling merged after phase 2 ran. Per `064/phase2/README.txt`, phase 2 ran at `b6e40f0`, which contains only #808–#810.
   - Phase 3 slow and combined says `main`, but `065/phase3/RUN.md` says it ran on branch `score-candidates-benches` @ `7af68c9`, with "PR #811 … not yet on main when this ran".

7. **"Real data" section · LOW · verified: yes.** The run record is `065/phase3-real-v2/` (after a failed first attempt in `065/phase3-real/failed-attempt-1`), and the write-up is `065/report-inputs/real_data.md`. The page says only "lands in `065/report-inputs/`". Stamp checked: dataset `senktide_ttx`, 66 recordings, matching `current_export.toml`'s default.

8. **Lines 19 and 147, "passes every budget" · LOW · verified: yes.** The precision swing is not recorded on held-out, and the close-events check is not run on fresh. **Fix:** "every budget recorded".

9. **Under-floor column and item 6 · LOW · verified: yes.**
   - The table shows the quiet background only. On fresh seeds the busy background loses much more: fast middle level 85/120 under the floor (71%), combined middle level 55/120, slow lowest level 50/120.
   - Item 6's 25/40, 20/40 and 15/40 come from the 8-seed `bench_floor.json` (Figure 4), a different seed set. They are correct for that source, but the fresh-seed share on fast is higher.
   - **Fix:** add the busy counts, or say which seed set item 6 describes.

10. **Latent tool issue (not wrong tonight) · LOW · verified: yes.** In `tools/make_final_parameters_report.py::held_out_budgets`, `ho.get("crowded_gain_vs_shipped", 0.0)` scores a missing close-events value as a pass. No row is missing it tonight.

**Record of experimental design and unit membership:** the bench is simulated, so there are no lab units. The only real-data claim points at a run stamped on the default export, and CLAUDE.md makes the export folder the source of record (withdrawn recordings are absent from it). The page reports no real-data numbers, so there are no unit counts to reconcile.

## Claim ledger (quoted · source · recomputed · verdict)

**Adoption table**

| Quoted | Source | Recomputed | Verdict |
|---|---|---|---|
| All 24 fresh F1 values, as scored and without decoys | `candidates.json` results | same to 3 d.p. | match |
| All 17 held-out gains and intervals | `search.json` `held_out.gain_vs_shipped` (also `candidates.json` `search_row`) | identical | match |
| All settings shown as changed | `candidates.json` proposal vs `search.json` shipped | same; no hidden changes, including NaN merge gaps | match |
| Budget verdicts, selection / held-out / fresh, all rows | see "What was checked" | every pass/fail agrees; fast CoactDetect held-out crowded −0.0441, slow SCE −0.0207, slow chorus_norm probe 1.433/min vs 1.0 | match |
| Bracketing, strict and "if a limit counts", all rows | `candidates.json` bracketing = `search.json` bracketing | agree | match (combined CoactDetect context: finding 4) |
| Chorus picks: fast seed1/seed4, slow seed3/seed3, combined seed1/seed0 | `train_rows` + `picked()` rule with CoactDetect's null budget | same | match |
| Under-floor: floors 5–6 (fast), 6–7 (slow), 6–7 (combined); 120/0/0 and 0/0/0 per level | `candidates.json` `under_floor`, quiet | same | match |

**Summary paragraph and definitions**

| Quoted | Source | Recomputed | Verdict |
|---|---|---|---|
| 4 adoptable (fast SCE; combined SCE, rate+context, SPIKE-synch) | recomputation | same | match |
| 10 held back = 5 limit + 4 cap/edge + 1 close-events | recomputation | same | match |
| 4 shipped points out of budget | recomputation | same | match |
| 400 bootstrap resamples | `BOOTSTRAP = 400` in `search_all_settings.py` | 400 | match |
| Seeds 1–48 / 49–96 / 6000–6023 / 56000–56011 / 66000–66011 | `search.json`, `candidates.json` | same | match |
| 120 events per level = 24 × 5 | scored + under per level | 120 | match |
| Floor: 1,000 draws, *J* = 20 s, 2 s window, 1/hour, min 3 | `bench_floor.json` rows; ADR-0008 | same | match for the bench-floor probe (the fresh-seed floor records carry no draw count) |
| MAX_CROWDED_DROP 0.02 | `bench.py` | 0.02 | match |
| "held-out, which nothing was chosen on" | `score_bench_candidates.proposal()` | chosen on held-out | **mismatch** (finding 1) |

**Figures**

| Quoted | Source | Recomputed | Verdict |
|---|---|---|---|
| Figure 2: 38 of 38 diagonal, 114 cells, versions as chosen | `cross_stream.json` | 38 versions, 114 rows all with F1, `all_reproduce` true, choices match | match |
| Figure 2: intervals in `adoption.json` `cross_stream` | `adoption.json` | present | match |
| Figure 3: 300 s stretch, 12 recordings, seeds 66000–66011 | ADR-0009, `candidates.json` | same; plotted slow locust (7.2) and slow chorus_norm (1.4) agree | match |
| Figure 4: 8 seeds; ADR ranges 5–10 / 6–8 / 5–10 | `bench_floor.json` | 48 rows = 3 × 2 × 8; ranges same | match |
| Figure 1 colours (4 blue diamonds) | recomputation | same | match |

**"What waits on Tony"**

| Item | Quoted | Recomputed | Verdict |
|---|---|---|---|
| 1 | locust gains +0.098 [+0.087, +0.110], +0.102 [+0.091, +0.115], +0.036 [+0.020, +0.052]; `n_synchronous_frames` = 1; slow rate `guard_sec` 0, slow SPIKE-synch `C_min` 0 | same | match |
| 2 | 0.181 / 0.148 (SPIKE-synch); 0.181 / 0.175 (rate); 7.24 / 3.69 vs 4.0 (slow locust); 0.245 vs 0.15 (combined rate); limits 0.10 | same | match on values; "Measured on" incomplete (finding 2) |
| 2 | "no admissible neighbour" | `DIAGNOSIS-sync-and-rate-moved-nothing.md` | match |
| 3 | alpha 1e-4 → 1.4e-9, 1e-5 → 1.4e-9; gains; −0.044 vs 0.02 | same | match |
| 3 | "stops binding" | contradicted | **mismatch** (finding 3) |
| 4 | round-1 context 5 s; pair at 20 s; ADR-0009 R5 = 120 s cap, no minimum | same | match (wording: finding 5) |
| 5 | guard ≤ ¼ context (`GUARD_MAX_CONTEXT_FRACTION = 0.25`, a runbook rule, not an ADR); 8 s guard on slow/combined grids | same | match |
| 6 | 40/40 at 3 and 4 ROIs; 25/40 (6 ROIs); 20/40 (8 ROIs); slow 15/40 busy only | `bench_floor.json` | match |
| Smaller items | slow SCE −0.0207, gain +0.014 [+0.011, +0.019]; chorus_norm 1.43 vs 1.0 | same | match |

**"What ran"**

| Quoted | Source | Verdict |
|---|---|---|
| `b6e40f0`, `a70b185`, `723f1e6`, `--max-extensions 6`, `--seeds 0 1 2 3 4 --device cuda` | run records | match |
| Phase 0 PR grouping; phase 3 slow/combined on `main` | git log, `065/phase3/RUN.md` | **mismatch** (finding 6) |
| Real-data location | night folder | partial (finding 7) |

## Files
- Artifact: `<worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md`
- Proposal pick rule (finding 1): `<worktree>\tools\score_bench_candidates.py` `proposal()`
- Context validity and bracketing (finding 4): `<worktree>\tools\search_all_settings.py` `valid()` / `bracketing()`
- Report tool (finding 10): `<worktree>\tools\make_final_parameters_report.py`
- Sources: `...\darkroom\bugarach\2026-09-25-final-parameters\` — `064\phase3\candidates.json`, `065\phase3\candidates.json` + `RUN.md`, `064\phase3-chorus-slow-combined\candidates.json`, `064\phase2\by-detector\search-fast-*\search.json`, `065\phase2\search-{slow,combined}\*\search.json`, `064\phase3-3x3\{selection_budgets.json, cross_stream.json, RUN.md}`, `065\bench-floor\bench_floor.json`, `065\phase3-real-v2\results.json`, `065\report-inputs\real_data.md`
