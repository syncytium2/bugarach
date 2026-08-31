---
status: in-progress
filed: 2026-08-11
---

# File the PySpike max_tau bug upstream

## KREUZ ANSWERED 2026-08-31. It is a regression, the fix is endorsed, and the route is a PR.

**The question this whole file was waiting on is settled, and it went the way the report
assumed.** Thomas Kreuz replied to the note three days after Tony sent it, with Mario Mulansky
cc'd from the first line — *"I put Mario in cc to alert him already of your upcoming PR."*
What he settled, in the order it matters:

- **He reproduced it himself, on his own example**, and got our numbers. Two trains,
  `[0 1 3 5 7 9]` and `[0 1.1 3.2 5.3 7.4 9.5]`, so the pairs are separated by 0, 0.1, 0.2,
  0.3, 0.4 and 0.5. In cSPIKE `max_dist=0.25` gives 0.5 — the first three pairs match — and
  `max_dist=0.35` gives 2/3. **PySpike returns 5/6 for both.** His reading of why is the
  report's: *"only the last spike pair is not matched, for all other pairs max_tau is ignored
  (or overwritten). So it indeed seems that we just forgot to track tau_max within the new
  get_tau function in v0.8.0."* That is an independent reproduction by the measure's senior
  author, arrived at from the same code without our fixture, and it names 0.8.0 unprompted.
- **The fix is endorsed as written:** *"So this should clearly be fixed and I am happy with
  your suggested correction. Please go ahead with sending the PR to Mario."*
- **A hard τmax is the semantics PySpike should have.** This is the answer the note actually
  asked for, and it disposes of the alternative the file has been hedging against since
  2026-08-23. His group's standing philosophy is *"to give the user options and not impose one
  specific variant over any other"* — the parameter-free measure stays the default, the
  adapted variants stay easily reachable. So τmax is an option that must work, not a default
  that was withdrawn.
