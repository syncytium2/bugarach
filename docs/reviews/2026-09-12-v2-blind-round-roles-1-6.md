# Blind round on the v2 reevaluation — roles 1–6, as returned

Companion: [roles 7–11](2026-09-12-v2-blind-round-roles-7-11.md). Adjudication and verdict:
[the run record](2026-09-12-surrogate-screen-reevaluated_2026-09-12.md).

**Artifact reviewed:** `docs/proposals/2026-09-12-surrogate-screen-reevaluated-v2.md` at `4b44e408`.

⚠ **Provenance of this file.** The harness wrote each agent's output to a temp file and every one
of those files is **0 bytes**; the reports arrived as task notifications instead. These are
reproduced from the session transcript, which is the only place they existed. They are faithful to
the returned text, lightly compressed in the longest prose sections — the findings tables, GRANT
lines, severities and numbers are as returned. Preserved because the run record's own complaint
about round 1 was that its reports were not kept, and losing round 2 the same way would make that
complaint worthless.

**Prompt every role received**, and nothing else: *"You are reviewing this document on its own
terms. You have not been told what any earlier review found; do not assume any particular defect
exists or does not."* Plus the output contract (first line `GRANT N ok — <tools>`, no file edits).
No finding was suggested, no ordering hinted, no verdict supplied.

---

## Role 1 — Claim & data verifier, "Prove It."

`GRANT 1 ok — Read, Grep, Glob, Bash`

Recomputed rather than eyeballed, across the production run, the probe run, `surrogate_stats.py`,
`surrogates.py`, `surrogate_discriminator.py`, the builders, Elephant 1.2.1, and Stella 2022.

**Matched exactly:** 53,432 core-hours at 19 draws (fast 4,495 + slow 138 + Cossart 48,799);
278,409 at 99; 46 of 358 unpriced; 47 of 144 slow (jISI 24, ISI-D 23) and 2 of 144 fast;
1,261–1,827 of 2,630 ROIs (47.95–69.47%); fast 47.63/0.159 ms = 299.8x, slow 4.144/0.152 = 27.3x;
7 fast radii including 20.0; coverage 1.000 vs 0.505; `recruited = 0.5 * n_roi` hardcoded at
`build_surrogate_report.py:603,:639`; Cossart 57 vs 42.88 and fast 3 vs 4.56; all six Holm floors
to six decimals; 260/520 and 220/440; every cell of the probe keystone table; all five destruction
rows; 654 required pairs; 248 rows / 126 stamped / 1 reason; seeds 1–4 at P = .34/.455/.705/.785.

**Design-record check, no defect:** `meta.json` gives DI 10 mice/17 recordings, MALE 12/22,
ORX 12/25, OVX 10/20 = 44 mice / 84 recordings; `skipped: []`, `n_recordings_loaded` = `n_recordings`.
Nothing silently dropped. Non-independence handled by mouse-grouped splits and folds.

| # | location | issue | sev |
|---|---|---|---|
| 1 | discriminator table, `fast/negative` | "not flagged" is false — P = 0.035, `significant=True`; this flag voided 126 fast rows | **high** |
| 2 | sources table row 4 | `docs/reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md` does not exist anywhere under `C:\Users\defazio\bugarach` | **high** |
| 3 | "the night's 100 splits and 99 draws" | K actually ranges 19–99; the whole joint-ISI family ran at 19 | med |
| 4 | within-scope paired floors 0.260 / 0.537 | hold only at maximum K; at K=19 the floor is 1.000. Conclusion strengthened | med |
| 5 | "differ on 5–7 of 13" | does not reproduce. Recomputed 4–8 pooled over scopes, dist {4:3, 6:59, 7:2, 8:51}; 6–8 at scope `all`. No tolerance (0, 1e-9, 1e-6) yields 5–7 | med |
| 6 | "roughly 480 splits and 960 draws" | recomputed **520 and 1,040** | med |
| 7 | "the probe is used only for… two recordings at three draws" | stage2/stage2b ran **84 recordings, 44 mice, 519/520 draws**; only Stage 1 used `--limit 2` | med |
| 8 | discriminator ⚠ | "a control that detects nothing gets ICC ≈ 0… the fast negative reads powered for exactly that reason" — that control *did* detect. ICC is within-mouse correlation of correctness, floored at 0 in `within_mouse_icc` | med |
| 9 | destruction table | headed "Medians" but four of five rows are a median over **one** cell | med |
| 10 | sources row 1 | none of the five named files is at the path given; they are in `steps_excluded/` and `cossart/` | low-med |
| 11 | sources row 3 | `score_cell` at `0dc6356` corrects Holm **within** scope (family 13); the run's numbers are family 65. The cited code cannot produce the cited floors | low-med |
| 12 | "cuts the required sample four- to fivefold" | exactly fivefold for `steps_excluded`; Cossart has one scope, so it buys nothing there | low |
| 13 | probe table, five scope rows | `all` is the union of DI/MALE/ORX/OVX — not five independent confirmations | low |
| 14 | sources line | Holm 1979, Tarone 1990, Phipson & Smyth 2010, the Elephant DOI/RRID and eLife 11:e78116 not checkable from this machine; Gerstein 2004 not on the shelf, so the attribution rests on `lit_needed.md` metadata and Elephant's citation tag | low |

