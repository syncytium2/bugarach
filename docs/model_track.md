# The model track — separate from the website, on purpose

> **This is the MODEL track.** The website is [`docs/webapp_spec.md`](webapp_spec.md).
> Tony, 2026-08-18: *"separate out the two main tasks (model and website)"*, and
> *"invest in building out the full infrastructure then refine the model"* — so the
> website has priority and nothing here blocks it.
>
> **Nothing here is approved to run.** The experiments and their costs are in
> [`docs/overnight_spec.md`](overnight_spec.md) Track B, which carries its own refusal
> block.

## Where the model actually stands

- **Centre−surround ties the best hand-written detectors** — 0.668 ± 0.061 against
  CoactDetect's 0.651 ± 0.044 — and wins on cost: 0.014 s to scan a held-out fold,
  1,149 parameters, 5.6 s to train.
- **It transfers worse than two of the six** from a quiet background to a busy one,
  which is a negative result about its own central claim. Fit busy, deploy quiet.
- **The multi-scale bank is redundant on this corpus** — one kernel scores the same for
  81 fewer parameters. Probably the corpus, which plants one event width.
- **The surround clamp is a wart, not a cause** — raising it changes nothing.
- **The per-cell architecture does not train**, and why is unresolved; it also trains at
  a tenth the learning rate of the model that works, so the comparison is uncontrolled.
- **Every learned number is one training run per fold.** No seed error bars anywhere.

## What is not established, and must not be claimed

- **Nothing here says any detector is right about a real slice.** The corpus is
  simulated; its settings are measured.
- **"Competes with state-of-the-art models from the literature" is not supported.** No
  literature model has been run on this corpus. See
  [`docs/todo/2026-08-17-literature-deep-dive-handoff.md`](todo/2026-08-17-literature-deep-dive-handoff.md),
  whose first item is to run two or three of them rather than search harder.

## The queue, in order

1. **Close the seed gap.** Every other number inherits its error bars.
2. **The event-rate ceiling.** The fitted surround is 9.7–18.1 s wide and *is* the
   background estimate, so events arriving faster than that should make the model
   subtract its own signal. One falsifiable prediction, cheap to test.
3. **The width ceiling** — the centre clamps at 64 samples, ~6.4 s.
4. **Drop the raw brightness channel** — one line, closes the last cheap explanation
   for the transfer asymmetry.
5. **A second corpus** from DANDI: it cannot score a detector, and it can say whether
   any of this survives statistics that are not ours.
6. **A corpus with varying event widths**, or DANDI instead of it, to settle whether
   multi-scale is worth keeping.

## The seam with the website

Exactly one thing crosses: **the app trains and runs whatever is in the
`ARCHITECTURES` registry.** Adding or removing a model is one class and one
`@register` line, and the app picks it up without an edit. So the model track can
change the model freely, and the website track can be built against the registry
rather than against any particular network.

The one model fact the app must encode today: **fit on the busier recordings and
deploy downward.** It is measured, it is free to implement, and it is the difference
between a −0.24 transfer penalty and a +0.12 gain.
