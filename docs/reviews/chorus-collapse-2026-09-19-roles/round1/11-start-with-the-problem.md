GRANT 11 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is the hand-off channel and not an editing tool. I hold no Edit, Write or NotebookEdit.)

Artifact reviewed: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html` (the built page, 194 lines). I found the four figures by their `<figure>` and `<figcaption>`. I checked them by caption text and did not look at the images, which are inline data. I edited nothing.

## Spine (one claim per element, in page order)

- **Title.** A third of chorus_norm's fits in goal 2 do not train.
- **Answer box, bullet 1.** The cause is the learning rate at the start of training: 292 of 396 inner fits collapse at lr 0.03, against 7 of 468 below it.
- **Answer box, bullet 2.** What breaks is the head: 152 of 153 collapsed fits have a head layer that never switches on, against 1 of 279 working fits.
- **Answer box, bullet 3.** It happens in the first steps. The same fit with the same weights trains at a lower learning rate or with a 200-step warm-up.
- **Answer box, bullet 4.** This is not the failure PR #596 fixed. That one was in the encoder; this one is a second mechanism, in the head.
- **§1 The finding it explains.** In each draw, 146 and 153 of chorus_norm's 432 inner fits called each whole recording as a single event (F1 0.125). 111 are the same fit in both draws, so the collapse follows configuration and starting weights rather than the data. It matters because the scores mix trained and untrained models.
- **§2 Which configurations collapse.** The learning rate almost fully separates collapse (lr 0.03 gives 42–92% per configuration). Encoder width and depth shift the share within lr 0.03. Seeds and folds do not matter.
  - **Figure 1.** Collapse is concentrated at the top of the learning-rate grid, in both nets.
  - **Table 1.** Collapse counts by learning rate and by draw, and the overlap between draws.
- **§3 What a collapsed fit is.** A collapsed fit has a dead head layer, so its output logit is flat (spread 0.0055 against 5.20). Its threshold then drops to the bottom of the grid, which turns the whole recording into one call. chorus_gain_norm also has a second, unexplained route to the same flat output.
  - **Figure 2.** A collapsed fit has a dead head layer and a working one almost never does. This is a scatter of the smallest live-unit share against output spread.
- **§4 When it happens, and what prevents it.** Both fits start flat. The collapsed fit's head starts losing layers by step 30 and its loss never falls. The same fit trains at lr 0.01 or 0.003, or with a 200-step warm-up, and the warm-up rescues 7 of 8 more fits.
  - **Figure 3.** The same fit collapses or trains depending only on its early learning rate. These are the loss curves: as run, with each counterfactual, and the working fit.
  - **Figure 4.** The collapsed fit's head dies layer by layer, and the working fit's does not.
  - **Table 2.** A 200-step warm-up at lr 0.03 rescues 7 of 8 collapsed fits.
- **§5 What it means, and the choice it leaves.**
  - Tuning never chose lr 0.03 (0 of 95 refits), so held-out scores were mostly spared. The cost is a grid that was in effect 13 of 24 configurations.
  - The 4 collapsed refits are the same failure.
  - Fixing it is goal 2's decision. The options are to drop lr 0.03, add a warm-up, or change the head.
  - Output spread detects a collapse without overlap between the groups, so it could gate fits.
- **§6 Limits.** Simulation only, one census recording, replays scored by training loss, and warm-up tried on 9 fits.
- **§7 Where everything is.** Data, tool, runs and the earlier diagnosis.

## The arc I judged against

This is the default analysis arc, adapted for a diagnosis page:

**problem (shown) → what it costs → where it occurs (configuration axes) → what it is (mechanism) → when it happens (onset) → what prevents it (counterfactual evidence) → the choice it leaves → residual risk → provenance.**

The page states no arc of its own. Its body order from §2 to §7 matches this arc and holds up. The departures are at the front: how the page opens, where the cost sits, and a problem that is never shown.

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | Whole page. The first figure is Figure 1 in §2. | **The page never shows the problem.** No figure shows what a collapsed fit's output looks like next to a working fit's on a recording. All four figures are downstream of the problem: collapse share by configuration, a scatter of dead-layer share against spread, loss curves, and a dead-layer count. What "one call for the whole recording" looks like is described only in words (§1, and the end of §3). The request asked to "examine a collapsed fit's output against a working one's", and Figure 2 answers that with a summary statistic instead. This is the incident this role exists for: the reader needs to see the problem first. | blocking | Make the first figure, in §1 or directly under the answer box, one census recording showing both fits. In lanes above the raster, per the house rule, show the collapsed fit's single call spanning the recording and the working fit's calls against the planted events. Under that, show the two output-logit traces (flat against varying) with each fit's threshold. Renumber the other figures. §3's "the threshold falls to the bottom of its grid" can then point back at it. | yes (all four captions read; none shows output over time) |
| 2 | Answer box, first thing the reader sees | **The page opens on the cause, not the problem.** The first sentence is "It is the learning rate at the start of training", and "chorus_norm collapses" follows before "collapse" has been defined. The size and meaning of the problem (146 and 153 of 432 fits, one call per recording, F1 0.125) first appear in §1. Putting the answer first is defensible for the PI who asked the question. But the box should open by saying what it is answering. | major | Open the box with one line stating the problem, taken from §1: "In goal 2, about a third of chorus_norm's inner fits (146 and 153 of 432 per draw) call each whole recording as one event." Keep the four cause bullets after it. With finding 1 fixed, the figure under the box does the same work visually. | yes |
| 3 | §5 relative to the answer box and §1 (the question asked about §5) | **The cost arrives after the mechanism, and it contradicts the cost stated at the start.** §1 says the problem matters "because chorus_norm's scores mix a working model with one that never trained". Four sections later, §5's first bullet says tuning never chose lr 0.03 (0 of 95 refits). Held-out scores were therefore not contaminated wholesale, and the real cost is a grid shrunk to 13 of 24 configurations in effect. The reader carries the wrong cost through the whole diagnosis. The box also summarises none of §5, so a reader who stops at the box misses the decision the PI has to make. | major | Split §5. (a) Move the "tuning stepped around it, at a cost" bullet and the "4 refits collapsed" bullet into §1 as the stated cost, replacing the current "It matters because…" sentence. (b) Add a fifth bullet to the answer box: effective cost (grid in effect 13 of 24; 4 collapsed refits) and the choice left (drop lr 0.03, add warm-up, or change the head; output spread can gate fits in the meantime). (c) Keep the options and the detection bullet where they are, after §4. That position is correct, because the options rest on Table 2 and the census separation. | yes |
| 4 | Answer box, bullet 4 (PR #596) | **This claim has no place in the body where the reader can judge it.** "This is not the failure PR #596 fixed … standardization repaired it" appears only in the box and in the §7 link. No section sets out the earlier diagnosis as context, and no section shows that the encoders of chorus_norm's collapsed fits are live. Checking #596 was the first step of the request, and it left no trace in the argument. | major | Put the #596 history in §1, after the problem and before the new mechanism: an earlier collapse, its cause, and its fix. In §3, where encoder and head are introduced, state the evidence that the encoder is not the failing part this time. If that was not measured, say so in §6 and soften the box bullet. | yes (grep: "596" and "deaf" appear only at line 63 and in §7; the other hits are inside image data) |
| 5 | §2, encoder width and depth | **A term is used before it is defined.** §2 breaks lr-0.03 collapse down by "the per-cell encoder's shape (4 or 8 units; 4 or 6 layers)". The architecture (shared per-cell encoder → standardization → vote → pooled statistics → 8×8 head) is first described in §3's opening sentence. | minor | Move §3's first sentence (the architecture) to the end of §1 or the start of §2. §3 then opens directly on the definition of a dead layer. | yes |
| 6 | §3, the chorus_gain_norm paragraph | **An unresolved side finding interrupts the main case.** The "second route to the same failure, and this page does not establish what it is" paragraph sits in the middle of the §3→§4 mechanism for chorus_norm. Its job in the argument is residual risk. | minor | Cut it to one sentence in §3 ("15 chorus_gain_norm collapses have no dead layer; see Limits") and move the detail to §6. | yes |
| 7 | §4, Figure 3 before Figure 4 | **The prevention evidence comes before the onset evidence.** The text goes onset (flat loss, dead layer by step 30) and then prevention (counterfactual replays, Table 2). The figures go the other way. Figure 3's headline claim is prevention ("depending only on its early learning rate") and it already carries the warm-up curves. Figure 4, the onset evidence, comes second. | minor | Swap them. First the as-run head-death figure (onset), then the loss curves with counterfactuals, then Table 2. Or remove the counterfactual curves from the first loss figure and show them with Table 2. | yes (figure numbering and captions read) |

## Answers to the specific questions

- **What does the reader see first?** The answer box, which opens on the cause (learning rate). The problem is named in the title and only quantified in §1. It is never shown. (Findings 1 and 2.)
- **Does evidence follow its claims?** Yes, in the body: box → §2 → §3 → §4 with their figures and tables. There are two exceptions. Bullet 4 (PR #596) has no evidence anywhere (finding 4). Figure order within §4 is reversed (finding 7).
- **Does any section arrive before it can be evaluated?** §2's encoder-shape breakdown comes before the architecture is described (finding 5). Otherwise no.
- **Does each section earn its position?** §2, §3, §4, §6 and §7 do. §1 does its job only partly: it states the problem but gives a cost that §5 later corrects. §5 mixes two jobs, cost and decision, and they belong in different places (finding 3). The chorus_gain_norm paragraph in §3 belongs with the limits (finding 6).
- **Where should §5 sit relative to the answer box?** Its headline (the effective cost and the decision left to the PI) belongs in the box. Its cost bullets belong in §1. The options and the detection bullet should stay after §4, because they rest on §4's evidence.
- **Does the page show the problem itself before explaining it?** No. No figure on the page shows a collapsed fit's output. This is the blocking finding.
