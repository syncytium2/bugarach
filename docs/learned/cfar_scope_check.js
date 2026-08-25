// Exercise the model half of cfar_scope.html in node, so the claims the page
// makes in prose are the ones its own arithmetic produces.
//
//     node docs/learned/cfar_scope_check.js
//
// It extracts the model functions from the page rather than re-implementing
// them, so this cannot drift from what a reader sees. Every number quoted in
// docs/reviews/cfar_demo_2026-08-24.md comes from a run of this file.
const fs = require("fs");
const path = require("path");

const src = fs.readFileSync(path.join(__dirname, "cfar_scope.html"), "utf8");
const body = src.match(/<script>([\s\S]*)<\/script>/)[1];
const model = body.slice(body.indexOf("var VARIANTS="),
                         body.indexOf("/* ---------- canvas helpers"));

global.window = { matchMedia: () => ({ matches: false }) };
const M = new Function("window", model +
  "\nreturn {VARIANTS,VIDS,state,makeScene,realize,refStats,zOf,alphas,mulberry32,dB,osK};"
)(global.window);

function trial(scenario, R, G, snr, pfa, nrec) {
  Object.assign(M.state, { scenario, R, G, snr, pfa });
  const A = M.alphas();
  const sc = M.makeScene();
  const lo = R + G, hi = sc.n - 1 - R - G;
  const inZone = i => sc.zone && i >= sc.zone[0] && i <= sc.zone[1];
  const acc = {};
  M.VIDS.forEach(v => (acc[v] = { hit: 0, tot: 0, fa: 0, tested: 0, zfa: 0, ztested: 0 }));

  for (let k = 0; k < nrec; k++) {
    const x = M.realize(sc, M.mulberry32(1000 + k * 7717));
    for (let i = lo; i <= hi; i++) {
      const isT = sc.tset.has(i);
      if (!isT && sc.skirt.has(i)) continue;   // target energy: neither hit nor alarm
      const st = M.refStats(x, i, R, G), z = inZone(i);
      for (const v of M.VIDS) {
        const det = x[i] > A[v] * M.zOf(v, st, R);
        if (isT) { acc[v].tot++; if (det) acc[v].hit++; }
        else {
          acc[v].tested++; if (det) acc[v].fa++;
          if (z) { acc[v].ztested++; if (det) acc[v].zfa++; }
        }
      }
    }
  }
  const out = {};
  for (const v of M.VIDS) {
    const a = acc[v];
    out[v] = {
      alpha: A[v],
      pd: a.hit / a.tot,
      pfa: a.fa / a.tested,
      ratio: a.fa / a.tested / pfa,
      zratio: a.ztested ? a.zfa / a.ztested / pfa : null,
    };
  }
  return out;
}

function show(title, r) {
  console.log("\n" + title);
  console.log("  rule   alpha     Pd      Pfa     x design   in transition");
  for (const v of M.VIDS) {
    const o = r[v];
    console.log("  " + v.padEnd(6) +
      o.alpha.toFixed(2).padStart(6) +
      (100 * o.pd).toFixed(1).padStart(8) + "%" +
      o.pfa.toExponential(2).padStart(10) +
      o.ratio.toFixed(2).padStart(9) + "x" +
      (o.zratio === null ? "        --" : (o.zratio.toFixed(2) + "x").padStart(12)));
  }
}

const N = 300;
show("homogeneous, R=8 G=2 SNR=13dB Pfa=1e-2  (all five calibrated to agree here)",
     trial("flat", 8, 2, 13, 1e-2, N));
show("clutter edge  (GO holds the rate through the transition; SO is worst)",
     trial("edge", 8, 2, 13, 1e-2, N));
show("two close targets  (GO has the worst Pd; SO the best)",
     trial("pair", 8, 2, 13, 1e-2, N));
show("onset ramp  (this preparation's transition, in radar's units)",
     trial("ramp", 8, 2, 13, 1e-2, N));
show("homogeneous, NO guard cells  (self-masking: the spread target raises its own bar)",
     trial("flat", 8, 0, 13, 1e-2, N));
show("two close targets, NO guard cells  (self- and mutual masking together)",
     trial("pair", 8, 0, 13, 1e-2, N));
show("homogeneous at Pfa=1e-3  (the calibration tracks the design point)",
     trial("flat", 8, 2, 13, 1e-3, N));
