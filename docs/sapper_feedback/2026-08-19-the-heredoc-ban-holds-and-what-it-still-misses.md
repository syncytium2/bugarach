---
rule: none-yet
status: open
filed: 2026-08-19
kind: settled dispute + one genuine gap in the vendored hook
---

# The heredoc ban holds. Read this before arguing it is over-broad

**If you are about to propose that quoted heredocs (`<<'EOF'`) are safe and the
gate should allow them — that argument was made on 2026-08-19, tested, and lost.
The evidence is two commands long and is below. Do not spend the afternoon again.**

Tony banned writing source through shell heredocs because session after session was
rewriting steps it had already done. `.claude/hooks/no-heredoc-source.sh` (vendored
from interface2) enforces it. His standing condition, 2026-08-19: *"if it can be
smarter great, but if i continue to see heredoc issues i will ban it again."*

## What happened

A session used quoted heredocs about thirty times in one night, checked its output,
found no damage, and concluded the gate was over-broad. It then read the hook's own
justification — two MATLAB failures — and found that neither of them is caused by a
heredoc at all. That part is correct and is the genuine gap in §3 below.

It then generalised from that to "heredocs are fine", which is wrong, and testing
the failure modes that actually bite showed why.

## 1. Unquoted delimiter: the shell eats the content

```sh
cat > d.py <<EOF
home  = "$HOME/data"
stamp = "$(date +%Y)"
price = "$5 per unit"
EOF
```

lands on disk as:

```python
home  = "/Users/<someone>/data"      # a personal path baked in — see SAP004
stamp = "2026"                        # frozen at write time
price = " per unit"                   # $5 expanded to nothing and vanished
```

Every line looks plausible in a diff. The third one silently lost data.

## 2. Delimiter collision: the file is truncated and the rest becomes shell

**This one defeats the quoted form too, which is the reason there is no safe subset
to carve out.** Content containing the delimiter ends the heredoc early:

```sh
cat > c.py <<'PYEOF'
doc = """
PYEOF
still_here = True
```

`c.py` is one line. `still_here = True` was handed to the shell, which answered
`command not found: still_here`. A file that ends mid-thought, and a session that
has to write it again — which is the complaint the ban came from.

Any delimiter can collide: `EOF` in a document about heredocs, `PYEOF` in a test
that quotes one, `JSEOF` in a file that discusses them. Choosing a rarer delimiter
lowers the odds and does not change the failure.

## 3. What the hook still misses, and it is the failure it is named after

The hook justifies itself with two MATLAB incidents:

```
sprintf('... \rightarrow ...')  -> printed "ightarrow"
warning('... %s\n   %s', ...)   -> string terminated early
```

**Neither is shell mangling.** Written through a heredoc — quoted *or* unquoted —
those lines reach disk byte for byte intact:

```sh
cat > q.m <<'EOF'   # ...and the same content with <<EOF
fprintf('(%s) %6.1f \rightarrow %6.1f\n', a, b, c);
EOF
diff q.m u.m        # IDENTICAL
```

The corruption happens later, when MATLAB's own `sprintf` reads `\r` as a carriage
return. Demonstrable without MATLAB, because C's `printf` does the same:

```sh
$ printf 'sees this: \rightarrow\n'
ightarrow
```

So a session that dutifully switches to the Write tool produces an identical file
and the identical `ightarrow`. **The gate does not prevent the failure it cites**,
and its message tells the reader that it does — which is the shape of a check that
manufactures confidence, the same defect its own header records about failing open.

The fix belongs in the same family as sapper's other rules: flag, in `.m` files, a
single-quoted format string passed to `sprintf`/`fprintf`/`warning`/`error`
containing `\` followed by a letter that is not one of MATLAB's real escapes
(`n t r f v \\ %% ' a b`). `\rightarrow`, `\alpha`, `\Delta`, `\times` — the LaTeX
that goes into figure labels — all match; `\n` and `\t` do not. Known-good
exception: strings already doubled as `\\rightarrow`.

That is a bugarach-side rule proposal. **The hook itself is vendored and must not be
edited here** — its misleading justification is interface2's to correct, and this
file is the report to hand them.

## The verdict

- **The ban stays.** §2 alone justifies it, and it applies to every delimiter.
- **There is no safe subset.** Quoting fixes §1 and does nothing for §2.
- **Use Write and Edit for source files.** They take content literally.
- **Do not relax the gate on the strength of §3.** That §3 is real makes the gate
  *incomplete*, not *unnecessary* — the two failures it does prevent are above.

One more thing worth recording, because it is why this got argued at all: the
session making the case had used heredocs thirty times that night and wanted them to
have been fine. A rule that has cost you nothing yet is the easiest one to talk
yourself out of.
