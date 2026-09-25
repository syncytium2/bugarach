GRANT 8 ok — Read, Grep, Glob

Role 8 (You Lost Me) on the one-page methods: 7 of 9 panels are blocking, and one arithmetic result looks like an error to anyone who checks it.

Artifact read: <repo>/docs/methods/one_page/methods_one_page.html. The PDF next to it could not be rendered here because pdftoppm is not installed, so layout, overflow and page breaks are **unchecked**. That belongs to agent 10. All findings below are from the HTML text, which is the source of the PDF. I checked terms against <repo>/docs/GLOSSARY.md only to learn what they mean and to suggest fixes. The reader is never assumed to know the glossary.

## Per-panel table

| # | Panel | Terms/identifiers first used here | Defined here? | Cold reader follows? |
|---|---|---|---|---|
| 0 | Title + draft note | "ADR-0010", "operating points", "scores" | none | no (minor: this is a draft banner) |
| 1 | Input. | ROI, t50, frame grid, stream (fast/slow/combined), "width attached to each event", "Detectors", "window" ("baseline windows"), "baseline", DI/OVX/MALE/ORX, "the pipeline" vs "the imaging pipeline" | ROI, t50, groups, and *combined* are defined. What fast vs slow *is* is not. "window", "baseline" and "detectors" are not defined. | **BLOCKING**: 3 or more undefined (window, baseline, what fast/slow means, detectors) |
| 2 | Participation floor. | floor, J, K, rigid shift, "co-active", "chance crossings", "1,000 shifts", "window" (in two senses) | floor, J, K and rigid shift are defined. "chance crossings" is not. "window" means a recording epoch and a 2 s coincidence bin in the same paragraph. Edge handling of the shift (wrap or drop) is not stated. | no (major) |
| 3 | Parameters for simulation. | "simulation(s)" (never motivated), SD, correlogram, "coordinated share", Gamma factors, "planted", "bracket", "Spacing", "each window's floor" | SD is defined. "planted", "coordinated share" and "bracket" are not, and the outer participation levels are not given. Participation is given for fast only. | **BLOCKING** |
| 4 | Simulated recordings. | "decoy bursts", "rankings", "Seeds", "selection", "held-out confirmation", "final scoring", "fast's are doubled" | none of these | **BLOCKING** |
| 5 | Scoring. | "Calls", precision/recall/F1, "merges", "operating point", "budgets", "empty recording", "elevated-rate stretch", "precision drop" | F1 is defined. "Calls", "operating point" and the referent of "precision drop" are not. The links from "empty recording" and "elevated-rate stretch" back to panel 4 are implied only. | **BLOCKING** |
| 6 | CoactDetect. | CoactDetect (name), S(t), w, "context window", "guard band", z, α, "merge gap", CFAR, "cell-averaging", "coordinate search", "shipped point", "held-out F1 gain", "bracketed", "a best value at the limit that switches a setting off" | S, z, α and CFAR are defined. w, context window, guard band, merge gap and shipped point are not. The set of optimized settings is not listed. | **BLOCKING** |
| 7 | Chorus. | Chorus (name), chorus_norm, chorus_norm_part, dilated convolution, "channel", "vote", "logit", "dilated head", "bounded count", "crops", class-weighted BCE, "floor − 1", "training seeds", "test recordings", "fresh seeds", "Every detector" | Vote is roughly defined and the ±27 s receptive field is given. Code identifiers are in the text. "logit", "channel" and "crops" are not defined. Evaluation sets have 3 names. | **BLOCKING** |
| 8 | Output. | "the flow", "window", "span", "aperture", "core", *width*, *amplitude* | core, width and amplitude are defined. "the flow" and "span" (as opposed to width) are not. What happens with a zero-width core is not stated. | no (major) |
| 9 | References | none | n/a | yes |

## Findings

Columns: location · issue · severity · suggested fix · checked against a source (yes/no)

1. **Panel 1, Input** · Nothing tells the reader what "fast" and "slow" streams *are*. "Differing only in the width attached to each event" leaves open: width of what, and why it matters. · blocking · Add a short clause, e.g. "fast and slow (events detected at short and long rise-time scales)". Use whatever the producer's actual criterion is. · no (the criterion is not in the artifact)

2. **Panels 1, 2, 3, 8: "window"** · The word means at least four different things: the producer's recording epoch ("baseline windows", "each window and stream", "each window's floor", "For each stream and window"); the 2 s coincidence bin (panel 2); the detector's count interval w (panel 6); and the "context window" (panel 6). The recording-epoch sense is never defined. · blocking · Define it once in Input, e.g. "Each recording is divided by the lab into condition epochs (baseline, treatment); every quantity is computed per epoch". Then say "epoch" for that sense everywhere and keep "window" for time intervals. · yes (GLOSSARY: generation window = the producer's baseline window)

