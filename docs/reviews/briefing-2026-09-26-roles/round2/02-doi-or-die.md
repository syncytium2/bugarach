GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I hold no Edit, Write or NotebookEdit tool. SubagentHandback is only the delivery channel. I stayed blind: I opened nothing under docs/reviews/briefing_2026-09-26-roles/ and read no git log or diff of make_briefing.py or its test. One grep listed filenames in that folder, and I did not open any of them.)

# Role 2 (DOI or Die): named attributions in the full-panel briefing

**Result: 4 findings to fix, 7 minor ones, and most attributions verify.** The most serious is the "_part" note (F1). It tells Tony that all three `_part` families carry per-cell votes and a membership loss, and the registry says `tube_part` has neither.

**What I checked:** the built `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, reduced to text at `<scratchpad>/mb2/text.txt`. I compared it against:
- ADR-0002, 0006, 0008 and 0010 in `<worktree>/docs/adr/`. ADR-0010 is on origin/main at commit 36153823; the local main checkout is stale and lacks it.
- `docs/GLOSSARY.md`: axis 2, the event floor, background, the close-events test and distractor/decoy.
- Every `@register` note in `src/bugarach/learn/nets/`.
- `src/bugarach/score.py` (scoring tolerance and merge count).
- `tools/score_bench_candidates.py` (bootstrap).
- `tools/search_all_settings.py` (`make_admissible` and the part-4 retirement).
- The four night notes: 065/README.md, 065/RUN_C.md, 064/README.md, 064/count/README.md.

## Findings (location · issue · severity · fix · verified against a source?)

**F1. "What is compared" box, the note on names ending in `_part` (`PART_NOTE`, make_briefing.py ~line 115).**
- **Issue:** It says every `_part` network adds "a bounded vote per cell summed into a count … and a membership term in the training loss", citing ADR-0010 part 5. That is wrong for `tube_part`, which the page scores in all three streams.
  - Its register note says: *"tube plus a count (ROIs with an onset in a 20-frame window) and the recording's floor as inputs … no membership loss, since tube has no per-cell stage"*. It trains with `PART_TRAINING_NO_MEMBERSHIP`.
  - ADR-0010 part 5 says the same: membership training is for the chorus and line families only, and tube and trace "train without it".
  - So the page gives both the registry and the ADR it cites a scope they do not have.
- **Severity:** Medium-high. It describes the wrong model to the person who will decide on adoption.
- **Fix:** Split the note. Chorus and line `_part`: bounded per-cell vote summed into a count, the floor as input, membership loss. `tube_part`: an onset count over a 20-frame window and the floor as inputs, no membership loss (ADR-0010 part 5). Better, build it from each model's register note, as the docstring says the learned lines already do.
- **Verified:** yes.

**F2. Terms, "merged calls" (cites ADR-0010 part 3).**
- **Issue:** The page defines it as "calls whose span covers two or more **planted** events". Both sources say something narrower:
  - ADR-0010 part 3: "two or more **scored** events".
  - `score.py` (`n_merged_calls`): "two or more scored planted events"; a "don't care" event under the floor (ADR-0009 decision 2) does not make a call a merge.
- **Severity:** Medium. It is a misquote of the cited ruling and overstates what is counted.
- **Fix:** Change it to "two or more scored planted events (under-floor 'don't care' events are not counted; ADR-0010 part 3, ADR-0009 decision 2)".
- **Verified:** yes.

**F3. "How to read it", the budgets paragraph: "The close-events test is not run on fresh seeds."**
- **Issue:** This implies the test is still part of the bench and was only left out here. ADR-0010 part 4 retired the close-events recording and its allowance, and `search_all_settings.py` says so under "part 4". The Glossary still describes the test as goal 1's fourth budget without the retirement; that is a stale source the page may have followed.
- **Severity:** Medium-low. It misstates why the budget is absent.
- **Fix:** "The close-events test is retired (ADR-0010 part 4): the scored recordings now contain close events."
- **Verified:** yes. The stale Glossary entry is a separate tree finding for whoever owns the Glossary.

**F4. "How to read it", the noise-unit sentence: "ADR-0010 counts 0.01 F1 as one noise unit…; rows closer than that are level."**
- **Issue:** ADR-0010 part 1 defines the noise unit (0.01 F1, the draw-to-draw spread from the fair comparison) for one purpose: the drop rule, where a detector more than one noise unit behind the leader on at least two streams is dropped. It does not say that rows closer than 0.01 are "level". That reading is the page's own, attributed to the ADR.
- **Severity:** Medium-low.
- **Fix:** Either quote the ADR's actual use ("ADR-0010's drop rule uses one noise unit, 0.01 F1…"), or present the "level" reading as this page's convention.
- **Verified:** yes.

**F5. "What is compared", the locust line: "modified from CICADA (ADR-0002; coded)".**
- **Issue:** This is accurate against ADR-0002 and the Glossary ("per-cell roll null" matches), but the page names CICADA without citing it. ADR-0002 says the citation goes in the help panel, the README and the methods text. For a PI briefing a pointer to the ADR is probably enough.
- **Residual ⚠ in the tree, not the page:** the Glossary credits CICADA to the Zenodo software DOI 10.5281/zenodo.10041434 and "Hamon et al. 2026". ADR-0002 says "Denis et al. 2020". The page leans on an attribution its two sources disagree about. I did not resolve which is right, because it is outside this artifact.
- **Severity:** Low for the page; the source disagreement is worth a todo.
- **Fix:** None needed on the page. File the Glossary/ADR-0002 citation mismatch.
- **Verified:** yes against the tree sources. The upstream CICADA citation is not verified.

**F6. Section 2, the method paragraph: participants counted with the review tool's ±1 s window, "the same for every detector".**
- **Issue:** This matches 065/README.md. But ADR-0010 ruling 3 says the call measure's `core_n_roi` is used on each stream where it passes validation, and the review tool's own window elsewhere. The page does not say why the fallback is in force (the validation and adoption are a pending morning decision).
- **Severity:** Low.
- **Fix:** Add "(ADR-0010 ruling 3: the call measure's core count is not yet adopted on any stream)", if that is the state of things. The night notes do not say either way.
- **Verified:** Partly. The window is verified against 065/README.md; the adoption state is not recorded in the night sources.

**F7. "What is compared", the chorus_norm and chorus_gain_norm lines.**
- **Issue 1:** "encodes each cell's trace, standardised over time" reads as though the input trace is standardised. The register note says the cell's *encoder output* is standardised over time before the vote.
- **Issue 2:** chorus_gain_norm's register note credits its vote to line ("then line's vote: a learnable gain started at 8 and a bias"). The page drops that lineage.
- **Severity:** Low.
- **Fix:** "encodes each cell's trace, standardises the encoding over time, then pools". "chorus_norm with line's vote: a learnable gain and bias".
- **Verified:** yes.

**F8. "What is compared", the SPIKE-synch line.**
- **Issue:** This is accurate against the Glossary as far as it goes, but it drops the Glossary's "tau-capped ISI-adaptive" and "(Kreuz lab)" attribution.
- **Severity:** Low.
- **Fix:** Optionally add "ISI-adaptive, Kreuz lab".
- **Verified:** yes.

**F9. Terms, "floor (ADR-0008)": "the smallest co-active cell count that is not chance there".**
- **Issue:** This is a loose paraphrase. ADR-0008 defines the floor as the larger of 3 ROIs and the smallest co-active count that the window's own rigid-shift null reaches at most once per hour. The page drops the minimum of 3 and the once-per-hour criterion.
- **Severity:** Low.
- **Fix:** "the larger of 3 ROIs and the smallest co-active count the window's own null reaches at most once an hour (ADR-0008)".
- **Verified:** yes.

**F10. Limit marks, "Context window 120 s, at the grid's upper edge … (ADR-0010 part 1)".**
- **Issue:** Part 1 is correct for "not bracketed". The reason the edge sits at 120 s is ADR-0009 decision 5's cap, which ADR-0010 part 4 records as Tony's preference.
- **Severity:** Low.
- **Fix:** Optionally add "(the 120 s cap, ADR-0009 decision 5)".
- **Verified:** yes.

**F11. "How to read it": "Tony asked to see new against old on 2026-09-26" beside "ADR-0010 ruling 2 retired the old bench as a reference".**
- **What checks out:**
  - Ruling 2 says "the old bench is not scored as a reference". The page's "decides nothing" is consistent with that.
  - The request is dated in the generator's docstring, which quotes Tony on 2026-09-26.
  - 065/RUN_C.md records the old-bench runs as an "orchestrator brief, 2026-09-26".
  - The fast seed count (24 fast seeds on the old bench, not doubled) is consistent with RUN_C.md.
- **Residual ⚠:** The only record of the request is the generator plus RUN_C.md. No durable decision record holds it, which is acceptable because it changes no ruling.
- **Severity:** Informational.
- **Fix:** None.
- **Verified:** yes, to the generator and RUN_C.md.

## Checked and correct
- **ADR-0010:**
  - "Moved the bench to event spacing measured in real recordings" matches part 2.
  - The old bench at "at least 120 s" apart matches the ADR's Context section.
  - Ruling 1's slow-ORX check is described correctly.
  - Ruling 5 is attributed correctly to guard 0, merge gap none, `C_min` 0 and locust's 1-frame run; the ruling names `C_min` and locust's run explicitly.
  - "The shortest context ruling 7 allows" (20 s) matches the ruling and `CONTEXT_MIN_SEC`.
  - Part 1 as the source of the bracketing requirement is correct.
  - k 0 read as a by-design limit and not a ruling-5 stop matches 064/count/README.md.
- **ADR-0006:** decoys are coordination by construction, and reports show F1 with and without decoy calls. Both are correct.
- **Budget list:** it matches `make_admissible` exactly: no-coordination recording, elevated-rate test inside the stretch (quiet and busy), outside the stretch (quiet), and precision swing. Learned models held to CoactDetect's limits matches the generator's `budgets_of`.
- **Bootstrap:** "95% percentile-bootstrap interval over seeds (2,000 draws)" matches `score_bench_candidates.py` (`BOOTSTRAP = 2000`, resampling seeds, `np.percentile` at 2.5 and 97.5). No literature citation is needed on an internal page.
- **Scoring tolerance:** 2.5 s matches `score.TOL_SEC`. The page itself discloses that it applies the tolerance span to span.
- **Glossary terms:** "background" (25th and 75th percentiles; quiet and busy) and "pick" (best held-out F1 within CoactDetect's no-coordination budget) match the Glossary and 064/README.md. The no-pick comparator matches 065/README.md finding 2.
- **Coded detector lines:** CoactDetect, LoCo, rate+context, binned SCE and locust are consistent with Glossary axis 2.
- **Learned model lines:** line and tube are consistent with their register notes. The register credits line and tube to Tony (2026-09-15 and 2026-08-16); the page omits that, which is harmless on a page written for Tony.

## Literature and correspondence
- The page claims nothing as novel or unattributed, so no prior-art search was triggered. I searched no external literatures. I did not verify the upstream CICADA citation (see F5).
- Correspondence: none is relevant to any claim on the page, so no "nobody was asked" residual applies.

## Outside my role
- **Recording identifiers on the page:** the built page names real recordings (figure captions and Table 6). That is fine for a private darkroom page, but it matters if the page is ever copied into the public repo with `--also`. I have not quoted any.
- **Count of intervals that change side:** the page's slow-ORX count differs from 065/README.md's. They appear to count different sets: the page counts against the shipped setting only, the README against both references. Another role should reconcile them.
