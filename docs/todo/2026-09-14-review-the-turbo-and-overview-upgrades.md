---
status: open
filed: 2026-09-14
---

# Review the turbo and every-slice overview upgrades on real data, and confirm each one works

> **Tony, 2026-09-14**, ending the session that built them: *"can you write up a todo to review
> these upgrades and confirm their functionality?"*

Six PRs (#543, #549, #551, #554, #556, #560) changed the raster viewer's two column views between 2026-09-12 and 2026-09-14. Each was
built in response to Tony testing the deployed page, checked in a headless browser against the real
export folder (`2026-08-18_revised_2v_periods`, 84 recordings), covered by
[`tests/test_webapp_turbo.py`](../../tests/test_webapp_turbo.py), and deployed. **None has been
reviewed by a person working through a real task.** A headless check proves that the page draws
what the code says. It does not prove that the picture is right for the job. That review is what this todo is for.

All of it lives in [`docs/site/viewer.template.html`](../site/viewer.template.html). Edit the
template, then `python3 tools/assemble_viewer.py`; `docs/site/raster_viewer.html` is built.
[`docs/INDEX.md`](../INDEX.md) has a row each for turbo and the overview.

## What changed, and what to confirm

Open the real export folder at <https://bugarach.tonydefazio.com/viewer> (hard-refresh first).
It lands in turbo.

### Turbo takes the page — #543, #551

- [ ] The side column is hidden while turbo or the overview is open. A click on any pipeline step
      leaves the column view and brings the side column back.
- [ ] Each raster's height follows its ROI count: one pixels-per-ROI scale for the whole column,
      2–4 px, growing only when every row fits. A 51-ROI slice is visibly taller than a 24-ROI one.
      **Check small fields:** a raster is never shorter than 40 px (three label lines), so a slice
      under 20 ROI is drawn taller than its count alone would make it.
- [ ] The x-axis stays pinned under the rows while they scroll.
- [ ] 3 px between rasters. The footnote is one line under the column.
- [ ] The ROI order toggle (by id / by events) is in turbo's bar, the overview's and the
      single-recording view's. Pressing it in one sets it everywhere. "By events" uses the same
      per-recording counts the single-recording view sorts on. ROI ids sort naturally (2 before 10).
- [ ] In the compact pipeline row, the merge arrow does not touch "Recordings".

### The every-slice overview — #543, #549, #554

- [ ] The red button names **what is on screen**: "Showing baseline only · blind" in turbo,
      "Showing TTX full trace · unblinded" (or "baseline only · unblinded") in the overview,
      "Showing one slice" in the single-recording view. It is outlined while blind and filled while
      unblinded. The tooltip says what a click does.
- [ ] Entering asks "Are you sure?" every time. Cancel changes nothing. Leaving returns to the view
      the overview was opened from.
- [ ] **data**: *baseline only* (every aligned slice, cut at its baseline) or a treatment. The
      treatment is **treatment 1**, the first period to start where the baseline starts or later.
      A second drug, wash or high K+ is drawn but never selects.
- [ ] **groups**: all, or any subset of `group_id`. Turning off the last pressed group means all.
- [ ] Counts follow the other pick (#560). Under TTX: DI 11 · MALE 9 · ORX 9 · OVX 9 = 38 rows.
      With DI picked: TTX 11 · senktide 6 · SB222200 0.
- [ ] Rows are aligned so each baseline **ends** at 0s. Under TTX the axis runs about −20m … 0s … 55m, and rows
      begin where their recordings began.
- [ ] The timings strip is pinned above the rows. It shows the **median** of each period across
      the rows on screen, on as many tracks as overlap needs, a faint line for the spread, and
      "n of N" where only some rows carry the period.
- [ ] A row whose own periods sit more than 5 s off the median carries them in a thin lane that
      scrolls with it. **On the real folder that is 36 of 38 TTX rows**, because treatment lengths
      vary by up to ten minutes and high K+ by more. Decide whether that is useful or noise.
- [ ] An amber "‹treatment› starts +Ns" appears only when a row's treatment does not begin at its
      baseline's end. No real slice triggered it.
- [ ] A recording with no period read as a baseline is named in an amber notice, not drawn.

### Assessed events and marks — #556, #560

- [ ] After **Assess all**, the single-recording raster shows its candidate lane at once. Before
      this, 3,168 candidates existed and none were drawn until something else redrew the raster.
      That was an old bug, not a regression.
- [ ] Turbo before an assessment: threshold marks from the K% / floor / window knobs, blue.
- [ ] Turbo after an assessment: the **assessed events are the blue triangles**, in verdict colours
      once judged, and the threshold marks move to a **grey** lane beneath. Each row labels its
      assessed count. This split was Tony's choice when asked.
- [ ] The overview draws the same marks by the same rule. Threshold marks run over the whole row,
      **treatment time included**, at turbo's knobs. Assessed events exist only inside baselines.

## Open questions this review should settle

1. **Threshold marks on treatment time are not tested against anything.** They are turbo's
   threshold — K ROIs within a moving window — applied to drug time, with no null. Is that a
   picture worth having next to the treatment, or does it invite reading a threshold as a finding?
   (FOUNDATIONS §9 on TTX not silencing coordination is the relevant caution.)
2. **The single-recording view still draws unjudged candidates light grey**, while turbo and the
   overview draw them blue. Tony was offered blue there too and has not answered.
3. **Turbo's knobs are not visible in the overview**, but they drive its threshold marks. Is that
   dependency discoverable, or should the overview show the K it is using in its bar?
4. **The per-row timing lane is near-universal on real data** (question under the overview above).
5. **The confirmation's wording**: "Set the MAHICE parameters blind first if you can. Look before
   you launch a run — but a K chosen after this is no longer a blind K." Written from Tony's "the
   idea is to set the params without prejudice, but the reality is you don't want to launch a run
   blind"; confirm it says what he meant.

## Done when

Every box above is ticked on the live page against a real export folder, or turned into its own todo
with what was wrong. The open questions each have an answer recorded here.
