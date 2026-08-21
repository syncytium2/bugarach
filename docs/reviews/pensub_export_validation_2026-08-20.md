# The penumbra-subtracted export, checked

One claim in the assembly report has no way to be re-derived. The crosstalk
control — the check that makes the co-participation result mean anything — was
computed on 2026-08-19 by reading two `.mat` stores, and store access closed the
next day. Its numbers carry a `⚠` because nothing in the current inputs can
reproduce them. Closing that needed one thing: a penumbra-subtracted export folder.

It arrived on 2026-08-20.

**Verdict: it conforms, it pairs with the right reference export, and two quantities
the historical control published come back out of it. Re-run the control.** Four things want a word with the producer;
none of them blocks the re-run, and two want an answer before the re-derived numbers
are published.

Folder: `<dropbox>/data/exports/bugarach/2026-08-20_pensub_revised_2v`, written by
interface2's `generate_export_folder.m` on 2026-08-20 at 14:26.

## The subtraction does what the control needs it to do

![A · fast, B · slow. Coactivity excess per minute at K = 3 for each of the 84 recordings, before and after penumbra subtraction, measured by `bugarach assess` against 200 per-ROI circular-shift surrogates in the baseline region. Blue where the value fell, orange where it rose, grey where it did not move; the heavy line joins the medians. Log axis; the region below the dashed line is exactly zero, not a small number. Fast falls from a median of 1.36 to 0.15 and slow from 0.84 to 0.15, and neither reaches zero.](pensub_coact.svg)

This is bugarach's own statistic, from `bugarach assess`, not a measure written for
this review — the null is a per-ROI circular shift within the window, which holds
every ROI's rate and burstiness and destroys only cross-ROI phase.

| stream | median excess/min, K = 3 | fell | rose | already 0 | sign test on the discordant |
|---|---|---|---|---|---|
| fast | 1.36 → **0.15** | 64 | 2 | 18 | p = 6 × 10⁻¹⁷ |
| slow | 0.84 → **0.15** | 55 | 2 | 27 | p = 2 × 10⁻¹⁴ |

**It survives the sibling correction and every group.** The 84 recordings come from
44 animals, so a per-recording count treats siblings as independent observations
(FOUNDATIONS §9). Collapsed to one value per animal, the excess still falls in 37 of
39 animals on fast (p = 3 × 10⁻⁹) and 33 of 34 on slow (p = 4 × 10⁻⁹), and the
direction holds inside all four experimental groups. Counting **recordings** whose
fast-stream excess moved at all, it fell in DI 17 of 17, MALE 21 of 21, ORX 13 of 14
and OVX 13 of 14.

**Attenuated, not abolished.** Nonzero excess survives in 49 of 84 fast recordings and
44 of 84 slow. That is the same shape the assembly report's conclusion has —
*crosstalk inflates the effect and does not account for it* — reached from the folders
alone.

A second measure, written independently for this review, agrees. It asks a narrower
question aimed straight at optical overlap: for each event, is there an event in a
**different** ROI within **±0.5 s** — five frames either side at this 0.1 s interval.
That window spans 1.0 s, the same width as the coactivity bin above, and is chosen to
match it: what differs is that it **slides with each event** instead of being a fixed
bin, so a coincident pair straddling a bin edge is still counted. A raw count of those
falls whenever trains thin, so it
is scored against the same circular-shift null, restricted to the ROIs both folders
carry:

| stream | excess near-coincidence | fell in | still above surrogate (z > 2) |
|---|---|---|---|
| fast | 0.091 → 0.055 | 59 / 83 | 60/82 → 42/80 |
| slow | 0.148 → 0.065 | 54 / 81 | 55/80 → 43/80 |

The denominators move because the measure is undefined where a recording has fewer
than two ROIs with events in the window, and `z` additionally needs a surrogate spread
above zero; `z > 2` is the conventional two-sigma line and nothing here turns on its
exact placement.

