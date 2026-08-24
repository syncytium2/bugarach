---
status: open
filed: 2026-08-24
---

# Kreuz answered three of our SPIKE-synch questions in April, and we have not used any of it

Thomas Kreuz — the author of the synchronization measure `sync_detect` is built
on — replied to Tony by email in April. It surfaced on 2026-08-24, alongside
[the attribution audit](2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md),
and it settles one design choice, weakens one claim this repo makes about itself,
and names a defect that is checkable in `sync.py` today.

Quoted where it matters, because the wording carries the conditions:

> "for global event identification you should first use the SPIKE-synchronization
> profile **C (symmetric)**, since identification should not depend on order. If
> you use E you would only identify events that follow the predominant order."
>
> "we combined the SPIKE-synchronization approach with a **thresholding of the
> mean calcium signal** (higher than 1.7 standard deviations from the mean, **both
> conditions had to be satisfied**). We also set a threshold for **maximum allowed
> gap** for spikes of the same event, in order to avoid fragmented events. For a
> follow up paper … we added a quite sophisticated postprocessing where we made
> sure that **no event contains more than one spike from the same pixel** (which
> was essential for the new method proposed in Ref. 47)."
>
> "Other groups often use some kind of **thresholding of the PSTH**, see **Mainen
> and Sejnowski, Science 1995** for what might be the original use of that."

## 1. C over E — the choice was right, and now it has an author behind it

`sync_detect` thresholds **C**, the symmetric profile; it is plotted as
*"SPIKE-synch C (ISI-adaptive)"* and E appears nowhere in this tree. That was a
port decision inherited from interface2's stack rather than an argued one, and
Kreuz gives the argument: **identification should not depend on order**, and E
would return only the events following the predominant order.

Nothing to change. It is worth a sentence in whatever methods surface this app
grows, because it converts an inherited default into a defended one.

## 2. The measure's own author built the same detection layer we did

[`detector_history.md`](../detector_history.md) files SPIKE-synch as *"Tier 2 — a
published measure, with our detector on top"*, quoting interface2's *"The
detection layer here is ours."* It already qualifies that honestly —
dual-threshold hysteresis is ordinary practice, so this is ours as an
implementation without being a novel method.

**Kreuz's own lab has published detection layers on this profile**, and two of the
three components match ours: a threshold on the profile, and a **maximum allowed
gap** for spikes belonging to the same event — which is `max_gap` in `sync.py`,
arrived at independently.

**Read that as reassurance, not as a debt.** The author of the measure, building a
detector on it, reached for the same two knobs we did; that is evidence the design
is right. What it costs is one word — *ours* becomes *ours, and the same as his* —
and what it buys is the third component we do **not** have, in §4, which he calls
essential. Per Tony's ruling in
[the attribution note](2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md),
cite it and move on.

⚠ **Citations as Kreuz gave them, not resolved against PubMed here.** Cecchini
et al., *PLoS Comput Biol*, 2022 (see SM1); Kreuz et al., *J Neurosci Methods*,
2024; Mariani et al., *J Neurosci Methods* (auditory follow-up) — refs 45, 46 and
47 of thomaskreuz.org/publications/journal-articles. Resolve them before any of
this is quoted; that is exactly the step whose absence produced the wrong SCE
attribution.

## 3. Their recipe has two conditions and this app can satisfy only one

They require the profile threshold **and** the mean calcium signal above 1.7 SD —
*"both conditions had to be satisfied"*. **bugarach cannot do the second half and
never will at this layer**: the input is per-ROI event times, not fluorescence
(FOUNDATIONS §4, `docs/export_folder_spec.md`). The trace exists upstream, in the
producer's MATLAB, and this is one of the few places where something real is lost
at the export boundary.

Not a defect and not a request to change the contract — a limitation to state
plainly if `sync_detect` is ever presented beside the published method, and a
concrete answer to *"what would the folder have to carry"* if that question is ever
asked seriously.

## 4. `min_n` counts an ROI more than once, and their postprocessing exists to stop that

Kreuz calls it *essential*: **no event may contain more than one spike from the
same pixel**. Our per-ROI equivalent is the glossary's own rule — coactivity is
distinct active ROIs, *"one count per ROI, never a spike count"*.

**`sync_detect`'s floor does not honour it.** Reading `binned_synchrony` and the
hysteresis scan: `Cn` is the size of the same-time group that last wrote to a bin,
and because one train's event times are unique, a same-time group is necessarily
distinct ROIs *within that instant*. But `min_n` is a floor on **`Cn` summed over
every bin of a candidate event** — so an ROI firing in three bins of one event
contributes three times to a floor that reads as *"how many ROIs took part"*.
A single busy ROI can help clear it.

