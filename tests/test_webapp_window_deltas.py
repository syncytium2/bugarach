"""The three-delta window generator in the browser.

A conforming folder states when each period ran and MAY state which part of it to
score. Last night's export from this project's own producer states the first and
not the second — deliberately, because deriving the second is a protocol decision
and the contract stopped making it. So the app has to let a person state it, and
this checks that what they get is what they asked for.

Every case here is hand-derived: the windows are simple arithmetic on period
bounds, so the right answer can be written down rather than compared against
another implementation. Synthetic folders only — FOUNDATIONS §5, and the real
corpus that motivated this is machine-local.

**The rules under test, and each has a way of being wrong that this catches:**

* the baseline runs BACKWARD from its end, because the minutes before the
  treatment are what the treatment is compared against
* every other period runs FORWARD from a delay, because the delay is the solution
  arriving
* both clamp, because a period can be shorter than the delta asked for
* a delay that outlasts its period yields no window at all rather than an
  inverted one
* no period is treated differently for what it is CALLED — the convention this
  replaces exempted anything whose label contained "hi", so `high K+` kept its
  whole period and renaming it `KCl` would have silently begun trimming it
* a window the producer sent is never overwritten

⚠ **CI does not run this** — it needs a chromium CI does not install.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

# one recording, four periods, chosen so every rule has something to bite on:
# a long baseline (backward trim), an ordinary drug (delay + cap), a period
# shorter than the cap (clamped), and one shorter than the delay (no window)
REGIONS = """slice_id,region_idx,label,start_sec,end_sec
s1,1,baseline,0,1800
s1,2,TTX,1800,3600
s1,3,high K+,3600,3900
s1,4,washout,3900,3960
"""
EVENTS = "roi,time_sec\n" + "".join(
    f"{r},{t}.0\n" for r in range(1, 6) for t in range(100, 3900, 200))
SLICES = "slice_id,frame_interval_sec\ns1,0.1\n"

SETUP = """async (v) => {
  const f = (name, text) => new File([text], name, {type: "text/csv"});
  await open([f("s1.csv", v.events), f("regions.csv", v.regions),
              f("slices.csv", v.slices)]);
  for (const [id, val] of Object.entries(v.controls))
    document.getElementById(id).value = String(val);
  for (const lab of (v.noDelay || [])) {
    const cb = document.getElementById("wDelay_" + lab);
    if (!cb) throw new Error("no delay toggle for " + lab);
    cb.checked = false; cb.onchange();
  }
  if (v.run) runWindows();
  const wins = REGIONS.get("s1").slice().sort((a, b) => a.idx - b.idx);
  return {
    chip: document.getElementById("cntWindows").textContent,
    runDisabled: document.getElementById("runWindows").disabled,
    toggles: [...document.querySelectorAll("#wDelays label")].map(l => l.textContent),
    baseOptions: [...document.getElementById("wBase").options].map(o => o.textContent),
    windows: wins.map(w => ({
      idx: w.idx, label: w.label, start: w.start, end: w.end,
      aStart: Number.isFinite(w.aStart) ? w.aStart : null,
      aEnd: Number.isFinite(w.aEnd) ? w.aEnd : null,
      derived: !!w.derived, tooShort: !!w.tooShort})),
    segments: analysisSegments({id: "s1"}, {t0: 0, t1: 3960})
      .map(s => ({label: s.label, start: s.start, end: s.end, source: s.source})),
  };
}"""

BASE = {"wBase": 1, "wBaseDur": 20, "wDelay": 2, "wTreatDur": 20, "wFloor": 4}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the window panel needs playwright")
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
            pg.goto(VIEWER.as_uri())
            yield pg, errs
        finally:
            browser.close()


def run(page, regions=REGIONS, controls=None, do_run=True, no_delay=()):
    pg, errs = page
    out = pg.evaluate(SETUP, {"events": EVENTS, "regions": regions,
                              "slices": SLICES,
                              "controls": {**BASE, **(controls or {})},
                              "noDelay": list(no_delay), "run": do_run})
    assert not errs, errs
    return out


def test_the_baseline_is_measured_backward_from_its_end(page):
    """A thirty-minute baseline asked for its last twenty gives 10:00 to 30:00 —
    not its first twenty. The end is the part the treatment is compared with."""
    w = run(page)["windows"][0]
    assert (w["aStart"], w["aEnd"]) == (600.0, 1800.0), w
    assert w["derived"] and not w["tooShort"]


def test_a_treatment_skips_its_delay_and_then_runs_its_length(page):
    """TTX ran 30:00 to 60:00. Two minutes for the solution, then twenty: 32:00
    to 52:00 — forward, and stopping short of the period's end."""
    w = run(page)["windows"][1]
    assert (w["aStart"], w["aEnd"]) == (1920.0, 3120.0), w


