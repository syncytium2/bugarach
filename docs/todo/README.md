# todo

One file per item (same shape as `sapper_feedback/` — concurrent sessions
never conflict). Filename `YYYY-MM-DD-<slug>.md`, frontmatter:

```
---
status: open | in-progress | waiting-on-tony | done
filed: YYYY-MM-DD
---
```

Mark `done` with a closing note rather than deleting — the record is part of
the dev-process story this repo showcases.

## `waiting-on-tony` — finished work that only a person can move

`open` means somebody should do this. It cannot say "this is **done**, and the one
step left is a human pressing send" — and that second kind drowns in a list of
fifty. Use `waiting-on-tony` when no session can make further progress: an external
mail, a post under Tony's name, a decision only he holds, a credential only he has.

Give the item a `waiting:` line in the body, one sentence naming the single action.
The briefing prints these **first and loudly**, using that line as the answer to
"what do I do?":

```
---
status: waiting-on-tony
filed: YYYY-MM-DD
---

# Title

waiting: Send `docs/kreuz_note.md` to Thomas Kreuz. Everything else is done.
```

The status earned itself. The PySpike report was finished, verified and correct for
twelve days while nothing in the repo said it was ready to go out.
