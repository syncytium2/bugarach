# ADR-0004: CI installs torch, and takes it from the CPU wheel index

## Status

Accepted, 2026-08-27, by Tony. Numbered **0004 and not 0003** because nine files on
`main` already cite ADR-0003 for *"Parity was the inheritance, not a standing
contract"*, which sits unmerged on the `parity-was-the-inheritance` branch pending
[the question about PR #298](../todo/2026-08-26-nine-files-name-an-adr-that-does-not-exist.md).
Taking 0003 here would break all nine citations. If that PR is declined and 0003 is
freed, this ADR still keeps its number — renumbering an accepted decision is worse
than a gap.

## Context

`pyproject.toml` has declared an optional extra since 2026-08-17:

```toml
dl = ["torch>=2.0"]
```

It was added in [`9582329`](https://github.com/syncytium2/bugarach/commit/9582329),
a commit that rewrote 445 lines of README and touched `pyproject.toml` on one line.
`.github/` was not in the diff. The extra existed so the README's install
instructions would be accurate, and nothing was ever wired to request it.

CI installed `pip install -e ".[ui]" pytest playwright`. So on every run, for ten
days, `tests/test_learn_nets.py` hit its module-level `pytest.importorskip("torch")`
and stood down — eleven structural checks on the published `tube` architecture,
collapsed into a single `1 skipped` line, with pytest exiting 0 and the README badge
green.

Those eleven are not incidental tests. A murderboard on 2026-08-16 found that
`docs/learned/report.html` asserted things about the architecture that nothing could
falsify, and they were written in response. The file's own docstring says the page's
footer claimed its tests had landed. They had landed. They had never run.

This repo had already met this failure mode twice and named it both times. `ci.yml`
sets `BUGARACH_REQUIRE_BROWSER` and `BUGARACH_REQUIRE_PR_API`, each with a comment
saying in terms that a guard which can go quiet is a green tick that looked at
nothing. The torch skip was the same shape with no guard, and it is the last one —
`ci.yml` is the only workflow in this repo that can fail, and the only test CI
anywhere in the stack, since interface2 and foundations have no `.github` at all.

### Why the index is a decision and not an implementation detail

torch ships in incompatible hardware variants of the same version, so PyTorch
publishes the CUDA build to PyPI as the default and runs its own indexes for the
rest. What PyPI's Linux default costs, per matrix leg:

| | |
|---|---|
| `torch==2.13.0` | 526.6 MB |
| `nvidia-cudnn-cu13` | 366.2 MB |
| `nvidia-nccl-cu13` | 206.0 MB |
| `nvidia-cusparselt-cu13` | 170.1 MB |
| `nvidia-nvshmem-cu13` | 60.4 MB |
| `triton` | 197.7 MB |
| **total** | **1,527 MB** |

against **191.8 MB** for `torch==2.13.0+cpu`, which declares none of them. The
matrix has three legs, so it is roughly 4.6 GB against 0.6 GB on every push and
every pull request — for a runner with no GPU, where not one of those libraries can
ever be loaded. `+cpu` wheels exist for cp311, cp313 and cp314, which covers the
matrix exactly.

## Decision

**CI installs `[ui,dl]`, and takes torch from `https://download.pytorch.org/whl/cpu`
in a separate, scoped `pip install`.**

```yaml
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[ui,dl]" pytest playwright
```

Two calls, deliberately. `--index-url` *replaces* PyPI, and the PyTorch index is not
a general mirror — it serves HTTP 403 for `panel`, `holoviews` and `pytest`, so
pointing the whole install at it breaks `[ui]`. The obvious alternative,
`--extra-index-url`, was declined: it would work, because `2.13.0+cpu` sorts above
`2.13.0` under PEP 440, but it works by a version-ordering side effect rather than
by saying what is meant, and it makes pip search both indexes for every package —
the shape behind dependency-confusion attacks. Scoping `--index-url` to the one
package that needs it says exactly what is intended and exposes nothing else.

Two supporting changes:

- `torch>=2.0` joins the `dev` extra, so a contributor running `pip install -e
  ".[dev]"` gets a suite that runs rather than one that quietly skips.
- `BUGARACH_REQUIRE_TORCH=1` is exported in CI, the third instance of the guard
  pattern already used for the browser and the PR API. `tests/test_learn_nets.py`
  fails on a missing torch when it is set and skips when it is not, and
  `tests/test_torch_available.py` asserts that the install line still names `dl`,
  still pins the index, and still declares the requirement.

## Consequences

**Eleven tests move from invisible to enforced.** `test_learn_nets.py` runs in CI on
all three Python versions. The badge now covers the learned detectors' architecture.

**A laptop is unchanged.** Nothing in `pyproject.toml` names an index. `pip install
-e ".[dev]"` on the MacBook resolves through PyPI exactly as before, and a Linux
workstation with a GPU still gets the CUDA build, which is what it should get. The
index choice is CI's alone, because the GPU-lessness that motivates it is CI's alone.

**CI gains a second host to depend on.** If `download.pytorch.org` is unreachable
the install step fails and the build goes red for a reason unrelated to the code.
This is the real cost, accepted against roughly 4 GB of transfer per run. **If it
proves flaky, drop the first `pip install` line and let torch come from PyPI** — the
suite is unaffected, only the runner's time and disk. That reversal needs no ADR;
`tests/test_torch_available.py::test_torch_comes_from_the_cpu_wheel_index` will fail
and should be updated in the same commit, and this ADR superseded if the change is
meant to stand.

**It exposed a defect that was hidden behind the skip.** Installing torch would also
have switched on `test_the_server_reproduces_the_published_bakeoff`, which trains the
tube model and asserts the per-fold counts in `docs/learned/bakeoff.json` come back
identical. It fails on a 4-core runner. `learn/train.py` seeds with
`torch.manual_seed` and pins nothing else, so torch takes its intra-op thread count
from the hardware — 10 on the Mac that generated the reference — and the CPU
reduction order goes with it:

```
threads   mean F1     n_detected per fold (published -> run)
     10   0.667972    71->71  47->47  58->58  45->45   reproduces
      1   0.685781    71->76  47->47  58->58  45->62
      2   0.685781    71->76  47->47  58->58  45->62
      4   0.685781    71->76  47->47  58->58  45->62
```

The mean F1 moves +0.018, about 2.7%, so the model is sound and the published
headline is robust; what is not true is that the numbers can be regenerated
anywhere. **This ADR does not fix that** — the fix is to pin the thread count in the
trainer and regenerate, which changes numbers `docs/learned/report.html` publishes to
a reader, and that is Tony's call. It is filed in
[`docs/todo/2026-08-27-the-bakeoff-reference-is-thread-count-bound.md`](../todo/2026-08-27-the-bakeoff-reference-is-thread-count-bound.md).
Until it is taken, that test skips wherever the thread count is not the one the
reference was made under, and says so in the skip message.

That last consequence is worth stating plainly, because it is an argument for the
change rather than against it: the defect had been sitting behind a skip, and
installing the dependency is what made it visible.
