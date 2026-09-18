GRANT 5 ok — Read, Grep, Glob

# Line-editor review of the self-supervised rigid-shift README

**Artifact:** `<worktree>/docs/learned/tube_self_supervised/README.md` at f2278da. I read all of it once, from top to bottom. Nothing under `docs/reviews/`, `docs/handoffs/` or `docs/todo/` was opened.

**The banned-construction search did not run as a script.** `murderboard_prose.sh` is not vendored in this repo and I have no shell, so I ran the house list by hand with Grep. The list: *not just X but Y* (widened to "not only" and "not merely") · *it's not about A, it's about B* · *it's worth noting* · delve, leverage, robust, seamless, crucial, landscape, tapestry · *In today's* · em-dash pivots · lists of three built for rhythm. Three-item lists were judged by eye. I also searched for:
- singular "data"
- British spellings
- positional references ("third", "last two", "above", "below")
- abbreviations

**Block lengths were counted by eye** from line lengths, at roughly 14 words per line. Every word and sentence count below is ±15 %. Tables, the reference list and the command table were not counted.

## Count table: constructions found

| line | construction | kind |
|---|---|---|
| 468 | "the most **robust** of the surrogates" | banned word (paraphrasing Stella et al.) |
| 544 | "the most **robust** of the surrogates they compared" | banned word (same paraphrase, repeated) |
| 18 | "whatever the surrogate moves, **not only** what it was meant to move" | a near-form of *not just X, but Y* |
| — | *it's worth noting*, *it's not about*, *In today's*, delve, leverage, seamless, crucial, landscape, tapestry | no hits |
| — | em-dash pivot into an uplifting close | no hits (every "—" is an empty table cell) |
| 576 | "The transfer is ours, not the ideas." | antithesis used as a closing line; borderline decoration |
| 537 + 574–576 | section opens with a summary ("Nearly every component here is prior art") and closes by restating it | preview plus recap |
| 37, 503, 109 | "So the page asks, in order:" · "In the order the argument raised them." · "Four decisions follow, in *What waits on Tony*." | throat-clearing and previews |
| 200, 325 | "grey", "labelled" | British spelling (house rule is American) |
| — | singular "data" | no violations (lines 201, 543 and 565 carry no verb; 555 is "dataset") |

## Count table: blocks over about 80 words

| block (lines) | words (≈) | sentences (≈) | passage-tested below |
|---|---|---|---|
| 11–15 surrogate intro | 80 | 5 | no |
| 17–22 two things can go wrong | 90 | 5 | yes (ambiguity) |
| 24–29 architecture | 85 | 4 | no |
| 97–102 finding: twins | 85 | 3 | yes (garden path) |
| 103–108 finding: real recordings | 90 | 3 | yes |
| 111–118 Exploratory callout | 115 | 6 | yes |
| 146–155 what the per-ROI test can see | 155 | 7 | **yes** |
| 169–177 aggregate table legend | 135 | 5 | yes |
| 185–190 cells-mean trace | 90 | 4 | yes |
| 196–201 Figure 3 caption | 85 | 5 | no |
| 222–229 the builds | 115 | 5 | yes |
| 249–258 bake-off table notes | 145 | 7 | no (each clause carries a caveat) |
| 260–272 plant probe | 170 | 7 | **yes** |
| 278–283 Figure 4 caption | 85 | 5 | no |
| 305–312 label-free table notes | 115 | 5 | yes |
| 314–322 truth-reading coverage | 135 | 6 | **yes** |
| 345–351 two results | 100 | 3 | yes |
| 367–372 models on twins | 90 | 4 | yes |
| 384–391 Figure 5 caption | 110 | 5 | no |
| 407–412 event definition | 90 | 5 | yes (repeated elsewhere) |
| 414–419 rate-cap bullet | 90 | 4 | no (payload first) |
| 440–448 edge enrichment | 135 | 7 | yes |
| 450–454 and 456–461 "Nothing here is ground truth" (twice) | 70 + 90 | 4 + 6 | **yes** |
| 505–510 decision on shared modulation | 90 | 5 | no |
| 511–518 decision on which build stays | 120 | 5 | yes |
| 519–527 decision on the objective | 125 | 3 | yes |
| 528–533 decision on the rate | 90 | 4 | no |
| 539–550 whole-train shifting lineage | 175 | 8 | **yes** |
| 557–563 CFAR lineage | 105 | 4 | no |
| 565–572 learning against a surrogate | 110 | 4 | no (citations a sceptic would want) |
| 578–584 other labs' detectors | 105 | 4 | yes (sentence length) |
| 634–641 what the records show | 120 | 5 | yes |
| 643–650 surrogates provenance | 125 | 4 | no |
| 661–676 what changed | 200 | 1 + 4 bullets | yes |

