# The no-order mean of the order indicator under the score sort

This note derives the mean of the order indicator F when no order is planted, for the score
(Borda) sort, as used in `order_limit.py`. The result is **exact** for every N, k and E, so it
holds at small E too. It is a one-dimensional lattice convolution that costs milliseconds. Its
large-E limit has a closed form,

$$
\mathbb{E}[F_\text{score}] \;\simeq\; \frac{c(N,k)}{\sqrt{\bar n}}, \qquad
c(N,k) = \sqrt{\frac{4(k+1)}{3\pi N}}, \qquad \bar n = \frac{E\,k(k-1)}{N(N-1)} .
$$

Nothing in this derivation is fitted. For the local search I give only bounds and a fit.

## 1. Set-up and assumptions

* There are E events, independent of each other.
* **A1 (membership).** Each event recruits a uniformly random k-subset of the N cells,
  independently of everything else.
* **A2 (null).** Within an event, the onsets are exchangeable and continuous, so there are no
  ties. The event's ranking of its k cells is therefore a uniform random permutation, independent
  of membership and of other events. `order_limit.simulate` with spread 0 satisfies this, because
  its onsets are i.i.d. Gaussian.
* Notation. In event e, let $r_{ie}\in\{1,\dots,k\}$ be the time rank of participant i, with 1
  the earliest. Let $u_{ie} = k+1-2r_{ie}$ be the number of cells that i leads in e minus the
  number that lead i.
* $D_{ij} = \sum_{e \ni i,j} \operatorname{sign}(t_{je}-t_{ie})$, which is positive when i
  leads. $n_{ij}$ is the number of events containing both i and j.
* Score: $s_i = \sum_j D_{ij} = \sum_{e\ni i} u_{ie}$. This is a Borda count. Up to sign and a
  factor 2, it is the centred rank sum $R_i - r_i(k+1)/2$ of Friedman, Durbin and Skillings–Mack,
  where $r_i$ is the number of events that contain i.
* The score sort puts i before j when $s_i > s_j$. Ties in s are broken by `argsort`, which
  depends on s alone.

## 2. Reduction to one pair

For a fixed order, $F\cdot\sum_{i<j} n_{ij} = \sum_{i<j} D_{ij}\,\operatorname{sign}(s_i-s_j)$,
where ties count 0 (see below). The denominator is **not random**: every event adds
$\binom{k}{2}$ co-participations, so $\sum_{i<j} n_{ij} = E\binom{k}{2}$. By exchangeability of
the cells (A1, A2),

$$
\mathbb{E}[F_\text{score}] = \frac{\binom N2\,\mathbb{E}[D_{12}\operatorname{sign}(s_1-s_2)]}{E\binom k2}
= \frac{\mathbb{E}[D_{12}\operatorname{sign}(s_1-s_2)]}{\bar n}.
$$

**Ties.** Suppose $s_1=s_2$. Swapping the labels of cells 1 and 2 preserves the null law. It
leaves the vector s unchanged, so it leaves the sort unchanged, but it maps $D_{12}\to -D_{12}$.
Tied pairs therefore contribute 0 in expectation, which is the convention $\operatorname{sign}(0)=0$.

## 3. The exact formula

Write $s_1-s_2=\sum_e Y_e$. Event e contributes:

| event e contains | prob. per event | $Y_e$ | law of $Y_e$ |
|---|---|---|---|
| both 1 and 2 | $p_2 = \frac{k(k-1)}{N(N-1)}$ | $u_{1e}-u_{2e} = 2(r_{2e}-r_{1e})$ | $\pm 2d$, with $P(\lvert r_2-r_1\rvert=d) = w_d = \frac{2(k-d)}{k(k-1)}$, $d=1..k-1$ |
| exactly one of them | $2p_1$, $p_1 = \frac{k(N-k)}{N(N-1)}$ | $\pm u$ | $u = k+1-2r$, r uniform on 1..k |
| neither | $1-p_2-2p_1$ | 0 | |

