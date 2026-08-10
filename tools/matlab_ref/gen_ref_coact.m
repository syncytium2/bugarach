function gen_ref_coact(inFile, outFile)
%gen_ref_coact  Reference outputs for the bugarach CoactDetect parity test.
%   Replicates explore_sce's wiring: raw t50rise cells + recording extent into
%   detect_local_coincidence (the function clips internally). Per-stream
%   explore_sce defaults; rng_seed fixed so the surrogate null is reproducible
%   (MATLAB rng(s)+rand == numpy RandomState(s).random_sample, verified).

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

% per-stream explore_sce defaults: int_win / context / alpha differ FAST vs SLOW
P = struct( ...
    'fast', struct('int_win_sec', 2, 'context_win_sec', 60,  'alpha', 1e-4), ...
    'slow', struct('int_win_sec', 1, 'context_win_sec', 120, 'alpha', 1e-6));

out = struct('ext', ext);
for stream = {'fast', 'slow'}
    st = stream{1};
    trains = d.([st '_t50rise']);
    sp = P.(st);
    CASES = { ...
        struct('mode','threshold', 'int_win_sec',sp.int_win_sec, 'context_win_sec',sp.context_win_sec, ...
               'min_rois',3, 'n_surrogates',100, 'alpha',sp.alpha), ...
        struct('mode','threshold', 'int_win_sec',sp.int_win_sec, 'context_win_sec',sp.context_win_sec, ...
               'min_rois',3, 'n_surrogates',50, 'alpha',0.01), ...
        struct('mode','peak', 'int_win_sec',sp.int_win_sec, 'context_win_sec',sp.context_win_sec, ...
               'min_rois',3, 'n_surrogates',100, 'alpha',sp.alpha, 'P',3, 'D',10), ...
        struct('mode','peak', 'int_win_sec',sp.int_win_sec, 'context_win_sec',sp.context_win_sec, ...
               'min_rois',3, 'n_surrogates',50, 'alpha',0.01, 'P',0, 'D',0)};
    sres = struct();
    for ci = 1:numel(CASES)
        c = CASES{ci};
        args = {'int_win_sec', c.int_win_sec, 'context_win_sec', c.context_win_sec, ...
                'min_rois', c.min_rois, 'n_surrogates', c.n_surrogates, ...
                'alpha', c.alpha, 'merge_gap_sec', 3, 'rng_seed', 20260706};
        if strcmp(c.mode, 'peak')
            args = [args, {'detection_mode', 'peak', 'peak_prominence', c.P, ...
                           'peak_min_distance_sec', c.D}]; %#ok<AGROW>
        end
        d5 = detect_local_coincidence(trains, ext, args{:});
        r = struct('params', c);
        ev = d5.events;
        if isempty(ev)
            r.onset_sec = []; r.width_sec = []; r.nrois = []; r.z = []; r.p = [];
            r.peak_sec = []; r.t50rise = []; r.t50fall = [];
        else
            r.onset_sec = [ev.onset_sec]; r.width_sec = [ev.width_sec];
            r.nrois = [ev.nrois]; r.z = [ev.z]; r.p = [ev.p];
            r.peak_sec = [ev.peak_sec]; r.t50rise = [ev.t50rise]; r.t50fall = [ev.t50fall];
        end
        if ci == 1                       % profiles: identical grid across cases
            r.nb = numel(d5.ctr);
            r.ctr_first = d5.ctr(1); r.ctr_last = d5.ctr(end);
            r.obs = d5.obs(:).';         % integer coactivity, full trace
        end
        % z / pval / nullmean are candidate-sparse and RNG-dependent per case
        candi = find(~isnan(d5.z));
        r.cand = candi(:).';
        r.z_cand = d5.z(candi).';
        r.pval_cand = d5.pval(candi).';
        r.nullmean_cand = d5.nullmean(candi).';
        sres.(sprintf('case%d', ci)) = r;
    end
    out.(st) = sres;
end

fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end
