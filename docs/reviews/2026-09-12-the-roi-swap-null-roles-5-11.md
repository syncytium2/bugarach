# Murderboard on the ROI-swap proposal — roles 5-11

> Companion to [roles 1-4](2026-09-12-the-roi-swap-null-roles-1-4.md). Same artifact, same caveats:
> landed as each report arrived, scrubbed only for absolute paths, and **the final message of each
> role is the authoritative one** — do not grep these transcripts for a grant line.

---

## Role 5 — Line editor, "Kill Your Darlings" (`murderboard-kill-your-darlings`)

**GRANT 5 ok — Read, Grep, Glob.**

⚠ **A gap in this review, declared.** The role's checklist requires `murderboard_prose.sh` and
requires its output pasted. **The tool is not vendored in this repo** and the role held no Bash, so
it could not have been run. Block word counts below are hand-derived and approximate — which is
exactly the unverified prose answer the architecture note warns about. *Worth a todo: vendor the
tool, or the role runs half-blind every time.*

### Mechanical search

Banned constructions — six instances of the *"not X; it is Y"* form: lines 23, 26, 160, 247, 276,
329. "Robust" at line 131 is **not a defect** — it reports Stella's own language.

British spellings against the repo's American-English rule: `modelling` (23), `binarisation` (162),
`artefact` (209, 212), `centre-surround` (288), `memorise`/`memorises` (312, 336). **Line 288 is the
one that matters** — `writing_conventions.md` already logs `centre-surround` as named drift against
`nets.py`'s own `center-surround`.

### C1 (critical) — "preparation" carries two referents, and the whole leak argument rests on it

The goal section means *this kind of experiment*; the proposal section means *one individual slice*.
The design's single load-bearing risk is named with the word in its second sense while the reader
met it in the first. **GLOSSARY already owns a word for the second sense: `slice`.** The document
additionally uses *recording*, *session*, *mouse* and *slice* alongside it without ever saying how
they nest — which is what the matching ladder is made of.

### C2 (critical) — the construction never says whether the k swapped ROIs come from one donor or k donors

If all k come from **one** donor slice, the swapped-in ROIs are mutually coordinated **with each
other** and the chimera contains real coordination in its negative class — the near-real negative
the document's own mixing section identifies as fatal. If from **k different** donors, heterogeneity
is maximised. **The two designs have opposite failure modes and the plan's expected results differ
under each.**

### C3 (critical) — the precondition stage's STOP is conditioned on the stage after it, which the ordering rule forbids. As written the gate is unevaluable.

### C4 (critical) — "operating point" is a reserved GLOSSARY term used for something else

GLOSSARY gives it a specific owner: *"a detector setting that was **chosen**, carrying the provenance
of the choice"* (`bench.OPERATING_POINTS`). A matching level is not a detector setting. Second defect
in the same sentence: "**at least one** matching level … **That** level" — if two qualify, which?

### H1 — "band statistic" is the first technical term the reader meets, is load-bearing, and is defined nowhere in the tree.
### H2 — the main test's training design reads two ways: the first clause fixes the negative class at k=N, the second varies k/N over four values.
### H3 — "identical marginal distributions" never says over what population. What is identical is the *pooled* distribution, and only if donors come from the same corpus.
### H4 — "window-matched" is undefined, and "window" already means four things (543 analysis windows, the pairing spec, the rigid-shift edge, GLOSSARY's region window).
### H5 — **thirteen bare enumerated cross-references**, against an explicit repo rule and the global rule.

**Not violations — the five stage headings.** Each pairs the ordinal with a descriptive name *at the
point it is defined*, which is what the convention prescribes, and the ordinal carries real content
because the stages must run in order. **Also not a violation: FOUNDATIONS §9** — a citation into an
external authority, in the form the convention allows.

**Violations — every back-reference by bare number.** The document did the hard part (it named each
stage) and then never uses the names. Worst case: *"filed as **item 4** of [the handoff todo]"*,
which sends the reader into another file to count list items. Plus five internal `§` references.

### H6 — "the plan is again the only authority for what was run" has no antecedent: which plan, and "again" refers to an event the reader has not been told about.

