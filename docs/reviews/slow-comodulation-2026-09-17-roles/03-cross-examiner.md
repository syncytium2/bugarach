GRANT 3 ok — Read, Grep, Glob

# Cross-Examiner report: slow co-modulation explainer, round 1

**Artifact:** `<worktree>/docs/learned/slow_comodulation/README.md`

**Scope:** I checked the page against all four figures (opened), `summary.json`, both generator tools, `src/bugarach/simulate.py`, `src/bugarach/bench.py`, `src/bugarach/detectors/coact.py`, the goal page, both companion reports, `recording_identity.md`, INDEX, GLOSSARY, FOUNDATIONS §5 and §9, MILESTONES, and the CLAUDE.md conventions.

**Counting basis pinned:** recordings are the unit that gets pooled, and mice are the unit that gets resampled for intervals. Lab fast and lab slow are two streams of one folder: the same 84 recordings from 44 mice. Cossart is 59 recordings from 32 mice. The excess counts behind the "share beyond 1 s" figures are counted over ordered ROI pairs.

**Summary:** no blocking findings, 8 major, 24 minor.

## What agrees (no finding)

- **The table:** all 45 cells, point values and interval bounds, match `summary.json`.
- **Counts and totals:**
  - 84 recordings, 44 mice and 26.88 hours on each lab stream; 59 recordings, 32 mice, 22.74 hours and a median of 566 ROIs on Cossart.
  - The Figure 4 groups (17/22/25/20 recordings from 10/12/12/10 mice) add up to 84 and 44.
  - The share of onsets CoactDetect removal takes: 2.5 % median and 10 % mean on fast, 7.1 % and 22 % on slow.
  - The share of excess beyond the cut is 0.91, 0.71 and 0.86.
  - The run took 90 s, so "under two minutes" holds.
- **Ratios:** +2.06 to +0.95 is about half, and +21.94 to +3.20 is about six-sevenths.
- **Slow-stream dip:** "+0.36 to +0.57" at *J* of 10 and 20 s matches `summary.json`.
- **Synthetic worlds:**
  - The 20 s world goes +0.75 → +0.50 at *J* = 10 s → +0.36 at *J* = 20 s, and the block control keeps about +0.15 to +0.18.
  - The events world at *J* = 20 s sits at about +0.12 until roughly 20–28 s.
  - The spec (24 recordings, 32 ROIs, 1,200 s, 0.0097 per s, 32 events of 7 ROIs, 0.3 s jitter) matches the code.
- **Settings:** lag bin edges, *J* values, the 20 s trim and 8 draws match. The symlog thresholds (1.0 in Figure 1, 0.5 in Figure 2 panel A) match the captions. CoactDetect's `min_rois = 3` and its slow settings (1 s bins, 120 s context, α 1e-6) match.
- **Quotes and links:** the `simulate.py` quote is exact. The INDEX group-nested-in-day claim holds (42 dates, none with two groups). All relative links resolve.
- **Conventions:** "modality" never appears, and "data" is never used, so the plural rule has nothing to catch. All four figures are numbered, and counts carry units.
- **Group order:** DI/MALE/ORX/OVX is the same in the Figure 4 caption and legend, and matches `tools/make_intro_figures.py`, `docs/conditioned_run.md` and the rigid-shift look.

## Major findings

**1. "No benchmark contains a shoulder" is contradicted by the bench itself.**
- **Location:** README l.55–57 (*"the simulator's background has no shared modulation at all, so no benchmark in this repository contains a shoulder"*) and l.175–176 (*"The benchmark has never contained any of this … no supervised model here has seen a shoulder"*).
- **Issue:** `src/bugarach/bench.py` l.387–389 sets `BENCH_RECORDING` with `hot_window=(1200.0, 1500.0)`, `hot_rate_hz=0.06` and `ramp_sec=30.0`. `simulate.py` l.776–787 adds that dense block to every ROI over the same 5 minutes. That is a shared, field-wide rate rise: the promiscuity probe (MILESTONES "The promiscuity probe", built, current). Every bench run is scored on that recording. The `n_distractors=6` correlated bursts are shared structure too.
- **Suggested fix:** narrow both sentences to "the simulator's *background* draws modulation per ROI". Then say that the bench recording does contain one shared 5-minute rate block (the promiscuity probe), which it keeps out of headline precision. Either measure its correlogram or state what it would look like.
- **Verified:** yes

