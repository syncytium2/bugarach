"""``bugarach lab`` — the local server that trains the tube off the page.

The decision is [`docs/adr/0001-the-lab-server.md`](../../docs/adr/0001-the-lab-server.md)
and the shape below is that ADR made executable. The short version: the published
page owns the interface and reaches nothing; **this** server owns the transport,
exists only on loopback, and hands out a copy of the same page with a shim
appended. Nothing is stripped at build time, so nothing can fail to be stripped —
the training panel is dead on the public site by *absence* of ``window.__lab``.

Four properties are load-bearing, and each is enforced here rather than
remembered:

**The only ``fetch(`` in the system lives in** :data:`SHIM`. It is appended to the
page in the response body and exists nowhere on disk under ``docs/site/``, which
is why ``tests/test_site_viewer.py`` and ``tools/build_site.py`` need no edit and
still pass against the source they always scanned.

**No filesystem access from a request.** The page already holds the user's folder
through the File System Access API and posts event trains as JSON. There is
exactly one path this module ever opens — :data:`VIEWER`, a module constant — and
no request may name it, extend it or select it. There is no traversal surface to
get wrong because there is no path handling at all.

**Loopback, explicitly.** ``127.0.0.1`` and never ``0.0.0.0``; a lab laptop on a
conference network is the case that rule protects. The ``Host`` header is checked
too, because binding loopback alone does not stop a hostile page in another tab
from pointing a name that resolves to 127.0.0.1 at this server.

**One training path.** :func:`bugarach.learn.train.train` and
:func:`bugarach.bench.pool_scores` — the functions every number in
``docs/learned/bakeoff.json`` came from. A second implementation would be free to
drift from the one the published figures were made with, and this repo has
already paid for a metric that forked in silence (see ``pool_scores``' docstring).

The rule the server does not get to relax
-----------------------------------------
**The threshold is never re-picked on the recording being analysed.** It is chosen
inside :func:`~bugarach.learn.train.pick_threshold` on held-out
training-regime data and travels with the model. ``/api/detect`` therefore
*refuses* a request carrying a threshold rather than ignoring it — a silently
dropped knob teaches a caller the knob works. Moving training to a process with
more room does not make a "re-tune on this slice" button acceptable; it hides
exactly the failure ``docs/learned/regime_shift_fitted.json`` measures.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"
"""The one file this server reads. A module constant, never a request parameter."""

DEFAULT_PORT = 8788
"""Claimed on the machine-local board. 5006 is ``bugarach view``'s."""

MAX_BODY = 64 * 1024 * 1024
"""A recording of event times is small; a body larger than this is a mistake or
an attack, and either way answering it is not this server's job."""


# ---------------------------------------------------------------------------
# the shim — the only fetch( in the system
# ---------------------------------------------------------------------------