def test_a_period_shorter_than_the_length_asked_for_is_clamped_not_extended(page):
    """`high K+` ran five minutes. Two for the delay leaves three, and the window
    stops at the period's end rather than running twenty minutes past it."""
    w = run(page)["windows"][2]
    assert (w["aStart"], w["aEnd"]) == (3720.0, 3900.0), w
    assert w["tooShort"], "a three-minute window under a four-minute floor"


def test_a_delay_that_outlasts_its_period_yields_no_window_at_all(page):
    """`washout` ran one minute and the delay is two. There is no window to give,
    and an inverted one would be worse than none — the guards on `regions.csv`
    refuse exactly that shape."""
    w = run(page)["windows"][3]
    assert w["aStart"] is None and w["aEnd"] is None, w
    assert w["tooShort"] and not w["derived"]


def test_no_period_is_treated_differently_for_what_it_is_called(page):
    """The convention this replaces exempted any label containing `hi` from both
    the delay and the length. `high K+` contains it; so does `histamine`; and
    `chelerythrine` does not, though a reader would expect it to. Here the label
    changes nothing — the same period under three names gets one answer."""
    got = []
    for name in ("high K+", "KCl", "chelerythrine"):
        regions = REGIONS.replace("high K+", name)
        got.append(tuple(run(page, regions=regions)["windows"][2].values())[4:6])
    assert len(set(got)) == 1, f"the label changed the window: {got}"


def test_a_window_the_folder_sent_is_never_overwritten(page):
    """Where a producer states what to score, that is their decision. The panel
    reports it and refuses to run rather than quietly replacing it."""
    stated = REGIONS.replace(
        "slice_id,region_idx,label,start_sec,end_sec",
        "slice_id,region_idx,label,start_sec,end_sec,"
        "analysis_start_sec,analysis_end_sec").replace(
        "s1,1,baseline,0,1800", "s1,1,baseline,0,1800,120,900").replace(
        "s1,2,TTX,1800,3600", "s1,2,TTX,1800,3600,1900,2500").replace(
        "s1,3,high K+,3600,3900", "s1,3,high K+,3600,3900,3650,3800").replace(
        "s1,4,washout,3900,3960", "s1,4,washout,3900,3960,3910,3950")
    out = run(page, regions=stated, do_run=False)
    assert out["runDisabled"], "the panel offered to overwrite the folder"
    assert "folder" in out["chip"]
    assert out["windows"][0]["aStart"] == 120.0, "the folder's window moved"
    assert not out["windows"][0]["derived"]
    assert all(s["source"] == "folder" for s in out["segments"])


def test_every_result_says_whose_window_it_used(page):
    """Three states, never two: the folder said it, you said it, or nobody did.
    A number computed from a window derived in this browser must not read as one
    the producer sent."""
    before = run(page, do_run=False)["segments"]
    assert {s["source"] for s in before} == {"none"}
    after = run(page)["segments"]
    assert {s["source"] for s in after[:3]} == {"you"}
    # the period with no window falls back to its whole extent, and says so
    assert after[3]["source"] == "none"
    assert (after[3]["start"], after[3]["end"]) == (3900.0, 3960.0)


