"""How much training-seed noise a configuration's inner score carries, by number of seeds.

Run from the repository root. Reads the per-fold F1 at training seeds 0 and 1 for the four learned
models in docs/learned/field_size_candidates/learned_vs_coact.json (the Mac), and chorus_gain_norm's
two seeds on the workstation from this folder.

One seed-to-seed gap g on a fold of 6 recordings gives a one-seed standard deviation of g / sqrt(2).
The inner score pools 3 inner folds, each from its own fit, so its seed noise is that / sqrt(3), and
/ sqrt(k) when k seeds are averaged. Two configurations are scored on the same recordings, so their
difference carries seed noise only: sqrt(2) times the inner-score standard deviation.
"""
import json
import math

HERE = "docs/learned/tuned_vs_coact/gate1/"
table = {r["model"]: r for r in
         json.load(open("docs/learned/field_size_candidates/learned_vs_coact.json"))["rows"]}


def per_fold(path, model):
    return [f["f1"] for f in json.load(open(path))["learned"][model]["per_fold"]]


gaps = {}
for m in ("tube", "chorus_norm", "chorus_gain_norm", "line_length"):
    s0, s1 = (table[m]["by_seed"][k]["f1_per_fold"] for k in ("0", "1"))
    gaps[f"{m} (Mac)"] = [b - a for a, b in zip(s0, s1)]
w0 = per_fold(HERE + "step3_tip_chorus_gain_norm/bakeoff.json", "chorus_gain_norm")
w1 = per_fold(HERE + "step3c_chorus_gain_norm_seed1/bakeoff_seed1.json", "chorus_gain_norm")
gaps["chorus_gain_norm (workstation)"] = [b - a for a, b in zip(w0, w1)]

pooled = []
for name, g in gaps.items():
    rms = math.sqrt(sum(x * x for x in g) / len(g))
    pooled += g
    print(f"{name:32} gaps {', '.join(f'{x:+.3f}' for x in g)}; one-seed sd per fold {rms / math.sqrt(2):.4f} F1")
sd_fold = math.sqrt(sum(x * x for x in pooled) / len(pooled)) / math.sqrt(2)
print(f"pooled over {len(pooled)} gaps: one-seed sd per fold {sd_fold:.4f} F1")
for k in (1, 2, 3, 5):
    sd = sd_fold / math.sqrt(3) / math.sqrt(k)
    print(f"k={k}: inner-score sd {sd:.4f} F1; difference of two configurations: sd {sd * math.sqrt(2):.4f},"
          f" two sd {2 * sd * math.sqrt(2):.4f} F1")
