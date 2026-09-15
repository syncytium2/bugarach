> **Public copy.** Lines that concern real treatment recordings are removed (23 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 11 ok — Read, Grep, Glob

# Role 11: argument order ("Start With the Problem")

I read the whole text view and looked at Figures 1 and 15. I made no edits.

## 1. The spine: one claim per section

0. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
1. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
2. **Glossary:** Defines 13 terms. It makes no claim.
3. **Surrogates:** The circular shift keeps each cell's own spacing where a shuffle does not. A bar built from the nearby 60 s follows a busy stretch, while a bar built from the whole recording fires 46 times inside it (Figure 2C).
4. **Hand-written detectors:** All six test "more lineup now than chance". They differ in what they count, how they model chance, and where the bar sits. A whole-recording bar (binned SCE, locust) fires in the busy block and a local bar does not (Figures 3–8).
5. **Learned detectors:** tube is a trained center-minus-surround filter. The guard and ratio variants each change one thing. The controls trace and tiny do badly, which shows tube's design is doing the work.
6. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
7. **Grading and tuning:** A hit is within 2.5 s, matched one-to-one. The setting is chosen over four rounds of cross-validation, and busy-block calls have a per-detector limit that the tuning does not enforce.
8. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
9. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
10. **Strengths and weaknesses table:** A per-detector verdict drawn from Sections 4–9.
11. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
12. **Credits:** Where each method comes from.

## 2. The arc I judged against

The default analysis arc (problem → cost → method → what it gets wrong → fix → evidence → residual risk) does not fit a comparison of twelve methods. I used this adapted version:

**problem → why it matters (cost) → chance model → the detectors → how we get an answer key (simulator, grading) → evidence (simulated) → application (real) → verdict per detector → residual risk → sources.**

In this arc, the "what the method gets wrong → fix" step is "a global bar fails in busy stretches → a local bar". That idea runs through the whole document, but the document never says so.

Against this arc the spine is mostly sound:
- **Surrogates before detectors is justified.** The Section 4 table cannot be read without Section 3.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Strengths and weaknesses last** matches what the requester asked for.

These three departures from the requester's order are not written down anywhere. They belong in the delivery summary.

The spine breaks in four places:
- **The cost** is missing from the front.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verdicts are given twice**, once before the evidence (the boxes in 4–5) and once after it (Section 10). The two copies now contradict each other.
- **Residual risk** is scattered across four sections.

## 3. The cold open

The reader sees, in order: the lede, the "In short" box (setup and a hedge), a 12-item contents list, then Figure 1.

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## 4. Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source? |
|---|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 7 | §4.6 weakness "(Section 7)" | A forward reference that points at the wrong section. The claim that changing SPIKE-synch's bar barely changes its results is supported in §8 (F1 0.48–0.53) and Figure 11C, not §7's procedure. A claim followed later by its evidence is allowed, but the pointer should land on the evidence. | Low | "(Figure 11C; Section 8)". | yes |
| 8 | §7.1 → §7.3; §7.2 → §7.3 | Two forward references inside one section. 7.1 cites "its own limit (Section 7.3)" and 7.2 says "Section 7.3 explains why that matters". The limit is part of grading, and the flaw in 7.2 (tuning ignores the limit) only makes sense once the limit is known. | Low | Reorder to 7.1 grading → 7.2 the busy-block limit → 7.3 choosing a setting. Both forward references disappear. | yes |
| 9 | §5 ¶1 "trained on 18 simulated recordings (Section 6)" | "18" comes before the 24 = 4 × 6 split in §7.2 that explains it. The pointer names §6, but the number comes from §7.2. | Low | "on three of four groups of simulated recordings (Section 7.2)", or drop the count here. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 11 | Figure 11C placed in §7 | A result shown in the method section. The panel plots F1 against the setting on all 24 recordings, and the reader is told what to look for only in §8 ("three flaws we can see in Figure 11C"). | Low | Move panel C next to Figure 12 in §8, or leave it and add "discussed in Section 8" to its caption. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 14 | Order departures from the brief | The draft departs from the requester's order in three ways: surrogates before detectors, simulated before real, and a problem section plus glossary first. The first two are defensible (see §2 above); the glossary is not (#5). None is stated to the requester. | Low (a finding about the delivery, not the artifact) | Name the departures and their reasons in the delivery summary. | yes |

## 5. Earliest point where each section's claim can be judged

| Section | Earliest intelligible position | Where it is now | Verdict |
|---|---|---|---|
| In short (as rewritten per #3) | 0 | 0 | stays |
| §1 problem (with #1, #2) | 1 | 1 | stays |
| §2 glossary | appendix / reference | 2 | moves (#5) |
| §3 surrogates | after §1 | 3 | stays; it is required before §4 |
| §4 hand-written | after §3, plus a note on the test recording | 4 | stays; add the note (#6) |
| §5 learned | after §4 | 5 | stays; drop measured claims (#4) |
| §6 simulator | before §7; its test-bed facts are needed by §4 | 6 | stays; preview in §4 (#6) |
| §7 grading | after §6 | 7 | stays; swap 7.2 and 7.3 (#8) |
| §8 sim results | after §7 | 8 | stays; its cost paragraph is echoed forward (#2, #13) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| §11 limits | after §10 | 11 | stays; restructured (#12) |
| §12 credits | end | 12 | stays |

## 6. Checked and not found

- **"Table 1 'limit' before 7.3"** is not a defect in this draft. Table 1 sits in §8, after 7.3. Limits first appear in §7.1 (#8), and Figure 11C's red ✕ comes after 7.3.
- **"Busy block" in Figures 2–9** is defined inline when it first appears (Figure 2C caption, §4 bullets). The gap is the bench's other properties (#6), not the term.
- **"Planted event"** is defined in the glossary and in Figure 1B's caption before Figure 2.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **§12 at the end** is correctly placed. The single forward reference to it (§4.5) is fine.

**Boundaries:** Whether "few false alarms" is supported, and the facts behind #4 (i)–(iv), belong to agents 1 and 4. Whether Figure 1 is readable belongs to agent 8. Figure numbering and the unnumbered table in §4 belong to agent 10. I raise the contradictions only because they come from giving verdicts before the evidence.

**Files:**
- `<scratchpad>\review\detector_review_textview.html`
- `<scratchpad>\review\_work\fig01_problem.png`
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
