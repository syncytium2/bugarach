GRANT 5 ok — Read, Grep, Glob

**Tooling note (a finding about the run, not the artifact).** The checklist requires `murderboard_prose.sh <artifact>`, its output pasted. That script **is not vendored in this repo** — `Glob **/murderboard*` in the worktree returns only `tools/murderboard_agents.py`, `tools/murderboard_freshness.sh`, `tools/murderboard_revendor.py`, `tools/murderboard_roster.sh` — and my grant holds no Bash, so I could not run it in any case. I substituted: the banned-construction pass ran as a Grep over the built HTML (output pasted below, it is a real search, not a description), and the block counts were done **by hand** from the built page and are therefore approximate (±5 words). Treat the count column as indicative; the judgement columns are unaffected. Worth filing: vendor `murderboard_prose.sh` from syncytium2/murderboard, or role 5 runs half-blind on every bugarach review.

Artifact read: `<worktree>/docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.html` (132 lines, all prose blocks + all three figure captions + Table 1's caption). Generator read: `<worktree>/tools/build_net_merge_gap_page.py` (lines 330–410, 460–609) so every wording fix below names the code line. Cross-checked against `report.html` in the same folder for figure names and for SCE.

---

## 1. Banned-construction search — output, not summary

Grep, case-insensitive, over the built page, pattern:
`not just .{0,40}but |it's not about|it is not about|worth noting|delve|leverage|robust|seamless|crucial|landscape|tapestry|In today's`

```
line · construction · kind
(no matches)
```

Second pass, house grammar rules:
`\bdata\b (is|was|shows|has|does)|\bthis data\b|—[^<]{0,80}$`  → **no matches** (no singular "data", no em-dash pivot into a closing uplift).

Three-item-list-for-rhythm: checked by eye. The three-item lists present are enumerations of real things (`0, 1, 2, 3, 5, 8, 15, 30 s`; the three net-ahead folds; "simulated recordings, baseline periods, the fast stream") — no rhythm padding. **The list I ran is the one in `docs/doc_review_process.md` role 5, the bugarach house list.**

Clean on the mechanical pass. Every finding below is a judgement or a house-rule (units / abbreviations / figure naming) hit.

## 2. Block census — counted by hand

```
block                                  · words · sentences
dim header (line 34)                   ·  ~31  · 1
lede (line 38)                         · ~148  · 5
§1 ¶1 (line 41)                        ·  ~95  · 4
§1 ¶2 (line 47)                        ·  ~60  · 2
§2 bullet "Goal 1's move rule"         · ~105  · 4
§2 closing ¶ (line 79)                 ·  ~50  · 1
§3 ¶1 (line 84)                        · ~125  · 2
§3 ¶2 (line 85)                        · ~145  · 4
§4 ¶ (line 89)                         · ~150  · 3
§5 ¶ (line 93)                         · ~165  · 4
§6 ¶ (line 101)                        ·  ~55  · 3
Fig 1 caption                          · ~120  · 6
```
The tool cannot judge these and neither does the table. The judgement is in F9–F12 below: §3 ¶1, §3 ¶2, §4 and §5 are the four blocks longer than their point, and in three of them the payload sits at the end.

---

## 3. Findings

**F1 · lede, line 38 · "the better chorus net" is two different nets · BLOCKING · verifiable: yes**
> "Counting every refit, the better chorus net ends +0.004 F1 from CoactDetect in this run's draw and ends −0.019 F1 from CoactDetect in the replicate's draw"

One noun phrase, two referents. Table 1 on this same page shows the better net on F1 alone is `chorus_norm` in this run's draw (+0.004) and `chorus_gain_norm` in the replicate's draw (−0.019) — `lede()` takes `lead_u[k]` per draw (build line 482). A reader takes "the better chorus net" as one net tracked across draws and concludes it swung 0.023 F1 between draws; in fact no single net did that. This is the page's headline sentence.
Fix (build line 481–484): name each. *"Counting every refit, `chorus_norm` ends 0.004 F1 ahead of CoactDetect in this run's draw and `chorus_gain_norm` ends 0.019 F1 behind it in the replicate's draw — the leader is a different net in each draw."* Also drop "ends X F1 **from** CoactDetect": with a signed number, "from" hides the direction the sign carries. Use ahead of / behind.

**F2 · lede, line 38 · the whole lede is bold, so none of it is emphasised · MAJOR · verifiable: yes**
Build line 341–342 wraps the return of `lede()` in `<b>…</b>`, and `lede()` itself emits `<b>Under the budget the answer holds</b>` and `<b>On F1 alone the sign depends…</b>` (lines 477, 480). Nested `<b>` inside `<b>` renders uniformly bold; `.lede` CSS sets only `font-size:17px`. The two sentences the author chose to promote are typographically indistinguishable from the other three, and 148 words of unbroken bold is the hardest paragraph on the page to read.
Fix: remove the outer `<b>` at line 341–342 (add `font-weight:600` to `.lede` only if the whole-lede weight was wanted, in which case the inner `<b>`s need a different device). *(Mechanical rendering overlaps role 10; I file it because it is what makes the lede's sentence structure unreadable.)*

**F3 · lede, line 38 · "the lead clears that scale" — whose lead, and in which draw · MAJOR · verifiable: yes**
> "Set the refits under 0.2 F1 aside, as the report does, and the lead clears that scale: `chorus_norm` +0.015 in the replicate's draw, 4 of 4 folds and `chorus_gain_norm` +0.013 in the replicate's draw, 4 of 4 folds."

Three defects in one sentence. (a) "the lead" is new — the preceding sentence reported a net **behind** by 0.019 in that same draw, so the reader has no lead in hand. (b) Both items are the replicate's draw; this run's draw is silently absent, and Table 1 says setting aside leaves it at +0.004 and −0.007, i.e. inside the noise scale. As written the sentence reads as a general result. (c) `and_join` with two items produces "4 of 4 folds and `chorus_gain_norm` +0.013" with no comma, so the list boundary is invisible and "in the replicate's draw" is stated twice.
Fix (build lines 471–475): factor the draw out and say what this run's draw does. *"Set the refits under 0.2 F1 aside, as the report does, and both chorus nets clear that scale in the replicate's draw — `chorus_norm` +0.015 F1 and `chorus_gain_norm` +0.013 F1, ahead in 4 of 4 folds each. In this run's draw they stay inside it."*

**F4 · lede, line 38 · "it settles nothing that was open" · MAJOR · verifiable: no**
Vague, and half-contradicted by the next clause ("Under the budget the answer holds", which *is* something settled). Name the open question — on the evidence of §3 that is whether the chorus nets beat CoactDetect on F1 alone. Fix: *"…and it does not settle whether a chorus net beats CoactDetect on F1 alone."* Also "moves each chorus net **toward** CoactDetect" understates one case: `chorus_norm` in this run's draw goes −0.007 → +0.004, i.e. past it.

**F5 · lede + §3 + §4 + §5 · bare F1 numbers, no unit · MAJOR (house rule) · verifiable: yes**
"goes from −0.007 as run to +0.004", "−0.032 as run, −0.018 tuned", "by +0.004", "loses 0.063", "against a draw-to-draw scale of 0.010". CLAUDE.md: every number carries its unit, counts included. The unit appears once per section at best ("0.010 F1"). Fix in the formatters (`signed()` call sites, build lines 460, 474, 482, 492–495, 510, 533, 566): carry "F1" on the **first** number of each block and on every number in a list that mixes quantities — §5's "loses 0.063 … loses 0.024 … at most 0.020" is F1 mixed with seconds in the same sentence.

**F6 · §2, line 57 · "binned SCE's top, 30 s" — undefined abbreviation · MAJOR (house rule) · verifiable: yes**
SCE appears exactly once on this page (Grep: line 58 only) and is never expanded. CLAUDE.md: define every abbreviation at first use. The parent report has the same gap (`report.html` line 59 uses SCE in its own lede unexpanded), so inheritance does not rescue it.
Fix (build line 362): *"…and runs to the top of the binned synchronous-calcium-event (SCE) detector's grid, 30 s…"*

**F7 · §1 line 41, §2 line 55 · figure references carry a number and no name · MAJOR (house rule) · verifiable: yes**
"(the report's Figure 3)" and "(the report's Figure 4)". CLAUDE.md: a reference in prose carries the number **and** the name. Verified against `report.html`: Figure 3 is *"Merging calls"*, Figure 4 is *"The nested cross-validation layout."*
Fix (build lines 345–346, 359): *"the report's Figure 3, merging calls"* and *"the report's Figure 4, the nested cross-validation layout."* Same defect on this page's own refs — "(Figure 1)" (line 84), "(Figure 2)" (line 89), "(Figure 3)" (line 93), "Figures 1 and 2" (line 101) — all bare. Use *"Figure 1, the chorus nets minus CoactDetect on F1 alone"*, etc.

**F8 · §1, §2, §5, §7 · sections of the report cited by bare number · MAJOR (writing conventions) · verifiable: yes**
"the report's section 7", "section 9", "section 6", "its section 11", plus "goal 1" ×4 and "goal 2" ×1. `docs/writing_conventions.md`: name things, don't index them; prefer the consequence to the label. A reader cannot tell what "the report's section 7" holds without opening it. Fix: *"the report's matched-gap re-scoring (its section 7)"*, *"the report's account of the failed trainings (section 6)"*, and name the goals rather than numbering them (their pages in `docs/goals/` have names).

**F9 · §3 ¶1, line 84 · four near-identical clauses, ~125 words, one sentence, duplicating Table 1 · MAJOR · verifiable: no**
> "Counting every refit, in this run's draw `chorus_norm` goes from −0.007 as run to +0.004 with its gap tuned (3 of 4 folds ahead; *t* 2.4, corrected 1.6), choosing 5, 8, 5, 8 s; in this run's draw `chorus_gain_norm` goes from … ; in the replicate's draw `chorus_norm` goes from … ; in the replicate's draw `chorus_gain_norm` goes from …"

Passage test: the one sentence this block exists to deliver is *tuning moves every chorus net up by about 0.01 F1, which is the noise scale.* The remaining ~110 words are 24 numbers that Table 1 already carries in a form the reader can scan. Nothing a sceptic demands is here that the table lacks. Four clauses of identical shape cannot be held in working memory, and the draw label is repeated four times because `alone_text` loops draw-major (build lines 489–495).
Fix (build 487–497): lead with the payload, group by draw, cut the gap lists to the table. *"Counting every refit, tuning moves every chorus net up by 0.008 to 0.010 F1 — about the noise scale. In this run's draw `chorus_norm` goes −0.007 → +0.004 and `chorus_gain_norm` −0.045 → −0.037; in the replicate's draw, −0.057 → −0.048 and −0.029 → −0.019. Folds ahead, *t* values and the chosen gaps are in Table 1."*

**F10 · §3 ¶2, line 85 · subject changes halfway; "often" contradicted by the next clause · MAJOR · verifiable: yes**
> "The chorus nets often fail to train, collapsing to one call per recording (the report's section 6), and those refits are inside the means above: 1 of the 40 refits behind them in this run's draw and 3 of the 40 refits behind them in the replicate's draw score under 0.2 F1."

(a) The sentence opens on "The chorus nets" and ends on a compound subject "1 of the 40 … and 3 of the 40 …" whose verb "score" arrives 30 words later. (b) "**often** fail" is denied by the page's own numbers in the same sentence: 1/40 and 3/40, i.e. 2.5% and 7.5%. (c) "the 40 refits **behind** them" reads as *trailing*, not *underlying*. Three defects, one sentence.
Fix (build 519–523): *"Some chorus-net refits fail to train, collapsing to one call per recording (the report's section 6), and they are inside the means above: 1 of 40 refits in this run's draw and 3 of 40 in the replicate's draw score under 0.2 F1."* Then the same four-clause problem as F9 follows in the next sentence ("`chorus_norm` +0.004 in this run's draw …; `chorus_gain_norm` −0.007 …; …") — group it by draw the same way. Payload of the whole block, currently last, is *"which treatment is right is not settled here"*: promote it to the block's second sentence.

**F11 · §4, line 89 · dangling modifier, "call less", and "the net leads only chorus_norm" · MAJOR · verifiable: yes**
> "Held to the shared false-alarm budget, a wider gap lets a net call less and so fit the budget at a lower threshold, and every chorus net gains"

"Held to the … budget" attaches grammatically to "a wider gap"; it is the *net* that is held to the budget. "call less" should be "make fewer calls" (count noun). And the sentence's subject shifts twice: gap → net → every chorus net.
Then:
> "the net leads only `chorus_norm` in this run's draw, fold 2, by +0.004, `chorus_norm` in the replicate's draw, fold 1, by +0.001, `chorus_gain_norm` in the replicate's draw, fold 4, by +0.012"

reads as *the net leads chorus_norm* — but the net **is** `chorus_norm`. And `ahead_phrase` joins three items with commas while each item already contains two commas (build lines 458–461), so the list cannot be parsed.
Fix (build 539–542, 458–461): *"A net held to the budget can use a wider gap to make fewer calls, and so meet the budget at a lower threshold; every chorus net gains: …"* and *"Only three folds of 32 go to a net: `chorus_norm`, this run's draw, fold 2 (+0.004 F1); `chorus_norm`, the replicate's draw, fold 1 (+0.001 F1); `chorus_gain_norm`, the replicate's draw, fold 4 (+0.012 F1)."* — semicolons between items, parentheses around the margins.

**F12 · §5, line 93 · "that setting" claims more than the code computes; relative clause collapses · MAJOR · verifiable: yes**
> "In all 64 the inner fits preferred at least one setting that the crowded check then refused, and in all 64 that setting had a wider gap than the one chosen."

The first clause says *at least one* setting was refused; the second says *that setting* — singular, definite — had a wider gap. Where several were refused, "that setting" has no referent. The code (build lines 554–555) computes `any(x.gap_sec > chosen …)`, i.e. *at least one of the refused settings* was wider. The prose asserts a stronger, different fact.
Fix: *"In all 64, the inner fits preferred at least one setting the crowded check refused, and in all 64 at least one of those refused settings had a wider gap than the one chosen."*
Same block:
> "A wide merge fuses events a few seconds apart, which the bench's recordings, with planted events at least 120 s apart, cannot penalize, and the crowded recordings can (Figure 3)."
A relative clause with an interpolated modifier and a trailing coordination hung off it. Fix: *"A wide merge fuses events a few seconds apart. The bench's recordings plant events at least 120 s apart, so they cannot penalize that; the crowded recordings can (Figure 3, the gap each fold chose)."*
Same block, last sentence (~60 words): "loses 0.063 and … loses 0.024 on the crowded recordings" suspends the object 25 words past the first number, and "more than the 0.02 the check allows, and every other choice loses at most 0.020" prints the same allowance at two precisions — **0.020 is not more than 0.02**, so the two halves look like a contradiction. Fix (build 562–568): quote the allowance once, at one precision, and say "at most 0.020 F1, inside the 0.020 F1 the check allows".

**F13 · §6, line 101 · verbless fragment · MAJOR · verifiable: yes**
> "The other 4 have held-out numbers: in that column, and for the chorus nets in Figures 1 and 2."
Nothing after the colon has a verb, and "in that column" cannot serve as the predicate.
Fix (build 586–587): *"The other 4 have held-out numbers, shown in that column and — for the chorus nets — in Figure 1 and Figure 2."* Also "changed **it** in 16 of 64 choices" (line 101): "it" could be the configuration or the gap; write "changed the configuration".

**F14 · §2 closing ¶, line 79 · counts cannot equal files · MINOR · verifiable: yes**
> "every fit's picked threshold, every recording's counts and every empty recording's call count **equal the run's own files**"
A count does not equal a file. Fix (build 383–385): "…**match the run's own files**". "exactly, not approximately" in the same sentence is one word doing the work of four — keep "exactly" and cut ", not approximately" unless the contrast is defending against a known objection.

**F15 · dim header, line 34 · "which it assumes" · MINOR · verifiable: no**
> "An addendum to the fair comparison's report (…), which it assumes."
"which" points back to the report, "it" forward to this page — the two pronouns cross. Fix (build 337–339): *"An addendum to the fair comparison's report (…). It assumes you have read it."* — or *"…report, which this page assumes you have read."*

**F16 · §2, bullet 4, line 64 · one bullet, four rules, ~105 words · MINOR · verifiable: no**
"Goal 1's move rule" bundles the 0.002 threshold, the crowded check, the crowded recordings' construction, and who applies the check. The payload — *the search only leaves 2 s for a real gain that also survives the crowded check* — is in the first 25 words; the rest is parameters. Split into two bullets: the move rule, then the crowded-recording check with its construction.

**F17 · §2, line 63 · "as the run chose the threshold alone" · MINOR · verifiable: no**
Ambiguous between "in the same way the run chose the threshold by itself" and "as the run chose only the threshold". Fix: *"…the same rule the run used when it chose the threshold on its own."*

**F18 · §1 ¶1, line 44 · "which bounds what the gap could do without measuring it" · MINOR · verifiable: no**
"it" = the gap, but the nearest candidate is "what the gap could do". Fix: *"…which bounds what the gap could be worth without tuning it."*

**F19 · §7, line 112 · a clause that restates its own first half · MINOR · verifiable: no**
> "A gap is taken only for at least 0.002 inner F1; a smaller gain is treated as no gain."
The second clause adds nothing. Cut it (build: the limits list).

**F20 · §3 ¶1 vs Figure 1 caption · same quantity, two names · MINOR · verifiable: yes**
Prose: "the median change from **swapping** the recordings alone". Caption: "the median change in F1 from **changing** the recordings alone". Pick one verb (build 396 vs 497). Related: the lede's "a draw-to-draw scale of 0.010" names a third thing that is the same number.

**F21 · lede · "draw" and "shortfall" used before they mean anything · MINOR · verifiable: yes**
"in both draws" appears in the lede; "draw of recordings" appears only inside SVG aria-labels (Grep: lines 86, 90, 94), never in prose. "shortfall" first appears in the lede and is never defined as *the as-run margin to CoactDetect*. First use is the lede, so define there: "in both draws of recordings" and "…closes 10% to 45% of the chorus nets' margin behind CoactDetect".

**F22 · §7, line 107 · "about 0.03% of firings" · MINOR · verifiable: no**
"firings" is unglossed on this page. Either name the unit the export uses or write "of the simulated firings". *(Whether an uncleared contamination should be a bullet at all rather than a stop is not mine — role 4 / role 7.)*

**F23 · §3 heading · "3. On F1 alone: it depends on the failed trainings" · MINOR · verifiable: no**
"it" in a heading has no antecedent; a heading is read out of order. Fix: *"3. On F1 alone: the sign depends on how the failed trainings are counted."* Also §6's heading "Every net, both draws" describes the table but not the paragraph under it, which is about re-choosing configurations.

---

## Boundaries
Not mine and not covered: whether the numbers are right (role 4), figure legibility/axis labelling/`--w:900px` overflow (role 10), section order (role 11), whether a cold reader can follow the nested cross-validation (role 8). I did not open the rendered screenshots directory — my unit is the sentence.

## The three fixes that matter most
F1 (the lede's headline attributes two nets' results to one), F2 (the lede is uniformly bold, so its structure is invisible), F9/F10/F11/F12 (four blocks, ~585 words, that restate Table 1 in prose a reader cannot hold — the payload is at the end of three of them, and promoting it is the fix, not trimming).
