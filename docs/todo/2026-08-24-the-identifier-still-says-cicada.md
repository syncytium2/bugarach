---
status: open
filed: 2026-08-24
---

# The detector is called locust and its identifier still says `cicada`

The user-visible label was renamed on 2026-08-24 — the rule is the Cossart lab's
CICADA, this implementation modifies it in two ways, and a modified port does not
carry the original's name in a public UI. **The identifier was deliberately left
alone**, so the repo now says `locust` to people and `cicada` to files:

| where | says | why |
|---|---|---|
| viewer lanes, scoreboard, help text, figures, README | **locust** | renamed 2026-08-24 |
| `detections.csv` `detector` column | `cicada` | **output contract** |
| `detector_settings.csv`, `run.json` | `cicada` | same contract |
| module, `cicada_detect`, `ref_cicada_synth.json`, `bench.OPERATING_POINTS` | `cicada` | internal, but see below |

**That split is defensible and it is not free.** The glossary now carries the
mapping in terms, and `ui/app.py`'s `TITLES` says it at the point of use — but a
reader who greps for what they saw on screen finds nothing, and the next session
to add a detector will not know which convention it is following.

## The contract half is not this repo's alone

`detections.csv`'s `detector` column is read by whoever consumes an export.
Changing a value in it is a **coordination cost with other teams**, not a rename:
every stored `run.json` and every downstream reader keys on `cicada` today.
[`docs/export_folder_spec.md`](../export_folder_spec.md) governs the input side;
the output contract is [`docs/webapp_spec.md`](../webapp_spec.md) and
`emit.py`. **This ecosystem has already been bitten once by two projects
diverging on a field name** — `width_sec`, recorded in interface2's own report as
the failure mode to avoid — so a unilateral change here is the wrong shape.

**Recommended:** if it moves at all, it moves as a spec revision that emits
`locust` and **accepts both on read** for at least one release, announced to
interface2 and fireflies before it lands, not after.

## The internal half is cheap and could go first

Module, function, fixture and bench-key renames touch nothing outside this repo
and could land in one mechanical pass with the contract value left as a literal
at the emit boundary. **The argument against doing it now** is that it makes
every historical commit, review record and figure harder to follow for a gain
that is purely tidiness — and that this repo has a live, larger rename question
open in `RESET.md` about what the whole assessor layer is called.

**Do not split the difference.** Either the identifier stays `cicada` everywhere
it is an identifier, which is today's state and is coherent, or it moves
everywhere at once with the contract handled properly. A half-renamed identifier
is the worst of the three.

## What was left showing the old name on purpose

- **`docs/learned/**`** — generated pages and figures. They are already one
  calibration behind ([RESET §5](../RESET.md)), which says regenerate in **one
  pass**; the new label arrives with that pass. Hand-editing them would mix a
  naming change into a stale artifact set.
- **`docs/reviews/**`, `docs/SESSIONS.md`, `HANDOFF-*`, dated todos** — records of
  what was said at the time. Renaming inside them falsifies the record.
- **`docs/FOUNDATIONS.md`** — a session does not edit it (CLAUDE.md). Its §2 and
  §9 name CICADA; folding the rename in is Tony's call.
- **Docstrings and comments across `src/`** that discuss the upstream tool. Many
  of them genuinely mean CICADA-the-tool and are correct as they stand; the ones
  that mean our detector are a prose sweep nobody has done.

## The figures say CICADA and the text says locust

Every committed figure draws the old label. The README's note under the hero
figure now says so out loud, using the same discipline the page already used for
the superseded numbers: quote the picture, and say when the picture is behind.
[The diagnostic figures are one calibration behind](2026-08-23-the-diagnostic-figures-are-one-calibration-behind.md)
is the item that rebuilds them, and it now has a second reason to run.
