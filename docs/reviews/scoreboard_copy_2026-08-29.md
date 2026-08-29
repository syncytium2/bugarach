# Murderboard run — the scoreboard panel copy

**The most portfolio-relevant screen in this project was invisible to every visitor,
and the gate holding it there had outlived its reason by nine days.** The panel scores
all six detectors on one simulated data set and one fold split — the comparison the
whole benchmark exists to make — and it sat behind `window.__lab`, which no visitor has.
This review is what released it.

It found eight defects. Two were the kind that only appear at the moment of publishing:
a sentence and a chip that both asserted the panel *was not published*, which publishing
would have turned into the page's own first lie about itself. One was worse than a copy
defect and is the reason this record is worth reading beyond the panel it is about — **the
test guarding the gate could not fail.**

---

## The finding that generalises: a gate nobody was measuring

The panel's own module docstring called its gate test *"the load-bearing one here — a
draft that ships is not a draft."* It asserted two things:

```python
assert re.search(r'<details[^>]*id="accScore"[^>]*\shidden', html)
assert pg.locator("#accScore").is_hidden()
```

Neither measured the gate.

`details.acc` is `display:none` until the rail adds `.on`, and **the rail shows one
accordion at a time**. So every panel on this page is `is_hidden()` on load — gated or
not. The assertion was true of the entire sidebar and said nothing whatever about the
scoreboard. Meanwhile the *actual* gate was `gated: true` on the panel's entry in the
rail registry — named in the file's own `accLab` comment as one of the two publish edits
— and **no test read it**.

The proof is that when the un-gating edit was made, the suite stayed green: 50 passed,
including the test that existed to stop exactly that change. It was caught only because
the panel still did not appear, which sent someone looking for why.

Both halves are replaced by assertions on the registry, and `accLab` is read the same
way — it must still be gated, because training needs a local server and publishing it
would hand a visitor a button that cannot work. That second assertion is what makes a
green run evidence: the two entries are read identically and must disagree.

**Mutation-checked.** Restoring `gated: true` on `accScore` fails both new tests and
nothing else. The old test passed under the same mutation.

## What else was found

| # | severity | finding | disposition |
|---|---|---|---|
| 1 | **blocking** | `SCORE_COPY.draft` read *"…which is why it does not appear on the published page."* Publishing it makes the page's own first line false. | **Removed, not reworded.** A reviewed panel says so by carrying no draft warning. |
| 2 | **blocking** | The `<summary>` chip read `draft` — same self-falsification, in the one place a reader sees before opening anything. | Now `6 detectors`, matching every other accordion's count chip. |
| 3 | **blocking** | The gate test could not fail (above). | Replaced; mutation-checked. |
| 4 | major | No attribution anywhere in the panel. The table renders `locust` and `SPIKE-synch` as bare labels — two other laboratories' methods, presented in a column headed *detector* beside this project's own. The attribution text lives in a different accordion. | New `provenance` caveat naming the Cossart lab and the Kreuz lab and pointing at the fuller note. |
| 5 | major | `tolerance` said *"read the ranking, not the gap"* — asserting the ORDER was safe. The table's own `±` refutes it: on the default folder two rows sat 0.085 apart with a fold spread of 0.105 on one. A caveat that retires one wrong reading by asserting another is worse than none, because it carries the page's authority. | Rewritten to say what the numbers support: decimals mean nothing, and neither does an order inside overlapping spreads. |
| 6 | major | `knobs` was unexplained in the rendered panel. Its meaning existed only in a source comment, so nothing on screen stopped a reader taking fewer-is-better. The 2026-08-20 todo predicted this exact reading. | New `knobs` caveat: *"it is not a score: more is not worse and fewer is not better."* |
| 7 | major | `simulatedOnly` — the single most important sentence on the panel — rendered **last**, behind a four-line paragraph about a trainer that is not running. | Moved above the table, on the same reasoning as `demoNote` above the raster: by the time a reader has scrolled past numbers to a footnote they have already believed them. |
| 8 | minor | `#scoreWhat` was empty until the run. A reader who opened the accordion and did not press the button was told neither what it does nor what it needs. | Filled at wire time by `wireScoreboard`. |

## What the review did NOT change, and why

**The empty rows stay.** On the page's default folder, `locust` scores 0 of 3 and
`SPIKE-synch` refuses outright. That looks like a defect and is the panel working: both
carry a stated reason on screen — locust's sweep ran off the end of its grid,
SPIKE-synch is off in this build pending a profile parity test. Filling them by choosing
friendlier defaults would be tuning the demo to flatter the detectors, which is the move
FOUNDATIONS §9 forbids in a neighbouring context and the same instinct here.

Worth recording that the first render made this look far worse than it is. Driving the
panel with the *test fixture's* smaller settings left four of six rows blank; at the
page's actual defaults, **four of six score every fold** (LoCo 0.893, CoactDetect 0.806,
RateDetect 0.637, SCE 0.548) and the two blanks are the explained ones. The reviewer's
own harness, not the artifact, produced the alarming version — which is why role 10
requires the render a visitor gets rather than any render.

## Convergence

