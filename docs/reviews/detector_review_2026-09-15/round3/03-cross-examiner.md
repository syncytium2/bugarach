> **Public copy.** Lines that concern real treatment recordings are removed (25 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 3 ok — Read, Grep, Glob

# Role 3, Cross-Examiner: consistency audit of the detector review (round 3, blind pass)

**What I checked:**
- The whole plain-text build.
- Figures 1–18, each opened as an image.
- Every token against `_work/numbers.json`, with spot checks in `sweeps.json`.
- Table 3's red cells, in the HTML.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**What holds:**
- Every value in Table 3 matches numbers.json. Table 4's F1 columns match Table 3. Table 3's red cells are the right three.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The prose numbers in Sections 2, 5, 7 and 8 match numbers.json. The exceptions are listed below.
- No banned word appears ("modality", bare "adaptive", "corpus").

Every finding ends with "Verified", meaning whether I checked it against a source.

## Blocking

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** In short ¶3; §8 "What these recordings show"; §7 "So no design here both ignores busy cells and keeps finding events among them"; §10 "every design either calls through busy stretches or goes partly blind in them".
- **Evidence:**
  - Table 1 says rate+context judges chance from "the average rate over the surrounding 60 seconds", which is a nearby-background bar.
  - §8 sets rate+context against "the detectors whose bar follows the nearby background".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The claim that nearby-bar detectors "miss most real events" is also false for tube-guard (65% inside).
- **Fix:** Put rate+context (and SPIKE-synch) in the classification by name. Give "ignores busy cells" a number, for example calls per minute in the block. Then either narrow the claim to the detectors it holds for, or say what rate+context pays instead (its false alarms in Figure 3B).
- **Verified:** yes.

## Major

**M1. The prose cites Figure 13C for numbers that Figure 13C does not show.**
- **Where:** §7 "CoactDetect at its shipped setting found 52% … and 24% … (Figure 13C …)"; In short ¶4; Table 4 rate+context "(2%)".
- **Evidence:**
  - Figure 13C plots tuned averages. For CoactDetect's 10% events it shows 0.57 and 0.19; the shipped values are 0.525 and 0.24.
  - Recall by event size at the shipped setting is not in any figure or table. That applies to the 52%, 24% and 2% figures.
- **Fix:** Add shipped recall by size to Table 3, or diamonds to Figure 13C. Label Figure 13C "tuned (average over rounds)".
- **Verified:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - `stage_blockrecall` runs 24 seeds × 3 event sizes, and `_block_events` draws each one separately, with retries.
  - That is why each size has 48 events inside the block and 120 outside. With 24 recordings in total, each size would have 16 inside events.
  - These recordings also carry no decoys outside the block: both decoys are moved into it. So they are not "the same recipe".
- **Fix:** Write "24 seeds, each built three times, once per event size (72 recordings; 48 events per size inside the block)". Note that the decoys were moved.
- **Verified:** yes.

**M3. Hansen 1973 is marked "(not read)", but the project's history file says it was read.**
- **Where:** §11, LoCo paragraph.
- **Evidence:**
  - `detector_history.md` §4.1 says the paper was read on 2026-09-14.
  - It also says reading it neither confirms nor rules out the credit: "where greatest-of began is not established". Gandhi & Kassam credit Hansen; Rohling credits Moore & Lawrence.
  - GLOSSARY records the Hansen attribution as withdrawn.
- **Fix:** Drop "(not read)". Replace "usually credited to" with the §4.1 wording: the earliest published description the project has found, with the origin not established.
- **Verified:** yes.

**M4. Section 7 publishes bake-off numbers that MILESTONES says are held.**
- **Where:** §7, Table 3, Table 4.
- **Evidence:**
  - The MILESTONES Open table lists "The 24-seed bake-off — held". Its owner is Tony, and what it blocks is "promoting any new bake-off number".
  - The 24-seed row says "held — do not promote".
  - The document flags its numbers as provisional but still gives outside readers a fresh bake-off.
- **Fix:** Record Tony's release decision for this document, or keep it internal. Separately, add a note to MILESTONES row "On the fitted field one winner holds across the axis". This run contradicts it (§7 says so), and the row still reads `current`.
- **Verified:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** §8, "rises in the slow stream (typical values …)".
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** For example: "splits in the slow stream: the median rises, but fewer than half of recordings are at or above baseline".
- **Verified:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - 84 is the whole `steps_excluded` folder.
  - 80 is the fitter's own selection, with floors applied (the comment in `make_detector_review.py`).
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Also, the simulator's levels were read off the earlier default folder on 2026-08-20. Figure 10 recomputes on the step-excluded folder of 2026-09-03, so "the 80 baselines the simulator was fitted to" is not literally the same data.
  - The same recomputation gives a 25th percentile of 5.0 mHz, while the document says it is "matching" the 5.2 mHz quiet level.
- **Fix:** Add one sentence each where 84, 80 and 67 first appear, saying which subset it is. Say "close to" instead of "matching". Say that the check was run on the step-excluded version of the recordings.
- **Verified:** yes.

**M7. "Breaks its limit" is counted on three bases.**
- **Where:** Figure 12 legend ("on all 24 recordings"); Table 3 red cells ("worst round … the project's own check uses the average"); §7 prose (rounds over the limit).
- **Evidence:**
  - Take locust. Its worst round (34.70 per minute) is red, and the prose says it broke its limit in 2 of 4 rounds. Its average is 19.35 against a limit of 25, so the project's own check passes it.
  - SPIKE-synch picked an over-limit setting in 4 of 4 rounds but broke the limit in only 3 held-out rounds.
- **Fix:** Pick one basis and name it everywhere, or add one line that reconciles the three.
- **Verified:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - In Figure 2B1 the green simulated line is below the black recorded line at every n from 1 to 16.
  - For n from 2 to 5 it is also below the circular-shift line, so "the simulated recordings line up more than the shift too" holds only from about n = 6 upward.
- **Fix:** Match the wording to the plot.
- **Verified:** yes, by eye and against `sur_sim_n8`.

**M9. Glossary conflicts and missing terms.**
- **Where:** §3.5; the Word list.
- **Evidence:**
  - GLOSSARY says locust "gets each event's duration from the producer", and adds "Duration is never derived here". The run uses `active_duration_sec=1.0` in fixed mode (`bench.OPERATING_POINTS`). The document's "on for a fixed 1 second" is correct, and the glossary is stale.
  - Several reader-facing words have no GLOSSARY entry, although each renames an existing glossary term: busy block (promiscuity probe), decoy (distractor), level (regime), setting / shipped setting (detector settings / operating point), bar, call, call level, marked windows (region / trimmed stats window), round. The checklist requires new terms to be added in the same change.
- **Fix:** Correct the locust entry. Add a short "reader-facing synonyms" block to GLOSSARY.
- **Verified:** yes.

## Minor

1. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
2. **§2 gives "about 24 of every 1,000"; Figure 2C's bar is labelled 25.** The source value is 24.5. **Fix:** round once. **Verified:** yes.
3. **Table 2 says decoys are placed "between minutes 2 and 18".** The code uses up to 18⅓, and Figure 2D shows a decoy just after minute 18. **Verified:** yes.
4. **§7 "tuned binned SCE, which scored higher at the busy level (0.45 against 0.63)".** The numbers are in quiet, busy order, which reads backwards. The sentence is also F1, inside a paragraph about small-event recall. **Verified:** yes.
5. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
6. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
7. **§6.3 gives the origins of only locust's, CoactDetect's and SPIKE-synch's shipped settings.** In `bench.py`, LoCo's is a "measured-regime F1 optimum", which was also chosen on a bench. §7's shipped-against-tuned comparison also leaves out SPIKE-synch (0.49 against 0.53). **Verified:** yes.
8. **Ranking language against "we do not rank them".** Table 4 says "Among the best scores", "Lowest average score" and "The lowest score of the four tube models". MILESTONES records a decided "No ranking; a table of performance". **Verified:** yes.
9. **"Best possible F1 0.83" is not a strict maximum.** §5 says decoys can sit close to a planted event, and Figure 10A1 shows one on top of a planted event. One call can then cover both, which gives 15 of 20 and an F1 above 0.83. **Fix:** write "about 0.83". **Verified:** yes.
10. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
11. **"Window" means five things:** Window A/B, marked windows, the nearby 60-second window, the 2.5-second scoring window, and the context window. GLOSSARY calls the scoring one "tolerance". Also, "small" and "large" events are never defined (only "mid-sized" is, in Table 4's caption), yet the In short section uses "small events" first. **Verified:** yes.
12. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
13. **Figure 9 legend and panel letters.** "▼ found by any of the four" changes the triangle's meaning from Figures 3–8. Panels B and C correspond to windows A and B. §4.1 says tube-guard makes "an event raise its own bar less", but the surround is not the bar; the call level is. **Verified:** yes.
14. **Raster axis labels say "33 ROI"** in Figures 2D and 10, but "33 ROIs" everywhere else. **Verified:** yes.
15. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
16. **Figure 12, rate+context at value 2.** `sweeps.json` gives 5.32 calls per minute, above the limit of 2, so the value should carry a red "breaks limit" square. At display resolution I could not see one; the green circle may hide it. **Fix:** check at full size. **Verified:** partly.
17. **§6.2 presents the busy-block handling as settled.** MILESTONES lists "How does the promiscuity probe enter the score?" as an open decision with two live rules. **Fix:** add one clause saying so. **Verified:** yes.
18. **Stale companion text.**
    - The `bench.TOLERANCE_GRID` docstring still says the "shipped 1.5 s" and "five of six flat from 0.75 s". MILESTONES records the move to 2.5 s.
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - MILESTONES' 24-seed row says locust's average was over its limit (30.62 per minute). This run's average is 19.35, and nothing explains the difference.
    - **Verified:** yes.
19. **MILESTONES says "locust is held out of the public build".** Check that this document's distribution is consistent with that decision. **Verified:** no (it is about distribution).

**Files:**
- `<scratchpad>\review\detector_review_plain.txt`
- `<scratchpad>\review\_work\numbers.json`
- `<worktree>\tools\make_detector_review.py` (lines 1213–1296, 1685–1708)
- `<worktree>\docs\GLOSSARY.md`
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- `<worktree>\docs\MILESTONES.md`
- `<worktree>\docs\detector_history.md` (§4.1)
- `<worktree>\src\bugarach\bench.py` (lines 172–218, 912–930)
- `<worktree>\current_export.toml`
