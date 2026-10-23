/* The rater sheet's raster: draws one row of event times, lets a person mark coordinated
 * events, and reports the marks and a real-or-synthetic judgement.
 *
 * Plain ES5 on purpose. It runs inside a Qualtrics question, where no build step or module
 * loader exists, and in the local preview page. No dependencies.
 *
 *   RaterSheet.mount(container, row, onChange) -> {destroy()}
 *     row      {id, n_roi, duration_sec, trains: [[t, ...], ...]}  (times in seconds)
 *     onChange called with {row, judge, marks} on every change; judge is null until chosen.
 *
 * Gestures (house raster navigation, ADR-0015/0016, adapted so a click can mark):
 *   click            mark an event at that time; click on a mark to remove it
 *   drag             zoom box: time only
 *   Shift-drag       slide in time
 *   Ctrl+wheel       zoom time at the cursor (the bare wheel scrolls the page)
 *   double-click     show the whole row
 */
(function (global) {
  "use strict";

  var ROW_PX = 9;            // one ROI's lane
  var AXIS_PX = 30;          // the time axis under the raster
  var LEFT_PX = 8;
  var MARK_HIT_PX = 7;       // a click this close to a mark removes it
  var DRAG_PX = 4;           // movement below this is a click, above it a drag
  var MIN_SPAN_SEC = 2;      // the deepest zoom

  var JUDGEMENTS = [
    ["sure_real", "Sure it is real"],
    ["probably_real", "Probably real"],
    ["probably_synthetic", "Probably synthetic"],
    ["sure_synthetic", "Sure it is synthetic"]
  ];

  // 60-base ticks labelled 45s / 2m / 2m30s (house time axis).
  var TICK_STEPS = [0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600];
  function label(t) {
    var r = Math.round(t * 10) / 10;
    var m = Math.floor(r / 60), s = Math.round((r - 60 * m) * 10) / 10;
    if (m === 0) return s + "s";
    return s === 0 ? m + "m" : m + "m" + s + "s";
  }
  function tickStep(span, px) {
    var want = span / Math.max(2, px / 90);
    for (var i = 0; i < TICK_STEPS.length; i++) if (TICK_STEPS[i] >= want) return TICK_STEPS[i];
    return TICK_STEPS[TICK_STEPS.length - 1];
  }

  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }

  function mount(container, row, onChange) {
    var marks = [];
    var judge = null;
    var view = [0, row.duration_sec];
    var history = [];

    var wrap = el("div", {"class": "rater-sheet", style: "font: 14px/1.4 system-ui, sans-serif; color: #222; max-width: 100%;"});
    var ylab = el("div", {style: "font-size: 12px; color: #555; margin: 4px 0 2px;"},
                  row.n_roi + " ROIs, one per lane; each tick is one calcium event onset");
    var canvas = el("canvas", {style: "display: block; width: 100%; border: 1px solid #bbb; background: #fff; cursor: crosshair; touch-action: none;"});
    var status = el("div", {style: "font-size: 12px; color: #555; margin: 4px 0 10px;"});
    var help = el("div", {style: "font-size: 12px; color: #777; margin-bottom: 10px;"},
                  "Click to mark a coordinated event; click a mark to remove it. Drag to zoom in time, " +
                  "Shift-drag to slide, Ctrl+wheel to zoom at the cursor, double-click to see the whole row.");
    var choice = el("div", {style: "margin: 6px 0;"});
    choice.appendChild(el("div", {style: "font-weight: 600; margin-bottom: 4px;"},
                          "Does this row look like a real recording, or a synthetic one?"));
    var buttons = [];
    JUDGEMENTS.forEach(function (j) {
      var b = el("button", {type: "button", "data-judge": j[0],
                            style: "margin: 0 6px 6px 0; padding: 6px 10px; border: 1px solid #888; border-radius: 4px; background: #f4f4f4; cursor: pointer; font: inherit;"}, j[1]);
      b.addEventListener("click", function () { judge = j[0]; paintButtons(); emit(); });
      buttons.push(b);
      choice.appendChild(b);
    });
    wrap.appendChild(ylab);
    wrap.appendChild(canvas);
    wrap.appendChild(status);
    wrap.appendChild(help);
    wrap.appendChild(choice);
    container.appendChild(wrap);

    var ctx = canvas.getContext("2d");
    var cssW = 0, cssH = row.n_roi * ROW_PX + AXIS_PX;

    function paintButtons() {
      buttons.forEach(function (b) {
        var on = b.getAttribute("data-judge") === judge;
        b.style.background = on ? "#2b5fab" : "#f4f4f4";
        b.style.color = on ? "#fff" : "#222";
        b.style.borderColor = on ? "#2b5fab" : "#888";
      });
    }

    function plotW() { return cssW - 2 * LEFT_PX; }
    function tToX(t) { return LEFT_PX + (t - view[0]) / (view[1] - view[0]) * plotW(); }
    function xToT(x) { return view[0] + (x - LEFT_PX) / plotW() * (view[1] - view[0]); }

    function resize() {
      var dpr = global.devicePixelRatio || 1;
      cssW = Math.max(300, canvas.clientWidth || container.clientWidth || 800);
      canvas.style.height = cssH + "px";
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }

    function draw(box) {
      var h = row.n_roi * ROW_PX;
      ctx.clearRect(0, 0, cssW, cssH);
      for (var i = 0; i < row.n_roi; i++) {
        if (i % 2) { ctx.fillStyle = "#f6f6f6"; ctx.fillRect(LEFT_PX, i * ROW_PX, plotW(), ROW_PX); }
      }
      ctx.strokeStyle = "#111"; ctx.lineWidth = 1.5;
      ctx.beginPath();
      for (var r = 0; r < row.n_roi; r++) {
        var tr = row.trains[r];
        for (var k = 0; k < tr.length; k++) {
          var t = tr[k];
          if (t < view[0] || t > view[1]) continue;
          var x = Math.round(tToX(t)) + 0.5;
          ctx.moveTo(x, r * ROW_PX + 1); ctx.lineTo(x, (r + 1) * ROW_PX - 1);
        }
      }
      ctx.stroke();
      // marks
      ctx.strokeStyle = "rgba(214, 72, 32, 0.85)"; ctx.lineWidth = 2;
      marks.forEach(function (m) {
        if (m < view[0] || m > view[1]) return;
        var x = tToX(m);
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
      });
      // axis
      ctx.strokeStyle = "#888"; ctx.lineWidth = 1; ctx.fillStyle = "#444";
      ctx.font = "11px system-ui, sans-serif"; ctx.textAlign = "center";
      ctx.beginPath(); ctx.moveTo(LEFT_PX, h + 0.5); ctx.lineTo(LEFT_PX + plotW(), h + 0.5); ctx.stroke();
      var step = tickStep(view[1] - view[0], plotW());
      for (var tk = Math.ceil(view[0] / step) * step; tk <= view[1] + 1e-9; tk += step) {
        var xt = Math.round(tToX(tk)) + 0.5;
        ctx.beginPath(); ctx.moveTo(xt, h); ctx.lineTo(xt, h + 5); ctx.stroke();
        ctx.fillText(label(tk), xt, h + 17);
      }
      if (box) {
        ctx.fillStyle = "rgba(43, 95, 171, 0.15)";
        ctx.fillRect(Math.min(box[0], box[1]), 0, Math.abs(box[1] - box[0]), h);
      }
      status.textContent = marks.length + (marks.length === 1 ? " event marked" : " events marked") +
        " · showing " + label(view[0]) + " to " + label(view[1]) + " of " + label(row.duration_sec);
    }

    function setView(a, b, remember) {
      var span = Math.max(MIN_SPAN_SEC, b - a);
      if (span >= row.duration_sec) { a = 0; b = row.duration_sec; }
      else {
        a = Math.max(0, Math.min(a, row.duration_sec - span));
        b = a + span;
      }
      if (remember) history.push(view.slice());
      view = [a, b];
      draw();
    }

    function emit() {
      if (onChange) onChange({row: row.id, judge: judge, marks: marks.slice().sort(function (p, q) { return p - q; })});
    }

    function toggleMark(x) {
      for (var i = 0; i < marks.length; i++) {
        if (Math.abs(tToX(marks[i]) - x) <= MARK_HIT_PX) { marks.splice(i, 1); draw(); emit(); return; }
      }
      var t = Math.round(xToT(x) * 10) / 10;
      if (t < 0 || t > row.duration_sec) return;
      marks.push(t); draw(); emit();
    }

    var down = null;
    function localX(ev) { var r = canvas.getBoundingClientRect(); return ev.clientX - r.left; }
    canvas.addEventListener("pointerdown", function (ev) {
      if (ev.button !== 0) return;
      canvas.setPointerCapture(ev.pointerId);
      down = {x: localX(ev), shift: ev.shiftKey, view: view.slice(), moved: false};
    });
    canvas.addEventListener("pointermove", function (ev) {
      if (!down) return;
      var x = localX(ev);
      if (Math.abs(x - down.x) > DRAG_PX) down.moved = true;
      if (!down.moved) return;
      if (down.shift) {
        var dt = (x - down.x) / plotW() * (down.view[1] - down.view[0]);
        view = down.view.slice();
        setView(down.view[0] - dt, down.view[1] - dt, false);
      } else draw([down.x, x]);
    });
    canvas.addEventListener("pointerup", function (ev) {
      if (!down) return;
      var x = localX(ev), d = down; down = null;
      if (!d.moved) { toggleMark(x); return; }
      if (d.shift) { history.push(d.view); return; }
      var a = xToT(Math.min(d.x, x)), b = xToT(Math.max(d.x, x));
      setView(a, b, true);
    });
    canvas.addEventListener("dblclick", function (ev) { ev.preventDefault(); setView(0, row.duration_sec, true); });
    canvas.addEventListener("wheel", function (ev) {
      if (!ev.ctrlKey) return;        // the bare wheel scrolls the page
      ev.preventDefault();
      var t = xToT(localX(ev)), f = ev.deltaY > 0 ? 1.25 : 0.8;
      setView(t - (t - view[0]) * f, t + (view[1] - t) * f, true);
    }, {passive: false});
    function onKey(ev) {
      if ((ev.ctrlKey || ev.metaKey) && (ev.key === "z" || ev.key === "Z") && history.length && wrap.matches(":hover")) {
        ev.preventDefault();
        var v = history.pop(); view = v; draw();
      }
    }
    document.addEventListener("keydown", onKey);
    global.addEventListener("resize", resize);

    resize();
    emit();
    return {
      destroy: function () {
        document.removeEventListener("keydown", onKey);
        global.removeEventListener("resize", resize);
        if (wrap.parentNode) wrap.parentNode.removeChild(wrap);
      }
    };
  }

  /* One line a Qualtrics export can carry and the scorer can read without a column map. */
  function encode(state) {
    return "row=" + state.row + ";judge=" + (state.judge || "") + ";marks=" +
      state.marks.map(function (m) { return m.toFixed(1); }).join(",");
  }

  global.RaterSheet = {mount: mount, encode: encode, JUDGEMENTS: JUDGEMENTS};
})(typeof window !== "undefined" ? window : this);
