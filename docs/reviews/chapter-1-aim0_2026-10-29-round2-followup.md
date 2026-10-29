# Follow-up pass (round 2, pass 2): Chapter 1 (Aim 0), blob cdc8fbf6

**Artifact reviewed:** the blob `cdc8fbf6afea9df5c496b218e3e5c99fc2a8c881`, committed in ca33ab6a. It was compared with the round-1 blob a3d06b04.

**Findings ruled:** every row of the eleven reports in `docs/reviews/chapter-1-aim0_2026-10-29-roles/`, 192 findings in all. Role 9's item 17 has no severity ("no change required"), so it is listed but not counted.

**Sources used besides the blob:**
- `docs/learned/synthetic_validation/ch1_figure_repairs.md`, the author's log of the figure repairs.
- `git diff 71ff2ab1 ca33ab6a`.
- Three regenerated PNGs, which I viewed: Fig 1.6, Fig 1.7 and Fig 1.9.

**Figure rulings I did not view:** they rely on the repairs log plus the new captions, and are marked "(per repairs log)". The figures are Fig 1.1 D/H, Fig 1.4 F annotation and Fig 1.10.

**How I ruled:**
- **fixed:** the defect named in the issue column is gone. Leftover sub-points from the suggested fix are noted in the evidence.
- **not fixed:** a named sub-defect is still visible, including partial repairs.
- **superseded:** the content was removed under Tony's theory-only ruling, or the claim it qualified was replaced.

## Role 1: Prove It

| finding | sev | ruling | evidence |
|---|---|---|---|
| R1-F1 | blocking | superseded (theory-only; per-group counts declined, ADR-0017) | No "baseline window" claim remains. Order power is now simulated at 1–5 events: "One to three events of 7 cells carry almost no power to detect order" (1.8). |
| R1-F2 | major | fixed | "Taking one sign per setting and pooling both records … 24 of 32 settings … p = 0.007" → general form "18 of 32 … (p = 0.60)". Like for like. |
| R1-F3 | major | fixed | "The median residual falls from 0.032 to 0.020 …; its signed median, the bias, falls from +0.030 to +0.013." |
| R1-F4 | major | fixed | "hard-core form predicts the tool's rate at 1.16 … participants at 0.90, where the tool measures 0.99 and 0.97"; "read jitter 1.62 and 1.43"; λ stated as "0.0099 Hz". |
| R1-F5 | major | fixed | "realistic ones taken from the lab's recordings … no statement in this chapter is about the recordings themselves … the bench's middle participation levels (0.20 and 0.38 of 33)". |
| R1-F6 | major | fixed | About: "Every simulation number is printed by a script listed under *Reproducing* … The one number from a review agent's unkept test is marked". Lim. 4 marks "(not kept)". Spearman and Mariani numbers removed. |
| R1-F7 | minor | fixed | "0.64–0.73 s whatever was planted at K = 3 or 4, and at K = 6 it rose only from a planted 0.5 s (0.43–0.68 s". |
| R1-F8 | minor | superseded | "Matches" became "The prediction is close but not exact … the held-out record has 17 at 0.01 Hz". The omitted P = 0.05 no longer cuts against the claim. |
| R1-F9 | minor | fixed | Conclusion: "predict the coordination-rates tool's participant count to about 1–2 % with a measurable residual bias". The 10+ cell scope appears only in 1.4.4. |
| R1-F10 | minor | fixed | 1.9.3: "The rederivations found the shared-background flaw in the first run". |
| R1-F11 | minor | superseded (theory-only) | The real-gap percentages (1.7 %, 7.5 %, 174 gaps) are gone from the chapter. |
| R1-F12 | minor | fixed | "resolves two events 0.44 s apart at σ = 0.105 s with 7 cells … and 0.59 s apart at σ = 0.131 s with 13 cells"; "between about 0.5 and 2.5 s". |
| R1-F13 | minor | fixed | 1.8: "A jitter of 0.105–0.131 s". |
| R1-F14 | minor | fixed | References now hold Kreuz T (2026), Lee & Wilson (2002) and Luczak et al. (2007). |

## Role 2: DOI or Die

