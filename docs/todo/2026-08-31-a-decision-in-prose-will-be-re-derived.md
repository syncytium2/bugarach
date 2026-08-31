---
status: open
filed: 2026-08-31
---

# A decision written in prose will be re-derived; put it where the code reads it

Tony, 2026-08-31, on the pointer file that preceded this one: *"I'm beginning to realize
the pointer fix was a Bandaid on a bullet wound."* He is right, and this is the wound.

## The incident, which is small and complete

**K for the Cossart corpus was decided by a real effort.** Measured across all 59 of their
recordings on 2026-08-29: our excess peaks at K=3, theirs at **K=12**. It was written into
a handoff on `main`, it was indexed by keyword, and the `[cossart]` role in
`current_export.toml` — a file the code reads on every run — carries the prohibition in
capitals: **DO NOT TRANSPLANT OUR K.**

A session then ran the whole transfer experiment at **k=3 and k=8**, spent about
twenty-five minutes of compute, wrote up the result, and landed it. Nothing stopped it. The
prohibition was three feet away in a file that had already been parsed into memory.

## Why every existing mechanism missed

- **The handoff had it, and handoffs are not read by default.** `docs/handoffs/` was not on
  the list of places searched, and nothing made it one.
- **The index had it**, keyword and all — *"K=3 vs K=12"*, with ⚠ *read before quoting any
  transfer figure*. The index was on an unmerged branch, red from an unrelated defect.
- **The briefing could not carry it.** That channel is at its byte ceiling; adding to it is
  what turned CI red earlier the same night.
- **The role note carries the ban but not the number.** It says do not transplant K, and
  never says what to use instead. A prohibition without an alternative is an instruction to
  improvise.
- **And the role note is stale**: it cites *"~405 ROIs"*, a figure the 2026-08-29 handoff
  explicitly retracted and replaced with **566**. A machine-read file is carrying a
  withdrawn number.

Five mechanisms, each doing part of the job, none of them the one that would have worked.

## The repair, and it is small

**Make the decision an input the code reads, not a document a human must find.**

1. **Put `k = 12` in the `[cossart]` role** of `current_export.toml` — tracked in git, read
   on every run, next to the folder it applies to.
2. **Make `derive_spec.py` read it.** Today `--k` is required and unconditional, with the
   good reasoning that *"which K is a human's call and this does not make it."* That
   reasoning is right and the implementation inverts it: the human's call exists, and the
   tool ignores it. The rule should be **use the declared K; require `--k` only when the
   role declares none**, and record in the spec which of the two happened.
3. **Fix the stale 405 → 566** in the same edit, and say in the note that the number was
   retracted, so the next reader does not re-retract it.
4. **Consider the general form.** A K, a `k_chosen`, a tolerance, a chosen operating point:
   each is a decision that currently lives in prose and is quoted by hand. The ones that
   parameterise a run should sit beside the data they parameterise.

## Why prose will keep losing

This project already knows the argument and has applied it elsewhere. FOUNDATIONS §6
refuses to load data without `dt` rather than defaulting it, because *"a loader that
refuses has not"* produced a number yet. The promiscuity probe was given a gate because a
measure that cannot fail a calibration is not a check. The same shape applies here: **a
decision that a tool does not read is a decision that a tool can contradict**, and prose is
how it contradicts it quietly.

The counter-argument deserves stating, because it is the reason `--k` is required today:
a K read automatically is a K nobody looks at, and an assessment silently parameterising a
shipped run is exactly what `docs/RESET.md` §1 warns about. That is answered by **declaring
it explicitly in a tracked file** rather than inferring it — the human still chooses, once,
in a place with a name, and the tool then cannot be talked out of it.

## Not done here

Filed rather than implemented, because it changes what `derive_spec.py` requires and that
is a contract other callers rely on. The overnight transfer has been re-run at K=12 and its
write-up corrected; that is the symptom fixed, not the cause.
