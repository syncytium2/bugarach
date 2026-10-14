GRANT 11 ok — Read, Grep, Glob

Role 11, argument order ("Start With the Problem"), round 1.
Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md and its five PNGs, all of which I opened. I judged it against the layout rule in c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\adr\0014-a-figure-page-is-figures-then-controls-then-text.md. That rule's points 1–4 apply because this is an explainer; point 5 does not. I edited nothing.

## The spine (one claim per unit)

Figures:
- F1. When cells share a moment, the count of onsets in a 1 s window (X) jumps, and that count is all the measure is built from.
- F2. A shifted copy and the recording have the same mean count (0.47 onsets per window). Only the recording has windows holding 5 to 11 onsets. The excess f₂ and f₃ above the 20 shifted copies is what the measure keeps.
- F3. On 48 simulated recordings both models recover the planted share inside the ±25% band, and both read low: fixed by 21% (the adopted model), binomial by 11%.
- F4. The share's error stays within −10% to −21% across window sizes and gap schedules. At a 4 s window, close pairs distort participants per moment (k) and moments per minute (λ).
- F5. A 5-minute stretch where the whole field is busier reads as about 4% coordination, while a slow rise does not (A). With few shared moments, one recording's answer is noisy, and pooling over recordings repairs that (B).

Text:
- T0 (lines 25–33). Provenance (date, script, numbers.json), then "everything here is simulated".
- T1, The objection. The measure never decides which onsets are coordinated; it measures how unevenly the window counts spread.
- T2, Terms. A glossary of nine terms.
- T3, The simulated recordings. The bench setup, a new gap schedule (Tony's call), and which recordings Figures 1 and 2 show.
- T4, §1. Sharing moments leaves the mean count alone and widens its spread; f₂ and f₃ measure that spread.
- T5, §2. Chance is measured by sliding each cell's train of onsets, not assumed to be zero.
- T6, §3. k = f₃/f₂ + 2 gives λ and then the share; f₃/f₂ is pooled over the run.
- T7, §4. There are two models; fixed is adopted to match the bench, not for accuracy, and it reads about a fifth low, so the treatment share is an underestimate.
- T8, §5. The share is safe at any window; k and λ should be read at 1–2 s.
- T9, What it cannot see. Fast field-wide changes are counted as coordination and slow ones are not; a recording with nothing planted gets no answer; few moments make one recording noisy.
- T10, How we know it works. The tool's self-check passes at ±25% (CAL_TOL); Figure 3 is that check and Figure 4A extends it.
- T11, What waits. The real numbers are held by the contamination stop, and the gap schedule is temporary.

## Arc used

I used the default analysis arc, adapted for an explainer that answers an objection: the objection → the idea that answers it → how it is computed → whether it works (validation) → what it gets wrong → what is still unknown.

The figures follow this arc cleanly (F1, F2 = method; F3, F4 = evidence; F5 = limits).

The text deviates in three places, none of them stated:
- Provenance opens it.
- The bench setup comes before the method.
- Validation (T10) comes after the limits (T9), although §4 (T7) has already used its result.

## Cold open

The reader first sees the title, then Figure 1 (the count) with its planted-moment lane, raster and window counts. It is close to the problem but is not quite it. The figure shows what coordination looks like, which is good. But the ▼ lane hands the reader the very definition the objection says the measure lacks, and nothing in the figure or its legend says the measure never sees that lane. The text's own cold open (T0) is provenance, not the objection.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | T10 "How we know it works" (lines 208–214), placed after T9 | Validation comes after the limits section, but its result is spent earlier. §4 (line 139) says "Both are inside the pass band" and reads Figure 3, while what the pass band *is* (the tool's self-check, CAL_TOL ±25%, run on every bench run) only arrives at line 210. The text also stops following figure order at the end: T9 covers F5, then T10 jumps back to F3 and F4A. | Medium | Move T10 to just before §4 (or open §4 with it). Then the reader knows what "passes" means before learning that the adopted model reads 21% low inside it. | yes (README lines 136–139 vs 208–213) |
| 2 | T7 §4 (lines 129–150), inside "How the measure works" | The deliverable's most consequential finding for a reader of treatment results ("take the fixed-model share as an underestimate of about a fifth") sits in subsection 4 of a mechanics section. It arrives before the validation framing it depends on (finding 1). §4 also explains the low reading with "Figure 4B and 4C" (line 142) before §5 has introduced what B and C show. | Medium | End "How the measure works" at §3. Make the model choice and its bias the first evidence section, after the moved T10 and next to Figure 3. Either move the Figure 4B/C sentence into §5, or tell the reader at that point what B and C plot (k and λ errors). | yes |
| 3 | T3 "The simulated recordings", second paragraph (lines 67–74) | The gap-schedule paragraph (close pairs, medium pairs, mixed, Tony's ruling, the todo) comes before the reader knows what a window is or why spacing could matter. It only becomes relevant in §5 (Figure 4), five sections later. | Medium | Keep one or two sentences of setup ahead of the method (32 cells, 45 min, planted moments, quiet and busy rates). Move the spacing paragraph to the head of §5, where it motivates Figure 4. | yes |
| 4 | T0 preamble (lines 25–33) | The text opens on provenance (date written, generating script, numbers.json, "a separate piece of work") rather than on the objection, contrary to the house rule's own ordering (provenance last). | Low–Medium | Make "The objection this answers" the first text heading. Move the date, script and numbers.json lines to the end beside "What waits". The one-sentence "all simulated" warning can stay up front or join T1. | yes (ADR-0014 point 4) |
| 5 | T1 objection (lines 37–40) vs T9 (lines 183–189) | The strongest answer to the objection only arrives at line 187, under limits: the measure does define coordination implicitly, as co-occurrence within a window *w*, beyond chance, and faster than about a minute. A sceptical reader holds that suspicion through the whole method. | Medium | Add one sentence to T1 stating what the measure *does* count as coordination (within one window, beyond what shifted copies give, faster than about a minute), with a forward pointer to "What it cannot see". | yes |
| 6 | T2 Terms (lines 42–57), between the objection and the method | A nine-item glossary separates the objection from its answer. Several entries (f₂, f₃, k, λ) say "defined below" or are redefined in §1 and §3 anyway. | Low | Trim it to the terms needed before §1 (cell, onset, shared moment, window, X), or move the full list after "What waits" as a reference. | yes |
| 7 | Figure 1 heading (line 3) | It is the cold open, but the planted ▼ lane hands the reader the very definition the objection says is missing. The legend does not say the measure never sees the lane, so the first image risks undercutting the page's premise. (Whether the legend is *readable* is role 8's call; this row is about what the opening establishes.) | Low | Add "(the measure does not see this lane)" to the legend's key for the planted lane. That stays within ADR-0014's rule that the heading holds only the key. | yes |
| 8 | Figure 5B, grouped with 5A under "cannot see" | 5B is about precision and pooling (evidence that the method works with few moments), not a blind spot. It fits after Figures 3 and 4. This is acceptable as is, because the figure's name ("how far one recording strays") states the second job. | Low | No move required. Optionally split 5B into its own figure placed after Figure 4, matching a text order of validation → robustness → precision → blind spots. | yes |

## What I checked and found sound

- The objection is the first text section after the preamble, and the title states the premise.
- The figure sequence F1→F5 runs method → evidence → limits, with no figure needed before it can be read.
- §1→§2→§3 is in dependency order: spread, then chance, then the solve.
- "What waits" correctly closes on the residual risk.
- No section lacks a job in the spine.
