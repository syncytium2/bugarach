# Note to Thomas Kreuz — open, copy, send

Paste-ready and unwrapped on purpose: no backticks, no hard wrapping, no tool
between this file and a mail client. Edit it in the mail, not here. The review
context — why Kreuz rather than the tracker, and what this note deliberately
leaves to the GitHub issue — is in
[the filing todo](todo/2026-08-11-file-pyspike-max-tau-issue.md).

Replace the two bracketed lines. Everything else is ready to go.

---

Subject: PySpike's max_tau has been inert since 0.8.0

[opener]

We have been porting the cSPIKE SPIKE-synchronization stack to Python for a calcium-imaging project, and validating the port against cSPIKE reference output. That turned up something in PySpike you will probably want to know about, since it touches your measures rather than just the packaging.

PySpike's max_tau — the maximum coincidence window, max_dist in cSPIKE — has had no effect since 0.8.0 on any spike interior to its own train. In the shared get_tau that 0.8.0 introduced, max_tau survives only as the initial value of the four surrounding ISIs, and every one of them is overwritten when that neighbour exists, so the returned window is the minimum of the interpolated half-ISIs and the cap is never consulted. 0.7.0 ended the same function with "if max_tau > 0.0: m = fmin(m, max_tau)"; the consolidation dropped that clamp from all three copies at once. The docstring still promises the bound.

It is not a small numerical difference. On two trains with a mean ISI around 10 s, max_tau of 1.0, 0.25 and 1e-6 all return SPIKE-Sync 0.3333 — a 1 microsecond window should return nothing. On a 30-train synthetic recording of ours at a 0.25 s cap, PySpike reports 0.3133 where the capped definition gives 0.0696. Anything that took max_tau at its word in the last three years has been reading uncapped numbers, and get_tau feeds spike-directionality and spike-train-order too, not only SPIKE-Sync.

I have a two-line fix — bound the returned window by max_tau/2, since get_tau receives the already-doubled true_max — which restores exactly what 0.7.0 did at MRTS=0 and leaves all 50 tests in PySpike's own suite passing on both backends. Happy to send it to Mario as a PR. Before I file anything I wanted to ask you the part only you can settle: is a hard τmax still the semantics you want PySpike to have? Your 2017 New J Phys paper introduces it as an optional extension and cSPIKE has carried max_dist all along, so I have written this up as a regression rather than a design change — but if 0.8.0 dropped it on purpose, then it is the docstring that should move, and I would rather hear that from you than guess at it in public.

[sign-off]
