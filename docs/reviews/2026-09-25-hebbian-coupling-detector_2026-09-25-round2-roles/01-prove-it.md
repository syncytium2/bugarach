GRANT 1 ok — Read, Grep, Glob, Bash

(SubagentHandback is the hand-off channel, not an editing tool. I hold no Edit, Write or NotebookEdit. A repo hook blocked writing a scratch script through a heredoc, so every recompute below ran as an inline `python3 -c`. Nothing was written to either repo. The only scratch output is the regenerated SVG under `<scratchpad>`.)

## Summary
- **Artifact reviewed:** `docs/proposals/2026-09-25-hebbian-coupling-detector.md` at 5f6a271, with its Figure 1.
- **Figure regenerated:** I reran `tools/make_hebbian_kernel_figure.py`. The regenerated SVG is byte-identical to the committed one, and I opened the committed PNG to confirm it shows the same thing.
- **Figure 1B recomputed independently:** instead of the tool's 400,000-draw Monte Carlo, I integrated the Gaussian-scatter, frame-floored lag distribution exactly. Every printed value matches to 3 decimals.
- **Findings:** 5 high, 5 medium, the rest low.

## Findings (location · issue · severity · suggested fix · verifiable against a source)

1. **Lines 262–265 (the span) · the tool's own numbers refute the argument for the sweep range · HIGH.**
   - The page says a span of two jitters puts about a fifth of coordinated updates on the negative lobe, and so the sweep runs from 3 to 6 frames.
   - But m = 3 is the *worst* span for this. The negative share is 30% fast and 37% slow at m = 3, against 22% and 24% at m = 2.
   - It only drops at m ≥ 4: 10% / 18% at m = 4, and 2% / 7% at m = 6.
   - Two jitters is 0.21 s fast (m = 2) and 0.27 s slow (m ≈ 3), so for slow "two jitters" already means 37%, not a fifth.
   - Fix: restate the rationale from the actual curve (the negative share falls only from m = 4), or start the sweep at 4 and say why m = 3 is kept.
   - Verifiable: yes (the tool's stdout, and my exact recompute).

2. **Line 264 "(Figure 1B)", and caption B's "the expected weight of one update" · the cited figure does not contain the quantity, and the panel is mislabeled · MEDIUM.**
   - Panel B plots only the expected Co. The negative-lobe fraction appears nowhere in the figure; the tool only prints it.
   - Both of the tool's quantities are per coordinated onset *pair*, including pairs further apart than m, which never update.
   - Per actual update the values are:

     | | fast, m = 2 | slow, m = 2 |
     |---|---|---|
     | pairs gated out (never update) | 10% | 20% |
     | expected Co per update | 0.161 (page: 0.144) | 0.104 (page: 0.083) |
     | negative share per update | 25% | 30% |

   - So the line-73 "artifact ≈ seven coordinated pairs" becomes about 6.2 per update. The 0.144 → 7 arithmetic is right only per pair (1/0.144 = 6.9).
   - Fix: relabel the y-axis and the stdout as "per coordinated onset pair", or divide by P(|k| ≤ m). Plot the negative share, or stop citing Figure 1B for it.
   - Verifiable: yes.

3. **Lines 269–271 ("each entry of D records the sign of its first pair of onsets") · false as stated · HIGH.**
   - At q₀ = 0.01, only a Co = +1 update, i.e. a same-frame pair, reaches the clamp from rest (0.022 > 0.0216).
   - With half-weighted ends the most negative Co is −cos(π/m) ≥ −0.866 (m ≤ 6). A negative first update therefore lands at ≥ 0.00334, inside the lower clamp at 0.0024, and the coupling keeps moving.
   - A +0.707 first step lands at 0.01907, also not clamped.
   - So entries lock only at the upper clamp, and only after a same-frame (or cumulative near-lag) coincidence. The conclusion to drop the paper's 0.01 still holds; the stated mechanism does not.
   - Fix: "any pair with a same-frame coincidence locks at the upper clamp and never moves again; negative updates never reach the lower clamp".
   - Verifiable: yes (recomputed).

4. **Line 267 and the ⚠ at lines 74–75 ("m is frozen only after [the jitter] is re-measured on the default dataset") · stale, because the re-measurement already exists · HIGH (a source the page did not consult).**
   - `docs/learned/runs/2026-09-23-jitter-correlogram-senktide-ttx/jitter_correlogram.json` records a re-measurement on `senktide_ttx` (66 recordings): calibrated σ = 0.1048 s fast and 0.1306 s slow.
   - `docs/learned/runs/2026-09-23-jitter-by-group-66/README.md` gives pooled 0.105 / 0.131 s. By group: fast 0.081–0.111 s, slow 0.104–0.152 s, with no significant group difference.
   - Recomputed at the new σ, Figure 1B barely moves: fast m = 2 gives 0.148 with 22% negative; slow m = 3 gives 0.214 with 36% negative.
   - Fix: cite the 2026-09-23 re-measurement, drop or retarget the ⚠, and say the per-group σ spread exists.
   - Verifiable: yes.

5. **Lines 284–293 ("Where the code comes from"; "Both repositories are BSD-3-Clause, under the same GitHub organization") · leaves out that clamor is private · HIGH.**
   - The GitHub API returns `"private": true, "visibility": "private"` for syncytium2/clamor; bugarach is public.
   - clamor's own record says it is private and has an unfinished list of things to settle before it goes public: CLAIMS.md item 0, including the owner's decision on the commit author address; HANDOFF.md also says "Private."
   - Copying `malsburg1986.py` verbatim into public `third_party/` publishes part of a private repo before those decisions are made. It also makes every "clamor's record says" citation on this public page unresolvable for outside readers.
   - The licence holders differ as well: clamor's LICENSE says "Copyright (c) 2026, Tony DeFazio", bugarach's says "Richard DeFazio". BSD-3 requires the copyright notice to travel with the copy; the plan names only a `vendored from` stamp. clamor's own CLAIMS flags exactly this defect: vendored files carrying no licence.
   - Fix: state that clamor is private, make publishing it an explicit ask for Tony, and carry clamor's LICENSE/notice with the vendored copy.
   - Verifiable: yes.

6. **Line 6 (the review record link) · dead link · MEDIUM.**
   - `docs/reviews/2026-09-25-hebbian-coupling-detector_2026-09-25.md` does not exist. `docs/reviews/` has only the `…_2026-09-25-roles/` and `…-round2-roles/` directories. I listed filenames only; I did not open them.
   - Fix: point at an existing record, or create it with the run.
   - Verifiable: yes.

7. **Lines 101–104 (±20 s surrogates "snapped to frames (`graph.jitter_trains`, the null behind the modularity result)") · wrong attribution · MEDIUM.**
   - `graph.jitter_trains` (graph.py:249) moves each onset by a continuous uniform ±jit and wraps it inside the window. It does not snap to frames.
   - Frame snapping exists only in `surrogates.shipped_dither`, which the modularity run does not use.
   - For a frame-grid kernel the snapping matters, so it is new work, not inherited.
   - Fix: "jittered as in `graph.jitter_trains` (continuous), then floored to frames here".
   - Verifiable: yes.

8. **Lines 141–142 ("The only STTC matrices this project has computed used a 2 s tile and were never stored") · slightly false · LOW.**
   - `tests/fixtures/ref_sttc_matlab.json` stores three recordings' 2 s STTC upper triangles (MATLAB reference).
   - Everything else is true: `modularity_vs_null` and `tools/modularity_null.py` default `dt = 2.0`, and the run writes only `meanSTTC` to CSV.
   - Fix: "…never stored beyond a three-recording parity fixture".
   - Verifiable: yes.

9. **Lines 275–277 ("Before the clamp that is exact, not approximate") · overclaim · LOW–MEDIUM.**
   - The mean is exactly zero for independent stationary trains on an unbounded record. With the state-dependent q(s) it is still a martingale: each increment's Co is independent of s and has mean zero.
   - In a finite window, though, the pair count at lag k scales as (T − |k|). The expected update is then r_i·r_j·(−Σ|k|w(k)), with Σ|k|w = −2, −4, −6.83, −10.47, −14.93 for m = 2…6.
   - So there is a small positive bias proportional to the product of the two rates. That is exactly the signature the line-194 rate-neutrality regression tests for.
   - Line 311's list of what breaks neutrality (dead time, slow drift) also names the wrong culprits: independent trains with their own autocorrelation keep a flat cross-intensity. Window edges and *shared* drift are what break it.
   - Fix: "exact up to window-edge terms of order m/T".
   - Verifiable: yes (derived).

10. **Tool docstring lines 18–19 and the `Q0_LIMIT` comment (line 42) in `make_hebbian_kernel_figure.py`; the tool's stdout "overshoot limit q0 < 0.0048" printed beside "one coincidence from rest" · wrong condition · LOW–MEDIUM.**
    - A single step *from rest* overshoots only when q₀ > s₀·s_d = 0.0096. For example, q₀ = 0.006 lands at 0.018.
    - 0.0048 = s₀·s_d/2 is the bound for no step *from anywhere in the band*: maximise x + a(1 − x²) with a = q₀/(s₀·s_d); the maximum exceeds 1 iff a > ½.
    - The page's line 271 states this correctly; the generator contradicts it.
    - Fix the docstring and the comment.
    - Verifiable: yes.

11. **Lines 34–39 (the route "waits on Tony's choice of surrogate") · imprecise · LOW.**
    - The goal page (lines 40–47) says nothing is built until Tony chooses between a rule written as tested code and stopping the goal. The surrogate screen is separately stopped.
    - Fix: quote the actual pending choice.
    - Verifiable: yes.

12. **Lines 313–317 ("the first stability test reproduces and the second does not (its CLAIMS item 5)") · partial citation · LOW.**
    - CLAIMS item 5 covers only the second (single-block) test.
    - The first reproducing is in README.md line 63 and `lit/malsburg-1986-implementation.md` line 247.
    - Fix: cite those two sources.
    - Verifiable: yes.

13. **Lines 230–231 ("the 1981 report was not reachable") · LOW.**
    - True from here: the proxy returned 403.
    - But clamor's `lit/malsburg-1986.md` lists the 1981 report as open access, deposited by the author at the Cogprints archive, "verified live".
    - Fix: say it is open access and was blocked in this environment, not unreachable.
    - Verifiable: yes.

14. **Line 153 ("most pairs … never update and sit tied at 0" as the reason for τ-b on Z) · LOW.**
    - For a pair that never updates in the data *or* in its surrogates, the per-pair standardization gives 0/0: Z is undefined, not 0.
    - Fix: define Z for zero-variance pairs.
    - Verifiable: yes (derived).

15. **Lines 4–5 ("two numbers only Tony sets") versus lines 163–165 · LOW.**
    - "What is asked" lists four values (more than half, 95th percentile, τ-b 0.9, 20 seeds) plus an approval.
    - The first stage needs two of them plus the approval.
    - Fix: align the counts.
    - Verifiable: yes.

16. **Line 11 (Stream: "the fast or slow class") · LOW.**
    - The default export carries three streams, fast, slow and combined (ADR-0008; `2026-09-23-chance-floor-66`).
    - The page's 2-stream scope is a choice and should be stated as one.
    - Verifiable: yes.

## Claim ledger (quoted value · cited source · recomputed value · verdict)

**The kernel and the step (Figure 1 panels A and C, Method detail)**

| Quoted value | Cited source | Recomputed value | Verdict |
|---|---|---|---|
| Lag sum −1 unweighted, 0 with half-weighted ends, for every m | eq. / tool | −1.000 and 0.000 for m = 2…6, analytic and tool | match |
| Co(k) = cos(πk/m) at period 2m, burst m | clamor `coactivity` | inner = outer = πa/m: exact reduction | match |
| clamor's `selftest()` pins the general form to the cosine | clamor | pinned at period 6 / burst 3 only; the reduction holds analytically for any m | match (note: the called function *is* the INTERPOLATED one; it just reduces) |
| Wrap: a pair 2m apart scores as coincidence | clamor line 231, subliminal gate at T + T_a/2 = 2.5m | confirmed | match |
| s₀ = 0.012, s_d = 0.8, q₀ = 0.01, eq. 8 form | clamor lines 79–86, 248 | same | match |
| Clamp 0.2–1.8 s₀ (0.0024–0.0216); `modulate()` clamps | clamor line 277 | same | match |
| One coincidence from rest → 0.0220 | tool | 0.012 + 0.01 = 0.0220 | match |
| q₀ = 0.004 → 0.0160; q₀/12 → 0.01283 | tool | same | match |
| No step from inside the band crosses the clamp when q₀ < s₀·s_d/2 = 0.0048 | page | derived: the bound is a ≤ ½ | match (the tool's docstring is wrong: finding 10) |
| "Each entry of D records the sign of its first pair" | page | false | mismatch (finding 3) |
| p. 35 implies about 0.01/12 | clamor CLAIMS item 2 | "exactly q₀/12" | match |

**The jitter and Figure 1B**

| Quoted value | Cited source | Recomputed value | Verdict |
|---|---|---|---|
| σ = 0.106 s fast, 0.135 s slow | decisions_pending item 2 | same | match (but superseded by the 2026-09-23 re-measurement 0.1048 / 0.1306 s: finding 4) |
| Participant jitter is Gaussian with SD σ (figure's model) | `simulate.py` line 848 `jitter_sec * rng.randn()` | consistent | match |
| Pair lag scatters by σ√2 | jitter-correlogram README | same | match |
| Fast m = 2: 0.144; artifact ≈ 7 pairs | tool | exact 0.144, 1/0.144 = 6.92; per update 0.161 → 6.2 | match per pair; label mismatch (finding 2) |
| Fast m = 2…6: 0.144, 0.313, 0.486, 0.622, 0.718 | tool | exact 0.144, 0.313, 0.486, 0.623, 0.718 | match |
| Slow m = 2…6: 0.084, 0.200, 0.344, 0.482, 0.595 | tool | exact 0.083, 0.200, 0.344, 0.482, 0.595 | match |
| "About a fifth negative at two jitters", hence a 3–6 sweep | tool / Figure 1B | 22–25% fast; slow 37% at m = 3; m = 3 worse than m = 2 | mismatch (findings 1, 2) |

**Data, nulls and project facts**

| Quoted value | Cited source | Recomputed value | Verdict |
|---|---|---|---|
| ±20 s jitter, 200 surrogate draws in the modularity run | graph.py line 297, `modularity_null.py` | same | match |
| Those surrogates "snapped to frames" | `graph.jitter_trains` | not snapped | mismatch (finding 7) |
| STTC only ever at a 2 s tile, never stored | graph / tools | 2 s everywhere; one test fixture stores it | mostly match (finding 8) |
| STTC undefined for ROIs with no onsets | graph.py line 98 | same | match |
| 66 recordings, 36 mice | ADR-0008 line 33; jitter-by-group-66 | same | match |
| About 32 ROIs per recording | `current_export.toml` 2,109 ROIs / 66 | 31.95; median 32 per the chance-floor run | match (note: about 35% of ROIs have no baseline events per FOUNDATIONS §9, so the active count is nearer 21) |
| Group nested in imaging day | goal page line 67; `recording_identity` reviews (84 recordings, 42–48 dates, none with 2 groups) | the default 66 is a subset of the 84 | match (by implication) |
| Six detectors, `detect_folder.DETECTORS` | detect_folder.py line 116 | ("rate", "coact", "loco", "sce", "cicada", "sync") | match |
| `with_microscope`, `effective_region_windows` | code | exist (detect_folder.py line 490, loco.py line 300) | match |
| torch only in the `dl` and `dev` extras | pyproject.toml | same | match |
| Both repositories BSD-3 | both LICENSE files | BSD-3, but different copyright holders, and clamor is private | partial (finding 5) |
| Freshness gate is advisory; draughtsman family read through a local clone | check_vendor_freshness.sh; todo 2026-09-19 | draughtsman clone is *optional* (resolves over gh) | minor mismatch |
| `third_party/draughtsman` precedent | tree | stamped on `__init__.py` | match |
| Export carries no ROI positions | export_folder_spec.md | no position or centroid columns | match |
| Open risk item 1 is modularity's blindness to overlap | todo 2026-08-20 | same | match |
| Curveball null used for membership | assembly_report line 14 | same | match |
| Core–periphery is an interpretation, not a fitted model | assembly_report line 361 | same | match |
| `assembly_power` plants one group with no times; "strength" = fraction of events recruited | assembly_power.py lines 20, 103 | same | match |
| `simulate_coordination` has rate spread, burstiness, dead-time floor, 0.1 s grid | simulate.py lines 434–445 | parameters present | match |
| "Most independent pairs never update" at FOUNDATIONS §9 background rates | derived | at r ≈ 0.01 Hz, span 0.9 s, T ≤ 1800 s: P(any update) ≈ 1 − exp(−r²·T·0.9) ≤ 15% | match |
| Frame about 0.1 s | jitter-correlogram README (onsets on the 0.1 s grid) | no data on this machine | unverifiable directly (plausible) |

**Goal page, clamor record, citations and dates**

| Quoted value | Cited source | Recomputed value | Verdict |
|---|---|---|---|
| Cross-recording negatives taught recording identity in every study that measured it | goal page line 120 | same | match |
| Quiet-to-busy transfer is under "Waiting on Tony" | goal page line 161 | same | match |
| Route waits on Tony's choice of surrogate | goal page | pending choice is rule-as-code vs stopping the goal | imprecise (finding 11) |
| clamor plans a letter to von der Malsburg and shows none | CLAIMS item 6 | "the letter is still to write" | match |
| clamor at c25c7e5 | clamor HEAD | c25c7e5 | match |
| Stability tests (CLAIMS item 5), item 1, item 2 | CLAIMS | item 5 covers only the second test; items 1 and 2 match | partial (finding 12) |
| clamor's open licence item concerns copied tooling | CLAIMS item 0 | vendored families only | match |
| Review record link on line 6 | — | missing | mismatch (finding 6) |
| Bibliographic volumes, pages and DOIs (Ahn, Aicher, Cutts & Eglen, Kempter, Sejnowski, Stark & Abeles, vdM & Schneider) | references list | consistent with my knowledge and clamor's PubMed-checked DOI; not fetched live (role 2's) | match / not fetched |
| "Tony chose a stamped copy, 2026-09-25" | the drafting session | no durable record | unverifiable |

**Source of record for group membership and units:**
- Group membership comes from the export folder's `slices.csv`, read through `bugarach.groups`; the mouse count comes from ADR-0008.
- Withdrawn recordings are the producer's call, already applied. The `senktide_ttx` default carries no contamination note: `dataset.contamination_note` returns None.
- The page names the mouse as the unit of replication. No finding on unit independence or withdrawn units.
- I could not reconcile the unit counts against the folder itself: the export is not present on this machine.

**Paths:**
- `docs/proposals/2026-09-25-hebbian-coupling-detector.md`
- `tools/make_hebbian_kernel_figure.py`
- `docs/learned/runs/2026-09-23-jitter-correlogram-senktide-ttx/jitter_correlogram.json`
- `docs/learned/runs/2026-09-23-jitter-by-group-66/README.md`
- `src/bugarach/graph.py`
- `tests/fixtures/ref_sttc_matlab.json`
- `clamor:clamor/malsburg1986.py`
- `clamor:CLAIMS.md`
- `clamor:HANDOFF.md`
- `clamor:lit/malsburg-1986.md`
