---
status: open
filed: 2026-08-30
---

# The first thirty seconds of this repo say Tony re-typed someone else's MATLAB, and a stranger published that

> **Not murderboarded** — a work item, not a deliverable. Every claim was re-verified
> against `main` at `0188362` on 2026-08-30 and the file:line is given for each.
> **If any of this reaches an outside reader as prose, murderboard that artifact.**

**Found from outside the repo.** A stranger read the four public repositories
adversarially while preparing a short-course page, concluded bugarach was *"a Python
re-typing of somebody else's MATLAB algorithms"*, and **published that before being
corrected.** The critique's finding was not that the repo lies. It is that the repo
**under-claims**, and the first screen hands a reader the misreading for free.

This is a **re-statement of the repo's own record**, not a new claim. Everything
below is already written down in [`docs/detector_history.md`](../detector_history.md),
which was compiled in 2026-08-22 from two interface2 reports plus Tony supplying the
half the reports could not: who wrote the originals.

## What the record says

| detector | what it actually is |
|---|---|
| `rate+context`, `CoactDetect`, `LoCo` | **Tony's** — designed for this preparation. `detector_history.md:11` |
| `SPIKE-synch` | the *measure* is Kreuz's; **the detector on it was written here**. `:19` |
| `binned SCE` | **not a port** — *"based on ideas in CICADA before we did the port"*, 18 days before it. `:29` |
| `locust` | **the** port, *"modified at port"*. `:27` |

**One of the six is a port.** Plus the learned detector and the whole
measure → simulate → train → detect loop, original, paper in preparation.

## What the front door says

| where | text | wrong how |
|---|---|---|
| `README.md:7` | *"bugarach **lifts six** coordinated-event detectors out of MATLAB"* | five of six were not lifted |
| `README.md:79` | *"**Six detector ports**"* — first row of **What is built** | same, in the summary table |
| `README.md:73–74` | interface2 *"is named here as the source of a port and never linked"* | true, and **says nothing about who wrote the originals** — the gap a stranger fills the ordinary way |
| `CITATION.cff:15` | *"Browser-based viewer and **Python ports of six** neural-coordination detectors (… locust …)"* | **the machine-readable one.** GitHub renders it in the *Cite this repository* widget and a citation manager reads it verbatim. It also names `locust`, which the public build withholds |

`README.md:79`'s own body then links to `detector_history.md` *"for which is which"* —
so the row title is wrong and the row defers the correction to another file. **The
summary is the part a reader keeps.**

## Why `CITATION.cff` is the highest-leverage line in the repo

It is the only one of the four that is **machine-readable, quoted verbatim by tools,
and rendered by GitHub in its own widget.** A wrong sentence in a README is read by
people who can also read the next paragraph. A wrong `abstract:` in a citation file
propagates into reference managers and bibliographies, where nothing sits next to it.

## Two traps for whoever writes the fix

1. **README and the site describe different detector sets, and both are right.** The
   README documents the whole repo — six. The public site **withholds `locust`** — five.
   So the attribution paragraph has to be **written twice**, not copy-pasted. Any prose
   quoting a count inherits this.
2. **It meets the count problem in the `<h1>`.** `tools/build_site.py:171` reads
   *"Six coordinated-event detectors ported from MATLAB"* — **wrong about the count and
   wrong about the word `ported`, in one sentence.** That is
   [`the site types what a token could substitute`](2026-08-30-the-site-types-what-a-token-could-substitute.md)
   item 3 and this item arriving at the same line. Doing them together beats sequencing;
   both sessions that looked at it reached that independently.

## Scope, and it is narrow on purpose

**This is a wording fix backed by an existing document.** It does not:

- re-derive who wrote what — `detector_history.md` settled that on 2026-08-22 with
  Tony's own input, and it is the authority;
- weaken the **port-fidelity** claim, which is real, checkable from a clone, and the
  thing that lets these stand in for the MATLAB originals — `README.md:79`'s body is
  careful about this and should survive intact;
- claim priority over CICADA, Kreuz, or anyone else. *"Written here on Kreuz's measure"*
  is the accurate form and is already the record's own phrasing.

The failure is one of **omission**, and the repair is to stop omitting.

## Provenance of this item

Handed over at the end of `bugarach-63`'s session on 2026-08-30, which found it and
reserved the branch name `who-wrote-these` **without filing anything**. It existed only
in cross-session messages and that reserved name — invisible to any later session — which
is why this file exists. That session did not start the work: Tony pulled it up for scope,
*"address this critique does not mean run wild."*

**The work is therefore not authorized by the existence of this file.** The paths are
free; the go-ahead is Tony's.
