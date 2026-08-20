---
status: open
filed: 2026-08-19
---

# `bench` still has its own guess at where a detector keeps its onsets

`bugarach.bench.false_positives_per_hour` does this:

```python
onsets = getattr(det, "onset_sec", None)
onsets = det.locs if onsets is None else onsets
```

That is a second copy of the knowledge `emit.DETECTOR_FIELDS` now holds — and a
partial one: it covers onsets and nothing else, so it cannot be extended to widths
or participant counts without growing into the full table that already exists.

**Fold it into the normalizer.** `emit.events_from(result, detector=name, ...)`
returns the same onsets and knows the other five quantities too, so the fallback
becomes a call and the mapping lives in exactly one place.

**Why it was left alone rather than fixed in the same change.** The writer landed
while the scoring lane was live in another session and reading `bench.py`; editing
that file underneath it would have bought a conflict worth more than the cleanup.
It is small, it is safe, and it should be done once that lane is landed —
`tests/test_emit.py` already covers the mapping it would start depending on.
