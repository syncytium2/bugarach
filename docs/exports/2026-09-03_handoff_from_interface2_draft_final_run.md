# Handoff -- the draft-final-run folder, and the artifact caveat on it

**From:** interface2 / `065/export-contract` | **2026-09-03**
**To:** bugarach | **Re:** the export folder for the **draft final run**

**One line: the folder is built, verified against your `origin/main`, and delivered. It is
deliberately labelled `PRE_ARTIFACT_KILLER`, because whole-field brightness steps that
produce FALSE COORDINATED EVENTS are still in it.**

```
<data>/exports/bugarach/2026-09-03_revised_2v_long_PRE_ARTIFACT_KILLER/
```

`<data>` is the shared data root -- `$BUGARACH_DATA_ROOT` on your side (kept out of this
file per your SAP004 / FOUNDATIONS section 5). A `README.md` sits
beside the CSVs and is the authority; this document is the same content routed to your
repo, because a note in interface2's `docs/` cannot reach you.

---

## 1. What changed since the folder you have

| folder | periods | analysis windows | width/peak/amp | use |
|---|---|---|---|---|
| `2026-08-17_revised_2v` | defective | -- | no | **quarantined** |
| `2026-08-17_revised_2v_v2` | yes | yes | **no** | **quarantined** |
| `2026-08-18_revised_2v_periods` | yes | **no** | yes | superseded |
| `2026-09-02_revised_2v_long` | yes | yes | yes | superseded on labelling only |
| **`2026-09-03_..._PRE_ARTIFACT_KILLER`** | yes | **yes** | yes | **<- this one** |

**Two things to unlearn from our earlier correspondence.**

1. **Our reply doc sent you to a quarantined folder.** `docs/exports/2026-08-17_bugarach_import_contract_reply.md`
   in interface2 named the `2026-08-17_*` pair in section 1 and section 8; both went to `_quarantine/` on
   2026-08-20. It now carries a SUPERSEDED banner. That document already cost a session,
   which opened `_v2`, found only `roi,time_sec,stream`, and concluded the contract does
   not deliver a per-event width or peak. **It does.**
2. **That reply's section 7 prose is wrong about windows.** It says *"It is now stated in the file
   as `analysis_start_sec`/`analysis_end_sec`"* while its own table says `windows="raw"`.
   The prose predates the 2026-08-18 default flip and was never updated. **Read the table,
   not the paragraph** -- and for this folder, read this document.

## 2. You are now getting analysis windows, by decision

Tony, 2026-09-02: bugarach gets the full available data, the treatment windows **as defined
in db4**, and **analysis windows defined by him at export** -- here the `long` paradigm.

`regions.csv` therefore carries **four** bound columns:

| columns | meaning |
|---|---|
| `start_sec` / `end_sec` | **what happened** -- the raw, untrimmed db4 period |
| `analysis_start_sec` / `analysis_end_sec` | **what to score** -- `long_window_20` |

**`long_window_20`:** baseline is the last **20 min backward from baseline end**; every
other treatment gets a **2-minute wash-in delay** then a **20-minute forward cap**,
anchored on **that treatment's own start**; **high K+ is exempt** from both the delay and
the cap. `region_min_sec = 900`.

> **WARNING: There are several timing regimes and they are not interchangeable.** Which applies
> depends on the detection routine, the hypothesis, the analysis and the consumer, and
> **Tony names it per export.** Two of our folders disagreeing on windows is the design,
> not a defect. **This folder is `long_window_20`, and `PROVENANCE.md` states it on the
> record.** Please do not infer the regime from the numbers or re-derive it -- read the
> sidecar. A future folder may carry a different regime and will say which.
>
> On our side this is now enforced rather than remembered: `generate_export_folder`'s
> `windows=` argument has **no default**, and omitting it raises `if2:windowsUnspecified`.
> Every export request must name its regime, or we come back and ask you.

## 3. WARNING: What supplying these windows costs you -- your open item

`supplied_region_windows` short-circuits **before** the baseline-at-0 and contiguity
checks, so a folder carrying `analysis_*` has its **raw** `start_sec`/`end_sec` validated
by **nothing on your side**. That is item 3 of the reply's section 8, still open.

**We have covered it on ours, so this is not a gap in what you received:**

- the exporter **refuses to write** a non-finite, unordered, or out-of-period analysis
  window (it errors, naming slice and region);
- our verifier runs **your** `region_windows` over the **raw** bounds of all 84 recordings
  independently -- check [3] below.

Worth closing on your end anyway, because the producer supplying `analysis_*` is exactly
the one nobody else is validating.

## 4. RED FLAG: THE CAVEAT -- field-step artifacts are in this data

**Whole-field brightness steps trip the detectors and produce false coordinated events.**
Measured 2026-09-03 over the **9 steps Tony confirmed** in the trace waterfall viewer.

**376 events of 23,666 (1.59 %)** from those 9 slices have their **onset** inside a
confirmed step.

| stream | slot | exported | onset in step | % |
|---|---|---:|---:|---:|
| fast | baseline | 3045 | 71 | 2.33 |
| fast | treat1 | 7051 | 40 | 0.57 |
| fast | treat2 | 4802 | 71 | 1.48 |
| slow | **baseline** | 1250 | 91 | **7.28** |
| slow | treat1 | 2217 | 50 | 2.26 |
| slow | treat2 | 1956 | 53 | 2.71 |

**The 9 affected slices, with step time:**

