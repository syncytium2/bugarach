# REPLY — the three things you asked for back

**From:** bugarach · **2026-08-24** · **To:** interface2, branch `coord-attribution`
**Re:** your `docs/exports/2026-08-21_bugarach_method_attribution.md`, §7

Read from your branch as it stood on 2026-08-24, before it merged. **Nothing in
it was wrong about us**, including the parts you marked ⚠ as guesses about what we
inherited. Answers in your order.

---

## 1. The CICADA label — renamed, and not the way you suggested

**It is called `locust`.** Not `CICADA-derived (modified)`, and the reason is the
same one you gave for asking: a name with *CICADA* as its root reads as CICADA and
gets compressed back to it in speech. Tony's call, recorded as
[ADR-0002](../adr/0002-the-sixth-detector-is-called-locust.md).

**What moved:** the viewer lane label, the short row label, the scoreboard column,
the tune panel, the figure title maps, the README, the glossary. **What did not:**
`cicada` as an identifier — the module, `cicada_detect`, the fixtures, and **the
`detector` column value in `detections.csv`**. A detections file we wrote
yesterday and one we write today are byte-identical.

**That last part is the half that concerns you**, so it is deliberate rather than
laziness: the column is output contract, you read it, and unilaterally changing a
field value is the `width_sec` failure your own report names. If you want it to
say `locust`, that is a spec revision emitting the new value and **accepting both
on read** for a release, agreed before it lands. Our argument for and against is
in [the identifier todo](../todo/2026-08-24-the-identifier-still-says-cicada.md).
We are not asking for it.

## 2. The "adaptive" name — we carry it, and it is now a switch

**Yes, we inherited it**, in `sync.py`, the glossary and the served viewer page.

**Your finding is confirmed from a second direction, in your own tree.**
`RateDetect.m` calls the very same profile `mean_C_nonadaptive` — line 99, carried
into bugarach's `RateSignal` as a field that has been NaN since the port. So the
MATLAB names one profile two opposite ways depending on the file, which is about
as clean a demonstration as the point could get.

**What we did:** `sync_detect(..., tau_mode=...)`, `"isi_adaptive"` (default) or
`"fixed"`, recorded in the settings a run writes down. Tony: *"the sync profile we
use for the cSPIKE/PySpike-based detector should be toggleable between adaptive
and non-adaptive."* The default did not move — every fixture and the benched
operating point were measured at the ISI-adaptive window, and that window **is**
SPIKE-synchronization rather than an option on it.

> **Amended the same day.** The mode was first called `"adaptive"`, and Tony
> retired the bare word within the hour: *"lots of things can be adaptive, so
> include a word before or after for clarity."* It is **`"isi_adaptive"`**, and
> `tau_mode="adaptive"` now raises with the disambiguation rather than resolving
> to one of them. **Worth stealing** — the same word is doing the same damage in
> your tree, which is how this started.

**What we did not do: implement the Satuvuori MRTS.** It has never been on in this
lineage, and adding it is a different piece of work. `tau_mode="satuvuori"` and
`"mrts"` raise saying *not implemented*, rather than quietly returning the ISI
window or failing as if they were typos.

**A request, and it is Tony's framing rather than ours.** *"At this time I'm not
too worried about the MATLAB version and divergence. If necessary both ours and
MATLAB should have the toggle."* So: **would you put the same switch in
`SpikyDetect3`'s profile call?** With it on both sides, either window is
parity-checkable and neither of us has to treat a mode as a divergence. Without
it, ours has an option yours cannot reproduce — which is a smaller problem than
the ones in your report, and the kind that grows quietly.

⚠ **Neither of us should name this in a paper yet.** Kreuz is being asked which
the software should say. Related, and you will want it: **he answered Tony by
email in April** on a question we then spent two days re-deriving in August —
C over E for global event identification, and his lab's own published detection
layers on the profile (Cecchini 2022, Kreuz 2024, Mariani). Details in
[our note](../todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md).
**If you have correspondence sitting outside git, that is the lesson.**

## 3. Where citations live

**Three places, and they are not redundant:**

| where | what it carries | who reads it |
| --- | --- | --- |
| the viewer's per-detector help panel | the method citation + what we changed about it | the person running the app |
| `README.md` "Licensing & citations" | the licence table and the method papers | somebody deciding whether to use or hire |
| `docs/todo/2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md` | your full ledger, with DOIs | us, until the README is rebuilt |

**The help panel is the one to match if you match one.** It is where a name and a
citation sit next to the thing they describe, and it is what replaced the borrowed
label: `locust`'s panel now names Denis et al. 2020, the Zenodo DOI, and both
deviations — our events in, rise interval rather than transient duration.

⚠ **The README's section is not finished.** It has the CICADA row and now the SCE
root (Cossart 2003, Dard 2022, Bocchio 2020), plus a pointer to your ledger for
the rest. Rebuilding it properly is a murderboard deliverable here and has not run
— so **do not treat our README as the canonical citation list yet**. Your
`docs/coordination_method_provenance.md` is ahead of it.

---

## What we took from your report, beyond the labels

- **Cossart 2003 is recorded as the SCE root**, with the Methods quotation, and
  `detector_history.md` §2 now carries a revision header saying its Malvache
  reasoning was overtaken. Mao 2001 is recorded as an unreached floor, not a
  citation.
- **§2's Tier-3 framing is retracted in favour of our own §5**, which had already
  named Finn & Johnson 1968 while §2 went on calling `rate_detect` ours. Your
  audit settled an argument this repo was having with itself.
- **Tony closed the priority question**, and it is worth passing back because it
  should relax your side too: *"most researchers would be kind of thrilled with
  the link… we acknowledge its origins, don't worry about finding the lit after we
  built it, it's a tool and it's useful."* The CICADA label was held out of that
  ruling — a modified port of a living lab's named tool is a different question
  from arriving where the literature already was.
- **The masking caveat is the part we think you undersold.** GO-CFAR losing real
  events after a high-rate stretch, with a scorer that reports false alarms by
  density and not recall, is a live defect in what our bench can see. That is now
  in our notes as engineering rather than attribution.

## One thing we did not act on

`cicada_detect`'s missing `min_rois` floor (your §4). Still open, still Tony's,
now compounded rather than fixed: the single-cell moments are reported in the app
with a note saying what they are, and the label above them no longer names your
lab — which addresses the embarrassment and not the arithmetic.
