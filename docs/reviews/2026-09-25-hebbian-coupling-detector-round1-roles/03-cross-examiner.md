GRANT 3 ok — Read, Grep, Glob

Role 3, Consistency auditor ("Cross-Examiner"), round 1
Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md

**What I checked:** the proposal line by line against itself; against the goal page's new bullet and its statements on the screen stop, the pre-registration hold, the quiet→busy transfer and recording identity; against the INDEX row, decisions_pending item 2, the jitter-correlogram README, assembly_report.md, the two assembly todos, GLOSSARY, FOUNDATIONS §9 and CLAUDE.md; against clamor's README, CLAIMS.md and malsburg1986.py; and against the code references the proposal names (assess.circular_shift_trains, graph.sttc_matrix, tools/assembly_power.py, tools/check_vendor_freshness.sh, pyproject extras, LICENSE).

**Counting basis:** the one counted population is "recordings", in the Check A/B stop rules ("most recordings"). The proposal quotes no recording counts, so there is no basis drift to reconcile. The count defects are in stages, checks and code lines (below).

Each finding reads: location · issue · severity · suggested fix · verified against a source (yes/no).

**High**

1. **Readout 1 (L99–102) vs `docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md` L92–100.**
   - The todo records why this project dropped the assessor's circular shift as the null for co-participation. It destroys all cross-ROI timing, and these recordings are known to be coordinated. So every recording clears it: "a resounding yes" that only means "these recordings are coordinated".
   - Readout 1 asks "is there learned structure?" against that same null. By the companion's own finding it would come out yes almost everywhere, whether or not there are assemblies.
   - Fix: say readout 1 can only show coordination, not structure beyond it, or give it a null that holds the events fixed. Cite the todo.
   - Verified: yes.

2. **The bound (L47–50, L129–131) vs clamor `malsburg1986.py` L87–97 and CLAIMS.md item 2.**
   - The proposal says a stray episode "cannot move a coupling far" and "one burst of coincidences cannot dominate".
   - clamor's own record says the opposite at the paper's stated q₀ = 0.01. That is 1.04× the half-range (`Q0_OVER_HALF_RANGE`), so one coincident step puts a resting synapse on the clamp.
   - Stage 1 runs q₀ = 0.01 (L92–93), so the property the proposal leans on fails at one of its own sweep points.
   - Fix: state that the protection holds only at the smaller step (q₀/12 and below), and cite CLAIMS item 2.
   - Verified: yes.

3. **"Copy the two functions" (L9–10, L163–165; INDEX row L117) vs clamor `malsburg1986.py` L85–86, L240–248, L277.**
   - `control()` reads clamor's module constants `S0` = 0.012, `S_D` and `Q0`. Its s₀ is fixed, not a parameter.
   - The clamp that actually keeps couplings "within 80 %" is `S_MIN`/`S_MAX` inside `modulate()`, which is not copied.
   - So copying `coactivity()` and `control()` alone does not give the bounded rule the proposal describes, and *s*₀ is not a free symbol as L16 implies.
   - Fix: list the constants and the clamp as part of the copy (or say they are re-implemented), and give *s*₀ = 0.012 from eq 8.
   - Verified: yes.

**Medium**

4. **"Nothing is built" heading vs Check B.**
   - The section heading (L115) says both checks are run "before anything is built", and L117 calls both cheap. But Check B "needs the rule" and runs in stage 1 (L132, L146).
   - The goal-page bullet (unsupervised-learning.md L51–52) repeats the error: "Two cheap checks come first, and either can stop it".
   - Also, Check A's stop does not stop the proposal. It continues if readout 3 beats CoactDetect (L126–127).
   - Fix: retitle as "one check before building, one first thing after". Correct the goal-page bullet in the same change.
   - Verified: yes.

5. **Stage count (L139–153).**
   - The stages are numbered 0, 1, 2, 3, which is already four. The next paragraph then says "A fourth stage waits on data".
   - Fix: "A fifth stage", or renumber from 1.
   - Verified: yes.

6. **Stage 1 (L143–144).**
   - "*D* should stay at *s*₀ within surrogate spread" contradicts L16, which defines *D* = *W* − *s*₀. *D*'s rest value is 0; *W*'s is *s*₀.
   - Fix: "*D* should stay at 0" (or "*W* at *s*₀").
   - Verified: yes, internal.

7. **Kernel section (L68–72) vs "How the code arrives" (L171–173).**
   - L71–72 says the interpolated part "is never exercised". L172 says stage 1 "sweeps *w* against the window, where the interpolated form is exercised".
   - The stage-1 sweep as described (L87–89: *w* at 2, 3 and 4 jitters, with period 2*w* and burst *w*) always stays on the pure-cosine case.
   - Fix: pick one. Either justify the copy by the stamp alone, or name the sweep that leaves the half-period case.
   - Verified: yes, internal, plus clamor L217–226.