```
20240708_17  @  167.0 s     20250826_192 @  653.8 s     20260122_259 @  448.0 s
20260701_331 @ 1401.0 s     20250911_222 @ 1642.0 s     20260707_346 @ 1990.7 s
20250808_186 @ 3057.0 s     20250904_211 @ 3530.0 s     20240723_22  @ 3820.1 s
```

The other 75 recordings carry no **confirmed** step.

**Four things this number is not:**

1. **It is the population AT RISK, not a correction.** A real transient can occur during a
   step. **376 is the most that could need excluding, not a count of false events.** We
   have excluded nothing.
2. **SLOW baseline at 7.28 % is UNEXPLAINED**, and the two readings differ in consequence:
   either a step is arithmetically more likely to land inside a broad SLOW event, **or a
   whole-field step is itself SLOW-shaped and is generating SLOW calls.** If the second,
   this is not a coincidence problem at all. Our data does not separate them. **This is the
   one we would most want your eyes on**, since CICADA keys on duration.
3. **Confirmed steps only, and it can only go up.** 282 further candidates are
   unadjudicated (168 reverting spikes rather than steps); 4 on `20240930_65` were rejected.
4. **`treat3` is zero because no confirmed step fell in a treat3 window** -- an absence of
   steps, not protection.

WARNING: **Denominator discipline.** 1.59 % is over the **9 affected slices** (23,666 events).
Over the whole export (264,539, confirmed by gate [2]) the same 376 are **~0.14 %**.
Neither figure should be quoted without naming which denominator it uses.

## 5. What we will send next, so you can plan

**Flag, do not drop.** The successor folder will carry a per-event **`on_field_step`** flag
plus **`field_step_id`**, and will remove nothing -- dropping would delete real transients
that merely coincide with a step. Under your spec extra columns are ignored, so the flag
costs you nothing until you choose to read it, and it makes the false-coordination question
answerable rather than unanswerable.

**The step table will NOT arrive as a `.csv` in the folder root.** Your loader treats every
`.csv` except `slices.csv`, `regions.csv` and `metric_dictionary.csv` as a recording, so a
`field_steps.csv` would be parsed as a recording named `field_steps`. It will go in
`PROVENANCE.md` or as a `.tsv`. (Checked: adding `README.md` kept the folder conforming.)

**Whether a coordinated event built from flagged members is itself false is your call on
your output.** We supply the input to decide with. We are not writing rules for your
detections -- we drafted some, realised it was not ours to do, and retracted them.

## 6. Verification -- against your `origin/main`, not a local checkout

```
[1] bugarach check      84/84 conforming
[2] round trip          264,539 events vs the store, 0 mismatches, max |delta| 5e-07 s
[3] region_windows      OK 84, FAILED 0   (run on the RAW bounds)
[4] analysis windows    238 checked, 0 unusable
[5] event properties    264,539 events, 0 unusable; width_def correct per stream
[6] NA-row power        report only -- 78 of 122 NA rows load-bearing
PASS (5 gates)
```

**Verified at `d18b921`** (`origin/main` at time of writing). Stated because it matters:
this box's bugarach checkout was stale at `af7fc22` with no `conform.py`, and the only
local copy that had one sat on an unmerged branch -- a green result from either is
attributable to nothing. We extracted your `origin/main` read-only and ran against that.

**Two of your API changes bit us, both now handled:**

- `load_slice` requires the `dt` keyword. Our verifier omitted it and raised `TypeError`
  **after** `[1] CONFORMING` had already printed -- so the run looked verified and was not.
  Fixed, passing `dt=None`, which your docstring documents as "not known here"; those
  checks read times, widths and amplitudes and compute no rates.
- `conform.py` does not exist at `af7fc22`, which is why a stale checkout fails oddly
  rather than clearly.

**238 regions, not 240.** Two trailing treatments under 240 s were dropped as *inclusion*,
not windowing -- the condition was never delivered and no analysis window rescues it. Both
named in `PROVENANCE.md` under "Regions removed by inclusion".

## 7. Two properties that are easy to get wrong

- **`width_sec` is not the same quantity in both streams.** `fast` is a real transient
  width (`halfprom_width_findpeaks_w`); `slow` is the **rise interval**
  (`rise_interval_peak_minus_t50rise`). **Key on `width_def`, never the column name** -- on
  `slow`, `peak_sec - time_sec` reproduces it exactly; on `fast` it does not and should
  not. The SLOW substitution is ours and predates your port (`explore_sce.m:481`).
- **A silent ROI is one row with `time_sec = NA`**, per (roi, stream) -- 122 here. They are
  the population, not padding: strip them and 8 of 84 recordings lose ROIs entirely (39
  ROIs), inflating every per-ROI rate.

## 8. What we would like back

1. **Confirm you are reading `2026-09-03_revised_2v_long_PRE_ARTIFACT_KILLER`**, and that
   the `analysis_*` columns are being used as given.
2. **Your read on section 4 item 2** -- could a whole-field brightness step *generate* SLOW calls,
   given CICADA keys on duration? That changes what the artifact work has to do.
3. **The `supplied_region_windows` gate fix** (section 3), still open from the reply's section 8.
4. **Tell us if anything looks wrong rather than working around it.** The folder is
   reproducible: `generate_export_folder(out, windows="both")` on interface2 branch
   `export-contract`, verified by `tools/verify_export_folder.py`.

---

**Delivered on branch `handoff-from-interface2-pak` rather than committed to your `main`,
because two of your sessions are live and we did not want to write into a checkout we did
not create.** Merge, cherry-pick or discard as you prefer.
