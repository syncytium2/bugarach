GRANT 1 ok — Read, Grep, Glob, Bash
(I also hold SubagentHandback, which only returns this report. Instruction blocks for three MCP servers (Claude_Docs, Dropbox, github) arrived mid-run, but none of their tools were given to me, so I hold no editing tool. I wrote nothing to either repo. I tried one heredoc script under the scratchpad, the repo hook blocked it, and all recomputation ran as inline `python3 -c`. There is no torch on this machine, so I ported clamor's `coactivity`/`control` to plain Python line by line from `clamor:clamor/malsburg1986.py` rather than importing them.)

Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md @ b190f02

## Claim ledger (quoted value · cited source · recomputed value · verdict)

| # | Line | Quoted | Source | Recomputed / found | Verdict |
|---|---|---|---|---|---|
| 1 | 36–37 | BiolCybern 54:29–40 (1986), DOI 10.1007/BF00337113 | clamor malsburg1986.py docstring | same | match (against the transcription, not the paper) |
| 2 | 42–45 | Co: +1 coincident, 0 at half overlap, −1 antiphase; exact cosine only for burst = period/2; the general form is INTERPOLATED | `coactivity` docstring | same | match |
| 3 | 47–49 | q(s) = q0(1−((s−s0)/(s0·s_d))²), zero at s0(1±s_d), s_d = 0.8 | `control`, S_D = 0.8 | same | match |
| 4 | 48–50 | "every coupling stays within 80 %", "a stray episode … cannot move a coupling far" | `control` + `modulate` | Only `modulate`'s `.clamp(S_MIN,S_MAX)` enforces the bound. `control()` goes negative outside the band (−0.0050 at 1.1·S_MAX). At the stated q0 = 0.01 and S0 = 0.012, one step from rest reaches 0.022 > S_MAX 0.0216 (and 0.002 < S_MIN 0.0024). | **mismatch** (see F1) |
| 5 | 52 | subliminal rule, paper p. 33 | `modulate` comment quoting p. 33 | same | match |
| 6 | 66 | clamor updates one row per burst; open question `update_column` | `__init__`, `modulate`, CLAIMS item 3 | same | match |
| 7 | 68–71 | period 2w, burst w gives Co = cos(πΔt/w): +1 at 0, 0 at w/2, −1 at w; checked in `selftest()` | port of `coactivity` | 1.0, 0.0, −1.0; 0.587785 = cos(0.3π) at 0.3w (w = 1 and w = 3). selftest pins period 6 / burst 3, one instance of the case. | match |
| 8 | 73–75 | the cosine integrates to zero over \|Δt\| ≤ w | ∫ = (2w/π)·sin(πL/w) | 0 at L = w | match |
| 9 | 77–78 | "Any other window length breaks it"; longer drifts down, shorter drifts up | same integral | Zero also at L = 2w, 3w, …. The sign is right only for w < L < 2w (down) and 0 < L < w (up). | **partial mismatch** (low) |
| 10 | 82–84 | sum over lags −K…K of cos(πk/K) = −1 for every K; half-weighting the end lags gives 0 | direct sum | −1.0 for K = 1…8; +1 correction gives 0.0 | match, but only when w is a whole number of frames (F2) |
| 11 | 80–81 | frame grid about 0.1 s, `frame_interval_sec` in `slices.csv` | export_folder_spec.md §slices.csv; jitter README §Figure 2 | the column exists; README checked onsets on a 0.1 s grid | match for the 2026-09-17 folder; **unverifiable** for the current default (no data on this machine) |
| 12 | 85–86 | jitter 0.106 s fast / 0.135 s slow, ruled 2026-09-22, decisions_pending item 2 | decisions_pending.md L78–84; jitter README table | same values | match (but see F3 on what the number is, and F4 on its folder) |
| 13 | 86 | "one to two frames" | 0.106/0.1, 0.135/0.1 | 1.06 and 1.35 frames | match |
| 14 | 87 | one jitter gives a kernel three lags long | floor(w/0.1 s) = 1 for both streams | lags −1, 0, 1 | match |
| 15 | 89–91 | README warns shared-frame artefacts (motion, light, neuropil) sharpen the zero-lag peak | jitter README "What to be careful about" | same | match |
| 16 | 92–93 | q0: paper's 0.01 against "about twelve times smaller" implied by the figures | CLAIMS item 2; `bursts_to_60pct` | Port with Co = 1: 11 bursts to reach +60 % at q0/12 (10 at q0/11, 12 at q0/13). Paper datum: 11. | match |
| 17 | 101 | `assess.circular_shift_trains` gives per-ROI circular shift | assess.py L340–353 | one uniform offset per ROI, wrapping | match (but the offsets are continuous; F5) |
| 18 | 104–106 | the todo's item 1: modularity cannot see overlapping groups; fix is link communities or mixed membership | todo 2026-08-20 item 1 | same | match |
| 19 | 119–120 | assembly report: "a core with a long tail and no recurring modules" | assembly_report.md L25–26 | "core–periphery … busy core, a long tail" | match; the report itself (L361) says this is an interpretation, not a fitted model |
| 20 | 124–125 | the eigenvalue statistic ran on the participation matrix of detected events, not STTC | assembly.py `stat_eigen` on `membership_matrix`; report L113–114 | yes, the events × ROI membership table | match |
| 21 | 122, 125 | "existing STTC matrices"; "this has not been run" | graph.py, tools/modularity_null.py | STTC matrices are not persisted anywhere, only recomputable, and modularity used dt = 2.0 s (`--dt` default). No eigen-residual analysis of STTC found in src/ or tools/. | "not run": match. "existing": **imprecise** (F9) |
| 22 | 144–145 | "planted overlapping groups at the strengths `tools/assembly_power.py` already plants" | assembly_power.py L19–23, L99–123 | It plants **one** assembly, not overlapping groups, and simulates **membership only**: "Onsets, jitter, background and the detector are … not modelled". Strengths are 0 … 1.0. | **mismatch** (F6) |
| 23 | 147–148 | groups ordered DI, OVX, MALE, ORX; effects run in opposite directions (§9) | CLAUDE.md; FOUNDATIONS §9 "Group-dependence is not optional" | same | match |
| 24 | 153 | the export carries no ROI positions | export_folder_spec.md recording/slices columns | no position or centroid column is specified | match against the spec; unverifiable against folder contents |
| 25 | 158–159 | ADR-0007: a request states the outcome; drafted here, posted by Tony | ADR-0007 Decision 2 and 4 | same | match |
| 26 | 163–165 | line-1 provenance stamp, the convention session_protocol.md and the murderboard copies follow | session_protocol.md L1; tools/murderboard_*.sh/.py | session_protocol stamp is on line 1; the murderboard copies carry theirs on **line 2**, after the shebang | minor mismatch (low) |
| 27 | 166 | both repos BSD-3-Clause under the same owner | both LICENSE files | Both BSD-3. Copyright lines read "Tony DeFazio" (clamor) and "Richard DeFazio" (bugarach). | licence: match. "Same owner": **unverifiable from the files** (low) |
| 28 | 166–167 | clamor's open licence item concerns its vendored tooling, not this model | CLAIMS item 0 | the blocker is vendored murderboard, armory and interface2 files | match |
| 29 | 10 | clamor is private | CLAIMS item 0, "The repository is private" | same | match |
| 30 | 168–169 | torch is in bugarach's `dev` and `dl` extras | pyproject.toml L28, L33–34 | same | match |
| 31 | 171 | "copying sixty lines" | malsburg1986.py L207–249 | 43 lines including blanks (36 non-blank) for both methods, plus the S0/S_D/Q0 constants and `import math` | **mismatch** (low) |
| 32 | 9–11 | Tony chose on 2026-09-25 to take a stamped copy | none | No record anywhere in the tree except this proposal and the goal-page line from the same commit | **unverifiable** attribution |
| 33 | 181–183 | clamor: the stability test reproduces, one-step amplification does not; "neither [eq 7 nor 8] is what fails there" | clamor README L63; CLAIMS items 1, 2, 5 | README's headline agrees. The later CLAIMS record does not: item 1 says the one-step gap closes under the `off_at_tc` reading; item 2 says eq 7–8 at q0 = 0.01 **re-lock** streams the dynamics had separated (6 of 6 seeds) and decide the matrix at onset 2; item 5 says the paper's second stability test does not reproduce. | **mismatch**: a superseded summary (F7) |
| 34 | 150–151 | clamor has only synthetic stimuli; this is the first real data its rule will see | grep of clamor | no real-data use found | match (as far as grep shows) |
| 35 | 4 | "needs no ruling that is still open to start its first stage" | proposal L137; goal page "Waiting on Tony" (exit criterion) | Stage 0 (Check A) has a stop threshold, and L137 says Tony sets thresholds "before any number is read". The goal page lists this route as "not yet ruled on". | **internal contradiction** (F8) |

## Findings

F1 · L47–50, L92–93 · **High** · The bound claim depends on code the proposal does not copy, and fails at the step it proposes to run.
- The 80 % bound comes from the clamp in `modulate()`, not from `control()`. The proposal copies only `coactivity()` and `control()` (L163).
- At q0 = 0.01 with S0 = 0.012, a single coincidence takes a resting coupling past the clamp, where q = 0 and it never moves again. clamor's own constants block says this: "a single coincident burst puts a resting synapse ON the clamp".
- My simulation: independent pairs, Δt uniform over ±w, 2,000 pairs. At q0 = 0.01, 78 % of pairs are pinned at a clamp after 5 updates and 99.9 % after 20. So "a stray episode … cannot move a coupling far" is the reverse of what happens at the paper's stated step.
- Fix: state that the clamp (from `modulate`) must be carried with the copy, and say that at q0 = 0.01 the rule becomes a one-shot sign latch. Verifiable: yes.

F2 · L82–89 · **High** · The half-weighted-ends repair holds only when w is a whole number of frames, and none of the six proposed widths is.
- The sweep widths are 2, 3 and 4 jitters: fast 2.12 / 3.18 / 4.24 frames, slow 2.70 / 4.05 / 5.40 frames.
- Plain grid sums: fast −0.791 / −0.656 / −0.529; slow +0.420 / −0.904 / −0.203. No half-weighting fixes these, and slow at 2 jitters drifts busy pairs **up**.
- The frame interval is also per recording in `slices.csv`, so a width in seconds maps to a different fraction of a frame in each recording.
- Fix: define w as a whole number of frames per recording (K = round(m·σ/Δ)) and say so. Verifiable: yes (recomputed).

F3 · L85–88 · **Medium** · "Cross-ROI jitter" names the wrong quantity for the kernel.
- The README's 0.106 / 0.135 s is σ, each participant's spread around a shared time. Pair lags, which are what Co reads, spread as σ√2. The measured pair-lag half-width at half height is **0.183 s fast / 0.230 s slow**.
- At w = 2 jitters the positive lobe (|Δt| < w/2) is only ±0.106 s fast and ±0.135 s slow, narrower than the measured pair-lag peak. Coordinated pairs at typical lags would then land on the negative lobe.
- Fix: size the kernel against the pair-lag half-width, or state the factor √2. Also mention the README's slow-stream tail out to about 1.5 s. Verifiable: yes.

F4 · L85 · **Medium** · The cited jitter measurement carries a warning the proposal leaves out.
- The README's header: "Measured on `2026-09-17_…STEPS_AND_PINS_EXCLUDED`, and the data have since changed (Tony, 2026-09-23: 'data changed. we'll come back to this.')".
- The measurement used 84 recordings. The current default (`senktide_ttx`) holds 66 of them, byte-identical per current_export.toml, and 18 are gone.
- The value is still the ruled one. But "frozen before stage 2" should say it comes from the superseded folder and point at todo 2026-09-23-the-overnight-runs-are-pinned-to-an-export-that-has-changed. Verifiable: yes.

