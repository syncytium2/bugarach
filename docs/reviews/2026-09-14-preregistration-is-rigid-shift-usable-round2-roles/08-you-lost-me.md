GRANT 8 ok — Read, Grep, Glob

# Role 8, "You Lost Me": blind pass on the rigid-shift pre-registration

Artifact: `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`, blob 2c9813d.

**What I did:** I read the page cold, top to bottom. After that I opened `docs/GLOSSARY.md` and `docs/goals/unsupervised-learning.md`. I also opened `src/bugarach/surrogates.py`, `surrogate_stats.py` and `surrogate_discriminator.py` to check whether identifiers exist and what a few terms mean. I opened no `docs/reviews/` file.

**Figure checks:** the page has no figures, so the false-friend and panel-readability checks had nothing to examine.

## Per-section verdict

Terms count as "undefined" when the page doesn't define them where they first appear. The last column says whether a cold reader can follow. "Blocking" means three or more undefined terms, or a gap that stops the rule from being run.

| Section | Terms and identifiers first used here | Defined here? | Cold reader follows? |
|---|---|---|---|
| Title and header note | surrogate screen, post-hoc, goal | goal is linked | yes |
| **The question** | rigid shift, ROI, train, *J*, coordination-blind classifier, planted coordination, "the timescale this project calls coordinated", self-supervised objective, negative class, "the model" | only rigid shift, and *J* partly. The classifier and planted coordination are explained several sections later. "The model" is never defined. | **blocking** (four or more undefined) |
| **Why rigid shift, and why only rigid shift** | 2026-09-11 overnight run, per-ROI leak test, fast and slow streams, Cossart, "the join", "accuracies" (of what, against what chance level), seed-0 defect, "the other survivors", uniform dither, joint-ISI, "this stage" | none. Most are links. | **blocking** |
| What this run cannot claim | both folders, baseline recordings, surrogate seeds, mouse folds, VIABLE (not defined until later) | partly | yes |
| **Data** | `dataset.current("steps_excluded")`, "four groups" (never named anywhere on the page), baseline windows (points to FOUNDATIONS §9), zero-event ROIs, motion-pinned recordings, "the producer" | zero-event ROIs only | **blocking** |
| The displacements — accepted | grid, leak-free, Bonferroni, 98.3 % interval, Cossart frames | no frame interval for Cossart; no one- vs two-sided | no |
| **Leak** | `surrogate_discriminator.forced_choice`, edge-band counts, symmetric statistics, within-pair permutations, the recording-identity run's `mouse_bootstrap`, "the screen's own smallest effect", "real against real", "flag", "that was the defect" | no | **blocking** |
| **Count preservation** | generation window, analysis window, `tube`, count leak, `edge_thinning` | only `edge_thinning` | **blocking** (three undefined) |
| **Destruction** | `surrogate_stats.destruction`, synthetic twins, floor, "the same key", the assessor, selection-corrected coactivity excess, participation, K scan, do-nothing, homogeneous resample, circular shift, "the assessor's own null", saturation, "566 median ROIs" | only "retained" | **blocking** (the worst section) |
| The outcome, per stream and overall | model tier, quiet → busy transfer penalty, treated window, simulator-trained models, six hand-written detectors | no. Also replaced by the amendments, with nothing here saying so. | no |
| **Not in this run** | band statistics, family size, ROI swap, MAHICE | no | **blocking** by count, but low harm because it is only a list of exclusions |
| What has to be built, and its cost | runner, seed-distribution voiding rule, `--limit`, darkroom | mostly | yes |
| Review, once; Sign-off | murderboard | n/a | yes |
| Amendments (status paragraph) | run record, UNDECIDED | n/a | **no.** It says "none is adopted yet … Do not run". A session reading top-down hits that order before the Adopted section, and nothing retracts it. |
| Adopted amendments: preamble and *Terms used below* | window, interior window, cell, bootstrap | yes | yes, but "cell" collides with "one imaged cell" (see findings) |
| **The outcome, completed** | decided, "could not pass", can-pass check, grid position, UNRESOLVED | "decided" is defined only for the leak gate | **blocking** (cannot be run as written) |
| The leak gate (amended) | interior windows, pair count, window layout, fold seed, can-pass check, "permutation machinery" | mostly | no. What the negative control does is contradictory. |
| The count gate (amended) | occupied frames, two one-sided tests, edge windows, `edge_thinning` "at a fixed 5 s" | mostly | no. The control's criterion is ambiguous. |
| **The destruction gate (amended)** | bin "10 frames", MATLAB assessor, gated K, "visible", excess ≥ 1.0 (what unit), saturation table, P(largest bin ≥ K), `freeze_half`, graded control, assessor seed | `freeze_half`, "largest bin" and the unit of excess are not defined | **blocking** |
| Randomness | run tag, "surrogate cell ids", the 2026-09-11 key scheme | mostly | yes |
| What was known before signing | none new | n/a | yes |
| What a PASS may claim | linear discriminator, next tier | mostly | yes |
| What STOPPED means | intrinsic, fixable instrument, aggregate-channel leak test | no | no. "Fixable instrument" is a judgment, not something to compute. |
| Groups | four groups (unnamed), leak point estimate (at which *J*?) | no | no |

