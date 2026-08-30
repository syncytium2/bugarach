/* loco — LoCo, as an object.

   ONE FILE IS ONE DETECTOR: the descriptor the page renders from, and the code
   that runs. Delete this file and loco is gone — picker, controls and algorithm
   together — which is the point of the folder (ADR-0005).

   Assembled into the page at BUILD time, not load time: docs/site is one
   self-contained file making zero requests, so it works from file:// and no
   recording leaves the machine. build_site.py's NETWORK guard enforces it.

   WHAT THE SHELL PROVIDES and this file uses: the shared helpers. `clipSorted`
   is called by five detectors and `matlabPrctile` by three, so they stay in the
   shell — a shared helper living in one detector's file would make deleting
   that file break the others.

   PARITY: `bugarach.detectors.loco` is the other implementation of this, and
   tests/test_webapp_loco_detect_parity.py pins the two. A change here that is
   not made there is a divergence, not an improvement.
*/

// ---- descriptor -------------------------------------------------------------
registerDetector(
{
    key: "loco",
    label: "LoCo",
    blurb: "how many together",
    ctl: "dLocoCtl", fine: "dFineLoco",
    read: dt => ({ gridDt: dt,
      binWidthSec: clamp(numById("lBin"), 0.1, 60),
      contextWinSec: clamp(numById("lCtx"), 10, 1200),
      thresholdPctile: clamp(numById("lPct"), 90, 99.9999),
      nSurrogates: Math.round(clamp(numById("lSur"), 20, 1000)) }),
    run: (trains, range, cfg) => locoDetect(trains, range, cfg),
    settings: cfg => "bin " + cfg.binWidthSec + " s · context "
      + cfg.contextWinSec + " s · " + cfg.thresholdPctile + "th percentile of "
      + cfg.nSurrogates + " shuffles · floor 3 ROIs",
    params: { binWidthSec: "lBin", contextWinSec: "lCtx",
              thresholdPctile: "lPct", nSurrogates: "lSur" },
    knob: { key: "thresholdPctile", input: "lPct", name: "threshold percentile", unit: "",
            scale: "tail", grid: [99.0, 99.5, 99.9, 99.99, 99.999, 99.9999] },
  }
);

// ---- algorithm --------------------------------------------------------------
function locoDetect(trains, range, opts) {
  const o = opts || {};
  const binw = o.binWidthSec === undefined ? 1.0 : o.binWidthSec;
  const mgap = o.mergeGapSec === undefined ? 2.0 : o.mergeGapSec;
  const ctx = o.contextWinSec === undefined ? 120.0 : o.contextWinSec;
  const pctile = o.thresholdPctile === undefined ? 99.9 : o.thresholdPctile;
  const tstep = o.thrStepSec === undefined ? 15.0 : o.thrStepSec;
  const nSur = o.nSurrogates === undefined ? 100 : o.nSurrogates;
  // min_rois is NOT a knob and is not exposed. FOUNDATIONS §9: a nonzero
  // coactivity excess is evidence about the preparation, not a false-alarm floor
  // to raise until it goes away.
  const minRois = o.minRois === undefined ? 3 : o.minRois;
  const u = rng32(o.seed === undefined ? 20260706 : o.seed);

  const tLo = range[0], tHi = range[1];
  const halfCtx = ctx / 2;
  const ev = clipSorted(trains, tLo, tHi);

  let edges = matlabColon(tLo, binw, tHi);
  if (edges.length < 2) edges = Float64Array.from([tLo, tHi]);
  const nb = edges.length - 1;
  const bc = new Float64Array(nb);
  for (let i = 0; i < nb; i++) bc[i] = edges[i] + binw / 2;
  const sObs = distinctCoact(ev, edges);

  const anchors = matlabColon(tLo, tstep, tHi);
  const thrA = new Float64Array(anchors.length);
  for (let ai = 0; ai < anchors.length; ai++) {
    const a = anchors[ai];
    // the segment IS the region here — see the note at the top of this block
    const tl = thresholdPool(ev, Math.max(a - halfCtx, tLo), a, binw, nSur, pctile, u);
    const tr = thresholdPool(ev, a, Math.min(a + halfCtx, tHi), binw, nSur, pctile, u);
    thrA[ai] = Math.max(tl, tr);
  }
  const thrBin = new Float64Array(nb);
  for (let i = 0; i < nb; i++) {
    let best = 0, bd = Infinity;
    for (let k = 0; k < anchors.length; k++) {
      const d = Math.abs(bc[i] - anchors[k]);
      if (d < bd) { bd = d; best = k; }          // np.argmin takes the FIRST
    }
    thrBin[i] = thrA[best];
  }
  if (o.thresholds) for (let i = 0; i < nb; i++) thrBin[i] = o.thresholds[i];

  const fb = [];
  for (let i = 0; i < nb; i++) if (sObs[i] > thrBin[i] && sObs[i] >= minRois) fb.push(i);
  const runs = [];
  if (fb.length) {
    const gapB = Math.max(1, matlabRound(mgap / binw));
    let cur = [fb[0]];
    for (let k = 1; k < fb.length; k++) {
      if (fb[k] - cur[cur.length - 1] <= gapB) cur.push(fb[k]);
      else { runs.push(cur); cur = [fb[k]]; }
    }
    runs.push(cur);
  }

  const starts = [], ends = [], mag = [], magTotal = [], thr = [], widths = [];
  for (const gi of runs) {
    const b0 = gi[0], b1 = gi[gi.length - 1];
    const sp = spanOf(ev, edges[b0], edges[b1 + 1]);
    let pk = 0;
    for (let k = 1; k < gi.length; k++) if (sObs[gi[k]] > sObs[gi[pk]]) pk = k;  // first max
    starts.push(sp.tfirst);
    ends.push(sp.tlast);
    widths.push(sp.tlast - sp.tfirst);
    mag.push(sObs[gi[pk]]);
    magTotal.push(sp.nrec);
    thr.push(thrBin[gi[pk]]);
  }
  return { starts, ends, widths, magnitude: mag, magTotal, threshold: thr,
           bc, sObs, thrBin, nEvents: starts.length };
}
