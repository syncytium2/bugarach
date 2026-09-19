"""The fair comparison's report builds from the committed run files, and keeps the house rules a
reader relies on: figures numbered 1 to N without gaps, each one referred to in the prose, inline
SVG only, and no personal path from the machine the run was on."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "build_fair_comparison_report.py"
RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"


@pytest.fixture(scope="module")
def html(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("report")
    res = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], capture_output=True,
                         text=True, cwd=REPO, timeout=600)
    assert res.returncode == 0, res.stdout + res.stderr
    return (out / "index.html").read_text(encoding="utf-8")


def test_figures_are_numbered_without_gaps_and_each_is_referred_to(html):
    numbers = [int(n) for n in re.findall(r"<figcaption><b>Figure (\d+)\.", html)]
    assert numbers == list(range(1, len(numbers) + 1)) and numbers
    for n in numbers:
        assert f'href="#fig{n}"' in html, f"Figure {n} is never referred to in the prose"
        assert f'id="fig{n}"' in html


def test_every_figure_is_inline_svg(html):
    assert html.count("<figure") == html.count("<svg")
    assert "<img" not in html


def test_no_personal_path_reaches_the_page_or_the_committed_files(html):
    for text in [html] + [p.read_text(encoding="utf-8") for p in RUN.rglob("*.json")]:
        assert not re.search(r"[A-Za-z]:\\\\?Users\\\\?[a-z]", text)
        assert "Dropbox" not in text


def test_the_crowded_check_covers_every_coded_choice():
    results = json.loads((RUN / "results.json").read_text())
    check = json.loads((RUN / "crowded_check.json").read_text())
    expected = {(d, row["outer_fold"], w) for d, rows in results["hand"].items() for row in rows
                for w in ("ungated", "gated")}
    got = {(c["detector"], c["outer_fold"], c["selection"]) for c in check["choices"]}
    assert got == expected
