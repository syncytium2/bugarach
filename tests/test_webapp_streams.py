"""Every stream gets analysed, and every result says which stream it came from.

The page drew both lanes of a two-stream recording from the beginning, and then
handed exactly one of them to the assessor, the detector and the sweep:

    const stream = [...data.streams.keys()].sort()[0];

Alphabetically first, which for this lab's folders is `fast`. Nothing on screen
said so outside the assess panel, and the other stream was not analysed at all —
so a reader watching the raster draw two lanes got a detection table about one of
them, unlabelled.

That is not a cosmetic gap. FOUNDATIONS §9 records that coordination under TTX
**splits by stream** — FAST at 0.46 of its own baseline, SLOW at 2.50 with 44% of
slices at or above it — and says in terms that a claim must name the stream.
A detection table that silently means `fast` is a claim that does not.

The other half of the rule is FOUNDATIONS §3: streams are generic, most outside
labs have exactly one, and the viewer treats single-stream as the default
presentation. So the fix is not "always show a stream column". It is: never drop
a stream, always name it **when there is more than one to tell apart**, and leave
the one-stream folder looking exactly as it did.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"


# ---------------------------------------------------------------- the folders

def _events(rois, centres, *, jitter=0.05, spread=None, seed=0):
    """Coordinated events: at each centre, `spread` ROIs fire within `jitter`."""
    rng = __import__("random").Random(seed)
    out = []
    n = spread or len(rois)
    for c in centres:
        for r in rois[:n]:
            out.append((r, round(c + rng.uniform(-jitter, jitter), 4)))
    return out


def _background(rois, dur, rate_hz, *, seed=1):
    rng = __import__("random").Random(seed)
    out = []
    for r in rois:
        t = 0.0
        while True:
            t += rng.expovariate(rate_hz)
            if t >= dur:
                break
            out.append((r, round(t, 4)))
    return out


def two_stream_csv(dur=1200.0, n_roi=20):
    """One recording, two streams, with DIFFERENT coordination in each.

    The counts are deliberately unequal. A page that analyses one stream and
    labels the result with the other's name would still produce a plausible
    table; unequal event counts mean the numbers themselves disagree, so the
    assertions below cannot pass by accident.
    """
    rois = [f"r{i:02d}" for i in range(1, n_roi + 1)]
    fast_centres = [90.0, 200.0, 310.0, 420.0, 530.0, 640.0]     # 6
    slow_centres = [150.0, 480.0, 700.0]                          # 3
    rows = []
    for roi, t in _events(rois, fast_centres, jitter=0.05, spread=14, seed=11):
        rows.append((roi, t, "fast"))
    for roi, t in _background(rois, dur, 0.010, seed=12):
        rows.append((roi, t, "fast"))
    for roi, t in _events(rois, slow_centres, jitter=0.30, spread=14, seed=21):
        rows.append((roi, t, "slow"))
    for roi, t in _background(rois, dur, 0.008, seed=22):
        rows.append((roi, t, "slow"))
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    body = "".join(f"{r},{t},{s}\n" for r, t, s in rows)
    return "roi,time_sec,stream\n" + body


def one_stream_csv(dur=1200.0, n_roi=20):
    """The same recording with the stream column absent — what most labs send."""
    rois = [f"r{i:02d}" for i in range(1, n_roi + 1)]
    rows = _events(rois, [90.0, 200.0, 310.0, 420.0, 530.0, 640.0],
                   jitter=0.05, spread=14, seed=11)
    rows += _background(rois, dur, 0.010, seed=12)
    rows.sort()
    return "roi,time_sec\n" + "".join(f"{r},{t}\n" for r, t in rows)


SLICES = "slice_id,frame_interval_sec\ns1,0.1\n"


def _folder(csv_text):
    return [{"name": "s1.csv", "text": csv_text},
            {"name": "slices.csv", "text": SLICES}]


# ---------------------------------------------------------------- the browser

@pytest.fixture(scope="module")
def viewer():
    pytest.importorskip(
        "playwright.sync_api",
        reason="the streams run in the page; checking them needs the page")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            page = browser.new_page()
            errs: list[str] = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto(VIEWER.as_uri(), wait_until="load")
            yield page, errs
        finally:
            browser.close()


OPEN = """async (files) => {
  await open(files, {quiet: true});
  return RECORDINGS.map(r => r.id);
}"""

SELECT = """async (id) => {
  const rec = RECORDINGS.find(r => r.id === id);
  await show(rec);
  const data = await loadRecording(rec);
  return [...data.streams.keys()].sort();
}"""

DETECT = """async (which) => {
  document.getElementById("dDet").value = which;
  paintDetectorChoice();
  await runDetect();
  const box = document.getElementById("detectOut");
  return {
    text: box.innerText,
    streams: DETECT ? [...new Set(DETECT.rows.map(r => r.stream))].sort() : [],
    perStreamCounts: DETECT
      ? DETECT.rows.reduce((a, r) => (a[r.stream] = (a[r.stream] || 0) + 1, a), {})
      : {},
    headers: [...box.querySelectorAll("th")].map(t => t.textContent.trim()),
  };
}"""

ASSESS = """async () => {
  await runAssess();
  const box = document.getElementById("assessOut");
  return {text: box.innerText,
          headers: [...box.querySelectorAll("th")].map(t => t.textContent.trim())};
}"""


def _open(page, files):
    return page.evaluate(OPEN, files)


# ---------------------------------------------------------------- the tests

def test_a_two_stream_folder_loads_both_streams(viewer):
    """The premise. If this fails the rest are testing the wrong thing."""
    page, errs = viewer
    assert _open(page, _folder(two_stream_csv())) == ["s1"]
    assert page.evaluate(SELECT, "s1") == ["fast", "slow"]
    assert not errs, errs


@pytest.mark.parametrize("which", ["rate", "coact", "loco", "sce"])
def test_every_stream_is_detected_on_not_just_the_first(viewer, which):
    """The bug, stated as a test.

    `sort()[0]` is `fast`, so a page with the old behaviour returns rows whose
    stream column is uniformly `fast` and never mentions `slow` at all.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    got = page.evaluate(DETECT, which)
    assert got["streams"] == ["fast", "slow"], (
        f"{which} reported rows for {got['streams']} — a stream the page drew a "
        "lane for was never analysed. FOUNDATIONS §9: the streams move in "
        "opposite directions under TTX, so dropping one is not a subset of the "
        "answer, it is a different answer.")
    assert not errs, errs


