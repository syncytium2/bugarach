# Own re-implementation of PySpike sim_ann_cython schedule (identity start, adjacent swaps,
# T0=2max(D), Tend=1e-5 T0, alpha=.9, 100N tries / 10N successes per level) vs Borda + insertion.
import numpy as np, time
rng = np.random.default_rng(1)
def A_of(D,p): Dp=D[np.ix_(p,p)]; return np.triu(Dp,1).sum()
def anneal(D):
    N=len(D); p=np.arange(N); T=2*D.max(); Te=1e-5*T; it=0
    r=rng.random; ri=rng.integers
    while T>Te:
        k=s=0
        while k<100*N and s<10*N:
            i=ri(N-1); d=-2*D[p[i],p[i+1]]
            if d>0 or np.exp(d/T)>r():
                p[i],p[i+1]=p[i+1],p[i]; s+=1
            k+=1
        it+=k; T*=0.9
        if s==0: break
    return p,it
def borda(D): return np.argsort(-D.sum(1),kind='stable')
def insertion(D,p):
    p=list(p); N=len(p); improved=True
    while improved:
        improved=False
        for a in range(N):
            x=p.pop(a)
            # gain of placing x at position j: sum_{y before j} D[y,x]... compute best position
            rest=np.array(p); g=np.concatenate([[0],np.cumsum(D[rest,x]-D[x,rest])])  # A contribution if x at j: sum_{y<j}D[y,x]+sum_{y>=j}D[x,y]
            base=D[x,rest].sum(); val=base+g; j=int(np.argmax(val))
            if val[j]>val[a]+1e-12: improved=True
            else: j=a
            p.insert(j,x)
    return np.array(p)
for N,signal in [(30,0.3),(60,0.1),(100,0.05),(100,0.0)]:
    lat=rng.permutation(N)
    # pair coincidence counts ~ Poisson(40); P(i leads j)=0.5+signal*sign(lat_j-lat_i)
    D=np.zeros((N,N))
    for i in range(N):
        for j in range(i+1,N):
            n=rng.poisson(40); pl=0.5+signal*np.sign(lat[j]-lat[i]); k=rng.binomial(n,pl)
            D[i,j]=2*k-n; D[j,i]=-D[i,j]
    perm=rng.permutation(N); D=D[np.ix_(perm,perm)]
    t=time.time(); pa,it=anneal(D); ta=time.time()-t
    pb=borda(D); pi=insertion(D,pb); pai=insertion(D,pa)
    print(f"N={N} sig={signal}: A_anneal={A_of(D,pa):.0f} (iters {it}, {ta:.1f}s py)  A_borda={A_of(D,pb):.0f}  A_borda+ins={A_of(D,pi):.0f}  A_anneal+ins={A_of(D,pai):.0f}")
