GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch (plus SubagentHandback, the harness's hand-back tool. I hold no Edit, Write or NotebookEdit.)

# Role 2 — citation and reference check, round 1
Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md

## What I checked, and where the trail stopped

**The 1986 citation is correct.** I checked it against Crossref for DOI 10.1007/BF00337113. The authors are "Ch." von der Malsburg and "W." Schneider, *Biological Cybernetics* 54(1):29–40, May 1986. PubMed 3719028 matches, including the DOI.

**I could not get the paper itself.** Springer's PDF link sends curl through idp.springer.com to a cookie error page. The PDF is not in clamor:lit (gitignored, and no copy is on this machine). So everything the proposal says the paper contains was checked only against clamor's transcription: clamor/malsburg1986.py, lit/malsburg-1986.md, lit/malsburg-1986-implementation.md and CLAIMS.md. That is one step short of the source.

**Tracing backward, I stopped one step short of the root.** The 1986 paper describes itself as an application of von der Malsburg's 1981 *Correlation Theory of Brain Function*, which is where the synaptic-modulation idea comes from. The Cogprints copy is behind a bot check: curl got a challenge page and WebFetch got HTTP 403. The 1994 Springer reprint is paywalled. So I have not seen the rule's origin.

**Tracing forward, I checked his next papers on the same idea.** These are the "dynamic link" line:
- von der Malsburg 1985, *Ber. Bunsenges. Phys. Chem.* 89:703–710, DOI 10.1002/bbpc.19850890625 (verified in Crossref)
- von der Malsburg & Bienenstock, *Europhys. Lett.* 3:1243 (1987), and Bienenstock & von der Malsburg, *Europhys. Lett.* 4:121 (1987). I have these from a CV and search snippets only, not Crossref.
- von der Malsburg & Buhmann 1992, *Biol. Cybern.* 67:233–242, DOI 10.1007/BF00204396 (verified in Crossref; one search result said 233–246, and Crossref says 242)

None of these that I found applies the rule to recorded data as a detector.

**Where I searched:**
- Searched: Crossref and PubMed for metadata; the von der Malsburg / dynamic-link literature (forward); STDP theory on the learning-window integral and rate drift; spike-train synchrony statistics (the cross-correlogram, jitter and hollowed-kernel methods); network overlapping communities (metadata only); one general search for Hebbian rules used as assembly detectors on spike or calcium data. That last one was shallow and found nothing on point.
- Not searched: the machine-learning "fast weights" literature (weights that change within one input sequence — the closest ML analogue of "a coupling that learns within one recording"); the physics literature on synchronisation in oscillator networks; Schneider's 1986 thesis (print only).

**These are unsearched fields, not a finding that no prior art exists (residual ⚠).**

**Nobody has been asked (residual ⚠).** clamor's record twice plans to write to von der Malsburg ("Ask", and "decide with the author" in CLAIMS items 1–3). I found no sign in either repo that anyone has written. The main thread should ask Tony whether anyone has contacted von der Malsburg (a senior fellow at FIAS) or anyone else about eq 7/8 or q₀. If there is correspondence, cite it as dated personal communication, per CLAIMS.md, and don't quote it.

## Findings
Format: location · issue · severity · suggested fix · checked against a source?

1. **L73–79, "rate-neutral… derived here, not measured"** · The proposal presents this as its own derivation, but the result already exists. Kempter, Gerstner & van Hemmen 1999, *Phys. Rev. E* 59:4498–4514, DOI 10.1103/PhysRevE.59.4498 (open-access PDF read; copy at <scratchpad>) shows that for inputs uncorrelated at the timescale of the window, the drift is W̃(0)·ν_in·ν_out, where W̃(0) is the integral of the learning window. The paper says: "In the limit of rate coding, the form of the learning window W is not important but only the integral ∫ds W(s) counts." A window with zero integral therefore has no rate-product drift, which is exactly the proposal's argument. The balanced / weight-dependent STDP literature (Song, Miller & Abbott 2000; van Rossum, Bi & Turrigiano 2000; Gilson & Fukai 2011) builds on this; those three I have from search results only. · **High** · Cite Kempter et al. 1999 for the principle and reword to "the zero-integral condition (Kempter et al. 1999), which this cosine meets at |Δt| ≤ w". The only new part is the application, not the insight. · **Yes**

2. **L129–135, Check B ("a signed coincidence count… a close cousin of STTC")** · There is closer prior art than STTC and it is not named. Stark & Abeles 2009, *J. Neurosci. Methods* 179:90–100, DOI 10.1016/j.jneumeth.2008.12.029 (verified) scores zero-lag coincidences against a local baseline taken from the flanks — a partially hollowed convolution window on the cross-correlogram. That is the same "positive centre, negative near-miss" idea. The jitter-surrogate lineage (Platkiewicz, Stark & Amarasingham 2017, already on the bugarach shelf under surrogates/) is the other near relative. · **Medium** · Add these beside STTC in Check B. A kernel that is "STTC with extra steps" may really be "a hollowed-window correlogram statistic with a bound". · Yes (metadata and abstract; full text not read)

3. **L181–183, "the stability test reproduces and the one-step amplification does not; only equations 7 and 8 are used here, and neither is what fails there"** · clamor's current record contradicts both halves. CLAIMS.md item 1 and implementation note round 3: under one reading of Fig. 4, Fig. 7's one-step amplification *does* reproduce without noise. CLAIMS item 2, "The plasticity step size — now part of the one-step question": with noise, modulation at q₀ = 0.01 re-locks streams the dynamics had separated in 6 of 6 seeds (1 of 6 separate at q₀/12). So eq 8's q₀ is implicated in what fails. · **High** · Restate from clamor's CLAIMS.md at a pinned sha. Say that eq 8's step size is an open fidelity question in the source, and that stage 1 is sweeping exactly that parameter. · Yes (against clamor's record, not the paper)

