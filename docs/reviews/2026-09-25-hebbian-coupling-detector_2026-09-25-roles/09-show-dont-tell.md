GRANT 9 ok — Read, Grep, Glob, Bash

**Role 9, Density & figure-first, round 1.** Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md (183 lines). As instructed, I treated each `##` section as a page, plus the preamble.

**Thresholds I used.** These are conventions, not researched optima.
- More than 40 words on a page.
- Any single text block over 60 words. A block is one paragraph or one bullet.
- A methods or results page with no figure.
- Two or more prose-only pages in a row.
- A figure under about 50% of the page.

The 40-word slide limit is loose for a written proposal: every section trips it. The block limit, the missing figures and the prose-only run are the ones that matter here.

**Figure share.** The document has no figures at all: no `![`, and no `.png` or `.svg` reference. So figure share is 0% on every page, and there is no rendered figure whose size could be measured.

## Count table

| page | total words | largest block (words) | figure? | figure share |
|---|---|---|---|---|
| preamble (status + abbreviations) | 199 | 69 (abbreviations) | n | 0% |
| The idea | 122 | 79 | n | 0% |
| The rule: eqs 7 and 8 | 221 | 66 (eq 8, the bound) | n | 0% |
| What changes for calcium events | 537 | 111 (width); also 106 (rate-neutral), 88 (frame grid), 74 (kernel point) | n | 0% |
| What the detector reports | 216 | 63 (readout 3) | n | 0% |
| What could make this worthless | 297 | 148 (Check A); 123 (Check B) | n | 0% |
| Stages | 264 | 101 (distance); 68 (simulation) | n | 0% |
| How the code arrives | 141 | 89 | n | 0% |
| What this does not claim | 93 | under 60 (3 bullets) | n | 0% |

**Every page is prose-only: 9 in a row, about 2,090 words.**

## Findings

Columns: location · issue · severity · suggested fix · could I verify it against a source.

