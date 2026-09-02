---
status: in-progress
filed: 2026-08-11
---

# File the PySpike max_tau bug upstream

## FILED 2026-09-01 — https://github.com/mariomulansky/PySpike/pull/89

Three files, +146/−4. Every numbered step below is done; what is left belongs to other
files and is listed there.

**It went out with Kreuz's private mail quoted in the description, and that was a
mistake.** The murderboard flagged it twice as a residual — *"he was not asked whether
he minds being quoted verbatim in a public forum"* — and it was treated as closed by
Tony's instruction to open the PR. It was not his alone to close: the words were
Kreuz's. The quotes were live for a little over an hour, drew no comments or reviews,
and were removed from both the description and the commit message.

**Removal is not retraction, and the note says so.** GitHub keeps the edit history of a
PR body, and the superseded commit `77f5b73` is still fetchable by hash from the fork
*and* from `mariomulansky/PySpike`, because the PR ref keeps it reachable. The first
draft of the apology told Kreuz the rewritten commit meant the earlier version was
gone; that was checked and false, and corrected before sending. An apology that
overstates the remedy is worse than none.

Tony sent the note on 2026-09-01 —
[`docs/kreuz_note_2_apology.md`](../kreuz_note_2_apology.md), trimmed by him to 142
words from 427. **The standing rule this leaves:** a third party's private
correspondence is not the user's to release on their behalf, and "the user told me to
post it" does not settle it. Raise it, and if it is going out anyway, get the
correspondent asked first.

The description was also cut to 764 words from ~3,600, on Tony: *"just the facts. what
we found, what we propose to fix it."* Three murderboard roles had said the same and
were not acted on until he said it.

### KREUZ CLEARED THE QUOTES 2026-09-02, AND THE PR STAYS TRIMMED ANYWAY. Do not restore them.

He replied to the apology the same day: *"for me no worry at all. It was all scientific
and factual content so I don't mind at all whether it is public or not. Even more so, if
you think it might help people to understand the issue, feel free to restore the full
version."* So the harm the apology was for did not land, and permission now exists.

**Tony's call was to leave PR #89 exactly as it is.** The reason a later session needs, so
it does not read this as unfinished repair: **the 2026-09-01 edit had two motives and only
one of them was Kreuz's to lift.** It removed his quotes *and* cut 4,027 words to 764 on
Tony's *"just the facts"*, in one stroke. His clearance disposes of the first. The second
is an editorial judgement about what a maintainer deciding whether to *merge* should have
to read, and it still stands. Mulansky was cc'd on Kreuz's own mail, so the endorsement
already reached the only person whose agreement the PR needs.

**Nothing about his staffing or unreleased work was ever in the PR body** — the board block
for this worktree had already ruled it out, and the redaction was of three passages only:
the "Thomas Kreuz reproduced this and asked for the PR" section, the *"give the user
options and not impose one specific variant"* line, and one clause crediting his two
figures to his mail. The clearance covers those three; it is not a licence to publish the
rest of the mail, which he did not offer and which is still Tony's to file or not.

**Both revisions of the body are recoverable and neither is in this repo.** GitHub keeps
them, and one query prints either:

```
gh api graphql -f query='{ repository(owner:"mariomulansky", name:"PySpike")
  { pullRequest(number:89) { userContentEdits(first:10)
      { nodes { editedAt diff } } } } }'
```

Two nodes: `2026-09-01T12:19` is the 4,027-word original, `13:35` the 764-word body live
today. The superseded commit `77f5b73` is likewise still fetchable by hash.

**The standing rule from the incident is unchanged by this.** Asking afterwards and being
told it was fine is luck, not process. It stays: get the correspondent asked *first*.

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

**What did not change:** the numbers or the finding. **What did change, and it is not small:
the patch file, the test, the harness and most of the description** — see the murderboard run
record, [`docs/reviews/pyspike_pr_2026-08-31.md`](../reviews/pyspike_pr_2026-08-31.md). The
short version is that the patch as it stood **could not be applied by `git apply`**: its
hand-written `python_backend.py` hunk was missing three trailing blank context lines, and
`patch(1)` is lenient about exactly that, so `tools/pyspike_patch_check.sh` had been green on a
patch a maintainer's own tooling would have rejected. The patch is now generated by `git diff`,
carries the regression test as a new-file hunk, and the harness gates **both** tools.

The patched build does reproduce Kreuz's cSPIKE figures — 0.500000 at `max_dist=0.25` and
0.666667 at 0.35, against his 0.5 and 2/3 — and that remains the strongest line in the PR,
because it is upstream's code, patched, landing on the reference implementation's values on an
example the maintainer's collaborator chose.

### One thing his reply does not answer — and the papers do

