---
status: open
opened: 2026-08-17
area: generator
---

# Planting the events erases the quiet tail, and no probe is involved

`bg_rate_shape` exists to reproduce one fact about real fields: **35% of ROIs
record no event at all** in a baseline window (`bugarach.bench.MEASURED_RATE_SHAPE`,
81 windows / 2 643 ROIs). It does. Then the coordinated events are planted on top
of it, and the quiet ROIs are gone.

`python tools/quiet_tail_vs_events.py` — 33 ROIs, 45 minutes, 9.6 mHz mean per
ROI, 20 seeds, the bench recording's own structure:

| | ROIs with no event |
|---|---|
| fitted background, no planted events | **28.8%** |
| fitted background, 15 events at 30/18/10% | **0.5%** |
| fitted background, 15 events at 100/75/50% | **0.0%** |
| flat background, no planted events | 0.0% |
| flat background, 15 events at 30/18/10% | 0.0% |

The arithmetic is not subtle once it is written down. Participants are drawn
uniformly over ROIs, so at a mean participating fraction of 19% an ROI escapes all
fifteen events with probability 0.81¹⁵ ≈ 4%. Thirty-three ROIs, and one of them
makes it.

Corroborated by a second implementation: the browser port of the generator that
ships with the raster viewer — same model, its own random source, written for a
different job — gives 28.2% and 1.1% on the first two rows.

## Why this is separate from what PR #50 already says

`docs/generator_revision_input.md` has the same mechanism twice, and this is a
third face of it that neither section states:

* **§1** — the promiscuity probe erases the tail, 26.7% → 0.0%. Conditional on
  switching `hot_window` on, and the report is careful that the bench runs a flat
  background today, so nothing is currently broken.
* **§2** — participation is drawn independently of an ROI's rate, and once ROIs
  genuinely differ 6.6-fold that uniform draw becomes an unchosen assertion.

New here: **the planted events alone do it**, with no probe, at the measured
participation. So any recording carrying both fitted heterogeneity and a normal
complement of coordinated events has no quiet tail — the two features cannot both
be true of the same recording as the generator is written. §1's finding is about a
test construct that can be turned off; this one is about the data every bench run
would produce the day `bg_rate_shape` is switched on.

It also gives §2's question a consequence. That ask — *are busier cells more
likely to take part in a coordinated event?* — is a fact about the preparation,
`fireflies` and global FOUNDATIONS §15 territory, and not ours to answer. What
this adds is what rides on it: while the answer is "uniformly", a simulated
recording matching the real silent fraction is one with almost no coordination in
it, and one with realistic coordination has a background nothing like a real
field's. Whichever way the lab answers, the generator can only reproduce one of
the two measurements it is fitted to.

## What not to do about it

Not this: reach for a zero-inflation term, drop the quiet ROIs, or tune
participation down until the tail survives. The silent fraction is not a target to
hit — it is a *consequence* of a fitted shape, which is the reason to believe the
shape rather than merely accept it, and hitting it by construction would throw
that away. And a zero-event ROI is not a dead ROI: that verdict belongs to the
exporter and needs every treatment of an ROI at once
([`2026-08-15-zero-event-rois-are-not-dead-rois.md`](2026-08-15-zero-event-rois-are-not-dead-rois.md)).

The decision this actually wants is §2's, made explicitly. If coordination
recruits with regard to how active a cell is, then drawing participants with a
rate-weighted probability leaves the quiet ROIs quiet and this closes with it. If
it does not, the generator is right and the finding belongs to the preparation:
a real field's silent third is telling us how few of its ROIs are available to
coordinate at all.

## Where it turned up

Building the raster viewer's simulator, which needed defaults a stranger could
trust and so had to be pointed at the measured values. The viewer ships with the
fitted background on and reports "no ROI in this recording is declared with no
events" on its own output — truthfully, which is how this got noticed.
