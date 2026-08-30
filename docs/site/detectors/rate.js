/* rate — RateDetect, as an object.

   ONE FILE IS ONE DETECTOR: the descriptor the page renders from, and the code
   that runs. Delete this file and rate is gone — picker, controls and algorithm
   together — which is the whole point of the folder (ADR-0005).

   The page assembles this in at BUILD time, not load time. docs/site is one
   self-contained file making zero requests, so it works from file:// and no
   recording can leave the machine; build_site.py's NETWORK guard enforces it.

   WHAT THE SHELL PROVIDES and this file may use: clamp, numById, eventRate.
   Anything else a detector needs, it brings.

   PARITY: bugarach.detectors.rate is the other implementation of this, and
   tests/test_webapp_rate_detect_parity.py pins the two at 1e-9. A change here
   that is not made there is a divergence, not an improvement.
*/

// ---- descriptor -------------------------------------------------------------
registerDetector(
{
    key: "rate",
    label: "RateDetect",
    blurb: "how fast",
    ctl: "dRateCtl", fine: "dFineRate",
    read: dt => ({ gridDt: dt,
      excessThresholdHz: clamp(numById("dThr"), 0.1, 50),
      rateWin: clamp(numById("dRate"), 0.1, 30),
      contextWin: clamp(numById("dCtx"), 5, 600) }),
    run: (trains, range, cfg) => rateDetect(trains, range, cfg),
    settings: cfg => "threshold " + cfg.excessThresholdHz + " Hz excess · rate window "
      + cfg.rateWin + " s · context " + cfg.contextWin + " s · dt " + cfg.gridDt + " s",
    /* WHICH CONTROL HOLDS WHICH PARAMETER — the map a saved settings file is
       read back through. `read` above is one direction only; without this, a
       file could be written and never loaded, which is provenance that looks
       like provenance and is not. Kept honest by
       `test_webapp_settings_file.py`, which derives the check from this
       registry: every key `read` produces is either in here with a control that
       exists, or declared `fixed`. */
    params: { excessThresholdHz: "dThr", rateWin: "dRate", contextWin: "dCtx" },
    knob: { key: "excessThresholdHz", input: "dThr", name: "excess threshold", unit: "Hz",
            scale: "linear", grid: [0.5, 1, 2, 3, 4, 5, 6, 8] },
  }
);

// ---- algorithm --------------------------------------------------------------
/* The context window is clipped to 0.9x the recording, and the value actually
   used travels with the result — a context wider than the recording is silently
   a different detector. */
function eventRateContext(trains, tRange, windowSec, contextSec, dt) {
  const maxCtx = 0.9 * (tRange[1] - tRange[0]);
  const ctxActual = contextSec >= maxCtx ? maxCtx : contextSec;
  const { rateX, rateY } = eventRate(trains, tRange, windowSec, dt);
  const ctx = eventRate(trains, tRange, ctxActual, dt);
  return { rateX, rateY, ctxY: ctx.rateY, ctxActual };
}

const RATE_PAD_S = 0.5;   // CHARACTERIZATION_PAD_S

/* RateDetect, threshold mode. Grid times whose rate excess over the local
   context clears the threshold, merged when no more than merge_gap_s apart. */
function rateDetect(trains, tRange, opts) {
  const o = opts || {};
  const thr = o.excessThresholdHz === undefined ? 5.0 : o.excessThresholdHz;
  const mergeGap = o.mergeGapS === undefined ? 3.0 : o.mergeGapS;
  const rateWin = o.rateWin === undefined ? 1.0 : o.rateWin;
  const ctxWin = o.contextWin === undefined ? 60.0 : o.contextWin;
  const dt = o.gridDt === undefined ? 0.1 : o.gridDt;

  const { rateX, rateY, ctxY, ctxActual } =
    eventRateContext(trains, tRange, rateWin, ctxWin, dt);
  const m = rateX.length;
  const excess = new Float64Array(m);
  for (let i = 0; i < m; i++) excess[i] = rateY[i] - ctxY[i];

  const cand = [];
  for (let i = 0; i < m; i++) if (excess[i] >= thr) cand.push(rateX[i]);
  let starts = [], ends = [];
  if (cand.length) {
    const brk = [];
    for (let i = 1; i < cand.length; i++)
      if (cand[i] - cand[i - 1] > mergeGap) brk.push(i - 1);
    const s = [0].concat(brk.map(i => i + 1));
    const e = brk.concat([cand.length - 1]);
    for (let i = 0; i < s.length; i++) {
      // a single-bin crossing is likely noise, and the Python drops it
      if (cand[e[i]] - cand[s[i]] > 0) {
        starts.push(cand[s[i]]); ends.push(cand[e[i]]);
      }
    }
  }
  // pad for characterization: onsets sit on a 0.1 s grid and the rate is
  // window-smoothed, so the stats get a margin matching the kernel
  starts = starts.map(x => x - RATE_PAD_S);
  ends = ends.map(x => x + RATE_PAD_S);

  const freqMax = [], freqMean = [];
  for (let i = 0; i < starts.length; i++) {
    let mx = 0, sum = 0, n = 0;
    for (let k = 0; k < m; k++)
      if (rateX[k] >= starts[i] && rateX[k] <= ends[i]) {
        if (rateY[k] > mx) mx = rateY[k];
        sum += rateY[k]; n++;
      }
    if (n) { freqMax.push(mx); freqMean.push(sum / n); }
    else if (m) {
      const mid = (starts[i] + ends[i]) / 2;
      let j = 0, bd = Infinity;
      for (let k = 0; k < m; k++) {
        const d = Math.abs(rateX[k] - mid);
        if (d < bd) { bd = d; j = k; }
      }
      freqMax.push(rateY[j]); freqMean.push(rateY[j]);
    } else { freqMax.push(0); freqMean.push(0); }
  }
  return { starts, ends, freqMax, freqMean, rateX, rateY, ctxY, excess,
           ctxActual, nEvents: starts.length };
}
