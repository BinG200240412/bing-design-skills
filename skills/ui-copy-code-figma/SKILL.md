---
name: ui-copy-code-figma
description: Reproduce a Figma mobile frame in an existing SwiftUI iOS app with group-aware pixel measurement, original asset export before coding, exact typography, preserved app behavior, and simulator screenshot verification. Use when the user provides a Figma node URL and asks for 1:1 replication, pixel measurement, design-to-code implementation, or says to use the same Figma replication method as before.
---

# Figma Pixel-Perfect SwiftUI

Translate a fixed mobile Figma frame into working SwiftUI. Treat the Figma screenshot as the visual reference, never as the implementation asset.

## Workflow

1. Load the installed `figma-design-to-code` and `figma-swiftui` skills before requesting design context.
2. Parse the file URL and node ID. Call `get_design_context` for the frame first, then inspect its Frame, Group, Component, and Instance hierarchy. Request child context only when the parent response lacks the information needed to implement it.
3. Call `get_screenshot` for the full frame. Save it as the visual reference used during verification.
4. Build a group-aware measurement map. Treat each meaningful top-level Group/Frame/Component/Instance as one layout unit and record its bounds, rotation, opacity, and position relative to its parent. Preserve its internal relative geometry. Do not measure or recalibrate every child independently when the group already defines that composition.
5. Split nodes into two classes before coding:
   - Artwork groups: illustrations, stamps, ornaments, poster compositions, textured lettering, or other visually fixed groups. Export the whole group as one original SVG or raster asset.
   - Live UI groups: text, timers, records, controls, buttons, accessibility targets, and dynamic state. Implement the group as a native container and position only its meaningful direct children relative to that group.
6. Create an asset inventory containing each original node ID, export format, asset name, and destination. Export every original Figma asset into `Assets.xcassets` before writing SwiftUI. Keep vector artwork as SVG and verify that each exported file opens and remains sharp. Do not begin visual implementation while required exports are still missing; report the exact missing node instead.
7. Inspect the existing app. Find the destination route, existing view, typography helpers, data models, and assets. Preserve working navigation and interactions.
8. Separate artwork from live content. Never recreate the internals of an exported artwork group with hand-positioned SwiftUI children. Never substitute screenshots, hand-redrawn symbols, SF Symbols, or AI-generated approximations when an original asset exists.
9. Implement the screen in the project's existing style. Place groups by their measured parent-relative bounds. For a fixed phone artwork canvas, use a known design size, `.topLeading` coordinates, and a uniform scale to fit the device. Keep tappable hit areas functional even when their visible labels are precisely positioned.
10. Match typography, colors, opacity, borders, and group transforms from Figma. Use Figma's raw pixels as iOS points only when the frame is designed at a 1x phone canvas. If the project has a user-approved global ink rule, such as black at 80% opacity, apply it consistently unless the node explicitly overrides it.
11. Build with the repository's required DerivedData location. Launch the screen directly with existing debug arguments when possible, then capture a simulator screenshot.
12. Compare the simulator screenshot against the Figma reference. Correct parent group placement first, then direct-child layout, and only then genuine internal discrepancies. Check every item in [references/verification-checklist.md](references/verification-checklist.md) and repeat until no meaningful mismatch remains.

## Guardrails

- Never flatten an interactive screen into one image.
- Never use a Figma screenshot as an app asset.
- Never guess spacing when node metadata is available.
- Never break an artwork group into individually calibrated children when the original group can be exported intact.
- Never start coding before the original-asset inventory has been exported and checked.
- Do not add new dependencies when the codebase already supports the design.
- Do not overwrite unrelated dirty-worktree changes.
- Do not install on a physical device unless the user requests it.
- If an original Figma asset cannot be exported, state exactly which node or asset is missing before substituting anything.

## Fixed-Canvas SwiftUI Pattern

Use this only for intentionally fixed mobile artwork whose source frame has a known point size:

```swift
GeometryReader { proxy in
    let design = CGSize(width: 420, height: 912)
    let scale = min(proxy.size.width / design.width, proxy.size.height / design.height)

    canvas
        .frame(width: design.width, height: design.height)
        .scaleEffect(scale, anchor: .topLeading)
        .frame(width: proxy.size.width, height: proxy.size.height, alignment: .topLeading)
        .offset(
            x: (proxy.size.width - design.width * scale) / 2,
            y: (proxy.size.height - design.height * scale) / 2
        )
}
.ignoresSafeArea()
```

For adaptable application layouts, prefer stacks and constraints while preserving measured gaps and dimensions.

## Deliverable

Finish with the implemented file paths, imported original assets, build result, simulator screenshot path, and any remaining measurable discrepancy. Keep the report short.
