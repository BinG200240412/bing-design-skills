# Pixel-Perfect Verification Checklist

Compare the Figma reference and simulator screenshot at the same canvas size.

- Frame: canvas size, safe-area treatment, crop, and centering match.
- Background: exact source asset, crop offset, scale, and color match.
- Group geometry: every meaningful group matches its parent-relative `x`, `y`, `width`, `height`, rotation, and opacity.
- Group integrity: exported artwork groups preserve their original internal composition; do not judge or reposition their children one by one.
- Live-group geometry: only meaningful direct children of dynamic UI groups are measured relative to the group container.
- Typography: family, weight, size, line height, alignment, and wrapping match.
- Rules and borders: thickness, inset behavior, opacity, and corner radius match.
- Artwork: every item in the asset inventory uses its original exported vector/raster file and remains sharp.
- Layering: overlaps, clipping, and z-order match the Figma screenshot.
- Dynamic content: live values remain readable without resizing the surrounding layout.
- Interaction: all buttons, gestures, navigation, and accessibility labels still work.
- Device QA: no blank regions, clipping, overlap, or text overflow on the target simulator.

If the screen is dynamic, verify both a reference-like seeded state and an empty or edge state.
