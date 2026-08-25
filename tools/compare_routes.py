#!/usr/bin/env python3
"""Do the browser and `bugarach detect` produce the same detections on one folder?

    python tools/compare_routes.py <export folder> --also docs/learned

**The measurement `docs/todo/2026-08-24-two-routes-two-answers-on-one-folder.md`
asks for**, and the hole the README names in terms: *"What nothing does is compare
a browser run and a `bugarach detect` run on the same folder, row for row."*

Two figures for the same folder were reported on 2026-08-23 — 51,968 rows from the
page, 34,124 from the CLI — and neither is reproducible: the rosters were not
pinned, and **neither output file was kept**. That is what this fixes. Both routes
run here with the **same detectors, the same stream and the same settings**, both
files are written to the darkroom rather than discarded, and the comparison is by
`(slice_id, detector, stream, onset_sec)`.

**A total is not the deliverable.** One row per event per detector by contract, so
a sum across detectors is dominated by whichever fires most and two runs can match
on it while disagreeing everywhere underneath. The output is a **per-detector
table**, plus the first rows where the two part and which side is missing them.

## What can be compared exactly, and what cannot

`rate` draws no random numbers, so it must agree **row for row**. `coact` and
`sce` draw circular-shift surrogates and the two implementations do not share an
RNG, so they agree to sampling error — the bar
`docs/testing_a_sampling_port.md` sets for a port that guesses.

⚠ **`sync` used to be the second exact anchor and is no longer available**: it is
off in the browser since 2026-08-24 (forks, and the `unavailable` field on its
registry row), so the page cannot run it. One deterministic detector is a thinner
anchor than two, and that is a cost of the disabling worth knowing about.

`loco` and `cicada` are ~97% of a six-detector run and are off by default here;
pass `--detectors` to include them.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_DETECTORS = ("rate", "coact", "sce")
DEFAULT_STREAM = "fast"

#: How close two onsets must be to be called the same detection. The bench scores
#: a hit at 1.5 s; this is far tighter because these are two implementations of
#: one algorithm on identical input, not a detector against planted truth.
MATCH_SEC = 0.05


# ----------------------------------------------------------------- the CLI route

def run_cli(folder: Path, out: Path, detectors, stream: str) -> Path:
    from bugarach.detect_folder import detect_folder

    out.mkdir(parents=True, exist_ok=True)
    detect_folder(folder, out_dir=out, detectors=tuple(detectors), stream=stream)
    return out / "detections.csv"


# ------------------------------------------------------------- the browser route

LOAD_AND_RUN = """async (cfg) => {
  await open(cfg.files, {quiet: true});
  /* THE STREAM IS CHOSEN AT THE DOOR and the page analyses one at a time, so a
     comparison against `bugarach detect --stream X` has to pick the same one.
     Through `chooseStream` rather than by assigning STREAM: it clears DETECT,
     FOLDER_RUN and ASSESS, which is the whole point — results about the stream
     you left are not claims about this one. */
  if (cfg.stream && typeof chooseStream === "function"
      && STREAMS_SEEN.includes(cfg.stream)) {
    chooseStream(cfg.stream);
  }
  if (STREAM !== cfg.stream) {
    return {csv: null, note: "asked for stream " + cfg.stream
            + " and the folder holds " + STREAMS_SEEN.join(", ")};
  }
  document.getElementById("dAll").checked = true;
  for (const k of Object.keys(DETECTORS)) {
    const b = document.getElementById("dPick_" + k);
    if (b) b.checked = cfg.detectors.includes(k);
  }
  paintDetectorChoice();
  await analyseFolder();
  return {
    csv: FOLDER_RUN ? detectionsCsv(FOLDER_RUN.rows) : null,
    ran: FOLDER_RUN ? FOLDER_RUN.detectors : null,
    stream: FOLDER_RUN ? (runJson(FOLDER_RUN).stream ?? null) : null,
    slices: FOLDER_RUN ? FOLDER_RUN.slices.length : 0,
    note: document.getElementById("folderWhat").textContent,
  };
}"""


def run_browser(folder: Path, out: Path, detectors, stream: str,
                viewer: Path) -> Path:
    from playwright.sync_api import sync_playwright

    files = [{"name": p.name, "text": p.read_text(encoding="utf-8")}
             for p in sorted(folder.iterdir())
             if p.is_file() and p.suffix.lower() == ".csv"]
    print(f"  feeding {len(files)} files to the page…")

    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            pg = b.new_page()
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(viewer.as_uri(), wait_until="load")
            pg.set_default_timeout(20 * 60 * 1000)
            got = pg.evaluate(LOAD_AND_RUN, {"files": files,
                                             "detectors": list(detectors),
                                             "stream": stream})
            if errs:
                raise SystemExit(f"the page raised: {errs[:3]}")
        finally:
            b.close()

    if not got["csv"]:
        raise SystemExit(f"the page produced no table: {got['note']!r}")
    print(f"  page ran {got['ran']} on {got['slices']} recording(s), "
          f"stream {got['stream']!r}")
    p = out / "detections.csv"
    p.write_text(got["csv"], encoding="utf-8")
    return p


# ------------------------------------------------------------------- the compare

def key_rows(path: Path):
    """`(slice_id, detector, stream) -> sorted onsets`, plus the raw rows."""
    from bugarach.emit import read_detections

    by = defaultdict(list)
    for r in read_detections(path):
        by[(r["slice_id"], r["detector"], r["stream"])].append(r["onset_sec"])
    return {k: sorted(v) for k, v in by.items()}


def pair_up(a: list[float], b: list[float], tol: float = MATCH_SEC):
    """Greedy nearest-neighbour match. Returns (matched, a_only, b_only)."""
    i = j = 0
    matched, a_only, b_only = 0, [], []
    while i < len(a) and j < len(b):
        if abs(a[i] - b[j]) <= tol:
            matched += 1
            i += 1
            j += 1
        elif a[i] < b[j]:
            a_only.append(a[i])
            i += 1
        else:
            b_only.append(b[j])
            j += 1
    a_only.extend(a[i:])
    b_only.extend(b[j:])
    return matched, a_only, b_only


def compare(cli_csv: Path, br_csv: Path, detectors) -> dict:
    cli, br = key_rows(cli_csv), key_rows(br_csv)
    keys = sorted(set(cli) | set(br))

    per_det = {d: {"cli": 0, "browser": 0, "agreed": 0,
                   "cli_only": 0, "browser_only": 0,
                   "slices_both": 0, "slices_cli_only": 0,
                   "slices_browser_only": 0} for d in detectors}
    first_parts = []

    for slice_id, det, stream in keys:
        if det not in per_det:
            per_det.setdefault(det, {"cli": 0, "browser": 0, "agreed": 0,
                                     "cli_only": 0, "browser_only": 0,
                                     "slices_both": 0, "slices_cli_only": 0,
                                     "slices_browser_only": 0})
        k = (slice_id, det, stream)
        a, b = cli.get(k, []), br.get(k, [])
        d = per_det[det]
        d["cli"] += len(a)
        d["browser"] += len(b)
        if a and b:
            d["slices_both"] += 1
        elif a:
            d["slices_cli_only"] += 1
        elif b:
            d["slices_browser_only"] += 1
        m, ao, bo = pair_up(a, b)
        d["agreed"] += m
        d["cli_only"] += len(ao)
        d["browser_only"] += len(bo)
        for t in ao[:3]:
            first_parts.append({"slice": slice_id, "detector": det,
                                "stream": stream, "onset_sec": t,
                                "side": "CLI only"})
        for t in bo[:3]:
            first_parts.append({"slice": slice_id, "detector": det,
                                "stream": stream, "onset_sec": t,
                                "side": "browser only"})

    first_parts.sort(key=lambda r: (r["detector"], r["slice"], r["onset_sec"]))
    return {"per_detector": per_det, "first_parts": first_parts[:20],
            "n_keys": len(keys),
            "slices_cli": len({k[0] for k in cli}),
            "slices_browser": len({k[0] for k in br})}


def report(res: dict, folder: Path, detectors, stream: str) -> str:
    lines = [
        "# Two routes, one folder — the row-for-row comparison",
        "",
        f"Folder: `{folder.name}` · stream `{stream}` · "
        f"detectors `{','.join(detectors)}`",
        f"Matching tolerance {MATCH_SEC:g} s — these are two implementations of "
        "one algorithm on identical input, not a detector against planted truth.",
        "",
        "| detector | CLI rows | browser rows | agreed | CLI only | browser only |",
        "|---|---|---|---|---|---|",
    ]
    for det, d in sorted(res["per_detector"].items()):
        lines.append(
            f"| `{det}` | {d['cli']} | {d['browser']} | **{d['agreed']}** | "
            f"{d['cli_only']} | {d['browser_only']} |")
    lines += ["",
              f"Recordings with rows: CLI {res['slices_cli']}, "
              f"browser {res['slices_browser']}.", ""]
    if res["first_parts"]:
        lines += ["## The first rows where they part", "",
                  "| detector | recording | stream | onset (s) | which side |",
                  "|---|---|---|---|---|"]
        for r in res["first_parts"]:
            lines.append(f"| `{r['detector']}` | {r['slice']} | {r['stream']} | "
                         f"{r['onset_sec']:.3f} | {r['side']} |")
    else:
        lines.append("**No row parted.** Every detection matched on both sides.")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("folder", type=Path)
    p.add_argument("--detectors", default=",".join(DEFAULT_DETECTORS))
    p.add_argument("--stream", default=DEFAULT_STREAM)
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--skip-cli", action="store_true")
    p.add_argument("--skip-browser", action="store_true")
    a = p.parse_args()
    detectors = tuple(x.strip() for x in a.detectors.split(",") if x.strip())

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    root = dest / "two_routes"
    cli_dir, br_dir = root / "cli", root / "browser"

    cli_csv = cli_dir / "detections.csv"
    if not a.skip_cli:
        print(f"CLI route: {', '.join(detectors)} on stream {a.stream}…")
        cli_csv = run_cli(a.folder, cli_dir, detectors, a.stream)
    print(f"  {cli_csv}")

    br_csv = br_dir / "detections.csv"
    if not a.skip_browser:
        viewer = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"
        print("browser route: same roster, same stream…")
        br_csv = run_browser(a.folder, br_dir, detectors, a.stream, viewer)
    print(f"  {br_csv}")

    res = compare(cli_csv, br_csv, detectors)
    text = report(res, a.folder, detectors, a.stream)
    print()
    print(text)

    for d in [root] + ([a.also] if a.also else []):
        d.mkdir(parents=True, exist_ok=True)
        (d / "two_routes_diff.md").write_text(text, encoding="utf-8")
        print(f"wrote {d / 'two_routes_diff.md'}")
    (root / "two_routes_diff.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