| round | blocking | major | minor | note |
|---|---|---|---|---|
| 1 (sighted) | 3 | 4 | 1 | against the render as a visitor gets it |
| 2 (blind, corrected file) | 0 | 0 | 1 | `simulatedOnly` shares the `sub` style with the fold-count line — two different kinds of statement at one weight |

**Stopping reason: severity floor reached** — no blocking and no major findings in the
blind round. Not the round cap.

**This review found and fixed 8 defects. It is not a correctness proof.** The table above
measures how quickly reviewers stopped finding things, not whether anything remains.

## Residual ⚠ — for Tony

1. **Role 2 was not run as a separate agent.** The process carves attribution out of its
   own size rule: *"any deliverable that attributes a method … runs role 2 as a SEPARATE
   agent — whatever its length"*, because a single pass inherits the drafter's search
   history. This ran single-pass. Finding 4 came out of it, so the role was not idle —
   but the blindness the rule is buying was not supplied.
2. **`simulatedOnly` and the fold-count line share a style.** Minor, surviving the final
   round, recorded rather than fixed — fixing it starts a round already decided against.
3. **The match tolerance is under revision.** The panel says 1.5 s, which is `main`. The
   unmerged `bench-background-is-not-flat` moves it to 2.5 s. When that lands the panel's
   default should move with it.

---

## Appendix — header and role ledger

- upstream:  syncytium2/murderboard @ f62acb3
- copy:      vendored @ f62acb3
- freshness: current (`--refresh`, exit 0)
- artifact:  `docs/site/raster_viewer.html` — the scoreboard panel, rendered via
  Playwright as a visitor gets it (`22c34439` → see git for the final hash)
- roles:     11 of 11 run
- rounds:    1 sighted + 1 blind; stopped at the severity floor

| role | findings | what was checked |
|---|---|---|
| 1 Claim & data verifier — "Prove It." | 1 (F1) | Recomputed every rendered quantity against `SCOREBOARD` JSON: fold counts, F1 ± sd, precision, recall, per-row `n of N`. All matched. The one mismatch was not numeric — the `draft` sentence's claim about the page is false the moment it publishes. `knobs` values were not independently recomputed → see residual. |
| 2 Citation & reference validator — "DOI or Die." | 1 (F4) | Every name the table renders: `locust`, `SPIKE-synch`, `CoactDetect`, `RateDetect`, `SCE`, `LoCo`. Two are other labs' methods and neither was attributed anywhere in the panel. Checked against GLOSSARY that `locust` is used and `CICADA` is not claimed. **Not run as a separate agent — residual 1.** |
| 3 Consistency auditor — "Cross-Examiner." | 0 | Panel text vs `GLOSSARY.md` (locust not CICADA ✓), the sub-line's counts vs the rendered rows ✓, the partial-fold sentence's row names vs the table ✓, the refusal cell vs its long-form paragraph ✓. |
| 4 Adversarial reviewer — "Reviewer 2." | 1 (F5) | Attacked the two strongest claims. "Read the ranking" does not survive the spreads the table itself prints. The empty rows survived the attack — they are explained on screen. |
| 5 Line editor — "Kill Your Darlings." | 0 blocking | `learnedAbsent` is long and buries its point, but every clause is load-bearing; left. |
| 6 Methods / domain expert — "RTFM." | 0 | Held-out procedure on screen matches `fair_bakeoff.run()`. SPIKE-synch's refusal text is accurate about the fixed-window divergence. Tolerance is `main`'s → residual 3. |
| 7 Reuse auditor — "Reinventing the Wheel." | 0 | `tunePool` wraps `poolScores` rather than forking it, and says so; the panel reuses `tunePlan` and the shared split, which CI pins against the Python. No re-derivation. |
| 8 Naive-reader accessibility — "You Lost Me." | 1 (F6) | Walked every column header cold. `knobs` was the one a stranger cannot guess and the one the todo predicted would read as fewer-is-better. |
| 9 Density & figure-first — "Show, Don't Tell." | 1 (F7) | Whole-panel unit: five caveat paragraphs against one table, with the most important sentence last. |
| 10 Build & craft gate — "Ship It." | 1 (F8) | **Table below.** Rendered in chromium at 1280×900, published condition (`window.__lab === undefined`) — twice: pre-run and post-run. |
| 11 Argument order — "Start With the Problem." | 1 (F8, shared) | Whole-sequence unit: the panel opened with a red draft banner and said nothing at all before the button was pressed. |

### Role 10 — Build & craft gate — "Ship It." — on the corrected render

| check | result |
|---|---|
| render obtained as a visitor gets it | ✓ chromium, `file://`, no lab shim |
| `window.__lab` undefined | ✓ |
| page errors | none, both renders |
| all 8 column headers present | ✓ detector, F1 (held out), folds, precision, recall, knobs, fit, detect |
| draft banner absent | ✓ |
| chip text | `6 detectors` |
| `simulatedOnly` position | above the table ✓ |
| caveat order | heldOut, tolerance, knobs, learnedAbsent, provenance ✓ |
| partial-fold sentence fires | ✓ (locust, 0 of 3) |
| refusal row renders with reason | ✓ (SPIKE-synch) |
| pre-run note non-empty | ✓ |
| panel reachable with no server | ✓ rail offers the step; navigating shows a working control |
| `accLab` still gated | ✓ |
