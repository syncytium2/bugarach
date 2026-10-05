GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch (plus SubagentHandback, the report channel; no editing tools held)

# Role 2, DOI or Die: blind round 3 on <worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md (run/final-parameters @ 0638de5)

**Summary:** 6 findings: 2 major, 4 minor, and 2 residual ⚠. The PR numbers, commit shas, run-record paths, ADR quotes and code references all check out. The problems are in how three sources are paraphrased or applied, and in the SPIKE-synch attribution around Decision 1.

## Findings

Each finding gives location · issue · severity · fix · verified.

**1. Decision 1, the "strict rule" list (lines 41–44)**
- **Issue:** The page says the four proposals "meet the runbook's strict rule", and words that rule as "every budget *that was checked* passes". The runbook's rule is stricter than that:
  - Phase 4 defines adoptable as "the gain interval is above zero, every budget passes, and the proposal is bracketed".
  - "What final means", item 3, says "confirmed on held-out seeds and on fresh seeds, inside every budget".
  - The words "that was checked" are not in the runbook. By the page's own lines 102–104, the precision swing is not recorded on held-out seeds and the close-events test is not run on fresh seeds. So the four meet a weaker rule, and the page credits that weaker rule to the runbook.
- **Severity:** major. It is the rule Decision 1 asks Tony to rule under.
- **Fix:** Say the four meet the runbook's rule except for budgets not measured on some seed sets (named in Table 2), and say that exception is the report's relaxation, not the runbook's.
- **Verified:** yes, against <worktree>/docs/handoffs/2026-09-25-overnight-final-parameters.md, lines 19–26 and 139–140.

**2. Decision 5, the `C_min` plateau (lines 252–253)**
- **Issue:** The page says slow SPIKE-synch's `C_min` of 0 "sits on a measured plateau: every value from 0 to 0.03 gave identical calls on seeds 1–48 (`bench_slow.py`)". The source does say that (src/bugarach/bench_slow.py lines 278–281), but it measured something else:
  - It is the 2026-09-21 adoption note, made on the bench before ADR-0008. That bench still had the elevated-rate stretch inside the planted recordings, and `min_n` was still searched.
  - It was measured at `dt` 0.1 s and `tau_max` 0.5 s.
  - The proposal it is offered for runs `dt` 0.00625 s and `tau_max` 1 s under the floor. The page itself says, two lines later, that the `dt` change alters what the floor-set minimum counts.
- **Severity:** major. It is cited as evidence in a decision.
- **Fix:** Attribute the plateau to its conditions ("measured 2026-09-21 on the bench before the floor, at `dt` 0.1 s"), or re-measure it at the proposal.
- **Verified:** yes, the source text and conditions. Whether the plateau holds at the proposal is not verified.

