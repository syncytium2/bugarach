# Orchestrator session 01Jfi: the floor needs a rethink, and the bench needs treatment periods

End-of-session summary from the bugarach orchestrator, Claude session
`session_01JfiRdkQXtxUauipSu5UxGY` (named here because another orchestrator session was finishing
up at the same time). It covers 2026-09-25 to 2026-10-07; the work was 2026-09-26 to 09-28. Times
are Michigan local time (EDT). **Nothing is running.** Both worker sessions (064 and 065, the
"20250925" pair) were paused by Tony on 2026-09-28, and the 065 used here is now archived.

## What changed in our understanding

1. **The simple rule is the method.** Sliding simple (`count_sliding`: distinct ROIs with an onset
   in a sliding 2 s window, called at the floor) matches retuned CoactDetect on the bench. On real
   baseline recordings they agree at least as well as CoactDetect agrees with itself. The learned
   models add under 0.02 F1 (dimensionless). The event floor (ADR-0008) does almost all the work,
   and its chance calculation uses the same statistic on shuffles, so the method is one statistic
   plus a permutation threshold.
2. **The bench cannot validate it.** The realistic bench (ADR-0010) takes its intervals from the
   same count, so a good score there is circular. Tony: *"this is circular"*.
3. **One floor per window fails under senktide.** On the real raster pages
   (darkroom `2026-09-28-senktide-rasters/`):
   - the window's own floor is raised by the senktide surge and misses later coordinated events
     in OVX and ORX;
   - the baseline floor carried over calls the surge wall to wall;
   - 20240814a47 (OVX, 17 ROIs) gets a floor of 18. Its surge lasts 82–90 s, longer than a ±20 s
     rigid shift can break (`a47-floor/`).
4. **The surge is chance at a raised rate, not one coordinated block** (`2026-09-28-surge-test/`).
   Against each ROI's local event rate the count stays under the 99.9th-percentile band at least
   93% of the surge, with brief excursions in DI, MALE and ORX. That supports ADR-0006.
5. **A local-rate threshold works where the window floor fails** (`local-rate-floor/`, PR #856).
   The threshold at each moment comes from each ROI's own event rate within ±30 s or ±60 s. It
   matches the floor at baseline, sits between the two floors under senktide, keeps calling in
   OVX and ORX after the surge, and makes a47 callable.
6. **Merging.** The 2 s window plus the 3 s merge gap joins coordinated events less than about
   5 s apart. Tony found them on the DI combined senktide page; `split_dip` (#852, merged) and
   #854 address it. Some pairs never drop below the floor between them, so no merge rule
   separates them.
7. **The export.** Tony found motion-correction exclusion windows that don't match the register
   window: 20260629_309 ROI 16 is over-excluded, 20260630_316 ROI 2 under-excluded. He is fixing
   it in interface2. Analyses wait for the corrected export, which then becomes the `default` in
   `current_export.toml`.

## Open PRs (all waiting on Tony; none set to auto-merge unless noted)

| PR | What | State |
|---|---|---|
| #848 | ADR-0012 (Proposed): one function builds the bench | decision pending |
| #851 | calibrated participation and jitter; jitter verdict: believe the correlogram | stacked on #848 |
| #853 | floor sensitivity tool (window width matters most; false-alarm rate and minimum barely do) | auto-merge off by hold |
| #854 | two calls never share an onset | ready; not auto-merged by Tony's pause |
| #855 | ADR-0013 (Proposed): the bench simulates treatment periods, with intervals, participation and jitter swept as difficulty axes | 7 open points |
| #856 | opt-in local-rate threshold for `count_sliding` | decision pending |

## Decisions waiting on Tony, in order

1. Accept or amend ADR-0013, and write the one sentence it needs in FOUNDATIONS §9: treatment
   windows may supply background event rates, while coordination comes from baseline only.
2. Which threshold to adopt. The local-rate threshold is the leading candidate, to be scored on
   the ADR-0013 bench.
3. The merge rule: current, 0.5 s merge gap, split at a dip, or 1 s window.
4. ADR-0012 / #848 and #851.
5. Older items: what ships (sliding simple as primary, CoactDetect as a check, learned models
   dropped), the fast-gallery verdict, the units rule for tables, methods PR #835, armory #23.

## Unexplained: the 065 session looking for missing t50rise

Tony, 2026-10-07: a 065 session "looking for missing t50rise" finished. **This orchestrator did not
request it**, and the 065 session briefed here (`065 bugarach 20260925`) was archived without
working on it. Its origin and result are not recorded in this session. `t50rise` is the onset
field every analysis reads (`assess_coactivity(onset_field="t50rise")`), so its result may bear on
the export fix. Whoever picks this up should read that session's report first.

## Lessons for the next orchestrator

- **Check worker times against file stamps before relaying them.** One worker's shell ignored the
  time zone and reported times up to 50 minutes late, and this session passed them on.
- **Workers read queued messages only between steps.** A hold sent while a worker is launching
  can arrive after the work is done.
- **The export is the input.** Don't put data-quality speculation into briefs or summaries
  (Tony, 2026-09-28).
- **Every table header states the quantity and its unit**, in chat as much as in files.
