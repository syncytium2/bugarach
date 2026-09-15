> **Public copy.** Lines that concern real treatment recordings are removed (23 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 3 ok — Read, Grep, Glob

# Role 3, Cross-Examiner: blind pass, round 2

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

Each row reads: location · issue and evidence · fix · could I verify it against a source.

---

## BLOCKING

**B1. Section 7 and Table 2 against MILESTONES "Open" and section C** · MILESTONES lists "The 24-seed bake-off — held; the input data may be revised". It says that blocks "promoting any new bake-off number". Its legend says `held` means "deliberately not to be quoted or promoted yet". The document publishes a full 24-recording bake-off for outside readers, and the footer says it is "a separate run of the project's bake-off tool". Its locust busy-block figures (average and worst round) also differ from the held row's 30.62 per minute, and nothing explains why. · Fix: get Tony's release on record and update the MILESTONES row in the same change. Otherwise, mark Section 7 as provisional and explain how this run relates to the held one. · Verifiable: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## MAJOR

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

· Fix: name locust, not a class of detectors. Say that rate+context also calls heavily in dense real stretches. Cite Figure 2C alone for the whole-recording versus nearby contrast. · Verifiable: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**M3. "In short", bullet 2, against §7** · "In short" says "Busier cells make **every** useful detector less sensitive". §7 says "almost every detector" and lists "two exceptions: tuned binned SCE rose". Tuned binned SCE recall also rises, from 0.48 to 0.60 (numbers.json `perf_baseline_*_sce.recall`). "Useful" is not defined anywhere. The same bullet says "57% in a quiet recording and 19% in a busy one", but those are averages over 24 recordings per level, not one recording each. · Fix: "almost every detector … (binned SCE is the exception)". Write "at the quiet level" and "at the busy level" instead of "a quiet recording". · Verifiable: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**M5. Figure 2C caption and §2, "Outside the block, each bar makes 3 calls: 1 on a planted event and 2 on decoys"** · In the generator (`make_detector_review.py`, around lines 530–556), every count, including "46 times inside the busy block", is limited to `view_c = (900, 1800)`, which is minutes 15–30. The recording is 45 minutes long and holds 15 planted events. Neither the caption nor the prose says the panel and the counts cover only minutes 15–30, so "1 on a planted event" reads as 1 hit out of 15. · Fix: state "minutes 15–30 shown; counts are for that span" in the caption and in §2. · Verifiable: yes, from the code.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**M12. Figure 12 panel C heading and caption against its content** · The heading reads "B, C · quiet background", but panel C's legend says "filled: quiet · hollow: busy", so it shows both levels. The Figure 12 caption for C does not mention the busy points. The hollow markers are all white, so the 30%/18%/10% shading is lost and busy recall by event size cannot be read. §7 quotes busy values from this panel ("19%", "12%"). · Fix: retitle to "B · quiet; C · quiet and busy", describe the filled and hollow markers in the caption, and give the hollow markers an outline shade by size. · Verifiable: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**M14. "In short" and §7 "no detector stands out" against MILESTONES section B, "On the fitted field one winner holds across the axis"** · That row is `measured` and `current`: "at 12 seeds, one detector leads at every grid point". The document says five detectors score alike and ranks none. The experiments differ (a 12-seed background axis against this 24-recording held-out run), but a reader of both sees opposite headlines. The document is consistent with the MILESTONES "No ranking" row. · Fix: one sentence in §7 or §10 saying why the earlier single-leader result is not repeated here, or a status note on that MILESTONES row. · Verifiable: yes.

## MINOR

1. **Figure 8B caption, "scores stay low; 0 calls"** · In the bottom row, one bin near 22m50s visibly passes the 0.1 bar. The 0 calls come from the rule that a call needs at least 3 events (`sync_detect` `min_n=3`). · Fix: "one bin passes 0.1 but holds fewer than 3 events; 0 calls". · Verifiable: yes.
2. **Figure 4B** · One count of about 9 near 22m48s sits beside a bar dash of about 8.6, which looks like "a count reaches it", yet the caption says "no count reaches it". The dash may belong to a neighbouring bin. · Fix: check it and either mention the near-miss or align the dashes to their bins. · Verifiable: no.
3. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
4. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
5. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
6. **Figure 11C "breaks its busy-block limit" against Table 2 and §7: two bases** · The markers in Figure 11C are computed on all 24 recordings. Table 2's red cells and §7's "SPIKE-synch in 3" come from held-out rounds. SPIKE-synch's chosen value is crossed on all four picks (`picks_over_limit` 4) but broke the limit in only 3 rounds. · Fix: add "on all 24 recordings" to the legend or caption. · Verifiable: yes.
7. **§7 "Every number comes from recordings the setting or the training never saw"** · The same section quotes Figure 11C values (for example SPIKE-synch F1 "0.48 to 0.53"), which come from all 24 recordings, not held-out ones. · Fix: limit the sentence to Figure 12 and Table 2. · Verifiable: yes.
8. **Table 2 "at the setting it ships with · calls per minute, busy block"** · The column does not say which level. It is the quiet level (`shipped_baseline_quiet_*`), matching the Figure 12B diamonds. · Fix: add "quiet". · Verifiable: yes.
9. **Figure 12B legend "floor: no calls drawn here"** · tube-ratio (0.008 per minute) sits on the floor even though it made calls. Table 2 calls trace's and tiny's busy-block rate "not meaningful", yet Figure 12B plots them unmarked. · Fix: "floor: fewer than 0.01 per minute drawn here", and grey out or footnote trace and tiny. · Verifiable: yes.
10. **Figure 2B** · The top legend says "recorded" while the in-plot legends say "real". The caption does not say B has two panels (fast stream, slow stream). · Fix: one word throughout, and "left: fast stream; right: slow stream" in the caption. · Verifiable: yes.
11. **Figure 2C caption "bins where each bar is passed by at least 3 ROIs"** · The code rule is count above the bar **and** at least 3 ROIs (line 539). The lanes are labelled "calls: …". · Fix: "calls: bins whose count passes the bar, with at least 3 ROIs". · Verifiable: yes.
12. **"Pass" against "reach"** · The Word list defines Bar as the value a measure "must pass", and binned SCE misses at count = bar. §3.5 locust "peaks … that reach the bar", §3.2 CoactDetect "3.72 … or more", and §4.1 "reaches the call level" all use "reach" or "or more". · Fix: say which rule each detector uses, or soften the Word list to "pass (or, for some detectors, reach)". · Verifiable: yes.
13. **§4.1 tube-guard "so an event does not raise its own bar"** · For learned detectors the document's term for the threshold is "call level". "Bar" here means the surround. · Fix: "does not raise its own surround". · Verifiable: yes.
14. **Grading vocabulary** · §6.1 says "a second call on an event already claimed". The key in Figures 3–9 says "already found". Figure 11A says "duplicate", without saying a duplicate counts as a false alarm. · Fix: pick one phrase, and add "(a false alarm)" to the Figure 11A label. · Verifiable: yes.
15. **Figure 9 panel letters against the Window A and Window B names** · In §3, Window A and Window B are panels A and B of Figures 3–8. In Figure 9 they are panels B and C, while panel A is the filters. · Fix: in the Figure 9 caption write "B (Window A)" and "C (Window B)". · Verifiable: yes.
16. **Figure 10 A1/A2 caption "one bench recording (seed 1) at the quiet and busy levels"** · The planted and decoy times differ between A1 and A2 (for example, the last planted event and the decoy positions), so these are not one recording at two levels. · Fix: "the seed-1 bench recording at each level (event times are drawn per level)", or show identical times. · Verifiable: yes, visually.
17. **Figure 10B "10 ROIs (30%) take part"** · I count about 8 ticks, all in the top few rows, where A1's planted columns span the full height. · Fix: check the zoom window and row range. · Verifiable: no.
18. **§4.2 "two simpler networks"** · numbers.json gives trace 2,065 and tiny 2,393 adjustable numbers, against tube's 1,149. · Fix: "structurally simpler (though with more adjustable numbers)". · Verifiable: yes.
19. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
20. **Retired bare "setting(s)" (GLOSSARY, Parameter vocabulary)** · It appears throughout, for example "the settings they ship with" and §8 "Fast-stream settings". The Word list defines it, which may be enough for outside readers. · Fix: either "detector settings" on first use and in the Word list, or record an exemption for outward documents. · Verifiable: yes.
21. **New terms missing from the glossary, where glossary synonyms exist** · decoy (glossary: distractor), busy block (promiscuity probe), limit (ceiling), call (detection), bar, call level, quiet/busy level (regime), round, training run, shipped setting (operating point). The checklist rule is that a new term enters the glossary in the same change. · Fix: add these as outward-facing aliases in GLOSSARY. · Verifiable: yes.
22. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
23. **"Quiet level" in the text against "quiet background" in Figures 10, 11C and 12** · Fix: pick one. · Verifiable: yes.
24. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
25. **§3.3 "spaces events 2 minutes apart" against §3 and §5 "at least 120 seconds apart"** · Fix: "at least 2 minutes". · Verifiable: yes.
26. **§3.4 "the whole recording in Figures 3 to 9"** · binned SCE is not in Figure 9. · Fix: "Figure 6". · Verifiable: yes.
27. **§11 "Five hand-written detectors were first written in MATLAB by the same author"** · "The same author" has no antecedent. · Fix: name the author, or write "by this project". · Verifiable: yes.

**Checked and consistent (no finding):**
- Table 1 against `settings` and §§3.1–3.6.
- §5 generator numbers (jitter, the 5-minute and 1-minute rate swings, the busy block and its easing-in, decoys, the precision cap of 0.71).
- §6.2 limits.
- §6.3 rounds (24, 4 × 6, 18).
- Every Table 2 and Table 3 value.
- §7 prose numbers.
- The Figure 11C chosen, shipped and limit markers.
- Figure 12A and 12B.
- The Figure 3, 6, 7 and 9 window call counts.
- Figure 10A planted and decoy counts (15 and 6 per panel).
- Figure 10C and 10D values.
- The §2 surrogate percentages and ratios.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Contents against the section headings.
- No "modality" or "multimodal", no bare "adaptive" (only inside a cited paper title), no "corpus".
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

Files: `<scratchpad>\review\detector_review_plain.txt`, `...\review\_work\numbers.json`, `<worktree>\tools\make_detector_review.py`, `...\docs\GLOSSARY.md`, `...\docs\FOUNDATIONS.md`, `...\docs\MILESTONES.md`, `...\src\bugarach\bench.py`, `...\src\bugarach\detectors\sync.py`.
