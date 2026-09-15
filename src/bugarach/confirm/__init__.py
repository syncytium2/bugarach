"""The rigid-shift confirmatory run, written as code before any recording is read.

The pre-registration in ``docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md``
was reviewed twice and could not be executed from its prose: results overlapped, two gates
could not fail, and an exclusion inverted its own purpose (the blind-round record in
``docs/reviews/``). Tony chose to have the rule written as tested functions instead, so that
review is a question of tests passing rather than of readings.

:mod:`bugarach.confirm.rule` holds the decision: how gate statistics become verdicts, and how
verdicts become one outcome. It reads numbers, never recordings.
"""
