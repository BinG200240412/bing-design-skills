# 提示词模板

只把当前主题真正需要的内容放入变量；不要把案例的部件数量、方向或故事永久锁进通用规范。

## 新图

```text
Use case: logo-brand.
Create ONE standalone pictogram of [SUBJECT], expressing [MEANING].
Style: flat FILLED-AREA / solid-silhouette construction, broad substantial masses and a few generous negative-space cutouts.
One uniform dark warm gray #41403D (RGB 65,64,61) on plain white.
Clean, crisp, smoothly antialiased boundaries.
Subtle hand-cut irregularity in shape: gently bent curves, slight asymmetry, small natural proportion differences.
Restrained human warmth, readable at 24–32 px.
Subject construction: [ONLY THE NECESSARY SHAPES].
One optically centered symbol on a square canvas, with clear margins.
No thin outline construction, blur, jagged edges, gradients, lighting, shadows, 3D, texture, grain, hatching, distressed printing, decorative border, extra symbols, text or watermark.
```

白底方便描摹，最终 SVG 背景透明。用户明确要透明位图时，在生图工具请求真实 alpha，不生成棋盘格图片。

## 局部修改

```text
Edit the attached pictogram.
Change ONLY [TARGET] to [REQUESTED CHANGE].
Keep [APPROVED SHAPES, POSITION, SCALE, NEGATIVE SPACES] unchanged.
Preserve flat filled-area construction, crisp boundaries, slight hand-cut irregularity and uniform #41403D on white.
Do not add other objects or introduce texture, lighting, gradients or outlines.
```

若结果带动已确认部分，且有原 SVG，可在矢量输出复用原路径并检查替换区域。翅膀、尾迹、箭头是当前任务的设计取舍，不是“增强动感”的固定配方。

## 已确认案例：圆日太阳舟

```text
A minimal Egyptian solar-barque-inspired pictogram.
One broad, shallow curved boat hull with both ends upturned at slightly different heights.
Above it, one substantial round sun disk, gently imperfect rather than compass-perfect, separated from the hull by clear white space.
Two solid masses only: boat and sun.
Compact, quiet silhouette.
No sails, mast, oars, waves, sun rays, speed trails, deity figures or decorative symbols.
Apply the common #41403D flat filled-area, crisp-edge, subtly hand-cut style.
```

这是现代设计转译。保留圆日是用户对此案例的最终选择；不意味着其他主题都用圆形或禁止动势。
