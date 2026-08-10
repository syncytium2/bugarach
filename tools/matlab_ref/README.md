# MATLAB reference generation

Regenerates the parity-test fixtures in `tests/fixtures/` from interface2's
MATLAB implementation. Needs MATLAB (R2025b used originally) and a local
interface2 checkout.

```bash
# 1. export slice trains to plain v7 .mat (writes ref_input_*.mat next to it)
python tools/matlab_ref/prep_ref_input.py   # edit paths at the bottom first

# 2. run the detectors under MATLAB and dump JSON
matlab -batch "addpath('<interface2>/RateViewer'); addpath('<interface2>'); \
  gen_ref('ref_input_synth.mat','ref_ratedetect_synth.json'); \
  gen_ref_peaks('ref_peak_gate.json')"
```

Path order matters: `RateViewer` must precede `SpikyViewer` — both hold a
`computeEventRate.m`, and only the RateViewer copy has the production 0.1 s
grid. Only references derived from the **synthetic** fixture are committed;
real-slice references are generated locally for spot validation and stay out
of the repo.
