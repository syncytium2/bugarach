# Two routes, one folder — the row-for-row comparison

Folder: `2026-08-18_revised_2v_periods` · stream `fast` · detectors `rate,coact,sce`
Matching tolerance 0.05 s — these are two implementations of one algorithm on identical input, not a detector against planted truth.

| detector | CLI rows | browser rows | agreed | CLI only | browser only |
|---|---|---|---|---|---|
| `coact` | 1376 | 1345 | **1224** | 152 | 121 |
| `rate` | 1613 | 1613 | **1613** | 0 | 0 |
| `sce` | 1692 | 1701 | **1681** | 11 | 20 |

Recordings with rows: CLI 80, browser 81.

## The first rows where they part

| detector | recording | stream | onset (s) | which side |
|---|---|---|---|---|
| `coact` | 20240708_13 | fast | 116.000 | CLI only |
| `coact` | 20240708_13 | fast | 1652.000 | browser only |
| `coact` | 20240708_13 | fast | 2086.000 | browser only |
| `coact` | 20240708_13 | fast | 2094.000 | browser only |
| `coact` | 20240708_13 | fast | 2200.000 | CLI only |
| `coact` | 20240708_13 | fast | 2366.000 | CLI only |
| `coact` | 20240708_17 | fast | 1738.000 | CLI only |
| `coact` | 20240708_17 | fast | 1792.000 | browser only |
| `coact` | 20240708_17 | fast | 2320.000 | browser only |
| `coact` | 20240708_17 | fast | 3086.000 | browser only |
| `coact` | 20240723_22 | fast | 4140.000 | browser only |
| `coact` | 20240726_34 | fast | 1362.000 | CLI only |
| `coact` | 20240726_34 | fast | 3918.000 | CLI only |
| `coact` | 20240726_36 | fast | 1118.000 | CLI only |
| `coact` | 20240726_36 | fast | 3256.000 | browser only |
| `coact` | 20240726_36 | fast | 3404.000 | CLI only |
| `coact` | 20240726_36 | fast | 3658.000 | CLI only |
| `coact` | 20240813_39 | fast | 376.000 | CLI only |
| `coact` | 20240813_39 | fast | 1048.000 | browser only |
| `coact` | 20240813_39 | fast | 1232.000 | browser only |
