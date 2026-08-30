/* sync — SPIKE-synch, as an object.

   ONE FILE IS ONE DETECTOR: the descriptor the page renders from, and the code
   that runs. Delete this file and sync is gone — picker, controls and algorithm
   together — which is the point of the folder (ADR-0005).

   Assembled into the page at BUILD time, not load time: docs/site is one
   self-contained file making zero requests, so it works from file:// and no
   recording leaves the machine. build_site.py's NETWORK guard enforces it.

   WHAT THE SHELL PROVIDES and this file uses: the shared helpers. `clipSorted`
   is called by five detectors and `matlabPrctile` by three, so they stay in the
   shell — a shared helper living in one detector's file would make deleting
   that file break the others.

   PARITY: `bugarach.detectors.sync` is the other implementation of this, and
   tests/test_webapp_sync_detect_parity.py pins the two. A change here that is
   not made there is a divergence, not an improvement.
*/

// ---- descriptor -------------------------------------------------------------
registerDetector(
{
    key: "sync",
    label: "SPIKE-synch",
    blurb: "how aligned",
    ctl: "dSyncCtl", fine: "dFineSync",
    /* OFF IN THIS BUILD (Tony, 2026-08-24). The page keeps the whole detector —
       `syncDetect` still runs, its parity test still calls it, and a
       `detections.csv` that already holds sync rows still draws — but nothing on
       the page can SELECT it, so no new run produces one.

       Why it is a field and not a deletion. Removing the row would take the
       parity harness, the ability to read back an older file, and the reason
       with it, leaving a page that is silently missing a detector nobody can
       ask about. `unavailable` says which detector, and why, on the control
       that would otherwise offer it. Same principle as the rail's `gated`: not
       in this build, drawn anyway, with the absence explained rather than
       hidden. Deleting the row is a different change and wants its own argument.

       To turn it back on, delete this one field. */
    unavailable: "The Python gained a fixed-window mode for the coincidence "
      + "window and this page did not, so 'adaptive' on the page means one of "
      + "two things. The page's profile is a second implementation rather than "
      + "a copy of the Python's, and unlike the scorer nothing pins the two "
      + "together — so they could already have drifted and no test would say "
      + "so. Off until a profile parity test exists.",
    /* THE ONLY `read` WITH NO `gridDt`, and the only one that needs none: its
       bin width is the detector's own calibrated resolution rather than the
       recording's frame interval. See SYNC_PROFILE_BIN_SEC. Because it is a
       parameter of the detector it goes into `detector_settings.csv` like any
       other, where the five grid-building detectors' interval is carried per
       recording in `frame_interval_sec` instead. */
    read: () => ({ profileBinSec: SYNC_PROFILE_BIN_SEC,
      tauMax: clamp(numById("dTau"), 0.01, 10),
      maxGap: clamp(numById("dGap"), 0.1, 30),
      CThreshold: clamp(numById("dC"), 0.001, 1),
      CMin: clamp(numById("dCmin"), 0.001, 1) }),
    run: (trains, range, cfg) => syncDetect(trains, range, cfg),
    settings: cfg => "coincidence cap " + cfg.tauMax + " s · max gap " + cfg.maxGap
      + " s · C " + cfg.CThreshold + " to start, " + cfg.CMin + " to sustain"
      + " · profile bin " + cfg.profileBinSec + " s (calibrated, not the frame "
      + "interval)",
    params: { tauMax: "dTau", maxGap: "dGap", CThreshold: "dC", CMin: "dCmin" },
    fixed: ["profileBinSec"],
    // an extra per-region column, and the sentence that explains it once the run
    // is over — both optional, both owned by the detector that needs them
    extra: { head: "of those, artifact",
             count: d => (d.isArtifact || []).filter(Boolean).length },
    note: n => n ? n + " of these are flagged as artifact — C is near-total, the "
      + "event is narrow, and most of the field is in it. That combination is a "
      + "stage knock rather than coordination. They are counted here and drawn "
      + "like the rest; deciding what to do with them is yours." : null,
    knob: { key: "CThreshold", input: "dC", name: "C to start an event", unit: "",
            scale: "log", grid: [0.005, 0.01, 0.02, 0.04, 0.08, 0.12] },
  }
);