## Key test: could a session with only this page run each gate and read the outcome?

**Leak gate: mostly yes.**
- **Clear:** interior 60 s windows; the mouse bootstrap with refitting; the 98.33rd and 1.67th percentiles against 0.55; uniform dither as positive control; the can-pass check.
- **Unclear:** what happens when 4 or more of the 20 negative-control seeds flag. The signed text says "void the stream". The amendment says "unchanged" and then "Nothing decides on its P values". A session cannot tell whether that result voids anything.
- **Unstated:** whether the positive control, negative control and can-pass check also use interior windows and the refitting bootstrap.

**Count gate: can compute, cannot fully classify.**
- **Clear:** the statistic, and PASS.
- **Missing:** "decided FAIL" is defined only for leak. A count interval that is neither inside ±2 % nor entirely outside it has no stated result.
- **Ambiguous control:** "must fall outside ±2 %" could mean the point estimate, the whole interval, or just "not inside".

**Destruction gate: no.**
- **Bin width:** "1.0 s, which is 10 frames" can't be built as stated. The code's bin is `2 * DESTRUCTION_HALF_WINDOW_FRAMES + 1` frames, always odd (`surrogate_stats.py:1177-1193`), so it can be 9 or 11 frames but not 10.
- **"Visible":** "excess before … at least 1.0" gives no unit. It also doesn't say whether it means the planted twin's excess or the planted-minus-unplanted difference. The code's `before` field is the difference.
- **`K = 4`:** it is an absolute count. The glossary says K is a percentage of the ROI population and that an absolute K "is not comparable". The page also doesn't say whether K = 4 has to be a gated K, or which participation level applies.
- **No gated K:** "no K is gated → VOID" doesn't say whether this is per participation level.
- **Old saturation rule:** the signed rule ("expected co-active ROIs exceeds top of K scan → *J* void") is neither restated nor retired.
- **Saturation table:** its event model doesn't give the ROI count, which varies by recording.
- **Decided FAIL:** undefined here too.

**Combining results: no.**
- **Overlapping cell results:** the four cell results can apply at once. A cell whose leak gate decidedly FAILs with valid controls, while its `freeze_half` control is out of range, meets both the FAIL and the VOID definitions. A cell with a failed can-pass check is "also UNDECIDED" even if another gate FAILs. No order of precedence is given.
- **Stream rollup:** once each cell has one result, the stream rule and the outcome table are complete.
- **Groups rule:** it creates "NARROWED for that stream", which is not one of the table's inputs.

