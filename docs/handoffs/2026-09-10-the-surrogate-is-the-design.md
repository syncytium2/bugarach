# Handoff — the surrogate IS the design, and choosing it is the whole job

> **Not murderboarded** — working material for sessions in this tree, same standing as
> `docs/run_records.md` and the root `HANDOFF.md`. Nothing here is for an outside reader.
> The **substance** of it did go through an eleven-role review; this file is the distillation.

> ⚠ **This is a SECOND live thread.** The root `HANDOFF.md` carries the loop/MAHICE thread and
> [#466](https://github.com/syncytium2/bugarach/pull/466). Nothing here supersedes it. When one
> lands, do not delete the other.

**No tree counts in this file** — those go stale. Derive them: `git rev-parse --short origin/main`
· `pytest -q` · `python3 tools/sapper.py --all`. Measured numbers *are* content and carry their
provenance.

**Nothing is half-done.** Every branch this thread opened is merged or merging: **#519** (the
withdrawn proposal + its run record), **#520** (the ask-list and the first shelf haul), **#521**
(the Brown haul and the IEEE authority record). What is open is a **decision**, not a task.

---

## Read these three, in this order, before doing anything

1. [`docs/reviews/2026-09-10-coordination-without-labels_2026-09-10.md`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md)
   — the run record. It opens with the finding rather than the ledger. **This is the file that matters.**
2. [`docs/proposals/2026-09-10-coordination-without-labels.html`](../proposals/2026-09-10-coordination-without-labels.html)
   — the withdrawn draft. Read its banner, then stop; it is wrong in its mechanism and is kept only
   because the record is *about* it.
3. [`docs/lit_needed.md`](../lit_needed.md) — what the shelf now holds, what is still missing, and
   the two correction blocks about how this session got things wrong.

## What happened

A session proposed a coordinated-event detector that needs **no labels**: discriminate a real
recording from a *dither* surrogate of itself — every event time independently displaced within
±*J* — so that whatever the model learns to key on is coordination. It was drafted for external
review. The murderboard ran all eleven roles and stopped it at round one with **nine blocking
findings on the mechanism**, not the prose.

## The two findings that outlive the proposal

**The surrogate was separable one cell at a time.** Within-cell onset intervals in the senktide
baseline windows have a hard floor — **0.40 s fast, 3.20 s slow** — that real data never violates
and an independent per-onset dither routinely does. At *J* = 1.6 s, **29.5 % of dithered windows
carry a sub-floor interval against 0.0 % of real ones**. That is a *support* difference, so one
hand-picked count with no fitting separates the classes at **AUC 0.647**, using no cross-cell
information whatsoever. The proposal's own likelihood-ratio argument makes this worse: an optimal
discriminator finds the impossible interval *first*, because nothing else has infinite odds.
*(Measured by murderboard role 6 against the export folder; reproduce before building on it.)*

**The negative control could not have caught it, and that is the transferable lesson.** The
proposed control was: dither once, use that as the positive against a further-dithered negative;
flat clears the design. But its positive class **already contains the leak**, which saturates —
0.000 real → **0.932** one dither → **0.953** two. The control comes back flat *because the leak is
total*, and the design pre-committed to reading flat as a pass.

> **A self-supervised objective needs a control whose reference class is provably free of the
> defect — and the obvious control, built by applying the same corrupting operation once more, is
> not that.** Anything here that manufactures its own negatives inherits this trap. The remedy is a
> direct diagnostic with no learned model in the loop: count the support violations at **level**,
> not increment.

## The thesis that survived

Self-supervised discrimination against a surrogate is still the only route in sight to a learned
detector that has not merely learned our simulator. Every learned number in this project is fitted
on a generator that plants one event width, uniform participation and no recurring assemblies. The
senktide/TTX baselines — twenty-two hours nobody can annotate — become trainable only under an
objective that manufactures its own negatives.

**What changes is which surrogate.** Pattern jitter preserves each event's recent history exactly,
so the lone-cell property the design wanted becomes true *by construction* instead of by hope.

## The next step — a surrogate screen, not a surrogate choice

Tony, 2026-09-10: *"why pick one replacement? we have compute to test all of them."* Right, and this
project already has the pattern — the tube 2×2 was built "so they can be measured rather than argued
about." **Compute is not the constraint; the decisive test needs no model at all.**

**Three tiers, cheapest first. A candidate earns the next tier by passing the one before.**

