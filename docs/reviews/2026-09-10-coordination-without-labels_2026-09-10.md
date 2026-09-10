# Murderboard run — the self-supervised coordination detector, and the surrogate that gives itself away

> **Mode: pre-mortem.** The artifact was reviewed before a line of its proposal was implemented.
> That is the whole value of what follows: the defect below would have cost a training pipeline,
> a figure campaign and an external circulation, and it cost a draft.

**Run stopped at round 1 and escalated, deliberately.** Not because the findings were minor —
because they are structural, and the process says so in terms: *"a flat or rising blocking count
after two rounds does not mean review harder; it means the artifact has a structural problem that
patching will not retire."* Nine blocking findings landed on the **mechanism**, not the prose. No
number of verify rounds turns this draft into the document it was trying to be, because the thing
it proposes does not work in the form proposed. **This run is delivered as unconverged.**

---

## The problem, stated first

The withdrawn draft proposed a coordinated-event detector that needs no labels. Take a real
recording; make a copy in which **every event time is independently displaced** by up to *J* — a
*dither*; train a network to tell the two apart. The pitch was that per-cell firing rates are
identical in both classes by construction, so the model cannot win on rate, and a lone cell
carries nothing to learn from, so the single-ROI failure that prompted the whole design becomes
structurally impossible.

**Two roles, working independently, measured that the surrogate is separable one cell at a time.**

Real within-cell onset intervals in this project's own senktide baseline windows have a hard
floor — **0.40 s in the fast stream, 3.20 s in the slow**. An event extractor cannot emit two
onsets from one cell inside a single calcium transient. Independent per-onset dithering has no
such floor, so the dithered class contains intervals whose probability under the real class is
**exactly zero**.

Cutting those baselines into 60 s windows:

| stream | *J* | real windows with a sub-floor within-cell interval | dithered windows | AUC of that one scalar |
|---|---|---|---|---|
| fast | 1.6 s | **0.0 %** (0 of 543) | 29.5 % | 0.647 |
| fast | 2.5 s | **0.0 %** | 38.3 % | 0.692 |
| slow | 2.5 s | **0.0 %** | 16.9 % | 0.585 |

That is not a distribution difference; it is a **support** difference. Any window containing a
sub-floor interval is a surrogate with probability 1, identified using **no cross-cell information
whatsoever**. One hand-picked count, no fitting, reaches AUC 0.692 — against a best learned
detector in this project of F1 0.681.

**The draft's own optimality argument is what makes this fatal rather than untidy.** It claimed the
optimal discriminator computes a monotone function of the likelihood ratio. A likelihood-ratio-optimal
model finds the impossible interval *first*, because nothing else on offer has infinite odds. The two
central claims destroy each other, and the draft states both, ~1,400 words apart, with no
cross-reference.

### The control could not have caught it

This is the finding worth carrying furthest. The draft proposed a negative control: dither a
recording once, use **that** as the positive against a further-dithered negative; a flat result
clears the design, a non-flat one is fatal.

The control's positive class **has already been dithered**, so every leak that arises *from*
dithering is present on both sides. It sees only the increment the second dither adds, and the leak
saturates:

| | P(window has an impossible within-cell interval) |
|---|---|
| real — 0 dithers | **0.000** |
| 1 dither — the control's POSITIVE | **0.932** |
| 2 dithers — the control's NEGATIVE | **0.953** |

The training objective faces 0.000 against 0.932 — perfect separability. The control faces 0.932
against 0.953 — deep in saturation, and **flat precisely because the leak is total**. Under the
draft's stated rule, that flatness reads as clearing the design.

A check that cannot fail, whose danger is that it *passes*. The draft made it load-bearing twice:
the only thing standing between the design and a confident artifact detector, and the calibrator
that sets the operating threshold.

### And the literature settled it first

The draft said it was "unsurprised to learn this exact construction has a name." It has several,
and two roles found them in under an hour:

- **Dithering.** Louis, Gerstein, Grün & Diesmann (2010), *Front. Comput. Neurosci.* 4:127 — defines
  the construction and its purpose in the draft's own words, and states that dithering *"distorts
  the inter-spike interval distribution toward that of a Poisson process."* Root: Date, Bienenstock
  & Geman (1998), Brown University tech. report ⚠ *confirmed by citation, not read — no open copy found.*
- **The variant chosen is the one singled out as unsafe.** Platkiewicz, Stark & Amarasingham (2017),
  *Neural Computation* 29(3):783–803, *"Spike-Centered Jitter Can Mistake Temporal Structure"* — the
  draft proposes spike-centred jitter, names neither it nor the interval-jitter alternative.
