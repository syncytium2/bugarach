# Murderboard run — docs/reviews/pensub_export_validation_2026-08-20.md

## The problem this run caught

The draft's headline evidence was a coincidence measure **written for this review**,
while `bugarach.assess` already implements the same null — a per-ROI circular shift
within the window — in tested production code the parity suite holds to 1e-9. Nothing
in the draft said so. Role 7 caught it, and the fix was not a citation: the project's
own tool was run on both folders, and it produced a **stronger** result than the ad-hoc
measure, on a statistic the assembly report already quotes.

That reordering is the whole value of the run. Everything else was arithmetic.

The same pass caught a claim that would have shipped as fact: the report asserted
retention of "65.3% fast and 58.7% slow" **restricted to shared ROIs inside the
declared regions**. The numbers were real and the second half of that sentence was
not — they were computed over all events, with no region restriction. A reader
checking the region-restricted figure would have got 63.6% and had no way to tell
which of us was wrong.

## What would have made it worse, and what generalises

The ad-hoc measure was not wrong. It agreed with the tested one. That is exactly the
condition under which a re-implementation ships — it works, so nothing objects, and
the project acquires a second definition of a quantity it already had. The rule that
caught it is mechanical (*does the project already do this?*) and does not depend on
the new code being defective.

Generalises: **when a review's own instrument duplicates the project's, the finding is
not "cite the original" — it is "run the original and lead with it."** The ad-hoc
measure earned a place as a second, narrower check, which is what it is good for.

## Findings by severity, per round

| round | mode | blocking | major | minor |
|---|---|---|---|---|
| 1 | 11 roles, single-pass | 5 | 5 | 4 |
| 2 | blind | 2 | 2 | 2 |
| 3 | blind | 2 | 2 | 1 |

**Stopping reason: severity floor not reached — round 3 still produced blocking
findings, and they were fixed. A fourth blind round was not run.** This run is
delivered as **converged on the numbers and not formally clean**: rounds 2 and 3 each
found a wrong quantity, and the honest reading is that a fourth round might find a
third. The residual `⚠` list below is what a reader must carry.

## Deviation from the process, stated

**The 11 roles were run single-pass in the main thread, not as parallel subagents.**
The process prescribes subagents for a deliverable this size; this session's harness
instructions forbid spawning them without the user asking. Every role's checklist was
walked in turn and every role's output is below — what was lost is the independence
between roles, which matters most for the blind passes. Rounds 2 and 3 were run blind
in the sense that the artifact was re-read from the top against the checklists rather
than against the finding list, but the reader was not a different reader. Discount
accordingly.

---

# Appendix — coverage

- upstream:  syncytium2/murderboard @ 729fb06
- vendored:  729fb06 (docs/doc_review_process.md, tools/murderboard_*.sh)
- freshness: current (`--refresh`, exit 0)
- artifact:  `docs/reviews/pensub_export_validation_2026-08-20.md`
  (`47eefbc` → `69bf778`); figure `docs/reviews/pensub_coact.svg` (`5df099e`)
- roles:     11 of 11 run
- rounds:    3 blind verify rounds; round cap reached with blocking findings open

## Role ledger

| # | role | findings | what it checked |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 6 | Claim ledger over all 41 quantities. Recomputed, not eyeballed: every `PROVENANCE.md` count against the CSVs; the `cmp` byte-identity of `regions.csv`; the revision stamp of all four export folders; `assess_archive.py --help` for the flag names in the command block. |
| 2 | Citation & reference validator — "DOI or Die." | 0 | No external citations. All six internal paths resolve (`assembly_report.md`, `export_folder_spec.md`, the todo, both tools, the figure). No findings, and that is what was checked. |
| 3 | Consistency auditor — "Cross-Examiner." | 3 | Counting basis pinned to recordings-vs-animals; glossary checked for `stream`/`modality` (banned term absent, usage correct); figure↔text agreement on every quoted median; varying table denominators. |
| 4 | Adversarial reviewer — "Reviewer 2." | 5 | Can the alarm ring — yes, 24 of 83 recordings moved the other way, so the test can fail. Magic constants (±0.5 s, 200 surrogates, z > 2). Sibling independence. The identity overclaim. Group breakdown demanded and supplied. |
| 5 | Line editor — "Kill Your Darlings." | 2 | Sentence-level pass. One residual (a clumsy clause at the ±0.5 s paragraph) accepted rather than fixed. |
| 6 | Methods / domain expert — "RTFM." | 2 | Circular-shift wrap semantics; same RNG seed across arms; the window actually scored (raw baseline region, not `region_windows`' 20-minute backward cap) — now stated in the report as a `⚠`. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 1 blocking | **The finding of the run.** `src/bugarach/assess.py` already implements this null. Fixed by running `bugarach assess` on both folders and leading with its result. |
| 8 | Naive-reader accessibility — "You Lost Me." | 2 | Read cold. `db4`, `t50rise`, `pensub` are producer vocabulary and land; "excess near-coincidence" was undefined on first use and is now defined where it appears. Chart-idiom check: a paired slope plot resembles nothing else in this field, so no false-friend risk. |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 | The primary claim is a figure, not prose. The roster and event differentials are tables, which is right for a differential. The "four things" section is the prose-heaviest block and stays prose — each item is an argument, not a comparison. |
| 10 | Build & craft gate — "Ship It." | 4 | Table against the rendered SVG, twice. Round 2: panels unlettered, y-axis without units, footer overflowing the 780px canvas, flat lines wearing the "fell" colour. All four fixed and re-rendered; the shipped figure is the one checked. |
| 11 | Argument order — "Start With the Problem." | 1 | Spine reduced to one claim per section. The draft opened on its verdict; it now opens on the un-re-derivable claim that motivated the export. Arc used: problem → what arrived → does it work → is it the right data → does it conform → what is odd → what it unblocks. |

## Residual ⚠ — what a reader must carry

1. **The identity claim is consistency, not proof.** Two published quantities reproduce
   at two significant figures. A different subtraction producing all four would be
   surprising; it is not excluded.
2. **The window is the raw baseline region**, not the capped analysis window
   `region_windows` derives. Every coordination number here is comparable
   folder-to-folder and is not the number a re-run of the assembly control will print.
3. **Five ROIs present in pensub and absent from the reference** have no stated
   mechanism. Producer question, open.
4. **Two recordings gain events.** Unmasking is plausible and unconfirmed.
5. **`penumbra`, `pensub` and `crosstalk` are not in `docs/GLOSSARY.md`.** The process
   wants a new term added in the same change; the term is the producer's and naming it
   is their call, so it is flagged rather than invented here.
6. **Rounds 2 and 3 each found a wrong quantity.** No fourth round was run.