**2. The "10–45 s" question is attributed to the goal page, which does not contain it.**
- **Location:** README l.158–159, *"The goal page asks whether shared modulation on timescales of 10–45 s counts as coordination."*
- **Issue:** `docs/goals/unsupervised-learning.md` never says "10–45 s" and never poses that question. The wording is in `docs/learned/tube_self_supervised/README.md` l.395 (decision 2), `docs/MILESTONES.md` l.60 and `docs/todo/2026-09-16-land-pr-588-and-finish-the-rigid-shift-report.md` l.103. The page intro (l.5–7) repeats the goal-page framing.
- **Suggested fix:** cite the rigid-shift report's "What waits on Tony" item, *"Does shared modulation on timescales of 10–45 s count as coordination?"*, and the MILESTONES row. Keep the goal page as the thread link only.
- **Verified:** yes

**3. The page contradicts the rigid-shift report without saying so.**
- **Location:** README l.158–162 and l.78–83, against `tube_self_supervised/README.md` l.74–76 and l.395–397.
- **Issue:** the rigid-shift report says *"Rigid shift at 10–20 s removes it"* (10–45 s modulation) and that shared modulation is *"absent on the lab fast stream (flat at 0.50)"*. This page measures two things that conflict with that:
  - Rigid shift removes only modulation faster than about *J*, so a 20 s *J* cannot remove 45 s modulation.
  - Lab fast does have a shoulder; it is drift that rigid shift leaves alone.

  Both reports can be true, since the report's "absent" is about what a classifier can detect, not about whether shared structure exists. But a reader holding both sees a flat contradiction.
- **Suggested fix:** add one sentence naming the report's two claims and saying how this page revises each. Then update the report or its MILESTONES row in the same change, or file the discrepancy.
- **Verified:** yes

**4. The "1 s cut" is really 1.35 s.**
- **Location:** README l.125–127 ("share at lags beyond 1 s is 0.91 … 0.71 … 0.86") and l.190 ("The 1 s cut").
- **Issue:** `peak_and_shoulder` in `tools/measure_slow_comodulation.py` l.379–380 splits bins by their lower edge (`lo < cut_sec`). No edge falls at 1.0 s: the bin from 0.965 to 1.352 s counts as "under". So the published shares are for lags beyond 1.35 s.
- **Suggested fix:** either say "beyond 1.35 s (the bin edge nearest 1 s)", or put an edge at exactly 1.0 s and rerun.
- **Verified:** yes

**5. CoactDetect removal takes most of the slow-stream shoulder, and the page never says so.**
- **Location:** README l.115 ("Every folder has both a peak and a shoulder"), l.163–165, and table rows 5–6.
- **Issue:** the page's own table shows lab slow at +0.15 (20–28 s) and +0.16 (56–78 s) as recorded, but +0.09 and +0.05 with CoactDetect episodes removed. That removes two-thirds of the shoulder at a minute. `summary.json` agrees: the excess beyond the cut falls from 368,409 onset pairs to 32,766. The prose says only the fast shoulder is "unchanged by removing CoactDetect's episodes". It still counts slow as having a shoulder, and says a slow-stream contrast rewards "the part of the shoulder faster than *J*".
- **Suggested fix:** state the slow-stream removal result next to the fast one. Qualify "every folder has a shoulder" for slow, where much of the shoulder goes with the episodes.
- **Verified:** yes

**6. The generator's docstrings state claims the page refutes.**
- **Location:** `tools/measure_slow_comodulation.py` l.9–11, l.30–32 and l.72–74.
- **Issue:**
  - The docstring says *"because rigid shift at 10–20 s removes both"* (events and slow modulation). The page finds drift passes untouched and events are spread, not removed.
  - The `BLOCK_SEC` and `block_120` docstrings say the block control removes *"everything faster, events and minute-scale modulation alike"* and that real minus block *"is the shared structure faster than 2 minutes"*. The page's ⚠ note (l.85–87) and "What this does not settle" (l.198–199) measure the block control keeping about +0.15 of +0.75 in the 20 s world.

  The tool ships with the page, so a reader of the code gets the hypothesis the page overturned.
