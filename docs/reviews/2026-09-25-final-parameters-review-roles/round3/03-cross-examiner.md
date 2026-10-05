GRANT 3 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is only the hand-off channel. I have no editing tool.)

# Role 3, Cross-Examiner: blind round 3 on `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md`

**What I checked.**
- **Sources:** the README; all four figure PNGs, each opened; `adoption.json` (the `rows` and `cross_stream` blocks, including under-floor counts, budgets and open axes); `adoption_table.md`; GLOSSARY; ADR-0008; ADR-0009; the runbook in `docs/handoffs/`; the goal page `docs/goals/coded-detector-optimization.md`.
- **Numbers I recomputed and found correct:**
  - The "14 of 48 off-diagonal cells" count in Decision 2.
  - The versions total: 18 shipped + 14 proposals + 6 chorus fits = 38.
  - The combinations: 128 treatment windows × 3 streams × 8 detectors = 3,072.
  - Fast busy loses 205 of 360 planted events, which is 57%.
  - Every value in Figure 1 and every Figure 2 diagonal cell against Table 1.
  - The under-floor call counts in Decision 1 against `adoption.json`.
  - The Figure 4 counts (25/40, 20/40 and 15/40) and floors.
  - The Decision 3 budget values: 0.181, 0.175, 0.245, 0.257, 7.24, 6.85, 7.23.
  - The precision figures 0.992 and 0.764.
  - The close-events values 0.0207, 0.0198 and 0.044.
  - The citations of ADR-0009 decisions 2, 4 and 5 and ADR-0008 decision 4.
- **Consistent, no finding:**
  - Group order DI, OVX, MALE, ORX.
  - The house rules: no "fire", and "data" is never used in the singular.
  - Category order: detectors run in the same order in every figure and table, and streams run fast, slow, combined.

## Findings

**1. The claim that most of each gain comes from fewer calls on decoys is wrong for two of the four proposals.**
- **Where:** Decision 1, "What the gain is made of: mostly fewer calls on decoys" (README lines 66–69). The goal page repeats it (line 51, "Most of each gain is fewer calls on decoys").
- **What the data show:**
  - *Combined rate+context:* decoy calls barely move, 125/126 → 115/114 (quiet/busy). F1 without decoy calls rises from 0.855 to 0.978, which is larger than the as-scored gain (+0.090). On busy, F1 without decoys goes from 0.710 to 0.956.
  - *Combined SPIKE-synch:* decoy calls go 121/98 → 118/94. F1 without decoys gains +0.029, more than the as-scored +0.017.
  - So for both, the gain comes from fewer non-decoy false alarms on busy, not from rejecting decoys.
- **A second false sentence:** "F1 without decoy calls is near 1 … for the shipped points too" is false for combined rate+context shipped, at 0.855 (Table 1).
- **Severity:** blocking. It misstates why two of the four adoptable proposals gain, and the goal page repeats it.
- **Fix:** state it per proposal. Only fast binned SCE is mostly a decoy effect (0.953 → 0.981 without decoys against +0.038 as scored). Correct the goal page in the same PR.
- **Verified:** yes, from `adoption.json` `cross_stream` rows for rate and sync, combined on combined.

**2. The text says the floor blocks binned SCE in the elevated-rate recording, but Figure 3 shows binned SCE calling freely there.**
- **Where:** Decision 1, "Some budget checks cannot fail here" (lines 91–97).
- **The text says:** for binned SCE and SPIKE-synch, the floor "blocks nearly every call in the stretch by construction", so "a pass there is no evidence for those two".
- **Figure 3 shows:** binned SCE (labelled "SCE") making about 5–6 calls per minute inside the stretch on fast and on combined, shipped and proposal, against limits of about 9–10. The claim holds for SPIKE-synch (0.2 calls per minute) and does not hold for binned SCE.
- **Severity:** major.
- **Fix:** limit the claim to SPIKE-synch. Say that binned SCE's check is live. The report's own methods caveat, that wider bins see more chance co-activity than the floor assumes, is the likely reason.
- **Verified:** yes, against the figure.