- **Counting statistics.** Per candidate: sub-floor within-cell interval rate, within-cell ISI
  divergence, edge-band onset density deficit, frame-0 / frame-*n*−1 pile-up (⚠ `learn/encode.py`
  **clips** — that is the worse of the two boundary policies and must not be reused unchanged),
  binning collisions, and **surrogate generation time**. Minutes. May eliminate half the field.
- **A per-cell-only discriminator** — a model that structurally cannot see across cells. If it beats
  chance on a candidate, that candidate leaks. This is the leak detector and the falsification test
  in one object, and it is cheaper than the real model.
- **The full model**, survivors only.

**The candidate set — and the first two are controls:**

| candidate | preserves | why it is in |
|---|---|---|
| circular shift | circular ISI multiset | the incumbent; four of the six hand-written detectors use it |
| **uniform per-onset dither** | rate only | **the KNOWN-BAD positive control.** A screen that fails to flag it is broken |
| rigid shift, no wrap | ISIs exactly, no splice | the cheap repair to the splice objection |
| dither with dead-time | rate + a declared floor τ | minimal fix to the killed one |
| joint-ISI dither | the ISI pair distribution | Louis et al. |
| **pattern jitter** | each event's recent history, exactly | Harrison & Geman — the one to beat |
| interval / window jitter | per-window counts | Amarasingham et al., conditional inference |
| operational-time dither | the rate profile under drift | Louis et al., aimed at the drift problem |

**Two axes fixed before the grid runs.** ***J* is per-stream** — at *J* = 2.5 s, 50.4 % of fast
within-cell ISIs sit inside 2*J* against 0.00 % of slow ones, so one value cannot serve both.
**τ, the dead-time floor, is declared, not fitted** — it is a property of the producer's event
extractor and is theirs to state, not ours to infer.

⚠ **Design it as a grid, not eight contests.**
[`todo/2026-08-23-four-variants-of-the-tube.md`](../todo/2026-08-23-four-variants-of-the-tube.md)
says in terms that the tube variants "are not a race," because the guard only paid once the bar was
multiplicative. Surrogate choice may interact with the pooling operator and with *J* the same way.

**What it actually costs is implementation, not compute.** Pattern jitter is a dynamic program;
joint-ISI dithering needs a per-cell 2-D ISI histogram; operational-time dithering needs a per-cell
rate estimate that is itself a parameter choice. Each needs its own support-violation tests, because
a subtly wrong surrogate produces a leak that looks like a finding. **And generation cost sits in
the training inner loop** — fresh negatives every epoch — so it may bind at training time even
though it is free in the screen. Measure it in the counting tier.

**The first figure this thread owes** is the leak itself: the within-cell ISI distribution, real
against each surrogate, with the floor marked. It was found by counting and reported in prose;
CLAUDE.md says render it.

## What the shelf holds now, and what each is for

`<darkroom>/bugarach/lit/` — resolve with `bugarach.paths.darkroom()`, never hardcode. `surrogates/`
did not exist this morning.

| paper | what it is for |
|---|---|
| Harrison & Geman 2009 | **pattern jitter — the algorithm.** Implement from this, not from a summary |
| Amarasingham et al. 2012 | interval/window jitter; *what the resampling conditions on is the null hypothesis*. Already cited in our README for LoCo and CoactDetect |
| Louis et al. 2010 | joint-ISI and operational-time dithering; also states dithering distorts the ISI distribution toward Poisson |
| Stella et al. 2022 | the six-way surrogate comparison. **Read before building the screen — it may already answer part of it** |
| Platkiewicz et al. 2017 | why spike-centred jitter mistakes temporal structure — the variant that was proposed |
| Date, Bienenstock & Geman 1998 | the root of the lineage |
| Hatsopoulos et al. 2003 | *"At what time scale does the nervous system operate?"* — the *J* question by another name |
| Elsayed & Cunningham 2017 | a surrogate preserving a feature set can only test what that set implies |
| Amarasingham et al. 2015 | what a surrogate test can and cannot conclude |
| `ml/` — Gutmann & Hyvärinen, Lopez-Paz & Oquab, Ilse et al., Wang et al., Jain & Wallace | the objective is **noise-contrastive estimation**; the control is a **classifier two-sample test**; localization is **weakly-supervised MIL**; and attention weights are **not** a safe participation readout |

**The lit search is finished. Do not redo it.** One paper outstanding — Gregers Hansen 1973, IEE
Conf. Publ. 105 — and it needs a library. IEEE Xplore does not index it and answers a fetch with
HTTP 418 / a CAPTCHA.

