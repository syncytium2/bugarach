GRANT 11 ok — Read, Grep, Glob

# Argument order review: `docs/learned/tube_self_supervised/README.md`

I only looked at the order. I read the artifact, its three figures, `docs/goals/unsupervised-learning.md` and `docs/pipelines/learned-model-evaluation.md`. I opened no earlier review records, handoffs or todos, and followed none of the artifact's links to them.

## Spine (one claim per section, in page order)

1. **Title:** rigid shift will be judged on what it hides, what it destroys, and what training on it alone buys.
2. **What this run found:** four claims.
   - The per-ROI leak test has power on the fast stream, and rigid shift passes it.
   - The aggregate test agrees when built from fitted models.
   - No learned build beats CoactDetect by a margin the four folds can resolve.
   - Training on rigid shift alone beats an untrained model only at the strict thresholds, and falls far short of supervised training.
3. **Exploratory banner:** this page replaces a version that was reviewed twice, nothing on it is promoted, and every number is in `summary.json`.
4. **Terms:** defines ROI, onset, F1, *J*, *t*(3) and SD.
5. **The problem:** nothing is annotated, so supervised detectors learn the simulator. A label-free detector needs copies of a recording that remove only alignment, and rigid shift is the candidate. Three questions follow, plus a fourth.
6. **What changed from the reviewed version:** six fixes, each of which moved a number or what it means.
7. **Figure 1, the leak tests:** on the fast stream, rigid shift hides from a per-ROI test whose positive control does separate. On the slow stream, what it removes above 22 s is shared modulation, not a leak. The aggregate test gives the same answer with fitted channels, but it cannot rule out co-activity.
8. **Figure 2, the bake-off and plant probe:** every learned margin over CoactDetect rests on one fold. The second sensor and the time bound change nothing measurable. `line` over `tube` is the only comparison that separates. The probe gives a direction, not a measurement.
9. **Figure 3, label-free training:**
   - Counting builds lose less F1 as the rate tightens.
   - Trained cells beat untrained ones only at ≤ 1 and ≤ 0.5 events per 10 minutes.
   - No trained cell gets near supervised training.
   - The truth-reading scores of the untrained arm and the real-trained arms come from detections that cover almost the whole recording.
   - The paired checks can see a change in onset count.
10. **On real recordings:** this is a consistency check.
    - Calls from models trained on rigid shift hold 0–1 ROIs.
    - Supervised models fire more often than either reference, and `line` is fourth of five on overlap with the references.
    - Detections of every kind cluster near the window edges.
11. **What this does not settle:** twelve limits.
12. **What waits on Tony:** four decisions.
    - Which `line` build stays.
    - Whether 10–45 s modulation counts as coordination.
    - Whether the objective is worth another attempt.
    - Which firing rate the label-free threshold should target.
13. **Published lineage:** almost everything here is prior art. Dropping onsets at the edge biases the null. What is new is narrow.
14. **Provenance:** commits, surrogate code, commands.

**The arc I judged against:** a question-led exploratory report. The problem, then its questions, then one section per question, then a real-data check, then residual risk, then the decisions, then credit and provenance. The page announces this itself ("Three questions follow, and the figures take them in order"), so leaving the default problem-to-fix arc is a stated choice, not a defect. What fails is where the page breaks its own declared arc.

**Cold open:** the reader first sees a four-bullet summary of results (item 2), then the page's review history (item 3). The problem arrives at line 42, after about 40 lines the reader cannot yet judge.

## Findings

**1. The page opens on results the reader cannot yet read**
- **Where:** lines 3–40 (summary, banner and terms, all ahead of "The problem" at line 42).
- **Issue:** The first bullet asks the reader to judge "the per-ROI leak test", "per-onset dither" and "rigid shift". The next ones use "the aggregate-channel gate", "counting builds", CoactDetect and "the stricter label-free thresholds". None of these is defined before line 51, and several not until Figures 1–3 (dither at line 114, counting builds at line 150, label-free and truth-reading thresholds at line 235). The terms block sits after the summary and defines none of them. The first thing the page shows is a summary of the work plus its review history, not the problem. The earliest point where these bullets make sense is after "The problem".
- **Severity:** high.
- **Fix:** Put a two- or three-sentence version of "The problem" above the findings: nothing is annotated, rigid shift is the proposed label-free negative, and the page asks whether it is clean and whether a detector can learn from it. Or move "The problem" first and the findings straight after it. Move "Terms" above whichever comes first, and add rigid shift, leak test and label-free threshold to it. Shrink the review-history part of the banner to one line.
- **Verifiable against source:** yes, by position in the artifact.

**2. "What changed from the reviewed version" splits the questions from their answers and depends on things not yet introduced**
- **Where:** lines 65–89, between the questions (lines 55–63) and Figure 1.
- **Issue:** This is a changelog for people who read the previous version, and it has no job in the argument. It also arrives before the reader can judge it:
  - "`line`'s docstring said one ROI casts at most one vote": `line` and its sensors are introduced at line 150.
  - "the truth-reading threshold … `fold_maker` … two, not four": that threshold is defined at line 235.
  - "the aggregate-channel gate is built from fitted models": the gate is explained in the Figure 1 caption.

  Worse, it sits right after "the figures take them in order", so the promised answer is postponed by 25 lines of fixes to things not yet shown.
