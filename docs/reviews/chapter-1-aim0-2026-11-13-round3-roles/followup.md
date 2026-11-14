## Murderboard PASS 2 (follow-up): chapter-1-aim0.md, round-3 findings checked against blob 2bd1467d

**Scope.** I read all eleven round-3 role reports and every hunk of `git -C <repo> diff f8e4d8c0 7f5ffc67`. That diff covers the chapter plus a 6-line docstring change in `ch1_intro_figures.py`; no PNG changed. I checked the changed text against:
- `ch1_intro_figures.log` and the chapter's Table 1.5;
- `bench.py` (lines 1056–1066) and `bench_slow.py` (lines 205–210);
- `generator.md` (lines 405–414) and `runs/2026-09-25-real-intervals/README.md`;
- `ch1_followups/README.md` (the window_counts tables), the rendered Figure 1.16 PNG;
- the 01-lit radar README and the DeFazio et al. 2026 PDF, read with pdftotext.

I edited no repository file. My only scratch files are under `<scratch>/mbF/`.

**Overall.** 14 of 52 medium-or-higher findings are fixed and 11 are partly fixed. One finding moved (the Figure 1.16 caption). 25 are not fixed: every figure-level and structural finding (roles 9, 11, figures for roles 3, 8 and 10) and two of role 8's three blocking rows. One is not applicable (a run-level finding). The diff also brings in 2 new medium–major defects and several lows, listed at the end.

### A. Rulings on medium / major / high / blocking findings

