GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 2 — DOI or Die: final-parameters morning report

Artifact: `docs/learned/runs/2026-09-25-final-parameters/README.md` (worktree `floor-and-grids`, branch `run/final-parameters`, HEAD `79efeda`). The darkroom copy (`<darkroom>/bugarach/2026-09-25-final-parameters/report/README.md`) is byte-identical.

The report makes no novelty claim and cites no external paper, so most of the work was internal attribution: PR, commit, ADR, run record and quoted source line. There is one external attribution issue, implicit, inside Decision 1.

## Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| 1 | "Real data" *Where it ran*; "What ran" row "3: real data" | "#814 is not merged, so the run is on unmerged code" is stale. `gh pr view 814`: MERGED 2026-09-25T07:21:58Z, merge commit `3153b9b`. The run finished 07:15:37Z on `879be03` (#814's head), and `3153b9b` and `879be03` have the **same tree** (`dbaa623…`), so the run's code is now exactly on `main`. The report's own commit `79efeda` (07:29Z) postdates the merge; the branch is based on `723f1e6`, which is probably why it still looked unmerged. | major | "Ran on `879be03` (#814's head) before it merged; #814 merged at 07:21Z as `3153b9b` with an identical tree, so the run's code is on `main`." Same in the What-ran row. | yes |
| 2 | Decision 1, row "combined · SPIKE-synch" (`tau_mode` isi_adaptive → fixed) | The proposal turns off the ISI-adaptive coincidence window, which the repo's own sources say defines the measure: `docs/GLOSSARY.md` calls it "core SPIKE-synchronization (Kreuz 2015), not an option on it" and says `fixed` "makes the measure rate-dependent again"; `src/bugarach/detectors/sync.py` calls `fixed` "ordinary fixed-window coincidence detection" and says the default "is not up for quiet revision". If adopted, a detector still called SPIKE-synch would no longer compute Kreuz, Mulansky & Bozanic's measure (2015, *J Neurophysiol* 113:3432–3445, doi:10.1152/jn.00848.2014, resolved via Crossref), so any methods text citing Kreuz for it would be a misattribution. None of the three "Read these before deciding" bullets says so. It also bears on the bench's own warning that SPIKE-synch keys on rate (`bench.py`, `MAX_PROBE_PER_MIN` docstring). | major | A bullet under "Read these three things before deciding": adopting this row replaces SPIKE-synchronization with fixed-window coincidence counting on combined, which needs its own ruling, a new name or qualifier, and a changed methods citation. | yes (repo sources + DOI) |
| 3 | "What ran" row "3: the 3 × 3": "`main` `723f1e6` (#812)" | `723f1e6` is the merge commit of **#813**; #812's merge is `1ad2654` (which `723f1e6` contains). The hash matches the run record (`064/phase3-3x3/RUN.md`); the PR label is wrong. | minor | "`main` `723f1e6` (after #812 and #813)" | yes |
| 4 | "What ran" table | #813 (`detect_with_floors.py` takes `grid_dt` and `imaging_rate_hz` from the recording) is missing, though it is in the real-data run's code. The task scope named #808–#814; the table accounts for all but #813. | minor | Name #813 in the real-data row. | yes |
| 5 | "What ran" row "1: pilot" | The row says both pilot folders ran on "PR B + PR A merged locally", but `064/pilot-chorus-prb-only/README.txt` says that pilot ran on PR B (#808) **alone, before PR A**; only `064/pilot/` had both. | minor | Split the row, or add "(`pilot-chorus-prb-only`: PR B alone)". | yes |
| 6 | "Real data" *Where it ran*: "supersedes `065/phase3-real-v2/`, where locust was left unseeded" | `065/phase3-real-v3/RUN.md` and `065/report-inputs/real_data.md` both say v2 left **locust and SCE** unseeded (only locust's verdicts differed: 4 flips). | minor | "where locust and SCE were left unseeded (only locust's verdicts changed, 4 flips)" | yes |
| 7 | Figure 3 caption: "every ROI's own event rate is raised to the background's 99th percentile" | `bench.ELEVATED_RATE_RECORDING` sets every ROI to **one** rate, `hot_rate_hz` = 0.1334 Hz on fast (0.0321 Hz on slow, `bench_slow.py`), the 99th percentile of 300 s baseline stretches; each ROI's own rate is not scaled. | minor | "every ROI's event rate is set to one rate, the 99th percentile of 300 s baseline stretches (0.1334 Hz on fast)" | yes |
| 8 | "What ran" *Selection budgets*: "re-derived independently in review, with no mismatch" | Not verifiable from the artifact: the re-derivation belongs to another role's review and has no record I could open. | minor | Point at the review record holding the re-derivation. | no |
| 9 | Decision 1, second bullet ("These are separate intervals… it was not computed") | The disclosure is honest, but the runbook (`docs/handoffs/2026-09-25-overnight-final-parameters.md`, "Verify each run record") required "intervals are paired", and the report does not say it departs from the runbook here. | minor | Add "(the runbook asked for paired intervals; this one was not computed)". | yes |

## Residual ⚠

- **Nobody has been asked about a fixed-window SPIKE-synch, as far as the record shows.** `sync.py` says Kreuz was "being asked what the software should call it". `docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md` records his April reply, which covers C over E, the detection layer and one-spike-per-pixel postprocessing, not fixed τ. **Question for Tony:** has anyone asked Kreuz (or anyone) about this variant? If so, cite it as a dated paraphrase (a public repo cannot quote private correspondence).
- **Locust's lineage is absent.** Locust derives from the Cossart lab's CICADA (ADR-0002; `cicada.py` says not to report its numbers as CICADA's). The report says "locust" throughout and never CICADA, which is correct, but has no pointer to ADR-0002 or `docs/detector_history.md` — fine for an internal page, needed before any excerpt goes out.

## Checked and correct (evidence for no finding)

- **Links:** the runbook, ADR-0008 and ADR-0009 resolve from the page's folder.
- **ADR-0009:** decision 4 (no limit loosened; a failing proposal is not adopted) and decision 5 (context grid 20–120 s, cap 120 s, silent below 20 s) are stated correctly, as is "recall counts only events above the floor, as ADR-0009 anticipated" (its Consequences).
- **ADR-0008:** the floor definition matches (≥3 ROIs, ≤1 call/hour, *J* = 20 s, 2 s window, ≥1,000 draws), as does the requirement to report stability across halves of the draws.
- **ADR-0006:** the decoy definition matches.
- **Runbook:** the quarter-of-context guard cap is the runbook's (step 5), not an ADR's, as stated; the strict "adoptable" rule matches Phase 4.
- **Quotes:** "the thing to look at before any of these is trusted" is verbatim in `src/bugarach/bench_combined.py` (across a line break, about the probe/elevated-rate ceilings, as the report says); "still unsigned" is verbatim in `src/bugarach/bench_slow.py` (about the close-events allowance).
- **Budget values:** every quoted limit matches its source — fast rate+context and SPIKE-synch precision swing limit 0.10 (measured 0.01 pre-floor); combined rate+context 0.15; slow locust elevated-rate ceiling 4.0/min; slow CoactDetect 1.0/min; combined rate+context outside-stretch 1/hour; close-events allowance 0.02.
- **"PR A's choice":** quiet-only gating of calls outside the stretch is stated in the #809 body.
- **Code:** `score_bench_candidates.proposal()` behaves as described; the `bench.settings_are_valid` fix and its test are in `79efeda` (`tests/test_bench_floor.py`); `MAX_EXTENSIONS` = 6, `BOOTSTRAP` = 400, `TOL_SEC` = 2.5 s, and both tools' CLI flags are confirmed.
- **Figure 4 re-measure:** 25/20/15 of 40 matches the #809 body's table.
- **Commits:** `b6e40f0` is #809's merge and contains #808 and #810; `a70b185` is #811's merge; `7af68c9` is #811's head; each run record's code stamp matches its row; `065/bench-floor/bench_floor.json` records no commit, as stated.
- **Darkroom records:** the DIAGNOSIS file is at the stated path, with the conclusion "a real budget, not a bug"; the real-data numbers (66 recordings, `senktide_ttx`, 128 windows, 3,072 cells, 2,696, 498, +17/+20 ROIs) match `real_data.md` and `RUN.md`.
- **Seeds and lengths:** fresh 6000–6023, null 56000–56011, elevated-rate 66000–66011 (offset 60,000); recording 45 min (2,700 s) with a 5 min stretch.
- **FOUNDATIONS §9** exists and is the section the runbook cites for "descriptive only".

## Searched and not searched

- **Searched:**
  - repo ADRs 0002/0006/0008/0009, the runbook, `GLOSSARY.md`, the Kreuz todo;
  - code: `bench.py`, `bench_slow.py`, `bench_combined.py`, `score.py`, `detectors/sync.py`, `detectors/cicada.py`, `tools/search_all_settings.py`, `tools/score_bench_candidates.py`, `tools/train_learned_on_bench.py`;
  - GitHub PRs #808–#814 via `gh`, and git ancestry/trees on `origin/main`;
  - every darkroom run record the report names;
  - Crossref (the Kreuz 2015 DOI).
- **Not searched:**
  - the rigid-shift-null references ADR-0006 lists (Grün 2002, Louis 2010, Stella 2022, Mölter 2018, Bilen 2020), reached only via ADR-0008 → ADR-0006 and not re-resolved;
  - Satuvuori 2017;
  - prior art on per-window null-derived participation floors (no novelty is claimed, so not blocking, but it is an unsearched field ⚠ if a methods text later presents the floor as the lab's own method);
  - table numbers against `adoption.json`, and the figures (not opened).
