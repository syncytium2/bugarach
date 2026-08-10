function gen_ref_cicada(inFile, outFile)
%gen_ref_cicada  Reference outputs for the bugarach CICADA parity test.
%   Runs generate_sce_cicada on an event_store built from the exported trains.
%   rise_dur is attached exactly as explore_sce>prepareSlice does (peak locs
%   minus t50rise, per ROI). RNG: randi(nf-1) per cell per surrogate — one
%   double per draw, floor(rand*k)+1 (verified equal on the shared stream).

d = load(inFile);

nreg = numel(d.regions_start);
regions = struct('name', {}, 'slot', {}, 'start_sec', {}, 'end_sec', {});
for k = 1:nreg
    regions(k).name = d.regions_name{k};
    regions(k).slot = d.regions_slot{k};
    regions(k).start_sec = d.regions_start(k);
    regions(k).end_sec = d.regions_end(k);
end
fast = struct('locs', {d.fast_locs}, 't50rise', {d.fast_t50rise}, 'width', {d.fast_width});
slow = struct('locs', {d.slow_locs}, 't50rise', {d.slow_t50rise}, 'width', {d.slow_width});
fast.rise_dur = cellfun(@(pk,on) pk(:) - on(:), fast.locs, fast.t50rise, 'UniformOutput', false);
slow.rise_dur = cellfun(@(pk,on) pk(:) - on(:), slow.locs, slow.t50rise, 'UniformOutput', false);
es = struct('slice_id', d.slice_id, 'fast', fast, 'slow', slow, 'regions', regions);

CASES = { ...
    struct('scope','global',   'nsync',2, 'pct',[99.99 99.9999], 'nsur',50, ...
           'mindist',4,  'admode','fixed',     'dfield','',         'adur',[1 2]), ...
    struct('scope','global',   'nsync',2, 'pct',99.9,  'nsur',50, ...
           'mindist',10, 'admode','per_event', 'dfield','rise_dur', 'adur',[1 2]), ...
    struct('scope','regional', 'nsync',3, 'pct',[99.9 99.99], 'nsur',50, ...
           'mindist',4,  'admode','fixed',     'dfield','',         'adur',[0.5 1]), ...
    struct('scope','global',   'nsync',1, 'pct',99.5,  'nsur',30, ...
           'mindist',4,  'admode','per_event', 'dfield','width',    'adur',[1 2])};

out = struct();
for ci = 1:numel(CASES)
    c = CASES{ci};
    cic = generate_sce_cicada(es, 'threshold_scope', c.scope, ...
        'n_synchronous_frames', c.nsync, 'sce_percentile', c.pct, ...
        'n_surrogates', c.nsur, 'sce_min_distance_frames', c.mindist, ...
        'imaging_rate_hz', 10, 'onset_field', 't50rise', ...
        'active_duration_mode', c.admode, 'duration_field', c.dfield, ...
        'active_duration_sec', c.adur, 'rng_seed', 20260706, 'emit_signal', true);
    cres = struct('params', c);
    cres.ext = cic.params.recording_extent;
    for stream = {'FAST', 'SLOW'}
        st = stream{1};
        s = cic.(st);
        r = struct();
        r.onset_sec = s.onset_sec(:).'; r.width_sec = s.width_sec(:).';
        r.magnitude = s.magnitude(:).'; r.mag_total = s.mag_total(:).';
        r.threshold = s.threshold(:).';
        r.region = cellstr(s.region(:).');
        r.in_stats_window = s.in_stats_window(:).';
        r.meets_floor = s.meets_floor(:).';
        stride = 50;
        r.sig_n = numel(s.signal.t);
        r.sig_t_first = s.signal.t(1); r.sig_t_last = s.signal.t(end);
        r.sig_y_sub = s.signal.y(1:stride:end).'; r.stride = stride;
        r.sig_y_sum = sum(s.signal.y); r.sig_y_max = max(s.signal.y);
        r.sig_thr = arrayfun(@(w) struct('label', char(w.label), 'value', w.value, ...
            'win_start', w.win_start, 'win_end', w.win_end), s.signal.threshold);
        cres.(st) = r;
    end
    out.(sprintf('case%d', ci)) = cres;
end

fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end
