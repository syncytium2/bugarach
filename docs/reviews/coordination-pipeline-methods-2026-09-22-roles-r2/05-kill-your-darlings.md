# Role 5 — Kill Your Darlings (round 2, blind pass, verbatim as returned)

GRANT 5 ok — Read, Grep, Glob

Role 5 (Kill Your Darlings), round 2, blind pass. Artifact: `docs\methods\coordination_pipeline_methods.md` (commit 464d995 per the brief; I did not check the hash). Read-only; I edited nothing.

## Run findings (about the run, not the artifact)

| # | issue | severity | fix | verifiable |
|---|---|---|---|---|
| R1 | The prose tool `tools/murderboard_prose.sh` does not exist. A Glob for `tools/murderboard_prose*` in the methods worktree found nothing. So there is no tool output to paste, and the tool-receipt part of this role is **not run**. I did the checks by hand with Grep. | medium | Vendor or write the tool, or remove the requirement from role 5 in the process document | yes |
| R2 | Which banned list I ran: `docs/writing_conventions.md` has no list of banned constructions (a Grep for delve/leverage/robust/crucial/em-dash/banned returned nothing). I used the role-5 checklist's own list: *not just X but Y*, *it's not about A*, *it's worth noting*, delve, leverage, robust, seamless, crucial, landscape, tapestry, em-dash pivot, *In today's*, rhythm triplets. I also ran the house rule that "data" is plural. | low | Name the list in the process file or in writing_conventions | yes |

## Mechanical results (by hand)

- **Banned words and phrases:** 0 hits in the body. The only em-dash is L422, in a reference title (PySpike—A Python library), so it is not a pivot.
- **Rhythm triplets:** none found. Every list of three names three real things (for example L16 and L143–178).
- **"Data" verbs:** 0 violations. "Data" appears at L29, 98, 249, 287 and 336, and none of these takes a verb.
- **Abbreviations and units:** failures are listed below as F4, F5, F24 and F25.

## Finding list

Severity: H = a reader could misread the method; M = imprecise or out of order; L = could be cut or smoothed.

