# Chapter 2, section draft: how detectors are tuned and scored, and where each tool comes from

**Use this page when** you want to know what a settings search maximises, how false calls are
counted, which established methods each part is taken from, and how far each citation was
checked.

> **Draft of a dissertation section, not murderboarded.** Second version, 2026-11-13. The first
> version rested on one web search per claim. Tony asked for the literature under each claim
> (*"it needs robust support that we are not inventing things, these are established tools"*).
> Eight Claude agents then traced one strand each; their reports are in
> [`learned/synthetic_validation/prior_art/objective/`](learned/synthetic_validation/prior_art/objective/README.md)
> and every citation below is taken from them. **No human has read these sources for this
> section.** Where a report says a quotation came through a summarising fetch tool, this page
> paraphrases and does not quote.

**The claim of this section.** Nothing in the way Chapter 2 tunes and scores detectors is a new
method. Each part is an established tool with a name, and in gravitational-wave transient
searches nearly the whole procedure runs end to end under standard names. Four details are this
project's own adaptations or have no exact precedent that the search found; they are listed in
section 8 and are not claimed as contributions.

**Why the section exists.** Three of this project's detectors were found, months after they
were written, to use the mechanisms of radar's constant-false-alarm-rate detectors
([`detector_history.md`](detector_history.md)). The scoring should not be a second case.

## How to read the citations

Each source carries the access level its report recorded:

| Mark | Meaning |
|---|---|
| **read** | An agent opened the full text and read the passage cited |
| **read via tool** | The full text was opened through a fetch tool that returns a small model's extraction; wording must be re-checked before quoting |
| **abstract** | Only the abstract or a catalogue record was read |
| **not read** | Named by other sources; nothing of it was opened |

Abbreviations: **FROC**, free-response receiver operating characteristic; **CFAR**, constant
false alarm rate; ***J***, the half-width in seconds of the shift applied to one cell's event
train; **twin**, a simulated recording with the same background as another and nothing planted.

## 1. The problem being solved

A detector reads a continuous recording of event onsets from about 30 cells and makes calls,
each a span of time. On real recordings there is no record of which moments were coordinated
events. Two things can go wrong and they trade against each other: a real event is not called,
or a call is made where there is no event. Time is continuous, so there is no countable set of
moments at which a false call could have been made.

Chapter 2 therefore tunes and scores on simulated recordings in which events are planted at
known times, and it needs three decisions: what a search maximises, what a false call is counted
on, and how far a result on simulated recordings may be carried.

## 2. The objective: the most events found, under a cap on false calls

**What is done.** Among candidate settings of one detector, the search proposes the setting
that finds the largest share of planted events among those whose false calls per hour are at or
under a stated cap. Code: [`src/bugarach/objective.py`](../src/bugarach/objective.py).

**Its name.** This is the **Neyman-Pearson criterion**: bound one kind of error and, under that
bound, minimise the other.

| Source | What it establishes | Access |
|---|---|---|
| Neyman & Pearson 1933, *Phil. Trans. R. Soc. A* 231:289-337, doi:10.1098/rsta.1933.0009, sec. II-III | Fix the chance of rejecting a true hypothesis; among tests that meet it, take the one with the greatest chance of rejecting a false one. The paper speaks of errors of the first and second kind, not of detection and false alarm, and says how the balance is struck is left to the investigator | read |
| Van Trees 1968, *Detection, Estimation, and Modulation Theory, Part I*, sec. 2.2, p. 33 | States it as a named criterion in detection terms: constrain the false-alarm probability and design the test to maximise the detection probability | read (course-hosted scan) |
| Lehmann & Romano 2005, *Testing Statistical Hypotheses*, 3rd ed., sec. 3.1 and Theorem 3.2.1 | Separates the formulation (bound one error, minimise the other) from the lemma (a likelihood-ratio test is most powerful when both distributions are known) | read |
| Scott & Nowak 2005, *IEEE Trans. Inf. Theory* 51:3806, doi:10.1109/TIT.2005.856955 | Uses the criterion to choose a rule from labelled examples when the distributions are unknown | read (technical-report version) |
| Tong, Feng & Li 2018, *Sci. Adv.* 4:eaao1659, doi:10.1126/sciadv.aao1659 | Names this Neyman-Pearson classification, and shows that capping the *observed* error rate does not cap the true one (section 6) | read |

