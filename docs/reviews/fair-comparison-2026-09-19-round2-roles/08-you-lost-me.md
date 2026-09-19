<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 8 ok — Read, Grep, Glob

(I also hold SubagentHandback, which only delivers this report. I hold no Edit, Write or NotebookEdit tool, and I edited nothing.)

# Role 8, "You Lost Me": fair-comparison report (built HTML, 16ac704)

**What I checked:**
- The whole built page: all body text of `report.html`, read through a length-filtered grep because the inline SVG lines are too long to open directly.
- Every render in `renders_round2/`: fig1–fig8 and table1–3. `page_full_1100px.png` is too small to read at the size it displays, so I used the individual renders instead.
- The table captions, read from `tools/build_fair_comparison_report.py` because the rendered captions sit on SVG-length lines.
- Two source checks: `src/bugarach/score.py` (how calls are matched to events) and `docs/GLOSSARY.md` (what a distractor is).
- Reader: a neuroscientist who knows calcium imaging and basic statistics and has never seen this project.

## Verdict per section and figure

| Where | Terms or identifiers first used here | Defined here? | Can a cold reader follow it? |
|---|---|---|---|
| Title, the line under it, and "The question / The answer" | coordinated event, coded detector, net, F1, CoactDetect, merge, call, **folds** ("4 of 4 folds"), **fast stream**, **baseline periods**, **chorus_norm**, **binned SCE**, workstation, "re-scored at matched gaps" | Coordinated event, coded, net and F1 are defined (F1 in the next paragraph). Not defined: folds, fast stream, baseline periods, chorus_norm, binned SCE. Merge and call are only implied. | **BLOCKING.** At least 5 undefined terms in the most-read paragraph. |
| "Terms used throughout" paragraph | ROI, F1, recall, precision, GPU, *t*, **outer folds**, goal 1, project lead | All except "outer folds", which is used inside the definition of *t* | yes |
| §1 and Figure 1 (raster) | raster, tick, distractor, probe, "18% planted event", quiet or busy background, "events" (used two ways) | Raster, distractor and probe are defined. The 18% participation level and the two backgrounds are only explained in §2. **"Event" means both one cell's firing and a coordinated event.** Why a distractor counts as a negative is not explained. | yes, with friction. Figure 1 is a real raster (x is time, rows are ROIs), not a false friend. |
| §2 | bench, recording seed, background, hit, tolerance, probe false alarms | yes | yes, but the hit rule contradicts Figure 5A (finding F2) |
| §3, Table 1, the warning box | sliding window, binned, "circularly shifted" / "shifted" / "rolled" (three words for the null model), CICADA, "ROIs lit", draughtsman, `<darkroom>`, PR #660 | Sliding and binned are explained later, in §4.3. The null model is never explained or drawn. CICADA, draughtsman and darkroom are not defined. | yes for the table. **No for the nets' mechanism: it is named, not shown** (F4). |
| §4.1 and Figure 2 (fold grid) | nested cross-validation, outer fold, inner loop, training seed, configuration, **"context-window rule in section 4.5"** | All except that rule, **which §4.5 never states** | yes, apart from the dangling rule reference (F3) |
| §4.2 and Figure 3 (fitting draws) | fitting set, threshold recordings, refit | yes | yes. The tiled strips read correctly. |
| §4.3 | counting mode, binned or sliding, alpha, context window, guard, LoCo percentile, merge gap | Merge gap is used here, but its bold definition only comes in §4.5 | yes |
| §4.4 and Figure 4 (schematic scatter) | shared false-alarm budget, 1.6× margin, "a floor that bound in no fold" | yes. "Bound", meaning a constraint was active, is statistician's jargon. | yes |
| §4.5 and Figure 5 | merge gap, crowded recordings, "the setting it replaces", "threshold picker", **"re-decoded"**, "the other workstation" | "Re-decoded" is not defined. "The other workstation" is only introduced in §5. | A (schematic): partly, see F2 and F5. B (curves): yes, see F9. |
| §5 and Figure 6 (seed strips) | replicate, WSMIP064 / WSMIP065 | These are machine hostnames and mean nothing to a reader | yes. The figure says little beyond "the two sets don't overlap", but it reads correctly. |
| §6, Table 2, Figures 7 and 8 | corrected *t*, **"not admissible"** or "no admissible setting", "failed to train", "failed-training signature" | "Admissible" first appears in Table 2 and the Figure 7 legend and is never defined | yes, apart from the admissible gap (F6) |
| Table 3 | crowded F1 of the choices (shown as ranges), folds passing | The ranges are not explained (min–max over folds?) | yes, with friction |
| §7 Limits | **fast / slow stream**, `steps_excluded`, `HANDOFF-…md decision 3`, commit 2120516, **"0.18"** (of what?), "6 median participants", **BENCH_RECORDING**, **"Tony"** | Streams are only named ("fast and slow"), not explained. The third bullet is an internal note pasted in verbatim. | **BLOCKING.** The third bullet ("One of the bench's values sits outside…") has at least 4 undefined terms or identifiers. |
| §8 Where everything is | paths, `ARCHITECTURES[name].make()` | Aimed at developers | acceptable for a locations section |