SHIM = """
<script>
/* bugarach lab shim — appended by `bugarach lab`, and by nothing else.
 *
 * THIS BLOCK IS THE REASON THE PAGE ABOVE STAYS HONEST. Everything that talks
 * to a host is here, in a copy that only ever leaves 127.0.0.1. The file this
 * was appended to contains no transport and is byte-identical to what the
 * public site publishes -- `tests/test_lab_server.py` asserts both halves.
 *
 * The panel in the page is inert unless `window.__lab` exists, so the public
 * copy is dead by ABSENCE. Nothing was removed, so nothing can fail to be
 * removed.
 */
(function () {
  "use strict";

  async function post(path, body, onProgress) {
    const r = await fetch(path, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok || !r.body) {
      const text = await r.text().catch(function () { return ""; });
      throw new Error("lab " + path + " failed (" + r.status + "): " + text);
    }
    /* The response is NDJSON: progress lines, then exactly one terminal line
     * that is either {event:"result"} or {event:"error"}. Read it as a stream
     * so a 900-step fit reports per-fold progress instead of looking hung. */
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = "", out = null, err = null;
    for (;;) {
      const chunk = await reader.read();
      if (chunk.done) break;
      buf += dec.decode(chunk.value, { stream: true });
      let nl;
      while ((nl = buf.indexOf("\\n")) >= 0) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;
        const msg = JSON.parse(line);
        if (msg.event === "progress") { if (onProgress) onProgress(msg); }
        else if (msg.event === "result") { out = msg; }
        else if (msg.event === "error") { err = msg; }
      }
    }
    if (err) throw new Error(err.message || "lab error");
    if (!out) throw new Error("lab " + path + " ended without a result");
    return out;
  }

  window.__lab = {
    /* What this server can actually do right now -- torch is the optional `dl`
     * extra, and its ABSENCE IS AN ANSWER, not an error to work around. The
     * panel reads this and says so plainly; every other stage keeps working. */
    capabilities: async function () {
      const r = await fetch("/api/capabilities");
      if (!r.ok) throw new Error("lab capabilities failed (" + r.status + ")");
      return r.json();
    },

    /* Fit on a corpus GENERATED FROM `spec` -- the measured statistics of the
     * user's own untreated recordings, which the page derived upstairs. The
     * user's recordings are not the training set: simulating a treatment would
     * spend the effect the experiment exists to measure. Returns held-out
     * fold scores and a handle for detect(). */
    train: function (req, onProgress) { return post("/api/train", req, onProgress); },

    /* Run a fitted model over recordings the page holds. The threshold travels
     * WITH the model and cannot be passed here -- the server refuses a request
     * that carries one rather than ignoring it. */
    detect: function (req, onProgress) { return post("/api/detect", req, onProgress); },
  };
})();
</script>
"""


def page_with_shim(html: str) -> str:
    """The published page plus the transport, joined only in a response body.

    Appended rather than injected: there is no marker in the page to find, so
    there is nothing a build could accidentally leave behind or a reviewer has
    to trust was removed.
    """
    return html + SHIM


# ---------------------------------------------------------------------------
# building a recording out of what the page posts
# ---------------------------------------------------------------------------

class BadRequest(Exception):
    """A request this server refuses, with the reason a caller can act on."""


def slice_from_request(rec: dict, *, index: int):
    """One posted recording -> a :class:`~bugarach.store.Slice`.

    The page sends what the import contract already defines — a recording id and
    per-ROI onset times in seconds on the recording's own clock. This is the
    whole of the server's input surface: no path, no filename, no handle to
    anything on disk.
    """
    if not isinstance(rec, dict):
        raise BadRequest(f"recording {index} must be an object, got {type(rec).__name__}")
    rois = rec.get("rois")
    if not isinstance(rois, list) or not rois:
        raise BadRequest(
            f"recording {index} has no 'rois' — expected a list of per-ROI "
            f"arrays of onset times in seconds")
    trains = []
    for r, v in enumerate(rois):
        if not isinstance(v, list):
            raise BadRequest(f"recording {index} ROI {r} must be an array of seconds")
        try:
            trains.append([float(x) for x in v])
        except (TypeError, ValueError) as exc:
            raise BadRequest(
                f"recording {index} ROI {r} carries a non-numeric onset: {exc}") from exc

    from bugarach.io import slice_from_events

    slice_id = rec.get("slice_id")
    if not isinstance(slice_id, str) or not slice_id.strip():
        raise BadRequest(
            f"recording {index} needs a 'slice_id' — it comes from the data and "
            f"is never a filename (docs/webapp_spec.md)")
    return slice_from_events(trains, slice_id=slice_id)


# ---------------------------------------------------------------------------
# the trainers — a seam, so the endpoints are checkable before the real fit
# ---------------------------------------------------------------------------

@dataclass
class Model:
    """A fitted model the server holds, and what it cost to fit.

    ``threshold`` is here and **nowhere in the detect request**: it was chosen on
    held-out training-regime data and travels with the model.
    """

    handle: str
    arch: str
    threshold: float
    dt: float
    n_params: int
    trainer: str
    predict: object = None
    report: dict = field(default_factory=dict)


