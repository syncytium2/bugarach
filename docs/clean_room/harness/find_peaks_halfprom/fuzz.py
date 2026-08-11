"""Seeded structured fuzzer for differential testing of find_peaks_halfprom.

Generates signals aimed at the spec's corner cases: piecewise ramps, values
quantized to a small grid (forcing exact ties and plateaus), inserted NaN
runs, occasional long flat runs, mixed magnitudes, and min_prominence
values including ones that EXACTLY equal a realized prominence.

API:
    compare(impl_a, impl_b, n_cases=500, seed=0) -> list of disagreement
        records (dicts with the full input, min_prominence, seed/case, and
        both outputs).

Standalone smoke test of a single implementation (invariants only):
    python3 fuzz.py [impl.py] [n_cases] [seed]
Differential mode from the command line:
    python3 fuzz.py impl_a.py impl_b.py [n_cases] [seed]
"""

import importlib.util
import json
import os
import sys

import numpy as np

TOL = 1e-9


# ----------------------------------------------------------------- generator

def _equal_peak_plateau_valleys(rng):
    """Equal-height peaks separated by flat valley runs — the discriminating
    shape for the rev-2 saddle rule (run collapse to leftmost index, ties
    between distinct runs to the nearest run). Valley levels frequently sit
    ABOVE ref so the half-prom edges clamp at the saddle position."""
    H = float(rng.choice([4.0, 5.0, 6.0, 8.0]))
    floor = float(rng.choice([0.0, 1.0, -2.0]))
    ref = (H + floor) / 2.0
    parts = [[floor] * int(rng.integers(1, 3))]
    n_peaks = int(rng.integers(2, 5))
    for i in range(n_peaks):
        parts.append([H] * int(rng.integers(1, 4)))     # peak plateau
        if i < n_peaks - 1:
            v = float(rng.choice([H - 1.0, H - 2.0, ref, floor + 1.0]))
            valley = [v] * int(rng.integers(1, 4))
            if rng.random() < 0.4:
                # two distinct equal-depth valley runs around a bump
                # (equal_valley_runs shape); bump == H adds another peak
                bump = float(rng.choice([v + 0.5, H]))
                valley = valley + [bump] + [v] * int(rng.integers(1, 4))
            parts.append(valley)
    parts.append([floor] * int(rng.integers(1, 3)))
    return np.concatenate([np.asarray(p, float) for p in parts])


