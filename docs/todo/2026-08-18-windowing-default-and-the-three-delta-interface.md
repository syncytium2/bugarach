---
status: open
filed: 2026-08-18
---

# The windowing default, decided — and the interface that replaces the guessing

**Read this before editing `docs/export_folder_spec.md`.** Two sessions were working on
that file at once on 2026-08-18. This is the design half, written down so the cleanup
half does not have to reconstruct it from a conversation it cannot see.

> **Point 4 is built, 2026-08-23 — for detection.** `bugarach detect <folder>` is the
> first consumer to have it: `detect_folder.with_folder_windows` settles a recording's
> windows **once, before any detector sees it**, writing the raw period bounds into the
> region rows as analysis windows where the producer stated none. Every detector then
> reads them through `supplied_region_windows`, so no protocol is applied and the two
> HALT guards never fire — and that reaches `sce_detect` and `cicada_detect` too, which
> derive their own windows internally and have no argument to divert. `region_windows`
> is untouched, as the constraint below requires. A baseline at 500 s with a 900 s gap
> after it is detected on; the same slice still raises out of `region_windows`. Both are
> asserted in `tests/test_detect_folder.py`.
>
> **Also confirmed while building it:** the design's safety argument — *"it moves no
> number this project has already measured"* — **does not hold for the two folders on
> this machine.** Neither `2026-08-18_revised_2v_periods` nor
> `2026-08-20_pensub_revised_2v` carries `analysis_start_sec`/`analysis_end_sec` on any
> of its regions, so both take the new default rather than the corrected export's. The
> claim was true of `2026-08-17_revised_2v_v2`, which is not what is in the exports
> directory now. Anything comparing a detection run against a MATLAB campaign has to
> reckon with that, and the fix is a producer conversation, not a consumer default.
>
> **Still not built:** the three-delta interface (point 5), the baseline *designation*
> that the open question below asks for, and the same default for assessment,
> simulation and optimization — `assess_coactivity`'s `window=None` path still derives,
> which is correct for the `.mat` store it is parity-tested against.

Tony's decision, 2026-08-18. It settles
[`2026-08-17-windowing-convention-is-not-optional.md`](2026-08-17-windowing-convention-is-not-optional.md),
which has been open since the contract shipped because it needed a scientific call
rather than a patch.

## The shape

1. **The producer exports full rasters plus treatment timing, whatever the goal.** No
   analysis-specific export. One folder serves every downstream question.
2. **Slice inclusion is the producer's.** Which recordings qualify — TTX and/or
   senktide, not APV+CNQX — is decided before the folder is written, as it is today.
3. **Analysis windows stay optional.** A producer with a policy states it, exactly as
   revision 3 already allows.
4. **With no analysis windows, bugarach applies no protocol at all.** It uses the
   **full-length baseline only**, for assessment, simulation and optimization.
5. **A basic interface lets the user define the windows they did not send** — three
   deltas relative to the treatment timing already in the folder.

The three deltas, precisely:

```
baseline window  = [baseline_end - base_dur,  baseline_end]
treatment window = [treat_start + solution_delay,
                    treat_start + solution_delay + treat_dur]
```

`base_dur`, `treat_dur`, `solution_delay`. Nothing else, and in particular **no label
special-casing**.

## Why the change is safe to make

**It moves no number this project has already measured.** interface2's corrected export
(`2026-08-17_revised_2v_v2`) supplies `analysis_start_sec`/`analysis_end_sec` on **all
240 regions** of all 84 recordings, so the no-windows default never fires for our own
folder. The default only ever applies to a producer who had no policy of ours to inherit
— which is exactly the population it is wrong for today.

That sentence belongs in the spec, because "we changed the windowing default" otherwise
reads far more alarming than it is.

## What is already built, and what is not

