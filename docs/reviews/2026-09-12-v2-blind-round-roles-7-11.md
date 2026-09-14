# Blind round on the v2 reevaluation — roles 7–11, as returned

Companion: [roles 1–6](2026-09-12-v2-blind-round-roles-1-6.md). Adjudication and verdict:
[the run record](2026-09-12-surrogate-screen-reevaluated_2026-09-12.md). Provenance of these
files, and the prompt every role received, are stated at the top of the companion.

**Artifact reviewed:** `docs/proposals/2026-09-12-surrogate-screen-reevaluated-v2.md` at `4b44e408`.

---

## Role 7 — Reuse auditor, "Reinventing the Wheel."

`GRANT 7 ok — Read, Grep, Glob, Bash`

Surface: the document, and the code that produced its numbers — `src/bugarach/{surrogates,
surrogate_stats,surrogate_discriminator,pattern_jitter,operational_time,count_dispersion,
time_axis}.py`, `tools/{build_surrogate_screen,build_surrogate_report,probe_discriminator}.py` —
against the production code they could have called (`assess.py`, `assess_folder.py`, `simulate.py`,
`detectors/rate.py`, `assembly.py`, `tools/assembly_power.py`, `tools/sampling_floor.py`,
`ui/app.py`) and against Elephant 1.2.1.

| # | issue | sev |
|---|---|---|
| 7.1 | **One stated rule, two implementations that disagree.** Both docstrings (`surrogates.py:596-606`, `:635-638`) say the window is √2·J, "the RMS rule", but `interval_jitter_bin` computes `round(√2·J)` while `window_shuffle_width` computes `2·round(J/√2)`. These differ on **5 of 6 fast radii, 2 of 6 slow, 5 of 6 Cossart** (J=1: bin 1 vs window 2; J=2: 3 vs 2 — **the window is narrower at twice the radius**; J=16: 23 vs 22; J=32: 45 vs 46). The screen compares candidates *at matched J*, so two candidates labelled with the same radius were run at different effective radii. `tests/test_surrogates.py:444-453` asserts both values, so the suite blesses the divergence. Step 3 proposes re-spending at exactly these radii | **major** |
| 7.2 | `pattern_jitter` (`:690`) re-derives `interval_jitter_bin`'s body inline — a third copy of the same conversion, and the mechanism by which 7.1 spreads | minor |
| 7.3 | **The reference's own default was the answer.** Elephant's `JointISI` has no bin-width argument — it derives `bin_width = truncation_limit / n_bins`, whose shipped defaults (100 ms / 100) give **exactly the 1 ms the document cites Stella for**. The adapter (`surrogates.py:500`) invents a J-linked rule instead. Step 1 is right that the width is wrong, but framing the fix as "Stella bin at 1 ms" hides that the implementation being wrapped already defaults there | minor |
| 7.4 | **Reuse is right, the re-parameterisation is undisclosed and the denominator is wrong.** `coact_excess` (`surrogate_stats.py:1175-1195`) correctly calls production `assess.assess_coactivity` — but at `n_surrogates=200` (`steps_excluded`) and `20` (Cossart) against the shipped default **1000**, which `assess.py:397-399` calls "the MATLAB default and what the reference numbers were produced at". The document says Cossart's 20 is "a tenth of the shipped ensemble": 20/1000 is a **fiftieth**; it is a tenth of `steps_excluded`'s 200. And the caution is scoped to Cossart only, so a reader takes the main destruction table as produced at the shipped ensemble when it too is a **fifth** of it | **major** |
| 7.5 | **The keystone arithmetic exists twice.** `build_surrogate_report.yardstick_reach` (`:396-460`) recomputes `band_floor`, `paired_floor` and both `*_holm` products inline, while `surrogate_stats.correction_reach` exists for exactly this and is what `build_surrogate_screen.py:823` calls. The same function already imports `smallest_n` from `surrogate_stats` (`:65`, with a comment saying the formula is imported rather than restated) — so the boundary-sensitive half is shared and the floors are copied. The copy also feeds itself different inputs (median `n_splits` over yardstick rows, `max` K over cells). Currently reproduces exactly, so drift risk rather than present error | moderate |
| 7.6 | **A value re-declared in the consumer that the producer already wrote into the file being read.** Both saturation functions (`:603`, `:639`) hardcode `recruited = 0.5 * n_roi`, while the dict they read three other fields from — `meta["streams"][<stream>]["destruction_twins"]` — records `"participation": [0.2, 0.5]` in both production `meta.json` files, and `surrogate_stats.DESTRUCTION_PARTICIPATION` owns the constant. The document lists this as a design residual rather than a one-line fix | moderate |
| 7.7 | The provenance row names four modules but **not `tools/build_surrogate_report.py`**, which computes the saturation numbers, the coverage figures and the reach box the document reports | moderate |
| 7.8 | Another private Playwright screenshot helper (`shoot_figures`, `:2196-2225`). `docs/todo/2026-08-18-render-png-duplicated-across-figure-tools.md` is **open**, names three copies and asks for one shared helper; the tree now has **19** tools calling `sync_playwright`, and this branch added one more | minor |
| 7.9 | `tools/assembly_pensub_compare.py:100-101` carries the comment "No SciPy — this repo does not depend on it." That is false (`pyproject.toml` requires `scipy>=1.11`) and is now contradicted by `surrogate_discriminator.binomial_power` | minor |
| 7.10 | `assess_folder.generation_window`'s extraction note says the screen now shares the window rule "rather than a sixth copy of it. The five older copies in `tools/` are left for their own change." Every per-scope number rests on that rule and five divergent copies remain | minor |