The $Y_e$ are i.i.d. and symmetric about 0. $D_{12} = \sum_{e\ni 1,2} x_e$ with
$x_e = \operatorname{sign}(Y_e)$ on shared events: within a shared event, the pair's sign and the
pair's contribution to the score difference are **the same random variable**. This is the
correlation between $D_{ij}$ and $s_i-s_j$ that the brief warned about.

By linearity over the events and symmetry over them,
$\mathbb{E}[D_{12}\operatorname{sign}(s_1-s_2)] = E\,p_2\;\mathbb{E}[x\,\operatorname{sign}(y+S)]$.
Here y is the shared-event contribution, $x=\operatorname{sign}(y)$, and $S=\sum$ of the other
$E-1$ events' $Y$. S is independent of y and symmetric. For $y=2d>0$,
$\mathbb{E}\operatorname{sign}(2d+S) = P(S>-2d)-P(S<-2d) = P(-2d<S\le 2d)$, and the same holds
for $y<0$ by symmetry. Since $E p_2=\bar n$,

$$
\boxed{\;\mathbb{E}[F_\text{score}] = \sum_{d=1}^{k-1} w_d\Big[P(|S|<2d) + \tfrac12 P(|S|=2d)\Big],\qquad
S = \sum_{e=1}^{E-1} Y_e \text{ i.i.d. as in the table.}\;}
$$

This is exact under A1–A2, with no approximation. S lives on the integers in
$[-2(k-1)(E-1),\,2(k-1)(E-1)]$, and its pmf is the $(E-1)$-fold convolution of one event's pmf.
`F_exact` in `kendall_w.py` computes it by FFT. Read as a sentence: **F's null mean is the
probability that the rest of the record fails to outvote a typical shared event's rank gap**,
with half credit for a tie.

## 4. Gaussian form and the large-E constant

One event's variance is

$$
\sigma_1^2 = \mathrm{Var}\,Y_e = p_2\cdot\frac{2k(k+1)}{3} + 2p_1\cdot\frac{k^2-1}{3} = p_2\cdot\frac{2N(k+1)}{3}.
$$

This uses $\mathrm{Var}\,u = (k^2-1)/3$, $\mathrm{Cov}(u_1,u_2) = -(k+1)/3$ within an event, and
$\mathrm{Var}(u_1-u_2) = 2k(k+1)/3$. With $S\approx\mathcal N(0,(E-1)\sigma_1^2)$ (central limit
theorem; the half-weight on $|S|=2d$ is the midpoint rule, so no continuity correction is needed),

$$
\mathbb{E}[F_\text{score}] \approx \sum_{d=1}^{k-1} w_d\left[2\Phi\!\left(\frac{2d}{\sqrt{(E-1)\sigma_1^2}}\right)-1\right].
$$

Linearising $2\Phi(x)-1\approx\sqrt{2/\pi}\,x$ and using
$\sum_d w_d\,2d = \mathbb{E}|y| = 2(k+1)/3$ gives

$$
\mathbb{E}[F_\text{score}] \approx \sqrt{\frac2\pi}\,\frac{2(k+1)/3}{\sqrt{(\bar n-p_2)\,2N(k+1)/3}}
= \sqrt{\frac{4(k+1)}{3\pi N(\bar n-p_2)}}\;\longrightarrow\;\frac{c(N,k)}{\sqrt{\bar n}},\quad
c(N,k)=\sqrt{\frac{4(k+1)}{3\pi N}} .
$$

The same constant follows from the joint-Gaussian shortcut. Take $X=D_{12}$ and $Y=s_1-s_2$.
Then $\mathrm{Var}X=\bar n$, $\mathrm{Cov}(X,Y)=\bar n\cdot 2(k+1)/3$ (shared events only), and
$\mathrm{Var}Y\approx\bar n\cdot 2N(k+1)/3$. For jointly Gaussian X and Y,
$\mathbb{E}[X\operatorname{sign}Y]=\sqrt{2/\pi}\,\mathrm{Cov}(X,Y)/\mathrm{SD}(Y)$. That is
linear in the covariance, not an arcsine. The arcsine belongs to
$\mathbb{E}[\operatorname{sign}X\operatorname{sign}Y]$, which F does not use, because F weights
each pair by its full $D_{ij}$. Equivalently,
$c = \sqrt{2/\pi}\,\sqrt{\bar n}\,\mathrm{Corr}(D_{12},s_1-s_2) = \sqrt{2/\pi}\sqrt{2(k+1)/(3N)}$.