// ---- algorithm --------------------------------------------------------------
/* SpikyDetect3's hysteresis scan, transliterated rather than tidied. A bin over
   C_threshold opens an event; bins over the lower C_min keep it open across gaps
   shorter than max_gap, and empty bins are stepped over without closing it. The
   control flow re-tests a gap it has not recomputed and lets the outer cursor
   jump to the bin that ended the event; both are load-bearing, because the
   Python they are checked against does the same and the MATLAB before it did. */
function syncDetect(trains, tRange, opts) {
  const o = opts || {};
  const tauMax = o.tauMax === undefined ? 0.25 : o.tauMax;
  const maxGap = o.maxGap === undefined ? 0.5 : o.maxGap;
  const Cthr = o.CThreshold === undefined ? 0.1 : o.CThreshold;
  const Cmin = o.CMin === undefined ? 0.1 : o.CMin;
  const minN = o.minN === undefined ? 3 : o.minN;
  /* THE PROFILE BIN, WHICH IS NOT THE FRAME INTERVAL. `sync.py` names this
     `PROFILE_BIN_SEC` and argues it at length: nothing upstream of the binning
     touches a grid, so this is the resolution of the DETECTOR — the way a
     spectrogram's window length belongs to the analyst and not the microphone —
     and it is the width the hysteresis thresholds were calibrated at. Wiring
     the recording's interval into it moves the detector off its operating
     point, which is exactly what this page did until now. `gridDt` is still
     honoured because the parity tests pass it by that name. */
  const dt = o.profileBinSec !== undefined ? o.profileBinSec
           : (o.gridDt === undefined ? SYNC_PROFILE_BIN_SEC : o.gridDt);
  const stat = o.statistic === undefined ? "mean" : o.statistic;
  const athr = o.artifactThreshold === undefined ? 0.85 : o.artifactThreshold;
  const afthr = o.artifactThresholdFraction === undefined ? 0.70 : o.artifactThresholdFraction;
  const aplat = o.artifactThresholdPlat90 === undefined ? 0.8 : o.artifactThresholdPlat90;

  const ev = clipSorted(trains, tRange[0], tRange[1]);
  const prof = adaptiveProfile(trains, tRange, tauMax);
  const { cx, cy, cn } = binnedSynchrony(prof.x, prof.y, dt, tRange, stat);
  const n2 = cy.length;

  const starts = [], ends = [], amps = [];
  let i = -1;
  while (i < n2 - 1) {
    i += 1;
    if (cy[i] > Cthr) {
      let cmean = cy[i], ncmean = 1;
      const evBegin = cx[i];
      let evEnd = evBegin, evSum = cn[i];
      let j = i + 1;
      let gap = j < n2 ? cx[j] - cx[i] : Infinity;
      while (j < n2 - 1 && gap < maxGap) {
        while (j < n2 - 2 && cy[j] === 0 && gap < maxGap) { j += 1; gap = cx[j] - cx[i]; }
        if (gap <= maxGap && cy[j] > Cmin) {
          cmean += cy[j]; ncmean += 1; evSum += cn[j];
          evEnd = cx[j]; i = j; j += 1;
        } else { i = j; break; }
      }
      if (evBegin === evEnd) evEnd = evEnd + dt;
      if (evSum >= minN) { starts.push(evBegin); ends.push(evEnd); amps.push(cmean / ncmean); }
    }
  }

  const art = flagArtifacts(starts, ends, amps, cx, cy, ev, athr, afthr, aplat);
  return { starts, ends, amps,
           widths: starts.map((s, k) => ends[k] - s),
           peakC: Array.from(art.peakC), plat90: Array.from(art.plat90),
           nParticipatingRois: Array.from(art.nPart), isArtifact: art.isArtifact,
           nTotalRois: trains.length,
           profileX: prof.x, profileY: prof.y, cx, cy, cn,
           nEvents: starts.length };
}