**Checked and clean, recorded so the surface shows as examined:**
- **The assessor's null is genuinely reused, not copied** — `assess.circular_shift_trains` was
  factored out of `assess_coactivity` and both `surrogates.circular_shift` and
  `window_circular_shift` call it (`:351-365`, `:827-847`). That is what makes "the circular shift
  *is* the assessor's own null" true in code rather than by assertion.
- **Elephant's histogram re-implementation matches the reference.** `_float_smoothed_histogram`
  (`:443-470`) reproduces Elephant's order exactly — histogram/outer product → `sqrt` →
  cutoff-limited `gaussian_filter`, same `_isi_to_index(refractory_period)` start index, same
  zeroing. The monkeypatch is an instance attribute and Elephant calls `self.joint_isi_histogram()`
  (`spike_train_surrogates.py:1083`), so it takes effect. **The square-root claim is correct against
  the source**: `sqrt` at `:995-996`, before smoothing at `:998-1009` and before
  `_normalize_cumulative_distribution`, which is affine and cannot undo it.
- **`holm()` is not a reinvention** — no prior Holm in the tree (`assembly.py` does Bonferroni over
  two statistics), statsmodels is not a dependency, SciPy ships no Holm.
- **The discriminator's power machinery is not a duplicate of `tools/assembly_power.py`**, which
  does simulation-based rejection rates; `binomial_power`/`required_pairs`/`within_mouse_icc` are
  analytic and new. `probe_discriminator.py` imports rather than re-derives.
- Other reuse done right: `count_dispersion.py` extracted from `fit_background_shape.py`;
  `detectors/rate.train_rate` factored out of `event_rate`; `destruction_twins` calls
  `simulate.simulate_coordination` with an opt-in, default-off floor mode so existing seeds
  reproduce; `time_axis.py` a documented port of `ui/app.py:_time_axis_hook`, tested against BokehJS.
- `ks_distance` is hand-rolled where `scipy.stats.ks_2samp` exists, but it is the exact two-sample
  statistic on integer arrays with no p-value needed — defensible, not filed.
- `coact_excess` passes `region_min_sec=0.0`, overriding the assessor's shipped 900 s guard; twins
  run 1,200 s and ~1,490 s, so the guard would not have fired. No effect on any reported number.

