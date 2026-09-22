# Morning summary to Tony, 2026-09-22 (verbatim)

The end-of-run summary delivered to Tony after the overnight methods-section run (PR #716), preserved
word for word at his request. Companions: the section (`coordination_pipeline_methods.md`), the cover
memo (`coordination_pipeline_methods_cover_memo.md`) and the run record
(`docs/reviews/coordination_pipeline_methods_2026-09-22.md`).

---

Written for: you (Tony), reading this in the morning.

The methods section has been through three full review rounds (the second and third blind) and is in the darkroom as a Word document. Before you use any results for LoCo, locust or binned SCE, read the cover memo: it lists five code defects that make some reported numbers differ from what the methods describe.

**Where things are** (`<darkroom>/bugarach/2026-09-22-methods/`)
- `coordination_pipeline_methods.docx`, with Word's `.pdf` and an `.html` copy. It has 16 pages, one figure and four tables.
- `coordination_pipeline_methods_cover_memo.docx`: everything that is for you rather than the manuscript.
- `fig1_benchmark_recording.png`: one benchmark recording, with what was planted in a lane above a plain raster.
- The repo copies are in PR #716, set to merge automatically once checks pass. The two review-record checks pass, and the tests covering the files I touched pass (386).

**What the review changed.** The first draft had three things wrong:
- **Search results:** it said the search left four detectors unchanged; it proposed changes for three of them.
- **Benchmark constants:** it said they were measured on this dataset; they were set from earlier data and only re-checked.
- **Close-events limit:** it implied the limit governed the coded-versus-learned comparison; it was only reported, and would have refused 19 of 48 coded choices.

Rounds 2 and 3 corrected a few dozen smaller claims against the code and the run records.

**Needs you first: a possible contamination.** Pinning isn't closed for three analyzed recordings (20260629_314, 20250926_237, 20260630_325). The dataset's own note says 314 was never run through the pinning detector. The producer's 2026-09-18 answer lists the other two as still under review. Your rule says a known contamination stops the work and goes to the producer that day. I haven't asked the producer, because whether this counts as known is your call.

**Code defects in the memo.** The methods describe the intended rule; the code does something else:
- LoCo and locust rates count calls whose onset falls outside the analysis window (212 LoCo and 234 locust calls in the fast stream).
- Binned SCE width and amplitude are measured over the wrong interval; measuring over the whole bin changes the result for 27% of its calls.
- `measure_calls` overwrites the detectors' own cell-count column with its own count.
- locust uses one threshold for the whole recording, baseline and treatments pooled, so a treatment that raises the rate also shifts the baseline threshold.
- The stored default settings for CoactDetect and LoCo are still the binned ones. The run's actual settings are now committed as `recorded_data_detector_settings.csv`.

**Decisions that are yours**
- **"Amplitude":** I kept your definition (cells ÷ width). Reviewers in all three rounds asked to rename it, and round 3 found it mostly tracks 1/width.
- **Citations for CoactDetect and LoCo:** the repo README asks for two papers (Grün et al. 2002; Amarasingham et al. 2012). Nobody here has read them, so they aren't cited yet.
- **Design problems a referee will raise:**
  - Distractors are built exactly like the 18% events and aren't kept away from them.
  - The elevated-rate test counts calls, so a long merge gap can hide firing.
  - No benchmark puts planted events on a treatment-level background, so sensitivity at treatment rates is unmeasured.
  - There is no statistics plan and no time-matched control.
- **Small calls:**
  - The participation move to 0.19 still gives 6 of 33 cells.
  - The learned detector used on recorded data is one refit I picked by judgement, run with a 2 s merge gap although selection chose 8 s.
  - The Kreuz personal-communication citation is gone, because his published papers carry the claim.

**Why the order differs from your list.** The section follows dependency order: optimization can't be explained before the scoring and limits it uses. All nine of your items are answered except the statistics part of "how the real data are assessed," which the section says is out of scope. Please also confirm that "the benchmark" means the synthetic benchmark recording and how it was built.

**Two things I didn't do**
- The build script lives only in my scratch folder, not the repo. A repo tool that writes to the darkroom by default is a small follow-up.
- The prose-check tool the review process names doesn't exist, so that review role checked by hand in every round.
