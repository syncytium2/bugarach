GRANT 3 ok — Read, Grep, Glob
(Also held: SubagentHandback, the hand-off channel, which is not an editing tool. The harness lists MCP servers (Claude_Docs, Dropbox, github) in its instructions, but none of their tools were surfaced to me, so I held no write-capable tool. I edited nothing and did not open docs/reviews/2026-09-25-hebbian-coupling-detector*.)

# Role 3, Consistency auditor ("Cross-Examiner"): findings

Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md, plus Figure 1 (hebbian_kernel.svg text and hebbian_kernel.png).

Counting basis I used: recordings = the 66-recording default export, 36 mice (ADR-0008). Streams = fast and slow, as the page defines them. Onsets on a 0.1 s frame grid.

| # | location | issue | severity | suggested fix | verified against a source? |
|---|---|---|---|---|---|
| 1 | l.239–240 vs l.256–257 | The page describes the subliminal rule two different ways. Method detail says "no change for a cell that has not burst within one period plus half a burst", which is T + T_a/2 and matches clamor `modulate()` (`dt.abs() <= period + burst / 2.0`). The gating bullet then calls the paper's cutoff "one and a half periods". In the burst-equals-half-period case this page uses, T + T_a/2 is 1.25 periods, not 1.5. | medium | Replace l.257's "the paper's one and a half periods" with "the paper's one period plus half a burst (1.25 periods at burst = half period)". | yes (clamor:clamor/malsburg1986.py l.267–271) |
| 2 | l.117–118 vs l.199–200 | Readout 3 defines *E*(*t*) as a **mean** of *Z* over the pairs in *A*(*t*), chosen because a sum grows with the square of the active count. The call comparison then uses "*E*(*t*) with *Z* replaced by its own mean (a squared active count)". A mean of a constant is that constant, not a squared active count, so the comparator as written is a flat line. | medium | Name the intended comparator explicitly. For example: "the pair **sum** with *Z* replaced by its mean, which is proportional to \|A\|(\|A\|−1)". Or state that the comparator is a count of active ROIs. | yes (internal) |
| 3 | l.103–104 | The page says the readout-1 surrogates are "jittered uniformly within ±20 s and snapped to frames (`graph.jitter_trains`…)". `jitter_trains` does not snap to frames: it displaces each onset uniformly in ±jit and **wraps inside the window**. The page mentions no wrapping. | medium | Describe the function as it is (uniform ±20 s, wrapped, continuous time). Otherwise, if snapping is intended, say it is a new step added on top. | yes (src/bugarach/graph.py l.249–265; tools/modularity_null.py l.65–67) |
| 4 | l.129–130, l.140, l.166–167 vs l.209–210 | The busy-core check runs first, before any detector code, at an STTC tile of "half the coincidence span". But *m* is only chosen ("frozen") in the simulation stage, which comes after that check. "What is asked" then says "STTC matrices at the chosen tile" without saying who chooses it or when. | medium | Give the busy-core check its own tile before it runs (for example, half of each end of the 3–6 frame sweep, or a stated value in seconds), or say it runs at every *m* in the sweep. | yes (internal) |
| 5 | l.315 ("re-locks streams the dynamics had separated") | **Reserved-word collision.** In the glossary, "stream" is AXIS 1 only: the fast/slow event stream. Here it means clamor's auditory stimulus groups. On a page that says "both streams" throughout, a reader will take it as fast/slow. | medium | Write "re-locks the two stimulus groups the dynamics had separated" (clamor's A/B cell groups). | yes (docs/GLOSSARY.md l.12–16; clamor CLAIMS item 2) |
| 6 | l.116, l.121, l.136, l.199 | **"call" is reserved.** The glossary defines it as "a detector's claim that a coordinated event happened, over a span of time". The page uses it for a per-frame score *E*(*t*) ("A call per frame"; "the call reduces to a weighted count"). Calls only exist after thresholding and merging, and l.201 scores them by F1 on events, so one heading uses both senses. | medium | Call *E*(*t*) "the per-frame score". Keep "call" for what crosses the surrogate threshold. | yes (GLOSSARY l.397–398) |
| 7 | l.149, 157, 184, 198, 203–206 | **"arm" is reserved.** The glossary defines it as one treatment of the same recording (as-is, surrogate, or with something removed), each divided by a null. The page uses it for the two branches of a stop check (Rank/Recovery) and for alternative learning rules ("covariance arm"). | low–medium | Write "test" or "branch" for the stop-check halves and "comparison rule" for the covariance and same-frame-excluded kernels. Or add a second sense to the glossary in the same change. | yes (GLOSSARY l.578–580) |
| 8 | l.135, l.158 | "the shape readout" is used twice but never defined. The three readouts (l.101–121) are not named that way. Presumably it means readout 2. | low–medium | Write "readout 2 (structure beyond coordination)", or name the readouts where they are listed. | yes (internal) |
| 9 | l.4–5 vs l.163–164 | **Count mismatch.** The header says the first stage "waits on **two numbers** only Tony sets, the stop thresholds". "What is asked" says "Set the **two stop thresholds**" and then lists **four** drafts ("more than half", 95th percentile, τ-b 0.9, 20 seeds). The first stage does use two of them, but "two stop thresholds" at l.163 means the two checks, which together need four numbers. | low–medium | l.163: "Set the four numbers in the two stop rules". l.5: "two numbers: 'more than half the recordings' and the 95th percentile". | yes (internal) |
| 10 | l.284–293 ("Where the code comes from") vs INDEX row l.117, clamor CLAIMS item 0 | The INDEX row calls clamor "the **private** repo syncytium2/clamor", and clamor's CLAIMS says "The repository is private". bugarach is public (CLAUDE.md), so copying `malsburg1986.py` into `third_party/clamor/` publishes a private repo's module. clamor CLAIMS item 0 says publishing copies "is a decision about those repos". The proposal says only "Both repositories are BSD-3-Clause, under the same GitHub organization" and never mentions private versus public. | medium | Add a line saying clamor is private and that copying the module publishes it, and put that release decision under "What is asked". | yes (clamor:CLAIMS.md l.84–119; docs/INDEX.md l.117) |
| 11 | l.314–315 | "A one-step onset gap reproduces under one reading of the paper's Figure 4 (item 1)" leaves out clamor's qualifier. It reproduces **without noise**. With the paper's noise, modulation at q₀ re-locks the groups in 6 of 6 seeds. | low | Add "without noise". | yes (clamor CLAIMS item 1; README l.88–93) |
| 12 | l.115 ("about 32 ROIs per recording") | **Counting basis.** The figure has no source. The only "32" in the tree is the median on the earlier 84-recording folder (docs/learned/cossart_transfer/README.md l.54), and it counts all ROIs. The grouping step can only use ROIs with events, and about 35–39% of ROIs have none in a baseline window (FOUNDATIONS §9; goal page). ADR-0008 gives 14–61 ROIs on the 66-recording default. | low–medium | Quote the 66-recording default's median and range, and the active-ROI median, with a source. | yes |
| 13 | l.47–51, l.216 vs docs/assembly_report.md | The assembly negative the page aims at was measured on the **84-recording** folder (2 of 79 fast, 2 of 78 slow above null). The new checks run on the 66-recording default. The page flags σ's superseded folder (⚠ l.74, l.265) but not this one. The page's own "66 recordings × 2 streams × 200 surrogate draws, the count the modularity run used" invites a reader to assume the recordings match. | low–medium | Say that the assembly result is on the earlier folder and that the busy-core check re-measures on the default. | yes (assembly_report.md l.13, 50, 232) |
| 14 | l.11, l.168, "both streams" throughout | ADR-0008, FOUNDATIONS §9 (rates for "fast, slow and combined") and decisions_pending item 10 all treat a **combined** stream as live on the default. The page defines stream as "the fast or slow class" and budgets ×2 streams. It also cites FOUNDATIONS §3 for that definition, but §3 says streams are generic and fast/slow is only a store convention. | low | Add one line saying combined is out of scope (or in scope), and cite the glossary rather than §3. | yes |
| 15 | l.71 (caption) and Figure 1B legend vs l.262; l.150; l.216/221 vs l.287 | These are used before they are defined. σ appears in the Figure 1 caption and panel B before its definition at l.262 (CLAUDE.md: every symbol defined before a figure uses it). τ-b is never defined, and τ already has two meanings in the glossary (dead time, SPIKE-synch window). "ADR" is used at l.216/221 and only spelled out at l.287. | low | Add σ and τ-b to the abbreviations list at the top, and move the ADR expansion there. | yes (CLAUDE.md plot conventions; GLOSSARY l.497–499) |
| 16 | l.263–265 | "puts about a fifth of coordinated updates on the negative lobe (Figure 1B)". Panel B plots the **expected Co**, not the fraction on the negative lobe, so the figure does not show the cited number. It is consistent by hand: at *m* = 2, P(\|k\| = 2) ≈ 0.22, and E[Co] ≈ 0.26 − 0.5·0.22 ≈ 0.15, against the plotted 0.144. | low | Cite the number as derived, or add the fraction to panel B. | yes (hand check; SVG l.91) |
| 17 | l.72, l.249 vs jitter README l.48–53 | The page says onsets are "floored to frames". The jitter record says the producer's onsets already sit on the 0.1 s grid ("every onset is rounded"). This makes no difference to lags, but the two documents describe the same operation differently. | low | "Onsets arrive on the frame grid; synthetic onsets are floored to it." | yes |
| 18 | Figure 1C legend "q0 / 12" vs l.209 "0.01/12" | *q*₀ is the variable being swept. Read with the other swept value, "q0 / 12" would be 0.004/12. The prose correctly says 0.01/12. | low | Change the legend to "q0 = 0.01/12". | yes (SVG l.138) |
| 19 | References | Stark & Abeles 2009 is listed in References but cited nowhere in the text. Aicher et al. is "2015" in the text (l.113), but the reference gives no year and an arXiv id from 2014. | low | Cite Stark & Abeles where the kernel shape is introduced (l.88–91), and make the Aicher year agree between text and reference. | yes (internal) |
| 20 | l.150–152 vs stage table l.184 | The just-STTC rank test says "in more than half the recordings of a stream", which reads as real recordings. The stage table puts the whole just-STTC check in the Simulation stage. It is unclear whether the simulation stage reads real recordings. | low | State which recordings the rank test uses. | yes (internal) |
| 21 | PNG vs SVG | The PNG is 2520×1256 px (aspect 2.0) and the SVG is 1260×540 (aspect 2.33). The PNG has a blank band under the legend. The content is identical. This is mechanical, so it is agent 10's area; noted only as a figure-to-figure agreement check. | low | Render the PNG from the SVG at its own aspect ratio. | yes |
| 22 | l.285, l.297–298 | The draughtsman precedent's stamp reads `vendored from draughtsman @ 5705c46`; the proposal specifies `vendored from syncytium2/clamor @ <sha>`. The proposal also says clamor would be read "through a local clone named by BUGARACH_CLAMOR, as draughtsman is". For draughtsman the clone is optional, with a `gh` fallback. | low | Match the precedent's stamp format, and say "an optional local clone, as for draughtsman". | yes (third_party/draughtsman/__init__.py l.1; tools/check_vendor_freshness.sh l.56, 129) |
| 23 | l.92–94, l.268–273 ("clamp") | The glossary entry says a `clamp` bounds a *fitted parameter* in `learn/nets.py`. Here it bounds a state variable, and does so inside clamor. | low | Write "clamor's clamp" on first use, or add the sense to the glossary. | yes (GLOSSARY l.292–294) |
| 24 | l.102–104 vs goal page "surrogate" table | The readout-1 null is independent per-onset uniform jitter. The goal page records that this kind of jitter leaks one ROI at a time: it breaks the dead-time floor, so a single count separates it from real data (AUC 0.647). The page does not say why that leak is harmless for a significance null on *Z*. | low | Add one sentence on why the leak does not matter for this use, or point readers to where that is argued. | yes (docs/goals/unsupervised-learning.md l.97, l.135) |

