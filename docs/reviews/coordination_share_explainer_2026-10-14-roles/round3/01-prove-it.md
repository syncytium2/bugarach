GRANT 1 ok — Read, Grep, Glob, Bash

Role 1, Prove It. I reviewed the README and its six PNGs in `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\`, which is the state committed in fd252301. I recomputed numbers from numbers.json and the sources. I also re-ran parts of the generator with the venv python, inline and read-only; nothing was written outside scratch.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against a source? |
|---|---|---|---|---|---|
| 1 | README "The question", last paragraph: "One input comes from real recordings: the bench's intervals between moments (Figure 3C), measured on the default data set…" | **False as stated.** Every simulated recording, not only Figure 3C, uses several constants measured on real recordings: the quiet and busy backgrounds 0.0049/0.0169 (`bench.REGIMES`), the per-cell rate shape and burst shape (`MEASURED_RATE_SHAPE`, `MEASURED_BURST_SHAPE`), the jitter 0.106 s, the moment sizes (participation 0.203 → 6 cells), the cell count 32, and the stretch level 0.1334 Hz. `bench.py:896` and `:1056-1071` record that REGIMES, participation and hot_rate_hz were re-measured on 2026-09-23 "on the default folder's 66 recordings", which is `senktide_ttx`, the folder under the contamination stop. The backgrounds were also computed as raw rate minus *this tool's* fixed-model coordinated share, so the backgrounds the page uses to test the tool are partly the tool's own output. | major | Replace with: "Every simulated recording takes its background rates, clumping, jitter, cell count and moment sizes from real baseline recordings, and Figure 3C also takes its intervals from them. The backgrounds, moment sizes and the stretch level were measured on the default data set now under the contamination stop. The backgrounds have this measure's own coordinated share subtracted." Make the Terms entry "Quiet and busy" say the same. | yes (`src/bugarach/bench.py` 890-900, 1023-1071; `current_export.toml` default + STOPPED note) |
| 2 | README "How far one recording strays", bullet "Real recordings are nearer the narrow end of moments. The bench's realistic intervals give about 7 moments per 45 minutes…" | **One number pooled across the four groups hides a tenfold difference between them.** The rate is right: 9.72 events/h × 0.75 h = 7.3, so 7. But it comes from `2026-09-25-real-intervals/summary.json`, pooled over DI 20.5/h, OVX 3.4/h, MALE 15.0/h and ORX 2.1/h. Over 45 minutes that is about 15, 3, 11 and 1.6 moments. "Real recordings" are not near 6 moments: DI sits at the 15-moment group, while ORX sits below the 3-moment group. DI is also the group holding all four contaminated recordings and 116 of the 212 events. FOUNDATIONS §9 and `bench.py`'s own docstring treat a pooled number as inadmissible on its own. | major | Give the range by group, ordered DI, OVX, MALE, ORX ("from about 15 moments per 45 minutes (DI) to under 2 (ORX)"), say the pooled 7 is what the bench plants, and note that DI's count comes from the contaminated folder. | yes (summary.json `groups`) |
| 3 | README "Window size…", first sentence: "median 41 s on the fast stream" beside "about 7 moments per 45 minutes" | Both numbers check out (p50 41.25 s; 9.72/h). A reader who multiplies them will see a contradiction, though: a 41 s median gap implies about 65 moments in 45 minutes. The reconciliation is that events clump within recordings and many baseline hours hold no events, and the page never says so. | minor | Add one clause, e.g. "events come in bursts, so a 41 s median gap goes with only about 10 events per hour". | yes |
| 4 | README "For developers": "every number quoted above is in numbers.json" | Overbroad. These numbers are not in numbers.json: 41 s, about 7 moments, 43% (CAL_NO_PROBE), 66 recordings, 6 decoys of 6 cells, 2 s merge, 300 s / 20 onsets / 5 cells, 900 s (15 min), −32/+32 s, 0.0049/0.0169 percentile provenance. All of them do check out against other sources (ledger below). | minor | Say "every number from the simulations is in numbers.json; the rest cite their source file", or name the sources. | yes |
| 5 | README "The check, and the two models": "the tool's own note on that (`CAL_NO_PROBE`) records that with the stretch in, the check fails, reading the share 43% high" | It is quoted accurately, but the 43% was measured on 2026-09-22 with the 0.127 Hz probe, the old 120 s spacing and the old backgrounds. The page presents it as current next to a 0.1334 Hz stretch and realistic spacing. | minor | Prefix with "when it was measured on 2026-09-22, at the then-probe of 0.127 onsets per second". | yes (tools/measure_coordination_rates.py:245-254) |
| 6 | README "Does it get the right answer?": "Every simulated recording here … with 15 shared moments planted per recording, 5 each joined by 10, 6 and 3 cells" | Not true of Figure 3B (every moment 6 cells) or Figure 3C (the realistic bench: 7 moments, split 2/3/2, plus 6 decoys). The sentence then lists the exceptions for Figures 5 and 6 only. | minor | Add "except Figure 3B (one size) and 3C (the bench's own, about 7 moments plus decoys)". | yes (generator `recording(size=)`, `bench.realistic_counts`) |
| 7 | README step 3: "That steadies the median over recordings, not a single recording's answer (Figure 6)" | Only half supported. Figure 6 does show that the pooled per-recording spread is not narrower. It does not test whether pooling steadies the median: the own and pooled medians are similar (0.83/0.82, 0.83/0.79, 0.87/0.83), and nothing compares how variable those medians are. The tool's stated reason is that "one recording's f3 is noisy". | minor | Drop "steadies the median" or cite where it is shown; otherwise say "the tool pools because one recording's f3 is noisy; Figure 6 shows it does not narrow a single recording's answer". | partly |
| 8 | README "What else it counts": "At the quiet background the same rise barely registers at all" | Loose. numbers.json shows the rise adds 0.00081 to the raw f₂, about 27% of the constant case's 0.0030. After subtraction the rising case reads *lower* than the constant one (rise_removed = 2.57, so over-subtracted). "Barely registers" hides that over-subtraction. | minor | Quote it: "adds about a quarter to the small raw f₂, and subtracting the copies removes more than that". | yes |
| 9 | README, last line: link `../../reviews/coordination_share_explainer_2026-10-14.md` | The target does not exist yet; only the `…-roles/` directory does. It may be written at the end of the run. | minor (process) | Make sure the record lands in the same commit, or the link is dead. | yes |
| 10 | README "Where the method comes from" (seven citations) | Volumes and pages match what I remember (Ehm, Staude & Rotter 2007, EJS 1:473; CuBIC 2010, JCNS 29:327; Kuhn, Aertsen & Rotter 2003, NC 15:67; Pipa et al. 2008, JCNS 25:64; Staude, Rotter & Grün 2008, NC 20:1973; Staude, Grün & Rotter 2010, FCN 4:16; Reimer et al. 2012, JNM 208:18). Nothing in the repo holds them. Separately, "the paper by Staude, Grün and Rotter on changing rates" is ambiguous, because two rate-change papers are cited. | minor | Role 2 should check the citations against the papers. Name the year in the "changing rates" sentence (2010, *Front Comput Neurosci*). | no |

**Unit and group record.** The page reads no real recording directly. Its real-data inputs come from the `senktide_ttx` folder: 66 recordings, groups DI 17, OVX 17, MALE 13, ORX 19, which sums to 66. The README's account of the contamination stop matches `current_export.toml` and the 2026-10-05 todo: 4 recordings, all DI; `_312` under-cut, `_309` over-cut, 3 not reviewed. It does not say that the inputs other than the intervals came from that folder (finding 1).

**Retraction check.** The README's correction that the shifted copies *do* remove most of a long stretch, against CAL_NO_PROBE's "cannot subtract it", is a new claim, so I tested it independently. I ran 3 seeds with a 900 s stretch at +0.1334 Hz on the quiet background. The copies removed 99.2%, 95.1% and 98.4% of the f₂ the stretch added. So the correction holds, and the README's statement that the module docstring (line 30) agrees is also correct.

## Claim ledger (quoted · source · recomputed · result)

- Figure 2 mean 0.44 onsets per window, recording and copy · nj fig2 · 0.4385 / 0.4385 · match
- "only the recording has windows holding 6 to 11" · nj max 11 / copy max 5 · match
- Copies' f₂ 0.03 · nj · 0.0283 · match
- Excess 0.20 / 1.21 · nj · 0.1998 / 1.2092 · match
- k ≈ 8.1 · 1.2092/0.1998 + 2 · 8.054 · match
- Planted mean 6.3 · nj · 6.333 · match
- 90 / 720 ordered pairs/triples, 720÷90 = 8 · 10·9, 10·9·8 · match
- 10-cell moment at 30m25s shown as bars 4 and 6 · regenerated seed 13 quiet · moment at 1824.99 s, k = 10; windows 1824 = 4 and 1825 = 6 · match
- Figure 1 = minutes 30–35 of quiet recording 13 · nj seed 13, 1800–2100 s · match; Figure 2 = busy recording 3 · match
- Figure 3A fixed −18%, binomial −8% · −17.7%, −7.5% · match
- Figure 3B fixed −5%, binomial +17% · −5.1%, +17.0% · match
- Figure 3C fixed −16%, binomial −2% · −15.6%, −2.3% · match
- Single recordings 0.67–1.12 · min of 0.681/0.743/0.671, max of 0.930/1.121/1.018 · match
- "up to 23%" (very close pairs) · 21.7/23.2/23.4% · match
- Fixed model 14–19% low (120 s only, medium, mixed, close at 1 and 2 s) · 13.6–18.6% · match
- Close pairs at 4 s −21% vs −14% for 120 s only · −21.2 / −13.6 · match
- Very close pairs 22–23% · 21.7–23.4 · match
- Binomial 3–17% low · 3.3–17.4 · match
- k at 4 s: +56% vs +33%; λ −49% vs −35% · 56.0/33.2; −49.5/−35.1 · match
- Very close: k +50…69%, λ −48…55% · 49.7–69.0; 47.7–54.7 · match
- All sets: k 26–69% high, λ 34–55% low · 26.5–69.0; 33.5–54.7 · match
- Medium pairs within about 5 percentage points of 120 s only · max gap 5.3 points (k at 2 s) · match ("about")
- Figure 5A: 8.2% (1 min), 3.0% (5 min), 1.2% (15 min), 3.7% (10 s), 7.9% (30 s), worst up to 14% · 8.21/3.05/1.17/3.71/7.89/13.7 · match
- 350–380 extra pairs per recording, about 1 minute and up · 364/377/369/349 · match (349 rounds to 350)
- 28 times quiet in all · (0.1334 + 0.0049)/0.0049 · 28.2 · match; stretch is additive in `simulate.py:903-914` · match
- Figure 5B: 2× 0.14%, 10× 1.0%, 28× 2.8%, about three quarters of onsets · 0.144/0.974/2.82%, 0.742 · match
- 30 s ramp, 5-minute stretch, sharp end · `ELEVATED_RATE_RECORDING` (1200–1500, ramp 30); simulate ramps in only · match
- Rise removed 98% (13× quiet) · 0.981 · match; clumping removed 99% · 0.994 · match
- No stretch: median 0.1%, −0.4% to +0.6% · 0.134/−0.437/+0.585% · match
- Nothing-planted run alone gives no answer · recomputed over 24 quiet nulls: pooled f₃ sum −2.41, so `pooled_ratio` returns NaN · match (one instance; "usually" not tested)
- Figure 6 tool 10th–90th percentiles: 15 moments 0.78–0.86; 6 moments 0.59–0.98; 3 moments 0.69–1.02 with single recordings 0.55–1.09; ¼ quiet 0.77–0.87; busy 0.76–0.92 (own 0.74–0.95) · all match nj
- "Every recording in Figure 6 gave an answer" · no_answer 0 ×5 · match
- 24/48 recordings per set · SEEDS 1..24, two backgrounds · match
- 20 shifted copies · `N_SURR = 20` · match
- Slides about −32 to +32 s · `shifted`: perm(32)·2 s, centred · about −31 to +31 s · match ("about")
- Two counts offset by half a window · `population_cumulants` · match
- f₂/f₃ formulas, fixed k = f₃/f₂ + 2, share = λk/N ÷ rate · `factorial_cumulants`, `solve`, `per_recording` · match
- ±25% band, reason not given · `CAL_TOL = 0.25`, no comment · match
- Decoys counted in the right answer · `truth()` includes `gt.distractors` · match; 6 decoys of 6 cells · n_distractors 6, round(0.18·32) = 6 · match
- Moment sizes 10/6/3 · round(0.30/0.203/0.10 × 32) · match
- Jitter 0.106 s, the check's own · `CAL_JITTER` · match
- Quiet/busy 0.0049/0.0169, 25th/75th percentiles · `REGIMES`, measured over 63 of 66 recordings as *background* rates · match on value; provenance incomplete (finding 1)
- Bench intervals real since 2026-10-07, median 41 s, under 2 s merged · `bench.SPACING_ENV` doc; summary p50 41.25, rule "less than 2.0 s apart merged" · match
- About 7 moments per 45 minutes · 9.717·0.75 = 7.29 · match (pooled; finding 2)
- 15-minute minimum baseline · `MIN_BASELINE_SEC = 900` · match
- `shape_usable` 300 s / 20 onsets / 5 cells · `fit_background_shape.py:49-51` · match
- Default data set `senktide_ttx`, 66 recordings, stop since 2026-10-05, 4 DI recordings, 3 not reviewed · current_export.toml + todo · match
- ADR-0017 makes this the first exception · ADR-0017 decision 4 · match
- "senktide's rising activity" · FOUNDATIONS line 351, "raises event frequency" · match
- Fixed model adopted because the bench plants fixed sizes · `ADOPTED_MODEL` comment · match; docstring "bracket" vs both reading low in 3A/3C · match
- Regeneration diff: numbers.json from round 1 (b3a92814) to round 2 (fd252301) only adds keys and changes no existing value · consistent

What I checked: every numeric and attributional claim in the README and the six figure captions against numbers.json, the generator, the tool, bench.py, simulate.py, fit_background_shape.py, current_export.toml, the 2026-10-05 todo, ADR-0017, FOUNDATIONS and the 2026-09-25 real-intervals summary. I recomputed the Figure 1 bars, the null-run pooling and the stretch subtraction. I viewed Figures 2, 3 and 6, and their printed values match numbers.json.
