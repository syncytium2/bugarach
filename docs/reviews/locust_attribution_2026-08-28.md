# Murderboard run — `site/index.html` (the CICADA attribution passages)

## What was at stake

A public page said, in bold, **"The lane marked `locust` is CICADA's method"** — beside
this project's own benchmark numbers, on a page written for outside readers. Locust is
the detector that fires 85 times (35 after retune) on a decoy block built to catch a
detector keying on activity rather than coordination. A reader who joined those two
sentences would conclude that **CICADA is promiscuous**.

That is #292's failure class inverted. #292 was about crediting the wrong laboratory;
this lends the right one a result it did not earn. And unlike a citation slip, it is not
recoverable by a correction later: the page is the artifact a hiring reviewer or a
collaborator reads.

**Four sources in the tree already disagreed with the page, and only the page asserted
it.** That is what made this a defect rather than a wording preference.

## What was found

**The claim was never validated, and the chain has a gap nobody had written down.**

```
Cossart CICADA  ──── never validated ────▶  interface2 generate_sce_cicada
   (their code,        "faithful" is an           (PARKED in f55643bf for
    MIT, 2019)         assertion in both)          over-detecting)
                                                          │
                                                    1e-9 ─┘
                                                          ▼
                                                   bugarach locust
```

`tools/matlab_ref/gen_ref_cicada.m` builds the parity fixture by running
`generate_sce_cicada` — interface2's own function. So the 1e-9 result validates bugarach
against interface2 and says **nothing** about CICADA. Both repos assert "faithful port"
and neither contains any comparison against the Cossart source; grepped both.

**It is a documented partial port.** `generate_sce_cicada.m`: *"we already have events, so
their per-cell transient-detection step is skipped."* A whole stage is absent. And
interface2's `docs/coordination_detectors_methods.md` §3 carries a **"Provenance
(important)"** block naming two changes *"beyond tuning"* — the skipped stage, and
replacing CICADA's active-duration model because the original *"over-detects
catastrophically on our long SLOW transients."*

**The page contradicted itself inside one paragraph.** Four sentences after claiming
locust *is* CICADA's method, the same `<p>` said *"No method from the literature has yet
been run on this project's recordings."* Both were bold; both cannot hold.

**Role 1 caught a precision gap the fix had missed.** README:634 records that the port is
of *"the older `sce_stats_utils`"*. The draft said only "the Cossart lab's
implementation", which invites a reader to compare against current CICADA. Corrected to
"an older version of".

## What was checked against primary sources, not against this repo's prose

Role 2's work, done against the artifacts themselves:

- **`sce_stats_utils.py` exists** at the cited path in `gitlab.com/cossartlab/cicada`, and
  defines **both** functions interface2 names — `get_sce_threshold(rasterdur, …)` and
  `detect_sce(traces, raster, …)`. So the port was made from **their code, not from the
  paper**, and the file-path claim is accurate. (The first parameter, `rasterdur`,
  independently confirms the duration model the port replaces.)
- **The citation is correct.** Zenodo `10.5281/zenodo.10041434` is CICADA v1.0.3,
  Denis/Dard/Quiroli/Cossart/Picardo, released 20 July 2020, CC-BY-4.0. The year was
  checked because the lit shelf holds `denis_2020_deepcinac.pdf` — a **different tool by
  the same five authors in the same year** — and a conflation there would have been easy.
  There is none.
- **The lit shelf does not hold a CICADA paper.** It holds DeepCINAC. So no publication
  describing the method has been read; the implementation was the source. That is
  defensible for a port and is now a stated residual, not a silent gap.

## What would validate this

The corrected page makes four checkable claims and each has a named source in the tree or
on the web: the skipped stage (`generate_sce_cicada.m` header), the duration-model
replacement (interface2 methods doc §3), the 1e-9 last-link validation
(`gen_ref_cicada.m`), and the citation (Zenodo record). **None rests on this repo's own
prose**, which is the standard the previous version of this paragraph failed.

The render was read back with tags stripped, twice, and the old claims are absent from the
built file — `grep` for both returns 0 on `site/index.html`.

## How it generalises

**An attribution fix that removes a name is not finished until the derivation is stated
somewhere the same reader reaches** — that was `index_2026-08-27`'s lesson, and it was
right. This run is its sequel and the correction to it: that fix, reaching for the
derivation, **overshot into identity**. Saying *"locust is CICADA's method"* discharged the
duty to credit and created a stronger claim than anyone had evidence for.