## Findings

Each finding gives: **location · issue · severity · suggested fix · checked against a source?**

**F1. Lede ("The question / The answer") and the line under the title. BLOCKING**
- **Issue:** The paragraph a reader is most likely to read alone depends on terms defined sections later:
  - "4 of 4 folds" and "3 of 4 folds". Folds are defined only in §4.1, and the Terms paragraph defines *t* in terms of "outer folds" without saying what those are.
  - "fast stream" and "baseline periods" (only in §7).
  - "chorus_norm", a code name.
  - "binned SCE" (binned is explained in §4.3, SCE in Table 1).
  - "Call" is never stated as "a detector's claim that an event happened here".
- **Fix:**
  - Add "outer fold (one quarter of the recordings, held out for scoring; §4.1)", "call", "fast stream" and "baseline period" to the Terms paragraph.
  - In the lede, write "the best net (chorus_norm)" and "a bin-counting detector, binned SCE", or drop the names there.
- **Checked against a source?** No. This is a reading judgment.

**F2. §2 hit rule versus Figure 5, panel A. Major**
- **Issue:** §2 says "a call that spans a long stretch hits **any** event inside it". Figure 5A shows one merged call over three events and says "two events lost". A careful cold reader sees a contradiction and loses trust in the merge-gap argument that the headline rests on. The scorer is one-to-one: each call can match only one planted event (`score.py`, `score_detections`, the `used[j]` flag). So Figure 5A is right and the §2 sentence misleads.
- **Fix:** In §2, write "a call hits a planted event inside its widened span, and each call can hit at most one event; each event can be hit by at most one call".
- **Checked against a source?** Yes (`src/bugarach/score.py`, lines 219–239).

**F3. §4.1, "Settings that break the context-window rule in section 4.5 were skipped". Major**
- **Issue:** There is no context-window rule in §4.5, or anywhere else on the page. The phrase "context window" appears twice in the report: in this sentence, and in the §4.3 definition ("the stretch used to estimate chance"). The reader follows the pointer and finds nothing.
- **Fix:** State the rule where it is used (for example, "a context window must be at least N× the merge gap"). If it lives elsewhere, point there instead.
- **Checked against a source?** Yes (grep of `report.html`: 2 occurrences. Same sentence in the builder, line 884.)

**F4. §3, the warning box, and Table 1. Major**
- **Issue:** The owner asked for figures that explain what was done. The procedure is illustrated (Figures 2–5). The contestants are not:
  - The four nets, the subject of the question, get one sentence each in Table 1. The box says their drawings "are not on this page yet".
  - The coded side's null model is not drawn either. It is "the same recording shifted in time", also called "circularly shifted" and "rolled". Those three wordings suggest three different operations.

  A cold reader cannot picture a "bounded vote … pooled three ways", or "compares it with its own surroundings in time". The box itself uses internal words (draughtsman, `<darkroom>`, "PR #660, not yet on main"). Nothing in the report says what the darkroom is.
- **Fix:**
  - Embed the architecture drawings. Failing that, add one schematic panel: per-ROI vote versus pooled-first, the only distinction §3 says matters.
  - Add one small panel showing a circular shift as the chance estimate, and use one word for it throughout.
  - Define "darkroom" once ("the project's shared output folder") or move the paths to §8.