F5 · L99–101, L107–109 · **Medium** · The null is not on the lattice the kernel is written for.
- `circular_shift_trains` draws `rng.random_sample(n) * win_dur`, continuous offsets. Surrogate onsets leave the 0.1 s grid, so surrogate lags are continuous while real lags are whole frames.
- The trapezoid weighting is undefined off-grid, and the variance of D (and the per-frame score E(t) thresholds) will differ between real data and null for a reason unrelated to coordination.
- Fix: shift by whole frames, or snap the shifted onsets back to the grid. Verifiable: yes (code).

F6 · L144–145 · **Medium** · `tools/assembly_power.py` does not plant overlapping groups and has no onset times.
- It plants one non-overlapping assembly in an events × ROI membership table, and its docstring says onsets and jitter are not modelled. The rule needs timing, so it cannot run on that output.
- Only the strength grid (0 … 1.0) and the geometry can be borrowed. The overlapping-group, timed generator is new work.
- The assembly report's "What should happen next" item 2 ("Do not plant assemblies in the generator") is also relevant; a stage-1-only simulator avoids it, but that should be said. Verifiable: yes.

F7 · L181–183 · **Medium** · The disclaimer quotes clamor's README headline, which clamor's later record revises.
- CLAIMS item 1: the one-step gap closes under one reading of Fig. 4.
- CLAIMS item 2: equations 7–8 at q0 = 0.01 re-lock separated streams in 6 of 6 seeds (1 of 6 separates at q0/12), and decide the matrix at onset 2.
- CLAIMS item 5: the second stability test (the single block, p. 36) does not reproduce.
- So "neither [equation 7 nor 8] is what fails there" is contradicted by clamor's own current record: the step size in equation 8 is implicated. Fix: cite CLAIMS items 1, 2 and 5, and drop "neither is what fails". Verifiable: yes.