**Which text an amendment overrides: not clear.**
- The only general rule is "where they disagree, the amendment wins". Only one amendment names the text it replaces (joint-ISI, "was never measured" above).
- At least nine other signed passages are replaced or changed without saying so (the override-map finding in the list below).
- Several amendments add to the signed text rather than contradicting it. For those, "disagree" doesn't settle whether the signed sentence still applies.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against a source? |
|---|---|---|---|---|---|
| 1 | Adopted amendments, preamble | **No override map.** "Where they disagree, the amendment wins" leaves the reader to find each conflict. Silently replaced or changed: the whole outcome section (both the stream rule and the table); the Bonferroni sentence ("every bound … 98.3 % interval") against the count gate's two-sided 96.67 %; count "onset count" → "occupied frames"; count interval 98.3 % → 96.67 %; count control "must *fail* this gate" → "fall outside ±2 %"; destruction pass (point value ≤ 0.25 → 98.33rd percentile ≤ 0.25); the old saturation *J*-void rule against gated K; leak scored on all windows → interior windows only; the negative control's "void the stream"; "a STOP on rigid shift stops the goal" → only when intrinsic. | blocking | Open the Adopted section with a table with one row per signed passage: the quoted signed phrase · replaced / added to / retired · the amendment that does it. Nothing above the line needs editing. | yes (the page itself) |
| 2 | Amendments status paragraph, lines 198–204 | Says "none is adopted yet … **Do not run until Tony has ruled on each**". The Adopted section follows with no line retracting it. A session scanning for a go/no-go finds the stop order first. | high | Add a dated line right after it: "Superseded 2026-09-14: all eleven adopted, see below." | yes |
| 3 | The outcome, completed: cell results | The four cell results don't exclude each other and have no precedence. FAIL and VOID overlap. UNDECIDED and VOID overlap. The "can-pass fails → UNDECIDED" rule overlaps a decided FAIL. | blocking | State an order, for example "VOID, then FAIL, then UNDECIDED, then PASS; the first that applies". Or write it as a decision list. | yes |
| 4 | The outcome, completed, together with the count and destruction gates | "Decided" FAIL and "could not pass" are defined only for the leak gate. The count and destruction gates can't produce FAIL or UNDECIDED by any written rule. | blocking | Give each its pair. Count: decided FAIL if the interval lies entirely outside ±2 %. Destruction: decided FAIL if the 1.67th percentile of retained is above 0.25. Anything else not passing is UNDECIDED. | yes |
| 5 | The leak gate (amended), "Negative control" | "Unchanged, 4 or more of 20" (the signed text says this voids the stream) contradicts "Nothing decides on its P values". | high | Say one thing: "4 or more of 20 flags makes every cell in the stream VOID". Or: "reported only, voids nothing". | yes |
| 6 | The destruction gate (amended), "The bin" | "1.0 s, which is 10 frames": the assessor's bin is `2h+1` frames, always odd. The signed "±2-frame (0.5 s)" bin is 5 frames. The page doesn't say whether 1.0 s is a width or a half-width, and can't be implemented as written. The same goes for slow's 2.0 s. | high | State the half-width in frames and the resulting width, for example "±5 frames, 11 frames wide, 1.1 s". Also state whether the controls run at both slow bins. | yes (`surrogate_stats.py:1177-1193`) |
| 7 | The destruction gate (amended), "Visible" | "Excess before the surrogate is at least 1.0": no unit, and it doesn't say whose excess (the planted twin's, or planted minus unplanted). | high | Name the quantity and its unit, for example "planted minus unplanted `coact_excess`, in the assessor's units, ≥ 1.0". | yes (the code's `before` = planted − unplanted) |
| 8 | Destruction (signed) and amended "K = 4" | K is never defined on the page. `K = 4` is absolute, but the glossary defines K as a percentage of ROIs and forbids absolute K across recordings. The page doesn't say whether K = 4 must be gated or which participation level applies. | high | Define K where it first appears ("K, the smallest number of co-active ROIs the assessor counts as an event; here an absolute count, not the MAHICE percentage"). Then say what happens if K = 4 is not gated, and give the participation level. | yes (GLOSSARY lines 195–203) |
| 9 | The destruction gate (amended), controls | `freeze_half` is a bare code identifier with no plain-language meaning. The code restores a seeded half of the ROIs to their input after the surrogate. | medium | "Half-frozen homogeneous resample: half the ROIs, chosen by seed, are left untouched." | yes (`surrogate_stats.py:1207`) |
| 10 | The destruction gate (amended), "Gated K" and "no K is gated" | Doesn't say whether VOID-for-destruction is per participation level. The signed saturation rule (*J* void) isn't retired, and the new saturation table's event model doesn't give the ROI count. | medium | "Per participation level; VOID if either level has no gated K. This replaces the signed saturation rule." Give the ROI count that the saturation table uses. | yes |
| 11 | The count gate (amended), control | "`edge_thinning` … must fall outside ±2 %" doesn't say whether this means the point estimate or the whole interval. "Fixed 5 s" doesn't name the parameter it sets. | medium | "Valid if its 96.67 % interval is not wholly inside ±2 %; 5 s is its `J`." | yes (`surrogates.py:813` takes `J`, `analysis_window`) |
| 12 | Groups | "NARROWED for that stream" is not an input to the outcome table, so a session can't combine it with the other stream. The leak point estimate isn't tied to a *J*. "Names the group" doesn't say whether the group is excluded from the claim or is its limit. | high | Put the group check inside the stream result (for example "PASS-narrowed") and add table rows for it. Say "at the passing cell". Say "the claim excludes group X". | yes |
| 13 | The outcome table, "any other combination" | PASS + UNDECIDED gives UNRESOLVED ("nothing is read"), and an UNDECIDED stream "is not rerun". So one passing and one undecidable stream end with nothing read, a worse outcome than PASS + FAIL (NARROWED). A cold reader will think this is a mistake. Whether it is terminal isn't stated either. | medium | Either add rows for PASS + UNDECIDED (and PASS + VOID after a rerun), or say outright that this is intended and terminal. | yes |
| 14 | What STOPPED means | "A FAIL traced to a fixable instrument or to window edges": a judgment with no rule for who traces it or how. It also contradicts the cell definition, where FAIL already requires valid controls. | medium | Delete that sentence, or send the case to VOID. Keep only the computable test ("no cell passes both leak and destruction with valid controls"). | yes |
| 15 | Terms used below, "cell" | "Cell" is defined as a stream at one *J*. The goal page defines ROI as "one imaged cell", and Randomness uses "surrogate cell ids", which is the code's `cell_id`, a different grain. A neuroscientist reads "cell" as a neuron. | medium | Rename to something like "setting" or "stream × *J* combination". Keep `cell_id` only as a code reference in backticks. | yes (goal page line 28; `surrogate_stats.py:1199`) |
| 16 | The question; Why rigid shift | Four or more undefined terms each: coordination-blind classifier, planted coordination, "the model", self-supervised objective; per-ROI leak test, seed-0 defect, survivors, uniform dither, joint-ISI, fast/slow, Cossart. An outside reviewer is lost by the second section. | blocking (by count; lower effect for Tony) | Add an abbreviations and terms line under the header, as the goal page does (its line 28), with forward pointers ("classifier: see *Leak*"). One clause each for uniform dither, joint-ISI and the seed-0 defect. | yes |
| 17 | Leak (signed) | edge-band counts, symmetric statistics, within-pair permutations, "real against real", "flag", "that was the defect": none defined. "Real against real" is a real window paired with another real window from the same recording. | blocking (by count) | One sentence each. For example: "real against real: each real window paired with another real window of its own recording; *flags* = permutation p < 0.05". | yes (`surrogate_discriminator.py:442`) |
| 18 | Destruction (signed) | twins, floor, "same key", assessor, selection-corrected coactivity excess, participation, K scan, do-nothing, homogeneous resample, circular shift: at least ten undefined terms. | blocking | A short definitions block at the start of the section. "Participation 0.2" = share of ROIs in each planted event. Do-nothing = the surrogate returned unchanged. And so on. | yes (GLOSSARY) |
| 19 | Data | "Four groups" is never named, but the Groups amendment requires reporting per group. "Motion-pinned", "the producer" and `steps_excluded` are undefined. | medium | Name the four groups. Explain `steps_excluded` in one clause (field-step-excluded). "Producer: the lab's MATLAB export". | yes |
| 20 | Displacements table and "What was known before signing" | "The largest leak-free value" suggests larger *J* leaked. The amendment says "1.4 s was the only slow displacement that did not" leak. A reader can't tell whether 2.8 s and 5.6 s leaked in the exploratory run or were never measured, and that changes how the declared values read. | medium | Say which grid values above the smallest declared *J* were measured, and what they showed. | partly (goal page line 81 lists only 0.7 and 1.4 s slow) |
| 21 | Displacements, Cossart row | *J* is given in frames with no frame interval, so "comparable to real event structure" can't be checked. The glossary defines *J* in ± seconds. | low | Give Cossart's frame interval and the conversion beside the row. | yes (GLOSSARY line 355) |
| 22 | The displacements; the count gate | "Every bound below is Bonferroni-widened to a 98.3 % interval" (it doesn't say one- or two-sided). The amendments use one-sided 98.33rd percentiles and a two-sided 96.67 % interval, and the defined term "Bootstrap" (resampling mice) is then used for a bootstrap over twins. | medium | Say in the override map that the one-sided and two-sided choices replace the sentence. Call the destruction bootstrap "twin bootstrap". | yes |
| 23 | The outcome, completed, Cossart | "Smallest passing cell" doesn't say smallest by grid position or by seconds. It doesn't say whether a Cossart PASS needs its own positive control, negative control and can-pass check. | low | "Lowest grid position; the Cossart leak result uses the full amended leak gate." | yes |
| 24 | Adopted amendments preamble | "All eleven" amendments are adopted, but the sections aren't numbered or named as eleven. A reader can't match the count to the text. | low | List the eleven by short name, which the override map in the first finding can also do. | yes |
| 25 | Tone, throughout | ALL-CAPS used for emphasis ("SIGNED", "STOP", which is not one of the outcome labels; the label is STOPPED). "566 median ROIs" reads badly. The leak threshold 0.55 is never set against chance (0.5). | low | Use STOPPED or plain words. "A median of 566 ROIs per recording". "Accuracy 0.55, where 0.5 is chance". | yes |

## Bottom line

Tony can follow the page. The session that has to build and run from it cannot, for three reasons:
- The count and destruction gates have no definition of a decided FAIL (the fourth finding).
- The four cell results overlap and no precedence is given (the third finding).
- The destruction gate's bin and "visible" threshold can't be computed as written (the sixth and seventh findings).

An outside reviewer is also lost by the second section. The single fix with the most effect is a supersession table at the top of Adopted amendments. The whole fix can go below the sign-off line, so nothing frozen needs editing.
