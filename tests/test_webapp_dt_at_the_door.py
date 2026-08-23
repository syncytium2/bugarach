"""The frame interval is asked for, never invented.

FOUNDATIONS §6: the sampling interval is a property of the recording, nothing
downstream can recover it, and *loading without it is refused rather than
defaulted* — "no default, no inference from the data, no fallback constant".

The page had the fallback constant three times over, and the folder check filed
a missing frame interval as a NOTE reading "detectors need one, this page does
not". So a conforming folder that declared no `frame_interval_sec` reported
**"✓ 2 of 2 conforming"**, ran all six detectors on a 10 Hz grid, and wrote a
`run.json` carrying `"frame_interval_sec": {"rec_a": 0.1, "rec_b": 0.1}` — a
number this file invented, sitting in the provenance sidecar beside measured
ones, indistinguishable from them, in a file that outlives the session. A lab
imaging at 20 Hz would have taken away a full `detections.csv` computed on
somebody else's clock with nothing anywhere saying so.

**Every test here presses a button.** The defect above survived a suite that
read data structures: `runJson` was correct about what it was given and what it
was given was fabricated two call frames upstream. So these open a folder, click
Detect, click Analyse the whole folder, type into the prompt, and read what is
on the screen afterwards.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"

# The page EXPLAINS the bug it no longer has, in a comment quoting the fallback
# verbatim. A scan that reads the explanation as the thing explained fires on
# the fix — `test_site_viewer.py` learned this the same way.
sys.path.insert(0, str(ROOT / "tools"))
from build_site import strip_comments  # noqa: E402

# Two recordings with enough going on for every detector to have something to
# say — and a slices.csv that carries identity but no frame interval, which is
# the whole point of the fixture.
def _events(seed: int, dur: float = 900.0, n_roi: int = 14) -> str:
    import random

    rng = random.Random(seed)
    rows = []
    for c in (120.0, 300.0, 480.0, 660.0):
        for r in range(1, 11):
            rows.append((f"r{r:02d}", round(c + rng.uniform(-0.1, 0.1), 4)))
    for r in range(1, n_roi + 1):
        t = 0.0
        while True:
            t += rng.expovariate(0.012)
            if t >= dur:
                break
            rows.append((f"r{r:02d}", round(t, 4)))
    rows.sort()
    return "roi,time_sec\n" + "".join(f"{r},{t}\n" for r, t in rows)


REGIONS = ("slice_id,region_idx,label,start_sec,end_sec\n"
           "rec_a,1,baseline,0,450\n"
           "rec_a,2,drug,450,900\n"
           "rec_b,1,baseline,0,450\n"
           "rec_b,2,drug,450,900\n")

# Conforming in every other respect. `group_id` is here so the folder cannot be
# dismissed as empty or malformed: slices.csv exists, has a row per recording,
# and simply never says how fast the microscope ran.
NO_DT = "slice_id,group_id\nrec_a,X\nrec_b,X\n"
WITH_DT = "slice_id,frame_interval_sec,group_id\nrec_a,0.02,X\nrec_b,0.02,X\n"


def _folder(slices: str) -> list[dict]:
    return [{"name": "rec_a.csv", "text": _events(11)},
            {"name": "rec_b.csv", "text": _events(12)},
            {"name": "regions.csv", "text": REGIONS},
            {"name": "slices.csv", "text": slices}]


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the refusal is a property of the running page")
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


def _open(pg, slices: str):
    pg.evaluate("async (files) => { await open(files); }", _folder(slices))


def _go(pg, step: str):
    """Walk to a stage the way a reader does — the pipeline rail across the top.

    Not `showSection` through `evaluate`: a control the rail cannot reach is a
    control nobody can press, and reaching it by hand would hide that.
    """
    pg.click(f'#rail [data-step="{step}"]')


@pytest.fixture
def opened_without_dt(page):
    pg, errs = page
    _open(pg, NO_DT)
    return pg, errs


# --------------------------------------------------------------------------
# the door


def test_a_missing_frame_interval_is_an_error_and_not_a_note(opened_without_dt):
    """The two tiers of the folder check mean what its own header says.

    A note is "read fine, may not be what you meant"; an error is "cannot be
    read as written". A folder missing one of the three facts the input
    contract asks for is the second, and calling it the first is what let this
    folder be announced as conforming.
    """
    pg, errs = opened_without_dt
    assert not errs, errs
    verdict = pg.eval_on_selector("#cntList", "e => e.textContent")
    assert "✕" in verdict, (
        f"the folder announced itself as {verdict!r} while declaring no frame "
        f"interval at all")
    panel = pg.eval_on_selector("#panel", "e => e.innerText")
    head, _, rest = panel.partition("Read fine")
    assert "frame_interval_sec" in head, (
        "the missing frame interval is not under 'Cannot be read as written':\n"
        + panel)


def test_the_problem_panel_opens_itself_rather_than_waiting_to_be_found(
        opened_without_dt):
    pg, _ = opened_without_dt
    assert not pg.eval_on_selector("#panel", "e => e.hidden")


def test_the_prompt_appears_and_says_which_recordings_it_covers(
        opened_without_dt):
    pg, _ = opened_without_dt
    assert not pg.eval_on_selector("#dtAsk", "e => e.hidden"), (
        "no way forward is offered: the folder is refused and the reader is "
        "told nothing about how to proceed")
    said = pg.eval_on_selector("#dtAsk", "e => e.innerText")
    assert "2 recordings" in said, said


# --------------------------------------------------------------------------
# the refusal


def test_analysing_the_whole_folder_refuses_instead_of_defaulting(
        opened_without_dt):
    """The load-bearing one. This exact click used to produce 51,968-row-shaped
    output on a grid nobody chose."""
    pg, errs = opened_without_dt
    _go(pg, "accDetect")
    pg.click("#runFolder")
    pg.wait_for_timeout(400)
    assert pg.evaluate("() => FOLDER_RUN") is None, (
        "the folder ran anyway — on what sampling interval?")
    said = pg.eval_on_selector("#detectOut", "e => e.innerText")
    assert "No frame interval" in said, said
    assert pg.eval_on_selector("#saveRun", "e => e.disabled"), (
        "a run.json is on offer for a run that did not happen")
    assert pg.eval_on_selector("#saveFolder", "e => e.disabled")
    assert not errs, errs


def test_detecting_on_one_recording_refuses_too(opened_without_dt):
    """The picture is more persuasive than the file, so the picture must not be
    drawn from an invented grid either."""
    pg, errs = opened_without_dt
    _go(pg, "accDetect")
    pg.click("#runDetect")
    pg.wait_for_timeout(600)
    assert pg.evaluate("() => DETECT") is None
    said = pg.eval_on_selector("#detectOut", "e => e.innerText")
    assert "No frame interval" in said, said
    assert pg.eval_on_selector("#saveDetections", "e => e.disabled")
    assert not errs, errs


def test_the_fallback_constant_is_gone_from_the_source():
    """A guard on the shape of the bug, not just on today's symptom.

    Three sites read `Number(m.frame_interval_sec) > 0 ? … : 0.1`. Any of them
    coming back would restore the whole defect, and a behavioural test only
    catches the paths it happens to walk.
    """
    src = strip_comments(VIEWER.read_text(encoding="utf-8"))
    bad = re.findall(r"frame_interval_sec\)[^\n]*:\s*0\.1", src)
    assert not bad, ("a fallback sampling interval is back in the page: "
                     + "; ".join(bad))


# --------------------------------------------------------------------------
# the way forward, and what it is recorded as


def test_a_supplied_interval_is_used_and_says_on_screen_that_it_is_yours(
        opened_without_dt):
    pg, errs = opened_without_dt
    _go(pg, "accList")
    pg.fill("#dtSec", "0.05")
    pg.click("#dtUse")
    pg.wait_for_timeout(400)
    meta = pg.eval_on_selector("#meta", "e => e.innerText")
    assert "0.05" in meta and "yours" in meta, (
        f"the raster's own header does not say where its dt came from: {meta!r}")
    assert not errs, errs


def test_supplying_one_retires_the_refusal_it_answers(opened_without_dt):
    """Found in this fix's own first draft, and it is item 2 again.

    Supply an interval and the results panel still read "No frame interval for
    rec_a" while the note under the raster said the detectors were running on
    the 0.05 s just given. Two claims about one recording, on one screen. A
    panel goes when what produced it stops being the case.
    """
    pg, errs = opened_without_dt
    _go(pg, "accDetect")
    pg.click("#runDetect")
    pg.wait_for_timeout(500)
    assert "No frame interval" in pg.eval_on_selector("#detectOut",
                                                      "e => e.innerText")
    _go(pg, "accList")
    pg.fill("#dtSec", "0.05")
    pg.click("#dtUse")
    pg.wait_for_timeout(400)
    _go(pg, "accDetect")
    assert pg.eval_on_selector("#detectOut", "e => e.innerText").strip() == "", (
        "the refusal is still on screen after the thing it refused over was "
        "supplied")
    assert not errs, errs


def test_what_the_reader_typed_is_recorded_as_theirs_in_run_json(
        opened_without_dt):
    """The provenance distinction, which is the point of the whole fix.

    A number a person stated and a number a producer measured are both usable
    and are not the same claim. `run.json` is the only place the difference can
    still be read six months later.
    """
    pg, errs = opened_without_dt
    _go(pg, "accList")
    pg.fill("#dtSec", "0.05")
    pg.click("#dtUse")
    _go(pg, "accDetect")
    pg.click("#runFolder")
    pg.wait_for_function("() => !document.getElementById('runFolder').disabled",
                         timeout=300000)
    run = pg.evaluate("() => runJson(FOLDER_RUN)")
    assert run["frame_interval_sec"] == {"rec_a": 0.05, "rec_b": 0.05}
    assert run["frame_interval_source"] == {"rec_a": "you", "rec_b": "you"}, (
        "the sidecar cannot tell a stated interval from a measured one")
    assert not errs, errs


def test_a_frame_interval_the_folder_sent_is_recorded_as_the_folders(page):
    pg, errs = page
    _open(pg, WITH_DT)
    assert pg.eval_on_selector("#dtAsk", "e => e.hidden"), (
        "the page asked for something the folder already sent")
    _go(pg, "accDetect")
    pg.click("#runFolder")
    pg.wait_for_function("() => !document.getElementById('runFolder').disabled",
                         timeout=300000)
    run = pg.evaluate("() => runJson(FOLDER_RUN)")
    assert run["frame_interval_sec"] == {"rec_a": 0.02, "rec_b": 0.02}
    assert run["frame_interval_source"] == {"rec_a": "folder",
                                            "rec_b": "folder"}
    assert not errs, errs


def test_a_supplied_interval_does_not_follow_the_reader_to_the_next_folder(page):
    """Everything else folder-shaped is cleared on open; this had to be too.

    Carrying it would be the same fabrication with one extra step — a number
    stated about one recording, applied silently to another.
    """
    pg, errs = page
    _open(pg, NO_DT)
    _go(pg, "accList")
    pg.fill("#dtSec", "0.05")
    pg.click("#dtUse")
    assert pg.evaluate("() => DT_SUPPLIED") == 0.05
    _open(pg, NO_DT)
    assert pg.evaluate("() => DT_SUPPLIED") is None, (
        "the last folder's stated frame interval was applied to a new one")
    _go(pg, "accDetect")
    pg.click("#runFolder")
    pg.wait_for_timeout(400)
    assert pg.evaluate("() => FOLDER_RUN") is None
    assert not errs, errs


def test_a_frame_rate_typed_into_the_prompt_is_refused_rather_than_clamped(page):
    """Clamping a mistyped interval into range would produce a plausible number
    nobody stated, which is the defect wearing a different hat."""
    pg, errs = page
    _open(pg, NO_DT)
    _go(pg, "accList")
    pg.fill("#dtSec", "0")
    pg.click("#dtUse")
    pg.wait_for_timeout(200)
    assert pg.evaluate("() => DT_SUPPLIED") is None
    said = pg.eval_on_selector("#dtWhat", "e => e.innerText")
    assert "seconds" in said.lower(), said
    assert not errs, errs
