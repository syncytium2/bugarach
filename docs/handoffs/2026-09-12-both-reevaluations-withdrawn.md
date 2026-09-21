# Handoff — both reevaluations are withdrawn; the night CAN flag, and that is Tony's call

> **Not murderboarded, by Tony's explicit instruction.** Working material for sessions in this tree.
> Nothing here is for an outside reader.

**Thread:** the surrogate screen — branch `surrogate-screen-overnight`, worktree of the same name,
PR [#530](https://github.com/syncytium2/bugarach/pull/530) (**still DRAFT**). This is the third live
thread in this repo; the root `HANDOFF.md` is the pipeline/MAHICE thread and
[`2026-09-10-the-surrogate-is-the-design.md`](2026-09-10-the-surrogate-is-the-design.md) is the
detector-design thread. **None supersedes another. Delete only your own file when your thread lands.**

**Everything is committed and pushed. Nothing is half-written.** Head is `860e5ee`.

---

## Stop here and read this first

**Tony stopped this thread deliberately on 2026-09-12**, answering two questions:

1. *How to proceed on the family-size decision?* → **"Need to discuss further before deciding."**
   No option was chosen. **Do not pick one for him.**
2. *Write a third draft now?* → **"Stop here for now."**

So: **do not write v3, do not start the code findings, do not run anything.** The next move is a
conversation with Tony about the family-size question below. He also said, in the same breath,
**do not interact with other sessions**.

The darkroom claim on [`docs/SESSIONS.md`](../SESSIONS.md) block 065 stays **ACTIVE** — correct by
its own stated release condition: the probe has reported, but the plan has not been reevaluated in
a document that survives review.

---

## The one decision that gates everything

**"Only a new run can flag" is FALSE, and that is the finding this thread ends on.**

The band floor is 1/101 = 0.009901 and it is **genuinely attained** — not a theoretical minimum:

| scope | n statistics | sitting exactly on the band floor | on the paired floor |
|---|---|---|---|
| DI | 3,757 | 1,145 | 1,346 |
| MALE | 3,757 | 1,144 | 1,232 |
| ORX | 3,757 | 1,189 | 980 |
| OVX | 3,757 | 1,146 | 1,118 |
| all | 3,757 | 1,223 | 1,407 |
| cossart | 858 | 229 | 341 |

So Holm on a **pre-declared family of five band statistics flags on the night's existing data**:
5 x 1/101 = 0.049505 < 0.05. The repo's own gate says so in one call:

```
correction_reach(m=5,  n_splits=100, K=99) -> band_reaches: True,  splits_needed: 100
correction_reach(m=6,  n_splits=100, K=99) -> band_reaches: False, splits_needed: 120
correction_reach(m=13, n_splits=100, K=99) -> band_reaches: False, splits_needed: 260
```

**The night ran exactly 100 splits.** The gate built during this session to prevent precisely this
error would have answered "yes, this can flag" — and it was never asked. Paired is unrescuable
either way: m ≤ 2 on `steps_excluded`, m ≤ 1 on `cossart`.

⚠ **The catch, and why it is Tony's call and not a measurement.** Choosing which five statistics
*now*, having seen which sit on the floor, is post-hoc and inadmissible. The remedy is a
**pre-declaration** — valid for a future run, or for a pre-registration defensible without reference
to these results. It is not a way to read a flag out of the night retroactively.

**The 13 statistics, listed without performance data on purpose:**

`band_f_2f@0.5x` · `band_f_2f@0.75x` · `band_f_2f@1x` · `subfloor@0.5x` · `subfloor@0.75x` ·
`subfloor@1x` · `edge_density` · `edge_density_analysis` · `inside_width` · `count_ac1_60s` ·
`fano_60s` · `ks_intervals` · `serial_dependence`

Cossart has 11 — the same set with the two band/subfloor radii in frames rather than three
multipliers.

⚠ **Do not compute which of these sit on the floor unless Tony decides the post-hoc route is
acceptable.** That number makes any later pre-declaration harder to defend, and it is cheaper to
leave unlooked-at than to un-see. Note for the discussion: three of the thirteen are the same
measure at different radii, twice over — which is itself an argument about what a family of five
would even mean.

**The options as they were put to him** (he chose none): pre-declare for the next run and buy
260/520 only if it fails · buy the 260/520 rerun now keeping all 13 · pre-declare and re-score the
night, labelled openly as post-hoc · decide after a v3 exists.

---

## What happened, so none of it is repeated

### Two drafts, both withdrawn, both mine

| draft | hash | outcome |
|---|---|---|
| [v1](../proposals/2026-09-12-surrogate-screen-reevaluated.md) | `e36082da` (was `d623f5a5` at review) | **WITHDRAWN** — four load-bearing conclusions rested on probe numbers where production numbers existed |
| [v2](../proposals/2026-09-12-surrogate-screen-reevaluated-v2.md) | `4b44e408` | **WITHDRAWN** — two blocking findings, one of them the *same* probe-for-production substitution, three times over, inside the section titled "with the power stated correctly" |

Both carry withdrawal banners. `docs/INDEX.md` row 125 now says the plan is again the only
authority and that **there is currently no authority for what to run next.**

### The murderboard feedback — all of it

- **[The run record](../reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md)** —
  adjudication, verdict, corrections with arithmetic, what survives, the seeded-vs-independent
  marking owed to Tony, residuals. Gated: roster 11/11 `mode: standard`, grants 11 ok and matching.
- **[Round 2 reports, roles 1–6](../reviews/2026-09-12-v2-blind-round-roles-1-6.md)**
- **[Round 2 reports, roles 7–11](../reviews/2026-09-12-v2-blind-round-roles-7-11.md)**
- The earlier murderboard on the *report* (not the proposals):
  [`report_steps_excluded_2026-09-11.md`](../reviews/report_steps_excluded_2026-09-11.md)

⚠ **Round 1's eleven reports (on v1) were NOT preserved and are gone.** The run record says so and
declines to reconstruct them from memory. Round 2's were nearly lost the same way — the harness
wrote every agent's output to a 0-byte file — and were recovered from the session transcript. **If
you run a murderboard in this tree, write the reports to `docs/reviews/` as they arrive.** Do not
trust the task output files.

### Verified against production during adjudication — do not re-derive

Each recomputed from the run folders, not quoted from a reviewer:

- **sqrt/nosqrt, 23 pairs at scope `all`:** `delta` differs on **9–13 of 13** (9 in 3 pairs, 13 in
  20); `real` 6–8; `band_p` 3–7; `paired_p` 1–5; **`band_p_holm` and `paired_p_holm` differ on 0 of
  13 in all 23 pairs.** The square root moves nearly every raw statistic and changes no corrected
  verdict. v2's "5–7 of 13" matches no metric at any aggregation.
- **Sizing for one discordant observation: 520 splits, 1040 draws** (v2 said 480/960). `paired_p` is
  two-sided `2*min(...)/(K+1)`, so one discordant draw takes the floor to 4/(K+1), not 3/(K+1).
  At K=1039 the adjusted P is exactly 0.050000 and does **not** fire under the strict `<`; K=1040
  gives 0.049952. Role 10's 780 assumed 3/(K+1) and is wrong; roles 1 and 6 were right.
- **The discriminator table's provenance is mixed three ways.** Production fast
  `homogeneous_resample` = ICC 0.11231 / 89 mice / 1669 pairs — which *is* v2's fast row, and the
  probe reproduces it, so the coincidence hid the substitution. Events likewise (ICC 0.00426 / 18;
  v2's "1,184" is the effective n, 1375/1.161). **The slow row (0.109 / 5.03 / 332 / 87) matches no
  production control** — production slow `homogeneous_resample` is 0.1397 / 107, and the designated
  `uniform_dither` positives span 0.0368–0.1228.
- **The fast negative control flagged.** Production `real_vs_real` fast: accuracy 0.5386, P = 0.035,
  `significant: True`, 830 pairs. v2's table says "not flagged" while its next paragraph relies on
  the flag.
- **20-seed production reruns exist for all three streams and v2 used the probe's five:**
  fast `flag_rate 0.05` (1 of 20, seed 0 only, all 20 tallied), slow `0.0`, events `0.0`. An
  α-level rate measured at n=20 — stronger than the hedge v2 shipped.
- **"of 144" is the ISI-family cell count** (72 `isi_dither` + 72 `joint_isi` per stream), not slow
  cells. Both streams have 144; fast has 2 ok, slow 47.
- **20 assessor surrogates is a tenth of `steps_excluded`'s 200 AND a fiftieth of the assessor's
  shipped 1000** (`assess.assess_coactivity` default). Say both.
- **91% of the 53,432 core-hours is Cossart** (48,799 vs 4,633 for `steps_excluded`).
- **K ranged 19–99**, not 99 — the whole ISI family ran at 19, where the within-scope paired floor
  is 1.000, not 0.260. The conclusion is strengthened by stating this correctly.

### Code findings the review raised — seven, all OPEN, none touched

Tony chose "stop here", so **none of these were started.**

1. **Two implementations of one stated rule disagree.** Both docstrings in `surrogates.py` say the
   window is √2·J; `interval_jitter_bin` computes `round(√2·J)`, `window_shuffle_width` computes
   `2*round(J/√2)`. Differ on 5 of 6 fast radii, 2 of 6 slow, 5 of 6 Cossart — **and at J=2 the
   window is narrower than at J=1.** `tests/test_surrogates.py:444-453` asserts both values, so the
   suite blesses it. Candidates sharing a radius label ran at different effective radii.
2. `pattern_jitter` re-derives the same conversion a third time inline.
3. **The keystone arithmetic exists twice** — `build_surrogate_report.yardstick_reach` recomputes
   what `surrogate_stats.correction_reach` is for, on different inputs. Reproduces exactly today.
4. **`recruited = 0.5 * n_roi` is hardcoded** (`build_surrogate_report.py:603,:639`) while the
   `meta.json` it already reads three fields from records `participation: [0.2, 0.5]`.
5. **`tests/test_surrogate_discriminator.py:308-312` certifies the ICC circularity** the review says
   must be removed — those assertions must *flip*, not be supplemented.
6. **CICADA is uncredited** — `detectors/cicada.py` declares itself a port derived from the Cossart
   lab's CICADA, separately citable (Zenodo 10041434).
7. **Zero figures in either draft**, against CLAUDE.md's "show the picture", while the same run ships
   five numbered SVG figures per report from `tools/build_surrogate_report.py` — including
   `fig_leak`, which v2 re-describes in prose.

### Literature — fixed this session, and what remains

Shelved at `6c74f84` under `<darkroom>/bugarach/lit/surrogates/`:

- **Gerstein 2004**, *Acta Neurobiol Exp* 64(2):203–207 (ane.pl, CC-BY)
- **Grün et al. 2010**, *BMC Neurosci* 11(Suppl 1):O15 (biomedcentral)
- **Pipa et al. 2008**, *J Comput Neurosci* 25(1):64–88 (Springer) — the NeuroXidence paper

**Two attribution corrections Gerstein forces**, now recorded: the dithering root is **Date,
Bienenstock & Geman 1998** (his own abstract says so, and it was already on the shelf); and he says
flat dither *adds* short intervals — he does **not** claim intervals shorter than any real one. That
stronger claim is bugarach's own measurement and was misattributed.

`surrogates/` and `ml/` had **no `README.md`** — fourteen PDFs in the state the shelf's top-level
README calls "indistinguishable from a PDF someone downloaded and forgot". Both written.

Still open on [`docs/lit_needed.md`](../lit_needed.md): **Louis, Borgelt & Grün 2010 ch. 17** — the
"paywalled" label was wrong, an open copy is at `portal.g-node.org/advanced-course-2019/`; and
**Stella, Quaglio, Torre & Grün 2019 3d-SPADE**, named by the review as the closest prior art for
what this screen does, along with `INM-6/SPADE_surrogates` and `INM-6/SPADE_applications`.

**Fetch routes that work** (now in INDEX row 124): publisher first — biomedcentral
`/counter/pdf/<doi>.pdf`, Springer `/content/pdf/<doi>.pdf`, ane.pl. Every PMC link returns a
bot-check. Europe PMC REST is half a route: `fullTextXML` serves metadata, `fullTextPDF` returns
**0 bytes**.

**Shelve what you fetch, in the same change.** Reviewers cannot deposit — judgment roles hold no
write tool, shell-holding roles are asked to keep to a scratch path — so the adjudicating thread is
the only legitimate operator. On 2026-09-12 one blind round paid for the same download twice.

---

## Traps this session hit, so the next one does not

- **`test_index_resolves.py` treats a backticked span containing `/` as a repo path.** Writing
  `` `surrogates/` `` in an INDEX row turned the suite red (2 failed). Spans with a `<...>`
  placeholder are skipped, which is why `` `<darkroom>/bugarach/lit/surrogates/` `` passes. Use the
  full placeholder form.
- **`murderboard_agents.py verify` captures the tool list with `([^\n|]*)`** — it stops at a pipe,
  so a table row is fine, but a **closing backtick inside the cell is captured as part of the last
  tool name** and fails all eleven roles. Write GRANT lines bare in the cell, no backticks.
- **`murderboard_roster.sh` matches `Mode:` with `^[[:space:]]*[*_|>[:space:]]*Mode:`** — a leading
  hyphen is not in that class, so `- mode: standard` reads as *undeclared*. Use a bare
  `Mode: standard` line.
- **Piping `git diff` into python decodes with the locale, not UTF-8.** A non-ASCII audit written
  that way reports mojibake bytes, every one below 0x100, so a CJK-range test can never fire — the
  check passes because it cannot see. Read `sys.stdin.buffer` and `.decode('utf-8')`.
- **This environment's console is cp1252**; printing non-ASCII from python crashes with
  `UnicodeEncodeError`. Use `ascii()` or set `PYTHONIOENCODING=utf-8`.
- **Use the session scratchpad, not `/tmp`** — `/tmp` writes did not land where expected here.
- **Capture pytest's exit code into a variable.** Piping through `tail` masks it; that mistake
  pushed a commit on a red suite earlier in this thread.

## Verify state before you touch anything

```
git -C ../bugarach-worktrees/surrogate-screen-overnight status -sb
git log --oneline -4            # expect 860e5ee, 6c74f84, 20d2d4c, 0dc6356
python -m pytest -q             # 199 in test_index_resolves; full suite ~49 in the surrogate tests
python tools/check_quotes.py --all && python tools/sapper.py --all
bash tools/murderboard_roster.sh check docs/reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md
python tools/murderboard_agents.py --process docs/doc_review_process.md verify docs/reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md
```

All were green at `860e5ee`.
