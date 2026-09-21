GRANT 5 ok — Read, Grep, Glob

---

## Run note before the findings (this is a finding about the run, not the artifact)

**`murderboard_prose.sh` could not be run.** Two reasons, both worth recording:

1. The role instruction says "run the tool, do not describe it" and names `murderboard_prose.sh`. Running it requires **Bash**, which role 5's grant (`Read, Grep, Glob`) does not include. The instruction and the grant are incompatible as written. This is not a fallback-path mismatch — my grant matches the process file exactly — it is a gap in the process file itself.
2. The script is **not vendored into bugarach**. `tools/` here holds `murderboard_agents.py`, `murderboard_freshness.sh`, `murderboard_revendor.py`, `murderboard_roster.sh` and no prose tool.

I reproduced the **word/form half** faithfully with Grep (the script's own patterns, read out of its source, and the banned-word run derived from `docs/doc_review_process.md` line 569). I could **not** reproduce the **block half** mechanically; the counts below are hand-derived and marked as such. **Treat the block table as judgement, not as tool output.**

**List cited:** the banned-word run in `docs/doc_review_process.md` role 5 — `delve, leverage, robust, seamless, crucial, landscape, tapestry` — plus the four regex forms from the script body.

### Banned constructions — scan output

```
line   construction                       kind   context
24     robust                             word   in: ...surveyed in Louis, Borgelt & Grün 2010 and ranked most robust by
—      not just X, but Y                  form   no match
—      it's not about A, it's about B     form   no match
—      it's worth noting                  form   no match
—      In today's ___                     form   no match
—      delve/leverage/seamless/crucial/landscape/tapestry  word   no match
```

**Judgement on the one hit:** line 24 `robust` is **not a defect**. It reports what Stella et al. 2022 concluded ("ranked most robust by"), i.e. it is the paper's finding in the paper's word. Keep. (Flagging it anyway so the absence of a flag is not what the record shows.)

**Near-miss, reported so it is not mistaken for a clean pass:** line 46, "**What rigid shift destroys is not only brief coordination**". This is `not only X` without the `, but Y` completion, so the regex does not fire. It is also a genuine correction of an earlier claim, not rhythm. **Keep.** Same for line 220, "**An edge artefact is not excluded — it is indicated**": an em-dash pivot, but into a *downbeat*, which is not the banned form.

**Three-item rhythm lists:** none. Lines 42, 228 and 251 each carry three items because there are three things.

### Block lengths — HAND-COUNTED, tool not run

| block | ~words | over 120? | payload sentence | where it sits |
|---|---|---|---|---|
| 23–33 (lineage) | ~145 | **yes** | "What is this project's own is narrow: making that construction differentiable and trainable…" | **last sentence** |
| 39–49 (what rigid shift destroys) | ~150 | **yes** | "What rigid shift destroys is not only brief coordination" | middle (line 46) |
| 51–57 | ~98 | no | first sentence | correct |
| 59–64 | ~95 | no | first sentence | correct |
| 207–214 | ~112 | borderline | first sentence | correct |
| 225–241 (bullet list) | ~220 | **yes** | n/a — list | see F-19 |
| 245–257 (numbered list) | ~170 | **yes** | n/a — list | see F-19 |
| all others | <110 | no | — | — |

---

## Findings

Severity: **critical** = a reader will take away something false · **major** = a reader stalls or cannot check the claim · **minor** = friction.

### Critical

**C-1 · line 207 vs the table at 192–202 · "label-free" names two different things, and the collision makes a bolded sentence read as false against its own table.**
> "**At the event itself, half the label-free calls contain no ROI onset at all.**"

The table's rows 196–199 are *supervised* models using the **label-free threshold rule**, and their medians are 4 and 5 ROIs — not zero. The rows with median 0 and 1 are `line vs rigid shift`, i.e. models **trained label-free**. So "the label-free calls" points at four rows where the claim is false and two where it is true. The document uses "label-free" for the threshold rule (lines 138, 196–199) and for the training regime (lines 132, 157, 227) without ever distinguishing them.
**Fix:** reserve "label-free threshold" for the rule and "trained against rigid shift" for the regime, everywhere. Then: "**At the event itself, half the calls from the models trained against rigid shift contain no ROI onset at all.**"
*Verifiable against a source:* yes — against the table on this page.

**C-2 · throughout · the document's most-repeated number has no named quantity.**
`0.49–0.53` (41), `0.41–0.49` (45), `0.66–0.69` (63, 182), `0.47–0.57` (180), `0.73–0.76` (180), `0.58–0.60` (251), `0.550 at 22.4 s` (250), `0.71–0.77` (190), `0.07 and 0.00` (174). None is ever told what it measures. F1 scores on the same page are also bare two-decimal numbers, so a reader has no way to know these are a different scale — and "reads at chance" (41) only parses once you have guessed it is an AUC. CLAUDE.md: *every number carries its unit*.
**Fix:** name it once, at first use (line 41), and carry the name: *"that control reads at chance — an area under the ROC curve (AUC) of 0.49–0.53 for a classifier asked to tell real from shifted…"*. Then every later range reads "AUC 0.66–0.69".
*Verifiable:* no — needs the author.

**C-3 · line 13 · a bolded scope claim the rest of the page contradicts.**
> "so every learned detector here is fitted on a **simulator** whose events were measured from the lab's own recordings"

Line 133 trains "on real lab fast-stream baselines", and the whole right half of the table at 159–164 is labelled "real, 10 s / real, 20 s".
**Fix:** "so every **supervised** detector here is fitted on a **simulator** whose events were measured from the lab's own recordings".
*Verifiable:* yes — lines 133 and 159–164.

**C-4 · line 35 · "the night answered all three" is contradicted forty lines later.**
> "Three questions follow, and the night answered all three."

Line 48 says "Whether that counts as coordination is the second decision below", and lines 249–251 list it as still open, under *What waits on Tony*. Also: which three? "What waits on Tony" has four. Also a preview sentence — throat-clearing the house voice forbids.
**Fix:** delete the sentence. The three bolded paragraphs that follow announce themselves.
*Verifiable:* yes — lines 48–49 and 249–251.

**C-5 · "line" carries three unrelated meanings on one page.**
`line` the architecture (52), "**Both `line` builds**" the family including the ablation (115), and "a **line**" the synthetic plant shape (103) — which is then divided by two other plant shapes in the table header "line ÷ burst". Line 277 confirms the name has already slipped once: "⚠ **`line` named the length-only build in the handoff written hours earlier**".
**Fix:** give the architecture a reader-facing name and use the identifier only in the provenance table and the code paths. E.g. "the **counting build** (`line`)" and "the **length-only build** (`line_length`)"; keep "a line" for the plant. Then line 115 becomes "Both counting builds tell a line plant from a burst better than `tube` does…".
*Verifiable:* no — naming is the author's.

### Major

**M-6 · line 53 onward · `tube` is the subject of the page and is never defined.**
`tube` appears 32 times. `line` gets a gloss at line 52 ("counts how many ROIs are lit and judges that count against its own background"); `tube` gets none, ever. Nor do `tube_guard`, `tube_ratio`, `tube_ratio_guard`, `tiny`, `trace`, `rate+context`, or "the tube family" (60) — seven of fourteen table rows are unexplained code identifiers. CLAUDE.md: *no internal code identifiers standing in for reader-facing names*.
**Fix:** one sentence beside the first gloss. At minimum a one-line-per-row key under the bake-off table.
*Verifiable:* yes — against `src/bugarach/learn/nets/`.

**M-7 · line 39 · a tautology standing where a caveat should be.**
> "**Rigid shift hides and it destroys — with the destruction measured only where it was measured.**"

"measured only where it was measured" asserts nothing. And "hides" has no object — a reader cannot tell whether rigid shift conceals coordination or conceals something from the analyst.
**Fix:** "**Rigid shift removes cross-ROI coordination, and that removal has been checked on two corpora, not on all of them.**"
*Verifiable:* no.

**M-8 · line 45 · a control named by its code identifier, compared against numbers whose scale is never given.**
> "a graded control (`freeze_half`, 0.41–0.49 against 0.00 and 1.00) shows the measure can register partial removal"

Three problems. `freeze_half` is a raw identifier. "against 0.00 and 1.00" does not say what those endpoints are. And if the scale is the same as line 41's chance band of 0.49–0.53, then 0.41–0.49 sits *at or below chance* — which would show **complete** removal, not partial, so the sentence's conclusion does not follow from its number.
**Fix:** name the control by what it does, state the endpoints, and reconcile the scale with line 41 or say plainly that they differ.
*Verifiable:* partly — the numbers are in `../rigid_shift_look/controls/`.

**M-9 · lines 56–57 vs 94–95 · "eight times slower" sits in a sentence about the ablation but the measurement is against `tube`.**
> "`line` fires 5.50 probe firings per fold against the ablation's 1.25, and trains eight times slower."
> "It is also 7.9 times slower to fit (51.4 s against `tube`'s 6.5 s)"

The sentence's comparator is the ablation; the only timing on the page is against `tube`. A reader will read 8× as `line` vs `line_length` — which the page never measures. Compounding it, line 94's "It" grammatically refers to "the second sensor", and a sensor is not slower to fit.
**Fix (line 57):** "…and takes 51.4 s to fit against `tube`'s 6.5 s, 7.9 times slower." **Fix (line 94):** "Fitting the two-sensor build is 7.9 times slower…" — and if the ablation's fit time exists, give it, since that is the comparison the sentence's claim needs.
*Verifiable:* yes — `line_bakeoff/bakeoff.json`.

**M-10 · line 92 · "the dense-but-random block" arrives with a definite article and no antecedent.**
> "**Probe firings** are calls in the dense-but-random block, excluded from precision…"

The reader has not met this block. It is the load-bearing definition of a whole table column.
**Fix:** "**Probe firings** are calls made inside a stretch of the benchmark where ROIs are dense but uncoordinated — no planted event is there to find. They are excluded from precision and reported separately, because a detector can buy recall with promiscuity."
*Verifiable:* yes — `tools/fair_bakeoff.py`.

**M-11 · line 131–133 · the sentence a reader must solve before they can read Figure 2.**
"six arms" is followed by what parses as three items; the reader must work out 2 corpora × 2 displacements + 2 controls. "with no labels on unlabelled" says the same thing twice.
**Fix:** break it. *"Four architectures × three torch seeds × four folds = 48 fits per arm, in six arms: two controls at J = 10 s (supervised, and untrained); and four label-free arms…"*
*Verifiable:* yes — the arithmetic on line 134 confirms six arms.

**M-12 · undefined abbreviations, four of them, in violation of the plot/document convention.**

| line | offender | fix |
|---|---|---|
| 29 | "is CFAR (Finn & Johnson 1968)" | "is **constant false-alarm rate** detection (CFAR; Finn & Johnson 1968)" |
| 99 | "the Cossart lab's CICADA (Denis et al. 2020)" | expand CICADA at first use |
| 100 | "`binned SCE` descends from…" | "binned **synchronous calcium events** (SCE)" — and it is the *first* use of SCE |
| 188 | "until a MAHICE review exists" | expand MAHICE, or say what the review is |

*Verifiable:* yes.

**M-13 · line 135 · `logits` bolded as a defined term, never defined; and a window given in frames only.**
The bold implies a definition follows and none does. And CLAUDE.md requires the conversion where two units name the same quantity — the page uses seconds everywhere else.
**Fix:** "…the top 1 % of the model's per-frame scores (**logits**, its pre-threshold output), comparing a real crop — a 4,096-frame window, N s at this stream's frame interval of M ms — against the same crop rigid-shifted."
*Verifiable:* yes — frame interval is in the export folder spec.

**M-14 · line 139 · a symbol introduced, never given a value, used once.**
*r* is never assigned; its values appear only as table column headers at line 146.
**Fix:** drop the symbol — "…fires at most a stated rate (0.5, 1 or 2 events per 10 minutes)…".
*Verifiable:* no.

**M-15 · line 146 · table headers drop the unit after the first column.**
> "| ≤ 0.5 events / 10 min | ≤ 1 | ≤ 2 | oracle |"

**Fix:** "| ≤ 0.5 ev/10 min | ≤ 1 ev/10 min | ≤ 2 ev/10 min | oracle |". Same defect at line 192's "median, share ≥ 3".

**M-16 · line 192 · two units for one quantity, no conversion.**
CLAUDE.md names this case in terms. **Fix:** add the frame interval and the seconds equivalent of ±2 frames to the header or a note under the table.

**M-17 · lines 66, 94, 102, 116 · "the second sensor" is never identified, and three names compete for possibly two things.**
The heading promises "What the second sensor buys". The page then speaks of "the count channel" (116), "**The orientation channels**" (117) — plural — and the ablation is "length only" (78).
**Fix:** state the two sensors once, in the heading's own paragraph. Then fix "channels" → "channel", or say why it is plural.
*Verifiable:* yes — `src/bugarach/learn/nets/line.py`.

**M-18 · line 118 · two numbers with no quantity and no connection to anything on the page.**
The ratios in the table above run 1.00–5.05. Nothing on the page is near 18.5.
**Fix:** "…the per-field spread of the raw line score is ±4.4 on a mean of 18.5 (arbitrary model units, which is why only ratios are shown)".
*Verifiable:* yes — `probe/line_vs_fuzz.json`.

**M-19 · redundancy across three sections — the same four numbers stated three times.**
Lines 51–57, 92–95, and the *What waits on Tony* item at 245–248 each carry: F1 0.713 vs 0.655, recall 0.750 → 0.933, probe firings 1.25 → 5.50, and the fit-time factor.
**Fix:** the decision item keeps the framing and drops the numbers, pointing at Figure 1 by number and name. Same treatment for the third statement of "the objective pays for any separation" (61–62, 229, 253–254).
*Verifiable:* yes — on this page.

**M-20 · line 227 · a bullet that asserts two incompatible things.**
> "**Each label-free row is one of two displacements**, and the table now shows both."

If each row is one displacement and the table shows both, nothing is unsettled — this bullet is in a section called *What this does not settle*. "now" refers to a revision the reader never saw.
**Fix:** delete the bullet, or state the residual limitation it was meant to carry.

**M-21 · line 216 · "inverted" and "backwards" say the same thing and neither says which way it now points.**
**Fix:** "⚠ **Events concentrate at window edges; the earlier version of this page reported the opposite.**"

**M-22 · line 122–123 · a sentence that contradicts its own premise.**
If the encoder *sorts* rows, row order is not unread — it is replaced.
**Fix:** "…so the diagonal a person sees in a raster is a fact about the **display's** row order, which the encoder discards before the model sees anything."

**M-23 · line 180 · "unplanted twins" is undefined jargon carrying a whole result.**

**M-24 · lines 186, 133 · "baselines" will be read as "reference scores".**
**Fix:** "All 84 lab fast-stream **baseline recordings**…".

**M-25 · line 44 · "participation" is an undefined internal quantity.**

**M-26 · line 204 · a code parameter standing in for a reader-facing statement.**
**Fix:** "they refuse to call any event with fewer than 4 ROIs, so their 1.00 is a floor, not a finding."

**M-27 · lines 233–236 · "that number" is ambiguous, and two denominators are irreconcilable.**
Three populations named "slices": 84, 47, 85. Separately, the null here is a **circular** shift, while line 25 states the rigid shift used in this run explicitly does **not** wrap.

### Minor

**m-28 · line 1 · the title promises the opposite of the finding.** The page's headline result is line 59: "**Training on rigid shift alone did not work**". **Fix:** "# Rigid shift as a teacher: what it destroys, and why training on it alone did not work".

**m-29 · lines 23, 39 · payload-last blocks; promote, don't trim.**

**m-30 · line 48 · a bare enumerated back-reference.** "the second decision below" → "the **shared-modulation decision** below."

**m-31 · lines 168, 170 · figures referenced with neither number nor name.**

**m-32 · line 178 · Panel C with no Panel A or B in its own figure.**

**m-33 · lines 73 vs 141 · one symbol, two definitions, no explanation** (sample vs population SD).

**m-34 · line 102–106 · "plant" used before it is defined, and its size given without a unit.**

**m-35 · line 104 · a term defined and then never used** — fuzz.

**m-36 · line 107 · the same statement twice in one sentence.**

**m-37 · line 60 · a redundant aside.**

**m-38 · line 63–64 · an inference stated as a fact**, where the same claim is correctly hedged 120 lines later. **Fix:** "so most of the **score** these models earn needs no cross-ROI structure at all."

**m-39 · line 56 · "fires … firings".**

**m-40 · lines 54, 153, 173, 209 · "where" used four times for "whereas".**

**m-41 · line 173 · a fractional count beside integers, unexplained.**

**m-42 · line 174 · two numbers, no quantity, no explanation of why there are two.**

**m-43 · line 208 · a share test reported as an equality** — the column is "share ≥ 3".

**m-44 · line 211 · a claim the table cannot support** — catch rates given for two of four.

**m-45 · line 55 · elliptical.**

**m-46 · line 218 · undefined jargon introduced once, at the point of a result** (difference-of-Gaussians).

**m-47 · line 230–232 · Latin where English is shorter** ("ceteris paribus"), and "samples" as a third unit for the time axis with no conversion.

**m-48 · lines 240, 278 · relative times that rot** ("a day old", "hours earlier").

**m-49 · line 254–255 · a verb with no object** ("which pooling rules localise").

**m-50 · line 256 · "the tables" unnamed.**

**m-51 · line 261 vs the table at 266–273 · "four stages", six rows.**

**m-52 · line 264 · dangling relative** ("which it should be").

**m-53 · line 283–284 · ambiguous antecedent.**

**m-54 · lines 17–18 · tense mismatch and the same point twice.**

**m-55 · lines 11–12, 209 · the event's timescale is defined vaguely at the front and precisely at the back.**

**m-56 · line 19 · "onset train" used before "onset" is defined.**

**m-57 · line 83, 88 · names that mislead** — `tiny` has **2,393 parameters**, more than every other model in the table.

**m-58 · line 72 · the prose claims a grouping the table does not show.**

**m-59 · line 98–99 · "two open defects" that a reader cannot find.**

**m-60 · line 49 · an unlinked document**, in a page where everything else is linked.

**m-61 · line 94 · a count that needs "more"** — "for 72 **extra** parameters".

**m-62 · line 166–167 · a label where the consequence would serve.**

**m-63 · line 190 · a ceiling that is not what you measure against.**

**m-64 · line 238 · an unnamed file.**

**m-65 · line 121, 124 · two terms for one concept, one sentence apart.**

**m-66 · line 104 · article inconsistency in a definition list.**

---

## Boundary notes

- Whether the two PNGs render their axes, labels and units correctly is **role 10's**; I read only the Markdown. Findings C-2, M-13, M-15, M-16, m-34 and m-47 concern the *prose and tables* and may have counterparts in the figures.
- Whether the sections sit in the right order is **role 11's**.
- Whether the numbers are true against the shipped folders is **role 4's**. I checked only internal arithmetic: 1,305 − 1,233 = 72 ✓, 0.713 − 0.655 = 0.058 ✓, 0.81 − 0.64 = 0.17 ✓, 4 × 3 × 4 × 4 + 48 + 48 = 288 ✓.
