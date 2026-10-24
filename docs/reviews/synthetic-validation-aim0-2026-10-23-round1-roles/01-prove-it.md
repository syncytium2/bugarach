GRANT 1 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch (and deferred NotebookEdit, SendMessage, WebFetch, Dropbox, Gmail/Docs MCP write tools). I used none of the forbidden ones on the artifact. The only files I wrote are under `_scratch/role-01/`. The run record should say this review took the general-purpose fallback path.

**Run finding (not about the artifact):** `aim1_figure.py` lines 152–153 save the PNG to `a.out` **and** to `HERE`. Passing `--out _scratch/role-01/` therefore still overwrites the tracked `docs/learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png`, so the brief's guard doesn't protect that file. I did not rerun the script. I checked the PNG by eye: its jitter series matches the reseeded record (0.05 Hz, σ = 0.2 reads about 0.73×).

## What I re-ran and recomputed

- **`theory.py`** (a copy, in scratch, about 13.5 s). Its `theory_check.json` is byte-identical to the committed one.
- **Same check on `aim1_one_source_shared_seeds.json`**, to see which numbers are stale.
- **`membership_limit.py` and `order_limit.py`.** Every number the page quotes reproduces exactly.
- **Blind A's `invert_cr.fit`** on both records.
- **Git history** for the old seed line.
- **Statistics recomputed from `theory_check.json`** (scripts `an1.py`, `an2.py`, `run_inv.py` in `_scratch/role-01/`).

## Claim ledger

