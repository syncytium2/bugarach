"""Navigating a page of rasters the way Igor Pro navigates a graph, in time only.

Tony, 2026-10-13, asked for Igor's graph gestures on the HTML rasters
(`docs/adr/0015-raster-pages-navigate-the-way-igor-does.md`), and the same day, on the first
real pages, took the vertical half back out: *"it's a bit of a mess. disable the pitch and
make zoom only x-axis"* (`docs/adr/0016-a-raster-zooms-in-time-only.md`).

- **Drag a box to zoom time.** Every recording on the page follows, because the panels
  share one time range. The box is a band the full height of the panel; a drag has no
  vertical meaning and no panel ever changes height.
- **Shift-drag slides** the time axis. Plain drag used to; the box has it now.
- **Ctrl+wheel zooms** time at the cursor. The bare wheel still scrolls the page.
- **Double-click shows everything; Ctrl+Z steps back** one view at a time.

Two halves. :func:`navigation_hook` sets up the bokeh tools on each panel, where a test can
read them off the model. :func:`add_navigation` appends one script to the saved page for
what bokeh has no tool for: the Shift swap, the view history and the bar at the bottom of
the window that says what the gestures are.
"""
from __future__ import annotations

#: On every panel the script should drive.
NAV_TAG = "bugarach-nav"


def navigation_hook(plot, element):
    """A HoloViews hook giving one panel the box zoom and the Ctrl+wheel zoom, in time only.

    Runs after ``_time_axis_hook``, which pins every zoom tool to x; the box added here is
    pinned the same way.
    """
    from bokeh.models import BoxZoomTool, CustomJS, PanTool, WheelZoomTool

    fig = plot.state
    toolbar = fig.toolbar
    tools = [t for t in toolbar.tools if not isinstance(t, BoxZoomTool)]
    box = BoxZoomTool(dimensions="width")
    toolbar.tools = tools + [box]
    toolbar.active_drag = box
    for tool in tools:
        if isinstance(tool, PanTool):
            tool.dimensions = "width"
        if isinstance(tool, WheelZoomTool):
            tool.dimensions = "width"
            tool.modifiers = {"ctrl": True}
            toolbar.active_scroll = tool
    fig.tags = list(fig.tags) + [NAV_TAG]
    # Deferred a tick: bokeh's box zoom answers a double-click itself by undoing its
    # last zoom, and whichever of the two runs second is the view the reader gets.
    fig.js_on_event("doubletap", CustomJS(
        code="setTimeout(() => window.bugarachNav && window.bugarachNav.reset(), 0);"))


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
  <span><b>drag a box</b> to zoom time, on every recording</span>
  <span><b>Shift-drag</b> slides</span>
  <span><b>Ctrl+wheel</b> zooms time</span>
  <span><b>double-click</b> shows everything</span>
  <span><b>Ctrl+Z</b> goes back one view</span>
</div>
<script>
(function () {
  const NAV_TAG = "__NAV_TAG__";

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

    // one time range, shared by every panel on the page
    const xr = figs[0].x_range;
    let quiet = false;
    const snapshot = () => ({ x: [xr.start, xr.end] });
    const same = (a, b) => a.x[0] === b.x[0] && a.x[1] === b.x[1];
    const home = snapshot();
    const stack = [home];

    function paintBar() {
      document.getElementById("bugarachNavAll").disabled = same(snapshot(), home);
      document.getElementById("bugarachNavBack").disabled = stack.length < 2;
    }

    function settle() {
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
    xr.properties.start.change.connect(changed);
    xr.properties.end.change.connect(changed);

    function show(view) {
      clearTimeout(timer);
      quiet = true;
      try { xr.setv({ start: view.x[0], end: view.x[1] }); } finally { quiet = false; }
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
      for (const f of figs)
        for (const t of f.toolbar.tools)
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
      rows: () => figs.map(f => [f.y_range.start, f.y_range.end]),
      heights: () => figs.map(f => f.height) };
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
    script = NAV_SCRIPT.replace("__NAV_TAG__", NAV_TAG)
    head, sep, tail = html.rpartition("</body>")
    if not sep:
        raise ValueError("the page has no </body> to put the navigation script before")
    return head + script + sep + tail
