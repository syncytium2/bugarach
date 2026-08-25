"""The browser's assessment against `bugarach.assess`, on the same bytes.

The webapp measures coordination itself, because a workflow a lab must install a
toolchain to start is a workflow most labs will not start. That means two
implementations of one measurement, which is the arrangement this project is
most careful about — so they are checked against each other rather than trusted.

**What must match exactly, and what cannot.** The measurement splits in two:

* deterministic — binned coactivity, clusters, participants, onset span, the
  observed jitter. These depend on nothing but the data, and any difference is a
  bug. Compared at 1e-9.
* Monte Carlo — the null, and therefore the coactivity excess and the tightness
  comparison. Both sides estimate it by sampling and their generators differ, so
  they agree to sampling error. Compared loosely, and reported.

**CI runs this**, since 2026-08-19 — the runner installs chromium and
sets `BUGARACH_REQUIRE_BROWSER=1`, so a browser that goes missing fails
`test_browser_available.py` loudly rather than letting this skip quietly.
Without a browser locally it still skips.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.assess import assess_coactivity
from bugarach.simulate import simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

N_SURROGATES = 200
BIN_SEC = 1.0
WINDOW = (0.0, 1800.0)

# one row per quantity that depends on nothing but the data
EXACT = [
    ("clustersPerMin", "clusters_permin"),
    ("partNObs", "part_n_obs"),
    ("spanMed", "span_med"),
    ("jitObs", "jit_obs"),
    ("obsMass", "obs_mass"),
    ("nCoactBins", "n_coact_bins"),
    ("nClustersObs", "n_clusters_obs"),
]

JS = """(cfg) => {
  const rec = RECORDINGS[0], data = rec.loaded;
  const stream = [...data.streams.keys()].sort()[0];
  const byRoi = data.streams.get(stream);
  const [ws, we] = cfg.window;
  const trains = data.order.map(id =>
    (byRoi.get(id) || []).filter(x => x >= ws && x <= we).map(x => x - ws));
  return assessCoactivity(trains, we - ws,
                          {nSurrogates: cfg.n, binWidth: cfg.bin})
    .map(a => ({K: a.K, clustersPerMin: a.clustersPerMin, partNObs: a.partNObs,
                spanMed: a.spanMed, jitObs: a.jitObs, obsMass: a.obsMass,
                nCoactBins: a.nCoactBins, nClustersObs: a.nClustersObs,
                coactExcess: a.coactExcess, jitDefined: a.jitDefined}));
}"""


def _write_recording(folder: Path) -> None:
    """One conforming recording, written by Python and read by both sides."""
    folder.mkdir(parents=True, exist_ok=True)
    s, _ = simulate_coordination(duration_sec=WINDOW[1], n_roi=25,
                                 bg_rate_hz=0.02, n_per_level=(5, 5, 5),
                                 min_sep_sec=60.0, seed=7)
    rows = ["roi,time_sec"]
    for r, v in enumerate(s.streams["events"].locs):
        if not len(v):
            rows.append(f"{r + 1},NA")
        for t in v:
            rows.append(f"{r + 1},{t:.1f}")
    (folder / "rec.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (folder / "slices.csv").write_text(
        "slice_id,frame_interval_sec\nrec,0.1\n", encoding="utf-8")


def _browser_result(folder: Path):
    pw = pytest.importorskip("playwright.sync_api",
                             reason="the browser assessment needs playwright")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            page = browser.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(VIEWER.as_uri())
            page.set_input_files(
                "#files", [str(q) for q in sorted(folder.iterdir())])
            page.wait_for_selector("#view:not([hidden])", timeout=30000)
            assert not errors, errors
            return page.evaluate(
                JS, {"n": N_SURROGATES, "bin": BIN_SEC, "window": list(WINDOW)})
        finally:
            browser.close()


@pytest.fixture(scope="module")
def both(tmp_path_factory):
    folder = tmp_path_factory.mktemp("export")
    _write_recording(folder)

    from bugarach.io import load_folder

    s = load_folder(folder)[0]
    py = {a.min_rois: a for a in assess_coactivity(
        s, window=WINDOW, n_surrogates=N_SURROGATES, bin_width_sec=BIN_SEC)}
    js = {row["K"]: row for row in _browser_result(folder)}
    return js, py


def test_the_two_implementations_see_the_same_K_scan(both):
    js, py = both
    assert sorted(js) == sorted(py) != []


@pytest.mark.parametrize("js_key,py_key", EXACT)
def test_the_data_dependent_half_matches_exactly(both, js_key, py_key):
    """No sampling is involved in these, so any difference is a bug."""
    js, py = both
    for K in sorted(py):
        a, row = py[K], js[K]
        jv, pv = float(row[js_key]), float(getattr(a, py_key))
        if np.isnan(jv) and np.isnan(pv):
            continue
        assert abs(jv - pv) < 1e-9, f"K={K} {js_key}: browser {jv} vs python {pv}"


def test_undefined_tightness_is_undefined_on_both_sides(both):
    """`jit_defined` is a state a reader acts on; the two must not disagree
    about whether the comparison exists."""
    js, py = both
    for K in sorted(py):
        assert bool(js[K]["jitDefined"]) is bool(py[K].jit_defined), f"K={K}"


def test_the_sampled_half_agrees_within_sampling_error(both):
    """The null is estimated, and the two generators differ. This pins that the
    difference stays sampling-sized rather than becoming a second answer."""
    js, py = both
    for K in sorted(py):
        jv, pv = float(js[K]["coactExcess"]), float(py[K].coact_excess)
        if np.isnan(jv) and np.isnan(pv):
            continue
        scale = max(abs(pv), 1.0)
        assert abs(jv - pv) / scale < 0.05, (
            f"K={K} coactExcess: browser {jv} vs python {pv} — more than "
            f"sampling error apart")
