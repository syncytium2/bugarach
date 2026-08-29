#!/usr/bin/env bash
# run_tube_screen.sh — the 2x2 tube mechanism screen, repeated across training seeds.
#
# WHY A LOOP AND NOT ONE RUN. `fair_bakeoff.py` trains each architecture ONCE per fold,
# so the only spread it reports is across folds — a property of the data split, not of
# the optimiser. Every learned number in this repo has that limitation, and the tube's
# headline is a 0.017 gap sitting inside a 0.061 fold spread. A variant that moves F1 by
# less than that has demonstrated nothing. Repeating the whole bake-off at different
# `--train-seed` values is what turns the comparison into a measurement.
#
# WHAT IT RUNS. Six learned architectures — the 2x2 over {subtract, ratio} x {no guard,
# guard}, plus `trace` and `tiny` as the weak baselines — and all six hand-written
# detectors, calibrated on the training folds and scored on the held-out fold through
# the same scorer. One set of recordings, one split, per seed.
#
# WHAT IT IS NOT. Preliminary. The spec is `docs/learned/generator_spec.json`, derived
# off the `.mat` store on a superseded difficulty axis, with `k_chosen: 3` inherited
# rather than re-decided. It can compare the tube to itself. It cannot settle whether
# the tube leads CoactDetect, and nothing it writes may be quoted as though it could.
#
#   bash tools/run_tube_screen.sh <outdir> [n_seeds]
set -uo pipefail

OUT="${1:?usage: run_tube_screen.sh <outdir> [n_seeds]}"
N="${2:-5}"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)

# The interpreter, FOUND rather than written down. A worktree has no `.venv` of its
# own, so this also looks in the sibling primary checkout — and SAP004 blocks the
# obvious shortcut of hardcoding the path, correctly: it carries a person's name and
# this repo is public. Override with BUGARACH_PY on a machine laid out differently.
PY="${BUGARACH_PY:-}"
if [ -z "$PY" ]; then
  for c in "$ROOT/.venv/bin/python" "$ROOT/../../bugarach/.venv/bin/python" \
           "$(command -v python3 || true)"; do
    if [ -x "$c" ] && "$c" -c "import torch" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
if [ -z "$PY" ]; then
  echo "no interpreter with torch installed. Set BUGARACH_PY, or:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -e '.[dev,dl]'" >&2
  exit 1
fi
echo "python: $PY"

mkdir -p "$OUT"
echo "tube screen: $N seeds -> $OUT"
echo "repo:  $ROOT"
echo "began: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

for s in $(seq 1 "$N"); do
  echo ""
  echo "=== train-seed $s of $N  ($(date -u +%H:%M:%SZ)) ==="
  PYTHONPATH="$ROOT/src" "$PY" "$ROOT/tools/fair_bakeoff.py" \
      --spec "$ROOT/docs/learned/generator_spec.json" \
      --out "$OUT" --folds 4 --seeds-per-fold 4 --train-seed "$s" \
    || echo "!! seed $s FAILED — continuing; the surviving seeds are still readable"
done

echo ""
echo "ended: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
ls -la "$OUT"
