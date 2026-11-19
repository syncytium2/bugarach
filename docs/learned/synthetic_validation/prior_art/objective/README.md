# Is the tuning objective a reinvention? Eight literature reports (2026-11-13)

**Use this folder when** you want the source behind a claim in
[`docs/scoring_objective.md`](../../../../scoring_objective.md), or want to know how far a
citation there was actually checked.

Tony, 2026-11-13, on the write-up of the tuning objective: *"pursue each of the web serach
results with agents to find the literature underlying the claims ... it needs robust support
that we are not inventing things, these are established tools"*.

Eight Claude agents each took one strand, opened primary sources where they could, and recorded
for every source whether the full text was opened, only the abstract, or nothing. The eighth was
told to assume the method is a reinvention and try to prove it. The reports are kept as
written, with two changes: paths on the machine they ran on were removed, and in the first
report one sentence was reworded ("They wrote of" became "The 1933 paper speaks of", and an
example lost its quotation marks), because the repository's check for private correspondence
reads "they wrote" beside a quotation as someone's letter. The sentence describes a published paper.

**How far to trust them.** They are agents' reports, not a human reading. Each marks its own
access level per source, and several say that quotations came through a summarising fetch tool
and must be re-read before being quoted. Spike-train papers are described in their own terms,
so the reports say "firing" where this repository would say "event" or "onset".

| file | strand |
|---|---|
| `01_neyman_pearson_and_cfar.md` | the criterion "most detections under a bound on false alarms", and radar's constant-false-alarm-rate detectors |
| `02_free_response_curve.md` | events found against false marks per unit, when the places a false call could fall cannot be counted |
| `03_seizure_detection_scoring.md` | sensitivity with false detections per hour, and what goes wrong with event-based scores |
| `04_time_slides_and_injections.md` | gravitational-wave searches: shifted background, planted signals, and real signals in the background |
| `05_spike_train_surrogates.md` | shifting whole trains as a surrogate, and its use for co-active cells in calcium imaging |
| `06_nested_resampling_and_rule_of_three.md` | resampling animals, its limits with few animals, and the bound from zero counts |
| `07_validation_on_simulated_truth.md` | validating detectors on simulated truth, matching simulations to data, and stating where results apply |
| `08_adversarial_search_for_missed_prior_art.md` | the search for names and pitfalls the others did not look for |
