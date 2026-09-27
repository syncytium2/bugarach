GRANT 5 ok — Read, Grep, Glob

**Role 5 (Kill Your Darlings), BLIND pass: 16 findings, none high. The worst is a modifier on the wrong name in three places: "(the runner-up…)" labels the reference, not the runner-up (P1). No banned constructions found. I did not open anything under docs/reviews/briefing_2026-09-26-roles/.**

Artifact: <darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html (646 lines). Generator: <worktree briefing-page>/tools/make_briefing.py. The fixes point at the generator, because the page is rebuilt from it.

**How the search was run.** `murderboard_prose.sh` does not exist in this repo, and I hold no shell, so I could not run it. I did the construction search with Grep on the built HTML, and I counted words and sentences per block by hand from the text I read. Those counts are estimates, not tool output.
- **List used:** the process file's house list: *not just X but Y*, *it's not about A, it's about B*, *it's worth noting*, delve, leverage, robust, seamless, crucial, landscape, tapestry, three-item rhythm lists, em-dash pivot into an uplifting close, and *"In today's ___"*.
- **House checks added:** "data" used as singular, "fire" for calcium events, and British spellings (the worktree's writing_conventions.md has an American English section).
- **Reading scope:** I read the prose in full: the byline, every box, paragraph and caption, Tables 1–6 and Terms. For the SVG I read Figure 1a in full and only the header, legend and caption lines of 1b and 1c.

### Construction search (Grep on the built page)
| line | construction | kind |
|---|---|---|
| — | not just / not only / it's not about / worth noting / In today's | 0 hits |
| — | delve, leverage, robust, seamless, crucial, landscape, tapestry | 0 hits |
| — | em-dash (" — ") anywhere in the prose | 0 hits, so no em-dash pivots |
| — | "data is/was/has/shows", "this data" | 0 hits |
| — | fire / fires / fired / firing | 0 hits |
| 61, 303, 359, 447, 538, 566, 568–570, 576 | "SPIKE" | Only inside the detector's proper name SPIKE-synch. Not a defect. |
| 47 | "favour" | British spelling |
| 233 | "grey" | British spelling |
| 566 | "centre" ×2, "standardised" | British spelling. writing_conventions.md names "centre−surround" as the known drift case. |
| — | three-item rhythm lists | None. Every triple (the three budgets, fast/slow/combined) has three real items. |

### Blocks (my counts: words · sentences)
| block | line | words | sentences |
|---|---|---|---|
| Byline | 44 | ~55 | 4 |
| Headline box ("What the new bench against the old bench shows") | 47 | ~205 | 8 |
| Figure 1a caption | 233 | ~60 | 5 |
| Table 1 caption | 564 | ~60 | 4 |
| "How to read it" box | 565 | ~470 | ~19 |
| "What is compared" box | 566 | ~190 | 13 |
| Viewer setup box | 573 | ~150 | 5 |
| Leader-rule paragraph | 574 | ~190 | 9 |
| "Passed over" list (fast stream) | 576 | ~110 | 1 |
| "Lanes in every figure below" line (×3) | 577, 583, 589 | ~30 each | 1 |
| Captions of Figures 2–9 | 579–593 | ~55–65 each | 2–3 |
| Section 3 lead-in lines | 595–596 | ~15 + ~35 | 1 + 2 |
| Terms | 598–645 | ~330 | ~25 |

### Passage test: the one sentence each block exists to deliver, and what the rest buys
- **Byline.** Payload: "The night's results, scored on seeds nobody tuned on; nothing is adopted." Every sentence is needed. Pass.
- **Headline box.** Payload, never written down: *on the new bench most rows beat CoactDetect's shipped setting; on the old bench almost none do.* That is 13, 16 and 12 rows against 4, 0 and 1.
  - What the rest buys: 18 numbers in three identical two-sentence templates. Table 1, directly below, repeats all of them.
  - The sentence a skeptic most needs comes last: proposals and picks were chosen on the new bench, so its numbers favour them.
  - Fix: promote the verdict, then the caveat, and leave the figures to Table 1. **Medium** (H1).
- **Figure 1a caption.** Payload: how to read the marks. Every word is needed. Pass (one spelling issue, S1).
- **Table 1 caption.** The opening words "At a glance." are throat-clearing. The rest is needed. **Low** (T1).
- **"How to read it" box.** This is really eight blocks:
  - (1) Paired ΔF1 and its interval's limits. Evidence a skeptic demands. Keep.
  - (2) "Rows within 0.01 F1 are level." Keep, but the lead sentence is opaque (A2).
  - (3) Two benches. Payload, placed last: *the old bench is scored because Tony asked, and it decides nothing.* The sentence about settings predating the new bench repeats the headline's last sentence and the Terms entries for both benches. Promote the payload and cut the repeat. **Low.**
  - (4) Decoys. Payload, placed last: *on slow, most of the spread between rows is how each row handles decoys.* That is a result, not reading advice, and it is buried in bullet 4. Promote it to the headline box. **Medium** (P2).
  - (5) Budgets. The closing sentence reconciles the page with "the worker's README", a file the reader does not have and the page does not link. It is there for the author's satisfaction. Cut it or move it into the details. **Medium** (C1).
  - (6–7) Seed counts and paths. Keep (see G3).
  - (8) The ORX-spacing check. Payload, placed last: *none of the 51 intervals flips sign under ORX-like spacing.* The sentence that follows, "It is not shown here.", adds nothing. Promote the payload and define "change side". **Medium** (A3).
- **"What is compared" box.** Payload: one line per detector. Four entries print their own name twice, and the count entries print a second label (R1). **Medium.**
- **Viewer setup box.** Payload: two clicks the first time, one after that. It earns its length. The last-but-one sentence is tangled (G4). **Low.**
- **Leader-rule paragraph.** Payload: *the leader is the top clean row that ran on real recordings; each figure shows the median call of one agreement kind against CoactDetect's proposal.* Its sentence 4 has a pronoun with the wrong antecedent and carries three facts (A1). **Medium.**
- **"Passed over" list.** Evidence the reader needs. Keep. It uses "reference" in a second sense (A4).
- **"Lanes" lines.** The modifier sits on the wrong name (P1). **High-visibility.**
- **Figure 2–9 captions.** The template earns its length. There are small defects (G5).
- **Terms.** Tight. Three terms the page uses are missing (D1).

### Findings
| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| P1 | lines 577, 583, 589; make_briefing.py 1121–1124 | "(the runner-up, the next row meeting the rule)" is appended after the whole lane list. It therefore sits on the last item, CoactDetect · proposal, which is the reference and not the runner-up. The runner-up is the middle lane. A reader who takes the page literally reads the reference as the runner-up. | Medium-high (misleads) | Attach the parenthetical to the runner-up entry (`ex["lanes"][1]`), not to the joined string. | yes (generator read) |
| H1 | line 47; `headline()`, lines 946–967 | The box is titled "What … shows" but never states what it shows. It is a numeric dump that duplicates Table 1. The caveat about the benches is placed last. | Medium | Open with a one-sentence verdict for each stream and the caveat. Leave the 18 numbers to Table 1, or give each stream a single clause. | yes |
| A5 | line 47 | "13 of 22 rows sit above CoactDetect's shipped setting" means *95% interval wholly above zero* (Table 1's column), but reads as point estimate above zero. On the fast new bench, 15 point estimates are positive, so the plain reading gives the wrong number. The figure header also says "23 rows", which includes the reference, while the headline says 22, which does not, and neither says so. | Medium | Write "13 of the 22 other rows have a 95% interval wholly above zero". | yes (Tables 1–2) |
| D2 | line 47 | "unflagged" is used before it is defined. The definition sits in the Table 1 caption, below. | Low | Write "(3 within every budget and off a search limit)", or define the word at first use. | yes |
| P2 | line 565, decoy bullet | A result ("on slow, the spread is mostly how each row handles decoys") is buried at the end of a reading-instructions bullet. | Medium | Promote it to the headline box. | yes |
| C1 | line 565, Budgets bullet; lines 1068–1070 | "The worker's README counts only … which is why it names one row where this page marks more." This refers to a file the page neither links nor needs. | Medium | Cut it, or move it into the details element with a link. | yes |
| A2 | line 565; lines 1052–1053 | "The order is a reading of intervals, not a ranking" is opaque, and the rows are in fact sorted by point ΔF1. | Medium | "Rows are sorted by ΔF1. Rows within 0.01 F1 of each other (one noise unit, ADR-0010) are level." | yes |
| A3 | line 565, ORX bullet; lines 1039–1043 | "Change side" is undefined: side of what? The payload (no interval crosses zero) comes after it, and "It is not shown here." is dead weight. The check is also named by index only ("ADR-0010 ruling 1's check"). | Medium | "Rows re-scored on ORX-like spacing: no interval crosses zero; 4 of 51 move between 'above zero' and 'includes zero'." Name the check before citing the ruling. | yes |
| A1 | line 574; lines 1097–1099 | "It is set against CoactDetect…" follows "Every row passed over is named with its reason", so "It" binds to the passed-over rows. The sentence also carries three facts. | Medium | "The leader is compared with CoactDetect at the setting the night's detection used, its proposal. That is not the leaderboard's reference, and it is itself on a search limit." Split into two sentences. | yes |
| A4 | line 576 vs 574 | "reference" has two senses on the page. Line 574 says the proposal "is not the leaderboard's reference". Line 576 then passes over "CoactDetect · proposal (CoactDetect is the reference)". | Medium | Line 576: "(it is the comparison side)". Keep "reference" for the shipped setting only. | yes |
| R1 | line 566; WHAT dict, make_briefing.py lines 99–106 | "SPIKE-synch: SPIKE-synch: …", "rate+context: rate+context: …", "binned SCE: binned SCE: …", "locust: locust: …". The count entries repeat a second label ("the simple rule, sliding: …"). The dict values carry a label that `render()` already prepends. | Medium | Strip the leading "name:" from those WHAT values. | yes (generator read) |
| G1 | Tables 3–4 marks, e.g. slow rows 3, 12, 14, 19; `_marks_html()` line 857 | "Over budget on the both benches" is ungrammatical, and it repeats wherever both benches fail alike. | Medium (repeated, visible) | Pass "both benches" without "the", or template it as `on {col}` with `col` = "the new bench" / "both benches". | yes |
| N1 | lines 565, 566, and the marks throughout Tables 2–4 | Name, don't index (house rule). The page uses "ADR-0010 ruling 1/2/5/7" and "ADR-0010 part 1/3/5" side by side. A reader cannot tell whether "part 5" and "ruling 5" are the same numbering. | Medium | Name each rule once ("the switched-off-value rule", "the bracketing rule", "the merged-calls rule") and put the ADR number in parentheses. Use one word, "ruling" or "part". | yes (text read; ADR not opened) |
| A6 | Tables 2–4 and Figure 1 row labels | "training run 0 of 5" and "training run 4 of 5" are zero-indexed but read as ordinals. "4 of 5" reads as the fourth run, and "0 of 5" reads as none. | Medium | Number the runs from one ("run 1 of 5"), or write "run #0 (runs 0–4)". | yes |
| S1 | lines 47, 233, 566; generator lines 107, 111, 112, 966, 1018 | British spellings (favour, grey, centre-surround ×2, standardised) break the house American English rule. writing_conventions.md cites centre-surround as its own example. | Low | favor, gray, center-surround, standardized. | yes |
| G2 | Tables 2–4 marks; line 171 | "Synchronous-frame run 1 frames" is plural after 1. "at the 99.9922th percentile" has an odd ordinal. The slow tube row shows a degenerate range, "held-out F1 of the 5 runs: 0.82–0.82". | Low | Use `n_of` for the frames unit. Write "threshold at percentile 99.9922". When min equals max, write "0.82 (all 5 runs)". | yes |
| G3 | line 565, seed bullets | "the count (binned), count (sliding) rows" is missing "and". The worker-directory paths (064/…, 065/…) are lookup keys shown as content. | Low | Add "and". Leave the paths in, but put them after the meaning. | yes |
| G4 | line 573 | "a link needs one click on Reopen and the browser's permission prompt, and you pick the results file again each visit." One verb is carried over two unlike objects (a click and a prompt), and the grammatical subject switches halfway. | Low | "After that, a link needs one click on Reopen and a yes to the browser's permission prompt; you re-pick the results file each visit." | yes |
| G5 | Figure 2–9 captions; lines 1156–1161 | "one of 1 call of its kind (1 away from window edges)". The counts in parentheses ("80 away…") carry no unit, against the house rule that every number carries its unit. | Low | When the pool is 1, write "the only call of its kind". Write "(80 calls away from window edges)". | yes |
| D1 | Terms | Missing terms: "leader", "unflagged", "noise unit". The abbreviations SCE and CICADA are never defined (house rule: define every abbreviation). | Low | Add the three terms and expand the two abbreviations. | yes |
| T1 | line 564 | "At a glance." is a throat-clearing label inside the caption. | Low | Cut it. | yes |

### Checked and clean
- **Voice:** there is no throat-clearing opener and no recap close. The page ends on Terms.
- **Conventions:** the stream axis is named correctly throughout. "data" does not appear, and "fire" does not appear. The group order is DI, OVX, MALE, ORX in every table, caption and list.
- **Figures:** Figures 1a–1c and 2–9 are numbered, and every cross-reference carries the number and the name.

### Out of my lane, noted once
The fast new bench used 48 seeds and the old bench 24 (line 565). The leader rule excludes rows on a search limit, yet the comparison side is itself on one (line 574). Both are stated plainly on the page; whether they hold up is for roles 4 and 11.

Per the hard constraints, no recording ids or individual call values are quoted in this report.