### Medium

M1 "the sharpest possible form of leak" — an unfalsifiable superlative sitting where the document's
own checkable term (**support violation**) belongs · M2 "This stage cannot succeed and is therefore
worth running" **contradicts its own gate** two lines above ("GO on chance" — chance *is* success) ·
M3 "the whole design's cheapest kill shot" is both overreach and a restatement of the preamble, and
is false anyway since the precondition recovery costs no compute · M4 "unbuyable afterwards" is a
price metaphor standing where the argument should be · M5 the status banner and the closing section
are the same paragraph twice (~140 words for ~70 of content) · M6 "Every stage emits its figure"
contradicted by three of five · M7 a three-row table followed by a claim about nineteen rows, with
no "excerpt" marker · M8 "that same flag" compresses a test result, a machine-readable void code and
a count into one clause · M9 "probe numbers used where production numbers existed" uses two
undefined terms to explain a withdrawal · M10 the leak-shape paragraph repeats the paragraph above
it with one number added · M11 "the single objection on which the design stands or falls" is
contradicted by the document's own closing section, which raises two more · M12 "the DC-free kernel
never reaches" has three readings and the ablation's rationale depends on which · M13 "figure" means
both *number* and *image* · M14 "bears on every 'no leak detected' below" points backwards.

### Passage test

Blocks that **earn their length**: the mixing section (290 w — the evidence a skeptic demands), the
literature section (330 w, four distinct payloads), the side quest's condition table.
Blocks to cut: the blind-control section (60 → 40 w), the arithmetic stage's closing (35 w, two of
three clauses are the preamble again), the construction-validity closing (**cut entirely** — false
and self-contradicting).

**Payload position.** The document mostly promotes payloads correctly. The two exceptions are the
goal section (payload is the last sentence — *"Get the surrogate wrong and the detector answers a
question nobody asked"*, the best sentence in the document) and the risk section (payload split
across two paragraphs). **Promoting those two is a bigger improvement than every cut above
combined.**

### Glossary compliance — clean where it matters most

No "modality" anywhere. "stream" used correctly throughout. The two collisions are **"operating
point"** (a direct hit on a reserved term) and **"preparation"** (a fifth word for an object the
glossary already names `slice`).

---

## Role 7 — Reuse auditor, "Reinventing the Wheel" (`murderboard-reinventing-the-wheel`)

**GRANT 7 ok — Read, Grep, Glob, Bash.**

### 1 (critical) — the precondition stage proposes to re-derive from archives a fact written in two files it already cites

`negative_control_pairs` is that construction and its docstring states the answer outright.
`tools/probe_discriminator.py:138` re-drives it, and the build-agents review **in the plan's own
worktree** says *"Negative control: consecutive real windows of the same recording."* The only live
question is whether the transcript-only workflow script called that function or rolled its own —
answerable by re-running `probe_discriminator.py`, which is cheaper than reading transcripts.

### 2 (high) — the reused component is misdescribed, and its stop rule would fire on the design's own predicted leak

`pool_symmetric` uses `POOL_STATS = ("mean", "sd", "min", "median", "max")` per per-ROI column, so
**`sd_count` is the across-ROI spread of per-ROI rate** — precisely what the arithmetic stage
proposes to measure. The two stages are nearly the same measurement on nearly the same quantities,
presented as independent tests with independent verdicts.

### 3 (high) — the training loop does not exist and the phrasing implies it does

`learn/train.py::train` is a **supervised per-frame BCE trainer on generated recordings**:
`make_recording` is `seed -> (slice, ground_truth)`, targets from `frame_targets`, threshold picked
on a disjoint *seed block* of more generated data. **No window-level label, no real-data path, no
paired objective.** `fold_maker` splits generated seeds, not mice. Budget the main test as new code
plus compute, not as compute.

### 4 (high) — the ablation is not a switch

The bypass is hardcoded at `tube.py:152` and again at `:277`. Removing it changes the head's input
width, and ADR-0005 makes one file one architecture — so this is a **new registered net module**,
not an `arch_over` key.

### 5 (high) — four statistics re-derived, none named at its canonical definition

