# Coordinated events in sparse multi-sensor event trains: what other fields already know

*A cross-field survey for a calcium-imaging project. It assumes no existing solution and works from the published literature and standard textbook results.*

---

## 0. TL;DR

- **The underlying model.** Our problem is a *marked cluster point process*, a Neyman–Scott process. Its parts are:
  - an unseen "parent" event train for each source (rate, inter-event statistics);
  - for each parent, a random subset of sensors (participation, membership), each firing at parent time + template latency + Gaussian jitter;
  - all of it sitting on independent Poisson background.

  Nearly every field below has solved one slice of this. None, as far as we found, has packaged all of (a)–(f) for N≈33, E≈5–50 events and jitter≈bin width. **The closest single model in neuroscience is PPSeq** (Williams et al., 2020). It has sequence types, per-neuron latency templates and widths, participation amplitudes, background rates and Bayesian inference.
- **(a) Threshold against chance has a closed form.** Particle physics has used it since the 1930s: the accidental *k*-fold coincidence rate is R_k ≈ k·C(N,k)·λ^k·w^(k−1). Radar's **M-of-N binary integration plus CFAR** is the same calculation turned into a data-driven threshold. Gravitational-wave **time slides** are the right surrogate: shift each sensor's train circularly by an offset larger than any real lag.
- **(b) Unlabelled estimation.** Use the **pair-correlation (cross-correlogram) of a Neyman–Scott process**. The peak *area* gives event rate × participation², and the peak *width* gives √2 × jitter (Palm-likelihood / minimum-contrast estimation, from spatial statistics). Correct the truncation at threshold k the way seismology handles magnitude of completeness, or astroparticle physics handles detector efficiency.
- **(c) Source separation.** Radar ELINT **deinterleaving** is the best template:
  1. describe every detected event by a descriptor word;
  2. cluster the descriptors;
  3. check each cluster's timing with PRI/interval statistics (CDIF/SDIF-style difference histograms).

  The descriptor word is our analogue of the pulse descriptor word (PDW): participation vector, latency vector, spread.
- **(d) Fixed vs random membership** maps onto **ecological co-occurrence null models**. Use the event × sensor incidence matrix and fixed-margin swap randomization (the "curveball" algorithm). There is also a cheap closed-form screen: test the dispersion of per-sensor participation counts against Binomial(E, m̄/N).
- **(e) Order has a fully analytical chance level** in classical rank statistics:
  - **Kendall's W / Friedman**: E(n−1)W ~ χ²(n−1), and E[W] = 1/E under the null. With 5 events, W ≈ 0.2 arises by chance.
  - **Skillings–Mack (1981)** handles the case where each event has a different participant subset.
  - Mean pairwise Spearman between events equals (E·W − 1)/(E − 1).
  - Consensus order needs no search over all orderings: Borda/mean-rank, least-squares latency from pairwise lags (TDOA / seismology double-difference), or spectral ranking. Exact Kemeny aggregation is NP-hard, which is why brute force is slow.
- **(f) Validation.** Every mature field uses **injection–recovery** on simulated data plus **time-slide background**: radar ROC by Monte Carlo, gravitational-wave software injections, synthetic ETAS catalogs in seismology, SpikeForest-style ground truth in spike sorting.

---

## 1. Common notation (used throughout)

| Symbol | Meaning | Typical value |
|---|---|---|
| N | sensors (cells) | 33 (30–40) |
| λ | background rate per sensor | 0.01 s⁻¹ |
| Δ | sampling bin | 0.1 s |
| T | recording length | 1200–3600 s |
| w | coincidence window | ≈ jitter span, 0.1–1 s |
| σ | jitter (SD of member times about the event time + template) | 0.1–1 s |
| q, m | participation probability per member / participants per event | m ≈ 5–12 |
| E | number of true events per source | ~5–50 |
| ℓ_i | template latency of sensor i (order) | — |

**Generative model** (the "truth" for part f), for each source s:

- parents ~ renewal or Poisson process, rate ρ_s;
- for each parent, a member set M ⊆ {1..N}:
  - *fixed membership*: M is drawn from a fixed group G_s, each member included with prob q;
  - *random membership*: M is a random m-subset;
- each i ∈ M fires at t_parent + ℓ_{s,i} + ε, with ε ~ N(0, σ_s²), then quantized to Δ;
- the background is Poisson(λ_i) on every sensor.

The literature calls this a **Neyman–Scott / Thomas cluster process with marks**. In seismology it is a cluster (ETAS-like) process. In radar it is "interleaved pulse trains from several emitters with jitter plus noise pulses". In neuroscience it is "sequences/assemblies on background spiking".

---

## 2. Radar and electronic warfare (the PI's interest)

### 2.1 CFAR detection and the cell-under-test

- **What it is.** Constant False Alarm Rate (CFAR) detection compares a test statistic in the *cell under test* (CUT) with a threshold. The threshold is a multiple α of the noise level estimated from *training cells* around it. *Guard cells* separate the two so the target does not leak into the noise estimate.
- **α in closed form.** α is set for a chosen probability of false alarm (Pfa). For cell-averaging CFAR on exponential (square-law) noise, Pfa = (1 + α/Nₜ)^(−Nₜ).
- **Variants:**
  - CA-CFAR (Finn & Johnson, 1968, *RCA Review*);
  - OS-CFAR, which uses an order statistic of the training cells and is robust to interfering targets in them (Rohling, 1983, *IEEE TAES*);
  - GO/SO-CFAR for clutter edges;
  - analysis in non-homogeneous backgrounds (Gandhi & Kassam, 1988, *IEEE TAES*).
- **Textbooks.** Richards, *Fundamentals of Radar Signal Processing* (McGraw-Hill); Skolnik, *Radar Handbook*.
- **Binary (M-of-N) integration** (Dinneen & Reed, 1956, *IRE Trans. IT*; Schwartz, 1956). Each of N looks is thresholded to 0/1, and a detection is declared if ≥M are 1. Pfa = Σ_{j≥M} C(N,j) p^j (1−p)^(N−j). This is *exactly* our "≥k of N sensors in a window" rule. Radar picks M for a target Pfa and the matching probability of detection (Pd), using closed-form binomial tails.

**Analogues to (a)–(f):**

- **(a)** CUT = one time window. Training cells = the same window's statistic at other times (excluding guard bins around it) or the time-slide surrogates. Statistic = coincidence count, or a weighted count (see Chair–Varshney in §10.1). The threshold k comes from the binomial tail at the target false-event rate. *CFAR is the data-driven threshold the PI wants.* It adapts automatically when λ drifts (bleaching, state changes), because λ̂ is local.
- **(b)** Radar estimates target SNR and fluctuation statistics (the Swerling cases) from detections. Participation fluctuating from event to event is the analogue of Swerling fluctuation.
- **(f)** ROC curves by Monte Carlo injection are standard.
- **Cheap or brute force?** CFAR and M-of-N are O(T) and closed-form. Only OS-CFAR needs a sort.
- **Few events.** CFAR's job is to control *false* alarms with few or no targets. Sample size is the number of training cells, not the number of targets. This suits our regime well.

### 2.2 Pulse deinterleaving and emitter separation (ELINT/ESM)

- **The problem.** An ESM receiver sees one interleaved stream of pulses from many emitters. Each pulse gets a **pulse descriptor word (PDW)**: time of arrival (TOA), RF, pulse width (PW), angle of arrival (AOA), amplitude. The task has two stages:
  1. **pre-sort** by clustering PDWs on the stable parameters (RF, AOA, PW);
  2. **deinterleave in time** within each cluster with PRI (pulse repetition interval) analysis.
