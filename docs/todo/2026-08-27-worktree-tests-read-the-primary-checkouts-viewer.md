---
status: open
filed: 2026-08-27
---

# A worktree that edits the viewer fails a test about a file it did not edit

`tests/test_lab_server.py::test_the_server_hands_out_the_page_with_the_shim`
fails in **any worktree that has edited `docs/site/raster_viewer.html`**, and the
message says "the page, unmodified" — which reads as *your edit broke the
server* and is nothing of the kind.

The venv holds one editable install, of the **primary checkout**:

```
$ .venv/bin/python -c "import bugarach.lab as l; print(l.VIEWER)"
<primary checkout>/docs/site/raster_viewer.html      # not the worktree you are in
```

`bugarach/lab.py` resolves `ROOT = Path(__file__).resolve().parents[2]`, so the
server serves the primary checkout's page while the test compares it against the
worktree's. Two different files, and the test is right that they differ.

`PYTHONPATH=$PWD/src` makes the whole file pass (20 passed, 1 skipped), so
nothing is wrong with the code — only with which tree the import lands in. CI
never sees it: one checkout, one page.

Found on 2026-08-27 while adding the Tune panel's sweep-range control, where it
cost a few minutes of thinking the range boxes had broken the lab shim.

**Options, none obviously right:**

- Have `conftest.py` assert the imported `bugarach` lives in the tree under test,
  and say so plainly if it does not. Catches this and every future instance of
  the same confusion, in one place, without changing how anyone runs anything.
- Resolve `VIEWER` from the test's own tree in `test_lab_server.py`. Narrower,
  and leaves the next worktree/editable-install collision to be rediscovered.
- Document it in `docs/git_workflow.md` and move on. Prose did not hold for the
  board claim; no reason to expect better here.

The first is the one worth doing, and it is small.
