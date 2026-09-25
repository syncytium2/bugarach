GRANT 4 ok — Read, Grep, Glob, Bash

# Role 4 — Reviewer 2: docs/learned/runs/2026-09-25-final-parameters/README.md

**Artifact:** `<worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md`. Also opened: all four PNGs, `adoption.json`, the generator `tools/make_final_parameters_report.py`, `tools/score_bench_candidates.py` (`proposal()`), `tools/search_all_settings.py` (`held_out()`), the budget constants in `src/bugarach/bench.py`/`bench_slow.py`/`bench_combined.py`, every `search.json` held-out block, and the darkroom files `064/phase2/DIAGNOSIS-sync-and-rate-moved-nothing.md` and `065/report-inputs/real_data.md`. No file was edited.

Each row: location · issue · severity · suggested fix · verified against a source.

## BLOCKING

**B1 · Adoption-table preamble ("seeds 49–96, which nothing was chosen on") and the summary ("Each has a held-out gain whose 95% interval is above zero").** The held-out seeds ARE used for selection. `score_bench_candidates.proposal()` picks "the search's best held-out candidate … whose gain interval is above zero": it ranks rounds / pair / shipped by held-out mean F1 and keeps only those with held-out lo > 0. Two consequences:
- The reported proposal's held-out interval carries selection bias: it is the maximum of 2–3 candidates (e.g. fast LoCo: rounds lo −0.019 was dropped, pair lo +0.001 was kept).
- "Gain interval above zero" cannot fail for any proposal, because it was the filter that produced the proposal. All 14 proposals, including the 10 held back, pass it by construction, so the adoptable test's `gain.lo > 0` clause is inert.

**Blocking** (the key independence claim). Fix: state that the held-out seeds chose among the search's final candidates, so the interval is not unbiased, and that the positive lower bound is a selection filter, not a test. Either report the fresh-seed gain with its interval (it is in `cross_stream.rows` `mean_f1_ci`) as the independent check, or add it to the adoptable rule. **Verified: yes** (`score_bench_candidates.py` L54–64; `search.json` held_out blocks).

**B2 · "What waits on Tony" item 2 (four shipped points out of budget) and the table's `precision_swing` fails.** Presented as facts about the detectors. But the phase 2 diagnosis says the swing is **new under the floor**: each recording's floor follows its own event rate, so the busy background takes a higher floor and removes a different set of planted events (per Figure 4, 25/40 middle-level events are under the floor on busy fast and none on quiet). The diagnosis calls "why the two backgrounds' precision now differs by 0.13–0.18" "a question for Tony", and the report drops that question. The budgets were also measured at the shipped points on the pre-floor bench (fast rate/sync swing measured 0.01, limit 0.10). A shipped point "failing its own budget" may be a scoring artifact of don't-care sets that differ between backgrounds, not a degradation. **Blocking** for the adoption decision: it is the premise behind "the searches moved nothing". Fix: carry the diagnosis's caveat and open question into item 2; state that each budget is a ceiling measured at the shipped point on the pre-floor bench; add "is the swing a floor artifact?" to the six questions. **Verified: yes** (DIAGNOSIS file; `bench.py` `MAX_PRECISION_DROP` comments).

## MAJOR

**M1 · Item 2 table "Measured on" column.** Understates. Slow locust shipped also fails the probe on held-out (6.85/min) and fresh (7.23/min), not only selection; combined rate+context shipped also fails the swing on fresh (0.257), not only selection. A failure repeating on three seed sets is stronger than the page says. **Major.** Fix: fill the column from `adoption.json` `shipped.budgets.*` for all three seed sets. **Verified: yes.**

**M2 · Figure 2 and the report's "tuned on a stream" framing.** The picture shows structure the text never mentions — a version tuned on combined often beats the stream's own version on that stream:
- combined-tuned LoCo (shipped) on fast 0.820 [0.806, 0.838] vs the fast LoCo proposal 0.794 [0.779, 0.809];
- combined-tuned CoactDetect proposal on fast 0.827 vs the fast proposal 0.809;
- combined-tuned rate+context proposal on slow 0.865 [0.855, 0.874] vs the slow proposal 0.834 [0.825, 0.843], and on fast 0.736 vs fast shipped 0.703.

