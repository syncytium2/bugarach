/* cicada — the sixth detector (key `cicada`), as an object.

   ONE FILE IS ONE DETECTOR: the descriptor the page renders from, and the code
   that runs. Delete this file and cicada is gone — picker, controls and algorithm
   together — which is the point of the folder (ADR-0005).

   Assembled into the page at BUILD time, not load time: docs/site is one
   self-contained file making zero requests, so it works from file:// and no
   recording leaves the machine. build_site.py's NETWORK guard enforces it.

   WHAT THE SHELL PROVIDES and this file uses: the shared helpers. `clipSorted`
   is called by five detectors and `matlabPrctile` by three, so they stay in the
   shell — a shared helper living in one detector's file would make deleting
   that file break the others.

   PARITY: `bugarach.detectors.cicada` is the other implementation of this, and
   tests/test_webapp_cicada_detect_parity.py pins the two. A change here that is
   not made there is a divergence, not an improvement.
*/

// ---- descriptor -------------------------------------------------------------
registerDetector(
{
    key: "cicada",
    /* NOT IN THIS BUILD — see `WITHHELD` below the registry. It carries no
       `unavailable` field on purpose: that mechanism draws the row, disables it
       and says why, and this detector is not to be present at all.

       ⚠ THIS ENTRY BRIEFLY HAD TWO `unavailable` KEYS, from two sessions
       withholding it on the same day for different stated reasons. JS takes the
       last one silently, so the page shipped one reason while the file contained
       two. Neither survives; the decision is a list now, and a list cannot hold
       the same key twice. */
    label: "sixth", blurb: "how many cells at once",
    ctl: "dCicCtl", fine: "dFineCicada",
    // NEEDS THE PEAK, which is why it carries a flag the other five do not: its
    // raster is anchored on `locs`, and the folder has to have sent enough to
    // locate one. `cicadaTrains` decides that and refuses in words when it cannot.
    peaks: true,
    read: dt => ({ gridDt: dt,
      scePercentile: clamp(numById("cPct"), 80, 99.99),
      nSurrogates: Math.round(clamp(numById("ciSur"), 20, 2000)),
      nSynchronousFrames: Math.round(clamp(numById("cSync"), 1, 50)),
      sceMinDistanceFrames: Math.round(clamp(numById("cDist"), 1, 200)),
      activeDurationSec: clamp(numById("cDur"), 0.1, 60),
      perEventDuration: document.getElementById("cPer").value === "per_event" }),
    run: (trains, range, cfg, extra) =>
      cicadaDetect(extra.peakTrains, extra.durTrains, range, cfg),
    settings: cfg => cfg.scePercentile + "th percentile of " + cfg.nSurrogates
      + " rolls · " + cfg.nSynchronousFrames + " frame window · peaks "
      + cfg.sceMinDistanceFrames + " frames apart · active "
      + (cfg.perEventDuration ? "per event (the folder's own width_sec)"
                              : cfg.activeDurationSec + " s")
      + " · dt " + cfg.gridDt + " s",
    /* `perEventDuration` is a boolean in `cfg` and a two-valued select on the
       page, so the map says which control and which value means true — a
       settings file has to be able to write it and read it back. */
    params: { scePercentile: "cPct", nSurrogates: "ciSur",
              nSynchronousFrames: "cSync", sceMinDistanceFrames: "cDist",
              activeDurationSec: "cDur",
              perEventDuration: { input: "cPer", on: "per_event", off: "fixed" } },
    /* A SINGLE CELL IS NOT A COINCIDENCE, and on a sparse folder CICADA will
       report a great many of them. The threshold comes from rolled surrogates,
       and where the raster is nearly empty the 99th percentile of that pool
       lands at one active cell — so every isolated transient clears it. Checked
       against the Python rather than assumed: on the same sparse input its own
       coactivity trace is identical frame for frame and it picks the same kind
       of peaks. The port is faithful; the operating point is degenerate.

       Counted and said out loud rather than filtered away. Raising a floor until
       the awkward rows disappear is the move FOUNDATIONS §9 forbids in terms,
       and the reader deciding whether locust suits their preparation needs to
       see this rather than have it tidied. */
    extra: { head: "of those, one cell only",
             count: d => (d.magnitude || []).filter(m => m <= 1).length },
    note: n => n ? n + " of these are single-cell moments. This detector's "
      + "threshold comes from rolling the raster, and where the recording is "
      + "sparse that threshold lands at one active cell — so an isolated "
      + "transient clears it and is reported as a coincidence. The detector is "
      + "doing what it does; the recording is too sparse for the answer to be "
      + "about coordination. The rule it implements was built for imaging where "
      + "many cells are active at once. Look "
      + "at how many cells the strongest events actually carry before reading "
      + "anything into the count." : null,
    knob: { key: "scePercentile", input: "cPct", name: "SCE percentile", unit: "",
            scale: "tail", grid: [90.0, 95.0, 98.0, 99.0, 99.5, 99.9] },
  }
);

