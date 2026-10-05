GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(SubagentHandback is also present; it is only the channel for returning this report. I hold no Edit, Write or NotebookEdit.)

# Role 2: citation and reference check ("DOI or Die"), round 1

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. I read the built file's text, every SVG text node and every `<title>` tooltip, and checked them against the generator.

**Surface:**
- Every named method, document, decision, date, run and number that the page credits to a source outside its own two results folders.
- The page's own statement about where its content comes from.
- Whether any private correspondence appears. None does: the page quotes nobody.

**Short version:** the page has no citations at all. Four internal attributions misstate their source:
- the rehearsal margin, which is the wrong net's number from a run its own README says not to quote;
- who found the fold defect;
- a real-recording number inside a page that says every number is simulated;
- the claim that "nothing on it is typed by hand".

The outside methods are named but never credited, although the project has already settled where each one comes from.

## Findings

Each finding gives its location, the issue, a severity, a suggested fix, and whether I checked it against a source.

**1. Headline "The answer, first" para 3; §6 para 1; §9 "How big a real difference has to be": the "+0.011 lead of the rehearsal run" is misquoted and should not be quoted as it is.**
- **Severity:** HIGH.
- **Checked against a source:** yes.
- **Wrong net.** The primary file is `docs/learned/tuned_vs_coact/shakedown_home_spec/results.json`, on `origin/replicate-run` and `origin/tune-bench-comparison`. Its `comparisons.gated` block gives:
  - chorus_norm minus CoactDetect: +0.0112 (t 2.45)
  - chorus_gain_norm minus CoactDetect: **+0.0160** (t 1.98)
  - By mean F1 (0.728 against chorus_norm's 0.724), chorus_gain_norm was the leading budgeted net. So "the leading net ahead of CoactDetect by +0.011 F1 under the budget" credits chorus_norm's margin to the leader.
- **The secondary sources disagree with the file.** HANDOFF-workstation-tuning.md says "+0.011 ungated and +0.012 gated (t 1.24 and 2.45)", which swaps the labels. The file says ungated +0.0122 (t 1.24) and gated +0.0112 (t 2.45). `tune_learned_vs_coact.py` line 122 and `docs/goals/learned-model-family.md` row 7 repeat "+0.011" with no net named.
- **The source says not to quote it.** The shakedown README: "No readout is planned from it, and nothing should quote it as a comparison."
- **Different simulation.** The rehearsal ran on the retired home spec, with the coded side on three knobs, the old budget and 240 s contexts. The page's between-draw spread (median 0.008, largest 0.027) was measured on the bench, so "sits inside it" compares across two simulations.
- **Fix:**
  - Cite `results.json` directly and name the net: "chorus_norm +0.011; the best budgeted net, chorus_gain_norm, +0.016".
  - Say it was the GPU shakedown on the retired home spec, with three-knob coded detectors and the old budget.
  - Either drop the "sits inside it" comparison, or state that the spread comes from a different simulation.
  - Tell WSMIP064: its handoff's gated/ungated labels are swapped.

**2. §4 warning box: "The rehearsal run found that two outer folds trained the same net" credits the wrong finder.**
- **Severity:** MEDIUM.
- **Checked against a source:** yes.
- **Who found it.** `docs/todo/2026-09-17-two-bake-off-folds-train-the-same-model.md` says the defect was "Found by the fourth blind murderboard of the rigid-shift report (role 1, Prove It), 2026-09-17", and in the bake-off harness (`fold_maker`), not the tuning tool.
- **What the rehearsal did.** It had the defect, and nothing more. The tuning-tool case was recorded when the fix went in (2026-09-18: "In the GPU shakedown at seed 0, held-out folds 3 and 4 both fitted recordings 1000–1009"). The goal page (row 5) says "the tuning tool had it too".
- **Fix:** "A review of an earlier report found that two outer folds could train the same net (link the todo); the rehearsal run turned out to have the same defect: …". The mechanism text (a contiguous run of 10, and 1000–1009) is accurate.

**3. §5 para 2, "shifting a recording by a fraction of a second then lost 30–36% of their calls", against §10 "Simulation only. Every number is on simulated recordings."**
- **Severity:** MEDIUM.
- **Checked against a source:** yes.
- **The number is from real recordings.**
  - Source: `docs/todo/2026-09-07-detector-calls-move-with-the-grid.md`.
  - Recordings: three real TTX baselines from `2026-09-03_revised_2v_long_STEPS_EXCLUDED_TTX` (20240930_65, 20240930_69, 20241002_72).
  - Measured with `tools/probe_shift_invariance.py`.
  - `docs/forks.md` §14 table heading: "on three real TTX baselines".
- **It is a mean over nine shifts.** CoactDetect's worst case kept 0.47 on one recording.
- **Why it matters:** the page states its own provenance, and the statement is false for this number.
- **Fix:** credit it ("measured on three real TTX baseline recordings, docs/forks.md §14"), and change §10 to "every result in the comparison is on simulated recordings".

**4. §11: "This page is built by tools/make_replicate_report.py from those two folders; nothing on it is typed by hand."**
- **Severity:** MEDIUM.
- **Checked against a source:** yes.
- **Some content is typed into the generator by hand.** It lives as literal prose in `tools/make_replicate_report.py` (lines ~778, 870, 895–903, 914, 964, 987–989, 1006, 1025–1037), and each item comes from a different document:
  - +0.011: shakedown results / HANDOFF-workstation-tuning.md
  - 30–36%: todo 2026-09-07
  - 12 ROIs, 4 recordings, 0.03%, "item 3": HANDOFF-slow-comodulation…
  - the 2026-09-17 decisions
  - "6 s apart"
  - "eight fitted constants"
  - the `tiny` history
- **This is how finding 1 got in.** A hand-typed number was presented as computed from the run folders.
- **Fix:** "The results are computed from those two folders; the history in sections 4, 5, 6, 8 and 10 is written by hand and cites its sources." Then add those citations.

**5. §5 para 1, "times 1.6": where the 1.6 comes from is never stated, although the source says to state it.**
- **Severity:** MEDIUM-LOW.
- **Checked against a source:** yes.
- **What the handoff says.** HANDOFF-workstation-tuning.md, *The budget*: "The 1.6 is bench's own ratio of CoactDetect's empty-recording budget to its measured rate (7.0 against 4.4)… the 1.6 was derived from binned CoactDetect's ratio, so say in the readout that it was carried over."
- **Here the reference is sliding CoactDetect**, so the ratio was carried over from the binned version.
- **Fix:** one clause, e.g. "1.6, the bench's own ratio of binned CoactDetect's empty-recording limit to its measured rate (7.0 to 4.4), carried over unchanged to the sliding reference".

**6. §3 "The contestants": none of the six coded detectors' origins is credited, although the project has already settled them.**
- **Severity:** MEDIUM.
- **Checked against a source:** yes, against the project's audit, with two roots web-checked.
- **Tony's ruling.** `docs/detector_history.md` (headers of 2026-08-24 and 2026-08-29) records Tony's ruling to "acknowledge the origins". The app was corrected for the same omission (todo `2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md`). This page is public and written for an outside reader. The settled origins are:
  - **binned SCE:** root is Cossart, Aronov & Yuste 2003, *Nature* 423:283–288 (web-checked). Malvache et al. 2016 is where the project met it, not where it began.
  - **locust:** a modified port of the Cossart lab's CICADA (gitlab.com/cossartlab/cicada). Per `cicada.py` and detector_history §6.3, never describe its numbers as CICADA's. Say "derived from", not "is".
  - **SPIKE-synch:** the SPIKE-synchronization measure is Kreuz and colleagues' (Kreuz, Mulansky & Bozanic 2015, *J Neurophysiol* 113:3432, web-checked; the GLOSSARY says "Kreuz 2015"). The detection layer is this project's.
  - **rate+context, CoactDetect, LoCo:** Tony's designs, which independently rebuilt parts of radar CFAR (constant false-alarm rate) detection. The cell-averaging form goes back to Finn & Johnson 1968, *RCA Review* 29(3):414–464, per detector_history §4. Where greatest-of began is "not established"; do not credit Hansen 1973.
- **Forward trace.** Kreuz's lab later published a detection step on the same profile (Cecchini et al. 2021, *PLoS Comput Biol* 17(5):e1008963, as recorded in detector_history; I did not re-check it). The page makes no novelty claim for SPIKE-synch, so this is information only.
- **Fix:** one sentence after the list, plus a link: "Where each comes from, and what is ours, is in docs/detector_history.md: binned SCE follows Cossart, Aronov & Yuste 2003; locust is a modified port of the Cossart lab's CICADA; SPIKE-synch puts a detection step on Kreuz and colleagues' SPIKE-synchronization (2015); rate+context, CoactDetect and LoCo were designed here and independently resemble radar CFAR detection."

**7. Figure 2 and §3, the chorus models: the code's own credit to prior art is dropped.**
- **Severity:** MEDIUM-LOW.
- **Checked against a source:** yes for Deep Sets. PointNet's metadata was not web-checked.
- **What the code says.** The `src/bugarach/learn/nets/chorus.py` docstring: "This is the standard answer to that, and it is not a new idea — a shared per-element encoder, a symmetric pool, a decoder on the pool is the Deep Sets shape (Zaheer and colleagues, 2017; Qi and colleagues, PointNet, 2017)". The page describes exactly that structure ("an encoder shared by every cell … three pooled views") without the credit.
- **Checked metadata for Deep Sets:** Zaheer, Kottur, Ravanbakhsh, Póczos, Salakhutdinov & Smola, "Deep Sets", *Advances in Neural Information Processing Systems 30* (2017), arXiv:1703.06114.
- **Fix:** add "(the Deep Sets construction, Zaheer et al. 2017)" to the Figure 2 caption. Add PointNet only after its metadata is checked.

**8. §3 and §5: the nulls are called "shuffled"; the code uses circular shifts.**
- **Severity:** MEDIUM-LOW.
- **Checked against a source:** yes.
- **Where on the page:**
  - §3: "shuffled versions of the same recording"
  - §3: "per-frame shuffled threshold"
  - §5: "compute their shuffled baseline exactly"
- **What the code does:**
  - `coact.py`: "rolling rate-local circular-shift null"
  - `sliding.py`: "an exact circular-shift null"
  - `cicada.py`: "circular-shift each cell independently"
  - `sce.py`: `surrogate_model="circular_shift"`
- **Why the word matters.** detector_history §2 records this exact distinction as the named difference between the SCE root and its descendants: "2003 resamples by interval reshuffling, where CICADA, Bocchio 2020, Dard 2022 and `sce_detect` all circular-shift." "Shuffled" names the other method.
- **Fix:** "compared with circularly shifted copies of the same recording (each cell's events rotated in time)", and change the other two phrases the same way.

**9. §5 para 2: "held back for the browser viewer's sake rather than for the values'" gives only one of the two recorded reasons.**
- **Severity:** LOW.
- **Checked against a source:** yes.
- **The recorded reasons.** The `src/bugarach/bench.py` comment on `loco` (and "for the reason on loco above" on `coact`) says the switch waits because it "moves the viewer's calibrated defaults while the browser still runs both detectors binned, **and moves the calls a slow-comodulation analysis is pinned to**". The `CODED_BASE` comment in `tune_learned_vs_coact.py` names both reasons; only the `CODED_BASE_SOURCE` string shortens it to the viewer.
- **Fix:** add "and for an analysis whose results are tied to the binned calls".

**10. §10, first bullet: "where the lab's treatments move the two streams in opposite directions" goes beyond its source.**
- **Severity:** LOW.
- **Checked against a source:** yes.
- **What the source says.** `docs/FOUNDATIONS.md` §9 says this of TTX specifically: coordination under TTX is FAST median 0.46 of baseline, SLOW median 2.50. It defers to `syncytium2/foundations` §15.1b and says treatment effects "are fireflies' and must not be re-derived here".
- **Fix:** "where, under TTX, the two streams move in opposite directions (FOUNDATIONS §9)".

**11. §10 bullet heading: "The bench's fitted numbers come from a folder with a known flaw" gets the provenance wrong.**
- **Severity:** LOW.
- **Checked against a source:** yes.
- **Where the values came from.** `bench.py` `MEASURED_PROVENANCE`/`MEASURED_ROLE`: the values were first taken from a MATLAB summary (`constellation/coordination_timescale_summary.csv`) and shape fits on the closed `.mat` archive. `steps_excluded` is where they were last *checked*.
- **The stored values are not the steps_excluded measurements.** From `docs/learned/bench_measured.json`, all inside their intervals:

  | constant | stored in the bench | measured on steps_excluded |
  |---|---|---|
  | rate shape | 0.275 | 0.269 |
  | burst shape, 300 s | 1.547 | 1.799 |
  | burst shape, 60 s | 1.388 | 1.516 |

- The bullet's body ("last measured on") is right; the heading is not.
- **The rest of the bullet checks out.** Item 3 of HANDOFF-slow-comodulation-on-the-de-pinned-export.md reads "`bench.MEASURED_ROLE` still points at the contaminated folder … 0.03 % of events … Untouched". The handoff gives 83 events of 264,075; 12 ROIs and 4 recordings are confirmed in HANDOFF-workstation-tuning.md.
- **Fix:** "The bench's fitted numbers were last checked on a folder with a known flaw".

## Checked and correct (verified against the source named)

- **Fold defect.** The mechanism (a contiguous run of 10 training recordings; held-out folds 3 and 4, counting from 1, both fitted 1000–1009) matches the todo's 2026-09-18 update.
- **fold_check.** Present in both `meta.json` declarations, with `distinct: true` and a link to the todo.
- **The two declarations** differ in exactly `recording_seeds` and `replicate`. I compared the darkroom `meta.json` files.
- **"--replicate 0 byte for byte / resumable"** matches the tool's comment at line 1226.
- **CoactDetect reference settings** (sliding, 2 s window, 120 s context, α 1e-5, 8 s merge, 1 s guard) equal `CODED_BASE` at 6fe09ab, which is reachable from `origin/main`. `bench.py` credits them to the 2026-09-17 sliding search "under FOUR budgets".
- **Coded grids** come from `bench.FULL_GRIDS` for all six (`hand_grid_source`). `budget_margin` is 1.6.
- **"8 s … checked against crowded recordings … 6 s apart":** `bench.TAIL_RECORDING` sets `min_sep_sec=6.0`. HANDOFF-coded-detectors.md: "Both merge gaps are bracketed: the axis was extended to 16 s and the crowded veto refused it." The page could add that bracket as a stronger statement.
- **Failed-training flag:** the tool's `failed_training_signature` is F1 ≈ 0.125 with threshold ≤ 1e-4.
- **`tiny` "every published run":** the `chorus.py` docstring says it. The todo 2026-08-28 table shows `tiny` at 0.125 with 4 of 4 folds on the floor. I confirmed one run directly; "every" rests on the docstring.
- **Baseline-only and fast-stream-first** are Tony's decisions of 2026-09-17 (goals README decisions 2 and 4; handoff, #621).
- **Re-measurement on the corrected export by both workstations on 2026-09-17**, with participation outside its interval in both folders: HANDOFF-workstation-tuning.md.
- **Background rates 0.0052 and 0.019** match FOUNDATIONS §9's interquartile range.
- **"WSMIP064 writes its own report":** the SESSIONS.md block shows `report/`.
- **`--replicate` on branch `replicate-run`** is at 7a95e8a.
- **No private correspondence** is quoted or paraphrased on the page.

## Literatures searched, and where I stopped

- **Searched** (mostly through the project's own audit, `docs/detector_history.md`, plus web checks):
  - calcium-imaging SCE detection: Cossart 2003 root, web-checked;
  - spike-train synchrony: Kreuz 2015, web-checked;
  - radar CFAR, as recorded;
  - set-function learning: Deep Sets, web-checked.
- **Where I stopped:**
  - I did not follow the SCE line further back than Cossart 2003; the audit says Mao 2001 is credited but "nobody has reached" it.
  - I did not re-read Cecchini 2021 or PointNet.
- **⚠ Not searched:**
  - comparing detectors at a matched false-alarm rate (FROC, Neyman–Pearson operating points), relevant to the "shared budget";
  - nested cross-validation methods;
  - between-draw variance in benchmark comparisons. A likely target is Bouthillier et al. on accounting for variance in ML benchmarks (2021); its metadata is unverified.
  - roots of difference-of-Gaussian kernels and dilated convolutions.
- **Why these are warnings, not blockers:** the page claims no novelty for any of these, so they remain open ⚠ items rather than findings.
- **⚠ Forward trace not done:**
  - CICADA's later applied papers (Bocchio 2020 and Dard 2022 are named in detector_history but were not read);
  - set-based (permutation-invariant) models applied to neural populations.

## Correspondence

I could not ask anyone myself; three questions need a person:
1. **Has anyone told WSMIP064's session** that its handoff swaps the shakedown's gated and ungated margins? Its own report may carry the same error (finding 1).
2. **Does Tony want the rehearsal quoted at all?** Its README says nothing should quote it.
3. **The Kreuz personal communication (April 2026)** in detector_history bears only on SPIKE-synch's detection step, which the page does not claim. It must stay paraphrased and cited, never quoted.

These remain ⚠ ("nobody was asked").

Sources:
- [SPIKY - Scholarpedia](http://www.scholarpedia.org/article/SPIKY)
- [Attractor dynamics of network UP states in the neocortex | Nature](https://www.nature.com/articles/nature01614)
- [Attractor dynamics of network UP states in the neocortex - PubMed](https://pubmed.ncbi.nlm.nih.gov/12748641/?dopt=Abstract)
- [Deep Sets - NeurIPS proceedings](https://proceedings.neurips.cc/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html)
- [[1703.06114] Deep Sets](https://arxiv.org/abs/1703.06114)

Key local paths:
- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py` (the hand-typed prose, lines ~770–1055)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\tools\tune_learned_vs_coact.py` (lines 122, 137, 218–236, 1226, 1581)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\bench.py` (lines 58–90, 523–620, 914, 1575)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\learn\nets\chorus.py` (lines 30–47)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\docs\forks.md` §14
- `<session-scratch>\scratchpad\mb\role02\` (my extracted page text and the shakedown `results.json` copy)
- `git show origin/replicate-run:docs/learned/tuned_vs_coact/shakedown_home_spec/results.json`
