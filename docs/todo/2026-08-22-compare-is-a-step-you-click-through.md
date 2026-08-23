---
status: open
filed: 2026-08-22
---

# Compare is a step, and it grumbles

Tony, 2026-08-22:

> *"compare is a step. that's my philosophy and it should force the user to at
> minimium click through with grumpy comments."*

**The decision.** Checking that the simulated data came out like the recording it
was aimed at is a step in the pipeline, not a button someone may or may not find.
It does not block, and it does not judge — it refuses to be skipped unnoticed, and
it keeps saying so if you go on anyway.

## Why it earns a step

Every operating point downstream is fitted on the simulated data. An unchecked
generator is an unchecked result, and `verifySimulation` says as much in its own
comment. Today it is a button inside the Simulate panel, disabled until a
measurement has aimed the generator, explaining that in a note nobody reads
because the panel is one of nine.

## What "grumpy" means, and what it must not become

It must not become a pass/fail. `verifySimulation` already refuses to rule on
whether the gap is acceptable, on the grounds that it depends on what the data is
for — the same refusal the assessor makes about K. Grumpy is the posture that
preserves both: the page insists you look, tells you what you did not look at, and
still will not decide.

Open, and a matter of taste rather than correctness: whether going on without
comparing leaves a persistent mark on the run — in the settings file, in
`run.json`, on the raster — or only a complaint on screen. The argument for the
mark is that the file outlives the complaint, and a setting fitted on unverified
data is exactly the thing a reader six months later would want flagged.

## Also settled the same day

**Assessing the simulated data stays possible and unadvertised.** It is a check
that the simulator and the assessor are happily married, and a superuser may want
to inquire; it is not a release priority and it does not get a step. Note that the
comparison above is itself an assessment of the simulated data, so the capability
is already there — this is about whether the ordinary Assess step offers itself on
that route, and the answer is: reachable, not featured.

## Related

- [`2026-08-22-a-back-route-for-a-reliable-pipeline.md`](2026-08-22-a-back-route-for-a-reliable-pipeline.md)
  — the automated route cannot come until this gate has an answer that is no
  longer a judgement.
