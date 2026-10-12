---
status: open
filed: 2026-10-12
---

# Export folder names come from the armory scheme: re-vendor, and check new `current_export.toml` names

**What changed upstream.** armory `tools/naming` now names export folders and the data files
inside them: branch `naming-exports`, approved by Tony 2026-10-12, README "Exports". A
bugarach-bound export will be named like this:

```
exports/bugarach_eval/pilot-20260811_export_roi_apv+cnqx+gz-then-hik_male_win20min_thr4x_flex+rigid_blanked_<date>/
```

- The threshold, moco and review state are in the name.
- Field steps, moco-pinning, dead-ROI and the archive (`revised_2v`) go in a `manifest.json`
  beside `PROVENANCE.md`.
- The files inside keep the names this repo's contract fixes: `<slice_id>.csv`, `slices.csv`,
  `regions.csv`, and the `.tsv` manifests. `manifest.json` is not a `.csv`, so `io.py:563`
  ignores it.
- Existing exports keep their names; new names start with the first batch built after this
  lands.

**Nothing here parses folder tokens today.** Folders are resolved by exact name from
`current_export.toml` (`dataset.py:211-215`), and that keeps working. Done when:

1. `tools/naming/` is re-vendored from armory once `naming-exports` is on armory's `main`:
   `artifact_name.py`, `codes.json` and `cases.json` together, per the header in the
   vendored copy. Pinned at `1fbf4c0` today, which has no `export` type.
2. A `current_export.toml` table added after this lands has a `name` that passes
   `python3 tools/naming/artifact_name.py check <name>`, and its `signal`, `win` and `source`
   agree with `artifact_name.py parse <name>` rather than being typed a second time.
   Existing entries are untouched.
3. If anything here ever needs a field from a folder name, it uses `parse` (JSON), never a
   regex on the name.

Filed from an armory cloud session (armory branch `naming-exports`), 2026-10-12.