| finding | sev | ruling | evidence |
|---|---|---|---|
| R2-F1 | blocking | fixed | "Sources used for a quantitative or novelty claim were read against that claim …; references marked ⚠ are cited from the repository's earlier reading or were not opened". All seven are ⚠. |
| R2-F2 | major | fixed | "The same group … introduced a direct shift beside annealing for latency correction (Kreuz et al. 2022) and later an extrapolation direct shift for it (Mariani et al. 2025)". |
| R2-F3 | major | fixed | "Kreuz T (2026) … *Biol Cybern* 120:21. ⚠" |
| R2-F4 | major | fixed | "(Diggle 1983 ⚠; Diggle & Gratton 1984, who also fit models that can only be simulated …); the Thomas process's K-function has a closed form used in practice (Waagepetersen 2007)". The wrong Lim. 5 correction is gone. |
| R2-F5 | major | fixed | "by fitting two straight lines to that feature's trajectory"; 1.9.1: "by a two-line change-point fit". |
| R2-F6 | major | fixed | "Fields not searched: point-process counting theory …, hydrology beyond the one rainfall paper, scan statistics". Reimer 2012 ⚠, Rodriguez-Iturbe ⚠ and Ehm 2007 ⚠ are cited. |
| R2-F7 | major | fixed | New rows: "The chance-cluster rate \| known in form … the assessor-specific run-start factor is new" and "How close two events can be \| no prior-art search was made". Residual: Tomlinson 2019, Thurstone and Silva 2015 are still absent. |
| R2-F8 | major | fixed | "Two enquiries would settle more than any search and have not been sent". Residual: the Kreuz correspondence is not cited. |
| R2-F9 | minor | fixed | "averaged over a displacement of up to ±j time steps". |
| R2-F10 | minor | fixed | "only when each pair's two weights sum to one, which unequal co-participation breaks". |
| R2-F11 | minor | fixed | "from ordinary cumulants … The tool itself works with factorial cumulants"; Ehm 2007 is cited. |
| R2-F12 | minor | fixed | "(Kruskal 1958, derived in secs. 3–4)"; 1.9.1: "credits its meaning under the normal to Esscher 1924". |
| R2-F13 | minor | not fixed | The gloss is still inside the page citation: "(Kish 1995, pp. 63–64; it is the intraclass correlation)". Only the Kish 1965 root was added. |
| R2-F14 | minor | fixed | "46:193–212 (to 227 with discussion)". |
| R2-F15 | minor | fixed | "sec. 3.1 of the preprint"; reference: "Read as arXiv 1610.07986". |
| R2-F16 | minor | not fixed | Still "Cecchini … et al." and "Mariani … et al.". Entries with no title remain: Chapin, Kuhn, Peyrache 2009/2010, Schneider, Staude 2008, Kreuz 2022, Wang 2024. Lee & Wilson and Luczak were added. |
| R2-F17 | minor | fixed | The "later convention" claim was dropped: "it is called the Thomas process, although Thomas (1949) gave only the count distribution". |
| R2-F18 | minor | fixed | "with Pavone's imaging group (Cecchini et al. 2021)". |

## Role 3: Cross-Examiner

