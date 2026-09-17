GRANT 5 ok — Read, Grep, Glob

# Line edit of `docs/learned/slow_comodulation/README.md` (branch unsup/slow-comodulation, commit ab736cd)

## Search record

`murderboard_prose.sh` isn't vendored here and I have no shell, so I ran the searches by hand with Grep. I used the banned-construction list from role 5 in `doc_review_process.md`, plus the house rules in `CLAUDE.md` and `docs/writing_conventions.md`.

| search | pattern | hits |
|---|---|---|
| *not just / not only* | `not just\|not only` | 0 |
| *it's not about A, it's about B* | `it's not about\|it is not about` | 0 |
| *it's worth noting* | `worth noting` | 0 |
| banned words | `delve\|leverag\|robust\|seamless\|crucial\|landscape\|tapestry` | 0 |
| *In today's ___* opener | `in today's` | 0 |
| em-dash pivot into an uplifting close | every `—` line read by hand (lines 5, 20–21, 36–37, 47–48, 159–161, 198, 283–284, 292, 337–338, 340–341) | 0. All are parentheticals or appositives, and none closes on a flourish. |
| three-item list built for rhythm | read by hand (lines 50–52, 198–208, 292–294) | 0. Each list really has three things in it. |
| "data" singular | `\bdata\b` | 1 hit (line 370, "data DANDI:000219"). It's a noun label with no verb, so it's clean. |
| British spelling | `-is(e/ed/ing/ation)`, `centre`, `round the`, `analys(e/ed)` | 8 defects: lines 87, 97, 123, 131, 337, 338, 365, 382 |
| bare enumerated labels | `item\|step\|panel … [A-H0-9]` and bare `Figure N` in prose | line 6, lines 181 and 272, plus the bare figure references below |
| throat-clearing, previews, recaps | `this page\|the rest of the page\|below\|above\|in this order` | lines 8, 55–57, 107 |
| terminology drift | `slow structure\|shared slow\|slow shared\|co-modulation\|shared change` | 13 lines, 7 names for one phenomenon |
| overloaded jargon | `\barms?\b\|paid for\|firing` | "arm" has 8 hits in two senses; "paid for" has 3 |

## Block table

Word counts are hand estimates (±10 %), not tool output. For each block: the sentence it exists to deliver, where that sentence sits, and what the other words buy.

| lines | block | words | sentences | payload | where | the other words buy |
|---|---|---|---|---|---|---|
| 3–9 | Why this page exists | ~95 | 3 | Rigid shift may or may not destroy slow shared rate change, and this page measures how much of that change there is. | start | A 30-word provenance parenthetical ("item 2 of…", "itself not yet re-reviewed") that a reader doesn't need to follow the point. The last sentence previews the page. |
| 11–13 | status | ~50 | 3 | Exploratory, one run, not a milestone. | start | It defines "measured" and "argued", which is needed. Line 13 overstates: many numbers from recordings carry no interval. |
| 19–25 | Figure 1 caption | ~95 | 6 | Variance of the population count ÷ its independent level, by bin width and surrogate. | start | Needed. |
| 29–38 | lab fast finding | ~150 | 5 | Shared count excess at a minute or more that isn't CoactDetect's events, and rigid shift leaves almost all of it (lines 34–36). | middle | The robustness checks (per-recording median, top-five dropped) are evidence a sceptic would want. |
| 39–42 | lab slow finding | ~70 | 3 | The slow stream's swings are mostly its events. | start | The ⚠ about concentration is needed. |
| 43–45 | Dard finding | ~45 | 2 | The largest swing, and it survives the block control. | start | Needed. |
| 46–48 | generator finding | ~45 | 1 | The generator carries more slow swing than the lab fast stream, and rigid shift leaves it. | start | Needed. |
| 50–57 | decision plus preview | ~110 | 3 | On lab fast, most slow structure sits at a minute or longer, beyond what rigid shift touches. | middle | The question repeats lines 288–289 almost word for word. Lines 55–57 are a preview of the page's order. |
| 61–65 | definitions | ~70 | 4 | ROI, onset, stream, lit. | — | Needed, but it arrives after ROI, *J*, CoactDetect and "drift" were already used (lines 19–48). |
| 69–79 | two kinds; surrogate | ~155 | 8 | What rigid shift does to shared modulation decides whether the detector is rewarded for it (line 79). | end | The definitions leading up to it are needed. |
| 83–91 | correlogram | ~130 | 7 | Events make a narrow peak, and shared modulation makes a broad shoulder. | end | The method is needed. Promote the payload to the start. |
| 95–105 | Figure 2 caption | ~160 | 8 | Three synthetic worlds and their correlograms. | start | Needed. |
| 107–110 | two things easy to miss | ~60 | 3 | Shared modulation also makes sub-second excess, and the generator's background reads zero. | bolded | "Two things in Figure 2 are easy to miss." is throat-clearing. |
| 112–114 | ⚠ relative excess | ~45 | 2 | The method can't see a rate change that spans the whole window. | end | Needed here. Repeated at lines 302–303. |
| 120–132 | Figure 3 and Figure 4 captions | ~145 | 8 | What each surrogate does, and the trimming. | — | Needed. |
| 136–149 | synthetic findings | ~200 | 9 | Rigid shift removes only modulation shorter than *J*, and the block control keeps events too. | bullet heads | Needed. Lines 143–146 are restated at 181 and 315–316. |
| 153–155 | recordings summary | ~45 | 2 | Sub-second peak everywhere, and long-lag excess on lab fast and Dard. | start | This block is a model for the others. |
| 159–171 | Figure 5 caption | ~190 | 6 | The data sources and the CoactDetect removal. | — | It carries the page's only definition of CoactDetect, 140 lines after its first use. |
| 175–185 | lab fast correlogram | ~175 | 7 | The recorded curve stays above zero out to a minute and more, and that plus Figure 1's count variance is the evidence that can fail (lines 183–185). | end | The trough at 1–2.7 s and the bump near 3 s don't bear on the decision; they belong in the details block. Promote the last sentence. |
| 186–192 | lab slow correlogram | ~95 | 5 | A real-against-shifted contrast on the slow stream rewards what follows an event as well as the event (lines 189–191). | middle | Number pairs that aren't mapped to lags. |
| 193–196 | Dard correlogram | ~55 | 3 | A small per-pair shoulder across 566 ROIs is the 9× count swing. | end | Fine. |
| 198–213 | three readings of the dip | ~230 | 12 | Splitting lagged pairs by membership would tell the readings apart, and it's a question for the producer. | end | The dead-time provenance ("measured by a review role…") and the Dard sentence at 212–213, which draws no inference. |
| 216–257 | details | tables plus ~110 | 5 | Numbers behind Figures 1 and 5. | — | Needed. |
| 262–284 | consequences for the label-free thread | ~300 | 12 | Rigid shift on real fast recordings contrasted mostly the event peak, and at most a small part of the minute-scale change. | first bullet | Lines 276–280 are provenance (shas, branch, results path) and could be a footnote. |
| 288–298 | the decision | ~140 | 6 | Nobody knows where the drift comes from, and nobody has asked. | end (⚠) | The question in lines 288–289 duplicates line 50. "that is what makes the choice real" is decoration. |
| 302–328 | what this does not settle | ~330 | 17 | Caveats. | — | 4 of 11 bullets repeat earlier text: 302–303 repeats 112–114, 309–312 repeats 36–38, 315–316 repeats 143–146, 317 points back to the excess caveat. |
| 334–346 | by group | ~170 | 8 | The pooled result isn't one group's, and there's no group difference to show (lines 345–346). | end | Promote it. |
| 350–372 | published lineage | ~260 | 13 | Prior art. | — | Line 350 is a flourish. "The ranking in Stella et al. 2022" has no referent. |
| 376–388 | reproduce | ~160 | 6 | How to rerun. | — | Needed. |

## Findings

| # | location (line) | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | 19–48 vs 61, 78, 166–170 | Abbreviations, symbols and jargon are used before they're defined. ROI is used at line 19 and defined at 61. *J* is used at 22 and defined at 78. CoactDetect is used at 23 and defined only inside the Figure 5 caption at 166. "Drift" is used at 36 and defined at 71–72. The lead findings can't be read cold, and "(each defined below)" doesn't fix that. | medium | Add one short glossary line before Figure 1 covering ROI, *J*, block control, CoactDetect episode and drift. Or expand each at first use and move CoactDetect's definition into "Two ways ROIs are active together". | yes |
| 2 | 169–170 | The symbol α is never defined. | medium | "α = 10⁻⁴, the false-alarm probability per bin the test allows" (or whatever α actually is in `coact_detect`). | yes |
| 3 | 6 | Bare enumerated label: "item 2 of *What waits on Tony*". | medium | Name the item: "the question of whether shared modulation should count, in *What waits on Tony*…". | yes |
| 4 | 181, 272 | "Figure 4, panel A" and "Figure 4, panel D" give a number with no name. | low | "Figure 4's planted-event world" and "Figure 4's full benchmark generator". | yes |
| 5 | 27, 134, 173, 196, 327, 345 | Prose references to figures give the number without the name. The house rule wants both. | low | For example "Figure 1, the count swing", "Figure 5, the recordings", "Figure 6, the group split". | yes |
| 6 | 87, 97, 123, 131, 337, 338, 365 | British spelling: normalised, centred, "wraps it round", analysed, orchidectomised, ovariectomised, randomising. | medium | normalized, centered, "wraps it around", analyzed, orchidectomized, ovariectomized, randomizing. | yes |
| 7 | 382 | `--resummarise` is a British-spelled command-line flag. The prose can't fix it without the tool changing too. | low | Rename the flag to `--resummarize` in `tools/measure_slow_comodulation.py` and here together, or record it as known drift. | yes (prose only; I didn't open the tool) |
| 8 | 1, 8, 34, 46, 53, 143, 264, 272, 298, 309 | Terminology drift: seven names for one phenomenon. They are "co-modulation" (title only), "shared modulation", "drift", "slow structure", "shared slow structure", "slow shared swing" and "shared change in onset count". The reader can't tell whether these are distinctions or synonyms. | medium | Keep "shared modulation" for the phenomenon, "drift" for the version slower than a minute (as defined), and "count swing" for the Figure 1 measure. Replace the others and retitle to match. | yes |
| 9 | 130, 180, 220, 239, 316, 318, 387 vs 272 | "Arm" is never defined, and it carries two meanings. Everywhere else it means one analysis variant (recorded or a surrogate). At line 272, "neither arm's contrast" means the two training regimes (real recordings and simulated ones). | medium | Define "arm" at line 130 ("each arm, recorded or one surrogate"). At line 272 write "so neither the real-trained nor the simulated-trained models' contrast contained…". | yes |
| 10 | 29, 39, 43 | Imprecise: "the population count swings about 2× chance". The measure is a variance ratio, so 2× the variance is about 1.4× the swing. "Swings" asserts amplitude. | medium | "the population count's variance is about 2× its independent level", or define "swing" once as the variance ratio in the Figure 1 caption and keep it. | yes |
| 11 | 50–57 and 286–289 | The decision question appears twice, nearly word for word. Lines 55–57 preview the page's order, which the house voice bans. | medium | Keep the question in one place (the closing section is where the provenance and ⚠ live). At line 50, keep only the sharpening sentence (lines 52–55). Cut lines 55–57. | yes |
| 12 | 8–9 | The last sentence previews the page. | low | Cut "This page shows what that slow structure is and how much of it the recordings hold." | yes |
| 13 | 107 | Throat-clearing: "Two things in Figure 2 are easy to miss." | low | Cut it and let the two bolded claims stand. | yes |
| 14 | 302–303, 309–312, 315–317 | Redundancy: four caveat bullets restate text at lines 112–114, 36–38 and 143–146. | medium | Replace them with one bullet that points back ("the relative-excess and block-control caveats above apply to every lab claim"), or cut the earlier copies. Keep one of each. | yes |
| 15 | 175–185 | Passage test: the payload ("the evidence that can fail…") is last, behind the trough and bump details, which don't bear on the decision. | medium | Open the bullet with the long-lag result and the evidence that can fail. Move the 1–2.7 s trough and 3 s bump to the details block. | yes |
| 16 | 183–185 | Broken coordination: "The evidence that can fail is that the recorded curve stays above zero …, which events … cannot produce, and the count variance of Figure 1 after events are removed." A that-clause is joined to a bare noun phrase. | medium | "Two checks can fail: the recorded curve stays above zero at lags of a minute and more, which events at a steady rate cannot produce; and Figure 1's count variance stays above 1 after events are removed." | yes |
| 17 | 186–191 | Ambiguous numbers: "(−0.56 and −0.51)", "(+0.03, +0.08)", "(−0.39, −0.31)" and "+0.35 to +0.57 at *J* of 10 and 20 s". Nothing says which value goes with which lag bin or which *J*. | medium | Label each value, for example "−0.56 at 2.7–4 s, −0.51 at 4–5.4 s" (use the real bin edges) and "+0.35 at *J* = 10 s, +0.57 at *J* = 20 s" (if that's the mapping). | yes (ambiguity); no (true mapping, which is in `summary.json`, not opened) |
| 18 | 194–195, 45 | "A shoulder of about +0.01 per pair": the excess is already a ratio pooled over pairs, so "per pair" misstates its unit. "The 9× count swing" is also ambiguous next to "about 15×" at line 44. | low | "a shoulder of about +0.01 excess…" and "the 9× swing that survives the block control (Figure 1)". | yes |
| 19 | 206–212 | Logic gap in the passage. The proposed split (members versus everyone) separates dead time from a network quiet interval. It doesn't separate either one from the third reading, "detection suppressed after a large transient", which is also members-only. So "would [tell them apart]" claims three-way separation for a two-way test. | medium | "Splitting … would separate the two extraction readings from a network quiet interval: both remove pairs only from members; a quiet interval removes them from everyone." | yes |
| 20 | 206 | Misplaced modifier: "A quiet interval after an event in the tissue" reads as an event in the tissue. | low | "A quiet interval in the tissue itself after an event". | yes |
| 21 | 212–213 | The sentence states a fact and draws no inference: the Dard dip at the same lags, under a different extractor. | low | State what it weighs against ("which weighs against a reading specific to this extractor") or cut it. | yes |
| 22 | 201–203 | Process provenance ("measured by a review role and not reproduced") inside a scientific reading. | low | Move it to a parenthetical citation: "(2.80 s; unreproduced, see the goal page)". | yes |
| 23 | 275–277 | The antecedent of "measured it" is unclear. "A 10 s scorer" is undefined. 0.669 and 0.522 are bare numbers with no metric named. | medium | "…measured the mixing on synthetic recordings: a scorer over 10 s windows separates an events-only recording from its 1.6 s shift at AUC 0.669…" (name the real metric). | yes (missing metric); no (which metric; `results.json` not opened) |
| 24 | 276–280 | Two shas, a branch and a results path inside a consequences bullet push the bullet's caveat (sinusoidal modulation) to the end. | low | Keep the payload and the sinusoidal caveat in the bullet. Move the paths and shas to a trailing parenthetical or the Reproduce section. | yes |
| 25 | 281–284 | Vague: "whether that explains its scores there". | low | "Whether that is why `count_excess` scored as it did on the simulated folds is not tested here." | yes |
| 26 | 291 | Decoration: "and that is what makes the choice real". | low | Cut it. | yes |
| 27 | 296–297, 328 | "FOUNDATIONS §9" and "§15" are bare section indices. | low | Add the name, for example "FOUNDATIONS §9 (baseline and group rules)". Use each section's actual title. | yes (the labels are bare); no (section titles not opened) |
| 28 | 307 | Missing comma makes a garden path: "weighted as the pooled curves weight recordings they cover 1.3 %". | low | "…weight recordings, they cover 1.3 %…". | yes |
| 29 | 340–342 | Overstatement: "dominated by one mouse each" and "close to one animal's", when the heaviest mouse carries 37–48 %, which is under half. | low | "one mouse carries 37–48 % of each group's fast onset pairs, so a group curve leans heavily on one animal". | yes |
| 30 | 343–344 | Elliptical: "and so does every group's on the slow stream except MALE's equal-weight curve". It's unclear whether this means pooled curves or equal-weight curves. | low | "…and on the slow stream every group's pooled and equal-weight curves do too, except MALE's equal-weight curve". | yes |
| 31 | 345–346 | Passage test: the payload (the pooled result isn't one group's, and no group difference is shown) comes last. | low | Open the group section with it. | yes |
| 32 | 136 | Stumble: "end up up to 2*J* apart". | low | "can land as much as 2*J* apart". | yes |
| 33 | 3–4, 79, 190 | The "paid for" metaphor can read as "costs". | low | "rewarded for". | yes |
| 34 | 13 | Imprecise: "Numbers from recordings carry a 95 % interval". Per-recording medians, the removal shares (61 %, 6.8 %) and the concentration figures carry none. | low | "Pooled numbers from recordings carry…". | yes |
| 35 | 362–364 | "The ranking in Stella et al. 2022" has no referent (ranking of what?), and no full reference appears in the lineage. | low | Say what was ranked, and add the citation. Checking the citation itself is role 2's job. | yes |
| 36 | 63–64 | "Their peaks trail the half-rise by roughly 0.3 s and 2 s" needs "respectively". | low | Add "respectively". | yes |
| 37 | 350 | Flourish: "The phenomenon is old; what is new here is the measurement on these recordings." | low | Cut it, or keep it only if the author wants the positioning claim. | yes |
| 38 | 384–388 | Broken parallelism: "check the pair count against …; that a fixed lag lands…; that the block control…". | low | "check that the pair count matches a brute-force count out to 300 s of lag; that a fixed lag…". | yes |
| 39 | 241 | The paired-difference table's headers carry no unit. By the house rule, dimensionless still needs saying. | low | "as recorded − rigid shift *J* 20 s (ratio)". | yes |

**Not found:** no banned constructions (list above), no singular "data", no bare step or option labels beyond line 6, and no bare count without a unit. Every count I checked carries its noun (ROIs, recordings, mice, draws, onsets, workers).

**Boundaries I kept:** I didn't check the numbers against `summary.json`, which is role 4's job. Figure alt-text versus caption, axis labels and panel rendering belong to role 10. Section order belongs to role 11. The Stella, Pipa and Harrison citations belong to role 2.