---

## Role 8 — Naive-reader accessibility, "You Lost Me."

`GRANT 8 ok — Read, Grep, Glob`

Unit of analysis: the `##` section. "Defined here" means defined *in that section, at first use* —
the Terms table is section 5, so it does not rescue sections 1–4. **Eight of fourteen sections are
blocking for a cold reader.** Four fixes retire most of them: promote and expand Terms, split the
overloaded word *floor*, define the five generators and the discriminator's power vocabulary in
place, and stop using *cells* for grid points.

**Figure rows could not be exercised and that is itself the finding (F17):** the document contains
no image, no panel and no figure number, so the chart-idiom / false-friend check, the per-panel
"what a cold reader sees" sentence, and the panel-archetype label had nothing to run against.

| # | issue | sev |
|---|---|---|
| F1 | **"cells" means grid points here and neurons to this audience.** "A rerun of the cells the night dropped costs 53,432 core-hours", "47 of 144 slow cells", "23 sqrt/nosqrt cell pairs", "358 dropped cells" all parse first as neurons, in a document whose subject is cross-ROI coordination. This is the textual form of the false-friend defect: the familiar reading arrives before the definition does | **blocking** |
| F2 | **Terms arrives three sections after the terms do.** Sections 2–4 use cells, draws, radii, scope, *J* and reporting group before any is defined | **blocking** |
| F3 | **"Floor" carries four meanings** — smallest attainable *P*, the saturation ceiling, the coactivity floor *K*, and (in the glossary) the shortest within-ROI interval. The header "50%: floor 3 → 8" is undecodable | **blocking** |
| F4 | **The discriminator table's entire vocabulary is undefined**: ICC never expanded, and design effect, effective n, pairs, required mice, positive/negative control all arrive with no gloss — then the lead is asked to rule on this section. Separately, `events` appears as a third stream where the glossary declares exactly `fast` and `slow`, and no `events` literal exists in the cited `surrogate_discriminator.py` | **blocking** |
| F5 | **Five generator names, none defined**: do-nothing, freeze-half, homogeneous resample, circular shift, uniform dither. "19 draws and 200 assessor surrogates" puts two different surrogate counts in one sentence with no statement of how they differ. And the table shows **negative retention** (−0.016, −0.004) against a Terms entry declaring the range 1 = all kept, 0 = all removed | **blocking** |
| F6 | **"Tier" and "void" are never defined**, yet decision 3 asks whether "the fast discriminator tier comes back" | **blocking** |
| F7 | **joint-ISI is never expanded or explained**, yet decision 1 — the most expensive call in the document, up to 278,409 core-hours — is entirely about it. ISI is never spelled out either | **blocking** |
| F8 | **"its square-root axis is a no-op" is unintelligible cold** — the reader is told a claim is withdrawn before knowing what axis, of what quantity, applied by what | **blocking** |
| F9 | **Frames and seconds for the same quantity, no conversion.** *J* is "seconds on `steps_excluded`, frames on Cossart", and one line compares *J* = 16 frames against *J* = 0.8 s directly. The Cossart frame interval is per-session and stated nowhere this reader can reach | major |
| F10 | Bare numbers without units: "278,409 at the plan's 99", "at 259/519", "(Cossart: 40)", "7 → 7", and "0.0498 / 0.0499" with no key for which is band and which is paired | major |
| F11 | **Five unresolved referents**: "the plan", "the shipped report", "the shipped ensemble", "the shipped-dither radius", "the gate now refuses less". None named or linked, and *shipped* is relative with no stated referent | major |
| F12 | The cited review does not exist, and is given as bare text where every other row in the same table is a followable path | major |
| F13 | "The keystone is one candidate at one radius on one stream" — the only antecedent for *keystone* is the withdrawn draft this document replaces. The lead's most important residual is stated in a word whose meaning was deleted | major |
| F14 | Internal identifiers stand in for plain-language concepts: `steps_excluded` and `cossart` as dataset names, `coverage`, `scored_share`, `recruited = 0.5 * n_roi`, `stage2_*`. `steps_excluded` labels a whole dataset on every table and tells an outside reader nothing | major |
| F15 | "sizing for one is roughly 480 splits and 960 draws" — one *what*? | major |
| F16 | Unparseable: "Its 248 candidate rows carry a single distinct void reason, stamped on 126" — 248 rows, one reason, 126 stamps, no account of the other 122. Then the reader must work out unaided that the discovery run is one of the five seeds | major |
| F17 | **No figure anywhere**, while the document name-drops five generators, a Holm floor, a destruction test, a saturation ceiling and an ICC design effect. A mechanism introduced only in prose is exactly what this check exists to catch | major |
| F18 | Abbreviations unexpanded at first use for a public reader: ROI, ISI, ICC, *P*, α (never given its value), DI/MALE/ORX/OVX, and Elephant (named as an authority before the reader learns it is software) | minor |
| F19 | Sources is nine references run together in one paragraph with `·` separators — a list smuggled into prose | minor |
| F20 | Terms defines `twin`, which the document never uses again, while nine terms it does use go undefined | minor |
| F21 | Two names for one concept: "reporting group" and "scope" | minor |
| F22 | "The screen exists to find a replacement, and shortlists nothing by design" — a cold reader cannot tell whether this is a limitation confessed or a property claimed | minor |
| F23 | "which stays below the line either way" — *the line* is undefined; α after correction is meant | minor |
| F24 | The status contradicts itself: the header says "draft, unreviewed"; the last residual describes a document that *was* reviewed | minor |

