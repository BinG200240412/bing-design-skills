#!/usr/bin/env python3
"""Audit a converted engraving: two-tone purity + optional grid count.
Usage: audit_engraving.py <image> [gx0 gy0 gx1 gy1]"""
import sys
from PIL import Image

path = sys.argv[1]
img = Image.open(path).convert("L")
W, H = img.size
px = img.load()

# --- two-tone purity: mid-gray fraction ---
hist = img.histogram()
total = W * H
black = sum(hist[:60]) / total
mid = sum(hist[60:201]) / total
white = sum(hist[201:]) / total
ink_coverage = black
print(f"black(<60): {black:.1%}  mid(60-200): {mid:.1%}  white(>200): {white:.1%}")
print("two-tone:", "PASS" if mid < 0.18 else "FAIL (too much gray)")
print(
    f"ink coverage(<60): {ink_coverage:.1%}  target: 30% (PASS range 27%-33%)"
)
if ink_coverage < 0.27:
    print("black-white balance: FAIL (too white; add solid blacks outside faces/skin)")
elif ink_coverage > 0.33:
    print("black-white balance: FAIL (too dark; thin small strokes or add dry-print flecks)")
else:
    print("black-white balance: PASS")

# --- grid count (optional region) ---
if len(sys.argv) > 5:
    RX0, RY0, RX1, RY1 = (int(v) for v in sys.argv[2:6])
    TH = 150
    def lines(axis, frac=0.5, gap=12):
        if axis == "v":
            sc = [sum(1 for y in range(RY0, RY1) if px[x, y] < TH) for x in range(RX0, RX1)]
            span = RY1 - RY0
        else:
            sc = [sum(1 for x in range(RX0, RX1) if px[x, y] < TH) for y in range(RY0, RY1)]
            span = RX1 - RX0
        raw = [i for i, s in enumerate(sc) if s >= span * frac]
        out, cur = [], []
        for i in raw:
            if cur and i - cur[-1] > gap:
                out.append(cur); cur = []
            cur.append(i)
        if cur: out.append(cur)
        base = RX0 if axis == "v" else RY0
        return [round(base + sum(c) / len(c)) for c in out]
    vl, hl = lines("v"), lines("h")
    print(f"grid lines: {len(vl)}V x {len(hl)}H -> cells {len(vl)-1}x{len(hl)-1}",
          "OK 9x9" if (len(vl), len(hl)) == (10, 10) else "NOT 9x9")
