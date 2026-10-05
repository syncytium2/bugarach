<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 11 ok — Read, Grep, Glob (plus SubagentHandback, which is only the report channel; I hold no Edit, Write or NotebookEdit)

Role 11, Start With the Problem (argument order). I reviewed only the order of the report, not its individual sections.
Artifact: %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html (built HTML, 299 lines). I read all the prose, every figure and table caption, the rows of Tables 1, 2 and 3, and the full-page render (renders_round1\page_full_1100px.png) to see what appears first on screen.

## The spine: one claim per section

- L0 (dim line under the title): this is goal 2, run on WSMIP064 overnight, on simulated baseline recordings from the fast stream only.
- L1 (the question): an earlier comparison had the nets ahead, but the two sides were tuned unequally, so that lead may have come from the tuning. This run tunes both sides equally and asks again.
- L2 (the answer in words): with both sides tuned, no net is ahead of CoactDetect. The one coded detector ahead of it uses a setting that goal 1 already ruled out, and the reason is deferred to section 7.
- L3: abbreviations.
- §1: coordinated events are hard to detect because cells fire at very different rates and the field has busy stretches, both of which make chance coincidences. Figure 1 shows a planted event, two distractors and the probe stretch.
- §2: real recordings have no answer key, so the report scores on a simulator fitted to real recordings. It plants events at two background rates, and a detector's score is its F1 averaged over the two.
- §3: there are ten contestants, four nets (including `tube` as a control) and six coded detectors. The nets differ in where they stop treating ROIs separately.
- §4.1: nested cross-validation (CV) chooses every setting without looking at the fold it is scored on.
- §4.2: a defect made different outer folds train the same model. It was fixed, and the fix was checked before launch.
- §4.3: the coded side runs in sliding mode, because tuning it in the worse binned mode would repeat the unfairness.
- §4.4: choosing on F1 alone rewards detectors that call more often, so every contestant is chosen twice: on F1 alone, and on F1 within a false-alarm budget anchored to CoactDetect.
- §4.5: the run was 1,963 jobs over 13.7 hours with no errors.
- §5: a disjoint replicate on WSMIP065 tests whether a margin survives a second draw of recordings. Its numbers are not given on this page.
- §6: no net beats CoactDetect, and tuning barely moved the nets, so the earlier lead is gone. Binned SCE (synchronous calcium events) comes first on paper, but "that result does not stand". Three coded detectors fall well behind under the budget. The t values overstate the evidence.
- §7.1: SCE's lead is an artifact of its 30 s merge gap. Goal 1's crowded veto, applied after the search, shows this (Table 3). The nets were never checked on crowded recordings.
- §7.2: locust has no admissible result under the budget, and CoactDetect went over the budget on the held-out fold in 1 of 4 folds.
- §7.3: two net refits failed to train, and they are kept in the means.
- §8: limits.
- §9: where the files are. Then provenance.

## The arc I judged against

I used the default analysis arc: the problem → what it costs → the method → what the method gets wrong → the fix → the evidence → the residual risk. This is a comparison report, so the "problem" has two layers:
- the analysis problem: the earlier comparison was unfair (lede L1);
- the domain problem: coordinated events are hard to detect (§1).

The report follows that arc well through §5, and its order matches the dispatch item for item:
- coordinated events and why they are hard: §1
- why a simulation: §2
- nested CV and the fold defect: §4.1–4.2
- sliding mode: §4.3
- two selections: §4.4
- the replicate: §5

§4.2 is a textbook "what the method gets wrong → the fix" step, and it is placed correctly, before the results. The arc breaks in §6–§7. A second "what the method gets wrong → the fix" step (the search did not apply the crowded veto, so the veto was applied afterwards) comes **after** the evidence it changes. The report does not state that deviation, and it is the main finding below.

**The cold open.** Above the fold the reader sees the title question, one line of provenance, the question paragraph (the analysis problem, stated clearly), the answer in words, then §1 with Figure 1 (what the domain problem looks like). The cold open is the problem, and the answer comes before any method, as the brief asked. Two weaknesses are findings 3 and 4.

