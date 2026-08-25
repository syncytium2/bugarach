---
status: open
filed: 2026-08-24
---

# Both of the history document's mechanism findings have been built, and it still says they have not

`docs/forks.md` §3 and §4 are **correct and current** — they carry the live setting,
the alternative, the measurement and the reason it has not been switched. Nothing
below is a defect in the register.

The two documents that *argue* the finding have not moved with it, and both are
written in the present tense about a tree that has changed underneath them.

**§5.1 of `docs/detector_history.md`** — the lead finding, the reason panel B exists:

> bugarach's three rolling detectors have no exclusion at all (panel B) — not even
> the 1968 baseline

All three take a `guard_sec` now. It landed on `loco` and `coact` together, and on
`rate` in its own pass. All three default to `0.0`, so the sentence is still true of
the **shipped behaviour** and no longer true of the code — and the difference does
argumentative work, because a reader takes "has no exclusion at all" to mean the
capability is missing and the fix unbuilt.

**§5.2 of the same document** says rate+context "has a rolling reference window and
no constant-false-alarm property." It has a `threshold_mode="multiplicative"` now,
measured, with the additive bar still live for parity. Same tense problem, same
cause.

**`tools/make_cfar_figures.py`** carries the guard version of it in its docstring —
*"None of bugarach's three rolling detectors has one"* — and draws panel B from that
premise, so the figure and its caption inherit it.

## The trap in fixing this

**Do not repair these sections from the commit messages.** `a15f5e3` is titled *"and
the prediction held"*; forks §4a is titled *"the prediction did **not** hold"* and
explains why — two earlier versions of that section compared **between** recordings,
and neither could tell masking relief from a bar that moved. With an internal
control it is the bar. §4b then records that the first §4a was measured off the
difficulty axis.

So the register has been corrected twice and the commit title has not. **forks.md is
the authority here**; anything written from `git log` will reintroduce a retracted
claim into a document whose whole value is that its claims are checked.

## What the repair looks like

The findings survive intact. Only the tense changes, and both get stronger for it:

- §5.1 moves from **"has none"** to **"has one, defaults it off, and here is what
  the measurement said"** — which names a result instead of an absence.
- §5.2 moves from **"no constant-false-alarm property"** to **"an additive bar
  live, a multiplicative one measured and waiting on a calibration campaign."**
  That is a sharper story than the original: the defect was real, the fix works,
  and it is blocked on `α` being a placeholder rather than on anyone disagreeing.
- Panel B's premise changes with it — the honest drawing is the shipped geometry
  labelled as a **default**, not as an absence. The figure will need regenerating.
- Worth folding in while there: LoCo **refuses** `guard_sec` under
  `null_context_mode="symmetric"`, on the grounds that the guard geometry only makes
  sense against the two-half rule. That constraint was discovered in implementation
  and is recorded nowhere in the history document.

The quotations in §5.1 are matched against the primaries on the lit shelf. Weinberg
and Rohling are about *why* guard cells exist and are unaffected by any of this — the
edit must leave them alone.

Related: [`2026-08-24-cfar-demo-and-radar-notes`](../reviews/cfar_demo_2026-08-24.md)
is the review that turned this up, and it makes the same correction on its own face.