- **Severity:** high.
- **Fix:** Move the section to just before "Provenance", or fold it into Provenance, and keep the banner's one-line pointer. The one change that matters to the argument (`line_bound` exists to test the stronger one-vote claim) belongs in Figure 2, where lines 150–153 already introduce `line_bound`. Add the reason there.
- **Verifiable against source:** yes.

**3. "The problem" motivates the questions on hiding and training, but not the architecture question or the aggregate test**
- **Where:** lines 55–61 (the architecture question), 76–77, 101–103 and 125–136 (the aggregate test), and 135 ("which is what a counting architecture computes").
- **Issue:** The page asks "Is a counting architecture better than the centre-surround one?" without saying:
  - why a counting architecture exists;
  - what is wrong with centre-surround;
  - why a supervised bake-off belongs in a report about rigid shift as a teacher.

  The goal page supplies the missing link: `tube` averages over ROIs before its first kernel, so it cannot tell a count leak from coordination, and an aggregate-channel test is "the precondition for training anything that averages over ROIs". None of that reaches this page. So panel C of Figure 1 arrives unmotivated. The ⚠ at line 135 leans on "counting architecture" 15 lines before the term is defined. And the bake-off reads as a side trip, when it is actually the supervised ceiling that Figure 3 is measured against (lines 243–252, 269).
- **Severity:** medium-high.
- **Fix:** Add two sentences to "The problem". First, a detector trained against a surrogate can learn any channel the surrogate moves, and one that averages over ROIs sees only how much of the field is lit, which is why the aggregate test exists. Second, a counting architecture (`line`) was built to count votes across ROIs, and its supervised score is both the licence for the family and the ceiling for label-free training. Define "counting architecture" there, not at line 150.
- **Verifiable against source:** yes (`docs/goals/unsupervised-learning.md`, "The model" table and "Open work").