- **Methods:**
  - **TOA difference histograms.** CDIF (cumulative difference histogram) is due to Mardia (1989, *IEE Proc. F*, "New techniques for the deinterleaving of repetitive sequences"). SDIF (sequential difference histogram) is due to Milojević & Popović (1992, *IEE Proc. F*). Both histogram the differences between pulse TOAs of order 1, 2, 3 … A real PRI produces a peak above a threshold curve that falls with difference order. The threshold is *derived for Poisson-random TOAs*: an analytical chance level for a periodic interval.
  - **PRI transform** (Nishiguchi & Kobayashi, 2000, *IEEE TAES*, after Nelson, 1993). A complex-weighted difference histogram that suppresses subharmonics.
  - **Sequence search.** Once a PRI candidate is found, walk forward along TOA + PRI ± tolerance and extract the train.
  - **Surveys.** Wiley, *ELINT: The Interception and Analysis of Radar Signals* (Artech House, 2006). Recent machine-learning deinterleaving uses clustering on PDWs (DBSCAN, mixture models) and RNNs.
- **Jitter.** Jittered PRIs smear the peaks. The fix is wider or overlapping PRI bins, which trades resolution for robustness. This is the same tension as our jitter ≈ bin width.

**Analogues:**

- **(c)** *Event-level* deinterleaving:
  1. turn each detected coordinated event into a "PDW": time, participant set (binary N-vector), latency vector, spread, size;
  2. cluster the PDWs (Jaccard on sets, rank correlation on latencies);
  3. for each cluster, test the inter-event intervals for regular PRI structure versus Poisson using difference histograms or the coefficient of variation (CV).
- **Timing as a separation cue.** With only 5–50 events, PRI histograms are weak unless sources are very periodic. Use them as a confirmation cue, not the primary separator.
- **(d)** In ESM, an emitter's AOA is constant and its RF may hop. Fixed vs random membership is the same as asking whether the "AOA" (participant set) is a stable descriptor (fixed) or not (random). If membership is random, participation carries no separation information, and you must separate by latency template, jitter or timing alone.
- **Cheap or brute force?** Difference histograms are O(n·c) for c difference orders. Sequence search is greedy. Combinatorial "assign every pulse to every emitter" is avoided by clustering first, which is the same lesson for us.

### 2.3 Track-before-detect (TBD)

- **The idea.** Integrate weak returns along *hypothesised trajectories* across many scans before thresholding. A target too dim to cross threshold in any single scan can then be detected.
- **Methods:**
  - dynamic programming (Barniv, 1985, *IEEE TAES*);
  - Hough-transform TBD;
  - particle-filter TBD (Salmond & Birch, 2001, *Proc. ACC*; Rutten, Gordon & Maskell, 2005);
  - the general idea of **coherent vs non-coherent integration**.
- **Analogues:**
  - **(a)** Integrate across time bins *along the latency template* rather than in a fixed window. Score a window with a template-aligned statistic: count sensors whose spike falls within ±2σ of t + ℓ_i. This is a matched filter, like seismology template matching. A sequence that never puts more than 3 cells in any single 0.1 s bin can still score 8 along its template.
  - **(e)** TBD's "trajectory" is our latency template.
- **Cost.** Exhaustive TBD over all trajectories is brute force. DP or particle filters make it tractable. For us the "trajectory" space (all orderings) is large, so estimate the template from strong events first, then matched-filter (the seismology recipe; §4.3).

### 2.4 Multi-target tracking and data association

- **Methods:**
  - **GNN** (global nearest neighbour; Hungarian assignment);
  - **JPDA** (joint probabilistic data association; Fortmann, Bar-Shalom & Scheffe, 1983, *IEEE J. Oceanic Eng.*);
  - **MHT** (multiple hypothesis tracking; Reid, 1979, *IEEE TAC*);
  - **Random-finite-set filters** for an unknown number of targets: PHD (Mahler, 2003, *IEEE TAES*), GM-PHD (Vo & Ma, 2006, *IEEE TSP*);
  - textbook: Bar-Shalom, Willett & Tian, *Tracking and Data Fusion* (2011).
- **Analogues:**
  - **(c)** When events from two sources overlap in time, deciding which spikes belong to which event is a *data-association* problem. The clutter density is λ, the detection probability is q, and the "measurement model" is the latency template. JPDA-style soft assignment gives each spike a posterior over {background, event A, event B}. That is what PPSeq does with Gibbs sampling.
  - **(b)** Tracking's clutter density and Pd are estimated jointly with the tracks. PHD filters estimate the *expected number* of targets without enumerating them. A useful mental model is "how many events are in this recording?" without having to label each one.
- **Cost.** MHT is exponential and pruned. JPDA is exponential in cluster size. GNN is polynomial (Hungarian, O(n³)). PHD is closed-form for Gaussian mixtures.

### 2.5 Time-difference-of-arrival (TDOA)

- **Methods:**
  - GCC-PHAT for robust delay estimation (Knapp & Carter, 1976, *IEEE TASSP*);
  - closed-form hyperbolic localisation from TDOAs (Chan & Ho, 1994, *IEEE TSP*);
  - the Cramér–Rao bound: delay variance ∝ 1/(effective bandwidth² × SNR).
- **Analogues:**
  - **(e)** Pairwise lags between sensors, measured as cross-correlogram peaks, are TDOAs. The latency template is recovered in closed form by **least squares on pairwise lag differences**: solve L·ℓ = b, where L is the graph Laplacian of sensor pairs. No search over orderings is needed.
  - **(b)** The precision bound is the analogue of TDOA CRB: per-pair lag SD ≈ σ√2/√(number of shared events). This tells you directly when order is recoverable.

---

## 3. Sonar and passive acoustic arrays

**Methods:**

- **Transient detection with the Page test (CUSUM):** Page (1954, *Biometrika*); applied to sonar by Abraham & Willett (2002, *IEEE J. Oceanic Eng.*).
- **Bearing–time records and beamforming.** Delay-and-sum over hypothesised directions is the array version of template matching.
- **Click-train detection and classification for odontocetes:** PAMGuard (Gillespie et al., 2008, *Proc. Inst. Acoustics*).
  - Click trains from several animals are interleaved, much like radar pulses.
  - Separation uses inter-click interval (ICI) consistency and bearing (TDOA across hydrophones).
  - This is a direct biological cousin of PRI deinterleaving.
- **Localising vocalising animals with TDOA arrays**, using hyperbolic fixes and probabilistic grids.

**Analogues:**

| Goal | Sonar analogue |
|---|---|
| (a) | CUSUM/Page test on the summed coincidence count. It detects sustained excess faster than fixed windows when jitter is broad. The threshold comes from average run length (ARL) to false alarm, which has closed-form approximations. |
| (c) | Click-train separation by ICI plus bearing, i.e. timing plus a latency/direction descriptor. |
| (e) | Bearing comes from TDOA. Chance bearing consistency is assessed with circular statistics. |

**Small samples.** Passive acoustics often classifies from a few clicks. It relies on per-click features and the consistency of ICI rather than on many repeats.

---

## 4. Seismology

### 4.1 Network coincidence triggers

- **Method.** Run STA/LTA at each station (Allen, 1978, *BSSA*). Declare a network event when ≥k stations trigger within a window, often with per-station weights. ObsPy implements this as `coincidence_trigger` (Beyreuther et al., 2010, *SRL*).
- **How the threshold is set.** In practice k is usually chosen empirically. Weighting stations by reliability is common.
- **Mapping.** STA/LTA is itself a CFAR detector: a short-term average over a long-term background. It is the same structure as our (a).

