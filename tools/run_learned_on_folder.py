#!/usr/bin/env python3
"""Train a learned detector on a folder's own spec, then run it on that folder.

    python tools/run_learned_on_folder.py --spec RUN/02_spec/generator_spec.json \
        --folder EXPORT_FOLDER --models tube tube_guard --out RUN/07_learned

WHY THIS EXISTS. "Nothing persists a trained model" is true and it is not the
same sentence as "the learned models cannot run on real data" — which is what
this project's own pipeline document, and a report written off it, had been
saying. No checkpoint means a model cannot survive the end of a process, so
`bugarach detect` (a separate process, reading settings from a table) cannot
apply one. It does not mean the model cannot see real recordings. Train and
predict inside ONE process and the gap closes for the length of that process,
which is exactly long enough to produce a figure.

Tony, 2026-09-08, on a raster page that drew the learned row grey: *"Why does it
say tube not run? One motivation for this exercise was to demonstrate our learned
pipeline for outside review."* The row was grey because of a claim that had been
carried forward without being tested. It was worth testing.

WHAT MAKES IT LEGITIMATE, and the three things that would make it not:

* **The encoder already takes a real recording.** `learn.encode.encode` wants a
  `Slice`, a sampling interval, and onset times — which is what an export folder
  is. It builds a binary onset raster and nothing else; amplitude and width are
  deliberately not channels, because the generator cannot produce them, so there
  is no representational gap between simulated and real input.
* **The architectures are cell-count invariant.** `tube`'s own docstring: cells
  are summed, "so the model never sees which cell is which and runs at any cell
  count". Trained on the spec's 26-ROI field, it runs on 13 and on 34.
* **It is run per analysis window**, the same way the six ports are, so each
  period is judged against its own background and no model gets context across a
  drug transition that the others were denied.

WHAT IT DOES NOT SETTLE, and the report must say so:

* The **threshold is chosen on simulated validation recordings** and applied to
  real ones unchanged. That is a transfer assumption, and it is the whole of the
  operating point.
* The **model is trained on a spec derived from these same recordings' baseline**,
  so the simulated training distribution is shaped by the data being scored.
* **One training seed.** The standing limitation of everything learned here.
* Row order inside the encoding is **busiest-first over the whole window**, so it
  is not causal. Fine for a figure of a finished recording; not a live detector.

Output is `detections.csv` in the same contract `bugarach detect` writes, so the
raster page and every reader of that file take it without knowing the difference,
plus `learned_settings.csv` recording each model's threshold, parameter count and
training cost. Destination defaults to the darkroom (FOUNDATIONS §5).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.detect_folder import _region_index, folder_analysis_windows  # noqa: E402
from bugarach.emit import DetectedEvent, write_detections  # noqa: E402
from bugarach.io import load_folder  # noqa: E402


#: The learned family, in the bake-off's own order. Named here rather than taken
#: from the registry so that "the full learned pipeline" means the same six
#: models the optimization ran, and a newly registered architecture does not
#: silently join a comparison nobody re-ran.
LEARNED = ("tube", "tube_guard", "tube_ratio", "tube_ratio_guard", "trace", "tiny")


def train_all(spec: dict, models, *, folds: int, seeds_per_fold: int,
              train_seed: int, steps: int):
    """Fit each architecture on the corpus the optimization was run on.

    THE SAME SIMULATED DATA AS THE OPTIMIZATION, and that is the requirement, not
    a convenience (Tony, 2026-09-08). The bake-off deals `folds x seeds_per_fold`
    recording seeds out of one generator spec and fits the learned models on the
    training folds; drawing a fresh block of seeds here — which is what
    `train`'s own default does — would fit these models on data the calibration
    never saw, and the two halves of the run would stop being comparable while
    still being printed side by side.

    So the seeds come from `bench.fold_split`, the recordings from the same
    `simulate_coordination(spec)` factory, and the hyperparameters from the
    bake-off, including its per-architecture learning rate. The one deliberate
    difference: the bake-off fits four times, once per held-out fold, because it
    scores on simulated data it must not have seen. Nothing here is scored on
    simulated data — the target is the real folder, which no fit can reach — so
    this fits ONCE over the whole simulated corpus. `fold_maker` still holds part
    of it back, so the threshold is picked on recordings the weights never saw.
    """
    from bugarach.bench import fold_split
    from bugarach.learn.train import fold_maker, train
    from bugarach.simulate import simulate_coordination

    # The bake-off's learning rates. Every published tube number was fitted at
    # 1e-2 and the three variants differ from it by a kernel change alone, so a
    # per-variant rate here would confound the mechanism with its optimisation.
    lr = {"tube": 1e-2, "tube_guard": 1e-2, "tube_ratio": 1e-2,
          "tube_ratio_guard": 1e-2, "trace": 1e-3, "tiny": 1e-3}

    split = fold_split(n_folds=folds, seeds_per_fold=seeds_per_fold)
    seeds = list(split.seeds)
    cache: dict[int, tuple] = {}

    def rec(seed: int):
        if seed not in cache:
            cache[seed] = simulate_coordination(seed=seed, **spec)
        return cache[seed]

    mk, n_fit, n_val = fold_maker(rec, seeds)
    out = []
    for name in models:
        t0 = time.perf_counter()
        trained = train(name, mk, n_train=min(10, n_fit), steps=steps,
                        crop=4096, batch=3, lr=lr.get(name, 1e-2), seed=train_seed)
        out.append((name, trained, time.perf_counter() - t0))
        print(f"  {name:18} fitted on {min(10, n_fit)} of {len(seeds)} simulated "
              f"recordings in {out[-1][2]:6.1f}s  threshold {trained.threshold:.4f}  "
              f"{trained.n_params} params", flush=True)
    return out, seeds, n_fit, n_val


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--spec", required=True, type=Path,
                    help="generator_spec.json the models are trained on")
    ap.add_argument("--folder", required=True, type=Path, help="the export folder to run on")
    ap.add_argument("--models", nargs="+", default=list(LEARNED),
                    help=f"architectures to fit (default, the full learned pipeline: "
                         f"{' '.join(LEARNED)})")
    ap.add_argument("--streams", nargs="+", default=["fast", "slow"])
    ap.add_argument("--seed", type=int, default=0, help="torch seed; one training run each")
    ap.add_argument("--folds", type=int, default=4,
                    help="the bake-off's fold count — sets the simulated corpus")
    ap.add_argument("--seeds-per-fold", type=int, default=2)
    ap.add_argument("--steps", type=int, default=900,
                    help="the bake-off's non-quick setting (default: 900)")
    ap.add_argument("--out", type=Path, default=None, help="destination (default: darkroom)")
    a = ap.parse_args(argv)

    raw = json.loads(a.spec.read_text())
    gen = raw.get("generator", raw)
    dt = float(gen.get("grid_sec", 0.1))

    if a.out is None:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / "learned_on_folder"
    a.out.mkdir(parents=True, exist_ok=True)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = sorted(load_folder(a.folder), key=lambda s: s.slice_id)

    print(f"fitting {len(a.models)} architecture(s) on the optimization's own corpus")
    fitted, seeds, n_fit, n_val = train_all(
        gen, a.models, folds=a.folds, seeds_per_fold=a.seeds_per_fold,
        train_seed=a.seed, steps=a.steps)

    events, settings_rows = [], []
    for name, trained, secs in fitted:
        # ONE MODEL, BOTH STREAMS, and that is a limitation rather than a choice.
        # A simulated recording has a single stream ("events"), so there is no
        # fast model and no slow model to fit — and the spec those recordings come
        # from was derived from the FAST assessment. So the slow stream is scored
        # by a model trained on a fast-shaped distribution, which is exactly the
        # asymmetry the six already carry on this cohort. Naming it here rather
        # than fitting twice on identical data, which would only disguise it.
        for sname in a.streams:
            settings_rows.append({
                "detector": name, "stream": sname,
                "threshold": f"{trained.threshold:.6f}",
                "n_params": str(trained.n_params),
                "dt_sec": f"{trained.dt:g}",
                "merge_gap_frames": str(trained.merge_gap_frames),
                # `pick_threshold` searches [0.0001, 0.9999] and warns when the
                # answer is an end of it: the search was still climbing when the
                # grid ran out, so the number is a bound rather than an operating
                # point. Carried into the table because a reader comparing rows
                # must not have to notice it from a log line that scrolled past.
                "threshold_at_grid_edge":
                    "yes" if min(abs(trained.threshold - 0.0001),
                                 abs(trained.threshold - 0.9999)) < 1e-9 else "no",
                "train_seed": str(a.seed),
                "simulated_corpus": f"{len(seeds)} recordings, "
                                    f"{a.folds}x{a.seeds_per_fold} (the bake-off's split)",
                "n_fit": str(min(10, n_fit)), "n_threshold_val": str(n_val),
                "steps": str(a.steps), "train_seconds": f"{secs:.1f}",
                "trained_on": a.spec.name,
                "trained_stream": "events (simulated; the spec is fast-derived)",
            })
            n_called = 0
            for s in slices:
                if sname not in s.streams:
                    continue
                _, wins = folder_analysis_windows(s)
                for w in wins:
                    out, _enc = trained.predict(
                        s, stream=sname,
                        extent=(float(w.win_start), float(w.win_end)))
                    for on, wd in zip(out.onset_sec, out.width_sec):
                        events.append(DetectedEvent(
                            slice_id=s.slice_id, stream=sname, detector=name,
                            mode="learned", onset_sec=float(on), width_sec=float(wd),
                            strength=float(trained.threshold),
                            strength_unit="score threshold",
                            width_def="above threshold, merged",
                            region_idx=_region_index(w),
                            region_label=(w.label or "").strip() or None,
                            n_roi=None,
                            identity=dict(s.meta)))
                        n_called += 1
            print(f"  {name:18} {sname:5} {n_called} call(s) on {len(slices)} recording(s)",
                  flush=True)

    det = write_detections(events, a.out / "detections.csv")
    import csv as _csv
    cols = list(settings_rows[0]) if settings_rows else ["detector"]
    with (a.out / "learned_settings.csv").open("w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(settings_rows)
    print(f"wrote {det}")
    print(f"wrote {a.out / 'learned_settings.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
