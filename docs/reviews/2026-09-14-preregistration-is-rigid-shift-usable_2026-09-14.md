# Murderboard run — the rigid-shift pre-registration

## The problem this review was for

Tony stopped the surrogate screen on 2026-09-12 because each review read like a reversal. The
pre-registration it reviewed was written to break that loop: fix the rule once, run a small
confirmatory check, read the result once. It was signed before this review ran, so nothing above
its sign-off line may change. Findings here become **dated amendments that Tony accepts or
rejects**, or residual flags.

So the one question that mattered: **if the run went ahead exactly as signed, could its result be
read?**

## What was found

**The direction survived. The rule, as signed, would not have produced a readable answer.** No
role argued against testing rigid shift, against the three-gate shape, or against deciding
before running. Eleven roles, independently, found that the signed rule has holes of four kinds.

1. **Three of its controls cannot fail**, so three gates cannot be shown to work.
   - **The do-nothing destruction control is an identity.** Both sides are scored with the same
     fixed assessor seed, so "retained" is exactly 1.0 by construction. RTFM ran it: 1.0000,
     spread 0.0. It is the same defect the 2026-09-11 review caught for circular shift, which
     this page excluded for exactly that reason.
   - **The count gate's control passes the gate it is meant to fail.** `edge_thinning` at the
     cell's own displacement *J* loses about *J*/120 of each window's onsets. At 1.6 s fast and
     1.4 s slow that is 1.2–1.3 %, inside ±2 %. Prove It, Reviewer 2 and RTFM each computed it
     separately.
   - **The count statistic cannot see rigid shift's loss.** The 60 s windows tile each
     generation window exactly, so the within-mouse average telescopes to about −*J*/(2*T*):
     −0.03 % to −0.29 %. Rigid shift passes by construction. The loss is real but sits in the
     first and last windows, which the average dilutes away.
2. **The rule cannot be executed as written.**
   - **The outcome table has no row for VOID**, no UNDECIDED state, and no mapping from the lab
     folder's displacements (seconds) to Cossart's (frames).
   - **"98.3 %" does not say whether it is one-sided or two-sided**, and the named bootstrap is
     hard-coded to 95 %.
   - **The bootstrap bound is anti-conservative.** It resamples a fixed cross-validated
     correctness vector without refitting: 13–42 % too narrow in RTFM's synthetic runs.
   - **The fold seed is unstated**, and it moves the upper bound by 0.03–0.07 against a 0.55
     margin.
3. **Its one protection is not delivered.** The page says what protects the run is "fresh
   randomness". Every instrument it calls unchanged is deterministically keyed: surrogate keys,
   twin seeds, the assessor seed and the fold seed. A runner reusing the screen's cell ids would
   redraw the exploratory surrogates exactly (Reinventing the Wheel, Prove It).
4. **Some outcomes are foreseeable, and the page does not say so.**
   - **Destruction at a 1.0 s bin likely fails at the small displacements.** By the review
     record's own formula, about 30–34 % of planted co-activity stays in the bin at the leak-free
     displacements. The pass line is 25 %. RTFM's largest-bin simulation is worse still.
   - **Every declared displacement except fast 5.0 s already has exploratory leak and destruction
     results on disk.** The candidate and the smallest *J* were picked by the same criterion now
     being tested (DOI or Die, citing Kriegeskorte 2009 and Nosek 2018).
   - **The slow stream's 1.0 s bin departs from the assessor's MATLAB origin**, which uses 2 s
     for slow (`measure_coordination_timescale.m` line 33). `forks.md` does not record the change.

**One factual error in the page, and in the goal page and a todo too:** "Joint-ISI was never
measured" is false. The leak test returned numbers at 36 joint-ISI cells on the lab folder, all
of them detected. Nothing else survived, so the conclusion stands; the reason given does not.

## Contamination — disclosed, because a pre-registration's value depends on it

