GRANT 5 ok — Read, Grep, Glob

Run note: no editing tool is in my function list. The harness also injected instructions for three MCP servers (Claude_Docs, Dropbox, github), and Dropbox has create, move and delete tools. None of those tools reached my function list, so I held none of them. I am noting it because a fallback spawn could expose them.

**Tool status.** `murderboard_prose.sh` is **not vendored**. `<repo>/tools/` has only `murderboard_agents.py`, `murderboard_freshness.sh`, `murderboard_revendor.py` and `murderboard_roster.sh`. So the search below was run by hand with Grep and the word counts are hand counts. Count this as "tool not run, manual substitute", not as a clean tool pass.

**List used.** I ran the process file's house list: not just/not only X but Y · it's not about A, it's about B · it's worth noting · delve · leverage · robust · seamless · crucial · landscape · tapestry · "In today's" · em-dash pivot · rhythmic triples. I also checked the repo's own rules: "fire" in any form, singular "data", "modality", and British spellings (writing_conventions.md, "American English").

## Banned-construction search (Grep on the HTML, output as returned)

- Pattern `(?i)not just|not only|it's not about|it&rsquo;s not about|worth noting|delve|leverag|robust|seamless|crucial|landscape|tapestry|in today|&mdash;|—|\bfir(e|es|ed|ing)\b|data (is|was|shows|has)` → **No matches found**
- Pattern `(?i)modality|\bdata\b` → line 25 `data`, line 29 `data`. Both are used without a verb ("taken from data", "fitted to the data"), so neither breaks the plural rule.
- **Em-dashes:** none in the file, so no em-dash pivots.
- **Three-item lists (judged by reading):** fast/slow/combined; (onset, span, count); mean, SD and top-four mean; precision, recall and F1. Each lists things that really are three. **No rhythmic triples.**
- **British spellings, found by reading (line · word):**
  - 29 · neighbours
  - 37 · standardised
  - 37 · labelled
  - 39 · centre

## Per-block table

All counts are by hand, about ±10%. The body totals about 1,090 words.

| Block (line) | Words | Sentences | Payload sentence | Where the payload sits | What the other words buy |
|---|---|---|---|---|---|
| Input (25) | ~143 | 6 | "The input is onset times (t50, 0.1 s grid) per ROI in fast, slow and a combined union stream." | Spread across the first three sentences. | The dataset counts are evidence a reader needs. "Detectors read onsets only" repeats "not from fluorescence traces". The last sentence (baseline windows only) belongs to the Parameters block. |
| Participation floor (27) | ~85 | 3 | Sentence 3: "the floor is the smallest count K of ROIs co-active within a 2 s window whose chance crossings stay at or below 1 per hour, and never fewer than 3 ROIs." | **At the end.** Sentence 1 is a looser preview of it. | The null construction is evidence and stays. "(a rigid shift)" and the unused symbol K buy nothing. |
| Parameters for simulation (29) | ~180 | 5 | "Four quantities were measured from baseline data and set the simulator: timing spread, background rate, participation, spacing." That sentence is **missing**, and the block opens straight into a list. | Absent | The numbers are evidence and stay. The block is a list without a thesis. |
| Simulated recordings (31) | ~117 | 5 | Sentences 1–2: 32 ROIs, 45 min, measured event count at three participation levels on a quiet or busy background. | Start | Empty and stress recordings, the ORX variant and seed separation are all needed. The problem is naming, not length (see findings). |
| Scoring (33) | ~88 | 3 | "Matched F1 (2.5 s tolerance) under fixed false-call budgets." | Start | Everything is needed. One term is undefined (the precision-drop baseline). |
| CoactDetect (35) | ~176 | 6 | "The method is a cell-averaging constant-false-alarm-rate (CFAR) test" (sentence 4) on the distinct-ROI count S(t). | **Buried mid-block.** | Sentences 5–6 cover the optimization rules. They are evidence a sceptic wants, but they are dense ("a best value at the limit that switches a setting off was reported as a finding"). |
| Chorus (37) | ~207 | 7 | "A learned, ROI-order-invariant convolutional detector, trained per stream on simulated recordings." | Split across sentences 1 and 3. | The architecture and training details are evidence. The last sentence (paired F1 comparison with CoactDetect) is **the benchmark, not Chorus**, and belongs in Scoring. |
| Output (39) | ~108 | 3 | Sentence 3: event time = call onset; width = core onset span; amplitude = core ROIs ÷ width, a packing measure, not fluorescence. | **At the end** | The core-extraction rule in sentence 2 is needed. "the flow" and "fixed aperture" are jargon. |

## Findings

