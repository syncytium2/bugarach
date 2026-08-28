# Deploy notes 2 — the live page is wrong about another lab, and the fix is queued behind the hold

**Companion to [`2026-08-28-what-351-changes-under-the-deploy.md`](2026-08-28-what-351-changes-under-the-deploy.md),
which covers `53b1d62`.** Between them the two notes cover three of the four queued
commits. That companion landed as **PR #361** at 18:18 on 2026-08-28, so the link resolves;
it was still open when this note was drafted, and the caveat saying so has been removed
rather than left to age. **This one leads with a decision rather than a description**, because unlike
#351's changes, one of these is already doing harm on the public internet.

This does **not** lift, amend or duplicate [`docs/DEPLOY_HOLD.md`](../DEPLOY_HOLD.md).
That file owns the hold and deliberately keeps no list of what is queued, because
`tools/site_staleness.py` computes it. This surfaces one judgement the hold's own text
says is a person's to make.

---

## ⚠ Read this first: the hold's escape clause may apply

**`bugarach.tonydefazio.com` right now tells readers that `locust` IS CICADA's method.**
Fetched from the live page, 2026-08-28:

> *"The lane marked locust **is CICADA's method**, ported from the Cossart lab's
> implementation and modified"*

and, four sentences later in the same paragraph:

> *"**No method from the literature has yet been run on this project's recordings**"*

Both are bold on the page. **They cannot both be true**, and the first one is not
supported by anything in either repo:

- `tools/matlab_ref/gen_ref_cicada.m` builds the parity fixture by running **interface2's
  own `generate_sce_cicada`**, so the 1e-9 result validates bugarach against interface2
  and says nothing about CICADA. Neither repo contains any comparison against the Cossart
  source; the word "faithful" is an assertion in both.
- It is a **documented partial port**. `generate_sce_cicada.m`: *"we already have events,
  so their per-cell transient-detection step is skipped."*
- interface2 **parked** that function in `f55643bf` for over-detecting on this
  preparation's long SLOW transients.

**Why this is not merely untidy.** Locust is the detector that fires 85 times (35 after
retune) on a decoy block built to catch a detector keying on activity rather than
coordination. Those numbers are on the same page. A reader who joins them to the bold
claim concludes **CICADA is promiscuous** — a result about our modified port, attributed
to another laboratory, on a page written for outside readers.

`DEPLOY_HOLD.md` anticipates exactly this and does not make it the deploy session's call
to route around:

> *"If a deploy genuinely cannot wait — a wrong number on a public page, a broken link,
> anything actively misleading a reader — that is not a hold to route around silently, it
> is a reason to say so and lift the hold deliberately."*

**So: raise it, do not act on it.** `ed5e02e` is the fix and it is queued. Whether it
rides the plumbing or goes early is Tony's decision and it should be recorded either way.
This note exists so nobody discovers the choice at deploy time.

**One line in `DEPLOY_HOLD.md` reads as reassurance and should not.** It says *"the
2026-08-27 status banners and the CICADA attribution are **already live** — they went out
at `0ed939d` before the hold existed."* That is factually correct and easy to read as
*settled*. What went live at `0ed939d` is the version this note is about.

---

## What is queued, and who owns each piece

`python tools/site_staleness.py` is the authority. **Run it; do not read a total off this
page.** The commit count behind `main` moves every time anything lands — it went 33 → 35
during the twenty minutes this note was being written — and a handoff quoting it is stale
before it is read. What is stable, and what the table below is for, is **which** commits
change what the site serves:

| commit | what it touches | covered by |
|---|---|---|
| `ed5e02e` | `tools/build_site.py` → the front page's prior-art paragraph and figure caption | **this note** |
| `173accd` | `docs/site/raster_viewer.html` — **222 insertions**, learned rows joining the table | *not covered — its author should add notes* |
| `f7c0edb` | `docs/site/raster_viewer.html` — 12 lines, an empty-state message when no trainer runs | *not covered — same* |
| `53b1d62` | `docs/site/raster_viewer.html` — sweep autofill, `beforeunload`, loop scheduling | [`…what-351-changes…`](2026-08-28-what-351-changes-under-the-deploy.md) |