⚠ Both measures score the **baseline region as sent**. Neither folder ships
`analysis_start_sec`/`analysis_end_sec`, so both fall back identically and the
comparison is like-for-like — but this is the raw period, not the 20-minute backward
cap that `region_windows` applies elsewhere in bugarach. A re-run of the assembly
control will use whatever window that path derives, and these numbers are not it.

## It is consistent with the store the historical control used

Three quantities the assembly report published from the `.mat`-against-`.mat`
comparison were recomputed here from the two folders, by a different route through a
different medium:

| the report says | measured from the folders |
|---|---|
| "retains 65% of fast events and 58% of slow" | **64.7%** fast (168,998 → 109,353), **57.7%** slow (95,541 → 55,174) |
| "coordinated clusters at K = 3 fall from 0.35 per minute to 0.05" | median **0.379 → 0.050** on fast |

Two published quantities, four numbers, all landing at the precision they were stated
to. That is not proof of
identity — the published values are quoted to two significant figures, so agreement at
that precision is weaker evidence than four matches make it feel — but it is strong
enough that the control should be **re-run rather than re-litigated**, and it would be
surprising if a different subtraction produced it.

## What `bugarach check` says

```
84 recording(s), 84 conforming
CONFORMING
```

No refusals, no warnings. Every advisory line is the one about ROIs with no declared
silence, and the file shape answers it: these are two-stream recordings, so an ROI
quiet in `fast` is still named by its `slow` rows. Because `check` runs
`region_windows` over every recording, this also says the windowing convention accepts
all 84 — the failure that halted 83 of 85 recordings in the pre-trimmed export of
2026-08-17 does not recur.

Every number in `PROVENANCE.md` reproduces from the files: 84 recordings, 2,479 ROIs,
164,527 events, 275 silent `(roi, stream)` pairs, 238 regions, `20250731_149` absent,
both short trailing treatments absent from `regions.csv`.

Structurally it is clean. One column set across all 84 recording files
(`roi, time_sec, stream, width_sec, width_def, peak_sec, amp`), UTF-8, no carriage
returns, no duplicate `(roi, stream, time)`, no negative or non-finite times, every
per-ROI train in time order, no `peak_sec` before its `time_sec`, no non-positive
width. Both sidecars join to the recordings in both directions with nothing left over,
and `n_roi_recorded` agrees with the file it describes on all 84.

The `width_def` audit the provenance asks for holds. On `slow`, `peak_sec − time_sec`
reproduces `width_sec` for 55,168 of 55,174 events; the six exceptions differ by
exactly 1 × 10⁻⁶ s, which is the printed precision and not a discrepancy. On `fast` it
does not reproduce it — 21 coincidental matches in 109,353 — which is what should
happen, because `fast` carries a real half-prominence width and `slow` carries a rise
interval.

## It pairs with `2026-08-18_revised_2v_periods`, and with nothing else

**Use the periods export as the "original" arm. Not `_v2`.** `_v2` carries
`analysis_start_sec`/`analysis_end_sec`, so it is scored on the producer's analysis
window while pensub — which sends no `analysis_*` columns — falls back to the derived
one. That difference has already moved a slow-stream indicator by 0.377 on a single
recording, larger than the effect it would be used to measure.

Against the periods export the pairing is exact where it has to be:

- the same 84 recordings, none on either side alone
- `regions.csv` **byte-for-byte identical** — verified with `cmp`, not compared row by row
- the same frame interval (0.1 s) on every recording
- the same `group_id` (DI, MALE, ORX, OVX) and `mouse_id` on every recording
- `slices.csv` differs in exactly one column, `n_roi_recorded`

Both were written from `_alive` stores off the same `revised_2v` archive and both
honour db4's `exclude` flag. That last bullet is the only substantive sidecar
difference, and it is the real one: the two stores do not carry the same ROIs.

## Four things for the producer

