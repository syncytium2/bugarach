"""The rate+context step-by-step page describes the program exactly.

`docs/detectors/rate_context_steps.md` is a plain-language walk-through written for outside reviewers.
An agent that saw only that page (code links removed) wrote `rate_from_page.py`; this test runs it against
the real `rate_detect` on simulated recordings and generated edge cases, under the stored settings and
three others. If the program changes and the page does not, this fails — the page is stale.
See docs/clean_room/WORKFLOW.md for the method.
"""
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
HARNESS = REPO / "docs" / "clean_room" / "harness" / "rate_context_steps"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fuzz = _load(HARNESS / "fuzz.py", "rate_steps_fuzz")
page = _load(HARNESS / "rate_from_page.py", "rate_steps_page").rate_context_calls


def _report(bad):
    return "\n".join(f"{b['case']} variant {b['variant']}: real {b['n_real']} calls {b['real']} / "
                     f"page {b['n_page']} calls {b['page']}" for b in bad[:10])


def test_page_matches_program_on_simulated_recordings():
    bad, n = fuzz.compare(page, fuzz.bench_cases(seeds=(1, 2)))
    assert n > 0
    assert not bad, _report(bad)


@pytest.mark.parametrize("seed", [20260916, 7])
def test_page_matches_program_on_edge_cases(seed):
    bad, n = fuzz.compare(page, fuzz.random_cases(n=150, seed=seed))
    assert n > 0
    assert not bad, _report(bad)