**What is borrowed and what is not.** The criterion is borrowed: it is the objective. The lemma
is not: nothing here is a likelihood-ratio test, no distribution is known, and no setting is
called optimal or most powerful. The rule only orders a finite set of settings by error rates
measured on simulated recordings. Scott & Nowak and Tong et al. are the precedent for using the
objective that way.

**A cap per hour, not a probability per test.** The criterion bounds a probability. Here the
bound is on a rate, calls per hour. Three literatures state the same constraint as a rate:

- **Sequential detection.** Lorden's formulation bounds the false-alarm rate, defined as one
  over the mean time to a false alarm, and optimises detection under it (Veeravalli & Banerjee,
  arXiv:1210.5552, sec. IV; **read**). Its objective is delay, not the share of events found, so
  it is the precedent for the per-time cap only.
- **Radar.** CFAR detectors set a threshold from a local estimate of the background so that the
  false-alarm probability holds as the background changes, and are compared by detection
  probability at a design false-alarm probability (Finn & Johnson 1968, *RCA Review* 29:414;
  Rohling 1983, doi:10.1109/TAES.1983.309350; Gandhi & Kassam 1988, doi:10.1109/7.7185; all
  **read**). These three papers pursue the same constrained objective; none of them names
  Neyman or Pearson. The textbook that links the two (Richards, *Fundamentals of Radar Signal
  Processing*, ch. 6 and 7) was seen as a table of contents only, so the link is stated here as
  a shared objective and not as a derivation.
- **Speech.** Keyword spotting reports the false-reject rate at one false alarm per hour
  (Sainath & Parada 2015; **search snippet only**).

**What is not claimed about combined scores.** Reporting detection at a stated false-alarm rate
is the convention in radar and in the NIST detection evaluations, where a single performance
number is called inadequate when two error types trade off (Martin et al. 1997, *Eurospeech*,
doi:10.21437/Eurospeech.1997-504; **read**). An F-score also moves with the proportion of
positives when the detector has not changed (Fawcett 2006, doi:10.1016/j.patrec.2005.10.010,
sec. 4.2; **read**). That is the whole argument. Other fields keep combined scores: the current
seizure-detection framework reports F1 beside false alarms per day (Dan et al. 2024,
arXiv:2402.13005; **read**). F1 is therefore reported beside the objective and is not what a
search maximises.

**Where the first pass went wrong.** On the bench sets of 2026-11-12 most tuned detectors
scored 0.97 to 1.00 on mean F1. The sets had no negatives, precision was near 1 for any
setting, and F1 followed recall alone.

## 3. Why false calls are counted per hour: the method of free response

**What is done.** The score is two numbers: the share of planted events found, matched one to
one, and false calls per hour of recording.

**Its name.** This is the **method of free response**. It was introduced for exactly this
setting, a listener reporting signals that arrive at arbitrary times in a long listening
interval, and only later carried into medical imaging.

| Source | What it establishes | Access |
|---|---|---|
| Egan, Greenberg & Schulman 1961, *J. Acoust. Soc. Am.* 33:993, doi:10.1121/1.1908935 | The method of free response: hits and false alarms for signals at random times in continuous observation | abstract |
| Miller 1969, *J. Acoust. Soc. Am.* 46:1473, doi:10.1121/1.1911889 | Names the FROC curve, and gives the reason an ordinary operating characteristic cannot be used: no observation interval is defined | abstract |
| Bunch et al. 1978 (*Proc. SPIE* 0127:124, doi:10.1117/12.955926) | First use in imaging | not read |
| Chakraborty 2013, *Acad. Radiol.* 20:915, doi:10.1016/j.acra.2013.03.001; Chakraborty 2010, doi:10.1093/rpd/ncp305 | The history above, and the imaging definitions: lesions correctly localized over all lesions, against non-lesion marks per image | read |
| Petrick et al. 2013, *Med. Phys.* 40:087001, doi:10.1118/1.4816310 | Minimum reporting for a detection system: sensitivity and mean false positives per case, with intervals, and a stated rule for matching marks to targets | read (first two thirds) |
| Setio et al. 2017, doi:10.1016/j.media.2017.06.015, sec. 3.3 | A widely used operating-point report: sensitivity at 1/8 to 8 false positives per scan | read |

