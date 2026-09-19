"""Gate 1 step 3's stop (Tony, 2026-09-16), for one learned model.

Usage: check_step3.py <model> <this machine's bakeoff.json> <learned_vs_coact.json>

STOP (exit 3) if, on any fold:
  * this machine's F1 is further from BOTH Mac seeds than the Mac's own largest
    per-fold seed-to-seed gap for the model, or
  * the failed-training signature: F1 near 0.125 with threshold at 0.0001.
Otherwise prints the per-fold record and exits 0.
"""
import json
import sys

model, mine_path, table_path = sys.argv[1:4]
mine = json.load(open(mine_path))["learned"][model]["per_fold"]
row = next(r for r in json.load(open(table_path))["rows"] if r["model"] == model)
s0 = row["by_seed"]["0"]["f1_per_fold"]
s1 = row["by_seed"]["1"]["f1_per_fold"]
gap = max(abs(b - a) for a, b in zip(s0, s1))

stop = []
print(f"{model}: Mac largest seed-to-seed gap {gap:.4f} F1")
for f in mine:
    k = f["fold"]
    f1, thr = f["f1"], f["threshold"]
    d0, d1 = f1 - s0[k], f1 - s1[k]
    far = abs(d0) > gap and abs(d1) > gap
    failed = abs(f1 - 0.125) < 0.01 and abs(thr - 1e-4) < 1e-6
    print(f"  fold {k}: F1 {f1:.4f}  Mac seed 0 {s0[k]:.4f} (diff {d0:+.4f})"
          f"  Mac seed 1 {s1[k]:.4f} (diff {d1:+.4f})  threshold {thr:.4g}"
          f"  train {f['train_sec']:.1f} s"
          + ("  <- FURTHER THAN THE SEED GAP FROM BOTH" if far else "")
          + ("  <- FAILED-TRAINING SIGNATURE" if failed else ""))
    if far:
        stop.append(f"fold {k} further than {gap:.4f} F1 from both Mac seeds")
    if failed:
        stop.append(f"fold {k} failed-training signature")
if stop:
    print(f"{model}: STOP: " + "; ".join(stop))
    sys.exit(3)
print(f"{model}: no stop")
