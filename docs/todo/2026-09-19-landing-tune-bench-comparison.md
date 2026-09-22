---
status: open
filed: 2026-09-19
---

# Landing `tune-bench-comparison`: what has to be true first

**The scan Tony asked for on 2026-09-19**, after the weekend's fair-comparison runs finished.
Every figure below is measured, not estimated. **Re-measured at 17:40 EDT the same day**, after gate
1 was repaired and #660 merged the four architecture figures in; the first column is the original
scan against `origin/main` at `ab4eef1`.

## What the branch is

| | first scan | now |
|---|---|---|
| commits ahead of `main` | 59 | **66** |
| files | 454 | **475** |
| insertions | 54,264 | **56,382** |
| **code, tests and tools** | 21 files, 3,742 | **25 files, 4,162** |
| **run output under `docs/learned/`** | 429 files, 49,509 | **440 files, 51,120** (363 in `tuned_vs_coact/`, 66 in `field_size_candidates/`, 9 in the new `comparison/`) |

**It merges into `main` with no conflict.** `sapper --all` reports **0 blocks** (78 warnings, nearly
all SAP015's "data is plural" on prose) and `check_quotes` is clear. The largest single file is a
results JSON of 4,805 lines. So nothing here is dirty; the gates below are all decisions or one
small repair, not a mess to clean up.

**Nine tenths of the diff is run output.** That is worth seeing before anyone reacts to "56,000
lines": the tool, the tests and the library changes are 4,162 lines across 25 files, and everything
else is what the runs produced.

## The five gates

### 1. ~~The base is red~~ — repaired 2026-09-19, and the prescribed fix was half wrong

`tests/test_tune_learned_vs_coact.py` has a **module-scoped fixture** that shells out to the tuning
tool with `timeout=600` and `--jobs 4`. Fourteen tests take it. When the subprocess misses the
budget the fixture raises, and each of those tests reports as a **setup error** — the 13 errors seen
on Python 3.13 and 3.14 while 3.11 passes.

The file carries **no `serial` mark**, and CI runs `pytest -n auto --dist loadfile` on a 4-core
runner. Four xdist workers are already loading the box when the fixture asks for four more jobs, so
the budget measures the other workers as much as the code. That is why one leg passes at 84 minutes
and two do not: a race, not a version defect.

CLAUDE.md states the remedy for exactly this shape, after the briefing's 3-second budget did the
same thing: *a test that asserts on wall-clock time needs `@pytest.mark.serial`*.

**Fixed in `b9752a9`** — the module carries `pytestmark = pytest.mark.serial` and the base went
green on run 1624 at 17:45 UTC. #660 then passed on the repaired base and merged.

**Half of what this gate prescribed was wrong, and the measurement is why.** It said to drop the
inner `--jobs` to 1 as well. WSMIP064 measured that before doing it: the quick run takes **276 s at
four jobs and 559 s at one** on that workstation, and 559 against a 600 s budget leaves no room on a
slower runner. So the jobs stayed at four and only the serial mark changed. The CI timings are
recorded beside the fixture: **419 to 545 s of the 600 s budget** across the three legs. Raising the
timeout would still have been the wrong repair, for the reason given above.

**One consequence to carry forward.** A serial module runs after the parallel pass with the runner
to itself, so every branch carrying this fixture now runs a **~2-hour** CI suite rather than ~10
minutes — #642's run 1624 took 2 h 06, #660's took 1 h 47. That cost arrives on `main` with this
branch and lands on every pull request in the repository afterwards. Whether the fixture should be
trimmed first is not part of this scan, but it should be asked before the landing, not after.

### 2. Landing this branch also lands #596, which is a decision Tony reserved

`eval-field-size-candidates` is an **ancestor** of this branch — 83 files and 24,820 insertions of
the total. #642's own description says so plainly: *"The base is #596's branch, whose merge is
Tony's call (it registers the learned models in the lab server and the model picker)."*

And #596 carries its own warning: registering `gauge` and `chorus` puts them in the lab server and
the model picker, and it asks to be held if they should stay out until a real-recording check.

**So merging this branch answers that question by accident.** It is the one gate here that is purely
a ruling, and it should be made deliberately rather than inherited.

### 3. One personal path, in a public repo, that the guard cannot see

`HANDOFF-workstation-tuning.md` carries a WSL UNC path with the username in it at line 682. SAP004
matches forward slashes only, so it passes unflagged —
[the blind spot](2026-09-19-sap004-is-blind-to-backslash-personal-paths.md), filed the same day.
One line to repair, and it must happen before the branch lands, not after: a push to this repo is
publication.

### 4. The root handoffs have to be resolved

The branch carries handoff files at the repository root. *No handoff on `main` == nothing in
flight*, so each one needs the three-way decision `docs/handoffs/README.md` sets out: delete it if
spent, move it to `docs/handoffs/` if any of it is still worth reading, never leave it at the root
claiming work that has landed.

### 5. ~~Ask what the landing is actually for~~ — answered 2026-09-21: the nets landed alone

**Tony's ruling: cut the nets-only branch.** Done in
[#680](https://github.com/syncytium2/bugarach/pull/680) — the seven architectures,
`train.py`'s GPU `device=`, `registered.py` and the `line`/`tube` edits: **11 files and 580
lines**, against the branch's 476 files and 56,584. Every session starting from `main` can now
see and run the whole model family.

It inherited none of what the whole branch carries: not gate 2's reserved ruling, not 51,000
lines of run output the darkroom already holds at 98.3 MB compressed, and not the two-hour CI
suite that arrives with the tuning fixture. **So the rest of this scan is now about whether the
run output and #596 should land at all**, which is a smaller question than it was.

The original reasoning, which still holds for what remains:

**The seven stranded architectures are 7 files of the 475.** `chorus`, `chorus_gain`,
`chorus_gain_norm`, `chorus_line`, `chorus_norm`, `gauge` and `tube_no_bypass` exist only here, so
every session starting from `main` is blind to more than a third of the model family. If that is the
goal, a nets-only branch does it today and drags along neither gate 2 nor 49,509 lines of run
output.

Landing the whole branch is a different and larger decision: it publishes the weekend's results into
the repository and settles #596. Both are reasonable; they are not the same act, and the small one
does not need the large one.

## Closes when

~~Gate 1 is repaired and the base is green~~ (done, `b9752a9`); ~~gate 3 is fixed~~ (done,
[#672](https://github.com/syncytium2/bugarach/pull/672) — the username is off the branch, though
the superseded commit stays fetchable and this is not a retraction); ~~gate 5 is answered~~
(done, [#680](https://github.com/syncytium2/bugarach/pull/680) — the nets landed alone).

**Two gates remain, both Tony's:**

- **Gate 2** — whether landing this branch also lands #596, registering `gauge` and `chorus` in
  the lab server and the browser's model picker. Deliberately unruled as of 2026-09-21.
- **Gate 4** — the five handoff files at the root, each needing the three-way decision
  `docs/handoffs/README.md` sets out.

And the question gate 5 leaves behind: **with the code already on `main`, is there a reason to
land 51,000 lines of run output the darkroom already holds?**