---

## Role 2 — Citation & reference validator, "DOI or Die."

`GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch`

**No fabricated bibliographic metadata.** Every named work resolves; every locator (volume, issue,
pages, article number, DOI, RRID, accession) is correct. That is the zero-tolerance check and it
passes.

| # | issue | sev |
|---|---|---|
| 1 | The cited review record **does not exist** — all 60 files in `docs/reviews/` listed, whole tree searched, darkroom searched, `git log --all --diff-filter=A` returns nothing | **blocking** |
| 2 | "Louis, Borgelt & Grün (2010, ch. 17)… still unread — paywalled" is **false**. Open full text at `portal.g-node.org/advanced-course-2019/_media/materials:chapter_17.pdf`; fetched and read during the review. pp. 359–382 confirmed from the PDF's running heads. Its abstract is this screen's premise almost verbatim | major |
| 3 | The dither root is one paper further back **and the cited paper says so**. Gerstein 2004 p. 205 credits Date et al. (1998), Hatsopoulos et al. (2003), Abeles & Gat (2001). **Date 1998 is already on this project's shelf** and `lit_needed.md` calls it "the root of the dithering lineage" | major |
| 4 | The attribution to Gerstein is overstated. He says flat dither "does change the original IH by **adding** short intervals and lowering the peak" — not intervals *shorter than any real one*. That stronger support-violation form is bugarach's own measurement (0 of 543 real fast windows vs 29.5% dithered) | major |
| 5 | Gerstein 2004 was cited from a paper the project did not hold; `lit_needed.md` still lists it under Open. Fetched during review from `ane.pl` (open access, 5 pp.) | major (process) |
| 6 | Elephant cited by **concept DOI** (`10.5281/zenodo.1186602`), which always resolves to the newest release, while every claim is 1.2.1-specific and `pyproject.toml` pins 1.2.1. Version DOI is `10.5281/zenodo.20629764`. RRID:SCR_003833 confirmed | major |
| 7 | Two entries carry no locator while every other does: Amarasingham et al. 2012 (*J Neurophysiol* 107(2):517–531, doi:10.1152/jn.00633.2011, on the shelf) and Friedman 2003 (PHYSTAT2003 SLAC, eConf C030908, SLAC-PUB-10325) | major |
| 8 | Lopez-Paz & Oquab cited as arXiv preprint; it is ICLR 2017 and the shelf files the published version | minor |
| 9 | The premise sentence has no citation and three citations have no sentence. **NCE is dropped entirely from v2** — Gutmann & Hyvärinen 2012, *JMLR* 13:307–361, is on the shelf and was found by role 2 of the 2026-09-10 review | major |
| 10 | "where Stella bin at 1 ms" credits the wrong paper — Stella state it as an inherited default attributing to Gerstein 2004 and Louis et al. 2010; in this codebase it comes from Elephant's `JointISI` defaults | minor |
| 11 | The square-root row argues from Elephant's code when the author's own words are stronger — Gerstein introduces the sqrt recipe *because* it changes the result: "no obvious mathematical foundation, but because of the good IH fits we have used it extensively" | minor |
| 12 | **The Cossart lab's data is credited; its method is not.** `detectors/cicada.py` declares itself a port derived from CICADA (`cossartlab/cicada`), separately citable — Zenodo 10041434, Denis, Dard, Quiroli, Cossart, Picardo | major |
| 13 | Second document in a row carrying "nobody was asked" — the 2026-09-10 record already listed this as residual #3. Two days on, the emails to Grün's group are unsent | minor / residual |