**1 · The ROI rosters are not nested, and five ROIs go the wrong way.** The pensub
store carries 2,479 ROIs against the reference's 2,630, differing on 39 of 84
recordings. 156 ROIs are in the reference and not in pensub, which is what a
subtraction-specific dead-ROI roster should do. But **five ROIs are in pensub and not
in the reference** — `20241002_72` roi 16, `20250806_176` rois 30 and 37,
`20260226_282` roi 11, `20260303_290` roi 26. An ROI that survives the subtracted
store and not the raw one is worth a sentence, because subtraction removing a reason
to discard an ROI is less obvious than subtraction creating one. **This is a question,
not a filter** — which ROIs are alive stays the producer's call (contract rev 6), and
nothing here will second-guess it.

The roster is not, however, what drives the event loss. Of the 100,012 events that
disappear, only 5,566 belong to ROIs the pensub store dropped; 94,446 come off ROIs
both stores keep. Restricted to the shared ROIs, retention is 65.3% fast and 58.7%
slow — the same numbers.

**2 · Two recordings gain events, and the gain is broad.** `20240814b49` rises 20.3%
(6,100 → 7,338) with 30 of 43 ROIs up on `fast`, and `20240815a51` rises 33.8%
(659 → 882) with 14 of 24 ROIs up. Unmasking is a real mechanism — remove a bright
neighbour's bleed-through and a small transient underneath it can cross threshold —
and the breadth across ROIs fits that better than a single bad trace would. Worth a
confirmation, since these two will pull against every other recording in the control.

**3 · The provenance stamp says contract revision 3.** The folder actually satisfies
revision 5 — it sends `width_sec` with a per-stream `width_def`, which rev 3 never
asked for — and revision 6. Only the stamp is stale, and it is stale in the same way
in three of the four export folders. It is what a later reader will trust.

**4 · Events past the last region end, in four recordings** — 375 in `20240708_13`,
639 in `20240815a51`, 38 in `20241122b_110`, 449 in `20260702_338`. Two are explained:
`20240815a51` and `20260702_338` are exactly the recordings whose short trailing
treatment the exporter drops, so those events are the dropped condition. The other two
have region tables that stop before the recording does. **This is not a pensub
defect** — the reference export does the same on the same recordings, with larger
counts (1,311 in `20240708_13`). It is legal under the contract, and those events are
silently never scored. It belongs in a conversation about the exporter.

## What this unblocks, and one caveat on the re-run

`tools/assembly_pensub_compare.py` can now run folder-against-folder — `--store`
takes an export folder and prefers it over a `.mat` store:

```
python tools/assess_archive.py --assemblies \
    --store <exports>/2026-08-18_revised_2v_periods --out <dir>/run_main
python tools/assess_archive.py --assemblies \
    --store <exports>/2026-08-20_pensub_revised_2v --out <dir>/run_pensub
python tools/assembly_pensub_compare.py \
    --main <dir>/run_main/assessment_real.json \
    --pensub <dir>/run_pensub/assessment_real.json --k 3
```

**Do not expect the counts to land on 21-of-26 and 21-of-25 exactly.** The historical
control quotes its denominators out of **85** recordings ("49-of-85 against 28-of-85");
both export folders honour db4's `exclude` and hold **84**. A re-run is a
re-derivation on a corpus the producer has since narrowed by one, not a reproduction —
so if a count moves by one, that is the reason, and 84 is the right corpus.

Once it has run, the `⚠` on the crosstalk control in `docs/assembly_report.md` comes
off and
[`docs/todo/2026-08-20-the-crosstalk-control-needs-a-pensub-export.md`](../todo/2026-08-20-the-crosstalk-control-needs-a-pensub-export.md)
closes. Until then it stands: the numbers are not withdrawn, and nothing in the current
inputs has yet reproduced them.

---

*Checked 2026-08-20 against `2026-08-20_pensub_revised_2v` and
`2026-08-18_revised_2v_periods`. Conformance by `bugarach check`; the primary
coordination measurement by `bugarach assess` at 200 surrogates. The structural,
differential and near-coincidence measurements were written for this review and are not
repo tooling — every number above names the folder and the tool it came from. Reviewed
by the murderboard; run record in
[`pensub_export_validation_murderboard_2026-08-20.md`](pensub_export_validation_murderboard_2026-08-20.md).*
