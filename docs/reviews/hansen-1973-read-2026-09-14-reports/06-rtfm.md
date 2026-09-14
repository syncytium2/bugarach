GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch (single-pass self-review by the main thread, not a separate agent)

The only method content is the paper's description of greatest-of CFAR. I read it against the 1973 text (pp. 325–327) and against Rohling 1983 eq. 7 and Gandhi & Kassam eq. 22.

| # | location | issue | severity | fix | verifiable |
|---|---|---|---|---|---|
| 1 | §4.1, "a rule for greatest-of's added loss in stationary noise" | The rule reads the general loss curve with an adjusted reference count. It gives greatest-of's total CFAR loss; the added loss is the difference from plain cell-averaging. The divisor is √2. The OCR dropped the radical: the worked example's x/N = 0.22 at 32 cells matches 32/√2, not 32/2. Role 4 confirmed this from the page image. | minor | "a rule for greatest-of's CFAR loss … with the number of reference samples divided by √2" | yes |
| 2 | §4.1, Fig. 5 example | The example is a single computed case. It was run with 32 reference cells, linear envelope detection and Pf = 10⁻⁵, and the paper notes that the detector law matters. | minor | State the conditions | yes |
| 3 | The mechanism statement "estimate the background independently from the leading and lagging reference samples and use the greatest" | Matches greatest-of as defined in Rohling (eq. 7) and Gandhi & Kassam (eq. 22). | no finding | — | yes |
