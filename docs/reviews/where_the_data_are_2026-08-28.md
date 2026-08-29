# Murderboard run — docs/where_the_data_are.md + docs/history.md

## The review found a live defect in shipped code, not just in the draft

The draft told a reader in doubt to run `python -m bugarach.dataset`. That command
**does not work**: there is no `python` on this machine's PATH, and a bare `python3`
fails with `No module named 'bugarach'` outside the venv — which is every worktree,
since worktrees have no `.venv` of their own.

The same broken invocation was **already live**, shipped in PR #382 two hours earlier,
in two places a person meets at exactly the wrong moment:

- the session briefing's alarm, printed when the data does not resolve
- the PreToolUse gate's block message, printed when a session goes looking

So the mechanism's own advice, delivered precisely when someone is trying to work out
whether the mechanism is broken, produced an error that reads like the mechanism being
broken. `PYTHONPATH=src python3 -m bugarach.dataset` works in both the primary checkout
and a worktree; all three sites now say that, and the briefing's guard test asserts it.

This is the murderboard finding that justifies the process here. Every documented
command had been run by the author — with a venv active or `PYTHONPATH` already
exported — so the defect was invisible to the person best placed to catch it, and
visible immediately to a role whose job is to run the command as written.

## The second finding: a number that will be wrong tomorrow

The draft quoted the census denominator as fixed — *"12,009 commands, 54 transcripts,
0.25%"*. The transcript record **grows every time anyone works in this repo**:
recomputed during this review it was 12,326 commands over 56 files in two project
directories, having been 11,292 earlier the same evening. The rate had already moved to
0.24%.

A reader re-running the census would get different figures and could reasonably
conclude the trigger had drifted when nothing had changed. The numerator — **30 hits,
all read by hand** — is the durable finding and is stable. Both docs and the gate's own
comments now say so, and the re-run instruction says to compare the count and its
contents, not the percentage.

## The third: three ways the evidence was weaker than it read

Role 4 attacked the two baselines and all three objections survived into the doc:

- The zero-false-positive figure was produced by **the author of the trigger reading
  its own hits**. An independent read is the stronger evidence and has not been done.
- The census scores sessions that ran **before the gate existed**. A gate changes what
  sessions do, so the false-positive rate in its presence is unmeasured.
- The live test's **"0 search-gate blocks" is not evidence the gate works** — it is
  what a broken gate also looks like. The `--selftest` establishes the gate can fire;
  the live run only shows it was not needed. The draft had presented zero blocks as a
  success row in a results table.

## Header

- upstream:  syncytium2/murderboard @ f62acb3
- copy:      vendored @ f62acb3
- freshness: current (`murderboard_freshness.sh --refresh --verbose`, exit 0)
- artifact:  `docs/where_the_data_are.md` (77e4e8a → 10a70ef), `docs/history.md` (9b87ade → 801bd5a)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds to clean

**Deviation from the process, stated rather than hidden:** the roles were run as a
single-pass self-review walking each checklist in turn, **not** as parallel subagents,
because this session operates under a standing instruction not to spawn agents unless
asked. The process permits single-pass only for small deliverables, so this is a
deviation on two multi-section docs. Its one hard exception did **not** apply: role 2
must run as a separate agent for any deliverable that attributes a method or claims
novelty, and these docs do neither. The cost is real and worth recording — a single
pass inherits the drafter's blind spots, which is the exact mechanism role 2's
exception exists to defeat.

## Role ledger

