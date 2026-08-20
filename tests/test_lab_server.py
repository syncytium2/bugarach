"""The lab server, and the gate that keeps the published page out of it.

`docs/adr/0001-the-lab-server.md` makes one promise that is worth more than the
feature: **the page that ships is unchanged**. Training exists only in a copy
handed out on loopback, with a shim appended, and the public site is dead by
absence of `window.__lab` rather than by anything being stripped. A promise like
that decays the moment it is only written down, so it is asserted here.

The endpoints are driven **through a real socket** rather than by calling the
handler's methods. The transport is the part being added, and framing — chunked
NDJSON, a terminal line that always arrives — is exactly what a direct call
would skip.
"""

from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from bugarach import lab as lab_mod

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"


# ---------------------------------------------------------------------------
# the gate — both halves
# ---------------------------------------------------------------------------

def _uncommented(text: str) -> str:
    """The page with comments removed, for the same reason `test_site_viewer`
    does it: the comments NAME the things the page must not do, so a check that
    reads them as code fires on the explanation of why it will never fire."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"^\s*//[^\n]*", " ", text, flags=re.M)


def test_the_published_page_defines_no_transport():
    """Catches a shim that migrated into the page.

    `test_site_viewer.py` already bans `fetch(` and eight other ways to reach a
    host, and it keeps doing that job. THIS check is narrower and aimed at the
    specific accident this ADR creates the opportunity for: somebody debugging
    the panel pastes the shim into the page to save a step, the page still opens
    fine locally, and the transport ships. The panel may READ `window.__lab`;
    it may never define it.
    """
    body = _uncommented(VIEWER.read_text(encoding="utf-8"))
    for defining in (r"window\.__lab\s*=", r"__lab\s*=\s*\{",
                     r"globalThis\.__lab\s*="):
        assert not re.search(defining, body), (
            f"{VIEWER.name} DEFINES window.__lab. That object is the transport, "
            f"and it exists only in the copy `bugarach lab` hands out. The page "
            f"reads it (`if (window.__lab)`) and never assigns it — otherwise "
            f"the published site grows a fetch and the privacy line stops being "
            f"a property of the file.")


def test_the_shim_is_not_on_disk_under_the_site_source():
    """The shim's only home is `bugarach.lab`. If a file under `docs/site/`
    carries it, the build will publish it whatever the page itself says.

    **What counts as carrying it is the assignment and the transport, not the
    name.** This test first rejected the bare substring ``window.__lab``
    anywhere under `docs/site/`, which contradicted the test directly above —
    that one's own failure message says *"The page reads it
    (`if (window.__lab)`)"* — and made ADR-0001's design unbuildable: the panel
    is inert on the published page precisely **because** it reads a capability
    object nobody defined there. A page forbidden to name the thing it checks
    for cannot check for it.

    So the check is: no definition, and no ``fetch(``. Those are what would
    actually turn a published file into one that can talk to something.
    """
    for p in sorted((ROOT / "docs" / "site").rglob("*")):
        if not p.is_file():
            continue
        body = _uncommented(p.read_text(encoding="utf-8", errors="ignore"))
        for defining in (r"window\.__lab\s*=", r"__lab\s*=\s*\{",
                         r"globalThis\.__lab\s*="):
            assert not re.search(defining, body), (
                f"{p.relative_to(ROOT)} DEFINES the lab shim. `docs/site/` is "
                f"what `build_site.py` publishes, and the shim exists only in "
                f"the copy `bugarach lab` hands out.")
        assert "fetch(" not in body, (
            f"{p.relative_to(ROOT)} contains a fetch. `docs/site/` is published, "
            f"and the transport belongs to the shim alone.")


def test_the_build_copies_the_viewer_rather_than_transforming_it():
    """The other half of the gate, at its source.

    The literal check the todo asks for — `site/viewer.html` byte-identical to
    `docs/site/raster_viewer.html` — can only run where a build has happened,
    and `site/` is gitignored build output that needs playwright chromium. So
    the property is asserted where it is DECIDED: the builder copies the file.
    The moment that becomes a transform (strip a marked block, inject a flag),
    the reviewed file stops being the shipped file and this fires.

    Read as text rather than imported, for the reason `test_site_viewer.py`
    gives: `tools/` is a directory of scripts, not an installed package.
    """
    build = (ROOT / "tools" / "build_site.py").read_text(encoding="utf-8")
    assert 'shutil.copyfile(viewer, SITE / "viewer.html")' in build, (
        "the build must COPY the viewer. A transform means the file reviewed "
        "in git is not the file that ships, which is the property ADR-0001 "
        "chose over reproducing colonel_kernel's build-time stripping.")
    # and it must still refuse to publish a page that reaches a host
    assert '"fetch(", "XMLHttpRequest"' in build or "'fetch('" in build or \
        'w for w in ("fetch("' in build, "the build's leak scan must survive"


def test_a_built_site_is_byte_identical_when_one_exists():
    """The literal check, run wherever a build actually happened.

    Skipped rather than removed: on a machine that has run `build_site.py` this
    is the real assertion, and skipping silently everywhere would make the
    previous test the only cover. Both are wanted.
    """
    built = ROOT / "site" / "viewer.html"
    if not built.is_file():
        pytest.skip("no built site/ here — run tools/build_site.py")
    assert built.read_bytes() == VIEWER.read_bytes(), (
        "site/viewer.html differs from docs/site/raster_viewer.html. The build "
        "started transforming the page.")


# ---------------------------------------------------------------------------
# the shim itself
# ---------------------------------------------------------------------------

def test_the_shim_holds_the_only_fetch_and_defines_the_object():
    assert "fetch(" in lab_mod.SHIM, "the shim IS the transport"
    assert "window.__lab" in lab_mod.SHIM
    for name in ("capabilities", "train", "detect"):
        assert name in lab_mod.SHIM, f"the shim must expose {name}()"


def test_the_served_page_is_the_page_plus_the_shim_and_nothing_else():
    """Appended, not injected. There is no marker in the page to find, so there
    is nothing a build could leave behind and nothing to trust was removed."""
    html = VIEWER.read_text(encoding="utf-8")
    served = lab_mod.page_with_shim(html)
    assert served.startswith(html), "the page must be handed out unmodified"
    assert served == html + lab_mod.SHIM


# ---------------------------------------------------------------------------
# a live server, over a socket
# ---------------------------------------------------------------------------

@pytest.fixture
def server():
    """A real bound server on a free loopback port, with the stub trainer.

    The stub is the point of the fixture: it makes the seam — routes, framing,
    refusals, the progress stream — testable without paying for a fit, which is
    why the todo puts the endpoints before the numerics.
    """
    httpd = lab_mod.make_server(port=0, trainer=lab_mod.StubTrainer(), quiet=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        t.join(timeout=5)


def _get(base, path):
    with urllib.request.urlopen(base + path, timeout=30) as r:
        return r.status, r.read().decode("utf-8"), r.headers


def _post(base, path, body):
    """POST JSON, read the NDJSON stream, return (progress lines, terminal)."""
    req = urllib.request.Request(
        base + path, data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json"}, method="POST")
    progress, terminal = [], None
    with urllib.request.urlopen(req, timeout=300) as r:
        for raw in r.read().decode("utf-8").splitlines():
            if not raw.strip():
                continue
            msg = json.loads(raw)
            (progress.append(msg) if msg["event"] == "progress"
             else None)
            if msg["event"] in ("result", "error"):
                terminal = msg
    return progress, terminal


def test_the_server_hands_out_the_page_with_the_shim(server):
    status, body, headers = _get(server, "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    assert VIEWER.read_text(encoding="utf-8") in body, "the page, unmodified"
    assert "window.__lab" in body, "and the shim, appended"


def test_capabilities_reports_the_trainer(server):
    _, body, _ = _get(server, "/api/capabilities")
    cap = json.loads(body)
    assert cap["trainer"] == "stub"
    assert cap["trains"] is True
    assert cap["models"] == []


def test_an_unknown_route_is_a_404_not_a_file(server):
    """There is no path handling here, so there is nothing to traverse. The
    check is that a route which looks like a path is still just an unknown
    route — the server never turns a request into a filename."""
    for probe in ("/etc/passwd", "/../../etc/passwd", "/docs/site/raster_viewer.html"):
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get(server, probe)
        assert exc.value.code == 404


def test_train_then_detect_through_the_stub(server):
    progress, result = _post(server, "/api/train", {"folds": 3})
    assert result["event"] == "result", result
    assert [p["fold"] for p in progress] == [0, 1, 2], "one line per fold"
    handle = result["model"]
    assert result["trainer"] == "stub"

    # a five-minute recording, two ROIs — the stub calls an event a minute
    rec = {"slice_id": "r1", "rois": [[1.0, 200.0], [1.5, 299.0]]}
    progress, result = _post(server, "/api/detect",
                             {"model": handle, "recordings": [rec]})
    assert result["event"] == "result", result
    det = result["detections"][0]
    assert det["slice_id"] == "r1"
    onsets = det["onset_sec"]
    assert len(onsets) == 5, f"one a minute over a ~299 s extent, got {onsets}"
    assert onsets[0] == pytest.approx(1.0)
    assert all(b - a == pytest.approx(60.0) for a, b in zip(onsets, onsets[1:]))


def test_detect_refuses_a_threshold_rather_than_ignoring_it(server):
    """The one rule the server does not get to relax.

    A silently dropped knob is worse than a refused one: the caller sees a
    plausible number come back and believes the knob worked, so a re-tune on
    the recording being analysed becomes invisible instead of impossible.
    """
    _, result = _post(server, "/api/train", {"folds": 2})
    handle = result["model"]
    for banned in ("threshold", "retune", "calibrate"):
        _, result = _post(server, "/api/detect", {
            "model": handle, "recordings": [{"slice_id": "r", "rois": [[1.0]]}],
            banned: 0.9})
        assert result["event"] == "error", f"{banned} must be refused"
        assert banned in result["message"]
        assert "held-out" in result["message"]


def test_an_unknown_model_is_an_error_in_the_stream(server):
    _, result = _post(server, "/api/detect",
                      {"model": "nope", "recordings": [{"slice_id": "r",
                                                        "rois": [[1.0]]}]})
    assert result["event"] == "error"
    assert "train() first" in result["message"]


def test_a_recording_must_name_itself_and_carry_rois(server):
    _, result = _post(server, "/api/train", {"folds": 2})
    handle = result["model"]

    _, r = _post(server, "/api/detect",
                 {"model": handle, "recordings": [{"rois": [[1.0]]}]})
    assert r["event"] == "error" and "slice_id" in r["message"]

    _, r = _post(server, "/api/detect",
                 {"model": handle, "recordings": [{"slice_id": "r"}]})
    assert r["event"] == "error" and "rois" in r["message"]

    _, r = _post(server, "/api/detect",
                 {"model": handle,
                  "recordings": [{"slice_id": "r", "rois": [["x"]]}]})
    assert r["event"] == "error" and "non-numeric" in r["message"]


def test_a_rebound_host_header_is_refused(server):
    """Binding 127.0.0.1 stops a packet from the network. It does not stop a
    page in another tab from resolving a name it controls to 127.0.0.1 and
    posting here, and the browser will send that happily."""
    req = urllib.request.Request(server + "/api/capabilities",
                                 headers={"Host": "lab.example.com"})
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req, timeout=30)
    assert exc.value.code == 403
    assert "rebinding" in exc.value.read().decode("utf-8")


def test_the_server_binds_loopback_only():
    httpd = lab_mod.make_server(port=0, trainer=lab_mod.StubTrainer(), quiet=True)
    try:
        assert httpd.server_address[0] == "127.0.0.1", (
            "0.0.0.0 puts a lab laptop's recordings on the conference network")
    finally:
        httpd.server_close()


def test_a_missing_page_is_reported_rather_than_served_empty(tmp_path):
    httpd = lab_mod.make_server(port=0, trainer=lab_mod.StubTrainer(),
                                viewer=tmp_path / "gone.html", quiet=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        base = f"http://127.0.0.1:{httpd.server_address[1]}"
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get(base, "/")
        assert exc.value.code == 500
        assert "broken tree" in exc.value.read().decode("utf-8")
    finally:
        httpd.shutdown()
        httpd.server_close()
        t.join(timeout=5)


# ---------------------------------------------------------------------------
# the shim in an actual browser
# ---------------------------------------------------------------------------

def test_the_shim_parses_and_works_in_a_browser(server):
    """Everything above checks the shim as a **string**.

    A stray brace in it would satisfy every one of those assertions and break
    the panel completely — the page would load, `window.__lab` would be
    undefined, and the training UI would silently look exactly like the public
    site. So the served page gets driven through chromium: the object exists,
    the NDJSON stream arrives as progress callbacks, and a refusal comes back to
    the caller as a thrown error rather than a plausible-looking result.
    """
    pytest.importorskip("playwright.sync_api",
                        reason="the shim needs a browser to be checked in")
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
            page.goto(server + "/", wait_until="load")

            assert page.evaluate("typeof window.__lab") == "object"
            assert page.evaluate("Object.keys(window.__lab).sort()") == \
                ["capabilities", "detect", "train"]

            got = page.evaluate("""async () => {
              const seen = [];
              const t = await window.__lab.train({folds: 3},
                                                 m => seen.push(m.message));
              const d = await window.__lab.detect({model: t.model,
                recordings: [{slice_id: 'r1', rois: [[1.0, 299.0]]}]});
              return {n: seen.length, onsets: d.detections[0].onset_sec};
            }""")
            assert got["n"] == 3, "the progress stream must reach the page"
            assert got["onsets"] == [1, 61, 121, 181, 241]

            refused = page.evaluate("""async () => {
              try {
                await window.__lab.detect({model: 'm1', threshold: 0.9,
                  recordings: [{slice_id: 'r', rois: [[1.0]]}]});
                return 'NOT REFUSED';
              } catch (e) { return e.message; }
            }""")
            assert "not accepted here" in refused, refused
            assert not errors, errors
        finally:
            browser.close()


# ---------------------------------------------------------------------------
# the real trainer, when torch is here
# ---------------------------------------------------------------------------

def test_the_tube_trainer_says_so_plainly_when_torch_is_absent():
    """torch is the optional `dl` extra, and its absence is an ANSWER."""
    tr = lab_mod.TubeTrainer()
    cap = tr.capabilities()
    if tr.available:
        assert cap["trains"] is True and cap["torch"]
    else:
        assert cap["trains"] is False
        assert "bugarach[dl]" in cap["reason"]
        assert "works without it" in cap["reason"]


def test_train_refuses_without_a_spec():
    """The training corpus is SIMULATED from measured statistics. Training on
    the recordings being analysed is the mistake the whole design avoids, so
    the absence of a spec is a refusal rather than a default."""
    tr = lab_mod.TubeTrainer()
    if not tr.available:
        pytest.skip("torch not installed")
    with pytest.raises(lab_mod.BadRequest) as exc:
        tr.train({}, lambda **kw: None)
    assert "spec" in str(exc.value)


def test_train_refuses_a_single_fold():
    tr = lab_mod.TubeTrainer()
    if not tr.available:
        pytest.skip("torch not installed")
    with pytest.raises(lab_mod.BadRequest) as exc:
        tr.train({"spec": {"n_roi": 5}, "folds": 1}, lambda **kw: None)
    assert "held-out" in str(exc.value)


def test_the_server_reproduces_the_published_bakeoff():
    """**This is the one that says the server has no second training path.**

    Point it at the corpus `docs/learned/bakeoff.json` was made from and the
    numbers must come back identical — not close, identical, because the same
    seeds through the same functions on the same machine are deterministic. A
    server that merely *resembled* `fair_bakeoff.py` would pass every other test
    in this file and quietly publish different numbers than the report does.

    ~25 s and it needs torch, so it does not run in CI: `.github/workflows/ci.yml`
    installs `[ui]`, not `[dl]`. That is stated rather than papered over — this
    check runs on a machine that has the training extra, which is every machine
    where anyone can change the thing it guards.

    Cross-machine drift in the float ops is possible in principle; if this ever
    fires with a *small* per-fold difference on a different platform, that is
    the finding, and the tolerance question gets answered then rather than
    pre-loosened now into a check that cannot fail.
    """
    tr = lab_mod.TubeTrainer()
    if not tr.available:
        pytest.skip("torch not installed — CI installs [ui], not [dl]")

    ref = json.loads((ROOT / "docs" / "learned" / "bakeoff.json").read_text())
    model = tr.train({"spec": ref["spec"], "arch": "tube",
                      "folds": ref["folds"],
                      "seeds_per_fold": ref["seeds_per_fold"], "steps": 900},
                     lambda **kw: None)

    want = ref["learned"]["tube"]
    assert model.report["seeds"] == ref["seeds"], (
        "the corpus split must be `bench.fold_split`'s, the same call "
        "`tools/fair_bakeoff.py` makes — a second derivation of the split "
        "agrees right up until somebody changes one of them")
    assert model.n_params == want["n_params"]
    for ours, theirs in zip(model.report["per_fold"], want["per_fold"]):
        where = f"fold {theirs['fold']}"
        # the tolerance is the F1's units and has to come back with it
        assert ours["tol_sec"] is not None, where
        assert ours["n_planted"] == theirs["n_planted"], where
        assert ours["n_detected"] == theirs["n_detected"], where
        assert ours["n_hit"] == theirs["n_hit"], where
        assert ours["threshold"] == pytest.approx(theirs["threshold"]), where
        assert ours["f1"] == pytest.approx(theirs["f1"]), where
    assert model.report["f1"]["mean"] == pytest.approx(want["f1"]["mean"])