Every row also scores highest in its slow column: the slow bench is simply easier, and F1 levels are not comparable across streams. Tony is choosing per-stream adoptions without being told this. **Major.** Fix: one sentence under Figure 2 naming these off-diagonal wins with intervals; a Tony question — does per-stream tuning hold up when a combined-tuned setting wins on fast and slow?; and a warning that F1 levels are not comparable across columns. **Verified: yes** (`adoption.json` `cross_stream.rows`).

**M3 · Summary: "passes every budget on selection, held-out and fresh seeds".** Overclaims: held-out never checks the precision swing (not recorded), fresh never checks the close-events allowance, and the elevated-rate "outside the stretch" budget is gated on quiet only. Adoptable combined rate+context makes 1.28 calls/h outside the stretch on busy (held-out) against a limit of 1.0, and Figure 3's bottom-right panel shows the same point above the bar. **Major.** Fix: reword to "passes every budget that was checked on each seed set", list the gaps inline, and state the combined rate+context busy value beside its adoptable "yes". **Verified: yes** (generator `fresh_budgets`/`held_out_budgets`; `search.json` `elevated_out_busy_per_hour`; Figure 3).

**M4 · `MAX_CROWDED_DROP` 0.02 (preamble; "Smaller items" slow binned SCE; item 3).** An unjustified, fragile constant:
- `bench_slow.py` says the allowance is "still unsigned on fast (the crowded-allowance sweep is its input)", and the report never says so.
- It is scored as a point estimate on 12 close-events seeds (`N_TAIL = 12`) with no interval.
- Slow binned SCE is excluded for −0.0207 against −0.02, a margin of 0.0007. The same statistic moved from −0.0198 (selection) to −0.0207 (held-out), and for fast CoactDetect from −0.017 to −0.044; the noise is plainly larger than the margin.

**Major.** Fix: state that 0.02 is provisional and unsigned, give the close-events loss a bootstrap interval, and present slow binned SCE as "at the allowance within noise" — a Tony call, not a settled "not adoptable". **Verified: yes** (`bench_slow.py` ~L331; `search_all_settings.py` `N_TAIL`; `adoption.json`).

**M5 · "Real data" section.** It says the run "lands in `065/report-inputs/`" (future tense), but `real_data.md` is already there, reporting 66 recordings, 3,072 cells, 502 verdict flips, and a treatment-window floor that differs from the baseline floor by up to +22 ROIs (ORX senktide). That bears directly on whether the ADR-0008 floor is fit for purpose, and the page Tony decides on shows none of it. Three run folders exist (`phase3-real`, `-v2`, `-v3`, the last with no `results.json`), and the report does not say which is the record. **Major.** Fix: summarise the counts or link `real_data.md` explicitly, and name `phase3-real-v2` as the run record (the one `real_data.md` cites). **Verified: yes** (darkroom listing; `real_data.md`).

**M6 · Figure 1 and the "fresh F1" column.** Point estimates only, with no intervals, although `cross_stream` holds them. Some fresh "gains" are inside the noise (slow rate+context 0.830 [0.822, 0.837] → 0.834 [0.825, 0.843]). Fresh F1 also plays no role in the adoptable rule (the generator never reads it for `adoptable_strict`), so the seed set that "neither the search nor the training saw" cannot veto an adoption on performance. **Major.** Fix: add 95% interval whiskers to Figure 1, and state plainly that fresh seeds gate budgets only, not gain, or add a fresh-gain criterion. **Verified: yes** (generator L178–181).

**M7 · Combined budgets gate three of the four adoptables.** `bench_combined.py`'s docstring says the combined probe ceilings (locust 68/min, SPIKE-synch 16/min) are "the thing to look at before any of these is trusted". Combined rate's probe ceiling is 8.0, while fast's is hand-set at 4.5 precisely to refuse rate's own F1 optimum at 4.98. The report treats all ceilings as equally valid. The adoptables pass by wide margins (probe 0.2 and 1.3), so no verdict flips. **Major/minor.** Fix: one line noting that the combined ceilings carry an open ⚠ in their own module. **Verified: yes.**