per-ROI **rate** is `bench.py:58-64` and `tools/make_roi_rate_distribution.py` already draws that
distribution against a reference, already defaulting to the darkroom · **burstiness** in this project
is the Fano factor of 60 s binned counts (`count_dispersion.fano`, `MIN_EVENTS_PER_ROI = 10`) — ⚠
and `count_dispersion` is **within-ROI over time despite its name**, not the across-ROI dispersion
wanted · **median ISI** exists as a discriminator feature but in **log1p of frames**, not seconds ·
**event width** is per-event in **whole frames** and present only when `has_width`.
⚠ `surrogate_stats.Summary` is deliberately **additive** and structurally cannot express across-ROI
dispersion — do not extend it.

### 6 (med-high) — the fold maker exists and the chimera breaks its contract

`mouse_folds` and `mouse_splits` need no building. **But both take one mouse label per unit**, and a
cross-mouse chimera has k+1 mice: a donor's mouse can sit in the training fold while the same mouse
appears as a target in the test fold. **Neither is expressible in the current signature.**

### 7 (med) — `correction_reach` exists and roughly does what the plan says, but is under-specified and pointed at the wrong stage

Signature `correction_reach(m, n_splits, K, *, alpha)`. The plan never mentions `K`, the draws per
cell — the other half of the answer and, at `2/(K+1)`, the binding one. Its test is **strict `<`** by
design, so a pre-registration landing on alpha buys nothing. And it is **not** the sizing tool for
the discriminator stages: that is `required_pairs` / `binomial_power`.

### 8 (med) — the report machinery is never named, so the plan is one session away from a third SVG kit

`tools/build_surrogate_report.py` already carries an inline-SVG kit, numbered figures, a page refused
if it contains no SVG, and a render gate. Two real obstacles worth stating: the kit lives inside a
tool rather than a module, and the tool hardcodes `OUT_DIRNAME` plus fixed `CANDIDATES`/`CONTROLS`
name lists — an ROI swap is in neither. Also `src/bugarach/time_axis.py` for the 60-base rule, and
SAP006 for `--out`/`--also`.

### 9 (med) — group metadata already loads. `recordings_from_slices` fills `.mouse` from `subject_id` and `.group` from `group_id`; `io.py:460 SUBJECT_ALIASES` canonicalises the spelling. Two gaps: `group_id` is **optional** in the contract, and ungrouped recordings need a convention (existing tools chose `"UNGROUPED"`).

### 10 (med) — the builder is genuinely new (nothing in `surrogates.py` substitutes ROIs; `git grep -i "chimera|donor|roi.swap"` is empty) but the plan does not commit to the interface it must match: `generate(name, trains, window, key, **params) -> SurrogateResult`, **every parameter in frames**, seeds via `zlib.crc32` into `RandomState` (SAP002 bans `default_rng` in `src/`). `generate` is strict — an unknown parameter is a `TypeError` — and the key `(recording_id, stream, cell_id, draw)` **has no slot for donor identity**.

### 11 (low-med) — representation gap: the surrogate side speaks `RecordingTrains` (frames), `tube` speaks `Slice` through `encode` (seconds). Two `encode` behaviours bear on a chimera and go unmentioned: rows are **sorted busiest-first**, so donor ROIs are re-ranked and ROI identity is already unavailable — a second, structural support for the side quest's argument; and `encode` **clips out-of-range onsets onto frames 0 and n−1**. The swap displaces nothing, so it should never fire — **which is an assertable property of the builder**, of exactly the kind the proposal makes about the ISI floor.

### 12 (low) — `learn/checkpoint.py` already persists a fit as JSON and `bugarach detect --model` runs it from a separate process. A multi-seed run produces the artifacts that facility exists for.

### 13 (med) — everything the plan calls "existing" is on an unmerged branch, and **`docs/INDEX.md` contains zero rows** matching `surrogate_stats`, `count_dispersion`, `build_surrogate_screen` or `surrogate_discriminator`. CLAUDE.md sends the next session to the index first; it will come back empty and re-derive — the failure the index was created for.

---

## Role 8 — Naive-reader accessibility, "You Lost Me" (`murderboard-you-lost-me`)