- **Suggested fix:** rewrite the three docstrings to match the measured behaviour and point to the page.
- **Verified:** yes

**7. Two cross-references cannot be checked against anything in the tree.**
- **Location:** README l.168–174.
- **Issue:**
  - `count_excess` ("the zero-parameter baseline in the rigid-shift report … subtracts a 30 s moving mean") appears nowhere else in the worktree: not in `tube_self_supervised/README.md`, not in `tools/` or `src/`.
  - *"The session running the rigid-shift report confirmed this independently … and is carrying it in that report"* also has no file behind it.
- **Suggested fix:** name the branch and file where `count_excess` and the confirmation live, or cut both to "argued, not checked here" until they land on `main`.
- **Verified:** no (checked for absence only)

**8. New terms are not in the glossary.**
- **Location:** throughout the page, against `docs/GLOSSARY.md`.
- **Issue:** these terms carry the argument and have no glossary entry: *excess coincidence*, *population cross-correlogram*, *peak* / *shoulder*, *block control* (2-minute block control), *circular shift* as a named surrogate arm, *shared modulation* versus *shared drift*, and *co-modulation*. The rule is that a new term enters the glossary in the same change.
- **Suggested fix:** add them under "Surrogate vocabulary", or a new "Cross-correlogram vocabulary" section, in this PR.
- **Verified:** yes

## Minor findings

**9. The same-ROI floor range mixes two folders.**
- **Location:** README l.135.
- **Issue:** "2.80–3.20 s on the slow stream" joins two values from different folders. The goal page l.78 gives 3.20 s on the *senktide baselines* and 2.80 s on the *field-step-excluded* folder, which is the one this page uses. It also marks both as *"measured by a review role — reproduce before building on it"*. A floor of 2.8 s also does not by itself explain a deficit that reaches 5.2 s.
- **Suggested fix:** quote 2.80 s for `steps_excluded`, carry the goal page's caveat, and note that the dip reaches past the floor.
- **Verified:** yes

**10. "Flat from about 3 s" does not match the table.**
- **Location:** README l.121–122 ("+0.05 to +0.09 … flat from about 3 s out to a minute").
- **Issue:** the table's 2.7–3.7 s bin is +0.15 [+0.10, +0.25], and it drops to +0.10 with episodes removed. The Figure 3A bottom panel shows the same bump. The range and "unchanged by removing CoactDetect's episodes" hold only from 3.7 s.
- **Suggested fix:** say "from about 4 s", or mention the 3 s bump.
- **Verified:** yes

**11. The rigid-shift report's gloss of *J* conflicts with the glossary.**
- **Location:** README l.23 ("*J*, the displacement radius").
- **Issue:** GLOSSARY l.356 defines *J* as "jitter radius: how far a dither may move one onset". The page follows the rigid-shift report's "displacement radius" instead. One reserved symbol now has two glosses.
- **Suggested fix:** update the glossary entry to cover rigid shift's use.
- **Verified:** yes

**12. The title term is never used, and the concept has many names.**
- **Location:** title and throughout.
- **Issue:** "co-modulation" appears only in the title. The body uses "shared slow modulation", "shared modulation", "shared drift", "drift over minutes", "the drift world", "the 5-minute world" and "shoulder".
- **Suggested fix:** define "co-modulation" once as the umbrella term, or retitle, and use one name per world.
- **Verified:** yes

**13. "Folder", "stream" and "export" are used loosely.**
- **Location:** README l.115, l.93, l.98.
- **Issue:** "Every folder has both a peak and a shoulder" covers three curves from two folders. The lab source is called "the lab export" (l.93) and "lab folder" (l.98).
- **Suggested fix:** "Every stream and folder…", and pick one name for the lab source.
- **Verified:** yes

**14. One arm has two names.**
- **Location:** Figures 2–4 legends and y-labels versus the table and prose.
- **Issue:** the figures say "circular shift within 2-minute blocks"; the table and prose say "2-minute block control". Only the Figure 2 caption connects them.
- **Suggested fix:** use one label, or put "(block control)" in the legend.
- **Verified:** yes