The page's gates were frozen before this review. Roles 1, 4 and 6 were told not to read the
exploratory run's outcomes for rigid shift at the declared displacements; roles 4 and 6 read
none. **Role 3 (Cross-Examiner) was not given that instruction — the main thread's omission —
and its report quotes exploratory leak outcomes for rigid shift at declared displacements**:
fast 2.5 s, slow 2.8 s and 5.6 s, and the Cossart larger displacements, all reported as
detected. Role 1 read the rows at the three smallest declared displacements to verify a cited
claim and reports no values from them. Anyone who reads `03-cross-examiner.md` has seen those
outcomes. **Any amendment adopted after this review is post-exposure and must say so.**

## What would validate a fix, and what is Tony's

None of the amendments below changes a signed threshold. Each one makes a gate able to fail,
makes the rule executable, or makes a claim honest. Tony accepts or rejects each; nothing is
applied until he does.

| amendment | closes | raised by |
|---|---|---|
| **Complete the outcome table.** Add VOID rows and an UNDECIDED state (the upper bound is not below 0.55 and the lower bound is not above it). A *J* voided by its controls cannot make a stream FAIL. Tie Cossart's *J* to grid position. List in advance what may change on a rerun after VOID: the broken instrument only | readability of every outcome | Prove It, Cross-Examiner, Reviewer 2, Kill Your Darlings, RTFM, You Lost Me, Show Don't Tell, Ship It |
| **Define the intervals.** One-sided 98.3 % bounds for the leak pass and the positive control, and a two-sided 96.7 % interval for the count gate (equivalence by two one-sided tests; Lakens 2017). Refit the folds inside the mouse bootstrap. Average correctness over the 20 fold seeds rather than choosing one | an executable, honest bound | Prove It, DOI or Die, RTFM, Reinventing the Wheel, You Lost Me |
| **Show the leak gate can pass.** Score two independent rigid-shift draws against each other at the same pair count; if even that cannot get under 0.55, the stream is UNDECIDABLE, not FAIL. Declare the pair counts | a STOP that is an instrument artefact | Reviewer 2, RTFM |
| **Make the count gate able to fail.** Score counts on windows at least *J* from a generation edge, and separately on the edge windows. Run `edge_thinning` at a fixed 5 s (about 4 % loss). Count occupied frames after encoding, which is what `tube` sees | the gate that passes by construction | Prove It, Cross-Examiner, Reviewer 2, RTFM, Reinventing the Wheel |
| **Replace do-nothing with a graded destruction control.** `freeze_half` with a declared expected band. Keep homogeneous resample, labelled as a guard against saturation only. Define retained as the code computes it. Declare the draw and twin-seed counts, a visibility floor, and an interval over draws. Publish the largest-bin saturation expectation for every *J* and K now | a destruction gate with a control that can miss | Prove It, Cross-Examiner, Reviewer 2, RTFM, Kill Your Darlings |
| **Score slow destruction at 2.0 s as well** (the MATLAB origin), and state which bin gates slow | the undocumented fork | Prove It, DOI or Die, Cross-Examiner, RTFM |
| **Salt every key with a run tag**, with a test that no confirmatory key equals an exploratory one | "fresh randomness" | Prove It, Reinventing the Wheel |
| **Disclose what was known.** Exploratory outcomes exist at the declared cells, the anchors were chosen by the gate's own criterion from voided rows, slow 0.7 s leaked, and role 3 exposed outcomes. A VIABLE or NARROWED result reads "held up under a rule fixed after an exploratory look at the same recordings" | an honest claim | Prove It, DOI or Die, Cross-Examiner, Reviewer 2, Start With the Problem |
| **Scope the claims.** VIABLE means "not separable by this per-ROI linear discriminator, per stream". Fast and slow offsets are independent, so a two-stream model can win on alignment: the model tier takes one stream, or uses one offset per ROI. The largest *J* is caveated as "coordination up to *J*". Destruction is a statement about synthetic twins | overreach from a PASS | Reviewer 2, RTFM |
| **Scope STOPPED.** Correct the joint-ISI statement. STOPPED names whether the failure is fixable (an edge or an instrument) or intrinsic, and only intrinsic stops the goal. Restore the aggregate-channel leak test as the precondition for any model that pools across ROIs | overreach from a FAIL | Prove It, Cross-Examiner, Reviewer 2 |
| **Report every gate per group** beside the pooled verdict (FOUNDATIONS §9) | pooled numbers | Prove It, Reviewer 2 |