class StubTrainer:
    """A trainer that fits nothing and calls an event a minute.

    It exists so the transport, the request and response shapes, the progress
    stream and the refusals can all be tested **before** any real numerics land
    behind them — the same reason ``docs/webapp_spec.md`` settles the output
    contract before the code that fills it. A test using this is testing the
    seam, and it can say so.
    """

    name = "stub"
    available = True
    period_sec = 60.0

    def capabilities(self) -> dict:
        return {"trains": True, "reason": None}

    def train(self, req: dict, emit) -> Model:
        folds = int(req.get("folds", 4))
        for f in range(folds):
            emit(stage="fold", fold=f, of=folds,
                 message=f"stub fold {f + 1}/{folds}")
        return Model(handle="", arch=str(req.get("arch", "tube")),
                     threshold=0.5, dt=float(req.get("dt", 0.1)),
                     n_params=0, trainer=self.name,
                     predict=self._predict,
                     report={"stub": True, "folds": folds})

    def _predict(self, model: Model, slice_):
        """One detection a minute, spanning the recording's own extent."""
        import numpy as np

        from bugarach.detectors.rate import recording_extent

        t0, t1 = recording_extent(slice_)
        onsets = np.arange(float(t0), float(t1), self.period_sec)
        return dict(onset_sec=onsets.tolist(),
                    width_sec=[model.dt] * onsets.size,
                    threshold=model.threshold)


class TubeTrainer:
    """The real fit: :func:`bugarach.learn.train.train` and nothing beside it.

    torch is the optional ``dl`` extra. When it is missing this reports that
    plainly through ``/api/capabilities`` and refuses ``/api/train`` with the
    install line — it is not an error to be worked around, and every other stage
    of the page keeps working without it.
    """

    name = "tube"

    #: The learning rates `tools/fair_bakeoff.py` used for the published run.
    #: Quoted from there rather than re-picked, because a rate chosen here would
    #: make this server's numbers a different experiment from `bakeoff.json`.
    LR = {"tube": 1e-2, "trace": 1e-3, "tiny": 1e-3}

    @property
    def available(self) -> bool:
        try:
            import torch  # noqa: F401
        except Exception:
            return False
        return True

    def capabilities(self) -> dict:
        if self.available:
            import torch
            return {"trains": True, "reason": None, "torch": torch.__version__}
        return {"trains": False, "torch": None,
                "reason": "PyTorch is not installed. Training is the optional "
                          "extra: `pip install bugarach[dl]`. Every other stage "
                          "of this page works without it."}

    def train(self, req: dict, emit) -> Model:
        if not self.available:
            raise BadRequest(self.capabilities()["reason"])
        return _train_tube(self, req, emit)

    def _predict(self, model: Model, slice_):
        det, enc = model.report["_trained"].predict(slice_)
        return dict(onset_sec=[float(x) for x in det.onset_sec],
                    width_sec=[float(x) for x in det.width_sec],
                    threshold=float(det.threshold), dt=float(enc.dt))


