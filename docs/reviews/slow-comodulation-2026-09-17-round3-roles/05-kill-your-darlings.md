GRANT 5 ok — Read, Grep, Glob

# Line edit of the slow co-modulation explainer: 32 findings, 3 high

I reviewed `docs/learned/slow_comodulation/README.md` in the `unsup-slow-comodulation` worktree, at commit 2f77de1. I read it top to bottom along with `docs/writing_conventions.md`.

The page is mostly clean line by line and follows the house voice. The biggest problem is that the summary at the top says things the body contradicts:
- It says **one group of mice carries most of the minute-scale excess**. The "By group" section says the result is **not one group's**.
- It calls the Dard et al. 2022 dataset's excess **large** without saying why. The body finds it reads larger mainly because that dataset images more ROIs.
- The "label-free thread" section opens by saying **nothing was run against a trained model**. Its own fourth bullet reports a check that was run against trained models.

After that, the main line-level problems are:
- "Baseline" carries three meanings on one page.
- Slow shared change goes by six names on one page.
- The three surrogates are defined twice, almost word for word.
- There is a preview sentence the house voice bans.
- Several figure and panel references give a letter with no name.

## Banned-construction search (house list from the role-5 checklist, run by hand with Grep)

`murderboard_prose.sh` is not vendored and I have no shell. These are Grep results, not tool output.

| construction searched | pattern | hits (line · text · kind) |
|---|---|---|
| delve, leverage, robust, seamless, crucial, landscape, tapestry | `\b(delve\|leverage\|robust\|seamless\|crucial\|landscape\|tapestry)\w*`, ignoring case | 372 · "rank trial shifting the most **robust** surrogate" · banned word |
| not just X, but Y / not only…but also | `not just\|not only\|but also` | none |
| it's not about A, it's about B | `it's not about\|it is not about` | none |
| it's worth noting / worth mentioning | `worth noting\|worth mentioning` | none |
| "In today's ___" opener | `In today's` | none |
| em-dash pivot into an uplifting close | every `—` (9 lines: 48, 85–86, 202, 237, 273–274, 277, 309) | none. Every dash is a parenthetical or a table cell; none ends on an upbeat close |
| three-item list built for rhythm | read by hand: 317–318, 321–322, the three readings in the aside at 277–287, 19–34 | none. Every triple names three real alternatives |
| "X, not Y" reversals (checked in case they were the banned pivot) | read by hand: 22, 274–275, 347, 403 | not hits. Each one states a substantive distinction |

**Also searched, for the house rules:**
- **"data" plural:** lines 44, 326 and 380. None has a verb in agreement.
- **British spellings** (`artefact|summarise|centre|analyse|colour|behaviour|modelling|labelled|favour`): two hits, at 323 and 393.
- **Bare enumerated labels:** checked with `(step|set|option|…|§)\s+[0-9A-Z]` and a pattern for panel letters in parentheses.
- **"modality":** none.

## Block table

Word counts are hand estimates, because the tool was not run.

