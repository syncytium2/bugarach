"""Navigating a page of rasters the way Igor Pro navigates a graph.

Tony, 2026-10-13, asked for Igor's graph gestures on the HTML rasters and ruled on the
three places they collide with what the pages did before
(`docs/adr/0015-raster-pages-navigate-the-way-igor-does.md`):

- **Drag a box to zoom.** Across is time, and every recording on the page follows because
  the panels share one time range. Igor draws a marquee and then asks which way to expand;
  here the direction of the drag is the answer, so there is no menu.
- **Down is row pitch, not a crop.** A vertical drag picks rows of one recording and that
  panel is redrawn taller, with longer marks. The ROI axis is an index, so a plain y-zoom
  that left the panel the same height would only hide rows.
- **Shift-drag slides** the time axis. Plain drag used to; the box has it now.
- **Ctrl+wheel zooms** time at the cursor. The bare wheel still scrolls the page.
- **Double-click shows everything; Ctrl+Z steps back** one view at a time.

Two halves. :func:`navigation_hook` sets up the bokeh tools on each panel, where a test can
read them off the model. :func:`add_navigation` appends one script to the saved page for
what bokeh has no tool for: the Shift swap, the view history, the row pitch and the bar at
the bottom of the window that says what the gestures are.
"""
from __future__ import annotations

#: On every panel the script should drive.
NAV_TAG = "bugarach-nav"
#: On a raster, whose rows can be re-pitched. A lane has rows nobody needs taller.
PITCH_TAG = "bugarach-row-pitch"

#: Rows picked by a vertical drag are drawn at least this tall.
ZOOMED_ROW_PX = 12
#: And the panel showing them is never taller than this, however many were picked.
ZOOMED_PANEL_MAX_PX = 600


def navigation_hook(row_pitch: bool = False):
    """A HoloViews hook giving one panel the box zoom and the Ctrl+wheel zoom.

    Runs after ``_time_axis_hook``, which pins every zoom tool to x. ``row_pitch`` lets the
    box take a vertical drag as well; leave it off for a lane.
    """
    def hook(plot, element):
        from bokeh.models import BoxZoomTool, CustomJS, PanTool, WheelZoomTool

        fig = plot.state
        toolbar = fig.toolbar
        tools = [t for t in toolbar.tools if not isinstance(t, BoxZoomTool)]
        box = BoxZoomTool(dimensions="auto" if row_pitch else "width")
        toolbar.tools = tools + [box]
        toolbar.active_drag = box
        for tool in tools:
            if isinstance(tool, PanTool):
                tool.dimensions = "width"
            if isinstance(tool, WheelZoomTool):
                tool.dimensions = "width"
                tool.modifiers = {"ctrl": True}
                toolbar.active_scroll = tool
        fig.tags = list(fig.tags) + [NAV_TAG] + ([PITCH_TAG] if row_pitch else [])
        # Deferred a tick: bokeh's box zoom answers a double-click itself by undoing its
        # last zoom, and whichever of the two runs second is the view the reader gets.
        fig.js_on_event("doubletap", CustomJS(
            code="setTimeout(() => window.bugarachNav && window.bugarachNav.reset(), 0);"))
    return hook