Each finding gives location · issue · severity · suggested fix · verified (yes/no).

1. **L25, 27, 31, 35, 39, 37 · "window" carries five meanings.** They are: baseline windows (analysis epochs); "for each window and stream" (a recording epoch); the 2 s co-activity window; CoactDetect's (t − w, t], "a window is called", and "context window"; and "409.6 s crops" in Chorus, which are windows by another name. A PI cannot tell which window the floor is computed "for". · **major** · Name the recording epoch once ("condition window: baseline or treatment") at L25. Say "2 s coincidence bin" for the floor and "context span" for CoactDetect. Keep "window" for one meaning only. · yes

2. **L31 → L33 · named items are renamed after their definition.** "Two further recordings carry nothing planted: one at quiet background" becomes "the empty recording" in Scoring and Chorus. "a 300 s stretch at the 99th percentile" becomes "the elevated-rate stretch". The seed sets "selection, held-out confirmation and final scoring" become "held-out", "test recordings" and "fresh seeds". A reader has to match names across blocks. · **major** · Name each item where it is defined: "an *empty recording* (quiet background, nothing planted) and a *stress recording* (…300 s at the 99th percentile…)". Use exactly "selection / held-out / final" seeds everywhere, and replace "test recordings" at L37 with one of them. · yes

3. **L33 · "a precision drop of at most 0.10": the baseline is unstated.** Is it a drop from the shipped setting, from CoactDetect, or between seed sets? The sentence cannot be checked as written. · **major** · Say what it drops from, e.g. "at most 0.10 below [X]". · yes (text); the intended baseline is not verified

4. **L37 last sentence · the benchmark comparison sits inside the Chorus block.** "Every detector was compared with CoactDetect on fresh seeds as a paired F1 difference…" is the benchmark method, and it currently reads as part of how Chorus was trained. "Every detector" also contradicts the two-detector scope. · **major** · Move it to the end of Scoring as "Chorus was compared with CoactDetect…". This moves a sentence between paragraphs, which is role 5's call. The order of sections is role 11's. · yes

5. **L29 · Timing-spread parenthetical is ambiguous.** "calibrated on simulations with known spread (fast 0.105 s, slow 0.131 s, combined 0.150 s)" puts the values right after "known spread". They read as the calibration inputs, not the measured SDs. · **major** · Put the values right after "standard deviation (SD) of participant onsets". Put the calibration clause last. · yes

6. **L29 · Participation is given for fast only.** "(fast 0.20)" has no slow or combined value, and "the outer two bracket it" gives no bracket values. Every other parameter has three streams and exact values. · **minor** · Give all three streams and the two outer levels, or say they are omitted by design. · yes

7. **L29 · Spacing numbers look inconsistent next to each other.** A median gap of 41.3 s sits beside 9.7 events per hour (a mean gap of about 370 s). The pair may be correct, if events cluster, but a reader will stop and suspect a typo. · **minor** · Add a few words: "gaps are clustered: median 41.3 s, overall rate 9.7 events per hour". · no (not checked against the measurement)

8. **L25 last sentence · "Every parameter taken from data below was measured on baseline windows only."** It is in the wrong block, and "below" is ambiguous (data below, or parameters described below?). · **minor** · Make it the opening of Parameters: "All parameters below were measured on baseline windows only." · yes

9. **L25 · "The pipeline starts from … exported by the imaging pipeline."** Two different pipelines are called "pipeline" in one sentence. · **minor** · "Detection starts from the calcium-event tables the imaging pipeline exports…" · yes

10. **L25 · "Detectors read onsets only."** This repeats "not from fluorescence traces" and the widths clause. · **minor** (cut for space) · Fold it into the widths clause: "…differing only in the width attached to each event, which detectors ignore." · yes

11. **L27 · Payload at the end; sentence 1 misstates it.** "at least as many co-active ROIs as chance could produce" is weaker than, and different from, the actual rule (chance crossings ≤ 1 per hour). · **major** · Open with the definition from sentence 3, then give the null construction. Delete sentence 1. · yes

12. **L27 · "(a rigid shift)" and the symbol K.** The first repeats "whole onset train is shifted by its own offset". K is defined and never used again. · **minor** (cut) · Delete both. · yes

13. **L27 · "keeps each ROI's rate and timing".** "Timing" is exactly what the shift changes. The clause means the inter-onset intervals are kept. · **minor** · Replace with "keeps each ROI's rate and inter-onset intervals". · yes

14. **L35 · Undefined symbol w and term "merge gap".** "(t − w, t]" uses w without defining it. The repo's CLAUDE.md requires every symbol defined before use. "merge gap" gets no value. · **major** (house rule) · Add "w, the coincidence width," and give the merge gap as a tuned setting. · yes