| block (lines) | words | sentences | payload sentence | where it sits | what the other words buy | verdict |
|---|---|---|---|---|---|---|
| "Why this page exists" (3–10) | ~97 | 3 | "whether shared modulation over tens of seconds counts as coordination" | middle of the second sentence | citations (keep); the parenthetical about the branch revising the rigid-shift report (only provenance) | trim the parenthetical; the timescale clashes with the decision (finding 4) |
| status callout (12–15) | ~50 | 3 | "nothing here is a milestone" | first | how to read "Measured" and "argued" (needed) | keep |
| short answer (19–34) | ~260 | 8 | the last bullet: rigid shift leaves minute-scale change on both sides | end | the per-dataset results (needed); undefined terms (CoactDetect, 2-minute blocks, promiscuity probe, "training contrast") | fix the contradictions (findings 1–2); define or cut the terms (finding 9) |
| decision pointer and roadmap (36–40) | ~80 | 2 | the first sentence | first | the second sentence is a preview of the sections | cut the second sentence (finding 5) |
| "The data." (44–53) | ~150 | 6 | the definitions | throughout | the ±2 s field-step detail is used again only at 348 | keep; could move the field-step detail |
| "The two kinds." bullets and the paragraph after them (55–70) | ~220 | 9 | "Both light more ROIs than independent cells would." | first sentence of the paragraph | defining the surrogates and CoactDetect, which is repeated in the Figure 2 caption | remove the duplication (finding 6) |
| Figure 1 caption (74–83) | ~190 | 9 | the warning that a log axis makes widths look equal | end | world definitions (needed); "depth chosen to be visible" (empty) | give the depth as a number (finding 20) |
| darkroom recording (85–89) | ~75 | 3 | "the rigid shift follows the recording's minute-to-minute swings almost exactly, and the circular shift does not" | end | where the file is and why it is not reproduced | promote the payload; fix "coordination" and the § reference (findings 10, 13) |
| excess coincidence (93–100) | ~140 | 8 | narrow peak vs broad shoulder | middle | the definition (needed) | keep |
| count-variance ratio (102–109) | ~150 | 7 | "the same thing seen two ways" | end | the definition; the Schluter gloss is repeated in the lineage at 363–364 | keep; cut one copy of the gloss |
| ⚠ relative to the window (111–115) | ~80 | 3 | why detrended numbers are reported | end | the reason for it | keep; "only partly visible" is vague (finding 30) |
| Figure 2 caption (121–125) | ~85 | 5 | what each surrogate does | throughout | repeats 62–70 | keep this copy; cut the other |
| Figure 3 caption (129–137) | ~170 | 7 | the arm definitions and the trimmed window | throughout | needed | fix the garden-path sentences (finding 15) |
| "Measured, from Figure 3" (139–157) | ~330 | 12 | "Surviving rigid shift at that bin width says nothing about what carries the change." | end of the third bullet | evidence (keep); a lab-slow claim that is not in Figure 3 | move the stray claim; fix the probe window (findings 11, 12) |
| Figure 4 caption (163–170) | ~160 | 6 | arms and datasets | throughout | needed | keep |
| Figure 5 caption (174–179) | ~100 | 5 | shading and the CoactDetect settings | throughout | needed | keep |
| "Measured, from Figures 4 and 5" (181–207) | ~560 | 20 | fast stream: "the pooled minute-scale excess is concentrated in some recordings, and about a third … is a straight-line trend"; Dard et al.: "reads larger mostly because it images more ROIs" | end of each bullet | numbers a sceptic would ask for (keep); the undefined "the reference" | **promote each bolded conclusion to the head of its bullet** (finding 7) |
| details: three tables and a paragraph (212–253) | ~95 in the paragraph | 4 | the leave-five-out result | first sentence | the removal shares | keep; label the table units (finding 24) |
| Figure 6 caption (260–265) | ~95 | 5 | group labels and the reading of them | end | needed | keep |
| "By group" paragraph (267–275) | ~190 | 6 | "The pooled result is not one group's, and it is not evenly spread." | first | evidence; the group-vs-imaging-day ⚠ (needed) | keep; "blocking" (finding 8) |
| slow-stream dip aside (277–291) | ~240 | 9 | "Splitting the lagged pairs … would separate …" | end | three readings (needed); the dead-time histogram | promote the test; add units to the counts (finding 14); the aside sits under "By group" (finding 26) |
| label-free thread (295–313) | ~370 | 13 | "what the contrast paid for was the events and structure faster than about 40 s" | middle of the first bullet | the cross-check on the other branch (keep); a `count_excess` bullet that says nothing checkable | fix the lead (finding 3); fix or cut the last bullet (finding 16) |
| decision (317–330) | ~215 | 8 | "No record in this tree says anyone has asked the producer, or the Dard et al. authors" | end | candidate sources (evidence for whose question this is) | promote the ⚠ next to "Nothing here says where the change comes from" |
| "What this does not settle" (334–350) | ~300 | 14 | one per bullet | head of each bullet | the effective-mice bullet repeats 205–207 | cut the repeat; "scatter" (finding 18) |
| published lineage (354–386) | ~600 | 20 | one citation per claim | head of each bullet | the Louis → Pipa → Harrison & Geman → Grün chain is the author being thorough | cut the chain to one citation plus "drops, not rolls" (finding 22) |
| reproduce (390–404) | ~150 in the paragraph | 5 | what the tests check | one sentence of ~95 words | needed | make the test list a bullet list (finding 28) |

## Findings

