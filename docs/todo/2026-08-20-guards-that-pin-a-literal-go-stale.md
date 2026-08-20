---
status: open
filed: 2026-08-20
---

# Three checks failed in one day for the same reason: they pinned a literal, and the literal moved

Not one bug three times — one *shape*, in three unrelated places, all found on 2026-08-20.
Worth a sweep, because the shape is invisible until the day it fires and then it looks
like three separate accidents.

## The three

**A test counted sentences.** `test_prose_about_the_network_is_not_a_leak` required the
viewer page to contain `fetch(` at least twice — a header promise plus an ADR comment. The
comment was reworded three commits after the guard was written, and `main` went red with
nothing about the page's safety changed. Fixed in PR #187: it now asserts that *some*
`NETWORK` primitive is discussed-but-not-used, over the whole tuple, so rewording one
sentence cannot empty it.

**A seed was a salted hash.** `synfire_scan.py` seeded numpy with
`abs(hash(slice_id))` and its docstring promised a rerun would reproduce. Python salts
string hashing per process, so no run ever reproduced any other, and ±1 differences in the
verdict tally were read as the effect of a code change. Fixed in PR #163 with
`zlib.crc32`.

**Four tools transcribed a constant.** `make_regime_figure`, `regime_shift`,
`derive_spec` and the generator sweep each held their own copy of `bench.REGIMES`'
endpoints. They all went stale the moment the axis was re-derived (PR #184) — and one of
them is a figure *caption*, which would have shipped the old numbers under the new
picture. Now all four read `bench.REGIMES`.

## The sweep worth doing

`grep` for the shape rather than the instances:

    # counts of a literal in a file the check does not own
    grep -rn "\.count(" tests/ | grep -E ">=|=="
    # magic numbers in assertions that name no source
    grep -rnE "assert .*[<>]=? *[0-9]" tests/
    # constants duplicated out of src into tools
    grep -rn "0\.0052\|0\.0190\|99\.999" tools/ docs/

For each, one question: **if someone reworded the prose or moved the constant, would this
fail for a reason that has nothing to do with what it guards?** If yes, it is pinning a
literal, and the fix is to assert the property.

## The rule that would have caught all three

A check should name the *property*, and derive the literal from wherever the property
actually lives. Three concrete forms:

- **Counting** anything the check does not own is a smell. Assert existence, or assert
  over a set, not a count.
- **A constant used in two places** is a constant in the wrong place. `tools/` importing
  from `src/bugarach/` costs one line and cannot drift.
- **A promise in a docstring** — "a rerun reproduces", "this is calibrated to X" — is a
  testable claim. If it is worth writing down it is worth a test, and `synfire_scan`'s
  reproducibility claim was false for as long as it was written.

## Not a sapper rule, and why

Tempting to mechanise, and the first draft of this note proposed it. But every form above
has legitimate instances — `test_bench` asserts real numeric thresholds against measured
detector behaviour and should — so a pattern rule would fire mostly on correct code and be
switched off. This is a review question, not a grep. It is filed rather than gated
deliberately; see `docs/sapper_feedback/` if a mechanisable subset is ever found.
