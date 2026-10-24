GRANT 5 MISMATCH — missing none; holds Bash, PowerShell, Edit, Write, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch / __update / __guide (and NotebookEdit among deferred tools)

(Run note for the ledger: I was spawned through the inline fallback as a general-purpose agent, so I held editing and shell tools my grant forbids. I used only Read and Grep. No file was edited or created. The `roles:` line must record a fallback path.)

**List run:** the house banned-construction list in `05-kill-your-darlings.md` (not just X but Y · it's not about A · it's worth noting · delve/leverage/robust/seamless/crucial/landscape/tapestry · rhythm triads · em-dash uplift · "In today's ___"), plus the "data is plural" rule.

## Tool output (verbatim, `_scratch/r3_prose_report.txt`, run by the main thread)

```
_scratch/r3_extract.md
  line   construction                       kind   context
  — no banned construction found

  blocks (word counts are mechanical; WHICH sentence is the payload is role 5's call)
  1          4 words    1 sentences
  3        153 words   10 sentences   << over 120
  17         6 words    1 sentences
  19       175 words    1 sentences   << over 120
  32        95 words    3 sentences
  41        11 words    1 sentences
  43         2 words    1 sentences
  45        91 words    6 sentences
  52        38 words    2 sentences
  56       289 words   10 sentences   << over 120
  75        12 words    1 sentences
  77        48 words    3 sentences
  83        93 words    4 sentences
  90       149 words    7 sentences   << over 120
  102        2 words    1 sentences
  104       64 words    3 sentences
  110       51 words    2 sentences
  115      351 words   12 sentences   << over 120
  139        9 words    1 sentences
  141      114 words    5 sentences
  151      122 words    1 sentences   << over 120
  159      103 words    1 sentences
  169       45 words    1 sentences
  173       32 words    1 sentences
  176       12 words    1 sentences
  178       42 words    2 sentences
  183        2 words    1 sentences
  185       73 words    4 sentences
  192      126 words    7 sentences   << over 120
  202       12 words    1 sentences
  204       46 words    2 sentences
  208        2 words    1 sentences
  210      122 words    7 sentences   << over 120
  218      243 words   11 sentences   << over 120
  235       59 words    3 sentences
  240       45 words    1 sentences
  245      139 words    2 sentences   << over 120
  252      208 words   11 sentences   << over 120
  270        9 words    1 sentences
  272       61 words    2 sentences
  278        2 words    1 sentences
  280      407 words   12 sentences   << over 120
  297        4 words    1 sentences
  299      202 words   11 sentences   << over 120
  316      390 words   25 sentences   << over 120
  349       27 words    1 sentences
  14 block(s) over 120 words — for each, name its payload sentence and where it sits
```

**Manual checks:** the tool cannot see the GLOSSARY entries, so I grepped them by hand. No banned construction is there either. The only *data* on the page is inside Tony's quotation (page 303), so it is exempt. The glossary has no singular *data*. I found no singular *data* split across a line break.

## Passage test: the 14 blocks over 120 words

Line numbers are goal-page lines, converted from the extract (extract n → page n+15; extract 316 → page 362).

| block (page line) | words | payload sentence | where it sits | what the other words buy | verdict |
|---|---|---|---|---|---|
| 18 Where it stands | 153 | One dated log entry per bullet | lead of each bullet | a status log | keep; fix the jargon in F1 and F2 |
| 34 symbols table | 175 | a table, not prose | — | definitions | keep; fix the M row (F3) |
| 71 Aim 1a bullets | 289 | four bold lead sentences | first in each bullet | the numbers behind each claim, which a skeptic needs | keep; fix F5–F8 |
| 105 "What it rests on" | 149 | "What is added here: g_n for Gaussian jitter and n onsets, the at-most-one-event term, and the joint fit." | second to last | the citations needed for a prior-art claim | **promote the payload to first**, after the heading |
| 130 predictions bullets | 351 | bold lead of each bullet | first | the residuals, which are evidence | keep; fix F10–F13 |
| 166 three-session table | 122 | a table | — | a row-by-row comparison | keep; define the "1/N correction" (F15) |
| 207 membership prose | 126 | "the ratio is 1 + (E − 1)/M" | middle | assumptions (needed) and verdict rates | keep; fix F19 |
| 225 Figure 4 caption | 122 | "F follows (2/π) arctan r, and with no order it is a finite-size bias falling as 1/√n̄." | second to last | panel key | keep; fix F21 |
| 233 order method + bullets | 243 | bold lead of each bullet | first | the numbers and their scope | keep; fix F22 and F23 |
| 260 Kreuz table | 139 | a table | — | the four differences | keep; F24 |
| 267 August + prior art | 208 | bold "…is consistent with a finite-size bias but untested" | first | the control numbers and citations | keep; fix F25–F28 |
| 295 Settled table | 407 | a table | — | the decision record | keep; fix F29 and F30 |
| 314 Tried and dropped | 202 | bold lead of each bullet | first | the reason each was dropped | keep; fix F31 and F32 |
| 362 plan item | 390 | "derive … then simulate to test the prediction" | first sentence | the ordered work list | keep; fix F33–F36 |