**The same pair in neighbouring fields.** Automated seizure detection has long reported the
share of seizures detected with false detections per hour or per 24 hours; Temko et al. 2011
(doi:10.1016/j.clinph.2010.06.035; **read**) call these the two most common event-based
measures. It is common practice, not a standard: the same sources complain that measures differ
between papers.

**What is borrowed and what is not.** The two axes are borrowed. The analysis that the imaging
field builds on them (rated marks, case-level figures of merit, jackknife inference) is not, and
this scoring is not called FROC analysis. Chakraborty warns against using the curve's area as a
summary, because the horizontal axis has no upper limit. The report here is the curve and one
operating point on it (`objective.operating_curve`).

**Pitfalls those fields document, and what is done about each.**

| Pitfall | Source | Here |
|---|---|---|
| Lengthening every detection raises the share found and lowers false detections per hour together, so both event-based measures can be made arbitrarily good | Temko et al. 2011 (**read**) | Matching is one to one, so a call that swallows two events finds one ([the tuning record](adr/0010-tune-train-and-review-against-the-data-as-they-are.md), decision 3). **Owed:** a time-based companion, the share of the recording spent inside calls |
| The result depends on the matching rule and the tolerance, and a wider tolerance flatters every detector | Chakraborty 2010; Petrick et al. 2013; Kallergi et al. 1999 (**abstract**) | One rule and one tolerance for every detector. **Owed:** the curve at a second tolerance |
| Imaging credits the best mark on a target and discards surplus marks; seizure detection's default counts any overlap | Chakraborty's online book, sec. 2.4.2; Ziyabari et al. 2017, arXiv:1712.10107 (**read**) | One-to-one matching is stricter than both, and this is said wherever a number is compared with those fields |
| A lenient scoring rule lets a random caller score well | Kim et al. 2022, arXiv:2109.05257 (**read**) | **Owed:** a random caller at the capped rate, drawn on the curve as a floor |
| A mean rate hides hours that far exceed it | Lorden's rate is defined for a stationary process | **Owed:** false calls by time block |
| False detections per hour depend on how dense the events are and which recordings are pooled | Temko et al. 2011, sec. 4.6 (**read**) | A rate is quoted with the recordings and the event rate it was measured on |

## 4. What a false call is counted on: shifted trains and time slides

**What is done.** A negative of a recording moves each cell's whole event train by its own
random offset, uniform in ±*J* with *J* = 20 s. Code:
[`src/bugarach/negatives.py`](../src/bugarach/negatives.py). The same construction is the null
that sets each recording's event floor
([the floor record](adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md)).

**Its names.** In neuroscience it is whole-train shifting, published as spike-train dithering,
SHIFT and trial shifting. In gravitational-wave searches it is time slides.

| Source | What it establishes | Access |
|---|---|---|
| Pipa et al. 2008, *J. Comput. Neurosci.* 25:64, doi:10.1007/s10827-007-0065-3, sec. 2.4 | Introduces random shifts of entire trains as the surrogate: cross-structure faster than the shift is destroyed, each train's own structure is kept at all timescales | read |
| Louis, Borgelt & Grün 2010, ch. 17 of *Analysis of Parallel Spike Trains*, doi:10.1007/978-1-4419-5675-0_17 | Evaluates it against five other surrogates and recommends it; intervals are fully kept, rates are smoothed over the shift width; shifted spikes are wrapped around the end so that chance coincidences are not underestimated | read |
| Louis, Gerstein, Grün & Diesmann 2010, *Front. Comput. Neurosci.* 4:127, doi:10.3389/fncom.2010.00127 | At a sharp shared step in rate the method gave up to 10 % false positives at a 1 % level | read |
| Stella, Bouss, Palm & Grün 2022, *eNeuro* 9(3), doi:10.1523/ENEURO.0505-21.2022 | Six surrogates compared; trial shifting suggested as the method of choice; rate modulation is kept only approximately | read |
| Amarasingham et al. 2012, *J. Neurophysiol.* 107:517, doi:10.1152/jn.00633.2011 | The principle: a perturbation of a given width tests for structure finer than that width and keeps what is slower; independence across cells is the wrong null when the aim is to isolate one timescale | read |
| Dard et al. 2022, *eLife* 11:e78116, doi:10.7554/eLife.78116; Bocchio et al. 2020, *Nat. Commun.* 11:4559 | Calcium imaging: an independent circular shift of each cell, and the 99th percentile of the co-active count over the shifted copies as the threshold for a synchronous event | read |
| Babak et al. 2013, arXiv:1208.3491; Usman et al. 2016, arXiv:1508.02357; Abbott et al. 2016, arXiv:1602.03839 | Time slides: one detector's data shifted against another's by more than the coincidence window, to estimate the rate of accidental coincidences. Valid when noise is not correlated between detectors | read via tool; read via tool; read |