---

## Role 9 — Density & figure-first, "Show, Don't Tell."

`GRANT 9 ok — Read, Grep, Glob, Bash`

Conventions adapted for a markdown report rather than a deck, and stated: unit is the `##` section
(14 of them); >40 words/slide scaled ~6x to **>250 words/section**; the >60-word single-block rule
kept unchanged, because that is about reading, not canvas; figure-share and margin rules **N/A** —
the document contains **zero** `![...]`, `<img>`, `<svg>` or `<figure>` elements, so figure share is
**0% in every section** and there is nothing whose bounding box could be mis-sized. A genuine N/A,
not a skip.

**Totals:** 2,310 words (1,234 in tables, 1,076 prose), 11 tables / 94 rows, **0 of 14 sections
carry a figure**. Sections over the block threshold: §1 (65 w), §7 (78), §9 (86), §10 (79, and 277 w
overall — the longest), §13 (70).

**Comparator, same run, same builder:** `report_steps_excluded.html` and `report_cossart.html` each
ship **5 numbered SVG figures**; `report_summary.html` ships 1. Nineteen markdown docs under `docs/`
already embed images and `tools/md_to_page.py` supports `<img>`. Figures in a markdown deliverable
are an established pattern here, not a new capability.

| # | issue | sev |
|---|---|---|
| 9.1 | **Zero figures across 14 sections and 2,310 words**, describing a run whose own shipped reports carry five numbered figures each, built by `tools/build_surrogate_report.py` (`fig_leak`, `fig_candidates`, `fig_windows`, `fig_flags`, `fig_destruction`). **This is the one artifact from the run with nothing to look at, and it is the one a decision gets made from.** Fix: embed at minimum three, reusing the existing builders — `fig_flags` and `fig_destruction` already consume exactly `stats.csv`/`destruction.csv`/`cells.csv` via `load_role()` + `candidate_rows()`; export with the existing `shoot_figures()` | **critical** |
| 9.2 | §9 Destruction is a **10-cell hand-typed slice of a 584-combination surface** (fast alone: 17 generators x up to 7 *J* x 4 *K* x 2 participation arms). Two *K* values and one *J* survive; **the *J* axis — the axis the whole screen is about — is invisible.** "no value at floor 8" typed five times in one column. Fix: retained-coordination heatmap, candidate x *J*, faceted by *K* ∈ {3,8} and participation ∈ {50%,20%}, with the missing arm as a **single hatched block with one legend entry** (all 123 rows at p0.2/K8 carry `planted_visible=False`, so the hole is real and one hatch states it once) | major |
| 9.3 | §7 Probe: five of six rows are **near-identical by construction** and the table's actual payload is a **cliff between 259/519 and 260/520**. A table is the worst way to show a discontinuity. Fix: plot smallest Holm-adjusted *P* per scope at the two sample sizes with the α = 0.05 line drawn; the 78-word ⚠ becomes the **caption**, which is exactly what a caption is for | major |
| 9.4 | §10 Discriminator: five rows **hand-picked from 677 candidate rows** carrying `icc`, `n_pairs`, `required_mice`, `n_mice`, `powered` each. The reader cannot see whether the five are typical or extreme, and the real claim — everything sits below the powered line — is a geometric fact rendered as arithmetic. Fix: required mice vs mice available, one point per control x stream, with y = x as the powered boundary | major |
| 9.5 | §6: the document's **bottom line** — Holm's floor x family size crosses α — delivered as two stacked arithmetic tables. Fix: attainable floor after Holm vs family size, α line, three labelled markers (as-run 65 · within-scope 13 · Cossart 11), plus a companion bar of splits/draws needed against what the night bought | moderate |
| 9.6 | The **cost/feasibility story is scattered as bare numbers across four sections**, and the reader must assemble the grid mentally to answer decision 1. Fully renderable: `cells.csv` carries `status` (ok 291 / intractable 239 for `steps_excluded`; 79/119 for `cossart`), `J`, `J_unit`, `seconds_per_roi_per_draw` and the per-cell projection in `why` | moderate |
| 9.7 | §5's mechanism is a **72-word prose block over the 60-word threshold**, and a schematic of it **already exists and already ships**: `fig_leak` ("a real-like raster, its uniform dither, the leak lane, the interval histogram"), Figure 1 in all three HTML reports from this very run. CLAUDE.md's "reuse them rather than describing what a figure would have shown" applies verbatim | moderate |
| 9.8 | Any figure added must be numbered and named — CLAUDE.md requires numbering "every figure, on every page that has one", with prose references carrying **number and name**. `figure(n, title, svg, caption)` in the builder already emits `Figure n. Title.`, so inheriting the numbering is free if the builders are reused. Also: *J*, *K*, τ are defined in §4 **before** first figure use — keep that ordering when figures land above it | moderate |
| 9.9 | **Five prose blocks over 60 words.** Four are ⚠ cautions and are **load-bearing — do not cut them**; they are precisely what the review earned. **Relocate, don't delete**: the ⚠ blocks in §7, §9, §10 become the captions for 9.3, 9.2 and 9.4 respectively. §13 Sources is a reference list smuggled into a paragraph — format it as a list. §1's 65-word block is the executive summary; leave it | minor |
| 9.10 | **Two runs of consecutive prose-only sections** — preamble + bottom line (184 w) opens with no visual, and Residual + Sources (296 w) closes the same way. Place Figure 1 or the floor-vs-α figure right after the bottom line. **The closing pair is where prose is correctly the medium** and is not flagged for conversion: eight distinct caveats with no shared axis, and a figure of unrelated caveats would be a worse artifact than the list | minor |