**Fixable now, without Tony, because none is above the line:** the goal page still calls the page
unsigned and lists settled items as open; "joint-ISI never measured" and "out to 1.4 s" are wrong
in the goal page and two todos; the INDEX does not point at the pre-registration; the only code
that produced the exploratory leak numbers is an untracked scratch script
(`run_discriminator.py`), copied to this session's scratchpad so it is not lost;
`murderboard_prose.sh` is not vendored into this repo.

## What this run does not warrant

This review found and adjudicated the defects below. It is not a correctness proof. The
convergence table measures how quickly reviewers stopped finding things, not whether anything
remains.

---

## Appendix — run header and role ledger

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md (550d3e49d189d128d7522985be787f610cb95b90 -> unchanged; frozen, repairs pending as amendments)
- roles:     11 of 11 run (fallback grants: spawned by name, 7 of 11 declared MISMATCH on Grep and Glob)
- reports:   2026-09-14-preregistration-is-rigid-shift-usable-roles/

The role reports are verbatim except for one edit: machine-local absolute paths were replaced with placeholders (`<darkroom>/`, `<review-session-scratchpad>/`, repo-relative paths), because this repository is public and sapper SAP004 blocks personal paths. No other character was changed.
- rounds:    1 — unconverged; the repair is Tony's amendments, and no blind round has run on them

Mode: standard

**Stopping reason:** round 1 of at most 3, stopped for a decision. The artifact is signed and
frozen, so it cannot be repaired by the main thread; the repair is a set of amendments only Tony
can accept. If he accepts any, the process calls for a blind round on the amended page.

**Findings by severity, round 1** (as each role graded them; roles used different scales, so
this is a count of rows, not a deduplicated total):

| role | blocking | major | minor or lower |
|---|---|---|---|
| 1 · Prove It | 3 | 8 | 8 |
| 2 · DOI or Die | 0 | 3 (+2 major for a write-up) | 8 |
| 3 · Cross-Examiner | 3 | 11 | 11 |
| 4 · Reviewer 2 | 3 | 9 | 4 |
| 5 · Kill Your Darlings | 5 (graded H) | 10 (graded M) | 14 |
| 6 · RTFM | 3 | 8 | 5 |
| 7 · Reinventing the Wheel | 1 | 7 | 6 |
| 8 · You Lost Me | 2 (+ 8 readability-blocking sections) | 9 | 9 |
| 9 · Show, Don't Tell | 0 | 4 | 4 |
| 10 · Ship It | 0 | 2 | 7 |
| 11 · Start With the Problem | 0 | 3 (graded medium) | 4 |

**The run itself.** The archive is named without the underscore the skill prescribes (`<stem>_<date>-roles`), because `murderboard_roster.sh` strips underscores from the `reports:` path before resolving it — an upstream defect in the gate, recorded here rather than worked around silently. Seven roles were spawned by name but reported missing Grep and Glob; each
covered the searches with `grep` through Bash, and none held an editing tool. Their declarations
are carried below verbatim. `murderboard_prose.sh` is not vendored here and role 5 holds no
shell, so the main thread ran the upstream copy (syncytium2/murderboard @ 81a0927) and handed role
5 its output. Ship It notes that `tests/test_index_resolves.py` covers only `docs/INDEX.md`; the
page's six links were checked separately and resolve.

### Role ledger