| finding (role · # · one line) | ruling | evidence |
|---|---|---|
| 1 · 1 · Finn 1967 cited unmarked but never opened (medium) | **fixed** | "Finn (1967, pp. 653 and 658; building on Finn 1966 ⚠)". The 01-lit radar README now holds `finn_1967_rca_review_28-4_issue.pdf`, read at p. 653 and p. 658. |
| 1 · 2 · 0.0096 Hz provenance mixed (84-slice set) (low–medium) | **fixed** | "a background rate of 0.0096 Hz per cell: all fast-stream onsets per cell on the lab's earlier 84-recording set … with no separate figure for the slow stream". This matches generator.md ("per-ROI rate 0.0096 Hz, 84 slices"). |
| 2 · 1 · Finn 1967 carries no ⚠ yet was not on the shelf (medium) | **fixed** | Same as 1·1: the scan is filed and the README updated. |
| 2 · 2 · Credit stops at Finn 1967; the root is Finn 1966 (medium) | **fixed** | "building on Finn 1966 ⚠"; reference added: "Finn HM (1966). Adaptive detection in clutter … doi:10.1109/sap.1966.271149. ⚠ (not held; cited by Finn 1967)". |
| 3 · 1 · Limitation 3 cross-reference "(*1.4*)" points nowhere (medium) | **not fixed** | It is unchanged: "not placed through the simulator's own measured-interval option (*1.4*)". |
| 3 · 2 · Figures 1.9 and 1.12 say "held-out record" while the text says "rerun" (medium) | **not fixed** | No PNG changed. The text also still says "16 conditions × 2 records" and "on the pooled records". |
| 4 · 1 · Realistic event counts are detector calls, so probably lower bounds (major) | **partly fixed, new defect** | Added: "the event counts are calls of a sliding 2 s count at each segment's chance floor, a detector whose recall for 7-cell events is well below 1 (*1.2.4*), so the counts are probably lower bounds". The cited evidence contradicts it (see new defect N1). 1.5.7 and 1.10 are not softened: "At a median segment … not readable" still rests on these counts. |
| 4 · 2 · Pooled headline although the per-group rates exist (major) | **not fixed** | Still pooled. The new "Two cautions" repeats that the "medians hide large differences between groups"; no per-group rates beside Table 1.5 or in 1.10. |
| 4 · 4 · 1.9.1 overreach: "CFAR kept false alarms near allowance because it was a prediction" (major) | **fixed** | "Its false alarms were too few to tell from the allowance in the busier stretch and none in the 0.0096 Hz stretches, where its estimate ran about twice the true background and its threshold correspondingly high." The repeated 6/12 agreement is gone. |
| 4 · 8 · "Elsewhere the correlogram does as well" understates it; no paired test (major) | **partly fixed** | "where the correlogram tool gives an estimate at 0.05 s and 0.2 s it does as well or better … a comparison of medians, with no paired test". The overclaim is gone and the missing test is disclosed, but no paired test was run. |
| 4 · 9 · "Readable" undefined and unevenly applied; rate has no table (major) | **partly fixed** | Defined: "a quantity is **readable** when at least 35 of the 40 recordings fall within 0.8–1.25". No rate column was added ("in-band counts in the follow-up record"). The 45-min paragraph still says "rate with 13 cells … but not with 7 on the fast stream", which implies the slow 7-cell rate at 30 of 40 passes. It also produces new defect N2. |
| 4 · 10 · The order clause in 1.10 lacks the caveat (major) | **fixed** | "if a latency template exists with a spread at least 2.5 times the jitter and the events are known without background". |
| 4 · 11 · K = 5 and 8 never scored, although the recordings exist (major) | **not fixed (deferred, disclosed)** | "scoring the existing background-only recordings at K = 5 and 8 would check them (*1.9.5*)". It is now listed in 1.9.5 item 1, not done. |
| 5 · R1 · Prose tool missing (high, about the run) | **n/a (run, not artifact)** | Nothing to rule on in the text. |
| 5 · F1 · "downstream-minus-⏎upstream" renders as "minus- upstream" | **not fixed** | It is at new line 744. |
| 5 · F2 · ⚠ used as a doubt flag in limitation 2 | **fixed** | "from error in the theory (not tested)". |
| 5 · F4 · "±25 %" for an asymmetric band of 0.8–1.25 | **not fixed** | Fig 1.12 caption, "a ±25 % convention"; 1.5.7, "a ±25 % band chosen as a convention". |
| 5 · F5 · "Readable" never defined | **fixed** | The definition quoted at 4·9. |
| 5 · F6 · Name clash between "a first run" and "the first experiment" | **not fixed, worsened** | The new 1.9.5 adds "Report the first run at the lab's values". |
| 5 · F7 · Term drift between "records" and "runs" | **not fixed** | "2 records" and "pooled records" remain. |
| 5 · F8 · Five names for the allowance, budget and floors | **not fixed** | — |
| 5 · F9 · "Cell" overloaded by the radar terms | **not fixed** | The paragraph is unchanged apart from the Finn clause. |
| 5 · F11 · "wide … and narrow" has no comparator | **not fixed** | — |
| 5 · F12 · Floor paragraph does five jobs; misplaced "therefore" | **not fixed** | — |
| 5 · F14 · "The two can differ" has the wrong antecedent | **not fixed** | — |
| 5 · F18 · The 10-cell scope spills over all three clauses of 1.10 | **fixed** | "…(below 0.9 of planted). Whatever the event size, a fixed threshold drowns…". |
| 5 · F19 · "Elsewhere does as well" contradicted by Table 1.3 | **fixed** | It is the same rewrite as 4·8. |
| 6 · 1 · The "CFAR" is a plug-in rule; its false-alarm rate is not constant (moderate) | **partly fixed** | Added: "Finn & Johnson scale the threshold for the size of the reference sample … this detector puts its noisy estimate straight into the known-rate floor, so its rate of chance calls is not held constant and runs higher than the floor's." Situation 4 still judges 1.5/h only against the allowance and blames the clutter edge alone. The "runs higher" claim has no source in the repository (N4). |
| 8 · blocking · 1.3.1 has three undefined terms ("goal page", "generator notes", "of 33 ⚠") | **fixed** | All three are removed from 1.3.1. Only "arcuate kisspeptin neurons" stays unglossed, which is below the three-term rule. |
| 8 · blocking · Prior work "Order" paragraph: SPIKE-order, latency correction, direct shift | **not fixed** | The paragraph is unchanged (new lines 739–743). |
| 8 · blocking · Table 1.9 row: Durbin, Skillings–Mack, W unglossed | **not fixed** | The row is unchanged. |
| 8 · 1 · Fig 1.16 caption: "7-cell 0.05 Hz panels stay near 0" (major) | **moved** | Now: "its 7-cell curves at 0.05 Hz stay near 0; the assessor's do not." In the rendered figure, at σ = 0.5 s and 0.05 Hz (panels D and H), the assessor's 7-cell curve sits at about 0.02–0.03, i.e. near 0. The false statement has moved from the count detector to the assessor. |
| 8 · 2 · Fig 1.10 and 1.11 C panel titles do not match the run names (major) | **not fixed** | The PNGs are unchanged. |
| 8 · 6 · 1.10 reads as a statement about real segments (major) | **fixed** | "In simulation at the lab's parameter values, one 20-minute segment supports…". |
| 9 · 1 · 2,800 words over 7 subsections with no figure; no run map (major) | **not fixed** | — |
| 9 · 2 · No "events needed" figure for the headline (major) | **not fixed** | — |
| 9 · 3 · Figure 1.2 placed after 1.2.1–1.2.3; no CFAR schematic (major) | **not fixed** | — |
| 9 · 4 · 0.01 Hz K = 3 mixture row missing from Figure 1.14 (major) | **not fixed** | — |
| 9 · 5 · Rounded-onset order power only in prose (major) | **not fixed** | — |
| 9 · 10 · Figure 1.6 cramped as a 2×4 grid (major) | **not fixed** | — |
| 11 · 1 · 1.3 gives predictions before 1.4 poses the question (High) | **not fixed** | No restructuring. |
| 11 · 2 · Fig 1.6 carries the violet joint-fit series (Medium) | **not fixed** | The caption still reads "The violet series … is the joint fit". |
| 11 · 3 · "How the predictions are tested" comes before any prediction (Medium) | **not fixed** | — |
| 11 · 4 · Fig 1.5 B and C belong to 1.8 (Medium-low) | **not fixed** | — |
| 10 · (no severities given) · figure, caption and Table 1.1 layout defects | **not fixed** | No figure changed. The Figure 1.10 caption's unclosed parenthesis is still at new line 957 (also role 5 F3). |

**Lower-severity findings the diff fixed:**
- 1·3, mouse independence: now "a mouse can contribute up to three slices (DeFazio et al. 2026)". The PDF says "no more than three slices per mouse were used", so the claim is supported.
- 1·5 / 3·6, the 14 missing CFAR draws: "4 or 5 in 14" matches log line 8 (4 cells in 1, 5 in 13; 63 + 4 = 67).
- 2·3, Sheppard: ⚠ added in Table 1.9 and the reference list.
- 2·4, Grün 1996: reference entry added.
- 2·5, Copeland: fixed in 1.8.2 only (see N11).
- 3·10, "fresh seeds": now "new seeds" (×3).
- 3·11, "quieter background": now "at 0.01 Hz" / "lower" (×2).
- 4·3, intervals: 0.182–0.233, 0.308–0.445, 0.090–0.124 s and 0.120–0.146 s all match bench.py and bench_slow.py; ⚠ dropped.
- 4·6, CFAR reference size: "about 19 background onsets … varies by about a quarter" is arithmetically right (2 × 30 × 33 × 0.0096 = 19.0; 1/√19 = 0.23).
- 8·8, ⚠ used outside its meaning: fixed in both places.
- 7·1, scorer: the docstring in `ch1_intro_figures.py` now says "same counts … may colour 3a and 3b the other way round".

**Lower-severity findings partly fixed:**
- 4·5: the 14 draws are reported, but the heading "found only when the background helps" still overstates for CFAR.
- 4·16: ⚠ replaced, but the caveat is not carried into 1.4 or 1.5.4.
- 4·17: the run is acknowledged in 1.9.5 but not reported.
- 4·20: the slow-stream background is addressed; the flat-background statement is not.
- 8·9: the internal labels are gone from 1.3.1, but "goal page" re-enters in 1.9.5 and "shipped" remains.

**All other minor/low findings remain as residual ⚠:**
- role 1: 4, 6–11;
- role 2: 6–8;
- role 3: 3–5, 7–9, 12–14;
- role 4: 7, 12–15, 18, 19;
- role 5: F3, F10, F13, F15–F17, F20–F35;
- role 6: 2–4;
- role 7: 2–12;
- role 8: 3–5, 7, 12–17;
- role 9: 6–9, 11–15;
- role 11: 5–9.

### B. New defects introduced by the diff

| # | location | issue | severity |
|---|---|---|---|
| N1 | 1.3.1, "Two cautions" | The claim that the counting detector's "recall for 7-cell events is well below 1 (*1.2.4*)" is contradicted by its own citation. Table 1.1 shows the sliding 2 s count finding the 7-cell event 2 (jitter SD 0.5 s) in 1.00 of draws. Only the 5-cell event 5 (0.66) is found less often. The lower-bound argument may still hold for real segments (participation varies, and floors vary with 14–61 cells), but no evidence for it is cited or shown. | major |
| N2 | 1.5.7, after the new definition | "With 7 cells … the tool four and two. At a median segment (one fast or two slow events) 7-cell events are therefore not readable". Under the ≥ 35 of 40 rule, the tool reads slow 7-cell events at E = 2 (37 of 40, Table 1.5), as the sentence before says. The two sentences contradict each other. "Borderline to readable" for 13 cells is also undefined under the new rule: fast at E = 1 is 30 by the joint fit (not readable) and 40 by the tool (readable). | medium |
| N3 | 1.5.7 | "participants are readable … from two events on by the joint fit (40 of 40)". Fast 13-cell at E = 4, 8 and 16 is 39 of 40 (Table 1.5). Should be "39–40 of 40". | low |
| N4 | 1.2.3, new last sentences | The claim that the chance-call rate "runs higher than the floor's" has no number in the chapter or `ch1_intro_figures.log`. Its only source is role 6's scratch simulation (0.63 vs 0.26 per hour at 0.0096 Hz; 0.51 vs 0.33 at 0.05 Hz). "The floor's" rate is also ill-formed, because the floor is a cell count, not a rate. Situation 4 still credits the 1.5/h busier-stretch rate to the clutter edge alone, which now sits in tension with this sentence. | medium |
| N5 | Fig 1.16 caption | "the assessor's do not [stay near 0]" is false at σ = 0.5 s (panels D and H, about 0.02–0.03). This is the moved defect in 8·1. | medium |
| N6 | 1.3.1, k bullet | "7 … and 13, of 33: participation 0.203 … and 0.375". 0.375 × 33 = 12.4 (× the measured 32 ROIs = 12.0), and 0.203 × 33 = 6.7. Rounding 12.4 to 13 is not explained. 1.5.7 also says this tool reads about 0.92 of planted, so a reading does not equal the planted k; how one was turned into the other is unstated. | low–medium |
| N7 | 1.3.1, k bullet | The jitter intervals ("the jitter intervals are 0.090–0.124 s and 0.120–0.146 s") are tacked onto the participation bullet instead of the jitter bullet above it. | low |
| N8 | 1.9.5 item 1 | "Report the first run at the lab's values (recorded on the goal page, 2026-11-11…)" has three problems. It reintroduces "goal page", the internal label removed from 1.3.1. "First run" collides with "the first experiment" (F6). The same item still asks to "Add realistic jitter (σ = 0.105 and 0.131 s) and 7 cells per event to the first experiment's grid", which is the run it has just said exists. | low–medium |
| N9 | 1.6.1 | "K = 5 and 8 were not simulated, with or without events … scoring the existing background-only recordings at K = 5 and 8 would check them". K is a threshold, not something simulated; the recordings exist and were not scored at those K. As written, the sentence contradicts its own next clause. | low |
| N10 | 1.2.3 | "30 s on each side holds about 19 background onsets": 19 is both sides together (each side about 9.5). It reads as 19 per side. | low |
| N11 | Table 1.9, "The score sort" row | It still says 'a Borda score ("Copeland counting" in Shah & Wainwright 2018)', while 1.8.2 now says "a net-wins variant of what Shah & Wainwright (2018) call Copeland counting". The fix was applied in one place only. | low |
| N12 | 1.9.1, new sentence | "Its false alarms were too few to tell from the allowance … and none in the 0.0096 Hz stretches" is a zeugma ("were … none"). Suggested: "…and there were none in…". | low |
| N13 | 1.5.6, new topic sentence | Restricted to "the busier background from 0.5 s up" and "0.05 s and 0.2 s". It leaves 0.01 Hz at 0.5 s and 1 s uncharacterized, where Table 1.3 shows the joint fit also ahead (0.98 vs 0.92; 1.01 vs 0.86, n = 5). | low |
| N14 | References, Grün 1996 | "Doctoral thesis, as cited by Grün et al. 1999. ⚠ (not held; details not checked)" gives no title or institution, so the entry cannot be looked up. | low |
| N15 | 1.2.4 situation 5 | The heading "An event below the threshold is found only when the background helps" now sits beside the newly reported 14 draws in which CFAR's threshold was 4 or 5 cells. In those draws CFAR needs no background onset, and the text does not reconcile the two. | low |

**Checked and correct in the diff:**
- "4 or 5 in 14" and "7 or more in 67" (log line 8).
- The participation and jitter intervals (bench.py, bench_slow.py).
- 0.0096 Hz on 84 slices (generator.md).
- "Rate needs at least four events with 13 cells and sixteen with 7" under ≥ 35 of 40 (follow-ups: fast 13 at E = 4 is 35, slow 13 at E = 4 is 37; fast 7 at E = 16 is 38, slow 7 at E = 16 is 40).
- Joint fit 7 cells needs 8 fast and 4 slow; the tool needs 4 fast and 2 slow (Table 1.5).
- "estimate ran about twice the true background" (0.0208 against 0.0096 Hz).
- "up to three slices" (DeFazio et al. 2026).
- Finn 1967 at pp. 653 and 658 (01-lit README).
- The scorer docstring (role 7 finding 1).

No broken internal links or section references were introduced. The "(*1.9.5*)" in 1.6.1 and "(*1.6.1*)" in 1.9.5 resolve.
