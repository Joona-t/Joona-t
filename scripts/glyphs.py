"""The moving glyph grid for the profile header: the name drawn in dense glyphs inside a field of light ones,
with a wave that changes every cell's glyph as it passes.

Cells that share a wave phase are one <text> element with a position per character, so the whole grid is at
most PHASES x FRAMES x 2 animated elements instead of one per cell (1,280 cells here).
"""
import math
from html import escape

FONT5 = {  # 5x7 dot letters
    "J": "00111 00010 00010 00010 00010 10010 01100", "O": "01110 10001 10001 10001 10001 10001 01110",
    "N": "10001 11001 10101 10011 10001 10001 10001", "A": "01110 10001 10001 11111 10001 10001 10001",
    "T": "11111 00100 00100 00100 00100 00100 00100", "Y": "10001 10001 01010 00100 00100 00100 00100",
    "R": "11110 10001 10001 11110 10100 10010 10001", "I": "01110 00100 00100 00100 00100 00100 01110",
    "K": "10001 10010 10100 11000 10100 10010 10001", "S": "01111 10000 10000 01110 00001 00001 11110",
}
COLS, ROWS, CELL_W, CELL_H, TOP = 64, 20, 9, 13, 30
PHASES, FRAMES, CYCLE = 16, 4, 4.8                       # wave steps, glyphs per cell, seconds per cycle
FIELD = [("·", .2), ("·", .32), (":", .4), ("+", .5)]    # the field: glyph and strength for each frame, kept faint
NAME = ["#", "#", "@", "#"]                              # the name: solid "#"; frame 2 ("@") is the lit crest passing
WORDS = (("JOONA", 2), ("TYRNINOKSA", 11))               # word and the grid row it starts on
HEIGHT = TOP + ROWS * CELL_H                             # y where the grid ends


def glyph_grid(uid, t, width):
    """Return (css, svg markup). t needs "ink" (glyph colour) and "hot" (crest colour)."""
    on = set()
    for word, row0 in WORDS:
        for i, ch in enumerate(word):
            for r, bits in enumerate(FONT5[ch].split()):
                on |= {(3 + i * 6 + c, row0 + r) for c, bit in enumerate(bits) if bit == "1"}
    x0 = (width - COLS * CELL_W) / 2 + CELL_W / 2
    cells = {}
    moat = {(c + dc, r + dr) for c, r in on for dc in (-1, 0, 1) for dr in (-1, 0, 1)} - on   # kept empty so the letters read
    for r in range(ROWS):
        for c in range(COLS):
            if (c, r) in moat:
                continue
            ph =int(c * .9 + r * 1.7 + 3 * math.sin(c * .35 + r * .6)) % PHASES
            cells.setdefault((ph, (c, r) in on), []).append((x0 + c * CELL_W, TOP + r * CELL_H))
    out = []
    for (ph, name), pts in sorted(cells.items()):
        xs, ys = " ".join(f"{x:g}" for x, _ in pts), " ".join(f"{y:g}" for _, y in pts)
        for f in range(FRAMES):
            ch, strength = (NAME[f], 1) if name else FIELD[f]
            fill = t["hot"] if name and f == 2 else t["ink"]
            delay = ((f / FRAMES - ph / PHASES) % 1 - 1) * CYCLE
            shown = int(ph / PHASES * FRAMES) == f   # on screen at t=0, and the still under reduced motion
            cls = "gl" + (" nm" if name else "") + ("" if shown else " off")
            out.append(f'<text data-art="1" class="{cls}" style="animation-delay:{delay:.2f}s" x="{xs}" y="{ys}" '
                       f'fill="{fill}" fill-opacity="{strength}">{escape(ch * len(pts))}</text>')
    css = f'''#{uid} .gl {{ font-size: 13px; text-anchor: middle; animation: {uid}-gl {CYCLE}s step-end infinite; }}
#{uid} .nm {{ font-weight: 700; }}
#{uid} .off {{ opacity: 0; }}
@keyframes {uid}-gl {{ 0% {{ opacity: 1; }} {100 / FRAMES:g}%, 100% {{ opacity: 0; }} }}'''
    return css, f'<g aria-hidden="true">{"".join(out)}</g>'
