GRANT 8 ok — Read, Grep, Glob

(I also hold SubagentHandback, the report channel. It is not an editing tool. I hold no Edit, Write or NotebookEdit.)

Role 8, naive-reader accessibility ("You Lost Me"). Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md. Figure: docs/proposals/2026-09-25-hebbian-coupling-detector/hebbian_kernel.png, which I opened and read. I read GLOSSARY.md by grep only. I did not read docs/reviews/*.

**Main result: 5 of the 11 sections are blocking, and one undefined name, "clamor", runs through 6 sections.** The blocking sections are The gap, What the detector reports, What could make this worthless, What is asked and What this does not claim. Stages is borderline.

## A. Per-section verdicts (each ## section treated as a slide)

| # | Section | Terms and identifiers first used here | Defined on the section? | Can a cold reader follow it? |
|---|---|---|---|---|
| 0 | Header, status, abbreviations | ROI, stream, STTC, CoactDetect, frame, *m*, Co(*k*), *s*, *s*₀, *s*<sub>d</sub>, *q*, *q*₀, *D*, *Z* — all defined. **Not defined:** "surrogates" (used inside the definition of *Z*), "paper's units" (which paper? It appears only in the title, and the unit is never named), "FOUNDATIONS §3", "murderboard round" | mostly | **yes**, with small gaps |
| 1 | The gap | simulator, surrogate, "stopped screen", pre-registration, "training negatives", null, "two knobs", "label-free", "assembly result", "first open risk", modularity (partly defined by its one-group-per-cell property) | **no** for screen, pre-registration, surrogate, null, assembly result, training negatives. "Two knobs" is a relative term whose referent (*m*, *q*₀) is never given here | **BLOCKING** (6 or more undefined terms) |
| 2 | The idea (plus the Figure 1 caption) | onset, baseline window, near-miss, plain Hebbian rule. In the caption: "ruled per-participant jitter σ", "participant", "same-frame artifact", "clamp", "Equation 8" (not stated until Method detail) | the prose body: yes (Hebbian is defined inline). The caption: no for ruled, participant, same-frame artifact, clamp, Equation 8 | prose **yes**; caption **no** (5 undefined terms) |
| 3 | Why this rule | stimulus/presentation (mapped to a recording, fine), learning window, drift, "negatives drawn across recordings taught a model which recording it was looking at", "a step below 0.0048" | the negatives sentence: no (what negatives? what model?). 0.0048 is unexplained here and derived only in Method detail | **yes**, with one opaque sentence |
| 4 | What the detector reports | eigenvalue, `graph.jitter_trains` (code identifier), "modularity result", "fixed-margin (curveball) null", "the assessor's coordinated clusters", "membership", weighted SBM, link communities, *A*(*t*), *E*(*t*), "quiet-to-busy transfer", "treatment window" | *E*(*t*) and *A*(*t*) are defined. **Not defined:** curveball/fixed-margin null, assessor, quiet-to-busy transfer, treatment window, membership | **BLOCKING** |
| 5 | What could make this worthless | "busy core" (in the heading; the core–periphery idea is explained only in the last bullet), STTC "tile", "shape readout", "the call", "planted", Kendall's τ-b, AUC | AUC is defined. **Not defined:** tile, shape readout (section 4 never gives readout 2 that name), planted. "Busy core" is defined too late | **BLOCKING** |
| 6 | What is asked | "the two stop thresholds", "clamor's record", "penumbra-subtracted export folder", "equations 7 and 8", "modularity run" | **no** for clamor, record, penumbra-subtracted. The equations are a forward reference | **BLOCKING** |
| 7 | Stages | "Back to clamor", declared objective, `tools/assembly_power.py`, `simulate_coordination` (identifier), rate spread, burstiness, "dead-time floor", "membership test", F1 (defined, good), antiphase, "*Z* replaced by its own mean (a squared active count)", `.mat` store, ADR-0007/0008 | groups are expanded (good). **Not defined:** clamor, dead-time floor, membership test, penumbra | **no** (borderline blocking) |
| 8 | Method detail | burst, subliminal rule (defined), clamor transcription, `selftest()`, `modulate()`, `INTERPOLATED`, `decisions_pending.md` item 2, "ruled jitter", trapezoid rule | mostly. Clamor is still never said to be a thing | **yes**, for a technical reader |
| 9 | Where the code comes from | draughtsman, `dl`/`dev` extras, `with_microscope`, `effective_region_windows`, `detect_folder.DETECTORS` | the identifiers are tolerable in an engineering section. Draughtsman is undefined | **yes** (engineering audience) |
| 10 | What this does not claim | "first stability test", "one-step onset gap", "the paper's Figure 4", "re-locks **streams** the dynamics had separated", "CLAIMS item 5" | **no** for all four | **BLOCKING**. See finding F9 on the "stream" collision |
| 11 | References | — | — | yes |

## B. Figure 1: what a cold reader sees, panel by panel

- **A.** A lollipop (stem) plot of a cosine-shaped weight against lag from −5 to +5 frames, with two hollow stems at ±4 at −0.5. **Readable.** It resembles a cross-correlogram, but the negative y-values stop that misreading, so it is not a false friend. One small point: the filled dots at ±5, sitting on 0, read as part of the kernel although those lags are gated out.
- **B.** Two rising lines (blue fast, orange slow), with a red dashed ceiling at 1 and a black line at 0 that carries a text label. **Readable as a trend.** However, the "independent onsets" series is drawn as a plain black zero line with no marker or legend entry, so it reads as an axis rather than a result.
- **C.** An upside-down parabola between two dashed vertical "clamp" lines, and three coloured triangles sitting on the zero line. **I cannot say what the triangles are without the caption, so this panel is a defect.** They sit at y≈0 on a step-size axis, so they read as points where *q* = 0. Their colours repeat B's fast/slow colours with a different meaning. Two of them belong to step sizes whose curves are not drawn. The resting value *s*₀ is not marked. And the panel's one claim, that the red triangle lands past the clamp (0.0220 vs 0.0216), is a gap of about a pixel.

## C. Finding list

Columns: location · issue · severity · suggested fix · could I verify it against a source.

**F1** · The gap (§1) · Six or more undefined terms: "stopped screen", "pre-registration", "surrogate", "null", "training negatives", "assembly result/first open risk". "Two knobs" is relative with no named referent. · **blocking** · Add one clause for each term ("a surrogate: a shuffled copy of the recording that keeps each cell's rate but breaks its timing"), and name the knobs ("the span *m* and step size *q*₀"). Say in one sentence what the screen and the pre-registration are, or drop them in favour of "waits on a decision by Tony". · yes

**F2** · The whole page, first body use in What is asked (§6). Then Stages, Method detail, Where the code comes from, What this does not claim · **"clamor" is never introduced.** A stranger cannot tell whether it is a person, a repository, a paper or a tool. It is load-bearing: a stage is named after it and the fidelity caveats rest on it. · **blocking** · Add an entry to the abbreviations list: "**clamor**: a sibling repository (syncytium2/clamor) that re-implements the 1986 model in code; 'clamor's record' is its list of which of the paper's results it reproduces." · yes

**F3** · What the detector reports (§4) · Undefined: "fixed-margin (curveball) null", "the assessor", "quiet-to-busy transfer", "treatment window", "membership". `graph.jitter_trains` is a code identifier in audience text. · **blocking** · Define the curveball null in words ("reshuffles which cells take part in each event while keeping each cell's and each event's count"). Gloss the assessor ("the repository's coordinated-event caller, `bugarach assess`"). Replace the identifier with "the jitter surrogate". Gloss quiet-to-busy transfer and treatment window. · yes

**F4** · What the detector reports (§4) · Illustrate, don't name-drop: three non-trivial mechanisms appear only as prose. They are the ±20 s jitter surrogate, the curveball null and the split-half learn/score behind *E*(*t*). The curveball null is new work, which makes a picture more important, not less. · major · Add a small schematic panel, or reuse an existing surrogate illustration if the repo has one: original onsets vs jittered onsets vs curveball-reshuffled membership; half A learns and half B scores, then they swap. · no (I did not search the repo for an existing illustration)

**F5** · What could make this worthless (§5) · Undefined: STTC "tile", "shape readout", "planted". "Busy core" is in the heading but is explained only in the last bullet. · **blocking** · Name the readouts in §4 ("1. the power check, 2. the shape readout, 3. the call") so later references resolve. Define tile as "STTC's coincidence window Δt". Move the core–periphery sentence to the top of the busy-core check. · yes

**F6** · What is asked (§6), and the status line · The page asks Tony to "set the **two** stop thresholds", then lists four numbers ("more than half", 95th percentile, τ-b 0.9, 20 seeds). A cold reader counts four and cannot tell which two are meant. · major · Either say "the two checks' thresholds (four numbers)" or list them as two groups under each check's name. · yes

**F7** · What is asked (§6), Stages, Distance · "Penumbra-subtracted" is never defined. A stranger will not know that the penumbra is the out-of-focus/neuropil ring around each ROI. · major · Define it at first use, one clause. · yes

**F8** · Figure 1 caption, panel B, and Method detail "The span" · The text says a span of two jitters "puts about a fifth of coordinated updates on the negative lobe (Figure 1B)". Panel B plots the *expected* update, not the fraction on the negative lobe, so the reader is sent to a panel that does not show the claimed quantity. · major · Either add the negative-lobe fraction to B (a second y-axis, or a small inset histogram of lags at *m* = 2 with the negative lobe shaded) or drop the figure pointer. · yes

**F9** · What this does not claim (§10) · "Equation 8's step size re-locks **streams** the dynamics had separated". In the 1986 paper a stream is a group of synchronised oscillators, while this page's abbreviations define **stream** as the fast/slow class of calcium event. A cold reader will take the page's definition, which makes the sentence nonsense. The same section also leaves "first stability test", "one-step onset gap" and "the paper's Figure 4" undefined. · **blocking** · Use a different word ("re-locks oscillator groups the dynamics had separated"), and gloss the two tests in a clause each or cite them without detail. · yes

**F10** · Figure 1 caption · Undefined in the caption: "ruled" jitter, "per-participant", "same-frame artifact", "clamp". "Equation 8" is referenced before it is stated. · major · "the jitter of each cell's onset around a shared event time, measured earlier (σ)". "Same-frame artifact: two onsets in the same frame from a shared cause such as motion or light, not coordination". Add "clamp" to the abbreviations list next to *s*<sub>d</sub>. Write "the step-size formula, Equation 8 (Method detail)". · yes

**F11** · Figure 1C, the triangles · Phantom structure: the triangles sit on the q≈0 line inside the q(s) plot, so they read as (s, q) points where the step size is zero. Their *y* position is meaningless. Two of them (q₀ = 0.004 and q₀/12) belong to step-size curves that are not drawn. · major · Move the landing positions to a lane or rug strip below the x-axis, or draw all three q(s) curves with each triangle on its own curve. Mark *s*₀ (rest) with a tick or a labelled vertical line so "from rest" has a visible origin. · yes (render)

**F12** · Figure 1C, the main claim · "At the paper's step it lands past the clamp" is the panel's point, but 0.0220 vs 0.0216 is a gap of about a pixel at this scale. The red triangle looks like it sits *on* the clamp. · major · Add an inset zoomed on 0.021–0.0225, or annotate the gap ("0.0004 past the clamp"). · yes (render)

**F13** · Figure 1B vs 1C, colours · Blue and orange mean *fast stream / slow stream* in B and *q₀ = 0.004 / q₀/12* in C. Within one figure, a reader carries B's meaning into C. · minor · Use different colours in C (for example greys, or one hue family) so they cannot be read as streams. (Boundary: if agent 3 treats colour consistency as its own cross-figure rule, file it there once.) · yes (render)

**F14** · Figure 1B, zero line · The "independent onsets: 0 at every span" result is drawn as a plain black line, identical to an axis, with a text label and no legend entry. · minor · Give it markers matching the other series and put it in the legend, or draw a separate zero axis in light grey. · yes (render)

**F15** · Figure 1C, legend text "q0 / 12" · This is relative, and it is ambiguous which *q*₀ is divided (the paper's 0.01). The body elsewhere writes 0.01/12. · minor · Write "q₀ = 0.01/12 ≈ 0.00083". · yes

**F16** · Figure 1A, note below the panel · "span m = 4 frames · lag sum -1 unweighted, 0 with the hollow end lags at half weight" puts list items into a legend with a "·" separator (tone rule). · minor · Split it into two lines, or move it into the caption, which already says it. · yes

**F17** · Why this rule (§3) · "Negatives drawn across recordings taught a model which recording it was looking at in every study the goal page found that measured it" cannot be parsed cold: which negatives, which model, which studies? · major · "Methods that train on real-vs-surrogate pairs drawn from different recordings have tended to learn to recognise the recording rather than the coordination; this rule never compares two recordings." · yes

**F18** · Stages (§7) · Undefined: "dead-time floor", "membership test". `simulate_coordination` is a code identifier in audience text. "E(t) with Z replaced by its own mean (a squared active count)" is cryptic. · major · "Dead-time floor: the minimum gap between two events in one cell". Name the membership test's source (the assembly report's curveball test). Replace the identifier with "the repository's coordinated-event simulator". Rephrase the control as "the same score with every pair given equal weight, which reduces to how many ROIs are active". · yes

**F19** · Abbreviations block · "Surrogates" is used in the definition of *Z* before it is defined anywhere. "Paper's units" names no unit and no paper. · minor · Add a **surrogate** entry. Say "arbitrary units from von der Malsburg & Schneider (1986)". · yes

**F20** · Where the code comes from (§9) · "draughtsman" is undefined, and `with_microscope`, `effective_region_windows` and `detect_folder.DETECTORS` are identifiers. The section is explicitly about code, so this is tolerable, but a portfolio stranger cannot tell what draughtsman is. · minor · Gloss draughtsman in one clause. · yes

**F21** · Figure 1, labels naming what each panel shows · Panels have letters only, and the caption heading names them collectively. This is acceptable under house style (no titles above plots). · minor / no action needed · Optional: open each caption clause with a name, as in "(A) Kernel.", "(B) What one update is worth.", "(C) The bound." · yes

## D. Checks that came out clean

- **Sentence case:** consistent in the title and all headings. No ALL-CAPS emphasis in prose; `INTERPOLATED` is a quoted code marker.
- **Units:** frames are given in seconds (0.1 s) on the axes and in the caption.
- **Groups:** expanded at first use in the Stages table (DI, OVX, MALE, ORX), and in house order.
- **False-friend check** (what the image resembles, what those axes mean there, whether they mean the same here):
  - A resembles a cross-correlogram. Negative weights break that reading, so it is not a false friend.
  - B is an ordinary line chart and reads correctly.
  - C resembles a dose-response or energy-landscape curve with markers. The only misreading is the triangle placement already filed as F11; it is not a wrong chart type.
