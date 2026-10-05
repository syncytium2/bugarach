> Archived verbatim except machine-local paths (shown as `<darkroom>`, `<worktree>`, `<scratchpad>`, `<repo>`, SAP004) and redactions: times and positions of calls on real recordings (findings 9, 13 and the
> S9–S17 rows) are replaced by `[t]`, because nothing derived from real data goes into this public repo
> (FOUNDATIONS §5). Each finding's substance survives: the caption time is a minute off the plotted call, and the
> Figure 10 call sits at the recording's first frame.

GRANT 8 ok — Read, Grep, Glob

Role 8 (You Lost Me), round 1. I read the built page `<darkroom>\bugarach\2026-09-26-full-panel\briefing\index.html` in full, including the Figure 1 SVG inline and the Terms table. I opened all nine example PNGs (Figures 2–10) as images and read the viewer instructions box in section 3 as a first-time user. I read everything as a stranger: Tony knows the preparation but not the code. The Terms table sits at the bottom of the page and nothing links to it, so a term counts as undefined wherever it is first used.

Nothing in this report quotes a recording id; figures are referred to by number.

## Per-section verdict

| # | Section / panel | Terms and identifiers first used here | Defined here? | Can a cold reader follow? |
|---|---|---|---|---|
| S0 | Title and byline | ADR-0010, "fresh seeds", "adopted" | none | **no** |
| S1 | Section 1 heading and "How to read it" box | CoactDetect, detector vs "learned pick", shipped setting, paired, seeds, background, bootstrap, bench (new/old), proposals, "a field some rows were chosen on", stream (fast/slow/combined) | F1 and ΔF1 only at the bottom; CoactDetect, bench, pick, proposal, seed, background none here | **BLOCKING** (8+ undefined) |
| S2 | Table 1 | "rows above / below", "top row (ΔF1)", raw model names (for example chorus_gain_norm_part), "pick, seed 4" | no | **BLOCKING** (garbled caption, identifiers, a disqualified row presented as "top") |
| S3 | Figure 1 (leaderboard) | row labels tube, line, line_part, tube_part, chorus_norm, chorus_norm_part, chorus_gain_norm, chorus_gain_norm_part, LoCo, locust, SPIKE-synch, binned SCE, rate+context, count (sliding/binned); "§5", "grid limit", "ruling 5", "budget", "best seed" | §5 and ruling 5 half-explained in the caption; everything else no | **BLOCKING** |
| S4 | Table 2 (fast) | budget-note lines; ruling-5 notes that name raw parameters (context_win, context_win_sec, guard_sec, k_offset, threshold_pctile, n_synchronous_frames); "grid floor / ceiling / cap / limit" | no | **BLOCKING** |
| S5 | Table 3 (slow) | "the recording with nothing planted", "calls/h", "dense block … (the probe)", "comparator only", "best seed", C_min, dt | probe and nothing-planted: partly, at the bottom | **BLOCKING** |
| S6 | Table 4 (combined) | "guard_sec at its edge (8.0)", "unbracketed, no axis named" | no | **BLOCKING** |
| S7 | Section 2 intro paragraph | "ran on the real recordings", `065/review/detect/calls.csv`, leader, baseline windows, median participant count, spans, "scoring tolerance", lanes | "agree" is defined (2.5 s); the rest no | **BLOCKING** |
| S8 | "Passed over" note (fast) | "LoCo · proposal", "91 calls on baseline windows" | n/a | **no** (garbled sentence) |
| S9 | Figure 2 | chorus_gain_norm_part, a LoCo lane (which setting?), participating ROIs, "floors" | ROI defined at the bottom; floors no | **no**: the caption's time is not on the axis |
| S10 | Figure 3 | as Figure 2 | as Figure 2 | **no**: the caption's time is outside the plotted window |
| S11 | Figure 4 | as Figure 2 | as Figure 2 | yes, with caveats |
| S12 | Figure 5 | "line" lane (which seed?), LoCo (which setting?) | no | **no**: the example call is not marked among about eight agreeing calls |
| S13 | Figure 6 | as Figure 5 | no | **no**: caption reads "20m60s" |
| S14 | Figure 7 | as Figure 5 | no | yes, with caveats |
| S15 | Figure 8 | chorus_norm_part lane | no | **no**: the example is not marked among seven calls |
| S16 | Figure 9 | as Figure 8 | no | **no**: the caption's time is a minute off; y label clipped ("30 RO") |
| S17 | Figure 10 | as Figure 8 | no | **no**: the call sits at the recording's first frame; "120 s either side" is false |
| S18 | Section 3 viewer box | viewer, "floor variant", "floors", export-folder literal name, a personal absolute path, Reopen, the permission prompt | no | **no** (see V1–V5) |
| S19 | Table 5 | group × first-treatment, "aligned at end of its own baseline" | readable to the PI | yes |
| S20 | Table 6 | recording ids (fine for the PI) | n/a | yes |
| S21 | Terms | defines F1, ΔF1, the benches, shipped/proposal, pick, budget, ruling 5, ROI, EDT | n/a | yes, but it is missing most of the terms above and nothing links to it |