15. **L35 · The CFAR identification is buried as sentence 4.** It is the sentence that tells a PI what the detector is. · **minor** · Open with it: "CoactDetect is a cell-averaging constant-false-alarm-rate (CFAR) test (Finn & Johnson, 1968) on S(t), the number of distinct ROIs with an onset in (t − w, t]." · yes

16. **L35 · "from the shipped point" and "a best value at the limit that switches a setting off was reported as a finding, not adopted".** The first is undefined jargon. The second takes three readings to parse. "extending any grid whose best value lay at an edge" and "bracketed by tested values" say half the same thing. · **minor** · Use "from the default settings". Rewrite as "A setting whose best value turned it off (e.g. guard = 0) was reported, not adopted." Keep one of the two bracketing clauses. · yes

17. **L37 · "each channel is standardised".** "Channel" is never defined; the filter output is not called channels. · **minor** · Add "the filter's output channels". · yes

18. **L37 · Floor offsets without a unit.** "extra events planted at floor − 1, floor and floor + 1" breaks the every-number-carries-its-unit rule. · **minor** · Change to "with participation of floor − 1, floor and floor + 1 ROIs". · yes

19. **L37 · "409.6 s crops".** This is jargon, and it is also a sixth window-like term. · **minor** · Change to "409.6 s training segments". · yes

20. **L37 · Code identifiers "chorus_norm" and "chorus_norm_part".** These are lookup keys, which runs against "Name things; don't index them". The brief names the detector "chorus". · **minor** · Use "Chorus" and "Chorus with participation input". Put the identifiers in parentheses once, if they are needed at all. · yes

21. **L31 · "fast's are doubled to keep the number of scored events comparable".** The possessive is awkward, and it is unclear what is doubled. · **minor** · Change to "fast gets twice as many seeds, because it plants fewer events per recording". · yes

22. **L39 · "the flow returns" and "fixed aperture".** "Flow" is undefined; "aperture" is jargon. · **minor** · Use "the detector returns" and "a fixed span around the call's center". · yes

23. **L39 · Non-parallel list.** "(±1 s fast; ±5 s slow and combined)" is followed by "more than 0.5 s (fast) or 2.5 s apart". The second list leaves out which streams the 2.5 s applies to. · **minor** · Change to "0.5 s (fast) or 2.5 s (slow and combined)". · yes

24. **L39 · Amplitude = core ROIs ÷ width is undefined when width = 0.** This happens with a one-ROI core or identical onsets. Precision issue, flagged here for role 4. · **minor** · Say what is reported when width = 0. · no

25. **L29, 37, 39 · British spellings.** "neighbours", "standardised", "labelled", "centre" break the house rule in writing_conventions.md. · **minor** · Change to "neighbors", "standardized", "labeled", "center". · yes

26. **L25 · Group counts without a unit after the first.** "(OVX, 17), (MALE, 13), (ORX, 19)" are bare counts. The rule says "never a bare count". · **minor** · Change to "(OVX, 17 recordings)" and so on, or rewrite as "…in four groups (recordings): DI 17, OVX 17, MALE 13, ORX 19". · yes

27. **L23 note · "under ADR-0010".** An ADR number is an index, not a name. · **minor** · Name what ADR-0010 decided, with the number in parentheses. · yes

28. **L29 · The block has no topic sentence.** At ~180 words, the reader gets four italic sub-labels without being told why these four. · **minor** · Add an opening sentence (see table), or accept it as a list with the baseline-only sentence from finding 8 as its opener. · yes

## Summary for adjudication

- **The prose is lean.** No banned constructions, no throat-clearing, no closing recap, and every block is dense with evidence.
- **Length is not the defect; naming and placement are.**
  - Majors 1–2 are term drift: "window" has five meanings, and the empty/stress recordings and seed sets are renamed after they are defined.
  - Major 4 is a sentence in the wrong block.
  - Majors 3 and 14 are undefined terms: the precision-drop baseline, and w with the merge gap.
  - Major 5 is an ambiguous parenthetical.
  - Major 11 puts the payload at the end of the floor block.
- **Suggested cuts:** "Detectors read onsets only", "(a rigid shift)", K, the duplicate bracketing clause at L35, and the vague floor preview. Together these free roughly 40 words. That pays for the added definitions (w, window names, units) without breaking the one-page limit.

Artifact: <repo>/docs/methods/one_page/methods_one_page.html
House rules applied: <repo>/docs/writing_conventions.md, <repo>/CLAUDE.md