### 4.2 Phase association across stations

**Methods:**

- **Classic grid association:** Johnson, Lindh & Hirshorn (1997, *Bull. Seism. Soc. Am.*, "Robust regional phase association").
- **REAL** (Zhang, Ellsworth & Beroza, 2019, *SRL*). Counts picks consistent with travel times from candidate grid sources (a grid-search "back-projection" of picks). An event is accepted if the number of consistent P and S picks exceeds thresholds.
- **PhaseLink** (Ross et al., 2019, *JGR*). A deep network that learns which picks belong together.
- **GaMMA** (Zhu et al., 2022, *JGR Solid Earth*). A Bayesian Gaussian mixture model. Each earthquake is a mixture component whose "mean" for each station is the predicted arrival time. Picks are soft-assigned. A background/noise component is included, and the number of events is inferred from data.
- **PyOcto** (Münchmeyer, 2024, *Seismica*). Fast space-partitioning association.

**Analogues:**

- **(c)** *GaMMA is structurally our problem.* An event is a mixture component, and each sensor's spike time has mean t_event + ℓ_i and variance σ². Picks from different events are separated by mixture EM. The difference: seismology *knows* ℓ_i from a velocity model and a source location, whereas we must learn ℓ_i per source. That is the "template matching" half (§4.3) or PPSeq.
- **(a)** REAL's "≥k consistent picks" is k-of-N coincidence *aligned to a hypothesised latency template*. The minimum pick count is set by hand or by false-association rates on synthetic data.

### 4.3 Template matching / matched filtering

**Methods:**

- correlation detection: Gibbons & Ringdal (2006, *GJI*);
- low-frequency earthquakes: Shelly, Beroza & Ide (2007, *Nature*);
- aftershock detection with "Match & Locate": Peng & Zhao (2009, *Nat. Geosci.*);
- **FAST**, unsupervised similarity search with locality-sensitive hashing: Yoon et al. (2015, *Sci. Adv.*).

**How the threshold is set.**

- The detection statistic is the network-averaged correlation coefficient.
- **Threshold = 8–9 × MAD of the daily correlation trace** (Shelly et al., 2007; Peng & Zhao, 2009).
- This is a robust CFAR on the empirical null. Because most windows are noise, the null comes from the data themselves.

**Small samples.** Templates are often single events. The template's own detection is the "seed", and new detections are stacked to refine it.

**Analogues:**

- **(a)** Once a few strong events give a latency template, *template-aligned scanning* detects weaker events with fewer participants. Threshold it by MAD-CFAR.
- **(c)** Template families: hierarchical clustering of events by waveform correlation, here latency/membership similarity.
- **(e)** The template *is* the order. Its significance is assessed by cross-validation: detect with a template built from other events.

**Cost.** Template correlation is O(T·N) per template, i.e. cheap. FAST shows how to find repeats *without* a template using hashing, avoiding all-pairs comparison.

### 4.4 Catalog declustering (separating background from clustered events)

**Methods:**

- window methods: Gardner & Knopoff (1974, *BSSA*);
- link-based methods: Reasenberg (1985, *JGR*);
- **ETAS**, a Hawkes process: Ogata (1988, *JASA*);
- **stochastic declustering**, giving each event's posterior probability of being background or triggered: Zhuang, Ogata & Vere-Jones (2002, *JASA*);
- **nearest-neighbour space–time–magnitude distance**, which gives a bimodal distribution separating clustered from background events: Zaliapin et al. (2008, *PRL*); Zaliapin & Ben-Zion (2013, *JGR*).

**Analogues:**

- **(c)** Two sources with different temporal statistics (Poisson vs bursty/self-exciting) can be separated by fitting a mixture of point processes and assigning each event a posterior. The Zaliapin nearest-neighbour bimodality is a cheap, closed-form diagnostic.
- **(b)** The **magnitude of completeness (Mc)** problem is the same as ours. The size distribution is observed only above the detection threshold, so the detection probability must be modelled to estimate the true rate (Ogata & Katsura, 1993, *GJI*).
  - Our "size" is the number of participants m.
  - Events with m < k are invisible, and the observed m-histogram is a truncated binomial or beta-binomial.

### 4.5 Arrival order and location

- **Arrival-order location.** Anderson (1981, *BSSA*, "Epicentral location using arrival time order"; we did not check the volume and pages) locates epicentres *from the order of arrivals alone*. Each pair of stations with known order constrains the source to one half-plane. Later "arrival-order misfit" methods drop the velocity model and need only monotone travel time with distance.
- **Double-difference relative location** with hypoDD (Waldhauser & Ellsworth, 2000, *BSSA*). Closed-form-ish least squares on pairwise time differences. It is the template for estimating relative latencies robustly from many noisy pairwise lags.

**Analogues:**

- **(e)** Arrival-order location is the fullest existing treatment of "order without accurate timing". With bin-quantized times (ties), pairwise precedence counts are the natural sufficient statistic.
- **(e)** Double-difference gives latency estimation by least squares, with no search over orderings.

---

## 5. Astroparticle and particle physics

### 5.1 Coincidence detection and accidental rates

- **Two-fold accidentals.** The rate is R_acc = 2τ·R₁·R₂ for resolving time τ (Eckart & Shonka, 1938, *Phys. Rev.*). Standard references: Knoll, *Radiation Detection and Measurement*; Leo, *Techniques for Nuclear and Particle Physics Experiments*.
- **k-fold among N identical channels.** The rate of chance coincidences of *distinct* channels within window w is **R_k ≈ k·C(N,k)·λ^k·w^(k−1)**, the standard multiplicity-trigger formula.
- **Multiplicity triggers in practice:**
  - **IceCube SMT-8:** ≥8 hit modules in about 5 µs (IceCube Collaboration, 2017, *JINST*);
  - **Pierre Auger surface-detector T3:** compact station configurations in coincidence (Abraham et al., 2010, *NIM A* 613);
  - **Fermi GBM:** ≥2 of 12 detectors above threshold (Meegan et al., 2009, *ApJ*);
  - **SNEWS** supernova coincidence across experiments (Antonioli et al., 2004, *New J. Phys.*).

  In all cases k and τ are chosen *analytically from accidental-rate formulas*, then verified with off-time data.
- **Off-time / time-slide background.** Gravitational-wave searches estimate the background by shifting one detector's data by offsets far larger than the light-travel time and recounting coincidences, over thousands of slides (e.g., Was et al., 2010, *CQG*; LIGO/Virgo search papers). Cosmic-ray and gamma-ray work uses "off-source" or "scrambled-time" background in the same way.
- **Significance with few counts:**
  - Li & Ma (1983, *ApJ*) for on/off counting;
  - Feldman & Cousins (1998, *PRD*) for intervals.
- **Look-elsewhere effect.** Scanning many windows inflates false positives (Gross & Vitells, 2010, *EPJ C*).
- **Scan statistics.** Sliding-window clusters have closed-form approximations: Naus (1982, *JASA*); Glaz, Naus & Wallenstein, *Scan Statistics* (Springer, 2001). Aldous's Poisson clumping heuristic (1989) is the general principle.

**Worked example for our regime** (N = 33, λ = 0.01 s⁻¹, w = 1 s, T = 1 h; independent Poisson background):

| k | R_k (per hour) ≈ k·C(33,k)·λ^k·w^(k−1)·3600 |
|---|---|
| 3 | ≈ 60 |
| 4 | ≈ 6 |
| 5 | ≈ 0.4 |
| 6 | ≈ 0.03 |

