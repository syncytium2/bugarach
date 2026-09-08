#!/usr/bin/env bash
# instrument: propagation
# check_vendor_freshness.sh — are bugarach's vendored copies current?
#
# bugarach vendors from TWO upstreams, so per the session protocol it needs one
# freshness entry per family:
#
#   session-protocol : docs/session_protocol.md + .claude/hooks/session-start.sh
#                      <- interface2
#   murderboard      : tools/murderboard_freshness.sh   <- syncytium2/murderboard
#   draughtsman      : third_party/draughtsman/ + the spec it draws from
#                      <- syncytium2/draughtsman
#
# This wrapper exists for ONE reason beyond convenience, and it is a safety
# property — see the WARNING below. Do not replace it with bare calls to
# murderboard_freshness.sh.
#
# ---------------------------------------------------------------------------
# HISTORY — upstream defect in murderboard_freshness.sh, FIXED at a46e255.
#
# `--slug` generalizes the gate to any vendoring relationship, but the offline
# fallback list `CLONE_CANDIDATES` was never generalized with it: it is a fixed
# list of *murderboard* paths ($HOME/Documents/murderboard, ...) that does not
# vary with --slug. Resolution order is gh -> local clone. So for a family whose
# slug `gh` cannot resolve, the gate silently answers with ANOTHER family's HEAD.
#
# Observed here 2026-08-12; fixed upstream 2026-08-17 (murderboard PR #13), where
# the guessed clone paths became slug-scoped: they are consulted only when the slug
# names murderboard, so another family with an unreachable upstream now gets
# "cannot determine" instead of murderboard's HEAD. This wrapper stays for the
# per-family invocation it already does; the safety property it was written for is
# now upstream.
#
# Original report: `gh api repos/syncytium2/interface2` returns 404
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
#   bash tools/check_vendor_freshness.sh            check all three families
#   bash tools/check_vendor_freshness.sh --verbose  print verdicts even when current
#
# ENV
#   BUGARACH_INTERFACE2  path to a local interface2 clone. Required for the
#                        session-protocol family (see WARNING). Machine-local:
#                        never hardcode it (sapper SAP004).
#   MURDERBOARD_REPO     path to a local murderboard clone (optional; the
#                        murderboard family resolves fine over gh).
#   BUGARACH_DRAUGHTSMAN path to a local draughtsman clone (optional; the repo is
#                        private, so this is the offline route when gh cannot
#                        reach it. Machine-local: never hardcode it, SAP004).
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
  --file tools/murderboard_freshness.sh \
  --file .claude/skills/murderboard/SKILL.md \
  || { [ $? -eq 1 ] && rc=1 || { [ "$rc" -eq 0 ] && rc=2; }; }

# --- family 3: draughtsman, the figure pipeline ------------------------------
# WHY A WHOLE PACKAGE AND A SPEC ARE ONE FAMILY. tools/make_architecture_diagram.py
# runs draughtsman's trace -> check -> render over the LIVE build_tube(), so the
# code and the spec that drives it have to come from the same upstream commit: a
# spec written against a newer reference grammar, or a renderer newer than the
# spec it draws, is a half-finished re-vendor. The gate takes the first file's
# stamp as the family's version and reports the others when they disagree, which
# is exactly that check.
#
# The stamp lives on __init__.py rather than on all twelve modules, so a re-vendor
# is one recursive copy plus one line, not a twelve-file diff.
#
# --clone is passed only when the env var names a real checkout. Written as a
# string rather than an array because this runs under bash 3.2 on macOS, where
# expanding an empty array under `set -u` is itself an error -- the same reason
# $VERBOSE above is unquoted.
DRAUGHTSMAN_CLONE=""
if [ -n "${BUGARACH_DRAUGHTSMAN:-}" ] && [ -d "${BUGARACH_DRAUGHTSMAN}/.git" ]; then
  DRAUGHTSMAN_CLONE="--clone ${BUGARACH_DRAUGHTSMAN}"
