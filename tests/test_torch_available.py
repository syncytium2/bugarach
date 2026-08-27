"""The third guard, and the one that was missing longest.

`tests/test_browser_available.py` exists because a skipped test and a passing
test look identical in a summary line. This is the same argument for torch, and
it had a ten-day head start: `[dl]` was declared in `pyproject.toml` on
2026-08-17, inside a commit that rewrote the README, and `.github/workflows/`
was not touched. Nothing ever installed it. So every test in
`tests/test_learn_nets.py` — eleven structural checks on the published `tube`
architecture, the ones a murderboard added precisely because the report's claims
were unfalsifiable — collapsed into a single `1 skipped` line, and pytest exited
0, and the badge on the README stayed green.

ADR-0004 wires the install. This file is what stops it coming loose again: the
install line is asserted here, so an edit to the workflow that drops the extra
fails a test instead of quietly returning the suite to where it was.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

REQUIRED = os.environ.get("BUGARACH_REQUIRE_TORCH") == "1"


def test_torch_is_available_where_it_is_required():
    """Fails only where the environment says torch is expected — CI sets that.
    Everywhere else this reports why it stood aside rather than passing
    silently, because "skipped" and "there is nothing to check" are different
    statements and only one of them is true here."""
    if not REQUIRED:
        pytest.skip("BUGARACH_REQUIRE_TORCH is not set — the learned-detector "
                    "tests may skip, and a green run here says nothing about "
                    "learn/nets.py")

    try:
        import torch
    except ImportError as exc:                            # pragma: no cover
        pytest.fail(
            f"BUGARACH_REQUIRE_TORCH=1 but torch is not installed ({exc}). "
            f"Every test in tests/test_learn_nets.py is skipping and the run "
            f"is green anyway.")

    # Not decoration: a wheel that imports but cannot run a convolution would
    # skip nothing and check nothing.
    x = torch.zeros(1, 1, 8)
    assert torch.nn.functional.conv1d(x, torch.ones(1, 1, 3)).shape == (1, 1, 6)


def test_ci_installs_the_dl_extra():
    """The regression this file exists for. `[dl]` spent ten days declared and
    uninstalled; the failure mode is silent, so it gets a check rather than a
    memory."""
    body = WORKFLOW.read_text(encoding="utf-8")

    installs = [ln.strip() for ln in body.splitlines()
                if "pip install" in ln and "-e" in ln]
    assert installs, "no editable install line found in ci.yml at all"
    assert any("dl" in re.search(r'"\.\[([^\]]*)\]"', ln).group(1).split(",")
               for ln in installs
               if re.search(r'"\.\[([^\]]*)\]"', ln)), (
        f"ci.yml installs {installs} — none of them names the `dl` extra, so "
        f"torch is absent and tests/test_learn_nets.py is skipping. That is "
        f"exactly the state ADR-0004 was written to end.")


def test_ci_requires_the_torch_tests_to_run():
    """Installing torch is half of it. Without the variable a future install
    regression downgrades to a skip again instead of failing."""
    body = WORKFLOW.read_text(encoding="utf-8")
    assert "BUGARACH_REQUIRE_TORCH=1" in body, (
        "ci.yml installs torch but does not declare that it requires it — if "
        "the install breaks, the learn tests go back to skipping green")


def test_torch_comes_from_the_cpu_wheel_index():
    """ADR-0004's actual decision, and the part most likely to be dropped by a
    later edit that only means to tidy the install. Losing it costs ~1.3 GB of
    unusable CUDA runtime per matrix leg; it is not a correctness bug, which is
    why nothing else would notice."""
    body = WORKFLOW.read_text(encoding="utf-8")
    assert "download.pytorch.org/whl/cpu" in body, (
        "ci.yml no longer pins torch to the CPU wheel index — see ADR-0004; if "
        "that was deliberate, supersede the ADR rather than deleting the line")
    # Commands only. `ci.yml` explains in a comment why --extra-index-url was
    # declined, and a check that cannot tell prose from instruction would forbid
    # writing down the reasoning — which is the opposite of what this repo wants.
    commands = [ln for ln in body.splitlines()
                if not ln.lstrip().startswith("#")]
    assert not any("--extra-index-url" in ln for ln in commands), (
        "ADR-0004 uses --index-url in a scoped `pip install torch` call. "
        "--extra-index-url makes pip search both indexes for every package, "
        "which is the dependency-confusion shape the ADR declined")


def test_the_learn_suite_is_not_empty():
    """A torch that imports proves nothing if the files that would use it have
    been renamed or removed, so the count is asserted rather than assumed."""
    files = sorted(Path(__file__).parent.glob("test_learn_*.py"))
    assert len(files) >= 2, (
        f"only {len(files)} learn test file(s) found — if these were renamed, "
        f"the torch guard above is now guarding nothing")