def gen_case(rng):
    """Generate one (S, min_prominence) case from a numpy Generator."""
    u = rng.random()
    if u < 0.02:                                   # empty input
        return np.empty(0), _gen_gate(rng)
    if u < 0.04:                                   # all-NaN input
        return np.full(int(rng.integers(1, 7)), np.nan), _gen_gate(rng)
    if u < 0.30:                                   # rev-2 discriminating shape
        S = _equal_peak_plateau_valleys(rng)
        if rng.random() < 0.25:                    # occasionally split by NaN
            st = int(rng.integers(0, S.size))
            S[st:st + int(rng.integers(1, 3))] = np.nan
        return S, _gen_gate(rng)
    if u < 0.34:                                   # tiny segments
        n = int(rng.integers(1, 5))
    else:
        n = int(rng.integers(2, 81))

    # Piecewise linear ramps between random breakpoints.
    k = min(n, int(rng.integers(2, max(3, n // 3) + 2)))
    xs = np.sort(rng.choice(np.arange(n), size=k, replace=False)).astype(float)
    if xs[0] != 0:
        xs = np.concatenate([[0.0], xs])
    if xs[-1] != n - 1:
        xs = np.concatenate([xs, [float(n - 1)]])
    ys = rng.uniform(-6.0, 8.0, size=xs.size)
    S = np.interp(np.arange(n, dtype=float), xs, ys)

    # Occasional long flat runs (plateaus, possibly at segment edges).
    if rng.random() < 0.4:
        for _ in range(int(rng.integers(1, 3))):
            ln = int(rng.integers(2, max(3, n // 2) + 1))
            st = int(rng.integers(0, n))
            S[st:st + ln] = S[st]

    # Quantize to a small grid to force exact ties / equal-height peaks /
    # plateau-shaped saddles / ref hitting samples exactly.
    if rng.random() < 0.6:
        grid = float(rng.choice([1.0, 0.5, 2.0]))
        S = np.round(S / grid) * grid

    # Mixed magnitudes on a slice.
    if rng.random() < 0.2:
        st = int(rng.integers(0, n))
        ln = int(rng.integers(1, n + 1))
        S[st:st + ln] = S[st:st + ln] * 10.0 ** int(rng.integers(-3, 4))

    # Occasionally go negative everywhere.
    if rng.random() < 0.1:
        S = S - float(rng.uniform(5.0, 20.0))

    # Insert NaN runs (segment boundaries; may touch plateaus/edges).
    if rng.random() < 0.5:
        for _ in range(int(rng.integers(1, 4))):
            ln = int(rng.integers(1, 6))
            st = int(rng.integers(0, n))
            S[st:st + ln] = np.nan

    return S, _gen_gate(rng)


def _gen_gate(rng):
    v = rng.random()
    if v < 0.4:
        return 0.0
    if v < 0.7:
        # Grid-aligned gates: with quantized signals these frequently equal
        # a realized prominence EXACTLY (inclusive-gate stress).
        return float(rng.choice([0.5, 1.0, 2.0, 3.0, 4.0]))
    return float(np.round(rng.uniform(0.0, 6.0), 2))


# ------------------------------------------------------------- serialization

def _sig_to_json(S):
    return [None if np.isnan(v) else float(v) for v in np.asarray(S, float)]


def _out_to_json(out):
    idx, prom, lx, rx = out
    return {"idx": [int(v) for v in idx],
            "prominence": [float(v) for v in prom],
            "left_x": [float(v) for v in lx],
            "right_x": [float(v) for v in rx]}


# --------------------------------------------------------------- comparison

def _run(impl, S, gate):
    try:
        return impl(S, gate), None
    except Exception as exc:            # noqa: BLE001 - report, don't crash
        return None, "%s: %s" % (type(exc).__name__, exc)


def _diff_record(impl_a, impl_b, S, gate, seed, case):
    out_a, err_a = _run(impl_a, S, gate)
    out_b, err_b = _run(impl_b, S, gate)
    reasons = []
    if err_a or err_b:
        reasons.append("exception a=%s b=%s" % (err_a, err_b))
    else:
        ia = list(out_a[0])
        ib = list(out_b[0])
        if ia != ib:
            reasons.append("idx mismatch")
        else:
            for name, a, b in (("prominence", out_a[1], out_b[1]),
                               ("left_x", out_a[2], out_b[2]),
                               ("right_x", out_a[3], out_b[3])):
                a = np.asarray(a, float)
                b = np.asarray(b, float)
                if a.shape != b.shape:
                    reasons.append("%s shape mismatch" % name)
                elif a.size and not np.all(np.abs(a - b) <= TOL):
                    reasons.append("%s mismatch" % name)
    if not reasons:
        return None
    return {"seed": seed,
            "case": case,
            "S": _sig_to_json(S),
            "min_prominence": float(gate),
            "reason": "; ".join(reasons),
            "output_a": _out_to_json(out_a) if out_a is not None else err_a,
            "output_b": _out_to_json(out_b) if out_b is not None else err_b}


def compare(impl_a, impl_b, n_cases=500, seed=0):
    """Run both implementations on n_cases generated inputs.

    Returns a list of disagreement records (empty list = full agreement).
    idx is compared exactly; the float arrays at absolute tolerance 1e-9.
    """
    disagreements = []
    for case in range(n_cases):
        rng = np.random.default_rng([seed, case])
        S, gate = gen_case(rng)
        subcases = [(S, gate)]
        # Extra subcase: a gate EXACTLY equal to a realized prominence
        # (harvested from impl_a at gate 0 — input generation only).
        out0, err0 = _run(impl_a, S, 0.0)
        if err0 is None and len(out0[1]) and rng.random() < 0.5:
            exact = float(out0[1][int(rng.integers(0, len(out0[1])))])
            subcases.append((S, exact))
        for S_, g_ in subcases:
            rec = _diff_record(impl_a, impl_b, S_, g_, seed, case)
            if rec is not None:
                disagreements.append(rec)
    return disagreements


# ------------------------------------------------------------- smoke testing

def check_invariants(impl, S, gate):
    """Return a list of invariant-violation strings for one case."""
    errs = []
    out, err = _run(impl, S, gate)
    if err is not None:
        return ["exception: " + err]
    idx, prom, lx, rx = out
    idx = np.asarray(idx)
    if not np.issubdtype(idx.dtype, np.integer):
        errs.append("idx dtype not integer: %s" % idx.dtype)
    if not (len(idx) == len(prom) == len(lx) == len(rx)):
        errs.append("array length mismatch")
        return errs
    if idx.size:
        if np.any(np.diff(idx) <= 0):
            errs.append("idx not strictly ascending: %s" % list(idx))
        if np.any(idx < 0) or np.any(idx >= len(S)):
            errs.append("idx out of range")
        elif np.any(np.isnan(np.asarray(S, float)[idx])):
            errs.append("peak index lands on NaN")
    for name, a in (("prominence", prom), ("left_x", lx), ("right_x", rx)):
        a = np.asarray(a, float)
        if a.size and not np.all(np.isfinite(a)):
            errs.append("%s not all finite" % name)
    if idx.size:
        if np.any(np.asarray(lx, float) > idx):
            errs.append("left_x > idx")
        if np.any(np.asarray(rx, float) < idx):
            errs.append("right_x < idx")
        if np.any(np.asarray(prom, float) < gate):
            errs.append("prominence below min_prominence gate")
    return errs


def smoke(impl, n_cases=500, seed=0, verbose=True):
    failures = []
    for case in range(n_cases):
        rng = np.random.default_rng([seed, case])
        S, gate = gen_case(rng)
        errs = check_invariants(impl, S, gate)
        if errs:
            failures.append({"seed": seed, "case": case,
                             "S": _sig_to_json(S),
                             "min_prominence": float(gate),
                             "errors": errs})
    if verbose:
        print("smoke: %d/%d cases pass invariants (seed=%d)"
              % (n_cases - len(failures), n_cases, seed))
        for f in failures[:10]:
            print(json.dumps(f, indent=1))
    return failures


# ------------------------------------------------------------------ CLI glue

def _load_impl(path):
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location(
        os.path.splitext(os.path.basename(path))[0] + "_fuzzmod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.find_peaks_halfprom


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    paths = [a for a in argv if a.endswith(".py")]
    nums = [int(a) for a in argv if not a.endswith(".py")]
    n_cases = nums[0] if len(nums) > 0 else 500
    seed = nums[1] if len(nums) > 1 else 0

    if len(paths) >= 2:                            # differential mode
        impl_a = _load_impl(paths[0])
        impl_b = _load_impl(paths[1])
        recs = compare(impl_a, impl_b, n_cases=n_cases, seed=seed)
        print("compare: %d disagreement(s) over %d cases (seed=%d)"
              % (len(recs), n_cases, seed))
        for r in recs[:10]:
            print(json.dumps(r, indent=1))
        return 1 if recs else 0

    impl = _load_impl(paths[0] if paths
                      else os.path.join(here, "adversary_impl.py"))
    failures = smoke(impl, n_cases=n_cases, seed=seed)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
