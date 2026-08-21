"""Did the simulation come out like the thing it was measured from?

Stage 5 of the pipeline, and the cheapest phase in
`docs/webapp_completion_plan.md`: *"you can look at it; nothing puts its measured
statistics beside the real folder's"*.

The generator is parameterised from an assessment — four measured quantities map
onto four knobs, and `simulateFromMeasurement` says which:

    roi_rate_med    -> the background rate
    clusters_permin -> how many coordinated events
    part_n_obs      -> how many ROIs take part
    jit_obs         -> how tight they are (the SD of participant onsets)

Nothing checked that the corpus that came out matches the folder that went in.
A generator can be wrong in ways that are invisible in a raster and obvious in a
number — `docs/todo/2026-08-14-generator-background-model-is-flat.md` is one
already on file — and every tuned operating point downstream is fitted on this
corpus.

**What this screen must not become.** A verdict. It reports the measurement of
the real folder beside the measurement of the simulation and the gap between
them; it does not decide whether the gap is acceptable, because that depends on
what the corpus is for. The assessment already refuses to pick K for the same
reason.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"


def _busy(dur=1500.0, n_roi=24, seed=3):
    """A recording with enough coordination and length to be assessable."""
    import random

    rng = random.Random(seed)
    rois = [f"r{i:02d}" for i in range(1, n_roi + 1)]
    rows = []
    for k in range(12):
        c = 60.0 + k * 115.0
        for r in rois[:8]:
            rows.append((r, round(c + rng.gauss(0, 0.25), 4)))
    for r in rois:
        t = 0.0
        while True:
            t += rng.expovariate(0.012)
            if t >= dur:
                break
            rows.append((r, round(t, 4)))
    rows.sort()
    return "roi,time_sec\n" + "".join(f"{r},{t}\n" for r, t in rows)


FOLDER = [{"name": "real1.csv", "text": _busy()},
          {"name": "slices.csv", "text": "slice_id,frame_interval_sec\nreal1,0.1\n"}]


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the comparison is built in the page")
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


# The whole loop, in the page: measure a real recording, accept a K, generate a
# corpus from that measurement, then measure the corpus and compare.
FLOW = """async (files) => {
  await open(files, {quiet: true});
  await show(RECORDINGS[0]);
  await runAssess();
  // the accept step, as the button does it
  const a = LAST_ASSESS.blocks[0].res.find(q => q.meetsFloor);
  simulateFromMeasurement(RECORDINGS[0], a, LAST_ASSESS.source,
                          LAST_ASSESS.blocks[0].stream);
  document.getElementById("sRec").value = "3";
  await runSim();
  await verifySimulation();
  const box = document.getElementById("verifyOut");
  return {
    text: box.innerText,
    headers: [...box.querySelectorAll("th")].map(t => t.textContent.trim()),
    rows: [...box.querySelectorAll("tr")].slice(1).map(
      tr => [...tr.querySelectorAll("td")].map(td => td.textContent.trim())),
    target: VERIFY ? VERIFY.target : null,
    got: VERIFY ? VERIFY.got : null,
  };
}"""


@pytest.fixture(scope="module")
def compared(page):
    pg, errs = page
    got = pg.evaluate(FLOW, FOLDER)
    assert not errs, errs
    return got


def test_the_comparison_has_both_sides(compared):
    """The premise: a real measurement and a simulated one, both present."""
    assert compared["target"], "nothing recorded what the generator was aiming at"
    assert compared["got"], "the generated corpus was never measured"


def test_it_reports_the_four_quantities_the_generator_is_set_from(compared):
    """Exactly the four `simulateFromMeasurement` maps onto knobs. A comparison
    that showed others would be reporting on things the generator never
    promised; one that showed fewer would be leaving a knob unchecked."""
    text = " ".join(" ".join(r) for r in compared["rows"]).lower()
    for want in ("rate", "cluster", "particip", "jitter"):
        assert want in text, (
            f"{want!r} is missing from the comparison; rows were "
            f"{[r[0] for r in compared['rows']]}")


def test_every_row_carries_a_measured_value_from_each_side(compared):
    """A table with a target column and an empty result column looks like a
    comparison and is a restatement of the request."""
    for row in compared["rows"]:
        assert len(row) >= 3, row
        for cell in row[1:3]:
            assert cell and cell != "—", (
                f"{row[0]}: one side of the comparison is empty ({row})")


RATE_WIRING = """(spec) => {
  for (const [k, v] of Object.entries(spec))
    document.getElementById(k).value = v;
  const made = simulateFolder(readSim());
  const out = [];
  for (const f of made.files) {
    if (f.name === "slices.csv" || f.name === "regions.csv") continue;
    const lines = f.text.trim().split("\\n");
    const head = lines[0].split(",");
    const iRoi = head.indexOf("roi"), iT = head.indexOf("time_sec");
    const per = new Map();
    let tmax = 0;
    for (const ln of lines.slice(1)) {
      const c = ln.split(",");
      const t = Number(c[iT]);
      per.set(c[iRoi], (per.get(c[iRoi]) || 0) + (Number.isFinite(t) ? 1 : 0));
      if (Number.isFinite(t)) tmax = Math.max(tmax, t);
    }
    const r = [...per.values()].map(n => 1000 * n / tmax).sort((a, b) => a - b);
    const m = r.length >> 1;
    out.push(r.length % 2 ? r[m] : (r[m - 1] + r[m]) / 2);
  }
  return out;
}"""


def test_the_rate_knob_is_connected_on_a_flat_background(page):
    """The wiring check, on the background where the question is well posed.

    On `flat` every ROI is drawn at one rate, so the median per-ROI rate and the
    mean are the same thing and "did the knob do what it said" has one answer.
    A failure here is a disconnected knob, not a modelling choice.

    Deliberately NOT asserted on the default `fitted` background: there the
    knob behaves as a mean over a heavily skewed population while the
    calibration path feeds it a median, so the two differ by construction. That
    gap is real and is filed as
    `docs/todo/2026-08-20-the-generator-is-set-from-a-median-and-fed-as-a-mean.md`
    — it is the generator's to fix or the assessor's, and a test that pinned the
    current ratio would freeze the discrepancy in place as though it were the
    specification.
    """
    pg, errs = page
    got = pg.evaluate(RATE_WIRING,
                      {"sRec": "3", "sMin": "25", "sRoi": "24", "sRate": "15",
                       "sEv": "0", "sJit": "250", "sSeed": "1", "sBg": "flat"})
    assert not errs, errs
    for med in got:
        assert 12.0 <= med <= 18.0, (
            f"asked for 15 mHz/ROI with no planted events and got a median of "
            f"{med:.1f} — the knob is not driving the background")


def test_it_names_what_it_measured_and_at_which_K(compared):
    """The assessment's own rule: quoting one of these numbers means naming the
    K it came from. That does not stop being true when the number is a target."""
    txt = compared["text"]
    assert "K" in txt and str(compared["target"]["K"]) in txt, txt[:300]
    assert "real1" in txt, "the recording the target came from is not named"


def test_it_does_not_deliver_a_verdict(compared):
    """No pass, no fail, no 'validated'. The gap is reported; what counts as an
    acceptable gap is the reader's call, the way K is."""
    low = compared["text"].lower()
    for banned in ("validated", "verified ok", "looks good", "good match",
                   "confirms", "within tolerance", "acceptable"):
        assert banned not in low, (
            f"the comparison delivers a verdict ({banned!r}); it reports a gap "
            "and the reader decides what it means")
    assert "passes or fails" in low, (
        "the panel should say plainly that it is not ruling on the gap")