## Checked and consistent (no finding)

**Figure 1 against the text:**
- Panel A: Co(k) = cos(πk/4) at k = 0, ±1, ±2, ±3 gives 1, 0.707, 0, −0.707. The ±4 ends are plotted hollow at −0.5, and the lag sum is 0.
- Panel B: fast at *m* = 2 is 0.144 (SVG y=300.0), and 1/0.144 ≈ 7 artifacts per coordinated pair. The slow curve sits below fast, the independent-onset line is at 0, and the artifact line is at 1. σ values 0.106 s and 0.135 s match decisions_pending item 2 and the jitter-correlogram README.
- Panel C: clamps at 0.0024 and 0.0216 (x=968.4 and 1195.7), peak q = 0.01 at s₀ = 0.012. The three triangles land at 0.0220, 0.0160 and 0.0128, each matching its legend. Figure and text agree that 0.0220 is past the 0.0216 clamp. The threshold s₀s_d/2 = 0.0048 is the correct no-overshoot bound.

**Constants against clamor:**
- s₀ = 0.012, s_d = 0.8, q₀ = 0.01, q₀/12.
- The eq 8 formula.
- `selftest()` pins the general form to the paper's cosine.
- The kernel wraps lags modulo the period.
- The row/column question is left open.
- The clamor sha c25c7e5 matches origin/main in clamor.
- CLAIMS items 2, 5 and 6 are cited correctly.
- Both repos are BSD-3.