| # | location | issue | sev | suggested fix | verifiable |
|---|---|---|---|---|---|
| F1 | whole document (L7, 78, 81, 100, 370) | "Event" means three different things: a calcium event, a coordinated event and a planted event. L7 defines a coordinated event as "a set of cells". L370 redefines it as "the group with the most distinct cells". L100 says "cannot see smaller events", meaning coordinated events with fewer than 4 cells. L81 says "Successive event times" and L80 says "at the event time", meaning planted events. | H | Use "calcium event" only where it is ambiguous; always write "planted event" and "coordinated event" in full. At L370 write "the call's core group", not "the coordinated event". At L100 write "coordinated events of fewer than 4 cells". | yes |
| F2 | L9, L189, L193 | L9 says a call has "an onset and an extent", L189 uses "width" and L193 uses "extent". These are two names for one quantity. | M | Use "width" throughout: "an interval, given by its onset and width". | yes |
| F3 | L80, L191–192 | "Nominal time" is used in Scoring (L191) and defined only there (L192), but the planted-event paragraph already needs it at L80 ("the event time plus Gaussian jitter"). | M | At L80 write "at the planted event's nominal time plus Gaussian jitter". Move "The nominal time is the time before jitter" there and delete it from L192. | yes |
| F4 | Table 1 caption (L29, L31) | TTX and senktide are used here and defined only at L354–355. SB222200 (L356) is never defined. | H | Define all three at first use, at L29: TTX (tetrodotoxin, a voltage-gated sodium channel blocker), senktide (a neurokinin-3 receptor agonist), SB222200 (a neurokinin-3 receptor antagonist; confirm against source). Then shorten L354–356 to the counts only. | yes |
| F5 | Table 1 (L33–36) | The group abbreviations DI, MALE, ORX and OVX are defined and never used again. | L | Delete the parentheticals. | yes |
| F6 | L20 | "From the same event detection" clashes with "detector", which the document reserves for coordinated-event detectors. It is also unclear whether the two streams hold the same events with different widths or different event sets. | M | Rewrite as: "Each event is exported twice, as two streams that differ only in how width is measured." If the event sets differ, say so. | no (needs the export specification) |
| F7 | L20–23 (block) | The payload, "fast stream only", comes last. "Rounded to the frame" is loose. | L | Rewrite as: "These methods use the fast stream, in which an event's width is its width at half prominence (MATLAB `findpeaks`), rounded to the nearest 0.1 s frame. The slow stream, not used here, takes the width from t50rise to peak." | yes |
| F8 | L17 | t50rise is named but not defined. | L | "…the time at which the event's fluorescence reaches half its rise (t50rise)". | yes |
| F9 | L46–47 | "8 windows on 8 ROIs in 4 recordings" is followed by "56 fast events … in 3 recordings". The reader cannot tell why 4 recordings became 3. "Screening cut" (L47) is undefined. "Has not been screened" is the wrong tense for a methods section. | M | Add "(the fourth held no fast events in its windows)" or whatever the reason is. Define the screening cut or cut the clause. Write "was not screened". | no |
| F10 | L49–51 | The heading "ROIs and periods" also covers a withdrawn recording. "Judged dead" and "not evaluated" do not say by whom or on what criterion. | L | Retitle it "ROIs, periods and recordings". Write "judged dead by the laboratory; ROI viability was not assessed in 18 recordings". | no |
| F11 | Table 2 caption (L107) vs L39–47 | L39 says the pipeline removed floor-pinned windows before export. The caption says the constants were "re-measured on the export before floor-pinned windows were removed". So there are two exports, and "the export" has no single referent. | H | Name the two exports ("an earlier export, before…" / "the analysed export"), or state that the re-measurement predates the removal. | no |
| F12 | Fig. 1 caption (L65–68) | The caption uses "participation level" and "distractors" before the text defines them. "Nothing is drawn on it" is a house convention, not information for a manuscript reader. | L | Cut "nothing is drawn on it". The forward reference can stay if the figure moves after the Distractors paragraph. | yes |
| F13 | L79 | "3 of the 33 cells (… 10%)": 3/33 = 9.1%, so it should be 9%. The other two are right (10/33 = 30%, 6/33 = 18%). | M | Write "9%", or write "nominally 10%". | yes |
| F14 | L81–82 | "Draws that overrun are rescaled" does not say what is rescaled, or to what. "Over 20 recordings" does not say which 20. "120 s apart" is used later as the "planted spacing" (L193, L230) but is never named. | M | "…the excesses of a draw that overruns are scaled down to fit" (confirm the mechanism). Name the 20 recordings (for example "seeds 1–10 at both backgrounds"). Add "(the planted spacing)" after 120 s. | no |
| F15 | L86–88 | "Exactly like … with the same cell count and jitter" says the same thing twice. "The score" and F1 are used before Scoring defines them. | L | Rewrite as: "They are built like the 18% events, so no detector can tell them apart, and they cap F1: a detector that reports every planted event and every distractor has precision 15/21 and F1 0.83 (Scoring)." | yes |
| F16 | L90–91 | "Reached by a linear ramp over the first 30 s" does not say whether the rate also ramps down at 1,500 s. | L | Add "and ends abruptly" or "and ramps down over the last 30 s", whichever is true. | no |
| F17 | L123–136, close-events bullet | CoactDetect is used here and defined only at L149. "Crowding" is used a sentence before its definition. The 0.38 cut is unexplained. The payload, "a detector that merges calls over long gaps fuses separate events here", comes last. | M | Open the bullet with the payload. Define crowding before using it. Write "a coded detector (CoactDetect, below)". Say where 0.38 comes from, or cut it. | yes (order); no (0.38) |
| F18 | L128–130 | "They use the benchmark seeds of the recordings they accompany": "they" and "accompany" are vague. | L | Rewrite as: "Each is generated with the seed of one quiet benchmark recording and so shares its background." | yes |
| F19 | L140–141 | "In each, calls separated by no more than the merge gap are joined" is false as stated. Table 4 gives binned SCE "no merging" and gives locust no merge gap. | H | "In all but binned SCE and locust, calls separated…" (confirm locust). | yes (against Table 4) |
| F20 | L145–146, Table 4 L253 | L146 says rate+context's threshold "depends on the number of cells", but Table 4 gives one value, 4.5 events s⁻¹. On recorded data with varying cell counts, the reader cannot tell which threshold ran. | H | Give the rule (for example "scaled by N/33"), or say that 4.5 is the value at 33 cells and how it scales. | no (needs code) |
| F21 | L146–147 | "It was designed independently": the text does not say independently of what. | L | "It was designed without reference to radar work, but has the structure of…", or cut the clause. | yes |
| F22 | L153 | "Exceeds the null mean by the one-sided Gaussian z for α" leaves out the unit, which is null standard deviations. α is used without being introduced. | M | "…when its count exceeds the null mean by z null standard deviations, where z is the one-sided Gaussian quantile for a nominal level α (z ≥ 4.26 at α = 10⁻⁵)". | yes |
| F23 | L180–182, L222, L240–243, Table 3 caption | "Binned mode" and "sliding mode" of CoactDetect and LoCo are never defined. The bullets at L149–157 describe windows but not modes. Later text depends on the difference ("sliding mode at the default values", "the default in binned mode"). | H | In each of the two bullets add: "In binned mode the window steps by its own length; in sliding mode it steps by one frame" (confirm). Define "binned default" and "sliding default" once and use those terms at L212 and L240–243. | no |
| F24 | L356 | "SB222200 first (12) or no treatment (5)": the numbers have no unit. | L | "(12 recordings)", "(5 recordings)". | yes |
| F25 | L380 | "LoCo (23) and CoactDetect (10)": the numbers have no unit. | L | "(23 calls)", "(10 calls)". | yes |
| F26 | L183 | cSPIKE is uncited and unexplained. | M | Add a citation or a short description of what cSPIKE is. | no |
| F27 | L181–182 | "Checked against MATLAB reference output" gives no tolerance, while SPIKE-synch gets one (10⁻⁹). "Checked only on the benchmark" does not say checked for what. | M | State the agreement criterion. Say "…were validated only by their benchmark scores" if that is what is meant. | no |
| F28 | L175–177 | "Empty bins" is ambiguous (no events, or zero coincidence?). "At least the minimum number of events" is circular. "A maximum" (L173) is called "window cap" in Table 4. | M | "bins with no events are skipped". "A call needs at least *minimum events* events (Table 4)". "capped at the window cap". | yes (terms); no (meaning of empty) |
| F29 | L193–194 | "A call wider than the planted spacing can therefore match any event within its extent plus 2.5 s" reads as if one call matches many events. Matching is one-to-one, and the "wider than the planted spacing" qualifier does no work. | M | Rewrite as: "A call therefore matches at most one planted event, anywhere within it or within 2.5 s of either end; a long call spanning several planted events is credited with one." | yes |
| F30 | L197 | "Before rates are formed": "rate" already means an event rate and a call rate (L359). Recall and precision are ratios. | M | "…before recall and precision are computed". | yes |
| F31 | L205–206 | "Published with each implementation, after a 2026-09-16 retune of one parameter per detector on this benchmark": a date is a lookup key, not content, and the text does not say which parameter was retuned. | M | Name the parameter per detector (or put it in Table 4) and drop the date. | no |
| F32 | Table 3 caption (L210–212) | A fourth limit is buried in the caption. "And differ by detector" repeats what the table shows. For learned detectors (L318) the close-events limit's reference, "the default setting", has no meaning. | M | Add the close-events limit as a table row, or move it into the text. Cut "and differ by detector". State the reference used for learned detectors. | yes (structure); no (the learned reference) |
| F33 | L235 | "Only the parameters each detector declares were searched" is code jargon ("declares"). | M | Rewrite as: "Every parameter in Table 4 was searched except minimum cells [and surrogates]." Confirm the list. | no |
| F34 | L240–247 | The losses of 0.041 and 0.042 F1 on the close-events test look like failures against the 0.02 limit. The reader is not told that the limit is measured against the binned default, which they beat. Reasons for not adopting are given for locust only; the SPIKE-synch and rate+context changes are rejected without a reason. | H | Add "…and so passed the close-events limit, which is set against binned mode". Give one reason each for SPIKE-synch and rate+context. | no (the reasons) |
| F35 | L267–268 | "1,149–1,905 parameters": "parameter" already means a detector setting. | M | "trainable weights". | yes |
| F36 | L262–263 | "1 where a cell has an event" does not say whether that means the event's t50rise frame only or its whole width. locust uses widths, so a reader will ask. | M | "1 in the frame of each event's t50rise" (or "throughout its width"). | no |
| F37 | L275–276, L286–287 | "Standardised over time within each input" leaves the reader asking what the input is. The answer comes 11 lines later, in Training. | L | Move L286–287 into the cell-set bullet: "…standardised over time within the crop in training and within the analysis window on recorded data". | yes |
| F38 | L284 | "Fitting pool" is undefined. | M | Say what it is in the optimization and in the nested cross-validation (for example "the tuning folds"). | no |
| F39 | L270–279 | Code names in backticks (`tube`, `chorus_norm`) mean nothing to a manuscript reader. | L | Cut them, or move them to a code-availability statement. | yes |
| F40 | L317–322 | "Merge gap" block: it covers two topics (learned merge-gap selection, and coded close-events failures). It cites "the replication" before L324 introduces it. "32 cases" is not broken down, while "48" is. | M | Split the block. Move the Replication paragraph above it. Write "26 of 32 cases (4 architectures × 4 folds × 2 rules)". | yes |
| F41 | L313 | "Over the measured duration" is vague. | L | "…over the test's total duration". | yes |
| F42 | L327–334, Separability | The payload, "a descriptive bar, not a significance test", comes last, after 100 words of derivation. | M | Open with: "Separability is a descriptive bar, not a significance test: …". Then give the definition and the reason for the caveat. | yes |
| F43 | L339–340 | "Shared by both streams" contradicts L23, which says the section describes the fast stream only. | M | Cut "shared by both streams", or say why it matters here. | yes |
| F44 | L343–346 | "For its fold the chosen configuration was the default" comes before the reader knows which refit, and so which fold, is meant. "The upper of the two middle held-out F1 values" is a long way to say "upper median". | M | Rewrite as: "Of its 20 refits (4 outer folds × 5 training seeds), the one used has the upper-median held-out F1 (0.726); in its fold the chosen configuration was the default." | yes |
| F45 | L357 | "At least 12 min (13.0–20 min)": the range already says ≥ 13 min, so "at least 12" is redundant or unexplained. | L | "13.0–20 min", or explain the 12 min floor. | yes |
| F46 | L376 | "When the window holds no events": "window" here means the 1 s window of step 1, but "window" is the defined term for analysis windows. | H | "…when step 1 finds no events". Call the step-1 span the "search span". | yes |
| F47 | L373–375 | Calling a count divided by a width "amplitude" collides with the fluorescence amplitude (L16). The text has to disclaim the collision. | M | Rename it (for example "recruitment rate") and delete the disclaimer clause. | yes |
| F48 | L381–382 | "Across all calls" does not say which calls: all detectors, and all windows of the recorded data? | L | "Across all calls of the seven detectors on recorded data". | no |
| F49 | L7 | "Within about 1 s" is a hedge inside a definition. | L | Give the number the method actually uses, or write "within ~1 s (the detectors' windows, 1–2 s)". | yes |
| F50 | L180, L189, L348 | Sentences open with lowercase detector names ("rate+context, …", "binned SCE's interval"). | L | Rephrase so that no sentence opens with a lowercase name (for example "The ports of rate+context…"). | yes |