NAV_SCRIPT = r"""
<style>
  body { padding-bottom: 44px; }
  #bugarachNavBar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000;
    display: flex; flex-wrap: wrap; align-items: center; gap: 6px 14px;
    padding: 6px 12px; background: #f6f6f4; border-top: 1px solid #c9c9c4;
    font: 12px system-ui, sans-serif; color: #333; }
  #bugarachNavBar button { font: inherit; padding: 2px 9px; cursor: pointer; }
  #bugarachNavBar button:disabled { cursor: default; }
  #bugarachNavBar b { font-weight: 600; }
</style>
<div id="bugarachNavBar">
  <button id="bugarachNavAll" disabled>show everything</button>
  <button id="bugarachNavBack" disabled>back one view</button>
  <span><b>drag a box</b> to zoom: across is time on every recording, down makes
    those rows taller</span>
  <span><b>Shift-drag</b> slides</span>
  <span><b>Ctrl+wheel</b> zooms time</span>
  <span><b>double-click</b> shows everything</span>
  <span><b>Ctrl+Z</b> goes back one view</span>
</div>
<script>
(function () {
  const NAV_TAG = "__NAV_TAG__", PITCH_TAG = "__PITCH_TAG__";
  const ZOOMED_ROW_PX = __ZOOMED_ROW_PX__, ZOOMED_PANEL_MAX_PX = __ZOOMED_PANEL_MAX_PX__;

  function figures() {
    const doc = window.Bokeh && Bokeh.documents && Bokeh.documents[0];
    if (!doc) return [];
    const all = doc.all_models;
    const models = Array.from(all.values ? all.values() : all);
    return models.filter(m => Array.isArray(m.tags) && m.tags.includes(NAV_TAG));
  }

  function start() {
    const figs = figures();
    // inner_height is filled in by the first layout; before it the panels have no size
    if (!figs.length || !figs.every(f => f.inner_height > 0))
      return setTimeout(start, 100);

    const xr = figs[0].x_range;
    const rows = figs.map(f => {
      const sized = [];
      for (const r of f.renderers) {
        const g = r.glyph;
        if (g && g.size && typeof g.size.value === "number")
          sized.push({ glyphs: [g, r.nonselection_glyph, r.selection_glyph,
                                r.hover_glyph, r.muted_glyph]
                         .filter(x => x && x.size !== undefined),
                       size: g.size.value });
      }
      return { fig: f, pitch: f.tags.includes(PITCH_TAG),
               y0: [f.y_range.start, f.y_range.end],
               height: f.height, inner: f.inner_height, sized };
    });

    let quiet = false;
    const snapshot = () => ({ x: [xr.start, xr.end],
      y: rows.map(r => [r.fig.y_range.start, r.fig.y_range.end]) });
    const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
    const home = snapshot();
    const stack = [home];

    /* ROW PITCH. A vertical drag leaves a y-range covering some of a panel's rows.
       Snap it to whole rows, then make the panel as tall as those rows need. */
    function pitchRows() {
      for (const r of rows) {
        if (!r.pitch) continue;
        const yr = r.fig.y_range, lo = Math.min(...r.y0), hi = Math.max(...r.y0);
        let a = Math.max(lo, Math.floor(Math.min(yr.start, yr.end) + 0.5) - 0.5);
        let b = Math.min(hi, Math.ceil(Math.max(yr.start, yr.end) - 0.5) + 0.5);
        if (b - a < 1) b = Math.min(hi, a + 1);
        if (b - a < 1) a = b - 1;
        const whole = b - a >= hi - lo - 1e-9;
        if (whole) { a = lo; b = hi; }
        if (yr.start !== a || yr.end !== b) yr.setv({ start: a, end: b });
        const pitch0 = r.inner / (hi - lo);
        let pitch = pitch0;
        if (!whole)
          pitch = Math.max(pitch0, r.inner / (b - a),
                           Math.min(ZOOMED_ROW_PX, ZOOMED_PANEL_MAX_PX / (b - a)));
        const height = Math.round(r.height - r.inner + (b - a) * pitch);
        if (r.fig.height !== height) r.fig.height = height;
        for (const s of r.sized) {
          const size = whole ? s.size
            : Math.max(s.size, Math.min(s.size * pitch / pitch0, 0.8 * pitch));
          for (const g of s.glyphs)
            if (g.size.value !== size) g.size = { value: size };
        }
      }
    }

    function paintBar() {
      const now = snapshot();
      document.getElementById("bugarachNavAll").disabled = same(now, home);
      document.getElementById("bugarachNavBack").disabled = stack.length < 2;
    }

    function settle() {
      quiet = true;
      try { pitchRows(); } finally { quiet = false; }
      const now = snapshot();
      if (!same(now, stack[stack.length - 1])) stack.push(now);
      paintBar();
    }

    let timer = null;
    const changed = () => {
      if (quiet) return;
      clearTimeout(timer);
      timer = setTimeout(settle, 120);
    };
    const watch = range => {
      range.properties.start.change.connect(changed);
      range.properties.end.change.connect(changed);
    };
    watch(xr);
    for (const r of rows) watch(r.fig.y_range);

    function show(view) {
      clearTimeout(timer);
      quiet = true;
      try {
        xr.setv({ start: view.x[0], end: view.x[1] });
        rows.forEach((r, i) =>
          r.fig.y_range.setv({ start: view.y[i][0], end: view.y[i][1] }));
        pitchRows();
      } finally { quiet = false; }
      paintBar();
    }

    function reset() {
      clearTimeout(timer);
      if (!same(snapshot(), home)) { show(home); stack.push(home); }
      paintBar();
    }

    function undo() {
      clearTimeout(timer);
      // a gesture still inside its debounce has moved the page but is not on the stack
      if (!same(snapshot(), stack[stack.length - 1])) show(stack[stack.length - 1]);
      else if (stack.length > 1) { stack.pop(); show(stack[stack.length - 1]); }
      paintBar();
    }

    /* SHIFT SLIDES. Bokeh gives the plain drag to one tool, so holding Shift hands
       it to the pan tool and letting go hands it back to the box. */
    function drag(type) {
      for (const r of rows)
        for (const t of r.fig.toolbar.tools)
          if (t.type === type && !t.active) t.active = true;
    }
    document.addEventListener("keydown", ev => {
      if (ev.key === "Shift") drag("PanTool");
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test((ev.target && ev.target.tagName) || "");
      if ((ev.ctrlKey || ev.metaKey) && !ev.shiftKey && !typing
          && ev.key.toLowerCase() === "z") { ev.preventDefault(); undo(); }
    });
    document.addEventListener("keyup", ev => { if (ev.key === "Shift") drag("BoxZoomTool"); });
    window.addEventListener("blur", () => drag("BoxZoomTool"));

    document.getElementById("bugarachNavAll").onclick = reset;
    document.getElementById("bugarachNavBack").onclick = undo;
    window.bugarachNav = { reset, undo, view: snapshot, depth: () => stack.length,
                           heights: () => rows.map(r => r.fig.height) };
  }
  start();
})();
</script>
"""


def add_navigation(html: str) -> str:
    """The saved page with the navigation script and its bar appended to the body.

    Refuses a page with no ``</body>``: appending after the document would leave a page that
    opens, draws and silently has no gestures.
    """
    script = (NAV_SCRIPT.replace("__NAV_TAG__", NAV_TAG)
              .replace("__PITCH_TAG__", PITCH_TAG)
              .replace("__ZOOMED_ROW_PX__", str(ZOOMED_ROW_PX))
              .replace("__ZOOMED_PANEL_MAX_PX__", str(ZOOMED_PANEL_MAX_PX)))
    head, sep, tail = html.rpartition("</body>")
    if not sep:
        raise ValueError("the page has no </body> to put the navigation script before")
    return head + script + sep + tail