None of the 14 blocks needs a cut on length alone. In each, the extra words are evidence or table structure. One block (page 105) has its payload sitting at the end.

## Findings

Each row gives: location · issue · severity · suggested fix · could I verify it against a source.

F1 · p.26 · "Assembled participation converges to random as 1/M" comes before M is defined (p.43), and it is the *excess* that falls as 1/M, not the participation · medium · "Assembled participation's excess over random falls as 1/M (M assemblies)" · yes (p.205 caption, p.210)

F2 · p.28 · "blind verify rounds" is undefined jargon · low · drop it, or write "with independent re-checks" · no

F3 · p.43 · The M row reads "assemblies or latency templates" but means a count · low · "number of assemblies or latency templates" · yes

F4 · p.67 · Why the shared seeds mattered is left implicit: the generator draws the background first, so every condition sharing a replicate index got the same background · low · say that consequence outright · yes (p.316)

F5 · p.73–74 · "(inside the pooled points of B)" is opaque · low · "(B pools them with the larger events, so this does not show)", or name the panel that does show it · no

F6 · p.76 · "MAHICE, the expert-reviewed threshold" conflates a procedure with a threshold. Per the glossary, MAHICE is the human identification step in which a person sets K · low · "(set by a person during MAHICE)" · yes (GLOSSARY:188, 197)

F7 · p.79–81 · The two causes are not parallel: "chance onsets inside… at low jitter" is a noun phrase, "the gather cutting…" is a gerund · low · "chance onsets entering the ±1.5 s gather at low jitter, and the gather truncating the event's own spread at high jitter" · n/a

F8 · p.83–84 · "the 4 s window stays within 0.68–1.04": at which jitter? The scope is ambiguous · medium · add "at every planted jitter" or "at 1 s jitter" · yes (aim1_one_source.json; not opened)

F9 · p.84–85 · "1.7× and 2.1× of planted" is ungrammatical · low · "1.7 and 2.1 times planted" · n/a