- **The drift argument is the published argument.** Amarasingham, Harrison, Hatsopoulos & Geman
  (2012), *J. Neurophysiol.* 107:517–531 — conditional inference; coarse rate structure is preserved
  by construction so the test isolates fine timing. **This paper is already cited in bugarach's own
  README**, for LoCo and CoactDetect's null. The citation the draft needed was in the repo.
- **Uniform dithering is measured as invalid.** Stella, Bouss, Palm & Grün (2022), *eNeuro*
  9(3):ENEURO.0505-21.2022 — systematic comparison of six surrogates; uniform dithering loses **up to
  10 % of spikes** to binning and clipping and generates false positives. It *recommends the shift
  family the draft rejects.*
- **The objective has a name:** noise-contrastive estimation (Gutmann & Hyvärinen 2010, 2012) and the
  classifier two-sample test (Lopez-Paz & Oquab, ICLR 2017). **The localization recipe has a name:**
  weakly-supervised event detection via multiple-instance learning (Ilse, Tomczak & Welling, ICML
  2018; Wang, Li & Metze, ICASSP 2019, which compares the five pooling functions the draft treats as
  an open choice).

## The repair, and why it strengthens the idea

**The thesis survives. The surrogate does not.** Self-supervised discrimination against a
surrogate, on recordings nobody can label, remains the only route in sight to a learned detector
that has not merely learned this project's simulator.

**Pattern jitter** (Harrison & Geman 2009, *Neural Computation* 21:1244–1258) preserves every
event's recent history exactly. The within-cell leak is then **zero by construction** — which
means the lone-cell property the draft wanted becomes *true by construction* instead of true by
hope. **Interval/window jitter** (Amarasingham et al. 2012) conditions on per-window counts and
removes the edge artifact as well. **Dithering in operational time** (Louis et al. 2010) conserves
the rate profile exactly under non-stationarity — which is the draft's stated central problem.

The draft's first open question — per-onset dither or per-cell rigid displacement — is a false
dichotomy. The literature exists because there is a third answer, and it is the right one.

## What else the run found, ranked

**Blocking, on the mechanism:**

1. The dead-time leak (above).
2. The control is blind to it (above).
3. **The design trains quiet and deploys busy — the direction this project has already measured as
   harmful.** `docs/model_track.md`: *"It transfers worse than two of the six from a quiet
   background to a busy one… Fit busy, deploy quiet,"* the difference between a **−0.24 transfer
   penalty and a +0.12 gain**. Under TTX the slow stream runs ~2.5× baseline. The draft's
   baseline→treated plan is quiet→busy, and it called the constraint *"the right experimental design
   anyway"* while the tree holds a measurement saying it costs a third of the score.
4. **"Provably no coordination" is false, so α is not a false-alarm rate.** Dither preserves
   co-modulation coarser than *J* by construction — the draft argues exactly this as its own selling
   point. Its control's positives are band-limited, not coordination-free.
5. **A ceiling never stated: coordination coarser than *J* is invisible by construction.** A broad
   3 s recruitment at *J* = 0.5 s cannot be detected at all.
6. **Dither's boundary artifact is worse than the splice it rejects** — two edge bands per cell per
   *window*, against one anomalous interval per cell per *recording*. And `learn/encode.py:119`
   **clips**, piling displaced onsets onto frame 0 and frame *n*−1: another support violation.
7. **The detector arithmetic is wrong throughout.** `nets.ARCHITECTURES` holds **six** learned
   architectures, not four; twelve detectors, not ten. The draft says "four learned" and "ten
   detectors", then "five of the six architectures" in the same section.
8. **"Nothing has been measured" is false** — the draft also quotes F1 scores, a bake-off design,
   artifact percentages and TTX effect sizes.
9. **The figure was invisible in dark mode.** `.mk rect{fill:var(--mark)}` matched nothing — no
   element carried the class — so all 134 marks fell back to black on a near-black ground, 1.23:1.
   A complete dark palette was authored and never reached the only figure. Fixed in this commit.

**Major, on claims about our own tree** — every one of these says the draft asserted something
about bugarach that bugarach contradicts:

- **A dither surrogate already exists and ships.** `graph.py:249` `jitter_trains` — per-onset uniform
  displacement, tested at `tests/test_graph.py:108`, used in production by `modularity_vs_null`. The
  draft pointed at SCE's `NotImplementedError` and called the idea *"contemplated and never built."*
  **And it wraps** (`graph.py:264`, `np.mod`), so the project's only dither has the splice the draft
  says dithering does not create.