**Verified clean:** Holm 1979 *Scand J Statist* 6(2):65–70 · Tarone 1990 *Biometrics* 46(2):515–522
PMID 2364136 · Phipson & Smyth 2010 *SAGMB* 9(1) Art. 39 doi:10.2202/1544-6115.1585 PMID 21044043 ·
Gerstein 2004 *Acta Neurobiol Exp* 64(2):203–207 (**pages confirmed off the PDF; Elephant's docs
misprint it as 203–208 — the document is right and Elephant is wrong**) · Stella 2022 *eNeuro* 9(3)
PMID 35584914, corroborates the short-interval claim · DANDI:000219 attribution exactly right
(Dard contact, Picardo, Cossart, INSERM, CC-BY-4.0) · Dard et al. 2022 *eLife* 11:e78116, Cossart
and Picardo co-corresponding at Turing Centre / Aix-Marseille / INSERM INMED U1249 · commit
`0dc6356` exists · both darkroom run folders exist.

**Forward trace on the wrapped tool (required):** Elephant is Grün's group's, and what that group
did next is **Stella, Quaglio, Torre & Grün (2019), 3d-SPADE, *Biosystems* 185:104022** — the
applied paper that selected joint-ISI dithering as SPADE's surrogate — plus **INM-6/SPADE_surrogates**
and **INM-6/SPADE_applications**, which run substantially the comparison this screen runs. None
appear in v2. ⚠ Closest prior art for the wrapping; the screen is unsituated against it.

**Where it stopped on the circular shift:** searched, not resolved. Malvache et al. 2016 *Science*
353(6305):1280–1283 and Villette et al. 2015 *Neuron* 88:357–366 are on the shelf but main-text
only, both deferring the null to supplementary methods we do not hold. `detector_history.md`
already names Cossart, Aronov & Yuste 2003 and Mao et al. 2001 behind it — a lead the residual does
not mention. Narrow the residual accordingly.