3. **Panel 1** · "The pipeline starts from … exported by the imaging pipeline" names two pipelines. "Detectors read onsets only" comes before any detector is introduced. "Every parameter taken from data below" is ambiguous: data below what? · minor · "This analysis starts from the event tables exported by the imaging software …". Drop "Detectors read onsets only" or move it to panel 6. Change to "every data-derived parameter described below". · yes

4. **Panel 2** · "Chance crossings" does not say what is crossed. "Over 1,000 shifts" is a bare count by house rules. The shift's edge rule is unstated: the glossary says onsets pushed past the end are dropped, not wrapped. That matters because panel 6 uses a *circular* shift, and a reader will assume both are the same. · major · "…whose chance rate of reaching K, over 1,000 surrogate draws, is at most 1 per hour… (onsets shifted past the window edge are dropped, not wrapped)". · yes (GLOSSARY, rigid shift)

5. **Panel 3, heading and first sentence** · "Simulation" is first used with no motivation. The reader has not been told that detectors are tuned and scored on synthetic recordings with known events, and why. This panel describes parameters of something not yet introduced. · blocking · One opening sentence: "Detectors were tuned and scored on simulated recordings with known ('planted') coordinated events, whose statistics were measured from baseline data as follows." This also defines "planted". · yes

6. **Panel 3, Spacing** · The numbers look self-contradictory to a cold reader. A median gap of 41.3 s implies about 87 events per hour, but the text says 9.7 per hour. Slow (25.1 s vs 22/h) and combined (24.8 s vs 25.3/h) show the same mismatch. Most likely the gaps are heavily clustered, so the median is short and the mean is long, but the text does not say so. A reader will take it as an error. · major · Say so explicitly: "gaps are clustered (median 41.3 s, but 9.7 events per hour)", or report the mean or a gap distribution alongside. · no (arithmetic yes; the cause is not verifiable from the artifact)

7. **Panel 3** · "After subtracting the coordinated share": the method is not stated. "The outer two bracket it": the outer participation values are not given. Participation is given for fast only (0.20); slow and combined are missing. · major · Give all three planted levels per stream, e.g. "0.10, 0.20, 0.30". Replace "coordinated share" with "excluding onsets inside detected coordinated events" (or whatever the actual rule is). · no

