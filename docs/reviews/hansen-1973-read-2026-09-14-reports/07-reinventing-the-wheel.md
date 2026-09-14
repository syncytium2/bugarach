GRANT 7 MISMATCH — single-pass self-review by the main thread, which holds more tools than this role's grant (Read, Grep, Glob, Bash); only reading and the checks named below were used

No analysis code was written. Checked the process and the copies:

| # | location | issue | severity | fix | verifiable |
|---|---|---|---|---|---|
| 1 | `docs/learned/detector_history.html` | Must be rebuilt with the project tool, `tools/md_to_page.py`. The build needs `PYTHONUTF8=1` on this machine: the new √ and ⁻ characters make the default Windows codec fail with UnicodeDecodeError. | major (overlaps role 10) | Rebuild with UTF-8 mode | yes |
| 2 | Darkroom copy of the history page | Stale since 2026-08-29. The darkroom claim (#570) covers rebuilding it once this change lands. | minor | Rebuild after merge, then release the claim | yes |
| 3 | Shelf README | The 1973 paper and the two evidence PDFs have no entries. The same claim covers adding them. | minor | Add the entries | yes |
| 4 | Tree-wide copies of the origin wording | Grepped for "withdrawn as unverified" and "nobody had read that paper". Every copy is in a file this change edits (detector_history twice, GLOSSARY, the proposal footer). | no finding | — | yes |
