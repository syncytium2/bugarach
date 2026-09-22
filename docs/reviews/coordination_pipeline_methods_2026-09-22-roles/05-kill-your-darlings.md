# Role 5 — Kill Your Darlings (round 1, verbatim as returned)

GRANT 5 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is not an editing tool. I hold no Edit, Write, NotebookEdit or shell.)

## Run findings (about the review, not the artifact)

- **R1. The prose tool does not exist, so it was not run.** There is no `murderboard_prose.sh` at `tools\`, and none anywhere under `<primary checkout>`. By the checklist's own rule, "not run" is a failure, not a clean result. I have no tool output to paste. Word and sentence counts below are my hand estimates, marked "~".
- **R2. My role cannot run the tool even where it exists.** The checklist says to run `murderboard_prose.sh`, but my grant (Read, Grep, Glob) has no shell. This conflict is in the process file, not in this run. Either give role 5 a read-only runner, or have the main thread run the script and pass its output in. Otherwise this checklist item cannot be met by the role it names.
- **Substitute search.** I ran Grep on the source .md using the checklist's own banned list (the house convention in the generated role file): `not just|not only|it's not about|worth noting|delve|leverag|robust|seamless|crucial|landscape|tapestry|in today's|—`. It found nothing. A second pass for singular "data" (`data is/was/has/shows/itself`, `this data`) also found nothing. I checked three-item lists by eye (L22, L40): the items are real, not there for rhythm. I did not open the built HTML, PNG or DOCX. This role reads prose, and the source is what the build renders.

## Findings

Columns: location · issue · severity · suggested fix · verifiable against a source (yes/no)

**Contradictions and ambiguities**

1. **L40 vs L274.** L40 says the analysis applies "no further exclusion, filtering or windowing of its own". L274 then keeps 67 of 84 recordings and compares only baseline against the first treatment. That is an exclusion. · high · Change L40 to "…applies no further event- or ROI-level exclusion; recording selection is described under *Recordings analysed*." · yes
2. **L189, L233, L259: "seed" has two meanings.** At L189 and L225 it means the benchmark generator's seed. At L233, L235 and L259 ("training seeds") it means the model's initialisation seed. It is never defined in either sense. · high · At first use write "generator seed" and "initialisation seed", and use those terms throughout. · yes
3. **L61, L86–88: "participation" has two meanings.** It is the three planted levels (30%, 18%, 10%) and also a single benchmark value (0.18). The reader cannot tell which planted quantity 0.18 is. · high · Say what the 0.18 sets, for example "the middle participation level (0.18) was set from the measured median participation, 0.190". · yes
4. **L246 vs L217: merge gap of the learned detectors.** L246 says the learned detectors' "merge gap was re-selected". Decoding (L217) fixes it at 2 s. "After the run" (L245) is also undefined. · high · State once when and how the merge gap is chosen, and cut "after the run". · yes
5. **L111 vs L116: calls in the elevated-rate block.** "Unmatched calls are false alarms", yet precision leaves out calls in the elevated-rate block. The reader cannot tell whether those calls are false alarms. · medium · Write "Unmatched calls outside the elevated-rate block, including calls on distractors, are false alarms." · yes
6. **L94: "Three further recording types".** The elevated-rate test (L96) is not a separate recording. It is a subset of calls in the benchmark recording. · medium · Write "Three tests measure specific failures:". · yes
7. **L263 vs L270–272.** "Detection used the analysis windows", but LoCo, binned SCE and locust ran on the whole recording. · medium · Write "Calls were counted in the analysis windows supplied by the imaging pipeline." L263 also repeats L13, so cut one of them. · yes
8. **L281: "at least 12 min" when the stated minimum is 13 min** (L268: 13–20 min; L281: 13.0 and 14.9 min). The threshold and the data do not match, and "An earlier rule required 15 min" is project history, not method. · medium · State the rule actually applied, and drop the history from the manuscript. · yes
9. **L63: the renewal process is not fully specified.** It says "120 s plus a gamma-distributed excess with coefficient of variation 1" but never gives the excess's mean. Gamma with CV 1 is simply exponential. · medium · Write "120 s plus an exponential excess of mean __ s". · yes
10. **L110: "measured as 0 if the time falls inside it".** "Measured" has no subject. · low · Write "…when the distance from the event time to the interval (zero if inside) is at most 2.5 s." · yes
11. **L183–184: "its best admissible value exceeded the current objective".** This compares a parameter value with an F1. · low · Write "when the objective at its best admissible value exceeded the current objective by ≥ 0.002". · yes
12. **L213–214: the sentence misparses.** "…where the positive weight is the negative-to-positive frame ratio, and the Adam optimizer." reads as if Adam were part of the where-clause. · low · Split into two sentences, or lead with "Models were trained with the Adam optimizer on weighted binary cross-entropy (positive weight = …)". · yes
13. **L218: "41 values between 10⁻⁴ and 0.9999"** does not say the spacing (linear, logarithmic or logit). "Held-aside training recordings" contradicts itself. · low · Name the spacing, and write "two recordings held out from training". · yes
14. **L235–236: "Each refit trained on 10 of the tuning recordings".** It does not say which 10, or why only 10 of 72. · medium · Say how the 10 were chosen. · yes
15. **L148 vs L145: context "around" vs "centred on" the window.** This reads as a difference between CoactDetect and LoCo, but Table 1 gives both a 120 s context. · low · Use one phrase, or state what actually differs (the null statistic). · yes
16. **L151: "thresholds each analysis window at the 98th percentile".** The count per bin is thresholded; the null is built per window. · low · Write "thresholds each bin's count at the 98th percentile of a circular-shift null built per analysis window". · yes
17. **L153 vs L146/L148/L151: "circular-roll null" vs "circular-shift null".** It is unclear whether these are the same thing. · low · Use one term, or define the difference. · yes
18. **L293–294: "or within the call itself if it is longer".** "It" and "longer" have no clear referent: longer than what? · low · Write "…within 1 s of the call's centre, or anywhere within the call if the call is longer than 2 s". · yes
19. **L302: "always less than 0.5 s apart".** "Always" overclaims. "The grouping chains" is jargon. · low · Write "…are often less than 0.5 s apart, so one group can span a whole long call." · yes

**Undefined terms and abbreviations** (house rule: define at first use)

20. **SCE (L108, L150), TTX (L274), senktide (L274), CICADA (L154), F1 (L117, formula only, never named).** · medium · Expand each at first use: synchronous calcium event, tetrodotoxin, senktide with its receptor target, CICADA's full name, "F1 score". · yes
21. **"call" (first used L96, defined L108), "setting" (L121), "objective" (L119, whose objective?), "shipped setting" (L134, first explained in the Table 1 caption at L166).** · medium · Define "call" and "setting" at their first use. Write "optimization objective". Replace "shipped" with "the default setting published with each implementation". · yes
22. **"coded detectors" (L137, L139).** This is project jargon for rule-based detectors. · low · Write "rule-based detectors (hereafter coded)", or just "rule-based". · yes
23. **Table 1 parameters with no definition anywhere: guard, null context (symmetric), synchronous frames, minimum distance, sustain level, maximum gap (L172–176).** Merge gap (L160) is used circularly ("calls closer than the merge gap are joined"). · medium · Add one-clause definitions to the detector bullets or to a table note. · yes
24. **L160–163: "ports", "verified to a tolerance of 10⁻⁹".** Ported into what language? Is the tolerance absolute or relative, and on what quantity? The sliding-window modes have no MATLAB counterpart, which implies they are unverified, but the text does not say so. · medium · Write "Python ports…, agreeing with MATLAB to 10⁻⁹ (absolute, on call times)", adjusted to what was actually compared. Add "the sliding-window modes were therefore not verified against a reference". · yes
25. **L211: "each cell's vote"** is an undefined metaphor. **L205: "population activity"** is undefined: a count or a fraction? · low · Write "each cell's encoder output". Write "number of active cells per frame". · yes
26. **L250: "ahead of a coded one separably"** is a coinage that is hard to read. · low · Write "A learned detector's lead over a coded one is called separable when…". · yes
27. **L102–103: "crowding" is defined after it is used.** "7 of 39 recordings" has an unexplained denominator (the dataset has 84). · medium · Move the definition before the 0.38 threshold, and say what the 39 are. · yes

**Name things, don't index them**

28. **L203–211, L259: code identifiers `line_length`, `chorus_norm`, `chorus_gain_norm`.** · low · Give readable names, or keep one identifier per architecture but define the family once. · yes
29. **L259: "the refit from fold 0 and training seed 2 of the replication".** These are zero-based internal indices. "The upper of the two middle values among its 20 refits" is the upper median, and the 20 (4 outer folds × 5 training seeds) is never derived. · medium · Write "the upper-median refit of the 20 in the replication (4 outer folds × 5 initialisation seeds)". Drop the indices, or move them to supplementary. · yes

**Draft state in a manuscript**

30. **L88–89, L135, L281, L302–305: ⚠ lines and "scheduled", "not yet been approved", "under review", "an earlier rule".** These are notes on the project's status. A methods section states what was done. · medium (for manuscript use) · Resolve each before submission, or move them to a cover note. Keep them in the review draft. · yes
31. **L91–92: "The measurement was made on the export before floor-pinned windows were removed and repeated on the current export."** "Current export" is internal. · low · Write "Removing the floor-pinned windows changed no measured value at four decimal places." · yes
32. **L284–285: "compared statistically in a separate analysis, not described here".** This is a dead end in a methods section. · low · Point to where it is described, or cut. · yes

**Redundancy and cuts** ("as brief as possible")

33. **L14 + L16.** "Recording metadata give the frame interval" and then "Every recording was acquired at a frame interval of 0.1 s." · low · Merge: "Recording metadata give the frame interval (0.1 s for every recording) and the animal's group." · yes
34. **L80–81: "and carries all of the elements above"** buys nothing. · low · Cut. · yes
35. **L154–155: "It is a partial, modified port of … CICADA's own transient detection is replaced… Its results are not results of CICADA."** The last sentence repeats the first two. · low · Keep it only if the author wants the disclaimer on purpose, and say so. Otherwise cut. · yes
36. **L192: "For CoactDetect and LoCo the search ran with sliding windows"** repeats "mode · sliding" in Table 1. · low · Cut, or keep only one of the two. · yes
37. **L289: "A detector's own call width follows its own rule"** says "own" twice. · low · Write "Each detector sets call width by its own rule." · yes
38. **L67–68 lead: "Two kinds of structure are included that a coordination detector should not report:"** · low · Write "Two structures a detector should not report:". · yes

**Order within blocks** (payload promotion; the section order is role 11's)

39. **L16–20 (~65 words).** The payload, "this section describes the fast stream only", comes in the last sentence. · low · Lead with it and fold in the stream definitions. · yes
40. **L47–59.** "Background rate" is used at L48 and defined at L53–57. The payload, "every synthetic recording is generated at both" rates, is the last sentence (L59). · low · Open with "Each synthetic recording is generated at two background rates, quiet and busy (…)", then describe the gamma modulation. · yes
41. **L61–92: the benchmark definition comes last.** "33 cells" is used at L62. "The benchmark recording is 2,700 s long with 33 cells" does not come until L80. · medium · Put the benchmark definition (length, cell count) first under *Synthetic recordings*. · yes
42. **L36–37.** The definition of floor pinning ("an ROI reported the frame minimum") comes after the count. · low · Define it first. · yes
43. **L160: "Calls closer than the merge gap are joined."** It sits between the detector list and the verification sentence. · low · Move it to the call definition in *Scoring* (L108). · yes

**Style for a manuscript**

44. **L225: the sentence opens with the numeral "48".** L70 writes "six" and "6 cells" in one sentence. · low · Write "Forty-eight…" or reword. Use numerals consistently. · yes
45. **L299: "amplitude" = cells per second.** That is a density or rate. A reader will read "amplitude" as fluorescence (L10 already uses event amplitude in that sense). · medium · Rename (for example "recruitment rate"), or state the collision. · yes
46. **L27–30, L277–278: group codes MALE, DI, ORX, OVX.** An all-caps "MALE" reads as a code, not a word. · low · Use "M" or "intact male", and use it consistently. · yes

## Passage test (block · ~words · payload · what the rest buys)

- **L8–14** (~110 words). Payload: analyses start from exported event tables, split into periods with analysis windows supplied by the pipeline. It is in the first sentence. The rest is needed field definitions. Only L14 is redundant with L16 (see finding 33).
- **L16–20** (~65). Payload: fast stream only. It sits at the end, so promote it (39).
- **L22–30** (~35 plus the table). Clean.
- **L32–40** (~85). Payload: two artifact classes removed upstream, and nothing further. The L40 clause contradicts L274 (1).
- **L47–59** (~115). Payload: the two-rate background, which sits at the end (40).
- **L61–65** (~70). Clean, apart from the missing excess mean (9).
- **L80–92** (~150). Payload: "Generator parameters were measured on the recorded baseline fast stream; all but participation fall inside their bootstrap 95% intervals." The words bought beyond that are "carries all elements above" (cut), measurement history (cut to a clause, 31) and a draft ⚠ (30). The block could be about 60 words.
- **L94–104** (~140). Each bullet puts its purpose second, which is fine. The close-events bullet uses "crowding" before defining it (27).
- **L108–121** (~110). Tight. Undefined "setting" and "objective" (21).
- **L139–163** (~250). The longest block. The bullets are dense but each earns its place. The trailing paragraph (L160–163) mixes merging and verification (43, 24).
- **L180–192** (~130). Tight, apart from the redundant last sentence (36).
- **L196–219** (~230). Tight. Identifiers and the misparsed sentence (28, 12, 13).
- **L223–254** (~300). The two ambiguities that matter most are here: the two meanings of "seed" (2) and the L245–246 merge-gap sentence (4). Otherwise it is justified by the procedure.
- **L258–285** (~230). Selection of the reported detector is written as indices (29). Contradiction with L40 (1). Draft ⚠ (8).
- **L289–305** (~170). The payload (one rule for every detector) is in the second sentence, which is fine. The ⚠ paragraph is a draft note (30).

The house voice mostly holds: short declarative sentences, no throat-clearing, no recap, no banned constructions. Most defects are about precision (1–19) and undefined terms (20–27), not about length.

Files: the source is docs\methods\coordination_pipeline_methods.md, and the tool that is missing is tools\murderboard_prose.sh.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