8. **Panel 4, Simulated recordings** · "Six decoy bursts" is undefined. The glossary says a decoy is built exactly like an 18%-participation planted event but labelled negative. The reader cannot tell what a decoy is or why it is there. · blocking (with #9) · "six decoy bursts (built like planted events at 18% participation but scored as non-events, to test whether a detector can be fooled by correlated bursts)". · yes (GLOSSARY, distractor)

9. **Panel 4** · Several terms are undefined here. "Seeds for selection, held-out confirmation and final scoring" names three roles that have not been introduced. "Seeds" is jargon. "Rankings" refers to detectors not yet introduced. "fast's are doubled" is unclear: doubled *what*, and why (fewer events per fast recording, 7 vs 17). · blocking · "Independent random sets of simulated recordings were used to choose settings, to confirm the choice, and for the final score; the fast stream uses twice as many recordings because it has fewer events (7 vs 17 per recording)". · yes

10. **Panel 4 → 5** · Names are inconsistent. Panel 4 says "Two further recordings carry nothing planted … a 300 s stretch at the 99th percentile". Panel 5 calls these "the empty recording" and "the elevated-rate stretch". It is also unclear whether the 300 s stretch is inside an otherwise empty recording or a planted one. · minor · Name them where they are introduced: "an *empty* recording … and an *elevated-rate* recording containing …". · yes

11. **Panel 5, Scoring** · "Calls" is the detector's output and the central noun of the whole method, but it is never defined. · blocking (with #12, #13) · "A detector's *call* is its claim that a coordinated event occurred over a span of time." · yes (GLOSSARY, call)

12. **Panel 5** · "Every operating point must stay within fixed budgets" uses "operating point" undefined here (and in the header note). · major · "Every setting of a detector (an *operating point*) must stay within …". · yes

13. **Panel 5** · "A precision drop of at most 0.10" is a relative word with no referent: drop relative to what (the decoy-free condition? the busy background? the shipped point?). The fast/slow/combined budgets (7, 1, 10 calls per hour) differ with no reason given. · major · Name the comparison, e.g. "precision on busy background may fall at most 0.10 below quiet". Add a few words on why the budgets differ by stream. · no

14. **Panel 6, CoactDetect** · Symbols are used without values or definitions: w (window length), "context window" (its range, 20–120 s, comes three sentences later), "guard band", "merge gap". The reader also cannot tell which of these were the tuned settings. · blocking · Up front: "Its settings are the count window w, the context window C (the surrounding span used to estimate the null), an optional guard band G excluded around t, the significance level α, and the merge gap (calls closer than this are joined)". · yes (GLOSSARY, merge gap)

15. **Panel 6: "cell-averaging CFAR"** · False friend. In radar, "cell" means a range bin. To a neuroscientist, "cell-averaging" reads as averaging over neurons, which is the opposite of what the null does here (it averages over time). · major · "a constant-false-alarm-rate (CFAR) test of the cell-averaging type used in radar, where 'cells' are time bins (Finn & Johnson, 1968)", or drop "cell-averaging". · yes

16. **Panel 6** · Undefined jargon: "the shipped point" (internal). "Held-out F1 gain" (gain over what?). "A best value at the limit that switches a setting off was reported as a finding, not adopted" cannot be followed cold. "Bracketed by tested values" is borderline. · major · "starting from the previously released settings"; "F1 gain over the starting settings, on the confirmation set"; "if the best value was the one that disables a setting (e.g. a guard band of zero), it was reported but not adopted". · no (what "shipped point" was is not checkable here)

17. **Panel 7, Chorus** · Internal code identifiers appear in reader-facing text: `chorus_norm`, `chorus_norm_part`. "Chorus" itself is never glossed. · major · Drop the identifiers. Call them "Chorus" and "Chorus-P (participation variant)". Add a short gloss of the name if it is kept. · yes

18. **Panel 7** · There are too many ML terms for this audience, and some are contradictory. "One dilated convolutional filter … each channel" says one filter and then channels without a count. "logit" is undefined for neuroscientists. "dilated head", "409.6 s crops" and "class-weighted binary cross-entropy" are unexplained. · major · "a stack of dilated convolutions (N channels)"; "outputs one event score per frame"; "trained on random 409.6 s excerpts". Keep BCE with a 3-word gloss or cut it. · no (channel count not in artifact)

19. **Panel 7** · Evaluation sets have three names across panels 4, 6 and 7: "test recordings", "fresh seeds", "held-out". In addition, "training seeds" (network initialisations) reuses "seed" for something different from the simulation seeds of panel 4. "Every detector was compared with CoactDetect" implies detectors other than Chorus that the page never names. "Within CoactDetect's empty-recording budget" attributes to CoactDetect a budget that panel 5 defined per stream. · major · Fix one name per set (e.g. tuning / confirmation / final) and use it everywhere. Say "five random initialisations". Say "Both Chorus variants were compared …" (or name the other detectors). Say "within the empty-recording budget". · yes

20. **Panel 8, Output** · "the flow" is an internal word. "span" (of a call) and "width" (of an event) are two different quantities that sound interchangeable. The page does not say what happens when the core has one ROI or zero width, where amplitude would divide by zero. The glossary says width is floored at the frame interval and one cell has no amplitude. · major · "the method returns"; "the call's time span (from the detector)" vs "the event's width (from onsets, below)"; add "width is floored at one frame (0.1 s); a single-ROI core has no amplitude". · yes (GLOSSARY, width and amplitude)

21. **Panel 8: "amplitude"** · False friend for calcium-imaging readers, for whom amplitude means ΔF/F. The disclaimer "not of fluorescence" helps, but the label is recognised before the disclaimer is read, and it will be misread wherever the column appears without this paragraph. · minor · Consider "packing density (ROIs s⁻¹)". If "amplitude" is kept by ruling, keep the disclaimer. · yes

22. **Header note** · "ADR-0010" is an internal decision-record identifier. "operating points and scores are results" uses "operating points" before any definition. · minor (draft banner) · Remove before the manuscript, or say "the procedure as fixed on 2026-09-25". · yes

23. **Whole page: mechanisms named, not shown** · The rigid shift, the circular-shift null and the call-core grouping are only named. On a one-page text methods section an illustration is not possible. · minor · Reuse existing project illustrations as a supplementary figure and cite it ("see Fig. S1"). · no

24. **Tone** · Spelling mixes US and UK: "optimized" but "standardised", "labelled", "neighbours", "centre". · minor · Pick one; US for most journals. · yes

Group order (DI, OVX, MALE, ORX) is correct, and 17+17+13+19 = 66 recordings adds up. Consistency check: 9.7 / 22.0 / 25.3 events per hour × 0.75 h gives 7 / 17 / 19 planted events per recording, which matches panel 4. The mismatch in #6 is therefore between the median gaps and the rates, not between the rates and the plant counts.

## Budget note
The page length is fixed, so most fixes above are one clause each. The four that cannot be cut without losing a cold reader are, in order: #5 (say why there are simulations and what "planted" means), #2 (the meaning of "window"), #11 (what a call is), and #14 (list CoactDetect's settings). Room can be found by cutting #18's ML detail and the α floor value.