### Measured 2026-08-24, and the shape is worse than the prediction

**The detector already computes the honest number.** `n_participating_rois` — the
distinct ROIs with an event inside the detected span — is right there in
`SyncDetection`, computed by `_flag_artifacts` for the artifact criterion. **The
floor does not consult it.** This is not a missing capability: it is two numbers
in one object, and the gate reading the wrong one.

`tools/make_min_n_figure.py`, 12 seeds per regime, the bench recording,
SPIKE-synch at its benched operating point:

![Two scatter panels, what min_n gated on against distinct participating ROIs, with the floor drawn as a dashed horizontal line and unity dotted. Most points sit above the floor and scatter around the diagonal; dark red points sit below it, including events at one and two distinct ROIs](../learned/sync_min_n.png)

| regime | events | gated > participants | **below the floor** | single-ROI |
| --- | --- | --- | --- | --- |
| `baseline_quiet` | 78 | 43 (55%) | **7 (9%)** | 2 |
| `baseline_busy` | 91 | 48 (53%) | **12 (13%)** | 3 |

> ⚠ **These numbers were wrong when first published, by a little.** The first
> version of the figure passed `ext=(0.0, 2700.0)` — the nominal duration — where
> the bench gives the detector `recording_extent(s)`, the span of the events
> themselves, which on seed 1 is `(0.3, 2692.8)`. Close enough to look right and
> different enough to move the counts: 5 below the floor became 7, and 44% became
> 55%. The tool now goes through `bench.run_detector` like everything else. **The
> conclusion did not change; the digits did**, and the digits were in `docs/learned/`
> for an hour.

**Five events across the two regimes were reported as synchrony events with one
participating ROI**, having cleared a floor whose purpose is to require three.
Nineteen cleared it with fewer than three. On **more than half of all events** the
gating number exceeds the participant count, so the two disagree routinely rather
than in a tail.

**The rate is background-dependent — 9% quiet, 13% busy** — and that matters more
than either number on its own: the defect grows where activity rises, so a
treatment that raises firing manufactures low-participation "events" by itself.
That is [`RESET.md`](../RESET.md) §6's confound arriving through a second door.

**What it does not change:** any published figure. These events are already inside
what SPIKE-synch reports, so its scores include them; the numbers move only if the
floor does.

The fix is a distinct-ROI floor — a **mechanism change**, so it lands behind a flag
defaulting to current behaviour, recorded in [`forks.md`](../forks.md), per
[`RESET.md`](../RESET.md) §7 step 4. Parity is the product; `min_n` as it stands is
what MATLAB does and must stay reachable. **Not done here**: this file measures,
and the flag is its own decision with a re-fit behind it.

### Which of the six are affected — only this one

Asked directly, and answered by asking each detector for the participant count it
already publishes rather than by inventing a common rule. Bench recording, 12 seeds
per regime, both regimes pooled:

| detector | its own count | events | median ROIs | below 3 |
| --- | --- | --- | --- | --- |
| rate+context | *none — a pooled rate has no participants* | 408 | — | — |
| CoactDetect | `nrois` | 413 | 6–7 | **0** |
| LoCo | `magnitude` | 327 | 6 | **0** |
| binned SCE | `magnitude` | 789 | 15–18 | **0** |
| locust | `magnitude` | 954 | 5–7 | **0** |
| **SPIKE-synch** | `n_participating_rois` | 169 | 4–5 | **19 (11%)** |

**The difference is structural, not incidental.** SCE, LoCo and CoactDetect apply
`min_rois` **per bin** to a genuine distinct-ROI count (`obs[np.unique(bi)] += 1`,
*"1 per ROI per bin"*), and an episode is a merge of bins that each cleared it — so
every bin in the event independently had three. SPIKE-synch is the only one that
**sums across bins**, and summing is what lets one ROI count more than once.

⚠ **Two wrong measurements were made getting here, and both looked plausible.**
A first pass applied one span rule — *distinct ROIs with an onset inside
`[onset, onset+width]`* — to all six, and reported `rate` finding **0 ROIs in 94%
of its events** and locust in **83%**. Both were artifacts of the rule, not
findings: `rate` has no `ends` field, so the span collapsed to zero width; and
locust's `magnitude` counts cells **active** across its sliding window — painted
active for the rise interval — not onsets inside its 0.3 s reported width, so
counting onsets asked a question the detector was not answering. **Six detectors do
not share onset semantics, and a uniform rule over them produces a confident wrong
answer.** The check that caught it was reading one event: SCE onset 1060.30, width
1.30, nearest event 1064.90, own magnitude 10 — its `onset_sec` is the *bin edge*.

### locust on the real folder: present, and much smaller than reported