**GRANT 8 ok — Read, Grep, Glob.** Read cold; opened no linked file, no CSV, no FOUNDATIONS — *"a
proposal that needs them to be followed is itself the finding."*

**Every section except the literature review and the side quest crosses the three-undefined-terms
line.** Thirteen undefined terms appear **before the first section**.

### Blocking

**B1** — *"The detector falls out of the discriminator."* The entire premise is one clause. A
discriminator scores *a window*; a detector emits *event times*. Nothing bridges them, and no
stage's success criterion is stated in detector terms. **I finished the document not knowing whether
the plan, if every stage passed, would have produced a detector.**

**B2** — `tube` is never defined. It is the only thing trained, named eleven times, and its
properties carry three separate arguments.

**B3** — "fast stream" / "slow stream" never defined. They partition every table, carry different
floors, and the design's viability hinges on "the stream that matters most" without saying which.

**B4** — "J" is a table column 100 lines before its only hint.

**B5** — "the screen" supplies most of the document's numbers and is never defined.

**B6** — the unit hierarchy (session / mouse / group / recording) is never stated **and the design is
built on it**. The tightest rung is "within-session", whose failure triggers the design-killing STOP.

**B7** — eight project-local nouns used as if shared: the export folder, `steps_excluded`, `cossart`,
"the night", the darkroom, board block 065, the harness archives, transcript-only.

**B8** — **"the floor" means three different things** (chance level, interval bound, worst-case
control), and the undefined senses appear *before* the defined one.

**B9** — **"cell" means both a neuron and a table entry within a single paragraph** — in the
paragraph whose whole job is to distinguish two granularities.

**B10** — "destruction" is a measured quantity that is never defined, and "coordination is destroyed
equally at every level" is the premise the entire main measurement rests on.

**B11** — "the outside read" is an unattributed authority supplying three claims.

**B12** — **no success criterion is computable anywhere in the plan.** Not one of the four gates could
be adjudicated by two readers to the same answer — in a document whose stated purpose is to
pre-declare stop-or-go.

