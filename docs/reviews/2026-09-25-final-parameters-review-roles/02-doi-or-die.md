GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch (also holds SubagentHandback, the report-return channel only; no Edit, Write or NotebookEdit; no file edited)

# Role 2 — Citations and references: final-parameters morning report

**Artifact:** `<worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md`. The darkroom copy (`<darkroom>/bugarach/2026-09-25-final-parameters/report/README.md`) is byte-identical (`cmp`).

## Findings (location · issue · severity · suggested fix · verified)

1. **"What ran" rows "0: the floor and the search (PR B) | #808, #810, #812" and "0: the bench (PR A) | #809, #811, #813".** Three of the six PRs are credited to the wrong phase and work. `gh pr view` titles (all MERGED):
   - #808 "PR B: ADR-0008's floor in run_detector and the scorer, the search grids, bracketing" — correct.
   - #809 "ADR-0009 decision 1: the elevated-rate test gets a recording of its own (PR A)" — correct.
   - #810 "Warm the elevated-rate recording's floors with the rest (follow-up to #808)" — a follow-up to #808, though about the bench's elevated-rate recording; acceptable under PR B.
   - #811 "score_bench_candidates.py: --benches, and a search per detector" — phase 3 scoring tooling, **not the bench**.
   - #812 "Phase 3: the 3 x 3 reads tonight's records; the floor cache survives a concurrent write on Windows" — phase 3, **not floor/search**.
   - #813 "detect_with_floors.py takes grid_dt and imaging_rate_hz from the recording" — phase 3 real data, **not the bench**.

   **Medium** (it tells Tony phase 0 was six PRs when it was three). Fix: #808 and #810 under PR B, #809 under PR A; #811 and #812 on the phase 3 rows, #813 on the real-data row. **Verified: yes.**

2. **"What ran" row "3: fresh seeds, slow and combined | WSMIP065 | `main`".** Wrong provenance: `065/phase3/RUN.md` says `Git: 7af68c97… (branch score-candidates-benches, PR #811 … not yet on main when this ran)`, so the slow and combined rows of the adoption table come from unmerged branch code, not `main`. **Medium** (the report states provenance its own run record contradicts). Fix: "`score-candidates-benches` `7af68c9` (PR #811, before merge)". **Verified: yes.**

3. **"What ran" rows "2: slow and combined searches" and "0: the bench (PR A)" — code listed as `main` with no commit.** The report pins a commit for WSMIP064's runs but not WSMIP065's. `065/phase2/RUN.md` records `b6e40f0` ("origin/main after #809"). I found no pin for `065/bench-floor/`, which holds only `bench_floor.json` (JSON contents not opened). **Low.** Fix: pin `065/phase2` to `b6e40f0`, and the bench-floor run to its commit or say it is unrecorded. **Verified: partly** (yes for phase 2; not established for bench-floor).

4. **"Real data" section → `065/report-inputs/`.** The pointer leads to a superseded run:
   - `065/report-inputs/real_data.md` names its run record as `065/phase3-real-v2/` (at `723f1e68`).
   - `065/phase3-real-v3/RUN.md` also exists and says v2 "left locust and SCE unseeded, and two runs with the same coded settings differed in 4 locust verdicts". v3 was rerun on the branch of PR #814, which `gh` shows as **OPEN**.
   - The report mentions neither v2, v3 nor #814, and does not say which run the real-data write-up describes.

   **Medium** (the run a reader will open is the one its author found non-reproducible). Fix: name the run that counts (v2 or v3), note that v3 depends on the unmerged PR #814, and note that v2's locust and SCE verdicts are unseeded. **Verified: yes.**

5. **Item 2 under "What waits on Tony": "The diagnosis is in the run record of phase 2."** Phase 2 has two run records (`064/phase2/`, `065/phase2/`); the diagnosis is `064/phase2/DIAGNOSIS-sync-and-rate-moved-nothing.md`. I checked that file: it gives shipped swings of 0.181 for both SPIKE-synch and rate+context against a limit of 0.10, and says the rescue rule has nothing to move to, so the report's paraphrase matches. **Low.** Fix: give the file path. **Verified: yes.**

6. **"What ran" bullet "Chorus: `tools/train_learned_on_bench.py --model <m> --seeds 0 1 2 3 4 --device cuda`".** The command as quoted cannot run: `--bench` is `required=True` (`tools/train_learned_on_bench.py:80`), and the runbook's version includes `--bench <b>`. **Low.** Fix: add `--bench <b>`. **Verified: yes.**