4. **L47–50, "every coupling stays within 80 %… The paper's reason… a stray episode of false synchrony cannot move a coupling far"** · Two problems:
   - (a) In clamor, the ±80 % bound is enforced by an explicit clamp in `modulate()` (S_MIN/S_MAX), not by q(s) alone. At the paper's q₀ one step is 1.04× the half-range (`Q0_OVER_HALF_RANGE`), so without the clamp a step overshoots. The proposal copies only `control()` and `coactivity()`, not the clamp.
   - (b) The "stray episode" rationale comes from clamor's docstring paraphrase and could not be checked against the PDF. clamor itself notes that at the stated q₀ "a single coincident burst puts a resting synapse ON the clamp", which contradicts that rationale.
   
   · **Medium** · Say the bound needs the clamp (or q₀ well below the half-range), and name the clamp as part of what is copied. Mark the paper's rationale "per clamor's transcription; PDF not rechecked", or note the tension. · (a) yes, clamor code; (b) **no**, no PDF

5. **L52–54 and L64, the "subliminal rule… automatic"** · As clamor transcribes it (p. 33), the rule is: no change if either cell has not burst within T + Tₐ/2. With period 2w and burst w, that is 2.5w. The proposal's version (no onsets, no pairs; nothing beyond ±w) is its own truncation, not the paper's rule. Also, clamor's `coactivity` wraps Δt modulo the period, so the caller has to filter |Δt| > w, or pairs out at (w, 2w) fold back onto positive Co. · **Low–Medium** · Call it "in the spirit of the subliminal rule (p. 33, per clamor)" and list the ±w cut-off among the deliberate deviations, as the symmetric update already is. · Yes (clamor code); p. 33 not checked against the PDF

6. **L163–169, copying `control()` "never edited in place"** · clamor's `control()` hard-codes the module constants S0 = 0.012 and S_D = 0.8. An unedited copy fixes *s*₀ at the paper's value, and the proposal leaves *s*₀ free. Both functions are staticmethods of `CocktailParty`, not free functions. · **Low (code; outside my role, flagged for the adjudicator)** · Say which constants come along, or copy the module. · Yes

7. **L77–78, "Any other window length breaks it"** · The integral of cos(πΔt/w) over |Δt| ≤ L is (2w/π)·sin(πL/w), which is also zero at L = 2w, 3w, and so on. "No other" is false as written. It also clashes with L71–72 ("never exercised") versus L171–173 ("stage 1 sweeps *w*… where the interpolated form is exercised"). · **Low (maths and consistency, belongs to other roles)** · Fix the wording ("no other length up to the first full period"). · Yes (arithmetic)