**What the shift keeps and what it destroys, stated with its scale.**

- It keeps every interval between one cell's own events.
- It keeps changes in rate that the cells share **approximately, and only those slower than
  the shift width**: the shared rate profile is smoothed over about 20 s.
- It destroys the timing between cells **at every scale up to about the shift width**, not
  only at one or two seconds.

**What *J* = 20 s declares.** In these sources the width of the perturbation is a scientific
statement of what counts as rate and what counts as coordination; it is not estimated. Pipa et
al. set it at 2 to 5 times the coincidence window. Here it is 10 to 20 times the 1 to 2 s window.
The consequence is definitional and has to be said: **shared change in rate on a scale of 2 to
20 s counts as coordination under this null**, and a detector will call it.
[The false-alarm record](adr/0006-a-false-alarm-is-coincidence-the-event-rates-explain.md)
already leaves the 10 to 45 s band unassigned; this is the same gap seen from the surrogate's
side.

**Four places where this use differs from the published method.**

1. **Onsets pushed past the ends are dropped, not wrapped.** The published form wraps. Dropping
   thins the first and last *J* seconds of every negative, so a score reads only the window in
   between (`Negative.valid_window`), where no onset can be missing. A negative does not keep
   each cell's event count exactly, and no page should say it does.
2. **The shift is bounded and short on purpose, to leave the minute-scale shared change in
   rate in the negative.** That is this project's adaptation. The calcium-imaging papers use an
   unbounded circular shift, which removes slow shared changes too; they support the null for
   the co-active count and not the claim that slow change is preserved. No gravitational-wave
   source shortens a shift for this reason; where detectors share noise that field stops using
   time slides, and it limits the span of shifts only to follow slow changes in the detectors
   (GWTC-1, arXiv:1811.12907, sec. III A; **read**).