## MINOR

**m1 · Undefined quantities:**
- "F1"/"mean F1" is defined only in Figure 1's caption (mean over quiet and busy), and the match rule is not given.
- "without decoys"/"decoy" is only cited to ADR-0006.
- "quiet/busy background", "close-events recordings" (how close, how many) and "elevated-rate stretch" (what rate: the background's 99th percentile) are undefined.
- The table labels "cap / limit / edge" and the candidate names "rounds / pair" are undefined, and "extension cap" is never tied to `--max-extensions 6`.
- The "held-out gain" shown is the bootstrap median, not the observed difference.
- "400 resamples" does not say "of recordings, paired".

Fix: one glossary block above the table. **Verified: yes.**

**m2 · Under-floor column.** The percentages (10/20/30%, 21/38/63%, 13/25/40%) are undefined (likely the share of ROIs), while Figure 4 labels the same levels by participant count (3/6/10 …): two units, no conversion. The column is identical on every row of a stream and covers quiet only. It is a bench property, not a detector property, and it hides the busy-background losses that item 6 describes. Fix: one row per stream, both units, busy added. **Verified: yes.**

**m3 · Unjustified constants in the floor paragraph / "What ran":** the 3-ROI minimum, 1,000 draws, *J* = 20 s, the 2 s co-activity window, "once per hour", the guard cap at a quarter of context, `--max-extensions 6`, and the budget rule `max(1, ceil(1.6 × measured))`. None is justified in the text, only cited. Fix: one clause each, or an explicit "set in ADR-0008 §x" per constant. **Verified: partly** (the constants match the ADRs by citation; the justifications were not checked).

**m4 · Item 1, fast locust.** `n_synchronous_frames` at 1 is not a change the fast proposal made (the table lists no change to it), so the shipped point already sits there. The strict rule holds back a proposal for an axis it did not move, and the shipped point would fail the same test. Worth stating so Tony weighs the rule correctly. **Verified: partly** (the changed-settings list omits the axis; the shipped `OperatingPoint` was not opened).

**m5 · Item 3 mechanism ("with the floor setting `min_rois` the detector's significance threshold stops binding").** A causal claim asserted without evidence (e.g. a sweep showing F1 flat in `alpha` below some value). Fix: soften to "likely", or show the sweep. **Verified: no.**

**m6 · Figure 2 note "reproduces … in 38 of 38 cases, and all 114 cells".** The figure shows 24 diagonal cells and 72 cells in total, so the 38 and 114 count JSON rows that include undrawn shipped variants. Both sides of the check also come from the same scorer on the same seeds, so it is a determinism/wiring check, not a validation. Fix: say what is counted, and call it a reproducibility check. **Verified: yes.**

**m7 · Figure 3 vs item 2.** Figure 3 (seeds 66000–66011) shows slow locust shipped busy at ~4.4/min, above the bar of 4, while item 2 quotes 3.69 busy on the selection seeds. Two seed sets are in play and the text never reconciles them. Fix: note which seeds each number comes from. **Verified: yes** (visual read of the figure vs the table).

**m8 · Figure 4 left panel.** Every planted recording's floor sits about one ROI above the no-coordination recording's floor on the same background, so the planted events probably raise their own null, and recall "on the events chance does not reach" is partly defined by the events themselves. Fix: a Tony question or a sentence. **Verified: no** (visual only).

## Checks I ran that came out clean
- The summary counts (4 adoptable; 5 + 4 + 1 held back; 4 shipped failing).
- Item 5 arithmetic (20/4, 30/4).
- Figure 4's right-hand counts vs item 6.
- Figure 1 markers vs the table.
- The fresh and selection budget checks have power: they did trigger (rate and SPIKE-synch swing, slow locust probe, close-events on held-out). The alarm can ring where a check is applied; its gaps are coverage (M3), not power.
