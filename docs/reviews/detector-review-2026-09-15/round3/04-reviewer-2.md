> **Public copy.** Lines that concern real treatment recordings are removed (47 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 4 ok — Read, Grep, Glob, Bash

# Reviewer 2 (adversarial) report on the coordinated-event detector review, round 3 blind pass

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Disclosure:** one search of `docs/` for "leads at every" returned one line from `docs/reviews/detector_review_2026-09-15/round2/03-cross-examiner.md`. I did not open that file. Finding M3 overlaps that line, but I reached it on my own from MILESTONES and `tests/test_background_curve.py`.

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## BLOCKING

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** "In short", paragraph 3 ("Detectors that judge chance from the nearby seconds make few false calls … They also miss most real events there"); §7, "So no design here both ignores busy cells and keeps finding events among them"; §10, "every design either calls through busy stretches or goes partly blind in them".
- **Evidence:**
  - rate+context also judges chance from the nearby 60 seconds (Table 1). At its shipped setting it makes 0.6 calls per minute in the busy block, against a limit of 2.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - tube-guard, whose surround filter is also local, finds 65% inside with a chance line of 12%.
  - The §7 text itself says "rate+context held up".
  - So the claim that local detectors go blind fails on two of the local designs. The "no design does both" claim only holds if "ignores busy cells" means roughly zero calls, and the document never defines it.
  - What the figure does support is different: **every detector's sensitivity changes with background, in both directions.** CoactDetect loses events in the block. rate+context gains: for events joined by 10% of ROIs it finds 19% inside the block against 0% outside, so its operating point moves up when the background rises.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:**
  - Replace the dichotomy with "every detector's hit rate depends on background rate; some lose events, some gain sensitivity (and false calls) as cells get busier."
  - Define "ignores busy cells" numerically if the dichotomy is kept.
  - Drop "judge chance from the nearby seconds" as the dividing mechanism. The real split is a bar that scales with surrogate spread versus mean plus a fixed offset.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The source is shaky. FOUNDATIONS gives the slow stream as "median 2.50 with 44% of slices at or above baseline". A median above 1 cannot coexist with fewer than half the recordings at or above 1, so "rises in the slow stream" rests on an inconsistent figure.
  - "Measured with these same six detectors" overstates. Per FOUNDATIONS it was the MATLAB campaign, and only two Python ports were rechecked, "magnitudes differing because settings and windowing differ".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Alternatively, give the per-group, per-stream breakdown with counts.
  - Fix or flag the median-versus-44% inconsistency at its source.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## MAJOR

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **(a) Unequal spacing.** `_block_events` accepts two in-block events only 30 seconds apart, inside a 220-second placement window. Planted events outside the block stay at least 120 seconds apart. The document says the 120-second spacing exists to avoid the known weakness that a nearby event raises a local bar (§5, §10). The inside/outside comparison therefore puts crowding on only one side.
  - For uniform placement, about 29% of accepted pairs sit 30 to 60 seconds apart. That is within LoCo's one-minute windows and rate+context's 60-second context.
  - Fix: require at least 120 seconds apart. The 220-second placement window allows it.
- **(b) The chance line is not a correction.** Recall "above its chance line" is not chance-corrected recall. Report (recall − chance)/(1 − chance), or a sham test: the same placement times with zero added cells.
  - Example: locust at 10% of ROIs goes from 0.77 to about 0.53 after correction. tube-guard at 18% goes from 0.65 to about 0.60.
- **(c) No uncertainty shown.** Each in-block cell is 48 events. A 95% interval on 4 of 48 runs roughly 3–20%, and on 7 of 48 roughly 7–27%.
  - "8% vs 15%", "56% vs 65%" and Table 4's "tube-guard … keeps more of its recall inside a busy stretch" than tube (65% vs 46%, from single trained copies) are not distinguishable at this n. The last one is also confounded by the training-run spread the document itself reports (tube F1 0.63–0.76).
  - Fix: add binomial intervals to the figure, and drop or soften the tube versus tube-guard comparison.
- **(d) Higher recall inside than outside is a warning, not a strength.** SPIKE-synch finds 92% inside vs 72% outside; rate+context finds 19% vs 0% at 10% of ROIs. When a busier background makes a detector find more, the background is lifting borderline counts over the bar. Table 4 lists both as "good at: keeps finding … inside a busy stretch". Move them to the weakness column, or at least describe them neutrally.
- **(e) "Seeds … which no setting or training saw" overstates.** The seeds are new, but the recipe is not. LoCo's shipped setting is labelled in `bench.py` as the "measured-regime F1 optimum", and locust's percentile was re-chosen on these background levels.
- **Verifiable:** yes (code lines cited above, `blockrecall.json`).

**M2. The busy block's size is an unjustified constant, and real busy stretches look far busier.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - At the block's roughly 65 mHz this is about 0.03, below the 0.1 level, so the bench sees few calls.
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - This is a hypothesis for the authors to check, not a measurement.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Check the SPIKE-synch explanation against the measured rate.
  - In §10, replace "Real busy stretches may look different" with the measured comparison.
- **Verifiable:** partly (calculation yes; real rates not yet measured).

**M3. "No detector stands out" is a claim of no difference from a test with little power, and it hides what the project already measured.**
- **Where:** "In short", paragraph 2; §7, paragraph 1.
- **Evidence:**
  - The comparison uses 4 rounds of 6 recordings. The rounds are not independent (training sets overlap by 12 of 18), and the decoys cap F1 at 0.83, which squeezes the scores together.
  - A paired comparison per recording, with all detectors on the same 24 recordings, was cheap and not done. So "about the same" is silence, not equivalence. The document should state what difference this design could detect.
  - §7 mentions "an earlier project run … found one detector ahead at every rate" but does not name it. MILESTONES row B records this as `measured`/`current`, and `bench.py`'s table gives the order CoactDetect > LoCo > rate+context > locust > SPIKE-synch > binned SCE. Withholding the name reads as softening.
  - Among the "five", tuned rate+context breaks its busy-block limit in 4 of 4 rounds. tube (1.40 calls per minute) and tube-guard (1.01) would fail the limit of 1 per minute that CoactDetect, LoCo and SPIKE-synch are held to. The "In short" lists all five as equals with no caveat.
- **Fix:**
  - Run and report a paired per-recording comparison, even just a sign test or bootstrap on F1 differences.
  - Name the earlier leader and say plainly that the two runs disagree.
  - Add to the "In short" that rate+context's tuned setting breaks its limit and the tube models have none.
- **Verifiable:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** §7, "SPIKE-synch's list does not control it … its score is not a tuned accuracy"; Table 4.
- **Evidence (Figure 12):**
  - SPIKE-synch's F1 ranges 0.48–0.53 across its list.
  - CoactDetect's F1 is flat across seven orders of magnitude of allowed chance (1 in 10 to 1 in 10,000,000), at roughly 0.69–0.74. LoCo's ranges roughly 0.67–0.74, and locust's is flat from the 99.9th percentile upward.
  - At the quiet level, CoactDetect's surrogate test barely matters. An allowed chance of 1 in 10 (about 1.3 spreads) scores the same as 1 in 10,000. That means the at-least-3-ROI floor and the 2-second bin are doing the work.
  - This undercuts §3.2's story that its strength is judging chance from the nearby minute, at least at the quiet level. It also explains the 99% decoy coverage.
- **Fix:**
  - Apply the same sentence to CoactDetect, LoCo and locust, or drop it for SPIKE-synch.
  - Report what share of CoactDetect's quiet-level calls would survive with the surrogate test removed (the 3-ROI floor alone).
- **Verifiable:** yes (Figure 12).

**M5. locust, the one detector derived from another lab's software, is shown in configurations that make it look worst, and the document does not say so.**
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - The same applies to LoCo: its slow-stream defaults are a 2 s bin and 60 s context, but it is run at 1 s and 120 s.
    - §8's "nobody has checked whether they suit it" is contradicted by the calibrated slow-stream pairs in the code.
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **An undisclosed history.** The `cicada.py` docstring records that the MATLAB predecessor "had already parked `generate_sce_cicada` for over-detecting on this preparation's long SLOW transients". The document does not mention this.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **"Close to openly released software" overstates.** It sits in "good at" while four deviations are listed and no output has ever been compared with CICADA's.
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Disclose the earlier over-detection finding.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Say in Table 4 that the single bar is this port's choice.
- **Verifiable:** yes (code cited).

**M6. The learned detectors' blindness is what their training taught them, but the document presents it as a property of the design.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Training also labels decoys as negatives, even though §5 says they cannot be told apart from 18% planted events. So the networks were trained on contradictory labels, which should push them away from mid-sized lineups. The document does not mention this.
  - "Ratio versions miss every real event" rests on single copies (the Figure 9 copies). §7 shows large variation between training runs, so blindness of the design is not shown.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Report the bench F1 of the copies used in Section 8.
- **Verifiable:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** "In short", paragraph 1; §1.
- **Evidence:**
  - The caption says the recording was chosen because it is where the six detectors' counts "differ most" of the eight. The "In short" gives its spread in counts with no such qualifier. This is a claim resting on a maximum.
  - "They disagree most where cells are busy" is a comparison asserted with no measure of disagreement or busyness. §8 admits "we did not measure how often the detectors agree".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:**
  - Say in the "In short" that this is the most divergent of the eight.
  - Give the range of max/min count ratios across all eight recordings in both streams.
  - Soften "disagree most where cells are busy" to "in the recordings shown, the largest disagreements were in dense stretches (not measured)".
  - Use one counting rule for both.
- **Verifiable:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The document treats busy stretches as independent extra events that a good detector should ignore. That is the busy-block model: uniform, 30-second ease-in.
  - The real transition may be coordination on a slower timescale. The detectors whose bar follows the nearby background are built never to call it. The detectors that "call through" it may be reporting something real.
  - The document defines coordination only as lineups of a few seconds on a steady background and never states that choice.
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable:** partly (picture yes; interpretation open).

**M9. Every simulated recording has 33 ROIs, and the detectors' rules depend on ROI count.**
- **Where:** Table 2, §3.6, §7, §8.
- **Evidence:**
  - SPIKE-synch's score is a share of N−1 ROIs, so its fixed 0.1 level means about 3 cells at 33 ROIs and fewer in smaller recordings.
  - Three detectors use a fixed floor of 3 ROIs. rate+context uses an absolute 5 events per second that does not scale with N.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** Add ROI count to §10's "what could be wrong", and ideally run the bench at a small and a large N.
- **Verifiable:** yes.

**M10. The slow stream has no bench at all, and the document does not say so plainly.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** State in §5 and §10 that every accuracy number is fast-stream only.
- **Verifiable:** yes.

---

## MINOR

1. **Some constants are defined but not justified.** The merge gaps (3 s, 2 s), the 60-second contexts, LoCo's 15-second reset, binned SCE's 10-second bin, locust's 1-second on-period and 4-frame separation, rate+context's 5 events per second, and the tube models' call level. Only one setting per detector was tuned. Add one sentence saying the rest were inherited and never tuned.
2. **Shipped settings are less independent than stated.** §6.3 omits that LoCo's shipped setting is the bench F1 optimum. It also omits that CoactDetect's viewer setting was kept over the default in its own code, which `bench.py` notes "scores F1 0.72 here". Both are selection on the bench.
3. **CoactDetect's true chance rate is measurable.** §3.2 says it has "not measured" the true chance rate at 3.72 spreads. It could be measured cheaply on surrogate-only recordings; do it or drop the "once in 10,000" sentence.
4. **The decoys are not quite as described.** Decoys sit only in minutes 2–18, while planted events span the recording. They follow no spacing rule, so a decoy can merge with a planted event. The 0.83 cap is therefore approximate, and "indistinguishable" holds only locally.
5. **The scoring window changed and no sensitivity check is shown.** MILESTONES records the move from 1.5 to 2.5 seconds together with the fitted background. Show whether the order of detectors holds at 1.5 seconds.
6. **The binned SCE anomaly signals a bench artifact.** Its tuned score is higher at the busy level (0.45 quiet vs 0.63 busy). §7 undercuts it with an untested reason; flag it in §10.
7. **The baseline counts do not match.** Figure 2 uses 84 baselines and §5 uses 80. Explain the difference.
8. **An unread source is cited.** Hansen (1973) is marked "(not read)". Cite what was read, or drop it.
9. **A weak strength for the learned detectors.** "Once trained it scans a recording thousands of times faster than real time" is true of all twelve.
10. **A strength at a rejected setting.** Table 4 credits rate+context with "Tuned, it finds more small events than any other" at a setting that breaks its limit in every round. Move it, or qualify it in the same cell.

---

## What Section 10 is missing

- The dichotomy problem and the fact that sensitivity moves with background (B1).
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The low power of "about the same" and the unnamed earlier leader (M3).
- The flat setting curves for CoactDetect, LoCo and locust (M4).
- The slow-stream settings being overridden, and locust's untested per-period option (M5).
- Training labels that teach blindness and contradict each other (M6).
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Only near-synchronous lineups counting as coordination (M8).
- The fixed 33 ROIs (M9) and the fast-stream-only bench (M10).
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Files relevant to these findings:**
- `<scratchpad>\review\detector_review_plain.txt`
- `<scratchpad>\review\_work\blockrecall.json`
- `<worktree>\tools\make_detector_review.py`
- `<worktree>\src\bugarach\detectors\cicada.py`
- `<worktree>\src\bugarach\detectors\loco.py`
- `<worktree>\src\bugarach\detect_folder.py`
- `<worktree>\src\bugarach\bench.py`
- `<worktree>\docs\FOUNDATIONS.md`
- `<worktree>\docs\MILESTONES.md`