**Where prose is right, stated plainly:** §2 decisions, §3 provenance, §4 Terms, §8 corrections and
§11 next steps are correctly tables or prose — distinct, non-commensurable items with no shared
numeric axis. Charting them would be decoration. §12 Residual is correctly a list.

---

## Role 10 — Build & craft gate, "Ship It."

`GRANT 10 ok — Read, Grep, Glob, Bash`

Artifact 13,611 bytes, mtime 2026-09-12 08:09. **What renders here: nothing** — 0 image references,
0 `<img>` tags, 0 occurrences of the string "Figure", and no HTML/PDF build. So the figure-craft half
of the checklist is inapplicable, and the effort was redirected into the other half of the mandate:
checks decided by *running a script*, walking every number in the document's ten tables against the
two named runs. A number naming a row the file does not contain is the same defect as a dropped panel.

**26-row check table. Passes:** build is current (artifact newer than every input); markdown table
structure (5/2/2/7/4/5/2/3/9/4 columns, no ragged row); encoding UTF-8 no BOM, 11 non-ASCII glyphs
(a cp1252 console would crash, as the brief warns); commit `0dc6356` exists and the cited symbols are
in that tree; **repo gates all clear** — `sapper.py --all`, `check_quotes.py --all`,
`pytest tests/test_index_resolves.py` (196 passed); probe table all 25 cells exact; Holm floor table;
destruction table all 5 rows exact including −0.016 and the empty 20%/K=8 cells; core-hour totals
exactly 53,432 and 278,409, 312 priced / 46 unpriced of 358; ROI exclusion; cost ratios; radii and
saturation; the five-seed re-run; `sd.required_pairs()` returns 654; step-0's claim about the shipped
report holds; void-reason counts 248 / 1 / 126.