## Findings
Columns: location · issue · severity · suggested fix · verified against source.

1. **S1, S3, S4–S6, S9–S17 (the whole page)** · **CoactDetect**, the reference every row is measured against, is never described: what it is or what "shipped setting" means for it. The same goes for every other detector and model name (LoCo, locust, SPIKE-synch, binned SCE, where SCE is never expanded, rate+context, count (sliding/binned), tube, line, and the chorus family). · **blocking** · Add a "What is being compared" box above Table 1 with one line per detector or model family, saying what it detects in plain words and marking which are hand-coded and which are learned. · yes

2. **Figure 1 row labels, Tables 1–4, Figure 2–10 captions and lanes** · Internal code identifiers appear as the audience-facing names: chorus_gain_norm_part, chorus_norm_part, chorus_gain_norm, chorus_norm, line_part, tube_part. The suffixes (_gain, _norm, _part) each encode a design choice that the page never explains. · **blocking** · Give plain display names, for example "chorus model, gain-normalized, participation input". Explain each suffix once in the new box from finding 1. Keep the identifier only in the viewer hover. · yes

3. **Tables 2–4, ruling-5 note lines; Table 4 row 13** · Raw parameter names with no units reach the audience: context_win, context_win_sec, guard_sec, k_offset, threshold_pctile ("at its cap (99.9921875)"), n_synchronous_frames, C_min, dt ("at its cap (0.00078125)"). "unbracketed, no axis named" is opaque. "guard_sec at its edge (8.0)" and "guard_sec at its limit (0.0)" use different words for what may or may not be the same condition. · **blocking** · Render each note as a plain concept with its unit, for example "the gap required before an event (guard) hit the search's lower edge, 0 s". Rewrite "unbracketed" as a sentence. Use one word for grid boundary throughout. · yes

4. **S1 box and Tables 1–4 vs Figure 1 and the Terms table** · **"Seed" means two different things.** "48 seeds per background" means simulated recordings. "pick, seed 4" means a model's training seed. ΔF1 is "averaged over seeds" in the first sense. A cold reader will conflate them. · **major** · Say "simulated recordings" (or "simulation seeds") for the first sense and "training run 4 of 5" for the second. Define both in Terms. · yes

5. **S1 "How to read it" box** · Dense and partly unreadable. "each column is partly a field some rows were chosen on and others were not" will not parse for a cold reader. "bench", "proposals", "learned picks", "background" and "ADR-0010" are all used before any definition. "The new and old benches score the same candidates" does not say what a candidate is. · **blocking** · Split it into three bullets: what a row is; what a bench is, with the new/old difference said in one line (planted events spaced as in real recordings vs at least 120 s apart); and the selection caveat restated as "proposals and picks were tuned on the new bench, so their new-bench numbers flatter them". Link each term to Terms. · yes

6. **Table 1 caption and cells** · The caption does not parse: "have a 95% interval wholly above …, including zero, or wholly below it". "1 rows" is ungrammatical. The "top row (ΔF1)" column names rows that are disqualified: on the fast/new line SPIKE-synch · shipped is over budget on both benches, and a cold reader will take that row as the winner. · **major** · Rewrite the caption as three column meanings. Singularize the count. Either make "top row" mean the top row within budget, or mark the disqualified top row as over budget in that cell. · yes

