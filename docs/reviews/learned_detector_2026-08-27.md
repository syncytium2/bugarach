# Murderboard run — the learned-detector page

> **Round 1 stopped after synthesis, on Tony's instruction; the fixes were applied
> the following night under a reframe from him — *the goal is the pipeline; this is
> a page documenting a stale learned model*.** That moved the deliverable rather than
> patching the findings, and dissolved several of them. Everything below is the
> original findings record, kept in the words it was written in. **What happened to
> each finding, and what ten further blind rounds turned up, is appended at the end
> — read that before acting on anything here.**

## What was at stake

The site had four pages and none of them mentioned the network. `bakeoff` did
not appear on the front page at all, so the one result that reads as machine
learning to an outside reader lived 280 lines deep in the README. FOUNDATIONS §8
makes this repo a portfolio artifact; the strongest evidence in it was not on the
artifact. The page under review was written to close that gap, and it is aimed at
a stranger deciding whether to hire its author.

That audience is what makes the findings below serious rather than tidy. A number
that overstates costs more here than a bug, and the page's own credibility is the
product it is selling.

## What was found

Eleven roles returned **191 findings, 31 of them blocking**. Five are structural
— they are not fixed by editing a sentence.

### 1 · The headline claim is contingent on a scoring choice that reverses it

The page leads with *"It ties the best hand-written detector in this project."*
That tie exists because `BenchResult.precision` is `n_hit / (n_detected − hot_fa)`
— firings inside the no-event probe block leave the denominator.

Recompute F1 from the per-fold `n_hit / n_detected` in `bakeoff.json`, counting
those firings as the false alarms they are:

| detector | F1 as published | F1 with probe firings counted |
|---|---|---|
| center−surround (learned) | 0.668 | **0.548** |
| CoactDetect | 0.651 | **0.640** |
| LoCo | 0.638 | **0.615** |

The ordering reverses and the learned model drops from first to third. 63 of its
221 detections — **29%** — fall inside a window that is 8.5% of the recording,
against 5 of 167 (3%) for CoactDetect.

The exclusion may well be the right rule; `bench.py` argues for it well. But the
page discloses that F1 cannot see the trap and then never says what F1 *would*
say, three sections below a standfirst that depends on the answer.
*(Reviewer 2, finding 1.)*

### 2 · The page's centrepiece is a claim this project already retracted

The architecture figure's caption says the fitted kernel widths are *"the model's
own estimate of how wide a coordinated event is"* and that the model *"found the
scale on its own."* The body says it again.

[`2026-08-16-learned-detectors-handoff.md`](../todo/2026-08-16-learned-detectors-handoff.md)
says: *"The fitted centre widths are not a pure measurement of the event.
Retrained on a quieter background with identical events they moved 40%. They land
in the right range and **should not be quoted as recovering the timescale.**"*

The data confirms the retraction. The same architecture fitted on the quiet
regime gives centres [2.44, 3.19, 6.72, 9.31] — a 3.8× span. *"All four converged
into one narrow band"* is a property of one background, not a finding about
events. This is the murderboard's own *a retracted claim stays retracted* rule,
walked into eleven days after the retraction was written.
*(Prove It, F1.)*

### 3 · The figure and the table describe two different models

`architecture_fitted.json` — the source of the converged-widths panel and of the
"ratio of 38 against a ceiling of 40" ablation — was fitted at background
**0.0190 Hz**. Every number in the results table comes from `bakeoff.json`, fitted
at **0.0097 Hz**, where the same architecture lands centres of **2.6–5.0 samples**
and a largest ratio of **23.5**.

Same architecture, same 1,149 parameters, different fits on different data,
quoted two paragraphs apart as one model. The page's headline architectural
finding moves ~35% with the background rate — itself a result nobody has
reported. *(RTFM, finding 3, which reproduced both fits.)*

### 4 · Zero citations, on a page whose argument is a comparison

The page names six other people's published methods in a table and puts this
project's network on top of it. It cites nobody.