F8 · L4 against L137 · **Medium** · "Needs no ruling that is still open to start its first stage" conflicts with "stop thresholds are … for Tony to set … before any number is read". Stage 0 has a stop threshold. The goal page also lists the route as "not yet ruled on". Fix: say the first stage waits on Tony setting Check A's threshold. Verifiable: yes (internal).

F9 · L122 · **Low** · "The existing STTC matrices" are not stored anywhere; they would be recomputed. The only prior STTC run used dt = 2.0 s (`modularity_null.py --dt`) with ±20 s jitter surrogates, not circular shift. Fix: name the dt for Check A. Verifiable: yes.

F10 · L73–79, L178–180 · **Medium** · "Rate-neutral" holds for the mean of D only.
- In my bounded random-walk simulation, mean D/half-range stays about 0 (|mean| ≤ 0.053). RMS |D| grows with the number of pair updates: at q0/12 it is 0.135 after 5 updates, 0.26 after 20, 0.53 after 100 and 0.87 after 500.
- So the Frobenius norm and the spread of D grow with the rates, "however busy either ROI is" notwithstanding. The circular-shift null, which keeps rates, is what absorbs this, and the text should say so.
- Scale check (derived, not measured): at the §9 fast background rates on about 1,800 s windows (9–30 events per ROI) with w ≈ 0.3 s, the expected chance updates per independent pair are 0.03–0.30. Most pairs would get no update and sit at D = 0 exactly. That makes Check B's rank correlation tie-dominated. Verifiable: yes (simulated and derived).