| # | quoted value (location) | cited source | recomputed | verdict |
|---|---|---|---|---|
| 1 | 240 simulated recordings | aim1_one_source.json | 240 rows = 48 cells × 5 seeds | match |
| 2 | check() "about 12 s" (l.30) | theory.py | 13.5 s | match |
| 3 | Predicted participants match measured "within about 0.03 in every cell" at 0.01 Hz (l.37) | theory_check.json | 10 of 72 cells exceed 0.03, worst 0.057. On the first run the worst was 0.086. It holds only for k ≥ 10 (worst 0.037) | **mismatch** |
| 4 | Poisson residual "5–15 %, growing with window and event rate" (l.38) | theory_check.json | Poisson vs exact: 1.2–19.9 % (w = 4 s, 45 events: 16–20 %). Against measured at 0.01 Hz: −5.5 to +25 %. The direction is right | **mismatch (range understated)** |
| 5 | Jitter fit: 0.2/0.5/1.0 → "0.17, 0.48, 1.0 s at both backgrounds"; 0.05 → "about 0.02 s" (l.41–43) | theory_check.json | Reseeded: 0.01 Hz gives 0.17/0.47/0.98; 0.05 Hz gives **0.15**/0.50/**0.94**; 0.05 s gives 0.025 (0.01 Hz) and **0.0074** (0.05 Hz). Usable: 25–29 of 30 at 0.05 Hz. The quoted values are the first run's (0.17/0.47/0.99 and 0.18/0.49/1.01; 0.05 → 0.02) and were not updated after the reseed | **mismatch (stale)** |
| 6 | "floors near the 0.1 s frame" (l.42) | theory.py `jitter_from_windows` | At 0.05 Hz the median of 0.0074 s equals q25, which is the optimiser's lower bound exp(ln 0.01 − 0.3). It is a search-bound artefact, not a frame floor | **mismatch (mechanism)** |
| 7 | Chance + planted cluster rate "within about 10 % at every K and background" (l.45) | theory_check.json | 4 of 12 rows exceed 10 %: 0.01 Hz K6 at +11.1 % and +15.4 %; 0.05 Hz K3/45 events at +11.7 %; K6/15 events at +11.1 %. Also, at 0.01 Hz K = 6 the chance term is 0.00, so those rows test only "every planted event makes one cluster", not the binomial tail | **mismatch** |
| 8 | Chance merging, (1 − q)² (l.44, l.69) | assess.py `_clusters` | merge_bins = 2: a run starts after 2 sub-K bins | match |
| 9 | "Not predicted: 5 cells, 15 events, 0.05 Hz" (l.47) | theory_check.json | 15 events: median deviation 0.24, max 5.6. **45 events, 5 cells, 0.05 Hz are also off**: median 0.08, max 0.21. Lines 52–53 quietly restrict to k ≥ 10 | **partial mismatch** |
| 10 | Exact form within a median 0.011 (worst 0.06) at 0.01 Hz, and 0.016 (worst 0.11) at 0.05 Hz for k ≥ 10 (l.51–53) | theory_check.json | 0.0106 / 0.057 and 0.0161 / 0.106 | match |
| 11 | All quoted medians | aim1_one_source.json | 17 coordination-rate estimates are NaN (3/3/11 by window, all at 0.05 Hz) and 12 assessment K = 6 estimates are NaN. `nanmedian` drops them and the page never says so | **unverifiable / undisclosed** |
| 12 | Old seeds were "1000 + seed in every cell"; the background is drawn first, so five shared backgrounds (l.75–76) | git d93b5c0d; simulate.py l.~770–800 | Both confirmed | match |
| 13 | "at 0.05 Hz the five happened to run low"; the 0.05 Hz rows "now sit on the prediction" | the two theory_check runs | Signed median (measured − exact k), k ≥ 10, 0.05 Hz: −0.040 on the shared-seed run, −0.005 reseeded | match |
| 14 | "each recording now has its own seed" | aim1_one_source.py l.55 | 1000 + 100·idx + seed is unique per recording. The JSON label says `seeding: "per cell"`, which undersells it | match (label imprecise) |
| 15 | Truncated SD 0.74 s (±1.5 s gather; l.83–84) | assess.py (wm = 1.5 × 1 s bin) | Analytic value 0.7426. Gather window confirmed. Attribution to "A and B": no kept file states it | match (value); attribution unverifiable |
| 16 | Noise "from Charlier polynomials (A and B)" (l.79) | blind_a/invert_cr.py; blind_b/theory_cumulant2.py | Charlier appears only in A. B uses the delta method on sample factorial cumulants | **partial mismatch** |
| 17 | ADR-0008 floor 6 at 0.01 Hz and 12 at 0.05 Hz; matches `window_floor` exactly or within one cell (l.85–86) | blind_b/theory_floor.txt | 6/6 and 12/12. Off by one at 0.10 Hz, at N = 100, and with events. Blind A kept no output | match (B); A unverifiable |
| 18 | "a 5-cell event can never pass it at either" | — | Holds only for the event's own cells. Background onsets in the window can lift a 5-cell event to 6 at 0.01 Hz | overstated |
| 19 | Count-detector recall "within about 0.03 in most conditions (B)" | blind_b/theory_count_detector.txt | 20 of 24 within 0.03. The 4 misses are all at 0.05 Hz and high K, max 0.119 (k10 σ1 K9: 0.529 vs 0.648) | match ("most") |
| 20 | Blind A's joint fit: jitter within about 5 % from 0.2 s; participants and rate within a few per cent (l.90–91) | invert_cr.py (its `fresh_cr.json` was not kept) | On the reseeded record σ is 0.97–1.03, k 0.99–1.03, rate 0.96–1.04. On the shared-seed record (what A actually ran on) 0.05 Hz σ reads 1.07–1.13. A's claimed basis cannot be re-run | match on reseeded; source not kept |
| 21 | Residuals: "B saw f3 5–7 % below at 0.05 Hz over 60 seeds"; "A saw rate 3–5 % above" (l.98–99) | blind_b/check_f3.py (output not kept); sim_cumulant_check.txt (40 seeds) | B's kept 40-seed output shows f3 3 %, 19 % (k5, w4), 4.8 % and 5.3 % below. A's rate is 1.03–1.04 on the shared-seed record, which fits | B unverifiable / partly contradicted; A match |
| 22 | Blind table rows "two sources with equal jitter not identifiable — A ✓ (rank), B ✓" and "slow rate change — A ✓" (l.70–71); "this session ✓ (on a second try)" | blind_a/, blind_b/ | No kept file mentions rank, identifiability or slow comodulation | **unverifiable** |
| 23 | Table row "exact cumulants with the at-most-one-event term — A ✓" | blind_a/theory_cr.py l.3 | A's f2 omits the surrogate's (1 − 1/N) factor. B's f3 omits (1 − 1/N²). It is a 3 % term, but "exactly" overstates A | minor mismatch |
| 24 | Membership: 44.5/45.0, 5.30/5.40, 1.94/1.98, 1.03/1.04 (l.125–126) | membership_limit.py | Identical | match |
| 25 | "missed members … shrink the excess by a factor blind pass B derived" (l.127) | blind_b/ | No such derivation. B has only gathered participants ≈ k + (N − k)(1 − e^{−3b}), a participant count, not a membership-excess factor. B predates the membership question | **unverifiable / likely misattributed** |
| 26 | Order checks: τ = 1 0.503/0.500; τ = 2.5 0.747/0.758; no-order bias constant ±0.01 over 25–800 events (l.139, l.141) | order_limit.py | Identical. F·√n̄ ranges 0.370–0.386. The page omits the τ = 0.25 case (0.179 vs 0.156, 15 % off) | match (low-τ case not shown) |
| 27 | M templates: "M = 2: 0.461 against 0.460; M = 64: 0.084 against 0.086" (l.140) | order_limit.py | The formula printed in the table gives 0.459 and **0.081**. The quoted predictions add the no-order bias in quadrature (`np.hypot`, l.71), which the table does not show. At M = 256 the bare formula gives 0.041 against 0.048 measured | **mismatch (formula ≠ quoted number)** |
| 28 | "the indicator and its null bias are closed forms" (l.153) | order_limit.py docstring ("c / sqrt(n_bar)") | 0.375 is fitted from this simulation, not derived. Only the 1/√n̄ scaling is predicted | **mismatch (self-description)** |
| 29 | "fast ρ −0.75", "strongly anti-correlated with spike count", control median 0.10, owner-permutation null (l.145–149) | todo 2026-08-19-…-cost.md l.20, 34, 71 | All present (0.101; −0.75) | match |
| 30 | "That is the August finding … and why the control's median sat at 0.10" | — | Causal link between two different estimators (score sort with known events vs PySpike annealing with adaptive windows). L.154–156 concede the constants differ. This is an inference, not checked | unverifiable |
| 31 | `synfire_scan.py` "anneals each recording several times and then re-anneals every surrogate" | tools/synfire_scan.py l.103–113, 202–205, 261/268 | 3 restarts × (1 + 200 surrogates) | match |
| 32 | PySpike not installed | venv | ModuleNotFoundError | match |
| 33 | "events ≥ 20 s apart"; windows 1, 2, 4 s; two offsets; 20 shift surrogates | aim1_one_source.py MIN_SEP; measure_coordination_rates.py l.98–166 | Confirmed | match |
| 34 | Figure 1 "carries predictions as dashed lines, fitted jitter as its own series" | aim1_figure.py, PNG | Confirmed; the PNG is the reseeded run | match |

**Membership-record check.** For synthetic data the source of record is the planted truth in each row's `true` block. It reconciles: 240 rows, 48 cells × 5. The non-independent units — shared backgrounds — were caught and the run regenerated. I diffed the regeneration against the first run: row count unchanged, `cell` and `seeding` fields added. But the Aim 0 first-result bullets were never re-derived from it (items 3, 5, 7).

## Findings

| location | issue | severity | suggested fix | verifiable against source? |
|---|---|---|---|---|
| l.40–43 (jitter bullet) | The numbers are the first run's. Reseeded at 0.05 Hz, 0.2 → 0.15 and 1.0 → 0.94, not "0.17 … 1.0 at both backgrounds". 0.05 → 0.0074 at 0.05 Hz | high | Quote per background from the current theory_check.json, with usable counts | yes |
| l.42–43 | The "floor near the 0.1 s frame" is the fitter's lower search bound (0.0074 s), not a frame effect | medium | Say the 0.05 s reading pins to the search bound; fix or report it as unresolved | yes |
| l.36–37 | "within about 0.03 in every cell" is false (10 of 72 exceed it, worst 0.057) and contradicts l.51–53 | high | Drop it or replace with "median 0.011, worst 0.06" | yes |
| l.38–39 | Poisson residual is up to 20 %, not 5–15 % | medium | Write "1–20 %" | yes |
| l.44–45 | The chance-cluster claim misses 10 % in 4 of 12 rows (up to 15 %). Its "prediction" assumes each planted event makes one cluster. At 0.01 Hz K = 6 it tests only that assumption | medium | Quote the worst case; say what the planted term assumes; note the blind passes' one-event term D | yes |
| l.47–48 | "Not predicted" names only 15-event cells; 45-event 5-cell cells at 0.05 Hz are also off (up to 0.21) | medium | Say "5-cell events at 0.05 Hz" | yes |
| all medians | 17 NaN coordination-rate estimates and 12 NaN K = 6 assessment estimates are silently dropped | low | State the counts beside the medians | yes |
| l.140 | Formula shown ≠ formula behind the quoted predictions (bias added in quadrature) | medium | Show F = √(F_M² + F_bias²), or quote 0.459 and 0.081 | yes |
| l.141, l.153 | "closed forms" for the null bias: the 0.375 constant is fitted | medium | Call it the scaling 1/√n̄ with an empirical constant | yes |
| l.145–147 | Applying the score-sort bias to explain PySpike's August numbers is an untested inference | medium | Mark it as a hypothesis pending the PySpike comparison | partial |
| l.127 | The membership shrink factor is attributed to blind B; no kept B file contains it | medium | Cite where it is, or remove the attribution | yes (absent) |
| l.70–71, 79, 83–84, 98 | Blind attributions not traceable to kept files: the rank/identifiability and slow-rate rows, Charlier "(A and B)", 0.74 s "(A and B)", B's "5–7 % over 60 seeds". The kept 40-seed output shows 3–19 % | medium | Keep the blind agents' reports and check_f3 output in blind_a/ and blind_b/, or soften to "reported by" | partial |
| l.66 | "exactly" for A: A omits the surrogate's 1/N term | low | Footnote it | yes |
| l.86–87 | "a 5-cell event can never pass it" ignores background cells joining | low | "cannot pass on its own cells" | yes |
| l.139 | Only the good-agreement τ values are shown; τ = 0.25 is 15 % off | low | Add the low-τ row or state the range | yes |
| aim1_one_source.json `seeding` | The label says "per cell"; the seed is per recording | low | Relabel | yes |
