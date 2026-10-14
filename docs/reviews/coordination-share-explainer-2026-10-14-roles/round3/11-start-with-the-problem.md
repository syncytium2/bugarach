GRANT 11 ok — Read, Grep, Glob

Role 11, argument order ("Start With the Problem"). I read only the order of the page. Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md. I opened Figure 1's PNG to see what the reader meets first. I took the layout constraint from docs\adr\0014-a-figure-page-is-figures-then-controls-then-text.md in the same worktree. Points 1–4 of that ADR apply because this is an explainer, so "figures first, then text" is fixed and I judged only the order within each block. I edited nothing.

**Overall:** the order mostly holds. Figures and text sections appear in the same order, the opening is the problem, and the cold open is right. There are two medium findings. The first is that the "mixed" set is used to explain Figure 3A before it is defined, and its close pairs muddy the "size variation alone" claim. The second is that the page's thesis evidence (Figure 5) sits fifth, and the page never says why.

## Spine (one claim per unit)

**Figures**
- F1, The count: the measure sees only onsets binned into 1 s windows (X), never the planted moments. A shifted copy removes the columns of ticks but keeps each cell's onsets.
- F2, Same mean, wider spread: coordination shows as extra spread in X at the same mean, and the excess pairs and triples over the shifted copies are what the measure keeps.
- F3, Recovered against planted: the adopted fixed model's median share passes the ±25% band on all three sets but always reads low. The binomial model is sometimes closer.
- F4, Window and intervals: the share barely moves with window size unless moments are closer together than a window. Participants per moment and moments per minute are badly off throughout.
- F5, What else it counts: with nothing planted, a stretch where the whole field is busier is counted as coordination (median up to 8%, single recordings up to 14%). Slow drift and each cell's own clumping are removed.
- F6, One recording: a single recording's share can stray widely, more so with few moments, and pooling the triples-to-pairs ratio does not narrow it.

**Text**
1. The question: the measure never defines a coordinated event. It implicitly counts onsets that land together in one window more often than in shifted copies, so field-wide rate changes count too (points to Figure 5).
2. (same section) This is the measure treatment results will go through, and a treatment that changes field rate, or the size or spacing of moments, will move it with no change in coordination. That is not yet measured.
3. (same section) Every figure is simulated; the real-data input is under a contamination stop.
4. Terms: vocabulary needed below.
5. Step 1: sharing shows as spread in the window counts, measured by f₂ and f₃.
6. Step 2: chance is measured by shifting each cell's train, and the copies' f₂ and f₃ are subtracted.
7. Step 3: f₃/f₂ gives k, f₂ gives λ, and together they give the share. The ratio is pooled across recordings.
8. Does it get the right answer? (setup): states the simulation design and gives a roadmap of Figures 3–6.
9. The check, and the two models: the medians pass, but the fixed model reads low for reasons that are understood, and accuracy does not justify choosing it.
10. Window size, and moments close together: the share is robust except when moments are closer than a window; k and λ are not.
11. What else it counts: a busy stretch is counted from its edges; slow drift and clumping are removed.
12. How far one recording strays: a single recording is imprecise, and real recordings sit at the imprecise end.
13. The simulated recordings: provenance of the simulations, plus which slice Figures 1 and 2 show.
14. Where the method comes from: the method is established; the literature's corrections are untried; this is what is new here.
15. What waits: real numbers are withheld (contamination stop), treatment windows are next, and the interval schedule is temporary.
16. For developers: code pointers, two places where the tool's own notes disagree with the figures, and the formulas.

## The arc I judged against
An adapted version of the default. This is a method audit with no "fix" step, so I used: question → the implicit answer → why it matters → how the method works → accuracy on the intended target → what else it counts → precision of one recording → provenance and literature → residual (what waits).

The page follows this arc closely, and figures and text appear in the same order (F1 and F2 go with steps 1–3; F3 to F6 each with their own section). Its one unstated choice is that "what else it counts", the part that directly answers the title question, comes after the accuracy sections. The arc is otherwise sound.

## What the reader sees first
Title, then Figure 1: planted moments in a lane, the raster, the window counts X, and a shifted copy. That is the right first image. The title question asks *how* the counting works, and Figure 1 is the visual answer: here are the moments, and here is all the measure sees. The text opens on the question itself, then the stakes (treatment), then the "all simulated" disclosure. The page opens on the problem, not on history or scope. No finding on the cold open.