**4. The first question promises an answer to "does it destroy alignment", and no section gives one**
- **Where:** lines 57–58 (the question), the title's "what it destroys", and the Figure 1 section (lines 91–136).
- **Issue:** Figure 1 measures only whether rigid shift *hides*. The planted-twin control (lines 129–130) shows the aggregate test can separate, not how much coordination rigid shift removes. The destruction figures (84–99 %) are in the earlier look, which this page cites only as "the earlier look" (line 123). The page answers half its own opening question and never says the other half is out of scope. Readers who checked the question against the answer will notice the gap.
- **Severity:** medium.
- **Fix:** Either narrow the question and title to what the page measures ("what it hides, what it removes on the slow stream"), or add one sentence to the Figure 1 section that points to where destruction was measured and says it was not rerun.
- **Verifiable against source:** yes (artifact text; the goal page's 2026-09-14 "Latest" line for the earlier destruction numbers).

**5. In Figures 2 and 3 the evidence comes before the claim**
- **Where:**
  - Figure 2: the 15-row table (line 155) and the paired-difference table (line 181) come before "Every learned margin over CoactDetect is carried by the third fold" (line 192).
  - Figure 3: the two tables (lines 243 and 257) come before the bold result at line 265.
- **Issue:** The Figure 1 section does this correctly: its bold claim (line 105) sits above its table. The next two sections do the reverse. The reader goes through 30 rows of numbers without knowing which comparison matters. For Figure 3 that is the mismatch between untrained and trained at ≤ 2 events per 10 minutes and at ≤ 1.
- **Severity:** medium.
- **Fix:** Put each section's bold claim sentence directly under the caption, above the tables, as Figure 1 does.
- **Verifiable against source:** yes.

**6. The caveat that `locust` is not CICADA reaches the reader only after the decisions**
- **Where:** line 170 (the table row "locust · port of another lab's · 0.545"), with the caveat at lines 442–445, inside the lineage section that follows "What waits on Tony".
- **Issue:** A reader who stops at the bake-off table, which is where the number is judged, reads 0.545 as a score for another lab's method. The line "its numbers are never measurements of CICADA" arrives about 270 lines later. The same applies to the SPIKE-synch row (0.267).
- **Severity:** medium.
- **Fix:** Add one sentence under the Figure 2 table, or a ⚠ in the "what it is" cell: "`locust` is a partial, modified port that skips CICADA's transient detection; not a measurement of CICADA". Leave the full credit in the lineage section.
- **Verifiable against source:** yes.

**7. The bias from dropping onsets at the edge is a residual risk, but it appears only after the decisions, in the credit section**
- **Where:** lines 416–421 (lineage), which follow "What this does not settle" (lines 351–385) and "What waits on Tony" (lines 387–405).
- **Issue:** "This run drops, which deflates the surrogate's coincidence count, biasing the null in the direction that makes real recordings look more coordinated" limits every rigid-shift result on the page. It bears on the question about 10–45 s modulation and on whether the objective is worth another attempt. Yet it is missing from the list of what this does not settle and arrives after Tony has been asked to decide. Two more pointers run in the wrong direction:
  - "the literature search behind the lineage below" (line 381);
  - the Stella et al. 2022 bullet (line 355), which quotes lineage facts before the lineage section.
- **Severity:** medium.
- **Fix:** Add a bullet on dropping onsets at the edge (its direction, and the 0.5 % and 1.1 % of onsets dropped) to "What this does not settle". Leave the credit text where it is.
- **Verifiable against source:** yes.

**8. The decisions are not in the order the argument raised them, and the upstream decision is second**
- **Where:** lines 387–405.
- **Issue:** The decisions follow the sections in this order: Figure 2 (which `line` build), Figure 1 (shared modulation and *J*), Figure 3 (the objective), then real recordings (firing rate). Whether 10–45 s modulation counts as coordination "decides whether *J* belongs at 10–20 s at all". That makes it upstream of everything trained in Figure 3, and so upstream of the objective decision, yet it is listed after the build choice. The premise that 10–20 s was a *choice* also first surfaces in the decision itself: the Figure 3 caption (line 225) gives "*J* = 10 s and 20 s" with no reason.
- **Severity:** medium-low.
- **Fix:** Order the decisions as the sections raised them: shared modulation and *J*, then the learned family and build, then the objective, then the threshold rate. Say in "The problem" or the Figure 3 caption where 10–20 s came from.
- **Verifiable against source:** yes.

**9. The build decision leads with the smaller question**
- **Where:** lines 389–394.
- **Issue:** The pipeline page says the comparison that licenses the work is against the hand-written detectors, and "is the second sensor worth it" is the smaller question. The first decision asks "which `line` build, if any, stays" and argues only between builds. The non-result against CoactDetect sits a section earlier (line 353) and is not restated where the decision is made.
- **Severity:** medium-low.
- **Fix:** Put the larger question first: "Whether any learned build stays, given none separates from CoactDetect (every margin rests on one fold); if one does, which." Then give the evidence between builds.
- **Verifiable against source:** yes (`docs/pipelines/learned-model-evaluation.md`, the bake-off stage, which says the licensing comparison is against the hand-written detectors).

**10. The summary sets up only two of the four decisions and does not say decisions are coming**
- **Where:** lines 3–21 against lines 387–405.
- **Issue:** The summary covers the bake-off (the build decision) and training (the objective decision). The slow-stream modulation result behind the *J* decision appears only in the middle of Figure 1's prose (lines 120–123). The real-recording event rates behind the firing-rate decision appear only in "On real recordings". The strongest real-data evidence for the objective decision is that calls from rigid-shift-trained models hold 0–1 ROIs (line 313). That is not in the summary, and the objective decision does not cite it. A reader who takes the summary as the case does not know the page ends by asking for four rulings, or what two of them rest on.
- **Severity:** medium.
- **Fix:** Add a closing summary bullet naming the four decisions, with a link to "What waits on Tony". Add the slow-stream modulation result and the finding that rigid-shift-trained calls hold 0–1 ROIs. In the objective decision, cite the 0–1 ROI result beside Figure 3.
- **Verifiable against source:** yes.

**11. Two passages have no job where they sit**
- **Where:**
  - The lanes-over-raster note, lines 345–349, in "On real recordings".
  - The window-edge ⚠, lines 336–343.
- **Issue:** The lanes paragraph says a figure was not redrawn and nothing on the page quotes it. That is housekeeping in the middle of the real-data case. The window-edge paragraph finds that "the threshold rule, not only the architecture, is involved", which bears directly on the firing-rate decision, but that decision does not mention it. So a finding with a job is not connected to it, and a paragraph with no job takes up a place in the argument.
- **Severity:** low.
- **Fix:** Move the lanes paragraph to "Provenance". Add a clause to the firing-rate decision: "the label-free rule also raises edge enrichment in every supervised model".
- **Verifiable against source:** yes.

**12. Terms are used before their definitions inside the Figure 1 and Figure 2 sections**
- **Where:**
  - "shared offset" and "per-onset dither" in the table at lines 109–111, defined at lines 113–116.
  - The line, burst, fuzz and wave plants, used in the Figure 2 caption (line 146, "a plant of equal ink") and defined at lines 198–202.
  - "Probe firings" and "Fit time", table columns at line 155, defined at lines 173–177.
- **Issue:** Small ordering slips inside sections. Each definition comes a few lines after first use, so the reader has to scan ahead once. The probe definitions are the worst case: about 50 lines after the caption.
- **Severity:** low.
- **Fix:** Move the definitions of shared offset and dither above their table. Move the definitions of the four plants into the Figure 2 caption's text on panel B, or directly under it.
- **Verifiable against source:** yes.

## What earns its position

These sections sit where the argument needs them:
- **"The problem"**, but it should come first.
- **Figures 1–3**, in the order of their questions.
- **"On real recordings"**, as the declared fourth question.
- **"What this does not settle"**, before the decisions.
- **Provenance**, at the end.

The lineage section is defensible after the decisions as credit, except for the residual-risk content in finding 7.