- **Checked against a source?** No.

**F5. Figure 5, panel A. False friend. Moderate**
- **Issue:** Panel A draws raw calls as short vertical ticks under blue down-triangles. That is exactly Figure 1's grammar, where a tick is one ROI firing and aligned ticks under a triangle are the planted event. A reader who has just learned Figure 1 sees "IIII under ▼" as the event's cells, not as detector output. The legend ("raw call") is read after the resemblance has already landed.
- **Fix:** Use a different mark for calls, such as short horizontal spans or open circles on a baseline. Label the rows "detector output". Keep ticks for cell firing only.
- **Checked against a source?** No. This is a render judgment.

**F6. Table 2, the Figure 7 legend, and §6. Moderate**
- **Issue:** "not admissible" and "no admissible setting" are used before any definition. The meaning (it fails the crowded-recording check, or the budget refused every setting) is only implied several bullets later. Table 2 shows binned SCE's 0.771 as the top score, with only "(4 of 4 not admissible)" beside it.
- **Fix:** In the Table 2 caption, add: "A result is not admissible when its choice fails the crowded-recording check (§4.5) or the budget refused every setting."
- **Checked against a source?** No.

**F7. §1, Figure 1 caption, §2. The word "event" has two meanings. Moderate**
- **Issue:** "Event" means both a single ROI's calcium event ("2,595 events in the whole recording", "0.0052 events per second per ROI") and a coordinated event ("15 planted events"). Both meanings appear in one sentence: "Finding the event means finding 6 aligned ticks among the 2,595 events". "Fire" is also used for both cells and detectors (§4.4).
- **Fix:** Call per-ROI occurrences "calcium events" or "firings". Keep "event" for coordinated events only. Say "call" for detectors.
- **Checked against a source?** No.

**F8. §1, distractor. Moderate**
- **Issue:** "A distractor is built exactly as an 18% planted event is built, and is labeled a negative." A cold reader asks what it represents, and how any detector could avoid it. The glossary's meaning ("real cross-ROI coincidence that is not a coordinated event … meant to be confusable") never reaches the page. "18%" is also used before participation levels are defined in §2.
- **Fix:** Add a sentence: it stands for a real but uncoordinated burst; by construction no detector can tell it from a planted event, so it costs every contestant alike. Also add "(an event joined by 18% of the ROIs; §2)".
- **Checked against a source?** Yes (`docs/GLOSSARY.md`, lines 334–337).

**F9. Figure 5, panel B. Minor**
- **Issue:** The x axis spaces 2, 4, 8, 16 and 30 s about equally and puts 0 s one step to the left. It is a log-like scale, but nothing says so. A reader who assumes a linear axis misjudges the slopes, including binned SCE's steep 16→30 s rise. The end labels are stacked, not placed at their lines: "chorus_norm" sits at about 0.79, but its line ends at 16 s, about 0.775.
- **Fix:** Label the axis as log-spaced or evenly spaced by doubling, or draw it linear. Put each label at its line's end, or add leader lines.
- **Checked against a source?** No.

**F10. §7, third bullet (the quoted declaration note). BLOCKING (under "limits")**
- **Issue:** "The bench holds 0.18; steps_excluded measures 0.1905 (6 median participants over 31.5 median ROIs) … BENCH_RECORDING's docstring …". The reader is never told what 0.18 is. It appears to be the middle participation fraction. The note also brings in an export-folder name, a code identifier and "awaiting Tony", while the rest of the page says "the project lead".
- **Fix:** Paraphrase: "The simulator's middle participation level is 18% of ROIs (6 of 33). The real data measure 19.05%, with a 95% interval down to 18.18% (= 6/33). The difference is a rounding, and changing it would shift every number, so it awaits the project lead's decision." Leave the verbatim note and its identifiers to the record.
- **Checked against a source?** No. I did not verify that 0.18 is the participation level.

**F11. §7 first bullet and the line under the title, "fast stream / slow stream". Moderate**
- **Issue:** Streams are only named ("two event streams (fast and slow)"). A calcium-imaging reader cannot tell what separates them: kinetics, signal source, detector family?
- **Fix:** Add one clause saying what each stream is, and define it at first use (the line under the title) or in the Terms paragraph.
- **Checked against a source?** No.

