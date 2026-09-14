#!/usr/bin/env python3
"""Is recording identity visible in our data, to a classifier that cannot see coordination?

    python tools/measure_recording_identity.py                 # steps_excluded, both streams
    python tools/measure_recording_identity.py --quick         # small run, for a smoke test

Design, gates and expectations are declared in ``docs/learned/recording_identity.md``,
committed before the first run. Two measurements, both with
:mod:`bugarach.surrogate_discriminator` unchanged, which reduces every ROI alone and pools
only by symmetric statistics, so cross-ROI timing is invisible to it:

- **chimera test** — each real 60 s baseline window against the same window with a share of
  its ROIs replaced by real trains from donors at four tiers (same recording at another time,
  same mouse, same group, other group). The gap between a tier and the same-recording tier is
  what where-the-donor-came-from costs, on its own.
- **window-pair test** — the ROI-swap plan's slice-identity stage as a forced choice: given an
  anchor window, which of two candidates is from the same recording?

Controls: real against real (must read chance), 30% thinning (must be detected). Intervals are
bootstraps over mice of the cross-validated per-pair correctness.

Output: ``results.json`` and ``recording_identity.png`` in the darkroom folder
``<darkroom>/bugarach/2026-09-13-recording-identity/`` by default; ``--also`` copies both into
the repo.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bugarach import dataset, io
from bugarach import surrogate_discriminator as sd
from bugarach.assess_folder import is_baseline

FIGURE_ID = "recording_identity"
OUT_DIRNAME = "2026-09-13-recording-identity"
WINDOW_SEC = 60.0
PAIR_GAP_SEC = 300.0
THIN_SHARE = 0.30
TIERS = ("self_other_time", "same_mouse", "same_group", "other_group")
PAIR_TIERS = ("same_mouse", "same_group", "other_group")
SWAP_SHARES = (0.5, 1.0)
GATE = 0.60
N_BOOT = 2000


def rng(*key) -> np.random.RandomState:
    return np.random.RandomState(zlib.crc32(repr(key).encode("utf-8")) & 0xFFFFFFFF)


@dataclass
class Rec:
    recording_id: str
    mouse: str
    group: str
    date: str
    dt: float
    window: tuple[int, int]          # baseline analysis window, frames, half-open
    trains: list[np.ndarray]         # int64 frames per ROI, inside ``window``

    def windows(self, aw: int) -> list[tuple[int, int]]:
        lo, hi = self.window
        return [(s, s + aw) for s in range(lo, hi - aw + 1, aw)]


def baseline_window_sec(s) -> tuple[float, float] | None:
    """The longest baseline region, with the producer's analysis window winning inside it —
    the rule ``assess_folder`` applies (and ``generation_window`` on the screen branch)."""
    base = [r for r in (s.regions or []) if is_baseline(r)]
    if not base:
        return None
    r = max(base, key=lambda r: r.end_sec - r.start_sec)
    if r.has_analysis_window:
        return float(r.analysis_start_sec), float(r.analysis_end_sec)
    return float(r.start_sec), float(r.end_sec)


def to_frames(t, dt: float) -> np.ndarray:
    x = np.asarray(t, dtype=float).ravel()
    x = x[np.isfinite(x)] / dt
    return np.sort((np.sign(x) * np.floor(np.abs(x) + 0.5)).astype(np.int64))


def load(folder, stream: str) -> tuple[list[Rec], list[tuple[str, str]]]:
    recs, skipped = [], []
    for s in io.load_folder(folder):
        w = baseline_window_sec(s)
        if w is None:
            skipped.append((s.slice_id, "no baseline region"))
            continue
        if stream not in s.streams or not s.has_dt:
            skipped.append((s.slice_id, f"no {stream} stream or no frame interval"))
            continue
        dt = float(s.dt)
        lo, hi = (int(v) for v in to_frames(w, dt))
        st = s.streams[stream]
        trains = []
        for v in (st.t50rise or st.locs):
            f = to_frames(v, dt)
            trains.append(f[(f >= lo) & (f < hi)])
        meta = s.meta or {}
        recs.append(Rec(s.slice_id, str(meta.get("subject_id") or s.slice_id),
                        str(meta.get("group_id") or ""), str(meta.get("date") or ""),
                        dt, (lo, hi), trains))
    return recs, skipped


def cut(train: np.ndarray, src: tuple[int, int], dst_start: int) -> np.ndarray:
    """The onsets of ``train`` inside ``src``, re-based so ``src[0]`` lands on ``dst_start``."""
    t = train[(train >= src[0]) & (train < src[1])]
    return t - src[0] + dst_start


def donor_pool(target: Rec, recs: list[Rec], tier: str) -> list[Rec]:
    if tier == "self_other_time":
        return [target]
    others = [r for r in recs if r.recording_id != target.recording_id and r.dt == target.dt]
    if tier == "same_mouse":
        return [r for r in others if r.mouse == target.mouse]
    if tier == "same_group":
        return [r for r in others if r.group == target.group and r.mouse != target.mouse]
    if tier == "other_group":
        return [r for r in others if r.group != target.group]
    raise ValueError(f"unknown tier {tier!r}")


def chimera(target: Rec, w: tuple[int, int], share: float, tier: str, recs: list[Rec],
            rs: np.random.RandomState) -> tuple[list[np.ndarray], dict] | None:
    """``target``'s trains in window ``w`` with ``round(share * N)`` ROIs replaced by donors.

    Every donor train is a real one-minute train of one donor ROI, from a random window of the
    donor's own baseline — never the target window itself when the donor is the target, so the
    same-recording tier always moves the train in time. Donor recordings rotate in a shuffled
    order, so none repeats until every one has been used. Returns ``None`` when the tier has no
    donor.
    """
    aw = w[1] - w[0]
    pool = donor_pool(target, recs, tier)
    if not pool:
        return None
    n = len(target.trains)
    k = int(round(share * n))
    replace = set(rs.choice(n, size=k, replace=False).tolist()) if k else set()
    order = rs.permutation(len(pool))
    per_donor: dict[str, int] = {}
    same_date = 0
    out = []
    j = 0
    for i in range(n):
        if i not in replace:
            out.append(cut(target.trains[i], w, w[0]))
            continue
        d = pool[order[j % len(pool)]]
        j += 1
        wins = [v for v in d.windows(aw) if not (d is target and v == w)]
        src = wins[rs.randint(len(wins))]
        roi = rs.randint(len(d.trains))
        out.append(cut(d.trains[roi], src, w[0]))
        per_donor[d.recording_id] = per_donor.get(d.recording_id, 0) + 1
        same_date += int(d.date == target.date)
    return out, {"max_rois_per_donor": max(per_donor.values(), default=0),
                 "n_donor_recordings": len(per_donor), "same_date": same_date, "replaced": k}


def thinned(trains: list[np.ndarray], w, rs) -> list[np.ndarray]:
    out = []
    for t in trains:
        t = cut(t, w, w[0])
        out.append(t[rs.random_sample(t.size) >= THIN_SHARE])
    return out


def cv_correct(Xr: np.ndarray, Xs: np.ndarray, mice, seed: int, l2: float = 1.0) -> np.ndarray:
    """Per-pair cross-validated correctness, exactly as ``forced_choice`` computes its accuracy."""
    folds = sd.mouse_folds(mice, 5, seed)
    scales = {int(f): sd._scale(np.vstack([Xr[folds != f], Xs[folds != f]]))
              for f in np.unique(folds)}
    correct, _ = sd._cv_correct(Xr - Xs, scales, folds, np.ones(len(mice)), l2)
    return correct


def mouse_bootstrap(values: np.ndarray, mice, seed, n_boot: int = N_BOOT) -> tuple[float, float]:
    """95% interval of the mean of ``values``, resampling mice with replacement."""
    mice = np.asarray([str(m) for m in mice])
    uniq, inv = np.unique(mice, return_inverse=True)
    sums = np.bincount(inv, weights=values)
    cnts = np.bincount(inv).astype(float)
    rs = rng("boot", seed)
    draws = rs.randint(uniq.size, size=(n_boot, uniq.size))
    means = sums[draws].sum(1) / cnts[draws].sum(1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def paired_bootstrap(a: np.ndarray, b: np.ndarray, mice, seed, n_boot: int = N_BOOT):
    """Interval of mean(a) - mean(b) over the same pairs, resampling mice."""
    return mouse_bootstrap(a - b, mice, ("paired", seed), n_boot)


def score(Xr, Xs, mice, seed, n_perm) -> dict:
    res = sd.forced_choice(Xr, Xs, mice, n_permutations=n_perm, seed=seed)
    correct = cv_correct(Xr, Xs, mice, seed)
    assert abs(correct.mean() - res.accuracy) < 1e-9, "per-pair correctness drifted from forced_choice"
    lo, hi = mouse_bootstrap(correct, mice, seed)
    return {"accuracy": res.accuracy, "ci": [lo, hi], "p_value": res.p_value,
            "n_pairs": res.n_pairs, "n_mice": res.n_mice, "top_features": res.top_features(),
            "_correct": correct}


def verdict(ci) -> str:
    if ci[1] < GATE:
        return "ADMISSIBLE"
    if ci[0] > GATE:
        return "NOT ADMISSIBLE"
    return "UNDECIDED"


def by_group(correct, groups, mice, seed) -> dict:
    out = {}
    groups = np.asarray(groups)
    mice = np.asarray(mice)
    for g in sorted(set(groups)):
        m = groups == g
        out[g] = {"accuracy": float(correct[m].mean()), "n_pairs": int(m.sum()),
                  "ci": list(mouse_bootstrap(correct[m], mice[m], (seed, g)))}
    return out


def run_stream(recs: list[Rec], stream: str, *, n_perm: int, max_windows: int | None) -> dict:
    aw = int(round(WINDOW_SEC / recs[0].dt))
    band = max(1.0, np.floor(sd.EDGE_BAND_SECONDS / recs[0].dt + 0.5))
    items = [(r, w) for r in recs for w in r.windows(aw)]
    if max_windows:
        pick = rng("subsample", stream).permutation(len(items))[:max_windows]
        items = [items[i] for i in sorted(pick)]
    mice = [r.mouse for r, _ in items]
    groups = [r.group for r, _ in items]
    seed = zlib.crc32(stream.encode()) & 0xFFFF
    Xr = np.array([sd.window_features(cut_all(r, w), w, band) for r, w in items])
    out: dict = {"stream": stream, "n_windows": len(items), "n_recordings": len(recs),
                 "n_mice": len(set(mice)), "controls": {}, "chimera": {}, "pairs": {}}

    # -- controls --
    rec_ids = [r.recording_id for r, _ in items]
    Xa, Xb, neg_mice = sd.negative_control_pairs(Xr, rec_ids, mice, seed=seed)
    neg = score(Xa, Xb, neg_mice, seed, n_perm)
    neg["passes"] = bool(neg["ci"][0] <= 0.5 <= neg["ci"][1])
    Xt = np.array([sd.window_features(thinned(r.trains, w, rng("thin", r.recording_id, w)), w, band)
                   for r, w in items])
    pos = score(Xr, Xt, mice, seed, n_perm)
    pos["passes"] = bool(pos["ci"][0] > 0.55)
    out["controls"] = {"real_vs_real": neg, "thinning": pos}
    out["void"] = not (neg["passes"] and pos["passes"])

    # -- chimera test --
    base_correct = {}
    for share in SWAP_SHARES:
        for tier in TIERS:
            rows, keep, info = [], [], []
            for idx, (r, w) in enumerate(items):
                got = chimera(r, w, share, tier, recs, rng("chimera", tier, share, r.recording_id, w))
                if got is None:
                    continue
                trains, meta = got
                rows.append(sd.window_features(trains, w, band))
                keep.append(idx)
                info.append(meta)
            keep = np.asarray(keep)
            res = score(Xr[keep], np.array(rows), [mice[i] for i in keep], seed, n_perm)
            res["verdict"] = verdict(res["ci"])
            res["n_targets_without_donor"] = len(items) - len(keep)
            res["max_rois_per_donor"] = int(max(m["max_rois_per_donor"] for m in info))
            res["share_same_date"] = float(sum(m["same_date"] for m in info) /
                                           max(1, sum(m["replaced"] for m in info)))
            res["by_group"] = by_group(res["_correct"], [groups[i] for i in keep],
                                       [mice[i] for i in keep], seed)
            res["_keep"] = keep
            if tier == "self_other_time":
                base_correct[share] = (keep, res["_correct"])
            else:
                bk, bc = base_correct[share]
                common, ia, ib = np.intersect1d(keep, bk, return_indices=True)
                lo, hi = paired_bootstrap(res["_correct"][ia], bc[ib], [mice[i] for i in common], seed)
                res["identity_cost"] = {"estimate": float(res["_correct"][ia].mean() - bc[ib].mean()),
                                        "ci": [lo, hi], "n_pairs": int(common.size)}
            out["chimera"][f"{tier}@{share}"] = res
            print(f"  {stream} chimera {tier:>15} k={share}: {res['accuracy']:.3f} "
                  f"[{res['ci'][0]:.3f}, {res['ci'][1]:.3f}] {res['verdict']}", flush=True)

    # -- window-pair test --
    gap = int(round(PAIR_GAP_SEC / recs[0].dt))
    for tier in PAIR_TIERS:
        A, S, D, pm = [], [], [], []
        for idx, (r, w) in enumerate(items):
            rs = rng("pair", tier, r.recording_id, w)
            same = [v for v in r.windows(aw) if abs(v[0] - w[0]) >= gap]
            pool = donor_pool(r, recs, tier)
            if not same or not pool:
                continue
            sw = same[rs.randint(len(same))]
            d = pool[rs.randint(len(pool))]
            dws = d.windows(aw)
            dw = dws[rs.randint(len(dws))]
            A.append(Xr[idx])
            S.append(sd.window_features(cut_all(r, sw), sw, band))
            D.append(sd.window_features(cut_all(d, dw), dw, band))
            pm.append(mice[idx])
        A, S, D = np.array(A), np.array(S), np.array(D)
        res = score(-np.abs(A - S), -np.abs(A - D), pm, seed, n_perm)
        res["gate"] = "below" if res["ci"][1] < GATE else ("above" if res["ci"][0] > GATE else "straddles")
        out["pairs"][tier] = res
        print(f"  {stream} window-pair {tier:>12}: {res['accuracy']:.3f} "
              f"[{res['ci'][0]:.3f}, {res['ci'][1]:.3f}]", flush=True)
    tiers = out["pairs"].values()
    out["pair_verdict"] = ("GO" if any(t["gate"] == "below" for t in tiers) else
                           "STOP" if all(t["gate"] == "above" for t in tiers) else "UNDECIDED")
    return out


def cut_all(r: Rec, w) -> list[np.ndarray]:
    return [cut(t, w, w[0]) for t in r.trains]


def strip_private(o):
    if isinstance(o, dict):
        return {k: strip_private(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [strip_private(v) for v in o]
    return o


def figure(results: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    streams = list(results["streams"])
    fig, axes = plt.subplots(len(streams), 2, figsize=(11, 3.2 * len(streams)), squeeze=False,
                             gridspec_kw={"width_ratios": [3, 2]})
    colours = {0.5: "#1f6fb4", 1.0: "#111111"}
    for row, st in enumerate(streams):
        R = results["streams"][st]
        ax = axes[row][0]
        labels = ["real vs real", "thinning 30%"] + [t.replace("_", " ") for t in TIERS]
        ctrl = [R["controls"]["real_vs_real"], R["controls"]["thinning"]]
        for i, c in enumerate(ctrl):
            ax.errorbar([i], [c["accuracy"]], yerr=[[c["accuracy"] - c["ci"][0]], [c["ci"][1] - c["accuracy"]]],
                        fmt="s", color="#b4521f", capsize=3)
        for share, dx in ((0.5, -0.12), (1.0, 0.12)):
            for j, tier in enumerate(TIERS):
                c = R["chimera"][f"{tier}@{share}"]
                ax.errorbar([2 + j + dx], [c["accuracy"]],
                            yerr=[[c["accuracy"] - c["ci"][0]], [c["ci"][1] - c["accuracy"]]],
                            fmt="o", color=colours[share], capsize=3,
                            label=f"swap share {share:g}" if j == 0 else None)
        ax.axhline(0.5, color="#9a9a9a", lw=0.8)
        ax.axhline(GATE, color="#9a9a9a", lw=0.8, ls="--")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels if row == len(streams) - 1 else [""] * len(labels), rotation=20)
        ax.set_ylabel(f"{st} · chimera vs real\naccuracy ({R['n_windows']} windows, {R['n_mice']} mice)")
        ax.set_ylim(0.4, 1.02)
        if row == 0:
            ax.legend(loc="upper left", frameon=False, fontsize=8)
        ax2 = axes[row][1]
        for j, tier in enumerate(PAIR_TIERS):
            c = R["pairs"][tier]
            ax2.errorbar([j], [c["accuracy"]], yerr=[[c["accuracy"] - c["ci"][0]], [c["ci"][1] - c["accuracy"]]],
                         fmt="o", color="#111111", capsize=3)
        ax2.axhline(0.5, color="#9a9a9a", lw=0.8)
        ax2.axhline(GATE, color="#9a9a9a", lw=0.8, ls="--")
        ax2.set_xticks(range(len(PAIR_TIERS)))
        ax2.set_xticklabels([t.replace("_", " ") for t in PAIR_TIERS] if row == len(streams) - 1
                            else [""] * len(PAIR_TIERS))
        ax2.set_xlim(-0.5, len(PAIR_TIERS) - 0.5)
        ax2.set_ylim(0.4, 1.02)
        ax2.set_ylabel(f"{st} · same recording?\nforced-choice accuracy")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--role", default="steps_excluded", help="current_export.toml role")
    ap.add_argument("--streams", nargs="+", default=["fast", "slow"])
    ap.add_argument("--permutations", type=int, default=199)
    ap.add_argument("--quick", action="store_true", help="300 windows, 39 permutations")
    ap.add_argument("--out", type=Path, default=None, help="default: the darkroom folder")
    ap.add_argument("--also", type=Path, default=None, help="also copy outputs here")
    a = ap.parse_args(argv)

    folder = dataset.current(a.role)
    if a.out is None:
        from bugarach.paths import darkroom
        dr = darkroom(OUT_DIRNAME, create=True)
        if dr is None:
            ap.error("no darkroom found; pass --out")
        a.out = Path(dr)
    a.out.mkdir(parents=True, exist_ok=True)
    n_perm = 39 if a.quick else a.permutations
    results = {"figure_id": FIGURE_ID, "role": a.role, "folder": folder.name,
               "window_sec": WINDOW_SEC, "pair_gap_sec": PAIR_GAP_SEC, "gate": GATE,
               "n_permutations": n_perm, "n_boot": N_BOOT, "quick": a.quick, "streams": {}}
    for stream in a.streams:
        recs, skipped = load(folder, stream)
        print(f"{stream}: {len(recs)} recordings, {len(skipped)} skipped", flush=True)
        R = run_stream(recs, stream, n_perm=n_perm, max_windows=300 if a.quick else None)
        R["skipped"] = skipped
        results["streams"][stream] = R
    clean = strip_private(results)
    (a.out / "results.json").write_text(json.dumps(clean, indent=2))
    figure(results, a.out / f"{FIGURE_ID}.png")
    print(f"wrote {a.out}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in ("results.json", f"{FIGURE_ID}.png"):
            shutil.copy2(a.out / f, a.also / f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
