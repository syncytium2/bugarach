function gen_ref_peaks(outFile)
%gen_ref_peaks  Reference micro-cases for the if2_peak_gate port parity test.
%   Deterministic crafted traces covering the semantics the port must match:
%   plateau left-edge reporting, staircase shoulders, tie-breaking under
%   min-distance, per-sample thresholds, NaN boundaries, exact-boundary
%   prominence/threshold comparisons, floor gate, and a smooth mixed trace.

cases = {};

% 1. simple triangles
cases{end+1} = mk('triangles', ...
    [0 1 3 1 0 2 6 2 0 1 4 1 0], 0.5, struct());

% 2. flat-topped plateau (left-edge reporting)
cases{end+1} = mk('plateau', ...
    [0 1 4 4 4 1 0 2 5 5 2 0], 0.5, struct());

% 3. rising staircase (shoulders are not peaks)
cases{end+1} = mk('staircase', ...
    [0 0 1 1 2 2 3 3 4 4], -1, struct());

% 4. equal twin peaks inside min-distance (stable descend sort keeps earlier)
cases{end+1} = mk('twin_ties', ...
    [0 5 0 0 5 0 0 0 3 0], 1, struct('min_distance', 4));

% 5. per-sample rolling threshold
S = [0 2 0 4 0 6 0 8 0];
cases{end+1} = mk('rolling_thr', S, [3 3 3 3 3 5 5 5 5], struct());

% 6. NaN-separated segments
cases{end+1} = mk('nan_bounds', ...
    [0 3 0 NaN 0 4 0 NaN NaN 2 5 2], 1, struct());

% 7. prominence exactly equal to gate P (boundary semantics)
cases{end+1} = mk('prom_boundary', ...
    [0 2 0 0 3 0], 0.5, struct('prominence', 2));

% 8a/8b. peak value exactly at threshold, strict vs non-strict
cases{end+1} = mk('thr_strict', [0 4 0 0 6 0], 4, struct('strict_above', true));
cases{end+1} = mk('thr_nonstrict', [0 4 0 0 6 0], 4, struct('strict_above', false));

% 9. floor gate
cases{end+1} = mk('floor', [0 3 0 0 8 0], 1, struct('floor', 5));

% 10. smooth mixture (deterministic; fractional half-prom edges + thinning)
x = 0:0.05:20;
S = 3*sin(x) + 2*sin(2.7*x + 0.4) + 1.5*sin(0.31*x + 2.0);
cases{end+1} = mk('smooth', S, 1.0, ...
    struct('prominence', 1.2, 'min_distance', 15));

out = struct('cases', {cases});
fid = fopen(outFile, 'w'); fwrite(fid, jsonencode(out)); fclose(fid);
fprintf('wrote %s\n', outFile);
end

function c = mk(name, S, thr, opts)
pk = if2_peak_gate(S, thr, opts);
c = struct('name', name, 'S', S, 'thr', thr, 'opts', opts, ...
           'idx', pk.idx(:).', 'val', pk.val(:).', ...
           'prominence', pk.prominence(:).', ...
           'width_samples', pk.width_samples(:).', ...
           'left_x', pk.left_x(:).', 'right_x', pk.right_x(:).');
end
