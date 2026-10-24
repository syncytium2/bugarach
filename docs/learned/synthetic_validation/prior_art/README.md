# What in Aim 0 was already known? (2026-10-24)

After the Kreuz search ([`../kreuz_sort/`](../kreuz_sort/README.md)), Tony noted that Grün's group
had covered some of this ground. Four more agents searched:
- **Grün's group, literature:** its papers on window loss, sequences and synfire chains.
- **Grün's group, code:** the Elephant library.
- **Other order literature:** replay, cortical sequences, sequence discovery and rank statistics.
- **A cross-field survey:** one agent given only the day-one problem and none of our answers,
  covering radar, seismology, particle physics, EEG, ECG, BCI and others.

The reports are kept verbatim. They describe spike-train literature in its own terms, so they say "firing" where this repository would say "event" or "onset" for calcium data (GLOSSARY, *firing*).

| file | what |
|---|---|
| `grun_literature.md` | Grün et al. 1999, Grün, Abeles & Diesmann 2008, Louis & Grün 2009/2010, CuBIC, Ehm et al. 2007, Schrader 2008, ASSET, SPADE, 3d-SPADE, Schneider et al. 2006 |
| `elephant_code.md` | Elephant at commit 32f1b56: `cubic.py`, `asset/`, `spade.py`, unitary events, CAD, surrogates, plus issues and PRs |
| `order_reduction_check.py` | the Elephant agent's own check of whether CAD's and ASSET's ordering reduce to a net-lead ranking (they do not, as implemented); not Elephant code |
| `order_literature.md` | replay (Lee & Wilson to Takigawa 2024), Luczak, Ikegaya, Abeles and Gerstein, seqNMF, PP-Seq, CAD, calcium-imaging propagation, and rank statistics (Kendall's W, tournaments, Kemeny) |
| `cross_field_survey.md` | the naive survey: radar (detection against local background, separating interleaved transmitters, tracking), sonar, seismology, particle physics, EEG and MEG, ECG, BCI, sensor fusion, scan statistics and ecology's null models |

## Verdict for each Aim 0 result

The Kreuz group's verdict (no fast sort, no analytical null) is in [`../kreuz_sort/`](../kreuz_sort/README.md).

| Aim 0 result | verdict | closest prior work |
|---|---|---|
| Window sharing g_n for **two** onsets | **known** for uniform jitter | Grün et al. 1999, the fission probability: 1 − F is g_2 with one spike fixed and the other uniform |
| g_n for **n** onsets, Gaussian jitter (the range form), and k̂ = 2 + (k − 2) g_3/g_2 | **not found** | Louis et al. 2009/2010 claim an n-onset form for uniform discrete jitter (2010 not opened); CuBIC and Ehm et al. 2007 link cumulants to event size with no jitter |
| The at-most-one-event term (events held apart) | **not found** | every model found uses Poisson or Bernoulli event times |
| Reading size and jitter across window widths | **known as a goal**, with uniform jitter, by a slope-change rule | Grün, Abeles & Diesmann 2008; Louis & Grün 2009/2010. Spatial statistics fits Thomas processes by minimum contrast across scales |
| The joint fit as a formal fit that also recovers the event rate | **not found** | Ehm et al. 2007 fits a rate per event size, but at one bin width and with no jitter |
| The score sort (rank cells by net lead count) | **known** | Borda and Copeland ranking of a tournament, within a factor of 5 of the best order (Coppersmith, Fleischer & Rudra 2006). In neuroscience, Schneider, Havenith & Nikolić 2006 rank units by summed pairwise delays, and Tomlinson et al. 2019 by net upstream–downstream count. Rediscovered independently by the naive survey |
| One template: F = (2/π) arctan(δ/σ) | **known** | Greiner's relation (via Kendall and Kruskal); Thurstone's Case V model |
| M templates: the signal falls as 1/√M | **partly known** | follows from Kendall's W algebra; no paper states it for mixed sequence templates |
| No-order bias ∝ 1/√(events) | **partly known** | Kendall & Babington Smith 1939 (Kendall's W): E[W] = 1/m with no order, so a ranking's agreement with the rank-sum consensus is about 1/√m. With every cell in every event the constant is analytic (about 0.64) |
| The constant under partial participation (0.38 for the score sort, 0.50 after search), the √n̄ scaling over shared events, and detection power at 5–25 events | **not found** | field practice is shuffles (replay, calcium imaging). Silva et al. 2015 warn that picking the best template inflates rank correlation |
| Chance clusters at K | **known in form** | the accidental-coincidence rate of particle physics; radar's threshold set against local background. Ours is the assessor-specific version (1 s bins, the merge rule) |
| Membership excess 1 + (E − 1)/M | analogue known | Kish's design effect; ecology's fixed-margin null models for presence–absence matrices |

## What changes

- **Novelty.** What Aim 0 can still call new is narrower:
  - the n-onset Gaussian window sharing and the size correction built on it;
  - the at-most-one-event term;
  - a formal joint fit that includes the event rate;
  - the no-order constants under partial participation, and the power at few events.
- **The ranking sort is textbook.** Its 1/√ no-order scaling follows from Kendall's W.
- **A lead.** Kendall's W, extended to incomplete rankings (Skillings & Mack 1981), may give the
  partial-participation constant analytically. Not yet tried.
- **Who to ask.** The ranking question for Kreuz is now "why anneal, given that Borda is the
  textbook approximation". The window-sharing and fit questions are for Grün's group (Louis et al.
  2010 especially).
