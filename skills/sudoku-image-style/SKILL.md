---
name: sudoku-image-style
description: 数独 App 的粗糙老报纸影刷版画出图管线——把参考图/照片转成高对比钞票纹铜版画经旧报纸压印后的效果（banknote intaglio + rough newsprint letterpress, two-tone），默认保留缺墨、飞白、毛边和轻微糊版，全画面黑白目标约 3:7。含生图提示词、机器审核（格线/两色纯度/黑白占比/文字残留）、文字拓印、真实数独数字烧入、去底和 vtracer 描摹。当用户提到"生成配图""老报纸/影刷/版画/钢笔画/铜版画""描摹成矢量""批量生图""数独风格的图"，或给图要"按工作流处理"时，必须使用。
---

# 数独版画出图管线（sudoku-image-style）

把任意参考图变成 App 统一语言：**19 世纪钞票凹版/铜版雕刻的造型，经 20 世纪中叶老报纸粗糙影刷；黑白两色、高对比、黑白约 3:7**，最后以矢量 SVG 进 App 资产。整条管线 = **提示词转绘 → 机器审核（不合格自动重试）→ 后期修补 → 去底 → 描摹 → 入库验证**。

管线里的每一步都有"为什么"，照做之前先理解，遇到变体知道怎么权衡。

## 工具

- **图像生成工具**（图转图/文生图）：使用当前环境已授权的内置工具，遵守其附图与透明背景要求。将结果保存到本次任务指定目录；不依赖某台机器的路径，也不为生图另开代理会话。
- **vtracer**（描摹 SVG）：需另行安装。下文命令使用 vtracer CLI；先用本机 `vtracer --help` 核对支持的选项。Python 包和命令行程序并不等价，不能因安装了 Python 包就假定已有同名 CLI。
- **Python + Pillow**：三个随包脚本依赖 Pillow。可用虚拟环境或 `uv run --with pillow python scripts/<脚本名>.py ...`，不假定系统 Python 已装依赖。
- **默认粗糙度基准**：`assets/newsprint-roughness-reference.png`（来自用户满意的 ShareEndgameScene）。它是印刷触感参考，不是构图或人物参考；需要时与内容图双图输入。

## 提示词模板（风格核，锁死）

```
19th-century banknote intaglio engraving and copperplate modeling,
reproduced through a rough mid-century newspaper letterpress process.
TWO-TONE image: solid black ink vs clean white paper ONLY.
TARGET THE WHOLE COMPOSITION AT APPROXIMATELY 30% BLACK INK AND 70% WHITE PAPER.
Build the image around a few broad solid black masses in hair, clothing,
cast shadows and dark props; do not let the result become pale or airy.
Solid blacks must show authentic newsprint wear: uneven ink density,
slightly rough and broken edges, small white dry-print flecks and occasional
tiny paper-fiber voids. Avoid perfectly uniform digital black.
Highlights and skin = pure white paper, left completely blank.
Mid-tones reduced to the absolute minimum — sparse fine hatching ONLY
where a form cannot be read otherwise; when in doubt, leave white.
Lines follow the form and volume of objects, never random direction.
STRICTLY NO grayscale washes, NO pencil smudging, NO halftone dots,
NO airbrush gradients, NO color, NO gray fills.
Maximum contrast. Prefer bold, slightly broken engraved strokes; use delicate
hairlines only where they will remain readable after reduction.
Pure white paper background (#FFFFFF).
```

**每句的用意**（改模板前先读懂）：
- `intaglio / copperplate` 是钞票纹路的命门词；写 "pen drawing" 会出素描。
- `TWO-TONE` + `when in doubt, leave white`：AI 默认爱给灰调，灰调是描摹断线和"发脏"的元凶，必须在提示词里掐死，不靠后期救。
- `lines follow the form`：治排线方向乱飞（排线不塑形 = 假铜版）。
- `30% BLACK / 70% WHITE`：防止生成图过白、只剩细线。黑量要从头发、衣物、投影和道具的完整黑块来，不能靠压黑脸和皮肤凑数。
- `rough newspaper letterpress`：粗糙、缺墨、飞白和轻微糊版是默认风格核心，不是需要清理的瑕疵。
- `pure white background (#FFFFFF)`：给后期"白底→透明"铺路，去底变成一行脚本的机械操作。
- `NO halftone dots`：防它用印刷网点偷懒做灰。

**任务行**（拼在风格核后面，按图定制）：