def _train_tube(trainer: TubeTrainer, req: dict, emit) -> Model:
    """Fold split, fit, score on the held-out fold — `fair_bakeoff.py`'s shape.

    Deliberately the same procedure, because ``bakeoff.json`` is what this is
    checked against: one corpus, one selection procedure, one scoring rule, and
    every number reported across folds with its spread. Divergence here would
    make agreement with that file impossible to interpret.
    """
    import statistics
    import time

    import numpy as np

    from bugarach.bench import pool_scores
    from bugarach.learn.train import train
    from bugarach.score import score_stream
    from bugarach.simulate import simulate_coordination

    spec = req.get("spec")
    if not isinstance(spec, dict) or not spec:
        raise BadRequest(
            "train needs a 'spec' — the generator settings measured from the "
            "user's own untreated recordings. The training corpus is simulated "
            "from those, never from the recordings being analysed.")
    arch = str(req.get("arch", "tube"))
    folds = int(req.get("folds", 4))
    per_fold_seeds = int(req.get("seeds_per_fold", 2))
    steps = int(req.get("steps", 900))
    if folds < 2:
        raise BadRequest(
            f"folds={folds}: with fewer than two folds there is no held-out "
            f"fold, and an in-sample score is not a result.")

    seeds = [1000 + i for i in range(folds * per_fold_seeds)]
    fold_of = {s: i // per_fold_seeds for i, s in enumerate(seeds)}

    cache: dict[int, tuple] = {}

    def rec(seed):
        if seed not in cache:
            cache[seed] = simulate_coordination(seed=seed, **spec)
        return cache[seed]

    emit(stage="corpus", message=f"generating {len(seeds)} recordings", of=len(seeds))
    for i, s in enumerate(seeds):
        rec(s)
        emit(stage="corpus", fold=None, done=i + 1, of=len(seeds),
             message=f"recording {i + 1}/{len(seeds)}")

    per_fold, last = [], None
    for held in range(folds):
        tr_seeds = [s for s in seeds if fold_of[s] != held]
        te_seeds = [s for s in seeds if fold_of[s] == held]
        emit(stage="fit", fold=held, of=folds,
             message=f"fitting {arch} on fold {held + 1}/{folds}")

        # `train` asks for recordings by seed; hand it the TRAINING folds only,
        # indexed through their own list. The held-out fold is unreachable from
        # here by construction rather than by discipline.
        def mk(seed, _t=tuple(tr_seeds)):
            return rec(_t[seed % len(_t)])

        t0 = time.perf_counter()
        tr = train(arch, mk, n_train=min(10, len(tr_seeds)), steps=steps,
                   crop=4096, batch=3, lr=trainer.LR.get(arch, 1e-3))
        train_sec = time.perf_counter() - t0
        last = tr

        te = [rec(s) for s in te_seeds]
        t1 = time.perf_counter()
        dets = [tr.predict(sl)[0] for sl, _ in te]
        detect_sec = time.perf_counter() - t1
        scs = [score_stream(gt, d) for (sl, gt), d in zip(te, dets)]
        p = pool_scores(scs, detector=arch, regime="heldout", seeds=te_seeds)
        per_fold.append(dict(
            fold=held, f1=p.f1, recall=p.recall, precision=p.precision,
            n_planted=p.n_planted, n_hit=p.n_hit, n_detected=p.n_detected,
            hot_fa=p.hot_fa, threshold=float(tr.threshold),
            train_sec=train_sec, detect_sec=detect_sec,
            n_params=int(tr.n_params)))
        emit(stage="scored", fold=held, of=folds, f1=float(p.f1),
             message=f"fold {held + 1}/{folds}: F1 {p.f1:.3f}")

    def spread(key):
        v = [f[key] for f in per_fold
             if f[key] is not None and np.isfinite(f[key])]
        if not v:
            return dict(n=0, mean=None, sd=None, min=None, max=None)
        return dict(n=len(v), mean=float(np.mean(v)),
                    sd=float(statistics.stdev(v)) if len(v) > 1 else 0.0,
                    min=float(min(v)), max=float(max(v)))

    return Model(
        handle="", arch=arch, threshold=float(last.threshold), dt=float(last.dt),
        n_params=int(last.n_params), trainer=trainer.name,
        predict=trainer._predict,
        report={
            "_trained": last,
            "per_fold": per_fold, "folds": folds, "seeds": seeds,
            "seeds_per_fold": per_fold_seeds, "steps": steps,
            "f1": spread("f1"), "recall": spread("recall"),
            "precision": spread("precision"),
            "train_sec": spread("train_sec"), "detect_sec": spread("detect_sec"),
        })


# ---------------------------------------------------------------------------
# the server
# ---------------------------------------------------------------------------

@dataclass
class Lab:
    """Server state: the fitted models, and the trainer behind them."""

    trainer: object
    models: dict = field(default_factory=dict)
    _n: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def put(self, model: Model) -> Model:
        with self._lock:
            self._n += 1
            model.handle = f"m{self._n}"
            self.models[model.handle] = model
        return model

    def get(self, handle) -> Model:
        if not isinstance(handle, str) or handle not in self.models:
            raise BadRequest(
                f"no model {handle!r} on this server — call train() first. "
                f"Models live in this process and do not survive a restart, "
                f"which is deliberate: a fitted model cached on disk outlives "
                f"the settings that produced it.")
        return self.models[handle]


def _public(model: Model) -> dict:
    """The model as the page may see it — no torch objects, no private keys."""
    report = {k: v for k, v in model.report.items() if not k.startswith("_")}
    return dict(model=model.handle, arch=model.arch, trainer=model.trainer,
                threshold=model.threshold, dt=model.dt,
                n_params=model.n_params, **report)


class LabHandler(BaseHTTPRequestHandler):
    """Five routes, no path handling, and one file on disk."""

    protocol_version = "HTTP/1.1"
    server_version = "bugarach-lab"
    sys_version = ""

    lab: Lab = None          # set by serve()
    viewer: Path = VIEWER
    quiet: bool = False

    # -- plumbing ----------------------------------------------------------
    def log_message(self, fmt, *a):
        if not self.quiet:
            super().log_message(fmt, *a)

    def _guard(self) -> bool:
        """Refuse anything that did not come from this machine, by name too.

        Binding 127.0.0.1 stops a packet from the network. It does **not** stop
        a page in another tab from resolving a hostname it controls to 127.0.0.1
        and posting here — DNS rebinding, and the browser will happily send it.
        So the Host header has to be loopback as well, which no rebound name is.
        """
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        if host not in ("127.0.0.1", "localhost", "::1", ""):
            self._json(403, {"error": (
                f"refused a request for Host {host!r}. This server answers "
                f"127.0.0.1 only — a name that resolves here from somewhere "
                f"else is the rebinding case, not a caller.")})
            return False
        peer = (self.client_address or ("",))[0]
        if peer not in ("127.0.0.1", "::1", "::ffff:127.0.0.1"):
            self._json(403, {"error": f"refused a request from {peer}"})
            return False
        return True

    def _send(self, code, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # This page reads the user's recordings. Nothing about it should be
        # cached, embedded in a frame, or sniffed into another type.
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise BadRequest(f"request body of {n} bytes exceeds {MAX_BODY}")
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError as exc:
            raise BadRequest(f"body is not JSON: {exc}") from exc

    # -- routes ------------------------------------------------------------
    def do_GET(self):
        if not self._guard():
            return
        route = self.path.split("?", 1)[0]
        if route in ("/", "/index.html", "/viewer.html"):
            return self._page()
        if route == "/api/capabilities":
            return self._json(200, self._capabilities())
        self._json(404, {"error": f"no route {route!r}"})

    def do_POST(self):
        if not self._guard():
            return
        route = self.path.split("?", 1)[0]
        if route not in ("/api/train", "/api/detect"):
            return self._json(404, {"error": f"no route {route!r}"})
        try:
            req = self._body()
        except BadRequest as exc:
            return self._json(400, {"error": str(exc)})
        self._stream(route, req)

    def _capabilities(self) -> dict:
        cap = dict(self.lab.trainer.capabilities())
        cap.update(trainer=self.lab.trainer.name,
                   models=sorted(self.lab.models),
                   viewer=self.viewer.name)
        return cap

    def _page(self):
        """The published page, from disk, with the shim appended.

        Read per request rather than cached, so editing the page and reloading
        shows the edit — the panel this serves is a code path CI never renders,
        which is the rot the ADR names, and making it awkward to look at would
        be the surest way to let it happen.
        """
        try:
            html = self.viewer.read_text(encoding="utf-8")
        except OSError as exc:
            return self._json(500, {"error": (
                f"cannot read {self.viewer.name}: {exc}. That file is the page "
                f"this server exists to hand out; a lab server with no page is "
                f"a broken tree, not a degraded environment.")})
        self._send(200, page_with_shim(html).encode("utf-8"),
                   "text/html; charset=utf-8")

    # -- the NDJSON stream -------------------------------------------------
    def _stream(self, route: str, req: dict):
        """Progress lines, then exactly one terminal line.

        Chunked rather than one JSON body because a 900-step fit over four folds
        runs for minutes, and a page that cannot show progress is a page that
        looks hung. The terminal line is always sent, ``result`` or ``error``,
        so the shim never waits on a stream that quietly stopped.
        """
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        def line(obj):
            data = (json.dumps(obj) + "\n").encode("utf-8")
            self.wfile.write(b"%X\r\n" % len(data) + data + b"\r\n")
            self.wfile.flush()

        def emit(**kw):
            line(dict(event="progress", **kw))

        try:
            out = (self._train(req, emit) if route == "/api/train"
                   else self._detect(req, emit))
            line(dict(event="result", **out))
        except BadRequest as exc:
            line(dict(event="error", message=str(exc)))
        except Exception as exc:                     # noqa: BLE001
            # The stream has already been committed with a 200, so an
            # unexpected failure cannot become a status code — it has to be
            # reported IN the stream or the caller hangs on a dead socket.
            line(dict(event="error",
                      message=f"{type(exc).__name__}: {exc}"))
        finally:
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()

    def _train(self, req: dict, emit) -> dict:
        model = self.lab.put(self.lab.trainer.train(req, emit))
        return _public(model)

    def _detect(self, req: dict, emit) -> dict:
        # Refused, not ignored. A knob that is silently dropped teaches the
        # caller it works, and this is the one knob the ADR says the server
        # does not get to offer.
        for banned in ("threshold", "thr", "min_rois", "retune", "calibrate"):
            if banned in req:
                raise BadRequest(
                    f"'{banned}' is not accepted here. The operating point is "
                    f"chosen on held-out training-regime data and travels with "
                    f"the model; re-picking it on the recording being analysed "
                    f"hides exactly the failure the regime-shift test measures "
                    f"(docs/adr/0001-the-lab-server.md).")
        model = self.lab.get(req.get("model"))
        recs = req.get("recordings")
        if not isinstance(recs, list) or not recs:
            raise BadRequest("detect needs a non-empty 'recordings' list")

        out = []
        for i, r in enumerate(recs):
            sl = slice_from_request(r, index=i)
            emit(stage="detect", done=i, of=len(recs), slice_id=sl.slice_id,
                 message=f"detecting on {sl.slice_id} ({i + 1}/{len(recs)})")
            det = model.predict(model, sl)
            out.append(dict(slice_id=sl.slice_id, **det))
        return dict(model=model.handle, arch=model.arch, detections=out)


def make_server(*, port: int = DEFAULT_PORT, trainer=None, viewer: Path = VIEWER,
                quiet: bool = False) -> ThreadingHTTPServer:
    """A bound, not-yet-serving server. Loopback only — the bind is the guard.

    Exposed separately from :func:`serve` so a test can bind port 0, drive the
    real handler over a real socket, and shut it down. A transport tested
    through anything but a socket is a transport whose framing is untested.
    """
    lab = Lab(trainer=trainer if trainer is not None else TubeTrainer())
    handler = type("_Bound", (LabHandler,),
                   {"lab": lab, "viewer": Path(viewer), "quiet": quiet})
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    httpd.lab = lab
    return httpd


def serve(*, port: int = DEFAULT_PORT, trainer=None, viewer: Path = VIEWER,
          open_browser: bool = False) -> int:
    """Run until interrupted. Prints the URL and what the trainer can do."""
    httpd = make_server(port=port, trainer=trainer, viewer=viewer)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    cap = httpd.lab.trainer.capabilities()

    print(f"bugarach lab — {url}")
    print(f"  serving {Path(viewer).name} from disk, with the __lab shim appended")
    print(f"  trainer: {httpd.lab.trainer.name}", end="")
    if cap.get("trains"):
        print(f" (ready{', torch ' + cap['torch'] if cap.get('torch') else ''})")
    else:
        print("\n  ⚠ training unavailable — " + str(cap.get("reason")))
    print("  loopback only; the published page is untouched. Ctrl-C to stop.")

    if open_browser:
        import webbrowser
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0