**15. The *J* levels are listed in different orders.**
- **Location:** README l.64 versus the Figure 2 and 3 legends.
- **Issue:** the prose lists *J* as 1.6, 10, 20 s. Both legends list 20, 10, 1.6 s (`ARMS_SYN` and the `fig3` loop).
- **Suggested fix:** use one order everywhere.
- **Verified:** yes

**16. The slow rows lack the rigid-shift row that the prose quotes.**
- **Location:** table versus l.136–137.
- **Issue:** lab fast has a "rigid shift *J* 20 s" row, lab slow has none, yet the prose quotes slow rigid-shift values "in `summary.json`".
- **Suggested fix:** add slow *J* 10 s and 20 s rows.
- **Verified:** yes

**17. The Figure 1 raster is a cropped window labelled from zero.**
- **Location:** Figure 1 caption, "1,200 s … one recording's raster".
- **Issue:** `fig1` draws t0=60 to t1=1140 s, an 18-minute crop, with ticks relabelled to start at 0s. The caption implies the full 1,200 s.
- **Suggested fix:** add "middle 18 minutes shown" to the caption.
- **Verified:** yes

**18. The events world is busier than the caption says.**
- **Location:** Figure 1 caption, "0.0097 onsets per ROI per second".
- **Issue:** the events world adds 224 planted onsets on top of that rate (`synthetic_recording`), which gives about 0.0155 per ROI per second.
- **Suggested fix:** say the base rate is 0.0097 and the events are added on top.
- **Verified:** yes

**19. The per-ROI control is not drawn "how `simulate.py` draws" it.**
- **Location:** Figure 1 caption, "which is how `src/bugarach/simulate.py` draws its background".
- **Issue:** the control uses one Ornstein–Uhlenbeck log-normal multiplier on a 20 s timescale per ROI. `simulate.py` l.762–765 draws piecewise-constant gamma multipliers at several scales per ROI. They are the same kind (per ROI) but a different mechanism.
- **Suggested fix:** "the same kind as…", not "how".
- **Verified:** yes

**20. Baseline length is stated as a flat 20 minutes.**
- **Location:** README l.200 ("20 minutes of baseline per recording").
- **Issue:** `recording_identity.md` l.17 gives analysis windows of 17–20 min. The mean here works out to about 19.9 min before trimming (26.88 h over 84 recordings, plus 40 s). Cossart is read whole, at about 24 min.
- **Suggested fix:** "17–20 minutes (lab); whole recordings, about 24 minutes (Cossart)".
- **Verified:** yes

**21. "26.9 hours analysed" is ambiguous.**
- **Location:** Figure 3 caption.
- **Issue:** after "the fast and slow streams", 26.9 hours reads as a total. It is per stream: each stream sums to 26.88 h.
- **Suggested fix:** "26.9 hours per stream".
- **Verified:** yes

**22. Pair counting basis.**
- **Location:** README l.29 ("For every pair of distinct ROIs") and l.125 ("Of all excess onset pairs").
- **Issue:** the code counts *ordered* ROI pairs (`pair_counts`, docstring l.13). At lag 0 each onset pair is counted twice; at longer lags, once. The ratio is unaffected. The excess-pair counts in the share figures are not: zero-lag pairs weigh double in "under", so the shares slightly understate the beyond part. The slow stream's negative dip also subtracts from "beyond", so its share is a net figure.
- **Suggested fix:** state "ordered pairs, net of deficits", or correct the zero-lag weight.
- **Verified:** yes

**23. Surrogate curves are not "means over draws".**
- **Location:** README l.202.
- **Issue:** `arms_for` averages observed and expected counts over draws, then divides. That is a ratio of pooled counts, not a mean of curves.
- **Suggested fix:** "pooled over draws".
- **Verified:** yes

**24. "Nothing changes" at *J* = 1.6 s is slightly strong.**
- **Location:** README l.80.
- **Issue:** the 20 s world goes from 0.745 to 0.691 at the shortest lag.
- **Suggested fix:** "little changes (+0.75 → +0.69)".
- **Verified:** yes

**25. The Cossart dip is visible but not mentioned.**
- **Location:** README l.117–118 and l.132.
- **Issue:** Cossart reads −0.05 [−0.08, −0.01] at 3.7–5.2 s, visible in Figure 3C. It does not just "fall to zero", and only the lab slow dip is discussed.
- **Suggested fix:** mention the small Cossart dip.
- **Verified:** yes

