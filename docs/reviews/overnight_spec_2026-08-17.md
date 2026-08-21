# Murderboard run — docs/overnight_spec.md
- upstream:  syncytium2/murderboard @ 783501e
- vendored:  783501e
- freshness: current
- artifact:  docs/overnight_spec.md (draft → committed, plus five other files it corrected)
- roles:     11 of 11 run
- rounds:    1 (the document is a proposal, not a shipped deliverable — see below)

**Single-pass self-review**, same limitation recorded on this session's other run: the
operator's standing instruction is not to use the Agent tool, so coverage is complete and
independence is not. ⚠ For this artifact the cost is lower than usual — the document is
almost entirely *checkable quantities and named procedures*, which role 1 can verify by
computation rather than by judgement, and that is where every defect was found.

**One round, deliberately.** The process's iterate-until-blind-clean rule is for a
deliverable that ships. This one is explicitly marked NOT APPROVED and its next reader is
Tony, who will either authorise it or not; a second blind round on an unapproved proposal
would be polishing a thing that may not survive contact.

## Role ledger

| # | role | outcome |
|---|---|---|
| 1 | Prove It | **4 findings, all fixed.** Every number recomputed from the JSONs; see the ledger below. This role found everything. |
| 2 | DOI or Die | No new citations. The DANDI track deliberately names no dataset, because picking one is a human decision — recorded as a checkpoint, not a gap. |
| 3 | Cross-Examiner | The wrong K claim was **not confined to this document**: it was in `bakeoff.md`, the webapp README, the pipeline figure, a todo, and the published report. All six corrected in one change. |
| 4 | Reviewer 2 | **B2 would not have tested its own hypothesis** — see below. Also demanded the control for B2 (recall can rise for reasons unrelated to the mechanism; the signature is precision, and it must be specific to centre−surround). |
| 5 | Kill Your Darlings | Two sentences cut. The "expected wall clock" table now carries the cost that matters rather than an average. |
| 6 | RTFM | Checked the clamp arithmetic against `nets.py` (`clamp(0.5, k/2)` → 64 samples), the surround widths against the fitted parameters, and the mean-interval arithmetic against the generator spec. The B2 defect is jointly this role's and role 4's. |
| 7 | Reinventing the Wheel | B2 and B3 are told to extend `ablate_tube.py` rather than write new tools; B1 to extend `fair_bakeoff.py`. No new scorer anywhere. |
| 8 | You Lost Me | Audience is a session, not a stranger, but "knee", "arm" and "seed axis" are each used where their meaning is recoverable. The ✅/⚠/❌ table is the entry point precisely so a tired reader gets the constraint before the content. |
| 9 | Show, Don't Tell | Prose and tables are right for a work spec; the two things worth drawing (B2's knee, B3's fitted-vs-planted width) are specified **as figures with named axes** rather than as "plot the results". |
| 10 | Ship It | Not a rendering artifact. The one figure it touches — `pipeline.svg` — was corrected and the report rebuilt; the built page is newer than the SVG it embeds. |
| 11 | Start With the Problem | The document opens on the constraint that shapes it (no human overnight, and a decision sits mid-pipeline) rather than on the list of work. Track A precedes Track B because a model refined on a pipeline nobody can run is a result nobody can reproduce, and that ordering is stated rather than implied. |

## Findings

**F1 · "K=4 halves the event rate" is wrong, and it had spread to six places.**
The scan says 0.0952 clusters/min at K=4 against 0.3500 at K=3 — **0.27, roughly a
quarter, not a half**. Nobody had divided the two numbers; the phrase entered from a
handoff and was copied into `bakeoff.md`, `README_for_the_webapp.md`, the pipeline
figure, the learned-detectors todo, and **the published report, twice**. All corrected,
and `generator_spec.json` is now a build-time store so the report quotes the scan instead
of a remembered ratio. *This is the second fabricated-or-drifted quantity this project's
murderboard has caught in two days; both were inherited rather than invented, which is
the harder case.*

**F2 · B2 would not have tested its own hypothesis.** As drafted it swept `min_sep_sec`
downward to raise the event rate. But the corpus plants 15 events in 3,525 s — a mean
interval of 235 s set by *count over duration* — and `min_sep_sec` is only a floor that
*permits* closer pairs. Lowering it would not have moved the mean interval, so the sweep
would have run, produced a flat line, and been reported as "no knee, hypothesis retired"
for a reason having nothing to do with the model. **Rewritten to sweep `n_per_level`**,
with the arithmetic checked: (5,10,20,40,80) per level gives mean intervals of 235, 118,
59, 29 and 15 s, which brackets the fitted surround width of 9.7–18.1 s.

**F3 · The surround width was overstated.** "100–350 samples, 10–35 s" was arrived at by
pairing the largest ratio with the wrong centre. Recomputed from the fitted parameters:
**97–181 samples, 9.7–18.1 s**. This matters more than a typo because it is the axis B2
sweeps across — the target band was wrong by a factor of two.

**F4 · B1's cost estimate was out by an order of magnitude.** "60 fits, ~10 min" averaged
over three models whose fit costs are 5.6 s, 8.0 s and **236 s**. The per-cell bank alone
is 80 minutes for the same sweep. Split into two rows, with the judgement made explicit:
run it anyway, once, because "it does not train" is currently an n=1 claim about a model
we have already written off.

## Residual ⚠

1. **Nothing here is approved.** The document says so at the top, in a block that names
   what a session may do without asking (read and correct) and what it may not (run).
2. **Independence, again.** One context wrote and reviewed this. The defects were all
   arithmetic, which is the kind self-review *can* catch; a defect of judgement would not
   have been caught, and B2 came uncomfortably close to being one.
3. **Track C names no dataset**, by design. Someone has to pick it, and the choice
   determines what every downstream number means.
4. **B4 may need a generator change rather than a config change**, which would make it a
   morning task with a review rather than overnight work. Flagged in place; not resolved.
