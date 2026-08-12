#!/usr/bin/env bash
# check_vendor_freshness.sh — are bugarach's vendored copies current?
#
# bugarach vendors from TWO upstreams, so per the session protocol it needs one
# freshness entry per family:
#
#   session-protocol : docs/session_protocol.md + .claude/hooks/session-start.sh
#                      <- interface2
#   murderboard      : tools/murderboard_freshness.sh   <- syncytium2/murderboard
#
# This wrapper exists for ONE reason beyond convenience, and it is a safety
# property — see the WARNING below. Do not replace it with bare calls to
# murderboard_freshness.sh.
#
# ---------------------------------------------------------------------------
# WARNING — upstream defect in murderboard_freshness.sh (present at b2b2ba2).
#
# `--slug` generalizes the gate to any vendoring relationship, but the offline
# fallback list `CLONE_CANDIDATES` was never generalized with it: it is a fixed
# list of *murderboard* paths ($HOME/Documents/murderboard, ...) that does not
# vary with --slug. Resolution order is gh -> local clone. So for a family whose
# slug `gh` cannot resolve, the gate silently answers with ANOTHER family's HEAD.
#
# Observed here 2026-08-12: `gh api repos/syncytium2/interface2` returns 404
# (not a public repo under that slug), so a session-protocol check without
# --clone resolved to murderboard's HEAD (635c5a8) and reported the vendored
# copy STALE. It was current. The header's promise of "never a false current"
# does not hold across families — and a false STALE is its own harm, because a
# gate that cries wolf gets ignored.
#
# The workaround, enforced below: NEVER check the interface2 family without an
# explicit --clone. If we do not know where that clone is, we report UNKNOWN
# rather than let the gate answer from the wrong repo.
# ---------------------------------------------------------------------------
#
# USAGE
#   bash tools/check_vendor_freshness.sh            check both families
#   bash tools/check_vendor_freshness.sh --verbose  print verdicts even when current
#
# ENV
#   BUGARACH_INTERFACE2  path to a local interface2 clone. Required for the
#                        session-protocol family (see WARNING). Machine-local:
#                        never hardcode it (sapper SAP004).
#   MURDERBOARD_REPO     path to a local murderboard clone (optional; the
#                        murderboard family resolves fine over gh).
#
# EXIT   0 = all checked families current   1 = something STALE   2 = undetermined

set -u
root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "not a git repo"; exit 2; }
GATE="$root/tools/murderboard_freshness.sh"
[ -r "$GATE" ] || { echo "missing $GATE"; exit 2; }

VERBOSE=""
[ "${1:-}" = "--verbose" ] && VERBOSE="--verbose"

rc=0

# --- family 1: the session protocol, vendored from interface2 ----------------
if [ -n "${BUGARACH_INTERFACE2:-}" ] && [ -d "${BUGARACH_INTERFACE2}/.git" ]; then
  bash "$GATE" $VERBOSE \
    --label session-protocol \
    --slug syncytium2/interface2 \
    --clone "$BUGARACH_INTERFACE2" \
    --file docs/session_protocol.md \
    --file .claude/hooks/session-start.sh || rc=$?
else
  echo "session-protocol: UNKNOWN — set BUGARACH_INTERFACE2 to a local interface2" \
       "clone. Not guessing: without it the gate answers from the wrong repo" \
       "(see the WARNING in this file)."
  [ "$rc" -eq 0 ] && rc=2
fi

# --- family 2: the murderboard review harness --------------------------------
# List EVERY vendored file of the family: the gate takes the first one's stamp as
# the family's version and reports the others if they disagree, which is how a
# half-finished re-vendor (process doc bumped, skill left behind) gets caught.
bash "$GATE" $VERBOSE \
  --label murderboard \
  --slug syncytium2/murderboard \
  --file docs/doc_review_process.md \
  --file tools/murderboard_roster.sh \
  --file tools/fetch_paper.py \
  --file tools/murderboard_freshness.sh \
  --file .claude/skills/murderboard/SKILL.md \
  || { [ $? -eq 1 ] && rc=1 || { [ "$rc" -eq 0 ] && rc=2; }; }

exit $rc
