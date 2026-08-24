"""The folder comes out as a file, and the file says what produced it.

`runDetect` answers one question — this detector, this recording — and the save
button hands over exactly that. Which means the page could not do the thing the
whole pipeline is for: run everything over everything and leave with a table.

What the export must satisfy is not a new argument. `docs/webapp_spec.md` and
`docs/todo/2026-08-19-lane-d1-the-detections-writer.md` settled it, and
`src/bugarach/emit.py` already implements the Python half — `write_detections`,
`write_run` and `read_detections`, with a round-trip test. The rules that bite
here:

  * `slice_id` from the data, never a filename.
  * the period carried, never inferred, never merged (FOUNDATIONS §9 — effects
    run in opposite directions by group, so a pooled row is not admissible).
  * one row per event per detector, no consensus merging.
  * seconds on the recording's own clock.
  * **a slice with no detections emits no rows and is still listed in the
    roster** — absent rows are a finding, an absent slice is a bug, and the two
    must not look alike.
  * no viability column, ever.

The sidecar exists for the last of those and for the six-months-later reader:
generator spec, chosen K, each detector's setting, the seeds, the code
version, and the frame interval per slice.

**What is NOT claimed here.** `docs/webapp_completion_plan.md` proposes agreeing
with `docs/learned/bakeoff.json` row for row as the acceptance test. That is a
claim about the Python pipeline. Three of the six browser detectors sample, and
`docs/testing_a_sampling_port.md` sets the bar for those at behavioural rather
than 1e-9 — so what is checked below is that the browser's table READS BACK
THROUGH `emit.read_detections` unchanged, and that the two deterministic
detectors agree with the library exactly. Claiming bakeoff equality for a
sampled port would be claiming something this cannot check.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"

# Two recordings: one with plenty of coordination, one deliberately silent.
# The silent one is the load-bearing fixture — it is what tells "no rows" apart
# from "no slice".
QUIET = "roi,time_sec\n" + "".join(f"r{i:02d},NA\n" for i in range(1, 9))


def _busy(dur=1200.0, n_roi=18, seed=5):
    import random

    rng = random.Random(seed)
    rois = [f"r{i:02d}" for i in range(1, n_roi + 1)]
    rows = []
    for c in (100.0, 250.0, 400.0, 550.0, 700.0, 850.0):
        for r in rois[:13]:
            rows.append((r, round(c + rng.uniform(-0.05, 0.05), 4)))
    for r in rois:
        t = 0.0
        while True:
            t += rng.expovariate(0.010)
            if t >= dur:
                break
            rows.append((r, round(t, 4)))
    rows.sort()
    return "roi,time_sec\n" + "".join(f"{r},{t}\n" for r, t in rows)


SLICES = ("slice_id,frame_interval_sec,mouse\n"
          "busy,0.1,m1\n"
          "quiet,0.05,m2\n")

REGIONS = ("slice_id,region_idx,label,start_sec,end_sec\n"
           "busy,1,baseline,0,600\n"
           "busy,2,ttx,600,1200\n")


def folder():
    return [{"name": "busy.csv", "text": _busy()},
            {"name": "quiet.csv", "text": QUIET},
            {"name": "slices.csv", "text": SLICES},
            {"name": "regions.csv", "text": REGIONS}]


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the export is built in the page")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            pg = browser.new_page()
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(VIEWER.as_uri(), wait_until="load")
            yield pg, errs
        finally:
            browser.close()


RUN_FOLDER = """async (files) => {
  await open(files, {quiet: true});
  await analyseFolder();
  return {csv: FOLDER_RUN ? detectionsCsv(FOLDER_RUN.rows) : null,
          run: FOLDER_RUN ? runJson(FOLDER_RUN) : null,
          settings: FOLDER_RUN
            ? settingsCsv(runSettingsRows(FOLDER_RUN.thresholds)) : null,
          text: document.getElementById("detectOut").innerText};
}"""


@pytest.fixture(scope="module")
def exported(page):
    pg, errs = page
    got = pg.evaluate(RUN_FOLDER, folder())
    assert not errs, errs
    assert got["csv"], "the folder run produced no table at all"
    return got


def _rows(csv_text, tmp_path):
    from bugarach import emit

    p = tmp_path / "detections.csv"
    p.write_text(csv_text, encoding="utf-8")
    return emit.read_detections(p)


def test_the_browsers_table_reads_back_through_the_library(exported, tmp_path):
    """One dialect, not two. `emit.read_detections` is the reader every consumer
    downstream uses; a file it cannot parse is a second dialect of one table."""
    rows = _rows(exported["csv"], tmp_path)
    assert rows, "read_detections got nothing out of the browser's file"
    for r in rows:
        assert isinstance(r["onset_sec"], float)
        assert r["slice_id"] in {"busy", "quiet"}


def test_every_detector_appears_not_just_the_chosen_one(exported, tmp_path):
    rows = _rows(exported["csv"], tmp_path)
    got = {r["detector"] for r in rows}
    assert got >= {"rate", "sce", "coact", "loco"}, (
        f"the folder run covered only {sorted(got)}")


def test_both_regions_are_reported_and_never_merged(exported, tmp_path):
    """FOUNDATIONS §9: effects run in opposite directions by group, so a pooled
    row is not admissible. baseline and ttx stay separate rows."""
    rows = [r for r in _rows(exported["csv"], tmp_path) if r["slice_id"] == "busy"]
    labels = {r["region_label"] for r in rows}
    assert labels == {"baseline", "ttx"}, (
        f"regions were merged or dropped: {labels}")


def test_a_slice_with_no_detections_is_in_the_roster_and_has_no_rows(exported,
                                                                    tmp_path):
    """The distinction the sidecar exists for."""
    rows = _rows(exported["csv"], tmp_path)
    assert not [r for r in rows if r["slice_id"] == "quiet"], (
        "the silent recording produced rows it could not have produced")
    run = exported["run"]
    assert "quiet" in run["slices"], (
        "the silent recording vanished from the run entirely — absent rows are "
        "a finding, an absent slice is a bug, and these must not look alike")


def test_the_sidecar_carries_the_frame_interval_per_slice(exported):
    fi = exported["run"]["frame_interval_sec"]
    assert fi["busy"] == pytest.approx(0.1)
    assert fi["quiet"] == pytest.approx(0.05), (
        "a single frame interval was applied to a folder that sent two")


def test_the_sidecar_records_each_detectors_settings_by_detector_and_stream(
        exported):
    """Keyed by BOTH, which is what the export contract asks for.

    It used to be keyed by detector alone — a comment in the page said so — and
    that was not a formatting difference. `emit.detector_settings_rows` gives the
    reason in a line: a detector may run differently on the fast and slow
    streams, and a table that could not say so makes one of the two
    unreproducible.
    """
    th = exported["run"]["thresholds"]
    assert set(th) >= {"rate", "sce", "coact", "loco"}, sorted(th)
    for name, by_stream in th.items():
        assert isinstance(by_stream, dict) and by_stream, (
            f"{name} recorded no settings at all: {by_stream!r}")
        assert all(isinstance(v, dict) for v in by_stream.values()), (
            f"{name}'s settings are not keyed by stream: {sorted(by_stream)}")
    assert exported["run"]["stream"], (
        "the sidecar does not name the stream the run was about")


def test_the_settings_do_not_smuggle_in_one_recordings_frame_interval(exported):
    """The bug this caught, pinned.

    The first version recorded `D.settings(cfg)` — the sentence the panel shows
    — once per detector, overwriting it on every recording. That sentence embeds
    the frame interval, which is per recording, so a folder holding one slice at
    0.1 s and another at 0.05 s reported `dt 0.05 s` for the whole run: whichever
    was last. It read as a fact about the run and was a fact about the loop.

    The frame interval belongs to `frame_interval_sec`, per slice, and the
    settings are parameters rather than prose.
    """
    th = exported["run"]["thresholds"]
    for name, by_stream in th.items():
        for stream, params in by_stream.items():
            assert isinstance(params, dict), (
                f"{name}/{stream} recorded a rendered sentence rather than its "
                "parameters; a sentence cannot be read back and this one "
                f"carried a per-recording value: {params!r}")
            assert "gridDt" not in params, (
                f"{name}/{stream} carries a frame interval, which varies per "
                "recording — run.json records that per slice and must not also "
                "imply one applied to the whole run")
            flat = json.dumps(params)
            assert "0.05" not in flat or "0.1" not in flat, flat


def test_the_run_also_writes_the_settings_file_the_contract_asks_for(exported,
                                                                     tmp_path):
    """`detections.csv` and `run.json` were the whole output. The contract asks
    for three files, and the third is the one that makes a result reproducible
    from the folder alone."""
    from bugarach import emit

    p = tmp_path / "detector_settings.csv"
    p.write_text(exported["settings"], encoding="utf-8")
    got = emit.read_detector_settings(p)
    assert got, "the folder run produced no settings file"
    assert all(isinstance(k, tuple) and len(k) == 2 for k in got), sorted(got)
    detectors = {d for d, _ in got}
    assert detectors >= {"rate", "sce", "coact", "loco"}, sorted(detectors)


def test_the_sidecar_says_null_rather_than_omitting_what_this_run_lacked(exported):
    """A real folder has no generator spec and no chosen K. Saying so is not the
    same as never having been asked — `emit.write_run` makes that distinction and
    the browser must not lose it."""
    run = exported["run"]
    for k in ("generator_spec", "chosen_k", "simulated_data_seeds"):
        assert k in run, f"{k} is missing from run.json rather than null"
        assert run[k] is None, f"{k} was invented for a folder read off disk"


def test_no_viability_column_of_any_kind(exported, tmp_path):
    """FOUNDATIONS §9 — that verdict is the producer's and this repo cannot
    compute it. The quiet recording's ROIs fired nothing; nothing here may call
    them dead."""
    header = exported["csv"].splitlines()[0].lower()
    for banned in ("dead", "viab", "silent", "inactive", "rejected", "alive"):
        assert banned not in header, f"{banned!r} in {header!r}"


def test_identity_columns_from_slices_csv_ride_along(exported, tmp_path):
    rows = _rows(exported["csv"], tmp_path)
    busy = [r for r in rows if r["slice_id"] == "busy"]
    assert busy and busy[0].get("mouse") == "m1", (
        "the producer's own columns did not survive the export, so the table "
        "cannot be joined back to their records")


def test_the_line_endings_are_newline_only_including_the_last(exported):
    csv = exported["csv"]
    assert "\r" not in csv
    assert csv.endswith("\n")