## Findings

Severity: **H** = a reader-facing defect that should not ship · **M** = clarity or precision loss · **L** = polish. "Verified" = yes means I checked it against the artifact or the house-rule file.

| # | location | issue | sev | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | 450–454 and 456–461 | **The "Nothing here is ground truth." paragraph appears twice**, with the same first two sentences. The second copy adds seeds and repeats the event definition from 407. The first adds "four groups". | **H** | Merge into one paragraph: the second copy plus "in four groups". Drop "An event merges detections closer than 2 s", which line 407 already says. | yes |
| 2 | 17–22 | Ambiguous reference. "So the first test asks…" is followed by "The second is that rigid shift … also removes slow co-modulation", so "the second" reads as a second *test*, but the sentence describes a failure. The test that answers it is never named here. | M | Name both: "The **leak tests** ask whether anything besides alignment moves… The second risk: rigid shift at *J* = 10–20 s also removes slow co-modulation… The **synthetic twins** test for that." | yes |
| 3 | 146–155, passage test | Payload: *"The circular shift, not dither, is what shows this test has power against a leak rigid shift could have; on the slow stream the test also picks up slow shared modulation at 22.4 s and 44.8 s."* That is two points in one block, and the first sits in sentence 5 ("The circular shift is the control that can"). The last sentence (displacements rounded to 1.4 s frames) explains "22.4 s" only after the number has appeared. "A leak rigid shift could have" is never named. The block's own reasoning says the circular shift is caught through counts moving together across windows, which is slow co-modulation, so the reader cannot tell what kind of power the control demonstrates. | M | Split into two paragraphs. Paragraph one: open with "The per-ROI circular shift is the control that shows power…", then name the leak it stands in for. Paragraph two: the slow stream, with the rounding sentence placed before 22.4 s. | yes (the ambiguity; not the logic) |
| 4 | 260–272, passage test | Payload is at the end: *"Read the panel as a direction: the counting builds separate a synchronous plant from bursts and fuzz more than `tube` does, and the builds cannot be ordered among themselves."* The four ratios (1.99 / 1.75 / 1.60 / 1.43) set up an ordering the next clause withdraws. The **wave** plant is defined but no result for it appears, except that its span "grows with the plant by construction". The burst claim carries no number. | M | Promote the direction sentence to the top. Give the ratios as one range, "1.43 (`tube`) to 1.99 (`line`), ±10–14 %". Either state a wave result or cut the wave from the prose and leave it to the panel. | yes |
| 5 | 314–322, passage test | Payload: *"Only two conditions trained on simulated recordings make narrow detections; every arm trained on real recordings and the untrained arm score by being on almost everywhere."* The sentence at 315–316 pairs two ranges with two more ranges using an implicit "respectively" ("0.499–0.577 and 0.503–0.559 … 0.954–0.985 and 0.962–0.984"). The subject of "23–128 s wide" is unclear. Line 317–318, "cover 0.005–0.010 and `count_excess` 0.004, at 0.662–0.696 and 0.648", has the same problem. | M | Give each arm its own clause ("trained on real: F1 0.499–0.577, detections covering a median 0.954–0.985 of the recording, each 23–128 s wide"), or use a four-row table: arm · F1 · median coverage · detection width (s). | yes |
| 6 | 104–106 | The sentence opens with a numeral and uses the same implicit "respectively": "0.799–0.830 and 0.903 of their events… and 0.046–0.070 and 0.073 on the rigid shift". | M | "Supervised models put 0.799–0.830 of their events on onsets in at least three ROIs (0.046–0.070 on the rigid shift); `count_excess` 0.903 (0.073)…" | yes |
| 7 | 107, 421 | "hold three ROIs" where the measure (table header at 397, caption at 386) is **at least** three. | M | "hold onsets in at least three ROIs". | yes |
| 8 | 517 | "hold 0.804–0.814 multi-ROI co-activity": a share with no noun. | M | "0.804–0.814 of their events hold onsets in at least three ROIs". | yes |
| 9 | 300, 404; 74, 280, 667 | **`count_share` is never defined.** `slow_modulation` first appears in a table at 303 and is described only at 348 and 422. It is also not a count, yet "three count baselines" (280, 667) includes it. | M | At line 74, or where `count_excess` is defined (291), give one clause for each of the three baselines. Call the group "zero-parameter baselines". | yes |
| 10 | 13–15 against 48 | **ROI is used at line 13 and defined only at line 48**, in Terms. "Crop" is used at 60–61 and 97 but defined only at 285 (4,096 frames, 409.6 s). "Head" (173, 270), "fold" (89), "SD" (231) and "SCE" (used at 245, expanded at 254) are also undefined at first use. INMED, EPFL, RRID and CICADA are never expanded. | M | Expand ROI at line 13. Add "crop" and "head" to Terms. Expand SCE in the table row. Expand or drop INMED, EPFL and RRID. | yes |
| 11 | 480–482 | "**bench**" is used nowhere else and is undefined. So is "dense probe stretch", while 231 and 249 call it the "promiscuity probe". | M | Say "bake-off" and "promiscuity-probe stretch". | yes |
| 12 | 99, 164, 349, 359, 369 | **One twin has at least four names**: "events-only twin", "planted-event twin", "synthetic twin with planted events and no modulation", "events twin" (the table column adds "events, no modulation"). The shared-modulation twin is also "modulation twin" (100) and "synthetic twin with shared slow modulation and no events" (86). | M | Pick one name per twin in Terms and use only that. If the aggregate-leak twins (174) and the twin check's twins (370) come from different generators, say so. | yes (naming; not whether the twins are the same) |
| 13 | 185–190, passage test | Payload (first sentence): *"The cells-mean trace alone does almost all of it."* The fourth sentence, "this test excludes a leak the shared offset would also carry and says nothing about whether the co-activity is coordination", does not parse on first reading: what does the shared offset carry? The last sentence (destruction was measured earlier) is a separate point. | M | "So this test rules out any leak that would also show under a shared offset; it cannot say whether the co-activity is coordination." Move the earlier look's destruction figure to its own sentence or to *What this does not settle*. | yes |
| 14 | 182–183 | "present at a shift of 1.6 s, where 40 s co-modulation is not": the ellipsis reads as "40 s co-modulation is not present". | L | "…present at a 1.6 s shift, which leaves 40 s co-modulation intact." | yes |
| 15 | 97 | Garden-path headline: "What training taught shows on synthetic twins" parses as "training taught shows". | L | "**Synthetic twins, not real crops, show what training taught:** …" | yes |
| 16 | 169–177, passage test | A legend, and mostly earned. One clause is a darling: the stationary twin "cannot fail and is kept only for continuity". A reader of this page gets nothing from continuity with a superseded version. The same row appears again at 332 ("cannot fail"). | L | Cut the stationary-twin rows from both tables, or keep them with a reason that serves this page. | yes |
| 17 | 111–118 and 661–663 | The history of the previous version is told twice. Line 111 dates it "the version of 2026-09-16"; line 661 calls it "the version reviewed on 2026-09-17". That is two dates for one object, and "third blind review" is an ordinal label. | M | Keep the history in one place: *What changed*. Cut the callout to "Exploratory. Nothing here is promoted… every quoted result is a key in `summary.json`… ⚠ marks a claim not to lean on." Give one date and name the review rather than numbering it. | yes |
| 18 | 204, 345 | Positional labels, against CLAUDE.md's rule on enumerated labels: "**the third fold**" and "**the last two rows**". | L | 204: "Without that fold". 345: "the 1.6 s shift and shared-modulation twin rows". | yes |
| 19 | 426, 507, 509, 522, 523, 531, 578 | Figure references that carry the number but not the name ("Figure 4", "Figure 5, panels C and D", "Other labs' detectors in Figure 3"). CLAUDE.md requires both. | L | "Figure 4, training without labels", and so on. Lines 84, 91, 96, 108 and 477 already do this. | yes |
| 20 | 305–312 | Redundancy: "In the `line` conditions … (all of them `line`, 2–4 per condition)". Also "8, 9 and 10 … at the three rates" uses the implicit "respectively" again. | L | "…fell to its grid's lowest value in 8, 9 and 10 fit-and-recording settings at ≤ 0.5, ≤ 1 and ≤ 2 (2–4 per `line` condition)". | yes |
| 21 | 369 | Fragment with no subject: "Above chance on the events twin in 11–12 of 12 fits per condition." | L | "Each trained condition is above chance on the events twin in 11–12 of its 12 fits." | yes |
| 22 | 374–378 | Two unrelated points in one block (training loss; ties on the same-crop control). "so ties are not what holds **it** at 0.5": "it" is unclear. | L | Move the ties sentence under the paired-checks table and name the check: "…holds the same-crop check at 0.5". | yes |
| 23 | 443 | Fragment: "at their bake-off thresholds 1.6–2.2 %." | L | "…and 1.6–2.2 % at their bake-off thresholds." | yes |
| 24 | 435 | "agree with each other at 0.780 (CoactDetect's events near LoCo's) and 0.591": the direction of the second number is left to inference. | L | "…and 0.591 (LoCo's events near CoactDetect's)". | yes |
| 25 | 539–550, passage test | Payload: *"Whole-train shifting is established (Pipa et al. 2008; recommended by Louis et al. 2010 and Stella et al. 2022), and every published form wraps the ends where this run drops onsets."* The part that matters for this page (drop versus wrap) is the last sentence. The ⚠ about the unread 2007 paper and the Grün 1999 abstract is thoroughness, not evidence a sceptic of this run would ask for. The Stella 25 ms dither and Louis's rolling also repeat *What this does not settle* (467–475). | M | Promote the drop-versus-wrap sentence to second place. Move the unread-origin ⚠ to a one-line note or cut it. Cite rather than restate the not-settle bullets. | yes (the prose; not the citations) |
| 26 | 468, 544 | "robust" is a banned-list hit, used twice for the same Stella et al. finding. | L | State what they measured, or state that "robust" is the paper's own term and keep it with that reason. Either way, say it once. | yes (the hit; not the paper) |
| 27 | 18 | "not only" is a near-form of the banned *not just X, but Y*. Here it carries a real claim. | L | "A detector trained against a surrogate learns everything the surrogate moves, including what it was not meant to move." | yes |
| 28 | 537, 574–576 | The lineage section previews its conclusion and then restates it. "The transfer is ours, not the ideas" is a rhetorical closing line. | L | Cut line 537. Keep 574–575 and drop the closing antithesis, or keep that line and cut 537. | yes |
| 29 | 11, 24, 503, 109 | Throat-clearing: "A label-free detector would need no annotation" (a tautology) · "The architecture question sits beside those two." · "In the order the argument raised them." · the findings bullet pointing to the decisions. | L | Cut all four. Line 11 can open "What a label-free detector needs instead…". | yes |
| 30 | 37–44 | A question list that previews the page, which the house voice rules out. It does map questions to figures. | L | Keep only if the author says it stays as the reader's map. Otherwise let the section headings do the job. (Section order belongs to role 11.) | yes |
| 31 | 222–229 | The parenthesis on the code name "orientation channels" (17 words) buys nothing for a reader of the results. | L | Move it to Provenance, or cut it. | yes |
| 32 | 578–584 | One sentence runs about 45 words with seven stacked commas ("`locust` is a partial, modified port, by way of interface2, of CICADA, from…"). "Partial, modified port" also appears at 246, 255 and 581. | L | Split into two sentences, one for the port and one for CICADA's provenance, and say "partial port" once. | yes |
| 33 | 634–641 | Last sentence: "…carried over unchanged from the previous run at `b85b5c9`, **which** the models it reads … make comparable here because their training did not change." "Which" has no clear antecedent. | L | "The probe is carried over from the previous run (`b85b5c9`). It is still valid here because the models it reads, the supervised fits and the seed-0, fold-0 checkpoints, were trained the same way in both runs." | yes |
| 34 | 661–676, passage test | Payload: *"This version adds controls that can fail: a 1.6 s shift, modulation twins, a circular-shift positive control, zero-parameter baselines, and the models scored on twins."* The bullet on reordering the page ("problem first, with terms before results, claims before tables") and the citation-correction list are process history. They serve a reviewer, not a reader. | L | Keep the first bullet. Move the rest to the review record. | yes |
| 35 | 67–68, 414, 529 | The rate cap "holds on the shifts, not on the recording" is stated three times (Terms, results, decisions). 89, 203, 465 and 511 likewise repeat "no learned model separates from CoactDetect". The bullet at 465–466 in *What this does not settle* is a settled finding. | L | Cut the 465–466 bullet, since the decision already sits under *What waits on Tony*. Keep the rate-cap statement in Terms and in the decision, and make the results bullet start from the numbers. | yes |
| 36 | 200, 325 | British spelling ("grey", "labelled") against `docs/writing_conventions.md`. | L | "gray", "labeled". Check whether "grey" is also in the Figure 3 generator's label. | yes |
| 37 | 280 | "(24 rows)": rows of what? | L | "(24 runs: 3 baselines × 2 *J* × 4 folds)". | yes |

The biggest problem is that the "Nothing here is ground truth" paragraph appears twice, at lines 450–454 and 456–461. Beyond that, three long blocks put their main point last or leave it unstated: the per-ROI test's power (146–155), the plant probe (260–272) and the whole-train shifting history (539–550). In the coverage block (314–322), the point is clear but pairs of ranges matched by an unstated "respectively" bury the numbers. Singular "data" had no violations, and no em-dash pivots turned up.
