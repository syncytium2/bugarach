GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I also hold SubagentHandback. It is the hand-off channel, not an editing tool. I held no Edit, Write or NotebookEdit. My only write was one text extraction under <scratchpad>/mb3/.)

# Role 2 (DOI or Die), blind pass: briefing index.html for the 2026-09-25 full-panel night

**Headline:** nothing on the page is fabricated or misattributed at the level of whether the source exists. Every ADR number, part and ruling the page cites is real and says roughly what the page says. There are three medium findings: the name used for ADR-0008's floor, a misstatement of what ADR-0006 rules, and how far "full panel" / "every learned model" reaches. The rest are low.

**What I checked, against the built page `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html` (visible text extracted):**
- Every ADR citation against the ADR text in `<worktree>/docs/adr/`: 0002, 0006, 0008, 0009, and 0010 (its decisions, which it calls parts 1–6, and rulings 1–8).
- The 12 detector and model descriptions against `docs/GLOSSARY.md` axis 2 and the `@register(note=...)` lines in `src/bugarach/learn/nets/*.py`.
- Statistical method claims against `tools/score_bench_candidates.py`, `tools/make_briefing.py`, `src/bugarach/score.py` and `tools/search_all_settings.make_admissible`.
- Bench and budget claims against `src/bugarach/bench*.py`.
- Night facts against 065/README.md, 065/RUN_C.md, 064/README.md and 064/count/README.md.
- Every credit to Tony.
- Upstream origins against `docs/detector_history.md`. I confirmed the Kreuz 2015 metadata on the web.

## Findings

Each finding: location · issue · severity · fix · verified against a source?

1. **Terms, "participation floor", plus Table 6 and the lead-in to the section 2 examples** · The page names ADR-0008's floor "participation floor". GLOSSARY.md says pages meaning ADR-0008's floor should say "event floor" or "the floor (ADR-0008)". It also defines a *different* term, **participant floor** ("the recruitment level below which a detector stops finding events"), one word away from the page's name. A reader who checks the glossary lands on the wrong definition. · **medium** · Rename to "event floor (ADR-0008)" everywhere, including the "floor variant" row and "ADR-0008 on the participation floor" in the ADR row. · verified: yes (GLOSSARY.md, the "event floor" and "participant floor" entries).

2. **"How to read it", Decoys bullet, and Terms "decoy"** · The page says "ADR-0006 rules that such a call is coordination by construction" (Terms: "rules it coordination by construction"). ADR-0006 decision 1 actually rules that *a call where coordination is present is not a false alarm*. "Coordination by construction" is said of the **decoys**, in its Consequences, not of a call. The same Consequences section says no bench, search or training run changes until the objective's ADR. That is why the bench still scores decoy calls as false alarms, and the page never says it. · **medium** · Suggested wording: "Decoys are coordination by construction, so ADR-0006 rules that a call on one is not a false alarm. The bench still scores it as one until the objective's ADR (ADR-0006, Consequences), hence F1 without decoys beside F1." · verified: yes (ADR-0006, Decision 1 and Consequences, first bullet).

3. **Page intro ("every learned model trained") and Terms "full panel" ("every learned model")** · ADR-0010 part 1 defines the learned half of the full panel as four families: chorus_norm, chorus_gain_norm, line (with its orientation channel) and tube, each with its participation changes. The registry holds about 19 architectures (chorus, chorus_line, gauge, tiny, trace, line_length, tube_guard, the tube_ratio variants and others) that were not trained. "Every learned model" overclaims. · **medium** · Write "the four learned families ADR-0010 part 1 names, each with and without participation (8 models)". · verified: yes (ADR-0010 part 1; `ls src/bugarach/learn/nets/`; 064/README.md, "8 learned models").

