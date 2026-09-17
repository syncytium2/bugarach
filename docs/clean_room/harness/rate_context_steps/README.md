# rate+context step page — clean-room harness

Checks that [`docs/detectors/rate_context_steps.md`](../../../detectors/rate_context_steps.md), the
plain-language walk-through of rate+context written for outside reviewers, describes the program exactly.

- `rate_from_page.py` — written 2026-09-16 by an agent given only the page with its code links removed
  (no repository, no web). Its docstring names that copy. Do not edit it to make a test pass: if the
  program changes, the page is what gets fixed, and a fresh agent rebuilds this file from the new page.
- `fuzz.py` — the cases: simulated bench recordings on both backgrounds, generated edge cases (clipped
  context, grid lengths, slot-boundary events, 0/1/2 neurons, bursts near the merge gap), each run under
  the stored settings and three others.
- [`tests/test_rate_context_steps.py`](../../../../tests/test_rate_context_steps.py) runs 1,216 of those
  comparisons in the normal suite.

**Result on 2026-09-16:** 8,616 runs, 35,553 calls, no differences (onset and width to 1e-9 s), counting a
one-time run of 2,000 extra generated cases. The agent's list of points where it had to guess was folded
back into steps 1, 2, 3, 7 and 9 of the page.

Run locally from a worktree with `PYTHONPATH=src`: the venv's editable install points at the primary
checkout, and without it the test compares the page against that copy of `rate.py` instead.