The project knows better elsewhere: the front page says *"Cite them, not this
repo"* for two of the six, the viewer carries locust's citation inline, and the
2026-08-24 audit closed all six as having published prior art. And the sentence
that erases it — *"No method from the literature has been run on these
recordings"* — **is false as written**. binned SCE is Cossart 2003's rule; locust
is CICADA's method; rate+context is cell-averaging CFAR. The front page carries
the same sentence two lines after naming locust as CICADA's method.

The architecture is not unattributed either:

- A **learnable-σ difference-of-Gaussians bank** is Pogoncheff, Granley & Beyeler
  (NeurIPS 2023), whose paper states *"each DoG kernel has learnable parameters"*.
- **"One cell, one vote" via windowed binarization** is Grün, Diesmann & Aertsen
  (2002)'s clipping step — the paper this repo's README already credits for LoCo
  and CoactDetect.
- The **"next experiment"** the page proposes — divide by the surround rather
  than subtract it — is **STA/LTA**, the standard seismological event trigger
  (Allen 1978, *BSSA* 68(5):1521–1532). Same ratio, same geometry, on a 1-D
  trace, forty-eight years old, and named nowhere in this repo.

*(DOI or Die, B1–B3 and M1–M7. Full verified bibliography in that role's return;
it read Cossart 2003's Methods and reference list first-hand and closed the
repo's own "reported, not read" gap on that quotation.)*

### 5 · Three architecture guarantees do not hold as stated — and two are the code's fault

The page states three properties that *"fall out of the shape rather than being
trained for."* Measured against a trained model at the shipped operating point:

- **Rate invariance by construction.** `Tube.forward` ends
  `self.head(torch.cat([bright, resp], dim=1))` — the head receives the raw,
  un-differenced brightness trace alongside the zero-integral responses. The
  *filter bank* is DC-invariant; the *network* is not, by design. On pure Poisson
  background with nothing planted, an 8× background change takes false alarms
  from 7 frames to 1,228. Zeroing the `bright` channel roughly halves that climb,
  so the leak is about half architectural and half the variance term the page does
  name. **Panel C, billed on the page as "the test", pushes a step through a numpy
  reimplementation of the kernel alone** — it cannot test the model.
- **One cell, one vote, enforced exactly.** Two bursting cells score **1.0000**,
  identical to a genuine four-cell crowd. The max-pool named as the mechanism caps
  nothing: the raster is already binary per (cell, frame), so pooling *widens* each
  onset fivefold. It also uses `int()` of the **narrowest** of four fitted widths.
- **"Cells are summed."** `bright = pooled.sum(dim=1) / max(n, 1)` — a mean, and
  the division is what delivers the cell-count invariance the sentence credits to
  the sum. The invariance is over participation *fraction*: a six-cell event scores
  1.0000 on 32 cells and **0.0283 on 300**.

Two of these were inherited faithfully from `nets.py`'s own docstrings, which
assert the same things. **The page is not the only thing that needs correcting.**
*(RTFM 1/4/6, Reviewer 2 3/21/22. Note a genuine disagreement: Prove It cleared
the one-cell-one-vote claim by reasoning from the binary raster; RTFM refuted it
by running the model. The empirical result stands and should be re-verified before
either is acted on.)*

## Everything else, grouped

**Selective reporting — two instances, both mine.**
The trap-block column has nine values (`tiny` 0.0 · `trace` 0.0 · CoactDetect 1.25
· LoCo 2.50 · SPIKE-synch 8.75 · tube 15.75 · rate+context 34.75 · binned SCE 58.75
· **locust 214.75**). The page quotes three. The six it drops are the interesting
ones — locust fires 13.6× the learned model while ranking 5th on F1, and
rate+context, which the page recommends on cost, fires 2.2× more.
`make_bakeoff_figures._rows()` already computes this column into its row dict and
never plots it. Likewise the scale ablation reports one scale (0.670) and four
(0.668) and omits two scales at **0.634**, which the "multi-scale capacity is
unused" reading does not predict. *(Show Don't Tell F1; Kill Your Darlings 22;
Cross-Examiner 13.)*

