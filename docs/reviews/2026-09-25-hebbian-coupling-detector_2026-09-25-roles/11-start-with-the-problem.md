GRANT 11 ok — Read, Grep, Glob

(Run note, not a finding about the artifact: SubagentHandback is my only other callable tool, and it only returns this report. My context also contained usage instructions for the Claude_Docs, Dropbox and github MCP servers, some of which can write. None of their tools were in my callable set and I used none of them. Record it in the ledger in case another role's harness exposed them.)

# Role 11: argument order ("Start With the Problem")

**Artifact:** docs/proposals/2026-09-25-hebbian-coupling-detector.md
**Compared against:** docs/goals/unsupervised-learning.md, and how three other proposals open:
- docs/proposals/2026-09-10-surrogate-evaluation-overnight.md opens on `## The problem`.
- docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md opens on a banner paragraph "Why this page exists", then `## The question`.
- docs/proposals/2026-09-12-the-roi-swap-null.md opens on its status, then `## Verdict`.

## The spine (one claim per section)

- **Banner and abbreviations.** This is a draft. It needs no open ruling to start. It does not touch the stopped surrogate screen, because it uses no training negatives. Tony has already chosen to bring the rule in as a stamped copy from clamor, not as a dependency.
1. **The idea.** A coupling between every pair of ROIs is strengthened when their onsets coincide and weakened on near-misses. At the end of a baseline window it records which pairs kept coinciding beyond chance. A plain Hebbian rule would learn event rates and grow without bound, and "the rule below" comes with both repairs.
2. **The rule (1986, equations 7 and 8).** The kernel runs +1 / 0 / −1 by timing offset, and the bound keeps every coupling within 80 % of its resting value. The coupling changes within one stimulus, so it can be used one recording at a time. The subliminal rule leaves silent ROIs at rest, which is what FOUNDATIONS §9 requires.
3. **What changes for calcium events.** Pairs within ±*w*, updated symmetrically. The kernel is taken at its one exact point, a cosine, which is rate-neutral to first order (derived here, not measured). The two end lags are weighted by half on the frame grid. *w* is set to 2–4 times the ruled jitter, and *q*₀ is swept. All of it is frozen in stage 1.
4. **What the detector reports.** Three readouts: a significance test on *D* against circular-shift surrogates; the shape of *D*, including overlapping groups, which targets the assembly negative's main open risk; and a per-frame call comparable to the six coded detectors. Baseline windows only.
5. **What could make this worthless.** Check A: the STTC matrices may carry nothing beyond a busy core (rank one), in which case readout 2 is dropped. Check B: *D* may just be STTC (rank correlation above 0.9), in which case the detector is not built. Tony sets the stop thresholds.
6. **Stages.** 0: Check A, with no new code. 1: simulation plus Check B, then freeze *w* and *q*₀. 2: real baseline recordings, reported per group. 3: report back to clamor. A fourth stage (distance) waits on ROI centroids, and the request for them is drafted.
7. **How the code arrives.** Two functions are copied from clamor with a provenance stamp, and the freshness check gains a clamor family. Keeping the whole copy for what is one cosine is justified by the stage-1 sweep.
8. **What this does not claim.** That the preparation has assemblies; that rate-neutrality holds for real trains; that the 1986 model reproduces its own paper.

**Arc used:** the one the caller specified. The problem (what gap in this project's work it fills) → why this approach → what could make it worthless → what is asked / what stage 0 costs → stages → non-claims.

**Actual order:** idea (a mechanism) → the rule (source and equations) → calcium adaptation (parameter detail) → readouts → what could make it worthless → stages → code logistics → non-claims.

**The problem step is missing entirely.** "Why this approach" is spread across sections 1 to 3. The ask is spread across sections 5 and 6 and never gathered.

**Cold open:** the reader first sees a status line, then a statement of what the proposal does *not* touch (the surrogate screen), then a logistics decision (stamped copy versus dependency), then a list of symbols, then the mechanism ("Treat each ROI as a unit…"). At no point before section 4 does the reader see the gap this fills. The title names the method, not the problem. All three comparison proposals open on their problem, their question or their verdict. This one departs from that pattern and does not say it is doing so.

## Findings

Each finding gives its location, the issue, the severity, a suggested fix, and whether I could verify it against a source.

**F1. The cold open has no problem statement, so the gap this fills is never stated.**
- **Location:** banner, lines 3–11, and `## The idea`, line 22.
- **Issue:** The goal page states the gap in its first paragraph: every learned number here was fitted on a simulator, and the only label-free route (surrogate contrast) is stopped. The screen was stopped on 2026-09-12, and the pre-registration is not buildable until Tony rules on it. The proposal's strongest motivation is that the rule learns inside each real recording, so it cannot have learned the simulator, and it needs no negatives. That is never said as a motivation. The banner mentions the screen only defensively ("does not touch the stopped surrogate screen"). The second motivation, the assembly negative's open risk that modularity cannot see overlapping membership, first appears in section 4, inside readout 2 (line 104). A reader has to hold roughly 90 lines of mechanism in suspense before learning why any of it matters.
- **Severity:** major.
- **Fix:** Add a first section, `## The gap`, of 3 to 5 sentences placed before "The idea":
  - The goal wants a detector that learns from real recordings rather than from the simulator.
  - Its one route is stopped (link the screen stop and the pre-registration's blocked state).
  - This rule learns within one real recording with no negatives, so it neither waits on the screen nor inherits the simulator.
  - Separately, it gives an instrument aimed at the assembly negative's first open risk (link the todo).
  Title optionally reframed around the gap.
- **Verified against a source:** yes (goal page lines 25–31 and 49–57; the proposal's lines 1–32 and 103–106).

**F2. The proposal never says which of its two jobs is the main one, so Check A's stop rule cannot be judged.**
- **Location:** the whole spine; decisive at lines 126–127, 1 and 177–178.
- **Issue:** The title and readout 3 say it is a detector, which is the unsupervised-learning goal. Readout 2 and the first non-claim say it is an instrument against the assembly negative. Check A's stop drops readout 2 but keeps the proposal alive if readout 3 beats CoactDetect. That only makes sense if the detector is the main job, and nothing earlier says so. Without a stated main job, a reader cannot tell whether failing Check A is a partial loss or most of the value.
- **Severity:** moderate to major.
- **Fix:** In the new `## The gap` section, name the primary goal (the detector) and the secondary one (assembly structure). Then word Check A's stop to match.
- **Verified against a source:** yes (the proposal's text).

**F3. The checks that could make this worthless come after about 60 lines of parameter detail they do not depend on.**
- **Location:** sections 2–3 (lines 34–93) come before section 5 (lines 115–137).
- **Issue:** Check A needs only the existing STTC matrices and the readout definitions; it does not use the rule at all. Its earliest intelligible position is right after the readouts. Check B needs only "negative lobe plus bound plus rate-neutral kernel", which fits in one paragraph. As written, the reader works through the trapezoid end-weighting, the *q*₀ disagreement and the jitter-based width before learning that a stage-0 check with no new code could make all of it moot.
- **Severity:** moderate.
- **Fix:** Reorder to: gap → idea (with a 3-line summary of the kernel, bound and rate-neutrality) → what it reports → what could make this worthless → what is asked → stages → then `## The rule` and `## What changes for calcium events` as a method section (labelled "Method detail — needed for stage 1") → how the code arrives → non-claims. State the deviation from source-first order in one line.
- **Verified against a source:** yes.

**F4. "Why this approach" is buried inside a citation paragraph and a parameter bullet.**
- **Location:** lines 39–40, 49–50 and 73–76.
- **Issue:** The three reasons for choosing this rule are scattered:
  - It learns within a single stimulus, so it is usable per recording (lines 39–40, in the middle of the source citation).
  - A stray burst of false synchrony cannot move a coupling far (lines 49–50).
  - It is rate-neutral without a rate term (lines 73–76, inside bullet 4 of the calcium section).
  None of the three is presented as the reason to choose this approach. Each arrives after the reader has already been told how the rule works.
- **Severity:** moderate.
- **Fix:** Gather the three into a short `## Why this rule` directly after the idea, with pointers down to the method detail.
- **Verified against a source:** yes.

**F5. A forward claim arrives before the reader can check it, and it is attributed to the wrong place.**
- **Location:** lines 30–32 ("The rule below comes with both repairs already in it").
- **Issue:** Only the bound (equation 8) is in the 1986 rule. The rate repair is this proposal's own choice of kernel point and window, derived in section 3 (lines 73–79: "Any other window length breaks it… derived here, not measured"). The reader meets a claim of a solved problem two sections before its evidence, and the claim credits the source rather than the adaptation. This is in scope because of where the claim sits. Whether it is supported is Reviewer 2's (agent 4) question.
- **Severity:** moderate.
- **Fix:** Reword to: "The 1986 rule bounds growth; the kernel point chosen under 'What changes for calcium events' removes the rate term — a derivation stage 1 tests."
- **Verified against a source:** yes (the proposal, lines 30–32 compared with 73–79).

**F6. There is no "what is asked", and the stage-0 cost is only implied.**
- **Location:** decisions are scattered across line 137 (the thresholds), line 141 (stage 0), lines 149–151 (stage 3 writes a finding into clamor) and lines 158–159 (a request drafted for Tony to post).
- **Issue:** This is a proposal asking Tony to approve a staged plan, yet the ask never appears as its own step. The reader has to piece together what to decide:
  - Approve stage 0.
  - Set the two stop thresholds before any number is read.
  - Later, approve stages 1–3, including a write into another repository.
  - Post the centroid request.
  Stage 0's cost appears only as "No new detector code" inside the stage list. The goal page's own summary of this proposal (lines 49–53) states it more clearly than the proposal does.
- **Severity:** major.
- **Fix:** Add `## What is asked` after the checks and before the stages. List the decisions now (approve stage 0; set or accept the thresholds for Check A and Check B), the stage-0 cost (existing STTC matrices, no new code, rough run time), and the decisions deferred to later stages.
- **Verified against a source:** yes.

**F7. "How the code arrives" sits in the middle of the case, and its opening decision duplicates the banner.**
- **Location:** lines 161–173, with the same decision in the banner at lines 9–11.
- **Issue:** The section's job is implementation logistics for a decision already made. Its position after the stages and before the non-claims is tolerable. Once F3 moves the method detail below the stages, it belongs with that method detail or in an appendix.
- **Severity:** minor.
- **Fix:** Move it under the method detail or into an appendix. Cut the banner's restatement to one clause that links to it.
- **Verified against a source:** yes.

## Earliest intelligible position, per section

| Section | Earliest intelligible position |
|---|---|
| Idea | 2, after the gap |
| Rule | after the idea |
| Calcium changes | after the rule |
| Readouts | right after the idea (uses only symbols defined in the abbreviations block) |
| Check A | after the readouts |
| Check B | after a one-paragraph kernel summary |
| Stages | after the checks and the ask |
| Code | anywhere after the stages |
| Non-claims | at the end, correctly placed |

Every section except "How the code arrives" has a job in the argument; F7 covers that one.

## Proposed spine after repair

1. The gap (goal page, screen stopped, assembly open risk; which job is primary)
2. The idea
3. Why this rule
4. What the detector reports
5. What could make this worthless
6. What is asked, and what stage 0 costs
7. Stages
8. Method detail: the 1986 rule, and what changes for calcium events
9. How the code arrives
10. What this does not claim

The only departure from the arc I used is that the method detail comes after the stages. The proposal should state that in one line.

**Not reviewed, because other roles cover it:** whether any claim is supported (agent 4); whether each section reads well to a stranger (agent 8); mechanical checks (agent 10); whether the ADR-0007 scope covers writing into clamor.
