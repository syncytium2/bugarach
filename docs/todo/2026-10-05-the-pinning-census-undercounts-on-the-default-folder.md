---
status: open
filed: 2026-10-05
---

# The pinning census undercounts, so the default folder's pinned-ROI exclusion is wrong on `20260629_312` and `20260629_309`

> **A question for the producer, not a filter.** bugarach adds no exclusion of its own (CLAUDE.md,
> "The export folder is the input"). The fix is a new export from interface2, once its corrected
> ROI sets are signed off. **The work stops until it arrives** (Tony, 2026-10-05): see the last
> section.

## What changed

The default folder, `2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED` (role
`senktide_ttx` in [`current_export.toml`](../../current_export.toml)), removes the events inside
moco floor-pinned windows. The ROIs and windows came from interface2's per-ROI census, and the
earlier note on `steps_and_pins_excluded` ends *"nothing in this folder needs to change."*

On 2026-10-05 an interface2 session (branch `mlspike-blanking-rerun`, handoff
`docs/handoffs/TASK_mlspike_pinning_census_underdetects.md` on that branch) recorded Tony's own
review of every ROI of `20260629_312` in the trace waterfall viewer. It found the census misses
more than half of the contaminated ROIs on that recording:

| recording | what the folder does | what Tony's review says |
|---|---|---|
| `20260629_312` | removes pinned events on ROIs 1, 14, 16 and 20 | **nine ROIs are contaminated over 0–375 s: 1, 2, 3, 4, 14, 16, 17, 18 and 20.** ROIs 2, 3, 4, 17 and 18 keep their events. ROI 8 may be a tenth, coupled to ROI 1's downstrokes; that is recorded, not measured |
| `20260629_309` | removes ROI 16 over 0–15.84 min | **too much.** The 15.84 min end is one coincident fast/slow pair, not an extent; Tony reads the disturbance as ending at about 6 min, so roughly 10 min of usable baseline was cut |
| `20260629_309`, `20260630_316`, `20250926_235` | census ROIs only | **not yet reviewed ROI by ROI.** The census screened them, and it is the census that just missed five of nine |

The interface2 session also tried five statistics against Tony's `_312` call. No threshold on the
census's own measures separates his nine ROIs from the other twelve. MLspike's `spk_autosigma` comes
closest, but its threshold was read off the same 21 ROIs it was scored on. It is a fit, not a
validated detector.

## What this means here

- **All four affected recordings are DI.** A by-group reading inherits the error on one group
  only, which is the case FOUNDATIONS §9 ("group-dependence is not optional") warns about.
- On `_312` the missed ROIs are pinned over the **same 0–375 s span** as the four the folder
  cleaned. That is the cross-cell structure a coordination detector exists to find, and that a
  rate-matched null cannot explain away (the producer's own reason for removing pinning, in the
  `steps_and_pins_excluded` note).
- What fixes it is a new export, not a change here. The producer has to finish the per-ROI review of
  `_309`, `_316` and `_235`, Tony has to sign off the corrected ROI sets and windows, and the folder
  is then re-cut. Until then the pinned-ROI rows in `moco_pinned_excluded.tsv` are known to be
  incomplete.

## Draft request to interface2 (Tony posts it; ADR-0007)

> **Title:** The default folder with every human-confirmed pinned interval excluded
>
> bugarach's default input is `2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED`.
> Its moco floor-pinning exclusion follows the per-ROI census, which the `_312` review on branch
> `mlspike-blanking-rerun` shows misses ROIs 2, 3, 4, 17 and 18 there and over-cuts `_309` ROI 16.
>
> **What should exist afterwards:** a new, dated folder that is the same 66 recordings with every
> event inside a **human-confirmed** pinned interval removed. The intervals are the corrected
> per-ROI review of `20260629_312`, `20260629_309`, `20260630_316` and `20250926_235`, once Tony has
> signed it off. `moco_pinned_excluded.tsv` lists every removed event, as it does now.
>
> **What must not change:** every other file byte-identical to the current folder. That means the
> other 62 recording files, and every row of `slices.csv`, `regions.csv` and
> `field_steps_excluded.tsv`. An event outside a confirmed interval stays, including on the four
> recordings. `PROVENANCE.md` names the review the intervals come from, who signed it off and when.
>
> **Not asked:** a new detector, a threshold or a corpus-wide rescreen. If the review finds pinning
> on a recording beyond these four, say so in the issue and we will decide together whether it is
> in scope.

## Draft comment closing interface2#2 (Tony posts it)

interface2#2 asked for `steps_and_pins_excluded` (84 recordings) re-exported without
`20260707_346`, giving 83. That 83-recording folder was never made. Instead, on 2026-09-23 the
default moved to the 66-recording `senktide_ttx` folder, which drops `_346`. **The closing comment
should say that, rather than "done as asked":**

> Satisfied by a different folder from the one asked for. bugarach's default since 2026-09-23 is
> `2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED` (66 recordings).
> `20260707_346` is absent from it. There is no recording file, and no row in `slices.csv`,
> `regions.csv`, `moco_pinned_excluded.tsv` or `field_steps_excluded.tsv`. Its `PROVENANCE.md`
> records why: *"Excluded by db4 `exclude == 1` (1): `20260707_346`."* (Checked 2026-10-05 against
> the folder itself, not inferred from the count.) The 83-recording all-arm re-export in item 1 was
> not made and bugarach does not need it: the 84-recording folder is an archive role now, read only
> to reproduce earlier runs. `20241004_80` is untouched. It is baseline-only, so it was never in the
> senktide/TTX folder, and it stays in the 84-recording one. Closing.

## Ruled: the work stops now (Tony, 2026-10-05)

CLAUDE.md: *"A known contamination stops the work. It does not become a caveat."* Tony's words,
relayed by the orchestrator: *"i suspect bugarach can't run until we confirm we have removed pinned
data"*. He confirmed it in the housekeeping session the same day: **the stop applies now, not when
the new export arrives.**

- **It fires by itself.** The `senktide_ttx` note in `current_export.toml` declares the
  contamination in the form `dataset.refuse_if_contaminated` reads, so `dataset.default()` and
  `dataset.current()` refuse before the session confirmation is asked for. Pinned by
  `test_the_default_stops_while_the_pinning_census_undercounts` in `tests/test_dataset.py`.
- **What may continue:** anything that does not read data through the dataset pointer. That covers
  fixture-only tests and CI, the bench and the simulator, docs, and drafting the requests above.
  Anything that scores, trains or reports on the default waits. **Do not set
  `BUGARACH_ACK_CONTAMINATION` to get past it** unless Tony has agreed for that analysis.
- **What clears it:** the producer's corrected export becoming the default, with the note and the
  test removed in the same change. A session's judgement that the effect is small does not clear it.
- The `steps_and_pins_excluded` note's *"nothing in this folder needs to change"* is superseded
  in place. Its history stays.

**Owner:** Tony (posting both drafts, and signing off the per-ROI review), then the producer (the
review of `_309`, `_316` and `_235`, and the re-export).
