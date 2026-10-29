GRANT 8 MISMATCH — missing none; holds forbidden tools Edit, Write, NotebookEdit (deferred, loadable), plus Bash, PowerShell, Agent, Artifact, Skill, and the Claude Docs write tools (batch, update). I used only Read, Grep and Glob. The fallback grant is a finding about the run, not about the chapter: the run record's `roles:` line should say that role 8 ran on a fallback path.

# Role 8, "You Lost Me": naive-reader accessibility. Round 3 blind verify, `docs/dissertation/chapter-1-aim0.md`

**What I checked:** the whole chapter (1,135 lines) and all 14 figures, opened as renders. I read each figure before its caption, as a reader from outside this subfield would. I checked three terms against their sources:
- "recording window" against `docs/goals/synthetic-validation.md` (line 359)
- "coordinated share" against `tools/measure_coordination_rates.py`
- "run-start" by grep of the chapter

I did not open any blind-excluded file.

**Verdict as a committee member:** I would sign off once the four major items below are fixed (F1–F4). The blocking rows in the table are blocking under this role's three-undefined-terms rule. Each can be fixed with a gloss or by moving a paragraph. The figures are mostly well built: Fig 1.2 A is a true raster, and Fig 1.3 B uses gridded tiles. I found no false-friend chart idiom.

## Per-section verdict

| unit | terms first used here | defined here? | cold reader follows? |
|---|---|---|---|
| Front note | "the repository's earlier reading" (⚠) | no; "the repository" is never named | yes |
| 1.1 Problem | stream of onsets, source, participation, jitter, membership, latency template | yes | yes |
| 1.1 Brute force, Fig 1.1 | coordination-rates tool, assessor, cluster, K | yes; "coordinated share" is deferred to 1.2.2 | yes |
| 1.1 Question and answer | **cell-by-cell structure, excess variance, reused cell groups, order indicator, fast stream** | no; "fast stream" is defined only in 1.2.1 | **blocking: 5 undefined terms in two sentences (l. 78–84)** |
| 1.1 Contributions | **surrogates, factorial cumulants, run-start factor, pair co-participation, design effect, order indicator, Copeland ranking, stationary event train** | no; "run-start factor" is never defined anywhere (F5) | **blocking** |
| 1.2.1, Table 1.1 | stream, Neyman–Scott, Thomas process, hard-core, **recording window**, "middle participation levels" | mostly yes; "recording window" no (F2) | no |
| Fig 1.2 | windows, bins, gather, threshold | yes; the pale stripes are not explained (F6) | yes, with the misread in F6 |
| 1.2.2 Tools | surrogate, f₂/f₃, coordinated onset rate, cluster, count detector, correlogram, calibration curve | mostly yes; "cross-cell onset correlogram" and "calibration curve" no | yes |
| Fig 1.3 | time-shift surrogate, margin-preserving and uniform nulls, score sort, F | yes; the worked example checks out (+3, +5, −3, −5; F = 0.67) | yes |
| 1.2.3 Prior work | fission probability, dithering, CuBIC, carrier, minimum contrast, K-function, direct shift, latency correction, SPIKE-order | partly; acceptable for a prior-work section | yes, for a specialist |
| 1.3 Methods (first experiment, residual, held-out) | residual, refusal, **frame-rounding term, event-train form** | the last two no | yes |
| 1.3 Realistic values, Fig 1.4 | renewal train, thinning, pair correlation | "pair correlation" not until 1.4.5; the Fig 1.4 title misleads (F3) | yes, with the misread in F3 |
| 1.3 Rederivation | **k̂, at-most-one-event term, per-estimate noise, event floor** | no; all defined later | **blocking** |
| 1.4.1–1.4.3 | k̂, g_n, R_n, factorial cumulants, falling factorial, at-most-one-event term | yes; "the edge" in Louis et al. (l. 382) is not | yes |
| Fig 1.5 | g₂, g₃, σ/w, full prediction | yes; marker color (cells per event) is not in the legend | yes |
| 1.4.4, Figs 1.6–1.7 | standard error of the median, sign test | yes | yes |
| 1.4.5 | pair correlation, general form, empirical train | yes; "empirical" is loose | yes |
| 1.4.6, Fig 1.8, Table 1.2, realistic table | joint fit, bound, in band, pooled as shipped | yes | yes |
| 1.5.1, Fig 1.9 | q, chance-cluster rate, one-per-hour budget, event floor | yes | yes, with the misread in F4 |
| 1.5.2, Table 1.3 | mixture, chance and event clusters | yes | yes |
| 1.6, Figs 1.10–1.11 | likelihood-ratio tests, **g (collides with g_n)**, m, π_K, plateau | yes except the collision (F7); the Fig 1.11 caption omits the 0.05 Hz thresholds (F8) | yes |
| 1.7.1, Fig 1.12 | assembly, perfect readout, reuse, deft², roh, pair co-participation | "pair co-participation" is never defined explicitly | yes |
| 1.7.2, Figs 1.13–1.14, Tables 1.4–1.5 | latency template, δ, r, score sort, local search, n̄, randomized test, **F_M, F₀** (Fig 1.13 legend), **ISI** (Table 1.5) | mostly; F_M, F₀ and ISI no | yes |
| 1.8–1.9 | dimensionless axes | yes; the conclusion misleads (F1) | yes, with the misread in F1 |

## Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| F1 | 1.9, "a window shorter than the jitter undercounts participants" | A reader who follows this line concludes that any window wider than the jitter is safe. That is false. Section 1.4.2 says k̂/k falls below 0.9 once σ passes about w/6, so a window six times the jitter already undercounts. | major | Say "a window less than about six times the jitter undercounts participants". | yes (chapter 1.4.2, Fig 1.5 B) |
| F2 | 1.2.1, "1–8 coordinated events per recording window (medians 1, 2 and 3…)", against 1.5.1 "the 7–16 coordinated events a realistic recording holds" and 1.8.1 "Participants can be read from one recording at 7–16 events" | "Recording window" is never defined. In the source it is the lab's baseline analysis window, not the 45-minute simulated recording. The chapter therefore gives two realistic event counts, 7–16 and a median of 1–3. It uses the larger for the joint-fit conclusion and the smaller for the order-power conclusion, without reconciling them. The 1.1 line "participants can be read from one recording" will be read as applying to a lab recording, where the median window holds 1–3 events and the joint fit was never tested. | major | Define the baseline window and give its duration. State in 1.1 and 1.8.1 which count each conclusion assumes, and that the joint fit was not tested at 1–3 events. | yes (`docs/goals/synthetic-validation.md` l. 359) |
| F3 | Fig 1.4 title, "Realistic parameter values sit between the points the joint fit resolves" | This reads as "surrounded by resolved points, so resolved". In fact both realistic boxes sit beside the unresolved 0.05 s column and below the resolved region: 2 and 16 of 40 recordings are in the band. | major | Retitle, for example: "Realistic values lie below the jitter the joint fit resolves". | yes (figure render; realistic table in 1.4.6) |
| F4 | 1.5.1, "4 at the realistic 0.0096 Hz (0.98 per hour)", Fig 1.9 | Presented flatly, K = 4 reads as a safe threshold. It sits on the budget line: 0.98 per hour against a budget of 1. At 0.01 Hz, 4% higher, the answer is already 5. In Fig 1.9 the two lines are indistinguishable but carry different labels, which confuses a cold reader. Section 1.6 quietly uses 5. | major | Say that K = 4 is on a knife-edge at 0.0096 Hz and recommend 5. Annotate Fig 1.9 to the same effect. | yes (chapter text and figure) |
| F5 | Contributions item 4 and Table 1.6, "the assessor's run-start factor" | The name never appears in 1.5.1, where the factor (1 − q)² is derived. A reader cannot connect a claimed contribution to its derivation. | minor | In 1.5.1, name the (1 − q)² term "the run-start factor". | yes (grep) |
| F6 | Fig 1.2 D (and the 2 s and 4 s rows) | The pale gray alternating stripes mark window extents. They stop at about 11 on the count axis, so they read as gray bars about 11 high. They have no legend entry and are not in the caption. This is phantom structure in the chapter's key explainer figure. | major (readability) | Run the stripes the full axis height or shade them very lightly with no top edge. Add a legend entry: "alternate windows shaded". | yes (render) |
| F7 | 1.6, "That within-cell minimum interval, g" | The symbol g collides with g_n, window sharing, which is the chapter's central function. g is not in Table 1.1. | minor | Rename it, for example g_min or τ_min, and add it to Table 1.1. | yes |
| F8 | Fig 1.11 caption | The caption gives only the assessor's threshold at 0.0096 Hz. Panels B, D, F and H use K = 8 (assessor) and 12 (count detector). Seven-cell events at those thresholds sit near 0, and that is unexplained without reading the footer. The footer's "the count chance first exceeds" is garbled. | minor | Put all four thresholds in the caption, note that k = 7 < 8 and < 12, and rewrite the footer phrase. | yes (render) |
| F9 | 1.1 "Question and answer", l. 78–84 | Blocking under the rule: "cell-by-cell structure", "excess variance", "reused cell groups", "order indicator" and "fast stream" all appear before any definition. | blocking (rule) | Gloss each in a clause, or point to 1.7 and 1.2.1. | yes |
| F10 | 1.1 Contributions | Blocking under the rule: eight or more forward terms, among them "surrogates", "factorial cumulants", "pair co-participation" and "Copeland". | blocking (rule) | Give each item a section pointer and a one-clause gloss. | yes |
| F11 | 1.3 "Rederivation" | Blocking under the rule: k̂, "at-most-one-event term", "per-estimate noise" and "event floor" are all used before their definitions. | blocking (rule) | Move the paragraph to after 1.5, or gloss the terms. | yes |
| F12 | 1.7.2, "The signal falls as 1/√M from √(2/π)·√(…), 0.65 at r = 2.5" | "Falls from 0.65" reads as the M = 1 starting value, which conflicts with the one-template value of 0.753 two bullets earlier. | minor | Write "F ≈ C/√M, with C = … (0.65 at r = 2.5)". | yes |
| F13 | 1.2.1, "which are the simulator's middle participation levels (0.20 and 0.38)" | The grid's levels are 0.15, 0.3 and 0.6 (Table 1.1), so it is unclear what "middle" refers to. | minor | Cut the clause, or name the simulator that has those levels. | yes |
| F14 | Fig 1.2 axis label, 1.2.2 | The axis reads "coordinated share of onsets", but the quantity is a rate per cell, λk/N. The text admits the mismatch. The label invites a reading as a fraction. | minor | Relabel: "coordinated onset rate per cell". Drop the "label it coordinated share" sentence. | yes (tool uses "share" for a value in Hz) |
| F15 | Fig 1.5 B caption, "accounts for the points below the lines at the 4 s window" | The points at small σ/w lie below the lines at the 1 s and 2 s windows too. | minor | "…the points below the lines, most at the 4 s window". | yes (render) |
| F16 | Fig 1.6 legend, "full prediction, 5 cells per event" | The markers are measurements placed at the full prediction, not predictions. | minor | "measured, at full prediction; 5 cells". | yes (render) |
| F17 | Fig 1.7 x-axis | The categories are equally spaced (0.1, 0.125, 0.2, 0.25 …), but the axis reads as a continuous log scale. | minor | Mark it as categorical, or space the points by log σ/w. | yes (render) |
| F18 | Fig 1.4 legend and caption | The legend has a "held-out record only (right half)" state the caption does not mention. | minor | Add it to the caption, or drop it if unused. | yes |
| F19 | Fig 1.8 C labels, "4 of 40 within 18 at bound" | The stacked lines run together as one phrase. | minor | Use a separator: "4 of 40 in band · 18 at bound". | yes |
| F20 | Fig 1.13 legends (F_M, F₀); Table 1.5 ("ISI-adaptive"); Fig 1.10 ("0.4 s in C"); Fig 1.14 (σ = 0.2 s in the footer only) | Notation and settings appear only in figures, undefined in the text. | minor | Define each in the caption. | yes |
| F21 | 1.4.5–1.4.6 and throughout, "the repository" | "The repository" is an internal identifier a committee reader cannot place. | minor | Name it once (bugarach) in 1.2.2. | yes |
| F22 | 1.7.2 frame rounding, "power rises from 0.91 to 0.99" | A reader sees 0.89 for the same cell in Table 1.4. The unrounded 0.91 is at σ = 0.105 s; the table is at σ = 0.2 s. | minor | Say that it is a separate run at σ = 0.105 s. | yes |

**"Taken to mean" checks that passed:** the front note's "No human has reviewed the derivations"; the Rederivation paragraph's "a consistency check, not independent review"; 1.8.4 item 6; and *About this chapter*'s "not a committee and not peer review". All four describe the AI review as work done, not as standing held. I found no inflated titles, roles or credits. Tone is sentence case throughout, with no ALL-CAPS and no list items smuggled into titles. Internal code identifiers appear only under *Reproducing*.
