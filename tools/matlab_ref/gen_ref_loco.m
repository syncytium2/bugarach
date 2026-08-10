function gen_ref_loco(inFile, outFile)
%gen_ref_loco  Reference outputs for the bugarach LoCo parity test.
%   Builds an event_store struct from the exported trains/regions and runs
%   detect_loco (both streams per call — FAST then SLOW share one RNG stream,
%   seeded per call). Case params cover maxlt/symmetric, both modes.

d = load(inFile);

nreg = numel(d.regions_start);
regions = struct('name', {}, 'slot', {}, 'start_sec', {}, 'end_sec', {});
for k = 1:nreg
    regions(k).name = d.regions_name{k};
    regions(k).slot = d.regions_slot{k};
    regions(k).start_sec = d.regions_start(k);
    regions(k).end_sec = d.regions_end(k);
end
es = struct('slice_id', d.slice_id, ...
            'fast', struct('locs', {d.fast_locs}, 't50rise', {d.fast_t50rise}), ...
            'slow', struct('locs', {d.slow_locs}, 't50rise', {d.slow_t50rise}), ...
            'regions', regions);

CASES = { ...
    struct('mode','threshold', 'bin',[1 2], 'ctx',[120 60], 'pctile',99.9, ...
           'nsur',100, 'tstep',[15 30], 'mgap',[2 4], 'nullmode','maxlt'), ...
    struct('mode','threshold', 'bin',[1 2], 'ctx',[60 60], 'pctile',95, ...
           'nsur',50, 'tstep',[30 30], 'mgap',[2 4], 'nullmode','symmetric'), ...
    struct('mode','peak', 'bin',[1 2], 'ctx',[120 60], 'pctile',99.9, ...
           'nsur',100, 'tstep',[15 30], 'mgap',[2 4], 'nullmode','maxlt', 'P',3, 'D',10), ...
    struct('mode','peak', 'bin',[1 2], 'ctx',[60 60], 'pctile',95, ...
           'nsur',50, 'tstep',[30 30], 'mgap',[2 4], 'nullmode','symmetric', 'P',0, 'D',0)};

out = struct();
for ci = 1:numel(CASES)
    c = CASES{ci};
    args = {'bin_width_sec', c.bin, 'context_win_sec', c.ctx, ...
            'threshold_pctile', c.pctile, 'min_rois', 3, ...
            'n_surrogates', c.nsur, 'thr_step_sec', c.tstep, ...
            'merge_gap_sec', c.mgap, 'null_context_mode', c.nullmode, ...
            'onset_field', 't50rise', 'rng_seed', 20260706, 'emit_signal', true};
    if strcmp(c.mode, 'peak')
        args = [args, {'detection_mode', 'peak', 'peak_prominence', c.P, ...
                       'peak_min_distance_sec', c.D}]; %#ok<AGROW>
    end
    lc = detect_loco(es, args{:});
    cres = struct('params', c);
    cres.ext = lc.params.recording_extent;
    for stream = {'FAST', 'SLOW'}
        st = stream{1};
        s = lc.(st);
        r = struct();
        r.onset_sec = s.onset_sec(:).'; r.width_sec = s.width_sec(:).';
        r.magnitude = s.magnitude(:).'; r.mag_total = s.mag_total(:).';
        r.threshold = s.threshold(:).';
        r.region = cellstr(s.region(:).');
        r.in_stats_window = s.in_stats_window(:).';
        r.meets_floor = s.meets_floor(:).';
        r.peak_sec = s.peak_sec(:).'; r.t50rise = s.t50rise(:).'; r.t50fall = s.t50fall(:).';
        r.nb = numel(s.signal.t);
        r.t_first = s.signal.t(1); r.t_last = s.signal.t(end);
        r.Sobs = s.signal.y(:).';
        r.thrBin = s.signal.threshold(:).';
        cres.(st) = r;
    end
    % region-window provenance (identical across cases; small)
    rw = lc.params.regions;
    cres.rw = arrayfun(@(w) struct('label', char(w.label), 'raw_start', w.raw_start, ...
        'raw_end', w.raw_end, 'win_start', w.win_start, 'win_end', w.win_end, ...
        'meets_floor', w.meets_floor, 'is_baseline', w.is_baseline, 'is_hik', w.is_hik), rw);
    out.(sprintf('case%d', ci)) = cres;
end

fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end
