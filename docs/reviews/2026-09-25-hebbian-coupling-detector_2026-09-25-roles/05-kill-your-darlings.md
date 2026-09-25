GRANT 5 ok — Read, Grep, Glob (plus SubagentHandback for the report). I hold no Edit, Write or NotebookEdit. The session context lists MCP servers (Dropbox, github, Claude_Docs) whose tools could write, but none of them was surfaced to me as a callable function, so I did not use or hold any.

**The prose tool did not run, and it is also missing from the tree.** Glob finds no `murderboard_prose.sh` anywhere under bugarach (I tried `tools/murderboard_prose.sh` and `**/murderboard_prose*`). I have no shell either. So this is not "the main thread will attach the output": the script the checklist requires does not exist here. Put that in the ledger as a finding about the run. I did the banned-construction search by Grep and reading, using the list in my agent file (the syncytium2 murderboard default). The block word counts below are my estimates, not tool output.

Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md

## A. Banned constructions (Grep plus reading)

- Searched for: not just…but, it's not about, worth noting, delve, leverage, robust, seamless, crucial, landscape, tapestry, "In today's". **0 hits.**
- Em-dash pivot into an uplifting close: I read all 17 em-dash lines. None pivots into an uplift; each introduces a gloss or apposition. **0 hits.**
- Three-item list built for rhythm: one near-hit. L117, "Two things, each cheap, each with a way to fail," is a rhythm line and also a preview (see finding 12).
- House rules: "fire", "firing", "fires", "fired": 0 hits. Singular "data": 0 strict hits, one borderline (finding 17).
- American English: 5 hits, finding 16.

## B. Findings

Columns: location · issue · severity · suggested fix · could I verify it against a source.

1. **L72 against L171–173** · The text contradicts itself. L72 says the part of clamor's transcription that is a judgement call "is never exercised". L172 says the copy is kept because stage 1 "sweeps *w* against the window, where the interpolated form is exercised". But the sweep at L87–88 keeps the kernel at the exact point (period 2*w*, burst *w*), so the sweep never reaches the interpolated form. The justification in the last section rests on a sweep the document does not describe. · **High** · Pick one. Either keep the exact point, delete the first reason at L172 and keep only the stamp reason, or add the off-point sweep to stage 1 and drop "never exercised" at L72. · yes (internal)

2. **Heading at L115 against L132** · The heading "checked before anything is built" is false for Check B. L132 says Check B "needs the rule, so it runs first thing in stage 1". · **High** · Retitle, e.g. "What could make this worthless, and the cheapest point to find out." Or say at L117 that Check A runs before the build and Check B right after the rule exists. · yes (internal)

3. **"window" throughout** · The word carries two meanings. It means the baseline window at L24, L26, L54, L100 and L108, and the ±*w* coincidence window at L60, L73 and L77 ("Any other window length breaks it"). At L172, "sweeps *w* against the window" could mean either. L77 also mixes half-width and length: the window is ±*w*, so its length is 2*w*, yet the text says "longer than *w*". · **High** · Call the second one the *coincidence width* everywhere, which is what the glossary line at L17 already names *w*. Keep "window" for the baseline window only. · yes

4. **Stages, checks and readouts: throughout** · The text refers to things by number, which the house conventions ban ("never `T3`, `stage 4`"). Examples: "stage 1 tests it" (L79), "Stage 1 runs both" (L93), "readout 2 has nothing to find and readout 3 reduces to…" (L120–121), "readout 3 can beat CoactDetect in stage 1" (L127), "readouts 1 and 2 are run on STTC" (L135), "before stage 2 reads a real recording" (L89), "Check A"/"Check B". The stages and readouts already have names at their definitions (*Simulation*, *Real baseline recordings*, *Back to clamor*; *is there learned structure?*, *what shape?*, *a call per frame*), and the checks have names in their questions. · **Medium** · Use those names in the cross-references: "the simulation tests it", "the shape readout has nothing to find and the per-frame call reduces to…". · yes (writing_conventions.md, "Name things; don't index them")