The report used to close with a design question — *"with `MRTS > 0` this lets `max_tau`
override the MRTS-raised window"* — and Kreuz did not address it, because the note left the
mechanism to the issue and never put it in front of him. **Do not upgrade it to "Kreuz
confirmed"**; his options-not-impositions answer is about the parameter existing, not about
this interaction.

**The murderboard closed it from the literature instead** (2026-08-31, role 6, which read the
papers rather than reasoning from them). Kreuz et al. 2017 §3.3 introduces τmax *alongside* the
adaptive window — *"We still use the adaptive coincidence detection from Eq. 1 but define a
maximum coincidence window τmax"* — and uses it as a hard physical constraint, a propagation
speed. Satuvuori's Eqs. 17–18 already pair MRTS with its own ISI ceiling: *"each side is
limited to half the ISI even if the threshold is larger."* And because `min` is associative and
commutative, applying the cap inside Eqs. 17–18 per side or outside Eq. 19 is the same
function — so the patch's placement is not one option among several.

So the PR now **states the answer with those two citations** and flags the interaction as a
behaviour change rather than an open question. Asking a maintainer to adjudicate something his
own paper settles was the one place the draft read as under-researched.

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
3. ~~**Open the PR against `mariomulansky/PySpike`**~~ — **DONE 2026-09-01,
   [PySpike#89](https://github.com/mariomulansky/PySpike/pull/89).** Three files, +146/−4,
   generated by `git diff` and accepted by `git apply` and `patch(1)` alike.
4. ~~**Then** put the PR URL in the eight places~~ — **DONE 2026-09-01.** FOUNDATIONS,
   README ×2, SAP003's message, `detectors/__init__.py`, the sapper_feedback table, the
   methodology-narrative todo, and the NOTE in `tests/test_sync_detect.py`.

**Nothing here is half-done.** What is left is not this file's:

- ~~**`syncytium2/bugarach` PR #426 is open and unmerged**~~ — **`origin/main` merged into the
  branch 2026-09-02**, four conflicts resolved. The advice that stood here — *"the vendored
  conflicts are spurious… take either side"* — **was true when written and false by the time
  anyone acted on it, and taking either side would have destroyed work.** Both sides do still
  stamp `564b944`, but `main` has since gained an `# instrument:` line in each of
  `murderboard_freshness.sh`, `murderboard_revendor.py` and `murderboard_roster.sh`, so
  `--ours` silently strips a landed declaration. **What was actually applied:** `--theirs`
  (main) for the three vendored files, `--ours` for this todo — `main` carries only the
  squashed snapshot of `f2e73e5` via #424, including a *"Draft issue text (not yet posted)"*
  section this branch deleted once the PR was filed, so on this file the branch is strictly
  newer. A stamp match is evidence about provenance, not about content; diff before trusting it.
- ~~**Two suite failures on this branch are not from this work**… `main` likely carries them
  too.~~ **`main` does not carry them and neither does this branch. Diagnosed 2026-09-02: the
  three failures are the shared venv, not the code.** `.venv` holds an editable install of the
  *primary* checkout, so `import bugarach` in **any** worktree resolves to
  `Developer/bugarach/src/bugarach` — and these three tests are exactly the ones that compare a
  worktree file against imported behaviour. `test_architectures_are_files` writes a probe
  architecture into this worktree's `src/` and asks the imported package to autoload it, which
  it cannot see; `test_lab_server` asserts the served page equals this worktree's
  `docs/site/raster_viewer.html`, and it is the primary's page that gets served.

  ```
  PYTHONPATH=src .venv/bin/python -m pytest -q     # 25 passed, 0 failed
  ```

  The stashing check that produced the original note could not have distinguished this: the
  failures persist under any content change to the worktree, because the worktree's content is
  not what is running. **Run the suite from a worktree with `PYTHONPATH=src`** — otherwise a
  green run proves something about the primary checkout.

  **This defect was already known, filed and indexed, and this session still re-derived it** —
  [`2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md`](2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md),
  its one-screen handoff
  [`the-worktree-src-fix-nobody-has-chosen`](../handoffs/2026-08-28-the-worktree-src-fix-nobody-has-chosen.md),
  and a row in [`INDEX.md`](../INDEX.md) under **Known traps** keyed on the words you would
  actually type. Three fixes are written up there and none is chosen; that decision stays
  theirs, not this file's. The three failing test names are now recorded in that todo so the
  next session greps its way there instead. **`docs/INDEX.md` first — that is what it is for.**
- **Three of the four disclosed behaviour changes still have no regression test** — the tie
  boundary, `Reconcile=False`, and the sorting permutation. Listed in the run record.

**Do not re-run the murderboard.** It ran on 2026-08-31 — eleven roles plus a four-lens blind
round — and stopped unconverged on flat severity. The record, with every residual, is
[`docs/reviews/pyspike_pr_2026-08-31.md`](../reviews/pyspike_pr_2026-08-31.md).

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

## Draft issue text (now the PR description — for review, not yet posted)

**Title:** Restore the `max_tau` coincidence-window cap (inert since 0.8.0)

### The bug

Since 0.8.0, `max_tau` has no effect on any pair of spikes that each have a
neighbour on both sides in their own train.

```python
a = pyspike.SpikeTrain([0.0, 1.0, 3.0, 5.0, 7.0, 9.0], 10.0)
b = pyspike.SpikeTrain([0.0, 1.1, 3.2, 5.3, 7.4, 9.5], 10.0)
```

The six pairs are 0, 0.1, 0.2, 0.3, 0.4, 0.5 s apart. A 0.25 s cap should admit
three of them, a 0.35 s cap four. **PySpike returns 5/6 for both**, and for every
positive cap down to 1 µs. The docstring, in all fourteen copies, says
`max_tau` bounds the window.

### Cause

`get_tau` seeds the four neighbouring-ISI slots with `max_tau` and overwrites
each one as soon as that neighbour exists. All four are overwritten exactly when
the pair is interior to both trains, and the cap is then never compared against
the window:

```cython
cdef double mF1 = max_tau        # <- only a default
...
if i < len(spikes1)-1 and i > -1:
    mF1 = (spikes1[i+1]-spikes1[i])      # <- overwritten, uncapped
...
return fmin(s1F, s2P)            # <- max_tau never enters
```

0.7.0 ended `get_tau` with `if max_tau > 0.0: m = fmin(m, max_tau)`, in each of
the three `.pyx` copies and in `python_backend.py`. 0.8.0 consolidated the Cython
side into one shared implementation without it, and the pure-Python copy lost it
too.

This is not only SPIKE-Sync: `get_tau` has 14 call sites across the three `.pyx`
files and 8 more in the pure-Python backend, so `spike_directionality`,
`spike_train_order`, `filter_by_spike_sync` and `optimal_spike_train_sorting` are
all affected.

### The fix

`get_tau` receives `true_max` — the span, or twice the user's cap when smaller —
so the bound is half of it.

```diff
@@ -43,8 +43,8 @@ cdef double get_tau(double[:] spikes1, double[:] spikes2,
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

Same two returns in `python_backend.py` with the builtin `min`. Between them that
is every caller on both backends — `directionality_python_backend.py` imports
`get_tau` from `python_backend`.

No `max_tau > 0` guard needed: at `0`/`None` the callers set `true_max` to the
span, so the bound is half the span, which is what 0.7.0 did by seeding `m` with
`interval` before halving. At `MRTS = 0` the patched function and 0.7.0's are
identical.

### What changes

Nothing at `max_tau` of `0`/`None` with default `Reconcile` — checked over the
suite and ~12,600 shipped-vs-patched probes on both backends. Four things do
change, all of them the cap working:

- `|Δt| == max_tau` is no longer a coincidence, matching cSPIKE's strict `<` and
  0.7.0.
- `Reconcile=False`: a half-ISI can exceed the span, and 0.9.0 returns it where
  this bounds it at half the span. Fuzzing 3,000 pairs, 23 `spike_sync` values
  moved, always down. `test_reconcile.py` passes either way.
- `filter_by_spike_sync` with a tight cap returns empty trains more readily.
  Empty trains already break `spike_directionality` on 0.9.0
  (`ZeroDivisionError`) — pre-existing, happy to file separately.
- `optimal_spike_train_sorting` can return a different permutation; at a very
  tight cap the directionality matrix is all zero, so the ordering is arbitrary.

Under `MRTS > 0` the cap now also overrides an MRTS-raised window. That looks
right — Kreuz et al. 2017 introduces τmax alongside the adaptive window, and
Satuvuori's Eqs. 17–18 already cap MRTS at half the ISI — but it is a behaviour
change, so I am flagging it.

### Tests

`test/test_max_tau.py` is new, because nothing in the suite passes `max_tau` for
a pair interior to both trains. The one existing assertion
(`test_distance.py:184`) uses a one-spike partner, which leaves two slots seeded
and passes either way; it is untouched and still green.

| pair separation (s) | 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| `max_tau` (s) | 0.05 | 0.15 | 0.25 | 0.35 | 0.45 | 0.55 |
| as shipped | 5/6 | 5/6 | 5/6 | 5/6 | 5/6 | 6/6 |
| with the patch | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 |

Six tests: that staircase, the profile at 0.25 s, the bound reaching
`spike_directionality`, strict increase, `0`/`None` still a no-op, and one
`MRTS > 0` case. Five fail as shipped and pass patched on both backends; the
sixth is the no-op invariant.

**56 tests over 13 collecting files, against 50 over 12 today.**

Verified on PySpike 0.9.0, NumPy 2.5.2, Python 3.14.5, macOS only.


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
