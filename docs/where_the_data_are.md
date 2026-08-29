# Where the data are, and how to tell whether that still works

You are probably here because something looked broken. Start at the top.

## Is it working right now? Three commands

```bash
PYTHONPATH=src python3 -m bugarach.dataset      # every declared role, resolved or not
bash tools/session_briefing.sh | grep "data in:"
bash .claude/hooks/the-folder-is-the-input.sh --selftest
```

Healthy looks like this:

```
data root: <…>/data
declared in current_export.toml:
  default  2026-08-18_revised_2v_periods
           -> <…>/exports/bugarach/2026-08-18_revised_2v_periods  (84 recording CSVs)

data in: 2026-08-18_revised_2v_periods — dataset.current() resolves it here

PASS
```

Three independent things are being asked there: does the repo **declare** a folder,
does this machine **resolve** it, and can the gate still **fire**. They fail
separately, and the table below turns each symptom into one of them.

> **Use `PYTHONPATH=src python3`, not a bare `python`.** It is the one form that works
> both in the primary checkout and in a worktree, which has no `.venv` of its own. A
> bare `python -m bugarach.dataset` fails on a machine where `python` is not on PATH,
> and a bare `python3` fails outside the venv with `No module named 'bugarach'` — an
> error about *your invocation* that reads exactly like the mechanism being broken.

## "It appears to fail" — what it usually is

| what you saw | what it means | what to do |
| --- | --- | --- |
| Briefing says `!! data in: <name> declared, NOT here` | The repo's declaration is fine; **this machine** cannot resolve it. Dropbox not mounted, still syncing, or a renamed folder. | Run the probe above — it names the root it tried. This is the state the alarm exists for: do **not** go looking with `find`, and do **not** fall back to a `.mat` store. |
| A `find` or `ls` was blocked and you meant it | The **search branch** of the gate. Legitimate cases exist: inspecting what the producer shipped, a raw `2R` acquisition folder, counting a store's slices. | Re-run prefixed with `BUGARACH_DATA_OK=1`. If the block was unreasonable, that is a false positive worth filing in `docs/sapper_feedback/`. |
| Something was blocked that reads no data at all | Almost certainly the **store branch**, which has a known false positive (below). | `BUGARACH_DATA_OK=1` clears it. |
| The briefing printed nothing about data | The line was dropped, or the whole payload degraded. Check line 1 for `(TERSE`. | If TERSE, the briefing went over budget — see *The budget*. If not, four guards in `tests/test_session_briefing.py` cover that line; run them. |
| A session still went hunting with `find` | **The real failure the whole mechanism exists to prevent.** | Re-run the census below. A number, not an impression, decides whether behaviour changed. |

**The distinction that matters most:** *the gate interrupted me* is not the same
failure as *a session got lost*. The first is noise and has an opt-out. The second is
what cost a day on 2026-08-27, and it is the one worth escalating.

---

## The answer the mechanism exists to give

```python
from bugarach import dataset
folder = dataset.current()            # the standard export
folder = dataset.current("pensub")    # the crosstalk control's pair
```

No path required, and `BUGARACH_DATA_ROOT` need not be set — `data_root()` finds the
Dropbox mount by itself. Every analysis tool takes `--dataset <name>`, so a path never
has to be typed. Which folder is current is declared in `current_export.toml` at the
repo root and **nowhere else**.

`dataset.current()` returns a **name**-addressed folder rather than a path because the
original failure was hand-pathing: a discovered absolute path passed to `--folder`
four times in one session. A path is a per-machine fact that reads like a repo one.

---

## The baselines, so a claim can be checked against a number

**Read the caveats with the numbers.** Both measurements below are real and both are
weaker than they look; the limitations are stated because a baseline quoted without
them becomes a warrant.

### The search gate's trigger, scored over the session record

Every Bash command in the bugarach session transcripts on the machine where the gate
was written, run through the real `grep -E` the hook uses:

| trigger | fires | judged |
| --- | --- | --- |
| **shipped**: a line-leading `find`/`ls`/`tree` naming `exports/`, `processed_archive` or `/data` | **30** | **0 false positives**, all 30 read by hand |
| rejected: the same, allowing the verb after `;` or `&&` | 140 | many false, incl. a heredoc writing a todo |
| rejected: any `find` rooted at the home directory | 46 | 23 false — about half |

All 30 were sessions locating the data root, listing export folders, or counting a
store's slices. **The numerator is the durable finding; the denominator is not.** The
transcript record grows every time anyone works here — it went from 11,292 commands to
12,326 across a single evening, over 56 files in two project directories — so the rate
(≈0.25%) moves without anything changing. On a re-run, compare the **count of hits and
what they are**, not the percentage.

Three limits on the "zero false positives" figure, none of which it can escape:

- **The hits were read by the person who wrote the trigger.** An independent read is
  the stronger evidence and has not been done.