F10 · p.101–103 · "the at-most-one-event term corrects for that": it does not say what is corrected (the Poisson form's chance of two events sharing a window). The glossary entry (GLOSSARY:682) is just as vague · medium · "…so a window never holds two of them. A Poisson event train would let two events share a window; the at-most-one-event term removes that contribution from the expected counts." · yes (theory.py; not opened)

F11 · p.127–128 · "and so does the prediction, which passes through the tool's own estimator" has an unclear referent · low · "the prediction excludes them too, because it is computed through the same estimator" · no

F12 · p.134–135 · "(blind pass A's route)" points forward to a section the reader has not met · medium · drop it here, or write "(found by one of the two check sessions, below)" · yes

F13 · p.149–150 · "the square because both preceding bins must be below K" is unexplained to a cold reader: why two bins? · low · name the assessor rule that forces it, in one clause · no (assess.py not opened)

F14 · p.132–133 · "7 and 10 of 48" maps to the backgrounds only by word order · low · "7 of 48 at 0.01 Hz and 10 of 48 at 0.05 Hz" · yes (by position)

F15 · p.168 · "drops the surrogate's 1/N correction" / "1/N² correction": the corrections are never defined · low · one clause: what the correction is for (finite-N surrogate overlap?) · no

F16 · p.180 · "window-budget closed form" is jargon, and the term is used nowhere else in docs/ · low · say what it computes · yes (grep)

F17 · p.181 · "count-detector recall within about 0.03": within 0.03 of what? · medium · "within about 0.03 of the simulated recall" (if that is what is meant) · no

F18 · p.184 · "The event floor (*Aim 1a*) is the consequence:" has no antecedent. Whose consequence? · medium · "The blind passes' up-crossing floor explains Aim 1a's K result:" · yes

F19 · p.188 · "its kept 40-seed output" is opaque · low · "(its saved 40-seed run gives 3–19 % per window)" · no

F20 · p.195 and p.219 · "population-count tool(s)" is used as a defined class, but it is defined nowhere on the page or in the glossary · medium · define it once: "tools that see only how many cells are active per window (the coordination-rates tool, the assessor, the count detector)", and add it to the glossary vocabulary · yes (grep, docs/ excluding reviews)

F21 · p.205 · Figure 3: "reuse E/M sets it": sets the excess or the verdict rate? · low · "the verdict's rate is set by reuse E/M" · no

F22 · p.213–214 · "The verdict flags every recording while reuse E/M is at least 1", then "At M = 1 it reads every recording 'uniform-only'". M = 1 has E/M = 45 ≥ 1, so the reader cannot tell whether "uniform-only" counts as flagged. It reads as a contradiction · medium · say which verdicts count as "flagged" in B · no

F23 · p.219 · "A latency template is not invisible… it reads as extra jitter" is stated as fact, in bold. Plan item 3 (p.371–373) lists the same claim as still to be checked by simulation, and p.139 hedges it with "would read". The page asserts in one place what it schedules as untested in another · medium · "is predicted to read as extra jitter (derived, not yet simulated)" · yes (p.372)

F24 · p.226–227 vs p.231 · Figure 4 says F is "0 with no order", then "with no order it is a finite-size bias". That contradicts unless the first means the infinite-event limit · medium · "(0 with no order in the limit of many events; 1 for a perfect sequence)" · yes

F25 · p.239–240 · "(0.176 against 0.156, which is the no-order bias)": grammatically, "which" makes 0.156 the bias. But (2/π)·arctan 0.25 = 0.156, so 0.156 is the closed form and the 0.02 excess is the bias. A reader will take it the wrong way round · **high** · "(0.176 against 0.156; the 0.02 excess is the no-order bias)" · yes (arithmetic)

F26 · p.244–245 · "which is the rate of a sum of random signs": *rate* already means events per unit time throughout the page · low · "the 1/√n scaling of a mean of random signs" · n/a

F27 · p.244–247 · "local search" is undefined on the page (it is defined only in the glossary). "Net lead count", "net wins" (p.276) and "Borda counting" (p.278) name one thing three ways · low · define local search in one clause and use "net lead count" throughout · yes (GLOSSARY:690)

F28 · p.272–273 · Kreuz et al. "warn that F is…": on this page F is *our* indicator, and Kreuz's is F_Kreuz (p.264). The quotation attaches Kreuz's warning to the wrong symbol · **high** · "warn that their indicator is 'not sufficient…'" · yes (p.227, p.264)

F29 · p.270–271 · The order-free control (0.101) beats both real values (0.036, 0.099), but the sentence does not say what that means · medium · "so neither stream's indicator exceeds an order-free control", if that is the intended reading · yes (the todo is cited; not opened)

F30 · p.267 · "The August anti-correlation with spike count": whose correlation? · low · "the synfire indicator's anti-correlation with spike count" · no

F31 · p.283 · "Their 2026 review (*Biol Cybern* 120, 2026)": the year is said twice · low · "Their review (*Biol Cybern* 120, 2026)" · n/a

F32 · p.297 · "the circularity column" is undefined jargon · medium · "an out-of-sample test (score on the generator you did not tune on)" · no

F33 · p.308 · The Settled row says the "excess falls as 1 + (E − 1)/M". That expression is the ratio; the excess is (E − 1)/M · medium · "Assembled participation's variance ratio is 1 + (E − 1)/M…" · yes (p.210)

F34 · p.318–320 · "'0.2 s reads 0.17 s' and the 'floor near the frame'" quote claims that no longer appear on the page, so a cold reader has no referent · low · "the earlier claims that 0.2 s read 0.17 s and that jitter floored near the frame interval" · yes

F35 · p.325 · "to test a 2× difference": between what? · low · name the two rates being compared · no

F36 · p.378–379 · In "The repository has met its limits", "its" has an ambiguous referent (the threshold? the method?). "The method to compare against" is never named (PCA/ICA assembly detection?). "Peyrache et al." has no year · low · "The repository has met that method's limits"; name the method; give the year · no

F37 · p.388 · "(Staude, Rotter & Grün 2008, *Neural Comput* 20:1973, separate coordination…)" has a citation acting as a verb's subject inside parentheses · low · "(Staude, Rotter & Grün 2008 … show how to separate…)" · n/a

F38 · GLOSSARY:687–691 vs 662–678 · The new section says "ROIs" in five entries and "cells" in the order-indicator entry · low · use "ROIs" in the glossary entry, as its neighbours do · yes

**Not my call:** p.250 says "falls below that at about 4 or more templates". From the page's own numbers, 0.753/√4 = 0.38, which is above the 0.35 top of the bias range, so M ≈ 5 may be the crossover. That is a number check for role 4. I name it only so it is not dropped.

**What I checked:** the extract in full (page lines 16–329 and 362–397), the prose-tool output, the new GLOSSARY entries (the jitter entry at lines 468–479 and the Synthetic-validation vocabulary at 659–691), and the "data" rule in `docs/writing_conventions.md`. I opened no figures or code; those checks belong to roles 10 and 4. I respected the blindness rule.