- **CoactDetect, LoCo and binned SCE do not use a whole-recording shift.** They use **rolling** and
  **regional** nulls, built explicitly against drift — `coact.py:7-11` names drug onset as the case.
  The draft's strongest argument (dither dissolves a drift confound the six suffer) is substantially
  wrong.
- **A declared α already exists**: `coact_detect(alpha=...)`, shipped at 1e-4, plus
  `bench.MAX_PROBE_PER_MIN` and `pick_operating_point` gating calibration on it.
- **The leak control has been run before, and came out non-flat.** `tools/make_null_leak_figure.py`
  caught a leak in the assessor's own rate-matched estimator.
- **`tiny` trains at a tenth the learning rate of the model it is compared against** (`lab.py:380`),
  which `model_track.md` already files as *"the comparison is uncontrolled."* So "the per-cell
  architecture does not train" is not evidence about the cell axis — and the *pooled* control is
  floor-pinned too.
- **Split by animal, not recording.** `slices.csv:mouse_id` — 67 recordings from **36 mice**, 22
  contributing more than one, and 5 appearing in *both* cohorts. The draft's fold rule leaks.
- **The unexplained 2.7 vs 1.2 fast:slow gap has an explanation** — group composition. Per group the
  within-cohort spread exceeds the between-cohort gap (ORX 1.75 vs 1.74). FOUNDATIONS §9 makes the
  pooled ratio inadmissible on its own.
- **Four recordings carry a known unflagged contaminant** — non-rigid motion correction pinned 12
  ROIs to the frame floor — and all four are in these cohorts.

**Vocabulary and attribution:**

- **"corpus" is retired** (GLOSSARY, Tony 2026-08-22). The draft uses it nine times.
- **The draft names `CICADA` as a detector here**; the detector is **locust**, and FOUNDATIONS §7
  makes that a provenance decision, not a label.