**3. Decisions 7–9 are labelled as unable to change today's set, but ruling "ship it" on Decision 7 would make combined CoactDetect adoptable.**
- **Where:** the at-a-glance table, row 7 ("no: search rule"), and the lead-in to "Search rules for next time" ("every proposal they touch is held back for another reason").
- **The conflict:** combined CoactDetect's only open axis is `alpha` (cap), per `adoption.json` and Table 1. Table 2 shows its proposal passing every budget on every seed set. Decision 7 offers "Ship it", which would make it adoptable, so the adoptable set would go from 4 to 5.
- **A context point that does not rescue it:** the report says the 120 s context point "is not flagged" by the bracketing record, so it does not count as another reason.
- **Severity:** major. It is a count Tony would decide on.
- **Fix:** mark Decision 7 "yes: combined CoactDetect". Alternatively, make the unflagged context edge an explicit reason and show it in Table 1.
- **Verified:** yes.

**4. Decisions 8 and 9 disagree about where combined LoCo's context went.**
- **Where:** Decision 8, line 299: "The search did go below on fast and combined LoCo, to 10 s and 5 s." Decision 9, lines 319–321: fast LoCo moved to 5 s, and "Slow and combined LoCo … round histories never moved the context off 120 s."
- **The conflict:** read together, combined LoCo reached 10 s in one place and never left 120 s in the other.
- **Severity:** major. Decision 9's argument that "no proposal changes" rests on this.
- **Fix:** say which search reached which value and in which search mode (rounds or pair). Reconcile the two decisions.
- **Verified:** no. The round histories are not in the files I was given.

**5. "Every LoCo search lowered its `threshold_pctile` to the 1st percentile" contradicts Table 1.**
- **Where:** Decision 8, lines 301 and 306.
- **The conflict:** the proposals sit at the top of the grid. Fast LoCo's proposal is 99.99 and slow LoCo's is 99.995 (unchanged). Decision 8 itself says fast LoCo's upper end, 99.99, "was never extended". A proposal at the unextended upper end of its grid would read as "edge", yet it is recorded as "cap" because of the lower-end extensions.
- **Severity:** major. The reader cannot tell whether the grid or the proposal went to the 1st percentile.
- **Fix:** write "extended the grid down to the 1st percentile; the proposal stayed at the top (99.99 / 99.995)". Also say why a proposal at the unextended upper end is not "edge".
- **Verified:** yes, from `adoption.json`: fast LoCo `open_axes` gives `threshold_pctile: cap`, and the proposal `threshold_pctile` is 99.99.

**6. The goal page counts eight rulings; the report and the goal page's own table list nine.**
- **Where:** the goal page, line 59, "the report's eight rulings". Its own table at line 171 lists nine and links "Decisions 1–9"; the report has Decisions 1–9.
- **Severity:** minor.
- **Fix:** "nine rulings".
- **Verified:** yes.

**7. "The proposals call far fewer of them" is not true of the busy middle level.**
- **Where:** Decision 1, line 72, the under-floor paragraph.
- **The data:** the busy middle level barely moves: 55 → 54, 42 → 41, 39 → 33, 60 → 49.
- **Severity:** minor.
- **Fix:** "far fewer at the lowest level; about the same at the busy middle level".
- **Verified:** yes.

**8. One parameter value is written two ways, and one of them is a banned word.**
- **Where:** the Decision 1 table (line 54) says `tau_mode` adaptive → fixed. Table 1 says `isi_adaptive` → fixed.
- **The rule:** the GLOSSARY retires bare "adaptive", and the code refuses `tau_mode="adaptive"`.
- **Severity:** minor.
- **Fix:** write `isi_adaptive` (ISI-adaptive).
- **Verified:** yes.

**9. "Decoy" is used throughout, but the glossary's term is "distractor".**
- **Where:** the whole README; the Definitions list maps decoy to distractor.
- **The rule:** a new word for an existing glossary concept must either not be used or be added to the glossary in the same change. Neither happened.
- **Similar undefined terms:** "shipped point" is not defined; the glossary calls it an operating point. The phrase "The settings shipped today" (line 12) uses the retired bare "settings".
- **Severity:** minor.
- **Fix:** use "distractor", or add "decoy" as an alias in the glossary entry in this PR. Change "settings shipped today" to "operating points shipped today".
- **Verified:** yes.

**10. The Definitions list files "don't care" under ADR-0008; it comes from ADR-0009.**
- **Where:** the Definitions list, "Event floor (ADR-0008)" entry, which defines "don't care" inside it.
- **The sources:** the glossary and Decision 1 (line 71) both attribute "don't care" to ADR-0009 decision 2.
- **Severity:** minor.
- **Fix:** give "don't care" its own entry citing ADR-0009 decision 2.
- **Verified:** yes.

