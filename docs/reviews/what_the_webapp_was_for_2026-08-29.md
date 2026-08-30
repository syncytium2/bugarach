# The review killed the document's headline finding, and the document was better for it

Tony asked for an assessment of why the app compares fewer methods than it was
designed to. The first draft's centrepiece was a four-line block of HTML — the
learned-model picker, carrying exactly one hardcoded `<option value="tube">` —-
presented as proof that *"tube is THE ONE"* was written into the markup and nobody
had ever decided it.

**It was false, and it had been false for a day.** `wireLab`
(`docs/site/raster_viewer.html:9991`) clears that select and rebuilds it from
`/api/capabilities`, one row per registered architecture. The hardcoded option is
the static-build fallback. The HTML comment immediately above the quoted line says
so in terms — *"Populated from the server's registry in `wireLab`; the single
hardcoded option that used to sit here was a second place to remember a new
model"* — and the draft's quote stopped one line short of it. `src/bugarach/lab.py`
anticipates the error explicitly: *"A hardcoded `<option>` list in the page would
be that second edit, and it would be the one nobody remembers."* The fix landed
2026-08-28, the day before the draft was written.

Eight of the eleven roles found it independently.

That matters beyond this document, because it is **the same defect class this
session spent the day cleaning up, committed by the session cleaning it up**:
reading a source and not the layer below it. PR #394 had rewritten a public caption
against ADR-0002's decision section without reading the addendum that superseded
it. This draft quoted markup without reading the comment above it or the function
below it. Prose that describes code goes stale in one direction — the code moves —
and the only defence is to read the code at writing time. CLAUDE.md already says
this (*"verify all counts/claims against the tree at writing time"*); the draft is
what ignoring it looks like.

Two more claims died the same way. The recall/precision pair used to argue that the
top two methods diverge behaviourally — 0.775/0.917 and 0.590/0.543 — turned out to
be **tube against its own earlier run**, not tube against CoactDetect, misread from
a review ledger line where an arrow meant "then" and was taken as "versus". And
*"the only literature comparison this project has"* restated a claim
`detector_history.md` §6.3 formally **retracted on 2026-08-29**, the same day: the
1e-9 parity measures this repo against interface2's MATLAB, not against CICADA, and
no literature method has been run on these recordings.

## What survived, and what the review added

The argument survived; its evidence was replaced. Verified across three rounds:
there is no detector registry in `src/`; each detector name is a string literal
appearing **14–19 times across 4–5 modules** (reproduced exactly by three roles
independently); five dispatch sites key on the name and **they disagree** —
`bench.run_detector` feeds `coact` and `sync` through `stream_trains` while
`detect_folder._run_flat` and `ui/app._compute` hand them raw `t50rise`; and the
Panel viewer contains no learned model at all.

The review also **corrected the locust diagnosis**, which the draft had got
backwards. The draft argued the platform could not express locust's input
requirement. It can — `peaks: true` declares it and `cicadaTrains` refuses in
words. What cannot express it is the **generator**: `simulate.py` plants no
per-event durations, so `has_width` is `False` and per-event mode would raise. The
bench can exercise only one of locust's two duration modes. That is a `simulate.py`
gap, not an architecture gap, and no registry fixes it — a materially different
conclusion, and the one now in the document.

And it found a live defect in the tree, outside the artifact. `docs/site/raster_viewer.html`
carried two user-facing strings naming a producer's duration rule — an option label
*"each event's own t50rise→peak"* and a settings line *"per event (t50rise→peak)"* —
inside SAP013's include scope but not matching its pattern. Both are fixed in the
same change. **SAP013 is narrower than the document claimed**, and the record says
so.

## What a clean run does not warrant

This run is evidence that eleven roles ran and that their findings were applied. It
is **not** evidence the document is correct. Three rounds found errors the previous
round missed, and round 3's blocking findings were caused by round 2's own fixes —
an edit to `raster_viewer.html` shifted two cited line numbers by five.

---

# Appendix — run record

