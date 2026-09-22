# Role 11 — Start With the Problem (round 1, verbatim as returned)

GRANT 11 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is only the channel for this report. I hold no editing tool, and I modified no file.)

**Role 11: argument order ("Start With the Problem"), read as dependency order for a methods section**
Artifact: docs\methods\coordination_pipeline_methods.md

**Arc used, as the brief asked.** For a methods section the order should follow dependency: input data → constructed test material → the instruments (detectors) → the yardstick (scoring and admissibility) → the tuning that uses the yardstick → learned models → the comparison → application to recorded data → the downstream measurement. Every term, table and population should be introduced before it is used. The cold-open test becomes "does it open on the input?" It does.

### Spine: one claim per section, in document order
1. **Detected calcium events.** The input is an export of detected events: ROI, t50rise, amplitude, width, periods and windows. There are 84 recordings in 4 groups, the fast stream only, and the producer removed two artifacts. The analysis applies no filtering of its own.
2. **Synthetic recordings.** The benchmark recording, built from a generator whose parameters were measured on recorded baselines, contains 15 planted events, distractors and an elevated-rate block at two background rates. Three test recordings target specific failures.
3. **Scoring.** Calls are matched to planted events within 2.5 s, one-to-one. The objective is F1 averaged over the two backgrounds. A setting must pass the four admissibility limits in Table 2.
4. **Coded detectors.** It describes six coded detectors, with their verification, and gives the settings used on recorded data in Table 1.
5. **Optimization of coded detectors.** Settings were chosen by coordinate search over admissible values on seeds 1–48 and confirmed on seeds 49–96.
6. **Learned detectors.** Four small frame-wise architectures are trained with weighted cross-entropy and decoded by a threshold and a 2 s merge.
7. **Comparison.** Coded and learned detectors are compared under 4-fold nested cross-validation, with two selection rules and a replication. Separability is judged by a Nadeau–Bengio corrected t.
8. **Analysis of recorded data.** The six coded detectors run at their Table 1 settings, plus one chosen learned refit, inside pipeline-supplied windows, on the 67 recordings whose first treatment was TTX or senktide.
9. **Width and amplitude.** One rule for all detectors derives the width and amplitude of each call from the recorded events inside it.

**Cold open.** The first thing a reader sees is the input data. That is the correct opening for a methods section and matches the PI's first item. No finding.

**Overall.** At section level the order is mostly sound. Sections 5→6→7→8→9 each depend only on what comes before. The defects are three backward dependencies across the section 3/4 boundary, and definitions stranded in late sections that earlier sections already rely on.

### Findings
Each finding gives location · issue · severity · suggested fix · could-I-verify.

**F1 · Table numbering (lines 121, 123, 139, 165) · major · verified: yes**
- Issue: Table 2 is cited (line 121) and printed (line 123) before Table 1 is first cited (line 139). Journals number tables in order of first citation.
- Fix: move Coded detectors ahead of Scoring (F2), then renumber so the first table cited is Table 1. Alternatively, swap the two numbers where they stand.

**F2 · Scoring section (lines 108, 127, 134) needs the Coded detectors section, which comes after it · major · verified: yes**
- Line 108 carves out "binned SCE reports its bin extent" before binned SCE has been introduced.
- The Table 2 columns name all six detectors before any is described.
- Line 134 bases the limits on "the shipped settings' measured rates", but "shipped setting" is first explained in the Table 1 caption (line 166).
- Line 108 assumes each call has a "width". That calls' widths follow each detector's own rule is only said in section 9 (line 289).
- Fix: order the sections as Coded detectors → Scoring → Optimization. Describe the detectors first (the six bullets and the port/verification paragraph). Say in one clause there that each detector reports a call with an onset and an extent. Then give Scoring.

**F3 · Table 2, close-events row (line 132): "the setting it replaces" · moderate · verified: yes**
- Issue: the idea of one setting replacing another only exists once the coordinate search is described (Optimization, line 184–185). At Table 2 the reader cannot evaluate the row.
- Fix: either move the admissibility table into Optimization, or add a one-line forward pointer ("the setting a search step would replace; see Optimization").

**F4 · Table 1 (lines 165–176) shows the search's output before the search is described · moderate · verified: yes**
- Issue: the caption says CoactDetect and LoCo "use the values selected by the search described under *Optimization*". The result arrives before the procedure that produced it.
- Fix: keep the detector descriptions in Coded detectors, but place the settings table at the end of Optimization (or at the head of Analysis of recorded data, where it is used, line 258). This also fixes the numbering if Admissibility becomes Table 1.

**F5 · Analysis windows are defined in section 8 (lines 263–268) but used from section 2 onward · moderate · verified: yes**
- Section 1 (line 13) says each period "carries an analysis window supplied by the imaging pipeline" without saying what it is.
- Section 2 (line 82) measures the benchmark on "the baseline analysis windows".
- The window rule (last 20 min of baseline, 2 min into treatment, 20 min cap) only arrives in section 8.
- Since the windows are supplied by the pipeline, they belong to the input.
- Fix: move the **Windows** definition list into section 1. Section 8 keeps only the sentence on which detectors ran per window and which ran on the whole recording.

