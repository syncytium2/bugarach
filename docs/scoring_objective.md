# The tuning objective and its negatives: the rationale, and who solved it first

**Use this page when** you want to know what a settings search maximises, why, and which
established methods it is taken from.

> Working material, not murderboarded. Written 2026-11-13. Tony, the same day, on the proposal
> to tune for recall under a false-call cap: *"you may build it along with a documented
> rationale. assure me we are not reinventing things other groups and fields have already
> resolved"*.

**The short answer: nothing here is new, and every part has a name in another field.** Three
of this project's detectors turned out to be constant-false-alarm-rate detectors from radar,
found months after they were written ([`detector_history.md`](detector_history.md)). This page
exists so the scoring is not a second case. It claims no novelty anywhere.

## The rule

Among candidate settings of one detector, a search proposes the setting that finds the largest
share of planted events, among those whose false calls per hour on rate-matched negatives are at
or under a stated cap. A setting over the cap is not a candidate. If none is under it, nothing
is proposed. Code: [`src/bugarach/objective.py`](../src/bugarach/objective.py), with negatives
from [`src/bugarach/negatives.py`](../src/bugarach/negatives.py) and recall from the existing
one-to-one scorer, `bugarach.score`.

## Why not mean F1

On the bench sets of 2026-11-12 most tuned detectors scored 0.97 to 1.00. The sets had no
negatives, so precision was near 1 for any setting, F1 followed recall alone, and settings
tied. F1 also folds two costs into one number at an exchange rate nobody chose. A cap states
the exchange rate.

## Each part, and its name elsewhere

How each source was checked is in the last column: **search** means found by web search on
2026-11-13 with its abstract or a search summary read and the paper not opened; **record** means
read by an earlier session and cited in the decision record named; **survey** means listed in
this repository's cross-field survey, whose references were not all verified
([`learned/synthetic_validation/prior_art/cross_field_survey.md`](learned/synthetic_validation/prior_art/cross_field_survey.md));
**memory** means standard material stated from the session's memory and not looked up.

| Part of the rule | What other fields call it | Source | Checked |
|---|---|---|---|
| Maximise detections subject to a bound on false alarms | The Neyman-Pearson criterion of detection theory. Radar's constant-false-alarm-rate detectors are built on it | Detection-theory lecture notes; survey section 2.1 | search; survey |
| Score events found against false calls per unit of recording, when the number of places a false call could occur is not countable | The free-response operating characteristic of lesion detection: fraction of lesions localized against false marks per image, introduced in 1978 | Chakraborty and co-authors' papers on free-response analysis | search |
| The same pair of numbers for a detector running over time | Seizure detection reports event-based sensitivity with false detections per hour | Neonatal seizure-detection evaluation papers | search |
| Plant known events, count how many are recovered at a false-alarm threshold | Injection and recovery. Gravitational-wave searches report the fraction of simulated signals recovered below a false-alarm-rate threshold | Search-pipeline method papers (for example arXiv:2207.10410) | search |
| A negative made by shifting each channel in time, so real coincidences are broken and each channel's own statistics stay | Time slides, the standard background estimate of gravitational-wave searches; spike-train surrogates in neuroscience | Was et al. 2010, *Class. Quantum Grav.* 27:015005; Louis et al. 2010 and Stella et al. 2022 through [the false-alarm record](adr/0006-a-false-alarm-is-coincidence-the-event-rates-explain.md) | search; record |
| The count of co-active channels that chance reaches | The accidental coincidence rate of particle physics; radar's M-of-N rule | Survey sections 2.1 and 5.1 | survey |
| Resampling mice, not recordings, for intervals | The hierarchical bootstrap | Saravanan, Berman & Sober 2020, *Neurons, Behavior, Data Analysis, and Theory* 3(5) | search |
| Zero false calls in *T* hours bounds the rate near 3/*T* | The rule of three | | memory |

## What those fields learned that changes how this is built

1. **Report the curve as well as the point.** The free-response literature reports the whole
   trade-off, and a single operating point beside it. The first draft of the Chapter 2 design
   set the curve aside. It is back: `objective.operating_curve` gives it, and a search reports
   it beside the proposed setting.
2. **An event-based score can be gamed by long calls.** The seizure literature notes that a
   detector marking long stretches finds every event while making few separate false
   detections. Here the guard already exists and stays: matching is one to one and merged calls
   are counted
   ([the tuning record](adr/0010-tune-train-and-review-against-the-data-as-they-are.md),
   decision 3). The share of the recording spent inside calls should be reported with every
   score as a second guard; that is not built yet.
3. **More shifted copies stop helping.** Was et al. 2010 found that the variance of a
   false-alarm rate estimated from time slides levels off as slides are added, at a level set by
   the channels' rates and the coincidence window. So the number of negatives is chosen by
   watching the spread of the estimate, and a large number of draws is not quoted as precision.
4. **The cap is a stated convention.** Gravitational-wave work uses different false-alarm-rate
   thresholds for different purposes. The cap here is likewise chosen and stated, and is not
   derived. It is Tony's to set, after each detector's rate on the negatives has been measured.

## Where this project's use differs, and why that is argued and not inherited

- **The shift is short on purpose.** A time slide in a gravitational-wave search is longer than
  any real lag between detectors. Here the shift is 20 s: longer than a coordinated event and
  shorter than the minute-scale change in rate that all cells share, so that change stays in
  the negative. That is a choice made in the false-alarm record, decision 2, for scoring only.
- **These are calcium events.** The surrogate literature is about spike trains. Its definition
  of chance is adopted as an argued choice (the same record), and nothing about what an event
  means to a cell is taken from it.
- **A negative of a recording with events keeps those events' onsets, scattered.** It is busier
  than the true background, so a false-call rate measured on it runs high. On simulated data a
  recording with nothing planted gives the true rate, and the difference between the two is
  measured. Gravitational-wave searches meet the same thing when real signals sit in the data
  their background is estimated from; how they handle it was **not searched** and is the first
  thing to look up before this difference is reported as a result.

## Not searched

Keyword spotting (false alarms per hour against false rejects), sleep-spindle and
sharp-wave-ripple detection, and spike-sorting benchmarks beyond the survey's one line on
SpikeForest. The sound-event-detection score cited in the false-alarm record (Bilen et al. 2020)
was not re-read. Any of these may hold a refinement; none is expected to change the rule, which
is the same in every field read.

## Sources found by search, 2026-11-13

- Was et al. 2010, time slides: <https://arxiv.org/abs/0906.2120>
- Injections recovered below a false-alarm rate: <https://arxiv.org/abs/2207.10410>
- Free-response analysis, Chakraborty's software and papers: <https://mirror.uned.ac.cr/cran/web/packages/RJafroc/index.html>
- Seizure-detection evaluation: <https://arxiv.org/abs/2106.00611>, <https://arxiv.org/abs/2508.04899>
- Hierarchical bootstrap: <https://pmc.ncbi.nlm.nih.gov/articles/PMC7906290>
- Neyman-Pearson criterion, lecture notes: <https://ece.iisc.ac.in/~parimal/2016/estimation/lecture-03.pdf>
