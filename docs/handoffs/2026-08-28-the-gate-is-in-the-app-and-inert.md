# The gate is in the app, and it cannot fire yet — 2026-08-28

**The app's sweep can now refuse a setting that cheats, and it will never do so**, because
the thing it refuses on is not in the data. That is the whole state of play, and closing it is
one change to the browser's generator plus the parity test that change earns.

The **promiscuity probe** is a dense-but-random block planted in a simulated recording with
**no coordinated events in it** — so anything a detector fires there is a false alarm by
construction, and how often it fires is the number that says whether a setting is winning on
F1 by keying on how busy the recording is. Python has gated operating-point selection on it
since 2026-08-22. The app now can too (#387) — but no recording the app generates contains
one, so the gate's input is always undefined and it always passes.

`main` green at `7637a84`; suite **1,536 passed, 16 skipped, 1 xfailed**; sapper clear.

> **Filed here rather than at the root, on purpose.** Nothing in this session is half-done —
> it all landed (#375, #377, #378, #381, #383, #387). A root `HANDOFF.md` means *work is in
> flight*, and the root one belongs to the 2026-08-27 session and is still live by its own
> test: `_still_live` is `any(state == "OPEN")`, not *all*, and #292, #53 and #50 are open.
> (I assumed the opposite first and checked before writing it down.) This is a **cue sheet**,
> not a rescue.

---

## The one thing to do first, and the trap in it

**Plant the promiscuity probe in the browser's generator.** Everything downstream of it is
built and tested; the generator itself exists and works — what it has never had is the hot
block.

The app's sweep is the bake-off that matters — Tony, 2026-08-28: *"all the bake-offs
are stale. the next bakeoff will be in app. that is the only pipeline that matters
now."* Its `pickOperatingPoint` had **two** of the Python's three refusals and not the
promiscuity gate. #387 added the third, plus the `hotFa` count it needs. Both are
inert today because **no recording the page generates has a probe**, and there is a
test pinning that a missing probe means *unknown* rather than *zero*.

⚠ **The trap, which is why #387 stopped short of planting it.** `simulate.py:693` is only
where the window becomes an exclusion argument:

```python
excl = None if hot_window is None else (float(hot_window[0]), float(hot_window[1]))
```

**The behaviour it buys is inside the planting function, and that is the part to port** —
`simulate.py:318-326` widens the excluded span by `min_sep`, then `hi = hi - gap_width`
*"place on the compressed timeline"*, and `:363` maps the drawn times back out
(`np.where(times >= gap_lo, times + gap_width, times)`). So planting **excludes** the hot
window by shortening the timeline, drawing on it, and restoring the gap afterwards. A port
that skips this puts planted events **inside the block that is supposed to contain
none**, and then the probe lies about precisely the thing it exists to measure: every
detection in there would be scoreable as a hit, `hotFa` would undercount, and the gate
would pass settings it should refuse. **Read `plant_times` end to end before writing
the JS.** That function also raises two errors worth porting — a window that leaves no
room, and events that cannot fit at `min_sep`.

**What is already done and needs no repeat:**

| | |
|---|---|
| `scoreDetections` returns `hotFa` | false alarms **overlapping** the window, matching `score.py:242` — not containment of the left edge |
| `poolScores` consumes it | `nScored = nDetected - hotFa`, spliced from `scoring.js`, parity-checked against `bench.pool_scores` on exactly this case |
| `gateOnProbe` refuses | `MAX_PROBE_PER_MIN`'s numbers; **does not re-rank** — a promiscuous winner is refused, never silently replaced by the runner-up |
| four tests | in `test_webapp_tune_parity.py`, beside the two refusals it already covered |

**Why this is not queue-jumping RESET §7.** Steps 3 and 4 (the K decision, mechanism behind
flags) sit in front of step 5 and are Tony's. This is neither: the probe is **benchmark data**,
not a change to any detector's mechanism, and it is on the app's side of the line rather than
the Python campaign's. It unblocks a gate that already shipped; it does not re-fit anything.

**A deliberate duplication, and it needs saying.** The browser's generator is a hand-written
port of `simulate.py` and the published page cannot call Python — `test_site_viewer.py` bans
`fetch(`, `<script src` and `import(`. So the hot block will exist twice on purpose. The
project's answer to that is parity tests, and there is an established pattern to copy:
`test_webapp_*_parity.py` hands the same input to both languages and demands agreement. Add
one for the probe rather than trusting the port.

**Predicted and unmeasured:** planting the probe should be roughly **F1-neutral**,
because the probe adds detections and then excludes them from the precision
denominator. That is algebra, not a measurement. Measure it before and after on the
same folder and state the answer — this repo has been wrong about exactly this kind
of prediction before. What is *not* neutral either way: the user's simulated recording
gains a dense block, which changes the raster they look at and the data they tune on.

## Cued, in the order they cost something

**1 · The gate is not on the live site.** `tools/site_staleness.py` reads *behind by 5
commits, 1 of which changes what it serves* — `d999ae4`, the gate. The deploy needs a
Cloudflare credential and is Tony's to run:

```
PATH=$PWD/.venv/bin:$PATH npm run deploy && python tools/audit_deployed_page.py
```

Note the site *was* current as of `3a0b63b`; #387 landed after it. This is not the old
staleness, it is one commit of new.

**2 · `bench.py:703` is wrong and has never been right.**

```python
span = BENCH_RECORDING["hot_window"]     # whatever recording produced this result
```

`hot_fa_per_min` computes against the bench recording's window regardless of which
recording the result came from. Correct today only because the bake-off spec happens
to carry the same window — luck, not design. **The browser is the reference here**:
its `hotFaPerMin(hotWindow)` takes the window as an argument. `score.py:239` reads it
from `gt.params`, which is where it lives. Filed in
[the bake-off todo](../todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md).

**3 · Do not act on that todo's fix section.** It prescribes repairing
`tools/fair_bakeoff.py` and regenerating `docs/learned/bakeoff.json`. Tony's ruling
above retires that path. The file carries the ruling at the top; the fix section is
left standing as a record of what *would* have been done, because the measurement in
front of it is the evidence for the probe job at the top of this handoff.

**4 · `tools/refit.py` (#378) is on the stale side.** It walks the Python campaign —
detector × regime through `sweep()` and `pick_operating_point()` — and it works, but
it is aimed at the bake-off Tony just retired. **Do not build on it.** It is still
useful as the worked example of catching the three refusals as *outcomes* rather than
letting the first end the run, which is what the app will need when a campaign there
grows past one sweep.

**5 · The lab server is not in the bake-off's path** — Tony's own instinct (*"the lab server
is probably obsolete. why use it if the app does it"*) turned out to be right for a reason
neither of us had checked.
`tuneDataSet()` walks `RECORDINGS` + `TRUTH` — the browser's own simulated folder. The only
place `labSpec()` **generates** anything is `api.train({spec: labSpec()})`, the PyTorch
training of the tube (stage 6b) — the one thing the browser cannot do, and ADR-0001's whole
rationale. (Its other reader, `paintLabWhat()`, merely displays which fields were carried, so
the panel says so rather than letting a default read as a measurement.) So adding `hot_window`
to `LAB_SPEC_DEFAULTS` would plant a probe in the **training** data and never in the sweep's.
The lab server goes obsolete when the browser can train, which is
[lane C](../todo/2026-08-19-lane-c-tube-trainer-in-the-browser.md), still `status: open`.

**6 · Two of RESET §7's steps are Tony's** and nothing else unblocks them: **step 3**,
the fresh assessment and the **K decision**; **step 4**, which mechanism changes go
behind flags. RESET.md reached `main` today (#377) — sessions had been reading §7 out
of `HANDOFF.md`'s copy because the source was on an unproposed branch.

**7 · The scoring decision is narrower than the todo's title.** #379 measured it:
`bench.py` has kept the probe out of F1 **and** gated on it at selection since
2026-08-22, which is the "third form" the todo lists as unconsidered. The gate **sides
with the probe-blind rule on the mechanism** (0 of 7 either way) and refuses what the
todo actually objects to — **31 of 56** additive candidates, moving additive's own
operating point. The open question is *"is the gate enough?"*, not *"pick one of two."*

## What I got wrong, because the pattern is the useful part

**I under-sized this area three times running**, and each correction came from reading
code rather than from my estimate: *"add a third branch"* → the probe does not exist →
*"one key in `LAB_SPEC_DEFAULTS`"* → wrong route entirely → *"a Poisson draw over a
window"* → plus the exclusion port above. If you are sizing the remaining work, read
`plant_times` first and quote the number after.

**Two of my own test drafts were wrong and the tests caught them**, which is the
argument for writing them: a curve helper that set `hot_fa` without adding it to
`n_detected`, shrinking `n_scored` and walking the peak off the point under test; and
a stub `hotFaPerMin` that ignored its argument, reporting a rate for a recording with
no probe. Both now carry a note saying why.

**A local suite failure that is not a failure.** `test_lab_server.py`'s page test goes
red in a worktree the moment you edit `raster_viewer.html`: the venv resolves
`bugarach` to the **primary checkout**, so `lab.py`'s `VIEWER` constant serves the
unedited page while the test compares against your edited one. `PYTHONPATH=src` makes
all 20 pass. Known and filed —
[worktree pytest reads the primary checkout's src](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md).
Separately, `test_hooks_installed` fails on any clone where `core.hooksPath` is unset — it is
set on this machine and passing, so you will only meet it on a fresh clone; `git config
core.hooksPath .githooks` is the fix, and it is what arms the commit gates.

**The commit gate refused me once, correctly.** I took a worktree for what looked like
a one-paragraph correction, skipped the board block as too small to bother with, and
the gate refused the commit. The "one paragraph" then grew into a change to
`raster_viewer.html`, which is contended. **The scope in a claim is a prediction —
re-read it when the work turns.**

## Also landed today, for the record

**#375** — locust's duration story, in Tony's account, as an ADR-0002 addendum and a
FOUNDATIONS §7 paragraph. The port takes CICADA's coordinated-event stage alone; that
stage needs a per-event duration; this preparation's slow events are not in the
literature and break it at full duration, so slow-event duration is truncated to
`peak − t50rise` **on export, by the MATLAB team**. So the imported duration is the
duration, and *"it is none of our business what the user decides to put in the duration
column of the import."* The rise-interval sentence in FOUNDATIONS was true all along —
what was missing was where a reader locates the step.

**#377** — `docs/RESET.md` on `main`, four days after it was written and never
proposed. Argument untouched; two operational claims corrected (CI-fails-on-every-PR,
fixed the way §9 itself prescribed) and §7 steps 0–2 marked done.
