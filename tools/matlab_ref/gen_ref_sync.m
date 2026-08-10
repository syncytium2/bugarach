function gen_ref_sync(inFile, outFile)
%gen_ref_sync  Reference outputs for the bugarach SPIKE-synchronization parity
%   test. Builds the cSPIKE index (SpikyRun), computes the tau-capped adaptive
%   synchrony profile, then SpikyDetect3 via runSpikyDetectionAdaptive
%   (incl. artifact flagging). Deterministic — no RNG. Dumps the RAW profile
%   (x, y) per stream/tau for cross-library comparison against PySpike.

d = load(inFile);

lo = inf; hi = -inf;
vals = [d.regions_start(:); d.regions_end(:)];
vals = vals(isfinite(vals));
if ~isempty(vals), lo = min(lo, min(vals)); hi = max(hi, max(vals)); end
allLocs = [d.fast_locs, d.slow_locs];
for k = 1:numel(allLocs)
    v = allLocs{k};
    if ~isempty(v), lo = min(lo, min(v)); hi = max(hi, max(v)); end
end
ext = [lo hi];

% per-stream viewer defaults: tau cap FAST 0.25 / SLOW 0.5, max_gap 0.5 / 2
TAU = struct('fast', 0.25, 'slow', 0.5);
GAP = struct('fast', 0.5,  'slow', 2.0);

CASES = { ...
    struct('mode','threshold', 'stat','mean', 'Cthr',0.1,  'Cmin',0.1,  'minn',3, 'tau','stream'), ...
    struct('mode','threshold', 'stat','max',  'Cthr',0.05, 'Cmin',0.05, 'minn',2, 'tau','stream'), ...
    struct('mode','peak',      'stat','mean', 'Cthr',0.1,  'Cmin',0.1,  'minn',3, 'tau','stream', 'P',0.1, 'D',1.0), ...
    struct('mode','threshold', 'stat','mean', 'Cthr',0.1,  'Cmin',0.1,  'minn',3, 'tau',1e6)};

out = struct('ext', ext);
for stream = {'fast', 'slow'}
    st = stream{1};
    trains = d.([st '_t50rise']);
    sp = cell(1, numel(trains));
    for k = 1:numel(trains)
        v = reshape(trains{k}, 1, []); v = v(isfinite(v));
        sp{k} = v(v >= ext(1) & v <= ext(2));
    end
    el = SpikyRun(sp, ext(1), ext(2));
    el.spikes_sorted = sp;

    sres = struct();
    profiles = struct();
    for ci = 1:numel(CASES)
        c = CASES{ci};
        if ischar(c.tau) || isstring(c.tau), tau = TAU.(st); else, tau = c.tau; end
        ap = computeAdaptiveProfile(el, tau);
        pkey = sprintf('tau%d', round(tau * 1000));
        if ~isfield(profiles, pkey)
            profiles.(pkey) = struct('tau', tau, 'x', ap.x(:).', 'y', ap.y(:).');
        end
        sds = struct('max_gap', GAP.(st), 'dt', 0.1, 'C_threshold', c.Cthr, ...
                     'C_min', c.Cmin, 'min_n', c.minn);
        if strcmp(c.mode, 'peak')
            sds.detection_mode = 'peak';
            sds.peak_prominence = c.P;
            sds.peak_min_distance_sec = c.D;
        end
        [sy, Cy2, Cx2] = runSpikyDetectionAdaptive(el, ap, sds, c.stat);
        r = struct('params', c, 'tau_used', tau);
        r.locs = sy.locs(:).'; r.widths = sy.widths(:).'; r.amps = sy.amps(:).';
        r.onsets = sy.happy_endings(:,1).'; r.ends = sy.happy_endings(:,2).';
        r.peak_C = sy.peak_C(:).'; r.plat90 = sy.plat90(:).';
        r.n_part = sy.n_participating_rois(:).';
        r.is_artifact = sy.is_artifact(:).';
        stride = 25;
        r.stride = stride;
        r.C_n = numel(Cy2);
        r.Cx_first = Cx2(1); r.Cx_last = Cx2(end);
        r.Cy_sub = Cy2(1:stride:end); r.Cy_sum = sum(Cy2); r.Cy_max = max(Cy2);
        sres.(sprintf('case%d', ci)) = r;
    end
    sres.profiles = profiles;
    out.(st) = sres;
end

fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end