**Bonus, resolved during review:** Pazienti, Diesmann & Grün (2007) BVAI, LNCS 4729:428–437,
doi:10.1007/978-3-540-75555-5_41 (note ch. 17's reference list prints it as two authors); Pazienti,
Maldonado, Diesmann & Grün (2008) *Brain Research* 1225:39–46 (**Maldonado**, whom "Pazienti et al."
hides); Grün, Borgelt, Gerstein, Louis & Diesmann (2010) *BMC Neuroscience* 11(Suppl 1):O15,
PMC3090783 — the free abstract form of the chapter-17 premise.

**Not searched — residual, not an absence of prior art:** the nonlinear-dynamics surrogate-data
literature (Theiler et al. 1992 and descendants), whose "destroy one feature, preserve the rest"
framing is the one v2's premise is written in. If one field is searched next, it should be that one.

---

## Role 3 — Consistency auditor, "Cross-Examiner."

`GRANT 3 ok — Read, Grep, Glob`

| # | issue | sev |
|---|---|---|
| 1 | **Three of five discriminator rows are probe numbers** in a document whose own provenance section says every figure is production. Fast positive (1,669 · 0.112 · 5.14 · 89) matches `stage4_steps_excluded` exactly (icc 0.11222, DE 5.14451, 89); production positives give 0.133/5.91/102, 0.135/5.99/104, 0.055/3.05/53. Slow (0.109·5.03·87) = probe; production `slow/controls/pos_J11.2.json` = 0.1228/5.534/96. Events (0.004·1.16·18) = probe; production `pos_J32` = 0.0316/2.328/36. Rows 2 and 5 *are* production. One table, two provenances, unlabelled | **high** |
| 2 | **The fast negative control did flag** — `p_value 0.035`, `significant true`, probe `negative_flagged: true`, verdict `UNUSABLE`; `discriminator.csv` stamps every fast row with it | **high** |
| 3 | **A 20-seed production rerun exists and is not used.** `fast/controls/negative_seeds.json`: `n_seeds 20`, `flag_rate 0.05`, seed 0 significant, 1–19 not → **0 of 19 fresh seeds**. The five-seed framing is the probe's | **high** |
| 4 | "The probe… on two recordings at three draws" contradicts results 50 lines later — `stage2` meta: `n_recordings_loaded 84`, K 519, 259 splits; `stage2b`: 84, 520, 260. Only stage 1 ran two recordings | **high** |
| 5 | **Reserved-word collision**: *family* is defined as the Holm family, then used five times as "the joint-ISI family" meaning a set of generators | med |
| 6 | "roughly 480 splits and 960 draws" does not follow from the document's own floors — S ≥ 520, D ≥ 1040. At 480/960 both land on 0.0541. Same off-by-one the document exists to expose | med |
| 7 | **The slow negative control is missing** from a table that otherwise enumerates control × stream — and it is the only clean one on `steps_excluded` (830 pairs, P = 0.415, ICC 0.0, DE 1.00). Its absence weakens decision 3 | med |
| 8 | "cuts the required sample four- to fivefold" — no fourfold anywhere; 65→13 and 1,300/2,600→260/520 are exactly 5x, and Cossart has one scope | med |
| 9 | Two per-stream rates aggregated over unequal, undeclared populations. Fast has exactly **2** scored cells; slow has 47 spanning ~10x. 4.14 ms matches no single cell | med |
| 10 | "At the night's 100 mouse splits and **99 draws**" — `cells.csv` K is 99 for the cheap class and **19** for every joint-ISI/ISI-dither cell. At 19 the paired floor is 1.000 | med |
| 11 | **Dead cross-reference** — the review record exists in neither the worktree nor the primary checkout. It is a bare code span, not a link, so `tests/test_index_resolves.py` cannot catch it | med |
| 12 | Provenance path is one directory above the files; each exists **twice**, under `steps_excluded/` and `cossart/`, with different contents. `control_power.csv` and `summary.json` unlisted | med |
| 13 | The "3 of 6 fast radii saturated" row marks a claim **False** then restates its substance; only the denominator's completeness is contested | low-med |
| 14 | "the 20% arm… was never reported" vs the table three sections earlier which reports it at floor 3. `meta.json` `destruction_status`: p0.2 ran ok at floors 3, 4 and 6; only K8 is absent. The reassigned "0.63 → 0.05" pair is a 3 → **6** scan, not 3 → 8 | low-med |
| 15 | Three labels for one population of 13 ("statistics", "checks", "the checks"); destruction caption implies one basis where four of five rows are single cells | low |
| 16 | `events` is Cossart's single stream but is never defined; every other table keys on folder, this one on stream | low-med |
| 17 | **No new term reaches the glossary.** GLOSSARY's *Surrogate vocabulary* section, added 2026-09-10 for this screen, still lacks scope, family, band, paired, twin, destruction/retained, saturated, draws. *twin* and *retained* are defined and never used | low-med |
| 18 | Cross-document disagreement on one total: v1's withdrawal notice says **278,415**, this says **278,409**, both citing production | low |
| 19 | "the three generators exclude a third to a half" — never names them; only `joint_isi` and `isi_dither` carry non-zero `not_estimable_rois` | low |
| 20 | **No table in the document is numbered or named**, and prose refers to them positionally ("unless the table says otherwise"). The superseded plan numbers Table 1–5 and Figure 1 | low-med |

**Checked and correct, do not re-litigate:** 47 of 144 slow (24+23) and 2 of 144 fast; 358 dropped
= 239 + 119; 46 unpriced = 23 + 23, leaving 312 priced; every Holm floor and every requirement;
the probe's 0.0498/0.0499 and 0.0500/0.0500 matching `stage2b`/`stage2` `meta.json` field-for-field;
the 0.0998 doubling; 13 statistics on `steps_excluded`, 11 on `cossart`; all five destruction rows
including recomputed uniform-dither medians (0.94759 → 0.42444; 0.654085); 19 draws / 200 surrogates
vs Cossart 5 / 20; 654 pairs; 1,669 / 830 / 1,375 / 671 pairs at 44 and 32 mice; 2,630 ROIs the same
denominator on fast and slow; the fractional-*K* residual; step 0's claim about the shipped report
(`not_estimable` appears 0 times in `report_steps_excluded.html`); scope order DI, MALE, ORX, OVX,
all matches the project's canonical order.

---

## Role 4 — Adversarial reviewer, "Reviewer 2."

`GRANT 4 ok — Read, Grep, Glob, Bash`

**What survives attack, stated so the ledger has it:** the `correction_reach` arithmetic is correct
and could not be broken. All six floors reconcile exactly (65x1/101=0.644; 13x1/101=0.129;
13x2/100=0.260; 11x1/101=0.109; 11x2/41=0.537), as do 260/520 and 220/440, the destruction medians
including freeze-half, 47/144 and 2/144, the 300x/27x ratios, 2,630 ROIs, 358 dropped, 46 unpriced,
53,432 core-hours, and "0 of 4 fresh seeds". The strict `<` in `smallest_n` is right and load-bearing.

| # | issue | sev |
|---|---|---|
| 1 | **The family size is a free parameter and the document never varies it.** It tests m=65 and m=13 only. Band floor is 1/101 = 0.00990, so a **pre-declared family of ≤5 flags on the night's existing data** (5/101 = 0.0495 < 0.05; `smallest_n(5,0.05)` = 100 splits, and the night ran exactly 100). Paired supports m≤2. So "could not have produced a corrected flag at any setting" and "Only a new run can flag" are **false as stated** — and they suppress the one remedy that costs nothing. The whole "buy a bigger sample" recommendation rests on this | **blocking** |
| 2 | **The discriminator table is from the probe, not production**, contradicting the document's own rule two sections earlier. This is the **same defect that withdrew the previous draft**, in the section titled "with the power stated correctly" | **blocking** |
| 3 | The two most prominent numbers price runs the document itself proves cannot flag (53,432 at 19 draws, 278,409 at 99; the paired floor at 99 draws is 0.26). Meanwhile step 3 recommends 520 draws, whose cost is given **nowhere** | major |
| 4 | **"Do-nothing stays at 0 of 13, which is the control behaving"** — a check that cannot fail, reported as reassurance. `do_nothing` returns its input (`surrogates.py:732`), so delta ≡ 0 and `band_p` = 1.000 identically. A sign error making every candidate flag spuriously would leave do-nothing at 0/13. It has **no power** against the false-positive mode it appears to exclude. The control with actual power is already in `yardsticks.csv` — `neg_heldout_band` ≈ 0.05 on real held-out halves — and is never mentioned | major |
| 5 | "both from the run's own projections" — 278,409 is **not** a second projection; it is 53,432 x 99/19 exactly. And linear scaling contradicts the run's own `why`, which records "between about 40 minutes per cell… and 2.7 hours" — a **4x spread** the single figure hides | major |
| 6 | "The probe is used only for… two recordings at three draws" is **false and load-bearing** — it is the sentence licensing trust in the probe boundary. stage2/2b: 84 recordings, K 519/520, 259/260 splits. stage4: 84 recordings, 1,669 pairs, 44 mice | major |
| 7 | The 260/520 vs 259/519 contrast **carries no data** — raw counts are identical at both sizes; only Holm's threshold moves. The flip is derivable from `correction_reach` without running anything, yet is presented under "What the probe established" | moderate |
| 8 | "46 of the 358 dropped cells carry no cost projection" — **false for 18 of the 46**, which carry an explicit projection in their own `why`. They lack the *phrase* "core-hours". A parsing artefact shipped as a data limitation | moderate |
| 9 | Step 0 acts on evidence the document calls insufficient — it lists correcting the "void" verdict as a minutes-long cleanup, while the same section says five seeds cannot separate α from 10α | moderate |
| 10 | **No figures at all.** The two central quantitative objects are a cost-vs-J extrapolation (`J^-1.82` fitted on 4 points, carrying the 53,432) and a retention-vs-K dose-response across 17 generators x 2 arms. An unplotted 4-point power-law extrapolation driving a 53,000 core-hour ask is exactly where an extrapolation hides | moderate |
| 11 | "fast: 47.6 ms… ~300x", "slow: 4.14 ms… ~27x" — ratios of medians with no n and no spread, and the fast one is **n=2 cells**; slow spans 0.000913–0.020415 s, a **22x internal spread** | moderate |
| 12 | Destruction medians with no n and no dispersion; the "freeze-half (graded)" row — the only one showing intermediate values — is **one cell**. And the "20%: floor 3 → 8" header is false: **no generator has any value at floor 8** there | moderate |
| 13 | Step 2 is called "code only", but `tests/test_surrogate_discriminator.py:308–312` asserts `design_effect == 1+(pairs_per_mouse-1)*icc` and `powered == (n_mice >= required_mice)` — the suite currently **certifies** the circularity the step must remove. Those assertions must flip, not be supplemented | moderate |
| 14 | "sizing for one is roughly 480 splits and 960 draws" reconciles with neither floor: one discordant split → n ≥ 520; one discordant draw → K ≥ 780 (its reading) | moderate |
| 15 | "One discordant draw lifts the adjusted *P* to 0.0998" mixes the two yardsticks — 0.0998 = 2 x 0.0499 doubles the *paired* floor, but doubling is right for the band | minor |
| 16 | α never given numerically despite "past α"; ICC, design effect, effective n, core-hour and "pairs" undefined; DI/MALE/ORX/OVX never expanded; τ undefined | minor |
| 17 | "The test needs 654 independent pairs" — depends entirely on `MIN_EFFECT=0.55` and `POWER=0.8`, neither stated | minor |
| 18 | "46 further cells unpriced" attributed to the joint-ISI decision but scoped to both folders; only ~19 are joint-ISI/ISI-dither, the rest `operational_time` (18) and others | minor |
| 19 | Decision 2 is internally inconsistent — the option is "add `scored_share`" (a share), the recommendation "publish the excluded count" (a count); and the stated cost sits against the residual "No verdict rule reads it today" | minor |
| 20 | Band and paired are **not independent** — same real value, same data, different reference distribution. Reporting both reads as two confirmations | minor |
| 21 | "47.9–69.5%: 1,261–1,827 of 2,630" pools three generators that differ systematically (`operational_time` ~48% vs `joint_isi`/`isi_dither` ~62–69%) | minor |
| 22 | **The positive control is the one candidate the statistic set was built against** — uniform dither's defect is manufactured short within-ROI intervals, and the statistics are largely interval-density measures. Detecting it demonstrates capability against the single failure mode the instrument was designed around | minor |

**The two it would not let through:** #1 and #2.

---

## Role 5 — Line editor, "Kill Your Darlings."

`GRANT 5 ok — Read, Grep, Glob`

⚠ **`murderboard_prose.sh` DID NOT RUN.** Two independent reasons, both declared: the script does
not exist in either tree (`tools/` holds only `murderboard_agents.py`, `murderboard_freshness.sh`,
`murderboard_revendor.py`, `murderboard_roster.sh`), though `tools/murderboard_revendor.py:87,105`
lists it in its vendoring manifest and `murderboard_freshness.sh:127-128` names it; **and** role 5's
grant carries no execution tool, so the role's own instruction ("run the tool, do not describe it")
is unsatisfiable under the grant it is issued with. Everything below is hand-counted and
Grep-derived. *(Note: `2026-09-10-coordination-without-labels_2026-09-10.md:249` declared this as
`GRANT 5 MISMATCH — missing Bash`; that reading is wrong — Bash was never in the grant — but it is
the third run in a row where this role's mechanical half went unexecuted.)*

**Banned-construction list: 0 hits** on all vocabulary (delve, leverage, robust, seamless, crucial,
landscape, tapestry) and all four rhetorical forms (*not just X but Y*, *it's not about A it's about
B*, *it's worth noting*, *"In today's ___"*). 18 em-dashes, all mid-sentence qualifiers; the document
closes on residual warnings, not an uplift. Secondary LLM-register sweep (utilize, myriad, navigate,
underscore, paradigm, ecosystem, streamline, deep dive, that said, in essence): 0 hits.

**Passage test: the document does not have a length problem.** No block exceeds 86 words, nothing
recaps, no throat-clearing, no section previews itself, and the closing section is residual risk
rather than a summary. Every finding below is a *precision* finding, not a *cut* finding.

| # | issue | sev |
|---|---|---|
| F1 | "Only a new run can flag." — the document's single most important sentence sits **last** in its paragraph, after two sentences of qualification | major |
| F2 | British spellings: "artefact" (27, 110), "normalised"/"normalisation" (109); `writing_conventions.md` §American English is explicit and dated | minor |
| F3 | Indexing, not naming: "(below)" (27), "see decision 1" (166), "before step 1" (168) — the exact form `writing_conventions.md` forbids | major |
| F4 | ICC never expanded; design effect and effective n undefined; **α never defined and never given its value**, yet "past α no corrected test can fire" is the central argument | major |
| F5 | ISI never expanded anywhere; DI/MALE/ORX/OVX bare codes; Terms defines "scope" as "the four mouse groups" without saying which four | minor |
| F6 | The probe/production distinction is asserted three times (lines 5, 6, 39) | minor |
| F7 | Terms defines `twin` and `retained`, **neither of which the document ever uses again** — `twin` appears only in its own definition. The purest darlings here | major |
| F8 | "Neither zero-reader is a test" coins a term at the moment of use and never defines it | minor |
| F9 | "The screen exists to find a replacement, and shortlists nothing by design" — compressed past the point of meaning | major |
| F10 | "sizing for one is roughly 480…" — "one" refers back across a sentence boundary | minor |
| F11 | A 42-word sentence carrying three facts (248 rows, one reason, 126 stampings, the mechanism) | minor |
| F12 | One sentence carries a recommendation *and* a retraction joined by "and" | minor |
| F13 | "revisits your 2026-09-10 ruling" — a date standing in for content | minor |
| F14 | "the plan" referenced three times, never named or linked, while the only link is to the withdrawn predecessor. The file exists at `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` | major |
| F15 | "The keystone is one candidate at one radius on one stream" — *keystone* has no referent in this document | major |
| F16 | **One glyph, three meanings**: "7 → 7" (raw→Holm), "floor 3 → 8" (two settings), "0.63 → 0.05" (a value moving) | major |
| F17 | "*no value at floor 8*" repeated verbatim five times in one column — 25 words saying one thing | minor |
| F18 | "3 of the 6 candidate radii saturate… excluding the 20-second shipped-dither radius" — "excluding" is ambiguous between two readings | major |
| F19 | Bare counts without units: "0 of 13", "differ on 5–7 of 13" | minor |
| F20 | **Four labels for one object**: "the overnight run", "the night's data", "the night", "production" — in a document whose whole point is a probe/production distinction | major |
| F21 | "the gate now refuses less" — "the gate" introduced with a definite article, never identified | minor |
| F22 | "where Stella bin at 1 ms" — subject-verb disagreement, inconsistent with line 61's "Stella et al. (2022)" | nit |
| F23 | `` `powered` `` quoted two ways in three lines | nit |
| F24 | The title promises "what the night bought" and no section delivers it | minor |

**Clean:** no throat-clearing, no self-previewing section, no closing recap, no decorative humour;
first person used consistently and concretely; short sentences, active verbs, concrete nouns; the
document names what it does not know in eight explicit residual bullets — including, unusually, a
residual about its own review being unconverged.

---

## Role 6 — Methods / domain expert, "RTFM."

`GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch`

Grounded first in Elephant 1.2.1 `spike_train_surrogates.py` (`JointISI.__init__`,
`joint_isi_histogram`, `bin_width`, `_window_cumulatives`, `_get_dithering_step`), the repo's
surrogate modules and builders, the production and probe folders, and from the shelf Stella 2022,
Louis 2010, Amarasingham 2012 (extracted with `pdftotext`). **Gerstein 2004 is not on the shelf.**

| # | issue | sev |
|---|---|---|
| F1 | **The discriminator table is probe data, not production** — the exact defect this draft was written to repair. Doc fast 0.112/5.14/89 = `stage4_steps_excluded/discriminator_probe.json`; production `control:pos_J2.5` reads acc 0.7645, **ICC 0.13294, 102 mice**. Slow: doc 87, production `pos_J11.2` **96**. Events: doc 18, production `pos_J32` **36**. **Production numbers exist and are worse, so the under-powering is understated.** ICC rises monotonically with *J* (0.0035 at J=0.1 s → 0.133 at J=2.5 s), so production carries one row per radius and the table needs a *J* column | **critical** |
| F2 | **The verdict is inverted** — that control's accuracy 0.5385, **P = 0.035, significant = True**, stamped verbatim on all 142 voided fast rows. The ⚠ mechanism is also misapplied: ICC 0 means no within-mouse clustering of correctness, not non-detection. The row that actually illustrates the point is the **slow** negative (acc 0.506, P = 0.415, ICC 0.0, powered True) — which is missing from the table | **critical** |
| F3 | "sizing for one is roughly 480 splits and 960 draws" — **wrong, and unsafe-direction wrong.** Band 2/(n+1), paired 4/(K+1); Holm x13 < α needs **n ≥ 520 and K ≥ 1040**. At 480/960 the adjusted *P* is 0.0541 both ways — *neither flags*. `smallest_n(26,.05)=520` and `smallest_n(52,.05)=1040` give the right answer; these numbers did not come from it. The identical boundary error `smallest_n`'s docstring was written about | major |
| F4 | "differ on 5–7 of 13" — the 23 pairs is right, **5–7 is not**. At scope `all`: **13 of 13 in 20 pairs, 9 of 13 in 3**. `paired_p` differs on 1–5, `band_flag` on 0–1, `real` on 6–8 (which should be 0 — same real recording, so the not-estimable mask moves with `use_sqrt`). No metric yields 5–7. The conclusion is *strengthened* | major |
| F5 | **The 260/520 demonstration is one radius on one stream, and the radius is not stated.** `stage2b` ran only `do_nothing` and `uniform_dither__J2.5s`, fast only — the **largest** fast radius, where the positive control is strongest (production sweep: acc 0.523 at J=0.1 s → 0.764 at J=2.5 s). Step 3 buys 260/520 for "the cheap class", most of which sits at small *J*. Also `stage2/2b` ran `neg_reps: 3` (production 20) and `skip_destruction: true` | major |
| F6 | "The probe is used **only**… on two recordings at three draws" describes `probe-surrogate-screen/{steps_excluded,cossart}` only. It does not describe stage2/2b (84 recordings, 519/520 draws), stage3 (4 recordings) or stage4 (84 recordings, 44 mice). Understates the probe's scale by ~2 orders of magnitude, in the sentence carrying "that distinction is what the withdrawn draft got wrong" | major |
| F7 | Citation defects: **(a)** Gerstein 2004 not on the shelf and unreachable from here, so the claim rests on secondary description. **(b)** Stella 2022 does not "corroborate" Gerstein — its Significance Statement claims discovery, and its defect is spike loss under binning plus altered ISI distributions, adjacent to but not identical with the claim. **(c)** Sources omits the papers behind three implemented generators, all on the shelf and named in `surrogates.py`: Louis, Gerstein, Grün & Diesmann 2010 (*Front Comput Neurosci* 4:127), Date, Bienenstock & Geman 1998, Harrison & Geman 2009. The only "Louis" in the document is the unread book chapter — a reader will conflate them. **(d)** Amarasingham 2012 does **not** state the doubled rank *P* `2·min(...)/(K+1)` that `paired_p` implements; `report_summary.html` credits Dwass 1957 / Barnard 1963 correctly and this document does not | major |
| F8 | Step 1's diagnosis is **exactly right** (`bw = J/2.0`; Elephant `bin_width = truncation_limit/n_bins`; `_max_change_index = floor(J/bw) = 2`; displacement ∈ {−2,−1,0,1,2}xJ/2) but the **prescription is not executable**: Stella's 1 ms is meaningful only as a *ratio* to their 15–25 ms dither, and every Elephant call here runs in frame units on 0.1 s frames, so 1 ms is 1/100 of a frame and cannot be represented. Restate as ≈ J/15 to J/25, floored at one frame | major |
| F9 | Both cost medians are right but **cost-selected** — cells were dropped *because* projected expensive, so survivors are not comparable across streams. The fast median rests on 2 of 144 joint-ISI cells | moderate |
| F10 | Core-hour figures right and correctly attributable (recomputed 53,435 @ 19, 278,427 @ 99; **313 of 315 priced dropped cells are joint-ISI/ISI-dither — 100.0% of the cost**), but the **unpriced** cells are not mostly joint-ISI: of ~43–45, **18 are Cossart `operational_time`**, 3 other, only ~22 joint-ISI | moderate |
| F11 | "46 of the 358 dropped cells carry no cost projection" — 358 ✓, but the 46 is off by one to three depending on the rule (45 lack "about N s per draw"; 43 lack any "N s per draw") | minor |
| F12 | "Medians, fast stream" — only `uniform_dither` has 6 cells; the other four have **exactly one row** per (participation, K) | minor |
| F13 | "a tenth of the shipped ensemble" — 20 is a tenth of the **200** used for `steps_excluded`, but "shipped" elsewhere in this repo means the assessor's default, which `assess.assess_coactivity` documents as **1000**. Against that, a fiftieth | minor |

**Checked and correct, do not re-litigate:** every Holm floor reproduced with `ss.correction_reach`;
260/520 and 220/440 including the strict-inequality boundary; the probe flag table exact, including
MALE band 7→6 and ORX paired 9→8, and the 0.0498/0.0499 minima; one discordant draw → 13x4/521 =
**0.0998** ✓; **the Elephant square-root claim is correct as stated** — `np.sqrt` applied to the
histogram *before* `gaussian_filter` and before `_normalize_cumulative_distribution`, which is affine
per cumulative slice and cannot undo it; joint-ISI reach 47 of 144 slow (24+23) and 2 of 144 fast;
ROI exclusion 47.9–69.5%, 1,261–1,827 of 2,630; 7 fast radii and 3 of 6 saturating (expected 15.5,
15.5, 8.61 > K_hi 8); every destruction median, both arms, and the 20% arm's absence at floor 8
(`planted_visible = False` on all 123 rows); fractional *K* (Cossart 0.1x566 = 56.6 → 57 vs
283x5/33 = 42.88; fast 0.1x31 = 3.1 → 3 vs 15.5x5/17 = 4.56); 358 dropped; discriminator sizing
(`required_pairs() = 654`, effective n = pairs/deff, required mice = ⌈654·deff/pairs-per-mouse⌉);
"248 candidate rows… stamped on 126" exact; five seeds (seed 0 P = 0.035 the discovery run, seeds
1–4 P = .34/.455/.705/.785); **"Neither zero-reader is a test" is sound** — `circular_shift` calls
the assessor's own `assess.circular_shift_trains`, and a circular shift of a uniform i.i.d. train is
again uniform i.i.d.; the gate refuses on family 13, not 65 (`build_surrogate_screen.py:822`).

**Method note for step 2:** the `seed` argument drives folds, the negative control's
pairing/orientation **and** the permutation null jointly, so the five runs are not clean replicates
of one null — worth naming when the multi-seed control is rebuilt.
