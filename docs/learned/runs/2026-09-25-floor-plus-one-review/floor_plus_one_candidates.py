"""candidates.json for the floor + 1 review: CoactDetect at its SHIPPED setting on every stream
(from each stream's bench module), and the chorus checkpoints last night's training runs picked.

    python floor_plus_one_candidates.py <final-parameters phase3-real-v3/candidates_merged.json> <out>
"""
import importlib
import json
import sys
from pathlib import Path

MODULE = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
          "combined": "bugarach.bench_combined"}
picked = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = {"benches": {}, "note": "floor + 1 review: CoactDetect shipped, chorus picked checkpoints"}
for stream, mod in MODULE.items():
    shipped = dict(importlib.import_module(mod).OPERATING_POINTS["coact"].params)
    out["benches"][stream] = dict(
        detectors={"coact": dict(shipped=shipped, proposal=dict(name="shipped", params={}))},
        chorus=picked["benches"][stream]["chorus"])
    print(stream, "coact shipped", shipped, "| chorus",
          {m: i.get("picked") for m, i in out["benches"][stream]["chorus"].items()})
Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print("wrote", sys.argv[2])
