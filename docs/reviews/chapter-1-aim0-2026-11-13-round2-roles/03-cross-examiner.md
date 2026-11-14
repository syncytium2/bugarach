GRANT 3 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude_Docs batch/update (plus deferred NotebookEdit, SendMessage, Dropbox and Gmail write tools)

**About the run, not the artifact:** this reviewer was handed tools beyond its grant, including editing tools. Only Read, Grep and Glob were used, and no file was edited. The run record's `roles:` line should say this role ran on a fallback path.

# Murderboard role 3 (Cross-Examiner): Chapter 1, blob 0acfccbb

**What I checked:** all 1,745 lines of the chapter. All 19 figures, opened as images. `ch1_intro_figures.log` and the parts of `ch1_intro_figures.py` it draws on (the DET event table, the docstring, the figure headers). `ch1_new_figures.py` (searched only). The `ch1_followups/README.md` and `separation/assessor_split/derivation.md` records, searched for specific numbers. `docs/GLOSSARY.md` (the vocabulary, surrogate and synthetic-validation sections, and the chapter's own terms). `docs/writing_conventions.md` (searched only). Nothing under `docs/reviews/` was opened.

## Findings

Each finding gives: location · issue · severity · suggested fix · could I verify it against a source.

**1. §1.7, first line (line 1233)**
- **Issue:** It says "Situation 3 of Figure 1.2 showed two events **3 s** apart". Everywhere else the gap is **4 s**: the §1.2.4 text, the Table 1.1 header, the Fig 1.2 caption, and the script (events at 81.0 and 85.0 s in `ch1_intro_figures.py`). The 3 s figure is the merge gap, so the two numbers have been swapped.
- **Severity:** High. A cold reader cannot reconcile 3 s with a 3 s merge gap.
- **Fix:** "4 s apart".
- **Verifiable:** yes.

**2. §1.6.1, line 1125, and §1.6.2, lines 1208–1209**
- **Issue:** The failure numbers back to §1.4 are swapped. §1.4 lists the failures as 1 undercount, 2 threshold/chance clusters, 3 flat jitter reading. But §1.6.1 (chance clusters) says "This explains the **third** failure of 1.4", and §1.6.2 (jitter reading) says "This is the **second** failure of 1.4".
- **Severity:** High. These are cross-reference errors on the chapter's main argument.
- **Fix:** §1.6.1 → "second failure"; §1.6.2 → "third failure".
- **Verifiable:** yes.

**3. §1.5.5, line 944–945 ("The denser slow trains miss the same way"), against Fig 1.10 A/B**
- **Issue:** The figure's own footers on the dense-train panels say "slow stream: 3 of 6 below the general form" for both rate and participants. The record agrees (`ch1_followups/README.md` table at lines 250–251):
  - 7-cell rate is measured above general.
  - 13-cell rate is below general at all three windows.
  - Participants split the same way.
- So the denser trains do not miss "the same way" (the pooled-rate panels C/D read 6 of 6).
- **Severity:** High. The claim is used to support "this residual is unexplained" being a systematic effect.
- **Fix:** Drop the sentence, or say that the denser slow trains show no consistent sign (3 of 6).
- **Verifiable:** yes.

**4. §1.5.5, line 930–931, against Fig 1.10 A**
- **Issue:** The text says the tool measures rate **0.99** (fast, 7 cells, 4 s, 25.5 events), which matches the record (0.989; 13 cells 0.998). In Fig 1.10 A the 4 s fast-stream measurements (small and large violet circles) sit at about **1.02–1.03**, above the 1.0 gridline. Participants are also about 0.005 off (figure ≈0.961, record 0.966). The caption says the points are pooled f₂/f₃ estimates. The record says per-recording medians agree within 0.03, which suggests the figure plots a different statistic from the one the caption names.
- The caption's "misses the fast-stream rate by up to 0.17" also has a different basis from the record's "misses … by 0.15".
- **Severity:** Medium.
- **Fix:** Regenerate the figure from the same pooled values the text quotes, or correct the caption's statement of what is plotted. Then reconcile 0.17 vs 0.15.
- **Verifiable:** partly. Text vs record: yes. Figure: positions read off pixels.

**5. §1.5.7 and Table 1.5 (lines 1063, 1067–1068, 1081, 1084): "window" used for the 20-minute segment**
- **Issue:** The text says "Jitter is not readable per window", "At a median window (one fast or two slow events)", "by events per window E", "up to eight events per window" and "at 16 events per window". The glossary's chapter-terms entry says "**baseline segment** … the chapter keeps 'window' for counting windows". The chapter itself defines p = λw as "events per window" (Table 1.2), so "events per window E" in Table 1.5 collides directly with p.
- **Severity:** High (a reserved word reused for another concept).
- **Fix:** "per segment" / "events per segment E" throughout §1.5.7 and Table 1.5.
- **Verifiable:** yes.

**6. §1.8.1, lines 1332–1336: the detection numbers rest on two different runs and do not reconcile**
- **Issue:** The text says "still in 13 % at reuse 0.045 (8 of 60 …)", then "62 % hold a repeat … 14 % of them are detected … against 2 %". Those last three come from the 1000-recording run (`ch1_followups/README.md` lines 909–917). That run's overall both-null rate is **0.094** [0.077, 0.114], and 0.62×0.14 + 0.38×0.02 ≈ 0.094, not 0.13. The headline 13 % is the 60-recording draw. The two numbers count the same quantity on two bases, and the larger run excludes 13 %.
- **Severity:** Medium.
- **Fix:** Lead with 9 % (1000 recordings) and note that the 60-recording point in Fig 1.17 B reads 13 % (8 of 60).
- **Verifiable:** yes.

**7. "Reproducing" block (line 1679) and the revision note (line 1643)**
- **Issue:** The comment says `ch1_intro_figures.py` makes "Figures 1.1–1.3, Table 1.1, 1.2–1.3 numbers". The script makes Figures **1.1, 1.2 and 1.4** and Table 1.1 (its docstring and section headers, lines 10–13, 234, 274, 476). Fig 1.3 is a 20261029 file and the script does not make it. The revision note correctly says "Figures 1.1, 1.2 and 1.4".
- **Severity:** Medium.
- **Fix:** "Figures 1.1, 1.2 and 1.4, Table 1.1, the §1.2–1.3 numbers". Also name the script that makes Fig 1.3.
- **Verifiable:** yes.

**8. §1.2.4 situation 4 (line 218): "four of the five false alarms fall within 13 s of its ends"**
- **Issue:** This number is not in `ch1_intro_figures.log`. The log prints the false-alarm count (5) but no timing. "About this chapter" says every simulation number is printed by a listed script.
- **Severity:** Low–medium.
- **Fix:** Have the script print it, or drop the claim.
- **Verifiable:** yes (it is absent from the log).

**9. The event floor is described two ways, and attached to a detector it was not computed on**
- **Issue:**
  - §1.2.3 (line 136–137) says the repository's floor was "found by simulating chance on flat Poisson backgrounds".
  - §1.6.1 (line 1135–1136) says it was found "under a rigid-shift null (each cell's train shifted as a whole, at random)". The glossary's event floor (ADR-0008) is the rigid-shift form, J = 20 s.
  - §1.6.1 also calls it "the count detector's event floor … in a 2 s sliding window", but §1.2.1, §1.3.4 and Fig 1.3 F define the count detector as fixed 2 s bins.
- **Severity:** Medium.
- **Fix:** State in one place: a rigid-shift null on simulated flat-Poisson recordings, on the sliding 2 s count, then applied to the fixed-bin detector.
- **Verifiable:** yes (against the glossary).

**10. Symbol τ against the glossary**
- **Issue:** The chapter uses τ for correlogram lag (C(τ), φ(τ; s)) and τ_min for a cell's minimum interval between its own onsets. The glossary says excess coincidence is "at a given lag *ℓ* (not τ, which is the dead time above)". So τ is reserved, and the chapter's τ_min is the glossary's dead time / provisional floor *f* under a third name.
- **Severity:** Medium.
- **Fix:** Use ℓ for lag. Either map τ_min onto the glossary's dead-time terms or add it to the glossary.
- **Verifiable:** yes.

**11. Symbol `a` defined twice**
- **Issue:** In §1.2.3, a = 1 − e^(−bw), the chance a cell is active. In §1.5.2, a = w/s. Neither is in Table 1.2.
- p is also both "events per window" and the p-values in §1.5.4–1.5.5.
- **Severity:** Low.
- **Fix:** Rename one `a`; consider a different letter for events per window.
- **Verifiable:** yes.

**12. "Held-out rerun" (the glossary term and the text) vs "held-out record" / "records"**
- **Issue:** The Fig 1.9 panel headers say "held-out record" and "both records". The Fig 1.12 legend says "resolved on both records". The text at line 852 says "16 conditions × 2 records" and at 919 "pooled records". The captions say "runs".
- **Severity:** Low.
- **Fix:** Use "run" / "held-out rerun" in figures and text.
- **Verifiable:** yes.

**13. Figure labels that do not match the text's terms**
- **Issue:**
  - Fig 1.7 B legend "full prediction" (also §1.3.3 line 420, "the full prediction") vs "hard-core form" in the Fig 1.7 caption and §1.5.3.
  - Figs 1.10 C and 1.11 C say "tabulated event counts" where the text says "pooled rates".
  - Figs 1.15 and 1.16 say "gap" / "real fast-stream gaps" where the glossary fixes **intervals** as the term and the text uses "intervals".
  - Fig 1.14 uses c/(c + e) where the text uses ν_c/(ν_c + ν_e).
- **Severity:** Low.
- **Fix:** Relabel the figures to the text's terms.
- **Verifiable:** yes.

**14. §1.6.2, lines 1211–1214: chance shares quoted as single values on an unstated basis**
- **Issue:** "0.01 Hz with K = 3 (chance share about 0.4)": the formula gives 0.20–0.43 over 45/15 events. "a predicted 0.34" at 0.05 Hz, K = 6: the Fig 1.14 D panel prints 0.22–0.46. The basis (pooled? which E?) is not stated, so the reader cannot line these up with the figure's ranges.
- **Severity:** Low–medium.
- **Fix:** State "pooled over 15 and 45 events", or quote the range.
- **Verifiable:** yes (arithmetic and figure).

**15. §1.8.2 frame-rounding power (line 1456) vs Table 1.7**
- **Issue:** The unrounded baseline "0.06 … at E = 2, 0.18 … at E = 3, 0.69 … at E = 5" (7 cells, r = 2.5) differs from Table 1.7's 0.08 / 0.20 / 0.68 for the same cell. The text quotes a separate run (1,000 recordings) without saying so.
- **Severity:** Low.
- **Fix:** Add "(a separate 1,000-recording run; Table 1.7 gives 0.08 / 0.20 / 0.68 at 300)".
- **Verifiable:** yes.

**16. Fig 1.5 A axis note and caption**
- **Issue:** Both say the offsets are "distinct multiple[s] of 2 windows (4 s)". The drawn offsets are −6, −2, +2, +6 s, which are not multiples of 4 s (they are odd multiples of 2, centered). "Span about N·2w" = 16 s, but the drawn span is 12 s.
- **Severity:** Low.
- **Fix:** "spaced by two windows, centered on zero".
- **Verifiable:** yes.

**17. Raster orientation across figures**
- **Issue:** Fig 1.3 puts cell 1 at the top (its caption says so). Figs 1.1, 1.2 and 1.4 put cell 1 at the bottom.
- **Severity:** Low.
- **Fix:** One orientation for all rasters.
- **Verifiable:** yes.

**18. "cluster" in two senses**
- **Issue:** §1.3.1 (line 270) says "Here a cluster is a coordinated event" (Neyman–Scott). From §1.3.4 on, "cluster" is the assessor's cluster, which can be a chance cluster, the sense the glossary's **chance cluster** uses.
- **Severity:** Low.
- **Fix:** In §1.3.1 say "a Neyman–Scott cluster is here a coordinated event", and keep bare "cluster" for the assessor's.
- **Verifiable:** yes.

**19. New terms with no glossary entry, or a second name for an existing one**
- **Issue:**
  - "cross-cell correlogram" (the glossary has "population cross-correlogram" and "cross-ROI onset correlogram").
  - "Aim 0", while the records and glossary call the same experiment "Aim 1a".
  - "excess reading" / "null reading" / "jitter reading".
  - "τ_min".
  - The chapter's K is the glossary's **absolute K**, not the reserved percentage K, and the chapter never says so.
- **Severity:** Low.
- **Fix:** Add these to the glossary's chapter-terms entry in the same change, and say once that K here is absolute.
- **Verifiable:** yes.

**20. Glossary vs the chapter (companion doc)**
- **Issue:**
  - The glossary entry "coordinated onset rate per cell" says it is labeled "coordinated share" in the Chapter 1 figures, but Figs 1.6 and 1.8 now say "coordinated onset rate". The glossary is stale.
  - Glossary participation is 0.20 fast / 0.38 slow; the chapter uses 7 and 13 of 33 (0.21 / 0.39).
- **Severity:** Low.
- **Fix:** Update the glossary.
- **Verifiable:** yes.

**21. Fig 1.16 footer**
- **Issue:** It defines the event floor as "the count chance first exceeds". The definition everywhere else is the smallest count chance reaches at most once per hour, which reads as the reverse.
- **Severity:** Low.
- **Fix:** "the smallest count chance reaches at most once per hour".
- **Verifiable:** yes.

**22. `ch1_new_figures.py` line 1204 (companion source)**
- **Issue:** It refers to "Figure 1.1 D/H", which is now Figure 1.6.
- **Severity:** Low.
- **Fix:** Renumber the comment.
- **Verifiable:** yes.

## Checks that came back clean

I reconciled these against each other, the log, the records or the figures, and found no disagreement:

- **Table 1.1:** all values against the log. This includes 196 of 200 (74 + 122), 119 / 67 (63 + 4), "7 of 200", the 0.021 Hz median, and the chance hits 0.21 / 0.34 / 0.01.
- **Fig 1.2 against the log:** event times 15, 45.95, 81 / 85, 151, 211 s. The drawn draw's outcomes and false-alarm marks: 1 fixed, 5 sliding, 0 CFAR.
- **Fig 1.4 numbers:** 0.48 / 0.87 and 0.10 / 0.47, g₂ 0.49 / 0.89 and 0.11 / 0.49, levels 0.891 / 0.881, HWHM 0.177 / 0.821, 397 / 450 and 119 / 450, 8×10⁻¹⁰.
- **Grid arithmetic:** 48 conditions, 240 recordings, 720 combinations, 160 recordings, 16 conditions × 3 windows = 48, 24 of 32 and p = 0.007, 18 of 32 and p = 0.60.
- **Fig 1.9 header counts** (7, 10, 17, 10 of 48; 12 of 16 twice).
- **Table 1.3 against Fig 1.11 A/B and the record.**
- **Table 1.4 against the Fig 1.11 C counts and the Fig 1.12 box labels** (2 and 16 of 40).
- **Table 1.5 against the record.**
- **Fig 1.12 ranges against the §1.5.6 ranges and the narrowed contribution 3.**
- **Table 1.6 against the §1.4 item 3 values and the "within" claims** (0.015, 0.006, 0.02, 0.03, 0.036).
- **Chance shares** 0.89–0.96 / 0.79–0.92 / 0.02–0.05, and the formula rates against the measured ones.
- **Fig 1.13 labels.**
- **The ≥5 / ≥8 threshold statements** across §1.6.1, Fig 1.13 and Fig 1.16.
- **Fig 1.15 separations** (0.44, 0.59, 0.26–0.76, 2.5–5.8 σ, 0.12–0.22).
- **576 points / 28,800 pairs** (72 × 400; derivation.md).
- **Fig 1.17 rates** (13 %, 1 / 60, 3 / 60).
- **Fig 1.5 C worked example** (net counts +3 / +5 / −3 / −5; F = 0.67).
- **Fig 1.5 B margins.**
- **Table 1.7 against Fig 1.19.**
- **Table 1.8's 0.28.**
- **The constants** 0.376, 0.65 and 1.044.
- **Category order** (fast before slow; 0.01 before 0.05 Hz; windows 1 / 2 / 4 s) is consistent across all figures and tables.