4. **"What each row is", the `_part` paragraph** · The page says "A name ending in _part is the same network with participation added (ADR-0010 part 5)". Part 5 says *every* learned model trained under the record learns participation. Training the plain variants alongside is a departure from part 5 as written. I could not find the decision (runbook or ruling) that authorised it, and the page does not say the plain rows are comparators outside part 5. · **low** · State that the plain variants were trained as comparators and cite the runbook or ruling that chose that. If none exists, flag it. · verified: partly. The part 5 text is verified; the absence of an authorising decision is a residual ⚠, from a search of `docs/` only. I did not read the runbook (orchestrator runbook of 3:29 PM EDT, not in the tree I searched).

5. **Tables 3–5, search-limit notes: "Context window 20 s … the shortest context ruling 7 allows, so the best value may lie beyond it (not bracketed, ADR-0010 part 1)"; also "the 120 s ceiling of ADR-0009 decision 5, so the best value may lie beyond it"** · Both limits are set by rulings:
   - ADR-0010 ruling 7 fixes 20 s as the shortest context and says the grid is not extended below it.
   - ADR-0009 decision 5, reaffirmed in ADR-0010 part 4, caps contexts at 120 s as Tony's preference.

   "May lie beyond it" points at values the rulings forbid. The page treats the count rule's k = 0 as "a lower limit by design … noted and not flagged" but treats these ruled limits as flags, a distinction no ADR makes. Whether an axis stopped by a ruled limit counts as bracketed is not settled in ADR-0010. The glossary's "edge" category is the nearest thing. · **low** · Either note these like k = 0 ("at the limit ruling 7 sets; the search would go further, which the ruling forbids"), or keep the flag and say that the bracketing status of a ruled edge is unruled. In the rows I checked, the flag does not change the leader choice, because each affected row is also flagged on its guard or a budget. · verified: yes (ADR-0010 ruling 7 and part 4; ADR-0009 decision 5; GLOSSARY "bracketed").

6. **"What each row is", binned SCE: "ported from the generate_sce routine"** · Credit stops at interface2's MATLAB routine. `docs/detector_history.md` §2 traces the method to its root: **Cossart, Aronov & Yuste 2003** (Yuste lab), with Malvache et al. 2016 as the modern restatement. The page gives locust (Cossart lab) and SPIKE-synch (Kreuz lab) their origins, so SCE is the odd one out. · **low** · Add "(the Yuste-lab rule of Cossart, Aronov & Yuste 2003, via interface2's generate_sce)". · verified: against the repo's own traced record only. I did not reopen the 2003 paper this pass; detector_history records that the root was retrieved on 2026-08-24.

7. **"What each row is", SPIKE-synch: "the ISI-adaptive SPIKE-synchronization profile of the Kreuz lab, with hysteresis detection"** · The measure is Kreuz's: Kreuz, Mulansky & Bozanic 2015, *J Neurophysiol* 113:3432–3445, doi:10.1152/jn.00848.2014, checked. But `detector_history.md` §2 says the detection layer (hysteresis, minimum trains, merge) and the τ-cap are bugarach's. The sentence reads as if the whole detector were the Kreuz lab's. · **low** · Suggested wording: "…profile of the Kreuz lab, with a τ-cap and hysteresis detection of our own". · verified: yes (detector_history §2 Tier 2; GLOSSARY axis 2; the web record).

8. **"Does the order hold on a bench spaced like the ORX recordings?", "Rank correlation … ρ"** · The method is Spearman (`make_briefing.spearman`, `orx_check`), but the page names only a "rank correlation" and never defines ρ. · **low** · Write "Spearman rank correlation (ρ)". · verified: yes.

9. **Omitted credits to Tony** · The register notes credit `line` as "Tony's vertical line, 2026-09-15" and `tube` as "Tony's tube, 2026-08-16". The count rule exists because Tony asked on 2026-09-26 (bench.py `OPERATING_POINTS["count"]`, the `count.py` docstring). The page credits Tony only with asking to see new against old. · **low** (the page is written for Tony) · Optionally add the origin to each "What each row is" line. · verified: yes.

10. **Terms "floor variant": "For the four detectors that take the floor as their minimum"** · ADR-0010 part 6 lists four (CoactDetect, LoCo, binned SCE, SPIKE-synch). But `count` and `count_sliding` also take the ADR-0008 floor as their own minimum (`count.py` docstring), and both appear on the leaderboard. "Four" is true only of the detectors that ran on the real recordings. · **low** · Write "the four detectors that ran on the real recordings and take the floor as their minimum (ADR-0010 part 6); the count rule does too, but did not run there". · verified: yes.