7. **Figure 1: false-friend check (render open, caption covered)** · Resembles: a forest plot. In that idiom the x axis is effect size, the vertical line marks no effect, and each row is one comparison with a CI whisker. Here: the same, so **not a false friend**. Two residual readability problems. (a) **Red** in a forest plot tends to read as "significant" or "harmful". Here it means "over a false-call budget, or no pick", a disqualification that has nothing to do with the interval. (b) The legend shows only a filled red mark, so an open red mark (old bench over budget) has no legend entry. What a cold reader sees: "about 63 rows of paired dots and whiskers around a zero line, some red for an unstated reason until the bottom of a 2,100-pixel scroll". The axis and legend exist only at the bottom, below all three stream blocks. · **major** · Use a neutral grey or hollow-with-X for disqualified rows rather than red. Add both red forms to the legend. Repeat the x-axis ticks and legend at the top of each stream block, or split the figure into three, one per stream. · yes

8. **Figure 1, slow block: "chorus_gain_norm_part · best seed, seed 4"** · Every other learned row reads "pick"; this one reads "best seed", and the difference is explained only in a Table 3 note ("no pick … a comparator only"). · **minor** · Label it "no pick (comparator)" in both places and define "comparator" in Terms. · yes

9. **Figure 2 and Figure 3 captions; Figure 6 and Figure 9 too** · **The call time in the caption does not match the plot.** Figure 2's caption gives a time a minute later than the call, outside the plotted axis. Figure 3's caption gives a time past the end of its axis, a minute after the call. Figure 9's caption is a minute late. Figure 6 reads "20m60s", which is not a valid time. The link's own time value in each case is one minute earlier than the caption. It looks as if minutes are rounded rather than floored. A cold reader looks for the call where the caption says and finds nothing. · **blocking** (readability; the numeric defect also belongs to roles 1 and 10) · Fix the minutes/seconds formatter (floor the minutes; carry 60 s). Better still, mark the example call on the lane (finding 10). · yes (caption vs rendered axis vs link time value)

10. **Figures 5, 8, 9 and 10** · **The example call is not marked.** Figure 5 shows about eight calls on which LoCo and CoactDetect both agree, and Figure 8 about seven. The caption says "the call at …" and the reader cannot tell which one is meant. That matters most for the agree/leader-only/ref-only reading the section depends on. · **blocking** · In a thin lane above the detector lanes, put a single down-pointing marker at the example call's time. That respects the no-drawing-on-the-raster rule. Or narrow the window so the example is the only call in it. · yes