- upstream:  syncytium2/murderboard @ f62acb3
- copy:      vendored @ f62acb3
- freshness: current (`murderboard_freshness.sh --refresh --verbose`, exit 0)
- artifact:  `docs/what_the_webapp_was_for.md` (`505385fc` → `07b48369`)
- roles:     11 of 11 run, as parallel subagents
- rounds:    1 full + 2 blind verify
- stopping reason: **severity floor**, blocking 8 → 3 → 2, all applied

## Findings by severity, per round

| round | blocking | major | minor |
|---|---|---|---|
| 1 (full, 11 roles) | 8 | 14 | 30+ |
| 2 (blind) | 3 | 4 | 6 |
| 3 (blind) | 2 | 1 | 2 |

Round 3's two blocking findings were both artifacts of round 2's fixes (shifted
line citations, and the absence of this record), not new defects in the argument.

## Role ledger

| # | role | findings | note |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 14 | Full claim ledger, 53 rows. Recomputed all 28 bake-off quantities from `bakeoff.json`; found the misattributed recall/precision pair and the invented symbol `detect_folder._params_for`. |
| 2 | Citation & reference validator — "DOI or Die." | 10 | Ran as a separate agent per the attribution rule. Found the retracted "only literature comparison" claim and that ADR-0002 was cited for a rule it does not contain. |
| 3 | Consistency auditor — "Cross-Examiner." | 12 | Found the counting bases unreconciled (six / five / four / seven) and that `sync`'s separate suppression was silently absorbed into a count. |
| 4 | Adversarial reviewer — "Reviewer 2." | 14 | Attacked the causal thesis and won: the calibration-cost explanation for the closed set was never engaged; the generator/platform conflation is its finding. |
| 5 | Line editor — "Kill Your Darlings." | 24 | Bold used 27 times in 1,630 words; three flourishes standing in for evidence; two metaphors restating claims already made plainly. |
| 6 | Methods / domain expert — "RTFM." | 12 | Confirmed the registry proposal is RNG-safe as written, and supplied the constraint that makes it stay safe: the record may carry call shape but never the stream set. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 12 | Found the proposal reinvents the browser's `DETECTORS`; found four existing todos the draft restated without citing, including a Tony-ruled one that contradicts its cost model. |
| 8 | Naive-reader accessibility — "You Lost Me." | 17 | `locust` and `cicada` never connected; "the six" used for two different sets; no statement of what the project is. |
| 9 | Density & figure-first — "Show, Don't Tell." | 8 | **FAIL, two blocking.** The doc retyped numbers a built figure already shows, and the retyping dropped two of nine rows in the direction of the argument. `learned/bakeoff.png` now embedded. |
| 10 | Build & craft gate — "Ship It." | 6 | Table of 10 mechanical checks. Caught that `sapper --all` never scanned the file (untracked, `git ls-files`), and replayed all 12 rules by hand. |
| 11 | Argument order — "Start With the Problem." | 11 | Best evidence was at 30%, thesis sentence at 76%, and the document closed by arguing against its own recommendation. Reordered. |

## Residual ⚠

1. **The bake-off numbers predate the difficulty-axis correction** (RESET §5). Quoted
   as they stand, flagged in the document, not regenerated.
2. **The architecture comparison is uncontrolled** — `trace` trained at a tenth of
   tube's learning rate, so "the pooled baseline is worse" is not separable from
   "it was trained differently." Flagged at the claim.
3. **The 1e-9 parity is against interface2's MATLAB, not CICADA.** Flagged where the
   document recommends keeping locust.
4. **SAP013 does not cover `docs/*.md`**, so this document's own duration prose is
   not mechanically checked. Worth a `docs/sapper_feedback/` entry; not filed here.
5. **The interface2 checkout and the upstream CICADA source were not read.** Every
   claim about interface2's internals rests on this repo's account of them.
6. **Role 2 could not confirm the epigraph quote** beyond this conversation; it is
   absent from git history, which is normal for a conversational ruling and is why
   it is dated inline.
