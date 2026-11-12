#!/usr/bin/env bash
# One detector-settings search per bench set, as a job array. Submitted by submit_search_sets.sh,
# which supplies the account, the output folder and the list of sets; do not sbatch this directly.
#SBATCH --job-name=bugarach_sets
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=36
#SBATCH --mem=64G
#SBATCH --time=08:00:00
set -euo pipefail
: "${BUGARACH_REPO:?}" "${BUGARACH_GL_OUT:?}" "${BUGARACH_SETS:?}"
VENV="${BUGARACH_VENV:-$HOME/bugarach-venv}"
read -r -a SETS <<< "$BUGARACH_SETS"
SET="${SETS[$SLURM_ARRAY_TASK_ID]}"
OUT="$BUGARACH_GL_OUT/$SET"
mkdir -p "$OUT"
cd "$BUGARACH_REPO"
export PYTHONPATH="$BUGARACH_REPO/src" PYTHONUTF8=1
# The search keeps each recording's floor under $OUT/floor_cache, so a rerun after a node
# reboot does not compute them again.
echo "set $SET   node $(hostname)   cpus $SLURM_CPUS_PER_TASK   commit $(git rev-parse --short HEAD)   $(date -Is)"
"$VENV/bin/python" tools/search_all_settings.py --bench "$SET" --sliding \
    --workers "$SLURM_CPUS_PER_TASK" --out "$OUT"
echo "search finished $(date -Is)"
