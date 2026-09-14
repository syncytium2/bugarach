---
status: done
filed: 2026-09-10
closed: 2026-09-14
---

# Nobody has read Gregers Hansen 1973, and it decides whose column is right

> ## Closed 2026-09-14: the origin is left unestablished, on purpose
>
> **Tony's ruling:** *"let's not replace origin, but discuss our attempt to find it. state what we
> know, what we don't know. and leave it at that"*. So the answer to the question in this file's
> title is *neither*, and the docs now say so:
> - `detector_history.md` **§4.1, Where greatest-of began** covers the searches tried, what three
>   shelf papers and one patent say, and what is not known. It is the authority now; this file and
>   `lit_needed.md` are not. The attribution cell for `maxlt` reads *origin not established*. The
>   murderboard run is [`reviews/greatest-of-origin_2026-09-14.md`](../reviews/greatest-of-origin_2026-09-14.md).
> - `GLOSSARY.md`, `README.md`, `learned/cfar_scope.html` and the withdrawn proposal's footer no
>   longer imply an origin. They point at §4.1.
>
> ⚠ **Two corrections to this file's own record:**
> - §4's column is headed **attribution**, not *origin*. The body below, `lit_needed.md` and the
>   2026-09-10 handoff all misquote it.
> - The "What that does to the dispute" paragraph in the revision below is **superseded**. It read
>   the memo's date as contradicting the talk, and proposed "the earliest published treatment" as a
>   replacement origin. The murderboard found the shelf does not support either: the 1980 paper
>   calls its authors' work *independent*, and Rohling 1983 credits a different proposer, Moore &
>   Lawrence 1980.
> - The 2026-09-10 review record ([roles 1–6](../reviews/2026-09-10-coordination-without-labels-roles-1-6.md),
>   row 4) says a reviewer *"confirmed independently"* that Hansen 1973 introduces greatest-of, with
>   pages 325–332. It names no source, and no source held that day gave those pages. Treat that row
>   as unsupported. The record itself is left as written.
>
> **Not done here, and still open:**
> - [the canonical surname](2026-09-10-the-canonical-surname-is-gregers-hansen.md). The new passage
>   keeps the document's *Hansen* form and names the canonical form once, so that change can land as
>   the rename it is.
> - [the follow-ups](2026-09-14-greatest-of-follow-ups.md) the review left: the darkroom copy of the
>   history page, the page builder's rendering, the shelf README, `maxlt`'s calibration, the other
>   attributions, and questions for Tony.
>
> Everything below is the record as it stood before the ruling.

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
