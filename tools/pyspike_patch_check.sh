#!/usr/bin/env bash
# Rebuild PySpike v0.9.0 with docs/pyspike_max_tau.patch and prove the two
# things the upstream report claims about it: that PySpike's own test suite
# stays green, and that the patched build produces the report's numbers.
#
# Everything happens in a scratch directory. Nothing touches the repo venv, so
# a session running this cannot move PySpike under another session's feet.
#
#   bash tools/pyspike_patch_check.sh [workdir]
#
# Needs: network (one tarball from GitHub), a C compiler, and a Python with
# numpy + cython available for the build. Takes about a minute.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${1:-${TMPDIR:-/tmp}/pyspike_patch_check}"
VER="0.9.0"
URL="https://github.com/mariomulansky/PySpike/archive/refs/tags/v${VER}.tar.gz"

# The venv is machine-local and lives in the primary checkout, so a worktree has
# none of its own -- git points us at the primary from anywhere in the tree.
find_python() {
    local primary
    [ -n "${PYSPIKE_CHECK_PYTHON:-}" ] && { echo "$PYSPIKE_CHECK_PYTHON"; return; }
    [ -x "${REPO}/.venv/bin/python" ] && { echo "${REPO}/.venv/bin/python"; return; }
    primary="$(cd "$REPO" && git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
    primary="${primary%/.git}"
    [ -n "$primary" ] && [ -x "${primary}/.venv/bin/python" ] \
        && { echo "${primary}/.venv/bin/python"; return; }
    command -v python3
}
PY="$(find_python)"

[ -x "$PY" ] || { echo "no usable interpreter (set PYSPIKE_CHECK_PYTHON)" >&2; exit 2; }
echo "== interpreter: $PY =="

mkdir -p "$WORK"
cd "$WORK"
[ -f "v${VER}.tar.gz" ] || curl -fsSL "$URL" -o "v${VER}.tar.gz"

rm -rf "PySpike-${VER}" build
tar xzf "v${VER}.tar.gz"
cd "PySpike-${VER}"

echo "== upstream suite, as shipped =="
"$PY" -m pytest test -q -p no:cacheprovider | tail -1

echo "== applying docs/pyspike_max_tau.patch =="
patch -p1 --quiet < "${REPO}/docs/pyspike_max_tau.patch"
grep -n "fmin(fmin" pyspike/cython/cython_get_tau.pyx
grep -n "min(min" pyspike/cython/python_backend.py

echo "== upstream suite, patched (pure-Python backend) =="
"$PY" -m pytest test -q -p no:cacheprovider | tail -1

echo "== building the patched Cython extension =="
"$PY" -m pip install . --quiet --target "${WORK}/build"
ls "${WORK}/build/pyspike/cython/"cython_get_tau*.so >/dev/null

echo "== upstream suite, patched (compiled backend) =="
mv pyspike pyspike_src_hidden
PYTHONPATH="${WORK}/build" "$PY" -m pytest test -q -p no:cacheprovider | tail -1
mv pyspike_src_hidden pyspike

echo "== the report's sweep, shipped vs patched compiled =="
cd "$WORK"
sweep='
import numpy as np, pyspike
rng = np.random.default_rng(0); edges = (0.0, 600.0)
a, b = (pyspike.SpikeTrain(np.sort(rng.uniform(*edges, 60)), edges) for _ in range(2))
print("  from:", pyspike.__file__)
for mt in (None, 1.0, 0.25, 1e-6):
    print(f"  max_tau={str(mt):>8}  {pyspike.spike_sync(a, b, max_tau=mt):.4f}")
a2 = pyspike.SpikeTrain([40.4, 77.3, 534.4], edges)
b2 = pyspike.SpikeTrain([58.8, 85.0, 300.0], edges)
x, y = pyspike.spike_sync_profile(a2, b2, max_tau=0.25).get_plottable_data()
print("  7.7 s pair coincident under a 0.25 s cap:",
      bool(dict(zip(np.round(x, 1), y))[77.3]))
'
echo "-- as shipped (expect 0.3500/0.3333/0.3333/0.3333, pair True) --"
"$PY" -c "$sweep"
echo "-- patched (expect 0.3500/0.1833/0.0500/0.0000, pair False) --"
PYTHONPATH="${WORK}/build" "$PY" -c "$sweep"

echo
echo "done. patched build left at ${WORK}/build"