## Findings

Each finding gives location · issue · severity · suggested fix · verified against the source (yes/no).

1. **§6 bullet 3, Table 2 annotations, Figure 7 caption, §7.1–7.2 · severity: high · verified: yes (lines 179, 193–199, 178 caption, 209–235)**
   - **Issue:** a verdict arrives before its evidence and before the rule it rests on.
     - §6 says SCE's first place "does not stand" and cites Table 3's "7 of 8" veto failures, but the crowded veto is first defined in §7.1, and Table 3 sits there too.
     - Table 2 already marks cells "(4 of 4 folds not admissible)", and Figure 7 draws hollow dots for "not admissible". "Admissible" is only explained in §7.1–7.2.
     - The lede sends the reader to §7 as well. So the reader has to take the headline correction on trust through two forward references.
     - The veto is not a check that "qualifies" results. It is part of the method: a rule about which choices count, applied after the search because the search left it out. That is the same kind of "the method got this wrong, and here is the fix" as §4.2, which the report correctly puts before the results.
   - **Answer to the question in the brief:** §7 belongs neither before §6 nor as a block inside it. It should be split by job:
     - **Rule → §4.** Move §7.1's mechanism into a new §4.5 (the old 4.5 moves, see finding 6). The mechanism is: events on this bench are ≥120 s apart, so merging calls widely costs nothing here and gains precision; on real recordings it fuses events; goal 1 lost 0.25–0.32 F1 this way; hence the veto's 0.02 F1 rule. Add the fact that this search did not apply it, so it was applied afterwards. Add §7.2's definition of "not admissible" (the budget refuses every candidate and the search returns its starting point).
     - **Outcome → §6.** Put Table 3 directly under the SCE bullet, so the verdict and its evidence sit together. Put §7.2's two cases beside the bullet on the budget results.
     - **Failed refits → §6.** Move §7.3 beside Figure 8, whose caption already points at those two dots.
     - **Unmeasured check → §8.** Move the warning that the nets were never checked on crowded recordings into Limits (finding 2).
   - After these moves §7 goes away. The lede's "for a reason explained in section 7" becomes the reason itself (finding 3).

2. **§7.1 warning box vs §8 · severity: medium · verified: yes (lines 224–226, 247–274)**
   - **Issue:** the report's biggest remaining risk is missing from its residual-risk section. The coded side was vetoed on crowded recordings but the nets were never tested on them. That limits the headline answer itself, since "no net is ahead" was measured only on well-spaced events. §8 lists eight limits and this is not one of them.
   - **Suggested fix:** add it to §8. Also mention it in one clause at the "No net is ahead" bullet in §6, the claim it qualifies.

3. **Lede, "The answer, in words" (L2) · severity: medium · verified: yes (lines 41–44)**
   - **Issue:** the answer is not fully intelligible where it stands.
     - It uses "the budget is anchored to" before §4.4 defines the budget.
     - It uses "goal 1 of this program" without saying what goal 1 is.
     - It postpones a reason that fits in one clause ("section 7").
     - It does not close the loop the question paragraph opened: whether the earlier lead came from unequal tuning. That payoff is only in §6 bullet 2 ("with both sides tuned, it is gone").
   - **Suggested fix:** rewrite it in words that need no later section. Something like: *"No net is ahead of CoactDetect, the reference coded detector; the nets' earlier lead came from unequal tuning. The one coded detector that scores higher does so by merging calls up to 30 s apart, which costs nothing on this simulator (its events are two minutes apart) but fuses closely spaced events on real recordings, and an earlier study in this program ruled it out for that reason."*

4. **Lede L1 and §3 · severity: medium · verified: yes (grep of "earlier": lines 36–38, 89–91, 191; none carries a number)**
   - **Issue:** the arc's "what it costs" step is missing. The report's motivation is that an earlier comparison had the nets ahead, but it never says by how much. So when §6 says the lead "is gone", the reader has nothing to measure that against.
   - **Suggested fix:** give the earlier margin once, with its unit, in the question paragraph. Then §6 bullet 2 reads as before → after.