## Passage test

| block | ~words | payload (one sentence) | what the rest buys | verdict |
|---|---|---|---|---|
| Opening definitions, L7–10 | 60 | Defines coordinated event, detector, call, coded and learned detectors | Nothing extra | Keep; fix F1 and F49 |
| Detected events, L14–18 | 85 | Analyses start from exported calcium events at 0.1 s frames | Row fields; the 127 empty rows (evidence) | Keep |
| Streams, L20–23 | 55 | Only the fast stream, whose width is measured at half prominence, is used | The slow-stream definition (context) | Promote the payload (F7) |
| Exclusions, L39–51 | 170 | The pipeline's exclusions were already applied; the analyses add none | Counts a sceptic would ask for | Keep; fix F9 and F10 |
| Background, L70–76 | 110 | Cells fire as independent gamma-modulated Poisson processes at two rates | Every number is a parameter | Keep |
| Planted events, L78–83 | 110 | 15 planted events at three participation levels, about 120 s apart | Realised intervals (evidence) | Keep; fix F13 and F14 |
| Distractors, L85–88 | 70 | Distractors are indistinguishable 18% bursts and cap F1 at 0.83 | The cap arithmetic (evidence) | Trim (F15) |
| Origin of constants, L98–105 | 120 | Every constant lies within its re-measured 95% interval except participation, which gives the same 6 cells | Sources of the constants (evidence) | **Payload is last; promote it to the first sentence** |
| Table 2 caption | 55 | Constants were re-measured; floor pinning barely moves them | The robustness check (evidence) | Keep; fix F11 |
| Close-events bullet, L131–136 | 90 | Tests whether a detector fuses separate events when they are close | Derivation of the 6 s spacing (evidence, but uses undefined terms) | **Payload is last; promote** (F17) |
| rate+context bullet | 75 | A moving-average excess over a threshold | The radar lineage (a citation) | Keep; fix F20 and F21 |
| CoactDetect bullet | 95 | Cell count against an exact circular-shift null, thresholded at z(α) | The α caveat (a sceptic needs it) | Keep; fix F22 and F23 |
| binned SCE bullet | 95 | Counts per 10 s bin against a pooled circular-shift percentile | Two sentences of lineage | Could trim the lineage by about 30 words |
| SPIKE-synch bullet | 120 | SPIKE-synchronization profile scanned with hysteresis | Citations of each component | Keep; fix F28 |
| Port validation, L180–185 | 80 | Which components were checked against MATLAB or PySpike, and how well | Nothing extra | Keep; fix F26 and F27 |
| Scoring, L189–195 | 110 | Match rule: at most 2.5 s, one-to-one, closest pair first | Consequences for long calls (currently misleading) | Rewrite (F29) |
| Table 3 caption | 85 | How the limits were set, plus a hidden fourth limit | Redundancy ("differ by detector") | Move and trim (F32) |
| Coordinate search, L225–231 | 120 | Greedy one-parameter search with a 0.002 F1 margin | Stopping rules (needed to reproduce) | Keep |
| Adoption, L240–247 | 120 | CoactDetect and LoCo moved to their searched settings; the other four run at defaults | Gains (evidence); rejected changes (reasons missing) | **Payload is last; promote; add reasons** (F34) |
| Nested cross-validation, L296–306 | 130 | Four outer folds, and how each family is tuned inside them | Every clause is a procedure | Keep |
| Two selection rules, L308–315 | 90 | A second selection caps false alarms at 1.6× CoactDetect's | Nothing extra | Keep; fix F41 |
| Merge gap, L317–322 | 95 | Learned merge gap reselected (mostly 8 s); coded close-events limit reported, not applied | Failure counts (evidence) | Split into two blocks (F40) |
| Separability, L327–334 | 140 | Separable means corrected paired t > 3.182, a descriptive bar and not a test | Why the correction is only a heuristic (a sceptic needs it) | **Payload is last; promote** (F42) |
| Learned detector used, L342–346 | 85 | The upper-median refit of the cell-set network with gain, threshold 0.972, merge gap 2 s | The alternative threshold (0.95) is evidence | Reorder (F44) |
| Width and amplitude, L364–382 | 200 | One shared rule measures a call's width and cell rate from its densest group of cells | Counts of the long-width edge cases (evidence) | Keep; fix F46 and F47 |

## Summary

- **No banned constructions, and no "data" violations**, checked against the checklist's own list (R2).
- **The prose tool is missing, so the tool part was not run** (R1).
- **The most serious problems (severity H) are:**
  - "event" carries three meanings (F1);
  - the drug abbreviations are defined late or never (F4);
  - the "in each" merge-gap claim contradicts Table 4 (F19);
  - rate+context's threshold is said to depend on cell count but is given as one value (F20);
  - binned and sliding modes are never defined (F23);
  - the close-events losses read as failures of the limit, and two rejected changes have no stated reason (F34);
  - "window" is overloaded in the width rule (F46);
  - the two exports have no single referent (F11).
- **Four blocks bury their payload at the end:** origin of constants, close-events bullet, adoption, and separability. Promoting the payload fixes each of them better than trimming would.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