| # | issue | sev |
|---|---|---|
| F1 | `fast · negative` verdict "not flagged" — **the run says the opposite**: `real_vs_real` fast is `significant=True, p=0.035, accuracy 0.5385`, and that flag is the single void reason stamped on 126 fast candidates. The document contradicts itself, since a later line correctly makes this flag the cause of the voiding. The ⚠ gloss also fails — it *did* detect. **Decision 3 rests on this row** | **HIGH** |
| F2 | `slow · positive` row (ICC 0.109, effective n 332, 87 mice): **no control row in the run carries those values.** The run's slow positive control (`kind=control`, `homogeneous_resample`) is ICC 0.1397 / 107 mice; the designated `discriminator_control` positive (`uniform_dither`) spans 0.0368–0.1228. The only rows at ICC 0.109 / 87 are `isi_dither` **candidates** — so the table mixes a candidate into a column of controls | MED-HIGH |
| F3 | "differ on 5–7 of 13" — 23 pairs exact, but **no column reproduces 5–7**: `band_p` 3–7, `paired_p` 1–5, `real` 6–8, `delta` 9–13, `band_flag` 0–1, stable across tolerances 0 to 1e-3. Under the closest reading the range understates the spread at the low end. The withdrawal itself stands — `delta` differing on 9–13 is a stronger fact | MED |
| F4 | "roughly 480 splits and 960 draws" — by the document's own floor, one discordant split gives 13 x 2/(n+1); at n = 480 that is **0.0541 > α**. Smallest n that works is 519 (≈520). 960 draws is sound but over-provisioned (its reading: 780 suffices), so the pair is also internally inconsistent | MED |
| F5 | The cited review record **does not exist** — not in the worktree, not in the primary checkout, nowhere under `C:\Users\defazio\bugarach`. It is the "where every number comes from" row that sources the whole withdrawal, and withdrawn v1 cites the same missing path | MED |
| F6 | The five production files are **not** in `2026-09-11-surrogate-screen/`; they are in `steps_excluded/` and `cossart/` beneath it, and `discriminator.csv` sits in `discriminator/<folder>/`. A reader following the path lands on `report_*.html` and `run_summary.json` | MED |
| F7 | **No darkroom copy exists.** CLAUDE.md: "A report counts as output, and 'in the repo' is not delivered" — the one artifact written for a person to read is the only one they cannot open | MED |
| F8 | **Zero figures**, against "If a finding is visual, render it before writing about it" and "number every figure, on every page that has one". Ten tables carry destruction curves across two arms and four floors, a power table and Holm floors — all visual findings rendered as digits | MED-LOW |
| F9 | The 53,432 / 278,409 totals are exactly right, but **91% of the cost is Cossart** (48,799 core-h) and only 4,633 is `steps_excluded` — while decision 1 sets that total beside "It runs on 47 of 144 slow cells today", a `steps_excluded` fact. A reader prices the wrong folder. The projection also covers `isi_dither` and `joint_isi` jointly | MED-LOW |
| F10 | The column "smallest adjusted *P*" values `0.0498 / 0.0499` — the `/` pairing is never identified (it is band / paired, verified) | LOW |
| F11 | "47 of 144 slow cells… and 2 of 144 fast" — numerators exact, but **144 is not the number of slow cells** (there are 265 per stream, 249 candidates). 144 is the count of cells carrying the square-root axis (`isi_dither` 72 + `joint_isi` 72). The denominator is undefined in the text | LOW |
| F12 | ICC, design effect, effective n, DI/MALE/ORX/OVX, α and τ undefined at first use, despite a Terms table that defines easier things | LOW |
| F13 | "not comparable with the table above" — a spatial reference to an unnumbered table; **no table in the document is numbered or named** | LOW |
| F14 | Destruction table: four rows are single cells and only uniform dither is a median over 6; only the 50% pair discloses this. The header also leaves the participation arm and the floor's units (co-active ROIs) to be inferred | LOW |
| F15 | The fractional-*K* residual (57 vs 42.9 at *J* = 16 frames; 3 vs 4.6 at *J* = 0.8 s) is **not verifiable against either named source** — these figures appear nowhere in the production run or the probe. Not asserted wrong; it is the one claim with no reachable provenance | LOW |
| F16 | The artifact is **untracked** (`??` in `git status`) while `docs/INDEX.md` — itself uncommitted — already routes readers to it as the authority that "wins over the plan". Nothing on `origin` carries either file | LOW |

