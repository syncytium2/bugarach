GRANT 5 ok — Read, Grep, Glob

(Delivery channel `SubagentHandback` also held; no Edit/Write/NotebookEdit, no Bash. Nothing under `docs/reviews/` was opened — blindness held.)

## Tool status

`tools/murderboard_prose.sh` **does not exist** in the worktree (`Glob tools/murderboard*` returns only `murderboard_agents.py`, `murderboard_freshness.sh`, `murderboard_revendor.py`, `murderboard_roster.sh`). **I ran the banned-construction search by hand** with Grep over the built file, case-insensitively, for: `not just`, `it's not about`, `worth noting`, `delve`, `leverage`, `robust`, `seamless`, `crucial`, `landscape`, `tapestry`, `in today's`, `modality`/`modalities` (the glossary's banned word), and for em-dash pivots (`.{60}—.{60}`). **Zero hits in prose** — the only `—` are the two "no configuration of that shape" dashes in Table 1. Three-item lists were checked by eye and all three ("starting weights / crop order / which recordings", "mean / spread / top-m mean", "drop lr 0.03 / add warm-up / change the head") enumerate real things, not rhythm. `\bdata\b` appears once outside CSS (line 292, "This page and its data (…)"), with no verb, so the plural rule is not violated. **List run: the house list in `doc_review_process.md` role 5, plus the project's banned word from `docs/GLOSSARY.md`.**

Block word counts (hand-counted, prose blocks only): terms box ~175 · answer box ~360 · §1 ~175 · §2¶2 ~105 · §2¶3 ~235 · §3¶1 ~150 · §4¶1 ~145 · §4¶2 ~185 · §4¶3 ~160 · §5¶1 ~155 · §5¶3 ~125 · §5¶4 ~180 · related work ~150. Passage-test verdicts are findings 6 and 7 below; every other block delivers evidence a sceptic would demand and earns its length.

All locations are line numbers in
`<worktrees>/chorus-verify/docs/learned/chorus_collapse/index.html`.

---

## Findings

**1 · line 224–226 · the "recovered" counts sit outside their own stated denominator · MAJOR**
> "Of the collapsed fits of the longer twins, 60 of 62 in chorus_norm were already collapsed where the shorter twin stopped, and 2 came later; 0 recovered with more steps. In chorus_gain_norm, 8 early, 0 later and 3 recovered."

A fit that "recovered" is by definition **not** a collapsed fit of the longer twin, so it cannot be counted inside "Of the collapsed fits of the longer twins". In chorus_gain_norm the arithmetic makes it plain: 8 early + 0 later = 8 collapsed at the longer stop, and the 3 recovered are a fourth category drawn from a different population (fits collapsed at the *shorter* stop). As written, a careful reader computes 8 + 0 + 3 = 11 and cannot reconcile it.
*Fix:* split the frame — "Of the longer twins' fits that collapsed, 60 of 62 (chorus_norm) and 8 of 8 (chorus_gain_norm) were already collapsed where the shorter twin stopped. Going the other way, of the fits collapsed at the shorter stop, 0 chorus_norm and 3 chorus_gain_norm recovered with more steps."
*Verifiable against a source:* **yes** — `docs/learned/chorus_collapse/collapse_table.json` and `tools/diagnose_chorus_collapse.py` hold the twin comparison.

**2 · line 281 vs line 240–241 · "8 distinct … runs" reads as contradicting "7 distinct runs" · MAJOR**
§5: *"Two of the fits are one training run counted twice; counted once, training loss fell below 0.5 in **6 of 7 distinct runs**."* Limits: *"The warm-up was tried on **8 distinct collapsed runs** of chorus_norm, chosen by hand."* The two can only be reconciled if the reader reconstructs that Limits silently folds Figure 1's own fit in with the 8 more — which nothing on the page says. On the page's face it is 7 versus 8.
*Fix:* make Limits explicit — "The warm-up was tried on Figure 1's collapsed fit and 8 more chosen by hand — 8 distinct training runs, because two of the 9 fits are one run stopped at two lengths."
*Verifiable:* **yes** — Table 3 (8 rows, one flagged "the same run as a longer twin's, stopped earlier") plus `replays/`.

**3 · line 91–92, 195, 198 (and §8 line 304) · "plain chorus" is never defined, and the intro promises a definition it does not give · MAJOR**
Line 56 introduces "chorus_norm and chorus_gain_norm are **two of** the small neural networks the project trains" — the "two of" tells the reader there are more and then never names one. "Plain chorus" then arrives in the answer box (line 91) and carries a whole strand of the argument (§4¶3, Figure 4, §8) as the reference failure mode. A cold reader cannot tell whether plain chorus is the un-normalized sibling of chorus_norm, a different architecture, or an earlier version.
*Fix:* one clause at line 62, beside the chorus_gain_norm definition: "Both are variants of **plain chorus**, the same net without the standardization over time; a separate diagnosis found its votes did not respond to events at all."
*Verifiable:* **yes** — `docs/learned/field_size_candidates/why_chorus.txt` and the todo.

**4 · line 198–199 · "so it can fail" / "Most collapsed chorus_norm fits pass it" — *fail* and *pass* attach to different subjects two sentences apart · MAJOR (ambiguity)**
> "…the test gives the same here for untrained plain chorus (0.0003, 0.0002, 0.0003), **so it can fail**. Most collapsed chorus_norm fits **pass it**…"

"So it can fail" reads first as *the test is unreliable* — the opposite of the intended "the test is capable of registering a failure, so a pass means something". And within the same breath "fail" is the test's verdict while "pass" is the fit's. One word, two senses, adjacent.
*Fix:* "…so the test still registers deafness when deafness is there. Most collapsed chorus_norm fits are not deaf: one onset moves a vote by a median of 0.40…" — and drop "pass/fail" for this test entirely.
*Verifiable:* no (wording only).

**5 · line 137 · the bold lead asserts more than the paragraph proves, and turns the page's term of art sideways · MAJOR**
> "**The configuration sets how often; within it, the draw decides which.**"

The paragraph's own conclusion is weaker and different: *"the seed's effect cannot be put down to its starting weights; the recordings it picks are **at least as likely**."* "At least as likely" is not "decides". Worse, "draw" is a defined term on this page (one complete run of the comparison, line 64) and the lead uses it as a causal agent, while the body's mechanism is the *training seed's choice of recordings within* a draw. Compounded by line 242's third sense — "a change that merely **re-drew** each fit's luck".
*Fix:* lead with the payload the paragraph earns: "**The configuration sets how often a fit collapses; which fits collapse is not carried across draws.**" Then state the seed result as the paragraph already does. Replace "re-drew each fit's luck" with "re-rolled".
*Verifiable:* **yes** — the paragraph's own statistics.

**6 · lines 76–109 vs 155–163, 187–191, 210–219 · the answer box and three sections share near-verbatim sentences · MAJOR (redundancy; ~360-word block)**
Examples: box line 105–107 *"the selection on F1 alone picked lr 0.03 in 6 of 8 folds, and both of its collapsed refits came from those picks; the selection under the false-alarm budget never did"* against §3 line 158–161, which is the same sentence with "did pick" and "never picked lr 0.03". Box line 86–89 against §4 line 187–191 (same counts, same clause order). Box line 99–101 against §5 line 213–218.
A summary that repeats its sections word for word means one of the two was not written for its own position. **Passage test on the box:** its payload is *"chorus_norm's fits collapse at lr 0.03 because the head never wakes, and a 200-step warm-up wakes it."* The per-net counts buy a sceptic's confidence and stay; the re-used sentences buy only the author's thoroughness.
*Fix:* compress each duplicated box bullet to one clause and its number, and let the section carry the sentence. Roughly 120 words come out of the box with nothing lost.
*Verifiable:* no (editorial).

**7 · line 246–255 (related work) · "That it prevents this collapse is this page's result." · MAJOR (overstatement in the payload sentence)**
The page's evidence is: one fit trained with a 200-step ramp, plus 6 of 7 other hand-picked runs reaching training loss below 0.5 — judged **by training loss only, not by calls on held-out recordings** (the page says so twice, lines 243–244 and 279–280), with no chorus_gain_norm fit tried (line 282). "Prevents this collapse" asserts more than that, and it is the sentence a reader will carry away because it closes the block.
*Fix:* "That the ramp trains most of the collapsed fits tried — 6 of 7 distinct runs, judged by training loss — is this page's result."
*Verifiable:* **yes** — Table 3 and §7.

**8 · line 166 · "the 111 fits collapsed in both draws" parses as a sentence, not a noun phrase · MAJOR (grammar, on a load-bearing sentence)**
> "That report reads the 111 fits collapsed in both draws as the same fits failing twice."

Read left to right, "the 111 fits collapsed in both draws" is subject-verb; the reader reaches "as the same fits" and has to restart. And the correction itself is imprecise: 111 fits *are* literally the same fits failing twice — what §2 refutes is the **implication** that something about the individual fit caused it.
*Fix:* "That report treats the 111 fits **that** collapsed in both draws as evidence that particular fits fail. §2, which configurations collapse, shows the configurations' rates alone predict that overlap: 111.5 expected against 111 observed. The overlap is not about the individual fit."
*Verifiable:* **yes** — line 137–141 of this page and the replicate report.

**9 · line 83 vs line 131 · the box and the body grade the same effect differently · MAJOR (precision)**
Box: *"chorus_gain_norm follows its encoder's shape **at least as much**"*; §2: *"chorus_gain_norm follows shape **more than** the learning rate"*. Table 1 supports the stronger statement (78% at 4 × 6 / lr 0.03 against 3% at 8 × 4 / lr 0.03; 25% at 4 × 6 / lr 0.01). Pick one.
*Fix:* use "more than the learning rate" in both places.
*Verifiable:* **yes** — Table 1 on this page.

**10 · line 246–247 · "Dead ReLU units … have been measured to grow with the learning rate" · MINOR (grammar/precision) + undefined abbreviation**
Units do not grow; their *share* does. And **ReLU is never expanded** — the house rule is every abbreviation at first use, and this is the one abbreviation on the page that is not (GELU, ROI, F1, SD, lr are all expanded).
*Fix:* "The share of **dead rectified-linear (ReLU) units** — units that output zero for every input — has been measured to grow with the learning rate."
*Verifiable:* **yes** — Gulcehre et al. 2022; `docs/GLOSSARY.md` expands the ReLU sense of "dead".

**11 · line 249–250 · "what fails is training's waking it, so these are related observations, not this mechanism" · MINOR (ambiguity)**
"Training's waking it" is a possessive gerund the reader has to parse twice, and "not this mechanism" leaves the referent dangling — *not this page's mechanism*? *not the mechanism of this failure*?
*Fix:* "here every head starts mostly silent, working fits included; what fails is that training never wakes it. The prior work describes a related observation, not the failure this page found."
*Verifiable:* no.

**12 · line 222 (first use), 239, Table 3 · "twin" is undefined jargon on a self-contained public page · MINOR**
§2 line 150–152 describes the relationship without naming it ("5 pairs of configurations differ only in step count; the shorter one's fits are the longer one's stopped early"); "the longer twins" then arrives at line 222 as a term. `docs/GLOSSARY.md` defines it, but the glossary does not travel with the page.
*Fix:* name it where it is described, line 150: "…differ only in step count — **twins**; the shorter twin's fit is the longer twin's stopped early…".
*Verifiable:* **yes** — `docs/GLOSSARY.md`, "twin (configurations)".

**13 · title/`<title>` and line 50 vs the whole body · "tuning fits" in the title, "inner fits" everywhere else · MINOR**
The glossary sanctions both ("Also called a tuning fit"), but on the page a reader meets "tuning fits" in the headline and never sees the word again.
*Fix:* either title it "inner fits", or add "(inner fits)" at line 66 where the term is defined.
*Verifiable:* **yes** — `docs/GLOSSARY.md`, "inner fit".

**14 · line 85–86 · "the head, the eight layers that turn the pooled per-ROI votes into the output" · MINOR (contradicted by §4 of the same page)**
§4 line 175–177 describes the head as **8 convolution layers plus a linear output layer** — nine, not eight. And the head's input is the three pooled statistics, not "the pooled per-ROI votes". Also: "eight" spelled here, "8" everywhere else (lines 175, 183, 214).
*Fix:* "the head — 8 convolution layers and a linear output, which turn the three pooled statistics into the score."
*Verifiable:* **yes** — line 172–177 of this page.

**15 · line 177 · "A GELU passes positive input" · MINOR (asserts more than is true)**
GELU is x·Φ(x); a positive input is attenuated, markedly so near zero (at x = 0.5 the output is ~0.35). "Passes" states identity.
*Fix:* "A GELU leaves large positive input almost unchanged and maps negative input to a small dip, no lower than −0.17, that still carries a gradient."
*Verifiable:* **yes** — Hendrycks & Gimpel 2016, already cited on the line.

**16 · line 231–233 · four pronouns, two referents, in one sentence · MINOR (ambiguity)**
> "A 50-step ramp is not enough, and **it** shows that a head can wake and die again: **it** is awake by step 40, has a silent layer again from step 110 and ends with 3 silent, while **its** loss retraces the fit as run."

The first "it" is the run, the second is the head, the third is the run again. "Ends with 3 silent" has no noun (3 what — layers). "Die" is a third metaphor beside *silent* and *dead* (line 187), and the glossary explicitly separates "silent" from the ReLU sense of "dead". "The fit as run" needs "as originally run" in prose.
*Fix:* "A 50-step ramp is not enough, and it shows a head can wake and fall silent again: the head is awake by step 40, has a silent layer again from step 110, and ends with 3 of 8 layers silent, while the loss retraces the original run."
*Verifiable:* no.

**17 · line 242–243 · "A replay with nothing changed reproduces the collapse, so doing nothing trains none of them" · MINOR (generalization from one case)**
The as-run replays verified were the **two** Figure 1 fits (line 210–211); §7 concedes "That a collapsed fit's head is never woken rests on the one collapsed fit replayed as run". "None of them" covers all 8.
*Fix:* "Replaying Figure 1's collapsed fit with nothing changed reproduces its collapse to the bit, and training is deterministic given the seed, so doing nothing would train none of these either." (Or state that all 8 were replayed unchanged, if they were.)
*Verifiable:* **yes** — `replays/`, `tools/diagnose_chorus_collapse.py`.

**18 · line 243 · "would train each as often as its configuration's fits train, 1.4 of 7" · MINOR (unit + readability)**
Bare count, no noun — the house rule wants "1.4 of 7 runs". And "train each as often as" invites the reader to look for a rate when the number is an expected count.
*Fix:* "…would be expected to train 1.4 of the 7 runs, the rate at which these configurations' fits train anyway."
*Verifiable:* **yes** — Table 1 / Table 3.

**19 · line 134–135 · "its other shapes in 8%, and at lr 0.01 its 4 × 6 configurations still collapse in 25%" · MINOR (bare percentages)**
The noun appears once ("in 78% of fits") and is then elided twice. Per the house rule every number carries its unit; the ellipsis also makes the reader re-check what the denominator changed to.
*Fix:* "…and its other shapes in 8% of fits; at lr 0.01 its 4 × 6 configurations still collapse in 25% of fits."
*Verifiable:* **yes** — Table 1.

**20 · line 128–131 · telegraphic semicolon list with no verb · MINOR (grammar)**
> "Training length is tangled with depth: at lr 0.03, 900 steps 65% (141 of 216 fits); 1,800 steps 82% (59 of 72 fits); 3,600 steps 85% (92 of 108 fits), and the 3,600-step configurations are all 6 layers deep."

Three verbless items followed by a comma-spliced independent clause.
*Fix:* "Training length is tangled with depth. At lr 0.03, 900-step configurations collapse in 65% of fits (141 of 216), 1,800-step in 82% (59 of 72) and 3,600-step in 85% (92 of 108) — and every 3,600-step configuration is 6 layers deep, so the two cannot be separated here."
*Verifiable:* **yes** — Table 1.

**21 · line 116–117 · "the only one of this configuration's 18 second-draw inner fits that trained (1 of 18)" · MINOR (redundancy)**
"(1 of 18)" restates "the only one of … 18". Same pattern at line 192–193 ("all have one (3 of 3)") and line 222 ("60 of 62 … and 2 came later").
*Fix:* drop the parenthetical in each.
*Verifiable:* no.

**22 · line 118–120 · "the threshold search keeps the first best value on its ascending list, the lowest, 0.0001" · MINOR (redundancy + ambiguity)**
"First on an ascending list" already means lowest; "the lowest" is a third apposition in one clause. Also "any threshold below **it**" two clauses earlier — "it" is the flat output *value*, which has not been named as a value.
*Fix:* "The collapsed fit's output is flat, so any threshold below that flat level gives the same single call; the threshold search takes the first of its ascending list of probabilities, 0.0001 (a logit of −9.2)."
*Verifiable:* **yes** — the builder.

**23 · line 121 · "as do 2 working chorus_norm fits'." · MINOR (grammar)**
A sentence ending on a bare possessive apostrophe.
*Fix:* "…as do those of 2 working chorus_norm fits."
*Verifiable:* no.

**24 · line 124–125 · "every configuration at lr 0.03 collapses in 42% to 92% of its fits" · MINOR (precision)**
A configuration does not collapse; its fits do — the page's own definition (line 72) makes collapse a property of a fit, and line 155 gets it right ("A configuration whose fits collapse…").
*Fix:* "every configuration at lr 0.03 has 42% to 92% of its fits collapse".
*Verifiable:* **yes** — line 72 of this page.

**25 · line 151–152 · "so they are left out of these tests" · MINOR (ambiguous pronoun)**
"They" could be the 5 pairs, the shorter fits, or both members.
*Fix:* "so the shorter twin's fits are left out of these tests."
*Verifiable:* no.

**26 · line 284–285 · "some of the starting silence may be scale rather than a layer that passes nothing" · MINOR (grammar, category mismatch)**
"Silence may be scale" sets a property against an object.
*Fix:* "…some of the starting silence may be a matter of scale rather than a layer that truly passes nothing."
*Verifiable:* no.

**27 · line 52–53 · "The draws' results were not changed; 14 replays of 10 fits retrain them from their own starting points" · MINOR (ambiguous "them" + stacked genitives)**
"Them" nominally points at "the draws' results", which is exactly what the clause before says was *not* changed; the intended referent is the fits. The preceding sentence also stacks three "of"s: "from the saved fits **of** both draws **of** the project's fair comparison…".
*Fix:* "A diagnosis built from the saved fits of the project's fair comparison between coded detectors and learned nets (goal 2), both draws. No draw's results were changed: 14 replays retrain 10 of those fits from their own starting points to watch the failure happen."
*Verifiable:* no.

**28 · line 187, 246, 232 · three words for one state: *silent*, *dead*, *die* · MINOR (consistency)**
Line 187 "counted 1 working fit as dead" uses "dead" informally for the page's own measure, while line 246 and the glossary reserve "dead" for the ReLU sense the page is explicitly **not** using. Line 232 adds "die".
*Fix:* keep "dead" exclusively for the ReLU sense; line 187 → "counted 1 working fit as silent"; line 232 → "fall silent again".
*Verifiable:* **yes** — `docs/GLOSSARY.md`, "silent layer", which makes the distinction in terms.

**29 · lines 220, 236, 245, Table 3 · four figure/table references carry the number without the name · MINOR (house rule)**
Line 236 "1 of them Figure 1's own configuration"; line 220 caption "the fits in Figure 1"; line 245 caption "each collapsed fit in Table 3"; Table 3 cell "(Figure 1's configuration)". Every prose reference elsewhere does it correctly ("Figure 3, silent layers and flat outputs"). *(Boundary: whether every figure is numbered and labelled at all is the mechanical reviewer's; this is the writing-convention half — number **and** name in the reference.)*
*Fix:* "Figure 1's configuration, the collapsed fit on a held-out recording" and so on; the Table 3 cell can stay bare since the table is adjacent.
*Verifiable:* **yes** — CLAUDE.md plot conventions.

**30 · line 97 and 206 vs line 207 · curly vs straight apostrophe in the same phrase · MINOR (typography)**
The link text reads "the earlier diagnosis’s test" (U+2019) while the Figure 4 caption reads "the earlier diagnosis's test" (straight). Everything else on the page uses straight.
*Fix:* normalise in the builder.
*Verifiable:* **yes** — `tools/diagnose_chorus_collapse.py`.

**31 · Figure 2 caption (line 127) · "the mark's shape is the encoder's shape" · MINOR (one word, two senses, in one clause)**
Also "Rows: learning rate, with the collapsed count over the row beside it" — "over the row" reads as *above the row* before it resolves to *out of the row's total*.
*Fix:* "the glyph encodes the encoder's width × depth" and "Rows: learning rate, with that row's collapsed count and total beside it."
*Verifiable:* no.

**32 · Figure 1 caption (line 63) · "each fit's output logit, lowest to highest in every 1-second bin" and "Shaded rows in panel A only aid reading" · MINOR**
The first phrase is a min–max band but does not say so; the second puts "only" where it modifies "aid".
*Fix:* "each fit's output logit, drawn as the range from lowest to highest within each 1-second bin"; "Shaded rows in panel A are a reading aid only."
*Verifiable:* no.

**33 · line 147–148 · "correlation 0.24, p = 0.147" — the coefficient is unnamed · MINOR (precision)**
Every other test on the page names its procedure ("collapse labels shuffled within each configuration"). Pearson and Spearman on 0.24 would mean different things.
*Fix:* name it — "Spearman correlation 0.24".
*Verifiable:* **yes** — the builder.

**34 · line 148–149 · "the recordings it picks are at least as likely" · MINOR (vague comparative)**
Likely to be *what*? The intended sense is "the likelier explanation", but "at least as likely" invites the reader to hunt for the probability.
*Fix:* "…so the seed's effect cannot be put down to its starting weights; the recordings it picks are the better candidate, and this page does not separate the two."
*Verifiable:* no.

**35 · §6 heading, line 257 · "The choice it leaves" · MINOR (dangling pronoun in a heading)**
A heading is read out of context, from a table of contents or a link. "It" has no antecedent there.
*Fix:* "6. The choice the collapse leaves".
*Verifiable:* no.

---

## What I checked and found clean

The banned-construction list (all 11 forms, zero hits). "Data" plural. Em-dash pivots and uplifting closes — none; the page ends on locations and references, correctly. Three-item lists — all substantive. Definitions at first use — ROI, logit, F1, GELU, SD, lr, top m, draw, inner fit, refit, configuration, collapse, census, silent are all defined in place (ReLU and "plain chorus" and "twin" are the three exceptions, findings 3, 10, 12). Internal arithmetic I could check line-against-line all reconciles: 292 + 7 = 299 = 146 + 153; Table 1's lr-0.03 column sums to 292 of 396 and the sub-0.03 columns to 7 of 468; 432 − 153 = 279 and 432 − 75 = 357; 8 + 3 twin categories aside (finding 1); 14 replays over 10 fits; F1 0.125 and the −9.2 logit are both right. Section order runs problem → scope → cost → mechanism → cause and remedy → choice → limits → locations, and each section's opening sentence follows from the previous section's last — no flow breaks beyond findings 5 and 8.
