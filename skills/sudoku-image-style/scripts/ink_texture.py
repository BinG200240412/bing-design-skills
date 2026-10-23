#!/usr/bin/env python3
"""墨晕纹理：给两色版画的黑块内部加"着墨不均"——老报纸凸版印刷的漏白感。

做法（教程页/新一局邮票/成就邮票/icon3 同款配方）：
1. 背景归白（>200 → 255），黑保持黑。
2. 14px 粗网格，每格一个 0.4–1.6 的着墨系数 → 晕染有"这一块那一块"的区域分布。
3. 黑像素（<100）按 基础率 × 区域系数 随机飞白。
4. 再撒少量 1–2px 干笔白团，让纹理有粗有细。

注意：面部细排线区慎用（飞白进脸会花）；字母/数字边缘密集处把基础率调低。

用法:
    python3 ink_texture.py <in.png> <out.png> [基础率=0.022] [白团数=1800]

产出供后续：定稿黑点提升、white2alpha 去底、vtracer 描摹（放大 2x + -f 2 保碎点）。
"""
import random
import sys
from PIL import Image, ImageDraw


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    rate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.022
    blobs = int(sys.argv[4]) if len(sys.argv) > 4 else 1800

    random.seed(42)
    im = Image.open(src).convert("L")
    w, h = im.size
    px = im.load()

    for y in range(h):
        for x in range(w):
            if px[x, y] > 200:
                px[x, y] = 255

    cell = 14
    density = [[random.uniform(0.4, 1.6) for _ in range(w // cell + 2)]
               for _ in range(h // cell + 2)]
    for y in range(h):
        cy = y // cell
        row = density[cy]
        for x in range(w):
            if px[x, y] < 100 and random.random() < rate * row[x // cell]:
                px[x, y] = 255

    d = ImageDraw.Draw(im)
    for _ in range(blobs):
        x, y = random.randrange(w), random.randrange(h)
        if px[x, y] < 100:
            r = random.uniform(1.0, 2.0)
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)

    im.save(dst)
    print("saved", dst, im.size)


if __name__ == "__main__":
    main()