- **The review's silence was space, not a verdict.** Kreuz confirms the omission from
  [arXiv:2510.07140](https://arxiv.org/abs/2510.07140) was an editorial constraint — the
  agreement was to present the basic ideas and example applications and leave details to the
  original papers, so MRTS appears only in passing and τmax *"isn't even mentioned at all."*
  Against that: *"we use it in the 2017 paper and again quite a lot in the two recent latency
  correction papers"*, and **Fig. 11 of Mariani et al. 2025 shows explicitly what the
  parameter changes.** *"So for sure it should be included and of course work correctly in
  PySpike as well."*

**The one complication the note raised itself is therefore closed**, and closed in the
direction that makes the report stronger rather than weaker. The 2026-08-23 check that found
the review carrying neither τmax nor MRTS, and the decision to ask rather than assert, did
exactly the work it was supposed to do: it surfaced the objection before a maintainer could,
and the answer came back with a figure reference we did not have.

### What changed in the plan

**Kreuz redirected step 2 from an issue to a PR.** The file's plan was: note → issue → offer a
PR. He read the note's closing offer and skipped the middle, and he alerted the maintainer
before we wrote anything. That is his call to make on his own project, and it is the faster
route. **The issue body is not wasted** — it is the reviewed 12 KB of mechanism, and it becomes
the PR description. See **Route** below for what that costs and the one thing to decide.

**What did not change:** the patch, the numbers, or the report's shape. Re-verified today
against `docs/pyspike_max_tau.patch` on a fresh v0.9.0 build —
`bash tools/pyspike_patch_check.sh` — upstream's suite is 50 green as shipped, patched on the
pure-Python backend, and patched on the compiled one; the sweep is
0.3500/0.1833/0.0500/0.0000; the 7.7 s pair stops being coincident under a 0.25 s cap.
**And the patched build reproduces Kreuz's own cSPIKE figures to the digit** — 0.500000 at
`max_dist=0.25`, 0.666667 at 0.35, against his 0.5 and 2/3. That is the single strongest line
available to the PR, because it is upstream's code, patched, landing on the reference
implementation's values on an example the maintainer's collaborator chose.

### One thing his reply does not answer

The report closes with a design question — *"with `MRTS > 0` this lets `max_tau` override the
MRTS-raised window"* — and Kreuz did not address it, almost certainly because the note left the
mechanism to the issue and never put it in front of him. His options-not-impositions answer
implies a hard cap should win over a raised floor, but that is our inference, not his sentence.
**Leave it in the PR as the open question it is.** Do not upgrade it to "Kreuz confirmed".

### Not to be re-raised

His reply also describes his staffing and some unreleased work. **None of it is quoted here or
anywhere in this public repo, and it should not be.** The sentences above are the ones he wrote
to be acted on. The full mail is in Tony's inbox; filing it durably is Tony's call.

---

Two things a later reader would otherwise get wrong:

- **The "adaptive" question did not go with it, and it is no longer Kreuz's to answer.**
  The note went without that paragraph, and Tony then **closed the question himself**
  (2026-08-28): in MATLAB the cSPIKE-based detection could be adaptive or non-adaptive,
  we ported the non-adaptive state, and if a toggle is ever wanted it is placed inactive
  in the state that reflects the port. He rated it minor against finishing the pipeline,
  and **no code changed**. So do not re-raise it with Kreuz and do not wait on him for it.
  The block below is the version that was live until then, kept because
  [the April todo](2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md)
  planned around it.
- **The ride-along is spent.** That todo's item 2 says *"These are one email, not two"* —
  which was true while the mail was unsent and is not now. Anything still wanted from
  Kreuz needs its own mail or a reply to this thread.

> **Superseded 2026-08-28 — the version that was live until the mail went.** A second
> question for the same mail appeared on 2026-08-24, and it was not
> drafted. Kreuz replied to Tony in April on a different subject, and that reply
> raised one thing only he can settle: **whether this port should keep calling its
> profile "adaptive"**, given that interface2's cSPIKE wrapper passed Satuvuori's
> adaptive time-scale argument as 0 while calling the code path adaptive — the
> word is now in `sync.py`, the glossary and the served viewer page. The argument
> is in [what Kreuz answered in April](2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md).
> **Deliberately not written into the note here**: that draft was reviewed as it
> stands, and a paragraph added without review is the failure this repo's document
> process exists to stop. Whoever sends the mail decides whether to fold it in, and
> drafting it is its own reviewable act.

1. ~~**Send the note**~~ — **DONE 2026-08-28**, [`docs/kreuz_note.md`](../kreuz_note.md)
   sent as drafted.
2. ~~**Then file the issue**~~ — **superseded 2026-08-31.** Kreuz asked for the PR instead
   and cc'd Mulansky. See **Route**.
3. **Open the PR against `mariomulansky/PySpike`** — the patch is
   [`docs/pyspike_max_tau.patch`](../pyspike_max_tau.patch), the description descends from
   `python tools/pyspike_issue_body.py`, and it needs the two additions in **Route** below.
   **Tony releases it**; the Process section's rule that external communication is his to send
   did not change because the destination did.
4. **Then** put the PR URL in the eight places listed at the bottom of this file. The version
   half of that pass is already done. The list says "issue URL" throughout — it is now a PR
   URL, and the eight places are the same eight.

~~If Kreuz answers that 0.8.0 dropped the clamp deliberately, stop and re-read before filing:
the report becomes a docs bug and most of it comes out.~~ **He answered the other way**
(2026-08-31): a regression, fix endorsed, cap wanted. This contingency is spent.

## Route — issue, or straight to the PR

**Kreuz asked for the PR, so the PR is the route.** What it costs, said plainly so nobody
re-opens it as a mistake: a PR description is read by people deciding whether to *merge*, and
this one is 12 KB of triage material aimed at someone deciding whether to *believe*. Most of
that weight was carrying the burden of proof against a maintainer who had never heard of the
problem. **That burden is gone** — the senior author reproduced it independently, named 0.8.0
himself, and told Mulansky it was coming.

So the description is the reviewed body, with two changes and no rewriting of what the
murderboard already passed:

- **Lead with Kreuz's confirmation and his example, not ours.** His two trains are six pairs
  at 0.1 s steps and the expected answers are exact fractions a reader checks in their head —
  strictly better as an opener than our 40.4/77.3/534.4 construction, which exists only to
  manufacture an interior spike. Keep ours; it is the one that shows the *mechanism*, and the
  ISI arithmetic under it is what makes the cause legible. Kreuz's goes first because it is
  the one Mulansky's collaborator already agrees with.
- **Add the row that closes it:** patched PySpike returns 0.500000 and 0.666667 on that
  example, against cSPIKE's 0.5 and 2/3. Reference implementation and patched code, same
  numbers, on an example neither of us chose to flatter the patch.

**What to cut, if anything:** the seven-row provenance table is the piece whose job was
persuasion, and Kreuz's *"we use it in the 2017 paper and again quite a lot in the two recent
latency correction papers"* now does that job in one sentence with better authority. It is
still the clearest statement of where the cap comes from, and it is cheap. **Recommend keeping
it** and adding Mariani et al. 2025 Fig. 11 to it — Kreuz points at that figure as the explicit
demonstration of what the parameter changes, and the table currently stops at 2017.

**The PR needs a regression test**, which the issue did not. Upstream's suite has exactly one
`max_tau` assertion (`test/test_distance.py:184`) and it cannot catch this — its one-spike
partner train keeps the cap live, which is why the bug shipped for three years. Kreuz's example
is the natural test: two trains, three caps, exact expected values, no fixture. Our own
[`test_pyspike_max_tau_is_still_inert`](../../tests/test_sync_detect.py) is the inverse — it
asserts the bug is *present* in the installed PySpike, so it goes red the day this merges and
a release ships. That is intended, and it is the trigger for step 4.

**A PR description is a document deliverable, so it goes through
[`/murderboard`](../doc_review_process.md) before it is sent** — the issue body was reviewed as
an issue, and the two additions above plus the reordering are new text nobody has reviewed.

---

Report to PySpike (`mariomulansky/PySpike`) that its `max_tau` coincidence-window
cap has no effect: in the MRTS-era `get_tau`, the cap enters only as the default
for missing edge-neighbor ISIs — whenever all four surrounding ISIs exist,
`max_tau` is ignored, so spikes seconds apart count as coincident under a 0.25 s
cap.

**Verified unreported as of 2026-08-11** (searched their tracker: no issue
touches the cap — closed #14 mentions `max_tau`, but as a units question). **Re-verified 2026-08-17**: still nothing on the tracker (#88,
interval edges, is the only open *issue*; #85 and #47 are open pull requests), and
`master`'s `cython_get_tau.pyx` still has no final clamp — `max_tau` survives only
as a seed that any interior spike overwrites. 0.9.0 is the newest version on PyPI
and exists upstream as the `v0.9.0` tag (PR #87, 2026-05-11); GitHub's Releases
page still tops out at 0.8.0.

**The regression is older than the draft first said.** 0.7.0 carried three
separate Cython copies of `get_tau`, each ending with
`if max_tau > 0.0: m = fmin(m, max_tau)`. 0.8.0 — the MRTS release, on PyPI
2023-07-14 — consolidated them into one shared `cython_get_tau.pyx` and dropped
the clamp from all three at once. So the cap has been inert for over three years
counting from that release, not since 0.9.0. Don't date it from the GitHub
*Releases* entry, which reads 2023-10-13 — three months late, because the tag was
only pushed after issue #71 asked for it. The tag itself is lightweight, so it
carries the July commit date and gives the right answer.

## Process

Draft the issue text below; **Tony reviews before anything is posted or sent**
(external communication). After filing, add the issue URL here and flip status.

**Kreuz first, then the tracker — and it worked.** Tony corresponds with Thomas Kreuz
directly, which beats a tracker that has gone three months without a maintainer comment.
Kreuz is senior author on the measure papers, maintains cSPIKE — where the same
parameter lives as `max_dist` — and works with Mulansky. So there are two
artifacts here and they are not the same document: a short note to Kreuz, which
asks the one question only he can settle (is a hard `τmax` still the semantics
PySpike should have?), and the issue, which carries the mechanism. Send the note
first; if he confirms it is a regression, the issue files itself with his answer
behind it. If he says 0.8.0 dropped the cap on purpose, the report changes shape
entirely — it becomes a docs bug — and we will have learned that in private
rather than in public.

> **Outcome, 2026-08-31 — keep this paragraph, it is the reason there is anything to send.**
> The private route returned a confirmation, an independent reproduction, an endorsement of
> the patch, a settled answer on the semantics, and the maintainer already cc'd — in three
> days, from a tracker that would have offered none of it. It also cost the tracker step
> entirely: Kreuz asked for the PR directly, so the "then the tracker" half never ran. A
> later session choosing between a cold issue and a mail to the person who wrote the measure
> has a data point here.

**Before posting**: done — the branch landed as `6eafdb6` and all three repo links
(fixture, `sync.py`, `test_sync_detect.py`) are pinned to that SHA, so they keep
showing the tree the report describes, including
`test_pyspike_max_tau_is_still_inert`.

**The note is a file you open and copy**: [`docs/kreuz_note.md`](../kreuz_note.md),
written unwrapped and without backticks so it goes straight into a mail client.
No tool, no command — it is one page a person edits in the mail anyway, and
putting a script in front of it was friction invented for no reason (Tony,
2026-08-23).

**The body does need the tool**, because it is 12 KB of fenced blocks and
tables, and this file is hard-wrapped near 80 columns while GitHub turns every
newline in an issue body into a line break — so pasting the source ships each
paragraph as a stack of ragged lines. `gh` wants a file anyway. **The destination changed on
2026-08-31 from an issue to a pull request** (see **Route**); the body and the tool did not,
so this is the same command with a different verb:

```bash
python tools/pyspike_issue_body.py > /tmp/pyspike_pr.md
gh pr create --repo mariomulansky/PySpike \
  --title "$(python tools/pyspike_issue_body.py --title)" \
  --body-file /tmp/pyspike_pr.md --head <fork>:restore-max-tau-cap --base master
```

The fork does not exist yet and neither does the branch — nothing has been pushed anywhere
outside this repo. Creating a public fork is itself an external act, so it waits for Tony
with the rest.

Rendered through GitHub's own markdown API, the issue body comes out as 2 tables
(12 rows, all three cells wide), 10 code blocks, 7 links and no stray
backslashes. The rows, links and backslash count are the murderboard's final
numbers; the code-block count is three lower because the 2026-08-23 shortening
cut three listings.

---

## Note for Thomas Kreuz

**The note itself lives in [`docs/kreuz_note.md`](../kreuz_note.md)** -- one copy,
paste-ready, no second version here to drift out of step with it.

Why it exists and what it deliberately leaves out: Kreuz is senior author on the
measure papers, he maintains cSPIKE, and Mulansky is his long-time collaborator,
so a mail to him reaches the people who can settle this faster than a tracker
that has gone three months without a maintainer comment. The note stays short on
purpose. It establishes only that the cap is a real parameter and that PySpike
lost it, then asks the one question that is genuinely his: is a hard tau_max
still the semantics PySpike should have? The mechanism -- the reproduction, the
arithmetic, the provenance table, the patch -- belongs in the issue below, and
would bury the question if it went in the mail.

If he answers that 0.8.0 dropped the clamp deliberately, the issue changes shape
before it is ever filed: it becomes a docs bug, and most of what follows comes
out.

### Is PySpike stale because the group moved to another stack? No (checked 2026-08-23)

Tony asked before sending, which was the right question. It is not stale, and the
evidence says so four ways:

- **Kreuz published a sole-author review of exactly these measures on 2025-10-08
  and revised it on 2026-07-28** — three weeks before this check
  ([arXiv:2510.07140](https://arxiv.org/abs/2510.07140)). Live work, not a closed
  chapter.
- **That review names SPIKY, PySpike and cSPIKE as the three implementations**,
  each with a footnote URL, and says all three "will soon also include the various
  algorithms for latency correction". PySpike is in his forward plans, so there is
  no successor stack the conversation should be aimed at instead.
- **Mulansky is still maintainer and still active**: he authored and merged both
  the packaging modernization (#86) and the v0.9.0 release (#87) himself on
  2026-05-11. PyPI independently confirms the two dates the report leans on —
  0.8.0 on 2023-07-14, 0.9.0 on 2026-05-11.
- **Kreuz commits to the PySpike repo directly** (docs and website updates,
  2023-06). He is not an outsider asking a favour there; he can act on his own
  answer.

**The check turned up a real complication, and the note now carries it.** That
review defines the coincidence window as the minimum of the four surrounding
half-ISIs with **no upper bound**, and mentions neither τmax nor the MRTS
anywhere — verified by grepping the paper's own text, not by trusting a summary of
it. That is not a retraction: a review of the measures need not carry the
software's optional parameters, and MRTS is missing from it too while nobody
thinks MRTS was withdrawn. But it does mean the note cannot treat "τmax is the
intended semantics" as settled, and the version that goes out says so in as many
words. Raising it ourselves is stronger than having it raised back at us, and it
turns a leading question into a real one.

**A later session revisiting this should re-read that paper first.** It is the most
recent statement of what these measures are, it postdates every other source the
report cites, and it is the reason the note asks rather than asserts.

---

## Draft issue text (for review — not yet posted)

**Title:** `max_tau` has no effect except at spike-train edges (regression since 0.8.0)

### Summary

`spike_sync` returns the same number for `max_tau` of 1.0, 0.25 and 1e-6 on
trains whose mean ISI is about 10 s. A 1 µs coincidence window should report no
coincidences at all; it reports SPIKE-Sync 0.33.

In `get_tau`, `max_tau` is only the initial value of each of the four
neighbouring ISIs, and each is overwritten as soon as that neighbour exists. The
window returned is the minimum of the interpolated half-ISIs, and `max_tau` is
never compared against it. Only spikes at the start or end of a train — where a
neighbour is genuinely missing — still see the cap.

The docstring still promises otherwise:

> `max_tau` — Maximum coincidence window size. If 0 or `None`, the coincidence
> window has no upper bound.

### Smallest reproduction

```python
import pyspike

# The middle pair is 7.7 s apart. The outer spikes exist only to give that
# pair a neighbor on each side -- that is what triggers the bug.
a = pyspike.SpikeTrain([40.4, 77.3, 534.4], (0, 600))   # seconds
b = pyspike.SpikeTrain([58.8, 85.0, 300.0], (0, 600))   # seconds

x, y = pyspike.spike_sync_profile(a, b, max_tau=0.25).get_plottable_data()
for t, c in zip(x, y):
    print(f"t={t:6.1f}  coincident={c:.0f}")
```

```
t=   0.0  coincident=0
t=  40.4  coincident=0
t=  58.8  coincident=0
t=  77.3  coincident=1
t=  85.0  coincident=1
t= 300.0  coincident=0
t= 534.4  coincident=0
t= 600.0  coincident=0
```

Two spikes 7.7 s apart are coincident under a 0.25 s cap. The arithmetic, all of
it from the ISIs surrounding that pair (spacing not to scale):

```
train a:    40.4 ─────── 77.3 ────────────────── 534.4
train b:         58.8 ─────── 85.0 ── 300.0

pair under test:  a@77.3 vs b@85.0                       gap = 7.7 s
surrounding ISIs: 36.9 (a), 457.1 (a), 26.2 (b), 215.0 (b)
window returned = min(36.9, 457.1, 26.2, 215.0) / 2    = 13.1 s
max_tau                                                = 0.25 s  <- never consulted

7.7 s < 13.1 s  =>  coincident
```

### The cap is inert across six orders of magnitude

```python
import numpy as np, pyspike

rng = np.random.default_rng(0)
edges = (0.0, 600.0)                       # seconds
a, b = (pyspike.SpikeTrain(np.sort(rng.uniform(*edges, 60)), edges)
        for _ in range(2))                 # mean ISI ~10 s

print(" max_tau   SPIKE-Sync")
for max_tau in (None, 1.0, 0.25, 1e-6):
    print(f"{str(max_tau):>8}   {pyspike.spike_sync(a, b, max_tau=max_tau):.4f}")
```

```
 max_tau   SPIKE-Sync
    None   0.3500
     1.0   0.3333
    0.25   0.3333
   1e-06   0.3333
```

The `None` row differs, but not because the cap works on the body of the trains:
it comes from the spikes at each end, the only ones where a missing neighbour lets
the default survive. Sweeping `max_tau` densely finds exactly one transition, at
the 1.2680583 s gap between the last pair — below it every positive value returns
0.3333, above it the uncapped 0.3500. (`max_tau=0`, like `None`, means no cap.)

A pair must be interior in *both* trains before all four defaults are overwritten,
so the cap still works on trains too short to have an interior spike. That is why
the suite does not catch this: its one `max_tau` assertion
(`test/test_distance.py:184`) scores a three-spike train against
`SpikeTrain([2.1], 4.0)`, and the one-spike partner keeps the cap live. The fix
below leaves that assertion green.

### Scope

`get_tau` is called from 14 sites across `cython_profiles.pyx`,
`cython_directionality.pyx` and `cython_distances.pyx`, so this is wider than
SPIKE-Sync: `spike_sync` and its `_multi` / `_profile` / `_matrix` forms and
`filter_by_spike_sync`, the three `spike_directionality` entry points, the six
`spike_train_order` ones, and `optimal_spike_train_sorting` through
`spike_directionality_matrix`. `spike_directionality` on the two trains above is
just as flat: -0.016667 uncapped, and 0.000000 at every one of 1.0, 0.25 and 1e-6.

### Cause

`pyspike/cython/cython_get_tau.pyx`, and the same logic in
`pyspike/cython/python_backend.py`. The parameter named `max_tau` here receives
`true_max` — the recording span, or twice the user's cap when one was given and it
is smaller — which matters for the patch. Annotations marked `<-`:

```cython
cdef double mF1 = max_tau        # <- only a default
cdef double mP1 = max_tau
cdef double mF2 = max_tau
cdef double mP2 = max_tau

if i < len(spikes1)-1 and i > -1:
    mF1 = (spikes1[i+1]-spikes1[i])      # <- overwritten, uncapped
if j < len(spikes2)-1 and j > -1:
    mF2 = (spikes2[j+1]-spikes2[j])
if i > 0:
    mP1 = (spikes1[i]-spikes1[i-1])
if j > 0:
    mP2 = (spikes2[j]-spikes2[j-1])

mF1, mF2, mP1, mP2 = mF1/2., mF2/2., mP1/2., mP2/2.
...
return fmin(s1F, s2P)            # <- max_tau never enters
```

At the default `MRTS=0`, `Interpolate(a, b, 0)` returns `min(a, b)`, so the
function reduces to the minimum of the four half-ISIs — a quantity `max_tau` never
touches. **MRTS does not substitute for a cap**: `Interpolate` is bounded above by
its second argument, the half-ISI facing the other spike, so raising MRTS can only
move the window up toward that bound, never down.

The clamp existed until 0.8.0, which replaced three per-file copies of `get_tau`
with one shared implementation and dropped it from all three at once. In 0.7.0 the
seed and the cap were separate parameters, and `max_tau` there is the user's raw
value rather than today's `true_max`:

```cython
    m *= 0.5
    if max_tau > 0.0:
        m = fmin(m, max_tau)
    return m
```

0.8.0 is on PyPI as of 2023-07-14, so the cap has been inert for three years. (The
GitHub *Releases* entry reads 2023-10-13, which is when the tag was pushed after
issue #71 asked for it; the tag is lightweight and carries the July commit date.)

I can't tell from outside whether the clamp was dropped deliberately or lost in
the consolidation. Either way the docstring and the code now disagree, and one of
them should move.

### Where the cap comes from

Since the measure itself is deliberately parameter-free, it is worth saying that
the cap is not an invention of the implementations:

| source | a global cap? | what it says |
| --- | --- | --- |
| Quian Quiroga, Kreuz & Grassberger 2002, Eq. 4 ([Phys Rev E 66:041904](https://doi.org/10.1103/PhysRevE.66.041904)) | **sanctioned** | *"…one could also make other choices, e.g. by taking τij smaller than in Eq.(4) or by using τ′ij=min{τ,τij}."* |
| Kreuz, Mulansky & Bozanic 2015, Eq. 19 ([J Neurophysiol 113:3432](https://doi.org/10.1152/jn.00848.2014)) | no | the parameter-free default: min of the four surrounding half-ISIs |
| Satuvuori et al. 2017, Eqs. 17–18 ([J Neurosci Methods 287:25](https://doi.org/10.1016/j.jneumeth.2017.05.028)) | no | MRTS, which is a floor — the opposite thing |
| **Kreuz, Satuvuori, Pofahl & Mulansky 2017** ([New J Phys 19:043028](https://doi.org/10.1088/1367-2630/aa68c3)) | **yes — `τmax`** | *"For some applications it might be appropriate to additionally introduce a maximum coincidence window τmax as a parameter."* |
| cSPIKE | yes — `max_dist` | requires `\|Δt\| < TAUij` **and** `\|Δt\| < max_dist` |
| PySpike ≤ 0.7.0 | yes — `max_tau` | `if max_tau > 0.0: m = fmin(m, max_tau)` |
| PySpike ≥ 0.8.0 | **no** | seeds four ISI slots, all overwritten for an interior spike |

`min{τ, τij}` is in the paper that introduced the adaptive window, as an
explicitly optional variant, and it is named and used in the SPIKE-order work
fifteen years later. Neither measure paper carries it because neither is about
bounding the window. For `max_dist > 0`, cSPIKE's two conditions are exactly
`|Δt| < min(TAUij, max_dist)`, which is what the patch computes.

### Suggested fix

`get_tau` receives `true_max`, so the bound to apply is half of it. In
`pyspike/cython/cython_get_tau.pyx`:

```diff
--- a/pyspike/cython/cython_get_tau.pyx
+++ b/pyspike/cython/cython_get_tau.pyx
@@ -43,8 +43,8 @@
     if i<0 or j<0 or spikes1[i] <= spikes2[j]:
         s1F = Interpolate(mP1, mF1, MRTS)
         s2P = Interpolate(mF2, mP2, MRTS)
-        return fmin(s1F, s2P)
+        return fmin(fmin(s1F, s2P), max_tau/2.)
     else:
         s1P = Interpolate(mF1, mP1, MRTS)
         s2F = Interpolate(mP2, mF2, MRTS)
-        return fmin(s1P, s2F)
+        return fmin(fmin(s1P, s2F), max_tau/2.)
```

and the same two returns in `pyspike/cython/python_backend.py`, which uses the
builtin rather than `fmin`:

```diff
--- a/pyspike/cython/python_backend.py
+++ b/pyspike/cython/python_backend.py
@@ -361,11 +361,11 @@
     if i<0 or j<0 or spikes1[i] <= spikes2[j]:
         s1F = Interpolate(mP1, mF1, MRTS)
         s2P = Interpolate(mF2, mP2, MRTS)
-        return min(s1F, s2P)
+        return min(min(s1F, s2P), max_tau/2.)
     else:
         s1P = Interpolate(mF1, mP1, MRTS)
         s2F = Interpolate(mP2, mF2, MRTS)
-        return min(s1P, s2F)
+        return min(min(s1P, s2F), max_tau/2.)
```

Those two files cover every caller in both backends —
`directionality_python_backend.py` imports `get_tau` from `python_backend`.

No `max_tau > 0` guard is needed: when the user passes 0 or `None` the callers set
`true_max = t_end - t_start`, so the new term bounds the window at half the
recording span, which is what 0.7.0 did by seeding `m` with `interval` before
halving. At `MRTS = 0` the two are the same function, and both land on
`min(interval/2, ISI/2 over existing neighbours)`, further clamped at `max_tau`
when one was asked for. Exact ties are unaffected — the new bound is strictly
positive for any positive cap.

One case does change against 0.9.0: with `Reconcile=False` a half-ISI can exceed
the recording span, and today's code returns it while the patch bounds it at half
the span. That is a restoration of 0.7.0 rather than a new hazard, but it is yours
to sign off on.

Patched, the sweep above becomes:

```
 max_tau   as shipped   with the patch
    None       0.3500          0.3500
     1.0       0.3333          0.1833
    0.25       0.3333          0.0500
   1e-06       0.3333          0.0000
```

Finite caps become monotone in `max_tau`, a 1 µs window reaches 0 — the smallest
cross-train gap here is 0.027 s — and the `None` row is unchanged.

**Your test suite stays green.** I built the `v0.9.0` tree with both diffs applied
and ran `test/`: 50 tests over all 13 files pass, patched and unpatched alike,
`test_reconcile.py` included. That is with the compiled Cython extension, rebuilt
from the patched `.pyx`.

One design question I did not want to decide for you: with `MRTS > 0` this lets
`max_tau` override the MRTS-raised window. That seems right for a hard cap, but it
is your call.

### What it costs downstream

We hit this porting the cSPIKE SPIKE-synchronization stack to Python and
cross-checking against both cSPIKE reference output and PySpike. Here is the cost
on a synthetic 30-train recording — simulated calcium event times, 2670 events at
2362 distinct times after dropping within-train duplicates, median ISI 31 s — from
[our committed test fixture](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tests/fixtures/synth_fastcal_s1.mat).
Both columns are `pyspike.spike_sync`, so this is PySpike against itself:

| `max_tau` | as shipped | with the patch |
| --- | --- | --- |
| uncapped | 0.3235 | 0.3235 |
| 0.25 s | 0.3133 | 0.0696 |
| 1 µs | 0.3119 | 0.0156 |

At a 0.25 s cap the shipped code reports 4.5× the synchrony the capped definition
allows. Our own port, which matches cSPIKE reference output to 1e-9 at that cap,
reproduces the patched column to the digit — corroboration rather than the
measurement, since it implements the same semantics the patch restores. The port
and the test that pins this:
[`sync.py`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/src/bugarach/detectors/sync.py),
[`test_sync_detect.py`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tests/test_sync_detect.py).

### Environment

PySpike 0.9.0 (pip, compiled Cython backend), NumPy 2.5.2, Python 3.14.5, macOS.
The pure-Python backend agrees, as-shipped and patched both; the two `Interpolate`
implementations agree on 200k random triples, so this is not a build artifact.

Happy to open this as a PR with a regression test — the patch is written, both
backends are built and your suite is green against it.

---

## Notes for the reviewer (not part of the issue)

- **The issue was cut by a quarter on 2026-08-23** (16.7 KB → 12.4 KB), and a
  short note to Kreuz was added as the primary route. What went, and why it can
  go: the cSPIKE `Spiketrains.cpp` excerpt and the two `max_dist` mismatch
  bullets (the `max_dist < 0` escape, and `max_dist = 0` admitting ties through a
  fast path) — real, checked, and PR-review material rather than triage material;
  the `spike_directionality` sweep listing, now one sentence carrying the same
  four numbers; the `optimal_spike_train_sorting` annealing parenthetical; and
  the long paragraph deriving that the patch equals 0.7.0 at `MRTS=0`, now two
  sentences. **Nothing the murderboard corrected was touched** — the 0.8.0
  dating, the `max_tau/2` bound, the separate `python_backend.py` diff, the
  synthetic-fixture wording, the 2670-at-2362 count, the edge-spike explanation
  of the `None` row, MRTS-is-a-floor, the `Reconcile=False` disclosure and the
  seven-row provenance table all survive verbatim, and the render check was
  re-run. The cut material is in git if the maintainer asks for it.
- **The note to Kreuz is not a short version of the issue.** It asks the question
  only he can answer and leaves the mechanism to the issue. If he says the cap was
  dropped deliberately, the issue becomes a docs bug and most of it comes out —
  which is the point of asking first.
- **The intent argument was cut, because it was false.** The draft claimed the
  callers "still" compute a doubled `max_tau`, offering that factor of 2 as
  evidence the bound was meant to survive. 0.7.0 has no `true_max` and no
  doubling — the seed and the cap were separate parameters — so the doubling was
  created by the same rewrite that dropped the clamp, and it is fully explained by
  `max_tau` now seeding an ISI slot that gets halved. It discriminates nothing. The
  report now rests on the docstring alone and asks which way the maintainer wants
  it resolved, which is both true and harder to argue with.
- **The patch changed twice during review.** The first draft proposed
  `fmin(tau, max_tau)`, which caps at *twice* the intended window — inside
  `get_tau` the parameter named `max_tau` is the already-doubled `true_max`. The
  blind re-review then caught that the corrected diff, applied where the draft
  said to apply it, raises `NameError` in `python_backend.py`, which imports only
  numpy and uses the builtin `min`. Both backends now get their own diff, and the
  patched sweep in the issue is the tested result.
- **The regression is from 0.8.0, not 0.9.0.** The first draft said 0.9.0 because
  that is the version we run. 0.7.0 has the cap and 0.8.0 does not, so the report
  now names the release that dropped it and the maintainer has a bisect boundary.
- **The citation was re-attributed twice, and the first correction overshot.**
  The original draft cited Kreuz et al. 2015 for the capped formula; that paper
  says the opposite — SPIKE-synchronization is "parameter- and scale-free" and its
  Eq. 19 has no upper bound — and the recipient co-authored it. The first fix
  swung to "`max_tau` is PySpike's own addition", which is also false and which
  this report's own "Expected behavior" section contradicted. cSPIKE has the same
  parameter as `max_dist` (`cSPIKE_mac/SpikeTrainSet.m:187`, and in eight of the
  nine signatures in the class help, and described in none of them; applied in
  `cSPIKEmex/Spiketrains.cpp:453` as a second condition on top of the adaptive
  window). The final version says what is actually true and is the
  strongest of the three: the cap is published, in a third paper
  (New J Phys 19:043028) that Mulansky himself co-authored, as an explicitly
  optional extension — which is why it is missing from the two measure papers and
  why 0.8.0 dropping it is a regression rather than a redesign. Verified verbatim
  from the PDF.
- **Scope was understated.** `get_tau` has 14 call sites across three `.pyx`
  files, not the four SPIKE-Sync entry points originally listed; the
  directionality and spike-train-order APIs take `max_tau` too and are equally
  affected.
- **The 0.25 s row is the operating point our detectors run at.** Our port's
  per-spike profile at that cap is what `tests/test_sync_detect.py` asserts to
  1e-9 against cSPIKE MATLAB reference output, so both columns are checkable from
  the repo.
- **The results table became PySpike-against-PySpike**, which removed two problems
  at once. It no longer asks the maintainer to trust an unpublished port for the
  headline number, and it no longer needs the definitional hedge about comparing
  our mean-of-per-spike-values against PySpike's summed-coincidence-over-summed-
  multiplicity. The 1 µs row, previously withheld because our port is
  cSPIKE-validated only at 0.25 s / 0.5 s / uncapped, ships now that both columns
  come from the same code path. The port's numbers reproduce the patched column to
  the digit, so it corroborates instead of carrying.
- **A rendered figure was considered and left out.** The finding is a scalar
  comparison, the ASCII derivation carries all of it, and unlike an image it can
  be quoted in a reply and read in a terminal — where triage happens. The one
  picture-shaped claims are both better as the tables they already are: the
  cSPIKE comparison has only two validated points, and the as-shipped-vs-patched
  sweep is four rows whose whole content is "one column moves and the other does
  not". Recorded, with both reasons, so a later session does not reopen it.
- **After filing**, the issue URL belongs in `docs/FOUNDATIONS.md` (the PySpike
  bullet at line 49), `README.md` (twice — lines 41 and 76), `tools/sapper.py`'s
  SAP003 message, `src/bugarach/detectors/__init__.py`, the NOTE comment in
  `tests/test_sync_detect.py`, `docs/sapper_feedback/2026-08-12-sap-id-namespace-collides-with-interface2.md`,
  and — the one an outside reader meets —
  `docs/todo/2026-08-11-methodology-narrative-doc.md`. All **eight** assert the bug
  today with no upstream reference. **The version half of this is already done**
  (2026-08-23): every one of the eight used to call it "PySpike 0.9.0's" bug, which
  this report shows is wrong, and all eight now date it to 0.8.0. What is left for
  the day the issue exists is the URL. `test_pyspike_max_tau_is_still_inert` is a
  ninth mention but already named 0.8.0 correctly; it points back here instead of
  keeping its own copy of this list, which had already drifted to three entries.
- **The three ⚠ flags the murderboard left are now cleared** (2026-08-23), which
  is what turns "here is a bug" into "here is a fix you can merge":
  - *Upstream's suite under the patch* — **green**. The `v0.9.0` tarball, both
    diffs applied, `pytest test`: **50 tests over all 13 files pass**, patched and
    unpatched alike. `test_reconcile.py` — the one to watch, given the
    `Reconcile=False` behavior change — is among them, as are `test_distance.py`
    (the suite's only `max_tau` assertion) and `test_directionality.py`.
  - *A patched **compiled** extension* — **built and run**. Cython rebuild of the
    patched `.pyx`, and it reproduces every patched number the report quotes: the
    sweep to 0.3500/0.1833/0.0500/0.0000 and the fixture table to
    0.3235/0.0696/0.0156. It also flips the smallest reproduction — the 7.7 s pair
    at a 0.25 s cap goes from coincident to not. So the two backends agree under
    the patch exactly as they do without it, and no claim in the report now rests
    on the pure-Python path alone.
  - *The 0.9.0 misdating* — **fixed in the tree**, in the same pass that added
    this note. See the bullet above; what is left there is the URL, not the
    version.
  Reproduce any of it with the recipe in `tools/pyspike_patch_check.sh`.
- **Still unverified** ⚠: nothing blocking, but worth saying — the patched build
  was exercised by upstream's suite and by this report's own numbers, not by a
  wider set of inputs, and it was built on macOS/CPython 3.14 only.
- SPIKY, the MATLAB GUI, is not in this tree at all, so it cannot be checked from
  here — the issue claims the cap only for cSPIKE and PySpike, both read directly.
- The repo links assume bugarach stays public at that path.