Corollaries.
* c depends on k and N only through $(k+1)/N$. In simple form,
  $\mathbb{E}[F]\approx\sqrt{4(k+1)(N-1)/(3\pi E k(k-1))}$.
* The run-length correction is $\bar n\to\bar n-p_2$, which is negligible. The real small-E
  effect is the saturation of $2\Phi-1$ together with lattice effects, and the exact formula
  handles both.

## 5. Special cases and the classical results

**k = N (complete rankings, Kendall's W).** Here $p_1=0$, $\bar n = E = m$, and
$c = \sqrt{4(N+1)/(3\pi N)}$. That is 0.683 at N = 10, 0.661 at N = 33, and $\sqrt{4/3\pi}=0.651$
as $N\to\infty$, which explains the review's 0.64–0.68. In this case there is an exact identity:
$F_\text{score}$ is the **mean Kendall τ between each event's ranking and the Borda (rank-sum)
consensus**, while the mean *Spearman* ρ between each event's ranking and the rank-sum vector
equals $\sqrt{W}$ exactly. The proof:
$\sum_e\sum_i (r_{ie}-\bar r)(R_i-m\bar r) = \sum_i (R_i-m\bar r)^2$, then divide by
$m\sqrt{S_0\sum_i(R_i-m\bar r)^2}$ with $S_0=(k^3-k)/12$. So F is the Kendall analogue of
$\sqrt W$, and $\mathbb{E}[W]=1/m$ (Kendall & Babington Smith 1939) gives the same $1/\sqrt m$ law.
The heuristic $(2/\pi)\arcsin(1/\sqrt m)\sqrt m$ tends to $2/\pi=0.637$, which is close to
$\sqrt{4/3\pi}=0.651$ but not equal. It also has the wrong N-dependence and the wrong small-m
behaviour (section D1 of the output).

**k = 2 (independent pairwise contests).** Here $c=\sqrt{4/(\pi N)}$. This is the Borda (or
Copeland, row-sum) ranking of a random weighted tournament.

**Durbin / Skillings–Mack.** The score vector's null covariance follows from the per-event
values $\mathrm{Var}\,u=(k^2-1)/3$ and $\mathrm{Cov}=-(k+1)/3$:

$$
\mathrm{Cov}(s) = \frac{k+1}{3}\big(k\,\mathrm{diag}(r_i) - C\big),\qquad C_{ij}=n_{ij},\;C_{ii}=r_i .
$$

This is (up to the factor $4$ from $u = -2(R-\bar R)$) the covariance of the centred rank sums
used by Durbin's (1951) test for balanced incomplete blocks. Skillings & Mack (1981) generalised
it to arbitrary incomplete designs. In a BIBD, Durbin's statistic is
$T = \frac{12(N-1)}{rN(k^2-1)}\sum_i (R_i - r(k+1)/2)^2 = \frac{3(N-1)}{rN(k^2-1)}\sum_i s_i^2$.
The quantity $\sigma_1^2$ above is
$\mathrm{Var}(s_1-s_2)$ per event, $\frac{k+1}{3}\,[k(r_1+r_2)-2n_{12}]/E$ in expectation over
the random design. So **the result reduces to Durbin's covariance structure (random-design
version, as in Skillings–Mack), and to Kendall's W when k = N**. F is not Durbin's statistic
itself. Durbin's T is a quadratic form in s, while F is the average signed agreement between
each pair's raw contests and the order s induces. Both, though, are built on the same
rank-sum vector and the same covariance.

## 6. What the simulation shows

The full tables are in `kendall_w_output.txt`, using fresh simulations with
`order_limit.simulate` and `order_limit.indicators`.

