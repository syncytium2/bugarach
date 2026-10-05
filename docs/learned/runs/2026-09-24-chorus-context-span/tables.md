#### Bench, every cell (F1 as scored; intervals are 95% bootstrap over 24 seeds)

| model | trained on | scored on | background | F1 whole | F1 pieces | whole − pieces | whole − pieces, > 30 s from edges | F1 w/o decoys, whole − pieces | stretch calls/min whole · pieces | same, > 30 s from edges | calls near an edge, whole · pieces |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chorus_norm | fast | fast | quiet | 0.795 [0.778, 0.810] | 0.810 [0.796, 0.823] | -0.015 [-0.028, -0.001] | -0.022 [-0.033, -0.011] | -0.013 [-0.027, +0.001] | 0.05 · 0.03 | 0.05 · 0.03 | 60 · 56 |
| chorus_norm | fast | fast | busy | 0.783 [0.765, 0.802] | 0.781 [0.760, 0.802] | +0.001 [-0.014, +0.016] | -0.006 [-0.019, +0.005] | -0.000 [-0.016, +0.016] | 0.02 · 0.01 | 0.02 · 0.01 | 67 · 59 |
| chorus_norm | fast | slow | quiet | 0.834 [0.826, 0.841] | 0.833 [0.826, 0.839] | +0.001 [-0.006, +0.008] | -0.000 [-0.007, +0.006] | +0.003 [-0.006, +0.012] | 0.29 · 0.33 | 0.21 · 0.27 | 76 · 73 |
| chorus_norm | fast | slow | busy | 0.815 [0.804, 0.827] | 0.818 [0.804, 0.831] | -0.003 [-0.011, +0.006] | -0.003 [-0.011, +0.003] | -0.002 [-0.014, +0.009] | 0.23 · 0.27 | 0.18 · 0.21 | 96 · 92 |
| chorus_norm | fast | combined | quiet | 0.828 [0.815, 0.838] | 0.825 [0.813, 0.837] | +0.002 [-0.009, +0.014] | +0.001 [-0.010, +0.009] | +0.006 [-0.007, +0.018] | 0.06 · 0.03 | 0.06 · 0.03 | 75 · 72 |
| chorus_norm | fast | combined | busy | 0.777 [0.757, 0.797] | 0.783 [0.767, 0.798] | -0.005 [-0.015, +0.004] | -0.002 [-0.013, +0.010] | -0.004 [-0.015, +0.009] | 0.01 · 0.01 | 0.01 · 0.01 | 72 · 68 |
| chorus_norm | slow | fast | quiet | 0.664 [0.653, 0.676] | 0.673 [0.660, 0.686] | -0.009 [-0.019, +0.001] | -0.008 [-0.019, +0.000] | -0.010 [-0.021, +0.000] | 0.00 · 0.17 | 0.00 · 0.00 | 42 · 64 |
| chorus_norm | slow | fast | busy | 0.688 [0.673, 0.706] | 0.700 [0.678, 0.721] | -0.011 [-0.025, +0.004] | -0.011 [-0.026, +0.003] | -0.010 [-0.028, +0.007] | 0.00 · 0.19 | 0.00 · 0.00 | 54 · 78 |
| chorus_norm | slow | slow | quiet | 0.837 [0.829, 0.846] | 0.840 [0.831, 0.848] | -0.002 [-0.006, +0.000] | -0.001 [-0.004, +0.000] | -0.001 [-0.004, +0.000] | 0.07 · 0.16 | 0.04 · 0.05 | 68 · 79 |
| chorus_norm | slow | slow | busy | 0.850 [0.844, 0.856] | 0.847 [0.839, 0.855] | +0.003 [-0.003, +0.010] | +0.002 [+0.000, +0.005] | +0.004 [-0.001, +0.010] | 0.07 · 0.18 | 0.04 · 0.05 | 84 · 94 |
| chorus_norm | slow | combined | quiet | 0.709 [0.693, 0.724] | 0.799 [0.786, 0.812] | -0.090 [-0.111, -0.071] | -0.087 [-0.111, -0.064] | -0.096 [-0.118, -0.075] | 0.00 · 0.20 | 0.00 · 0.00 | 59 · 94 |
| chorus_norm | slow | combined | busy | 0.739 [0.718, 0.758] | 0.755 [0.735, 0.773] | -0.016 [-0.032, -0.001] | -0.020 [-0.040, -0.002] | -0.017 [-0.034, -0.000] | 0.00 · 0.21 | 0.00 · 0.00 | 62 · 91 |
| chorus_norm | combined | fast | quiet | 0.696 [0.681, 0.711] | 0.737 [0.719, 0.753] | -0.042 [-0.058, -0.026] | -0.040 [-0.059, -0.022] | -0.045 [-0.063, -0.028] | 0.05 · 0.35 | 0.02 · 0.14 | 52 · 77 |
| chorus_norm | combined | fast | busy | 0.728 [0.711, 0.745] | 0.745 [0.732, 0.757] | -0.018 [-0.030, -0.005] | -0.022 [-0.036, -0.009] | -0.018 [-0.032, -0.003] | 0.07 · 0.28 | 0.03 · 0.12 | 66 · 79 |
| chorus_norm | combined | slow | quiet | 0.843 [0.836, 0.849] | 0.843 [0.836, 0.849] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | 1.00 · 0.72 | 0.81 · 0.56 | 89 · 86 |
| chorus_norm | combined | slow | busy | 0.836 [0.828, 0.844] | 0.836 [0.828, 0.844] | -0.000 [-0.004, +0.004] | -0.004 [-0.007, +0.000] | -0.001 [-0.005, +0.003] | 1.01 · 0.82 | 0.82 · 0.66 | 108 · 103 |
| chorus_norm | combined | combined | quiet | 0.832 [0.825, 0.839] | 0.830 [0.823, 0.837] | +0.003 [-0.003, +0.008] | +0.000 [-0.005, +0.005] | +0.003 [-0.003, +0.008] | 0.03 · 0.20 | 0.00 · 0.08 | 79 · 88 |
| chorus_norm | combined | combined | busy | 0.766 [0.737, 0.792] | 0.777 [0.754, 0.795] | -0.010 [-0.026, +0.005] | -0.011 [-0.029, +0.005] | -0.012 [-0.032, +0.007] | 0.02 · 0.17 | 0.00 · 0.03 | 81 · 95 |
| chorus_gain_norm | fast | fast | quiet | 0.798 [0.781, 0.813] | 0.805 [0.789, 0.819] | -0.007 [-0.020, +0.006] | -0.013 [-0.027, -0.002] | -0.007 [-0.021, +0.007] | 0.00 · 0.00 | 0.00 · 0.00 | 59 · 54 |
| chorus_gain_norm | fast | fast | busy | 0.763 [0.744, 0.782] | 0.762 [0.741, 0.781] | +0.001 [-0.014, +0.016] | -0.003 [-0.021, +0.016] | +0.005 [-0.012, +0.022] | 0.00 · 0.00 | 0.00 · 0.00 | 67 · 65 |
| chorus_gain_norm | fast | slow | quiet | 0.844 [0.837, 0.850] | 0.845 [0.839, 0.851] | -0.001 [-0.003, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | 0.09 · 0.18 | 0.06 · 0.09 | 70 · 76 |
| chorus_gain_norm | fast | slow | busy | 0.821 [0.809, 0.832] | 0.812 [0.798, 0.826] | +0.009 [+0.003, +0.015] | +0.007 [+0.001, +0.013] | +0.011 [+0.003, +0.020] | 0.06 · 0.09 | 0.03 · 0.03 | 90 · 90 |
| chorus_gain_norm | fast | combined | quiet | 0.826 [0.814, 0.838] | 0.827 [0.818, 0.836] | -0.001 [-0.008, +0.007] | -0.003 [-0.010, +0.004] | -0.000 [-0.009, +0.008] | 0.00 · 0.00 | 0.00 · 0.00 | 75 · 74 |
| chorus_gain_norm | fast | combined | busy | 0.719 [0.688, 0.748] | 0.724 [0.698, 0.748] | -0.005 [-0.021, +0.012] | -0.003 [-0.020, +0.012] | +0.001 [-0.017, +0.021] | 0.00 · 0.00 | 0.00 · 0.00 | 69 · 70 |
| chorus_gain_norm | slow | fast | quiet | 0.657 [0.643, 0.671] | 0.655 [0.639, 0.670] | +0.003 [-0.003, +0.009] | -0.002 [-0.005, +0.000] | +0.004 [+0.000, +0.010] | 0.00 · 0.00 | 0.00 · 0.00 | 40 · 39 |
| chorus_gain_norm | slow | fast | busy | 0.674 [0.658, 0.692] | 0.657 [0.634, 0.680] | +0.017 [+0.001, +0.034] | +0.005 [-0.007, +0.016] | +0.023 [+0.006, +0.039] | 0.00 · 0.00 | 0.00 · 0.00 | 51 · 44 |
| chorus_gain_norm | slow | slow | quiet | 0.837 [0.827, 0.848] | 0.837 [0.828, 0.847] | +0.000 [-0.005, +0.005] | +0.000 [+0.000, +0.000] | +0.000 [-0.004, +0.004] | 0.05 · 0.05 | 0.03 · 0.03 | 65 · 66 |
| chorus_gain_norm | slow | slow | busy | 0.852 [0.844, 0.861] | 0.846 [0.835, 0.858] | +0.006 [-0.000, +0.013] | +0.002 [-0.002, +0.007] | +0.007 [+0.003, +0.013] | 0.02 · 0.03 | 0.01 · 0.01 | 82 · 79 |
| chorus_gain_norm | slow | combined | quiet | 0.723 [0.705, 0.739] | 0.708 [0.694, 0.721] | +0.014 [+0.002, +0.026] | +0.008 [-0.002, +0.018] | +0.016 [+0.004, +0.028] | 0.00 · 0.00 | 0.00 · 0.00 | 56 · 50 |
| chorus_gain_norm | slow | combined | busy | 0.661 [0.612, 0.702] | 0.660 [0.613, 0.699] | +0.001 [-0.011, +0.012] | -0.002 [-0.016, +0.011] | -0.001 [-0.014, +0.011] | 0.00 · 0.00 | 0.00 · 0.00 | 48 · 48 |
| chorus_gain_norm | combined | fast | quiet | 0.684 [0.671, 0.698] | 0.682 [0.668, 0.696] | +0.003 [-0.004, +0.010] | +0.000 [-0.006, +0.006] | +0.004 [-0.004, +0.011] | 0.03 · 0.10 | 0.03 · 0.07 | 45 · 45 |
| chorus_gain_norm | combined | fast | busy | 0.704 [0.688, 0.720] | 0.705 [0.682, 0.726] | -0.001 [-0.015, +0.013] | -0.011 [-0.020, -0.003] | +0.001 [-0.013, +0.016] | 0.03 · 0.11 | 0.03 · 0.07 | 56 · 51 |
| chorus_gain_norm | combined | slow | quiet | 0.842 [0.835, 0.848] | 0.837 [0.829, 0.846] | +0.004 [-0.001, +0.011] | +0.003 [+0.000, +0.007] | +0.006 [+0.001, +0.011] | 1.26 · 0.90 | 1.02 · 0.73 | 95 · 81 |
| chorus_gain_norm | combined | slow | busy | 0.838 [0.830, 0.846] | 0.832 [0.822, 0.842] | +0.006 [-0.002, +0.014] | -0.001 [-0.004, +0.000] | +0.007 [+0.000, +0.014] | 1.52 · 1.11 | 1.22 · 0.92 | 120 · 95 |
| chorus_gain_norm | combined | combined | quiet | 0.819 [0.806, 0.831] | 0.819 [0.807, 0.830] | -0.000 [-0.012, +0.013] | -0.010 [-0.021, -0.002] | +0.003 [-0.010, +0.016] | 0.01 · 0.05 | 0.01 · 0.03 | 73 · 64 |
| chorus_gain_norm | combined | combined | busy | 0.764 [0.732, 0.793] | 0.770 [0.746, 0.794] | -0.006 [-0.021, +0.009] | -0.013 [-0.029, +0.001] | -0.002 [-0.018, +0.013] | 0.00 · 0.03 | 0.00 · 0.02 | 76 · 73 |

#### No-coordination recording, calls per hour (12 seeds, 9 hours each mode)

| model | trained on | scored on | whole [95%] | pieces [95%] | whole − pieces [95%] |
|---|---|---|---|---|---|
| chorus_norm | fast | fast | 0.89 [0.11, 1.78] | 0.67 [0.00, 1.44] | +0.22 [+0.00, +0.56] |
| chorus_norm | fast | slow | 0.56 [0.22, 0.89] | 0.22 [0.00, 0.56] | +0.33 [+0.00, +0.67] |
| chorus_norm | fast | combined | 1.22 [0.56, 2.00] | 0.44 [0.11, 0.78] | +0.78 [+0.33, +1.33] |
| chorus_norm | slow | fast | 0.11 [0.00, 0.33] | 0.11 [0.00, 0.33] | +0.00 [+0.00, +0.00] |
| chorus_norm | slow | slow | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| chorus_norm | slow | combined | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| chorus_norm | combined | fast | 0.56 [0.00, 1.33] | 0.11 [0.00, 0.33] | +0.44 [+0.00, +1.22] |
| chorus_norm | combined | slow | 0.33 [0.00, 0.67] | 0.00 [0.00, 0.00] | +0.33 [+0.00, +0.67] |
| chorus_norm | combined | combined | 0.11 [0.00, 0.33] | 0.00 [0.00, 0.00] | +0.11 [+0.00, +0.33] |
| chorus_gain_norm | fast | fast | 0.78 [0.00, 1.67] | 0.56 [0.00, 1.11] | +0.22 [+0.00, +0.56] |
| chorus_gain_norm | fast | slow | 0.33 [0.00, 0.67] | 0.22 [0.00, 0.56] | +0.11 [+0.00, +0.33] |
| chorus_gain_norm | fast | combined | 1.11 [0.33, 2.11] | 0.67 [0.00, 1.44] | +0.44 [+0.11, +0.78] |
| chorus_gain_norm | slow | fast | 0.11 [0.00, 0.33] | 0.11 [0.00, 0.33] | +0.00 [+0.00, +0.00] |
| chorus_gain_norm | slow | slow | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| chorus_gain_norm | slow | combined | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| chorus_gain_norm | combined | fast | 0.11 [0.00, 0.33] | 0.11 [0.00, 0.33] | +0.00 [+0.00, +0.00] |
| chorus_gain_norm | combined | slow | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| chorus_gain_norm | combined | combined | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |

#### Real windows, all groups (calls per hour; share = calls matched one-to-one within 2.5 s)

| model | stream | windows | kind | hours | whole calls/h | pieces calls/h | share of whole calls matched | share of pieces calls matched |
|---|---|---|---|---|---|---|---|---|
| chorus_norm | fast | 66 | baseline | 21.8 | 30.57 | 28.60 | 86.7% | 92.6% |
| chorus_norm | fast | 128 | treatment | 31.4 | 24.05 | 25.01 | 91.1% | 87.6% |
| chorus_norm | fast | 194 | all | 53.2 | 26.73 | 26.48 | 89.0% | 89.9% |
| chorus_gain_norm | fast | 66 | baseline | 21.8 | 19.80 | 19.98 | 92.1% | 91.3% |
| chorus_gain_norm | fast | 128 | treatment | 31.4 | 17.27 | 18.00 | 95.6% | 91.7% |
| chorus_gain_norm | fast | 194 | all | 53.2 | 18.31 | 18.81 | 94.0% | 91.5% |
| chorus_norm | slow | 66 | baseline | 21.8 | 20.99 | 21.22 | 96.7% | 95.7% |
| chorus_norm | slow | 128 | treatment | 31.4 | 35.52 | 36.19 | 97.0% | 95.2% |
| chorus_norm | slow | 194 | all | 53.2 | 29.57 | 30.05 | 96.9% | 95.4% |
| chorus_gain_norm | slow | 66 | baseline | 21.8 | 20.08 | 19.80 | 96.3% | 97.7% |
| chorus_gain_norm | slow | 128 | treatment | 31.4 | 31.03 | 30.71 | 95.9% | 96.9% |
| chorus_gain_norm | slow | 194 | all | 53.2 | 26.54 | 26.24 | 96.0% | 97.1% |
| chorus_norm | combined | 66 | baseline | 21.8 | 46.25 | 45.06 | 92.9% | 95.3% |
| chorus_norm | combined | 128 | treatment | 31.4 | 59.93 | 61.68 | 96.0% | 93.3% |
| chorus_norm | combined | 194 | all | 53.2 | 54.32 | 54.86 | 94.9% | 94.0% |
| chorus_gain_norm | combined | 66 | baseline | 21.8 | 40.61 | 40.24 | 92.8% | 93.6% |
| chorus_gain_norm | combined | 128 | treatment | 31.4 | 54.42 | 54.93 | 94.0% | 93.1% |
| chorus_gain_norm | combined | 194 | all | 53.2 | 48.76 | 48.91 | 93.6% | 93.3% |

#### Real windows by group and window kind

| model | stream | group | windows | whole calls/h | pieces calls/h | share of whole calls matched |
|---|---|---|---|---|---|---|
| chorus_norm | fast | DI · baseline | 17 | 76.76 | 73.41 | 87.8% |
| chorus_norm | fast | DI · treatment | 32 | 41.16 | 40.90 | 94.4% |
| chorus_norm | fast | OVX · baseline | 17 | 11.79 | 10.00 | 77.3% |
| chorus_norm | fast | OVX · treatment | 34 | 11.96 | 16.28 | 84.5% |
| chorus_norm | fast | MALE · baseline | 13 | 30.94 | 27.89 | 87.9% |
| chorus_norm | fast | MALE · treatment | 26 | 25.71 | 24.57 | 91.8% |
| chorus_norm | fast | ORX · baseline | 19 | 5.41 | 5.25 | 85.3% |
| chorus_norm | fast | ORX · treatment | 36 | 19.00 | 19.44 | 88.1% |
| chorus_gain_norm | fast | DI · baseline | 17 | 44.82 | 46.06 | 90.9% |
| chorus_gain_norm | fast | DI · treatment | 32 | 32.26 | 33.28 | 97.6% |
| chorus_gain_norm | fast | OVX · baseline | 17 | 7.50 | 6.96 | 88.1% |
| chorus_gain_norm | fast | OVX · treatment | 34 | 4.32 | 5.06 | 88.6% |
| chorus_gain_norm | fast | MALE · baseline | 13 | 23.44 | 23.44 | 96.0% |
| chorus_gain_norm | fast | MALE · treatment | 26 | 21.15 | 20.67 | 93.8% |
| chorus_gain_norm | fast | ORX · baseline | 19 | 5.73 | 5.73 | 94.4% |
| chorus_gain_norm | fast | ORX · treatment | 36 | 13.28 | 14.58 | 95.1% |
| chorus_norm | slow | DI · baseline | 17 | 48.71 | 48.71 | 96.7% |
| chorus_norm | slow | DI · treatment | 32 | 61.61 | 62.62 | 98.4% |
| chorus_norm | slow | OVX · baseline | 17 | 6.79 | 6.61 | 94.7% |
| chorus_norm | slow | OVX · treatment | 34 | 10.11 | 10.11 | 93.9% |
| chorus_norm | slow | MALE · baseline | 13 | 28.36 | 29.77 | 96.7% |
| chorus_norm | slow | MALE · treatment | 26 | 42.15 | 43.29 | 96.5% |
| chorus_norm | slow | ORX · baseline | 19 | 3.66 | 3.66 | 100.0% |
| chorus_norm | slow | ORX · treatment | 36 | 31.21 | 31.85 | 96.2% |
| chorus_gain_norm | slow | DI · baseline | 17 | 47.12 | 46.76 | 97.0% |
| chorus_gain_norm | slow | DI · treatment | 32 | 55.76 | 55.00 | 96.1% |
| chorus_gain_norm | slow | OVX · baseline | 17 | 6.79 | 6.79 | 100.0% |
| chorus_gain_norm | slow | OVX · treatment | 34 | 7.03 | 6.29 | 87.7% |
| chorus_gain_norm | slow | MALE · baseline | 13 | 26.02 | 25.31 | 94.6% |
| chorus_gain_norm | slow | MALE · treatment | 26 | 38.08 | 38.89 | 98.3% |
| chorus_gain_norm | slow | ORX · baseline | 19 | 3.50 | 3.34 | 90.9% |
| chorus_gain_norm | slow | ORX · treatment | 36 | 26.35 | 26.02 | 95.1% |
| chorus_norm | combined | DI · baseline | 17 | 106.41 | 104.47 | 94.4% |
| chorus_norm | combined | DI · treatment | 32 | 90.82 | 90.57 | 97.5% |
| chorus_norm | combined | OVX · baseline | 17 | 22.32 | 20.71 | 85.6% |
| chorus_norm | combined | OVX · treatment | 34 | 33.79 | 38.85 | 91.2% |
| chorus_norm | combined | MALE · baseline | 13 | 50.86 | 49.92 | 92.6% |
| chorus_norm | combined | MALE · treatment | 26 | 68.83 | 66.88 | 95.7% |
| chorus_norm | combined | ORX · baseline | 19 | 10.19 | 9.87 | 93.8% |
| chorus_norm | combined | ORX · treatment | 36 | 50.64 | 53.67 | 96.8% |
| chorus_gain_norm | combined | DI · baseline | 17 | 92.29 | 90.53 | 93.7% |
| chorus_gain_norm | combined | DI · treatment | 32 | 81.80 | 80.66 | 96.3% |
| chorus_gain_norm | combined | OVX · baseline | 17 | 17.14 | 17.86 | 91.7% |
| chorus_gain_norm | combined | OVX · treatment | 34 | 28.36 | 28.61 | 84.8% |
| chorus_gain_norm | combined | MALE · baseline | 13 | 48.05 | 48.05 | 90.7% |
| chorus_gain_norm | combined | MALE · treatment | 26 | 62.49 | 63.30 | 97.4% |
| chorus_gain_norm | combined | ORX · baseline | 19 | 9.87 | 9.55 | 93.5% |
| chorus_gain_norm | combined | ORX · treatment | 36 | 48.59 | 50.54 | 92.4% |
