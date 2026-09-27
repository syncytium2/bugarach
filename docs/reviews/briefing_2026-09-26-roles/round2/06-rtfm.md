GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(The harness also gave me SubagentHandback, which is only the reporting channel. I held no Edit, Write or NotebookEdit.)

# Role 6 (RTFM): blind review of the built briefing page

**Summary:** the page applies the scorer, the budgets and the scoring rules correctly. I found one methods problem with real consequence (finding 1). The rest are wording drift from what the source says, and things that are hard-coded where they should be read from the run's files.

## What I read, and what I checked independently

**Sources read:**
- ADR-0010 in full
- ADR-0006, on decoys
- ADR-0008, on the floor
- `tools/score_bench_candidates.py`: `paired_difference`, `per_seed_f1`, `proposal`, `picked`, `seeds_for`/`seed_factor`
- `tools/search_all_settings.py`: `make_admissible`, `bracketing`, and the realistic switches
- `tools/make_final_parameters_report.py`: `fresh_budgets`, `failed`, `BUDGET_NAME`
- `src/bugarach/score.py`: `TOL_SEC`, `score_detections`, the extent field, merges
- `src/bugarach/bench.py`: `SPACINGS`, `seed_factor`, `pool_scores`, the precision rule, the four budget dictionaries on all three stream modules, the background rates
- `tools/detect_with_floors.py`: `calls.csv`, `windows.csv`, `chosen`, `PARTICIPANTS_RULE`
- The whole of `<worktree>/tools/make_briefing.py`

**Re-run against the night's files** (scratch only, in `<scratchpad>/mb2`; nothing written anywhere else):
- **Budgets and intervals, all 126 cells:** I recomputed every row × bench cell's failed budgets straight from `candidates.json` using the admissibility rule, plus its paired ΔF1 mid/lo/hi and its mean F1. There were **0 mismatches** with `briefing.json`.
- **The count-rule files:** their CoactDetect shipped and proposal rows match the main files exactly on the new, old and ORX benches, so rows merged in from those files are paired against the same reference.
- **Settings used on the real recordings:** `results.json` `chosen` matches the fresh-realistic proposals and learned picks for every detector and stream, so `ran_on_real`'s inference is correct tonight.
- **Seed counts:** 48 fast / 24 slow / 24 combined on the new bench and 24/24/24 on the old, as the page says, and consistent with `seed_factor`.
- **Floors:** no baseline window lacks a floor, so the calls-per-hour denominators are not biased by windows where CoactDetect could not run.
- **The "about 0.99 without decoys" claim on slow:** holds (14 of 19 rows at or above 0.985 on the new bench).

## Findings

Each finding gives location · issue · severity · fix · verified against a source.

