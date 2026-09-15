> **Public copy.** Lines that concern real treatment recordings are removed (19 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 8 ok — Read, Grep, Glob

# Role 8 (You Lost Me): blind cold-read of `detector_review.html`

I read `detector_review_plain.txt` from top to bottom, first as a smart 6th grader and then as a scientist from a nearby field. I opened all 18 figures as images and checked a few tables in `detector_review_textview.html`. I did not open any earlier review.

Overall, most sections read well. Terms are usually defined where they first appear, and the detector figures (3 to 8) are clear. The two places a cold reader is lost on the first screen are the "In short" summary and Section 2. There are also four places where a figure seems to contradict the sentence that cites it. A reader who checks the figure will stop trusting the text.

## Verdict by section

The "undefined" column lists terms that are used in the section before they are explained, or never explained.

| Section | Terms first used here | Undefined here | Can a cold reader follow? |
|---|---|---|---|
| Subtitle | detector, "failed to learn" | "learn" (learned detectors come in §4) | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| **§2 + Fig 2** | surrogate, shuffle, circular shift, bar, percentile, bin, log scale, decoy, busy block, bench (in the figure key), spike timing | **bin (only "2-second slice" nearby), bench (figure key), spike (3)** | **BLOCKING by the three-term rule; easy fix** |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| §3.1–3.4 | standard deviation, bell-shaped spread | bell-shaped | yes |
| §3.5–3.6 | "switched on" period, CICADA, gap-based closeness | none | yes (hard, but explained) |
| §4, 4.1, 4.2 | neural network, training, call level, filter, center, surround, guard, ratio, control, learning rate | radar "guard cells" | yes |
| §5 + Table 2 + Fig 10 | simulator, bench, seed, mHz, quiet/busy level, flat/fitted, variance, bunching | "fitted to", "typical shift", "measures back" | **no (major)**: the timing-spread paragraph and Fig 10D (M2, M4) |
| §6 | hit, miss, false alarm, recall, precision, F1, busy-block limit, round, tie rule | looser/loosest, "project's viewer" | yes |
| §7 + Figs 12–14 + Table 3 | tuned, statistical test, decoy calls set aside, chance line | "tuned" is never stated as a term | **no (major)**: the small-event paragraph (M1) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| §10–12 | CFAR | none | yes |

## Findings

### Blocking

| # | Where | Problem | Fix | Checked against a source? |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| B2 | **§2**, first paragraph, and Fig 2 key | "Bin" is used ("a real bin must pass") without being named as the "2-second slice" just before. "Bench" is in the Fig 2B key but is not defined until §5. "Spike timing" is used, but "spike" is not explained until §8. | Say "we call each 2-second slice a *bin*". Relabel the Fig 2B key "simulated recordings (Section 5)". Gloss spike: "the brief electrical signals nerve cells send". | yes |

### Major

| # | Where | Problem | Fix | Checked? |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M3 | §2, "The simulated recordings line up more than the shift too", and Fig 2B1 | In Fig 2B1 the green simulated line is *below* the blue circular-shift line for n = 1 to 5 and only crosses above near n = 6. The sentence reads as true at every n. | Qualify it as "at 6 or more ROIs" and say in one clause why it is lower at small n, or that the reason is unknown. | yes (figure); the reason is not verifiable |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M6 | Fig 2B y-axes and Fig 13B y-axis | Tick labels are written as powers of ten (10 to the −1 through −6, and 10 squared). A 6th grader cannot read them, and Fig 2B is the main evidence for choosing the circular shift. | Label ticks in words or percentages: "1 in 10", "1 in 100", … or 10%, 1%, 0.1%. For 13B: 0.01, 0.1, 1, 10, 100. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

### Minor

| # | Where | Problem | Fix | Checked? |
|---|---|---|---|---|
| m1 | Subtitle | "two that failed to learn" comes before the reader knows programs can learn. | "two learning programs that failed to learn". | yes |
| m2 | Fig 1 / §1 | "six detectors", but the title says ten. Which six, and why are the learned ones left out? | "the six hand-written detectors (Section 3)" plus a reason. | yes |
| m3 | Whole document | "Hand-written" is never defined, and it is not in the word list. | Word list: "written by a person as fixed rules, unlike a learned detector". | yes |
| m4 | §4.1 | "Radar detectors do the same with 'guard cells'" is unexplained jargon. | Gloss it or cut it. | yes |
| m5 | Fig 9A | The flat notch at 0 s in the two guard panels is not explained in the caption. The third and fourth rows show tube only, while the lanes show all four models. | Caption: "the flat gap at the center of the guard filters is the blanked 0.8 s"; "rows 3–4 show tube only". | yes |
| m6 | §3.2 | "smooth bell-shaped spread" | "the familiar bell curve". | yes |
| m7 | §6.3, Fig 12 | "looser / loosest" is never defined. | "looser = a lower bar, so more calls". | yes |
| m8 | §6.3 | "came from the project's viewer" | "were picked by eye in the project's viewing program". | yes |
| m9 | §5 | "fitted to" and "typical shift 0.36 s" are unclear; is "typical" the standard deviation? | Say which. | no |
| m10 | §5 "Two background levels" | Adding planted events and decoys takes the busy level *down* from 19 to 17.2 mHz, which is counterintuitive and not explained. | One clause of explanation, or check the number. | no |
| m11 | §2 compared with §5 | 84 real baselines in Fig 2 vs 80 in Fig 10; the difference is unexplained. | Say why. | no |
| m12 | Fig 2C compared with §2 text | Bar label "recorded · 25"; the text says "about 24". | Use one number. | yes |
| m13 | §7 | "found one detector ahead at every rate" does not say which detector. | Name it, or explain why it is left out. | no |
| m14 | Table 4 | "83% at 10% of ROIs" is hard to parse. The shipped rate+context "2%" appears in no figure or table. | "83% of the smallest events (3 cells)"; show the source of 2%. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m16 | Fig 12 x-axes | Unevenly spaced values (0.5, 1, 2, 3 … 8; 99, 99.5, 99.9) are drawn evenly spaced, so the axis reads as linear. | Caption: "values are evenly spaced on the axis, not to scale". | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m18 | Several sections | Sentences begin with lowercase detector names ("locust turns…", "tube-ratio divides…") and read as typos to a stranger. | "The locust detector turns…". | yes |
| m19 | §1 "How this document goes" | Sections 9, 11 and 12 are skipped. | Add one clause. | yes |
| m20 | §11 "within 10⁻⁹" | No unit. | "10⁻⁹ seconds", or "a relative difference of 10⁻⁹". | no |
| m21 | Word list, "Log scale" | "Each step is ten times" does not fit Fig 10D (30 s, 1 m, 2 m, 5 m). | "each equal step multiplies by the same amount". | yes |
| m22 | Fig 10B | The caption says 10 ROIs, but only about 7–8 ticks are visible. At an 8-second zoom the event does not look like a "vertical stripe", which is what §1 taught the reader to expect. | Caption: "spread over 1.2 s, so at this zoom the stripe looks like a scatter". | yes |

## What each figure shows, read cold

In short: 13 of the 18 captions got me there, and Figures 2, 9, 10, 12 and 13 did so only partly.

| Figure | What I think it shows, in one sentence | Did the caption get me there? |
|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 2 | Real, shifted and shuffled rasters (A); how often n cells line up, on a log scale (B); shuffles doubling events (C); a busy block where a flat bar is passed 46 times and a rising bar is not passed at all (D). | Partly: A has no pointer (M7), B has the green-line conflict and tick labels (M3, M6). |
| 3 | rate+context: the rate spikes past a dotted bar at the planted event, and two spikes in the busy block are false alarms. | Yes. |
| 4 | CoactDetect: a count of 7 far above a short bar at the planted event; in the busy block bars near 10 sit above counts near 4. | Yes. |
| 5 | LoCo: a stepped bar the planted event passes, which rises to about 7 in the busy block. | Yes. |
| 6 | binned SCE: the planted count only touches the bar, so it is a miss; every 10-s bin in the busy block is above the bar, giving 18 false alarms. | Yes. |
| 7 | locust: one flat bar; a double call at the planted event and 15 false alarms in the busy block. | Yes. |
| 8 | SPIKE-synch: per-event dots and per-frame score against 0.1; the planted event peaks just under, and one busy-block frame passes with too few events. | Yes. |
| 9 | The filter shapes of the four tube models, then lanes, raster, tube's brightness and tube's score in the two windows. | Partly (m5). |
| 10 | Two full simulated recordings with planted events and decoys, a zoom on one event, and real vs simulated rate spread and bunching. | Partly: D contradicts the text (M2). |
| 11 | A cartoon of hit / second call / false alarm / miss, and a grid of which 6 recordings each round scores. | Yes. |
| 12 | F1, recall and precision across each detector's list of settings, with the chosen, shipped and limit-breaking settings marked. | Mostly (m16). |
| 13 | F1 per detector at two levels, busy-block call rates against limits, and recall by event size. | Partly: C is tuned-only and the caption does not say so (M1); tick labels (M6). |
| 14 | Recall inside vs outside the busy block, with a chance line; the rising-bar detectors and the ratio models go blind inside it. | Yes. |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 16 | The same four recordings, slow stream: clean vertical stripes that most detectors agree on. | Yes. |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 18 | The same four recordings, slow stream: counts closer together, locust highest among the hand-written detectors. | Yes. |

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Terms the word list does not cover

These are all used in the text:
- **bake-off**
- **mid-sized / small / large events** (define each by the share of ROIs taking part)
- **hand-written detector** (vs learned)
- **tuned**
- **loose / looser**
- **busy-block limit**
- **period** (defined only in the Table 1 caption)
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **spike**
- **fitted** (simulator)
- **CICADA**
- **stripe**

Entries already in the list are accurate, except that "Log scale" does not fit every log axis in the document (m21).

## Files
- `<scratchpad>\review\detector_review_plain.txt`
- `<scratchpad>\review\detector_review_textview.html`
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
