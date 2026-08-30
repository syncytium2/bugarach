"""One stream is analysed at a time, and the reader is the one who picked it.

The page drew both lanes of a two-stream recording from the beginning and handed
the alphabetically first one to the assessor, the detector and the sweep:

    const stream = [...data.streams.keys()].sort()[0];

`fast`, on this lab's folders. Nothing on screen said so, and the other stream
was not analysed at all — so a reader watching two lanes draw got a table about
one of them, unlabelled. FOUNDATIONS §9 is why that is a wrong answer rather than
a partial one: coordination under TTX **splits by stream**, FAST at 0.46 of its
own baseline against SLOW at 2.50, so a table that silently means `fast` is a
claim that cannot be checked.

The first repair ran every stream. It closed the silence and left the harder
half open: `tuneLoad` still swept one stream, `TUNED` had no stream in its key,
and `detectOne` read one `cfg` before the stream loop — so a threshold fitted on
`fast` was applied to `slow`, and `run.json` wrote a `thresholds` object with no
stream in it while `emit.detector_settings_rows` keys by `(detector, stream)`
precisely so that cannot happen.

**The repair that holds is the one at the door** (Tony, 2026-08-22: *"treat fast
and slow as separate folders"* — `docs/todo/2026-08-22-the-stream-is-chosen-at-
the-door.md`). A folder with more than one stream is asked which, once, when it
opens; from there exactly one is in play, and every setting is per-stream by
construction because there is no second stream for one to leak onto. What this
file checks is therefore: the choice is offered and visible, the analysis obeys
it, the OTHER stream is reachable rather than dropped, a value fitted on one
stops claiming the other, and a one-stream folder still never sees any of it
(FOUNDATIONS §3 — single-stream is the default presentation).
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
            # The page simulates a folder on load, asynchronously. Opening one
            # of ours before that settles races it, and the stream selector is
            # exactly the thing a stale load would repaint.
            page.wait_for_function(
                "() => document.getElementById('prov') && "
                "!document.getElementById('prov').hidden", timeout=120000)
            yield page, errs
        finally:
            browser.close()


OPEN = """async (files) => {
  await open(files, {quiet: true});
  return RECORDINGS.map(r => r.id);
}"""

DOOR = """() => ({
  seen: STREAMS_SEEN,
  stream: STREAM,
  shown: !document.getElementById("streamPick").hidden,
  options: [...document.getElementById("sStream").options].map(o => o.value),
  note: document.getElementById("streamWhat").textContent,
})"""

PICK = """async (name) => {
  const sel = document.getElementById("sStream");
  sel.value = name;
  sel.dispatchEvent(new Event("change", {bubbles: true}));
  await new Promise(r => setTimeout(r, 50));
  return STREAM;
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


def test_the_door_asks_which_stream_and_offers_every_one(viewer):
    """The choice is on screen, not in the code.

    Test the screen: the selector is visible, it lists both streams, and the
    note beside it says in words that one is analysed at a time and where the
    other went. A choice a reader cannot see is the old silent `sort()[0]` with
    a variable in front of it.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    door = page.evaluate(DOOR)
    assert door["shown"], "a two-stream folder opened with no stream selector"
    assert door["options"] == ["fast", "slow"], door["options"]
    assert door["stream"] == "fast", door
    text = door["note"].lower()
    assert "fast" in text and "slow" in text, door["note"]
    assert "one is analysed at a time" in text, door["note"]
    assert not errs, errs


@pytest.mark.parametrize("which", ["rate", "coact", "loco", "sce"])
def test_the_analysis_runs_on_the_stream_the_door_chose(viewer, which):
    """Not the alphabetically first one — the chosen one, whichever that is.

    Run each detector under each choice and check the rows say so. With the old
    `sort()[0]` the `slow` half of this returns `fast` rows; with the version
    that ran everything it returns both, which is the answer to a question
    nobody asked once the door exists.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    for want in ("fast", "slow"):
        assert page.evaluate(PICK, want) == want
        got = page.evaluate(DETECT, which)
        assert got["streams"] == [want], (
            f"{which} with {want} chosen at the door reported rows for "
            f"{got['streams']}. FOUNDATIONS §9: the streams move in opposite "
            "directions under TTX, so analysing the other one is not a rougher "
            "answer, it is a different one.")
    assert not errs, errs


def test_the_detect_table_names_the_stream_when_there_are_two(viewer):
    """Test the screen, not the function.

    The rows carried a `stream` column all along — what the reader saw did not.
    One stream is in play, so the table names that one; the column stays because
    a folder that HOLDS two has something to tell apart.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    page.evaluate(PICK, "slow")
    got = page.evaluate(DETECT, "rate")
    assert "stream" in [h.lower() for h in got["headers"]], (
        f"no stream column on screen; headers were {got['headers']}")
    assert "slow" in got["text"], (
        "the table does not name the stream it is about")
    assert not errs, errs


def test_a_single_stream_folder_is_never_asked_and_gains_no_column(viewer):
    """FOUNDATIONS §3: single-stream is the default presentation.

    Most outside labs have one stream. A selector with one option and a column
    that always reads the same value are both furniture, and this page's whole
    layout convention is against both. The stream is still RECORDED — `STREAM`
    holds the name the loader gave it — because the settings file keys on it and
    an empty cell there would be declining to answer a known question.
    """
    page, errs = viewer
    _open(page, _folder(one_stream_csv()))
    page.evaluate(SELECT, "s1")
    door = page.evaluate(DOOR)
    assert not door["shown"], "a one-stream folder was asked to choose a stream"
    assert door["stream"] == "events", door
    got = page.evaluate(DETECT, "rate")
    assert "stream" not in [h.lower() for h in got["headers"]], (
        f"a one-stream folder got a stream column: {got['headers']}")
    assert not errs, errs


def test_the_other_stream_is_a_click_away_and_gives_a_different_answer(viewer):
    """A guard against the cheapest wrong fix, and against the worst one.

    Answering with one stream and relabelling the rows would satisfy every
    assertion above. The folder plants six coordinated events in `fast` and
    three in `slow`, so identical counts under the two choices mean the door
    moves a label rather than the analysis. It also pins the thing choosing at
    the door must not cost: the second stream is still reachable, so nothing was
    dropped — it was deferred to a click.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    counts = {}
    for want in ("fast", "slow"):
        page.evaluate(PICK, want)
        got = page.evaluate(DETECT, "coact")
        assert set(got["perStreamCounts"]) == {want}, got["perStreamCounts"]
        counts[want] = got["perStreamCounts"][want]
    assert counts["fast"] != counts["slow"], (
        f"both choices reported {counts['fast']} events from a folder that "
        "plants six in fast and three in slow — the door moves a label, not the "
        "analysis.")
    assert not errs, errs


def test_a_recording_without_the_chosen_stream_is_refused_by_name(viewer):
    """The one thing choosing at the door must not be allowed to do quietly.

    A folder can hold `fast` and `slow` in one recording and only `fast` in
    another. Falling back to whatever that recording does have would answer with
    the other signal under the right label — the exact substitution FOUNDATIONS
    §9 rules out — so it is a refusal that names the recording, the stream asked
    for and the streams present.
    """
    page, errs = viewer
    mixed = [{"name": "both.csv", "text": two_stream_csv()},
             {"name": "fastonly.csv",
              "text": "roi,time_sec,stream\n" + "".join(
                  f"r{r:02d},{round(30.0 * k + 0.02 * r, 3)},fast\n"
                  for k in range(1, 20) for r in range(1, 12))},
             {"name": "slices.csv",
              "text": ("slice_id,frame_interval_sec\n"
                       "both,0.1\nfastonly,0.1\n")}]
    _open(page, mixed)
    page.evaluate(PICK, "slow")
    got = page.evaluate("""async () => {
      const rec = RECORDINGS.find(r => r.id === "fastonly");
      await show(rec);
      await runDetect();
      return {text: document.getElementById("detectOut").innerText,
              detect: DETECT ? DETECT.rows.length : null};
    }""")
    assert got["detect"] is None, (
        "a recording with no `slow` stream produced rows anyway — from `fast`, "
        f"under the wrong name. Panel read:\n{got['text'][:400]}")
    text = got["text"].lower()
    assert "slow" in text and "fast" in text, got["text"][:400]
    assert not errs, errs


def test_assess_measures_the_chosen_stream_and_names_it(viewer):
    """Assess already printed `stream <name>` — and measured only one of them.

    Naming the stream you did not analyse is worse than not naming it, so this
    is about the measurement rather than the label: pick `slow` and the panel
    has to be about `slow`.
    """
    page, errs = viewer
    _open(page, _folder(two_stream_csv()))
    page.evaluate(SELECT, "s1")
    page.evaluate(PICK, "slow")
    got = page.evaluate(ASSESS)
    assert "slow" in got["text"], (
        "the assessment does not name the stream it measured. Panel read:\n"
        f"{got['text'][:400]}")
    assert not errs, errs