**An ablation with zero power, reported as a result.**
The page says raising the surround-ratio ceiling from 40 to 200 "changed the score
to 0.668 — identical." The two runs are bit-identical in every field because the
clamp **never binds** in any four-scale run: the largest fitted ratio is 23.5. It
is a no-op, not a null result. The 38-against-40 observation that motivates the
paragraph comes from the *other* fit (§3 above). Where the clamp does bind — the
one-scale runs, raw ratios 41.27 and 40.45 — the scores differ, as they must.
*(RTFM 5.)*

**Provenance the page never states.**
The 85 recordings were assessed from `event_store_onset_revised_2v_alive_rescued`
— the `.mat` store CLAUDE.md declares closed. FOUNDATIONS §9 has since re-derived
the difficulty axis from the approved export folder *precisely because* the store
carries withdrawn recordings. `architecture_fitted.json`, `regime_shift_fitted.json`
and `learned_results.json` all predate that 2026-08-20 re-derivation and sit on the
retired 0.0038/0.0175 endpoints. Separately the assessment is **FAST stream only**,
and FOUNDATIONS §9 requires a claim to name its stream; the page never does.
*(Reviewer 2 4/5; Prove It F3, F18.)*

**Uncontrolled comparisons presented as controls.**
Both floor models land their threshold on the **low edge** of the searched grid —
`pick_threshold`'s own boundary warning fired on 7 of 8 control fits — and
`bakeoff.md` says in terms that their F1 "is not an operating point." The page
prints the numbers bare and builds a conclusion on them. `fair_bakeoff.py:54` also
gives the tube **10× the learning rate** of the two it is called a control against,
which the handoff already lists as open item 3: *"'Building the invariant in beats
hoping for it' is the reading, not yet the finding."* The page asserts the finding.
*(Cross-Examiner 2; Prove It F2, F6; Reviewer 2 7.)*

**A held-out set that is not held out.**
`pick_threshold` is written correctly — validation seeds are disjoint and asserted.
But `fair_bakeoff.py:180` passes `mk = lambda seed, _t=tuple(tr_seeds): rec(_t[seed % len(_t)])`,
which discards the seed's identity. Fold 0's four validation recordings are
**all four** training recordings. The scored fold is genuinely untouched, so the
headline F1 is not inflated — but the page's sentence *"chosen on held-out data"*
is one of its fairness guarantees, and it is false as run. `make_architecture_figures.py`
passes the seed through and does not have this bug, so the two tools behave
differently. *(RTFM 2; Prove It F4; Reviewer 2 8.)*

**Domain errors.**
K is **`min_rois`**, the minimum number of participating cells — not a cluster
count. The page says "how many clusters the activity falls into" and "a human
picks the cluster count — here 3," which tells a reader someone chose to have
three clusters; at K=3 there are hundreds. A **circular shift preserves each
cell's onset count exactly**, so it cannot be a null for per-cell rate — only
jitter and cluster count have nulls, not the four quantities the page lists. And
*"each by a hand-written rule: count active cells in a window, compare against a
shuffled null"* is false for two of six: rate+context uses no surrogate, and
SPIKE-synch counts no cells in a window. *(Cross-Examiner 1; Prove It F11, F12.)*