**1.** Leaderboard headline, Table 1, Figure 1, and the "above zero / unflagged" counts
- **Issue:** Every row is paired only against CoactDetect's *shipped* setting, which predates the new bench. The rows it is compared with (proposals and learned picks) were chosen on the new bench.
  - The scorer also computes `paired_f1_vs_coact["proposal"]`, the comparison against CoactDetect's own new-bench tuning. The page drops it.
  - Recounted against that reference on the new bench (not counting CoactDetect's own rows), rows with an interval wholly above zero fall from 12/15/11 to **0/1/1** (fast/slow/combined). Against shipped, the page reports 13/16/12, a count that includes CoactDetect's own proposal.
  - The examples section already uses CoactDetect's proposal as its reference, so the page uses two different CoactDetect settings as its reference.
  - The headline does admit that selection favours the rows it compares. But "13 of 22 rows sit above CoactDetect" is not the like-for-like reading. ADR-0010 part 5's bar ("beat CoactDetect's fresh-seed F1 … paired interval above zero") does not say which CoactDetect setting it means.
- **Severity:** Medium–High
- **Fix:** Add the vs-proposal interval as a column, or as a second count in Table 1 and the headline. Say that the proposal is not adoptable (guard 0 is an off-limit value under ruling 5), which is why shipped stays the reference. Let the reader see both.
- **Verified:** yes (recomputed from `candidates.json`)

**2.** "How to read it" → Budgets: "The close-events test is not run on fresh seeds."
- **Issue:** ADR-0010 part 4 **retired** the close-events recording and `MAX_CROWDED_DROP`, and the search turns that veto off under realistic spacing (`ev.crowded = … and not realistic()`). The sentence makes it sound like a live budget that was skipped.
- **Severity:** Low–Medium
- **Fix:** "The close-events test was retired by ADR-0010 part 4; the scored recordings now contain close events."
- **Verified:** yes

**3.** `limit_marks`, the † mark, "unflagged", and the leader rule
- **Issue:** Any unbracketed axis is marked "not adoptable as tuned". That includes `limit` reasons that are not off-values (count offset k = 0 at ADR-0008's floor), `grid_floor`/`grid_ceiling` (context at 20 s under ruling 7, 120 s under ADR-0009 decision 5), and an `edge` (combined CoactDetect guard 8 s).
  - ADR-0010 settled only off-values (ruling 5) and caps (ruling 6).
  - The 2026-09-25 report kept "a limit counts as a bracket" as a separate column, "because which rule applies is Tony's".
  - Rows flagged for this reason alone tonight: fast count proposal, combined count (sliding) proposal, combined CoactDetect proposal. The page says "What it decides: nothing", yet it applies the strict reading.
- **Severity:** Low–Medium
- **Fix:** Tell the two apart: "off-value/cap (ruled)" versus "at a limit by design or a grid edge (strict runbook reading; the looser reading is open)". Alternatively, name the strict rule as the runbook's.
- **Verified:** yes (`search_all_settings.bracketing`, ADR-0010 rulings 5–8, `make_final_parameters_report` docstring)

**4.** "How to read it", ADR-0010 ruling 1 line
- **Issue 1 (coverage):** `orx_check` reads only `065/fresh-orx`, so the 6 count-rule rows are left out ("4 of 51"), although `064/count/fresh-orx/candidates.json` exists. `EXTRA_GLOBS` even matches that file, but skips it because its spacing is orx.
- **Issue 2 (wording):** "a bench spaced like the slow ORX recordings" is inaccurate. The orx spacing draws each stream's gaps from the ORX recordings (`spacing_overrides`, `pool="ORX"`). Ruling 1 singled out slow as the reason for the check; it did not limit the check to slow.
- **Issue 3 (scope):** It counts rows whose interval changes side, not whether the rankings hold, which is what ruling 1 asks. That is acceptable, but should be said.
- **Severity:** Low–Medium
- **Fix:** Merge the count-rule ORX file into the check the same way the new and old benches are merged. Reword to "spaced like the ORX recordings, on each stream". Optionally add a rank-agreement figure.
- **Verified:** yes

**5.** "How to read it", ΔF1 definition, and the Table 2–4 caption
- **Issue:** The per-seed F1 in ΔF1 is `pool_scores(..., regime="both")`: counts from the seed's quiet and busy recordings are pooled, then one F1 is taken. It is not the mean of the two backgrounds' F1s, which is what the F1 columns are. The caption blames only seed-averaging for the columns not subtracting.
- **Severity:** Low
- **Fix:** "per seed, F1 pooled over that seed's quiet and busy recordings".
- **Verified:** yes (`score_bench_candidates.per_seed_f1`, `bench.pool_scores`)

**6.** Examples prose: "its proposal, which … is itself on a search limit"
- **Issue:** Hard-coded text, not read from `chosen` and the flags.
  - True tonight: guard 0 on fast and slow; guard 8 s at a grid edge on combined, which is an edge rather than a limit.
  - It would be false on a night where CoactDetect ran shipped or bracketed.
- **Severity:** Low (latent)
- **Fix:** Build the sentence from `ref_which` and the proposal row's flags.
- **Verified:** yes

**7.** `ran_on_real`
- **Issue:** It infers the setting used on the real recordings from the leaderboard (proposal if one exists) rather than reading `results.json` `chosen`, which records exactly which setting ran and its parameters. It is correct tonight, but would silently mismatch if detection ran from a different `candidates.json`.
- **Severity:** Low (latent)
- **Fix:** Compare against `chosen[stream]["detectors"][det]["which"]` and its params, and `chosen[stream]["chorus"][fam]` for the learned picks.
- **Verified:** yes

**8.** `classify` / `_overlaps` with binned SCE
- **Issue:** The bench scores binned SCE over `extent_sec` (`score.EXTENT_FIELD`), but `calls.csv` stores only `width_sec`, which for SCE is the spread of the events in the bin. If SCE were ever leader or runner-up, its agreement would be measured over a different stretch from the one it was benched on. SCE is neither tonight.
- **Severity:** Low (latent)
- **Fix:** Refuse SCE as leader, or carry extent into `calls.csv`, or note it on the page.
- **Verified:** yes

**9.** Leader rule prose: "disagrees with CoactDetect at least once each way"
- **Issue:** The code (`not all(k.values())`) also requires at least one agreeing call.
- **Severity:** Low
- **Fix:** "…agrees at least once and disagrees at least once each way."
- **Verified:** yes

**10.** Participants line in the examples
- **Issue:** The page correctly labels the ±1 s count as the review tool's own. ADR-0010 part 6 / ruling 3 says the core count (`core_n_roi` from `call_measure.py`) replaces it on each stream where the planted-truth check passes. The page does not say whether that check ran or failed.
- **Severity:** Low
- **Fix:** One clause: "the call measure's core count is not adopted on any stream yet (ADR-0010 ruling 3)", or whatever the status is.
- **Verified:** partly (the ADR, yes; whether the check ran, no)

**11.** Terms glossary: "merged calls" and "floor"
- **Issue:**
  - "merged calls": `score.py` counts only *scored* events (at or above the floor), by containment, with no tolerance.
  - "floor": ADR-0008's floor is max(3, the chance floor at 1 call per hour), not simply "the smallest count that is not chance".
- **Severity:** Low
- **Fix:** Add "scored (at or above the floor)" and "never below 3 ROIs".
- **Verified:** yes

**12.** "How to read it": "95% percentile-bootstrap … (2,000 draws)" and "ADR-0010 counts 0.01 F1 as one noise unit … rows closer than that are level"
- **Issue:**
  - The 2,000 draws is a literal. It matches `BOOTSTRAP` in today's scorer, but the run record does not carry it.
  - ADR-0010 defines the noise unit for its drop-from-tuning rule. "Level" is the page's extension of it.
- **Severity:** Low
- **Fix:** Import `BOOTSTRAP`. Phrase the second as "ADR-0010's noise unit (0.01 F1, used for its focus rule)".
- **Verified:** yes

**13.** Hidden dropped seeds
- **Issue:** `n_seeds` and `n_dropped` from `paired_difference` are never shown. No leaderboard row has dropped seeds tonight: the only rows that do are unpicked training runs, with up to 8 of 48 seeds dropped. A future pick with dropped seeds would show an interval over fewer seeds with no mark.
- **Severity:** Low (latent)
- **Fix:** Mark a row where `n_seeds` is below the stream's seed count.
- **Verified:** yes

## Files
- Code reviewed: `<worktree>/tools/make_briefing.py`
- Page reviewed: `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, plus its `briefing.json`
- Nothing was written outside `<scratchpad>/mb2`; no files were modified.
