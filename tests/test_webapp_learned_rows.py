"""The learned rows, driven through a browser against a real lab server.

`test_webapp_scoreboard.py` opens the page as `file://`, where `window.__lab` is
undefined and the table is the six. This opens the page **as `bugarach lab`
serves it** — same file, shim appended — and drives the same button, so the path
that was added for the learned rows is exercised rather than merely parsed.

That distinction cost a claim. On the day the route landed, the page's JS was
checked with `node --check` and every symbol was confirmed defined, and the work
was handed over as *"nothing has driven this end to end in a browser."* Parsing
is not running: `chosenArchs`, `learnedRows` and the request assembly could each
have been individually well-formed and still wrong together.

**The stub trainer, deliberately.** What is under test here is the page — that it
selects architectures, ships the corpus with its participant onsets, splits by
its own folds, scores what comes back through its own scorer and paints it. The
numerics are `tests/test_lab_fit_folds.py`'s job, and paying for four real fits
to check a table would make this too slow to run.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from bugarach import lab as lab_mod

ROOT = Path(__file__).resolve().parents[1]

# Small enough to fit six recordings and a fold split into a few seconds.
SIM = {"sRec": "6", "sMin": "25", "sRoi": "24", "sRate": "12", "sEv": "14",
       "sJit": "300", "sSeed": "4"}

DRIVE = """async (sim) => {
  /* WAIT for `wireLab` to populate the picker from the registry before touching
     it. It is async, and repopulation REPLACES the options — so a selection made
     before it lands is silently discarded. This test passed without the wait and
     was racing: the run that photographed the panel hit it, selected three
     architectures, and trained one. */
  const sel = document.getElementById("lArch");
  for (let i = 0; i < 100 && sel.options.length < 2; i++)
    await new Promise(r => setTimeout(r, 50));
  for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
  await runSim();
  document.getElementById("scTol").value = "1.5";
  // every architecture the server offers, so the multi-select is exercised
  [...sel.options].forEach(o => { if (!o.disabled) o.selected = true; });
  await scoreAllDetectors();
  const box = document.getElementById("scoreOut");
  return {
    board: SCOREBOARD,
    text: box.innerText,
    archs: [...sel.options].map(o => ({value: o.value, label: o.textContent,
                                       selected: o.selected,
                                       disabled: o.disabled})),
    multiple: sel.multiple,
    chosen: chosenArchs(),
  };
}"""


@pytest.fixture(scope="module")
def served():
    """The page as the local server hands it out, in a real browser."""
    pytest.importorskip("playwright.sync_api",
                        reason="the panel is a property of the running page")
    from playwright.sync_api import sync_playwright

    httpd = lab_mod.make_server(port=0, trainer=lab_mod.StubTrainer(), quiet=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as e:                    # noqa: BLE001
                pytest.skip(f"no chromium available: {type(e).__name__}")
            try:
                pg = browser.new_page()
                errs: list[str] = []
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.goto(base + "/", wait_until="load")
                got = pg.evaluate(DRIVE, SIM)
                assert not errs, errs
                yield got
            finally:
                browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()
        t.join(timeout=5)


def test_the_picker_is_multi_select_and_comes_from_the_registry(served):
    """A hardcoded option list is the second edit a new architecture needs, and
    the one nobody remembers. It is also where this broke once already: the rows
    were assumed to be strings and would have rendered as `[object Object]`."""
    assert served["multiple"], "one architecture at a time cannot compare two"
    values = [a["value"] for a in served["archs"]]
    from bugarach.learn.nets import ARCHITECTURES
    assert values == sorted(ARCHITECTURES), values
    for a in served["archs"]:
        assert "[object" not in a["label"], (
            f"the picker rendered {a['value']} as {a['label']!r} — the registry "
            f"rows are objects, not names")
        assert a["label"], f"{a['value']} has no label"


def test_something_is_selected_by_default_so_the_button_does_something(served):
    assert served["chosen"], (
        "no architecture is selected, so pressing Score every detector would "
        "silently produce the same table as before the learned rows existed")


def test_selecting_every_architecture_trains_every_architecture(served):
    """The multi-select has to actually carry more than one model through.

    This is where the picker's async population bites: `wireLab` replaces the
    options after `capabilities()` resolves, and a selection made before that
    lands is discarded without a word. A run that selected three and trained one
    is the failure this pins.
    """
    offered = {a["value"] for a in served["archs"] if not a["disabled"]}
    assert set(served["chosen"]) == offered, (
        f"selected {sorted(offered)} but chosenArchs() reports "
        f"{sorted(served['chosen'])}")
    trained = {r["which"] for r in served["board"]["rows"] if r.get("learned")}
    assert trained == offered, f"trained {sorted(trained)} of {sorted(offered)}"


def test_a_learned_row_reaches_the_table(served):
    rows = served["board"]["rows"]
    learned = [r for r in rows if r.get("learned")]
    assert learned, (
        "the scoreboard ran under a live lab server with an architecture "
        "selected and produced no learned row — the path this exists to check")
    for r in learned:
        assert not r.get("refused"), r.get("refused")
        assert r["label"] in served["text"], "the row is not on screen"


def test_the_learned_row_met_the_same_folds_as_the_six(served):
    """The whole point. Two runs on two fold assignments is not a comparison."""
    rows = [r for r in served["board"]["rows"] if not r.get("refused")]
    assert len({r["nFolds"] for r in rows}) == 1, (
        "the learned rows were offered a different number of folds than the six")
    learned = [r for r in rows if r.get("learned")]
    assert all(r["nScored"] == r["nFolds"] for r in learned)


def test_the_learned_row_is_scored_rather_than_hollow(served):
    """It went through `scoreDetections` and `tunePool` like every other row."""
    for r in [x for x in served["board"]["rows"] if x.get("learned")]:
        for field in ("f1", "precision", "recall"):
            assert r[field] is not None, f"{r['which']} has no {field}"
        assert 0.0 <= r["f1"] <= 1.0


def test_the_knobs_column_is_not_quietly_a_parameter_count(served):
    """A trained model exposes one setting. Putting 1,149 parameters in a column
    headed `knobs` would make one column mean two things in one table."""
    for r in [x for x in served["board"]["rows"] if x.get("learned")]:
        assert r["knobs"] == 1, r["knobs"]


def test_the_panel_says_what_a_learned_row_is_and_what_its_spread_is_not(served):
    low = served["text"].lower()
    assert "same" in low and "scorer" in low, (
        "nothing tells the reader the learned row shares the six's scorer")
    assert "one training run per fold" in low, (
        "a learned row's spread mixes data variation with training variation "
        "and the panel must not present it as the six's kind of ±")


def test_the_absent_sentence_is_gone_now_that_the_row_is_present(served):
    """The panel must not still explain an absence the table contradicts."""
    low = served["text"].lower()
    assert "no learned detector is in this table" not in low
