# ADR-0001: The lab server — training off the page, without changing what ships

## Status

Accepted, 2026-08-19. Adds a local capability and a publish gate. Changes **nothing** in
the published page — that is the whole design, and it is asserted mechanically rather
than remembered.

Descends from `colonel_kernel`'s ADR-0048, *A dev-only lab mode for loading local
recordings* (its `docs/adr/0048-dev-only-lab-mode.md` — a sibling repo, deliberately not
linked, because a relative path out of this tree resolves for nobody but this machine).
The principles are taken wholesale; the mechanism is different, and the difference is the
interesting part.

## Context

The webapp has to **train the tube network on the user's own recordings**
([`docs/webapp_completion_plan.md`](../webapp_completion_plan.md), stage 6b). Nothing in
the browser does that today, and the page cannot simply call out for it: it promises a
lab that its recordings never leave the computer, and that promise is a property of the
file rather than a paragraph. [`tests/test_site_viewer.py`](../../tests/test_site_viewer.py)
bans `fetch(`, `XMLHttpRequest`, `<script src`, `import(` and six other ways a page can
reach a host, and [`tools/build_site.py`](../../tools/build_site.py) refuses to publish it
otherwise.

So there were three routes, and each buys something different.

**Write the trainer in JS, inline.** Keeps every promise and needs no install. It also
means hand-writing dilated `conv1d` forward and backward, GELU, stride-1 `max_pool1d`
with argmax routing, gradients through the difference-of-Gaussians kernel, and Adam —
roughly a thousand lines of new numerics whose correctness nothing else in the tree
checks. The model is small (1,149 parameters, 5.6 s in PyTorch) so it is *feasible*; it
is not *cheap*, and until it is finished there is no demo at all.

**Ship pretrained weights and infer in the browser.** Cheap, and it deletes the thing
being demonstrated. The claim is that a model fitted to **this lab's** measured
statistics competes with detectors calibrated on the same ground truth. A frozen model
trained on our corpus is not that claim.

**Run the training locally, off the page.** `bugarach.learn.train` and
`bugarach.bench.pool_scores` already exist, have parity tests, and produced every number
in `docs/learned/bakeoff.json`. A transport in front of them is a few hundred lines and
no new dependency — torch is already the optional `dl` extra. The cost is that training
stops being installable-free.

The thing that made the third option acceptable is ADR-0048's shape: a capability that
exists **only locally**, gated so that the published artifact is unchanged, with the
gating asserted rather than inferred. Its closing warning is the one that matters here —
*"'we did not add anything third-party, therefore the privacy property holds' is exactly
the reasoning the Cloudflare beacon disproved"*. That beacon was injected at the edge, was
UA-gated so `curl` could not see it, and served from this project's own domain for over a
week.

**Where the mechanism has to diverge.** colonel_kernel gets its gating free from a
bundler: `import.meta.env.DEV` is substituted to `false` at build time, the branch becomes
dead code, and Rollup emits no chunk for the component at all. bugarach has no bundler.
Its page is a hand-written HTML file and its build is `shutil.copyfile`. Reproducing
ADR-0048 literally would mean **stripping** a marked block during the build — which works,
and costs the property that the file reviewed in git is exactly the file that ships.

## Decision

**A local server that owns the transport; a page that owns the interface and stays
byte-identical to what it ships.**

- **The page owns the UI and the decision.** The training panel lives in
  `docs/site/raster_viewer.html`, inert, behind `if (window.__lab)`. It contains no
  `fetch(`, no `<script src`, nothing on the banned list. `test_site_viewer.py` is
  unchanged and still passes against the source; `build_site.py` still copies the file
  rather than transforming it.
- **The local server owns the transport.** `bugarach lab` serves that same file **from
  disk**, with a shim appended that defines `window.__lab`. The shim holds the only
  `fetch(` in the system and exists only in the copy the local server hands out.
- **Dead by absence, not by stripping.** On the published page nobody injected a shim, so
  `window.__lab` is undefined and the panel never appears. Nothing was removed, so nothing
  can fail to be removed — which retires ADR-0048's stated failure mode (both of its gates
  fail *silently*, and a static import anywhere defeats them) rather than porting it.
- **The server never touches the filesystem.** The page already holds the user's folder
  through the File System Access API. It posts event trains as JSON and receives
  detections and scores back. The server binds `127.0.0.1` only, reads no path, and takes
  no filename from the request.
- **One training path, not two.** The server calls `bugarach.learn.train` and
  `bugarach.bench.pool_scores` — the same functions that produced `bakeoff.json`. A second
  implementation would be free to drift from the one every published number came from.
- **The panel is styled unlike the rest of the app** — the way ADR-0048 marks its `LAB`
  control — so it is never mistaken for something a visitor to the public site has.

**The gate.** A test asserts that the published page defines no transport and that
`site/viewer.html` is identical to `docs/site/raster_viewer.html`. Both halves are needed:
the first catches a shim that migrated into the page, the second catches a build that
started transforming it.

## Consequences

**Good.** Stage 6b becomes a few hundred lines over code that already has parity tests,
rather than a thousand lines of new numerics. The public artifact is unchanged and the
guarantee is checkable instead of remembered. The server, having no filesystem access and
no path handling, has no directory-traversal surface to get wrong — ADR-0048 needed a
serve-by-basename rule precisely because its endpoints read a folder, and this one does
not. And it de-risks the JS trainer: when that lands it has a reference implementation to
match instead of an unanswered question.

**The cost, and it is real.** Training stops being installable-free. Stages 1 through 5
and detection stay pure-browser and reach anybody with a browser; *"train the tube on my
folder"* becomes the one step that wants `pip install bugarach[dl]`. That is a genuine
reduction in reach, accepted on the judgement that a lab training a model on its own
corpus is already a lab that can install a Python package.

**What this does not decide.** The in-browser trainer is **not cancelled** — it is
resequenced. It remains the route to training with no install at all, and this ADR makes
it cheaper by giving it something to be checked against. See
`docs/todo/2026-08-19-lane-c-tube-trainer-in-the-browser.md`.

**The failure mode to watch.** The panel's UI is in the published page and inert there, so
it is a code path CI never renders and visitors never see — it can rot unnoticed. The same
cost ADR-0048 accepted for the same reason, and bounded the same way: it drives the
ordinary loader and the ordinary detector paths rather than a private one.

**A rule the server does not get to relax.** The threshold is chosen on held-out
training-regime data and is **never** re-picked on the recording being analysed. Moving
training to a process with more room does not make a "re-tune on this slice" button
acceptable; it hides exactly the failure the regime-shift test measures
(`docs/learned/regime_shift_fitted.json`).