## Findings
(location · issue · severity · suggested fix · verified against source)

1. **"The check, and the two models", the Figure 3A bullet (line 145) and the Figure 3 legend (line 11)** · Figure 3A is identified as "the mixed set of Figure 4", but the mixed set is defined only in the next subsection (lines 177–180). The setup paragraph (lines 126–128) describes only 15 moments at 10, 6 and 3 cells. A reader judging the 18% figure therefore does not yet know those recordings also contain close and medium pairs. This leaves "From size variation alone it reads 5% low (one size) to 18% low (three sizes)" (line 161) arriving before the reader can evaluate it: by Figure 4, the 120-s-only set reads about 14% low, so part of the 18% is spacing, not size. That number is a truth question for roles 1 and 4; the ordering defect is mine. · **Medium** · Define the interval sets, or at least "mixed = 2 close + 2 medium pairs", in the setup paragraph of "Does it get the right answer?" before Figure 3 is discussed. Then the forward reference in Figure 3's legend points at something already introduced. · yes

2. **"The question" (line 37) and the position of "What else it counts" / Figure 5** · The title question is answered in the opening section with a promise: "Figure 5, what else it counts, shows how much." The evidence for the page's thesis, and for the main treatment caveat (line 43–45), is fifth of six figures and the fourth results section, after the accuracy check and the window sweep. The order is defensible as standard validation order (bias, then specificity, then variance), but it is never stated. The roadmap paragraph (lines 128–130) lists the figures without saying why Figure 5 waits. · **Medium** · Either move "What else it counts" and Figure 5 directly after "How the measure works" (making it Figure 3), since it completes the answer to the title question, or keep the order and have the roadmap paragraph say so in one sentence ("first how well it finds what was planted, then what it counts when nothing is planted"). · yes

3. **"The check, and the two models" (lines 135–137)** · "with the stretch in, the check fails, reading the share 43% high" arrives two sections before the reader learns why a field-wide busy stretch inflates the share (the edge mechanism, "What else it counts", lines 203–212). At this point the claim cannot be evaluated. · **Low** · Add a pointer, "(why: What else it counts, Figure 5A)", or move the sentence into the Figure 5 section's first bullet. · yes

4. **Step 3, last paragraph (lines 120–122)** · The claim about pooling ("steadies the median over recordings, not a single recording's answer (Figure 6)") arrives four sections before its evidence. It is also contradicted in emphasis by line 246 ("Pooling did not narrow the spread here … more widely with 6 moments"). The forward pointer is fine, but the reader carries a reassurance that the evidence section then undercuts. · **Low** · Shorten step 3 to state what the tool does (it pools f₃/f₂). Leave the claim about the consequences of pooling to "How far one recording strays", where Figure 6 can support it. · yes

5. **Step 3 (lines 115–116)** · "so the answer reads high; *Why the fixed model reads low*, below, says why" sends the reader forward to a section titled the opposite of what they just read. That section does explain it (k reads high, λ reads low, the share reads low), but the order makes it look like a contradiction at the point of reading. · **Low** · Add a half-clause in place: "k reads high and moments per minute low, so the share ends up low; *Why the fixed model reads low* explains." · yes

6. **"Does it get the right answer?" setup paragraph (lines 126–130) and the H2 structure** · The roadmap places Figures 3–6 under this heading, but only Figures 3 and 4 are its subsections; Figures 5 and 6 sit under their own H2 sections. The heading levels do not match the stated argument. · **Low** · Either nest "What else it counts" and "How far one recording strays" as H3s under this H2, or limit the roadmap sentence to Figures 3 and 4 and let the next two H2s introduce themselves. · yes

7. **"For developers", second bullet (lines 322–323)** · The finding that the tool's docstring says the two models "bracket" the answer, while both read low in Figures 3A and 3C, is a result about the measure that a non-developer reader could misread from the tool's own wording. It sits in the appendix. The figures are in the body, but the correction is not. · **Low** · Add one sentence at the end of "The check, and the two models": "Both models read low on A and C, so they do not bracket the answer." Keep the code pointer in For developers. · yes

## Surfaces with no finding
- Cold open (problem first).
- Figures and text sections appear in the same order.
- Terms come before first use.
- "The simulated recordings" and "Where the method comes from" are placed as provenance, after the results. Each has a job: reproducibility, and naming the untried corrections.
- "What waits" closes on the residual risk.
- Every section has a job in the spine; none needs moving to an appendix.