5. **L4–5** · The sentence misparses and is ambiguous. "It needs no ruling that is still open to start its first stage" first reads as "a ruling open to starting". "First stage" is also unclear, because the stages are numbered from 0. · Medium · "Its first step, the busy-core check, can start without any open ruling." · yes

6. **L53, L112, L148** · The FOUNDATIONS section is cited by number only ("§9"; bare "(§9)" at L148). A reader cannot tell what "the right behaviour under §9" means. · Medium · Name the content once: "FOUNDATIONS §9, the facts about the preparation that constrain what a detector result means". Then state the relevant fact at each use, e.g. at L148 "group effects run in opposite directions". · yes (FOUNDATIONS.md L308)

7. **L158–159** · "Under ADR-0007 the request states an outcome" names neither the request (none has been introduced) nor its recipient (the producer, i.e. interface2). The ADR is cited by number only. · Medium · "The request goes to the producer as an outcome, not a tool (ADR-0007, bugarach sessions do not act in interface2): *each ROI's centroid…*" · yes (CLAUDE.md)

8. **Undefined jargon at first use** · Terms a cold reader cannot decode:
   - "the stopped surrogate screen" (L5)
   - "the assessor" (L6, L100)
   - "the covariance rule's subtraction of chance" (L76)
   - "CoactDetect" (L122)
   - "the six coded ones" (L110)
   - "mixed-membership or link communities" (L104)
   - "the membership test" (L145)
   - "penumbra-subtracted store" (L155)
   - "the quiet → busy transfer" (L113)
   - "the jitter run's README" (L81); then "The same README" at L89, in a different bullet eight lines later

   · Medium · Give each a clause at first use, or add them to the abbreviations block at L13–18. For the method at L104, say it is undecided: "a method that lets a cell belong to two groups; which one is not chosen yet." · no (I did not open the sources for each)

9. **L47–49** · The symbol *s*_d is used without a definition. The abbreviations block defines *s*₀, *q*₀ and *w* but not *s*_d. The block is also missing *q*(*s*), *K*, *A*(*t*) and *E*(*t*); those last three are at least defined where they are used. · Medium · Add "***s*_d**, the bound, as a fraction of *s*₀" to L13–18. · yes

10. **L171** · "copying sixty lines for it", where "it" is the single cosine, misstates what is copied. The copy is two functions, and `control()` is the equation 8 bound, not the kernel. · Low · "At the chosen point the kernel is one cosine and the bound is one line." Keep the stamp argument. · yes (internal, L163)

11. **L9–11 against L163–167** · The provenance and licensing point is made twice: "stamped copy… not as a dependency" and "both repositories are his; clamor is private", then again as "Both repositories are BSD-3-Clause under the same owner". · Low · Keep the ruling in the status box (who decided, and why not a dependency). Keep the mechanics in "How the code arrives" and cut the repeated ownership clause from one of them. · yes

12. **L117** · "Two things, each cheap, each with a way to fail." is a preview of what the section says, with a rhythm-built tail. It asserts nothing the two paragraphs do not. · Low · Cut it. · yes

13. **Passage test, L119–127 (Check A, about 130 words)** · Payload: "If the STTC coupling's off-diagonal variance beyond the leading eigenvector is at null level, the shape readout is dropped for that stream." That payload sits in the last two lines, as the "Proposed stop". The earlier sentences buy real evidence: why a rank-one coupling would be fatal, and why the existing eigenvalue statistic does not already answer the question. Nothing to cut. · Low · Promote the stop to the opening sentence, then give the rationale. · yes