def test_the_detect_table_names_the_stream_when_there_are_two(viewer):
    """Test the screen, not the function.

    The rows carried a `stream` column all along — what the reader saw did not.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    got = page.evaluate(DETECT, "rate")
    assert "stream" in [h.lower() for h in got["headers"]], (
        f"no stream column on screen; headers were {got['headers']}")
    assert "fast" in got["text"] and "slow" in got["text"], (
        "the table does not name either stream in its cells")
    assert not errs, errs


def test_a_single_stream_folder_gains_no_stream_column(viewer):
    """FOUNDATIONS §3: single-stream is the default presentation.

    Most outside labs have one stream. A column that always reads the same value
    is furniture, and this page's whole layout convention is against it.
    """
    page, errs = viewer
    _open(page, _folder(one_stream_csv()))
    page.evaluate(SELECT, "s1")
    got = page.evaluate(DETECT, "rate")
    assert "stream" not in [h.lower() for h in got["headers"]], (
        f"a one-stream folder got a stream column: {got['headers']}")
    assert not errs, errs


def test_the_two_streams_do_not_report_the_same_events(viewer):
    """A guard against the cheapest wrong fix.

    Running one stream and relabelling the rows twice would satisfy every
    assertion above. The folder plants six coordinated events in `fast` and
    three in `slow`, so identical per-stream counts mean the second stream was
    copied rather than analysed.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    got = page.evaluate(DETECT, "coact")
    counts = got["perStreamCounts"]
    assert set(counts) == {"fast", "slow"}, counts
    assert counts["fast"] != counts["slow"], (
        f"both streams reported {counts['fast']} events from a folder that "
        "plants six in fast and three in slow — the second stream looks copied, "
        "not analysed.")
    assert not errs, errs


def test_assess_reports_every_stream(viewer):
    """Assess already printed `stream <name>` — and measured only one of them.

    Naming the stream you did not analyse is worse than not naming it, so this
    one is about the measurement, not the label.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    got = page.evaluate(ASSESS)
    assert "fast" in got["text"] and "slow" in got["text"], (
        "the assessment covers one stream and names it; the other was not "
        f"measured. Panel read:\n{got['text'][:400]}")
    assert not errs, errs