So **k ≈ 5 gives fewer than one false event per hour at w = 1 s.** With w = 0.3 s, k ≈ 4 suffices. The threshold scales as w^(k−1). This shows directly why jitter (which forces wide windows) raises the required k. It also shows that a template-aligned window (§4.3) lowers k.

The formula assumes stationary independent Poisson background. Calcium data violate it through slow drifts, burst-prone cells and neuropil correlations. For that reason the *operational* threshold should come from time slides or CFAR, with the formula as a sanity check.

### 5.2 Air-shower arrival-time ordering → direction

- **Method.** Fit a plane (or curved) shower front to station trigger times: t_i = t₀ + (**n**·**x**_i)/c. This is linear least squares, so it is closed-form. The fit χ² tests consistency. See Pierre Auger Collaboration (2015, *NIM A* 798) on surface-detector reconstruction.
- **Testing anisotropy across events.**
  - Rayleigh / first-harmonic analysis (Linsley, 1975, *PRL*). Chance probability P(≥r) = exp(−E·r²/4) for E events.
  - Li–Ma significance for excesses on the sky.

**Analogues:**

- **(e)** If the cells have spatial positions, fit a "propagation plane" to each event's latencies vs cell coordinates: latency = t₀ + **s**·**x**. That gives a propagation *direction* per event in closed form. Consistency of direction across events then has an **analytical chance level from the Rayleigh test**, valid for small E.
- **(e) generalised.** Without spatial structure, the same linear model with free per-cell latencies is the least-squares template of §2.5.

### 5.3 Other relevant particle-physics practice

