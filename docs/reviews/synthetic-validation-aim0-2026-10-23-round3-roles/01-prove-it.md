GRANT 1 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs MCP (batch/guide/update) and other deferred MCP tools (Gmail, Dropbox, etc.). I was spawned through the inline general-purpose fallback. I used only Read/Grep/Glob/Bash, and only wrote under `_scratch/r3-role-01/`. No tracked file was touched: `git status` shows only `_scratch/` plus a `docs/reviews/…-round3-roles/` folder that some other session created, which I did not open.

## Role 01 "Prove It": findings
Columns: location · issue · severity · suggested fix · verified against a source (yes/no)

1. **Extract l.115–118 (Participants, "7 and 10 of 48 … where about 2 are expected"), and `theory.summary()` l.294–300** · The expected count is wrong for this statistic. summary() computes z = (median − pred)/(1.2533·SD/√n), with n = 5 and `np.nanstd` (ddof = 0), and then expects 0.0455·48 ≈ 2.2. I simulated that exact statistic on 10⁶ null draws of 5 normals: P(|z|>2) = 0.118, so **about 5.7 of 48** are expected, not 2. On top of that, the three windows reuse the same recordings, so the 48 condition-windows are not independent. So 7 of 48 at 0.01 Hz is consistent with noise, and 10 at 0.05 Hz is only mildly above it. The headline "predicted closely, not to within noise" is not supported at 0.01 Hz. · **high** · Use a calibrated null: a t-like or bootstrap SE for the median at n = 5, or the simulated 11.8 % rate. Restate the result and fix summary()'s "expected". · yes

2. **Extract l.235–237 (lab scale: "bias about 0.18–0.35 … falls below that at about 4 or more templates")** · Two problems.
   - The bias range uses c = 0.38 for every event size, but c was fitted only at 10 of 33 cells. `order_limit.json` c_by_field at 33 cells gives c = 0.26 at k = 5, 0.37 at k = 10 and 0.51 at k = 20. Interpolating for 7–13 cells (n̄ 1.19–4.43, which I confirmed) gives a bias of about 0.20–0.28. The formula is also extrapolated below the smallest n̄ tested (2.13).
   - The crossover claim does not hold. F_M(4) = 0.325 (json) is below the bias only against the 0.35 upper end. Against 0.18–0.28 the crossover is at about M = 6–16.
   · medium · Use the k-matched c, flag the extrapolation, and restate the crossover as a range. · yes

3. **Extract l.131–132 ("worst ratio 5.6 of planted")** · 5.6 (5.608) is the worst *residual* |measured/planted − predicted/planted|, not a ratio. The worst measured ratio for 5-cell events at 0.05 Hz is **6.32** of planted (w 2 s, σ 1 s). · medium · Say "worst residual 5.6", or quote the ratio 6.3. · yes

4. **Extract l.111–113 ("medians exclude them, and so does the prediction")** · The prediction is computed once from the expected cumulants through `solve()`. It cannot exclude the 17 refused recording-windows, so the measured medians carry a selection the prediction does not share. Blind A says the same thing ("the selection that removes them biases the medians"). · low-medium · Delete "and so does the prediction", or state the selection bias. · yes

5. **Extract l.171, *Aim 0, checked by two more sessions* ("chance joiners lift a 5-cell event to 6 about a third of the time at 0.01 Hz and 0.2 s jitter (B)")** · Blind B's REPORT.md has no such claim. B's own `theory_assess.txt` (σ 0.2, k 5, b 0.01, K 6) gives event-added clusters of about 0.12 per event predicted, and 0.13–0.18 observed. The Aim 1a record's condition medians are 0–0.27. None of these is "a third", and the attribution to B has no source. · medium · Requote from B's numbers (about 1 in 8), or drop the attribution. · yes

6. **Extract l.157 (table: blind A "stated, untested" for "two equal-jitter sources inseparable")** · Blind A never states this. Its §5.1 gives the linear multi-source f₂ and calls it "a rank and conditioning question … answered before simulating". Only B states non-identifiability. · medium · Blind A: "implied by its linear form, not stated". · yes

7. **Extract l.259–260 and plan item 1, l.320–322 ("`synfire_scan.py` … with and without `max_tau`")** · `tools/synfire_scan.py` has no `max_tau` option (its argparse lists none). The repository also records `max_tau` as **inert** in released PySpike: FOUNDATIONS §2 l.81, `docs/kreuz_note.md`, and `docs/detector_history.md` l.341–343, which pins it with `test_pyspike_max_tau_is_still_inert`. The fix is only in upstream PR #89. As written, the proposed test cannot discriminate. · medium-high · Say it needs the patched PySpike (or bugarach's own τ) plus a new flag. · yes