**Figures.**
`bakeoff.png` labels the sixth detector **CICADA** where the table says **locust** —
the glossary makes these different things, so the figure asserts the Cossart lab's
software was benchmarked, which the page's own caveat denies. The fix is
deterministic and reads JSON only: `make_bakeoff_figures.py` already imports the
rename map and the PNG simply predates it by six days. Beyond that, the page is
**2,171 words with two figures, 100% of its visual content in 23% of its height**,
seven of nine sections carrying nothing to look at, and no picture of the problem
at all. Three figures it needs are already committed and were each build-verified
into a scratch copy: `pipeline.svg` (renders *shorter* than the prose box it
replaces), `architecture.svg` (carries the 1,137 of 1,149 parameters the prose
omits — the centre−surround stage the whole section is about is **12 parameters**),
and `regime_shift_fitted.png` (24 values where the prose quotes 3).
*(Ship It F-1; Show Don't Tell F1–F7; Start With the Problem F2.)*

**Craft.** `<tr class="learned">` matches no CSS rule, so the three learned rows
render identically to the seven hand-written ones while the adjacent figure uses
colour for exactly that distinction. `td.n` (right-aligned tabular numerals) is
defined and applied nowhere, so nine rows of decimals sit left-aligned in a
proportional face. Neither is a missing stylesheet — both fixes are already in
`report.css`. All four panels of `architecture_fitted.png` lack x-axis labels.
*(Ship It F-2, F-3, F-4.)*

**Readability.** Four sections are blocking for a cold reader. **F1 is never
defined** on a page where every claim rides on it. The six detector names arrive
with no gloss and no origin, which is exactly the variable that sets how
impressive "ties the best of them" is. *(You Lost Me.)*

## Findings about the repo, not the page

These surfaced during the review and are not this branch's to fix:

- **`nets.py`'s docstrings assert two things the model does not do** (§5 above).
- **`fair_bakeoff.py`'s threshold selection** does not hold out what it claims to.
- **`architecture_fitted.json` is fitted at a different background** from every
  published number, and nothing says so.
- **SAP009 has a live blind spot.** `make_tube_figure.py:153` is
  `rowA = _probe(raster * ticks * dmark)` — a shaded treatment window and two
  marker rows drawn onto a raster. The rule's pattern is `\braster\w*\s*\*\s*hv\.`,
  so `sapper --all` reports **clear** on a file that breaks the rule it exists for.
  Wider than the naming gap already filed in `docs/sapper_feedback/`.
- **`docs/learned/problem_view.png` has no generator anywhere in `tools/`** — an
  orphan that violates the raster rule and cannot be regenerated to fix it.
- **`tests/test_site_dates.py` carries a hardcoded three-page list** where
  `test_site_coherence.py` derives from `bs.PAGES`, and `build_site.py:1017`
  prints its unstamped complaint without returning 1 — so the stamp is the one
  published-page property locked at neither end.
- **My own `build_site.py` comment claims a staleness guard I did not implement.**
  It says the build refuses when the page is behind its data; the code checks only
  that the file exists.
- **The front page carries the same false "no method from the literature" sentence.**
- **Role 2 returned "0 findings" on this page's ancestor** — *"the page cites no
  papers, DOIs or external attributions … nothing to verify."* On a page naming six
  other people's methods, that is the defect inverted, and it was a single-pass
  self-review. Worth a process rule: **role 2 enumerates the named methods first,
  then checks each for a citation, before checking the citations that are present.**

## What would validate the fix

Four of the five structural findings are settled by running something, not by
argument:

1. Publish both F1 numbers, or state why the probe exclusion is the right rule
   *at the point the tie is claimed*.
2. Re-fit `architecture_fitted.json` on the bake-off spec, or state in the caption
   that it is a separate fit and give both centre ranges.
3. Push a background sweep through the **whole trained model** with nothing
   planted, and use that as panel C. The table in RTFM finding 1 is that panel
   already measured.
4. Add the citations. The bibliography is verified and ready to paste in role 2's
   return.

The retracted-widths claim (§2) is settled by deletion, not by measurement.

---

# Appendix

- upstream:  syncytium2/murderboard @ `3593c44`
- copy:      vendored @ `3593c44`
- freshness: current (verified at review time with `--refresh`, exit 0)
- artifact:  `site/learned_detector.html` (`5e03e854` -> **unchanged, no fixes applied**)
- roles:     11 of 11 run
- rounds:    **0 blind verify rounds — run halted after synthesis**

## Role ledger

| # | Role | Findings | Blocking |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 21 | 3 |
| 2 | Citation & reference validator — "DOI or Die." | 14 | 3 |
| 3 | Consistency auditor — "Cross-Examiner." | 21 | 2 |
| 4 | Adversarial reviewer — "Reviewer 2." | 26 | 7 |
| 5 | Line editor — "Kill Your Darlings." | 42 | 4 |
| 6 | Methods / domain expert — "RTFM." | 10 | 3 |
| 7 | Reuse auditor — "Reinventing the Wheel." | 10 | 0 |
| 8 | Naive-reader accessibility — "You Lost Me." | 16 | 5 |
| 9 | Density & figure-first — "Show, Don't Tell." | 12 | 2 |
| 10 | Build & craft gate — "Ship It." | 9 | 1 |
| 11 | Argument order — "Start With the Problem." | 10 | 1 |
| | **total** | **191** | **31** |

Role 7 returned no blocking finding and said so with its evidence: it loaded the
published fit into a real `build_tube()`, called `_kernels`, and diffed all four
numpy copies of the difference-of-Gaussians against it. Maximum divergence
**8e-9** — float32 against float64. The figure this page embeds is numerically
correct. It is correct *by luck*: the two clamps `nets.py` applies and the numpy
copies omit happen not to bite, the page's own text puts the reader 2.25 units
from the ceiling that would break it, and no test compares any copy to the model.
`tools/make_tube_figure.py`'s copy has already drifted on four axes at once and
draws a surround **0.54×** the model's peak weight — on a published page, today,
found by nobody, because nothing was comparing.

Roles 10 and 3 both ran the project's own gates: `pytest` on the four site test
files, 91 passed, exit 0; `tools/sapper.py --all`, clear, exit 0. The page's
responsive and theme behaviour passed every row of the render ledger at 1440px,
1100px and 390px in both themes — including the 9×7 table, which scrolls inside
its own container without the document ever scrolling.

## Residual ⚠ carried forward

- ⚠ **Prove It and RTFM disagree** on whether "one cell, one vote" holds. RTFM ran
  the model; Prove It reasoned from the encoding. Re-verify before acting.
- ⚠ **The embedded architecture figure is correct today** and nothing in the tree
  keeps it correct across a retrain.
- ⚠ **Sonar, seismology beyond Allen 1978, pre-2006 chemometrics CWT, change-point
  detection and MEA burst detection were not searched.** No systematic database
  search was run — web search plus full texts only. Any "nobody has done this"
  sentence needs one first.
- ⚠ **Kreuz's own later applied papers are unresolved** (Cecchini 2022,
  Kreuz 2024, Mariani) — the papers where the measure's author builds a detector
  on his own profile. They bear directly on publishing SPIKE-synch's
  bottom-of-table 0.254 under his name, and must be resolved before that citation
  ships.