"Verified" means I checked the claim against the page itself or a file in the tree.

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | 24–25 vs 267 | The short answer says "one group of mice carries most of it". "By group" opens with "The pooled result is not one group's", and 273–275 say these are differences between groups of recordings, not group differences. The DI group's pooled ratio is 3.71 at 1-minute bins; the OVX group's is 3.30. | high | "and it is uneven: DI recordings sit highest, and every group leans on one mouse". Drop "group of mice". | yes |
| 2 | 28–29 vs 202–204 | The short answer calls the Dard et al. excess "large" and leaves out the body's own conclusion: per pair of ROIs it is 0.021, against 0.019 on the lab fast stream, and "the dataset reads larger mostly because it images more ROIs". | high | Add "— per pair of ROIs it is close to the lab fast stream; the size comes from imaging more ROIs". | yes |
| 3 | 295 vs 306–310 | "nothing here was run against a trained model" is followed by a bullet reporting how models trained against rigid shift scored. | high | "Argued from the figures above. The only trained-model result is the check on `unsup/rigid-shift-report-residuals`, reported here, not rerun." | yes |
| 4 | 7 vs 317, 59–60 | The question at the top is about modulation "over tens of seconds". The decision at the end is about change "over a minute or more". A reader cannot tell whether change between 10 s and 45 s is part of the decision. Line 302 explicitly leaves that range unseparated. | medium | Use one timescale in both places, or say in the decision that change between 10 s and 45 s is left open. | yes |
| 5 | 38–40 | "The page builds to it in this order: …" previews the sections and repeats the headings. The house voice bans previews. | medium | Delete the sentence and keep the first one. | yes |
| 6 | 62–70 vs 121–125 | Rigid shift, circular shift and block control are each defined twice, with near-identical wording: "slides each train by its own lag and wraps it around", "does the circular shift inside each 2-minute block separately". | medium | Keep the definitions beside Figure 2, the surrogates drawn. At 62–70, keep only the label-free detector, surrogate and CoactDetect, pointing to Figure 2. | yes |
| 7 | 183–191, 199–204 | The payload of each "Measured" bullet is its last, bolded sentence, reached only after 7 to 10 numbers with intervals. | medium | Start each bullet with its bolded conclusion and put the numbers after it. | yes |
| 8 | 1, 7, 19–34, 59, 190, 317, 327 | One quantity goes by six names: "co-modulation" (title only), "shared modulation", "shared change in onset rate", "drift" (defined at 59 but seldom used), "minute-scale excess", and "minutes-scale" at 327 next to "minute-scale" elsewhere. Line 268 adds "blocking" for the block control. | medium | Pick "shared modulation" for the general quantity and "drift" for a minute or more, and use them everywhere. Write "minute-scale" and "the block control". | yes |
| 9 | 21–34 | The short answer uses CoactDetect, "scrambled within 2-minute blocks", "promiscuity probe", "label-free models", "training contrast" and "faster structure" before any of them is defined. CoactDetect is defined at 68; the probe only at 155, though 75 uses it too. "Faster" has no comparison. The title and the short answer also use "ROI" before it is spelled out at 46. | medium | Spell out "region of interest (ROI)" in the first bullet. Replace the jargon with plain gists: "the lab's event detector", "a 5-minute rise in every ROI's rate that the generator plants". Write "structure faster than about 40 s". | yes |
| 10 | 87 | "FOUNDATIONS §5" is a bare section index. | medium | "(the data policy in FOUNDATIONS)" | yes, FOUNDATIONS.md line 125: "## 5. Data policy" |
| 11 | 155 | "raised by 0.06 onsets per second for 1,200–1,500 s" reads as a duration of 20 to 25 minutes. It means the window from 1,200 s to 1,500 s, a 5-minute probe, which is what line 31 says. | medium | "raised by 0.06 onsets per ROI per second from 20m to 25m" | yes, 300 s matches "5-minute" at 31 |
| 12 | 152–153 | Under "Measured, from Figure 3" (synthetic data only) sits "on the lab slow stream removing episodes first lowers what it keeps". That is lab data, not in Figure 3. "the sign" also overclaims. | medium | Move the clause to the lab slow-stream bullet near 192–195 and write "a sign". | yes, Figure 3 caption 129–137 |
| 13 | 85 | "What coordination and drift look like …: its population count per minute". Per-minute counts cannot show sub-second coordination. | medium | "What drift looks like …" | no, the darkroom PNG was not opened; the conclusion follows from the sentence's own description |
| 14 | 281–282 | "per second of interval there are 15 at 2.8–3.4 s, 95 at …, about 1,050 beyond": the counts have no unit and no pooling basis. | medium | "15 within-ROI intervals per second of interval width, pooled over all slow-stream recordings" (or whatever the true basis is) | yes, the unit is missing on the page |
| 15 | 132–133, 136 | Two garden-path sentences. "**Episodes removed, then block control** runs CoactDetect …" reads as a clause. "so onsets rigid shift drops never enter" is missing a relative pronoun. | medium | "The arm *episodes removed, then block control* runs …"; "so that onsets dropped by rigid shift never enter". | yes |
| 16 | 311–313 | "Whether that is why it scored as it did there is not tested here." The reader is never told how `count_excess` scored, so the bullet asserts nothing checkable. | medium | Give the score and where it comes from, or cut the bullet. | yes |
| 17 | 46, 311, 321, 325, 348 | "Baseline" means three things: the stretch before treatment, a reference detector (`count_excess`, "a baseline on that branch") and baseline fluorescence. | medium | At 311, write "a reference detector with no fitted parameters". | yes |
| 18 | 343–344 vs 156–157 | The page explains the generator background's 0.88 as a systematic offset from a fixed 60 s grid, then later calls it "scatter". | low | "so synthetic ratios carry an offset of about 10 %; differences smaller than that are not separable". | yes |
| 19 | 298–302 | "faster than about 40 s" is never derived (it is 2*J* at *J* = 20 s), and the next sentence says "between 10 and 45 s". | low | "faster than about 2*J* = 40 s", and use 40 s in both places. | yes |
| 20 | 79, 345 | "their depth is chosen to be visible" gives no number, and "five to ten times deeper" uses an undefined measure. | low | State the modulation depth, for example as the peak-to-trough fraction of the rate. | yes |
| 21 | 70, 99, 139, 141–154, 181, 298, 305 | Figure references give a number without a name ("Figure 2", "Figure 3, panel F", "Figures 4 and 5"). The findings bullets cite bare panel letters, "(B–D)" and "(F)", well after the letters were defined. The house rule wants number and name. | low | "Figure 3, what the surrogates remove, panel F". In the bullets, add the world names: "(20 s, 5-minute and shallow 1-minute worlds)". | yes |
| 22 | 365–373 | The Louis → Pipa → Harrison & Geman → Pipa, Riehle & Grün → Grün chain is thoroughness a sceptic will not ask for. The "robust" hit sits in the same bullet. | low | Keep Louis et al. and Harris, plus "this page drops rather than rolls". Cut the chain. Rephrase Stella et al. with their actual criterion, or state why "robust" stays as their term. | yes |
| 23 | 323 | "artefact" is British spelling. | low | "artifact" | yes |
| 24 | 214, 244 | The first details table has no unit in its header; the paired-differences table gets "(dimensionless)" only in its lead sentence. Each cell of the per-recording table packs three unlabeled quantities. | low | Header "1 s bins (ratio, dimensionless)". Split the per-recording table into three columns: median [quartiles], % of recordings above 1, detrended median. | yes |
| 25 | 188–189 | "scored against the reference": "the reference" is undefined here. It is the 8-draw mean, per 240–241. | low | "against the 8-draw mean" | yes |
| 26 | 196, 277 | "see the aside below" points 80 lines ahead, into the "By group" section, which is not about the dip. | low | Say "see *Why the slow stream dips*, under By group", or move the aside into the lab slow-stream bullet. Where it sits between sections is the order reviewer's call. | yes |
| 27 | 207 | "23–25" has no unit and no dataset. | low | "23–25 effective mice across the three datasets" | yes |
| 28 | 398–404 | The test sentence lists nine checks in about 95 words. | low | Make it a bullet list. | yes |
| 29 | 393 | The row says "re-summarize" and the flag beside it says `--resummarise`. "rebuilds both summaries … from results.json" also reads as if `results.json` were one of them. | low | Rename the flag in the tool (American spelling); write "rebuilds `summary.json` and its checks from `results.json`". | yes (spelling); no (did not open the tool) |
| 30 | 113 | "a change that spans the whole window is only partly visible": which measurement it is invisible to is not said. | low | "is only partly visible to the excess coincidence". | yes |
| 31 | 326–327 | "movement within about 2 s of a movement" repeats itself, and "report activity stable" is missing "that … is". | low | "link activity to movements within about 2 s, … and report that activity is stable across each recording". | yes |
| 32 | 306 | "the unmerged branch" points back about 300 lines to line 9. | low | Name it: `unsup/rigid-shift-report-residuals`. | yes |

All paths are relative to `<worktree>/`. I edited nothing.