- **It scores sessions that ran *before* the gate existed.** A gate changes what
  sessions do, so the false-positive rate *in its presence* is unmeasured.
- It covers the **search** branch only. The store branch is not clean — see below.

### The first live test, 2026-08-28

A fresh session was asked to pick a real baseline recording, run two detectors and draw
the raster — a task needing the data, whose prompt named neither the folder nor the call:

| | |
| --- | --- |
| Bash calls | 36 |
| commands hunting for the data | **0** |
| `dataset.current()` calls | 5 |
| search-gate blocks | 0 |

It read `dataset.py` and called `dataset.current()`, and never touched the filesystem
looking for data. Three things that result does **not** establish:

- **It is one session.** One clean run is not evidence the mechanism generalises.
- **It does not show the briefing caused it.** The session spent about seven calls
  orienting before opening `dataset.py`, so it may have found the resolver by reading
  source, as any session might.
- **Zero gate blocks is not evidence the gate works** — it is what a broken gate also
  looks like. That the gate *can* fire is established by its `--selftest`, not here.
  What this run shows is that the gate was not *needed*.

What it does establish is narrower and still worth having: the 2026-08-27 failure did
not recur under a prompt designed to provoke it.

### Re-running the census

There is no census script in `tools/` — it reads a private transcript directory and
belongs to no analysis. Reconstruct it by scoring the two patterns from
`.claude/hooks/the-folder-is-the-input.sh` against the Bash `tool_use` entries in
`~/.claude/projects/*bugarach*/*.jsonl`, and **read the hits by hand.**

The hand-read is not optional. The first version of this census scored true positives
with a rule that overlapped its own trigger, so the false-positive rate came out at
zero by construction. A classifier that shares a definition with the thing it grades
reports agreement forever.

---

## Known defects

**The store branch false-positives on commands that only mention a store.** It fires on
a store name (`processed_archive`, `event_store*`) appearing anywhere alongside
`python`, `matlab`, `--store` or `open(` — which catches commands that *write about*
stores rather than read one. Two hit on 2026-08-28 alone: writing a tool whose
docstring named a store, and a census script carrying `processed_archive` as a regex
string. Neither read anything.

Clears with `BUGARACH_DATA_OK=1`. The fix is to require the name in a *reading*
position rather than anywhere in the command, measured against the transcript record
before and after so the tightening does not quietly open a hole. The **search** branch
does not share this defect: it was measured before it shipped.

**The budget.** The briefing's input line lives in a payload capped at 9,000 bytes, and
a fresh clone with no data and no darkroom renders about 8,700B. That is the form to
measure — not a configured laptop, where the darkroom resolves in one line and the
alarms are short. The gap is around 90B and falls entirely on the side with no margin:

```bash
cp -R <worktree> /tmp/ci && cd /tmp/ci && git config --unset core.hooksPath
HOME=$(mktemp -d) bash tools/session_briefing.sh | head -1
```

Over budget the briefing degrades to `TERSE`, which drops the FOUNDATIONS §9 extract —
the preparation facts that bind what a detector result can mean — down to its bolded
claims. Running record:
[the budget ratchet](todo/2026-08-27-the-briefing-budget-ratchets-the-digest-oscillates.md).

---

## Why the mechanism has the shape it has

Four things answer four different questions. Each was added because the ones before it
could not reach the case that followed.

| | answers | reaches |
| --- | --- | --- |
| `current_export.toml` | *which* folder | anyone who asks the repo |
| `bugarach.dataset` | *where* it is on this machine | anyone who calls it |
| the session briefing | pushes both, unasked, at startup | every session, whether or not it asks |
| the PreToolUse gate | catches a session that went looking anyway | the moment of the mistake |

The division of labour between the last two is deliberate and was paid for. **The
briefing's job is to make the search unnecessary; the gate's job is to catch the session
that searched anyway.** Corrective prose that only a session already going wrong needs
belongs in the gate, which speaks at the moment of need and has no byte budget — not in
a payload every session pays for. That rule was settled when the briefing's unresolved
alarm came in 13 bytes over.

*A note on vocabulary, for a reader who has not worked here:* **sapper** is
`tools/sapper.py`, which turns incidents into checks that fire at commit time (`SAP007`
is its rule forbidding store reads in the tree); the **darkroom** is the shared Dropbox
folder that figures and reports are written to; the **briefing** is
`tools/session_briefing.sh`, injected into every session at startup.

## See also

- [`export_folder_spec.md`](export_folder_spec.md) — the contract. **Revision 6**
  (2026-08-20) records what re-deriving a producer's decision cost; the contract itself
  has since moved on and is at revision 8.
- [`history.md`](history.md) — the episode that produced all of this, and the other
  moments that changed how the project works.
- `docs/todo/2026-08-28-the-resolver-exists-and-is-invisible.md` — the full build
  record, including the two defects CI caught that a green local suite could not.
