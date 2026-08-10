function gen_ref_sce(inFile, outFile)
%gen_ref_sce  Reference outputs for the bugarach binned-SCE parity test.
%   Runs generate_sce on an event_store built from the exported trains/regions.
%   Cases cover regional/whole, threshold (merge off + on) and peak modes.
%   One seeded RNG stream per call, FAST then SLOW (rand(1,n_roi) per
%   surrogate, empty ROIs included).

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
    struct('mode','threshold', 'analysis','regional', 'bin',10, 'pctile',99, ...
           'nsur',200, 'min_rois',3, 'mgap',NaN), ...
    struct('mode','threshold', 'analysis','regional', 'bin',2, 'pctile',95, ...
           'nsur',100, 'min_rois',3, 'mgap',3), ...
    struct('mode','peak', 'analysis','regional', 'bin',2, 'pctile',99, ...
           'nsur',200, 'min_rois',3, 'mgap',NaN, 'P',3, 'D',20), ...
    struct('mode','threshold', 'analysis','whole', 'bin',10, 'pctile',99, ...
           'nsur',200, 'min_rois',3, 'mgap',NaN), ...
    struct('mode','peak', 'analysis','whole', 'bin',5, 'pctile',95, ...
           'nsur',100, 'min_rois',3, 'mgap',NaN, 'P',0, 'D',0)};

out = struct();
for ci = 1:numel(CASES)
    c = CASES{ci};
    args = {'analysis_mode', c.analysis, 'bin_width_sec', c.bin, ...
            'threshold_pctile', c.pctile, 'n_surrogates', c.nsur, ...
            'min_rois', c.min_rois, 'merge_gap_sec', c.mgap, ...
            'onset_field', 't50rise', 'rng_seed', 20260706, 'emit_signal', true};
    if strcmp(c.mode, 'peak')
        args = [args, {'detection_mode', 'peak', 'peak_prominence', c.P, ...
                       'peak_min_distance_sec', c.D}]; %#ok<AGROW>
    end
    sce = generate_sce(es, args{:});
    cres = struct('params', c);
    cres.ext = sce.params.recording_extent;
    for stream = {'FAST', 'SLOW'}
        st = stream{1};
        s = sce.(st);
        r = struct();
        r.onset_sec = s.onset_sec(:).'; r.width_sec = s.width_sec(:).';
        r.magnitude = s.magnitude(:).'; r.mag_total = s.mag_total(:).';
        r.threshold = s.threshold(:).';
        r.region = cellstr(s.region(:).');
        r.in_stats_window = s.in_stats_window(:).';
        r.meets_floor = s.meets_floor(:).';
        r.peak_sec = s.peak_sec(:).'; r.t50rise = s.t50rise(:).'; r.t50fall = s.t50fall(:).';
        r.sig_t = s.signal.t(:).'; r.sig_y = s.signal.y(:).';
        r.sig_thr = arrayfun(@(w) struct('label', char(w.label), 'value', w.value, ...
            'win_start', w.win_start, 'win_end', w.win_end), s.signal.threshold);
        cres.(st) = r;
    end
    out.(sprintf('case%d', ci)) = cres;
end

fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end