The general form: **crediting and equating are different acts, and the fix for
under-crediting is not maximal crediting.** The safe construction names the lineage and
the deviations in the same breath.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ 3593c44
- copy:      **vendored** (repo's own `docs/doc_review_process.md` + `tools/murderboard_*.sh`)
- freshness: **current** (`murderboard_freshness.sh --refresh --verbose`: *"current (@ 3593c44, via remote)"*, exit 0)
- artifact:  `site/index.html`, built from `tools/build_site.py` (`488e15c6` -> `11094a11`)
- roles:     **11 of 11 run**
- rounds:    2 blind verify rounds to clean

> ⚠ **Role 2 was NOT run as a separate agent, and the process says it must be.** The
> process file makes role 2 un-collapsible for *"any deliverable that attributes a method
> … whatever its length"*, because a single pass inherits the drafter's search history.
> **This deliverable is exactly that case.** This session is configured not to spawn
> subagents, so the requirement could not be met. What was done instead: every attribution
> claim was checked against a **primary source off this machine** — the GitLab file, the
> Zenodo record — rather than against the repo's own prose, and the lit shelf was checked
> for a describing paper. That is stronger than a normal single pass and **weaker than the
> rule requires.** A re-review with an independent arm is warranted before any wider
> distribution of this page.

> ⚠ **No CICADA publication has been read.** The shelf holds DeepCINAC, not CICADA. Every
> statement the page makes about what CICADA does is sourced from **its code** and from
> interface2's port notes. Fetching Dard et al. (STAR Protocols), which documents the
> CICADA pipeline, would close this.

### Role ledger

| # | role | findings | note |
|---|---|---|---|
| 1 | Claim & data verifier | **1 fixed** | the draft said "the Cossart lab's implementation" where README:634 records the port is of the **older** `sce_stats_utils`; corrected. Re-derived the rest: the file and both functions exist at the cited path, the Zenodo record's authors/date/licence, the parity fixture's actual input (`generate_sce_cicada`, not CICADA), the parked status in `f55643bf` |
| 2 | Citation & reference validator | 0 | **see the ⚠ above — run single-pass against the rule.** Zenodo 10041434 verified: CICADA v1.0.3, five named authors, 20 Jul 2020, CC-BY-4.0. Deliberately checked for a DeepCINAC conflation (same authors, same year, on our shelf) — none present. Cossart/Aronov/Yuste (2003) retained as the SCE root. No new citation added |
| 3 | Consistency auditor | **1 fixed** | the self-contradiction inside one `<p>`: "is CICADA's method" against "no method from the literature has yet been run here". The second is now the true, narrower "…in its own form". Page now agrees with README:614, README:634, `ui/app.py:133` and interface2's methods doc §3 — previously it disagreed with all four |
| 4 | Adversarial reviewer | 0 | attacked the replacement for the opposite failure: does it now *under*-credit? It does not — CICADA is named, linked, cited, and identified as the origin of the method in the first sentence. The added caveats are all sourced and none is a hedge about the Cossart lab's work; they are about **ours** |
| 5 | Line editor | 0 | the long paragraph was split in two: lineage and citation first, deviations second. Each sentence asserts one thing |
| 6 | Methods / domain expert | 0 | verified the two named deviations against `generate_sce_cicada.m` (skipped transient detection) and cicada.py (rise interval vs transient duration). `rasterdur` in the upstream signature independently confirms the duration model being replaced |
| 7 | Reuse auditor | 0 | no new analysis code. The page points at the citations and the landscape page rather than restating them |
| 8 | Naive-reader accessibility | 0 | read cold: "derived from", "skips a stage", "changes how long a cell counts as active", "checked only at its last link" are all plain. No internal identifier appears in the prose. "1e-9" is the one technical token and it is glossed by "matches … to" |
| 9 | Density & figure-first | 0 | +1 paragraph on a page whose surrounding blocks are the same length. **Prose is right here** and the reason is stated: the content is a chain of provenance with three links, which a reader follows in sentences; a diagram would need the same words as labels |
| 10 | Build & craft gate | 0 | **built and read back from the render twice**, tags stripped. `grep` for both retired claims returns **0** on `site/index.html`. Source fingerprint moved `488e15c6` -> `11094a11`. Full suite **1498 passed, 3 skipped, 1 xfailed**; sapper clear |
| 11 | Argument order | 0 | lineage → citation → deviations → what the numbers do and do not mean. The reader learns whose method it derives from **before** being told how it differs, which is the order that credits rather than hedges |

### Residual ⚠

1. **Role 2 not independent** (above). The one rule the process says may not be collapsed.
2. **No CICADA publication read** (above).
3. **The site is not redeployed.** This changes the built page in the repo only; a deploy
   is Tony's to ask for.
4. **interface2 parked `generate_sce_cicada`; bugarach ships it calibrated.** Probably
   deliberate — bugarach carries the rise-interval mitigation, so it ships the fixed
   version — but the upstream "parked" status is written down nowhere in bugarach, and a
   reader of either repo alone would not know. Not this page's job to resolve.