def test_a_period_kind_can_be_told_it_waits_for_no_solution(page):
    """A drug has to arrive; a depolarising challenge is already there. Ticking
    `high K+` off gives it its whole period back — 60:00 to 65:00 rather than
    62:00 to 65:00 — and it clears the four-minute floor it was failing."""
    out = run(page, no_delay=["high K+"])
    w = out["windows"][2]
    assert (w["aStart"], w["aEnd"]) == (3600.0, 3900.0), w
    assert not w["tooShort"], "five minutes should clear a four-minute floor"

    # and the one the delay outlasted now has a window at all
    assert run(page, no_delay=["washout"])["windows"][3]["aStart"] == 3900.0


def test_the_toggle_moves_only_the_kind_it_names(page):
    """Turning the delay off for one period kind must not touch the others —
    otherwise it is a global switch wearing a label."""
    out = run(page, no_delay=["high K+"])
    assert (out["windows"][1]["aStart"], out["windows"][1]["aEnd"]) \
        == (1920.0, 3120.0), "TTX lost its delay along with high K+"
    assert out["windows"][0]["aStart"] == 600.0, "the baseline moved"


def test_the_toggle_is_the_users_list_not_a_rule_about_names(page):
    """The distinction from the convention this replaces. `chelerythrine` does
    not contain `hi` and `histamine` does, so a substring rule treats them
    differently and this must not: ticking one off leaves the other delayed,
    whatever either is called."""
    regions = REGIONS.replace("high K+", "histamine")
    out = run(page, regions=regions, no_delay=["histamine"])
    assert out["windows"][2]["aStart"] == 3600.0, "histamine kept a delay"

    regions = REGIONS.replace("high K+", "chelerythrine")
    out = run(page, regions=regions)
    assert out["windows"][2]["aStart"] == 3720.0, (
        "chelerythrine was exempted without anyone asking for it")


def test_the_baseline_keeps_its_backward_window_even_if_its_label_repeats(page):
    """A label can appear twice — a control period at the start and again at the
    end is an ordinary design. The designation is by POSITION, so the first is
    the baseline and runs backward from its end, while the second is a treatment
    like any other and answers to the toggle. Unticking that shared label must
    move the second and leave the first alone."""
    regions = REGIONS.replace("s1,4,washout,3900,3960",
                              "s1,4,baseline,3900,5100")
    out = run(page, regions=regions, no_delay=["baseline"])
    base, repeat = out["windows"][0], out["windows"][3]
    assert (base["aStart"], base["aEnd"]) == (600.0, 1800.0), (
        f"the designated baseline stopped running backward: {base}")
    assert (repeat["aStart"], repeat["aEnd"]) == (3900.0, 5100.0), (
        f"the repeat should start at its own start with no delay: {repeat}")


# two recordings whose period 2 is a DIFFERENT drug — the ordinary shape of a
# real folder, and the one a single-recording fixture cannot express
TWO_SLICES = """slice_id,region_idx,label,start_sec,end_sec
s1,1,baseline,0,1800
s1,2,TTX,1800,3600
s1,3,high K+,3600,3900
s2,1,baseline,0,1800
s2,2,senktide,1800,3600
s2,3,high K+,3600,3900
"""


def test_one_period_index_can_carry_several_drugs(page):
    """Across a folder, period 2 is whichever drug that recording got. A list
    that keeps the first label seen per index hides the rest — on this project's
    own corpus that meant the delay toggles offered two period kinds out of six,
    with TTX and senktide silently absent and undeleayable.

    Both drugs must get a row, and the baseline chooser must name both rather
    than picking one and implying it is the period."""
    pg, errs = page
    out = pg.evaluate(SETUP, {
        "events": EVENTS, "regions": TWO_SLICES, "slices":
            "slice_id,frame_interval_sec\ns1,0.1\ns2,0.1\n",
        "controls": BASE, "noDelay": [], "run": False})
    assert not errs, errs
    assert set(out["toggles"]) == {"TTX", "senktide", "high K+"}, out["toggles"]
    period2 = [o for o in out["baseOptions"] if o.startswith("period 2")][0]
    assert "TTX" in period2 and "senktide" in period2, (
        f"the chooser names one drug and hides the other: {period2!r}")
