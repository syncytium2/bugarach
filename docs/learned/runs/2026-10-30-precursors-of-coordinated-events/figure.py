import sys, pickle, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
out = sys.argv[1]; dst = sys.argv[2]
d = pickle.load(open(f"{out}/precursor.pkl", "rb"))
U = pd.read_csv(f"{out}/univariate_within_auc.csv", dtype={"sid": str})
GROUPS = ["DI", "OVX", "MALE", "ORX"]; GC = dict(zip(GROUPS, ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]))
def tlab(x):
    x = int(x); s = "-" if x < 0 else ""; x = abs(x)
    return s + (f"{x // 60}m" + (f"{x % 60}s" if x % 60 else "") if x >= 60 else f"{x}s")

fig, ax = plt.subplots(2, 4, figsize=(17, 7.5), gridspec_kw=dict(width_ratios=[2.2, 1, 1.6, 1]))
for i, st in enumerate(["fast", "slow"]):
    # Figure a: peri-event population rate
    C = d["peri"][st]; t = np.arange(-120, 30) + 0.5
    E = np.array([c["E"] for c in C]); Cc = np.array([c["C"] for c in C])
    a = ax[i, 0]
    t5 = np.arange(-120, 30, 5) + 2.5
    rs = np.random.RandomState(2)
    for M, col, lab in [(Cc, "0.55", "random times (no event in prior 60 s)"), (E, "k", f"around an event ({sum(c['nev'] for c in C)} events)")]:
        M5 = M.reshape(len(M), -1, 5).mean(2)
        boots = np.array([M5[rs.randint(0, len(M5), len(M5))].mean(0) for _ in range(2000)])
        a.step(t5, M5.mean(0), where="mid", color=col, lw=1.5, label=lab)
        a.fill_between(t5, *np.percentile(boots, [2.5, 97.5], 0), step="mid", color=col, alpha=.2, lw=0)
    a.axvspan(-5, 0, color="#f3d9a4", alpha=.6, lw=0, label="unreadable: detector absorbs onsets here")
    a.set_ylim(0, 3); a.set_xlim(-120, 30)
    a.set_xticks(np.arange(-120, 31, 30)); a.set_xticklabels([tlab(x) for x in np.arange(-120, 31, 30)])
    a.set_ylabel(f"{st} · {len(C)} recordings\nonset rate / recording mean")
    if i == 0: a.legend(fontsize=7.5, loc="upper left", frameon=False); a.set_title("Figure 1a. Population onset rate around an isolated event\n(mean of recordings, 5 s bins, 95% CI resampling recordings)", fontsize=9, loc="left")
    if i == 1: a.set_xlabel("time from event onset")
    # Figure b: inter-event interval CV vs dead-time Poisson
    I = d["icis"][st]; ici = [np.array(x) for x in I.ici]; dmin = min(x.min() for x in ici)
    cvd = np.array([(x.mean() - dmin) / x.mean() for x in ici])
    b = ax[i, 1]
    for g in GROUPS:
        m = (I.group == g).values
        b.scatter(cvd[m], I.cv.values[m], s=12 + 2 * I.ncalls.values[m], color=GC[g], label=f"{g} ({m.sum()})", alpha=.8)
    b.plot([0, 2], [0, 2], "k:", lw=.8); b.set_xlim(.5, 1.1); b.set_ylim(0, 2)
    b.set_ylabel(f"{st} · {len(I)} recordings ≥4 events\nCV of inter-event interval")
    if i == 1: b.set_xlabel(f"CV expected, Poisson + {dmin:.0f} s dead time")
    if i == 0: b.set_title("Figure 1b. Event timing vs memoryless", fontsize=9, loc="left"); b.legend(fontsize=7, frameon=False)
    # Figure c: within-recording AUC per feature
    c = ax[i, 2]
    feats = [("log_since", "time since\nlast event"), ("r30", "all onsets\n5–30 s before"), ("b30", "background\n5–30 s before"),
             ("b60", "background\n30–60 s before"), ("mx2", "densest 2 s\nin last 10 s")]
    Us = U[U.stream == st]
    for j, (f, lab) in enumerate(feats):
        g = Us[Us.feat == f]
        for k, (col, off, mk) in enumerate([("auc", -.17, "o"), ("auc_iso", .17, "s")]):
            v = g[col].dropna()
            c.scatter(np.full(len(v), j + off) + np.random.RandomState(j).uniform(-.06, .06, len(v)), v, s=9,
                      color=[GC[x] for x in g.loc[v.index, "group"]], marker=mk, alpha=.6)
            c.plot([j + off - .12, j + off + .12], [v.median()] * 2, "k", lw=2)
    c.axhline(.5, color="k", ls=":", lw=.8); c.set_ylim(0, 1); c.set_xticks(range(len(feats)))
    c.set_xticklabels([l for _, l in feats], fontsize=7)
    c.set_ylabel(f"{st} · {Us.sid.nunique()} recordings ≥3 events\nAUC, event 5–15 s ahead")
    if i == 0: c.set_title("Figure 1c. One feature at a time, within each recording\n(circles: all moments; squares: no event in last 60 s; bar = median)", fontsize=9, loc="left")
    # Figure d: participants' share before vs after
    P = d["partic"][st].dropna(subset=["f_ev", "f_post"])
    e = ax[i, 3]
    e.scatter(P.f_post, P.f_ev, s=10, color=[GC[x] for x in P.group], alpha=.7)
    e.plot([0, 1], [0, 1], "k:", lw=.8); e.set_xlim(0, 1); e.set_ylim(0, 1)
    e.set_ylabel(f"{st} · {len(P)} events\nshare of onsets from participants,\n30 s BEFORE")
    if i == 1: e.set_xlabel("same share, 30 s AFTER")
    if i == 0: e.set_title("Figure 1d. Do the joiners start early?", fontsize=9, loc="left")
fig.tight_layout()
fig.savefig(dst, dpi=130)
print(dst)