- ⚠ **Kreuz answered Tony by email on 2026-04-23** and none of it reached the page.
  Correspondence was available and unused — recorded as a finding, not an absence.
- ⚠ **`tests/test_site_dates.py` no longer covers every published page**, and
  `build_site.py` does not fail on the same property.

---

# What happened next — the fixes, and ten more blind rounds

**Appended 2026-08-28.** Round 1 above found 191 findings and the page did not ship.
Tony then reframed the deliverable, the page was rewritten, and the verify loop ran
until two consecutive blind passes returned nothing blocking.

- artifact:  `site/learned_detector.html` (`5e03e854` → current)
- rounds:    **11** (1 original + 10 blind verify)
- commits:   17 on `learned-detector-page`, none merged, nothing deployed

**The loop was stopped, not exhausted.** Rounds 8 and 10 returned nothing blocking, and
round 11 was run as a final triage rather than as another repair cycle. Every round
after the first found something real; the findings narrowed steadily, but none came back
empty. What follows is therefore an honest account of a converging process that was
halted at a sensible point, not a proof that nothing remains.

## The reframe, and why it was not a way of avoiding the findings

*"Our goal is to achieve the pipeline. This is a page documenting a stale learned
model."* The page's subject moved from the model to the apparatus that scores it.

That legitimately dissolved three of the five structural findings rather than
patching them. A page whose subject is the apparatus **can** say plainly that this
pass through it is stale, which the old page could not, because the old page's
headline depended on the numbers being live. The retracted kernel-width claim stopped
being the centrepiece and was deleted. The tie stopped being the headline.

It did not dissolve the rest, and those were fixed by measurement:

