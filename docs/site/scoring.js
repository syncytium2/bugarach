/* bugarach — folds and pooling, in the browser
   =============================================

   BEGIN bugarach-scoring (splice marker — see the note at the foot of this file)

   Two pure functions, no DOM and no state. They are the half of
   `tools/fair_bakeoff.py` that makes a number on screen mean something: divide
   the corpus once, fit on the training folds, and report what came back from
   the fold nothing was fitted on.

   Without them the page sweeps one detector's one knob on one recording and
   scores it against that recording's own planted events. Every number that
   comes out is in-sample. It is a demonstration of the sweep, not a measurement
   of the detector, and nothing on the screen distinguishes the two.

   Ports of `bugarach.bench.fold_split` and `bugarach.bench.pool_scores`. Neither
   draws a random number, so they are checked against the Python exactly rather
   than statistically — `tests/test_webapp_scoring_parity.py`, at 1e-9, the same
   bar the browser detectors hold.

   The rule these exist to obey, from `docs/learned/README_for_the_webapp.md`:
   *"`pool_scores` is the single scoring path … Do not compute F1 in the UI
   layer — an earlier version of the regime-shift tool did its own arithmetic
   and put the two halves of a comparison on different metrics."* That is the
   whole reason this is a function and not six lines at the call site. It has
   already gone wrong once at full scale: a review found the learned models
   pooled by hand as hits/detections while the six detectors went through
   `pool_scores`, which excludes the promiscuity probe, and the two halves of a
   comparison captioned "scored by the same rule" sat on different denominators.
   SCE reads precision 0.91 one way and 0.11 the other. */


/* ---- the corpus, divided once ------------------------------------------- */

/* A fold split is worth something only if it is the SAME split for everyone
   being compared. Derive it here and pass it around; deriving it twice invites
   two detectors to be scored on different held-out sets under one heading.

   Fully determined by the base seed and the two counts: recording seeds run
   consecutively from the base and are dealt out in contiguous blocks. No
   shuffle, so there is no random source for the browser and the command line to
   agree about — which is what lets a run here reproduce a split made there. */
function foldSplit({ nFolds = 4, seedsPerFold = 3, baseSeed = 1000 } = {}) {
  // One fold is refused rather than allowed to degenerate: with a single fold
  // there is nothing left to fit on, and what comes back is a held-out score
  // with no training set behind it — the exact claim this split exists to make
  // true.
  if (!Number.isInteger(nFolds) || nFolds < 2)
    throw new Error(`nFolds=${nFolds} leaves no training data — fitting on ` +
                    `three and scoring on the fourth needs at least two folds`);
  if (!Number.isInteger(seedsPerFold) || seedsPerFold < 1)
    throw new Error(`seedsPerFold=${seedsPerFold} makes an empty fold`);
  if (!Number.isInteger(baseSeed))
    throw new Error(`baseSeed=${baseSeed} is not an integer, so the corpus ` +
                    `it names is not reproducible`);

  const seeds = [];
  for (let i = 0; i < nFolds * seedsPerFold; i++) seeds.push(baseSeed + i);

  const checkFold = (held) => {
    if (!Number.isInteger(held) || held < 0 || held >= nFolds)
      throw new Error(`fold ${held} is outside 0..${nFolds - 1}`);
  };
  const foldOf = (seed) => {
    const i = seed - baseSeed;
    if (!Number.isInteger(i) || i < 0 || i >= seeds.length)
      throw new Error(`seed ${seed} is not in this corpus ` +
                      `(${baseSeed}..${baseSeed + seeds.length - 1})`);
    return Math.floor(i / seedsPerFold);
  };

  return {
    seeds, nFolds, seedsPerFold, baseSeed, foldOf,
    /* everything outside the held-out fold — what a knob may be fitted on */
    train: (held) => { checkFold(held); return seeds.filter(s => foldOf(s) !== held); },
    /* the held-out fold — what the reported number is scored on, and the only
       recordings nothing was fitted on */
    test: (held) => { checkFold(held); return seeds.filter(s => foldOf(s) === held); },
  };
}


/* ---- pooling ------------------------------------------------------------- */

/* Pool per-recording scores into one result.

   POOLED COUNTS, NOT THE MEAN OF PER-RECORDING RATIOS. A recording that happens
   to plant fewer events should not carry the same weight as a fuller one, and a
   recording with no detections at all makes precision undefined rather than
   zero. Averaging the ratios gets both wrong and looks identical on screen.

   `scores` are the objects the page's `scoreDetections` returns — nPlanted,
   nDetected, nHit, nFa, byFrac — plus, where a probe exists, hotFa and
   distractorHits. Anything scored against this corpus pools through here,
   including a learned model or a one-off candidate. That is the point of it
   being a function. */