// ---- algorithm --------------------------------------------------------------
function cicadaDetect(peakTrains, durTrains, range, opts) {
  const o = opts || {};
  const dt = o.gridDt === undefined ? 0.1 : o.gridDt;
  const nsync = Math.max(1, Math.round(o.nSynchronousFrames === undefined
                                       ? 1 : o.nSynchronousFrames));
  const pctile = o.scePercentile === undefined ? 99.0 : o.scePercentile;
  const nSur = o.nSurrogates === undefined ? 100 : o.nSurrogates;
  const minDist = Math.max(1, Math.round(o.sceMinDistanceFrames === undefined
                                         ? 4 : o.sceMinDistanceFrames));
  const adur = o.activeDurationSec === undefined ? 1.0 : o.activeDurationSec;
  const perEvent = !!o.perEventDuration;
  const u = rng32(o.seed === undefined ? 20260706 : o.seed);

  const wLo = range[0], wHi = range[1];
  const empty = { starts: [], ends: [], widths: [], magnitude: [], magTotal: [],
                  threshold: NaN, obs: new Float64Array(0),
                  bctr: new Float64Array(0), nEvents: 0 };
  if (wHi <= wLo) return empty;

  const nf = Math.max(1, Math.floor((wHi - wLo) / dt));
  const nc = peakTrains.length;
  if (nc < 1) return empty;
  const dframes = Math.max(1, Math.floor(adur / dt + 0.5));

  /* logical [nc x nf], each event active from its own frame for its own length.
     A frame outside the window is SKIPPED, not clamped to an edge: clamping
     would pile every out-of-range event onto frame 0 and invent a synchrony
     there. */
  const raster = [];
  for (let c = 0; c < nc; c++) {
    const row = new Uint8Array(nf);
    const v = peakTrains[c] || [], d = (durTrains && durTrains[c]) || null;
    for (let k = 0; k < v.length; k++) {
      const t = v[k];
      if (!Number.isFinite(t)) continue;
      const f = Math.floor((t - wLo) / dt);
      if (f < 0 || f >= nf) continue;
      let df = dframes;
      if (perEvent && d) {
        const dv = d[k];
        df = Number.isFinite(dv) ? Math.max(1, Math.floor(dv / dt + 0.5)) : 1;
      }
      const hi = Math.min(nf, f + df);
      for (let j = f; j < hi; j++) row[j] = 1;
    }
    raster.push(row);
  }

  // distinct cells active in each nsync-frame sliding window
  const m = nf - nsync;
  if (m < 1) return empty;
  const obs = new Float64Array(m);
  for (let c = 0; c < nc; c++) {
    const row = raster[c];
    let inWin = 0;
    for (let j = 0; j < nsync; j++) inWin += row[j];
    for (let i = 0; i < m; i++) {
      if (inWin > 0) obs[i] += 1;
      inWin -= row[i];
      if (i + nsync < nf) inWin += row[i + nsync];
    }
  }

  /* CICADA's get_sce_threshold: roll each cell by randi(nf-1), sum active cells
     PER FRAME, pool every surrogate together, take the percentile of the pool.
     Pooled rather than per-surrogate — the threshold is one number about the
     whole recording, and taking a percentile per surrogate and averaging is a
     different statistic that looks just as reasonable. */
  let threshold = 0;
  if (nf >= 2) {
    const pool = new Float64Array(nSur * nf);
    for (let s = 0; s < nSur; s++) {
      const off = s * nf;
      for (let c = 0; c < nc; c++) {
        const row = raster[c];
        const k = Math.floor(u() * (nf - 1)) + 1;      // MATLAB randi(nf-1)
        for (let j = 0; j < nf; j++) {
          // np.roll(row, k)[j] === row[(j - k) mod nf]
          let src = j - k; if (src < 0) src += nf;
          pool[off + j] += row[src];
        }
      }
    }
    threshold = matlabPrctile(Array.from(pool), pctile);
  }

  /* local maxima >= threshold, plateau taking its LEFT edge (> left, >= right),
     thinned tallest-first to at least minDist apart with earlier winning ties */
  const cand = [];
  for (let i = 0; i < m; i++) {
    if (!(obs[i] >= threshold) || obs[i] <= 0) continue;
    const l = i > 0 ? obs[i - 1] : -Infinity;
    const r = i < m - 1 ? obs[i + 1] : -Infinity;
    if (obs[i] > l && obs[i] >= r) cand.push(i);
  }
  cand.sort((a, b) => obs[b] - obs[a] || a - b);
  const kept = [];
  for (const i of cand)
    if (kept.every(j => Math.abs(i - j) >= minDist)) kept.push(i);
  kept.sort((a, b) => a - b);

  const starts = [], ends = [], widths = [], magnitude = [], magTotal = [];
  for (const i of kept) {
    const s = wLo + i * dt, e = wLo + (i + nsync) * dt;
    starts.push(s); ends.push(e); widths.push(e - s);
    magnitude.push(obs[i]);
    magTotal.push(obs[i]);
  }
  const bctr = new Float64Array(m);
  for (let i = 0; i < m; i++) bctr[i] = wLo + (i + nsync / 2) * dt;
  return { starts, ends, widths, magnitude, magTotal, threshold, obs, bctr,
           nEvents: starts.length };
}