14. **Passage test, L85–91 (the width bullet, about 110 words)** · Payload: *w* is a multiple of the ruled jitter, the sweep is 2, 3 and 4 jitters, and one value is frozen before real recordings are read. The last sentence (same-frame artifacts sharpen the zero-lag peak) is a separate point about crosstalk. It dangles here: "another reason distance and crosstalk matter below". · Low · Move that sentence to the distance paragraph at L153–159, where crosstalk is argued. · yes

15. **L24–28** · "which pairs kept coinciding more than their timing would give by chance" is imprecise, since timing is what coincidence is made of. What the chance baseline controls for is event rate. · Low · "…more often than their event rates alone would produce." · yes (L30–31 makes the rate point)

16. **L53 "behaviour", L54 "penalised", L72 "judgement", L91 "centre", L166 "licence"** · British spellings. The house rule is American English. · Low · Change to behavior, penalized, judgment, center, license. · yes (writing_conventions.md, "American English")

17. **L151** · "this is the first real data its rule will see" puts "data" in a singular frame. It is a borderline case for the house plural-data rule. · Low · "these are the first real data its rule will see". · yes

18. **L1, L15, L58, L181 ("the 1986 plasticity rule", "the 1986 paper", "The 1986 units", "the 1986 model")** · The year is used as the name, which is a date doing the work of content. · Low · Name it once in the title by its authors or function ("the von der Malsburg–Schneider rule"), then say "the paper" or "the model". · yes (writing_conventions.md)

19. **L52–54** · "For us this is automatic, below, and it is…": the "below" dangles and "For us" is throat-clearing. · Low · "Here it holds by construction (see *Pairs*): an ROI with no events keeps *s*₀, is not penalized, and is not dropped." · yes

20. **L99** · "A statistic of *D* (its Frobenius norm and its leading eigenvalue)" says one statistic and then names two. · Low · "Two statistics of *D*, its Frobenius norm and its leading eigenvalue, each against…" · yes

21. **L153–155** · "**Distance.**" is a heading buried mid-paragraph. "If it did, the question is" mixes tenses. · Low · Start the paragraph with the bolded name. Use "would be". · yes

22. **L5–7** · "the one null it uses is… circular shift, used as a significance test only" repeats "use". · Low · "…its one null, the assessor's circular shift, serves only as a significance test." · yes

23. **L80–81, "on this folder"** · The text does not say which export folder. · Low · "on the default dataset" (or name the table). · no

24. **L181** · "That the 1986 model reproduces its own paper" is muddled: the claim is about clamor's transcription reproducing the paper's results. · Low · "That clamor's transcription reproduces the paper's results." · yes (internal)

## C. Passage test, the remaining blocks

These blocks earn their length:
- **L3–7 status:** the one-line payload opens it.
- **L24–32 idea:** the payload "a plain Hebbian rule learns rates" is at L30–31 and is well placed.
- **L36–40:** the payload "it changes during one stimulus, so it works per recording" is the last clause. It could lead, but the block is short.
- **L73–79 rate-neutrality:** the payload opens it, and the first-order caveat is evidence a sceptic would demand.
- **L80–84 frame grid:** tight.
- **L129–135 Check B:** the stop is at the end. Same fix as finding 13, but lower priority, because the opening sentence already states the risk.
- **L175–183:** each bullet asserts one thing.

## D. Boundary notes

- Whether the rate-neutrality derivation, the 80 % bound arithmetic, and the cosine sum of −1 are true belongs to role 4. I checked only that the prose asserts them consistently.
- The order of sections belongs to role 11.
- Whether writing a finding into private clamor at stage 3 is allowed belongs to other roles. I did not assess it.

---
*Attached by the main thread, not part of the role's report:* `murderboard_prose.sh` is not vendored in bugarach; the main thread ran clamor's vendored copy (stamp `3a6a8fb`) on the round-1 artifact. Output: no banned construction found; five blocks over 120 words, at lines 62 (503 words, the whole "What changes" bullet list counted as one block), 99 (175), 119 (148), 129 (123) and 141 (163).
