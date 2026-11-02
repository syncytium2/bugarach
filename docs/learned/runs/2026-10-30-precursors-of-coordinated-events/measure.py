"""Can a coordinated event be predicted? Baseline windows only, per stream.

Events = CoactDetect calls, variant own_floor, from run 2026-09-24-detect-66-floors.
Reads the default export (senktide_ttx) for onsets. Exploratory.
Usage: python precursor.py <calls.csv> <outdir> [--drop-pinned]
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.stats import rankdata

def roc_auc_score(y, p):
    y = np.asarray(y); r = rankdata(p); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

def average_precision_score(y, p):
    y = np.asarray(y)[np.argsort(-np.asarray(p))]; tp = np.cumsum(y)
    return (tp / np.arange(1, len(y) + 1))[y == 1].mean()

class LR:
    def fit(self, X, y, l2=1.0):
        X = np.asarray(X, float); y = np.asarray(y, float)
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-12
        Z = np.c_[np.ones(len(X)), (X - self.mu) / self.sd]
        def f(w):
            z = Z @ w; ll = np.sum(np.logaddexp(0, z) - y * z) + 0.5 * l2 * w[1:] @ w[1:]
            g = Z.T @ (1 / (1 + np.exp(-z)) - y); g[1:] += l2 * w[1:]
            return ll, g
        self.w = minimize(f, np.zeros(Z.shape[1]), jac=True, method="L-BFGS-B").x
        self.coef_ = self.w[1:][None]
        return self
    def predict_proba(self, X):
        Z = np.c_[np.ones(len(X)), (np.asarray(X, float) - self.mu) / self.sd]
        p = 1 / (1 + np.exp(-(Z @ self.w)))
        return np.c_[1 - p, p]
from bugarach import dataset

GROUPS = ["DI", "OVX", "MALE", "ORX"]
PINNED = {"20260629_312", "20260629_309", "20260630_316", "20250926_235"}
PAD = 1.0          # participant pad, as PARTICIPANT_PAD_SEC
PRE, POST = 120, 30  # peri-event range, s
ISO = 60           # isolated: no call onset in the preceding ISO s
GAP, HOR = 5.0, 10.0  # predict a call onset in (t+GAP, t+GAP+HOR]
rng = np.random.RandomState(0)

calls_path, out = Path(sys.argv[1]), Path(sys.argv[2])
drop = "--drop-pinned" in sys.argv
out.mkdir(parents=True, exist_ok=True)
folder = dataset.current()
sl = pd.read_csv(folder / "slices.csv", dtype={"slice_id": str})
rg = pd.read_csv(folder / "regions.csv", dtype={"slice_id": str})
rg = rg[rg.label == "baseline"].set_index("slice_id")
calls = pd.read_csv(calls_path, dtype={"slice_id": str})
calls = calls[(calls.window_kind == "baseline") & (calls.detector == "coact") & (calls.variant == "own_floor")]
if drop:
    sl = sl[~sl.slice_id.isin(PINNED)]

recs = []  # per recording x stream dicts
for _, s in sl.iterrows():
    sid = s.slice_id
    ev = pd.read_csv(folder / f"{sid}.csv")
    a, b = rg.loc[sid, "analysis_start_sec"], rg.loc[sid, "analysis_end_sec"]
    for stream in ["fast", "slow"]:
        e = ev[(ev.stream == stream) & (ev.time_sec >= a) & (ev.time_sec < b)]
        c = calls[(calls.slice_id == sid) & (calls.stream == stream)].sort_values("onset_sec")
        recs.append(dict(sid=sid, group=s.group_id, mouse=str(s.mouse_id),
                         stream=stream, a=a, b=b, n=int(s.n_roi_recorded),
                         t=e.time_sec.to_numpy(), roi=e.roi.to_numpy(),
                         con=c.onset_sec.to_numpy(), cw=c.width_sec.to_numpy()))

def pop_rate(r, edges):
    h, _ = np.histogram(r["t"], edges)
    return h / r["n"] / np.diff(edges)

def isolated(r, t0):
    return not np.any((r["con"] < t0) & (r["con"] >= t0 - ISO))

res = {"dataset": dataset.stamp(), "drop_pinned": drop, "streams": {}}
peri, partic, icis, pred_rows = {}, {}, {}, []
bins = np.arange(-PRE, POST + 1, 1.0)
for stream in ["fast", "slow"]:
    R = [r for r in recs if r["stream"] == stream]
    # ---- A. inter-call intervals
    rows = []
    for r in R:
        if len(r["con"]) >= 4:
            d = np.diff(r["con"])
            rows.append(dict(sid=r["sid"], group=r["group"], ncalls=len(r["con"]), cv=d.std(ddof=1) / d.mean(),
                             med=np.median(d), rho=np.corrcoef(d[:-1], d[1:])[0, 1] if len(d) >= 4 else np.nan,
                             ici=d.tolist()))
    icis[stream] = pd.DataFrame(rows)
    # ---- B. peri-event population rate, events vs random isolated anchors
    curves = []
    for r in R:
        mean_rate = len(r["t"]) / r["n"] / (r["b"] - r["a"])
        if mean_rate == 0: continue
        ev_t = [t0 for t0 in r["con"] if isolated(r, t0) and t0 - PRE >= r["a"] and t0 + POST <= r["b"]]
        if not ev_t: continue
        def curve(t0):
            return pop_rate(r, t0 + bins) / mean_rate
        E = np.mean([curve(t0) for t0 in ev_t], axis=0)
        ctrl = []
        for _ in range(400):
            t0 = rng.uniform(r["a"] + PRE, r["b"] - POST)
            if isolated(r, t0): ctrl.append(curve(t0))
        C = np.mean(ctrl, axis=0)
        # non-participant ROIs only, against the SAME ROI set at random isolated times
        def curve_set(tc, keep_rois):
            keep = np.isin(r["roi"], keep_rois)
            h, _ = np.histogram(r["t"][keep], tc + bins)
            return h / max(len(keep_rois), 1) / mean_rate
        ENP, CNP = [], []
        for t0 in ev_t:
            w = r["cw"][np.argmin(abs(r["con"] - t0))]
            part = set(r["roi"][(r["t"] >= t0 - PAD) & (r["t"] <= t0 + w + PAD)])
            nonp = [x for x in range(1, r["n"] + 1) if x not in part]
            ENP.append(curve_set(t0, nonp))
            cc = []
            for _ in range(100):
                tc = rng.uniform(r["a"] + PRE, r["b"] - POST)
                if isolated(r, tc) and abs(tc - t0) > 60: cc.append(curve_set(tc, nonp))
            CNP.append(np.mean(cc, axis=0) if cc else np.full(len(bins) - 1, np.nan))
        ENP, CNP = np.mean(ENP, axis=0), np.nanmean(CNP, axis=0)
        curves.append(dict(sid=r["sid"], group=r["group"], mouse=r["mouse"], nev=len(ev_t), E=E, C=C, ENP=ENP, CNP=CNP))
    peri[stream] = curves
    # ---- C. do the upcoming participants have onsets early? pre-window [-30,-2] s
    prow = []
    for r in R:
        T = r["b"] - r["a"]
        for t0, w in zip(r["con"], r["cw"]):
            if not isolated(r, t0) or t0 - 30 < r["a"]: continue
            part = np.unique(r["roi"][(r["t"] >= t0 - PAD) & (r["t"] <= t0 + w + PAD)])
            if len(part) == 0: continue
            def frac(tc):
                m = (r["t"] >= tc - 30) & (r["t"] < tc - 2)
                tot = m.sum()
                return np.nan if tot == 0 else np.isin(r["roi"][m], part).sum() / tot, tot
            f_ev, n_ev = frac(t0)
            # null: same participant set at random isolated times far from this event
            fn = []
            for _ in range(200):
                tc = rng.uniform(r["a"] + 30, r["b"])
                if abs(tc - t0) > 60 and isolated(r, tc):
                    v, _ = frac(tc)
                    if not np.isnan(v): fn.append(v)
            # rate expectation
            cnt = pd.Series(r["roi"]).value_counts()
            f_rate = cnt.reindex(part).fillna(0).sum() / max(cnt.sum(), 1)
            # mirror window after the event, [end+2, end+30], if no call starts there
            e = t0 + w
            f_post = np.nan
            if e + 30 <= r["b"] and not np.any((r["con"] > t0) & (r["con"] < e + 30)):
                m = (r["t"] > e + 2) & (r["t"] <= e + 30)
                if m.sum(): f_post = np.isin(r["roi"][m], part).sum() / m.sum()
            prow.append(dict(sid=r["sid"], group=r["group"], mouse=r["mouse"], f_ev=f_ev, n_pre=n_ev, f_post=f_post,
                             f_null=np.mean(fn) if fn else np.nan, f_rate=f_rate,
                             share_part=len(part) / r["n"]))
    partic[stream] = pd.DataFrame(prow)
    # ---- D. prediction table, 1 s steps
    for r in R:
        mean_rate = len(r["t"]) / r["n"] / (r["b"] - r["a"])
        if mean_rate == 0: continue
        cend = r["con"] + r["cw"]
        incall = np.zeros(len(r["t"]), bool)
        for c0, c1 in zip(r["con"], cend):
            incall |= (r["t"] >= c0 - PAD) & (r["t"] <= c1 + PAD)
        tb = r["t"][~incall]
        for t in np.arange(r["a"] + 60, r["b"] - GAP - HOR, 1.0):
            inside = np.any((t >= r["con"] - PAD) & (t <= cend + PAD))
            if inside or np.any((r["con"] > t) & (r["con"] <= t + GAP)):
                continue
            y = int(np.any((r["con"] > t + GAP) & (r["con"] <= t + GAP + HOR)))
            prev = cend[cend < t]
            since = t - prev.max() if len(prev) else t - r["a"]
            def rate(lo, hi):
                return ((r["t"] >= t - hi) & (r["t"] < t - lo)).sum() / r["n"] / (hi - lo) / mean_rate
            m5 = (r["t"] >= t - 5) & (r["t"] < t)
            # max distinct ROIs in any 2 s window in the last 10 s
            tt, rr = r["t"][(r["t"] >= t - 10) & (r["t"] < t)], r["roi"][(r["t"] >= t - 10) & (r["t"] < t)]
            mx = max((len(set(rr[(tt >= x) & (tt < x + 2)])) for x in tt), default=0)
            pred_rows.append(dict(stream=stream, sid=r["sid"], group=r["group"], mouse=r["mouse"], y=y,
                                  log_since=np.log(since), no_prev=int(len(prev) == 0),
                                  r5=rate(0, 5), r30=rate(5, 30), r60=rate(30, 60),
                                  d5=len(set(r["roi"][m5])) / r["n"], mx2=mx / r["n"],
                                  b30=((tb >= t - 30) & (tb < t - 5)).sum() / r["n"] / 25 / mean_rate,
                                  b60=((tb >= t - 60) & (tb < t - 30)).sum() / r["n"] / 30 / mean_rate,
                                  b5=((tb >= t - 5) & (tb < t)).sum() / r["n"] / 5 / mean_rate))

P = pd.DataFrame(pred_rows)
FEATS = ["log_since", "r5", "r30", "r60", "d5", "mx2", "b5", "b30", "b60"]
# label-free within-recording z-scores, so a model can only learn WHEN, not WHICH recording
for f in FEATS:
    g = P.groupby(["stream", "sid"])[f]
    P[f + "_z"] = (P[f] - g.transform("mean")) / (g.transform("std") + 1e-9)
P.to_csv(out / "prediction_table.csv", index=False)
# univariate within-recording AUC, recordings with >= 3 calls in the baseline window
uni = []
ncalls = {(r["stream"], r["sid"]): len(r["con"]) for r in recs}
for (stream, sid), g in P.groupby(["stream", "sid"]):
    if ncalls[(stream, sid)] < 3 or g.y.nunique() < 2: continue
    gi = g[(g.no_prev == 1) | (g.log_since > np.log(60))]  # nothing called in the last 60 s
    for f in FEATS:
        uni.append(dict(stream=stream, sid=sid, group=g.group.iloc[0], mouse=g.mouse.iloc[0], feat=f,
                        auc=roc_auc_score(g.y, g[f]), ncalls=ncalls[(stream, sid)],
                        auc_iso=roc_auc_score(gi.y, gi[f]) if gi.y.nunique() == 2 else np.nan))
pd.DataFrame(uni).to_csv(out / "univariate_within_auc.csv", index=False)
FS = {"timing_z": ["log_since_z"], "activity_z": ["r5_z", "r30_z", "r60_z", "d5_z", "mx2_z"],
      "all_z": [f + "_z" for f in FEATS],"timing": ["log_since", "no_prev"],
      "activity": ["r5", "r30", "r60", "d5", "mx2"],
      "all": ["log_since", "no_prev", "r5", "r30", "r60", "d5", "mx2"]}
auc = []
for stream in ["fast", "slow"]:
    D = P[P.stream == stream].reset_index(drop=True)
    for fs, cols in FS.items():
        D[f"p_{fs}"] = np.nan
        for m in D.mouse.unique():  # leave one mouse out
            tr, te = D.mouse != m, D.mouse == m
            if D.y[tr].nunique() < 2: continue
            mdl = LR()
            mdl.fit(D.loc[tr, cols], D.y[tr])
            D.loc[te, f"p_{fs}"] = mdl.predict_proba(D.loc[te, cols])[:, 1]
        for sid, g in D.groupby("sid"):
            if g.y.nunique() == 2:
                auc.append(dict(stream=stream, fs=fs, sid=sid, group=g.group.iloc[0], auc=roc_auc_score(g.y, g[f"p_{fs}"]),
                                ap=average_precision_score(g.y, g[f"p_{fs}"]), prev=g.y.mean(), n_pos=g.y.sum()))
        pooled = roc_auc_score(D.y, D[f"p_{fs}"])
        res["streams"].setdefault(stream, {})[f"pooled_auc_{fs}"] = pooled
    # coefficients of the all-feature model on everything (for sign only)
    mdl = LR().fit(D[FS["all"]], D.y)
    res["streams"][stream]["coef_all"] = dict(zip(FS["all"], mdl.coef_[0].round(3).tolist()))
    res["streams"][stream]["n_steps"] = int(len(D)); res["streams"][stream]["prevalence"] = float(D.y.mean())
AUC = pd.DataFrame(auc)

import pickle
pickle.dump(dict(res=res, peri=peri, partic=partic, icis=icis, AUC=AUC), open(out / "precursor.pkl", "wb"))
AUC.to_csv(out / "auc_by_recording.csv", index=False)
for k in icis: icis[k].drop(columns="ici").to_csv(out / f"ici_{k}.csv", index=False)
for k in partic: partic[k].to_csv(out / f"participants_pre_{k}.csv", index=False)
json.dump(res, open(out / "results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
print(AUC.groupby(["stream", "fs"]).auc.describe())
