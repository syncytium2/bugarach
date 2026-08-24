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

`sync_detect` thresholds **C**, the symmetric profile; the served viewer plots it
as *"SPIKE-synch C (adaptive)"* and E appears nowhere in this tree. That was a
port decision inherited from interface2's stack rather than an argued one, and
Kreuz gives the argument: **identification should not depend on order**, and E
would return only the events following the predominant order.

Nothing to change. It is worth a sentence in whatever methods surface this app
grows, because it converts an inherited default into a defended one.

## 2. "The detection layer here is ours" is weaker than this repo has been saying

[`detector_history.md`](../detector_history.md) files SPIKE-synch as *"Tier 2 — a
published measure, with our detector on top"*, quoting interface2's *"The
detection layer here is ours."* It already qualifies that honestly —
dual-threshold hysteresis is ordinary practice, so this is ours as an
implementation without being a novel method.

**Kreuz's own lab has published detection layers on this profile**, and two of the
three components match ours: a threshold on the profile, and a **maximum allowed
gap** for spikes belonging to the same event — which is `max_gap` in `sync.py`,
arrived at independently. So the tier is right and the sentence around it is not:
the construction is not merely *ordinary*, it is *published by the measure's own
author*, and the papers are named.

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

⚠ **Predicted from the code, not measured.** Nothing here has counted how often
a detected event's summed `Cn` exceeds its distinct-ROI count, and the effect
could be small at the shipped operating point. **The measurement is cheap and
comes first**: report distinct participating ROIs alongside summed `Cn` for every
`sync_detect` event on the bench recording, and see how far apart they are.

If they are far apart, the fix is a distinct-ROI floor — which is a **mechanism
change**, so it lands behind a flag defaulting to current behaviour, recorded in
[`forks.md`](../forks.md), per [`RESET.md`](../RESET.md) §7 step 4. Parity is the
product; `min_n` as it stands is what MATLAB does and must stay reachable.

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

1. **Measure the `min_n` gap** (§4). One bench run, no fetching, and it is the
   only item here that could change a number.
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
