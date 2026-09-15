> **Public copy.** Lines that concern real treatment recordings are removed (33 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 11 ok — Read, Grep, Glob

# Role 11: argument order ("Start With the Problem"), blind pass, round 2

**Artifact read:** `detector_review_plain.txt`, checked against `detector_review_textview.html` for the order of the opening. I also opened `fig01_problem.png`, because the cold open depends on which panel comes first.

**What I checked:** the order of the title, summary, contents and the twelve sections, plus the order of panels in Figure 1. I checked whether the summary's claims point at the right evidence, whether the ending lands, and each of the four departures from the brief. I did not check whether individual claims are supported (role 4) or whether a single section reads well to a stranger (role 8), except where a pointer or a position depends on it.

## The spine: one claim per unit

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **§2 Surrogates.** The circular shift keeps each cell's own spacing, so its bar is not too low the way a shuffle's is. Real baselines line up more than a shift explains. A bar from nearby seconds rides out a busy stretch where a whole-recording bar fires 46 times, at a cost in sensitivity that is not measured.
- **§3 Hand-written detectors.** The six differ in what they count, where "chance" comes from and how the bar is set. Designs with one bar per stretch (binned SCE, locust) are predicted to flood busy stretches; designs with a local bar are not.
- **§4 Learned detectors.** The tube family learns a center-versus-surround comparison. The ratio versions were built to resist busy stretches. The two controls (trace, tiny) failed to train.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **§6 Grading and tuning.** F1 with a 2.5-second hit window, a separate limit on busy-block calls, and settings chosen in 4 rounds on recordings the score never uses.
- **§7 Simulated results.** Five detectors tie. A busier background costs sensitivity to small events. Some high scores come with many busy-block calls. Some tuned settings sit at the end of their lists.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **§11 Sources.** Where each method comes from.
- **§12 Word list.** Definitions.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Verdict on the four departures from the brief

1. **Problem section first: serves the reader, but the opening doesn't do the job yet.** See blocking-free majors 1 and 2 below.
2. **Surrogates before detectors: serves the reader.** Table 1's "how it judges chance" column, and every "what the design risks" note about busy stretches, only make sense once §2's whole-recording versus nearby-seconds contrast is known. The cost is that §2 uses words defined later (see minor findings 2 and 3).
3. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
4. **Word list as an appendix: serves the reader,** because terms are explained where they first appear. The one exception is at the cold open itself (minor 3).

A fifth departure is taken from the brief rather than added: the detectors come before the simulator. Figures 3 to 9 all run on a bench recording that §5 has not yet described. The "test recording" paragraph in §3 covers enough of the gap, so I judge this acceptable (minor 2).

---

## Blocking

None. The problem is near the top, and the one figure that shows it is in §1.

## Major

**M1. §1 never says what the problem costs.**
- **Location:** §1, paragraphs 3–4.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes (the claim's own text is in "In short", §7 and §10).

**M2. §1 doesn't set out the route, and Figure 1B has no job in the prose.**
- **Location:** §1 prose; Figure 1 panel B.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes.

**M3. The cold open leads with background and a result, and the picture of the problem comes last.**
- **Location:** the "In short" box order; §1 paragraph 1; the panel order of Figure 1.
- **Issue:**
  - **Summary box:** the first thing a reader sees is a result on simulated recordings scored by F1, before they know what either is. The problem itself ("the detectors disagree more than ten-fold, and nobody can say which is right") is the last bullet.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **Figure 1:** the first panel is a quiet raster with nothing on it (A). The disagreement, which is the one image that shows the problem, is the bottom panel (C). This repeats the pattern behind this role's founding incident: the problem appears, but not first.
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **§1 prose:** open with one sentence stating the disagreement and pointing at the figure, then the preparation.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes (box order, panel order and paragraph order were all checked in the built HTML and PNG).

**M4. "In short" bullet 3 points at the wrong evidence, and its claim is broader than §7.**
- **Location:** "In short" bullet 3.
- **Issue:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - Figure 2C is, in its own caption, "an illustration, not any one detector's rule".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **The claim is broader than the evidence.** The same table shows tuned rate+context at 5.3 calls per minute, over its limit in 4 of 4 rounds, even though it takes chance from nearby seconds. tube also calls about once a minute there.
  - **"Matters most" has no support.** No section compares how much each factor matters.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes.

**M5. The ending trails off into caveats and never answers §1's question.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes.

**M6. Figure 11C is a result placed in the methods section.**
- **Location:** §6.3, Figure 11C ("Section 7 reads this figure").
- **Issue:** panel C shows each detector's scores across its setting list on all 24 recordings. That is a result, and its interpretation comes a whole section later. The evidence arrives before the claim it supports, with a note apologizing for the order.
- **Fix:** move panel C next to "What Figure 11C shows about the tuning" in §7, either as a panel of Figure 12 or as its own figure after Figure 12 (renumbering later figures). Figure 11 keeps A (the grading rule) and B (the rounds), which are method.
- **Verifiable against source:** yes.

## Minor

**m1. Within §7, the qualifications of the tie come four paragraphs after the tie.**
- **Location:** §7, paragraph order.
- **Issue:** "What Figure 11C shows" (LoCo and binned SCE picked the loosest value on the list; SPIKE-synch's list doesn't control it) and the paragraph on learned-detector spread both qualify "Five detectors score about the same". They arrive after the busy-background and busy-block paragraphs.
- **Fix:** move both paragraphs to immediately after the paragraph on the tie and shipped settings.
- **Verifiable against source:** yes.

**m2. Simulator vocabulary is used before §5 defines it.**
- **Location:** Figure 1B, Figure 2C caption, §3's test-recording paragraph, §4 opening.
- **Issue:** "planted event", "busy block" and "decoy" are used in §§1–4. Each place explains the term locally or points ahead, so nothing is unreadable, but four places carry the explanation instead of one.
- **Fix:** once M2's roadmap sentence is in place, add a single sentence in §1 alongside Figure 1B defining the three terms, and cut the repeated glosses. Keep §5 where it is: its checks on the simulator belong next to grading.
- **Verifiable against source:** yes.

**m3. Terms from §8 and §12 are used earlier.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Issue:** the cold open sends the reader to the last section for "stream". The four groups aren't named until §8.
- **Fix:** explain streams in one clause at first use in §1. In §2, write "four groups of mice (Section 8)".
- **Verifiable against source:** yes.

**m4. A §2 finding is never used again.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Issue:** this is a finding (real baselines line up about ten times more than the shift predicts at 8 or more ROIs) with no later use. Nothing downstream picks it up.
- **Fix:** give it a job or shorten it. Either cite it in §1 as evidence that there is something to detect, or connect it in §10 to the caveat that a whole-baseline shift also breaks shared slow changes.
- **Verifiable against source:** yes.

**m5. The failed controls have no job in the argument but appear throughout.**
- **Location:** lede ("Twelve computer programs"), §4.2, Table 2, §7 ("as did, slightly, the two failed controls"), §8, Table 3.
- **Issue:** trace and tiny failed to train, and §4.2 says their failure shows nothing about the tube design. They support no claim, yet they are counted in the title's "twelve" and add a footnote and extra notes along the way.
- **Fix:** say "ten detectors, plus two controls that failed to train". Keep §4.2 as a short note, and move their rows in Tables 2 and 3 to a footnote or an appendix line.
- **Verifiable against source:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Issue:** §3 itself says its two windows show how a detector works, not how well. The measured busy-block behavior is in Figure 12B and Table 2.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** add one line before Table 3. For example: "Section 3 listed what each design should do well and badly; this table is what Sections 7 and 8 measured."
- **Verifiable against source:** yes.

**m8. §4's training setup doesn't match §6.3's without a bridge.**
- **Location:** §4 opening versus §6.3.
- **Issue:** §4 says each network trained on 10 recordings and chose its call level on 2. §6.3 says the graded learned detectors train on the rounds' 18. The only link is a clause in the Figure 9 caption.
- **Fix:** in §4 add "(these are the copies drawn here; Section 6.3 trains fresh copies for grading)".
- **Verifiable against source:** yes.

**m9. The §10 caveats don't say which conclusion each one threatens.**
- **Location:** §10, "What could be wrong".
- **Issue:** for example, "quiet level busier than intended" weakens the quiet/busy contrast in "In short" bullet 2, and "decoys cap precision" affects the "one false call for every two correct ones" line.
- **Fix:** tag each caveat with the claim it affects.
- **Verifiable against source:** yes.

**m10. Two other "In short" bullets lack pointers or overstate §7.**
- **Location:** "In short" bullets 2 and 4.
- **Issue:** bullet 2 has no pointer, and "every useful detector" is stronger than §7's "almost every" (tuned binned SCE rose). Bullet 4's "often mark the same moments" has no pointer.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable against source:** yes.

## Checked and left alone

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **"Read this first" at the top of §8:** correctly placed.
- **§11 sources after §10:** acceptable as back matter.
- **§6.2's busy-block limit:** defined before §7 uses it.