3. **Offsets are independent, so some pairs of cells stay nearly aligned.** The difference of
   two offsets is spread over ±40 s, so a pair that was co-active within 1.5 s stays so in about
   7 % of negatives (the surrogate report's arithmetic). Groups of three or more are almost
   always separated. Gravitational-wave pipelines impose a minimum relative shift instead.
4. **These are calcium events.** The case against other surrogates in the spike-train
   literature rests on refractoriness and interval regularity, which are not established for
   calcium event onsets. The case for whole-train shifting carries over, because it leaves the
   structure inside each train untouched whatever that structure is. The percentages measured
   in those benchmarks do not carry over.

## 5. Where the false-call rate is trusted: generated negatives, and the limits of a shifted one

**The established benchmark design is not a shifted copy.** The spike-train benchmarks count
false positives on data **generated** to be independent, with the rate profiles of the recorded
data: Stella et al. 2022 build artificial data with each experimental dataset's statistics
under two generating models; Louis, Borgelt & Grün 2010 and Pipa et al. 2008 do the same with
designed rate changes (all **read**). In such data every detection is a false positive by
construction. On experimental data, Stella et al. note, one cannot speak of false positives at
all without ground truth.

**So on simulated recordings the false-call rate comes from the twin.** A twin, the same
simulated background with nothing planted, is this project's form of that design. It is the
rate to report and to hold to the cap. The shifted negative is the only construction a real
recording allows, and Chapter 2's job is to measure how far it is from the twin.

**Three reasons a shifted negative of a recording can mislead.**

| Reason | Source | Direction |
|---|---|---|
| The recording's own coordinated onsets stay in the negative, scattered | Abbott et al. 2016, sec. V: a signal's triggers pair with noise in the shifted data, the background is over-estimated and significance is conservative (**read**). Capano et al. 2017, *Phys. Rev. D* 96:082002, arXiv:1601.00130: keeping all samples over-estimates on average; removing coincidences is unbiased on average and under-estimates in the typical realisation (**read**) | Rate too high |
| Shared structure faster than the shift is erased from the negative | Louis et al. 2010; Grün 2009, doi:10.1152/jn.00093.2008 (**read via tool**) | Rate too low |
| The floor was set from the same shift | Takigawa et al. 2024, *eLife* 13:e85635, doi:10.7554/eLife.85635: a randomisation used to estimate false positives must not be the one used for detection; when it is, the estimate returns the nominal level (**read**) | Rate near the cap by construction |

The third applies to any detector whose participation minimum is the recording's floor: its
false calls on further shifts of the same recording are held near one per hour by the way the
floor was made, and say little about the detector.

**What follows for the design.**

- The difference between twin and shifted negative is **two opposing effects**, and one number
  hides them. Three recordings separate them: the twin; a shift of the twin (what shifting does
  to background alone); a shift of the recording with events (what leftover onsets add).
- The gravitational-wave result is that the excess is large only far in the tail and small at
  working thresholds (GWTC-3, arXiv:2111.03606, app. D; **read**). Whether that holds here is
  measured, not assumed: an event here contributes onsets on many cells at once.
- **One null has an unknown systematic error.** Two independently built nulls for the same
  catalogue gave reliabilities of 24 % and 51 % (Thompson et al. 2018, arXiv:1710.06758;
  **read**). A second construction is needed to bracket a real recording's rate.
  `bugarach.surrogates` already holds candidates.

## 6. How sure the numbers are

**A cap met on a sample is not a cap on the true rate.** Tong et al. 2018 show that choosing a
threshold so that the observed error is at or under the bound leaves the true error above the
bound in about half of realisations. This applies twice here: to the cap in the objective, and
to the floor rule "at most one chance call per hour". Their remedy is to choose with a stated
tolerance for exceeding the bound. **Owed:** the objective compares an upper confidence bound
on the rate with the cap, and states the confidence; until then every statement reads "at most
X false calls per hour on these simulated negatives" and nothing wider.

**More shifted copies stop helping.** Every shifted copy reuses the same trains, so the
variance of the estimated rate reaches a floor set by the channels' rates and the coincidence
window (Was et al. 2010, arXiv:0906.2120, eq. 10, for stationary Poisson triggers; **read via
tool**). Hours of shifted negative from one recording are not independent hours.

**Zero false calls.** With no false call in *T* hours, and false calls treated as a Poisson
process, the one-sided 95 % upper bound on the rate is 3.0/*T*, the rule of three; the upper end
of the two-sided exact interval is 3.7/*T*. The arithmetic was confirmed; the primary papers
(Hanley & Lippman-Hand 1983, doi:10.1001/jama.1983.03330370053031; Jovanovic & Levy 1997,
doi:10.1080/00031305.1997.10473947) were **not read**. The bound is too low if false calls come
in bursts.

**Few animals.** Recordings from one animal are not independent, and treating them as
independent makes intervals too narrow (Lazic 2010, doi:10.1186/1471-2202-11-5; Aarts et al.
2014, doi:10.1038/nn.3648; both **read**). Resampling animals removes that error and leaves
another. With 5 clusters a cluster bootstrap rejected a true null 15 % of the time at a nominal
5 % (Cameron, Gelbach & Miller 2008, working-paper version; **read**), and 24 clusters per arm
has been called the minimum at which to consider it (Flynn & Peters 2004,
doi:10.1186/1472-6963-4-33; **read**). Nothing tested 3. So for a set built from 7 mice, and
above all from 3:

- the result is called **a resampling range that respects the nesting**, never a 95 %
  confidence interval, and it is probably still too narrow;
- the number of animals and each animal's own value are shown beside it;
- animals are resampled with replacement and each animal's recordings are kept intact, which is
  the standard cluster bootstrap (Cameron et al. 2008; Field & Welsh 2007, **abstract**). With
  one or two recordings per animal there is almost nothing to resample inside one.

Building each simulated recording from one resample of animals, with the whole parameter
vector re-measured on it, is a **bootstrap predictive simulation**, the resampling analogue of
posterior predictive simulation (Fushiki, Komaki & Aihara 2005, doi:10.3150/bj/1116340296;
**abstract**). It is not a double bootstrap and not a plain parametric bootstrap.

## 7. Planting and recovering events, and how far a result carries

**Its names.** Injection and recovery in gravitational-wave searches; hybrid and simulated
ground truth in spike sorting; planted-assembly benchmarks in assembly detection.

| Source | What it establishes | Access |
|---|---|---|
| Usman et al. 2016, sec. 4.1; GWTC-1, sec. VII; GWTC-3, app. D | Sensitivity is measured by adding simulated signals and counting those recovered above a significance threshold | read via tool; read; read |
| Rossant et al. 2016, *Nat. Neurosci.* 19:634, doi:10.1038/nn.4268 | Known spikes added to real recordings, used both to choose detection settings and to score the result | read |
| Magland et al. 2020, *eLife* 9:e55167, doi:10.7554/eLife.55167 | Benchmarks on paired, simulated and curated truth; one setting across studies to limit over-fitting | read |
| Mölter, Avitan & Goodhill 2018, *BMC Biol.* 16:143, doi:10.1186/s12915-018-0606-4 | Planted assemblies with a designed default and one-at-a-time sweeps; performance depends strongly on the parameters of the data | read |
| Stella et al. 2022 | Simulated data built from each experimental dataset's own statistics, under two generating models | read |
| Rupprecht et al. 2021, *Nat. Neurosci.* 24:1324, doi:10.1038/s41593-021-00895-5 | Training data matched to the noise level and frame rate measured in the target data | read |

**"The pool is drawn from what was measured"** therefore has one direct precedent, Stella et
al. 2022, and one for the principle, Rupprecht et al. 2021. It is not the norm: most assembly
benchmarks use designed values. Three corrections to how this may be described:

- It is **an** established way to validate, not the established way. Authors of a simulator
  call it alternative and complementary to paired recordings (Buccino & Einevoll 2021,
  doi:10.1007/s12021-020-09467-7; **read**).
- It is **simulated ground truth**, not hybrid: nothing is planted into real recordings.
- The calcium spike-inference benchmarks (Theis et al. 2016; Berens et al. 2018; Rupprecht et
  al. 2021) use real paired recordings and cannot be cited as validation by simulation.

**The threshold for "found" is a stated choice.** Gravitational-wave pipeline papers quote
sensitivity at one false alarm per 100 years; the GWTC-3 catalogue uses a different criterion
for its headline figure and several false-alarm thresholds for other lists, each justified by a
trade between purity and completeness. In seizure detection quoted targets run from about one
false detection per hour to fewer than one per 24 hours, justified by what a clinician will
tolerate. **No source calls the threshold a convention in those words; that reading is this
section's.** Neyman and Pearson say the balance is the investigator's. The cap here is Tony's
to set, after each detector's rate on the negatives has been measured.

**Hold-outs.** Tuning on part of the pool and scoring on the rest follows the community
benchmarks' hidden test sets (Berens et al. 2018, doi:10.1371/journal.pcbi.1006157; **read**).
Scoring on a region of the measured ranges left out of tuning, and on a simulator variant, is
the simulator's analogue of leave-one-domain-out evaluation, which is one of three named ways
of choosing a model and is not recommended over the others by its source (Gulrajani &
Lopez-Paz 2021, arXiv:2007.01434; **read**). Using the same model to make the test data and to
analyse them has a name, the inverse crime (Kaipio & Somersalo 2007; **search snippet only**).

**Where a result applies.** A recording whose measured parameters fall outside the ranges the
pool covered is flagged as untested. The established term is the **applicability domain**, from
the OECD's principles for validating chemical models. Its primary sources (OECD 2007; Netzeva
et al. 2005, doi:10.1177/026119290503300209) were **not read**; the wording was checked in
Sahigara et al. 2012 (doi:10.3390/molecules17054791; **read**), which also shows that different
ways of drawing the domain disagree. The form used here is the simplest, a range per parameter.

**The limit, stated plainly.** Agreement on simulated recordings does not guarantee agreement
on real ones. Theis et al. 2016 (doi:10.1016/j.neuron.2016.04.014; **read**) found that
performance on simulated calcium recordings was not predictive of performance on real ones, and that
algorithms built on the simulator's own model did well on it. Magland et al. 2020 found that
simulated benchmarks may not reproduce the noise statistics of real recordings, and that
simulated data flattered precision in particular. The simulation tests only the properties it
contains.

**One circularity the precedents do not face.** If the planted events' parameters came from a
detector's calls on real data, the design would tune detectors on events shaped by a detector.
Chapter 1's tools were built to avoid that: the coordination-rates tool uses no event definition
and no threshold. The exception is the spacing between events, which is measured from peaks of
a co-active count against the floor. The chapter has to say which inputs are detector-free and
which are not.

## 8. What is this project's own, or has no exact precedent

None of these is claimed as a contribution. Each is a use of a standard principle and is listed
so that no reader takes it for standard practice with a citation behind it.

| Item | What the search found |
|---|---|
| The floor as worded: the smallest co-active count the shifted null reaches at most once per hour, per recording | The principle is everywhere (CFAR; a threshold from a null sample; the calcium-imaging percentile). The neuroscience precedents use a percentile or a p-value per frame, not a rate per hour. The exact form was not found |
| A short, bounded shift chosen to keep minute-scale shared change in rate | The timescale principle is established (Amarasingham et al. 2012). No source makes this specific choice; one abstract says long shifts are tolerable for moderate fluctuations (Was et al. 2010, *Class. Quantum Grav.* 27:194014; **abstract**) |
| Reporting twin against shifted negative as a standing column | Comparing a surrogate estimate with known truth on simulated recordings is established (Capano et al.; Stella et al.; Thompson et al.). The standing column appears uncommon |
| Refusing a setting at the edge of its search grid | Common practice in tutorials; no canonical citation found |

The search found no detector of sharp-wave ripples, sleep spindles or interictal spikes tuned to
a per-hour cap on a shifted null; those sources were reached only as snippets.

## 9. What this changes in the design

| Change | State |
|---|---|
| The false-call rate on simulated recordings is the twin's; the shifted negative is measured against it | Proposed in the design document; now with its precedent |
| The twin-to-shift difference is split with a third recording, the shift of the twin | Owed |
| A second, independently built null for real recordings | Owed |
| The cap is compared with an upper bound on the rate, at a stated confidence | Owed; `objective.py` uses the observed rate today |
| A minimum relative offset between cells, or a statement of how many pairs stay aligned | Owed |
| The share of time inside calls, the curve at a second tolerance, a random-caller floor, false calls by time block | Owed |
| The 2 to 20 s band is named as coordination under this null wherever the null is described | Done on this page; the two decision records are not edited |
| Intervals from few animals are called resampling ranges, animals kept intact | Owed in the measuring tool |
| The module's statement that a negative keeps each cell's count | Corrected |

## 10. What was not verified, and what to request

**Not read at all, and carrying a claim:** Richards's textbook (the link from the criterion to
CFAR); Miller 1969 and Egan et al. 1961 (the reason no false-positive fraction exists, and the
origin); Bunch et al. 1978; Hanley & Lippman-Hand 1983 and Jovanovic & Levy 1997 (rule of
three); Netzeva et al. 2005 and the OECD guidance (applicability domain); the supplement of
Malvache et al. 2016 (how that paper builds its null); Gotman 1982 and 1990 (the origin of
false detections per hour); Kay 1998 and Poor 1994.

**One identifier to check.** The two reports that read Capano et al. give different arXiv
numbers for it, 1601.00130 and 1708.06710. A search on 2026-11-13 ties the published paper to
the first; the second carries the same title and may be a companion. Both reports describe the
same study.

**Read only through a summarising tool, so re-read before quoting:** Grün 2009; Was et al.
2010; Usman et al. 2016; Babak et al. 2013; Miller et al. 2014; most excerpts in the
free-response report.

**Not searched:** scan statistics; change-point evaluation; the anomaly-detection benchmarks;
interictal spike detection; partial-area summaries (McClish 1989); how gravitational-wave
pipelines keep injections out of the background they are scored against.

**Requests for Tony, most important first.** Each report lists more.

1. Richards, *Fundamentals of Radar Signal Processing*, sections 6.1 and 7.1 to 7.3 (book).
2. Miller 1969, doi:10.1121/1.1911889.
3. Egan, Greenberg & Schulman 1961, doi:10.1121/1.1908935.
4. Was et al. 2010, *Limitations of the time slide method*, doi:10.1088/0264-9381/27/19/194014.
5. Hanley & Lippman-Hand 1983, doi:10.1001/jama.1983.03330370053031.
6. Ren et al. 2010, doi:10.1080/02664760903046102.
7. Malvache et al. 2016, supplementary methods, doi:10.1126/science.aaf3319.
8. Gotman 1990, doi:10.1016/0013-4694(90)90032-F.
9. Netzeva et al. 2005, doi:10.1177/026119290503300209.
10. Bunch et al. 1978, doi:10.1117/12.955926.