**Six fields, 400 events, 200 recordings each (score sort).** The fitted c values are the
earlier fits from 20 recordings each.

| N | k | $\bar n$ | c predicted | c fitted earlier | c simulated ± SE | E[F] exact | F simulated ± SE | z |
|---|---|---|---|---|---|---|---|---|
| 15 | 5 | 38.1 | 0.412 | 0.408 | 0.405 ± 0.006 | 0.0667 | 0.0656 ± 0.0010 | −1.0 |
| 33 | 5 | 7.58 | 0.278 | 0.259 | 0.276 ± 0.003 | 0.1006 | 0.1003 ± 0.0010 | −0.4 |
| 33 | 10 | 34.1 | 0.376 | 0.374 | 0.371 ± 0.004 | 0.0644 | 0.0635 ± 0.0006 | −1.4 |
| 33 | 20 | 143.9 | 0.520 | 0.507 | 0.517 ± 0.005 | 0.0433 | 0.0431 ± 0.0004 | −0.5 |
| 100 | 10 | 3.64 | 0.216 | 0.216 | 0.214 ± 0.001 | 0.1129 | 0.1124 ± 0.0007 | −0.7 |
| 100 | 30 | 35.2 | 0.363 | 0.373 | 0.360 ± 0.002 | 0.0611 | 0.0607 ± 0.0004 | −1.1 |

The two largest gaps from the earlier fit, (33, 5) and (100, 30), are noise in that fit. The
fresh simulation agrees with the formula.

**Small runs, 33 cells, 1000 recordings each.**

| k | E | $\bar n$ | E[F] exact | Gaussian form | $c/\sqrt{\bar n}$ | F simulated ± SE (SD) | z |
|---|---|---|---|---|---|---|---|
| 7 | 10 | 0.40 | 0.478 | 0.468 | 0.509 | 0.474 ± 0.002 (0.067) | −1.6 |
| 7 | 25 | 0.99 | 0.314 | 0.311 | 0.322 | 0.315 ± 0.001 (0.044) | 0.6 |
| 7 | 60 | 2.39 | 0.206 | 0.205 | 0.208 | 0.204 ± 0.001 (0.031) | −1.2 |
| 7 | 140 | 5.57 | 0.135 | 0.135 | 0.136 | 0.136 ± 0.001 (0.020) | 0.8 |
| 13 | 10 | 1.48 | 0.343 | 0.341 | 0.349 | 0.343 ± 0.001 (0.044) | −0.5 |
| 13 | 25 | 3.69 | 0.219 | 0.219 | 0.221 | 0.221 ± 0.001 (0.029) | 1.8 |
| 13 | 60 | 8.86 | 0.142 | 0.142 | 0.143 | 0.143 ± 0.001 (0.019) | 1.3 |
| 13 | 140 | 20.7 | 0.0932 | 0.0931 | 0.0933 | 0.0927 ± 0.0004 (0.012) | −1.3 |

The output file also covers three more checks. An E sweep at (33, 10) from E = 5 to 800 is
within 1.4 SE everywhere. The k = N case at N = 10 and 33, with m = 2 to 100, is within 0.9 SE.
The k = 2 case is within 2.2 SE.

Where each form holds:
* The **exact formula** matches every case within simulation error: 33 comparisons, all
  |z| ≤ 2.2, about what chance gives.
* The **Gaussian form** is within 0.003 of exact for $\bar n\gtrsim 1$. At $\bar n=0.4$ it is
  0.01 low, about 5 SE.
* The **$c/\sqrt{\bar n}$ law** is within 0.002 for $\bar n\gtrsim 2$. It runs high where F
  saturates: +0.03 at $\bar n = 0.4$ and +0.008 at $\bar n = 1$. So the observation that c is
  flat in E is correct down to $\bar n\approx 2$. Below that, $c_\text{eff}$ falls: 0.355 at
  $\bar n=0.43$ against 0.376.
* In the k = N case, $\sqrt W$ equals the mean Spearman-to-consensus to every printed digit,
  which confirms the identity in section 5.

## 7. The local search (stretch)