- **TTX ROI median is 31, not 32** (senktide's value, copied).
- **`Hansen 1973` vs `Hansen & Sawyers 1980`** — ⚠ **the two roles that checked it disagree, and the
  draft may be right.** Role 2 verified independently that Hansen 1973 introduces GO selection and
  the 1980 paper measures its cost, so `detector_history.md` §4 appears to cite the analysis in a
  column headed *origin*. **Unresolved; needs Tony.** Nobody on this project has read Hansen 1973.
- **The novelty retraction is understated and reversed.** The retraction rests on three papers read
  in full and concludes the question is *closed*; the draft describes it as leaving the question open.

**Craft:** SVG text renders at 4.14 px on a phone; no italic axis is requested although *J* is set in
`<em>` throughout; the code block clips 15 px at 1200 px; `--faint` is 2.79:1 in light mode and
carries the entire footer including the lab attributions; `fatal` and `redesign` render in the same
colour.

**Structure:** the two headline asks are posed 100 lines before the terms in them are defined; the
figure interrupts a promise ("three reasons") and illustrates a construction introduced 1,300 px
earlier; the strongest claim sits in the ninth of thirteen sections, inside a de-emphasis panel;
5.3 viewport-heights of the back half carry no graphic at all.

## What this run does NOT warrant

This review found and characterised nine blocking defects. **It is not a correctness proof.** It
says the roles ran and what they found; it cannot say that a corrected design is sound, and no
convergence table could. In particular, the leak was found by two roles reasoning about *one*
mechanism — the refractory floor. Nothing here establishes that a pattern-jitter surrogate has no
analogous leak; it establishes that the obvious one is closed by construction. **That has to be
measured, on the export folder, before any model is trained.**

## Generalises beyond this artifact

**A self-supervised objective needs a negative control whose reference class is provably free of the
defect — and the natural control is usually not.** The draft's control was built by applying the same
corrupting operation one more time, which is the intuitive construction and the one that cannot see a
saturating leak. Any future design here that manufactures its own negatives inherits this trap.
The direct diagnostic — count the support violations at level, not increment, without a learned model
in the loop — is the thing that works, and it is cheaper than the model it protects.

---

# Appendix — the record

- upstream:  syncytium2/murderboard @ 81a0927
- copy:      vendored @ 81a0927
- freshness: current
- artifact:  `docs/proposals/2026-09-10-coordination-without-labels.html` (`34a4396` -> `63bb0fe`)
- roles:     11 of 11 run (compiled role agents, grants mixed — roles 4 and 5 declared MISMATCH)
- rounds:    0 blind verify rounds — **run halted at round 1 and escalated; see the stopping reason**
- mode:      pre-mortem, unconverged

**Stopping reason: structural, not round cap and not severity floor.** Nine blocking findings landed
on the proposal's mechanism rather than its expression. The process's escalation rule applies: patching
cannot retire a defect in the thing being proposed. The artifact is withdrawn in place with a banner
rather than repaired, and the redesign is Tony's call.

## Findings by severity, round 1

| round | blocking | major | minor | outcome |
|---|---|---|---|---|
| 1 | 9 | 31 | 40+ | halted — escalated to the human |

## Role ledger

Grants are quoted verbatim from each role's opening line, per the skill.

| # | role | grant declared | findings | note |
|---|---|---|---|---|
| 1 | Prove It — claim & data verifier | GRANT 1 ok — Read, Grep, Glob, Bash | 20 | Recomputed every corpus figure from the export folder. All match except the TTX ROI median (31, not 32). Found the detector-count error and the false "nothing measured". |
| 2 | DOI or Die — citation validator | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 15 | Every named work resolves; no fabricated metadata. Found the dithering literature, NCE, C2ST and MIL prior art. Disputes `detector_history.md` on Hansen. |
| 3 | Cross-Examiner — consistency | GRANT 3 ok — Read, Grep, Glob | 24 | Corpus arithmetic reconciles exactly. Found the retired "corpus", CICADA-as-detector, the samples/seconds unit contradiction, and the missing `class="mk"`. |
| 4 | Reviewer 2 — adversarial | GRANT 4 MISMATCH — missing Grep, Glob; holds Read, Bash | 9 | **Found the control-saturation defect and the quiet→busy transfer contradiction.** Substituted `rg`/`grep` through Bash, so no check was skipped. |
| 5 | Kill Your Darlings — line editor | GRANT 5 MISMATCH — missing Bash; holds Read, Grep, Glob | 70 | Could not run `murderboard_prose.sh` (no Bash; and the script is not in either tree). Declared rather than glossed. Found six ordinal back-references violating CLAUDE.md and three British spellings. |
| 6 | RTFM — methods expert | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 18 | **Measured the dead-time leak on the export folder.** Identified the variant against the published taxonomy and named pattern jitter as the repair. |
| 7 | Reinventing the Wheel — reuse audit | GRANT 7 ok — Read, Grep, Glob, Bash | 15 | Of six things the proposal would build, three are new; the surrogate, the leak control, the declared-α calibration and the membership readout all already exist here. |
| 8 | You Lost Me — naive reader | GRANT 8 ok — Read, Grep, Glob | 30 + figure | Four blocking sections. Read cold without opening the repo, as required. Senktide never defined; fast/slow never explained; *J* never given a value. |
| 9 | Show, Don't Tell — density & figure-first | GRANT 9 ok — Read, Grep, Glob, Bash | 14 | Measured every block in the render: 4,164 words, 6.7 % graphic ink, first figure at 36.9 % scroll depth. Audited the raster rule clause by clause — the figure passes it. |
| 10 | Ship It — build & craft | GRANT 10 ok — Read, Grep, Glob, Bash | 12 | Eight full-page renders across three theme states at two widths. No horizontal page scroll, nothing clipped by the viewBox, all 17 tokens defined in all three blocks. |
| 11 | Start With the Problem — argument order | GRANT 11 ok — Read, Grep, Glob | 12 | Recommends splitting the asks, inverting the lede, moving the figure and promoting the controls section. Confirms "Where we are" earns its position. |

⚠ **Two roles reported `MISMATCH`**, so the header's `named agents` claim is reported alongside them
rather than instead of them, and this record does not present the run as something else. Both roles
substituted equivalent coverage and said so; role 5's `murderboard_prose.sh` genuinely did not run,
and that is a gap, not a clean result.

## Residual ⚠ for Tony

1. **Which surrogate replaces the dither** — pattern jitter, interval jitter, or operational-time
   dithering. This is the design decision the whole redesign turns on.
2. **Hansen 1973 vs Hansen & Sawyers 1980.** Two roles disagree and `GLOSSARY.md`,
   `README.md` and `detector_history.md` do not agree with each other either. Nobody here has read
   the 1973 paper.
3. **Nobody was asked.** This project has a live correspondence channel with Thomas Kreuz, and Sonja
   Grün's group wrote the paper that answers both of the draft's open questions. One email each,
   before anything is circulated. *(Cite, never quote — CLAUDE.md.)*
4. **Whether to accept the quiet→busy transfer penalty** or bound it before any treatment number is read.
5. **Four contaminated recordings** — motion-correction frame-floor pinning — in or out of training.