11. **Terms "background"** (not an artifact defect; recorded because the page and the glossary disagree) · The page's "25th and 75th percentiles … with the coordinated share subtracted" matches `bench.py`, `bench_slow.py` and `bench_combined.py`. GLOSSARY.md "background" and "regime" still carry the raw 0.0052 and 0.019 figures with no subtraction. The GLOSSARY "distractor" entry ("whether a call on one should count … is an open question") and "bracketed" ("whether a limit counts … is open") are also stale since ADR-0006 and ADR-0010 ruling 5. · **low** · The fix belongs in GLOSSARY.md, not on the page. · verified: yes.

12. **Night sources, not the artifact** (for the adjudicator; the page itself is correct on both points):
    - 064/count/README.md calls the ORX spacing "slow ORX's gaps". `bench.spacing_overrides` actually uses each stream's own ORX gaps, and that is what the page says.
    - 065/README.md attributes LoCo's held threshold to "ruling 8". It is ruling 7 (064/README.md has it right).

    · **low** · Correct them in the source notes if they are ever reused. · verified: yes.

## Verified and correct

- **Page vs ADR-0010:**
  - part 2 (spacing from real data);
  - ruling 2 (old bench not a reference; fast about 7 events instead of 15, seeds doubled; also `bench.seed_factor`);
  - part 1 (noise unit 0.01 F1, focus rule; "borrowing" is stated honestly);
  - part 3 (merged-call definition);
  - part 4 (close-events test retired);
  - ruling 5 (off-limit values, `C_min` named explicitly);
  - ruling 1 (ORX check; the code applies it on every stream, "slow above all", and the page says "every stream").
- **Page vs ADR-0008:** the floor rule (larger of 3 ROIs and the rigid-shift null reached at most once an hour).
- **Page vs ADR-0002:** locust modified from CICADA "by what it is fed"; Cossart lab (also GLOSSARY and detector_history §2).
- **Page vs the net register notes:** chorus_norm, chorus_gain_norm, line, tube, and the three `_part` notes, including tube_part's 20-frame count and the absence of a membership loss.
- **Page vs GLOSSARY axis 2:** CoactDetect, LoCo and rate+context.
- **Statistics and budgets:**
  - bootstrap is percentile, 2,000 draws, over seeds (`paired_difference`, `BOOTSTRAP = 2000`);
  - scoring tolerance is 2.5 s (`score.TOL_SEC`);
  - budget rule, including "outside on the quiet background, as the search gates it" (`make_admissible`);
  - limits are per detector and mostly measured, with rate+context's hand-set (bench.py);
  - learned models are held to CoactDetect's limits (064/README.md);
  - the pick definition (064/README.md).
- **Night facts:**
  - "17" (RUN_C list);
  - only one row over budget in the workers' notes (065/README.md finding 2);
  - the count rule's untuned starting point, set 2026-09-26 (bench.py).
- **Credit to Tony:** "Tony asked to see new against old" is verified against Tony's own 2026-09-26 request, quoted in the `make_briefing.py` docstring.

## Residuals (⚠)

- **Prior-art search:** the page claims nothing as novel or "ours", so no field search was owed. Searched: repo docs, and the web for Kreuz 2015 only. Not searched: primary papers for SCE (2003) and CICADA (Hamon et al. 2026 or the Zenodo record); I relied on the repo's traced records.
- **Correspondence:** not relevant here. There is no unattributed claim, and the page quotes no private correspondence.
- **Finding 4:** the runbook that may authorise training the plain variants was not read.

Sources:
- [SPIKY: a graphical user interface for monitoring spike train synchrony, J Neurophysiol](https://journals.physiology.org/doi/full/10.1152/jn.00848.2014)
- [PubMed 25744888](https://pubmed.ncbi.nlm.nih.gov/25744888/)