| finding | how it was resolved |
|---|---|
| Headline contingent on the probe-exclusion rule | `tools/probe_inclusive_f1.py` rescores the same detections with probe firings charged. **Both columns are now in the table.** The column reorders the field: locust falls from fifth to seventh, and the learned model loses 0.120 of F1 where CoactDetect loses 0.011 |
| Retracted fitted-width claim | deleted, and the retraction stated |
| Two fits quoted as one model | no `architecture_fitted` token remains in the results argument; the page now names all five kinds of fit it carries |
| Zero citations | six methods cited with DOIs, plus the architecture's own precedents and the seismological trigger the page proposes as its next step |
| Three architecture guarantees | each re-measured; see below |

## What the four blind rounds cost, and what they were worth

Every round found something real. The findings narrowed each time, which is what
convergence looks like, but **no round was clean until the fifth**.

**Round 1 (verify).** The rate-invariance probe set `hot_rate_hz` equal to the
background to flatten its recordings. The hot block is *additive*, so that doubled the
rate inside a 300 s window instead of removing it — and the store's own note said "no
hot block". 41% of the firings counted at baseline lay inside the contaminated
stretch. Also: 1,128 + 12 = 1,140, and the model has 1,149. The final 1×1 layer holds
9 and the prose had dropped it.

**Round 2.** *"The two learned models at the floor are silent."* They are not. The
per-cell bank emits two detections per fold, and those two calls cover twelve
distractors and two planted events across two recordings — one span per recording,
99.6% of it. Its probe count is zero because `score.py` never puts a matched detection
in the false-alarm set. **A zero in that column means one of two opposite things.**
The table now carries the distractor column so the contradiction is visible in two
adjacent cells.

**Round 3.** The architecture finding was a coin flip. "Two bursting cells outscore
four distinct ones" holds on 5 of 10 independently trained fits, loses on 3, ties on
2 — the two scores are saturated sigmoids a median of 0.0002 apart. `tools/probe_one_vote.py`
now runs the grid and the store keeps the fragile contrast as a tally so the page
cannot quote it as a value.

**Round 4.** The page corrected `build_tube`'s docstring by name and the correction
was backwards. *"One bursting long enough does"* generalised from two cells to one,
and no measurement stood behind it. Measured: a single cell fires on 0/10 at one
onset, **4/10 at five, and 0/10 at twenty**. Bursting longer makes it worse — the
model has a preferred run length. Also caught two figures asserting claims the page
retracts, and a "free fit reaches 41.3" that was a *clamped* run's raw parameter (the
free run reaches 59.3, a stronger number sitting in the same store).

**Round 5.** Ran clean of blocking findings.


## The ten blind rounds, and what each cost

Every round found something. None came back empty. The findings narrowed, and the
character of them changed — from *the page is about the wrong thing* to *this arrow
clears that label by 3.7 units*.

| round | blocking finding | whose fault |
|---|---|---|
| 1 (verify) | the rate probe contaminated its own null recordings while the store's note said they were empty; 1,128 + 12 ≠ 1,149 | mine, new |
| 2 | "the floor models are silent" — they swallowed the whole recording; a zero in the trap column means the opposite | mine, original |
| 3 | the architecture finding was a coin flip: 5 of 10 seeds | mine, original |
| 4 | the page corrected a docstring by name and the correction was backwards | **my round-3 fix** |
| 5 | "no detector ever sees ground truth" — the learned models are supervised on it | **my round-4 fix** |
| 6 | a sentence that contradicted itself in thirty words, in the honesty section | **my round-5 fix** |
| 7 | the caption said the six are swept against truth; no arrow reached them | **my round-5 fix** |
| 8 | none | — |
| 9 | two SVG labels lengthened past the layout, one clipped off the viewBox | **my round-8 fix** |
| 10 | none | — |
| 11 | final triage | — |

**Five of the ten blocking findings were defects introduced by the previous round's
fix.** That is the single most useful number in this record. A reviewer who stops after
one pass ships those five, and every one of them was in the sentence or the figure the
previous round had just corrected — the place nobody looks twice.

It is also why round 9's response was a guard rather than another careful edit.
`tests/test_svg_labels.py` measures every hand-written SVG's text through Chromium: no
label outside its viewBox, no two overlapping. **Round 10 then found a hole in that
guard** — it compared only labels sharing a rounded baseline, and the fix that prompted
it had split the row onto three interleaved baselines, straight through the gap. The
reviewer proved it by mutation rather than by argument. It compares boxes now, and its
own can-it-fail test carries that case.

