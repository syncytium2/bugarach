"""The chorus-collapse readout is rebuilt from the data committed beside it, and must come out the same.

The tables and replays under docs/learned/chorus_collapse/ were produced from the runs' fits by
`tools/diagnose_chorus_collapse.py table | census | replay`, which need the darkroom, a GPU and the
chorus code; `page` needs only those tables. Rebuilding the page here proves that every number on it
still follows from the committed data under the tool's own checks (its asserts are the page's claims),
and that the committed page is what the tool builds, not a hand-edited copy."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "diagnose_chorus_collapse.py"
DATA = ROOT / "docs" / "learned" / "chorus_collapse"


@pytest.fixture(scope="module")
def D():
    spec = importlib.util.spec_from_file_location("diagnose_chorus_collapse", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["diagnose_chorus_collapse"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_page_rebuilds_from_committed_data(D):
    D.R._SVG_N[0] = 0          # SVG ids count up per process; the committed page was built fresh
    built = D.page(DATA)
    assert built == (DATA / "index.html").read_text(encoding="utf-8")


def test_figures_are_numbered_in_order_and_each_is_cited(D):
    D.R._SVG_N[0] = 0
    html = D.page(DATA)
    numbers = [int(n) for n in re.findall(r"<b>Figure (\d+)\.</b>", html)]
    assert numbers == list(range(1, len(numbers) + 1)) and numbers
    for n in numbers:
        assert f">Figure {n}, " in html, f"Figure {n} is never referred to by number and name"


def test_no_personal_path_reaches_the_public_page():
    # the account name comes from this machine, so the check itself names nobody
    for p in DATA.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8").lower()
            for bad in ("users\\", "home\\", "wsl$", "dropbox", Path.home().name.lower() + "\\"):
                assert bad not in text, f"{p.name} carries {bad!r}"
