# 来源与整理边界

整理日期：2026-10-23。源文件来自本机已安装的技能目录；不是从当前官方 Figma 插件中复制出的技能合集。

| Skill | 本机来源类别 | 整理处理 |
|---|---|---|
| ui-copy-code-figma | 本机 Codex 自定义技能目录 | 原样保留入口、检查表与 UI 元数据 |
| handcut-solid-icons | 本机 Codex 自定义技能目录 | 保留规范、提示词、矢量化脚本、PNG / SVG 风格参考 |
| sudoku-image-style | 本机共享技能目录 | 保留风格核、后处理脚本和粗糙度参考；工具说明改成可迁移形式 |

Figma 的本机显示名为 `UI—COPY—CODE—FIGMA`，机器名称为 `ui-copy-code-figma`。两者来自同一目录的配置，不是两个 skill；本次未收录官方 Figma 插件中的其他技能。

「自定义目录」只描述存放方式，不证明逐字作者身份或许可。现有副本未附 LICENSE / NOTICE，安装记录也未提供这三项的可核实上游来源。因此没有新增覆盖全仓库的开源许可证。visual-design 已按维护者要求从此次上传范围排除。

## 整理前入口文件指纹

以下是本机源 `SKILL.md` 的 SHA-256，可用于后续比对；不是整理版文件的摘要。

```text
ui-copy-code-figma  79ed994d18d2da5402a254cb7d5b0428e37996c5fe87fd7179b631f586b82af9
handcut-solid-icons 89ad2ae33da390712ea30e18460eb6d0b05aa8d001f07e9b61c66c3cdb2fd683
sudoku-image-style 8b47015bff25cf0a992cedaf65eb9cf975e63993d05e614eef4169af4150c8e9
```

## 具体改动

- Figma、icon：内容未改，复制时排除系统缓存和编译缓存。
- sudoku-image-style：移除用户名、绝对工作路径、私人桌面图路径、过时的固定运行时假设及嵌套 Codex 会话调用。保留图像风格与处理参数。Python vtracer 包与 vtracer CLI 的依赖分别说明。

## 未包含

visual-design、本机官方插件、PPT 字体与提词服务、个人课程样稿、App 工程、聊天记录、Obsidian 库、开发者证书、API key 和账户配置。

## 公开前

确认各项原作者、上游来源及可再分发范围；参考图也需单独确认。确认后再保留或补充相应 LICENSE / NOTICE。代码中的依赖名称不是把依赖代码一起再许可；Pillow、vtracer、PyYAML 的许可由各自项目提供。