**1 · Prove It** — GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)
36-row claim ledger. Blocking: the count control passes its gate; the interval cannot be computed as specified; the Cossart displacement is undefined. Found joint-ISI was measured, slow 0.7 s leaked, do-nothing cannot fail, "fresh randomness" is not delivered, and exploratory results exist at declared cells.

**2 · DOI or Die** — GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)
Major: the slow bin departs from the MATLAB origin (2 s); sidedness is undeclared (Lakens 2017); "exploratory then confirmatory on the same data" is not a recognised confirmatory design (Nosek 2018, Kriegeskorte 2009). Traced rigid shift's credit back past Pipa 2008 to Pipa, Riehle & Grün 2007 (closed access, unread). Nobody was asked: residual.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Blocking: an incomplete outcome table; the count control passes its gate; "retained" is defined unlike the code. Major: the slow grid logic is wrong as stated, and the page silently changes the exit criterion. ⚠ Quoted exploratory leak outcomes at declared displacements (see *Contamination*).

**4 · Reviewer 2** — GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)
Blocking: the count gate cannot fail for rigid shift; FAIL can be assembled from void cells; neither destruction control can fail. Major: fast and slow offsets are independent, so there is a leak the gate cannot see; pass probability is undeclared; §9 pooling; STOPPED overreaches. Read no exploratory outcomes.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
No banned construction (tool run by the main thread). Two blocks over 120 words, both carrying execution rules. Five amendment-grade ambiguities: the Cossart *J*, VOID rows, point versus bound, bin width, and what a failed destruction control voids.

**6 · RTFM** — GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash, WebSearch, WebFetch)
Grounded in Elephant 1.2.1 source and Lopez-Paz & Oquab 2017. Blocking: the count statistic telescopes and its control is void; do-nothing is an identity (run: 1.0000); the leak gate has no UNDECIDED state and is likely underpowered at ICC 0.11. Addendum: 50 × 20-seed simulation confirms the negative-control chance rates.

**7 · Reinventing the Wheel** — GRANT 7 MISMATCH — missing Grep, Glob; holds Read, Bash (no editing tools)
Blocking: the existing instruments replay exploratory randomness. The exploratory leak numbers came from an untracked scratch script. Most of the planned build already exists in `probe_discriminator.py`, the screen tool and the recording-identity tool, with three traps: the 95 % bootstrap, default seeds, and the saturation formula.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
Per-section table: 10 of 16 sections blocking for a cold reader. Execution-level: bin width ambiguity, outcome-table gaps, sidedness, no commit pin for "unchanged". Figures needed for rigid shift and the planted-twin test.

**9 · Show, Don't Tell** — GRANT 9 MISMATCH — missing Grep, Glob; holds Read, Bash (no editing tools)
No figures on a 1,637-word page. Drawing the outcome flow exposed the VOID and Cossart gaps. Proposed rule-drawing figures before the run (generators, windows and bins, outcome flow, blank reading template), with a "text wins" clause.

**10 · Ship It** — GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)
Rendered through GitHub's markdown API and Python-Markdown; three tables render with correct column counts, six of six links resolve. Major: the one-stream outcome row renders in the wrong column; there is no VOID row. Sapper and quote check clean.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
The section order is sound. Medium: the 1.0 s timescale arrives after the claims that depend on it; "Why rigid shift" uses terms defined later; the reporting caveat sits far above the outcome table.

### Residual ⚠
- ⚠ Every amendment above is **pending Tony**. Until he rules, the signed page is not runnable as written.
- ⚠ Exploratory outcomes at declared displacements are in the role 3 report.
- ⚠ Pipa, Riehle & Grün 2007 and Pipa & Grün 2003 are unread (closed access): the origin trace for rigid shift stops one step short.
- ⚠ Nobody has asked Grün's group or Pipa about whole-train shifting on continuous recordings, or asked why the MATLAB author chose 2 s for slow.
