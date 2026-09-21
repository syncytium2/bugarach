"""The leaderboard derives its verdict rather than carrying one.

The failure this guards against is the one `bakeoff.md` already has a todo for:
a table of retyped numbers that goes stale without anything going red. So the
tests here check the *rule*, not today's answer — except for one smoke case that
proves the committed files still parse into rows.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from leaderboard import (  # noqa: E402
    RUNS,
    T_CRIT_DF3,
    Row,
    read_rows,
    render,
    standing,
)


def row(mean: float, t_corrected: float, **over) -> Row:
    base = dict(
        draw="first draw",
        selection="gated",
        model="chorus_norm",
        variant="config_kept",
        mean=mean,
        t_corrected=t_corrected,
        folds_ahead=2,
        folds=4,
        within_noise=False,
    )
    base.update(over)
    return Row(**base)


class TestSeparability:
    def test_a_large_positive_margin_clears(self):
        assert row(0.08, T_CRIT_DF3 + 0.5).separable

    def test_a_margin_inside_the_corrected_interval_does_not(self):
        assert not row(0.08, T_CRIT_DF3 - 0.5).separable

    def test_being_ahead_is_not_enough(self):
        """The whole point of the bar: ahead and separable are different claims."""
        r = row(0.0043, 1.56)
        assert r.mean > 0
        assert not r.separable
        assert r.verdict == "ahead, not separably"

    def test_a_large_negative_margin_never_clears(self):
        """A net losing decisively has a big |t| too — sign must be checked."""
        r = row(-0.15, -8.5)
        assert not r.separable
        assert r.verdict == "behind"


class TestStanding:
    def test_it_says_nobody_cleared_when_nobody_did(self):
        text = standing([row(-0.01, -1.0), row(0.004, 1.5)])
        assert "No learned detector has cleared the bar" in text
        assert "Of 2 comparisons" in text
        assert "1 put a net ahead" in text

    def test_it_names_the_models_that_clear(self):
        text = standing([row(0.09, 4.0), row(-0.01, -1.0)])
        assert "1 of 2 comparisons clear the bar" in text
        assert "chorus_norm" in text

    def test_it_counts_every_comparison_as_an_attempt(self):
        """41 shots at a bar is the number a final run has to be read against."""
        text = standing([row(-0.01, -1.0)] * 41)
        assert "Of 41 comparisons" in text


class TestAgainstTheCommittedRuns:
    @pytest.fixture(scope="class")
    def parsed(self):
        rows, constants = read_rows(RUNS)
        if not rows:
            pytest.skip(f"no committed comparison files under {RUNS}")
        return rows, constants

    def test_both_draws_are_present(self, parsed):
        rows, _ = parsed
        assert {r.draw for r in rows} == {"first draw", "replicate"}

    def test_both_selections_are_present(self, parsed):
        rows, _ = parsed
        assert {r.selection for r in rows} == {"gated", "ungated"}

    def test_the_model_name_survives_the_key_split(self, parsed):
        """Keys read '<model> <variant> - coact'; an underscored model must stay whole."""
        rows, _ = parsed
        assert "chorus_gain_norm" in {r.model for r in rows}
        assert all(" " not in r.model for r in rows)

    def test_every_variant_is_one_the_page_can_gloss(self, parsed):
        from leaderboard import VARIANTS

        rows, _ = parsed
        assert {r.variant for r in rows} <= set(VARIANTS)

    def test_the_noise_scale_is_carried_through(self, parsed):
        _, constants = parsed
        assert constants["noise_f1"] == pytest.approx(0.01)

    def test_the_page_states_its_accounting(self, parsed):
        """Reporting one accounting silently would mislead the other way."""
        rows, constants = parsed
        page = render(rows, constants)
        assert "every refit" in page
        assert "Neither accounting is neutral" in page

    def test_the_page_says_what_is_not_frozen(self, parsed):
        rows, constants = parsed
        page = render(rows, constants)
        assert "crowded-recording allowance" in page
        assert "stopping rule was deliberately not set" in page
