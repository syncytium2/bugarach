/* sce — binned SCE, as an object.

   ONE FILE IS ONE DETECTOR: the descriptor the page renders from, and the code
   that runs. Delete this file and sce is gone — picker, controls and algorithm
   together — which is the point of the folder (ADR-0005).

   Assembled into the page at BUILD time, not load time: docs/site is one
   self-contained file making zero requests, so it works from file:// and no
   recording leaves the machine. build_site.py's NETWORK guard enforces it.

   WHAT THE SHELL PROVIDES and this file uses: the shared helpers. `clipSorted`
   is called by five detectors and `matlabPrctile` by three, so they stay in the
   shell — a shared helper living in one detector's file would make deleting
   that file break the others.

   PARITY: `bugarach.detectors.sce` is the other implementation of this, and
   tests/test_webapp_sce_detect_parity.py pins the two. A change here that is
   not made there is a divergence, not an improvement.
*/

// ---- descriptor -------------------------------------------------------------
registerDetector(
{
    key: "sce",
    label: "SCE",
    blurb: "was anything happening",
    ctl: "dSceCtl", fine: "dFineSce",
    read: dt => ({ gridDt: dt,
      binWidthSec: clamp(numById("sBin"), 1, 120),
      thresholdPctile: clamp(numById("sPct"), 80, 99.99),
      nSurrogates: Math.round(clamp(numById("sSur"), 20, 2000)) }),
    run: (trains, range, cfg) => sceDetect(trains, range, cfg),
    settings: cfg => "bin " + cfg.binWidthSec + " s · "
      + cfg.thresholdPctile + "th percentile of " + cfg.nSurrogates
      + " shuffles · one bar per window · floor 3 ROIs",
    params: { binWidthSec: "sBin", thresholdPctile: "sPct", nSurrogates: "sSur" },
    knob: { key: "thresholdPctile", input: "sPct", name: "threshold percentile", unit: "",
            scale: "tail", grid: [90.0, 95.0, 98.0, 99.0, 99.5, 99.9] },
  }
);

// ---- algorithm --------------------------------------------------------------
function sceDetect(trains, range, opts) {
  const o = opts || {};
  const bw = o.binWidthSec === undefined ? 10.0 : o.binWidthSec;
  const pctile = o.thresholdPctile === undefined ? 99.0 : o.thresholdPctile;
  const nSur = o.nSurrogates === undefined ? 200 : o.nSurrogates;
  const minRois = o.minRois === undefined ? 3 : o.minRois;
  const mgap = o.mergeGapSec === undefined ? NaN : o.mergeGapSec;
  const u = rng32(o.seed === undefined ? 20260706 : o.seed);

  const wLo = range[0], wHi = range[1];
  const empty = { starts: [], ends: [], widths: [], magnitude: [],
                  magTotal: [], threshold: NaN, obs: new Float64Array(0),
                  bctr: new Float64Array(0), nEvents: 0 };
  if (wHi <= wLo) return empty;

  const lw = wHi - wLo;
  const ev = clipSorted(trains, wLo, wHi);
  const nRoi = ev.length;
  const nBins = Math.max(1, Math.ceil(lw / bw));
  const bctr = new Float64Array(nBins);
  for (let i = 0; i < nBins; i++) bctr[i] = wLo + (i + 0.5) * bw;
  // the bin index is CLIPPED into range rather than dropped, so the last bin
  // takes the window's final instant — same rule CoactDetect uses, and not the
  // `discretize` rule LoCo uses
  const binOf = t => {
    let i = Math.floor((t - wLo) / bw);
    return i < 0 ? 0 : (i > nBins - 1 ? nBins - 1 : i);
  };

  const obs = new Float64Array(nBins);
  for (const v of ev) {
    if (!v.length) continue;
    const seen = new Set();
    for (const x of v) seen.add(binOf(x));
    for (const i of seen) obs[i] += 1;
  }

  let thr;
  if (o.threshold !== undefined) {
    thr = o.threshold;
  } else {
    // one offset per ROI per surrogate, and EMPTY ROIs ARE DRAWN FOR — they
    // consume their place in the stream even though they contribute nothing
    const draws = new Float64Array(nSur * nRoi);
    for (let i = 0; i < draws.length; i++) draws[i] = u() * lw;
    const nullCounts = new Float64Array(nSur * nBins);
    for (let r = 0; r < nRoi; r++) {
      if (!ev[r].length) continue;
      for (let s = 0; s < nSur; s++) {
        const d = draws[s * nRoi + r];
        const act = new Set();
        for (const x of ev[r]) {
          let sh = (x - wLo + d) % lw;
          if (sh < 0) sh += lw;
          act.add(binOf(wLo + sh));
        }
        for (const i of act) nullCounts[s * nBins + i] += 1;
      }
    }
    thr = matlabPrctile(nullCounts, pctile);
  }

  const sig = [];
  for (let i = 0; i < nBins; i++) if (obs[i] > thr && obs[i] >= minRois) sig.push(i);
  if (!sig.length) {
    return { ...empty, threshold: thr, obs, bctr };
  }

  // every in-window event with its bin and its ROI — the merge and the episode
  // statistics are both computed from these rather than from the bins
  const evTimes = [], evBin = [], evRoi = [];
  for (let r = 0; r < nRoi; r++)
    for (const x of ev[r]) { evTimes.push(x); evBin.push(binOf(x)); evRoi.push(r); }
  const binFirst = new Float64Array(nBins).fill(NaN);
  const binLast = new Float64Array(nBins).fill(NaN);
  for (let k = 0; k < evTimes.length; k++) {
    const b = evBin[k];
    if (Number.isNaN(binFirst[b]) || evTimes[k] < binFirst[b]) binFirst[b] = evTimes[k];
    if (Number.isNaN(binLast[b]) || evTimes[k] > binLast[b]) binLast[b] = evTimes[k];
  }

  const runs = [];
  let cs = sig[0], ce = sig[0], runLast = binLast[sig[0]];
  for (let k = 1; k < sig.length; k++) {
    const b = sig[k];
    // NaN gap compares false and therefore never merges — which is also what
    // the default merge_gap of NaN means
    if (binFirst[b] - runLast <= mgap) { ce = b; runLast = binLast[b]; }
    else { runs.push([cs, ce]); cs = ce = b; runLast = binLast[b]; }
  }
  runs.push([cs, ce]);

  const starts = [], ends = [], widths = [], mag = [], magTotal = [];
  for (const [fb, lb] of runs) {
    let mx = -Infinity;
    for (let b = fb; b <= lb; b++) if (obs[b] > mx) mx = obs[b];
    const rois = new Set();
    let tfirst = Infinity, tlast = -Infinity;
    for (let k = 0; k < evTimes.length; k++) {
      if (evBin[k] >= fb && evBin[k] <= lb) {
        rois.add(evRoi[k]);
        if (evTimes[k] < tfirst) tfirst = evTimes[k];
        if (evTimes[k] > tlast) tlast = evTimes[k];
      }
    }
    const w = rois.size ? tlast - tfirst : NaN;
    // the reported onset is the BIN's start, not the first event in it
    starts.push(wLo + fb * bw);
    widths.push(w);
    ends.push(wLo + fb * bw + (Number.isNaN(w) ? 0 : w));
    mag.push(mx);
    magTotal.push(rois.size);
  }
  return { starts, ends, widths, magnitude: mag, magTotal, threshold: thr,
           obs, bctr, nEvents: starts.length };
}