- **Unfolding** (D'Agostini, 1995, *NIM A*) corrects observed distributions for detector efficiency and resolution. Applied to our (b): recover the true participation distribution from the observed, threshold-truncated one.
- **Blind analysis and injected signals** (signal injection, "mock data challenges") are directly relevant to (f).

---

## 6. EEG and MEG

**Spike and HFO propagation order.**

- Interictal spikes and high-frequency oscillations (HFOs) propagate across contacts. Analyses compute onset latencies per channel and rank-order or lead–lag maps.
  - Example: Tomlinson et al. (2016, *Ann. Neurol.*) on interictal spike propagation sequences.
  - The literature on spike-onset vs propagated sites is large; we did not verify exact references.
- **Significance** is usually tested with channel-label permutation, or across-spike consistency (consensus leader frequency vs a binomial null).

**Microstates and source separation.**

- **EEG microstates:** Lehmann et al. (1987); review by Michel & Koenig (2018, *NeuroImage*). Modified k-means on topographies; the number of clusters is chosen by cross-validation or meta-criteria.
- **ICA:** Bell & Sejnowski (1995, *Neural Comput.*); Makeig et al. (1996, *NIPS*).
- **HMM states in MEG:** e.g., Vidaurre et al. (2017, *PNAS*) and (2018, *Nat. Commun.*).

**Cross-channel latency.**

- Lagged coherence, Granger/transfer entropy.
- **Cross-correlation lag with surrogate (phase-randomized or time-shifted) nulls.**

**Analogues:**

- **(c)** Microstate clustering of *event topographies* (participation vectors) is the same as our event-PDW clustering. It is a simple k-means with an empirical choice of k.
- **(e)** Interictal propagation studies face exactly our few-events problem (tens of spikes). They mostly use permutation tests. The analytical rank-statistic answers in §12 are underused there.

**Small samples.** Shrinkage covariance (Ledoit & Wolf, 2004, *J. Multivar. Anal.*) is the norm.

---

## 7. Multi-lead ECG and cardiac mapping

- **QRS detection** (Pan & Tompkins, 1985, *IEEE TBME*). Adaptive thresholds track running estimates of signal and noise peaks. This is effectively a CFAR.
- **Beat clustering / ectopy separation.** Holter algorithms cluster beats by morphology (templates). PVCs (premature ventricular contractions) and sinus beats are *two sources with different activation orders and timing*. A PVC has an early coupling interval and a different QRS axis. Example: Lagerholm et al. (2000, *IEEE TBME*), Hermite functions with self-organizing maps (SOM).
- **Activation mapping.**
  - Local activation times (LATs) per electrode give isochronal maps.
  - Conduction velocity comes from fitting a plane or polynomial to LAT vs position: Bayly et al. (1998, *IEEE TBME*); review by Cantwell et al. (2015, *Comput. Biol. Med.*).
  - The plane fit is the same closed-form least squares as the air-shower front.
- **Few beats.** Ensemble averaging aligned on a fiducial point. Mapping systems annotate one beat per site and assume beat-to-beat stationarity.

**Analogues:**

| Goal | Cardiac analogue |
|---|---|
| (c) | Sinus vs ectopic beats, separated by activation-order template plus coupling interval. Exactly "two sources with distinct latency templates and timing". |
| (e) | Activation order via plane or Laplacian fits. Chance level is rarely formalised, because cardiac activation order is physically strong (large latency spread relative to jitter). |

**Lesson.** Order is easy when template spread ≫ jitter. Ours is the harder regime (spread ≈ jitter ≈ bin).

---

## 8. Brain–computer interfaces

**Methods:**

- **Event-related detection across channels:** P300 spatial filtering with xDAWN (Rivet et al., 2009, *IEEE TBME*).
- **Small-sample classification:** shrinkage LDA (Blankertz et al., 2011, *NeuroImage*); Riemannian geometry (Barachant et al., 2012, *IEEE TBME*).
- **Chance levels with few trials:** "Exceeding chance level by chance" (Combrisson & Jerbi, 2015, *J. Neurosci. Methods*). With n trials, the 95% chance accuracy follows the binomial inverse CDF and can be far above 50% for small n.

**Analogues:**

- **(e)** Any order/classification score from few events must be judged against the *small-n binomial or permutation null*, not the asymptotic one. BCI has made this a standard reporting requirement.
- **(b)** Regularise template estimation (shrinkage toward a uniform latency prior) when E is small.

---

## 9. Neural spike trains and multi-electrode arrays (home field)

### 9.1 Synchrony and assembly detection with explicit chance models

- **Unitary Events** (Grün, Diesmann & Aertsen, 2002, *Neural Comput.*). Expected coincidence counts under independence come from firing rates (analytical: Poisson/binomial). Significance comes from the "joint-surprise". Surrogate methods are compared in Louis, Gerstein, Grün & Diesmann (2010, *Front. Comput. Neurosci.*) and Grün (2009, *J. Neurophysiol.*), covering spike dithering and trial shuffling.
- **SPADE** (Torre et al., 2013, *Front. Comput. Neurosci.*; Quaglio et al., 2017, *Front. Comput. Neurosci.*; Stella et al., 2019). Frequent-itemset mining of spatio-temporal patterns, with surrogate-based significance on pattern spectra (size × count).
- **Cell Assembly Detection, CAD** (Russo & Durstewitz, 2017, *eLife*). Agglomerative assembly detection with arbitrary lags and statistical testing.
- **PCA/ICA assemblies** (Peyrache et al., 2010, *J. Comput. Neurosci.*; Lopes-dos-Santos, Ribeiro & Tort, 2013, *J. Neurosci. Methods*). The number of assemblies is set *analytically* by the **Marchenko–Pastur** upper eigenvalue bound (1 + √(N/T_bins))² of the binned correlation matrix. This is a closed-form chance threshold.

### 9.2 Calcium-imaging ensembles

- **Coactivity-threshold method** (Miller, Ayzenshtat, Carrillo-Reid & Yuste, 2014, *PNAS*). Frames whose number of coactive cells exceeds a shuffle-derived threshold (circular-shift each cell) are "high-activity frames". These are clustered into ensembles by SVD and similarity.
- **SVD-based ensemble detection** (Carrillo-Reid et al., 2015 and later). Evaluated with ground truth in Mölter, Avitan & Goodhill (2018, *BMC Biol.*); we recall this but did not verify it.

**Mapping.** This is the most direct published version of our (a) and (c). Its weaknesses for our case:

- a fixed single-frame window (bad when jitter ≈ bin);
- a shuffle threshold set per dataset, rather than CFAR-local;
- no latency templates.

### 9.3 Sequence detection

| Method | Reference | Notes |
|---|---|---|
| **seqNMF** | Mackevicius et al., 2019, *eLife* | Convolutive NMF with a cross-orthogonality penalty; significance from held-out data vs shuffles. |
| **PPSeq** | Williams, Degleris, Wang & Linderman, 2020, *NeurIPS* | Neyman–Scott point-process model. Latent sequence events with type, time and amplitude; each neuron has per-type offset (latency), width (jitter) and weight (participation); a background rate; collapsed Gibbs sampling gives posterior assignment of every spike. *This is almost exactly our generative model.* What it lacks for us: explicit fixed-vs-random membership tests, and an analytical order chance level. |
| **Rank-order / replay methods** | Lee & Wilson, 2002, *Neuron*; Foster & Wilson, 2006, *Nature*; Diba & Buzsáki, 2007, *Nat. Neurosci.* | Spearman correlation between event order and template, with cell-ID shuffle nulls. |
| **SPOTDisClust** | Grossberger, Battaglia & Vinck, 2018, *PLoS Comput. Biol.* | Clusters events by optimal-transport distances between multi-neuron spike patterns. Directly applicable to event-PDW clustering with latencies. |
| **Similarity-based assembly-sequence clustering** | Watanabe et al., 2019, *Front. Neuroinform.* | — |

**Caution from Mokeichev et al. (2007, *Neuron*).** Apparently repeating motifs can arise by chance in surrogate data. The surrogate choice matters, and this is the canonical warning for (e).

### 9.4 MEA burst and network-burst detection

- Methods: Chiappalone et al. (2005, *J. Neurosci. Methods*); Wagenaar et al. (2006, *BMC Neurosci.*); Pasquale et al. (2010, *J. Comput. Neurosci.*, ISI-histogram-based thresholds).
- Review of single-channel burst detectors: Cotterill et al. (2016, *J. Neurophysiol.*). Its main finding: methods disagree widely, and thresholds adapted to the data (ISI-histogram valleys, rank surprise) beat fixed ones.
- **Network bursts** are defined as ≥k channels bursting within a window. This is again M-of-N.

### 9.5 Spike-sorting validation

- SpikeForest (Magland et al., 2020, *eLife*) is the model for (f): ground-truth hybrid datasets and standard accuracy metrics.

---

## 10. Other fields

### 10.1 Multi-sensor fusion and IoT (distributed detection)

- **Methods:**
  - Tenney & Sandell (1981, *IEEE TAES*);
  - **Chair–Varshney optimal fusion rule** (Chair & Varshney, 1986, *IEEE TAES*);
  - textbook: Varshney, *Distributed Detection and Data Fusion* (Springer, 1997).
- **The Chair–Varshney rule.** Combine binary local decisions u_i ∈ {0,1} with weights:
  - log((1 − P_M,i)/P_F,i) for u_i = 1;
  - log(P_M,i/(1 − P_F,i)) for u_i = 0.
- **Transfer to (a).** Instead of counting k, *weight* each participating sensor by how surprising its spike is:
  - P_F,i = λ_i·w (its background firing probability in the window);
  - P_D,i = its participation probability.

  A cell that rarely fires on its own contributes more evidence than a chatty one. With heterogeneous λ_i, this is strictly better than the raw count. Under the null, its tail is a Poisson-binomial with a closed form (Le Cam / saddle-point / FFT recursion).

### 10.2 Network intrusion and packet-burst detection

- **Burst and change detection:**
  - Kleinberg burst detection (Kleinberg, 2002, *KDD*; a two-state HMM on inter-arrival times);
  - CUSUM;
  - PCA subspace anomaly detection with the closed-form Q-statistic threshold of Jackson & Mudholkar (1979): Lakhina, Crovella & Diot (2004, *SIGCOMM*).
- **Coordinated/lockstep behaviour of groups:**
  - **CopyCatch** (Beutel et al., 2013, *WWW*): groups of users liking the same pages within the same time window;
  - **SynchroTrap** (Cao et al., 2014, *CCS*);
  - **BotMiner** (Gu et al., 2008, *USENIX Security*): clusters hosts by co-activity.
- **Analogues:**
  - **(d)** Lockstep detection is literally "fixed groups that act together repeatedly" vs "random coincidences". CopyCatch searches for (group, time-window) bicliques.
  - **(a)** Kleinberg's HMM gives a principled, cheap burst segmentation of the summed activity trace.

### 10.3 Spatial scan statistics and epidemic cluster detection

- **Kulldorff spatial scan statistic** (Kulldorff, 1997, *Commun. Stat. Theory Methods*). Significance via Monte Carlo replicates of the maximum statistic, which handles multiple testing over windows.
- **Space–time permutation scan** (Kulldorff et al., 2005, *PLoS Med.*). Needs no population-at-risk. The null permutes times relative to locations, which is the same idea as time-slides.
- **Fast subset scan** (Neill, 2012, *JRSS B* 74:337–360). Many score functions satisfy **linear-time subset scanning (LTSS)**: sort the elements by a priority (e.g., the per-sensor likelihood ratio) and the optimal subset is one of the top-j for some j. *Exact search over 2^N subsets is replaced by an O(N log N) sort.*
- **Knox test** for space–time interaction (Knox, 1964), with a Poisson approximation to its null; Mantel (1967).

**Analogues:**

- **(a)** For each candidate time window, finding *which subset of sensors* participates (and the score) is a subset scan. LTSS makes it exact and cheap: sort sensors by spike-in-window likelihood ratio, then evaluate N nested subsets.
- **(a)** Kulldorff's Monte Carlo of the *maximum* statistic is the right way to set a threshold that accounts for scanning many windows (look-elsewhere).

### 10.4 Ecology: species co-occurrence null models (added; directly answers (d))

- **The setting.** An incidence matrix (sites × species) is tested for non-random co-occurrence against null models that preserve margins.
- **Statistics and nulls:**
  - C-score (Stone & Roberts, 1990);
  - variance ratio (Schluter, 1984, *Ecology*);
  - fixed–fixed swap randomization (Gotelli, 2000, *Ecology*);
  - the fast exact **curveball algorithm** (Strona et al., 2014, *Nat. Commun.*).
- **Transfer to (d).** Rows = detected events, columns = sensors.
  - *Random membership* predicts that, given event sizes and per-sensor participation rates, the matrix looks like a fixed-margin random draw.
  - *Fixed membership* predicts block structure: high C-score, a large top eigenvalue of the co-participation matrix beyond Marchenko–Pastur, and a bimodal distribution of per-sensor participation.
- **Cheap closed-form screen.** Under random m-subsets, each sensor's participation count ~ Binomial(E, m̄/N) (approximately; better, hypergeometric given sizes). The dispersion index χ² = Σ_i (c_i − E·m̄/N)² / (E·m̄/N·(1 − m̄/N)) tests heterogeneity. A fixed group makes it explode (members ≈ qE, non-members ≈ λwE).

### 10.5 Social-network cascade timing

**Methods:**

- **NetInf** (Gomez-Rodriguez, Leskovec & Krause, 2010, *KDD*). Network inference from cascade timing; submodular greedy.
- **NetRate** (Gomez-Rodriguez, Balduzzi & Schölkopf, 2011, *ICML*). Convex in transmission rates.
- **Hawkes processes:** Hawkes (1971, *Biometrika*); Linderman & Adams (2014, *ICML*), Bayesian network discovery.
- **Source identification, "rumor centrality":** Shah & Zaman (2011, *IEEE TIT*).

**Analogues:**

- **(e)** Cascades are events with a leader→follower order. NetRate turns many cascades into a *convex* estimate of pairwise "who-follows-whom" rates. That is a closed-form-ish alternative to searching orderings.
- **(c)** Mixtures of Hawkes processes separate sources by their triggering structure.
- **(e)** Rumor-centrality theory gives exact probabilities of identifying the source on trees. That is the closest thing to an analytical "leader detection" chance level.

### 10.6 Rank aggregation and permutation statistics (the math under (e))

- **Computational cost of exact aggregation.**
  - **Kemeny optimal aggregation is NP-hard** (Bartholdi, Tovey & Trick, 1989; Dwork, Kumar, Naor & Sivakumar, 2001, *WWW*). This is why searching all orderings is slow.
  - **Footrule aggregation** is solvable by bipartite matching in polynomial time and is a 2-approximation to Kemeny (Dwork et al., 2001).
  - **Borda / mean-rank** is O(E·n). It is the MLE for the Thurstone/Plackett–Luce family under mild conditions.
- **Spectral and synchronisation methods.**
  - **SerialRank** (Fogel, d'Aspremont & Vojnovic, 2014, *NeurIPS*): spectral ranking from pairwise comparisons.
  - **SyncRank** (Cucuringu, 2016, *IEEE TNSE*): angular synchronisation from pairwise offsets.
- **Probabilistic ranking models.**
  - **Mallows model:** Mallows (1957, *Biometrika*). The MLE consensus is the Kemeny ranking; the spread parameter measures order consistency.
  - **Plackett–Luce** (Luce, 1959; Plackett, 1975). Gives a likelihood for top-k or partial orders, which is useful when only participants are ranked.

---

## 11. Cross-field synthesis per goal

| Goal | Best closed-form tool | Best surrogate/empirical tool | Brute force to avoid |
|---|---|---|---|
| (a) detect + threshold | Accidental-coincidence / binomial M-of-N tail, R_k ≈ k·C(N,k)λ^k w^(k−1); scan-statistic correction; Chair–Varshney weighted count (Poisson-binomial tail) | **CFAR** (local λ̂ with guard bins); **time slides** (circular per-sensor shifts); MAD threshold on template-correlation trace; Kulldorff max-statistic Monte Carlo | Exhaustive subset search → **LTSS** sort |
| (b) participation, jitter, rate | Neyman–Scott pair-correlation: CCG excess area ≈ ρ·q_i q_j·T, width SD ≈ σ√2; zero/k-truncated binomial MLE for m; Sheppard's correction σ² ≈ s² − Δ²/12; efficiency-corrected rate ρ̂ = E_det / (T·P(Bin(N,q) ≥ k)) | Injection–recovery calibration (GW, seismology Mc studies) | Full MCMC over all spikes (PPSeq) only if needed |
| (c) separate sources | GaMMA-style Gaussian mixture on event descriptors; PRI/CV interval statistics per cluster | Microstate-style k-means with cross-validated K; stochastic declustering posteriors | Joint assignment of all spikes to all events (MHT) → use JPDA/Gibbs soft assignment |
| (d) fixed vs random membership | Per-sensor participation dispersion χ² vs Binomial; Marchenko–Pastur top eigenvalue of co-participation | Curveball fixed-margin swaps (C-score) | — |
| (e) order + chance | **Kendall W / Friedman χ²**, **Skillings–Mack** for partial participation, pairwise sign tests, Rayleigh for directions | Within-event latency permutation (exact null) | All n! orderings → Borda / least-squares latency / spectral |
| (f) validation | Analytical ROC from binomial tails | Monte Carlo injection into real background (hybrid data), time-slide false-alarm curves | — |

### 11.1 When (b) parameters are and are not recoverable (cross-field consensus)

- **Participation q.**
  - Recoverable from the m-histogram only when N·q is comfortably above k; that is, much of the distribution must be above threshold, as with the seismology Mc rule.
  - If N·q ≈ k, the truncated fit is degenerate. Rate and q trade off, just as completeness and the b-value trade off.
  - The pairwise CCG area (q_i q_j ρ) is *not* truncated by the event threshold. Use it to break the degeneracy.
- **Jitter σ.**
  - Within-event spread after removing template latency and applying Sheppard's correction Δ²/12.
  - Only identifiable if σ is not ≪ Δ (then everything is one bin; only an upper bound Δ/√12 is available) and the window w ≥ ~3σ.
  - Jitter and latency template are confounded if the template is not learned: spread from a consistent order looks like jitter. Fit both.
- **Event rate ρ.** Detected count divided by detection efficiency. It cannot be estimated below one or two events per recording except as an upper limit (Feldman–Cousins style).
- **Inter-event timing** (renewal shape, periodicity). Needs ≳20–30 events per source. With a handful, report the CV with bootstrap intervals only.
- **Two sources.** Separable only if they differ in at least one descriptor (membership set, latency template, jitter, timing) by more than its within-source scatter. The Fisher discriminant ratio of the descriptor is the predictor. Under random membership with the same jitter and no order, sources are *not* identifiable except by timing.

---

## 12. Analytical answers for (e): order with few events and its chance level

Several fields give **closed-form** null distributions. All of them assume that, under H₀, the order of participants within each event is a uniformly random permutation (exchangeable latencies). That holds exactly for within-event label permutation.

1. **Kendall's coefficient of concordance W** (Kendall & Babington Smith, 1939, *Ann. Math. Stat.*; equivalent to the Friedman, 1937, *JASA*, test).
   - Setup: E events (the "raters") each rank the same n sensors.
   - Null: E[W] = 1/E, and E·(n−1)·W ~ χ²(n−1) approximately (exact tables for small E, n).
   - **Implication:** with 5 events, a W of about 0.2 is what chance gives. Naively interpreting W as "20% consistent order" is wrong. With 10 events, chance W ≈ 0.1.
   - Tie correction is available, which matters at 0.1 s bins with jitter ≈ Δ.
2. **Mean pairwise Spearman between events.**
   - ρ̄ = (E·W − 1)/(E − 1), so its null mean is 0.
   - For complete rankings, Var(ρ_pair) = 1/(n−1).
3. **Template known in advance** (e.g., learned on other events, i.e. cross-validated).
   - Per-event Spearman has null mean 0 and variance 1/(m−1) for m participants.
   - The average over E events has variance ≈ (1/E)·mean(1/(m_e−1)).
   - Exact small-sample distributions of Kendall's τ come from Mahonian numbers (Kendall, 1938, *Biometrika*).
   - This is the cleanest way to avoid the "template fit on the same data" bias.
4. **Partial participation** (different sensor subsets per event).
   - **Skillings–Mack (1981, *Technometrics* 23:171–177)**: a Friedman-type statistic for arbitrary missing-data patterns. It is χ² approximate, and Monte Carlo is recommended for small or tied designs.
   - **Durbin (1951)**: for balanced incomplete designs.
   - Implemented in the R package `Skillings.Mack`.
5. **Pairwise precedence (sign tests).**
   - For sensors i, j co-participating in n_ij events, the count of "i before j" ~ Binomial(n_ij, ½) under H₀.
   - Tied events (same bin) are dropped or split.
   - The aggregate statistic Σ (2·wins − n)² / n is approximately χ², with dependence corrected by permutation.
   - This is the arrival-order logic of seismology (Anderson, 1981) and is robust to quantization.
6. **Page's L test** (Page, 1963, *JASA*). Tests a *pre-specified* order (e.g., a spatial gradient hypothesis). It has an exact/normal null and more power than Friedman when the hypothesis is directional.
7. **Rayleigh test on propagation directions** (astroparticle anisotropy; circular statistics, Mardia & Jupp). If cell positions are known, fit a plane wave per event and test direction consistency: P ≈ exp(−E·R̄²) for mean resultant length R̄ (Rayleigh's Z = E·R̄²). Valid for small E with standard corrections.
8. **Power and detectability.**
   - For a pair with template latency difference d and jitter σ, P(i leads j) = Φ(d/(σ√2)).
   - With n_ij shared events, the sign test detects this when n_ij·(P − ½)² ≳ ~2.
   - **Example:** d = σ gives P ≈ 0.76, needing roughly 10–15 shared events per pair for 80% power at α = 0.05. d = 0.3σ gives P ≈ 0.58, needing ~100+.
   - This gives the "when can and can't it be recovered" boundary in closed form.

**Avoiding brute-force search.** Any of the following, then test with items 1–5:

- consensus order by mean (or median) within-event rank (Borda);
- least-squares latencies from pairwise median lags (Laplacian solve, as in TDOA/hypoDD);
- spectral SerialRank.

If the order is fit on the same events, use the *in-sample* null of W (item 1), which already accounts for the fit. Do not compare in-sample template correlations against the per-event null of item 3.

**Fields with an analytical answer:**

- nonparametric statistics (Kendall/Friedman/Page/Skillings–Mack/Durbin);
- astroparticle physics (Rayleigh / harmonic analysis for arrival directions);
- seismology for order-based location constraints (geometric, not probabilistic);
- network source detection (rumor-centrality probabilities, on trees only).

Neuroscience replay and EEG propagation mostly use shuffles, even though the analytical forms above apply.

---

## 13. Ranked list of the most transferable ideas

1. **Accidental-coincidence formula + CFAR/time-slide threshold** (particle physics + radar + gravitational waves).
   - *Why it fits:* our background is low-rate Poisson-like and N is moderate, which is the exact regime of multiplicity triggers. CFAR makes k adapt to drifting rates. Time slides (circular per-cell shifts of more than about 10 s) preserve each cell's own statistics while destroying cross-cell alignment.
   - *What it replaces:* a fixed hand-picked k, or a single global shuffle threshold.
2. **Generative cluster-point-process model (PPSeq / GaMMA style) as the core estimator.**
   - *Why it fits:* the problem statement *is* a marked Neyman–Scott process. It estimates participation, jitter, latency template, background and source identity jointly, with soft assignment of every spike.
   - *What it replaces:* threshold-then-cluster pipelines that bias every downstream estimate, e.g. participation inflated by threshold truncation.
3. **Closed-form rank-concordance statistics for order (Kendall W / Friedman, Skillings–Mack, pairwise sign tests), with Borda or least-squares consensus.**
   - *Why it fits:* gives exact small-E chance levels and handles partial participation and ties. Polynomial time.
   - *What it replaces:* searching all orderings and ad-hoc shuffles.
4. **ELINT-style deinterleaving: event descriptor words → cluster → per-cluster interval analysis.**
   - *Why it fits:* the same staged separation problem (several emitters, few pulses each, jittered timing). It is fast, interpretable and gives clear failure modes.
   - *What it replaces:* single-shot clustering of high-activity frames that ignores latency and timing.
5. **Template-aligned matched filtering with a MAD-CFAR threshold** (seismology, plus TBD).
   - *Why it fits:* once strong events define a template, weaker events with fewer participants become detectable. Integrating along the latency template beats a fixed window when jitter ≈ bin.
   - *What it replaces:* a fixed-window coincidence count, which needs a larger k because w must cover the whole latency spread.
6. **Fixed-margin null models for membership** (ecology curveball, plus dispersion χ² and Marchenko–Pastur).
   - *Why it fits:* it directly answers fixed vs random membership with exact conditional nulls.
   - *What it replaces:* eyeballing participation heat-maps.
7. **Detection-efficiency (completeness) correction for rates and participation** (seismology Mc, astroparticle aperture/unfolding).
   - *Why it fits:* events below k are invisible, and correcting for this is mandatory for unbiased (b).
   - *What it replaces:* reporting raw detected counts and mean detected size.
8. **Weighted fusion (Chair–Varshney) and LTSS subset scanning.**
   - *Why it fits:* heterogeneous background rates across cells mean not all coincident cells are equal evidence. LTSS finds the best participant subset per window exactly and cheaply.
   - *What it replaces:* unweighted counting.

**Validation (f)** should borrow from gravitational-wave and seismology practice:

- hybrid injection (simulated events added into *real* background trains);
- injection–recovery curves as functions of participation, jitter, latency spread and E;
- false-alarm-rate curves from time slides;
- explicit "not recoverable" zones derived from the closed-form bounds in §11.1 and §12.8.

---

## 14. Radar parallels, spelled out

| Radar / EW concept | Mapping onto our problem |
|---|---|
| Range–Doppler cell | A time window (bin + jitter allowance) on the shared clock |
| Cell under test (CUT) | The candidate event window at time t |
| Training cells | The same statistic in windows away from t (or in time-slide surrogates), giving local λ̂ and the null distribution |
| Guard cells | Bins immediately around t (≥ jitter span) excluded from training so that the event does not inflate its own background |
| CFAR multiplier α / Pfa | Threshold k (or weighted score) set from the binomial / Poisson-binomial tail for a target false-event rate per hour |
| OS-CFAR (robust to interferers) | Median/quantile-based background estimate, robust to other events in the training window |
| M-of-N binary integration | "≥ k of N sensors fire within w": the identical formula |
| Swerling fluctuation models | Event-to-event variation in participation (how many sensors join) |
| Non-coherent vs coherent integration | Plain window count vs template-aligned count (latency-compensated) |
| Track-before-detect | Accumulating evidence along the latency template (and across repeated events) before declaring a weak event |
| Pulse | One coordinated event |
| Pulse descriptor word (TOA, RF, PW, AOA, amplitude) | Event descriptor: time, participant set, latency vector/order, spread (jitter), size |
| Emitter | Source of coordinated events |
| PRI (and jitter / stagger) | Inter-event interval statistics of each source |
| CDIF/SDIF histograms, PRI transform | Difference histograms of event times within a cluster to test periodicity vs Poisson; threshold derived for random TOAs |
| Pre-sort on RF/AOA | Clustering events by participation and latency template |
| AOA stable per emitter | Fixed membership (stable participant set) |
| Frequency-agile emitter | Random membership: the "spatial" descriptor is useless, so separate by template/timing |
| Data association (GNN/JPDA/MHT) | Assigning individual spikes to events (or background) when events overlap |
| Clutter density | Background rate λ·N per unit time |
| Probability of detection Pd | Participation probability q per member |
| PHD filter (expected target count) | Estimating the number of events without enumerating them |
| TDOA / GCC-PHAT | Pairwise lag between cells from the CCG peak, giving the latency template by least squares |
| Cramér–Rao bound on TDOA | Precision of latency/order: ≈ σ√2/√(shared events); sets the order-recoverability limit |
| Radar ROC by Monte Carlo | Injection–recovery validation on simulated data |

**What does *not* transfer from radar.** Radar has huge numbers of pulses per emitter and physically stable PRIs. Our 5–50 events per source make PRI analysis a weak cue. Radar also has rich continuous descriptors (RF, PW), while ours are mostly binary participation plus noisy, quantized latencies. So use the radar *architecture* (CFAR → descriptors → cluster → interval check) but expect separation to rest on membership and latency more than on timing.

---

## 15. Key references (grouped)

Most citations are standard and well known. A few could not be fully verified during this survey and are marked †. Check their volume and page details before formal citation.

**Radar / EW / tracking:**
- Finn & Johnson 1968 *RCA Rev.*
- Rohling 1983 *IEEE TAES*
- Gandhi & Kassam 1988 *IEEE TAES*
- Dinneen & Reed 1956 *IRE Trans. IT*
- Richards, *Fundamentals of Radar Signal Processing*
- Mardia 1989 *IEE Proc. F*†
- Milojević & Popović 1992 *IEE Proc. F*†
- Nishiguchi & Kobayashi 2000 *IEEE TAES*
- Wiley 2006 *ELINT* (Artech)
- Barniv 1985 *IEEE TAES*
- Salmond & Birch 2001
- Reid 1979 *IEEE TAC*
- Fortmann, Bar-Shalom & Scheffe 1983 *IEEE JOE*
- Mahler 2003 *IEEE TAES*
- Vo & Ma 2006 *IEEE TSP*
- Knapp & Carter 1976 *IEEE TASSP*
- Chan & Ho 1994 *IEEE TSP*

**Sonar:**
- Page 1954 *Biometrika*
- Abraham & Willett 2002 *IEEE JOE*
- Gillespie et al. 2008 (PAMGuard)

**Seismology:**
- Allen 1978 *BSSA*
- Beyreuther et al. 2010 *SRL*
- Johnson et al. 1997 *BSSA*
- Zhang, Ellsworth & Beroza 2019 *SRL* (REAL)
- Ross et al. 2019 *JGR* (PhaseLink)
- Zhu et al. 2022 *JGR Solid Earth* (GaMMA)
- Münchmeyer 2024 *Seismica* (PyOcto)
- Gibbons & Ringdal 2006 *GJI*
- Shelly, Beroza & Ide 2007 *Nature*
- Peng & Zhao 2009 *Nat. Geosci.*
- Yoon et al. 2015 *Sci. Adv.* (FAST)
- Gardner & Knopoff 1974 *BSSA*
- Reasenberg 1985 *JGR*
- Ogata 1988 *JASA*
- Zhuang, Ogata & Vere-Jones 2002 *JASA*
- Zaliapin et al. 2008 *PRL*
- Ogata & Katsura 1993 *GJI*
- Anderson 1981 *BSSA*†
- Waldhauser & Ellsworth 2000 *BSSA*

**Astroparticle / particle physics:**
- Eckart & Shonka 1938 *Phys. Rev.*
- Knoll, *Radiation Detection and Measurement*
- IceCube Collaboration 2017 *JINST*
- Abraham et al. (Auger) 2010 *NIM A*
- Pierre Auger Collaboration 2015 *NIM A*
- Meegan et al. 2009 *ApJ*
- Antonioli et al. 2004 *NJP*
- Was et al. 2010 *CQG*
- Li & Ma 1983 *ApJ*
- Feldman & Cousins 1998 *PRD*
- Gross & Vitells 2010 *EPJ C*
- Linsley 1975 *PRL*
- D'Agostini 1995 *NIM A*
- Naus 1982 *JASA*
- Glaz, Naus & Wallenstein 2001 (Springer)

**EEG/MEG, ECG, BCI:**
- Lehmann et al. 1987
- Michel & Koenig 2018 *NeuroImage*
- Bell & Sejnowski 1995 *Neural Comput.*
- Vidaurre et al. 2017/2018
- Tomlinson et al. 2016 *Ann. Neurol.*†
- Pan & Tompkins 1985 *IEEE TBME*
- Lagerholm et al. 2000 *IEEE TBME*
- Bayly et al. 1998 *IEEE TBME*
- Cantwell et al. 2015 *Comput. Biol. Med.*
- Rivet et al. 2009 *IEEE TBME*
- Blankertz et al. 2011 *NeuroImage*
- Barachant et al. 2012 *IEEE TBME*
- Combrisson & Jerbi 2015 *J. Neurosci. Methods*
- Ledoit & Wolf 2004 *J. Multivar. Anal.*

**Neural spike / imaging:**
- Grün, Diesmann & Aertsen 2002 *Neural Comput.*
- Grün 2009 *J. Neurophysiol.*
- Louis et al. 2010 *Front. Comput. Neurosci.*
- Torre et al. 2013
- Quaglio et al. 2017
- Russo & Durstewitz 2017 *eLife*
- Peyrache et al. 2010 *J. Comput. Neurosci.*
- Lopes-dos-Santos et al. 2013 *J. Neurosci. Methods*
- Miller et al. 2014 *PNAS*
- Mölter et al. 2018 *BMC Biol.*†
- Mackevicius et al. 2019 *eLife*
- Williams et al. 2020 *NeurIPS* (PPSeq)
- Lee & Wilson 2002 *Neuron*
- Foster & Wilson 2006 *Nature*
- Diba & Buzsáki 2007 *Nat. Neurosci.*
- Grossberger et al. 2018 *PLoS CB*
- Watanabe et al. 2019 *Front. Neuroinform.*
- Mokeichev et al. 2007 *Neuron*
- Chiappalone et al. 2005
- Wagenaar et al. 2006
- Pasquale et al. 2010
- Cotterill et al. 2016 *J. Neurophysiol.*
- Magland et al. 2020 *eLife*

**Fusion, intrusion, scan statistics, ecology, cascades, ranking:**
- Tenney & Sandell 1981 *IEEE TAES*
- Chair & Varshney 1986 *IEEE TAES*
- Varshney 1997 (Springer)
- Kleinberg 2002 *KDD*
- Lakhina et al. 2004 *SIGCOMM*
- Jackson & Mudholkar 1979 *Technometrics*
- Beutel et al. 2013 *WWW*
- Cao et al. 2014 *CCS*
- Gu et al. 2008 *USENIX Sec.*
- Kulldorff 1997 *Commun. Stat.*
- Kulldorff et al. 2005 *PLoS Med.*
- Neill 2012 *JRSS B* 74:337–360
- Knox 1964
- Mantel 1967 *Cancer Res.*
- Schluter 1984 *Ecology*
- Stone & Roberts 1990 *Oecologia*
- Gotelli 2000 *Ecology*
- Strona et al. 2014 *Nat. Commun.*
- Gomez-Rodriguez et al. 2010 *KDD* (NetInf)
- Gomez-Rodriguez et al. 2011 *ICML* (NetRate)
- Hawkes 1971 *Biometrika*
- Linderman & Adams 2014 *ICML*
- Shah & Zaman 2011 *IEEE TIT*
- Kendall 1938 *Biometrika*
- Kendall & Babington Smith 1939 *Ann. Math. Stat.*
- Friedman 1937 *JASA*
- Durbin 1951 *Br. J. Psychol. Stat. Sect.*
- Page 1963 *JASA*
- Skillings & Mack 1981 *Technometrics* 23:171–177
- Mallows 1957 *Biometrika*
- Plackett 1975 *Appl. Stat.*
- Dwork et al. 2001 *WWW*
- Bartholdi, Tovey & Trick 1989
- Fogel et al. 2014 *NeurIPS*
- Cucuringu 2016 *IEEE TNSE*
- Diggle, *Statistical Analysis of Spatial Point Patterns*
- Tanaka, Ogata & Stoyan 2008 *Biometrical J.* (Palm likelihood for Neyman–Scott)