| # | role | findings |
| --- | --- | --- |
| 1 | Claim & data verifier — "Prove It." | **2.** Denominator quoted as fixed but drifts (12,009→12,326 in one evening; rate 0.25%→0.24%) — **fixed**, restated around the stable numerator. "54 transcripts on this machine" spans two project directories, not one — **fixed**. Recomputed ledger: 30 hits ✓, 36 bash calls ✓, 0 hunts ✓, 5 `current()` ✓, 84 recordings ✓, 8,705B fresh clone ✓ (8,721B after the fix), 9,000B budget ✓, 17,568B ✓, "fifteen tests" ✓, 9.6KB todo dump ✓. |
| 2 | Citation & reference validator — "DOI or Die." | **1.** No external literature is cited, so no DOI checks apply. All internal attributions verified against the tree: export contract **revision 6** (2026-08-20) does record the selection rule ✓; SAP004/006/007/009 exist with the described purposes ✓; FOUNDATIONS §5 is Data policy ✓, §9 is the preparation facts ✓. Three Tony quotes checked **verbatim** against `current_export.toml`, `tools/session_briefing.sh` and `docs/sapper_feedback/` — none quoted from memory. Finding: the contract has since moved to **revision 8**, so citing 6 alone could read as stale — **fixed**, both revisions now named. |
| 3 | Consistency auditor — "Cross-Examiner." | **0 findings.** Checked: the two docs agree on every shared number (budget 9,000B, fresh-clone size, "13 bytes over", the 30-hit census); cross-links resolve in both directions; no glossary-reserved term misused — in particular "modality" (banned) does not appear; "export folder" and "store" used consistently with `export_folder_spec.md`. |
| 4 | Adversarial reviewer — "Reviewer 2." | **3.** Zero-FP figure graded by the trigger's own author; census scores pre-gate sessions only; "0 gate blocks" presented as success when it is also the broken-gate signature. All three **fixed** as explicit limits rather than removed. |
| 5 | Line editor — "Kill Your Darlings." | **1.** The original opening ("The one call…") buried the reader's actual question under background — **fixed** by the reorder under role 11. Otherwise tightened wording in the symptom table; no redundancy or undefined jargon left standing that role 8 did not already file. |
| 6 | Methods / domain expert — "RTFM." | **1, blocking.** `python -m bugarach.dataset` fails as written; correct form is `PYTHONPATH=src python3 -m bugarach.dataset`, verified working in both the primary checkout and a venv-less worktree. **Fixed in the doc and in the two live sites that already shipped it.** |
| 7 | Reuse auditor — "Reinventing the Wheel." | **0 findings.** Checked whether an existing doc already covers this: `dataset.current()` is mentioned in `SESSIONS.md`, two todos and a handoff, but only in passing — no existing diagnostic surface is duplicated. The docs point at `export_folder_spec.md` for the contract rather than restating it. |
| 8 | Naive-reader accessibility — "You Lost Me." | **1.** "sapper"/"SAP007", "the darkroom" and "the briefing" were used without definition; `TERSE` and "§9" appeared as bare tokens — **fixed** with a short vocabulary note and by spelling out what a TERSE degrade costs. No figures in either doc, so the false-friend and phantom-structure checks do not apply. |
| 9 | Density & figure-first — "Show, Don't Tell." | **0 findings, with the judgement stated.** Longest text block ~95 words (the census caveats); no section is prose-only where a figure would serve. The payload of the operational doc is the **symptom→cause table**, already tabular, and the mechanism summary is a four-row table rather than a paragraph. Prose is right for `history.md`: it is narrative, and its unit is the episode. No replacement figure is named because none is warranted — this is a lookup document, not an argument from data. |
| 10 | Build & craft gate — "Ship It." | **0 findings.** Nothing renders (Markdown, no figures), so the row-per-panel table degenerates to a file check: all 4 internal links resolve; all 15 referenced repo paths exist; both tables well-formed; every one of the three documented commands **executed verbatim** and exited 0. Fingerprints changed for both files, confirming the fixes are in the shipped copies. |
| 11 | Argument order — "Start With the Problem." | **1.** The doc opened on background ("The one call") with the symptom table third, while its reader arrives mid-doubt holding a symptom. **Fixed** — reordered to verify-commands → symptom table → the answer → baselines → known defects → why it has this shape. Arc named: *symptom → triage → mechanism → evidence → limits*, a deliberate deviation from the default analysis arc because this is a reference, not a case. |

## Residual ⚠

- **⚠ The zero-false-positive read is not independent.** The 30 census hits were
  classified by whoever wrote the trigger. Recorded in the doc; an independent read
  would settle it.
- **⚠ The false-positive rate in the gate's presence is unmeasured.** The census covers
  only sessions that predate it.
- **⚠ The store branch's known false positive is documented, not fixed.** It fired
  twice on 2026-08-28. The fix is scoped in the doc and not attempted here.
- **⚠ Roles were run single-pass, not as parallel subagents** (see Header).

## Calibration

**This review is evidence that the roles ran — not a proof that the documents are
correct.** A clean murderboard warrants that eleven specified checks were applied and
what each found; it does not warrant that the docs are free of defects, that the
measured baselines will hold, or that the mechanism they describe works. Three of the
four residual flags above are limits on the evidence itself.