```
Convert the attached image into this engraving style, preserving the exact
composition, poses and objects: <逐一列出画面主体>.
- 装饰性小盘面（卡片、手持物）: "sudoku cards MUST keep their printed
  numerals, drawn naturally in perspective as part of the artwork."
- 正式大盘面: "the large sudoku grid must have EXACTLY 9 columns and
  9 rows, complete clean grid lines, ALL cells EMPTY."
- 海报文案区: "the text-block area should become clean empty paper
  with at most a thin engraved decorative border line."
```

**默认：老报纸影刷肌理**（风格核已内置，每张都要有；原稿黑块仍像数码填充时，后期再补）：

```
Preserve authentic LETTERPRESS print texture: uneven ink density, rough
ink edges, dry-print flecks and slight loss of tiny details. The result
should feel physically printed on cheap newspaper, not digitally distressed.
```

**变体：朴素墨印风**（用户嫌"太精致、不像老报纸印刷"时）：双图输入——内容参考图 +
风格参考图（由用户为当前任务提供，不读取私人桌面目录），提示词核心：few bold lines, large
solid shapes, generous white space（simplicity itself is the detail）、黑色形状 RESTRAINED
roundedness（墨印肉感但不卡通）、小密线 FORBIDDEN（60 年代报纸印不出来）。这种图块面大，
vtracer 不用放大、直接 `-f 2` 原尺寸描。

## 铁律（都是踩坑踩出来的）

1. **AI 写字必错**（英文错拼、中文鬼画符、数独盘数字无效）。所以：
   - **文案/标题**：提示词让 AI 把文字区留成净纸，后期从原图**拓印贴回**——按亮度阈值（lum < 130）抠出原图文字层转黑，贴到版画的同一位置。字形 100% 保真。
   - **正式数独盘的数字**：要求 AI 留空盘，后期用代码烧真实谜题（字体用项目里的 EBGaramond-VF.ttf 或系统 Bodoni 72 Bold，按画面年代选）。
   - **例外**：小卡片/手持物上的装饰性数字，让 AI 原生画（`keep their printed numerals`）——透视自然不飘。代价是不保证有效数独，这是说好的取舍，不要再后期贴（贴必飘）。
2. **AI 数不对格子**。说"正好 9×9"也会画成 9×8、7×9。它自己汇报"是 9×9"也不算数——**必须脚本数线验收**，不合格带具体反馈打回（"currently has 7 columns, must be exactly 9"），最多重试 3 次。
3. **提示词一次到位，审核机制兜底**。能写进提示词的（风格、白底、空盘、肌理）都前置；AI 原理上做不到的（透明通道、必对的数字、数格子）留给脚本。
4. **全画面黑白比例目标 = 3:7**。原始生成图以亮度 `<60` 作为实黑墨像素，黑占比 `27%–33%` 才 PASS；抗锯齿暗灰不计入实墨。低于 27% 是过白：带具体比例反馈重生，要求在头发/衣物/深阴影/道具增加整块黑；不许全局阈值压暗，不许填黑面部排线。高于 33% 才做抽稀与飞白。

## 流水线

### 1. 转绘
当前图像工具 + 风格核 + 任务行。大图（海报）一张一次；批量时逐张跑。
提示词末尾加一句 "Save the raw generated PNG into the requested output directory AS-IS — do NOT apply any
thresholding or post-processing."——codex 会"好心"自己做硬阈值后处理，218 一刀切下去排线全变噪点，必须提前禁止；两色纯度靠审核把关，不靠硬二值。

### 2. 审核（scripts/audit_engraving.py）
```
python3 scripts/audit_engraving.py <图> [gx0 gy0 gx1 gy1]
```
- **两色纯度**：中间灰（60-200）占比 < 18% 才 PASS（纯 AA 边缘而已）。
- **黑白平衡**：全画面亮度 `<60` 的实黑墨像素目标 `30%`，`27%–33%` 为 PASS。这项在统一成 `#41403D` 之前的原始黑白稿上审核，与两色纯度里的 `black(<60)` 同口径。
- **格线计数**：给了区域就数横竖线，必须 10+10 条。注意**审核区域要画准**——画窄了会漏数，画宽了会把装饰框线算进来；先用裁图确认盘面边界再数。
- **文字残留**：肉眼检查（让 AI 留白的区域有没有长出鬼画符）。
- 任一不合格 → 带具体反馈重新转绘，≤3 次。