**The coordination fact worth more than any single row: three separate sessions have
edited `docs/site/raster_viewer.html` since the last deploy.** `53b1d62`, `173accd` and
`f7c0edb` land together, and none of the three was tested against the other two. The
viewer that ships is a combination no session has driven.

## What `ed5e02e` changes, exactly

**Prose on one page. No viewer, no figure, no code the build reads beyond
`build_site.py`.** The diff is 35 lines in `build_site.py`, of which the two rewritten
passages are the whole content change; the rest of the commit is a murderboard run record
and an unrelated todo, neither of which the build reads.

Two passages:

1. **The prior-art paragraph.** *"is CICADA's method"* → *"is **derived from** CICADA's
   method"*, ported from **an older version** of their implementation. A second paragraph
   is added naming the two deviations (the skipped transient-detection stage, the replaced
   active-duration model) and stating that the chain is **checked only at its last link**.
   It closes: *"So locust's results on this page are a result about locust, not about
   CICADA, and no method from the literature has been run here in its own form"* — which
   also retires the self-contradicting sentence.
2. **The figure caption's name key.** *"locust is the CICADA method"* → *"locust is
   derived from the CICADA method"*, plus the two deviations in a clause.

**Nothing else on the page moves.** Citations are unchanged and were verified: Zenodo
`10.5281/zenodo.10041434` is CICADA v1.0.3, five named authors, 20 July 2020, CC-BY-4.0.

## What the pre-flight should do for this commit

Cheap and mechanical — this is prose, so the checks are string-level:

```bash
python tools/build_site.py
grep -c "is CICADA's method" site/index.html                       # expect 0
grep -c "No method from the literature has yet been run" site/index.html   # expect 0
grep -c "derived from CICADA's" site/index.html                    # expect 1
```

Then **read the paragraph on the served page, not from `file://`** — the front page is one
of the pages that was found to differ over HTTP, and `docs/deploy.md` is emphatic about
it. The paragraph is longer than what it replaced; confirm it has not pushed the
`The full landscape →` link or the section below it into an awkward break at narrow
widths.

**Do not re-check the attribution wording itself at deploy time.** It was murderboarded
(11/11 roles, 2 rounds, record at
[`docs/reviews/locust_attribution_2026-08-28.md`](../reviews/locust_attribution_2026-08-28.md))
and re-litigating it in a deploy window is how a correct fix gets softened by someone in a
hurry.

## What this note does not know

- **`173accd` and `f7c0edb` are not mine** and are not described here beyond their diffstat.
  222 insertions into the viewer is not a footnote; whoever wrote it should add a note like
  #361's or say plainly that none is needed.
- **The viewer has not been driven with all three changes present.** See above.
- **Whether the attribution fix justifies lifting the hold.** Raised here, decided elsewhere.

## One thing that is not about the deploy but will reach it

A worktree's `pytest` imports the **primary checkout's** `src`, because the venv holds one
editable install and the two are rarely at the same commit. A green suite in a worktree
can mean the tests passed against another branch's code — and it already corrupted two
reported test counts on 2026-08-28. Filed as
[`docs/todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md`](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md).

It matters here because **"the suite was green before we deployed" is one of the sentences
this hazard can make untrue**, and a deploy is exactly when somebody says it. Run
pre-deploy checks from the primary checkout, or with `PYTHONPATH=$PWD/src`.

## Provenance

Written 2026-08-28 by the session that made `ed5e02e`, at Tony's request — *"prepare a doc
called deploy notes 2 for the deploy session that is waiting on a few things still in
flight."* The live-page quotes were fetched from `bugarach.tonydefazio.com`, not
reconstructed from the repo. The queued list came from `tools/site_staleness.py` rather
than being hand-kept, for the reason `DEPLOY_HOLD.md` gives: a second copy of "what is
pending" goes stale.
