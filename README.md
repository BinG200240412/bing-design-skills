# BinG Design Skills

从数独 / Arright 的设计与开发流程中整理出的三个 skill，涵盖 Figma 版面校正和两种不同的插图语言。每个目录可以单独使用，不需要安装整套；不包含 visual-design。

| Skill | 用途 | 适合什么时候用 |
|---|---|---|
| [UI—COPY—CODE—FIGMA](skills/ui-copy-code-figma/SKILL.md) | Figma → SwiftUI 像素级还原与校正 | 分组测量、原始资产导出、字体与间距校对、模拟器截图比对 |
| [handcut-solid-icons](skills/handcut-solid-icons/SKILL.md) | 灰色手绘面型 icon / logo | `#41403D`、实心色块、轻微歪扭、真实 SVG 交付 |
| [sudoku-image-style](skills/sudoku-image-style/SKILL.md) | 粗糙老报纸铜版画管线 | 人物、海报插图、缺墨肌理、去底、矢量化与数独格线检查 |

Figma 校正负责「忠实还原」。面型 icon 与老报纸版画是两套语言，不自动混用。

### Figma 的大写名称

`UI—COPY—CODE—FIGMA` 是本机原有的显示名，保存在 `agents/openai.yaml`。对应的目录名和调用名是 `ui-copy-code-figma`，两者是同一个 skill，不是另外一份。保留小写机器名称，避免破坏技能发现和调用。

## 目录与安装

每个 `skills/<名称>/` 都以 `SKILL.md` 为入口，相关脚本、参考与资产放在同一目录。

将需要的单个目录复制到所用工具的技能目录。例如本地 Codex 的 `~/.codex/skills/`，或 Claude Code 的 `~/.claude/skills/`。不要覆盖已有同名版本；先比对或另行备份。安装方式仍以目标工具的支持范围为准。

调用示例：

```text
用 $ui-copy-code-figma 校对这个 Figma 节点和现有 SwiftUI 页面，先检查分组和原始资产。
用 $handcut-solid-icons 做一枚园艺工具图标，交付 SVG 和预览。
用 $sudoku-image-style 把这张参考图做成老报纸版画，先保留原构图。
```

## 工具依赖与验证

- Figma skill 需要有权限的 Figma 工具；SwiftUI 的构建与模拟器验证需要 macOS / Xcode。宿主要求先加载的 Figma 技能仍须遵守，本包不转发官方插件。
- 图像生成需要当前环境可用且获准使用的图像工具；本仓库不包含 API key。
- Python 脚本使用 Pillow，icon 描摹另需 Python 包 vtracer。检查包结构还需要 PyYAML。
- icon 的 `--preview` 使用 macOS Quick Look；其他平台可仅导出 SVG。版画文档中的 vtracer CLI 需另行安装。

在仓库根目录运行：

```bash
uv run --with pillow --with vtracer --with pyyaml python verify_bundle.py
```

这会检查三个 skill 的元数据、本地引用、隐私路径、Python 语法，并实际运行图片脚本的轻量测试。不调用生图、Figma 或真机安装；不代表这些外部能力已经端到端验证。

## 这个整理版改了什么

- 保留三个独立 skill，未修改本机安装版本。
- 去掉固定用户名路径、私人记忆依赖和「必须另开 Codex 生成图」的旧说明。
- 按维护者要求排除 visual-design；PPT 引擎、提词服务、字体、课堂示例均未收录。
- 不包含 App 源码、会话、密钥、签名或 Obsidian 文档。

## 来源与公开发布

详见 [PROVENANCE.md](PROVENANCE.md)。现有本机副本没有附带可核实的统一开源许可，本次不代填 MIT，也不声称三个 skill 的每段文字均由维护者手写。两份风格参考图及 SVG 随包保留用于对齐；公开发布前需由维护者确认 skill 与参考素材的来源和再分发权利。GitHub 备份默认使用私有仓库。

本仓库只保存这三个技能及相应说明、校验工具，不包含个人聊天历史或本机配置。
