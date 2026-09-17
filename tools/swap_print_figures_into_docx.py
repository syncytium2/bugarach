"""Swap print figures into Tony's edited docx, in place, keeping every text edit.

Finds each old figure by its exact bytes in word/media, replaces the image, and rescales the drawing's
height (wp:extent and a:ext) to the new image's aspect at the same width. Backs the file up first.
"""
import hashlib
import re
import shutil
import struct
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bugarach.paths import darkroom  # noqa: E402

D = darkroom() / "2026-09-15-detector-review-plain"
DOC = D / "detector_review_plain-td.docx"
#: Only figures not yet swapped: a swapped figure's old bytes are gone from the docx, so a done pair would
#: stop the run ("found n of m"). Done so far: fig_orient, fig_problem, fig_chance (1-3).
#: Done so far: 1-3, 10-15 (swapped once, then redrawn shorter from the bytes kept in `swapped_v1/`).
PAIRS = {"fig_scores.png": "print_figures/fig18_scores.png",
         "fig_busy.png": "print_figures/fig19_busy.png"}


def png_size(b):
    return struct.unpack(">II", b[16:24])


md5 = lambda b: hashlib.md5(b).hexdigest()   # noqa: E731
old_by_hash = {md5((D / o).read_bytes()): o for o in PAIRS}
backup = D / "detector_review_plain-td.before-print-figures.docx"
if not backup.exists():
    shutil.copyfile(DOC, backup)

zin = zipfile.ZipFile(DOC)
rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
doc = zin.read("word/document.xml").decode("utf-8")
replace = {}
for n in zin.namelist():
    if n.startswith("word/media/"):
        o = old_by_hash.get(md5(zin.read(n)))
        if o:
            replace[n] = (D / PAIRS[o]).read_bytes()
if len(replace) != len(PAIRS):
    sys.exit(f"found {len(replace)} of {len(PAIRS)} figures by their bytes; nothing written")

for n, new in replace.items():
    target = n.split("/", 1)[1]
    rid = re.search(r'<Relationship [^>]*Id="(rId\d+)"[^>]*Target="' + re.escape(target) + '"', rels) \
        or re.search(r'<Relationship [^>]*Target="' + re.escape(target) + r'"[^>]*Id="(rId\d+)"', rels)
    rid = rid.group(1)
    w, h = png_size(new)
    # the <w:drawing> holding r:embed="rid"
    m = None
    for dm in re.finditer(r"<w:drawing>.*?</w:drawing>", doc, flags=re.S):
        if f'r:embed="{rid}"' in dm.group(0):
            m = dm
            break
    if m is None:
        sys.exit(f"no drawing for {rid}")
    block = m.group(0)
    cx = int(re.search(r'<wp:extent cx="(\d+)"', block).group(1))
    cy = round(cx * h / w)
    nb = re.sub(r'(<wp:extent cx="\d+" cy=")\d+(")', rf"\g<1>{cy}\g<2>", block)
    nb = re.sub(r'(<a:ext cx="\d+" cy=")\d+(")', rf"\g<1>{cy}\g<2>", nb)
    doc = doc[:m.start()] + nb + doc[m.end():]
    print(n, rid, f"{w}x{h}px", f"height {cy / 914400:.2f} in")

tmp = D / "detector_review_plain-td.swapping.docx"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename in replace:
            zout.writestr(item, replace[item.filename])
        elif item.filename == "word/document.xml":
            zout.writestr(item, doc.encode("utf-8"))
        else:
            zout.writestr(item, zin.read(item))
zin.close()
shutil.move(str(tmp), str(DOC))
print("updated", DOC.name, "; backup", backup.name)