**Numbers:**
- 66 recordings from 36 mice, and group nested in imaging day: ADR-0008 (34 dates).
- 200 surrogates, 2 s tile, ±20 s: tools/modularity_null.py.
- The six detectors: detect_folder.DETECTORS.

**Code references exist:** torch extras `dl`/`dev` (pyproject), `sttc_matrix`, `simulate_coordination`, `with_microscope`, `effective_region_windows`, tools/make_hebbian_kernel_figure.py, and the assembly_power "strength" meaning.

**Companion documents:**
- Goal page bullet (l.49–54) and INDEX row l.117 agree with the page.
- ADR-0007: the producer request states an outcome and Tony posts it.
- FOUNDATIONS §9: the page is baseline-only and reports per group.
- All four linked todos exist; "item 1" of the open-risks todo is the overlapping-groups item.

**House rules:**
- Group order is DI, OVX, MALE, ORX, with the abbreviations expanded.
- "Coactivity" is avoided, as the page claims.
- No "fire", "modality", "corpus", bare "settings" or bare "adaptive".
- "data" is plural (l.223).
- There is one figure, and it is numbered.

**Not verified:** that the review-record link at l.6 resolves (I was told not to open that path).

## Relevant paths
- docs/proposals/2026-09-25-hebbian-coupling-detector.md
- docs/proposals/2026-09-25-hebbian-coupling-detector/hebbian_kernel.svg
- src/bugarach/graph.py (jitter_trains, l.249)
- clamor:clamor/malsburg1986.py (modulate, l.250–285)
- clamor:CLAIMS.md (items 0, 1, 2, 5, 6)
- docs/GLOSSARY.md (stream l.12, clamp l.292, call l.397, arm l.578)
- docs/adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md
- docs/assembly_report.md
