# Floor + 1 review, detection run (WSMIP065, for Tony)

- Evidence for a decision Tony has not made. Nothing is adopted; ADR-0008 is unchanged.
- Floor: ADR-0008 per-window floor, bench per ADR-0009, plus a variant own_plus_1 (the window's own floor + 1 co-active ROI).
- Git: c30d88c62eafdbbd14989cb4d44f379a191ec133 (branch floor-plus-one-variant: main f90814c + --floor-offset; PR pending)
- Dataset: senktide_ttx = 2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED, 66 recordings (confirmed by Tony this session; stamped in results.json)
- Detectors: CoactDetect at its SHIPPED setting on every stream; chorus_norm and chorus_gain_norm at last night's picked checkpoints (models from 2026-09-25-final-parameters/064/phase2/models-*); every detector that draws random numbers seeded (#814).
- Candidates: candidates.json, built by floor_plus_one_candidates.py (beside this file).
- Started: 2026-09-25T10:47:39Z

    python tools/detect_with_floors.py --candidates <run/candidates.json> --models <2026-09-25-final-parameters/064/phase2> --floor-offset 1 --workers 44 --out <run>
- Finished: 2026-09-25T10:53:00Z