**F12. §4.5 and §6, "re-decoded", "threshold picker". Minor**
- **Issue:** Decoding (turning a net's per-frame probability into calls, at a threshold and merge gap) is never described. So "re-decoded from its saved model, keeping its threshold" is opaque, and so is why no retraining is needed.
- **Fix:** In §3 or §4.5, add one clause: "decoding: thresholding the net's per-frame probability and merging nearby crossings into calls".
- **Checked against a source?** No.

**F13. §4.5 ("the other workstation pointed at…") and §5 ("WSMIP065"). Minor**
- **Issue:** The replicate is referred to before §5 introduces it, and machine hostnames appear in prose and in the Figure 6 labels.
- **Fix:** Use "the replicate run (§5)". Drop the hostnames from reader-facing text or put them in parentheses in §8.
- **Checked against a source?** No.

**F14. §6 bullets and Figures 7 and 8, net names. Minor**
- **Issue:** The nets are known only by code identifiers (chorus_norm, chorus_gain_norm, line_length, tube). The page says so, but the names don't carry their mechanism, so each bullet sends the reader back to Table 1.
- **Fix:** Give one plain gloss per name at first use in §6 or in the figure row labels (for example, "chorus_norm (per-ROI vote)"), or add a short key beside Figure 7.
- **Checked against a source?** No.

**F15. Table 3, "crowded F1 of the choices" (such as 0.820–0.837). Minor**
- **Issue:** The ranges are not explained, and the pass rule has to be recalled from §4.5.
- **Fix:** Caption: "range over the 4 folds' choices; a choice passes if it scores no more than 0.02 below the setting it replaces".
- **Checked against a source?** No.

**F16. Figure 7, panel B, locust. Minor**
- **Issue:** The × marks are plotted at about 0.55 on the F1 axis, so they read as scores, although the caption says the value is "not an admissible result".
- **Fix:** Put the × in a gutter or at a labelled position off the scale, or grey out the whole row.
- **Checked against a source?** No.

**F17. Figure 2, panel B. Minor**
- **Issue:** The three rows (the inner rotations) have no labels.
- **Fix:** Label them "rotation 1–3".
- **Checked against a source?** No.

## Per-panel "what a cold reader sees"

- **Figure 1:** A black-and-white raster of 33 cells over about 10 minutes. There is a filled blue ▼ above a faint vertical line of ticks at about 16.5 min, two hollow ▼ at about 17 and 18 min, and a hatched band from 20 min where the whole raster gets dense. Readable.
- **Figure 2:** Left, a 4×4 grid with one dark "scored once" tile on the diagonal. Right, a 3×3 grid of "trains / scores" with the scoring tile on the diagonal. Readable.
- **Figure 3:** Two groups of four 48-cell strips, with blue fitted cells, an orange threshold cell and dark held-out blocks. In the top group three rows share the same blue block; in the bottom group the blue cells are spread across folds. Readable.
- **Figure 4:** A schematic scatter of grey points, a shaded region on the right for "outside the budget", and two ringed choices, one on each side. Readable.
- **Figure 5A:** Triangles over ticks over grey bars. It can be misread as a raster (F5).
- **Figure 5B:** F1 lines against merge gap, with coded detectors rising steeply toward 30 s. Readable, but see the axis-scale issue in F9.
- **Figure 6:** Two rows of 48 empty boxes, grouped by outline shade. Readable but thin.
- **Figure 7:** Dot strips per contestant with mean bars; nets in blue above a dashed line; hollow circles and × marks in panel B. Readable.
- **Figure 8:** Differences from CoactDetect, nearly all left of a dashed zero line, with orange diamonds for the replicate. Readable.

## Tone

- Headings are consistently sentence case.
- There is no ALL-CAPS emphasis.
- Lists are formatted as lists.
- One inconsistency: "Tony" in §7 against "the project lead" everywhere else (covered in F10).

## Files

- Artifact: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`
- Generator: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py` (context-window sentence at line 884, table captions at lines 631, 658, 690)
- Source checks: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\score.py` (lines 201–239), `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\GLOSSARY.md` (lines 334–337)
- Renders reviewed: `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\renders_round2\`
