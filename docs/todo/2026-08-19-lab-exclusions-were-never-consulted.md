---
status: open
filed: 2026-08-19
---

# The lab says which recordings are analysable, and nothing here was asking

**Two recordings the lab had marked `exclude=1` were inside every number this project has
reported about the assembly question** — the membership tallies, both modularity runs, the
crosstalk pairing, and the geometry the power curve was computed at. They were found by a
murderboard role that had just been told to look for the source of record a deliverable did
*not* open.

## Where the answer lives

`$BUGARACH_DATA_ROOT/indiegroups_db4.xlsx`, sheet **`indiegroups`**, column **`exclude`**.
Six (date, mouse) rows carry a `1`, each with a reason in `notes`:

| date | mouse | reason |
|---|---|---|
| 20240904 | 45 | post surgery too long |
| 20250723 | 55 | post surgery too short |
| 20250724 | 56 | post surgery too short |
| 20250731 | 57 | 6 minute ttx treatment, too short |
| 20260129 | 73 | post surgery too long |
| 20260304 | 81 | possible PRO? |

Only one of those dates has recordings in the onset store: **`20250731_149`** and
**`20250731_151`**.

## Why nothing caught it

The onset store is a store of recordings, not a statement about which recordings are
analysable — and every tool in this repo takes the store as its universe. The workbook is
named in `if2_paths().xls` and is read by interface2 for slice metadata, but no bugarach
code path had ever opened it. An eleven-role review passed the report twice without noticing,
because every role checked the claims against the sources the document *named*.

## What was done

`tools/lab_excluded.py` derives the list from the workbook and writes
`docs/learned/lab_excluded_slices.txt` with its provenance in the header;
`bugarach.assembly.load_excluded` reads it, and `assembly_power.py`,
`assembly_pensub_compare.py` and `make_modularity_figure.py` all take `--exclude-file`.
Tests lock the rule, including that a withdrawn recording is dropped *before* pairing — one
of the ten discordant recordings originally reported was a withdrawn one.

**Every conclusion survived**, which is worth stating plainly: the corrected numbers move by
a recording or two and no verdict changes. The one number that moved across a conventional
line is the fast stream's own McNemar for the crosstalk attenuation, p = 0.031 -> **0.0625**;
the combined nine-recording sign test is p = 0.0039 and unchanged in direction.

## What is still open

- **The match is by DATE, not slice.** The workbook keys on (date, mouse) and carries no
  slice id, so a date with several slices excludes all of them. On this corpus that is the
  same two recordings either way, but the bluntness should be fixed at the source rather
  than lived with.
- **The exclusion reason here is about the TREATMENT** — "6 minute ttx treatment, too short"
  — and every measurement in this line of work is **baseline-only**. So there is a real
  argument that these two baselines are usable and the mark does not bite. That is Tony's
  call, not the analysis layer's: this repo's own rule is that *selection is the producer's
  call* (Tony to fireflies, 2026-08-10), and the default is therefore to respect the mark.
  Both sets of numbers are reported so the decision is reversible.
- **Every other deliverable in this repo that counts recordings should be re-checked**
  against this column. The assembly work is simply where it was noticed. The generator's
  derived spec, the bake-off corpus and the coordination report all take the store as their
  universe.
- **`exclude` is not the only column nobody read.** The workbook also carries `study`,
  `surgery`, `age`, `postsurgery` and `intensity`. Nothing here establishes that none of
  them should gate an analysis.