## Corrections owed in the tree, deliberately NOT made here

Each is a real defect found this session and left for a change with its own review.

- **`Gregers Hansen` is the canonical surname**, confirmed by the IEE volume's contents listing and
  IEEE's own authority record. `GLOSSARY.md`, `README.md` and `detector_history.md` write *Hansen* /
  *Hansen VG* — a variant IEEE does list, so not an error, but not canonical. Includes the 1980
  paper: **Gregers Hansen & Sawyers**.
- **Whether `detector_history.md` §4 is right** to head its Hansen & Sawyers 1980 row *origin*. The
  chronology leans toward 1973 introducing greatest-of, but that is titles, not papers. **Do not
  change the column until someone has read the 1973 paper.**
- **`docs/export_folder_spec.md` does not mention field steps**, though the current export ships
  `on_field_step` and `field_step_id` and the loader drops both silently. Harmless on this folder,
  not harmless on the FLAGGED companion.

## Traps — most of them mine, this session

- **Do not write an identifier from memory.** Three fabricated PMCIDs went into a file written
  *immediately after* an eleven-role review, one of them landing on a different paper in the same
  journal and year. Every ID a review role supplied was right; every one generated from memory was
  wrong. `docs/lit_needed.md` carries the eutils recipe. Confirm the download:
  `pdftotext -f 1 -l 1 <pdf> -`.
- **Search the tree; do not argue from a reading of it.** Seven claims the proposal made about
  bugarach were contradicted by bugarach — a dither surrogate already ships (`graph.py`
  `jitter_trains`, tested, in production, **and it wraps**); a declared α already exists; the leak
  control has been run before and came out non-flat; `tiny` trains at a tenth its comparator's
  learning rate so "the per-cell architecture does not train" is not evidence about the cell axis.
  ⚠ **On the nulls, the glossary was right and the reading was wrong** — `GLOSSARY.md` says
  *rolling* for CoactDetect and LoCo in plain terms. `docs/INDEX.md` exists for exactly this.
- **A document written after the murderboard has not been murderboarded.** That is how the
  fabricated identifiers shipped.
- **The local board gate fires at your first commit, which is hours after the work exists.** It
  blocked a commit here for a worktree created ten minutes earlier. Claim when you pick up the task.
- **`merge_when_green.sh` reaps the worktree when the branch lands**, and two concurrent invocations
  race — one wins, the other reports "merge already in progress" and the directory is gone.

## Blocked on Tony

> **Every open item in this file is filed as a todo**, so this handoff can be deleted when the
> thread lands and nothing is lost. Its first version was not — the items existed only here, in a
> file the tree instructs the next session to delete. A sibling session caught that and was right
> to; the fix is below and the items are in `docs/todo/`, where open work belongs.

1. [**Which surrogates enter the screen**](../todo/2026-09-10-which-surrogates-enter-the-screen.md),
   and whether it runs as a grid.
2. [**τ, the dead-time floor**](../todo/2026-09-10-the-dead-time-floor-is-the-producers-number.md) —
   the producer's number, not ours to infer.
3. [**Gregers Hansen 1973**](../todo/2026-09-10-nobody-has-read-hansen-1973.md) — a library job; it
   settles the §4 origin column.
4. [**The quiet→busy transfer penalty**](../todo/2026-09-10-the-design-trains-quiet-and-deploys-busy.md).
   `model_track.md` measures "fit busy, deploy quiet" at −0.24 against +0.12, and training on
   baseline to deploy on treated is the bad direction. Accept it, or bound it before any treatment
   number is read.
5. [**Four recordings with motion-correction frame-floor pinning**](../todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md)
   — in or out of training.

## The rest of the open work, also filed

- [**Build the surrogate screen**](../todo/2026-09-10-build-the-surrogate-screen.md) — the three
  tiers, the fixed axes, the figure it owes, and what to reuse rather than rebuild.
- [**The canonical surname is Gregers Hansen**](../todo/2026-09-10-the-canonical-surname-is-gregers-hansen.md)
  — actionable now, needs no new source.
- [**The export contract does not mention field steps**](../todo/2026-09-10-the-export-contract-does-not-mention-field-steps.md)
  — and the loader drops both columns silently.
- [**`encode()` clips onsets onto the boundary frames**](../todo/2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md)
  — inert on real data, fires on every surrogate that displaces an onset.
