# Murderboard run — loco_coact_as_cfar.html

- upstream:  syncytium2/murderboard @ 5e6b299
- vendored:  5e6b299 (re-vendored mid-run — see *The gate fired* below)
- freshness: current
- artifact:  reviewed as `docs/learned/loco_coact_as_cfar.html` (a518b696), **withdrawn before
  landing** and preserved unmodified at
  [`artifacts/loco_coact_as_cfar_draft_2026-08-25.html`](artifacts/loco_coact_as_cfar_draft_2026-08-25.html)
  so every finding below can still be checked against the thing that produced it. It is **not**
  in `docs/learned/`, which is a shipping surface, and it should not be moved there uncorrected.
- roles:     11 of 11 run
- rounds:    1 review round; **0 blind verify rounds — the run was stopped and escalated
  instead of patched**, per the process's rule on structural problems
- verdict:   **DO NOT LAND THE PAGE.** Land the findings.

---

## The problem this run found

A page was drafted comparing two of this repo's coordination detectors — LoCo and
CoactDetect — against radar's CFAR variants. Its thesis was that the two share a statistic
and a null and differ only in reference-window geometry, and that this difference decides
what a guard interval can do to each.

**The geometric half of that is true and checks out to the pixel.** Three independent roles
verified every span against the detector source: LoCo's halves are one-sided (the anchor is a
boundary of each, not its center), CoactDetect's window is centered on the bin, the drawn
spans are exact at 5.4 px/s, and the compaction geometry matches `coact.py` line for line.
That finding survives this review intact and is worth keeping.

**Almost everything the page built on top of it does not.** Eleven roles returned findings
that converge on three failures, and the page's own sources contradict it in each:

**1. The thesis sentence is falsified by the code.** "Everything that separates them is the
shape of the reference window" — but at the shipped operating points LoCo bins at 1 s on FAST
and CoactDetect at 2 s, so "the same statistic" is two statistics; LoCo shifts within each
60 s half and pools coactivity over all bins × surrogates, while CoactDetect shifts within one
60 s window and keeps `n_sur` counts for the test bin alone, so "the same null" shares a
technique and not a specification; and LoCo additionally quantizes its threshold to anchors
every 15 s, clamps context to region bounds, and assigns each bin its *nearest* anchor.

**2. The figure's organizing image is not true of one of its two subjects.** Every lane is
drawn on one dashed "cell / bin under test" line. LoCo does not have one: a bin can be judged
by a reference window centered up to 7.5 s away on FAST, 15 s on SLOW. CFAR's defining
property is that the reference slides *with* the cell under test. LoCo's does not, and that is
a larger departure from the analogy than anything the page's table records. The same figure
also draws a 4 px void at LoCo's anchor — a guard that does not exist at the shipped
`guard_sec = 0.0`, on the one lane whose point is that there is no guard there.

**3. Two of the three conclusion cards are unsound at the root.**

- *"CoactDetect is the only one with the CFAR promise"* rests on its α being a stated design
  point while LoCo's 99.9th percentile is a tuned constant. `bench.py` declares α a swept knob
  — `grid=(1e-2 … 1e-7)` — adopted because 1e-4 scores F1 1.00 where the signature default
  scores 0.72. It is a grid-selected constant, the same epistemic status as 99.9, and
  `detector_history.md` §5.3 is *titled* "Nobody here has stated a design false-alarm
  probability." Worse, the code does not honor α at all on some bins: when the surrogate
  standard deviation is zero, `coact.py` sets `pval = 0.0` and the bin fires regardless of α.
- *"Neither guard is doing guard-cell work"* offers one mechanism — a fixed high percentile of
  a shrunken null pool — for both detectors. **CoactDetect has no percentile**; its bar is a
  Gaussian tail on `n_surrogates` counts, and `n_surrogates` does not change under a guard. The
  card leads with the detector its stated mechanism cannot explain.

---

## What would validate this, and what it would take

The salvageable artifact is much smaller than the one drafted: **the geometry figure and the
one claim it actually supports** — that LoCo's one-sided halves and CoactDetect's centered
window make a guard cheap for one and structurally awkward for the other. That claim is
verified. Everything reaching past it into false-alarm promises, shared statistics, or what
the guard measurement means needs evidence this repo does not yet have.

Three things would have to be true before a corrected page ships:

1. **The citations exist.** The page currently carries **zero** — no author, no year, no DOI —
   while asserting four CFAR terms of art. That regresses against a ruling made the day before
   in `docs/todo/2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md`: *"Cite the
   origins, say plainly that we arrived independently, and stop there."*
2. **The "no analogue" claim survives a wider search.** The page says the circular-shift null
   has no CFAR analogue. Nonparametric / distribution-free CFAR is a named branch doing exactly
   that, and neither the lit shelf nor `detector_history.md` has ever searched it. Grün's
   Unitary Events — which this repo's own attribution todo names as these detectors' method —
   belongs in that row and is absent.
