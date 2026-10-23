#!/usr/bin/env python3
"""White background -> transparency via luminance-to-alpha mapping.
Keeps hairline strokes (no hard threshold). Usage: white2alpha.py <in> <out>"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
img = Image.open(src).convert("L")
# alpha = 255 - luminance (white->0 transparent, black->255 opaque)
alpha = img.point(lambda v: 255 - v)
out = Image.new("RGBA", img.size, (0, 0, 0, 0))
out.putalpha(alpha)
# RGB channels: solid black (alpha carries the ink density)
out.save(dst)
print("saved", dst)
