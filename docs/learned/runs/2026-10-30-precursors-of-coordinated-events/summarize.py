import sys, pickle, numpy as np, pandas as pd
out = sys.argv[1]
d = pickle.load(open(f"{out}/precursor.pkl", "rb"))
U = pd.read_csv(f"{out}/univariate_within_auc.csv", dtype={"sid": str})
A = d["AUC"]
rng = np.random.RandomState(1)
GROUPS = ["DI", "OVX", "MALE", "ORX"]

def mouse_boot(df, col, n=2000):
    mice = df.mouse.unique(); per = df.groupby("mouse")[col].apply(list)
    meds = []
    for _ in range(n):
        s = rng.choice(mice, len(mice)); meds.append(np.median(np.concatenate([per[m] for m in s])))
    return np.percentile(meds, [2.5, 97.5])

for st in ["fast", "slow"]:
    print(f"\n######## {st}")
    I = d["icis"][st]
    ici = [np.array(x) for x in I.ici]
    dmin = min(x.min() for x in ici)
    cv_dt = np.array([(x.mean() - dmin) / x.mean() for x in ici])
    print(f"ICI recs(>=4 calls) {len(I)}; CV median {I.cv.median():.2f}; dead-time-Poisson CV median {np.median(cv_dt):.2f}; "
          f"obs<deadtime in {(I.cv.values < cv_dt).mean():.2f}; serial rho median {I.rho.median():.2f}")
    print("  CV by group:", {g: (round(I[I.group == g].cv.median(), 2), int((I.group == g).sum())) for g in GROUPS})
    C = d["peri"][st]; bins = np.arange(-120, 31)[:-1]
    E = np.array([c["E"] for c in C]); Cc = np.array([c["C"] for c in C])
    EN = np.array([c["ENP"] for c in C]); CN = np.array([c["CNP"] for c in C])
    print(f"peri: {len(C)} recs, {sum(c['nev'] for c in C)} isolated events")
    for lo, hi in [(-120, -60), (-60, -30), (-30, -10), (-10, -4)]:
        m = (bins >= lo) & (bins < hi)
        dall = E[:, m].mean(1) - Cc[:, m].mean(1); dnp = EN[:, m].mean(1) - CN[:, m].mean(1)
        print(f"  [{lo},{hi}) s  all ROIs: ratio med {np.median(E[:, m].mean(1) / Cc[:, m].mean(1)):.2f} up in {(dall > 0).mean():.2f}"
              f" | non-participants: ratio med {np.nanmedian(EN[:, m].mean(1) / CN[:, m].mean(1)):.2f} up in {(dnp > 0).mean():.2f}")
    Pp = d["partic"][st].dropna(subset=["f_ev", "f_null"])
    per = Pp.groupby(["sid", "mouse"]).agg(pre=("f_ev", "mean"), null=("f_null", "mean")).reset_index()
    per["d"] = per.pre - per.null
    ci = mouse_boot(per, "d")
    print(f"participants' share of onsets in [-30,-2] s: pre {Pp.f_ev.median():.2f} vs same set at random times {Pp.f_null.median():.2f};"
          f" per-rec diff median {per.d.median():+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}] up in {(per.d > 0).mean():.2f} of {len(per)} recs")
    pp = Pp.dropna(subset=["f_post"])
    print(f"  pre vs post (mirror window after event), {len(pp)} events: pre {pp.f_ev.median():.2f} post {pp.f_post.median():.2f}; "
          f"pre>post in {(pp.f_ev > pp.f_post).mean():.2f}")
    # univariate within-recording AUC
    Us = U[U.stream == st]
    print(f"univariate within-recording AUC (recs with >=3 calls: {Us.sid.nunique()}), predict a call 5-15 s ahead:")
    for f, g in Us.groupby("feat"):
        ci = mouse_boot(g, "auc"); gi = g.dropna(subset=["auc_iso"]); cii = mouse_boot(gi, "auc_iso")
        print(f"  {f:10s} median {g.auc.median():.2f} [{ci[0]:.2f},{ci[1]:.2f}]  >0.5 in {(g.auc > .5).mean():.2f}  "
              f"| no call in last 60 s: {gi.auc_iso.median():.2f} [{cii[0]:.2f},{cii[1]:.2f}] ({len(gi)} recs)  "
              + " ".join(f"{gr}:{g[g.group == gr].auc.median():.2f}({(g.group == gr).sum()})" for gr in GROUPS))
    many = {s for s in Us.sid.unique()}
    Am = A[(A.stream == st) & A.sid.isin(many)]
    Am = Am.merge(U[["sid", "mouse"]].drop_duplicates(), on="sid")
    print("model (leave-one-mouse-out), within-recording AUC, recs >=3 calls:")
    for fs, g in Am.groupby("fs"):
        ci = mouse_boot(g, "auc")
        print(f"  {fs:11s} median {g.auc.median():.2f} [{ci[0]:.2f},{ci[1]:.2f}]  AP {g.ap.median():.3f} vs prevalence {g.prev.median():.3f}")
    print("pooled AUC:", {k: round(v, 3) for k, v in d["res"]["streams"][st].items() if k.startswith("pooled")})
