# ADR-0019: The decoys are retired; negatives are rate-matched and carry no coordination

## Status

Accepted, 2026-10-23, by Tony: *"Consider old decoys dead. We'll add rate matched negatives to
our toolset."* This ruling is new as of that date. It is not a record of an earlier one: on
2026-10-22 Tony recalled deprecating decoys, and a search of all three machines, `origin` and
GitHub found no such ruling ([the todo](../todo/2026-10-22-decoys-were-never-deprecated.md)).

It closes the question [ADR-0006](0006-a-false-alarm-is-coincidence-the-event-rates-explain.md)
left to "the objective's ADR", that is, whether the decoys leave the bench or are rebuilt. The
other open links of the scoring design (the objective and its false-alarm limit) are still open,
and this ADR does not decide them.

## Context

**What the decoys were.** Each bench recording planted six *decoys* (`distractor` in code; six
per recording on fast, slow and combined). Each was built like a middle-participation planted
event, with the same participation and jitter, and labelled negative. ADR-0006 decision 1 ruled
that a call where coordination is present is not a false alarm, so the decoys could not be
negatives. Since then, F1 has been reported both with and without decoy calls.

**What they did to the scores.** At the installed settings (ADR-0006's table, held-out seeds
49–96), four of six detectors on slow found every planted event, and the decoys alone separated
them. The 2026-09-17 review measured 119 of 150 decoys sitting within 60 s of a planted event.

**How related fields use decoys.** No synchrony or assembly benchmark we checked uses negatives
identical to its positives (ADR-0006's references). Fields that do use decoys build them to be
**known false while looking real**, and use their hit rate to estimate the false-discovery rate:

- in proteomics, the target–decoy search matches spectra against reversed or shuffled sequences
  that cannot occur (Elias & Gygi 2007);
- in statistics, knockoffs are synthetic variables that copy the real ones' correlation structure
  and are known to have no effect (Barber & Candès 2015; Candès et al. 2018);
- in drug screening, DUD-E gives each known binder 50 property-matched decoys that are presumed
  inactive (Mysinger et al. 2012).

Our decoys were the reverse: true positives scored as false.

## Decision

1. **The decoys are retired.** No new bench, search, training run or document plants them,
   scores against them or reports a number that depends on them.
2. **A negative is rate-matched and carries no coordination.** It keeps each channel's own event
   rate and the shared slow change in rate (minute-scale and above, ADR-0006 decision 2), and
   destroys the alignment between channels. That is ADR-0006 decision 3. Here it becomes a
   **tool in the toolset**, not a construction tied to the bench: given any multichannel
   recording of event times, simulated or real, it produces matched negatives. The per-ROI rigid
   shift at a *J* of seconds is the existing instance. Building the tool, and deciding whether it
   offers more than one construction, is open work.
3. **Numbers already recorded stay as they were.** Results scored with decoys are records of
   their date. A later document says "since then" when it reports the change, and does not call
   the old numbers corrected. This follows the 2026-10-20 no-ranking ruling for the detector
   document.

## Consequences

- **The bench code still plants decoys** (`n_distractors=6` in the bench configurations in `bench.py` and
  `bench_slow.py`, with `bench_combined.py` inheriting slow's count and setting its own `distractor_frac`). Setting them to zero changes every bench number and is its own PR, with
  the scores re-derived. Until it lands, report only `f1_without_decoys` and
  `precision_without_decoys`, which give the scores as if the decoys were not there.
- **The learned models' labels** no longer have a decoy case. Those models are on hold
  (2026-10-22), so nothing is retrained now.
- **The reply to the plain document's reviewer** can say that decoys were dropped and why, as
  something that changed "since then".
- **The rate-matched negative belongs to the general toolset** Tony set out on 2026-10-22, where
  the input is any multichannel stream of unlabelled event times. It does not depend on this
  lab's data.
- **Reopening this** takes a negative that is coordination by construction and can still be
  defended as false. That is a new ADR that supersedes this one.

## References

- Elias, J. E. & Gygi, S. P. (2007). Target-decoy search strategy for increased confidence in
  large-scale protein identifications by mass spectrometry. *Nat. Methods* 4:207–214.
  doi:10.1038/nmeth1019.
- Barber, R. F. & Candès, E. J. (2015). Controlling the false discovery rate via knockoffs.
  *Ann. Statist.* 43:2055–2085. doi:10.1214/15-AOS1337.
- Candès, E., Fan, Y., Janson, L. & Lv, J. (2018). Panning for gold: "model-X" knockoffs for high
  dimensional controlled variable selection. *J. R. Stat. Soc. B* 80:551–577.
  doi:10.1111/rssb.12265.
- Mysinger, M. M., Carchia, M., Irwin, J. J. & Shoichet, B. K. (2012). Directory of Useful Decoys,
  Enhanced (DUD-E): better ligands and decoys for better benchmarking. *J. Med. Chem.*
  55:6582–6594. doi:10.1021/jm300687e.
- The synchrony references are ADR-0006's: Grün et al. 2002, Louis et al. 2010, Stella et al.
  2022, Mölter et al. 2018, and Bilen et al. 2020.