**Two notes that are not findings.** The commit named in the source row, `0dc6356`, changed exactly
one file (the withdrawn v1 document) — the code symbols it credits are real in that tree, so the row
is accurate as a tree reference, but it may read as "the commit that added the code". And the
document's care about *K* is warranted: the run's own `meta.json` uses `K` for draw count while
`destruction.csv` uses `K` for the coactivity floor — exactly the collision the Terms table calls out.

---

## Role 11 — Argument order, "Start With the Problem."

`GRANT 11 ok — Read, Grep, Glob`

**9 findings: 5 major, 4 minor. No blocking.**

**What it put on the record as right, unprompted:** the cold open. *"The overnight run could not have
produced a corrected flag at any setting, and that was derivable from the plan before it started"* —
the first sentence a reader meets is the problem stated as a problem. And sections 7, 8, 10, 11, 12,
13, 14 are all in defensible positions, with §7→§8 (the requirement, then the demonstration that
260/520 is exactly that requirement) singled out as the document's strongest sequence.

*(Adjudication note: role 4's blocking finding later showed the sentence role 11 praised is the false
one. The ordering judgement stands; the claim it ordered does not.)*

| # | issue | sev |
|---|---|---|
| 1 | **"The problem, unchanged" is at position 6 of 13** — the motivation is stranded in the middle while the answer and the decisions are hoisted to the top. This is, verbatim, the incident the checklist exists for | major |
| 2 | **The three decisions are requested before any of their supports arrive** — decision 3 literally says "(below)", which the document concedes rather than fixes | major |
| 3 | **Terms sits three sections after the terms are first used** | major |
| 4 | **The erratum table splits the evidence block** and restates numbers that §10, §12 and §13 give as primary evidence | major |
| 5 | **Two near-isomorphic recommendation lists sit eight sections apart** with different numbering | major |
| 6 | The bottom line's strongest sentence arrives last in its paragraph | minor |
| 7 | Section titles describe process ("What the probe established about the instrument") where they could carry the claim | minor |
| 8 | The residual list mixes decisions for Tony with defects for a session, in one undifferentiated run of bullets | minor |
| 9 | Outside its scope but flagged: **the run record cited at L36 does not exist** — a dead cross-reference belongs to roles 1 and 3, and the one source it could not reach was the one that would have told it what previous reviewers found, which is the correct state for a blind pass | minor |