The search maximises $\sum_{\text{ordered pairs}} D_{ij}$, a linear ordering problem
(feedback-arc-set) instance on a random weighted tournament. I did not derive its constant.
What I have:

* **Lower bound.** $c_\text{search}\ge c_\text{score} = \sqrt{4(k+1)/(3\pi N)}$, because the
  search starts at the score order and only accepts improvements. Borda / row-sum ordering is
  also a constant-factor approximation to the weighted feedback-arc-set optimum (Coppersmith,
  Fleischer & Rudra 2010).
* **Upper bound (crude).** For a fixed order,
  $\mathrm{Var}(F) = \frac{2(2k+5)}{9Ek(k-1)}$, because each event adds a Kendall S statistic
  with variance $k(k-1)(2k+5)/18$. A Gaussian union bound over the $N!$ orders gives
  $c_\text{any order}\le\sqrt{4(2k+5)\ln N!/(9N(N-1))}$. It is loose, 1.7 to 2.6 times the
  simulated search constant.
* **Fit.** $c_\text{search}^2 - c_\text{score}^2$ hardly depends on k at fixed N, and it falls
  roughly as a power of N. So I fit $c_\text{search}^2 \approx 4(k+1)/(3\pi N) + aN^{b}$.
  Over 11 fields (N = 15 to 200, k = 5 to 60, 400 events, 100–200 recordings each), the fit
  gives $a = 0.544$ and $b = -0.488$. That is about $c_\text{search}^2 \approx 4(k+1)/(3\pi N) + 0.54/\sqrt N$,
  with a largest error of 0.010, against SEs of 0.001 to 0.007. The search to score ratio runs
  from 1.15 to 1.54, highest at small k/N. The union bound lies 1.7 to 2.6 times above the
  simulated search constant.
  This fit is empirical and not derived. Read it as follows: the score sort captures the part of
  D that is explained by the cells' Borda scores, and the search then harvests a k-independent
  residual tournament. For a random tournament the optimal excess is $\Theta(N^{3/2})$ (Spencer
  1971; Fernandez de la Vega 1983), which would make that residual term scale as $1/N$. The
  fitted exponent differs from that, which suggests the insertion search sits well below the
  optimum at these N, or that finite-N effects dominate.

## 8. Assumptions and limits, restated

1. Uniformly random k-subsets with fixed k. A variable k needs only a per-event mixture in the
   table of section 3, and the formula stays exact.
2. Continuous i.i.d. onsets within an event, so no ties. Tied onsets, such as frame-rounded
   ones, change the laws of $Y_e$ and $x_e$ (sign 0). The same convolution still works with
   the tied rank laws, but this note does not do it.
3. Events independent. Perfect readout: no background and no cross-event pairing.
4. Only the **mean** is derived. The SD, needed for a threshold, is not, so use the simulated
   SDs. Ties in s are handled exactly (section 2).

## References

* Durbin, J. (1951). Incomplete blocks in ranking experiments. *British Journal of Psychology,
  Statistical Section* 4, 85–90.
* Skillings, J. H. & Mack, G. A. (1981). On the use of a Friedman-type statistic in balanced and
  unbalanced block designs. *Technometrics* 23(2), 171–177.
* Kendall, M. G. & Babington Smith, B. (1939). The problem of m rankings. *Annals of
  Mathematical Statistics* 10(3), 275–287.
* Friedman, M. (1937). The use of ranks to avoid the assumption of normality implicit in the
  analysis of variance. *JASA* 32, 675–701.
* Kendall, M. G. (1938). A new measure of rank correlation. *Biometrika* 30, 81–93.
* Coppersmith, D., Fleischer, L. K. & Rudra, A. (2010). Ordering by weighted number of wins
  gives a good ranking for weighted tournaments. *ACM Transactions on Algorithms* 6(3), 55.
* Spencer, J. (1971). Optimal ranking of tournaments. *Networks* 1, 135–138.
* Fernandez de la Vega, W. (1983). On the maximum cardinality of a consistent set of arcs in a
  random tournament. *Journal of Combinatorial Theory B* 35, 328–332.
