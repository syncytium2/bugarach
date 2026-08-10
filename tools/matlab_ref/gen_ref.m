function gen_ref(inFile, outFile)
%gen_ref  Reference outputs for the bugarach rate+context detector parity test.
%   Replicates explore_sce's wiring exactly: light shim from t50rise trains,
%   extent = union span of regions + locs (generate_sce>local_recording_extent),
%   RateDetect with rate_win=1 / context_win=60 on the RateViewer (0.1 s) grid.

d = load(inFile);

% ---- extent: regions + LOCS (not t50rise), per local_recording_extent ----
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

CASES = { ...
    struct('mode','threshold','thr',5,'gap',3), ...
    struct('mode','threshold','thr',8,'gap',1), ...
    struct('mode','threshold','thr',100,'gap',3), ...     % no events
    struct('mode','peak','thr',5,'P',2,'D',10), ...
    struct('mode','peak','thr',3,'P',0.5,'D',30)};

out = struct('ext', ext);
for stream = {'fast','slow'}
    st = stream{1};
    trains = d.([st '_t50rise']);
    sp = cell(1, numel(trains));
    for k = 1:numel(trains)
        v = reshape(trains{k}, 1, []); v = v(isfinite(v));
        sp{k} = v(v >= ext(1) & v <= ext(2));
    end
    el = struct('t_range', ext, 'light', true, 'empty', sum(cellfun(@numel, sp)) == 0);
    el.spikes_sorted = sp; el.spikes = sp;
    sres = struct();
    for ci = 1:numel(CASES)
        c = CASES{ci};
        ds = struct('dt', 0.01, 'tmin', ext(1), 'tmax', ext(2), ...
                    'rate_win', 1, 'context_win', 60);
        if strcmp(c.mode, 'peak')
            ds.detection_mode = 'peak';
            ds.peak_prominence = c.P;
            ds.peak_min_distance_sec = c.D;
            [rd, ~, ~, sig] = RateDetect(el, ds, c.thr, 3);
        else
            [rd, ~, ~, sig] = RateDetect(el, ds, c.thr, c.gap);
        end
        r = struct('params', c);
        r.locs      = rd.locs(:).';
        r.widths    = rd.widths(:).';
        r.amps      = rd.amps(:).';
        r.freq_max  = rd.intra_event_freq_max(:).';
        r.freq_mean = rd.intra_event_freq_mean(:).';
        r.hilite    = sig.hilite;                 % Kx2, varies with thr
        if ci == 1                                % traces identical across cases
            stride = 25;
            r.signal_M  = numel(sig.t);
            r.t_first   = sig.t(1);   r.t_last = sig.t(end);
            r.stride    = stride;
            r.y_sub     = sig.y(1:stride:end).';
            r.ref_sub   = sig.ref(1:stride:end).';
            r.y_sum     = sum(sig.y);  r.ref_sum = sum(sig.ref);
            r.y_max     = max(sig.y);  r.ref_max = max(sig.ref);
        end
        sres.(sprintf('case%d', ci)) = r;
    end
    out.(st) = sres;
end

fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end