interface2's §4 says locust has no `min_rois` floor and that on quiet slices the
surrogate percentile lands at about one cell, *"compressing a ~29–40× group
contrast to ~2.7×"*. **Simulation cannot test that claim** — on the bench, on a null
recording, and on a null with the fitted background shape (`bg_rate_shape` 0.45),
no detector reports an event below three, because planted events always carry three
or more participants and the flat field leaves the surrogate null enough spread.

So it was run on the approved export folder — 84 recordings, read-only, aggregates
only:

| detector | stream | events | median | below 3 | 2-cell | 1-cell |
| --- | --- | --- | --- | --- | --- | --- |
| locust | fast | 6775 | 8 | 22 (0.3%) | 22 | **0** |
| locust | slow | 5165 | 8 | 23 (0.4%) | 23 | **0** |
| binned SCE | fast / slow | 1438 / 1894 | 16 / 17 | 0 | 0 | 0 |
| LoCo | fast / slow | 1371 / 2454 | 7 / 10 | 0 | 0 | 0 |

**The floor is genuinely missing and it costs 45 events in 11,940 — 0.4%, all of
them two cells, none of them one.** That is a real defect worth closing and it is
not the one described: nothing here could compress a group contrast by an order of
magnitude. Their number presumably comes from a different data set — the store
holds recordings this folder does not, and the dead-ROI rule has been applied here.
**Worth telling them**, because the report's §4 currently reads as a reason to put
locust behind a caveat in the UI, and on this folder that is not proportionate.

This also bears on RESET §4's *"SPIKE-synch's 0.254 is not its accuracy"* — that
is about a swept knob that could not bind. This is a second reason the number is
not the detector, and the two are independent.

## 5. `rate_detect` has a neuroscience root as well as a radar one

interface2's audit closes `rate_detect` as cell-averaging CFAR (Finn & Johnson
1968), which is where the *threshold form* comes from. Kreuz names where the
*practice* comes from in this field: **thresholding the PSTH**, pointing at
**Mainen & Sejnowski, *Science*, 1995** as possibly its original use. ⚠ Neither
paper has been read here, and Kreuz himself hedges with *"what might be"*.

Two roots for one detector is not a contradiction — it is the reason
`detector_history.md` §3 is organised as four traditions. Worth carrying into the
reference list as lineage rather than as the algorithm.

## What to do, cheapest first

1. ~~**Measure the `min_n` gap** (§4).~~ **Done 2026-08-24** — 9% of events in the
   quiet regime and 13% in the busy one clear the floor with fewer than three
   participating ROIs; five have one. **SPIKE-synch is the only one of the six**
   where this happens, because it is the only floor that sums across bins. On the
   real folder locust's missing floor costs 45 events in 11,940, all two-cell.
   Figure and tables in §4.
2. **Ask Kreuz the "adaptive" question while the line is open.** interface2 reports
   that their cSPIKE wrapper passed Satuvuori's adaptive time-scale argument as
   **0** — disabled — while calling the code path "adaptive"; our `sync.py`
   docstring, the glossary and the public viewer all inherit the word. It is
   ambiguous rather than plainly wrong: τ here really is ISI-adaptive, but
   `AdaptiveSPIKESynchroProfile`'s "Adaptive" means the Satuvuori extension that
   was off. **He answers email.** One question settles what the app should call it.
   **A mail to him is already drafted and waiting** — [`docs/kreuz_note.md`](../kreuz_note.md),
   paste-ready since 2026-08-11, asking whether a hard τmax is still PySpike's
   intended semantics. **These are one email, not two.** That draft was reviewed as
   it stands, so the "adaptive" paragraph needs writing and reviewing before it goes
   in; [the filing todo](2026-08-11-file-pyspike-max-tau-issue.md) carries the note
   for whoever sends it.
3. **Resolve the three Kreuz-lab citations** (§2) before quoting any of them.
4. **Fold C-over-E into the methods surface** (§1), whenever that surface exists —
   see question 3 of [the attribution note](2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md).

## The meta-finding, which is the expensive one

**This email is from April.** The repo spent 2026-08-21 and 2026-08-22 building a
literature shelf, filing
[`which detector origins are actually settled`](2026-08-21-which-detector-origins-are-actually-settled.md),
and writing a 741-line history to answer questions whose author had already
answered several of them in writing, to Tony, months earlier. There is no shared
place where a reply from an outside expert lands, so it sat in a mailbox while
sessions reasoned around it.

**Everything durable in this project is in git, and the correspondence is not.**
The cheapest fix is a `docs/correspondence/` file per exchange — who, when, what
they were asked, what they said, quoted — so the next session greps it instead of
re-deriving it. Two exchanges are already known to belong there: this one, and
whatever produced interface2's Cossart 2003 read.
