"""The per-ROI-only discriminator: can a surrogate be told from its own recording one ROI at a time?

A surrogate **leaks** when something other than cross-ROI timing gives it away. This
module is the plan's second tier (``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``,
"The per-ROI-only discriminator — required"): a classifier two-sample test
(Friedman 2003; Lopez-Paz & Oquab 2017) that is **blind to coordination by
construction**, so anything it detects is a leak.

How it stays blind. Every ROI is reduced over time, on its own, to a short feature
vector — onset count, interval quantiles, shortest interval, onsets in the two edge
bands — by the functions in :data:`ROI_FEATURES`, each of which receives one ROI's
onsets and nothing else. Only then are ROIs combined, and only by symmetric
statistics (mean, spread, minimum, median, maximum over ROIs), which cannot tell which
ROI is which, let alone when two ROIs fired together. Two windows whose ROIs have the
same trains up to a relative shift get identical features.

How it is scored. Each real analysis window is paired with the same window of its own
surrogate. A linear logistic model on the within-pair feature difference, with no
intercept, is a forced choice: it calls the window with the higher score real, and
its accuracy is the share of pairs it gets right (a tie — identical features — counts
half). Folds are grouped by mouse, so no mouse is ever in both the training and the
test side of a fold. The null permutes the label **within each pair** — which of the
two is called real — and refits every fold, so the one-sided *P* is the share of
permutations scoring at least the observed accuracy (with the usual +1).

Sizing. α = 0.05 and the smallest effect worth detecting is 55% forced-choice
accuracy (the plan, Table 4). :func:`required_pairs` finds the exact one-sided
binomial test size that detects it with the declared power (0.8 by default — the plan
names α and the effect, not the power, so it is a parameter and it is reported).
Pairs within a mouse are not independent, so the size is also stated **in mice**,
through the design effect of the observed within-mouse correlation of correctness.

Controls. Uniform dither is the positive control (it must be detected) and real
against real the negative control (it must not be); :func:`run_cell` runs both beside
a candidate and :func:`apply_controls` marks the candidate's result void when either
fails, as the plan requires.

Numpy only for the model — no scikit-learn, no torch. ``np.random.RandomState`` for
every draw (sapper SAP002 blocks ``default_rng`` in ``src/``).

``src/bugarach/learn/nets/tiny.py`` is deliberately not used: it sums per-ROI votes
frame by frame, which is a coactivity trace — exactly what a sound surrogate removes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np

__all__ = [
    "ALPHA", "MIN_EFFECT", "POWER", "EDGE_BAND_SECONDS", "INTERVAL_QUANTILES",
    "ROI_FEATURES", "POOL_STATS", "roi_feature_names", "feature_names",
    "roi_features", "pool_symmetric", "window_features", "pair_features",
    "mouse_folds", "fit_pairwise_logistic", "forced_choice", "required_pairs",
    "binomial_power", "within_mouse_icc", "negative_control_pairs",
    "DiscriminatorResult", "apply_controls", "run_cell", "discriminate_windows",
]

ALPHA = 0.05
MIN_EFFECT = 0.55
POWER = 0.8
EDGE_BAND_SECONDS = 5.0           # the plan's edge band, Table 3; callers convert to frames
INTERVAL_QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)


# -- per-ROI features: each function sees ONE ROI's onsets inside ONE window ----------------
#
# ``t`` is a sorted 1-D int64 array of one ROI's frame indices already restricted to the
# half-open ``window``; ``band`` is the edge band in frames. Intervals are in frames and
# enter as log1p, so a zero interval (two onsets in one frame) is 0 and the sub-floor end
# of the distribution — where leaks live — is not crushed by the long tail.

def _count(t: np.ndarray, window, band) -> np.ndarray:
    return np.array([float(t.size)])


def _interval_quantiles(t: np.ndarray, window, band) -> np.ndarray:
    if t.size < 2:
        return np.full(len(INTERVAL_QUANTILES), np.nan)
    return np.log1p(np.quantile(np.diff(t).astype(float), INTERVAL_QUANTILES))


def _shortest_interval(t: np.ndarray, window, band) -> np.ndarray:
    if t.size < 2:
        return np.array([np.nan])
    return np.array([math.log1p(float(np.diff(t).min()))])


def _edge_band(t: np.ndarray, window, band) -> np.ndarray:
    a, b = window
    return np.array([float(np.sum(t < a + band)), float(np.sum(t >= b - band))])


ROI_FEATURES: tuple[tuple[str, tuple[str, ...], Callable], ...] = (
    ("count", ("count",), _count),
    ("interval_quantiles",
     tuple(f"interval_q{int(round(q * 100)):02d}" for q in INTERVAL_QUANTILES),
     _interval_quantiles),
    ("shortest_interval", ("interval_min",), _shortest_interval),
    ("edge_band", ("edge_start", "edge_end"), _edge_band),
)
"""The per-ROI feature functions, in column order: (group, column names, function)."""

POOL_STATS = ("mean", "sd", "min", "median", "max")
"""Symmetric statistics taken over ROIs, per per-ROI column. None depends on ROI order."""


def roi_feature_names() -> list[str]:
    return [c for _, cols, _ in ROI_FEATURES for c in cols]


def feature_names() -> list[str]:
    """Names of the pooled window features, in the order :func:`window_features` returns."""
    names = [f"{s}_{c}" for c in roi_feature_names() for s in POOL_STATS]
    return names + ["frac_active", "frac_with_interval"]


def roi_features(train, window, edge_band) -> np.ndarray:
    """One ROI's feature vector over one analysis window.

    ``train`` is ONE ROI's onsets (1-D frame indices); anything else is refused, so the
    only way ROIs meet is :func:`pool_symmetric` after this reduction.
    """
    t = np.asarray(train)
    if t.ndim != 1:
        raise TypeError(f"roi_features takes one ROI's train (a 1-D array), got shape {t.shape}")
    a, b = int(window[0]), int(window[1])
    t = np.sort(t[(t >= a) & (t < b)].astype(np.int64, copy=False))
    return np.concatenate([np.asarray(fn(t, (a, b), float(edge_band)), dtype=float)
                           for _, _, fn in ROI_FEATURES])


def pool_symmetric(per_roi: np.ndarray) -> np.ndarray:
    """Pool an (n_roi, n_roi_features) matrix over ROIs by symmetric statistics.

    Undefined values (NaN: an ROI with fewer than two onsets has no intervals) are left
    out of each statistic; a column with no defined value pools to zeros, and the two
    trailing shares — ROIs with an onset, ROIs with an interval — say how much was there.
    """
    M = np.asarray(per_roi, dtype=float)
    n_col = len(roi_feature_names())
    if M.ndim != 2 or M.shape[1] != n_col:
        raise ValueError(f"expected (n_roi, {n_col}) per-ROI features, got shape {M.shape}")
    out = []
    for j in range(n_col):
        v = M[:, j]
        v = np.sort(v[~np.isnan(v)])           # sorted: summation order cannot leak ROI order

        if v.size == 0:
            out.extend([0.0] * len(POOL_STATS))
        else:
            out.extend([v.mean(), v.std(), v.min(), float(np.median(v)), v.max()])
    n = M.shape[0]
    count = M[:, 0] if n else np.zeros(0)
    has_iv = ~np.isnan(M[:, 1]) if n else np.zeros(0, bool)
    out.append(float(np.mean(count > 0)) if n else 0.0)
    out.append(float(np.mean(has_iv)) if n else 0.0)
    return np.asarray(out, dtype=float)


def window_features(trains: Sequence, window, edge_band) -> np.ndarray:
    """The pooled feature vector of one stream over one analysis window.

    ``trains`` holds one train per ROI. Each is reduced alone by :func:`roi_features`;
    the reductions are pooled by :func:`pool_symmetric`. Nothing else touches the trains.
    """
    rows = [roi_features(train, window, edge_band) for train in trains]
    M = np.vstack(rows) if rows else np.empty((0, len(roi_feature_names())))
    return pool_symmetric(M)


def pair_features(real: Sequence[Sequence], surrogate: Sequence[Sequence], windows: Sequence,
                  edge_band) -> tuple[np.ndarray, np.ndarray]:
    """Features of every (real window, the same window of its surrogate) pair.

    ``real[k]`` and ``surrogate[k]`` are the ROI trains of one recording's stream and of
    its surrogate; ``windows[k]`` is the analysis window both are cut to; ``edge_band`` is
    a band in frames, or one per pair where frame intervals differ between recordings.
    """
    n = len(windows)
    if len(real) != n or len(surrogate) != n:
        raise ValueError("real, surrogate and windows must have one entry per pair")
    bands = np.broadcast_to(np.asarray(edge_band, dtype=float), (n,))
    Xr = np.array([window_features(real[k], windows[k], bands[k]) for k in range(n)])
    Xs = np.array([window_features(surrogate[k], windows[k], bands[k]) for k in range(n)])
    return Xr.reshape(n, -1), Xs.reshape(n, -1)


# -- folds -----------------------------------------------------------------------------------

def mouse_folds(mice: Sequence, n_folds: int = 5, seed: int = 0) -> np.ndarray:
    """Fold index per pair, every mouse wholly inside one fold, folds balanced in pairs.

    Mice are shuffled with ``seed``, then placed largest first into the fold holding the
    fewest pairs. Fewer mice than folds gives leave-one-mouse-out.
    """
    mice = np.asarray([str(m) for m in mice])
    uniq, inv, sizes = np.unique(mice, return_inverse=True, return_counts=True)
    if uniq.size < 2:
        raise ValueError(f"a mouse-grouped test needs at least two mice, got {uniq.size}")
    k = int(min(n_folds, uniq.size))
    rs = np.random.RandomState(seed)
    order = rs.permutation(uniq.size)
    order = order[np.argsort(-sizes[order], kind="stable")]
    load = np.zeros(k, dtype=np.int64)
    fold_of_mouse = np.empty(uniq.size, dtype=np.int64)
    for m in order:
        f = int(np.argmin(load))
        fold_of_mouse[m] = f
        load[f] += sizes[m]
    return fold_of_mouse[inv]


# -- the model -------------------------------------------------------------------------------

def _sigmoid(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))


def fit_pairwise_logistic(D: np.ndarray, l2: float = 1.0, max_iter: int = 100,
                          tol: float = 1e-9) -> np.ndarray:
    """Weights w minimising Σ log(1 + exp(−D·w)) + (l2/2)|w|², by damped Newton.

    Each row of ``D`` is (labelled-real − labelled-surrogate) features; there is no
    intercept, so the model is symmetric in the pair: swapping the two negates the score.
    """
    D = np.asarray(D, dtype=float)
    n, p = D.shape
    w = np.zeros(p)
    if n == 0:
        return w

    def objective(v):
        return float(np.logaddexp(0.0, -(D @ v)).sum() + 0.5 * l2 * v @ v)

    f = objective(w)
    for _ in range(max_iter):
        z = D @ w
        q = _sigmoid(-z)                                   # P(model wrong) per row
        g = -(D.T @ q) + l2 * w
        H = (D * (q * (1.0 - q))[:, None]).T @ D + l2 * np.eye(p)
        step = np.linalg.solve(H, g)
        t = 1.0
        while True:
            cand = w - t * step
            fc = objective(cand)
            if fc <= f + 1e-12 or t < 1e-8:
                break
            t *= 0.5
        converged = np.linalg.norm(w - cand) < tol * (1.0 + np.linalg.norm(w))
        w, f = cand, fc
        if converged:
            break
    return w


def _scale(X: np.ndarray) -> np.ndarray:
    s = X.std(axis=0)
    s[~np.isfinite(s) | (s < 1e-12)] = 1.0
    return s


def _cv_correct(diff: np.ndarray, scales: dict, folds: np.ndarray, orient: np.ndarray,
                l2: float) -> tuple[np.ndarray, list[np.ndarray]]:
    correct = np.empty(diff.shape[0])
    weights = []
    for f, s in scales.items():
        te = folds == f
        D = diff / s * orient[:, None]
        w = fit_pairwise_logistic(D[~te], l2=l2)
        score = D[te] @ w
        correct[te] = np.where(score > 0, 1.0, np.where(score < 0, 0.0, 0.5))
        weights.append(w)
    return correct, weights


# -- sizing ----------------------------------------------------------------------------------

def binomial_power(n, alpha: float = ALPHA, effect: float = MIN_EFFECT):
    """Exact power of the one-sided binomial test of chance (0.5) at true accuracy ``effect``."""
    from scipy.stats import binom
    n = np.asarray(n)
    crit = binom.ppf(1.0 - alpha, n, 0.5)       # reject when correct > crit
    return binom.sf(crit, n, effect)


def required_pairs(alpha: float = ALPHA, effect: float = MIN_EFFECT, power: float = POWER,
                   n_max: int = 50_000) -> int:
    """Smallest number of independent pairs from which the exact one-sided binomial test at
    ``alpha`` detects ``effect`` with at least ``power`` — at that size **and every larger
    one** (exact binomial power saw-tooths, so the first size to cross can dip back)."""
    n = np.arange(1, n_max + 1)
    ok = binomial_power(n, alpha, effect) >= power
    if not ok[-1]:
        raise ValueError(f"no test size up to {n_max} reaches power {power}")
    bad = np.flatnonzero(~ok)
    return int(n[bad[-1] + 1]) if bad.size else 1


def within_mouse_icc(values: np.ndarray, mice: Sequence) -> float:
    """One-way ANOVA intraclass correlation of per-pair outcomes within mouse, floored at 0."""
    values = np.asarray(values, dtype=float)
    mice = np.asarray([str(m) for m in mice])
    uniq, inv = np.unique(mice, return_inverse=True)
    k, n = uniq.size, values.size
    if k < 2 or n <= k:
        return 0.0
    sizes = np.bincount(inv)
    means = np.bincount(inv, weights=values) / sizes
    grand = values.mean()
    msb = float(np.sum(sizes * (means - grand) ** 2) / (k - 1))
    msw = float(np.sum((values - means[inv]) ** 2) / (n - k))
    m0 = (n - np.sum(sizes ** 2) / n) / (k - 1)
    denom = msb + (m0 - 1.0) * msw
    if denom <= 0:
        return 0.0
    return float(min(1.0, max(0.0, (msb - msw) / denom)))


# -- the test --------------------------------------------------------------------------------

@dataclass
class DiscriminatorResult:
    """One forced-choice test. ``void`` is set by :func:`apply_controls`, never here."""
    accuracy: float
    p_value: float
    n_pairs: int
    n_mice: int
    n_folds: int
    n_permutations: int
    alpha: float
    min_effect: float
    power: float
    required_pairs: int
    pairs_per_mouse: float
    icc: float
    design_effect: float
    required_mice: int
    powered: bool
    significant: bool
    fold_accuracy: list[float] = field(default_factory=list)
    null_accuracy: np.ndarray = field(default_factory=lambda: np.zeros(0), repr=False)
    weights: np.ndarray = field(default_factory=lambda: np.zeros(0), repr=False)
    feature_names: list[str] = field(default_factory=list, repr=False)
    void: bool = False
    void_reason: str = ""

    def top_features(self, k: int = 5) -> list[tuple[str, float]]:
        """The standardised weights of largest magnitude — what gave the surrogate away."""
        if self.weights.size == 0:
            return []
        order = np.argsort(-np.abs(self.weights))[:k]
        names = self.feature_names or [str(i) for i in range(self.weights.size)]
        return [(names[i], float(self.weights[i])) for i in order]

    def summary(self) -> dict:
        """Plain values for a report or a JSON record."""
        return {
            "accuracy": self.accuracy, "p_value": self.p_value,
            "significant": self.significant, "n_pairs": self.n_pairs,
            "n_mice": self.n_mice, "n_folds": self.n_folds,
            "n_permutations": self.n_permutations, "alpha": self.alpha,
            "min_effect": self.min_effect, "power": self.power,
            "required_pairs": self.required_pairs,
            "pairs_per_mouse": self.pairs_per_mouse, "icc": self.icc,
            "design_effect": self.design_effect, "required_mice": self.required_mice,
            "powered": self.powered, "fold_accuracy": list(self.fold_accuracy),
            "null_accuracy_mean": float(self.null_accuracy.mean()) if self.null_accuracy.size else None,
            "top_features": self.top_features(), "void": self.void,
            "void_reason": self.void_reason,
        }


def forced_choice(Xr: np.ndarray, Xs: np.ndarray, mice: Sequence, *, n_folds: int = 5,
                  n_permutations: int = 199, alpha: float = ALPHA,
                  min_effect: float = MIN_EFFECT, power: float = POWER, l2: float = 1.0,
                  seed: int = 0, names: Sequence[str] | None = None) -> DiscriminatorResult:
    """Score real against surrogate, pair by pair, with mouse-grouped folds and a within-pair
    permutation null.

    ``Xr[k]`` and ``Xs[k]`` are the pooled features of pair k's real window and the same
    window of its surrogate; ``mice[k]`` its mouse. Features are scaled per fold by the
    training side's spread (centring cancels in a difference), so a column that never
    varies gets no weight.
    """
    Xr = np.asarray(Xr, dtype=float)
    Xs = np.asarray(Xs, dtype=float)
    if Xr.shape != Xs.shape or Xr.ndim != 2:
        raise ValueError(f"real and surrogate features must be matching 2-D arrays, "
                         f"got {Xr.shape} and {Xs.shape}")
    n = Xr.shape[0]
    if len(mice) != n:
        raise ValueError("one mouse per pair")
    if 1.0 / (n_permutations + 1) >= alpha:
        # The smallest P a permutation test can return is 1/(B + 1). At B = 19 that is
        # 0.05, so P < 0.05 can never happen: a test that cannot reject, refused rather
        # than reported as "not detected".
        raise ValueError(f"{n_permutations} permutations cannot reach P < {alpha}; "
                         f"use at least {math.ceil(1.0 / alpha)}")
    folds = mouse_folds(mice, n_folds, seed)
    uniq_folds = np.unique(folds)
    scales = {int(f): _scale(np.vstack([Xr[folds != f], Xs[folds != f]])) for f in uniq_folds}
    diff = Xr - Xs

    correct, weights = _cv_correct(diff, scales, folds, np.ones(n), l2)
    acc = float(correct.mean())
    fold_acc = [float(correct[folds == f].mean()) for f in uniq_folds]

    rs = np.random.RandomState(seed + 1)
    null = np.empty(n_permutations)
    for b in range(n_permutations):
        orient = np.where(rs.random_sample(n) < 0.5, -1.0, 1.0)
        c, _ = _cv_correct(diff, scales, folds, orient, l2)
        null[b] = c.mean()
    p = float((1 + np.sum(null >= acc - 1e-12)) / (n_permutations + 1))

    mice_s = np.asarray([str(m) for m in mice])
    n_mice = int(np.unique(mice_s).size)
    req = required_pairs(alpha, min_effect, power)
    per_mouse = n / n_mice
    icc = within_mouse_icc(correct, mice_s)
    deff = 1.0 + (per_mouse - 1.0) * icc
    req_mice = int(math.ceil(req * deff / per_mouse))
    return DiscriminatorResult(
        accuracy=acc, p_value=p, n_pairs=n, n_mice=n_mice, n_folds=int(uniq_folds.size),
        n_permutations=int(n_permutations), alpha=alpha, min_effect=min_effect, power=power,
        required_pairs=req, pairs_per_mouse=float(per_mouse), icc=icc, design_effect=deff,
        required_mice=req_mice, powered=bool(n_mice >= req_mice), significant=bool(p < alpha),
        fold_accuracy=fold_acc, null_accuracy=null,
        weights=np.mean(weights, axis=0) if weights else np.zeros(Xr.shape[1]),
        feature_names=list(names) if names is not None else
        (feature_names() if Xr.shape[1] == len(feature_names()) else []))


# -- controls --------------------------------------------------------------------------------

def negative_control_pairs(X: np.ndarray, recording_ids: Sequence, mice: Sequence,
                           seed: int = 0) -> tuple[np.ndarray, np.ndarray, list]:
    """Real against real: each real window paired with another real window of its own
    recording, which of the two is called "real" drawn at random.

    Windows of one recording are paired in their given order, (1st, 2nd), (3rd, 4th), …;
    an odd one out is left unpaired. The random orientation makes the pair exchangeable
    by construction — slow drift within a recording cannot masquerade as a label — so
    this checks the machinery (folds, scaling, the null), and must not be flagged.
    """
    X = np.asarray(X, dtype=float)
    rec = np.asarray([str(r) for r in recording_ids])
    mice = list(mice)
    rs = np.random.RandomState(seed)
    a_idx, b_idx = [], []
    for r in dict.fromkeys(rec):                      # recordings in first-seen order
        idx = np.flatnonzero(rec == r)
        for i in range(0, idx.size - 1, 2):
            a_idx.append(idx[i])
            b_idx.append(idx[i + 1])
    a_idx = np.asarray(a_idx, dtype=np.int64)
    b_idx = np.asarray(b_idx, dtype=np.int64)
    flip = rs.random_sample(a_idx.size) < 0.5
    first = np.where(flip, b_idx, a_idx)
    second = np.where(flip, a_idx, b_idx)
    return X[first], X[second], [mice[i] for i in a_idx]


def apply_controls(result: DiscriminatorResult, positive: DiscriminatorResult | None,
                   negative: DiscriminatorResult | None) -> DiscriminatorResult:
    """Mark ``result`` void when a control fails: uniform dither not detected (no power
    here), or real against real flagged (the test is broken). A missing control is itself
    a reason — an uncontrolled result is not reported as clean."""
    reasons = []
    if positive is None:
        reasons.append("positive control (uniform dither) not run")
    elif not positive.significant:
        reasons.append(f"positive control (uniform dither) not detected: accuracy "
                       f"{positive.accuracy:.3f}, P = {positive.p_value:.3g}")
    if negative is None:
        reasons.append("negative control (real against real) not run")
    elif negative.significant:
        reasons.append(f"negative control (real against real) flagged: accuracy "
                       f"{negative.accuracy:.3f}, P = {negative.p_value:.3g}")
    result.void = bool(reasons)
    result.void_reason = "; ".join(reasons)
    return result


def run_cell(Xr: np.ndarray, Xs: np.ndarray, mice: Sequence, recording_ids: Sequence, *,
             X_positive: np.ndarray | None, seed: int = 0, **kw
             ) -> tuple[DiscriminatorResult, DiscriminatorResult | None, DiscriminatorResult | None]:
    """One grid cell: the candidate, its positive control and its negative control.

    ``X_positive`` is the features of the same windows under uniform dither (generated by
    the caller, over the generation window, like any candidate); ``None`` leaves the
    positive control unrun and the candidate void. Returns (candidate, positive, negative),
    the candidate already passed through :func:`apply_controls`.
    """
    cand = forced_choice(Xr, Xs, mice, seed=seed, **kw)
    pos = (forced_choice(Xr, X_positive, mice, seed=seed, **kw)
           if X_positive is not None else None)
    Xa, Xb, neg_mice = negative_control_pairs(Xr, recording_ids, mice, seed=seed)
    neg = None
    if len(set(map(str, neg_mice))) >= 2:
        neg = forced_choice(Xa, Xb, neg_mice, seed=seed, **kw)
    return apply_controls(cand, pos, neg), pos, neg


def discriminate_windows(real: Sequence[Sequence], surrogate: Sequence[Sequence],
                         windows: Sequence, mice: Sequence, edge_band, **kw
                         ) -> DiscriminatorResult:
    """:func:`pair_features` then :func:`forced_choice`, for callers holding trains."""
    Xr, Xs = pair_features(real, surrogate, windows, edge_band)
    return forced_choice(Xr, Xs, mice, **kw)
