# The every-knob search on the ADOPTED fast bench

**Run 2026-09-23, 03:03–03:17 on WSMIP065**, 13.6 minutes, 12 workers.
`tools/search_all_settings.py --bench fast --sliding`, on `main` at `534f24c`, which **contains
`2c19003`** — the adoption (#756). Verified by ancestry before launching, not assumed: fast probe
**0.1271 Hz** and quiet background **0.0042 Hz** were read out of the running module.

The integer-floor fix (#755) is in force, so `min_rois` and `min_n` step as counts.

**This changes nothing.** `bench.OPERATING_POINTS` is not edited; adopting any point below stays
Tony's, as it was for the slow reference.

Abbreviations: **F1**, the harmonic mean of recall and precision; **ROI**, region of interest.

## Held out, against the settings in force

| detector | shipped | pick | gain [95%] |
|---|---|---|---|
| **LoCo** | **0.750** | — | **nothing in its grid beat it** |
| CoactDetect | 0.720 | 0.754 | +0.035 [+0.026, +0.044] ⚠ |
| SPIKE-synch | 0.646 | 0.699 | +0.052 [+0.041, +0.065] |
| locust | 0.608 | 0.667 | +0.060 [+0.048, +0.071] |
| rate+context | 0.652 | 0.657 | +0.006 [−0.000, +0.012] |
| binned SCE | 0.474 | — | nothing beat it |

**LoCo's shipped point is still the best single number on this bench**, and the search could not
improve it. Two of six came back unimproved, against zero on combined — the fast settings have
been searched before, and it shows.

**rate+context's interval touches zero** (−0.000). It is reported as a gain because the midpoint
is positive, but it is not separable from no change and should not be read as one.

## ⚠ CoactDetect's pick is inadmissible by the crowded rule

Its crowded-recording score is **−0.021** against a `MAX_CROWDED_DROP` of **0.020**. One
thousandth over, and over. The pick is: alpha 1e-4 → **3e-5**, context 60 → **120 s**, merge gap
3 → **8 s**.

That allowance is itself the unsigned 0.02 constant WSMIP064 spent a sweep measuring, so a pick
sitting one thousandth outside it is a question about the constant as much as about the pick.

## Where SPIKE-synch lands

#756 established that on the re-anchored axis SPIKE-synch is **flat** and **wins the busy end**
— fourth at 2.1 mHz/ROI, first at 25 mHz (0.665 against LoCo 0.657, CoactDetect 0.633) — and
that this follows from its flatness on the measured jitter, ruled a result rather than a defect.

Its search gain here, **+0.052**, is the second largest of the six. So on the adopted bench it
both wins the busy end untuned *and* has more headroom than CoactDetect does.

⚠ **What none of this settles**, and #756 says so itself: whether a bench whose busy end is won
by a detector that cannot see the axis is the bench these searches should run on. A flat detector
*should* win where the others have degraded. But it changes what "best at the busy end" means —
partly "least sensitive to the thing the axis varies" — and every number in the table above was
measured on exactly that axis. The gains are valid as measurements of each detector against this
bench. They do not establish that this bench's busy end asks the right question.

## ⚠ `C_min` 0.0025 for the third time

SPIKE-synch's pick again puts `C_min` at **0.0025** — one eighth of its 0.02 grid floor, three
halvings, `MAX_EXTENSIONS` exhausted. That is now **slow, combined and fast: the same value on
every bench it has been searched on.**

On combined this was tested rather than assumed: pinning `C_min` back to the grid floor of 0.02
costs **nothing at all** (`2026-09-23-full-search-combined-sync-rerun`). The parameter is flat
across 0–0.03 because the profile steps by about 1/31, so the edge rule walks a plateau and
reports where it stopped as though it had chosen. The same is almost certainly true here; it was
not re-tested, because one bench establishing a parameter does nothing is enough to stop reading
its extension as a finding.

## A caution about this record's own `null_per_hour` column

**Do not read it as a budget verdict.** It is computed on few seeds and is noisy enough to invent
violations. On this run it reported LoCo at 4.00 calls/hour against a budget of 3.0 and
CoactDetect at 7.69 against 7.0. Measured properly over 24 seeds, **every shipped fast setting is
within all three budgets**: LoCo 1.72, CoactDetect 3.28, precision swings 0.073 and 0.063 against
0.10, probes 0.17 and 0.07 per minute against 1.0.

The same column produced a false flag on the slow run. It cost a correction on both.

The search's own *"the starting point breaks a budget"* message in round 1 is the same thing seen
from inside: an admissibility check on the selection seeds, not a standing violation.
