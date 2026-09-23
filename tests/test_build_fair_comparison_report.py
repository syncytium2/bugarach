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


SUPERSEDED_BENCH = "SUPERSEDED BENCH"
"""Kept as a literal, deliberately. Importing it from the tool would make this file agree
with whatever the tool happens to say today; the point is to pin the contract from outside."""


@pytest.fixture(scope="module")
def html(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("report")
    res = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], capture_output=True,
                         text=True, cwd=REPO, timeout=600)
    if res.returncode != 0 and SUPERSEDED_BENCH in res.stdout + res.stderr:
        pytest.skip(
            "the 2026-09-18 run was scored on a bench that no longer exists: it declared "
            "jitter_sec 0.36 s, and the bench adopted the measured 0.106 s on 2026-09-22. "
            "The run's numbers stand; its report cannot be re-rendered against today's "
            "constants. Re-run, freeze, or render with a superseded-bench banner is Tony's "
            "call -- docs/todo/2026-09-22-the-corrected-jitter-flattens-spike-synch-across-"
            "the-axis.md. These house-rule checks resume when run and bench agree again.")
    assert res.returncode == 0, res.stdout + res.stderr
    return (out / "index.html").read_text(encoding="utf-8")


def test_the_builder_refuses_a_run_from_a_different_bench():
    """The guard itself, pinned from outside the tool.

    Without this the skip above would be self-fulfilling: a builder that quietly stopped
    checking would simply stop skipping, and every house-rule test below would pass on a
    page carrying today's constants over another bench's results. This asserts the builder
    still compares the run's declared `bench_recording` against the live bench and refuses
    **by that name**, so the skip can be trusted to mean what it says.
    """
    src = TOOL.read_text(encoding="utf-8")
    assert SUPERSEDED_BENCH in src, (
        "the builder no longer names its superseded-bench refusal, so the skip in this "
        "module would hide a real failure instead of reporting a known one")
    assert '"jitter_sec"' in src and "bench_recording" in src, (
        "the builder no longer compares the run's declared bench_recording against the live "
        "bench -- a report could be rebuilt across a bench change without saying so")


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
    """The repository is public, and sapper SAP004 matches forward-slash paths only (armory
    finding 23), so a Windows or WSL path would pass the commit gate. This test looks for both
    slash forms, and for the running machine's own user name, read at run time rather than
    written here."""
    me = Path.home().name.lower()
    for text in [html] + [p.read_text(encoding="utf-8") for p in RUN.rglob("*.json")]:
        low = text.lower()
        assert not re.search(r"[a-z]:[\\/]+users[\\/]+[a-z]", low)
        assert not re.search(r"[\\/]+(home|users)[\\/]+[a-z0-9._-]+[\\/]", low)
        assert "wsl$" not in low and "dropbox" not in low
        assert len(me) < 3 or me not in low


def test_the_merge_gap_evidence_reproduces_the_run_at_its_own_gaps():
    """Figure 5 and the headline rest on merge_gap.json. It changes one setting at a time, so it is
    only evidence if, at each side's own gap, it gives back exactly what the run scored."""
    doc = json.loads((RUN / "merge_gap.json").read_text())
    results = json.loads((RUN / "results.json").read_text())
    for d, rows in doc["coded"].items():
        assert len(rows) == len(results["hand"][d]) * 2
        assert max(r["reproduces_run"] for r in rows) < 1e-9, d
    # The nets were trained and scored on the GPU and are re-scored here on the processors, whose
    # arithmetic differs slightly: the worst refit lands 0.0015 F1 away. A defect in the re-decoding
    # (a wrong threshold, a wrong recording) moves a refit by tenths, not thousandths.
    for m, rows in doc["nets"].items():
        assert len(rows) == len(results["learned"][m]) * 2
        assert max(e["reproduces_run"] for r in rows for e in r["per_seed"]) < 0.005, m


def test_the_fold_draw_evidence_is_regenerable():
    """Figure 4's before-fix strips come from the project's own fold_maker, not a copied rule."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("evidence", REPO / "tools" / "fair_comparison_evidence.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    doc = json.loads((RUN / "fold_draws.json").read_text())
    from bugarach.learn.train import TRAIN_SEED_BLOCK, VAL_SEED_BLOCK, fold_maker
    decl = json.loads((RUN / "meta.json").read_text())["declaration"]
    for h, got in doc["before_fix"].items():
        train = sorted(int(s) for s, f in doc["fold_of"].items() if f != int(h))
        mk, _, _ = fold_maker(lambda r: r, [f"{b}:{s}" for s in train for b in ev.REGIMES])
        fitted = sorted({mk(TRAIN_SEED_BLOCK + doc["seed"] * 1000 + i) for i in range(doc["n_train"])})
        picked = sorted({mk(VAL_SEED_BLOCK + doc["seed"] * 1000 + i) for i in range(4)})
        assert (fitted, picked) == (got["fitted"], got["threshold"]), h
    assert decl["fold_check"]["distinct"] is True


def test_the_crowded_check_covers_every_coded_choice():
    results = json.loads((RUN / "results.json").read_text())
    check = json.loads((RUN / "crowded_check.json").read_text())
    expected = {(d, row["outer_fold"], w) for d, rows in results["hand"].items() for row in rows
                for w in ("ungated", "gated")}
    got = {(c["detector"], c["outer_fold"], c["selection"]) for c in check["choices"]}
    assert got == expected
    # Both references are scored, so "which reference changes no verdict" is read from a file.
    assert set(check["shipped_reference"]) == set(results["hand"])
    assert all("passes_veto_vs_shipped" in c for c in check["choices"])


def test_the_refit_rule_reads_both_draws_alike():
    """Section 6 sets refits under LOW_F1 aside in this run and in the replicate by one rule; the
    replicate's summary must carry that rule's output, computed by the same function."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("evidence", REPO / "tools" / "fair_comparison_evidence.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    repl = json.loads((RUN / "replicate_summary.json").read_text())
    this = ev._refit_health(json.loads((RUN / "results.json").read_text()))
    for health in (repl["refits"], this):
        for m, by_sel in health.items():
            for w, folds in by_sel.items():
                for x in folds:
                    assert x["low"] == [s for s, f in zip(x["seeds"], x["f1"]) if f < ev.LOW_F1]


def test_the_breakdown_covers_every_fold_and_selection():
    doc = json.loads((RUN / "breakdown.json").read_text())
    for group in (doc["detectors"], doc["nets"]):
        for rows in group.values():
            assert {(r["outer_fold"], r["selection"]) for r in rows} == \
                {(h, w) for h in range(4) for w in ("ungated", "gated")}
            for r in rows:
                for b in ("quiet", "busy"):
                    rec = r["by_background"][b]["recall_by_participation"]
                    assert set(rec) == {"0.1", "0.18", "0.3"} and all(0 <= v <= 1 for v in rec.values())
