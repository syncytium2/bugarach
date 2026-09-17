> **Public copy.** Lines that concern real treatment recordings are removed (23 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 11 ok — Read, Grep, Glob

# Role 11: argument order ("Start With the Problem"). Blind pass, round 3

**What I read:**
- The built artifact's text, `detector_review_plain.txt`.
- The order of headings and figures in `detector_review_textview.html`, to see where Figure 1 actually sits.
- `_work/fig01_problem.png`.

I did not open any earlier review. Everything I report is about the order of sections. Whether a claim is supported belongs to agent 4, and whether a single slide is readable belongs to agent 8.

## The spine: one claim per section

0. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
1. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
2. **Surrogates.** Chance has to be estimated. A circular shift keeps each cell's own pattern, while a shuffle sets the bar too low. Where the surrogate comes from sets a trade-off: a bar from nearby time avoids false alarms in a busy stretch but hides real events there.
3. **Hand-written detectors.** Six ways to ask "more lineups than chance?", each shown on one test recording with what the design should do well and badly.
4. **Learned detectors.** The tube models learn center-against-surround widths. Two control networks failed to learn, and by the document's own account their failure proves nothing.
5. **Simulator.** Recordings with a known answer, built in four layers. Decoys cap F1 at 0.83. The simulator is wrong in four known ways.
6. **Grading and tuning.** Hit/miss rules, a busy-block limit on calls, and four rounds that choose each setting on recordings it is not scored on.
7. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
8. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
9. **Side by side.** What was measured for each detector.
10. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
11–12. References and word list.

## The arc I judged against

The default arc is: problem → cost → method → what the method gets wrong → fix → evidence → residual risk.

This document is an evaluation, so its arc is: **problem → why it matters → the principle (estimating chance) → the tools → the test bed → the grading rules → the verdict where the answer is known → the tools where it is unknown → synthesis → implication and residual risk.**

That is defensible, and the §1 roadmap states most of it. The one unstated deviation is that there is no "fix" step (finding m3).

## Cold open

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Verdict on the four departures from the brief

| Departure | Verdict |
|---|---|
| Problem section first | **Serves the reader.** An external reviewer gets the reason to care before the mechanics. It is weakened only by where Figure 1 sits (B1). |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Word list as an appendix | **Neutral to good.** Terms are defined inline at first use, so the list is for lookup. Placing it after the references is a minor miss (m6). |

## Does the ending answer the opening?

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Findings

| # | Location | Issue | Severity | Suggested fix | Checked against source? |
|---|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m3 | §10 | This is an evaluation with no "fix" step, and the document never says so. §10 ends on "none of these detectors provides one yet" and then lists what was left out. It does not say what would separate "cells got busier" from "cells coordinated more". | minor | Add one sentence stating that the document proposes no fix, and name what would close the gap, even if it is only the direction the lab is exploring. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m6 | §11 / §12 order | The lay reader needs the word list more than the references, but it comes last. | minor | Swap §11 and §12, or link the word list from *In short*. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

## What works and should survive the repair

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- §5's "What the simulator gets wrong" comes before any score, so the reader carries the caveat into §7 instead of meeting it afterwards.