**26. The header's interval promise does not cover the synthetic numbers.**
- **Location:** README l.4 ("Numbers carry a 95 % interval from resampling mice").
- **Issue:** the synthetic-world numbers (l.54 and l.76–86) carry no interval, and their "mice" are recordings.
- **Suggested fix:** scope the header to the recordings.
- **Verified:** yes

**27. The §9 group rule is applied to only two arms.**
- **Location:** README l.140–152, against FOUNDATIONS §9 ("a pooled across-group number … is not admissible on its own").
- **Issue:** Figure 4 splits only the as-recorded and block-control arms. The pooled claims about CoactDetect removal, rigid shift and the slow dip have no group split.
- **Suggested fix:** state that those arms were not split by group, or add them to Figure 4.
- **Verified:** yes

**28. The §5 reading needs a precedent or a ruling.**
- **Location:** `summary.json`, Figures 3–4, and `tools/make_slow_comodulation_figure.py` l.19–20.
- **Issue:** FOUNDATIONS §5 l.127–130 reads *"Real stores (and anything derived from real data) stay machine-local"*. The tool justifies committing pooled real-derived curves as "no real raster". There is precedent (the repo copies in `recording_identity/` and the rigid-shift look), but the page's reading is narrower than §5's text.
- **Suggested fix:** cite the precedent or ruling that allows pooled curves in the repo, or flag it for Tony.
- **Verified:** yes (text); no (ruling)

**29. §9 is misdescribed.**
- **Location:** README l.182 ("FOUNDATIONS §9 sends such questions to the lab").
- **Issue:** §9 names `syncytium2/foundations` FOUNDATIONS §15 as the authority on the preparation. Questions about extraction go to the producer (CLAUDE.md, export folder rule).
- **Suggested fix:** "§9 defers to the global FOUNDATIONS §15; extraction questions go to the producer".
- **Verified:** yes

**30. Darkroom path notation differs from companion docs.**
- **Location:** README l.214.
- **Issue:** the page writes `<darkroom>/2026-09-17-slow-comodulation/`. The goal page, the rigid-shift look and `recording_identity.md` write `<darkroom>/bugarach/<dated folder>/`. `darkroom()` does resolve to the bugarach subfolder, so the page is correct, but the notation is inconsistent.
- **Suggested fix:** use `<darkroom>/bugarach/2026-09-17-slow-comodulation/`.
- **Verified:** yes

**31. "Darkroom only" is not enforced by the tool.**
- **Location:** README l.213 ("`results.json` (per recording, darkroom only)").
- **Issue:** the tool writes `results.json` to whatever `--out` is given. `--out` is required and has no darkroom default, so nothing enforces "darkroom only".
- **Suggested fix:** say "put `<dir>` in the darkroom", or default `--out` to `darkroom()`.
- **Verified:** yes

**32. Companion docs are left stale.**
- **Location:** goal page, `tools/measure_slow_comodulation.py` l.93–95, `recording_identity.md` l.16, `docs/SESSIONS.md` l.19–20.
- **Issue:**
  - The goal page has no pointer to this page yet; SESSIONS says one will be added at landing. The goal page's "Twenty-two hours of baseline recordings" (l.20) matches neither lab stream (26.9 h) nor the lab-plus-Cossart total.
  - The generator's `SYN` docstring cites "CoactDetect's 2.70 events per 10 minutes" on lab fast, but `summary.json` records a median of 1.0 per 10 minutes at the same operating point. The 2.70 is the rigid-shift report's number, and its statistic is not stated.
  - Group order is DI/MALE/ORX/OVX here but ORX/MALE/OVX/DI in `recording_identity.md` and DI/MALE/OVX/ORX in `tools/make_assembly_figure.py`. The glossary fixes no canonical order, and Figure 4's order comes from `sorted()`, not a declared order.
- **Suggested fix:** add the goal-page pointer in this PR and fix its hours line. Correct or source the 2.70. Declare a group order in the glossary.
- **Verified:** yes

**Also (not numbered):** "In Figure 2's terms" (l.124) gives the figure number without its name. Figures 1 and 2 are referenced correctly elsewhere.