3. **The guard conclusion is re-derived.** See the escalation below; it may be inverted.

---

## Escalations — three findings that outrank the page

These are why the run was stopped rather than patched. Each is about the repo, not the draft.

### E1 · `detector_history.md` §4 credits the wrong paper for greatest-of

Line 281 attributes GO-CFAR to **Hansen & Sawyers 1980** and marks it *read in full*.
Greatest-of selection is introduced in **Hansen 1973** (*IEE Conf. Publ. 105, Radar — Present
and Future*, 325–332); the 1980 paper is the detectability-**loss analysis**. The repo already
half-knows this — `GLOSSARY.md` and `detector_history.md:28` both say "Hansen 1973" — so the
attribution table disagrees with the glossary two files away. **This is structurally the same
error §4 already caught once** (Gandhi & Kassam credited for censoring, corrected to Weiss and
Rickard & Dillard *per Rohling*). Hansen 1973 is not on the shelf; the origin claim reaches
this repo second-hand only.

### E2 · `forks.md` §4a's guard conclusion may be inverted

§4a concludes the guard is "not the guard-cell mechanism" because its recall gain is **flat
across the neighbour gap**. Guard cells relieve **two** maskings, and §5.1 names both:
*self*-masking (the event's own energy in its own reference) and *mutual* masking (a
neighbour's). **Self-masking relief is gap-independent by construction** — every event
self-masks, crowded or isolated — so a flat gain is the signature of guard-cell work with no
mutual-masking component, not of no guard-cell work. The same objection undercuts §4a's second
leg: the sparse bench is described as a place "where nothing can be masked", but §5.1 says in
terms that the test bin's own events sit in the null pool that judges it, so self-masking is
present there too.

Two further observations that bear on it, both from §4a's own table:

- **It is non-monotonic and the middle cell is never discussed.** CoactDetect reads 0.711 at a
  15–30 s gap, **0.882** at 30–60 s, and 0.855 with no neighbour at all — a neighbour at
  30–60 s leaves recall *better* than no neighbour. Under the crowding story that cannot happen.
- **A better structural argument is available and unused.** LoCo's guard excises around the
  **anchor**, not the tested bin (`loco.py`). At a 5 s guard with anchors every 15 s, only about
  a third of bins have their own events removed from the reference at all. That is a
  construction-level reason LoCo's guard cannot do guard-cell work, and it is checkable.

**This is a question for a human, not an edit.** §4a has already been corrected twice and its
current form is the careful one. Either the flat-gain reading needs the self-masking
distinction added, or this objection is wrong — and settling it is worth more than the page
that raised it.

### E3 · A third document still says the guard does not exist

`docs/GLOSSARY.md` ("guard cells / guard interval": *"bugarach has none; that absence is the
finding"*) joins `detector_history.md` §5.1/§5.2 and `tools/make_cfar_figures.py`'s panel B
docstring. All three describe a tree that has moved on; `forks.md` §3 and §4 are correct and
current. Folded into
[`2026-08-24-the-history-document-describes-a-tree-that-has-moved-on`](../todo/2026-08-24-the-history-document-describes-a-tree-that-has-moved-on.md).

---

## The gate fired, and it was right to

The run could not start: `murderboard_freshness.sh` exited 1 with the vendored process at
`fae0eca` against upstream `5e6b299`. Re-vendored and landed on `main` first (#299). **Two of
the rules that arrived in that bump shaped this run**: role 2 must run as its own agent on any
deliverable that attributes a method — which is how E1 was found — and a clean run must state
in its own record that it proves the roles ran, not that the artifact is correct.

---

## Findings by severity

| round | blocking | major | minor | outcome |
|---|---|---|---|---|
| 1 | **9** | 38 | 31 | escalated — not patched |

**Stopping reason: structural, escalated to the human.** Not a severity floor and not a round
cap. The process's rule is that a flat or rising blocking count means the artifact has a
problem patching will not retire; here the *first* round's blocking findings go to the thesis
sentence, the figure's organizing image, and two of three conclusions. Patching that is not a
fix, it is a new draft — and a new draft has no review behind it.

---

# Appendix — role ledger

All eleven roles ran as parallel subagents against the built HTML and its renders in both
themes.

| # | Role | Findings | Note |
|---|---|---|---|
| 1 | **Claim & data verifier — "Prove It."** | 5 major, 7 minor | 53-row claim ledger. Every geometry, refusal, compaction, `min_rois`, α, percentile and crowding-cost claim verified against code or `forks.md` §4a. Caught `0.061 s` (published value is **0.060**), an unsourced radar Pfa range, "raises the estimate by its full amplitude" (a cell-averaging estimate rises by A/N), and the falsified "everything that separates them". Confirmed no claim was sourced from a commit message. |
| 2 | **Citation & reference validator — "DOI or Die."** | 2 high, 3 medium, 5 residual ⚠ | Run as a separate agent per the new rule. Found E1 (Hansen 1973 vs 1980, and line 281 disagreeing with the glossary), zero citations on the page, and that the "no analogue" claim is unclear against nonparametric/distribution-free CFAR. Named five unsearched literatures as residual ⚠, incl. genomics peak calling (MACS local-λ), the closest live prior-art risk. |
| 3 | **Consistency auditor — "Cross-Examiner."** | 2 blocking, 8 major, 5 minor | Traced `0.061` to its origin: CoactDetect's **fold-1** value against LoCo's **four-fold mean**. Found the page silently closes the contradiction §6.5 says is "measurable, not editorial", narrows §4a's warning from "F1 **or recall**" to F1 only, and attributes the 4× cost gap to a surrogate pool both detectors share. Clean on the glossary ban: no "modality", stream/detector axis vocabulary correct. |
| 4 | **Adversarial reviewer — "Reviewer 2."** | 7 blocking, 12 major, 9 minor | Produced E2. Also: α is grid-shopped (`bench.py`), the `sd == 0` path fires regardless of α, every quoted delta lacks n and CI (the sparse-bench leg is 5 extra detections out of 120), the measurements are synthetic and the page never says so, and "independent methods agree" is one method on two recordings. |
| 5 | **Line editor — "Kill Your Darlings."** | 3 blocking, 11 major, 8 minor | The page is written in **British English**; `docs/writing_conventions.md` mandates American and warns it "bites hardest in figure labels" — 10 instances, several inside the SVG. Also "precision pays" is reversible, the green `win` tag contradicts the card two sections down, and 22 em dashes do four different jobs. |
| 6 | **Methods / domain expert — "RTFM."** | 2 blocking, 9 major, 5 minor | Independently reached the card-3 mechanism failure and added the sharper argument: LoCo's guard excises around the **anchor**, not the tested bin. Found the bake-off folds ran at percentile 99.0/99.0/99.5/99.0 — never the 99.9 the table calls LoCo's bar — and that degenerate spans send the threshold to `inf`, not down. |
| 7 | **Reuse auditor — "Reinventing the Wheel."** | 4 major, 4 minor, 1 note | `tools/make_cfar_figures.py::build_b` already owns this subject; two figures now claim the same geometry in two palettes. The page's colors **contradict** the module's load-bearing vocabulary (`#a03623` = "moment under test" there, "problem" here) — inherited from `cfar_scope.html`, so shipped twice. No check script, breaking the `cfar_scope_check.js` pattern set one commit earlier. |
| 8 | **Naive-reader accessibility — "You Lost Me."** | 7 blocking rows, 12 findings | Per-section verdict table, every row blocking. **"CFAR" is never expanded anywhere on the page.** The figure is a *false friend*: read cold it uses the grammar of a Gantt chart or genome-browser track, where rows coexist and vertical alignment means co-occurrence — here the rows are mutually exclusive alternatives. Also flagged "cell" colliding with the reader's meaning of cell on a page about neural tissue. |
| 9 | **Density & figure-first — "Show, Don't Tell."** | 3 high, 3 medium, 3 low | Measured, not judged: figure is 16.9% of scroll height; the last 60% of the document has no picture. Root finding — **the page draws its setup and writes its evidence**: of fifteen quantities, only the span durations are drawn. Named three replacement figures, the best being the sampling distribution behind the guard claim. |
| 10 | **Build & craft gate — "Ship It."** | 25-row table, 11 defects | **Gate verdict: HOLD.** The anchor line strikes annotation glyphs in three places (an em dash renders as a cross); the guard is drawn at two scales (±9.6 s vs ±5.2 s) on a figure captioned "one time axis"; "guard" has three different glyphs. Light-theme contrast below AA at 10–12 px. Figure unreadable at 380 px. Page-level layout, table containment and theme tokens all pass. |
| 11 | **Argument order — "Start With the Problem."** | 1 critical, 4 major, 4 minor | The companion page that teaches CFAR from scratch (`cfar_scope.html`) is merged, one link away, and never referenced — so lane 1 cannot be evaluated where the reader meets it. The page's only actionable claim sits last, weighted as one of three peer cards, while the stake is in an unbolded tail clause. |

---

## What a clean run does NOT warrant

This review found 78 defects and fixed none of them, because the run was stopped and escalated
rather than patched. **It is not a correctness proof.** The severity table measures how quickly
reviewers stopped finding things, not whether anything remains — and with zero verify rounds it
does not even measure that. Nothing here certifies the geometry finding beyond the three
independent verifications recorded against role 1, 3 and 7.