fi
bash "$GATE" $VERBOSE $DRAUGHTSMAN_CLONE \
  --label draughtsman \
  --slug syncytium2/draughtsman \
  --file third_party/draughtsman/__init__.py \
  --file docs/learned/architecture.spec.json \
  || { [ $? -eq 1 ] && rc=1 || { [ "$rc" -eq 0 ] && rc=2; }; }

# --- family 4: armory, the file-send gate and its remedy ----------------------
# ADDED WITH THE FAMILY ITSELF, deliberately. These two files arrived vendored on
# 2026-09-03, and the alternative was to land them with no freshness check at all
# — which is the defect this whole gate exists to answer, in a different costume:
# a copy that cannot say it has fallen behind. The estate had just paid for it.
# The stranded branch `vendor-send-goes-nowhere` carried these same two files
# pinned at 9e62f10 while armory's canonical had moved to 1469e7a, and nothing
# anywhere in this repo would have said so.
#
# THE TWO ARE ONE FAMILY because the hook points at the remedy:
# send-goes-nowhere.py tells a session its file reached nobody and names
# `tools/show.py` as what to do instead. A hook newer than the tool it recommends,
# or a tool whose interface moved under the hook's advice, is a half-finished
# re-vendor — which is exactly what listing both under one label catches.
ARMORY_CLONE=""
if [ -n "${BUGARACH_ARMORY:-}" ] && [ -d "${BUGARACH_ARMORY}/.git" ]; then
  ARMORY_CLONE="--clone ${BUGARACH_ARMORY}"
fi
bash "$GATE" $VERBOSE $ARMORY_CLONE \
  --label armory \
  --slug syncytium2/armory \
  --file tools/show.py \
  --file .claude/hooks/send-goes-nowhere.py \
  || { [ $? -eq 1 ] && rc=1 || { [ "$rc" -eq 0 ] && rc=2; }; }

# --- family 3: draughtsman, which draws the front page's model figure --------
# THE HEADER OF THIS FILE HAS NAMED THIS FAMILY SINCE THE DAY IT WAS WRITTEN AND THE
# CODE NEVER CHECKED IT. That is not a missing feature, it is the failure mode this
# whole file is about: a gate that DESCRIBES a check reads exactly like one that
# performs it, and nobody re-reads a header to see whether the body agrees with it.
#
# What it cost, 2026-09-05: `third_party/draughtsman/` sat pinned at cb7fc2a while
# draughtsman fixed, in bb83174, an edge that routed through the box it was meant to
# bypass. The front page published that figure for three days. Nothing was red.
#
#   python3 <draughtsman>/tools/edge_collisions.py docs/learned/architecture.svg
#     mean -> concat  runs through 'dog': 56 of 147 units (38%) clips it   (x2)
#
# `syncytium2/draughtsman` resolves over `gh` — checked, not assumed, because the
# WARNING at the top of this file is about a family whose slug does NOT resolve and
# which therefore answered with another repository's HEAD. This one needs no --clone.
#
# ⚠ THE SPEC IS DELIBERATELY NOT LISTED HERE. `docs/learned/architecture.spec.json`
# began as draughtsman's `examples/tube/spec.json` and has since diverged on purpose:
# upstream added `layout.wrap`, which folds the figure into a column and is right for
# a documentation page and wrong for this one, which is a wide banner. Listing it
# would report a deviation we intend as staleness, every run, until someone silenced
# the gate. It needs a stamp that can say "derived from, with deviations" and that
# does not exist yet — see the board entry of 2026-09-05.
bash "$GATE" $VERBOSE \
  --label draughtsman \
  --slug syncytium2/draughtsman \
  --file third_party/draughtsman/__init__.py \
  || { [ $? -eq 1 ] && rc=1 || { [ "$rc" -eq 0 ] && rc=2; }; }

exit $rc
