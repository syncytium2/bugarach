# ADR-0006: A false alarm is a call on coincidence the event rates explain

## Status

Accepted, 2026-09-23, by Tony. It covers **scoring and tuning detectors** on the fast, slow and
combined streams, and nothing wider. The first ADR since ADR-0005 on 2026-08-29; the habit restarts
with it ([README](README.md)).

It is **link 3** of the scoring design worked through on 2026-09-23, the one that says what counts
as chance. The event floor (link 1), the objective and its false-alarm limit (links 5 and 6) and
the real-data check (link 4) are still being decided. Each gets its own ADR, which cites this one.

## Context

**The bench held two definitions of a false alarm that disagreed.** Every bench recording scores a
detector against:

- planted coordinated events at three participation levels;
- the **elevated-rate test**, a 300 s stretch with every ROI's event rate raised and nothing
  planted;
- the **no-coordination recording**, background only;
- six **decoys** per recording (`distractor` in code).

The first two negatives are **coincidence the event rates explain**, and a call on them is a false
alarm under any reading. The decoys were built as a middle-level planted event with only the label
changed, the same participation and the same jitter
(`simulate.py`, the correlated-burst block). So a call on a decoy counted as a false alarm although
it was, by construction, a call on coordination.

Measured on held-out seeds 49–96, at each stream's installed settings:

| stream | decoys touched | F1 as scored | F1 with decoy calls left out of precision |
|---|---|---|---|
| fast | 14–100 % | 0.474–0.751 | 0.481–0.893 |
| slow | 99.8–100 % | 0.757–0.859 | 0.894–1.000 |
| combined | 37–100 % | 0.571–0.807 | 0.607–0.933 |

On slow, four detectors of six find every planted event (recall 0.999–1.000) and would score
0.998–1.000 without the decoys. As scored, they sit near 0.85. **What separated detectors on slow
was the decoys alone**, and a decoy cannot be told from an event. The settings search optimised
F1 against them, and the learned models trained on them labelled 0 (`learn/encode.frame_targets`)
with the threshold then picked by F1 on recordings that held them (`learn/train.pick_threshold`). A
network shown the same pattern labelled both ways can only lower its confidence in both.

**What the literature uses as a negative.** The synchrony literature counts false positives on
data whose rates change and which carry no excess synchrony. Louis et al. (2010) use rate steps.
Stella et al. (2022) use independent trains that copy recorded rate profiles. Grün et al. (2002)
use sliding windows because rates are not stationary. No benchmark we checked uses negatives
identical to its positives. The nearest-looking case, cross-triggers in sound-event detection
(Bilen et al. 2020), penalises calls on a genuinely *different* labelled class. The references
were checked on 2026-09-23 (scratch note, not in the tree; the full list is below).

That literature is about **spike trains**, and these are calcium events, whose meaning to the cell
is open ([#766](https://github.com/syncytium2/bugarach/pull/766), glossary: *firing*, retired). So
its definition is adopted as an argued choice here, not inherited as a fact about the preparation.

**The recordings separate two timescales.** Re-measured on the de-pinned default export, 84
recordings from 44 mice, on all three streams
([#768](https://github.com/syncytium2/bugarach/pull/768)):

- once CoactDetect's episodes are removed, what the population does together **at 1-second bins
  reads about 1.0**, no more than independent ROIs;
- **at 1-minute bins it still reads 2.2–2.5** on every stream (fast 2.36, slow 2.17, combined 2.51,
  after the 120 s block control), and no surrogate that destroys sub-second timing touches it.

So coordinated events and shared change in event rate sit roughly two orders of magnitude apart
in time. What the minute-scale change *is* — the preparation's state, a measurement that moves
every ROI's detection threshold together, or something worth detecting — is not known, and no one
has asked the producer.

## Decision

1. **A false alarm is a call on coincidence the ROIs' event rates explain**, including rates that
   change together. A call where coordination is present is not a false alarm, whatever label a
   bench gives it.
2. **Shared change in event rate at a minute or more is background, for scoring and tuning.** Tony,
   2026-09-23: *"let's call it background for this purpose."* A call on that change alone is a false
   alarm. This is a working choice for one purpose and **not a finding about the preparation**; what
   the change is waits, flagged as important
   ([todo](../todo/2026-09-23-minute-scale-shared-change-is-background-for-now.md)).
3. **A negative is built from rate structure with no coordination.** On the bench that is the
   no-coordination recording and the elevated-rate test. On real recordings it is a surrogate that
   keeps each ROI's own event timing and minute-scale shared change and destroys the alignment
   between ROIs: the per-ROI rigid shift at a *J* of seconds, which #768 measured leaving the
   minute-scale part in place: with the episodes removed, the 1-minute reading goes from 2.54 to 2.48
   on fast, 2.61 to 2.45 on slow and 2.77 to 2.68 on combined, at *J* = 20 s.
4. **The same definition holds on fast, slow and combined.** Each stream's rates, jitter and
   participation are its own measurements. What counts as chance does not change between them.

## Consequences

- **The decoys, as built, cannot be negatives.** They are coordination by construction, so under
  (1) a call on one is not a false alarm. Whether they leave the bench or are rebuilt as
  coincidence the rates explain is for the objective's ADR (links 5 and 6), and until then **no
  bench, search or training run changes**. Anything reported in the meantime shows F1 with and
  without decoy calls, as the bench tables page does.
- **The learned models' labels follow the same rule.** A future training run labels 1 on planted
  coordination and 0 on everything else. The current models learned from contradictory labels, and
  are retrained once the objective's ADR says what they are tuned to.
- **The 10–45 s band is unassigned.** Nothing on the bench plants structure there, so this ADR binds
  nothing in it. A real-data check that uses the rigid shift chooses *J* knowing that it treats the
  band below *J* as coordination-scale and the band above it as background.
- **Writing it up.** The methods section can state the definition, its source in the synchrony
  literature, the argued transfer to calcium events, and the measured separation of timescales that
  makes it usable here. It must also say that minute-scale shared change was treated as background
  by choice.
- **Reopening it** takes an answer about what the minute-scale change is. If it turns out to be
  something the preparation does that the analysis should detect, this ADR is superseded, not
  edited.

## References

- Bilen, Ç., Ferroni, G., Tuveri, F., Azcarreta, J. & Krstulović, S. (2020). A framework for the
  robust evaluation of sound event detection. *Proc. ICASSP 2020*, 61–65. arXiv:1910.08440.
- Grün, S., Diesmann, M. & Aertsen, A. (2002). Unitary events in multiple single-neuron spiking
  activity: II. Nonstationary data. *Neural Comput.* 14:81–119. doi:10.1162/089976602753284464.
- Louis, S., Gerstein, G. L., Grün, S. & Diesmann, M. (2010). Surrogate spike train generation
  through dithering in operational time. *Front. Comput. Neurosci.* 4:127.
  doi:10.3389/fncom.2010.00127.
- Stella, A., Bouss, P., Palm, G. & Grün, S. (2022). Comparing surrogates to evaluate precisely timed
  higher-order spike correlations. *eNeuro* 9(3). doi:10.1523/ENEURO.0505-21.2022. The repository's
  earlier reading warns against citing its *conclusion* about which surrogates agree
  ([INDEX](../INDEX.md), surrogates row); this ADR cites only its false-positive design.
- Mölter, J., Avitan, L. & Goodhill, G. J. (2018). Detecting neural assemblies in calcium imaging
  data. *BMC Biol.* 16:143. doi:10.1186/s12915-018-0606-4. Checked for decoy-style negatives; it has
  none, and it scores assembly membership rather than event times.
