/* The rater sheet's raster: draws one row of event times, lets a person mark coordinated
 * events, and asks how real the row looks on a slider.
 *
 * Plain ES5 on purpose. It runs inside a Qualtrics question, where no build step or module
 * loader exists, and in the local preview page. No dependencies.
 *
 *   RaterSheet.mount(container, row, onChange) -> api
 *     row      {id, n_roi, duration_sec, trains: [[t, ...], ...]}  (times in seconds)
 *     onChange called with {row, real, marks} on every change. real runs from +1 (sure it is
 *     real) through 0 (no idea) to -1 (sure it is synthetic), and is null until the slider is
 *     touched.
 *   RaterSheet.demo(container, row, eventTime, onDone, lane) -> {stop()}
 *     a 30-second animated walk-through of every control, on a row of its own.
 *
 * Navigation follows the house raster rules (ADR-0015/0016), adapted so a click can mark:
 * the buttons above the raster do everything, and the gestures are shortcuts for the same.
 *   click            mark an event; click a mark to remove it
 *   drag             zoom box, time only
 *   Shift-drag       slide in time
 *   Ctrl+wheel       zoom at the cursor (the bare wheel scrolls the page)
 *   double-click     the whole row
 */
(function (global) {
  "use strict";

  var MAX_LANE_PX = 10, MAX_RASTER_PX = 620;   // lanes shrink so 566 ROIs (Cossart) still fit
  var AXIS_PX = 36;          // the time axis under the raster
  var OVERVIEW_PX = 14;      // the strip above the raster showing where the view sits
  var PAD_PX = 10;
  var MARK_HIT_PX = 7;       // a click this close to a mark removes it
  var DRAG_PX = 4;           // movement below this is a click, above it a drag
  var MIN_SPAN_SEC = 2;      // the deepest zoom
  var INK = "#1f1f1f", MUTED = "#4a4a4a", ACCENT = "#2b5fab", MARK = "rgba(214, 72, 32, 0.9)";

  /* ---- the time axis: the house rule for an axis a reader can zoom (bugarach.ui.navigate,
   * ZOOM_LABEL_JS). 60-base ticks; once ticks are closer than a minute, a whole minute reads
   * 12m and the ticks after it carry seconds only; the first label is always in full. */
  var STEPS = [0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800];
  function fullLabel(t) {
    var t10 = Math.round(Math.abs(t) * 10), m = Math.floor(t10 / 600), s10 = t10 - m * 600;
    var secs = s10 % 10 ? (s10 / 10).toFixed(1) : String(s10 / 10);
    if (!m) return secs + "s";
    if (!s10) return m + "m";
    return m + "m" + (s10 < 100 ? "0" : "") + secs + "s";
  }
  function tickLabel(t, step, index) {
    var t10 = Math.round(Math.abs(t) * 10), m = Math.floor(t10 / 600), s10 = t10 - m * 600;
    if (step >= 60 || !s10 || !m || index === 0) return fullLabel(t);
    return (s10 % 10 ? (s10 / 10).toFixed(1) : String(s10 / 10)) + "s";
  }
  function tickStep(span, px) {
    var want = span / Math.max(2, px / 80);
    for (var i = 0; i < STEPS.length; i++) if (STEPS[i] >= want) return STEPS[i];
    return STEPS[STEPS.length - 1];
  }

  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  var BTN = "margin: 0 6px 6px 0; padding: 7px 12px; border: 1px solid #8a8a8a; border-radius: 5px; " +
            "background: #f4f4f4; color: #1f1f1f; cursor: pointer; font: 600 14px system-ui, sans-serif;";

  // A symmetric track, so neither end of the slider looks heavier than the other.
  var SLIDER_CSS = ".rs-range{-webkit-appearance:none;appearance:none;height:8px;border-radius:4px;" +
    "background:linear-gradient(to right,#d8d8d8,#f2f2f2 50%,#d8d8d8);outline-offset:4px}" +
    ".rs-range::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;border-radius:50%;" +
    "background:#9a9a9a;border:2px solid #fff;box-shadow:0 0 0 1px #777;cursor:pointer}" +
    ".rs-range::-moz-range-thumb{width:20px;height:20px;border-radius:50%;background:#9a9a9a;" +
    "border:2px solid #fff;box-shadow:0 0 0 1px #777;cursor:pointer}" +
    ".rs-range.rs-set::-webkit-slider-thumb{background:#2b5fab}.rs-range.rs-set::-moz-range-thumb{background:#2b5fab}";
  function ensureStyle() {
    if (document.getElementById("rs-style")) return;
    var s = document.createElement("style"); s.id = "rs-style"; s.textContent = SLIDER_CSS;
    document.head.appendChild(s);
  }

  function mount(container, row, onChange) {
    ensureStyle();
    var ROW_PX = Math.max(1, Math.min(MAX_LANE_PX, Math.floor(MAX_RASTER_PX / row.n_roi)));
    var marks = [];
    var spans = [];            // the view's width, in seconds, when each mark was placed
    var real = null;
    var view = [0, row.duration_sec];
    var history = [];

    var wrap = el("div", {"class": "rater-sheet", style: "position: relative; font: 15px/1.45 system-ui, sans-serif; color: " + INK + "; max-width: 100%;"});

    var bar = el("div", {style: "display: flex; flex-wrap: wrap; align-items: center; margin: 4px 0 2px;"});
    var buttons = {};
    [["in", "Zoom in  +"], ["out", "Zoom out  −"], ["left", "◀  Earlier"], ["right", "Later  ▶"],
     ["whole", "Whole row"], ["back", "Undo zoom"]].forEach(function (b) {
      var x = el("button", {type: "button", style: BTN, "data-nav": b[0]}, b[1]);
      buttons[b[0]] = x;
      bar.appendChild(x);
    });
    var where = el("div", {style: "font-size: 14px; color: " + MUTED + "; margin: 2px 0 4px;"});
    var canvas = el("canvas", {style: "display: block; width: 100%; border: 1px solid #b5b5b5; background: #fff; cursor: crosshair; touch-action: none;"});
    var status = el("div", {style: "font-size: 15px; font-weight: 600; margin: 6px 0 2px;"});
    var help = el("div", {style: "font-size: 14px; color: " + MUTED + "; margin-bottom: 14px;"},
                  "Click a coordinated event to mark it; click a mark to remove it. If two events sit close " +
                  "together, mark both (zoom in to place them). Shortcuts: drag across " +
                  "a stretch to zoom into it, Shift-drag to slide, Ctrl + mouse wheel to zoom at the cursor, " +
                  "double-click for the whole row.");

    var judge = el("div", {style: "margin: 8px 0 4px; max-width: 640px;"});
    judge.appendChild(el("div", {style: "font-weight: 600; margin-bottom: 6px;"},
                         "How real does this row look?"));
    var slider = el("input", {type: "range", min: "-100", max: "100", step: "1", value: "0",
                              "aria-label": "How real does this row look",
                              "class": "rs-range", style: "width: 100%; margin: 8px 0;"});
    var ends = el("div", {style: "display: flex; justify-content: space-between; font-size: 14px; color: " + MUTED + ";"});
    ends.appendChild(el("span", {}, "Real"));
    ends.appendChild(el("span", {}, "No idea"));
    ends.appendChild(el("span", {}, "Synthetic"));
    var judged = el("div", {style: "font-size: 14px; color: " + MUTED + "; margin-top: 4px;"},
                    "Move the slider to answer. If you have no idea, set it in the middle, but do touch it.");
    judge.appendChild(slider);
    judge.appendChild(ends);
    judge.appendChild(judged);

    wrap.appendChild(el("div", {style: "font-size: 14px; color: " + MUTED + "; margin-bottom: 2px;"},
                        row.n_roi + " ROIs, one per lane. Each tick is one calcium event onset."));
    wrap.appendChild(bar);
    wrap.appendChild(where);
    wrap.appendChild(canvas);
    wrap.appendChild(status);
    wrap.appendChild(help);
    wrap.appendChild(judge);
    container.appendChild(wrap);

    var ctx = canvas.getContext("2d");
    var cssW = 0, rasterTop = OVERVIEW_PX + 6, rasterH = row.n_roi * ROW_PX;
    var cssH = rasterTop + rasterH + AXIS_PX;

    function plotW() { return cssW - 2 * PAD_PX; }
    function tToX(t) { return PAD_PX + (t - view[0]) / (view[1] - view[0]) * plotW(); }
    function xToT(x) { return view[0] + (x - PAD_PX) / plotW() * (view[1] - view[0]); }
    function wholeX(t) { return PAD_PX + t / row.duration_sec * plotW(); }

    function resize() {
      var dpr = global.devicePixelRatio || 1;
      cssW = Math.max(320, canvas.clientWidth || container.clientWidth || 900);
      canvas.style.height = cssH + "px";
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }

    function draw(box) {
      ctx.clearRect(0, 0, cssW, cssH);
      // overview strip: the whole row, with the part on view shaded
      ctx.fillStyle = "#ececec"; ctx.fillRect(PAD_PX, 2, plotW(), OVERVIEW_PX - 4);
      ctx.fillStyle = "rgba(43, 95, 171, 0.55)";
      ctx.fillRect(wholeX(view[0]), 2, Math.max(3, wholeX(view[1]) - wholeX(view[0])), OVERVIEW_PX - 4);
      ctx.fillStyle = MARK;
      marks.forEach(function (m) { ctx.fillRect(wholeX(m) - 1, 2, 2, OVERVIEW_PX - 4); });
      // lanes
      for (var i = 0; i < row.n_roi; i++) {
        if (i % 2 && ROW_PX >= 3) { ctx.fillStyle = "#f5f5f5"; ctx.fillRect(PAD_PX, rasterTop + i * ROW_PX, plotW(), ROW_PX); }
      }
      ctx.strokeStyle = INK; ctx.lineWidth = 1.6;
      ctx.beginPath();
      for (var r = 0; r < row.n_roi; r++) {
        var tr = row.trains[r];
        for (var k = 0; k < tr.length; k++) {
          var t = tr[k];
          if (t < view[0] || t > view[1]) continue;
          var x = Math.round(tToX(t)) + 0.5;
          ctx.moveTo(x, rasterTop + r * ROW_PX + (ROW_PX > 2 ? 1 : 0)); ctx.lineTo(x, rasterTop + (r + 1) * ROW_PX - (ROW_PX > 2 ? 1 : 0));
        }
      }
      ctx.stroke();
      ctx.strokeStyle = MARK; ctx.lineWidth = 2;
      marks.forEach(function (m) {
        if (m < view[0] || m > view[1]) return;
        var x = tToX(m);
        ctx.beginPath(); ctx.moveTo(x, rasterTop); ctx.lineTo(x, rasterTop + rasterH); ctx.stroke();
      });
      // axis
      var y0 = rasterTop + rasterH;
      ctx.strokeStyle = "#6a6a6a"; ctx.lineWidth = 1; ctx.fillStyle = INK;
      ctx.font = "600 13px system-ui, sans-serif"; ctx.textAlign = "center";
      ctx.beginPath(); ctx.moveTo(PAD_PX, y0 + 0.5); ctx.lineTo(PAD_PX + plotW(), y0 + 0.5); ctx.stroke();
      var step = tickStep(view[1] - view[0], plotW()), idx = 0;
      for (var tk = Math.ceil(view[0] / step - 1e-9) * step; tk <= view[1] + 1e-9; tk += step, idx++) {
        var xt = Math.round(tToX(tk)) + 0.5;
        ctx.beginPath(); ctx.moveTo(xt, y0); ctx.lineTo(xt, y0 + 6); ctx.stroke();
        var lab = tickLabel(tk, step, idx), w = ctx.measureText(lab).width / 2;
        ctx.fillText(lab, Math.min(Math.max(xt, PAD_PX + w), PAD_PX + plotW() - w), y0 + 21);
      }
      if (box) {
        ctx.fillStyle = "rgba(43, 95, 171, 0.15)";
        ctx.fillRect(Math.min(box[0], box[1]), rasterTop, Math.abs(box[1] - box[0]), rasterH);
      }
      var whole = view[0] <= 0 && view[1] >= row.duration_sec;
      where.textContent = whole ? "Showing the whole row, " + fullLabel(row.duration_sec) + "."
        : "Showing " + fullLabel(view[0]) + " to " + fullLabel(view[1]) + " of " + fullLabel(row.duration_sec) +
          " (" + fullLabel(view[1] - view[0]) + " wide). The blue band above the raster shows where you are.";
      status.textContent = marks.length + (marks.length === 1 ? " event marked" : " events marked");
      buttons.back.disabled = !history.length;
      buttons.back.style.opacity = history.length ? "1" : "0.45";
    }

    function setView(a, b, remember) {
      var span = Math.max(MIN_SPAN_SEC, b - a);
      if (span >= row.duration_sec) { a = 0; b = row.duration_sec; }
      else { a = Math.max(0, Math.min(a, row.duration_sec - span)); b = a + span; }
      if (remember && (a !== view[0] || b !== view[1])) history.push(view.slice());
      view = [a, b];
      draw();
    }
    function zoomBy(f, at) {
      var c = at == null ? (view[0] + view[1]) / 2 : at;
      setView(c - (c - view[0]) * f, c + (view[1] - c) * f, true);
    }
    function slide(frac) {
      var d = (view[1] - view[0]) * frac;
      setView(view[0] + d, view[1] + d, true);
    }

    function emit() {
      if (onChange) onChange({row: row.id, real: real,
                              marks: order().map(function (i) { return marks[i]; }),
                              spans: order().map(function (i) { return spans[i]; })});
    }
    function order() {
      return marks.map(function (_, i) { return i; }).sort(function (p, q) { return marks[p] - marks[q]; });
    }
    function hitMark(x) {
      for (var i = 0; i < marks.length; i++) if (Math.abs(tToX(marks[i]) - x) <= MARK_HIT_PX) return i;
      return -1;
    }
    function toggleAt(x) {
      var i = hitMark(x);
      if (i >= 0) { marks.splice(i, 1); spans.splice(i, 1); }
      else {
        var t = Math.round(xToT(x) * 10) / 10;
        if (t < 0 || t > row.duration_sec) return;
        marks.push(t);
        spans.push(Math.round((view[1] - view[0]) * 10) / 10);
      }
      draw(); emit();
    }
    function setReal(v) {
      real = Math.max(-1, Math.min(1, v));
      slider.value = String(Math.round(-real * 100));     // real on the left
      slider.classList.add("rs-set");
      var a = Math.abs(real);
      judged.textContent = a < 0.1 ? "Your answer: no idea." :
        "Your answer: " + (a > 0.66 ? "sure" : a > 0.33 ? "probably" : "slightly") + " " +
        (real > 0 ? "real." : "synthetic.");
      emit();
    }
    slider.addEventListener("input", function () { setReal(-Number(slider.value) / 100); });
    slider.addEventListener("pointerdown", function () { if (real === null) setReal(-Number(slider.value) / 100); });
    slider.addEventListener("keydown", function () { if (real === null) setReal(-Number(slider.value) / 100); });

    buttons["in"].onclick = function () { zoomBy(0.5); };
    buttons.out.onclick = function () { zoomBy(2); };
    buttons.left.onclick = function () { slide(-0.5); };
    buttons.right.onclick = function () { slide(0.5); };
    buttons.whole.onclick = function () { setView(0, row.duration_sec, true); };
    buttons.back.onclick = function () { if (history.length) { view = history.pop(); draw(); } };

    var down = null;
    function localX(ev) { var r = canvas.getBoundingClientRect(); return ev.clientX - r.left; }
    function localY(ev) { var r = canvas.getBoundingClientRect(); return ev.clientY - r.top; }
    canvas.addEventListener("pointerdown", function (ev) {
      if (ev.button !== 0) return;
      canvas.setPointerCapture(ev.pointerId);
      var y = localY(ev);
      if (y < rasterTop) {                       // the overview strip: jump there
        var c = (localX(ev) - PAD_PX) / plotW() * row.duration_sec, half = (view[1] - view[0]) / 2;
        setView(c - half, c + half, true);
        return;
      }
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
      if (!d.moved) { toggleAt(x); return; }
      if (d.shift) { history.push(d.view); draw(); return; }
      setView(xToT(Math.min(d.x, x)), xToT(Math.max(d.x, x)), true);
    });
    canvas.addEventListener("dblclick", function (ev) { ev.preventDefault(); setView(0, row.duration_sec, true); });
    canvas.addEventListener("wheel", function (ev) {
      if (!ev.ctrlKey) return;                   // the bare wheel scrolls the page
      ev.preventDefault();
      zoomBy(ev.deltaY > 0 ? 1.25 : 0.8, xToT(localX(ev)));
    }, {passive: false});
    global.addEventListener("resize", resize);

    resize();
    emit();

    // Positions in page pixels, for the demo's pointer.
    function at(elm, fx, fy) {
      var r = elm.getBoundingClientRect(), w = wrap.getBoundingClientRect();
      return {x: r.left - w.left + r.width * (fx == null ? 0.5 : fx), y: r.top - w.top + r.height * (fy == null ? 0.5 : fy)};
    }
    return {
      wrap: wrap,
      destroy: function () {
        global.removeEventListener("resize", resize);
        if (wrap.parentNode) wrap.parentNode.removeChild(wrap);
      },
      setView: setView, zoomBy: zoomBy, slide: slide,
      whole: function () { setView(0, row.duration_sec, true); },
      mark: function (t) { toggleAt(tToX(t)); },
      setReal: setReal,
      pointAtTime: function (t, lane) {
        var p = at(canvas, 0, 0);
        return {x: p.x + tToX(t), y: p.y + rasterTop + (lane == null ? rasterH / 2 : lane * ROW_PX)};
      },
      pointAtButton: function (name) { return at(buttons[name]); },
      pointAtSlider: function (v) { return at(slider, (1 - v) / 2, 0.5); },
      pointAtCanvas: function () { return at(canvas, 0.5, 0.5); },
      boxPreview: function (t0, t1) { draw([tToX(t0), tToX(t1)]); },
      reset: function () { marks = []; spans = []; real = null; history = []; slider.value = "0";
        slider.classList.remove("rs-set"); view = [0, row.duration_sec]; draw(); emit(); }
    };
  }

  /* ---- the 30-second walk-through ---- */
  function demo(container, row, eventTime, onDone, lane) {
    var LANE = lane == null ? Math.floor(row.n_roi / 2) : lane;
    var box = el("div", {style: "position: relative;"});
    container.appendChild(box);
    var sheet = mount(box, row, null);
    sheet.wrap.style.pointerEvents = "none";
    var caption = el("div", {style: "font: 600 16px/1.4 system-ui, sans-serif; color: #fff; background: rgba(31, 31, 31, 0.88); " +
                                    "padding: 8px 12px; border-radius: 6px; margin: 0 0 8px; min-height: 2.8em;"});
    box.insertBefore(caption, box.firstChild);
    var cursor = el("div", {style: "position: absolute; left: 0; top: 0; width: 18px; height: 18px; border-radius: 50%; " +
                                   "background: rgba(214, 72, 32, 0.85); border: 2px solid #fff; box-shadow: 0 0 0 1px #d64820; " +
                                   "transform: translate(-50%, -50%); transition: left 0.9s ease, top 0.9s ease, transform 0.15s; " +
                                   "pointer-events: none; z-index: 5;"});
    sheet.wrap.appendChild(cursor);
    var timers = [];
    function moveTo(p) { cursor.style.left = p.x + "px"; cursor.style.top = p.y + "px"; }
    function press() {
      cursor.style.transform = "translate(-50%, -50%) scale(0.7)";
      timers.push(setTimeout(function () { cursor.style.transform = "translate(-50%, -50%)"; }, 180));
    }
    var span = 40, a = Math.max(0, eventTime - span / 2), b = a + span;
    var steps = [
      [0, function () { sheet.reset(); moveTo(sheet.pointAtCanvas());
        caption.textContent = "Each row is " + fullLabel(row.duration_sec) + " of " + row.n_roi + " cells, one per lane. Each tick is one calcium event."; }],
      [4000, function () { caption.textContent = "A coordinated event is many cells becoming active together. At this width they are hard to see, so zoom in.";
        moveTo(sheet.pointAtTime(a, LANE)); }],
      [7500, function () { caption.textContent = "Drag across a stretch to zoom into it."; press(); }],
      [8000, function () { moveTo(sheet.pointAtTime(b, LANE)); }],
      [8600, function () { sheet.boxPreview(a, b); }],
      [9200, function () { sheet.setView(a, b, true); }],
      [10500, function () { caption.textContent = "Or use the buttons: zoom in and out, slide earlier and later.";
        moveTo(sheet.pointAtButton("right")); }],
      [12000, function () { press(); sheet.slide(0.5); }],
      [13000, function () { moveTo(sheet.pointAtButton("left")); }],
      [14000, function () { press(); sheet.slide(-0.5); }],
      [15000, function () { caption.textContent = "Click the event to mark it.";
        moveTo(sheet.pointAtTime(eventTime, LANE + 0.5)); }],
      [16300, function () { press(); sheet.mark(eventTime); }],
      [17800, function () { caption.textContent = "Clicked by mistake? Click the mark again to remove it."; press(); sheet.mark(eventTime); }],
      [19300, function () { press(); sheet.mark(eventTime); caption.textContent = "Marked again."; }],
      [20500, function () { caption.textContent = "Whole row takes you back out. Undo zoom steps back one view.";
        moveTo(sheet.pointAtButton("whole")); }],
      [21800, function () { press(); sheet.whole(); }],
      [23000, function () { caption.textContent = "Last, say how real the row looks: real on the left, no idea in the middle, synthetic on the right.";
        moveTo(sheet.pointAtSlider(0)); }],
      [24600, function () { press(); moveTo(sheet.pointAtSlider(0.45)); sheet.setReal(0.45); }],
      [26200, function () { moveTo(sheet.pointAtSlider(-0.2)); sheet.setReal(-0.2); }],
      [27800, function () { caption.textContent = "If two events sit close together, mark both. Then Next. Some rows have none at all."; }],
      [30000, function () { cursor.style.display = "none"; if (onDone) onDone(); }]
    ];
    steps.forEach(function (s) { timers.push(setTimeout(s[1], s[0])); });
    return {
      stop: function () {
        timers.forEach(clearTimeout);
        sheet.destroy();
        if (box.parentNode) box.parentNode.removeChild(box);
      }
    };
  }

  /* One line a Qualtrics export can carry and the scorer can read without a column map. */
  function encode(state) {
    return "row=" + state.row + ";real=" + (state.real == null ? "" : state.real.toFixed(2)) + ";marks=" +
      state.marks.map(function (m) { return m.toFixed(1); }).join(",") +
      ";spans=" + (state.spans || []).map(function (w) { return w.toFixed(1); }).join(",");
  }

  global.RaterSheet = {mount: mount, demo: demo, encode: encode};
})(typeof window !== "undefined" ? window : this);