F11 · L62–64 · **Low** · Double counting is ambiguous. "On each onset of ROI i … every onset of every other ROI j … contributes one update to W_ij and W_ji". Looping over all i visits each onset pair twice, which doubles the effective q0; with the bound, update order matters. Fix: specify one update per unordered onset pair. Verifiable: yes (text).

F12 · Check A/B (L122–135) against L53–54 · **Low–Medium** (missing values) · STTC returns NaN when either train is empty (graph.py L97–107), and §9 puts about 35 % of ROIs with no events in a baseline window. D gives those ROIs exact zeros. The comparison must drop them from STTC while §9 forbids dropping them from D's readouts. The proposal should say how both checks handle them. Verifiable: yes.

F13 · Stage 2 (L147–148), design-record check · **Medium** · The per-group plan ignores two parts of the design record.
- Per-group reporting follows §9. But the default is 66 recordings from 36 mice (ADR-0008 L33), so recordings from one mouse are not independent (`subject_id`, export spec rev 4).
- The goal page also records that group is perfectly confounded with imaging day (checked on the 84-recording folder).
- Neither appears. Fix: count mice, not recordings, and state the day confound. Withdrawn recordings: the producer applies these, and none are at issue. Verifiable: yes.

F14 · L9–11 · **Low** · The attribution of Tony's 2026-09-25 choice has no record in the tree. Unverifiable. If it was said in conversation, record it where it can be checked (the goal page or an ADR). Verifiable: no.

F15 · L77, L171, L163, L166 · **Low**:
- "Any other window length breaks it" is false at 2w, 3w, …; say "any window shorter than w or between w and 2w".
- "Sixty lines" is 43, plus the constants.
- "Line-1 stamp" is line 2 in the murderboard copies.
- "Same owner" against copyright lines "Tony DeFazio" / "Richard DeFazio". Probably one person, but not checkable from the files.

Also noted, not a finding for this role: the interpolated kernel is not rate-neutral off the exact point. Burst 0.5 or 1.5 on period 2 gives a mean of −0.318 or +0.318 over the period. So L172's "sweep w against the window, where the interpolated form is exercised" would break the rate-neutrality the proposal relies on, beyond the internal contradiction with L72.

## What I checked
Every number, citation, attribution and "X does Y" statement in the artifact, against:
- clamor: malsburg1986.py (constants, `coactivity`, `control`, `modulate`, `selftest`, `bursts_to_60pct`), CLAIMS.md items 0–5, README, LICENSE, lit/malsburg-1986-implementation.md.
- bugarach: goals/unsupervised-learning.md, decisions_pending.md item 2, the jitter-correlogram README, graph.py, assess.py, assembly.py, assembly_report.md, the overturn todo, tools/assembly_power.py, tools/modularity_null.py, export_folder_spec.md, current_export.toml, pyproject.toml, FOUNDATIONS §9, ADR-0007, ADR-0008, the vendor stamps and tools/check_vendor_freshness.sh.

Mathematical claims were recomputed: the continuous integral, the discrete sums for K = 1–8, the kernel at the six proposed widths, the q0/12 inversion and a bounded random walk. No real recordings are on this machine, so frame-interval and ROI-position claims about the current folder are checked against the spec only.