**B13** — **the plan is not executable from this document.** Missing: how ROIs are chosen for swapping
(matching on rate would change the cheapest stage's entire prediction); what a window is and where
543 came from; how baseline segments are identified in donors; how many chimeras per target; the
train/test split for the main test; which model is "the existing per-ROI-only discriminator"; the
dataset's size; where figures are written.

### Major

**M1** — the planned headline figure is a false friend: a connected line with slope and intercept
called out is the grammar of a regression, but x is four nominal pools whose spacing is undefined.
**A fluent reader will read a slope off that chart and believe it means something.** Worse, accuracy
(unitless) and dispersion (Hz) share one panel.
**M2** — bare enumerated labels throughout; each stage already has a real name in its own heading.
**M3** — relative words with no referent: "ORX up" in *what measure*? "the stream that matters most"?
"surviving out to 1.6 s" — surviving what?
**M4** — the withdrawn-drafts section cannot be learned from, by the audience most likely to repeat it.
**M5** — the dose axis's purpose arrives 100 lines after the dose axis.
**M6** — the precondition paragraph is where the argument jumps hardest: seven new objects in thirteen
lines.
**M7** — "surrogate" is characterised (well) but never *defined* as a constructed object.

### Minor

m1 a six-item list smuggled into a sentence · m2 table header says "real share sub-floor", prose says
`real_share` · m3 three-row table, "nineteen rows" · m4 "binarisation" appears from nowhere · m5
internal identifiers in audience-facing prose, worst case `surrogate_stats.correction_reach` — *"the
one action item in the document's free-opportunity paragraph is inert"* · m6 **no mechanism is
introduced graphically**; the two scheduled figures are both results figures, there is no
explanatory one · m7 five consecutive paragraphs opening with a bold phrase flattens emphasis so the
genuinely load-bearing sentence does not stand out.

### Where the document is strong

The support-violation / soft-difference split, the placement in the shift-predictor lineage, the
statement of why every train being real makes the prior failure unavailable, and the side quest's
three-condition table **all survive a cold read intact.** The gaps are almost entirely vocabulary and
executability, not reasoning.

---

## Role 9 — Density & figure-first, "Show, Don't Tell" (`murderboard-show-dont-tell`)

**GRANT 9 ok — Read, Grep, Glob, Bash.** Unit of analysis is the **section**, not the slide — this is
flowing Markdown with no page geometry, so the canvas-share measurement does not apply and
figures-per-section is substituted.

**Zero figures in 3,242 words**, in a document that says of itself *"Every stage emits its figure
before its prose."* The sibling proposal also carries zero — **this is the thread's habit, not one
lapse.**

Sections over 250 words with no figure: the goal (283), the literature review (328), **the proposal
(503)**, the side quest (334), the closing (306). Longest unbroken prose blocks: 119 (the main test),
102 (twice).

### Critical

**1** — the construction the whole document is about is **100% prose. Nothing shows a chimera.**
**2** — an already-measured visual finding, sitting in a CSV on disk, described in prose plus a
three-row range-string excerpt of an eighteen-row table. **This is the repo rule's literal case.**
**3** — **the stop-or-go gate is written in a unit the specified figure cannot produce.** "Slope" over
an ordinal ladder with undefined spacing is not a number.

### The figures, specified

**`explain_swap`** — three stacked black-and-white rasters, shared time axis, 60-base ticks, x axis
on the bottom panel only. y-labels `target · 30 ROI`, `donor pool · 4 recordings`,
`chimera k/N 0.5 · 15 swapped`. **Provenance is a per-row property, not a per-time one, so it cannot
go in a lane above** — a down-triangle would point at a *time*, not a row. Put it in the **left
gutter, outside the plot area**: a thin colour swatch column, one colour per source recording. The
raster stays black and white and identity goes where the conventions already put it. *What the
reader sees in two seconds: the chimera's rows are literally the same rows, unmoved — only the
gutter colour changes. That is the entire support-subset argument.* Hold the raster in a variable
named `raster` so SAP009 can see it.

**`explain_floor`** — three panels, shared log x = within-ROI interval (s). Dither: real density
filled with its hard left edge, dithered outline with mass to the left, region shaded, vertical rule
at `0.40s`/`3.20s`. Mixing: the same region at m = 1, 2, 4 — **the shaded mass gets shorter and the
left edge never moves.** ROI swap: one curve, **the panel is deliberately empty and its emptiness is
the argument.**

**`leak_screen_rows`** — two panels sharing 18 rows grouped stream × J. Left: leak AUC with sd
whiskers, rule at 0.5. Right: real and dithered share on the same row. *What the current three-row
range table actively hides: every real mark pinned exactly on zero, eighteen times, and policy and
time-base making essentially no difference.*

**`dispersion_ladder`** — the document's version **would not render**: dispersion is a scalar but "the
real distribution as a band" treats it as a distribution; the statistic is unnamed; no units; it
draws one of the four statistics the stage computes; and "one panel per matching level" implies
per-panel titles, which the conventions forbid. Replace with rows = statistic, one x axis of matching
level on the bottom row only, band = 5th–95th percentile over real recordings — **and that definition
must be written into the document, because the GO gate reads off it.**

**`accuracy_vs_dispersion`** — **is a line over a nominal axis legitimate?** Partly. The ladder is
ordinal and **nested**, so connecting points is defensible. What is not legitimate is the word
**slope**: the run is undefined. Preferred fix — **make the x axis metric**: plot accuracy against
the measured dispersion itself. Slope then means *accuracy per unit dispersion*, and the prediction
stops being decorative and becomes a reference line. Fallback — keep the ordinal axis and report
`accuracy(global) − accuracy(within-session)` as a **range**, never a slope.
Add the transpose **`accuracy_vs_dose`** (x = k/N, metric): the document's own headline prediction is
about that axis and is invisible on the panel it specified. Both panels: **each seed as a thin line
with the mean heavy**, not a mean with an error bar — the ablation's own note is the reason.

**`chimera_marginals`** — the stage's only possible outcome is catching our own error, so the figure
must make the **failure** legible: on a pass the reader sees one curve where there should be two; on
a bug, *which* panel separates names the bug (width → resampling, rate → donor pool not baseline-only,
count → duration mismatch).

**`bright_ablation`** — paired slopegraph, one line per seed per matching level, drawn individually.

**`group_confusion`** — three 4×4 matrices, shared colour scale. *"Accuracy collapses" is not the
interesting result; which pair of groups stops being separable is, and only the matrix says it.*

### Tables

Should be a table: the surrogate placement table (**an empty cell is the only way to actually show an
absence** — prose can only assert one); a one-screen stage summary **as an addition, not a
replacement**; an open-items table with a "blocks" column. Should stay prose: the three properties of
the preparation — each carries a mechanism *and* a forward consequence, and a table would strip the
link.

### Two things worth saying plainly

**The document is a plan, and that excuses the stage figures — it does not excuse the rest.** The
construction schematic, the support diagram and the leak screen are **all renderable today**. Those
three are the repo rule's literal case, and shipping without them is the 2026-08-13 failure: the text
arrives, the evidence does not.

**The strongest defect here is not a missing picture, it is a decision rule in an impossible unit** —
and it is the one finding that would still bite if every figure were drawn.

---

## Role 10 — Build & craft gate, "Ship It" (`murderboard-ship-it`)

**GRANT 10 ok — Read, Grep, Glob, Bash.**

### Gates, verbatim

```
python3 tools/sapper.py --all        -> sapper: clear          EXIT=0
python3 tools/check_quotes.py --all  -> check_quotes: clear     EXIT=0
pytest tests/test_index_resolves.py  -> 206 passed in 0.06s
```

Full suite: `2 failed, 2340 passed, 46 skipped, 1 xfailed`. **Both failures are a harness artifact,
not a branch defect** — the venv is editable-installed against the primary checkout, so the test
writes its probe into the worktree package dir while imports resolve elsewhere. The same test passes
in the primary checkout (`4 passed`). CI builds per-checkout.

### Merge blockers

**1 (HIGH)** — the review link does not resolve; it exists only on `origin/surrogate-screen-overnight`
(`860e5ee`), and it is the sole support for the withdrawn-drafts section.
**2 (HIGH)** — "nineteen rows" → **18** data rows.
**3 (HIGH)** — **bugarach implements two distinct functions**: `surrogates.py:368 rigid_shift(…, J)`
and `surrogates.py:404 trial_shift(…, J, f)`, run as **separate candidates** in the screen.
`trial_shift`'s `f` is the pseudo-trial parameter that makes it TR-SHIFT. The document equates
`rigid shift` with TR-SHIFT; it should not. Also the span reads `rigid shift` where the identifier is
`rigid_shift`.

### Medium

**4** — leans on Stella's ranking against INDEX row 125, and does not link the todo that corrects it.
**5** — 0.307 → **0.306**.
**6** — `surrogate_stats.correction_reach` is on an unmerged branch; a reader on this branch cannot
find it.
**7** — 🛑 ✅ → ∈ are **not cp1252-encodable** (`{U+2192 ×3, U+2208 ×1, U+26A0 ×2, U+2705 ×5,
U+1F6D1 ×5}`), and the document says a session is live on the Windows workstation, which is where a
cp1252 console is. ⚠ is already repo convention and is fine.
**8** — **no INDEX row for this proposal.** Not caught by `test_index_resolves.py`, which checks
resolution, not coverage.
**9** — no `## Sources` section; the sibling proposal ends with one.

### Low

**10** — darkroom-relative paths with the root never stated; `reproduction/` also matches the SPAN
pointer regex, the known trap that has reddened the suite · **11** shelf PDFs cited without their
`surrogates/` prefix · **12** sixteen bare enumerated labels; the sibling proposal scores **0** on the
same grep · **13** a prose sentence inside a code span used as link text · **14** "columns
`floor_sec`" — one column · **15** Perkel cited with no shelf copy and no `lit_needed.md` entry ·
**16** the 1,261 hedge is closeable in one pass and closing it removes a caveat that currently
weakens the closing section.

### Checked and clean

All three tables parse (5/5/5/5/5, 4/4/4/4, 4/4/4/4/4). No heading-level skips. Emphasis balanced.
Valid UTF-8, no BOM, no CRLF, no trailing whitespace, final newline, **zero mojibake**. The locale
trap did not fire — the risk here is cp1252 *printing*, not decoding. Numbers verified exact:
`real_vs_real` both streams; **126 of 248** (my first count of 142 wrongly included the 16 control
rows); 326/218 and 106/99; floors; 543 windows. FOUNDATIONS §9 confirmed at lines 327 and 370–371.
tube claims confirmed. Board block 065 confirmed. Four of five relative links resolve; all eight
internal `§` references resolve.

---

## Role 11 — Argument order, "Start With the Problem" (`murderboard-start-with-the-problem`)

**GRANT 11 ok — Read, Grep, Glob.**

The arc judged against, for a *proposal that requests resources*: **the decision being asked for →
the problem, shown → why the current approach fails → the proposed fix → why it cannot fail the same
way → what it costs and how we learn cheaply → residual risk.** A proposal has a reader who must act,
so the ask brackets the case rather than trailing it.

### High

**A** — **the decision the reader must make is never stated.** Tony must decide whether to spend
workstation compute, and no sentence says what he is being asked to approve. The plan has stop-or-go
gates *inside* it; the document has no gate *on* it.
**B** — **the cost, and the fact that it is almost zero, arrive last.** "Stages 0–2 need no compute
worth naming" and "the cheapest test that can kill the design runs first" are both true, both
excellent, and both sit where a reader deciding whether to fund has already decided. **The document
hides its own easiest yes.**
**C** — the non-decision banner precedes the proposal and duplicates the closing section near-verbatim.
At position zero the reader cannot evaluate any of it — "it does not prune any candidate" is
unintelligible before the proposal exists.
**D** — **the literature section interrupts.** Its job is *support for the proposal*, so the reader
must reverse-engineer the proposal from its own precedent. It also breaks the document's tightest
transition: the failure case ends and the fix should begin.
**E** — one part of it genuinely belongs *before* the proposal and is the exception: **rigid shift is
the incumbent**, and a reader will ask "why not just use that?" before hearing about chimeras.
Bundling the competing-alternative beat with the precedent beat forces the whole section into the
wrong slot.
**F** — **the strongest reason to act now is filed under "what this plan does not settle."**
Pre-registration being free now and unbuyable later is a time-sensitivity argument *for approving the
run* — an asset in the caveat bin.
**G** — **the strongest argument is buried at ~42%**: every train is a real train, so the null's
support is a subset, so the previous failure mode is unavailable by construction. It is the only
thing here that makes the last disaster non-repeatable.
**H** — cold open is on meta, then on the goal. The first substantive content is the aim; what the
problem *looks like* is at ~16%.
**K** — **the ending trails off into caveats and stops on housekeeping.** The final sentence of a
funding proposal is a board-claim instruction.

### Medium

**I** — the side quest lands between the main ask and its cost, and is a **second unpriced ask**.
**J** — the two pieces of it that bear on the main case sit at the very end of a section the
main-case reader has already been pulled away from.
**L** — a caveat that points the wrong way ("below" — nothing is below it).
**M** — the withdrawn-drafts note is provenance sitting inside the argument, interrupting a tight
three-beat failure case.
**N** — a failing precondition positioned as an afterthought; correct in dependency terms, wrong in
emphasis.
**O/P** — the interval floor is listed third of three and consumed immediately by the next section ·
the leak × destruction join is stated in three places and consumed by a stage that never mentions it.

### Recommended order

status (one line) → **the ask** *(new)* → what failed, shown → why this preparation makes surrogates
hard → the proposal → precedent → the precondition → the plan → residual risk → **cost and the
decision** → the side quest, priced, as a clearly-optional appendix.

**Net effect:** the reader currently meets three meta-blocks, a goal, four failures, a literature
review and a proposal before learning what they are being asked for, and meets the cost in the final
paragraph. Under the recommended order the document's two best facts — the failure mode is
unavailable by construction, and the first three stages are free — do work at the top instead of
being discovered at 42% and 99%.
