"""Deliberately broken pattern_jitter variants, for WORKFLOW.md's sanity check of the fuzzer.

Each mutant is the adversary with one defect switched on (``adversary.Variant``). The fuzzer
must catch every one of them on generated cases, not only on the named vectors: a mutant the
fuzzer lets through means its generator is missing a shape, and a zero-disagreement result
from it would mean nothing.

The first column of ``MUTANTS`` is the defect; the last is a spec or adversary vector that
already kills it, checked separately so a mutant that no vector kills is also visible.
"""

import importlib.util
from pathlib import Path

_HERE = Path(__file__).parent


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pj_harness_{name}", _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


adversary = _load("adversary")
fuzz = _load("fuzz")

# name: (Variant flag, what the defect is, a vector that kills it)
MUTANTS = {
    "R_plus_one":       ("R_plus_one", "history length off by one, R + 1", "R_binds"),
    "split_at_R":       ("split_at_R", "an interval of exactly R starts a new pattern",
                         "interval_R_and_R_plus_1"),
    "gap_minus_one":    ("gap_minus_one", "'at least R' read for 'longer than R'", "R_binds"),
    "gap_no_span":      ("gap_no_span", "gap measured start to start, span left out",
                         "end_to_start_gap"),
    "gap_next_span":    ("gap_next_span", "gap uses the next pattern's span", "span_binds_next"),
    "centred":          ("centred", "window centred on the start, not the fixed partition",
                         "three_singletons"),
    "anchor_zero":      ("anchor_zero", "partition anchored at frame 0, not at start",
                         "anchor_at_start"),
    "block_plus_one":   ("block_plus_one", "block boundary wrong: L + 1 frames",
                         "three_singletons"),
    "clip_to_block":    ("clip_to_block", "later onsets clipped to the start's block",
                         "rigid_pair"),
    "last_free":        ("last_free", "last pattern not held fixed", "three_singletons"),
    "first_free":       ("first_free", "first pattern not held fixed", "anchor_at_zero"),
    "uniform_open":     ("uniform_open", "uniform over open candidates, not count-weighted",
                         "coupled_weights_matter"),
    "select_ge":        ("select_ge", ">= in the selection rule", "quarter_boundary"),
    "skip_single_draw": ("skip_single_draw", "no draw for a one-candidate list",
                         "single_candidate_draws"),
    "float_rule":       ("float_rule", "floating-point counts and comparison",
                         "float_share_trap_06"),
    "descending":       ("descending", "candidates walked in descending order",
                         "three_quarters"),
}


def make(name):
    flag = MUTANTS[name][0]
    v = adversary.Variant(**{flag: True})
    return fuzz.Impl(f"mutant:{name}", v.sample, v.count)


def reference():
    return fuzz.Impl("adversary", adversary.pattern_jitter, adversary.pattern_jitter_count)


def run(n_cases=150, seed=0, differential=True):
    """{mutant name: number of generated cases on which the fuzzer flags it}."""
    ref = reference() if differential else None
    return {name: len(fuzz.compare(make(name), ref, n_cases=n_cases, seed=seed))
            for name in MUTANTS}


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    for mode in (True, False):
        res = run(n_cases=n, differential=mode)
        label = "differential" if mode else "black-box checks only"
        print(f"--- {label}, {n} cases")
        for k, v in res.items():
            print(f"{k:18s} caught on {v:4d} cases")