### 3. 后期修补（按需要）
- **统一墨色（必做，标准锁死）**：墨色不靠 AI 生成时调，一律后期统一。生成图保持纯黑，后期把黑提升到 **#41403D**（深墨发灰，60 年代油墨没有纯黑；用户定的标准值，改要问过他）：定稿按通道做黑点提升（0→65/64/61，白不变）；透明底先跑 white2alpha 再把 RGB 统一染 #41403D 保留 alpha；SVG 描完 `sed 's/#000000/#41403D/g'`。App 内渲染：`P.ink`（文字）和 `P.inkPrint`（插图）目前都等于 #41403D，改色两边一起改。
- **老报纸墨晕纹理（默认审核，不足时必做，在统一墨色之前）**：先和 `assets/newsprint-roughness-reference.png` 比较。若黑块过于均匀、边缘过于数码化，跑 `python3 scripts/ink_texture.py <in.png> <out.png> [基础率=0.022] [白团数=1800]`：背景归白 → 14px 网格区域密度起伏（0.4–1.6）→ 黑块内按比例飞白 → 撒 1–2px 干笔白团。力度参考：人物场景 0.028/2600，字标邮票 0.022/1800（字母边缘要干净）。原稿已有足够缺墨时不叠加，防止变成人工噪点。纹理处理后必须重跑 `audit_engraving.py`；若实黑占比跌破 27%，应降低飞白力度，不得再用全局压暗补回。描摹时放大 2x + `-f 2`，碎点才能以矢量存活。面部细排线区别下手。
- **文字拓印贴回**：原图文字区阈值抠层 → 黑字 → 贴回（位置/缩放按版面实测）。
- **烧真实数字**：先探测格线（投影找峰；细线太淡就拟合等距点阵），逐格烧给定数；**被遮挡的格自动跳过**（格心区域暗像素 >3% 即跳过）；纸面有质感时擦除用"格角中位色 + 高斯噪点"，不要平涂。倾斜的卡片盘：读 4 角点 → 单应变换（PIL `Image.transform(PERSPECTIVE)`），数字层在小尺寸 canonical 画布上画（900→实际只有 ~2x 缩放），笔画才不会被缩没。
- **墨量中间值**（图太脏/太重时）：不要全局填白点（会糊脸）。做法 = 黑笔画**整条随机抽稀**（连通组件 <400px 的按 ~28% 删除，排线变疏但不断线）+ 深陷死黑核内的白飞白填回一半（局部均值 <60 才动）。面部排线区绝不许填黑。

### 4. 去底（scripts/white2alpha.py）
```
python3 scripts/white2alpha.py <in.png> <out.png>
```
亮度→alpha 映射（白=全透明、黑=不透明），**不做硬二值**——发丝笔触全保住，App 里纸纹直接透出来。

### 5. 描摹（vtracer）
**输入用白底定稿，不要用透明底**——vtracer 不读 alpha，透明区 RGB 是黑，整幅会描成一块黑板。
```
vtracer --preset bw --colormode bw -m spline -f 6 \
  --corner-threshold 60 --segment-length 4.5 --splice-threshold 45 \
  --path-precision 2 --optimize 2 <定稿.png> <out.svg>
```
三个坑：
- **细线太淡被丢**：不要全局加深（大黑块会糊），用"局部加深"——只在盘面/文字区域做 `v<235 → v-90` 的曲线，人物保持原灰度，再描。
- **小尺寸文字/数字被 speckle filter 吃掉**（`-f 6` 丢小碎块）：整图放大 2-3 倍再描，或 `-f 2`。描完坐标跟着放大没关系，SVG 本来就能缩。
- **描完一定要渲染回来验收**（`qlmanage -t -s 900 -o /tmp out.svg`），重点看：排线是否连续、小字是否存活、密集区有没有糊成黑块。

### 6. 入库验证
- 资产：`Assets.xcassets/<名>.imageset/`，SVG 的 Contents.json 必须带 `"preserves-vector-representation": true`。
- 渲染：`.renderingMode(.template)` + `foregroundStyle(P.ink)`——印在纸上的效果，主题色统一换。
- 编译 → 模拟器截图 → 放大验证细节（数字对位、透明区域透纸、字标笔画）。

## 产物命名惯例

- `<名>-定稿.png`（白底位图）、`<名>-透明底.png`、`<名>-矢量.svg`，存用户指定文件夹；
- App 资产另起名字（如 `ShareEndgameScene`），与用户素材文件夹分离。