**11. Figure 3 does not show chorus's budget, and a chorus fit that fails it is never mentioned in the prose.**
- **Where:** Figure 3 and Table 2.
- **The conflict:** Table 2 shows the slow chorus_norm picked fit failing the elevated-rate test inside the stretch against CoactDetect's limits. Figure 3 draws no limit bar for chorus, and its caption says chorus "has no budget of its own". The failure appears only in Table 2 and in no decision's text.
- **Severity:** minor.
- **Fix:** draw CoactDetect's limit on the chorus columns, or note the failure in Decision 3.
- **Verified:** yes, from the figure (slow chorus_norm sits at about 1.4 and 1.1 calls per minute) and Table 2.

**12. Figure 3 uses different names and marker shapes from the other figures.**
- **Where:** Figure 3 against Figures 1 and 2 and the text.
- **The differences:** Figure 3 labels the detector "SCE" where everything else says "binned SCE". It marks the proposal with a triangle, where Figure 1 uses a diamond.
- **Severity:** minor.
- **Fix:** relabel the axis "binned SCE". Either unify the proposal marker or say in the caption that it differs.
- **Verified:** yes.

**13. Some numbers lack units, and the Table 2 caption names a label the table never uses.**
- **Where and what:**
  - Real data (lines 466–469): the "+17", "+20" and "+1" for MALE have no unit; only DI's first value says "ROI".
  - The Decision 5 table header reads "held-out gain [95%]", without "in F1".
  - Table 1 reads "5 frames → 1 frames".
  - The Table 2 caption defines "Not checked", but the table uses only "not run" and "… not recorded".
- **Severity:** minor.
- **Fix:** add "ROIs"; write "held-out gain in F1 [95%]"; write "1 frame"; make the caption's labels match the cells.
- **Verified:** yes.

**14. Two numbers in Decision 3 do not name their seed set.**
- **Where:** Decision 3.
- **The two numbers:**
  - "Shipped slow locust made … 5.00 in the new one". The same stretch reads 7.24, 6.85 and 7.23 in the table above it. The 5.00 is presumably seeds 1–8 on quiet, but the text does not say.
  - "84 decoy calls on quiet and 23 on busy" is also unlabelled. It matches the fresh seeds.
- **Severity:** minor.
- **Fix:** name the seed set for both.
- **Verified:** partly. The 84 and 23 are verified as fresh-seed values; the 5.00 is not.

**15. Table 1 is missing the under-floor counts the runbook asked for in every row.**
- **Where:** Table 1, against the runbook's Phase 4 specification.
- **The gap:** the runbook asks each adoption-table row to give "the under-floor counts". Table 1 has none. Decision 1 covers only the four adoptable proposals, and Table 3 gives only per-stream counts of planted events, not calls.
- **Severity:** minor.
- **Fix:** add a column, or state that it was dropped.
- **Verified:** yes.

**16. Two different locust proposals score identically everywhere. This is a question for the data, not a defect in the text.**
- **Where:** `adoption.json` `cross_stream`.
- **The data:** the fast-tuned and combined-tuned locust proposals score identically, to every recorded digit, on all three benches (0.76647, 0.81943, 0.78188). Table 1 lists different changes for them: fast changes `sce_min_distance_frames` 4 → 128, combined changes `n_synchronous_frames` 5 → 1. Separately, fast CoactDetect shipped and fast binned SCE proposal have the same under-floor call triple (5, 6, 49).
- **Severity:** minor. It needs checking, not rewording.
- **Fix:** confirm that `sce_min_distance_frames` is inert at these settings, or that the rows were not mixed up.
- **Verified:** no.

Findings 1–5 are what would change Tony's decision. Finding 1 also needs the goal page corrected in the same PR.

**Files:**
- `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md`
- `<worktree>/docs/learned/runs/2026-09-25-final-parameters/adoption.json`
- `<worktree>/docs/goals/coded-detector-optimization.md`
- `<worktree>/docs/GLOSSARY.md`
- `<worktree>/docs/adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md`
- `<worktree>/docs/adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md`
- `<worktree>/docs/handoffs/2026-09-25-overnight-final-parameters.md`