8. **L13–14, L75, L30–32, L104: named concepts with no reference** · 
   - STTC: Cutts & Eglen 2014, *J Neurosci* 34(43):14288–14303, DOI 10.1523/JNEUROSCI.2767-14.2014 (verified; bugarach's assembly_report.md already cites it).
   - Covariance rule: Sejnowski 1977, *J Math Biol* 4:303–321, DOI 10.1007/BF00275079 (verified).
   - The unbounded growth of plain Hebbian learning and its classic repair: Oja 1982, *J Math Biol* 15:267–273, DOI 10.1007/BF00275687 (verified). Eq 8's soft bound is a different repair, and Oja is the standard contrast.
   - Link communities: Ahn, Bagrow & Lehmann 2010, *Nature* 466:761–764, DOI 10.1038/nature09182 (verified).
   - Mixed membership: Airoldi, Blei, Fienberg & Xing 2008, *JMLR* 9:1981–2014 (Crossref returned only their 2005 workshop paper; the JMLR details are from memory, **not verified**).
   - Circular-shift surrogates and the trapezoid rule are standard; the internal `assess.circular_shift_trains` exists (src/bugarach/assess.py:340).
   
   · **Low** (internal proposal) · Add a short reference list. Mark Airoldi as unverified until checked. · Yes, except Airoldi

9. **L9–11 and L166–167, provenance and licence** · 
   - Verified: clamor is private (its CLAIMS.md: "The repository is private"). Both repos are BSD-3 and both are under the syncytium2 org. clamor's licence blocker concerns vendored murderboard/armory/interface2 files, and malsburg1986.py is not one of them.
   - But the copyright lines differ: bugarach LICENSE says "Richard DeFazio" and clamor's says "Tony DeFazio". "Same owner" is true of the org, and the named holder is written two ways.
   - The origin of the code is draughtsman, not clamor: the implementation note says "Carried from draughtsman … @ e9b6d39", and clamor's history is squashed into one commit (c25c7e5).
   
   · **Low** · Stamp the copy "from syncytium2/clamor @ c25c7e5 (originally draughtsman)" and say "under the same GitHub organisation". · Yes

10. **L92, "a step about twelve times smaller that its own figures imply"** · Matches CLAIMS item 2 and round 3: q₀/12 from "60 % … after 11 bursts" (p. 35). Check passed at the level of clamor's record; not checked against the PDF. · — · — · Partly (clamor only)

11. **L42–45, L65–72, Co's shape and the half-period cosine case** · These match clamor's `coactivity` docstring and selftest: cos(2πΔt/T) when burst = T/2, which is cos(πΔt/w) at T = 2w. The INTERPOLATED marking is accurately reported. Check passed at the level of clamor's record. · — · — · Partly (clamor only)

12. **Internal references** · All resolve: `graph.sttc_matrix` (graph.py:128), `tools/assembly_power.py`, the goals page and its "Waiting on Tony" row on quiet→busy, the assembly-negative todo item 1 (overlapping groups), and decisions_pending §2 (0.106 s / 0.135 s, ruled 2026-09-22). I did not open "the jitter run's README, Figure 2". · — · — · Yes

## Outside the artifact (for clamor, not this review)
- clamor:CITATION.cff gives the authors as "Christoph" and "Werner". clamor's own lit/malsburg-1986.md says the paper does not print Schneider's first name and "'Werner' stays unconfirmed and should not be written down as fact". Crossref and PubMed give only initials. This is a guessed name in bibliographic metadata.

## Residual ⚠
- The 1986 PDF was not reachable (Springer bot check). Every "the paper says" claim is verified only against clamor's transcription.
- The 1981 Correlation Theory (the root) was not reachable: Cogprints returned a bot check / 403, and the reprint is paywalled.
- Machine-learning fast weights, the oscillator-synchronisation literature, and Schneider's thesis were not searched.
- No evidence that von der Malsburg or anyone else was asked. The main thread should ask Tony.
- The Kempter 1999 PDF sits in my scratchpad. Moving it to the lit shelf is the adjudicating thread's job, per docs/lit_needed.md.

Sources: https://lcnwww.epfl.ch/gerstner/PUBLICATIONS/Kempter99.pdf · https://link.aps.org/doi/10.1103/PhysRevE.59.4498 · https://pubmed.ncbi.nlm.nih.gov/19167428/ · https://pubmed.ncbi.nlm.nih.gov/1498189/ · https://link.springer.com/article/10.1007/BF00204396 · https://www.jneurosci.org/content/34/43/14288.abstract · https://www.dam.brown.edu/people/documents/BienenstockCV_2008.pdf · https://link.springer.com/chapter/10.1007/978-3-642-82657-3_26 · https://api.crossref.org/works/10.1007/BF00337113
