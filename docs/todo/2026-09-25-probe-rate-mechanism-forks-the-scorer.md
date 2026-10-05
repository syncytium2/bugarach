---
status: open
filed: 2026-09-25
---

# `tools/probe_rate_mechanism.py` pools precision by its own rule

**What:** the tool's `score()` pools precision as `n_hit / n_detected` by hand, and its docstring
says it is *"mirroring bench.evaluate's pooling"*, which it is not. That fork is the finding of
[the two-scorers todo](2026-08-25-two-scorers-two-winners-and-nothing-decides.md), closed on
2026-09-25 because [ADR-0009](../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)
decision 1 settled the rule: the elevated-rate test is scored on a recording of its own, against
its own budget, and never enters precision.

**Do one of:**
- make `score()` pool through `bench.pool_scores`, so it scores the way the bench does; or
- retire the tool if nothing still reads it (`docs/INDEX.md` and `docs/pipelines.md` say what
  does).

Either way the docstring stops claiming to mirror a rule it does not. Nothing is blocked on this.
