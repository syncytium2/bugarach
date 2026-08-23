---
status: done
filed: 2026-08-20
closed: 2026-08-23
---

# Where the webapp work stands, and what to do next

**Closed 2026-08-23. Every "what to do next" on this page is done and every open pull
request on it has merged** — chromium is on the CI runner, CICADA is the sixth browser
detector, and the stack was rebased and landed. A status page is only useful while its
status is current, and a stale one is worse than none: this one still said the sixth
detector was missing on a day the page ran all six.

**What was carried out of it before it closed**, because a status page is the wrong
place for anything that outlives the status:

- *Test the screen, not the function*, and the Playwright trap that came with it, are
  now a section in
  [`docs/testing_a_sampling_port.md`](../testing_a_sampling_port.md).
- *Deterministic arithmetic reached only through a sampled path is untested* was
  **already** a named section in that same file — it is the one that cost the most,
  and it is written up there at more length than here.
- *LoCo's null and the region-blind question* became
  [`2026-08-23-locos-null-is-blind-to-the-region-it-was-cut-from.md`](2026-08-23-locos-null-is-blind-to-the-region-it-was-cut-from.md),
  where it also gets what it never had: a test that could fail.
- *Should `assess_archive.py` keep its store fallback?* and *should `bench.REGIMES` be
  re-derived from the folder?* are both open under "Still open" in
  [`2026-08-20-six-tools-still-read-stores.md`](2026-08-20-six-tools-still-read-stores.md),
  which is the page that measured the shift and is where a reader would look.
- *`high K+` and the solution delay* is the label-substring hazard in
  [`2026-08-18-windowing-default-and-the-three-delta-interface.md`](2026-08-18-windowing-default-and-the-three-delta-interface.md).
  Contract revision 7 has since removed the wash-in delay from the folder path
  entirely, so what survives is the question about the viewer's window panel rather
  than about detection.
- The closing note about two sessions duplicating each other's work became a rule:
  claim on the machine-local board when you **pick up** the task, with a `Touches:`
  line, and a commit gate enforces it.

*Everything below is the session record as filed, kept as history.*

One session, 2026-08-18 to 2026-08-20. Everything below is pushed; nothing is
uncommitted and nothing is half-done. **No `HANDOFF.md` from this session** — that
file means work in flight, and there is none.

## What landed

**All five browser detectors.** RateDetect and SPIKE-synch are pure functions of
the data and are checked against the Python at 1e-9. LoCo, CoactDetect and SCE
sample, and the method for testing those is written down in
[`docs/testing_a_sampling_port.md`](../testing_a_sampling_port.md) — it is the most
reusable thing here and cicada and the learned detectors will need it.

Best F1 per detector on the page's own simulated folder: CoactDetect 0.90, LoCo
0.89, RateDetect 0.80, SCE 0.64, SPIKE-synch reporting that its knob is not what
limits it there.

**The tuning step**, which closes the loop: the generator keeps what it plants, the
sweep scores every setting against it, and `bench.pick_operating_point`'s refusal of
a boundary answer came over with the rule.

**Spec revisions 5 and 6.** An event is located at its `t50rise`; the contract asks
for width, producer-defined, travelling with `width_def`; and the folder is the
folder, with nothing reading around it.

## Open pull requests

| | | |
|---|---|---|
| #148 | CI installs chromium | **merge first** — 530→580 passed, 51→3 skipped |
| #133 | the analysis-window panel | independent |
| #146 | the heredoc verdict | one file, no code |
| #149 | worktree sweep + `tools/worktree_sweep.sh` | one file, no code |
| #156 | SAP007 + the source-data folder | |
| #167 | three tools converted (stacked on #156) | |

## Decisions waiting on a person

**Re-derive `bench.REGIMES` from the folder?** On the approved folder the per-ROI
rate quartiles are 5.2 and 19.0 mHz against the 3.8 and 17.5 currently in the file;
the difficulty span narrows from 4.61× to 3.65×. Every bench number in the repo was
computed against the old range. `bench.py` also argues that p25 "lands within 5% of
the TTX median" — an argument the shift breaks. The fitted shapes barely move
(0.275→0.277, 1.388→1.429).

**`high K+` and the solution delay.** The window panel applies one delay to every
period, which leaves 21 of 60 `high K+` windows under four minutes because those
periods run from 14.7 min down to 6 seconds. There is a per-period toggle; whether
a terminal challenge should take a wash-in delay at all is a protocol question.

**LoCo's null and the region-blind question.** The browser runs one analysis segment
per call, which makes LoCo's raw-region clamp a no-op — so its null comes from the
analysis window rather than the period it was cut from. The port is faithful to the
Python; the calling pattern differs. Only bites where an analysis window is narrower
than its region.

**Should `assess_archive.py` keep its store fallback**, and should `cli.py` /
`ui/app.py` — the store path's own entry points — survive at all?

## What to do next

1. **Merge #148 first.** Until it lands, a green tick on any webapp PR certifies
   only the Python, and that is why a night of detector work sat unreviewed.
2. **Port cicada**, the sixth detector. It was deliberately left: its `onset_field`
   defaults to `locs`, the peak, because CICADA's original does and because
   `t50rise → peak_loc` is the event duration. Read
   [`store.py`](../../src/bugarach/store.py)'s note before touching it — two
   sentences in that file have already misled two readers.
3. **Rebase the stack.** Everything here is behind `main`, which moved 20+ commits
   during the session.

## The two lessons worth carrying

**Test the screen, not the function.** A window-provenance bug shipped because every
test read `analysisSegments` directly and none pressed the button; the numbers were
right and the sentence beside them said "whole period — none sent" about a window
the detector had just used. Only the screen goes in a slide.

**Deterministic arithmetic reached only through a sampled path is untested.**
Dividing by `n` instead of `n−1` shifts every z-score by half a percent — an order
of magnitude under sampling error, invisible to anything that goes through the
shuffles. It survived everything until the arithmetic was pulled out and compared
directly.

## And one about this repo rather than the code

Two sessions converted the same two tools within hours of each other, neither
knowing the other had started. The same day, one session read a worktree that was
being actively written to as abandoned, and another concluded nobody was doing the
CI work while somebody was. The boards exist for this and were not enough, because
39 worktrees with no way to tell live from finished is not a list anybody can read.
`tools/worktree_sweep.sh` (#149) is a partial answer; the rest is that a session
should claim **before** starting, not when it first commits.