11. **Figures 2–10: false-friend check on the lanes** · The raster (x = time, rows = ROIs) is a real raster, so the raster itself passes. But the **detector lanes are drawn as vertical tick bars**, the same mark as a raster event. Covered, the top panel reads as three more raster rows, and bar width (the call's span) reads as a burst. The section 3 box says the viewer shows "▼ at each onset", so the static figures and the viewer describe calls with different marks. · **major** · Either draw the lanes as the same down-pointing ▼ the viewer and house convention use, or keep spans but draw them as filled horizontal boxes with borders so they cannot be read as raster events. Say in one caption line what bar width means. · yes

12. **Figures 2–10: lane colors and lane choice** · Lane colors (grey, purple, teal) are unexplained. Why a third lane (LoCo in Figures 2–4, "line" in Figures 5–7, chorus_norm_part in Figures 8–10) is there is never said. "LoCo" and "line" do not say which setting or seed; the leaderboard has LoCo both shipped and proposal, and line picks from different seeds per stream. · **major** · In each subsection heading, name the three lanes with their settings and why the third lane is shown (for example "the next row on the leaderboard"). · yes

13. **Figure 10** · The example "CoactDetect only" call is at [t]: a sliver at the first frame of the recording. The caption says "120 s either side", but the window starts at 0 s. A cold reader cannot tell a recording-edge artifact from a real call, and a start-of-file call is the least representative example. · **major** · State that the window is truncated at the recording start. Flag that the call lies on the edge, or choose the next median call away from the edge. · yes

14. **Figure 9 y-axis label** · Clipped to "combined · 30 RO". · **minor** (mechanical; role 10 owns it, noted here because it is what a reader sees) · Widen the left margin. · yes

15. **Figures 2–10 x-axis label** · The axis label is a bare "t". · **minor** · "time in recording". · yes

16. **Section 2 intro (S7)** · A code path appears in audience text (the calls.csv path under the review folder). "The top row that ran on the real recordings" implies some rows did not, and says neither which nor why. "leader", "baseline windows", "median participant count" and "spans" are undefined. · **blocking** · Drop the path, or move it to a footnote. Say which leaderboard rows were run on real recordings. Define "baseline window" (the pre-treatment period) and "participants" (ROIs with an event inside the call). · yes

17. **"Passed over" note (S8)** · "none gives an example of: LoCo · proposal calls it; CoactDetect does not; CoactDetect calls it; LoCo · proposal does not." The semicolons run the two disagreement categories together and the sentence does not parse. · **major** · "LoCo at its proposed setting made 91 calls on baseline windows, and CoactDetect made every one of them too, with none the other way, so there is no disagreement to show." · yes

18. **Captions of Figures 2–10 and the section 3 box: "floors", "floor variant"** · Undefined everywhere, including Terms. · **major** · Define it in Terms and at first use, for example "floor: the per-ROI minimum amplitude an event must reach; variants differ in how that minimum is set". Use the actual meaning, which I cannot verify from the page. · yes (absence verified)

19. **Byline (S0)** · "ADR-0010" (also in the S1 box, Figure 1 caption and Terms), "scored on fresh seeds" and "nothing here is adopted" all assume project vocabulary. "ADR" is never expanded. · **major** · "Planted-event spacing was changed on 2026-09-25 to match real recordings (decision record 10)"; "fresh seeds: simulated recordings not used for tuning"; "adopted: made the new default". · yes

20. **Tables 2–4, budget-note lines; Terms "budget"** · Budget notes are readable, which is good. But "calls per hour outside an elevated-rate window" is in Terms and appears in no table, and "elevated-rate window" is undefined. Table 4 row 6 is flagged "over budget … 0.10 against a limit of 0.1": equal as displayed, so a reader sees a contradiction. · **minor** · Print enough digits to show the excess (for example 0.104). Define "elevated-rate window" or drop that budget from Terms if nothing in this run uses it. · yes

21. **Terms table (S21)** · It sits at the end with no anchors linked from first use. It misses CoactDetect, all detector names, stream, seed (both senses), background (quiet/busy), floor, floor variant, participants, baseline window, leader, comparator, held-out, grid limit, bootstrap, SCE and ADR. · **major** · Add the missing entries, link each first use to its entry, and add a pointer under the nav ("new terms: see Terms"). · yes

22. **Section 3 viewer box, as a first-time user (V1)** · **The box comes after the links that need it.** Every Figure 2–10 image and caption links into the viewer, but the setup steps are in section 3. A reader who clicks Figure 2 first lands in an empty viewer with no instructions. · **blocking** · Move the "Opening one recording" box to the top of section 2, or put a one-line pointer in every caption ("first time? see the setup steps in section 3"). · yes

23. **Section 3 viewer box (V2)** · Step 1 names the export folder by its internal folder name but not where it lives on disk, so a first-time user does not know where to browse. · **major** · Say where it is ("under the exports folder in your Dropbox bugarach data directory"). Keep the literal name as a secondary line. · yes

24. **Section 3 viewer box (V3)** · Step 2 prints a full personal absolute path to the results file. That is an internal file path in audience text, and it is machine-specific: it will be wrong on any other machine. · **major** · "the file detections.csv in the same folder as this page". Do not print the absolute path. · yes

25. **Section 3 viewer box (V4)** · "After that, a link needs one click on Reopen … the results file is picked again each visit unless it is copied into the export folder": a first-time user cannot tell whether they should copy it. "floor variant" and "floors" are undefined (finding 18). "▼ at each onset" contradicts the bars in Figures 2–10 (finding 11). · **minor** · Say plainly: "each visit you will re-pick detections.csv" (or give the recommended action). Align the mark description with the figures. · yes

26. **Tone check** · Sentence case is consistent. There are no stray capitals or ALL-CAPS in prose, and I found no lists smuggled into titles. · **none** · none · yes

## Summary for synthesis
- **Blocking rows:** S1, S2, S3, S4, S5, S6 and S7 each introduce three or more undefined terms or identifiers. The caption-time mismatches (finding 9) make Figures 2, 3, 6 and 9 unreadable as captioned. The unmarked example calls (finding 10) do the same for Figures 5, 8, 9 and 10. Figure 10 also has the recording-edge call (finding 13). The viewer instructions come after the links that need them (finding 22).
- **False-friend verdicts:**
  - Figure 1 is a real forest plot, so it passes. Its red is misleading (finding 7).
  - The rasters in Figures 2–10 are real rasters, so they pass. The detector lanes, drawn as tick bars, read as extra raster rows (finding 11).
- **Boundary notes:** the time formatter in finding 9 is also a number-correctness defect for roles 1 and 10. The clipped label in finding 14 is role 10's. I filed both because they are what makes the panels unreadable to a stranger.