5. **§6, the "How much the t values can carry" paragraph (line 202), placed after Table 2, the bullets and Figure 8 · severity: medium · verified: yes**
   - **Issue:** the note that tells the reader how to read the t values comes after they have already read t = -13.0, -17.6, -67.5 as tests. The abbreviations line even defines t as a paired statistic, which invites reading it as a test.
   - **Suggested fix:** move the paragraph to the top of §6, before Table 2 and Figure 7, or into §4 next to the fold discussion. Give the abbreviation entry for t a pointer to it.

6. **§4.5 "The size of the run" · severity: low · verified: yes (lines 156–161)**
   - **Issue:** this section does no work in the argument. It is run bookkeeping placed between the method (§4.4) and the replicate design (§5).
   - **Suggested fix:** move it to §9 or Provenance, keeping "no errors" as a one-line pointer if wanted.

7. **§5 and §9 · severity: medium · verified: yes (lines 164–171, 277–295)**
   - **Issue:** the report calls the replicate "the real check" (line 206), but it has no place in the reading order. Its numbers are withheld, and §9 "Where everything is" does not list its page. So the arc's evidence step ends by pointing outside the document with no path to follow. The replicate finished at 07:48 on 2026-09-19 and this page was built at 08:16.
   - **Suggested fix:** add the replicate page's location to §9 and to §5. Add one line to §8 saying this page's answer is provisional until the replicate is read against it. Or, if the owner allows, add the replicate's headline agreement or disagreement to §6.

8. **L0, the dim line under the title · severity: low · verified: yes (lines 31–33)**
   - **Issue:** the first text a reader sees is provenance: goal number, machine name and start and end timestamps. It comes before the question. This is minor because the question follows in the next paragraph.
   - **Suggested fix:** keep only "Simulated recordings, baseline, fast stream; written for a new reader" under the title. Move the machine and times to Provenance.

9. **§1, Figure 1 · severity: low · verified: yes (line 63 caption, line 58)**
   - **Issue:** Figure 1 is captioned "One simulated bench recording" before §2 explains what the bench is and why the report simulates. Putting the problem picture first is the right order, so this is an acceptable deviation, but the word "bench" arrives before the reader can evaluate it.
   - **Suggested fix:** add a clause to the caption ("from the project's simulator, section 2"). Do not reorder.

## Checked and fine

- §1 → §2 → §3 → §4 follows the dispatch order exactly.
- §4.2 (defect, then fix, then the check before launch) comes before any number.
- §4.3 and §4.4 each state their reason before their rule.
- §3 explains that `tube` is a control before its result.
- §8 and §9 are correctly at the end.

## Proposed spine after the fixes

1. Lede: the question, with the earlier margin (finding 4), then the answer in plain words (finding 3).
2. §1 the problem (Figure 1).
3. §2 the bench.
4. §3 the contestants.
5. §4 fairness:
   - 4.1 nested CV
   - 4.2 the fold defect
   - 4.3 sliding mode
   - 4.4 two selections and the budget
   - 4.5 admissibility: the crowded veto applied after the search, and what "not admissible" means (finding 1)
   - 4.6 or §5: the replicate design, with where to find its results (finding 7)
6. §6 results, in this order:
   - how to read t (finding 5)
   - Table 2 and Figure 7
   - the bullets, with Table 3 under the SCE bullet
   - Figure 8, with the failed refits beside it
7. Limits, now including that the nets were never checked on crowded recordings (finding 2).
8. Where everything is, plus the run size (finding 6).

## Outside my role (for the main thread to route, not a finding)

§8 bullet 2 reports a known contamination in the fitted constants (motion-correction floor-pinning in `steps_excluded`) as a limit. Whether that is allowed under this repo's rule that a known contamination stops the work rather than becoming a caveat (CLAUDE.md) is for the roles that judge substance and policy (role 2 or role 4), not for argument order.
