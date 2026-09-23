#!/usr/bin/env python3
"""Event frequency, participation, background rate and probe level, without defining an event.

    python tools/measure_coordination_rates.py --jobs 12 --out docs/learned/runs/<dated-name>

**Why.** The onset correlogram (``tools/measure_jitter_correlogram.py``) measures how tightly
cells fire together without deciding which onsets form an event. It cannot separate how
*often* cells fire together from how *many* join: its excess area is frequency × participation²,
so many small events and few large ones look the same. Tony, 2026-09-22: *"the correlogram gives
us the width of the event. how do we get the frequency and participation"* — and then the
background levels (quiet, busy) and the probe.

**The statistic.** Slide a window of ``w`` seconds along the recording and count how many onsets
fall in it, over all cells (the population count *X*). Its **factorial cumulants** are

* ``f2 = E[X(X-1)] - E[X]²`` — pairs of onsets in one window beyond chance,
* ``f3 = E[X(X-1)(X-2)] - 3 E[X(X-1)] E[X] + 2 E[X]³`` — triples beyond chance.

Cells firing independently at constant rates put **exactly zero** in both, whatever their rates;
only firing that is shared adds to them. If shared moments happen at rate λ and each of *N* cells
joins one with probability *p*, then per window ``f2 = λ w N(N-1) p²`` and
``f3 = λ w N(N-1)(N-2) p³``. So ``p = f3 / ((N-2) f2)``, then λ, then each cell's **coordinated
share** of its own rate, λp. Staude, Rotter & Grün (2010, *J Comput Neurosci* 29:327) use the same
cumulant route; the multiple-interaction model is Kuhn, Aertsen & Rotter (2003, *Neural Comput*
15:67).

**Slow shared drift is not coordination and also adds to both terms.** So each recording is
compared with surrogates that shift every cell's train circularly by its own offset, every two
cells at least two windows apart (:func:`shifted`); fine timing does not survive, shared
modulation slower than the offsets' span (about a minute at the primary 1 s window) does, and the
surrogate's cumulants are subtracted. Shared modulation faster than that span is counted as
coordination — on the fast stream the correlogram's 5–10 s level is small beside its peak.

**How many cells join a moment needs a model** (:func:`solve`): pairs and triples fix
λ·E[k(k-1)] and λ·E[k(k-1)(k-2)], not E[k], because a moment joined by one cell looks like
background. Two are reported and bracket it: ``fixed`` (every moment the same size, as the bench
plants them) and ``binomial`` (each cell joins independently).

**What it reports, per stream (fast, slow, combined), at windows of 1, 2 and 4 s.**

* participants per moment, moments per minute and each cell's coordinated share, per model.
  Report only: the bench plants a fixed participant count at three levels with a 120 s spacing
  floor (Tony's rulings, ``docs/handoffs/2026-09-22-overnight.md``).
* **quiet / busy**: the 25th / 75th percentile over recordings of the slice-mean per-cell rate —
  raw (what ``tools/remeasure_bench.py`` measures, so it reproduces ``bench.REGIMES``) and
  **background** (raw minus the coordinated share). **Both are taken over the recordings that
  clear ``fit_background_shape``'s floors** (:func:`shape_usable`), because that is the set
  ``remeasure_bench`` used to set ``bench.REGIMES`` — otherwise the comparison is between two
  recording sets and the difference reads as a measurement. The all-recordings pair is reported
  beside it as ``*_all_recordings``. Corrected 2026-09-22, after the first run compared the two
  sets: quiet appeared to fall 30% while busy agreed to 2%, which is the signature of the cut
  and not of coordination.
* **probe**: every 300 s stretch of every baseline window, slice-mean per-cell rate, 99th
  percentile over all stretches — raw and background — and the percentile the bench's current
  ``hot_rate_hz`` sits at.

**Calibration is the test.** The same estimator runs on each bench's simulated recordings, where
every planted event's participants are known. It passes when the coordinated share per cell is
recovered within ``CAL_TOL`` (median relative error over recordings). The record says whether it
passed; nothing here edits the bench. **The calibration recordings carry no elevated-rate
stretch** — a joint rise in rate reads as coordination to this statistic and the surrogates
cannot subtract it, so including the probe would measure that rather than event recovery. The
numbers behind that, and the over-subtraction it admits on real busy stretches, are in
:data:`CAL_NO_PROBE`.

**Combined** is ``bugarach.combined``: every fast and slow onset of a cell as one stream, nothing
deduplicated (Tony, 2026-09-22), calibrated on ``bench_combined`` at that bench's own jitter. Until
2026-09-23 this tool dropped a slow onset within a frame of a fast one; that assumption is gone,
so the first run's combined rows are not comparable with later ones. A fast and a slow onset in
the same frame still count as one active frame for that cell, as any two onsets would.

**What it reads.** The default dataset (``dataset.default()``), each recording's baseline analysis
window (``assess_folder.generation_window``, ``bench.MIN_BASELINE_SEC`` floor), ``t50rise`` onsets.
Baseline only (FOUNDATIONS §9).
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

DT = 0.1                    # s, one frame
WINDOWS = (1.0, 2.0, 4.0)   # s; the answer should not depend on w once w is well above the jitter
PRIMARY_W = 1.0
N_SURR = 20
STRETCH_SEC = 300.0         # the probe's length on both benches
STRETCH_STEP = 30.0
PROBE_PCT = 99.0
CAL_TOL = 0.25
SIM_SEEDS = tuple(range(1, 25))
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
CAL_JITTER = {"bugarach.bench": 0.106, "bugarach.bench_slow": 0.135}
"""The jitter the calibration plants: the correlogram's measured values, adopted by Tony on
2026-09-22. Fixed here rather than read from the bench, so the calibration means the same thing
whether it runs before or after the bench's constants move. The combined bench has no entry and
plants its own ``jitter_sec``, which the correlogram sets before this runs (bench_combined's route)."""


# ---------------------------------------------------------------- the estimator (pure)

def factorial_cumulants(X) -> tuple[float, float]:
    """(f2, f3) of a sample of counts. Zero in expectation for independent Poisson counts."""
    X = np.asarray(X, float)
    m1 = X.mean()
    m2 = (X * (X - 1)).mean()
    m3 = (X * (X - 1) * (X - 2)).mean()
    return float(m2 - m1 ** 2), float(m3 - 3 * m2 * m1 + 2 * m1 ** 3)


def population_cumulants(trains, L: int, wf: int) -> tuple[float, float]:
    """(f2, f3) of the population count in windows of ``wf`` frames, averaged over two offsets.

    ``trains`` holds each cell's onset frames in [0, L). Two offsets (0 and half a window) halve
    the share of shared moments split by a window edge."""
    allf = np.concatenate([np.asarray(t, int) for t in trains]) if trains else np.zeros(0, int)
    out = []
    for off in (0, wf // 2):
        n = (L - off) // wf
        if n < 2:
            continue
        f = allf[(allf >= off) & (allf < off + n * wf)] - off
        X = np.bincount(f // wf, minlength=n)[:n]
        out.append(factorial_cumulants(X))
    return tuple(float(v) for v in np.mean(out, axis=0))


def shifted(trains, L: int, spacing: int, rng) -> list[np.ndarray]:
    """Each cell's train moved circularly by its own offset, **every two cells at least
    ``spacing`` frames apart**: a random permutation of multiples of ``spacing``, centred.

    **Why distinct offsets.** A surrogate is subtracted to remove what is not fine-timed sharing;
    if two cells of one event are moved by similar amounts they stay together and the surrogate
    subtracts real signal. Independent shifts of up to ±5 s lost 35% of the planted pairs on the
    bench (2026-09-22); a minimum shift alone still lost 36%, because cells shifted the same way
    stay together. Distinct offsets recovered 0.98 of them at a 1 s window. The cost: offsets span ``N × spacing``, so only
    shared modulation slower than that survives into the surrogate (about a minute at 1 s windows
    and 33 cells)."""
    N = len(trains)
    offs = rng.permutation(N) * spacing + rng.randint(0, spacing)
    offs = offs - offs.mean().astype(int)
    return [(np.asarray(t, int) + int(d)) % L for t, d in zip(trains, offs)]


def excess_cumulants(trains, L: int, wf: int, n_surr: int, rng):
    """Real (f2, f3) minus the mean over shift surrogates (cells ≥ 2 windows apart)."""
    f2, f3 = population_cumulants(trains, L, wf)
    s = np.array([population_cumulants(shifted(trains, L, 2 * wf, rng), L, wf)
                  for _ in range(n_surr)])
    return f2 - s[:, 0].mean(), f3 - s[:, 1].mean()


def solve(f2: float, f3: float, N: int, w: float, model: str = "fixed") -> dict:
    """Participants per shared moment, its rate λ (per s), and the coordinated share per cell.

    Pairs and triples fix only ``λ·E[k(k-1)]`` and ``λ·E[k(k-1)(k-2)]``, where *k* is how many
    cells join a moment. The mean *k*, and so the share of onsets that are coordinated, needs an
    assumption about how *k* varies, because a moment joined by one cell looks like background.
    Two are reported, and they bracket the answer:

    * ``"fixed"`` — every moment has the same *k*: ``k = f3/f2 + 2``. This is how the bench plants
      events (three fixed levels), so it is the one the bench calibration tests.
    * ``"binomial"`` — each cell joins independently with probability *p*: ``p = f3/((N-2)f2)``,
      mean ``k = Np`` (the multiple-interaction model).
    """
    nan = dict(k=float("nan"), lam=float("nan"), share=float("nan"))
    if N < 3 or not (f2 > 0) or not (f3 > 0):
        return nan
    r = f3 / f2
    if model == "fixed":
        k = r + 2
        lam = f2 / (w * k * (k - 1))
    elif model == "binomial":
        p = r / (N - 2)
        k = N * p
        lam = f2 / (w * N * (N - 1) * p * p)
    else:
        raise ValueError(model)
    return dict(k=float(k), lam=float(lam), share=float(lam * k / N))


def stretch_rates(trains, L: int, stretch: int, step: int) -> np.ndarray:
    """Slice-mean per-cell rate (per s) in every ``stretch``-frame stretch, stepping by ``step``."""
    N = len(trains)
    if N == 0 or L < stretch:
        return np.zeros(0)
    counts = np.zeros(L, int)
    for t in trains:
        np.add.at(counts, np.asarray(t, int), 1)
    c = np.concatenate([[0], np.cumsum(counts)])
    starts = np.arange(0, L - stretch + 1, step)
    return (c[starts + stretch] - c[starts]) / (N * stretch * DT)


def shape_usable(n_roi: int, n_events: float, duration_sec: float) -> bool:
    """``fit_background_shape``'s floors — the ones that decide the bench's own recording set.

    ``tools/remeasure_bench.py`` computes ``regime_quiet_hz`` / ``regime_busy_hz``, which is
    where ``bench.REGIMES`` came from, over ``[r for r in recs if r["shape_usable"]]`` only.
    Measuring quiet/busy here over ALL recordings and comparing against that number compares
    two different recording sets and reports the difference as though it were a measurement.

    It is not a small effect, and the signature gives it away: the floors cut short, sparse and
    few-ROI windows, which are the quiet tail, so **quiet moves and busy barely does**.
    """
    import fit_background_shape as fb

    return bool(duration_sec >= fb.MIN_DURATION_SEC and n_events >= fb.MIN_EVENTS
                and n_roi >= fb.MIN_ROIS)


def measure(trains, L: int, rng, windows=WINDOWS, n_surr=N_SURR) -> dict:
    """Everything one recording contributes. ``trains`` in frames, window ``L`` frames long."""
    N = len(trains)
    T = L * DT
    counts = np.array([len(t) for t in trains], float)
    out = dict(N=N, T=T, rate=float(counts.mean() / T) if N else float("nan"),
               shape_usable=shape_usable(N, float(counts.sum()), T), cum={})
    for w in windows:
        f2, f3 = excess_cumulants(trains, L, int(round(w / DT)), n_surr, rng)
        out["cum"][str(w)] = dict(f2=f2, f3=f3, n_win=L // int(round(w / DT)))
    out["stretches"] = stretch_rates(trains, L, int(round(STRETCH_SEC / DT)),
                                     int(round(STRETCH_STEP / DT))).tolist()
    return out


MODELS = ("fixed", "binomial")

CAL_NO_PROBE = """Why the calibration plants no elevated-rate stretch, and what that admits.

Found 2026-09-22, when the probe moved to the measured 99th percentile and the fast
calibration went from passing to failing by 1.7x the tolerance. It was the probe, not the
backgrounds. Fast bench, fixed model, 1 s window:

    old backgrounds + old 0.06 Hz probe      share +6%   pass
    new backgrounds + old 0.06 Hz probe      share +2%   pass
    new backgrounds + new 0.127 Hz probe     share +43%  FAIL  (moment rate +39%)
    new backgrounds + no probe stretch       share -16%  pass

**The mechanism is a limit of the estimator, not a defect in the constants.** Every cell
lifts to 0.127 Hz across the same 300 s, and a joint rise in rate is indistinguishable from
many shared moments to a statistic built on factorial cumulants of the population count.
The surrogates cannot subtract it either: per-cell circular shifts move each train
independently, so they break the joint rise up rather than preserving it.

So the probe stretch was making the calibration measure the estimator's response to a
correlated rate change, which is not what it exists to check. It is removed here, and the
backgrounds it validates were measured and calibrated before the probe ever moved.

⚠ **What this admits, and it belongs with the adopted numbers:** on real recordings the same
effect runs. A baseline window containing a stretch where the whole field is busier will
have some of that rise counted as coordination and subtracted, so the background rates may
be **slightly over-subtracted**. The measured probe percentile bounds how much — the
coordinated share at the fast probe is 0.6% of the rate, so on that stream the effect is
small; on slow, where the share at the probe is 35.9%, it is not obviously small and is the
first thing to re-check if the slow bench behaves oddly."""

#: The model whose coordinated share the bench adopts, named once so the record and
#: `tools/remeasure_bench.py` cannot disagree about which of the two brackets was used.
#: ``fixed`` because that is how the bench plants events — a fixed participant count at
#: each level — so it is the bracket that matches the thing being subtracted from.
ADOPTED_MODEL = "fixed"


def pooled_ratio(recs, w: float, model: str) -> float:
    """f3/f2 pooled over recordings, each weighted by its number of windows.

    ``fixed``: Σ f3·n / Σ f2·n, which is k-2. ``binomial``: Σ f3·n / Σ (N-2)·f2·n, which is p."""
    num = sum(r["cum"][str(w)]["f3"] * r["cum"][str(w)]["n_win"] for r in recs)
    den = sum((r["N"] - 2 if model == "binomial" else 1) * r["cum"][str(w)]["f2"]
              * r["cum"][str(w)]["n_win"] for r in recs)
    return float(num / den) if den > 0 and num > 0 else float("nan")


def per_recording(recs, w: float, model: str) -> list[dict]:
    """Each recording's k, λ and share, with the f3/f2 ratio pooled (one recording's f3 is noisy)."""
    q = pooled_ratio(recs, w, model)
    out = []
    for r in recs:
        f2, N = r["cum"][str(w)]["f2"], r["N"]
        if not (np.isfinite(q) and q > 0 and N > 2):
            out.append(dict(k=float("nan"), lam=float("nan"), share=float("nan")))
            continue
        k = q + 2 if model == "fixed" else N * q
        pairs = k * (k - 1) if model == "fixed" else N * (N - 1) * q * q
        lam = f2 / (w * pairs)
        out.append(dict(k=float(k), lam=float(lam), share=float(lam * k / N)))
    return out


def summarize(recs, w: float = PRIMARY_W, probe_now: float | None = None) -> dict:
    """The reported numbers from per-recording measurements, at window ``w``, under both models."""
    raw = np.array([r["rate"] for r in recs])
    st_raw = np.concatenate([np.asarray(r["stretches"]) for r in recs]) if recs else np.zeros(0)
    # Quiet and busy are reported on the bench's OWN recording set, so that comparing them
    # against bench.REGIMES compares measurements and not two different sets of recordings.
    # The all-recordings pair is kept beside it, suffixed, because it is what the coordination
    # statistic itself saw.
    keep = np.array([bool(r.get("shape_usable", True)) for r in recs])
    raw_u = raw[keep] if keep.any() else raw
    out = dict(recordings=len(recs), window_sec=w, stretches=int(st_raw.size),
               recordings_shape_usable=int(keep.sum()),
               quiet_raw_hz=float(np.percentile(raw_u, 25)),
               busy_raw_hz=float(np.percentile(raw_u, 75)),
               quiet_raw_hz_all_recordings=float(np.percentile(raw, 25)),
               busy_raw_hz_all_recordings=float(np.percentile(raw, 75)),
               probe_raw_hz=float(np.percentile(st_raw, PROBE_PCT)) if st_raw.size else float("nan"))
    if probe_now is not None and st_raw.size:
        out["bench_probe_hz"] = probe_now
        out["bench_probe_percentile_raw"] = float((st_raw < probe_now).mean() * 100)
    for model in MODELS:
        pr = per_recording(recs, w, model)
        shares = np.array([x["share"] for x in pr])
        bg = raw - np.nan_to_num(shares)
        st_bg = (np.concatenate([np.asarray(r["stretches"]) - np.nan_to_num(s)
                                 for r, s in zip(recs, shares)]) if recs else np.zeros(0))
        out[model] = dict(
            participants_per_moment=float(np.nanmedian([x["k"] for x in pr])),
            participation=float(np.nanmedian([x["k"] / r["N"] for x, r in zip(pr, recs)])),
            shared_moments_per_min=float(np.nanmedian([x["lam"] for x in pr]) * 60),
            coordinated_share_hz=float(np.nanmedian(shares)),
            coordinated_share_of_rate=float(np.nanmedian(shares / raw)),
            quiet_background_hz=float(np.percentile(bg[keep] if keep.any() else bg, 25)),
            busy_background_hz=float(np.percentile(bg[keep] if keep.any() else bg, 75)),
            quiet_background_hz_all_recordings=float(np.percentile(bg, 25)),
            busy_background_hz_all_recordings=float(np.percentile(bg, 75)),
            probe_background_hz=(float(np.percentile(st_bg, PROBE_PCT)) if st_bg.size
                                 else float("nan")),
        )
    return out


# ---------------------------------------------------------------- real recordings

def _frames(v, lo, hi) -> np.ndarray:
    v = np.asarray(v, float)
    v = v[np.isfinite(v) & (v >= lo) & (v < hi)]
    return np.unique(np.round((v - lo) / DT).astype(int))


def _real(args):
    folder, i, seed = args
    from bugarach.assess_folder import NoBaselineRegion, generation_window
    from bugarach.bench import MIN_BASELINE_SEC
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    try:
        w, _ = generation_window(s)
    except NoBaselineRegion:
        return None
    if w is None or w[1] - w[0] < MIN_BASELINE_SEC:
        return None
    dt = s.require_dt()
    assert abs(dt - DT) < 1e-9, f"{s.slice_id}: frame interval {dt}, this tool assumes {DT}"
    lo, hi = w
    L = int(round((hi - lo) / DT))
    from bugarach.combined import COMBINED, has_sources, stream_of

    trains = {}
    for stream in ("fast", "slow", COMBINED):
        if stream in s.streams or (stream == COMBINED and has_sources(s)):
            st = stream_of(s, stream)
            trains[stream] = [np.minimum(_frames(v, lo, hi), L - 1) for v in (st.t50rise or st.locs)]
    rng = np.random.RandomState(seed + i)
    return {"slice_id": s.slice_id,
            **{k: measure(v, L, rng) for k, v in trains.items()}}


# ---------------------------------------------------------------- calibration on the benches

def truth(gt, N: int, T: float) -> dict:
    """What the estimator should return on a simulated recording, from its planted events."""
    ks = np.array([len(e.rois) for e in list(gt.events) + list(gt.distractors)], float)
    if ks.size == 0:
        return dict(share=0.0, k=float("nan"), lam=0.0)
    return dict(share=float(ks.sum() / (N * T)), k=float(ks.mean()), lam=float(ks.size / T))


def _sim(args):
    bench_name, regime, seed = args
    import importlib

    b = importlib.import_module(bench_name)
    # No elevated-rate stretch. The calibration asks one question — are planted
    # coordinated events recovered at the background rates — and the probe stretch
    # answers a different one, whether a detector keys on rate. Leaving it in does not
    # make the test stricter, it makes it measure something else: see CAL_NO_PROBE.
    s, gt = b.make_recording(regime, seed,
                             jitter_sec=CAL_JITTER.get(
                                 bench_name, b.BENCH_RECORDING["jitter_sec"]),
                             hot_window=None, hot_rate_hz=0.0)
    T = float(gt.params["duration_sec"])
    L = int(round(T / DT))
    trains = [np.minimum(_frames(t, 0.0, T), L - 1) for t in s.streams[b.STREAM].t50rise]
    m = measure(trains, L, np.random.RandomState(seed))
    return m, truth(gt, len(trains), T)


def calibrate(results, w: float = PRIMARY_W, model: str = "fixed") -> dict:
    """How well ``model`` recovers what the bench planted: share, participants, rate."""
    recs = [m for m, _ in results]
    pr = per_recording(recs, w, model)
    rel = lambda a, b: a / b - 1 if b > 0 else float("nan")  # noqa: E731
    share_err = [rel(x["share"], t["share"]) for x, (_, t) in zip(pr, results)]
    k_err = [rel(x["k"], t["k"]) for x, (_, t) in zip(pr, results)]
    lam_err = [rel(x["lam"], t["lam"]) for x, (_, t) in zip(pr, results)]
    med = float(np.nanmedian(share_err)) if share_err else float("nan")
    return dict(window_sec=w, model=model, recordings=len(results),
                share_rel_error_median=med,
                participants_rel_error_median=float(np.nanmedian(k_err)),
                rate_rel_error_median=float(np.nanmedian(lam_err)),
                passed=bool(np.isfinite(med) and abs(med) <= CAL_TOL))


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20260922)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    import importlib

    from bugarach import dataset
    from bugarach.io import load_folder

    folder = dataset.default()
    n = len(load_folder(folder))
    rec = {"dataset": dataset.stamp(), "dt": DT, "windows_sec": list(WINDOWS),
           "primary_window_sec": PRIMARY_W, "surrogate": "per-cell circular offsets, all pairs >= 2 windows apart", "surrogates": N_SURR,
           "stretch_sec": STRETCH_SEC, "probe_percentile": PROBE_PCT, "cal_tolerance": CAL_TOL,
           "streams": {}, "calibration": {}}
    with ProcessPoolExecutor(a.jobs) as ex:
        real = [r for r in ex.map(_real, [(str(folder), i, a.seed) for i in range(n)]) if r]
        for stream in ("fast", "slow", "combined"):
            recs = [r[stream] for r in real if stream in r]
            probe_now = None
            if stream in BENCHES:
                probe_now = importlib.import_module(BENCHES[stream]).BENCH_RECORDING["hot_rate_hz"]
            # The per-recording coordinated share, at the primary window and the model
            # the bench adopts, so `tools/remeasure_bench.py` can subtract it per
            # recording and bootstrap the regimes honestly rather than being handed a
            # pooled number it cannot resample. Keyed by slice_id, which both tools
            # carry. `shape_usable` travels with it for the same reason: the regimes are
            # measured on fit_background_shape's set, and a consumer should not have to
            # re-derive which recordings those are.
            shares = per_recording(recs, PRIMARY_W, ADOPTED_MODEL)
            by_slice = {r["slice_id"]: s for r, s in zip(
                [x for x in real if stream in x], shares)}
            rec["streams"][stream] = {
                "by_window": {str(w): summarize(recs, w, probe_now) for w in WINDOWS},
                "adopted": {"window_sec": PRIMARY_W, "model": ADOPTED_MODEL},
                "per_recording": [{"slice_id": r["slice_id"], "N": r[stream]["N"],
                                   "rate_hz": r[stream]["rate"],
                                   "shape_usable": bool(r[stream].get("shape_usable", True)),
                                   "share_hz": (None if not np.isfinite(
                                       by_slice[r["slice_id"]]["share"])
                                       else float(by_slice[r["slice_id"]]["share"]))}
                                  for r in real if stream in r],
            }
            print(f"{stream}: {json.dumps(rec['streams'][stream]['by_window'][str(PRIMARY_W)])}",
                  flush=True)
        for stream, bench_name in BENCHES.items():
            jobs = [(bench_name, g, s) for g in ("baseline_quiet", "baseline_busy") for s in SIM_SEEDS]
            res = list(ex.map(_sim, jobs))
            rec["calibration"][stream] = {f"{m}@{w}": calibrate(res, w, m) for w in WINDOWS for m in MODELS}
            print(f"calibration {stream}: {json.dumps(rec['calibration'][stream][f'fixed@{PRIMARY_W}'])}",
                  flush=True)
    (a.out / "coordination_rates.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"wrote {a.out / 'coordination_rates.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
