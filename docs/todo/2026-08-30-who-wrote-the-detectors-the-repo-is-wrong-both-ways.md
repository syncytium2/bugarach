---
status: open
filed: 2026-08-30
---

# Who wrote the detectors — the repo is wrong in both directions, and the fix is smaller than it looks

> **Not murderboarded** — a work item. Verified against `main` at `0188362` and
> against interface2 at `c711e737` on 2026-08-30; file:line given for each claim.
> **If any of this reaches an outside reader as prose, murderboard that artifact.**

> ⚠ **REWRITTEN 2026-08-30, hours after filing.** This file was first called
> *"the repo underclaims its own authorship"* and that title was itself an
> over-claim. Tony then said *"we built the first version of loco and coact detect
> in matlab together"*, which makes the repo wrong in the **other** direction too.
> **Read [`docs/detector_history.md`](../detector_history.md)'s 2026-08-30 revision
> first** — it is the authority and it moved. The original framing survives only for
> the README/`CITATION.cff` half.

## The two errors, in opposite directions

**1. The front door under-claims.** It says the repo is six ports of other people's
MATLAB. It is one.

**2. The lineage doc over-claimed.** It said three detectors were Tony's alone. Two
of the three were built with AI sessions, and its independence-from-CFAR claim rested
on a mental state that is not available when a model is a co-builder. **Corrected
2026-08-30** — see that file's own revision block; this item does not restate it.

**The repair is not "claim more."** It is to say accurately what was written where,
and by whom, in both directions.

## Error 1 — what the front door says

| where | text | the problem |
|---|---|---|
| `README.md:7` | *"bugarach **lifts six** coordinated-event detectors out of MATLAB"* | **accurate about the mechanism** — six Python implementations were made from six MATLAB originals. It omits **whose** MATLAB, and that omission is the whole defect |
| `README.md:79` | *"**Six detector ports**"* — first row of **What is built** | reads as six ports of *other people's* methods. Its own body then links to `detector_history.md` *"for which is which"* — so the summary is wrong and defers the correction to a file nobody opens. **The summary is the part a reader keeps** |
| `README.md:73–74` | interface2 *"is named here as the source of a port and never linked"* | true, and **says nothing about who wrote the originals** — the gap a stranger fills the ordinary way |
| `CITATION.cff:15` | *"Browser-based viewer and **Python ports of six** neural-coordination detectors (… locust …)"* | **the machine-readable one.** GitHub renders it in *Cite this repository*; citation managers quote it verbatim, where no next paragraph sits beside it. Also names `locust`, which the public build withholds |

⚠ **The word "port" is doing two jobs and the README conflates them.** (a) MATLAB →
Python, a code path, true of nearly all of them. (b) Someone else's method → this lab,
an intellectual path, true of **one**. A reader sees (b) and the repo means (a).

**The first version of this file got that wrong**, saying *"five of six were not
lifted."* They were lifted — mostly out of Tony's own MATLAB. Omission, not error.

## What the record actually supports, with its caveats attached

From [`detector_history.md`](../detector_history.md), **including** its 2026-08-30
revision. These caveats are load-bearing and belong wherever the correction is
written, not in a footnote:

| detector | origin | caveat that must travel with it |
|---|---|---|
| `rate+context` | designed here; commit body states it in Tony's terms — *"excess = primary rate (1s) − context rate (60s)"* | **AI-assisted commit** (2026-05-13). 08-24 also calls it cell-averaging CFAR |
| `CoactDetect` | built here | **built with AI sessions** — Tony, 2026-08-30 |
| `LoCo` | built here | **built with AI sessions.** `maxlt` is GO-CFAR (Hansen 1973); percentile-of-pool is kin to OS-CFAR |
| `SPIKE-synch` | Tony's detector on Kreuz's measure | **"Not novel either"** — Kreuz's own lab published the same two-knob detector (Kreuz et al. 2022) |
| `binned SCE` | **not a port** | published root is **Cossart 2003, from Yuste's lab**, predating CICADA |
| `locust` | **the** port, modified at port | the one case where "port" means (b) |

**So the honest correction is narrow: say who wrote the MATLAB originals.** It is
**not** "these are novel", and for two of the six the record says the opposite.

## Two traps for whoever writes it

1. **README and the site describe different detector sets, and both are right.** The
   README documents the repo — six. The public site **withholds `locust`** — five. The
   attribution paragraph is **written twice**, not copy-pasted.
2. **It meets the count problem in the `<h1>`.** `tools/build_site.py:171` reads
   *"Six coordinated-event detectors ported from MATLAB"* — **wrong about the count and
   wrong about "ported", in one sentence.** That is
   [the site types what a token could substitute](2026-08-30-the-site-types-what-a-token-could-substitute.md)
   item 3 meeting this item at the same line. Both sessions that looked reached that
   independently; doing them together beats sequencing.

## Scope

**A wording fix backed by an existing document**, now that the document is correct.
It does not re-derive who wrote what, does not weaken the **port-fidelity to 1e-9**
claim (about code, not ideas — `README.md:79`'s body is careful and should survive
intact), and claims priority over nobody. Tony closed priority on 2026-08-24:
*"most researchers would be kind of thrilled with the link … it's a tool and it's
useful."*

## Provenance

Handed over at `bugarach-63`'s session end on 2026-08-30, which found it and reserved
the branch name `who-wrote-these` **without filing anything** — it existed only in
cross-session messages and a name that was never cut. That session did not start the
work; Tony pulled it up for scope: *"address this critique does not mean run wild."*

**The existence of this file is not authorization.** The paths are free; the go-ahead
is Tony's.

The outside critique that started it: a stranger read the four public repos
adversarially for a short-course page, concluded bugarach was *"a Python re-typing of
somebody else's MATLAB algorithms"*, and **published that** before being corrected.
That critique was right that the front door misleads. It did not know about error 2.