**3. Decision 1, the Decision 1 table (line 54) and "the adaptive coincidence window" (line 61)**
- **Issue:** The table gives `tau_mode` as "adaptive → fixed". The code has no value "adaptive": GLOSSARY lines 50–55 retire the bare word, and the code refuses `tau_mode="adaptive"`. The shipped value is `isi_adaptive` (bench_combined.py line 224, and the page's own Table 1, line 382). Line 61 also uses bare "adaptive".
- **Severity:** minor.
- **Fix:** Write `isi_adaptive → fixed` in the table, and "ISI-adaptive coincidence window" in the prose.
- **Verified:** yes.

**4. Decision 1, "(Kreuz 2015)" (line 62)**
- **What checks out:** The glossary quote is exact (GLOSSARY line 60).
- **Issue:** Decision 1 asks for "a changed methods citation", but "Kreuz 2015" is ambiguous. Two 2015 papers introduce SPIKE-synchronization:
  - Kreuz, Mulansky & Bozanic 2015, "SPIKY: a graphical user interface for monitoring spike train synchrony", J Neurophysiol 113:3432–3445, doi:10.1152/jn.00848.2014;
  - Mulansky et al. 2015.
- **The root:** The ISI-adaptive coincidence window, which is the thing being turned off, goes back further than 2015. It comes from event synchronization: Quian Quiroga, Kreuz & Grassberger 2002, Phys Rev E 66:041904.
- **Where I stopped:** The SPIKY paper's own page returned HTTP 403, so the chain is verified one step short of it. I read the lineage from the reference list of Mulansky & Kreuz, "PySpike", arXiv 1603.03293 v2, which gives τ = ½·min of the four surrounding ISIs and cites both 2015 papers and the 2002 paper.
- **Severity:** minor.
- **Fix:** Give the full citation. For the naming ruling, name the 2002 origin of the adaptive window and the 2015 SPIKE-synchronization papers.
- **Verified:** yes, one step short of the paywalled or blocked primary source.

**5. Decision 1, "No record shows anyone has asked the measure's author about this variant" (line 65)**
- **What checks out:** As far as I can find, this is literally true.
- **Issue:** The sentence leaves out records that bear on it:
  - The project has an open line to Kreuz: Kreuz, personal communication, 2026-04-23; a mail about PySpike's `max_tau` cap sent 2026-08-28 and one quoted on PySpike PR #89 dated 2026-08-31; and his reply of 2026-09-02.
  - The neighbouring "adaptive" naming question was deliberately closed by Tony on 2026-08-28 without being asked (<worktree>/docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md, item 2).
- **Forward trace:** The authors' own later work, Satuvuori et al. 2017 (the minimum relevant time scale, MRTS), is their sanctioned way to stop the window from tightening. It is the nearest prior art to a less-adaptive variant, and a reader deciding a name should know it exists.
- **Severity:** minor. It carries a residual ⚠ (see below).
- **Fix:** Cite the existing correspondence by date, paraphrased and not quoted (the repo is public). Say that asking is one email on an open thread. Mention MRTS as the authors' own intermediate option.
- **Verified:** yes, the records exist. Whether anything was asked after 2026-09-02 is not verified.

**6. Decision 1, "ADR-0009 says as much" (line 96)**
- **Issue:** The page claims ADR-0009 agrees that "a pass there is no evidence for those two". ADR-0009's Consequences section says less than that. It says the test "partly measures the floor", that a floor-honouring detector "makes few calls there by construction", and that it "still separates detectors by what they call above that floor". It does not say a pass is uninformative.
- **Severity:** minor.
- **Fix:** Write "ADR-0009 expected the test to partly measure the floor", and keep the stronger conclusion as the report's own.
- **Verified:** yes, against ADR-0009 lines 86–89.

## Lead for roles 1 and 3 (not my scope, not verified)

Combined SPIKE-synch ships with `tau_max` = 0.25 s (bench_combined.py line 223), and the proposal keeps it. The ISI-adaptive window equals the cap wherever the surrounding half-ISIs are longer than 0.25 s. At these event rates that is probably most events. If so, shipped and proposal differ mainly in dense stretches. Then "changes what the detector is" is true by definition (per the glossary) but may be small in practice.

## Residual ⚠
- **Nobody was asked (finding 5).** I cannot ask Tony. The main thread should ask him whether Kreuz has been asked about a fixed-window variant, or anything related, since 2026-09-02.
- **Fields searched.** Only the spike-train synchrony literature (the PySpike and SPIKY lineage). The artifact claims nothing is novel or "ours", so I did not run a wider prior-art search.

## Checked and clean
- **PRs #808–#814** (via `gh pr view`): titles, heads and merge commits all match the "What ran" table.
  - #808 merged as 678f19b; #809 merged as b6e40f0, which contains #808 and #810.
  - #811: head 7af68c9, merged as a70b185.
  - #812 merged before #813; #813 merged as 723f1e6.
  - #814: head 879be03 contains #813, and merged as 3153b9b. The two commits have the identical tree (dbaa623…), and 3153b9b is on origin/main.
- **ADR-0006:** the decoy definition matches, including that `distractor` is the code name.
- **ADR-0008:** decision 4's quote "so we can compare" is exact; the stability check, the floor definition (at least 3 ROIs, *J* = 20 s, 1,000 draws, 2 s window, at most once per hour) and the precedent all match.
- **ADR-0009:** decisions 2, 4 and 5, and the "a third to a half" expectation, all match.
- **Runbook:** the guard cap at a quarter of the context is there. No ADR mentions a guard cap: I grepped for "quarter" and "guard".
- **Glossary:** the quotes on the distractor and on ISI-adaptive are exact.
- **FOUNDATIONS §9:** it supports "descriptive only" (treatment effects belong to fireflies).
- **Code references:**
  - `score_bench_candidates.proposal()` behaves as the page describes.
  - `search_all_settings.py` has `--sliding`, `--max-extensions` (default 6), `Evaluator` and `make_admissible`.
  - `train_learned_on_bench.py` takes the flags the page quotes.
  - `bench.context_fits_the_null` exists.
  - `bench_slow.py` calls the close-events allowance "still unsigned", as quoted.
  - The default dataset is `senktide_ttx`, 66 recordings.
- **Darkroom records:** all 15 paths the page cites exist under <darkroom>/bugarach/2026-09-25-final-parameters/. Their READMEs and RUN.md files confirm:
  - the code shas for phases 2 and 3;
  - the pilot built on #808 and #809 merged locally and never pushed;
  - the v2 → v3 difference of exactly 4 locust flips;
  - the real-data counts: 3,072 combinations, 2,696 with different floors, 498 flips.
- **Not checked:** inside 065/bench-floor/bench_floor.json, for whether it records a code commit.