| finding | sev | ruling | evidence |
|---|---|---|---|
| R3-F1 | blocking | fixed | The real-gap numbers now match `--check-real`: "1.16 … 0.90 … 0.99 and 0.97"; "1.62 and 1.43". |
| R3-F2 | major | fixed | χ² removed. The slow stream is handled: "On a slow-type interval list … both forms predict it". |
| R3-F3 | major | fixed | Per-setting sign test on both forms: 24/32 (p = 0.007) → 18/32 (p = 0.60). |
| R3-F4 | major | fixed | "Measured still sat above predicted in 35 of 48 setting-windows in the first experiment (p = 0.002)". |
| R3-F5 | major | fixed | 1.9.3 credits the shared-background flaw to the rederivations. |
| R3-F6 | major | fixed | Fig 1.7 caption: "Blue lines are derived … The local search's line is fitted". The viewed PNG legend reads "derived exact mean" and "derived asymptote 0.376 / √n̄". |
| R3-F7 | major | fixed | Contribution 6: "its exact mean when no order is present". 1.6.2 separates the lattice convolution from "approaches c/√n̄". Power is "300 recordings per point". |
| R3-F8 | major | fixed | "at K = 3 or 4, and at K = 6 … (0.43–0.68 s; Figure 1.1 H)". |
| R3-F9 | major | fixed | Fig 1.9: "the assessor's half-split point (2.5 s)". The viewed PNG label reads "assessor: half its split plateau at 2.5 s". |
| R3-F10 | major | fixed | "at 0.05 Hz 0.055 (worst 0.38; held-out worst 0.62)". The conclusion is scoped to participants. |
| R3-F11 | minor | not fixed | 1.1 and 1.8 use 0.105–0.131 s, but Next step 2 still reads "Add realistic jitter (σ = 0.1 and 0.15 s)". |
| R3-F12 | minor | fixed | The chapter uses "7 and 13 of 33" throughout. (The goal page, outside this artifact, still says "7–12" at l.29.) |
| R3-F13 | major | fixed | Table 1.1: "an absolute count of cells (not the glossary's percentage K)". |
| R3-F14 | minor | fixed | "spacing" is gone; the text says "intervals between events" and "held at least 20 s apart". (Fig 1.9's on-figure labels still say "fast-stream gap".) |
| R3-F15 | minor | fixed | "joining called bins with at most one uncalled bin between them (its 3 s merge gap)"; "(m + ½) bins, with m = 2". |
| R3-F16 | minor | fixed | "(As a ratio to planted, that share is the same as the fraction of onsets that are coordinated, which is how the figures label it.)" |
| R3-F17 | minor | fixed | "found Kreuz's indicator falling as event counts rose". "Spikes" survives only in Kreuz's column. |
| R3-F18 | major | fixed | The references are added, and the front-matter claim is narrowed with ⚠ markings. |
| R3-F19 | minor | fixed | "and re-plotting Figure 1.1 on dimensionless axes". |
| R3-F20 | minor | fixed | "as the event floor already is" was removed; the event floor is now "a different statistic counted in a 2 s sliding window". |
| R3-F21 | minor | fixed | Caption: "markers are dodged horizontally for visibility" (D/H, per repairs log). |
| R3-F22 | minor | fixed | The Fig 1.9 caption uses "A–C" and "D". The viewed PNG has uppercase letters. |
| R3-F23 | minor | fixed | Fig 1.4 caption: "gray points"; Fig 1.10 caption: "centers". |
| R3-F24 | minor | fixed | "between about 0.5 and 2.5 s", which sits next to the 0.44 and 0.59 s just quoted. |
| R3-F25 | minor | fixed | "π_K is the chance one event reaches K"; "top-m recovery"; "𝔼[max(0, 1 − R_n / w)]"; LBG now "±j". |
| R3-F26 | minor | fixed | "eleven Claude review agents, spawned as general-purpose agents". |

## Role 4: Reviewer 2

| finding | sev | ruling | evidence |
|---|---|---|---|
| R4-F1 | blocking | fixed | 1.4.6: "usable for participants and rate in each recording but not for jitter … 1.06 × planted [0.39, 1.53] … 8 of 40 recordings at the bound"; Limitation 3. |
| R4-F2 | blocking | fixed | Table 1.3 covers 1–5 events and r = 1, 2.5 and 5. "One template at best" is gone. The conclusion reads "at one event no order test has power, and at a few it has little". |
| R4-F3 | major | fixed | "the power of particular tests … so they bound the best achievable separation from above"; † "value is optimistic". |
| R4-F4 | major | fixed | The Fig 1.7 C axis starts near 0.3 and the lines are labeled "derived" (PNG viewed). |
| R4-F5 | major | fixed | Like-for-like tests. The causal "it was the surrogates" is gone. The 35/48, p = 0.002 result is quoted. |
| R4-F6 | major | fixed | 1.3: "So the whole grid was rerun with fresh seeds and every check repeated on that held-out record." |
| R4-F7 | major | fixed | 1.9.3: "Not every result was simulated: the E = Me case …, the latency template …, the many-template order form away from fixed E, and the Palm form … were derived only." |
| R4-F8 | major | fixed | Rate is given at both backgrounds with worst cases, plus "The tool refused in 17 of 720 recording-windows". Residual: the share's worst case and its 0.05 Hz value are not given. |
| R4-F9 | major | fixed | Table 1.2 against the correlogram: "The joint fit is the better estimator from about 0.5 s up, and at the busier background." |
| R4-F10 | major | fixed | "setting medians … within 0.91–1.13 at 0.01 Hz and 0.88–1.12 at 0.05 Hz". Fig 1.11 gives the per-point range of the four ratios. |
| R4-F11 | major | superseded (theory-only) | The "action-potential independent" claim is gone. |
| R4-F12 | major | fixed | "Which of these was already known is set out in *1.9.1*". 1.9.1 lists "scan statistics and the distribution of the normal range … replay". |
| R4-F13 | minor | fixed | "(ADR-0008) … K = 5 and 8 were not simulated, so those values extrapolate … event floor … gives 6 and 12 cells". |
| R4-F14 | minor | fixed | "The 48 setting-windows reuse the same recordings across windows, so these counts overstate the independent evidence." P = 0.05 is superseded by "close but not exact". |
| R4-F15 | minor | not fixed | The criteria are still mixed: the tests at "80 % power" against the tools' point where the split "reaches half its plateau". 0.6 became 0.5. |
| R4-F16 | minor | not fixed | Scaling, the 0.005 s bound, merge and binomial noise are now defined. Still unexplained: the criterion behind "33 of 33 comparisons", how the median SE was computed, and the reasons for the 20 s, ±1.5 s, 80 %/5 % and 5-recording constants. |
| R4-F17 | minor | not fixed | Next step 2 still reads "σ = 0.1 and 0.15 s" against 0.105/0.131 elsewhere. |
| R4-F18 | minor | fixed | "where the tool measures 0.99 and 0.97". |
| R4-F19 | minor | fixed | "re-simulated with the shipped code in a second pass". |
| R4-F20 | minor | fixed | "Only the mean is derived, not the spread, which is what detection depends on." |
| R4-F21 | minor | fixed | "At the busier background the assessor reads a constant jitter; the joint fit tracks the planted value from 0.2 s up." |
| R4-F22 | minor | fixed | "(8 of 60; binomial 95 % interval about 6–25 %)"; "with 200 surrogates per null"; "their common 1–2 % shortfall is one error, not seven". |
| R4-F23 | minor | superseded (theory-only) | The Spearman ρ values are removed. |
| R4-F24 | minor | fixed | "Shah & Wainwright … optimal for top-m recovery from comparisons independent across pairs, whereas lead signs within one event are transitive and so dependent". |

## Role 5: Kill Your Darlings

| finding | sev | ruling | evidence |
|---|---|---|---|
| R5-F1 | major | not fixed | The results are still told about five times: the 1.1 "answer" paragraph, Contributions, 1.9.1, the 1.8 opening ("turns the two failures of Figure 1.1 into consequences of a formula") and the conclusion. The banned preview form persists: "In brief: the closest precedents are …". |
| R5-F2 | major | fixed | The Louis comparison is now given in full only in 1.2.3, with a different point in 1.4.1, the 1.9.1 rows and Fig. 6 once (1.9.2). The 1.3.5 and Next-step repeats are gone. |
| R5-F3 | major | fixed | Exact and asymptote are separated in Contribution 6, 1.6.2 and 1.9.1. |
| R5-F4 | major | fixed | Defined: fast and slow ("two event types, called fast and slow"), hard-core, merge gap, correlogram tool, CoactDetect/LoCo and event floor. Baseline window, August and Aim 1 are gone. Residual: "Palm" and "shipped" are undefined. |
| R5-F5 | major | fixed | "between about 0.5 and 2.5 s", consistent with the 0.44/0.59 s operating points. |
| R5-F6 | minor | not fixed | Next step 2 "σ = 0.1 and 0.15 s" survives. |
| R5-F7 | minor | fixed | "Floor" now means only the event floor. Separation uses "the separation the tests achieve" and "the tools' limit". |
| R5-F8 | minor | not fixed | Unchanged: "The data set only the plateau, π_K²". |
| R5-F9 | minor | not fixed | 1.1 says "It does not replace simulation: it tells simulation where to look" under a 1.8 heading "What the theory replaces, and what it does not". |
| R5-F10 | minor | fixed | "±j time steps"; "top-m". The K-function is glossed as "the pair-count curve across scales". |
| R5-F11 | minor | fixed | "In each, the terms beyond the first are the at-most-one-event term" now says which terms. |
| R5-F12 | minor | **moved** | The old instances are gone: the frame-rounding parenthetical, the one-parameter-fit history, "Reading the prior work sharpened". New process history sits in the 1.6.2 results: "The earlier record's power at 10 and 25 events used a 300-recording null without randomization … it is not quoted here." |
| R5-F13 | minor | fixed | The throat-clearing sentence is gone; 1.9.3 opens "**Against simulation**". |
| R5-F14 | minor | fixed | "wins minus losses (Copeland's rule …)". |
| R5-F15 | minor | fixed | 1.4.3 ties the 1 s window's 0.34–0.42 to k̂. |
| R5-F16 | minor | fixed | "overpredicts participants by about 1 %"; "(SD over 200 recordings)"; χ² gone. Residual: "The score sort sits on it". |
| R5-F17 | minor | fixed | "Sobering" is gone. |

## Role 6: RTFM

| finding | sev | ruling | evidence |
|---|---|---|---|
| R6-F1 | major | fixed | Absolute 0.032 → 0.020, and the signed bias +0.030 → +0.013 is labeled as bias. |
| R6-F2 | major | fixed | Per setting on both forms: "24 of 32 … p = 0.007" → "18 of 32 … p = 0.60". |
| R6-F3 | major | fixed | "F is the Kendall-τ analogue of √W"; "at n̄ = 0.4 the asymptote runs 0.03 high". |
| R6-F4 | major | fixed | "neither applies directly here", with both model mismatches stated. |
| R6-F5 | major | fixed | "Power here is for detecting that order is present, not for recovering how many templates"; E = 1–5 and r = 1/2.5/5 were simulated. |
| R6-F6 | major | fixed | "ordinary cumulants … compound Poisson model with a Poisson carrier and exactly synchronous copies; the multiple-interaction model … is a special case"; 1.4.2 says the forms "relax CuBIC's two assumptions". |
| R6-F7 | major | fixed | "bound the best achievable separation from above … The oracle reaches 0.07–0.2 s"; † for size above 7.5 %. |
| R6-F8 | minor | fixed | 1.2.2 gives each tool's merge rule, "It counts onsets, not distinct cells, and averages over two window offsets". |
| R6-F9 | minor | fixed | "q becomes a Poisson-binomial tail over the per-cell rates; what temporal over-dispersion does to it is not derived". |
| R6-F10 | minor | fixed | The K qualifier was added; the 0.74 s ceiling claim is gone. |
| R6-F11 | minor | fixed | "At 0.01 Hz and K = 6, one cell above the safe threshold". |
| R6-F12 | minor | superseded | The claim became "close but not exact", so the borderline P = 0.05 no longer cuts against it (as R1-F8). |
| R6-F13 | minor | fixed | "a fixed offset drawn from N(0, δ²)". |
| R6-F14 | minor | fixed | The "given distance" wording is gone, matching 1.2.3. |
| R6-F15 | minor | fixed | 1.9.1: "Kreuz et al. 2017 describe the finite-size bias without a formula". |
| R6-F16 | minor | fixed | Kuhn 2003 ⚠ and Staude 2008 ⚠ are marked; the Kreuz 2026 reference is added. |
| R6-F17 | minor | not fixed (now disclosed) | "The fit reports no per-recording uncertainty; a parametric bootstrap would supply one." It is a limitation and next step, not done. |

## Role 7: Reinventing the Wheel

| finding | sev | ruling | evidence |
|---|---|---|---|
| R7-F1 | blocking | fixed | "Against the correlogram tool, run as shipped on the same 240 recordings (Table 1.2)"; the tool is introduced in 1.2.2. |
| R7-F2 | major | fixed | The quoted numbers are now the `--check-real` values. The 1.17/0.89 figures and the χ² are dropped. |
| R7-F3 | minor | fixed | "That part was already in the repository's own field-size and chance-floor tools"; event floor "gives 6 and 12 cells". |
| R7-F4 | minor | not fixed | `split.py` at ca33ab6a still hard-codes `TOOLS = {"assessor": 1.0, "count": 2.0}` and `merge_gap_sec=3.0`. The chapter has no sentence on the separate pair generator. |
| R7-F5 | minor | not fixed | `theory.py` still monkeypatches `sim._place_renewal` (l.429–437). The chapter does not say why the ADR-0010 path is not used. |
| R7-F6 | minor | not fixed | Next step 4, "Compare the order indicator with Kreuz's on the same simulated trains", does not route through `synfire_scan`. |
| R7-F7 | minor | fixed | "It counts onsets, not distinct cells"; "(its 3 s merge gap)". |

## Role 8: You Lost Me

| finding | sev | ruling | evidence |
|---|---|---|---|
| R8-F1 | blocking | fixed | "split into two event types, called fast and slow (DeFazio et al. 2026)". |
| R8-F2 | major | fixed | The provenance note moved to the end ("About this chapter"). The heading is now "**Review.** … eleven Claude review agents". Residual: "were read" stays passive. |
| R8-F3 | major | fixed | "falling as event counts rose". |
| R8-F4 | major | superseded (theory-only) | The KNDy / action-potential sentence is removed. |
| R8-F5 | blocking | fixed | The Contributions are in plain words, e.g. "A closed form for the chance that all of one event's onsets fall in one window when jitter is Gaussian". |
| R8-F6 | major | fixed | New Fig 1.2: "What one recording looks like, and what each tool counts" (raster plus windows). |
| R8-F7 | major | fixed | Fig 1.7 is labeled "derived" (PNG viewed). |
| R8-F8 | major | fixed | The y-axis reads "resolvable separation Δ (s)" (viewed). The caption defines "the separation Δ at which a test calls a pair of events two". |
| R8-F9 | blocking | fixed | "Down-pointing triangles mark tests that resolved every separation tried". The families are explained (blue pooled, red/green identity, gray oracle). "Within-cell minimum interval" replaces g. |
| R8-F10 | major | fixed | Figure and text both say 2.5 s. |
| R8-F11 | major | fixed | Merge rule: "m = 2 because both tools join triggered bins that have at most one untriggered bin between them"; 0.6 replaced. |
| R8-F12 | minor | not fixed | The Fig 1.10 caption still does not explain the sawtooth ripple or what E–H add. The "ADR-0008 floor" label and "centre" were fixed (per repairs log). |
| R8-F13 | minor | not fixed | The caption is fixed ("M = 1 is E/M = 45"; "(dotted and dashed lines)"), but the viewed y-axis still reads "pair-count variance ÷ random" against the caption's "pair co-participation variance". |
| R8-F14 | major | fixed | "The margin-preserving null shuffles which cells join which event while keeping each cell's event count; the uniform null draws …". |
| R8-F15 | major | fixed | `solve()`, `fit_joint(...)`, `check()` and `event_train.py` are gone from the prose; module paths are only in *Reproducing*. |
| R8-F16 | major | not fixed | "Hard-core" is now defined (1.2.1). Still undefined: "Palm" ("Poisson, hard-core, renewal, empirical and Palm trains are implemented") and "the event train's pair correlation". |
| R8-F17 | minor | fixed | "the first experiment"; Aim 1a is gone. |
| R8-F18 | major | fixed | "CoactDetect and LoCo, two of the six ported detectors, which compare each moment with its recent context". The correlogram tool is defined. August and Synfire scan are gone. |
| R8-F19 | major | superseded (theory-only) | "Baseline window" is removed. |
| R8-F20 | minor | fixed | Table 1.3 is a grid (cells per event × events, by r). |
| R8-F21 | minor | fixed | 1.8: "0.105–0.131 s". |
| R8-F22 | minor | not fixed | The dodge note is scoped to "D and H". The A–C/E–G offsets are still unexplained; the repairs log says those panels are unchanged. |
| R8-F23 | minor | not fixed | Still "gray points are the same measurements placed at the prediction for a Poisson event train". The on-figure legend was not touched (repairs log). |
| R8-F24 | minor | fixed | 1.2.3 now has bold topic subheads, and 1.1 names "the closest precedents". |

## Role 9: Show, Don't Tell

| finding | sev | ruling | evidence |
|---|---|---|---|
| R9-F1 | blocking | fixed | Fig 1.1 is in 1.1, Fig 1.2 in 1.2.2 and Fig 1.3 in 1.4.1. |
| R9-F2 | major | fixed | Fig 1.2 is a raster with the tools' windows and bins. |
| R9-F3 | major | fixed | Fig 1.3: "A: … g₂ … g₃ … Gaussian … dashed lines are uniform … B: … k̂/k against jitter over window". |
| R9-F4 | major | not fixed | The real-intervals figure is not embedded; 1.4.5 gives the realistic-interval results as prose numbers. |
| R9-F5 | major | fixed | Fig 1.5: "How many clusters chance alone gives the assessor at each threshold". |
| R9-F6 | major | fixed | Fig 1.8 is a power plot against events. |
| R9-F7 | major | fixed | The four-way Kreuz comparison is now a table. Residual: Coppersmith and Shah & Wainwright are still in 1.6.2. |
| R9-F8 | minor | not fixed | The numeric density moved with the content into 1.4.4–1.4.6, and the held-out numbers add to it, e.g. "On the held-out record they lie within 0.86–1.22 and 0.86–1.36, participants 0.98–1.06 and 0.89–1.16, rate 0.94–1.04 and 0.87–1.45". |
| R9-F9 | minor | not fixed | There is no separation ruler, and Fig 1.10 E–H are still in place. |
| R9-F10 | minor | fixed | Both say 2.5 s. |
| R9-F11 | minor | fixed | Fig 1.7 C says "derived". |
| R9-F12 | major | fixed | Fig 1.11: "Realistic parameter values sit between the tested points". |
| R9-F13 | minor | not fixed (optional) | No graphical abstract was added. |
| R9-F14 | minor | fixed | The Louis paragraph is shortened, and the 1.3.5 repeat is gone. |
| R9-F15 | minor | fixed | The front note moved to "About this chapter" at the end. |
| R9-F16 | minor | not fixed | Fig 1.1 now has an assertion title, but the Fig 1.10 caption still re-lists the conditions ("7 and 13 of 33 cells; jitter 0.105 and 0.5 s; background 0.0096 and 0.05 Hz"). |
| R9-F17 | — | n/a | No finding ("no change required"). |

## Role 10: Ship It

| finding | sev | ruling | evidence |
|---|---|---|---|
| R10-F1 | major | fixed | f₂ and f₃ are now separate indented blocks with a blank line between them. |
| R10-F2 | major | fixed | Fig 1.7 PNG was rebuilt (136187 bytes, against 124729 in round 1); the legend reads "derived exact mean, score sort" (viewed). |
| R10-F3 | major | fixed | The D/H series are dodged (per repairs log), and the caption says so. |
| R10-F4 | major | fixed | Fig 1.9 draws ▼ at the axis floor, with legend entry "resolves at every separation tested … drawn at the axis floor" (viewed). |
| R10-F5 | major | fixed | Fig 1.9's reference labels sit outside the axes to the right of C (viewed). |
| R10-F6 | major | fixed | Figs 1.9/1.10 re-exported at 12 in wide (per repairs log). Fig 1.9's text is legible (viewed). |
| R10-F7 | minor | fixed | The Fig 1.4 F annotation was moved to an empty corner (per repairs log; not viewed). |
| R10-F8 | minor | fixed | "(dotted and dashed lines)" matches the legend (viewed). |
| R10-F9 | minor | not fixed | The Fig 1.1 caption now uses panel letters, but Fig 1.6 still shows "M = 1 (rightmost): uniform null only" (viewed). |
| R10-F10 | minor | fixed | Fig 1.9 uses A–D (viewed). |
| R10-F11 | minor | fixed | "centers" appears in Fig 1.9 (viewed) and in the Fig 1.10 caption. |
| R10-F12 | minor | fixed | 2.5 s is used throughout. |
| R10-F13 | minor | fixed | Fig 1.7's closed-form lines are blue in A–C (viewed). |
| R10-F14 | minor | not fixed | Cited in prose: 1.1, 1.3, 1.8 and 1.11. Cited only in their own captions: 1.2, 1.4, 1.5, 1.6, 1.7, 1.9 and 1.10. |
| R10-F15 | minor | not fixed | Still "g_n(w, σ)", "(k)_r" and "R_n" beside Unicode subscripts. |
| R10-F16 | minor | not fixed | The alt text is still "![Figure 1.x]". The PNG titles "Figure 1"–"Figure 4" were not updated (repairs log), and the renumbering makes the mismatch worse: goal Figure 4 is now chapter Fig 1.7. |

## Role 11: Start With the Problem

| finding | sev | ruling | evidence |
|---|---|---|---|
| R11-F1 | blocking | fixed | 1.1 "What brute force found" shows both failures with Fig 1.1 before any derivation. |
| R11-F2 | blocking | fixed | "The premise of this dissertation is that a recording mixes **two or more sources** … This chapter takes **one source on purpose**." |
| R11-F3 | major | fixed | The blockquote was replaced by the "About this chapter" note at the end. |
| R11-F4 | major | fixed | The Contributions are in plain words; the old/new paragraph is cut to "Which of these was already known is set out in *1.9.1*. In brief …". |
| R11-F5 | major | fixed | "1.3 Methods: the testbed …", then "1.4 … predicted, then tested" and "1.5 … predicted, then tested". |
| R11-F6 | minor | fixed | 1.4.5 "Where the hard-core form fails, and the general form" follows the test in 1.4.4. |
| R11-F7 | major | fixed | "1.6.2 Order: how many events does an order test need?". The Synfire comparison now comes after Table 1.3. |
| R11-F8 | minor | fixed | 1.7 opens on the cost: "counted as one, which lowers the event count and raises the apparent participation". |
| R11-F9 | minor | fixed | Fig 1.9 (tests) comes before the bullets that start with tests; Fig 1.10 (tools) follows. |
| R11-F10 | major | fixed | 1.9.1 "What is old and what is new" opens the Discussion, and 1.2.3 is descriptive. |
| R11-F11 | minor | fixed | Checking is now 1.9.3 inside the Discussion; the held-out protocol is in Methods (1.3). |
| R11-F12 | minor | fixed | The Mariani 9.7 s / 861.8 s timing is removed. |
| R11-F13 | minor | fixed | "Reading the prior work sharpened" is gone; the conclusion ends on "the full count distribution … is the first thing to test". |

## Summary of rulings by round-1 severity

| round-1 severity | total | fixed | not fixed | moved | superseded |
|---|---|---|---|---|---|
| blocking | 12 | 11 | 0 | 0 | 1 (R1-F1, theory-only / ADR-0017 declined) |
| major | 77 | 71 | 3 (R5-F1, R8-F16, R9-F4) | 0 | 3 (R4-F11, R8-F4, R8-F19, all theory-only) |
| minor | 103 | 73 | 25 | 1 (R5-F12) | 4 (R1-F8, R1-F11, R4-F23, R6-F12) |
| **all** | **192** | **155** | **28** | **1** | **8** |

## What this means

- **No round-1 blocking finding is still open.** Eleven are fixed. One (R1-F1) was superseded by Tony's theory-only ruling, which declined the per-group real-data counts (ADR-0017).
- **Three majors are still open:**
  - **R5-F1:** the results are still told about five times, and the "In brief" preview form remains.
  - **R8-F16:** "Palm" and "pair correlation" are still undefined.
  - **R9-F4:** the realistic-interval results are still prose, with no figure.
- **One "moved" defect (R5-F12):** process history inside the results now sits in 1.6.2, lines 560–562 of the blob ("The earlier record's power at 10 and 25 events … is not quoted here").
- **One open minor recurs across three roles:** Next step 2 still says "σ = 0.1 and 0.15 s" (R3-F11, R4-F17, R5-F6).
- **Most remaining minors are figure leftovers:**
  - the Fig 1.10 caption: no ripple explanation, no reason for panels E–H, conditions still listed;
  - Fig 1.6: the y-axis term and "rightmost";
  - the Fig 1.4 legend wording;
  - figures cited only in their own captions;
  - `g_n`-style underscores;
  - alt text and PNG titles.
- **Code-reuse minors left untouched:** R7-F4/F5/F6 (`split.py` settings, the `_place_renewal` monkeypatch, `synfire_scan`).

Nothing was edited.
