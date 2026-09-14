---
status: open
filed: 2026-09-10
---

# Nobody has read Gregers Hansen 1973, and it decides whose column is right

> ## Revision, 2026-09-14: nobody will read it, so the question changes
>
> **The library job is off.** Tony, 2026-09-14: the paper *"resolves only to a conference listing"*,
> and he can find no documentation of what was in the talk. The closing condition below, *someone
> reads the paper*, can no longer be met.
>
> **The shelf already held what can be known**, and nobody had searched it for this question. Full
> quotes and sources are in [`lit_needed.md`](../lit_needed.md), in the Gregers Hansen entry:
> - **Gregers Hansen & Sawyers 1980, §I**, citing the talk as its reference [1]: the talk gave *"a
>   simple rule for determining the detectability loss"* of cell-averaging CFAR with greatest-of
>   selection. So by its author's own account the talk **treated** greatest-of.
> - **The same paragraph cites J.H. Sawyers's Hughes Aircraft internal memo of 15 February 1972**,
>   an exact analysis of the *"'Split' mean level threshold detector"*. That is twenty months before
>   the talk.
> - **Gandhi & Kassam 1988** say Hansen *"proposed"* greatest-of, cite the talk as its reference
>   [9], and supply the **325–332** page range. That list is the only source for the pages.
> - **Rohling 1983** credits greatest-of to the 1980 paper, not to the talk.
>
> **What that does to the dispute:** neither column is right as an *origin*. The 1973 talk is
> contradicted by the 1972 memo; Hansen & Sawyers 1980 is contradicted by its own citation of the
> talk. What the published record supports is **the talk as the earliest published treatment of
> greatest-of that any paper on the shelf cites**, with its proposal credited by Gandhi & Kassam 1988, and **Gregers
> Hansen & Sawyers 1980 as the loss analysis**.
>
> **Now closes when** Tony rules on the wording for `detector_history.md` §4's attribution column,
> `GLOSSARY.md` (*"GO-CFAR (Hansen 1973)"*), `README.md` (*"the origin"*) and `detector_history.md`
> near line 204. All three are outside-reader documents, so the edit goes through the murderboard.
> Do it together with [the surname fix](2026-09-10-the-canonical-surname-is-gregers-hansen.md), since
> it touches the same lines. The body below is kept as written.

> **A library job.** ~~Every online route is exhausted; this needs a physical or institutional copy.~~
> Superseded 2026-09-14; see the revision above.

## The dispute

`GLOSSARY.md` and `README.md` cite **Gregers Hansen 1973** as the origin of greatest-of CFAR — the
lineage behind LoCo's `maxlt`. [`detector_history.md`](../detector_history.md) §4 instead puts
**Gregers Hansen & Sawyers 1980** in a column headed *origin*, and marks it read-in-full. Two
murderboard roles came out on opposite sides on 2026-09-10.

The shelf holds the 1980 paper. It does not hold the 1973 one, so the question cannot be closed from
what we have.

## What is established

- **The paper is real and its title is confirmed.** The volume's own contents listing is on the shelf
  at `radar/iee_conf_105_1973_CONTENTS_ONLY.pdf` — IEE Conference Publication 105, *Radar — present
  and future*, 23–25 October 1973, Savoy Place, London — and reads
  *"GREGERS HANSEN,V.: Constant-false-alarm-rate processing in search radars"*.
- ⚠ **Our claimed page range `325–332` appears in no source we hold.** Treat it as unverified.
- **The chronology leans toward 1973 without establishing it.** From the IEEE author profile
  (`radar/gregers_hansen_AUTHOR_PROFILE_ieee.pdf`) and OpenAlex: 1971 *Siebert and Dicke-Fix CFAR
  Radar Detectors* → 1972 *Cell Averaging LOG/CFAR Receiver* → **1973** → 1980 *Detectability Loss
  Due to "Greatest Of" Selection in a Cell-Averaging CFAR*. A 1980 title that **costs** a technique
  presupposes it exists. That is titles, not papers, and it is equally consistent with GO
  originating in the 1971 or 1972 papers, which we also do not hold.

## Routes already exhausted — do not redo these

- **IEEE Xplore does not index it.** It is an **IEE** (British) conference publication; the author
  profile jumps 1972 → 1974. Xplore also answers a fetch with HTTP 418 and a CAPTCHA.
- **OpenAlex has the record** but with no DOI and a garbage venue field (*Medical Entomology and
  Zoology*), so it confirms existence and year and nothing else.

## Closes when

Someone reads the paper and rules on whether it introduces greatest-of selection. Then
[`detector_history.md`](../detector_history.md) §4's column is either confirmed or corrected — and
the page range gets a source. Related, and separately actionable now:
[`the canonical surname is Gregers Hansen`](2026-09-10-the-canonical-surname-is-gregers-hansen.md).