**F6 · Recording subsets introduced after measurements made on them (lines 82, 102, 274–278) · moderate · verified: yes**
- Section 2 measures the benchmark parameters "on the baseline analysis windows of the recorded fast stream". It does not say whether that means all 84 recordings or the 67 analysed.
- Line 102 cites "7 of 39 recordings". A population of 39 is introduced nowhere, before or after.
- The only subset rule (67 recordings, TTX or senktide first) arrives in section 8.
- Fix: state in section 1 which recordings each later step draws on (measurement set, crowding set, analysed set), or state the set at each point of use. Whether "39" is correct is for agents 2 and 4. My finding is only that it arrives with nothing that lets the reader evaluate it.

**F7 · Learned detectors (lines 196–219): the training data are described only in the next section · moderate · verified: yes**
- Issue: section 6 says how models are trained, but not what they are trained on. It mentions "two held-aside training recordings" (line 219) with no training set to set them aside from. The training set ("10 of the tuning recordings", line 235–236) is first described in section 7.
- Fix: add one sentence to Training in section 6 saying models were trained on synthetic benchmark recordings, with the split given under Comparison. Or move the refit description up.

**F8 · Line 246: "when their merge gap was re-selected" · minor · verified: yes**
- Issue: section 6 fixes the learned merge gap at 2 s (line 218). Re-selecting it is never introduced, so this sentence depends on a step that appears nowhere.
- Fix: introduce the re-selection in Decoding (section 6) or in Two selection rules.

**F9 · "call" and "false alarm" used before Scoring defines them (lines 96–99, 104) · minor · verified: yes**
- Issue: the test-recording bullets say "calls made inside", "Every call is a false alarm" and "fuses separate events". "Call" is defined at line 108.
- Fix: give a one-clause gloss at first use in section 2 ("a call, a detector's report of a coordinated event"). Or acceptably keep it, because section 2 must precede Scoring (Scoring needs the elevated-rate block and the test recordings).

**F10 · "seeds" first appears in Optimization (line 189) · minor · verified: yes**
- Issue: the synthetic section never says that benchmark recordings are indexed by random seed. Seeds 1–48 and 49–96 are therefore the first mention of a population the reader has not been told exists.
- Fix: add one sentence at the end of "The benchmark recording" saying each seed gives one recording at each background.

**F11 · Process: the document departs from the PI's specified order, and the departure is unstated · major (for the run record, not the manuscript) · verified: yes against the brief**
- The PI's order has optimization (3) and model training (4) before the benchmark (5), the scoring parameters (6) and the knobs for each detector (7).
- The document has benchmark (inside §2) → scoring (§3) → knobs (§4) → optimization (§5) → training (§6), plus a Comparison section (§7) the PI did not list.
- In dependency terms the document's order is the more defensible one. Optimization cannot be stated before its objective, admissibility limits and parameters are, and the benchmark is what optimization runs on. Taken literally, the PI's order would put a use before each of its definitions. So the fix is not to reorder the document to the PI's list.
- The PI's item 5 ("what the benchmark is and how it was determined") has two readings. It may mean the synthetic benchmark recording (lines 80–92), or the coded-versus-learned comparison (§7). The draft resolves it silently.
- Fix: the main thread should put the deviation and the ambiguity to the PI explicitly. Something like: "scoring and knobs moved ahead of optimization because optimization uses them; the benchmark is described inside Synthetic recordings; Comparison added". Record the ruling. Do not leave the reordering implicit.

### Where each section can first be understood, and its job

| § | job in the argument | earliest intelligible position | verdict |
|---|---|---|---|
| 1 | defines the input | 1 | holds, once F5 and F6 are absorbed |
| 2 | defines the test material | 2 | holds; needs a gloss for "call" (F9) and seeds (F10) |
| 3 | defines the yardstick | after §4 | **move** (F2) |
| 4 | defines the instruments | 3 | **move up**; its settings table moves down (F4) |
| 5 | tuning | after §3 and §4 | holds |
| 6 | learned models | after §2 and §3 | holds; missing its training data (F7) |
| 7 | comparison | after §5 and §6 | holds |
| 8 | application to recorded data | after §4, §5 and §7 | holds; give its window definition to §1 (F5) |
| 9 | downstream measurement | after §8 | holds; correctly last, matching the PI |

No section lacks a job, so nothing belongs in an appendix.

**Recommended order (smallest change):**
1. Detected calcium events, gaining the windows and the recording subsets.
2. Synthetic recordings.
3. Coded detectors, descriptions only.
4. Scoring, with the admissibility table as **Table 1**.
5. Optimization, closing with the settings table as **Table 2**.
6. Learned detectors.
7. Comparison.
8. Analysis of recorded data.
9. Width and amplitude.

Outside my scope: the ⚠ flags at lines 88, 135, 281 and 302 are for other roles. I only note that each one arrives at a position where the reader can evaluate it.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