function poolScores(scores, { detector, regime, seeds = [], knobValue = null,
                              tolSec = null } = {}) {
  const list = [...scores];

  /* The tolerance is the number's units, so it travels with it. Scores measured
     at different tolerances are not poolable: counts add whatever they were
     counted against, so mixing them produces a plausible number whose matching
     rule is a blend of two — invisible in the result and invisible on screen. */
  const tols = new Set();
  for (const sc of list) {
    const t = sc.tolSec != null ? sc.tolSec : tolSec;
    if (t == null)
      throw new Error(
        "a pooled score must carry the tolerance it was matched at — pass " +
        "tolSec, or set it on each score. A bare F1 with no tolerance beside " +
        "it reads as timing accuracy, which this bench does not measure.");
    if (!Number.isFinite(t))
      throw new Error(`tolSec=${t} is not a finite number of seconds`);
    tols.add(t);
  }
  if (tols.size > 1)
    throw new Error(
      `cannot pool scores measured at different tolerances: ` +
      `${[...tols].sort((a, b) => a - b).join(", ")} s. A pooled count is ` +
      `only meaningful against one matching rule.`);

  const out = {
    detector, regime, knobValue,
    nPlanted: 0, nDetected: 0, nHit: 0, nFa: 0,
    hotFa: 0, distractorHits: 0,
    byFrac: new Map(),
    seeds: [...seeds],
    /* null only when nothing was pooled — an empty result has no tolerance to
       claim, and neither does the Python it is checked against */
    tolSec: tols.size ? [...tols][0] : null,
  };

  for (const sc of list) {
    out.nPlanted += sc.nPlanted;
    out.nDetected += sc.nDetected;
    out.nHit += sc.nHit;
    out.nFa += sc.nFa;
    out.hotFa += sc.hotFa || 0;
    out.distractorHits += sc.distractorHits || 0;
    const by = sc.byFrac instanceof Map ? sc.byFrac : new Map(sc.byFrac || []);
    for (const [frac, [n, h]] of by) {
      const [pn, ph] = out.byFrac.get(frac) || [0, 0];
      out.byFrac.set(frac, [pn + n, ph + h]);
    }
  }

  /* Detections the headline numbers are computed over — everything outside the
     promiscuity probe. The probe plants no events, so it contributes no hits
     and its firings would otherwise land entirely in the precision denominator.
     The browser's generator plants no probe, so today this equals nDetected and
     the distinction costs nothing; it stops being free the day one is added,
     which is exactly when a page computing its own precision would quietly
     disagree with the Python. */
  out.nScored = out.nDetected - out.hotFa;

  out.recall = out.nPlanted ? out.nHit / out.nPlanted : NaN;

  /* Precision OUTSIDE the probe. Fold the probe in and the headline stops
     measuring the detector and starts measuring how hard the probe was set:
     CICADA reads F1 0.09 that way against 0.68 in the upstream campaign, on 599
     hot-window detections out of 601 false alarms. That is this project's own
     cautionary tale — the benchmark, not the detectors, was the original
     problem — reached by turning one knob too far. */
  out.precision = out.nScored ? out.nHit / out.nScored : NaN;

  out.f1 = (Number.isFinite(out.recall) && Number.isFinite(out.precision)
            && out.recall + out.precision > 0)
    ? 2 * out.recall * out.precision / (out.recall + out.precision)
    : NaN;

  /* Recall at one participation level. The headline hides the thing worth
     knowing: a detector that finds every full-field event and nothing at 10% is
     a different instrument from one that degrades gracefully, and the two can
     share an overall recall. */
  out.recallAt = (frac) => {
    const [n, h] = out.byFrac.get(frac) || [0, 0];
    return n ? h / n : NaN;
  };

  /* The probe's own number, gated separately from precision: firings per minute
     inside the dense-but-random block, where by construction there is nothing
     to find. Takes the window because only the generator knows whether it
     planted one — the browser's does not, and NaN is the honest answer there
     rather than a rate computed against a window that does not exist. */
  out.hotFaPerMin = (hotWindow) => {
    if (!hotWindow) return NaN;
    const minutes = (hotWindow[1] - hotWindow[0]) / 60 *
                    Math.max(1, out.seeds.length);
    return minutes ? out.hotFa / minutes : NaN;
  };

  return out;
}


/* END bugarach-scoring

   Everything above this line is spliced verbatim into
   `docs/site/raster_viewer.html` when the UI phase that consumes it lands. It
   is kept here, and written as plain script rather than a module, because that
   page is a single self-contained file with no `import(` in it — the build
   refuses to publish one that has any, since a page that fetches is a page that
   could send, and this one tells the reader their recordings never leave their
   computer.

   Until that splice, the page has no second copy to drift from. Afterwards it
   would, so `tests/test_webapp_scoring_parity.py` arms a byte-for-byte check
   the moment the markers appear in the viewer: two copies of one scorer is the
   failure this whole file exists to prevent, and it is not going to be caught
   by reading. */

/* The export below is for the test runner only. Pasted into the page, `module`
   is undefined and `typeof` says so without throwing, so the line is inert. */
if (typeof module === "object" && module !== null && module.exports)
  module.exports = { foldSplit, poolScores };
