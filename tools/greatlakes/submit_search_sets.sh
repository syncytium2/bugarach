#!/usr/bin/env bash
# Submit one search per bench set to Great Lakes, and the verdict job that follows them.
#
#   export BUGARACH_SLURM_ACCOUNT=<the lab's Slurm account>
#   export BUGARACH_GL_OUT="<a dated folder on the shared research drive>"
#   bash tools/greatlakes/submit_search_sets.sh            # every set with a record
#   bash tools/greatlakes/submit_search_sets.sh fast_di    # or the ones named
#
# The account and the drive's path are not in this repository, which is public; they are in
# the lab's private access notes (docs/greatlakes/README.md says where).
# Everything a workstation session must read goes under $BUGARACH_GL_OUT: results, Slurm logs,
# and run_record/VERDICT_set_searches.txt.
set -euo pipefail
: "${BUGARACH_SLURM_ACCOUNT:?set BUGARACH_SLURM_ACCOUNT to the Slurm account to charge}"
: "${BUGARACH_GL_OUT:?set BUGARACH_GL_OUT to an absolute folder on the shared research drive}"
case "$BUGARACH_GL_OUT" in /*) ;; *) echo "BUGARACH_GL_OUT must be an absolute path" >&2; exit 2;; esac
export BUGARACH_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="${BUGARACH_VENV:-$HOME/bugarach-venv}"
[ -x "$VENV/bin/python" ] || { echo "no environment at $VENV: run tools/greatlakes/setup_env.sh" >&2; exit 2; }
if [ "$#" -gt 0 ]; then SETS="$*"; else
  SETS="$(PYTHONPATH="$BUGARACH_REPO/src" "$VENV/bin/python" -c 'from bugarach import bench_sets; print(" ".join(bench_sets.names()))')"
fi
export BUGARACH_SETS="$SETS"
N=$(wc -w <<< "$SETS")
mkdir -p "$BUGARACH_GL_OUT/logs" "$BUGARACH_GL_OUT/run_record"
echo "sets ($N): $SETS"
echo "out: $BUGARACH_GL_OUT"
JOB=$(sbatch --parsable --account="$BUGARACH_SLURM_ACCOUNT" --array="0-$((N - 1))" \
  --output="$BUGARACH_GL_OUT/logs/search_%A_%a.out" --error="$BUGARACH_GL_OUT/logs/search_%A_%a.err" \
  --export=ALL "$BUGARACH_REPO/tools/greatlakes/search_sets.sbatch")
echo "submitted array $JOB"
VER=$(sbatch --parsable --account="$BUGARACH_SLURM_ACCOUNT" --partition=standard --cpus-per-task=1 \
  --mem=2G --time=00:10:00 --job-name=bugarach_verdict --dependency="afterany:$JOB" \
  --output="$BUGARACH_GL_OUT/logs/verdict_%j.out" --error="$BUGARACH_GL_OUT/logs/verdict_%j.err" \
  --export=ALL --wrap "PYTHONPATH='$BUGARACH_REPO/src' '$VENV/bin/python' '$BUGARACH_REPO/tools/greatlakes/verdict_search_sets.py' --out \"\$BUGARACH_GL_OUT\" --sets \$BUGARACH_SETS")
echo "submitted verdict $VER (runs when every search has ended)"
{ echo "submitted $(date -Is)"; echo "array $JOB"; echo "verdict $VER"; echo "sets $SETS";
  echo "commit $(git -C "$BUGARACH_REPO" rev-parse HEAD)"; } > "$BUGARACH_GL_OUT/run_record/SUBMITTED_set_searches.txt"
