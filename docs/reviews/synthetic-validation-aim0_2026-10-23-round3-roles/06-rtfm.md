GRANT 6 MISMATCH — missing none (WebSearch/WebFetch were deferred and loaded on request); holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, and the Claude Docs, Dropbox and Gmail MCP tools. None of the editing or writing tools was used on the artifact. This is a run finding: the record's `roles:` line should say role 6 ran through the fallback path.

**Grounding.**
- Kreuz et al. 2017 NJP 19:043028 was read in full from the curated library. `--have` found "kreuz 2017 leaders and followers spike-order njp.pdf", so nothing was fetched and nothing was added to `_NEEDED.md`.
- PySpike 0.9.0 (the latest PyPI release) source was downloaded and read. Its pure-Python backend was run without installing it.
- `theory.check()` was rerun with its output in scratch. It is byte-identical to the repo's `theory_check.json`.
- `order_limit.py` and `membership_limit.py` were rerun on copies. Both JSONs are byte-identical to the repo's.
- Scratch is in `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r3-role-06\` (test scripts in `scripts/`, outputs alongside). No tracked file was touched and nothing was written to Dropbox.

## Findings (location · issue · severity · suggested fix · could I verify against a source)

1. **Plan item 1, and the "Against Kreuz" bullet's test** ("`synfire_scan.py` … with and without `max_tau`") · The proposed control cannot work as written. · **High**
   - `tools/synfire_scan.py` has no `max_tau` argument.
   - PySpike's `max_tau` does not cap the coincidence window in released PySpike (0.8.0 and 0.9.0, both backends). It is used only as the neighbour distance for a train's first or last spike: `get_tau` in `cython_get_tau.pyx` and `python_backend.py`.
   - The project already knows this. `docs/FOUNDATIONS.md` §2 records it, and the fix (PySpike PR #89) is still open and unmerged (checked with `gh api`).
   - My test (33 cells, 10 per event, an event every 25 s, no background): `max_tau = 2 s` cut detected coincidences only from 6105 to 5906, against 4500 true within-event pairs.
   - Fix: say the test needs PR #89 (or the patched `get_tau`) plus a new `max_tau` flag in `synfire_scan.py`. Otherwise "with `max_tau`" silently measures the uncapped case.
   - Verified: yes (source code and simulation).

2. **"Participants: predicted closely, not to within noise … 7 and 10 of 48 condition-windows sit beyond 2 SE where about 2 are expected"** (and `theory.summary`, the `0.0455 · n` line) · The null reference is wrong. · **Medium-high**
   - z = (median − prediction) / (1.2533·SD/√5) uses an SD estimated from 5 values with `np.nanstd` (ddof 0).
   - Under a normal null (400k simulations), P(|z| > 2) = 0.117, not 0.0455. So about 5.6 of 48 are expected, not 2.2.
   - Binomial tails: 7 of 48 has p = 0.33, i.e. within noise. 10 of 48 has p = 0.05, marginal. The 48 are also not independent: the same 5 recordings feed three windows.
   - There is better evidence for a small bias. Measured participants sit above the prediction in only 14 of 48 (0.01 Hz) and 17 of 48 (0.05 Hz), with median signed residual −0.006 and −0.005.
   - Fix: replace the 2-SE count with a sign test, or a z threshold calibrated by simulation for n = 5, and correct "about 2 expected".
   - Verified: yes (simulation and `theory_check.json`).

3. **"Not predicted: 5-cell events at 0.05 Hz … (worst ratio 5.6 of planted)"** · 5.6 is the worst residual \|measured − predicted\| (5.608, k at the 2 s window). The worst measured ratio to planted is 6.32 (`summary()`: "5-cell: 0.83–6.32"). · **Medium** · Fix: say "worst residual 5.6" or "up to 6.3× planted". · Verified: yes.

4. **Kreuz table, "coincidences" and "normalization" rows** · The cross-event coincidences are not neutral: they carry the reverse order. · **Medium**
   - A leader's onset in event e+1 is closer to a follower's onset in event e than the other way round. So adaptive windows preferentially pair them in anti-order.
   - PySpike 0.9.0 on the true template order, at r = 2.5, 33 cells, 10 per event, 100 events, no background:
     - all 4500 within-event pairs were detected, with signed sum +3254 (exactly the known-event value);
     - with regular 25 s gaps there were 1605 extra cross-event coincidences (+36 %) with signed sum −735. PySpike's F was 0.157 against F·(k−1)/(N−1) = 0.203 (−23 %);
     - with renewal gaps (20 s + Exp(40 s)) there were +44 % extra coincidences with signed sum −161;
     - with no order planted, the extras only add noise (+47, +98).
   - So "0.28 at 10 of 33 cells" holds only for known-event coincidences. The "+33 %" figure depends on the event spacing.
   - Fix: add that cross-event coincidences also lower F against the planted order, by an amount that depends on how regular the spacing is. Note this as an input to the comparison not yet made.
   - Verified: yes (one seed per setting, pure-Python backend).

5. **Order section and `order_limit.py`: closed form and the lab-scale paragraph** · The order model has no frame grid. On 0.1 s frames, tied onsets get sign 0, both in F (`np.sign`) and in PySpike (multiplicity 2, value 0). At the lab's σ ≈ 0.1 s, many pairs tie. · **Low-medium**
   - My test (true order, δ = σ = 0.1 s): F was 0.435 unrounded and 0.397 rounded to 0.1 s (−9 %).
   - Fix: state the omission, or add `grid` to `simulate()`.
   - Verified: yes (simulation).

6. **"At the lab's scale … score-sort bias about 0.18–0.35"** · The range applies c = 0.38, which was fitted at k = 10, across k = 7–13. The page's own fits show c depends on k (0.26 at k = 5, 0.51 at k = 20 for 33 cells). The low end, n̄ ≈ 1.2, is below the smallest n̄ simulated (2.1). · **Low** · Fix: give c for k = 7 and 13, or widen the range and flag the extrapolation. · Verified: yes (`order_limit` output).

7. **"Untested candidate: the surrogates' shifted copies are not independent of the event train (about 1 % of the pair count)"** · I ran a direct test, and it supports the candidate. · **Low**
   - Setup: event-only recordings from the Aim 1a generator (k = 10, E = 45, min_sep 20 s), 40 recordings per jitter.
   - Surrogate f2 was −0.012 against the modelled −(pk)²/N = −0.0008 at w = 1, and −0.045 against −0.013 at w = 4.
   - Excess f2 sat +0.55 % to +1.1 % above prediction at σ = 0.2. Through k̂ = 2 + f3/f2 and λ̂ = f2/(w·k̂(k̂ − 1)), a 1 % rise in f2 becomes about +3 % in rate. That matches the sign and size of the 0.03 median rate residual.
   - Noise at this run size is comparable, so this is partial.
   - Fix: "partly tested: right sign and size".
   - Verified: yes (simulation).

8. **"Sorting by net wins approximates the best order within a factor of 5 when pair weights are normalized (Coppersmith et al.)"** · The factor 5 bounds the feedback-arc (disagreement) weight, under w(i,j) + w(j,i) = 1. It does not bound F, and it says nothing near no order, where disagreements are about half of all comparisons. · **Low** · Fix: say "within 5× of the fewest disagreements". · Verified: yes (abstract, [ECCC report](https://eccc.weizmann.ac.il/report/2005/131/download), [SODA version](https://cse.buffalo.edu/faculty/atri/papers/algos/fas-soda.pdf)).

9. **`tools/synfire_scan.py` docstring** ("the numpy seed is fixed per recording so a rerun reproduces"), which plan item 1 relies on · The page is right that the annealer uses libc `rand()`. The tool's docstring is wrong: only the relabel surrogates reproduce. Unseeded `rand()` restarts at its default seed in every process, so a rerun reproduces only with the same call order and C runtime. · **Low** · Fix: note this beside plan item 1, or file a todo for the tool. · Verified: yes (`cython_simulated_annealing.pyx`). Also, PySpike's sort needs the Cython build; there is no pure-Python annealer.

10. **Membership, Figure 3 B** · The verdict runs at 200 surrogates per null. The package default is 1000 (`assess_assemblies`). The minimum p of 1/201 still clears α/2 = 0.025, so the verdicts are resolvable, but the run is not at shipped settings. · **Low** · Fix: state "200 surrogates (shipped 1000)". · Verified: yes.

## Checked and clean
- **Derivation:** factorial moments under at most one event per window; the surrogate terms −(pk)²/N and 2(pk)³/N² (from independent per-cell trains, each with at most one onset per window). The Poisson event-train limit is also correct.
- **Window sharing:** g_n = E[max(0, 1 − R/w)]. Frame rounding is exact in expectation for integer windows on the frame grid (`s_eff = σ`). The `excess_cumulants` and `predict_solve` code matches the derivation.
- **Chance clusters:** 60·q(1 − q)² matches `_clusters` (merge if within 2 bins; single-bin clusters always gather K or more within ±1.5 s). Unique-ROI bin counts give p = 1 − e^(−b).
- **Event floor:** reran `bugarach.event_floor.window_floor` (200 draws, 2 seeds each): 6 cells at 0.01 Hz and 12 at 0.05 Hz, stable across both halves of the draws.
- **Numbers:** every Aim 0 number on the page matches `summary()`. The Aim 1a numbers match the record: K = 6 gives 0–0.27; assessor jitter 0.66–0.73 and 0.49–0.67 s; event rate at 1 s jitter 1.67× and 2.11×; the 4 s window 0.68–1.04; share ranges. A 1 s Gaussian truncated at ±1.5 s has SD 0.743 s.
- **Shipped settings:** the tool is benchmarked at its shipped settings (`N_SURR` 20; windows 1, 2, 4 s). The assessor's reduced surrogate count touches only observation-based outputs, as the page states.
- **Order closed forms:** (2/π) arctan r = (2/π) arcsin(δ/√(δ² + σ²)) (Greiner/Kendall). The M-template variance identity (2/π) arcsin(r²/(1 + r²)) holds.
- **Membership:** the 1 + (E − 1)Σp_m² derivation holds, and the Figure 3 curve matches it.
- **Kreuz 2017:** eq. 14 normalisation, giving F·(k − 1)/(N − 1) for known coincidences; sec. 2.5 surrogates, binomial-if-independent; sec. 3.1 finite-size effect; the quote "not sufficient to reliably compare two datasets with widely different number of spike trains and spikes" is verbatim; annealing over neighbour swaps.
- **Glossary:** the jitter entry's 1.67σ half-width ratio is correct.

No literature fetches failed and nothing needs adding to the want-list.
