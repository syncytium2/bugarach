"""Export bugarach store slices to plain v7 .mat for the MATLAB reference generator."""
import sys
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, "/Users/tonydefazio/Developer/bugarach/src")
from bugarach.store import load_slice  # noqa: E402

SCRATCH = Path(__file__).parent


def export(src, dst):
    s = load_slice(src)
    def cells(stream, f):
        return np.array([getattr(stream, f)[i] for i in range(stream.n_rois)],
                        dtype=object).reshape(1, -1)
    out = {
        "slice_id": s.slice_id,
        "fast_locs": cells(s.fast, "locs"),
        "fast_t50rise": cells(s.fast, "t50rise"),
        "fast_width": cells(s.fast, "width"),
        "slow_locs": cells(s.slow, "locs"),
        "slow_t50rise": cells(s.slow, "t50rise"),
        "slow_width": cells(s.slow, "width"),
        "regions_start": np.array([r.start_sec for r in s.regions], dtype=float),
        "regions_end": np.array([r.end_sec for r in s.regions], dtype=float),
        "regions_name": np.array([r.name or "" for r in s.regions],
                                 dtype=object).reshape(1, -1),
        "regions_slot": np.array([r.slot or "" for r in s.regions],
                                 dtype=object).reshape(1, -1),
    }
    sio.savemat(dst, out)
    # scout: pooled t50rise rate scale to pick thresholds
    for name in ("fast", "slow"):
        st = getattr(s, name)
        pooled = np.sort(np.concatenate([v for v in st.t50rise] or [np.empty(0)]))
        lo = min([r.start_sec for r in s.regions] + [pooled.min() if pooled.size else np.inf])
        hi = max([r.end_sec for r in s.regions] + [pooled.max() if pooled.size else -np.inf])
        if pooled.size:
            counts, _ = np.histogram(pooled, bins=np.arange(lo, hi + 1, 1.0))
            print(f"{Path(src).stem} {name}: n={pooled.size} ext=[{lo:.2f},{hi:.2f}] "
                  f"peak 1s-rate ~{counts.max()} Hz, mean {pooled.size/(hi-lo):.2f} Hz")
        else:
            print(f"{Path(src).stem} {name}: empty")


export("/Users/tonydefazio/Developer/bugarach/tests/fixtures/synth_fastcal_s1.mat",
       SCRATCH / "ref_input_synth.mat")

real = Path.home() / ("University of Michigan Dropbox/Richard DeFazio/data/"
                      "processed_archive/event_store_onset_revised_2v/20240708_13.mat")
if real.exists():
    export(real, SCRATCH / "ref_input_real.mat")