8. **Width of the kernel (L80–89).**
   - The zero-sum trapezoid construction needs *w* = *K* whole frames (L82). But *w* is "a multiple of the jitter", and 2 × 0.106 s = 0.212 s, 3 × 0.135 s = 0.405 s, which are not whole frames.
   - `frame_interval_sec` is a per-slice mean (export_folder_spec L613), not exactly 0.1 s.
   - The rounding rule that joins the two is missing.
   - Fix: say *w* is the jitter multiple rounded to whole frames per recording.
   - Verified: yes.

9. **Jitter constants (L85–86) vs the jitter README L4–8.**
   - The README carries a ⚠: it was measured on `2026-09-17_…STEPS_AND_PINS_EXCLUDED`, and "the data have since changed" (Tony, 2026-09-23). It points to `todo/2026-09-23-the-overnight-runs-are-pinned-to-an-export-that-has-changed.md`.
   - The proposal cites 0.106 s and 0.135 s as ruled, with no caveat.
   - Fix: carry the ⚠, or re-measure on the current default before *w* is frozen.
   - Verified: yes.

10. **"Needs no ruling that is still open" (L4–5) vs the goal page and L137.**
    - The goal page (L47) says "nothing is built or run until Tony chooses between a rule written as tested code and stopping the goal".
    - The proposal's own L137 needs Tony to set the stop thresholds before any number is read. Stage 0 (Check A) reads numbers.
    - Fix: say that stage 0 waits on Tony setting the Check A threshold, and state how this route relates to the goal page's hold.
    - Verified: yes.