7. **Item 4: "ADR-0009 decision 5 set 120 s as the longest context and no shortest one."** A loose paraphrase. Decision 5 sets the context grids to "20, 30, 45, 60, 90 and 120 s" and says "the shorter values let a search find a short context". It sets no explicit shortest value, but it does name 20 s as the grid's lower end, so "extended below the 20 s grid" is an extension past what the ADR wrote, and "no shortest one" is an inference from its silence. **Low.** Fix: "ADR-0009 decision 5 caps context at 120 s and lists 20 s as the grid's lowest value; it does not say whether a search may extend below it." **Verified: yes.**

8. **Other ADR citations (ADR-0008/0009 in the header and Floor paragraph; ADR-0009 decisions 1, 4 and Consequences; ADR-0006 on decoys; FOUNDATIONS §9).** No issue. All resolve and say what the report says:
   - ADR-0008: max(3, null floor), 1,000 draws, *J* = 20 s, 2 s window, ≤ 1 call/hour.
   - ADR-0009 decision 1: the elevated-rate recording; decision 4: no limit loosened; Consequences: lowest level under the floor, 3 ROIs fast / 4 combined, "as ADR-0009 anticipated".
   - ADR-0006: decoy calls left out of precision.
   - FOUNDATIONS §9: exists and constrains how real-data results are read.

   **None. Verified: yes.**

9. **Budget constants named in the report.** No issue. All match `src/bugarach/bench*.py`: `MAX_CROWDED_DROP` = 0.02; fast `MAX_PRECISION_DROP` sync/rate = 0.10; combined rate = 0.15; slow `MAX_PROBE_PER_MIN` cicada (locust) = 4.0 and coact = 1.0; `MAX_EXTENSIONS` = 6 (the default for `--max-extensions`). **None. Verified: yes.**

10. **Runbook link and other cited paths.** No issue in the report. All exist: `docs/handoffs/2026-09-25-overnight-final-parameters.md`; `tools/make_final_parameters_report.py`, `detect_with_floors.py`, `search_all_settings.py`, `train_learned_on_bench.py`; every darkroom record folder named in "What ran"; commits `b6e40f0` (#809 merge), `a70b185` (#811 merge) and `723f1e6` (#813 merge). The report's "adoptable" definition, seed ranges (1–48, 49–96, 6000–6023, elevated-rate 66000–66011) and quarter-of-context guard cap match the runbook or run records. *Out of scope, for whoever owns the runbook:* since the move to `docs/handoffs/`, the runbook's own relative links (`docs/adr/...`, `docs/FOUNDATIONS.md`, `docs/handoffs/README.md`) no longer resolve. **None for the report; low for the runbook. Verified: yes.**

11. **Phase 1 row "PR B + PR A merged locally, never pushed".** Not verifiable: `064/pilot/` has no record file with a git line, and there is also an unmentioned sibling folder `064/pilot-chorus-prb-only/`. **Low.** Fix: cite the pilot's record, or mark the claim unrecorded. **Verified: no.**

12. **Named methods (rigid-shift null, SPIKE-synch, locust, CoactDetect, LoCo, binned SCE, rate+context, chorus).** The report claims nothing as novel and cites no external literature; it uses the methods only as detector names whose parameters are up for adoption. Locust is a modified port of the Cossart lab's CICADA (Denis et al. 2020); ADR-0002 puts that citation in the help panel, README and methods text, not in every internal report, so its absence here does not break ADR-0002. If this page is ever read by outsiders, it names "locust" with no pointer to its origin; a one-line gloss or glossary link would fix that. **None / informational. Verified: yes** (ADR-0002).

## What I searched and did not search
**Searched:**
- the report text;
- the six PRs via `gh`, plus #814 (not mentioned in the report);
- ADR-0002, 0006, 0008 and 0009; the runbook; FOUNDATIONS §9;
- the budget constants in `bench.py`, `bench_slow.py` and `bench_combined.py`;
- the argparse of the cited tools; git for the pinned commits;
- the darkroom night folder: the RUN.md/README files in 064/phase2, phase3, phase3-chorus-slow-combined, phase3-3x3, 065/phase2, phase3, phase3-real-v3, and report-inputs/real_data.md.

**Not searched:**
- **External literature:** the artifact has no bibliographic references and no novelty claims, so no web or DOI search was needed; none was run, and forward tracing does not apply.
- **The figure and table values themselves** (F1 values, intervals, "38 of 38", "114 cells"): the number-checking roles own these.
- **The contents of `bench_floor.json` and `adoption.json`.**
- **Correspondence:** no human was asked, because there is no unattributed or novelty claim that would require it. No gap results.