**F1 · "What changes for calcium events" (lines 56–93) · major · verified: yes (I read the section and the jitter run's README and Figure 2)**
- **Issue:** This is the proposal's central technical argument: the kernel point, the rate-neutrality claim, the half-weighted end lags and the choice of width. It is 537 words in four blocks over 60, and it describes a curve on a lag grid that is never shown. The claim "sums to −1 rather than 0 unless the end lags are halved" is a picture. So is "one jitter leaves the kernel three lags long". CLAUDE.md's "Show the picture" rule applies directly.
- **Replacement: new Figure 1, the kernel on the frame grid.**
  - Panel A: Co(Δt) = cos(πΔt/w) as a continuous curve, with stems at the whole-frame lags (0.1 s frames) for w = 2, 3 and 4 jitters (fast stream, 0.106 s).
  - Draw the two end stems hollow at half weight, and print both sums beside each: "−1 unweighted / 0 trapezoid".
  - Panel B: the real pair-lag correlogram, the black curves in panel C of the jitter README's Figure 2 (from `jitter_correlogram.json`), overlaid with the kernel at each candidate w. The reader then sees where real coincidences fall on the positive lobe and on the near-miss lobe.
  - Panel C: expected update against window length, for independent trains. It should be zero at a window of exactly w, negative when longer and positive when shorter. Label it "derived, not measured", as the text does.
  - Plot the x axis in frames and seconds, and give the frame interval, per the units rule.
- **Prose that stays:** one sentence per bullet saying what to look at. The first-order caveat about q(s) moves to the caption or a footnote. It is relocated, not deleted.
- **Stale-data caveat if Figure 2 is reused:** the jitter README carries a ⚠ "data have since changed" banner. The reused panel must carry that caveat in its caption.

**F2 · "The rule", eq 7 and eq 8 blocks (lines 42–50) · minor · verified: yes (clamor/docs/model.html)**
- **Issue:** The bound q(s) is described in words and one inline formula. It is a downward parabola that reaches zero at s₀(1 ± s_d).
- **Replacement:** a small panel with q(s) against s, marking s₀ and the two zeros at s_d = 0.8. clamor's docs/model.html already contains exactly this two-panel figure: "The two shape functions … Co(Δt) … q(s)".
- **Do not embed clamor's figure as it stands.** clamor is private, and that panel is drawn at the resting run's period, not at period 2w. Re-render both shapes from the stamped copy in bugarach, at period 2w and burst w. The q(s) panel can be panel D of Figure 1, or Figure 2.

**F3 · "The idea" (line 24, 79-word block) and the "Pairs" bullet (lines 62–64) · major · verified: yes**
- **Issue:** The learning procedure is narrated: walk in time order, strengthen, weaken, and the subliminal ROI stays at s₀. This is the walk-through the task names, and it is never shown.
- **Replacement: new figure, the learning walk-through, drawn as a schematic from a synthetic toy.**
  - Four or five ROIs over a few seconds, as a black-and-white raster.
  - A lane above it with down-pointing ▼ marks at each onset. Colour gives the sign of each pair update: green for a coincidence, red for a near-miss. Nothing is drawn on the raster itself (CLAUDE.md raster rule, sapper SAP009).
  - To the right, heatmaps of D at three moments. One ROI has no onsets and its row stays at s₀: that is the subliminal rule, visible.
- **Prose that stays:** "The idea" shrinks to about two sentences pointing at the figure. The paragraph on the failure of the plain Hebbian rule (line 30) is fine as prose.

**F4 · "What the detector reports" (lines 95–113) · minor · verified: yes**
- **Issue:** Three readouts, each running from the matrix D to a statistic, a null and an output. The same pipeline is described three times in prose.
- **Replacement:** a flow schematic. Onsets feed the rule, which produces D. D then branches three ways:
  1. the Frobenius norm and leading eigenvalue against a histogram from the circular-shift surrogates;
  2. the spectrum plus overlapping groups;
  3. a trace of E(t), with the threshold set on the surrogates.
- Each branch labelled "significance test only" or "a call" as the text does. Or state that prose is acceptable here. It is the weakest of the figure candidates, because the ideas are distinct rather than sequential.

**F5 · "What could make this worthless" and "Stages" (lines 115–159) · major · verified: yes**
- **Issue:** Two blocks of 148 and 123 words, plus Stages at 264 words. Together they hold the decision logic Tony is actually asked to act on: the stop thresholds "for Tony to set or change before any number is read". That logic is spread across two sections of prose.
- **Replacement:** a stage and stop-rule flowchart.
  - Stage 0, Check A: residual variance after the leading eigenvector, against surrogates. If it is at null level, drop readout 2 for that stream. Continue only if readout 3 beats CoactDetect.
  - Stage 1, simulation: Check B, the rank correlation between D and STTC. If it is above 0.9 in most recordings, stop and run readouts 1 and 2 on STTC directly. Freeze w and q₀.
  - Stage 2: real baseline recordings, in the order DI, OVX, MALE, ORX.
  - Stage 3: back to clamor.
  - Stage 4 (distance): drawn dashed, labelled "waits on data we do not have".
  - Put the two proposed thresholds in highlighted boxes on the branches, so the decisions Tony must make are visible at a glance.
- **Prose that stays:** the reasoning behind each check shrinks to two or three lines under the chart. The distance paragraph (101 words; the crosstalk caveat and the ADR-0007 request wording) stays as prose but moves to its own short subsection or an appendix. It is relocated, not cut.

**F6 · run of 9 prose-only pages · major · verified: yes**
- **Issue:** Nothing breaks the prose from the first line to the last, in a repo whose CLAUDE.md says to render before describing.
- **Fix:** F1, F3 and F5 together break the run at the three points where a reader would otherwise have to picture something. Number them Figure 1 to Figure 3 or more (CLAUDE.md numbering rule), and cite each by number and name in the prose.

**F7 · existing figure `clamor:figures/model.svg` · minor, advisory · verified: yes**
- **Issue:** It shows the 1986 oscillator network: 20 E-cells and an H-cell inhibitor, with α and β. The proposal says explicitly (line 58) that "the oscillator is left behind". Reusing it would show readers the machinery this proposal drops.
- **Fix:** do not reuse it. If a one-line "what the 1986 model was" figure is wanted, it belongs in an appendix, captioned as the thing not being used.

**F8 · places where prose is right, and why · no action · verified: yes**
- Preamble status box: provenance and the decision record, which is the text's own job. The 69-word abbreviations block is a glossary: acceptable, or optionally a two-column table.
- "How the code arrives" (89-word block): licence, provenance stamp and CI dependency. These are facts with no shape to draw.
- "What this does not claim": caveats. Keep every word. These are what a review earns and must not be cut to meet a count.

**Boundaries.**
- I did not check whether the figures are numbered or whether the cross-document reference "the jitter run's README, Figure 2" names its figure. Those belong to other roles and to agent 10's mechanical checks.
- No rendered figure exists, so there is no canvas geometry for agent 10 to measure either.
- Nothing was written to the scratchpad.
