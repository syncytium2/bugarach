"""One detections file per lane for the floor + 1 review pages, from detect_with_floors' calls.csv.

    python floor_lanes.py <run folder> <lanes folder>

Lanes, in page order: coact · floor, coact · floor+1, chorus_norm · floor, chorus_norm · floor+1,
chorus_gain_norm · floor, chorus_gain_norm · floor+1. The detector field carries the lane name, so
the page tool's detector_lanes shows each as its own row. Written through emit.write_detections,
the detect step's own format, so emit.read_detections reads them back.

CoactDetect's calls are the ones its own_floor and own_plus_1 runs made. Chorus has no
participation parameter: its calls are written once ("unfloored") with their participants, and a
floor keeps those whose participants reach it, the rule detect_with_floors counts by.
"""
import csv
import sys
from pathlib import Path

from bugarach.emit import DetectedEvent, write_detections

run, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
LANES = [("coact", "floor"), ("coact", "floor+1"), ("chorus_norm", "floor"),
         ("chorus_norm", "floor+1"), ("chorus_gain_norm", "floor"), ("chorus_gain_norm", "floor+1")]
events = {lane: [] for lane in LANES}
with (run / "calls.csv").open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        det, var = r["detector"], r["variant"]
        if det == "coact":
            lane = {"own_floor": "floor", "own_plus_1": "floor+1"}.get(var)
            keep = [lane] if lane else []
        elif det in ("chorus_norm", "chorus_gain_norm") and var == "unfloored":
            p = int(r["participants"])
            keep = [lab for lab, col in (("floor", "own_floor"), ("floor+1", "own_plus_1"))
                    if r[col] not in ("", None) and p >= int(float(r[col]))]
        else:
            keep = []
        for lab in keep:
            events[(det, lab)].append(DetectedEvent(
                slice_id=r["slice_id"], stream=r["stream"], detector=f"{det} · {lab}",
                mode="floor-review", onset_sec=float(r["onset_sec"]),
                width_sec=float(r["width_sec"]), strength=float(r["participants"]),
                strength_unit="co-active ROIs", region_idx=int(r["region_idx"]),
                region_label=r["label"] or None))
paths = []
for i, (det, lab) in enumerate(LANES, 1):
    p = out / f"{i}_{det}_{lab.replace('+', '_plus_')}.csv"
    write_detections(events[(det, lab)], p)
    paths.append(p)
    print(p.name, len(events[(det, lab)]), "calls")
(out / "ORDER.txt").write_text("\n".join(str(p) for p in paths) + "\n", encoding="utf-8")
