# Real inter-event intervals (WSMIP065, ADR-0010 part 2 step 1)

- Measurement only; no bench change. Baseline windows only (FOUNDATIONS section 9).
- Floor: ADR-0008 per-window floor (event_floor.window_floor, 1,000 draws), each baseline window's own.
- Git: 1964ae67cf6093af4e3c966e35161ec1fc2d2f34 (branch real-intervals; PR pending)
- Dataset: senktide_ttx = 2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED, 66 recordings (confirmed by Tony this session; stamped in summary.json and intervals.json)
- Started: 2026-09-25T15:40:04Z

    python tools/measure_real_intervals.py --out <this folder> --workers 44
- Finished: 2026-09-25T15:40:36Z
