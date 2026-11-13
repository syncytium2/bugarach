#!/usr/bin/env bash
# Build bugarach's Python environment on Great Lakes, once, from a login node.
#
#   bash tools/greatlakes/setup_env.sh
#
# Uses uv, which brings its own Python 3.14, because the cluster's modules are older than
# bugarach needs. The environment goes in $BUGARACH_VENV (default: ~/bugarach-venv), in the
# home directory, which the university's pages give as the place for software builds.
# Run it again after a `git pull` that changes pyproject.toml.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="${BUGARACH_VENV:-$HOME/bugarach-venv}"
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null; then
  echo "== installing uv into ~/.local/bin"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
echo "== uv $(uv --version)"
uv venv --python 3.14 "$VENV"
uv pip install --python "$VENV/bin/python" -e "$REPO" pytest
"$VENV/bin/python" - <<'PY'
import sys, numpy, scipy, bugarach
from bugarach import bench_sets
print("python", sys.version.split()[0], "numpy", numpy.__version__, "scipy", scipy.__version__)
print("bench sets:", ", ".join(bench_sets.names()))
m = bench_sets.load(bench_sets.names()[0])
s, gt = m.make_recording("baseline_quiet", 1)
print("simulated one recording:", len(gt.events), "planted events")
PY
echo "ENVIRONMENT: READY at $VENV"