**Point 4 is already the behaviour for assessment.**
[`assess_folder.py:143-150`](../../src/bugarach/assess_folder.py#L143-L150) takes the
producer's analysis window where one exists and otherwise falls back to
`(r.start_sec, r.end_sec)` — the whole baseline period, **uncapped** — naming in the
report which of the two it used. So this is not new work there; it is generalizing an
existing rule to the two consumers that lack it.

**Simulation and optimization do not have it.** They reach windows through
[`assess.py:266`](../../src/bugarach/assess.py#L266), which calls
`effective_region_windows` and therefore falls through to `region_windows` — this
project's convention — whenever the folder states nothing. That fall-through **is** the
bug this decision fixes.

**Detection has it as of 2026-08-23**, and it is the consumer where the fall-through was
fatal rather than merely wrong: `sce_detect` and `cicada_detect` derive their windows
inside themselves and take no argument that could divert them, so the only place the
decision *can* be applied for all six is on the recording, before the call.
`detect_folder.with_folder_windows` does exactly that and nothing else.

**The interface does not exist in any form.**

## What this kills, and the constraint that comes with it

The prize is the substring rule. [`loco.py:132`](../../src/bugarach/detectors/loco.py#L132):

```python
is_hik = (not is_baseline) and ("hi" in name.lower())
```

Any region whose label contains those two letters is exempted from both the delay and
the cap. interface2 verified the trap in both directions (their
`bugarach-export-folder` branch, 2026-08-18): `histamine` and `washin` trip it —
`chelerythrine` does **not**, and our spec is wrong to say it does — and renaming
`high K+` to `KCl` or `elevated K+` would silently begin trimming all 60 high-K windows
with nothing on either side failing. Three deltas and no substring match removes the
whole class.

**The constraint: `region_windows` must not be edited.** It is a 1e-9 parity port of
`if2_region_windows` and FOUNDATIONS §2 makes that parity the product. The hi-K rule
stays *there*. The new behaviour is a **separate path**, which is what FOUNDATIONS §4
already requires — "the two paths must not be merged". The store keeps the aCa5z
convention; the folder gets none. Today's defect is precisely that the folder path falls
*through* into the store path.

## The open question this design must answer

**What makes a region "the baseline"?** "Baseline only for assessment, simulation and
optimization" cannot be implemented without a rule, and **three rules exist in the tree
today, two of which disagree**:

| where | rule |
|---|---|
| [`assess_folder.py:38`](../../src/bugarach/assess_folder.py#L38) | label prefix — `baseline`, `base`, `pre`, `control`, `acsf` |
| [`loco.py:131`](../../src/bugarach/detectors/loco.py#L131) | positional — `k == 0` |
| [`assess.py:271`](../../src/bugarach/assess.py#L271) | positional, inherited via `RegionWindow.is_baseline` |

Neither existing answer is clean. Positional contradicts the spec's own "no privileged
region, and no protocol vocabulary". Label-matching silently assesses **nothing** for a
lab that writes `ctrl` or `0 min` — and note that `assess_folder` deliberately refuses to
fall back to region 1, because the spec names that as something producers must not do.

There is also an asymmetry worth resolving while it is being touched: a folder with **no
`regions.csv` at all** is assessed over its whole extent and says so, while a folder
**with** regions but no recognizable baseline gets nothing. Those two absences are
treated very differently for no stated reason.

**Suggested resolution:** the interface already puts the user in front of the windows, so
make the baseline a **designation** rather than a guess. That makes it three deltas plus
one selection, not three deltas — and it removes the label vocabulary from the code
entirely instead of extending it.

## Two things the implementation must get right

**The deltas need clamping.** `baseline_end - base_dur` runs before the baseline start
whenever `base_dur` exceeds the period; `treat_start + solution_delay + treat_dur` runs
past `treat_end` on a short application. `region_windows` already clamps
(`min(raw_end - raw_start, baseline_window_max_sec)`) and the generator must too.

**The gate that catches it if it does not is already on `main`.** PR #123 made
`supplied_region_windows` refuse an analysis window falling outside its own period, so
the window generator's output is checked by the same door a producer's is. Write the
generator to emit `analysis_*`, and it is validated for free.

**Detection is deliberately not in the list.** Assessment, simulation and optimization go
baseline-only — FOUNDATIONS §9, *"everything should be based on baseline recordings"*.
**Detection runs every region**, or the tool cannot do the thing it exists for. This is
the one point in the design that can be misread, so it should be stated in the spec
rather than implied.

## One gap this leans on harder

Producer-side inclusion is right and is what the contract already asks for. But **the
folder has no way to say a recording was withdrawn**, so it cannot distinguish "this
folder is complete" from "someone dropped twelve". Leaning more weight on producer-side
inclusion makes that gap more load-bearing, not less. interface2 raised it independently.
An optional `excluded` column, or a count the folder can state, would close it — see
[`2026-08-18-experimental-groups-are-not-in-the-import-contract.md`](2026-08-18-experimental-groups-are-not-in-the-import-contract.md).

## For the session cleaning up the spec

The document has grown **260 → 444 lines in six commits over two days**, and every one of
those commits added an incident narrative to a contract a stranger is meant to read:

| commit | lines | |
|---|---|---|
| `1be5170` | 260 | the murderboard on the contract |
| `2e9406b` | 292 | the validator |
| `a198567` | 317 | the window gate |
| `5339eff` | 357 | revision 3 — the two window pairs |
| `f986ec0` | 394 | revision 4 — group and subject |
| `748a4e0` | 444 | the analysis-window guards |

The last 22 are mine and are the most cuttable thing in the file: roughly six normative
lines about what is refused, wrapped in sixteen about how interface2 found it. **Cut them
to the normative core without asking** — the incident is recorded here and in the commit
message, which is where it belongs.

The structural suggestion, worth more than any individual trim: the revision-header stack
is doing two jobs badly. A producer needs the *current* contract; a bugarach session needs
*what changed and why*. Splitting those into one clean spec plus a `CHANGES` section at
the bottom takes roughly 120 lines out of a reader's way and loses no incident.

## Also unrecorded, and relevant to anyone editing this spec

**interface2 replied to the export request on 2026-08-17, revised 2026-08-18, and nothing
in this repo mentions it.** It is `docs/exports/2026-08-17_bugarach_import_contract_reply.md`
on their **unmerged** branch `bugarach-export-folder`, alongside `generate_export_folder.m`
and `tools/verify_export_folder.py`. Their own todo still reads `status: open` and cites
spec **revision 2**; we are on 4.

Four spec corrections they asked for, none applied:

- The `baseline` mechanism. Our spec says the exporter "overwrites the first region's real
  name" and that "its original name is lost". **Both are wrong** — db4 has no column for a
  baseline name, so nothing is discarded. `if2_load_exp_timing.m:59` assigns the literal.
  The practical advice ("read region 1's label as *whatever region 1 was called*") is right
  and should stay; the mechanism sentences should go. Read region 1's label as a constant,
  not as data.
- The `NA` argument splits by file shape. In a **single-stream** file an `NA` row saves
  every silent ROI; in a **multi-stream** file it saves only ROIs silent in *every* stream.
  Our 1.47× worked example is correct — they retracted a claim that it was not.
- The `hi` rule: `chelerythrine` does not contain `hi`, and the trap is **wider** than
  bounds — `if2_norm_treatment` maps `startsWith(s,'hi') → 'high K+'`, so a future
  `histamine` region would arrive *renamed to a different drug*.
- "Five columns, and none of them derived" now sits below a seven-column table.

Two further things they reported that this repo has not recorded anywhere:

- **The folder we verified is the defective one.** `2026-08-17_revised_2v` halts 83 of 85
  recordings; `..._revised_2v_v2` is the corrected one. `docs/SESSIONS.md` lists both
  without saying which.
- **The labels we receive are raw db4 free text, not normalized** — six spellings of hi-K
  across 60 regions. Our exemption is correct *by luck*. If they regenerate the stores the
  vocabulary collapses under us, which is another argument for the design above.

## Still open, and untouched by any of this

`frame_interval_sec` is validated by `conform.py` and **wired to no detector**.
`rate_detect` raises `GridDtNotSetWarning`; `cicada.imaging_rate_hz` stays `10.0` in
silence for a rig that is not 10 Hz — the failure the field exists to prevent. See
[`2026-08-16-dt-does-not-travel-with-the-recording.md`](2026-08-16-dt-does-not-travel-with-the-recording.md),
which argues the interval should become a property of the recording rather than an
argument to three detectors, and warns that it touches the fixture chain against a 1e-9
bar.

## Review status

**Not murderboarded.** Written under an active two-session collision, where being readable
today beats being polished tomorrow. Every file, line number and count above was verified
against the tree at `39acdd1` rather than recalled; the interface2 claims were read from
their branch, not summarized from memory. The design itself is Tony's and is recorded, not
evaluated. **If this becomes the spec revision, run `/murderboard` on that** — the counts
and parity claims in it are exactly the class CLAUDE.md requires it for.