11. **Reserved word "coactivity" (L14–15; clamor's `coactivity()`) vs GLOSSARY L245–246.**
    - The glossary defines coactivity as "distinct active ROIs per bin/window (one count per ROI)", the quantity CoactDetect counts. Here it names a timing kernel.
    - Fix: call Co "the coincidence kernel" in prose, and note once that clamor's function name is the paper's usage.
    - Verified: yes.

12. **Reserved symbol *K* (L82–84) vs GLOSSARY L128–138, L196–204.**
    - *K* is the coactivity floor, a percentage of ROIs, "defined once". The proposal reuses it for the half-width in frames.
    - Fix: use another letter (e.g. *m*), and add it to the abbreviation line.
    - Verified: yes.

13. **Stage 3 / the penumbra-subtracted store (L153–156) vs CLAUDE.md "The export folder is the input. The store is closed."**
    - The proposal proposes testing whether the distance falloff "survives the penumbra-subtracted store", which is a `.mat` store.
    - Fix: frame it as a producer request for a penumbra-subtracted export folder, in the same ADR-0007 outcome form as the centroid request.
    - Verified: yes.

14. **Stage 1 (L144–145) vs `tools/assembly_power.py` (docstring L22, L99–111) and the 2026-08-18 todo L145–146.**
    - assembly_power plants one assembly into a membership table: "no onsets, no detector". It plants neither overlapping groups nor onset trains.
    - "Planted overlapping groups at the strengths assembly_power already plants" can reuse its strength parameter (fraction of events recruited), not its planting.
    - Fix: say that only the strength grid is reused, and that onset-level, overlapping planting is new code.
    - Verified: yes.

15. **"A stamp is how a later change gets noticed" (L167–168, L173) vs `todo/2026-09-19-the-vendor-freshness-gate-is-advisory-and-nothing-runs-it.md`.**
    - The open todo says nothing invokes `check_vendor_freshness.sh`, and that private upstreams make it answer "undetermined" off-machine. clamor is private (L10).
    - Fix: cite the todo, and say a clamor family needs a local-clone env var like `BUGARACH_DRAUGHTSMAN`.
    - Verified: yes.

**Low**

16. **"Neither is what fails there" (L181–183) vs clamor README L93–95 and CLAIMS items 2–3.**
    - clamor lists eq 8's step size as one of the open questions in the one-step failure: under the E correction it re-locks separated streams. It lists eq 7's row/column choice as changing the outcomes.
    - CLAIMS item 2 does say q₀ cannot cause the *uncorrected* failure.
    - Fix: narrow the claim to that case.
    - Verified: yes.

17. **Units of the jitter (L86).**
    - "Measured cross-ROI jitter" of 0.106 s / 0.135 s is the per-participant σ (README L22–38). The pair-lag spread that *w* is compared against is σ√2, with half-width 0.183 / 0.230 s.
    - Fix: say "per-participant jitter σ", and state which scale *w* is a multiple of.
    - Verified: yes.

18. **"Any other window length breaks it" (L77–78).**
    - For a cosine of period 2*w*, the integral is also zero at whole multiples of *w*, so the claim is overstated.
    - Fix: "any window length other than a multiple of *w*". Or note that the kernel is truncated at *w* by construction.
    - Verified: yes, arithmetic.

19. **Abbreviation line (L13–18).**
    - *s*, *s*_d, *q*(*s*), *K*, *A*(*t*), *E*(*t*) and CoactDetect are used without definition.
    - Eq 8 is written in *s* (clamor's name for the coupling), while every later line uses *W*.
    - *E*(*t*) also collides with clamor's *E*_i(*t*), the E-cell activity.
    - Fix: define them, and write eq 8 in *W* (noting *s* = *W*).
    - Verified: yes.

20. **"Window" overloaded (L26, L59, L77, L101, L172).**
    - It means the baseline window, the kernel's ±*w* span, and "window length". The glossary's "analysis window" is a third meaning (the 60-second cut).
    - Fix: say "coincidence span ±*w*" for the kernel.
    - Verified: yes.

21. **"Burst" for calcium activity (L131 "one burst of coincidences"; L65 "per burst").**
    - Elsewhere the proposal correctly keeps "burst" for the paper's oscillator.
    - Fix: "one episode of coincidences".
    - Verified: yes.

22. **"Refractory floor" (L180) vs GLOSSARY L409–419 and L497–503.**
    - The glossary names refractoriness as a spike-train prior. The project term is the dead time τ, or the observed floor.
    - Fix: "a dead-time floor".
    - Verified: yes.

23. **"Detected events" (L124–125) vs assembly_report L349–351 and GLOSSARY L226.**
    - The membership table is built from the assessor's clusters, not from a detector's calls.
    - Fix: "the participation matrix of the assessor's coordinated clusters".
    - Verified: yes.

24. **Core description (L119–120) vs assembly_report L361–363 and L398–399.**
    - The report flags core–periphery as "an interpretation, not a fitted model" (⚠). Check A is in effect the test the report's recommendation 4 asks for.
    - Fix: carry the ⚠ and say so.
    - Verified: yes.

25. **Stage 2 per-group reporting (L147–148) vs goal page L66 and decisions_pending item 1 L53–54.**
    - Group is perfectly aliased with imaging day in this export, and the proposal does not carry that caveat.
    - The §9 reason quoted is also narrower than stated: §9 L385–387 names opposite-direction effects under TTX, not at baseline.
    - Fix: add the confound caveat, and cite §9's general rule rather than the TTX example.
    - Verified: yes.

26. **Tony's vendoring ruling (L9–11) vs the ADR rule in CLAUDE.md.**
    - The ruling is recorded only in a draft proposal. No ADR exists; a grep for clamor in docs/ finds no adr file.
    - Fix: file an ADR in the PR that first copies the code, or note that it is pending.
    - Verified: yes.

27. **"Sixty lines" (L171) vs clamor L207–248.**
    - `coactivity` plus `control`, docstrings included, is about 42 lines. It is more only if the constants and clamp (finding 3) are counted.
    - Fix: give the number after finding 3 is settled.
    - Verified: yes, approximately.

28. **Goal-page bullet (unsupervised-learning.md L50–51): "copied from syncytium2/clamor".**
    - It reads as done, while the proposal says nothing is built.
    - Fix: "to be copied from".
    - Verified: yes.

29. **Companion defect, for clamor rather than this artifact: clamor README L66–67 vs malsburg1986.py L33–35, L217.**
    - The README calls the single `INTERPOLATED` judgement call "eq 5's time index". The code marks the coactivity stretching as `INTERPOLATED` too.
    - The proposal follows the code, which is correct. Tony should post the fix to clamor.
    - Verified: yes.

**Checked and consistent**

- The INDEX row (L117) matches the proposal, apart from finding 3's incompleteness.
- decisions_pending item 2's values and date match the proposal.
- The quiet→busy transfer is correctly placed under *Waiting on Tony* on the goal page.
- The screen stop is not touched.
- Recording identity is not engaged, since every comparison stays within one recording.
- FOUNDATIONS §9: the baseline-only rule and zero-event ROIs being kept both match.
- Group order is DI, OVX, MALE, ORX.
- "Six coded" detectors matches the glossary.
- The clamor facts check out: the eq 7 kernel at period 2*w* / burst *w* reduces to cos(πΔ*t*/*w*) as `selftest()` pins; q₀ at twelve times smaller; the `update_column` question; the subliminal rule; the stability test reproducing and the one-step amplification not; private repository; BSD-3 on both sides; the licence item is about vendored tooling.
- torch is in both the `dev` and `dl` extras, and `circular_shift_trains` and `sttc_matrix` exist.
- No "fire", no "modality", no singular "data" verb.
- The ±½ end-lag arithmetic is correct: the plain sum is −1 and the trapezoid sum is 0.
