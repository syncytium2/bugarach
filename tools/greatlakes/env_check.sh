#!/usr/bin/env bash
# What a Great Lakes login node offers bugarach. Read-only: installs and changes nothing.
#
#   bash tools/greatlakes/env_check.sh
#
# bugarach needs Python 3.14 (pyproject.toml). The university's pages give 2021 versions as
# examples and do not say whether a login node reaches PyPI, so this asks the node itself.
set -u
echo "== host: $(hostname)   date: $(date -Is)"
echo "== python modules"
module -t avail python 2>&1 | grep -i python | head -40
echo "== system python: $(python3 --version 2>&1)"
echo "== uv: $(command -v uv || echo 'not installed') $(uv --version 2>/dev/null)"
for url in https://pypi.org/simple/numpy/ https://github.com https://astral.sh/uv/install.sh; do
  code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' "$url" || echo "no answer")
  echo "== reach $url: $code"
done
echo "== home: $(df -h "$HOME" | tail -1)"
echo "== slurm accounts for this user"
sacctmgr -nP show assoc user="$USER" format=account,partition 2>&1 | sort -u | head -20
