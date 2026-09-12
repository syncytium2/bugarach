#!/usr/bin/env python3
"""Stage 4 of the surrogate probe: can the per-ROI discriminator tier answer at all?

The plan calls this tier **required**. In the 2026-09-11 run it was **void on the whole
fast stream**: its own negative control — real against real — flagged, so not one accuracy
it reported supported any claim about any candidate. And it was underpowered by arithmetic
that needed no data at all: at alpha 0.05 and the plan's 55% forced-choice effect the test
needs 654 pairs for its declared 0.8 power, while the windows in play supplied 543 (power
0.73). Both facts were knowable before a single draw was generated.

So this runs **only the two controls** — uniform dither, which must be detected, and real
against real, which must not be — and it refuses before spending anything when the pairs
available cannot reach the declared power. Nothing here scores a candidate; the point is to
find out whether the instrument can speak before the grid is asked to listen.

It exists as its own tool because the discriminator is not wired into
``build_surrogate_screen.py``, which is why the 2026-09-11 run drove it from scratch scripts
outside the git tree (``run_notes.json`` records that as debt).
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

from bugarach import surrogate_discriminator as sd
from bugarach import surrogate_stats as ss

TOOLS = Path(__file__).resolve().parent
OUT_DIRNAME = "probe-surrogate-screen"


def _screen_tool():
    """The grid tool, imported by path, for its canonical parameter rule.

    ``params_for`` is the one place that converts a cell into adapter parameters — J in
    seconds against each recording's own frame interval, and which generators take which
    arguments. Reimplementing "uniform dither takes J" here would be a second rule to keep
    in step, which is the defect the reuse auditor exists to catch.
    """
    spec = importlib.util.spec_from_file_location(
        "_bss_for_probe", TOOLS / "build_surrogate_screen.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_bss_for_probe"] = mod
    spec.loader.exec_module(mod)
    return mod


def analysis_windows(rec) -> list[tuple[int, int]]:
    """Whole 60-second analysis windows inside one recording's generation window.

    The frame count comes from the recording's own ``dt``, so two recordings at different
    frame intervals get windows of the same duration rather than the same frame count. A
    trailing part-window is dropped: a shorter window has systematically fewer onsets, and
    the discriminator's features are counts.
    """
    aw = max(1, int(np.floor(ss.ANALYSIS_WINDOW_SEC / rec.dt + 0.5)))
    lo, hi = int(rec.window[0]), int(rec.window[1])
    return [(s, s + aw) for s in range(lo, hi - aw + 1, aw)]


def build_pairs(recs, name: str, cell: dict, params_for) -> dict:
    """One (real window, same window of its surrogate) pair per analysis window.

    Returns the feature matrices and the per-pair bookkeeping the controls need. The
    surrogate is drawn once per recording — a single draw is all a control needs, and the
    draw is seeded by recording and cell, so this is reproducible.
    """
    draws = ss.draw_surrogates(name, recs, 1, cell["id"],
                               lambda r: params_for(cell, r.dt), min_K=1,
                               measure_memory=False)
    real, surr, windows, mice, rec_ids, bands = [], [], [], [], [], []
    for rec in recs:
        got = draws.trains.get(rec.recording_id) or []
        if not got:
            continue
        sur_trains = got[0]
        band = max(1.0, np.floor(sd.EDGE_BAND_SECONDS / rec.dt + 0.5))
        for w in analysis_windows(rec):
            real.append(rec.trains)
            surr.append(sur_trains)
            windows.append(w)
            mice.append(rec.mouse)
            rec_ids.append(rec.recording_id)
            bands.append(band)
    if not windows:
        return {"n_pairs": 0}
    Xr, Xs = sd.pair_features(real, surr, windows, np.asarray(bands, dtype=float))
    return {"n_pairs": len(windows), "Xr": Xr, "Xs": Xs, "mice": mice,
            "recording_ids": rec_ids, "n_mice": len(set(map(str, mice))),
            "stopped": draws.stopped}


def _as_dict(res) -> dict | None:
    if res is None:
        return None
    try:
        return {k: v for k, v in dataclasses.asdict(res).items()
                if not isinstance(v, (np.ndarray, list, dict))}
    except TypeError:                                        # not a dataclass
        return {k: v for k, v in vars(res).items()
                if not isinstance(v, (np.ndarray, list, dict))}


def run_stream(recs, stream: str, cell: dict, params_for, *, n_permutations: int,
               seed: int, allow_underpowered: bool) -> dict:
    """The two controls on one stream, feasibility first."""
    need = sd.required_pairs()
    built = build_pairs(recs, cell["name"], cell, params_for)
    n = built.get("n_pairs", 0)
    power = float(sd.binomial_power(n)) if n else 0.0
    out = {"stream": stream, "n_pairs": n, "n_recordings": len(recs),
           "n_mice": built.get("n_mice", 0), "pairs_needed": need,
           "power_at_n": power, "declared_power": sd.POWER,
           "min_effect": sd.MIN_EFFECT, "alpha": sd.ALPHA,
           "positive_control": None, "negative_control": None, "verdict": ""}
    if n == 0:
        out["verdict"] = "no analysis window fits inside any generation window"
        return out
    if power < sd.POWER and not allow_underpowered:
        out["verdict"] = (
            f"underpowered by arithmetic: {n} pairs give power {power:.2f} against the "
            f"declared {sd.POWER}; {need} pairs are needed at a {sd.MIN_EFFECT} effect. "
            f"No control was run.")
        return out
    # Uniform dither is the positive control and must be detected; real against real is
    # the negative and must not be. A tier whose negative control flags cannot be read at
    # all — which is what voided every fast-stream accuracy on 2026-09-11.
    pos = sd.forced_choice(built["Xr"], built["Xs"], built["mice"],
                           n_permutations=n_permutations, seed=seed)
    Xa, Xb, neg_mice = sd.negative_control_pairs(
        built["Xr"], built["recording_ids"], built["mice"], seed=seed)
    neg = None
    if len(set(map(str, neg_mice))) >= 2 and len(neg_mice) > 0:
        neg = sd.forced_choice(Xa, Xb, neg_mice, n_permutations=n_permutations, seed=seed)
    out["positive_control"] = _as_dict(pos)
    out["negative_control"] = _as_dict(neg)
    pos_ok = bool(getattr(pos, "significant", False))
    neg_flagged = bool(getattr(neg, "significant", False)) if neg is not None else None
    out["positive_detected"] = pos_ok
    out["negative_flagged"] = neg_flagged
    if neg is None:
        out["verdict"] = ("no negative control: fewer than two mice have two windows of "
                          "one recording to pair")
    elif neg_flagged:
        out["verdict"] = ("UNUSABLE — the negative control flags, so real windows of one "
                          "recording are separable from each other and no accuracy on "
                          "this stream means anything")
    elif not pos_ok:
        out["verdict"] = ("UNUSABLE — the known-bad positive control was not detected, so "
                          "the tier has no demonstrated power here")
    else:
        out["verdict"] = "usable: the positive control is detected and the negative is not"
    if power < sd.POWER:
        out["verdict"] += (f" (⚠ still underpowered: {n} pairs, power {power:.2f}, "
                           f"{need} needed — run with more windows before trusting a "
                           f"non-detection)")
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--role", help="export role from current_export.toml")
    src.add_argument("--dataset", help="an export folder")
    p.add_argument("--out", default=None,
                   help=f"output folder (default: darkroom()/{OUT_DIRNAME}/<role>)")
    p.add_argument("--streams", nargs="*", default=None)
    p.add_argument("--limit", type=int, default=None,
                   help="use only the first N recordings")
    p.add_argument("--J-sec", type=float, default=None,
                   help="uniform dither radius in seconds (per recording's own dt)")
    p.add_argument("--J-frames", type=float, default=None,
                   help="uniform dither radius in whole frames")
    p.add_argument("--n-permutations", type=int, default=199)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--allow-underpowered", action="store_true",
                   help="run the controls even when the pairs available cannot reach the "
                        "declared power (the refusal is the point; this is for probes)")
    args = p.parse_args(argv)

    from bugarach import dataset
    from bugarach.io import load_folder

    if args.J_sec is None and args.J_frames is None:
        print("error: pass --J-sec or --J-frames for the positive control's dither radius",
              file=sys.stderr)
        return 2
    if args.role:
        folder, role = dataset.current(args.role), args.role
    else:
        folder, role = Path(args.dataset), Path(args.dataset).name
    if args.out:
        out = Path(args.out)
    else:
        from bugarach.paths import darkroom, unresolved_message
        root = darkroom()
        if root is None:
            print(unresolved_message("--out DIR"), file=sys.stderr)
            return 1
        out = Path(root) / "bugarach" / OUT_DIRNAME / role
    out.mkdir(parents=True, exist_ok=True)
    print(f"discriminator probe: {role} -> {out}")

    bss = _screen_tool()
    slices = load_folder(folder)
    if args.limit:
        slices = slices[: args.limit]
    names = sorted({n for s in slices for n in s.streams})
    report = {"role": role, "folder": str(folder),
              "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
              "J_sec": args.J_sec, "J_frames": args.J_frames,
              "n_permutations": args.n_permutations, "streams": {}}
    unusable = 0
    for stream in (args.streams or names):
        recs, skipped = ss.recordings_from_slices(slices, stream)
        if not recs:
            print(f"  {stream}: no recording carries it ({len(skipped)} skipped)")
            continue
        J = args.J_frames if args.J_frames is not None else args.J_sec
        unit = "frames" if args.J_frames is not None else "sec"
        cell = {"id": f"probe_ud__{stream}", "name": "uniform_dither",
                "J": J, "J_unit": unit, "f": None}
        res = run_stream(recs, stream, cell, bss.params_for,
                         n_permutations=args.n_permutations, seed=args.seed,
                         allow_underpowered=args.allow_underpowered)
        report["streams"][stream] = res
        print(f"  {stream}: {res['n_pairs']} pairs from {res['n_recordings']} recordings, "
              f"power {res['power_at_n']:.2f} (needs {res['pairs_needed']} for "
              f"{res['declared_power']})")
        print(f"    {res['verdict']}")
        if "UNUSABLE" in res["verdict"] or "underpowered by arithmetic" in res["verdict"]:
            unusable += 1
    (out / "discriminator_probe.json").write_text(
        json.dumps(report, indent=1, default=str), encoding="utf-8")
    print(f"wrote {out / 'discriminator_probe.json'}")
    return 1 if unusable else 0


if __name__ == "__main__":
    raise SystemExit(main())
