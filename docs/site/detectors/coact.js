/* coact — CoactDetect, as an object.

   ONE FILE IS ONE DETECTOR: the descriptor the page renders from, and the code
   that runs. Delete this file and coact is gone — picker, controls and algorithm
   together — which is the point of the folder (ADR-0005).

   Assembled into the page at BUILD time, not load time: docs/site is one
   self-contained file making zero requests, so it works from file:// and no
   recording leaves the machine. build_site.py's NETWORK guard enforces it.

   WHAT THE SHELL PROVIDES and this file uses: the shared helpers. `clipSorted`
   is called by five detectors and `matlabPrctile` by three, so they stay in the
   shell — a shared helper living in one detector's file would make deleting
   that file break the others.

   PARITY: `bugarach.detectors.coact` is the other implementation of this, and
   tests/test_webapp_coact_detect_parity.py pins the two. A change here that is
   not made there is a divergence, not an improvement.
*/

// ---- descriptor -------------------------------------------------------------
registerDetector(
{
    key: "coact",
    label: "CoactDetect",
    blurb: "how unlikely",
    ctl: "dCoactCtl", fine: "dFineCoact",
    read: dt => ({ gridDt: dt,
      intWinSec: clamp(numById("cWin"), 0.1, 60),
      contextWinSec: clamp(numById("cCtx"), 10, 1200),
      alpha: clamp(numById("cAlpha"), 1e-7, 0.5),
      nSurrogates: Math.round(clamp(numById("cSur"), 20, 1000)) }),
    run: (trains, range, cfg) => coactDetect(trains, range, cfg),
    settings: cfg => "bin " + cfg.intWinSec + " s · context " + cfg.contextWinSec
      + " s · alpha " + cfg.alpha + " per bin · " + cfg.nSurrogates
      + " shuffles · floor 3 ROIs",
    params: { intWinSec: "cWin", contextWinSec: "cCtx", alpha: "cAlpha",
              nSurrogates: "cSur" },
    knob: { key: "alpha", input: "cAlpha", name: "alpha", unit: "per bin",
            scale: "log", grid: [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7] },
  }
);

// ---- algorithm --------------------------------------------------------------
function coactDetect(trains, range, opts) {
  const o = opts || {};
  const bw = o.intWinSec === undefined ? 0.5 : o.intWinSec;
  const C = o.contextWinSec === undefined ? 60.0 : o.contextWinSec;
  const minRois = o.minRois === undefined ? 3 : o.minRois;
  const nSur = o.nSurrogates === undefined ? 200 : o.nSurrogates;
  const alpha = o.alpha === undefined ? 0.01 : o.alpha;
  const mgap = o.mergeGapSec === undefined ? 3.0 : o.mergeGapSec;
  const u = rng32(o.seed === undefined ? 20260706 : o.seed);

  const t0 = range[0], t1 = range[1];
  const ev = clipSorted(trains, t0, t1);
  const nb = Math.max(1, Math.ceil((t1 - t0) / bw));
  const edges = new Float64Array(nb + 1);
  for (let k = 0; k <= nb; k++) edges[k] = t0 + k * bw;
  const ctr = new Float64Array(nb);
  for (let k = 0; k < nb; k++) ctr[k] = t0 + (k + 0.5) * bw;

  // distinct ROIs per bin — one per ROI per bin, however often it fired
  const obs = new Float64Array(nb);
  for (const e of ev) {
    if (!e.length) continue;
    const seen = new Set();
    for (const x of e) {
      let b = Math.floor((x - t0) / bw);
      if (b < 0) b = 0; else if (b > nb - 1) b = nb - 1;
      seen.add(b);
    }
    for (const b of seen) obs[b] += 1;
  }

  const z = new Float64Array(nb).fill(NaN);
  const pval = new Float64Array(nb).fill(NaN);
  const nullmean = new Float64Array(nb).fill(NaN);
  const cand = [];
  for (let b = 0; b < nb; b++) if (obs[b] >= minRois) cand.push(b);

  if (o.pvals) {
    for (let b = 0; b < nb; b++) pval[b] = o.pvals[b];
  } else {
    for (const b of cand) {
      const blo = edges[b], bhi = edges[b + 1];
      const cLo = Math.max(t0, ctr[b] - C / 2);
      const cHi = Math.min(t1, ctr[b] + C / 2);
      const cw = cHi - cLo;
      const tlo = blo - cLo, thi = bhi - cLo;
      const ctx = [];
      for (const e of ev) {
        if (!e.length) continue;
        const vv = [];
        for (const x of e) if (x >= cLo && x <= cHi) vv.push(x - cLo);
        if (vv.length) ctx.push(vv);
      }
      // one draw per (surrogate, context ROI), surrogate-major — the same stream
      // shape the MATLAB scalar-rand loops consume
      const counts = new Float64Array(nSur);
      const draws = new Float64Array(nSur * ctx.length);
      for (let i = 0; i < draws.length; i++) draws[i] = u();
      for (let j = 0; j < ctx.length; j++) {
        for (let s = 0; s < nSur; s++) {
          const d = draws[s * ctx.length + j];
          let hit = false;
          for (const x of ctx[j]) {
            let sh = (x + d * cw) % cw;
            if (sh < 0) sh += cw;
            if (sh >= tlo && sh < thi) { hit = true; break; }
          }
          if (hit) counts[s] += 1;
        }
      }
      const st = coactStats(obs[b], counts);
      nullmean[b] = st.mu; z[b] = st.z; pval[b] = st.p;
    }
  }

  // a NaN p-value is not significant — the bin was never a candidate
  const sig = [];
  for (const b of cand) if (pval[b] <= alpha) sig.push(b);

  const startsB = [], endsB = [];
  if (sig.length) {
    let sCur = sig[0], prev = sig[0];
    for (let k = 1; k < sig.length; k++) {
      const b = sig[k];
      // gap measured from the END of the previous significant bin, not its start
      if (edges[b] - edges[prev + 1] <= mgap) prev = b;
      else { startsB.push(sCur); endsB.push(prev); sCur = prev = b; }
    }
    startsB.push(sCur); endsB.push(prev);
  }

  const starts = [], widths = [], ends = [], nrois = [], evZ = [], evP = [];
  for (let k = 0; k < startsB.length; k++) {
    const s = startsB[k], e = endsB[k];
    starts.push(edges[s]);
    widths.push(edges[e + 1] - edges[s]);
    ends.push(edges[e + 1]);
    let mx = -Infinity, zmax = NaN, pmin = NaN;
    for (let b = s; b <= e; b++) {
      if (obs[b] > mx) mx = obs[b];
      // merged episodes span non-candidate bins whose z/p are NaN, and MATLAB's
      // max/min ignore NaN — so these are the nan-variants, not the plain ones
      if (!Number.isNaN(z[b])) zmax = Number.isNaN(zmax) ? z[b] : Math.max(zmax, z[b]);
      if (!Number.isNaN(pval[b])) pmin = Number.isNaN(pmin) ? pval[b] : Math.min(pmin, pval[b]);
    }
    nrois.push(mx); evZ.push(zmax); evP.push(pmin);
  }
  return { starts, ends, widths, nrois, z: evZ, p: evP,
           ctr, obs, zProf: z, pvalProf: pval, nullmean,
           nEvents: starts.length };
}
