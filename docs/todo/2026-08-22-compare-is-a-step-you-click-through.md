---
status: closed
filed: 2026-08-22
closed: 2026-08-23
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

## Closed 2026-08-23 — the step, the grumble, and yes to the mark

**The step and the grumble landed with the two-track rail.** Compare has its own
panel and its own place in the rail, between the simulated data and everything
downstream of it, and it cannot be skipped unnoticed: while a data set is aimed
at a real measurement and has not been checked against it, the rail step reads
**not checked yet** in the nag colour on every repaint, and the Tune panel says
what that costs where the cost lands. Neither blocks. The check has no verdict,
so there is nothing to enforce.

**The open question above, answered: yes, a mark — in the two files, and not on
the raster.** `run.json` gains `generator_checked` beside `generator_spec`, and
the settings file gains a `fitted_generator_checked` provenance row.

*Why the mark.* The precedent is `frame_interval_source`, two fields away in the
same sidecar and added for this exact shape of hole: a file recording only a
value cannot tell a measurement from a statement, so a 0.1 the page invented
looked identical to a 0.1 the producer meant. `generator_spec` had it too. A spec
with nothing said about whether anybody compared it with the recording it was
aimed at **reads as checked**, because absent and fine are indistinguishable —
and every operating point downstream was fitted on that data.

*Why the settings file too.* That is the one thing that crosses the gap. The
sweep runs on invented recordings and the detector runs on real ones; `fitted_on`
already said which data set, and could not say whether that data set had been
checked. The row is computed at save rather than stamped at the sweep, because
comparing after sweeping still checks the generator and a flag frozen at the
click would call that unchecked.

*Why not the raster.* A mark on the picture would be read as a property of the
recording. It is a property of the run.

*And it still does not judge.* No `ok`, no threshold, no pass. Three facts —
aimed at whom, at which K, compared or not — plus, where a comparison exists, the
same ratios the panel prints and already introduces as "not a verdict and not a
percentage error". `run.json` from a folder off disk carries `null`, on
`generator_spec`'s own rule: there was no generator, so there is nothing to have
checked, and a `false` there would read as a folder somebody failed to verify.

    "generator_checked": {
      "aimed_at": "simulated_01",
      "at_k": 3,
      "compared": false,
      "note": "the Compare step was not run against this data set, so nothing
               here says the generator produced what it was asked for"
    }

Pressed through in `tests/test_webapp_unchecked_generator.py`, including a test
that fails if any key of the record is ever spelled like a ruling.

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