8. **Extract l.248 (Kreuz table: PySpike annealing "draws from the C library's `rand()`, so a numpy seed does not fix it")** · This contradicts `tools/synfire_scan.py` l.27–31, which fixes the numpy seed per recording "so a rerun reproduces". The August results rest on that. Nothing in the repo (outside the blind-excluded reviews) supports the `rand()` claim, and PySpike is not installed here, so I could not check it. One of the two documents is wrong. · medium · Cite the PySpike source line, and correct either synfire_scan's docstring or the page. · no

9. **Extract l.61 ("That is the case for setting K per recording (MAHICE, the expert-reviewed threshold)")** · GLOSSARY l.196–204 defines MAHICE's K as one *percentage* per review, "never a different one per slice". At a fixed field size that is a fixed absolute K whatever the background, which is the very failure Aim 1a shows. Setting the threshold per recording from its own null is ADR-0008's event floor (per window), not MAHICE. · medium · Point at ADR-0008's per-window floor, or say MAHICE as defined does not do this. · yes

10. **Extract l.306–307 (Tried and dropped: frame-rounding term "biased the joint fit about 18 % low at 0.05 s")** · I reran the joint fit on the current record with s_eff = √(σ² + dt²/12), for the 10+-cell conditions at 0.05 s. It reads 8 % low at 0.01 Hz and 35 % low at 0.05 Hz. No kept artifact holds "18 %", which is perhaps an average or from the old record. The other half of the claim, "rounding adds nothing in expectation", I confirmed by simulation: g₂ 0.7751 simulated against 0.7744 unrounded and 0.7720 with dt²/12. · low · Give the two figures by background. · yes (partly)

11. **Extract l.56–57 (Aim 1a: "chance alone gives … 7.97 … and 3.86 at K = 4")** · 3.86 is the prediction; the measured value is 3.85 (pooled 3.848), as the page itself says at l.136. · low · Use 3.85, or say "predicted". · yes

12. **Extract l.67–68 ("The 1 s window reads 0.34–0.4 of planted at 1 s jitter (A, E)")** · The range is the per-condition, 10+-cell range at 0.01 Hz. At 0.05 Hz it runs 0.35–0.42. The panels cited, A and E, show pooled values: 0.401 and 0.385. · low · "0.34–0.42 per condition (10+ cells)". · yes

13. **Extract l.126 heading ("Event rate and share … biased one way")** · Only at 0.01 Hz (43 and 41 of 48 above). At 0.05 Hz it is 30 and 29 of 48, about even. · low · Scope the heading to 0.01 Hz. · yes

14. **Extract l.204, and GLOSSARY "latency template" ("a template adds to the jitter, so the two cannot be told apart there")** · This is stated as fact. Plan item 3 lists it as untested, and order_limit/theory never simulate a template through the coordination-rates tool. g₃ for a fixed triple of offsets is not iid-Gaussian, so it holds only on average over random membership. · low · Mark it "derived, untested" in both places. · yes

15. **Extract l.130 ("a reviewer estimated about 1 %") and l.247 ("a reviewer's test … +33 % coincidences")** · Both rest only on murderboard records. No script or output is kept in `learned/` (theory.py and order_limit.py repeat them with no artifact behind them). Under the blindness rule I cannot open those records. · low · Keep the probe scripts beside the claims. · no

16. **Settled row l.291 ("A joint fit … recovers … participants and rate")** · The rate's condition medians go down to 0.73 of planted at 0.05 Hz, a 27 % miss. "Recovers" is strong for that. · low · "rate within 0.73–1.14". · yes

17. **Literature specifics (Coppersmith factor 5; Shah & Wainwright; Mariani 9.7 s vs 861.8 s on 183 trains; Kreuz 2017 eq. 14 and the sec. 3.1 quote; Biol Cybern 2026 still annealing; Grün 1999; Pazienti; Kish)** · Not in any repository source; I did not open the papers. The ⚠ flags on the page are present where it says abstract-only. · info · none · no

**Design / unit-membership record:** the source of record is each row's `true` and `seed` in `aim1_one_source.json`. Seeds are 1000 + 100·condition + seed, so each is unique per recording, and the chance arm uses 910000/950000 + s (also unique). The shared-background flaw is recorded and fixed, and the old record is kept. The blind passes ran on the old record and the page says so. Nothing is withdrawn or excluded except the 17 refusals, which are counted.