The guard's first run found a defect nobody was looking for: a clipped label in
`landscape.svg`, a different figure on a different published page, shipping cut
mid-word.

## What the loop could not do

**It never questioned the deliverable.** Eleven roles and ten blind rounds, every one
correct within its remit, and not one said *this is a page about the wrong thing*. Tony
said it in a sentence the next morning. The loop checks whether a page is sound; it does
not check whether it is the page you wanted.

**It has no power over seed variance**, which is the defect underneath at least ten of
the findings — a single training run reported as a result. Four extra fits on one fold
would settle it and cost about 25 seconds. Until they are run, the fold spread (0.061
F1) is wider than most effects this page discusses, and every reviewer who noticed said
so independently.

## The pattern across all eleven rounds

**Ten of the findings are the same defect in different clothes: a single run reported
as a result.** The probe-inclusive column, the rate sweep, the one-vote comparison,
the fitted widths, the transfer asymmetry, three of the ablations. In every case the
number was correct and the claim built on it was not, because seed variance in this
project has never been measured and the fold spread (0.061 F1) is wider than most of
the effects being discussed.

That is the finding to carry out of this review. It is already the oldest open item on
the model track; what this run adds is that it is not a footnote — **it is the thing
that keeps producing wrong sentences**, including inside a review whose subject is
wrong sentences.

## What is now mechanized rather than remembered

- Four probe tools, four stores, and **every number on the page is a build-time token**.
  Each tool writes its whole store; one of them did not, and that was itself a finding.
- `build_site.py` rebuilds the page to a temp path and byte-compares before publishing,
  so a regenerated store with an un-regenerated page fails the build. Mutation-tested.
- `tests/test_site_dates.py` derives its page list from `bs.PAGES` instead of carrying
  a copy, and `build_site.py` now returns 1 on an unstamped page instead of printing.

## Still open, filed rather than fixed

Six todos, each naming what the fix would cost:

- [`the model does not do what its docstring says`](../todo/2026-08-27-the-model-does-not-do-what-its-docstring-says.md) — `nets.py` asserts two things the model does not do. Fixing the *model* is the handoff's open item 4 and moves every published number.
- [`the threshold is picked on the recordings it trained on`](../todo/2026-08-27-the-threshold-is-picked-on-the-recordings-it-trained-on.md) — `pick_threshold`'s assertion checks seed integers that a modulo makes meaningless. No published number is wrong; the guarantee is.
- [`the fitted kernels figure is a different fit`](../todo/2026-08-27-the-fitted-kernels-figure-is-a-different-fit.md)
- [`a published figure with no generator`](../todo/2026-08-27-a-published-figure-with-no-generator.md)
- [`role 2 must enumerate before it verifies`](../todo/2026-08-27-role-2-must-enumerate-before-it-verifies.md) — upstream, in the vendored process
- [`SAP009 misses an overlay through a named variable`](../sapper_feedback/2026-08-27-sap009-misses-an-overlay-through-a-named-variable.md)

## Residual ⚠ carried to Tony

- ⚠ **Which F1 column is *the* score is an open decision** —
  [`two scorers, two winners`](../todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md)
  is `waiting-on-tony` and **blocks the re-fit**. `probe_inclusive_f1.py` is a third
  implementation of one of the two rules. It picks no winner and feeds no operating
  point, and the page prints both columns and says the question is open — but a public
  page now carries a position on a blocked internal decision.
- ⚠ **Seed variance is still unmeasured**, and the page leans on a fold spread as a
  believability floor throughout. Four extra fits on one fold would settle it.
- ⚠ **Kreuz's later applied papers are unresolved**, and his April correspondence is
  still unused, while the page publishes a bottom-of-table score under his measure's
  name. The page mitigates by saying the detection layer is this project's, not his.
- ⚠ **Sonar, seismology past Allen 1978, and several other literatures were not
  searched**, and no systematic database search was run.
