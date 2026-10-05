GRANT 8 ok — Read, Grep, Glob (also holds SubagentHandback, the hand-off channel only; no editing tool)

# Role 8 — You Lost Me: final-parameters night report

**Reviewed:** `<worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md` plus the four PNGs beside it (`figure1_fresh_f1.png`, `figure2_cross_stream.png`, `figure3_elevated_rate.png`, `figure4_bench_floors.png`), all four opened. Each section was read cold, then terms were checked against `...\floor-and-grids\docs\GLOSSARY.md`. No file was edited.

**Overall:** three sections are blocking — "In one paragraph", the table key and the adoption table — mainly an ordering problem. The summary paragraph uses about ten terms that are defined only afterwards in the table key, or never. Three terms (`cap`, "extension cap", "decoy") are defined nowhere on the page or in the glossary. Separately, the page reintroduces three names the glossary retired or contradicts: "probe", "crowded" and "empty".

## Per-section verdict table

| # | Section / panel | Terms and identifiers first used here | Defined here? | Cold reader follows? |
|---|---|---|---|---|
| S1 | Title, "Nothing here is adopted" and "Floor" paragraph (L1–13) | `bench*.py`, operating point, runbook, ADR-0008, ADR-0009, floor, minimum participation, ROIs, rigid-shift null, *J*, co-activity window, "don't care", recall, precision | Floor and "don't care": yes (good). *J*, rigid-shift null, ROI: no. The ADRs are named by number only; what they decide is visible only in the link slugs. | **no** — two undefined terms, not blocking. "Floor" also collides with the glossary's other floor (the provisional within-ROI interval *f*, glossary L476). |
| S2 | "In one paragraph" (L15–30) | adoptable, strict rule, binned SCE, SCE, fast/slow/combined (streams), rate+context, SPIKE-synch, locust, CoactDetect, LoCo, held-out gain, 95% interval, budget, selection seeds, fresh seeds, "inside its grid on every axis", "a value that cannot go further", extension cap, grid edge, close-events recordings, shipped points, "out of budget under the floor" | Almost none. Held-out, fresh, budget and bracketed are defined only in the next section; extension cap and grid edge never; SCE and "stream" never expanded. | **BLOCKING** — 10+ terms before their definitions. |
| S3 | Table key (L32–58) | seeds (as recordings), bootstrap, background, quiet, busy, "the training", decoy calls, ADR-0006, elevated-rate stretch, `MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, no-coordination "(empty)" recording, `MAX_PRECISION_DROP`, precision swing, close-events recordings, `MAX_CROWDED_DROP`, "search's own gate", bracketed (strict), limit, guard, final grid, participation level, chorus, checkpoint, "training rule's anchor" | Held-out, fresh, bracketed and limit: yes. Not defined: decoy, elevated-rate stretch, close-events recordings, guard, "the search's own gate", chorus, participation level, what "training" is. | **BLOCKING** — at least 6 undefined terms. |
| S4 | Adoption table (L60–87) | `rounds:`, `pair:`, ~20 parameter identifiers (`alpha`, `context_win_sec`, `threshold_pctile`, `sce_min_distance_frames`, `n_synchronous_frames`, `guard_sec`, `C_min`, `null_context_mode maxlt`, `tau_mode isi_adaptive`, `dt`, `max_gap`, …), `cap`, `edge`, `fail: crowded`, `fail: precision_swing`, `fail: probe`, `picked seed1`, `chorus_norm`, `chorus_gain_norm`, "10%: 120 under" | `limit`/`edge` covered by the key; `cap`, rounds/pair and the percentage levels are not; no plain-language gloss for any identifier. | **BLOCKING** — this is the decision surface, and `cap` alone decides four rows. |
| S5 | Figure 1 | dumbbell per detector × stream; shipped (circle); proposal (diamond, blue/orange); chorus (grey) | yes | **yes** (minor: F1 never expanded) |
| S6 | Figure 2 | "the 3 × 3", tuned-on / scored-on, `candidates.json`, "38 of 38", "114 cells", `adoption.json` `cross_stream` | Axes: yes. Counts and reading direction: no. | **no** — F9, F10 |
| S7 | Figure 3 | elevated-rate recording, stretch, WSMIP065, seeds 66000–66011, per-detector budget bars, symmetric log scale, "SCE" | Purpose of the recording not given; why budgets differ per detector not given. | **no** — F11–F13 |
| S8 | Figure 4 | recording kind, floor range over 8 seeds, ADR-0009 expected range, elevated-rate recording (triangle with dotted line), no-coordination recording (grey tick), participants per planted event | Left panel partly; right panel yes. | **no** — F14, F15 |
| S9 | "What waits on Tony" items 1–6 and smaller items | hard limit, `n_synchronous_frames`, `guard_sec`, `C_min`, probe, admissible neighbour, "run record of phase 2", `min_rois`, extension cap, round-1, pair grid, guard cap, "chance does not reach" | Partly | **no** — only item 1 is phrased as a question; F16–F20 |
| S10 | Real data (L194–198) | "66 recordings", "both floors", `tools/detect_with_floors.py`, WSMIP065, `065/report-inputs/` | "Both floors" undefined; the page defines only one floor. | **no** (minor section) |
| S11 | What ran (L200–220) | PR A, PR B, WSMIP064, WSMIP065, phases 0–4, `--sliding`, `--max-extensions 6` | Provenance only | **yes** as a record (minor: WSMIP064/065 never identified as machines or sessions) |

## What a cold reader sees in each figure (caption covered)

- **Figure 1:** three panels, one per stream; a row per detector with an open circle joined by a grey line to a diamond (blue = adoptable, orange = not, grey = chorus). Readable as-is.
- **Figure 2:** eight blue 3 × 3 heatmaps with numbers, bold on the diagonal. Resembles a confusion matrix (F9).
- **Figure 3:** six strip plots of coloured circles and triangles, filled or open, on a log-like axis with a zero row, beside short black bars at a different height for each detector.
- **Figure 4:** left, small coloured bars inside grey bands, with down-pointing triangles and dotted tails above and short grey ticks below; right, bars of the percentage of events under the floor at each participant count, grouped by stream and background.

## Findings (location · issue · severity · suggested fix · verified against a source)

**F1 · S2 "In one paragraph", L17–30.** Uses held-out gain, selection/held-out/fresh seeds, budget, "inside its grid", "strict rule", extension cap, grid edge, close-events recordings and "out of budget under the floor" before any is defined; the definitions come in the next section, or never. Tony reads this paragraph first and decides from it. **Blocking.** Fix: an inline gloss of a few words at first use (e.g. "held-out gain (F1 gain on seeds nothing was chosen on)", "the close-events test (a recording with events as little as 6 s apart)"), or move the key above it. **Verified: yes** (page text).

**F2 · S2 L24; S4 `cap` cells; S9 item 3.** "Extension cap" and `(cap)` are defined nowhere, on the page or in the glossary. The key defines "edge" and "limit" but not "cap", although cap is what holds back four proposals; the only clue is `--max-extensions 6` at the very end. **Blocking.** Fix: a key line — "**cap**: the search extended this axis's grid the maximum 6 times (`--max-extensions 6`) and the chosen value sits at the last extension" — and give the cap value for `alpha`. **Verified: yes** (glossary grep finds no match).

**F3 · S3 L38 "without decoy calls (calls on decoys left out of precision, ADR-0006)"; table header "without decoys".** "Decoy" is never defined, and the glossary has no "decoy"; its nearest term is **distractor** (glossary L375). The reader cannot tell whether they are the same thing. **Major.** Fix: one clause ("a planted correlated burst that is not a coordinated event"), and either use the glossary word or add "decoy" to the glossary as a synonym. **Verified: yes.**

**F4 · S3 L45 "no-coordination (empty) recording".** The glossary says explicitly: *Not "empty": the cells are active throughout* (L424); this parenthesis reintroduces the retired, misleading word. **Moderate.** Fix: drop "(empty)"; "no-coordination recording (cells active, nothing coordinated planted)". **Verified: yes.**

**F5 · S4 cells `fail: probe`, `fail: crowded`; S9 item 2 "probe (calls per minute…)"; Figure 4 in-image caption `probe_bench_floor.py`.** "Probe" and "crowded" are retired names: the glossary renamed them *elevated-rate test* and *close-events test* on 2026-09-21 because "'probe' said nothing". The table shows raw code tokens (`precision_swing`) where the key uses prose ("precision swing"). **Moderate.** Fix: "fail: elevated-rate", "fail: close-events", "fail: precision swing". Tool filenames can stay. **Verified: yes.**

**F6 · S3 L42–47, L50.** Several terms are named but not explained:
- "The elevated-rate stretch" is used before it is said what it is (a 5-minute stretch in which each cell's independent event rate is raised about 12×, with no planted events).
- "Close-events recordings" are never described.
- "Precision swing" first appears at L50 as a bare noun, not as the name of L46's "precision difference".
- "The search's own gate" is undefined.
- Limit values are given only for the close-events test (0.02).

**Major.** Fix: one plain clause per budget (what the recording is, what a call there means, the limit value); name the term at L46 ("the precision difference … — the *precision swing*"); and say why the precision-swing limit is 0.10 on fast but 0.15 on combined (item 2's table). **Verified: yes.**

**F7 · S4, "settings that change" column.**
- About twenty internal parameter identifiers carry no plain-language meaning, e.g. `sce_min_distance_frames` 4 → 128 (128 what?), `null_context_mode maxlt → symmetric`, `tau_mode isi_adaptive → fixed`, `dt` 0.1 → 0.00625 (unit?). In an adoption record the identifiers are the payload and should stay, but a later reader cannot tell what any change *does*.
- `rounds:` and `pair:` are undefined.
- The bracketed column cites axes (`guard_sec`, `C_min`) that the changes column does not show, so their value (0?) is invisible.

**Major.** Fix: a short legend under the table, one line per identifier with its concept and unit (e.g. "`sce_min_distance_frames` — minimum gap between locust calls, frames at *x* s/frame"); define `rounds` and `pair`; show the value of any axis the bracketed column cites. **Verified: yes.**

**F8 · S4, "fresh F1" and "under the floor" columns; `picked seed1`.**
- "0.769 → **0.809** / 0.956" puts three numbers under a two-part header; it does not say whether "without decoys" belongs to the proposal or the shipped point.
- "Seed" means two things: bench seeds (1–48, 49–96, 6000–6023) are simulated recordings, while `seed1` in the chorus rows is a training seed.
- "10%: 120 under" gives participation as a percentage, while Figure 4 and item 6 give participant counts (3, 6, 10 ROIs), with no conversion (house units rule).

**Major.** Fix: relabel "shipped → proposal (as scored) / proposal without decoys"; write "training seed 1"; give levels as "10% (3 ROIs)" or add a conversion line. **Verified: yes.**

**F9 · Figure 2 — false-friend check.**
- It resembles a **confusion matrix**: bold diagonal, blue tiles, rows × columns.
- In that idiom rows are the true class and columns the predicted class; the diagonal is "correct" and off-diagonal mass is error, so an off-diagonal cell brighter than the diagonal reads as a problem.
- Here rows are the stream a version was tuned on and columns the bench it was scored on. Columns differ in difficulty (slow is darkest in almost every panel), so an off-diagonal cell above the diagonal (rate+context tuned on combined, scored on slow: 0.87 against 0.77 on the diagonal) is expected, not a transfer anomaly.
- The only valid comparison is *down a column*, and nothing tells the reader so. A fluent reader will read across rows and conclude that tuning on combined "transfers better than it fits".

**Major.** Fix: redraw so a column comparison is what the eye makes (e.g. colour each column relative to that column's diagonal — a difference from the tuned-on-this-bench version), or state in the caption "compare down a column; columns differ in bench difficulty". **Verified: no** (a judgement about how the figure will be read).

**F10 · Figure 2 caption, L108–109.** "38 of 38" and "all 114 cells" match nothing a reader can count: the figure shows 8 panels × 9 = 72 cells, 24 of them diagonal. `candidates.json` is an internal filename. **Moderate.** Fix: say what the 38 and the 114 count (e.g. "per background, including …"), and write "the search's recorded fresh-seed F1" instead of the filename. **Verified: yes** (counted from the render).

**F11 · Figure 3 caption, L115–120.** "The elevated-rate recording (ADR-0009 decision 1)" never says what it is or what a call inside the stretch means (a detector keying on rate rather than on coordination). Budget bars differ widely by detector (1 to ~70 calls/min) with no reason given. "WSMIP065" is an internal machine name. **Major.** Fix: one sentence — "a 5-minute stretch where each cell's independent event rate is raised ~12×, with no coordinated events; a call there is a rate-driven false alarm" — plus where each detector's budget comes from; replace or gloss WSMIP065. **Verified: yes** (glossary L366).

**F12 · Figure 3 legend.** Three encodings stack: colour = detector (redundant with the x-axis), filled/open = background, circle/triangle = shipped/proposal. The legend glyphs for "shipped point" and "quiet background (filled)" are the same dark filled circle, so the key is ambiguous. **Moderate.** Fix: draw the shape key with open grey outlines, and drop the redundant detector-colour legend or say colour only repeats the x label. **Verified: yes** (render).

**F13 · Figure 3 y axes.** On the symmetric log scale, the linear region between 0 and 10⁻¹ makes marks at ~0.01–0.05 look like "nearly zero", on a par with true zeros; a cold reader cannot tell 0 from 0.02 calls/min. **Minor.** Fix: mark the linear/log break, or annotate the non-zero near-zero values. **Verified: yes** (render).

**F14 · Figure 4 left panel.** The elevated-rate recording is drawn as a down-pointing triangle with a dotted tail. Under the house convention a down triangle means "look below", so it reads as a pointer to the bar underneath, not as a data range. The caption never says why the elevated-rate recording's floor matters (it sits at 16–20, far above everything else). **Moderate.** Fix: a plain range mark (bar or line with end caps), like the other recording kinds, and a clause on why this floor is shown. **Verified: yes** (CLAUDE.md plot conventions).

**F15 · Figure 4 vs the table's "under the floor" column.** Figure 4 counts 40 events per level; the table counts 120. These are different seed sets (8 re-measure seeds against 24 fresh seeds), and neither says so. A reader comparing "40/40" with "120 under" will think one of them is wrong. **Moderate.** Fix: name the seed set by each count ("8 seeds × 5 events" in Figure 4; "24 fresh seeds × 5" in the table). **Verified: yes.**

**F16 · S9 heading "What waits on Tony" and L29 "Six questions go to Tony".** Only item 1 is written as a question; items 2–6 are findings, and the reader cannot tell what decision is asked for. Item 5 ends "The rule is the runbook's, not an ADR's"; item 6 ends "as ADR-0009 anticipated". **Major.** Fix: open each item with its question in bold (e.g. item 5: "Should the quarter-context guard cap stay, given it excludes 8 s guards at 20–30 s contexts?"). **Verified: yes.**

**F17 · S9 item 4.** "Round-1 candidate", "the pair grid" and "extended below the 20 s grid" are undefined; the paragraph gives facts (5 s vs 20 s) without the decision or why it matters. I could not work out what is asked. **Major.** Fix: define the search's rounds and pair grid (they also appear as `rounds:`/`pair:` in the table) and state the question, e.g. "Should a context below 20 s be allowed, since ADR-0009 set no minimum?". **Verified: yes.**

**F18 · S9 item 5.** "Guard" is defined nowhere (guard on what?). "At contexts of 20 s and 30 s (quarters of 5 s and 7.5 s)" is inverted — 5 s and 7.5 s *are* the quarters of 20 s and 30 s. **Moderate.** Fix: "at 20 s and 30 s contexts the cap is 5 s and 7.5 s, so an 8 s guard is never searched", and define guard in the table key. **Verified: yes.**

**F19 · S9 item 6, L184.** "Recall there is measured on the events chance does not reach" is hard to parse, and the item mixes participant counts ("3 ROIs on fast") with the table's percentage levels. **Minor.** Fix: "recall at these levels now counts only the events above the floor", and give both units once. **Verified: yes.**

**F20 · S9 items 1–3.** Concepts are named by identifier alone (`n_synchronous_frames` at 1, `guard_sec` 0, `C_min` 0, `min_rois`), and "The diagnosis is in the run record of phase 2" has no path. **Moderate.** Fix: name each concept in plain words first, then the identifier (e.g. "locust's required run of synchronous frames (`n_synchronous_frames`) is at its minimum, 1"), and link the phase 2 record. **Verified: yes.**

**F21 · S10 Real data.** "Every window under both floors" — the page defines only one floor, so "both" has no referent. **Moderate.** Fix: name both floors (e.g. "the ADR-0008 per-window floor and <the other>"). **Verified: yes.**

**F22 · S1 L9–12.** "Rigid-shift null" and *J* are used without definition (per the glossary, *J* is the jitter/shift radius), and "floor" collides with the glossary's other floor (the provisional within-ROI interval *f*). **Minor.** Fix: "*J* = 20 s (each ROI's whole train shifted by up to ±20 s)", and "participation floor" once to set it apart. **Verified: yes** (glossary L468, L476).

**F23 · Page-wide.**
- SCE, F1 and ROI are never expanded (house rule: define every abbreviation).
- "Stream" is never defined.
- Chorus is never said to be a learned model.
- WSMIP064/065 and PR A/PR B are internal handles with no gloss.
- Figure 3 labels the detector "SCE" where the text says "binned SCE".

**Minor.** Fix: expand at first use; one clause each for "stream" and chorus ("the learned detector trained on the bench"); "binned SCE" in Figure 3. **Verified: yes.**

## Tone check
Sentence case is consistent; no ALL-CAPS; no lists smuggled into titles. Only Figure 3's legend packs two rules into one entry ("top row gates both backgrounds, bottom row the quiet one only"), and it is readable. No finding.

## Outside my role (for the numbers team, not re-checked by me)
The page shows "38 of 38" and "114 cells" against 72 drawn cells. L24 files LoCo on fast and slow under "the extension cap or a grid edge", while the table gives LoCo-fast only cap and limit, no edge.