## Claim ledger: values that match (all recomputed)
- **Theory output reproduces exactly.** I ran `theory.check()` with HERE redirected to scratch. Its `theory_check.json` is **byte-identical** to the committed one.
- **Other records reproduce exactly.** `membership_limit.py` and `order_limit.py`, rerun from scratch copies, produced JSON **byte-identical** to the committed files.
- **Symbols table:** N 33 · k 5/10/20 · σ · b · E 15/45 · w 1/2/4 · K 3/4/6 · 48 conditions × 5 = 240 · 45 min · events ≥ 20 s apart (MIN_SEP) · 0.33/1 planted per min. All match.
- **Event floor at 33 cells:** 6 at 0.01 Hz, 12 at 0.05 Hz. Recomputed with `event_floor.window_floor` on fresh backgrounds (60 draws, 2 seeds each). Match.
- **Aim 1a values:**
  - K = 6, 5-cell events: 0–0.27 of planted · match
  - assessor jitter at 0.05 Hz (pooled): 0.66–0.73 s at K 3/4, 0.49–0.67 s at K 6 · match
  - truncated-Gaussian SD: 0.7427 · match
  - 4 s window: 0.68–1.04 · match
  - rate at the 1 s window: 1.67× and 2.11× · match
  - share at 2 and 4 s: 0.78–1.11 and 0.67–1.11; 5-cell: 0.09–3.58 · match
- **Participants:** residual 0.007/0.037 and 0.016/0.106; Poisson about 0.05 (0.046, 0.049); 17 of 720 refused, all 5-cell at 0.05 Hz · match
- **Joint fit:**
  - planted 0.2/0.5/1.0 s read 0.219, 0.495, 1.011 s and 0.197, 0.520, 1.011 s · match
  - ranges 0.88–1.13 / 0.94–1.14 / 0.73–1.14 · match
  - planted 0.05 s reads 0.075 and 0.039 s; 1 and 4 fits at the bound · match
  - 5-cell events: 0.10–3.56 of planted · match
- **Rate and share:** 0.032/0.182, 0.055/0.384, 0.017/0.071, 0.024/0.284; 43 and 41 of 48 above · match
- **Chance clusters:** predicted 0.2558/0.0191/0.0001 and 7.973/3.860/0.284; measured 0.2616/0.0196/0 and 7.974/3.848/0.279; all inside the exact 95 % intervals · match
- **Assessor rules (`assess.py`):** merge_bins = 2 means "both preceding bins below K"; gather ±1.5 s; 1 s bins · match
- **Membership:**
  - random rate 3 of 60; 400 / 60 simulations; flagged 100 % for E/M ≥ 1, 83 % at 0.3, 27 % at 0.045 · match
  - M = 1 gives 60 of 60 "uniform-only" · match
  - predicted 1 + (E − 1)/M · match
- **Order:**
  - one template: 0.503 and 0.753; 0.176 vs 0.156; 1.9 % low at r = 5 · match
  - M templates: up to +9.8 % at M = 2–16 · match
  - c 0.38 / 0.50; 0.22–0.51 / 0.31–0.60 · match
  - n̄ 1.19–4.43 · match
  - F_Kreuz factor 9/32 = 0.28 (arithmetic only) · match
- **August todo:** ρ −0.75 / −0.40; control 0.101 (40 recordings) vs 0.036 / 0.099 · match
- **Blind reports:**
  - 1/N and 1/N² drops · match
  - B's window-ratio estimator reads 0.2 s 5–15 % high (1.05–1.15 across both window pairs in its `.txt`) · match
  - count detector within about 0.03 in 20 of 24 (19 strictly) · match
  - floor within one cell · match
  - B's f3 3–19 % low in its 40-seed `.txt` · match
  - A's rate 3–5 % high · match
- **Commit order:** the at-most-one-event term was in d495ab0e (15:40); the blind reports were first committed in bc0a1f80 (15:54); both blind passes branched from c442014a · match
- **GLOSSARY jitter entry:** σ 0.105/0.131 and half-widths 0.186/0.228 match the 2026-09-23 run README; 0.150 s combined matches `bench_combined.py`; 1.67 matches the arithmetic · match
- **Run-record link:** `docs/reviews/synthetic-validation-aim0_2026-10-23.md` exists (checked by path only) · match

Scratch files (only under `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r3-role-01\`): `aim1a.py`, `run_theory.py`, `theory_summary.txt`, `floor.py`, `round.py`, `ml.py`/`ol.py` with their reproduced JSONs.
