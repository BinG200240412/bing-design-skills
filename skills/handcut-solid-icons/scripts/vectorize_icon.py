#!/usr/bin/env python3
"""Trace a flat icon into a single-color SVG; optionally render a macOS preview."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"


def export_icon(source, output, color="#41403D", preview=False, preview_size=1254, force=False):
    try:
        from PIL import Image
        import vtracer
    except ImportError as exc:
        raise RuntimeError(
            "Missing Pillow or vtracer. Run with: uv run --with pillow --with vtracer python "
            + str(Path(__file__).resolve())
            + " INPUT.png OUTPUT.svg --preview"
        ) from exc

    source = Path(source).expanduser().resolve()
    output = Path(output).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"Input not found: {source}")
    if source.suffix.lower() == ".svg":
        raise ValueError("Input is already SVG; edit/copy its vector paths directly.")
    if output.suffix.lower() != ".svg":
        raise ValueError("Output extension must be .svg")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
        raise ValueError("Color must have six hex digits, e.g. #41403D")
    color = color.upper()
    if not 24 <= preview_size <= 4096:
        raise ValueError("Preview size must be between 24 and 4096")

    preview_path = output.with_name(output.stem + "-preview.png")
    targets = [output] + ([preview_path] if preview else [])
    for target in targets:
        if target == source:
            raise ValueError("Output would replace the source image")
        if target.exists() and not force:
            raise FileExistsError(f"Output exists; use a new filename: {target}")
    renderer = shutil.which("qlmanage") if preview else None
    if preview and not renderer:
        raise RuntimeError("--preview needs macOS qlmanage; export SVG without this flag elsewhere.")

    with Image.open(source) as original:
        rgba = original.convert("RGBA")
    width, height = rgba.size
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flattened = Image.alpha_composite(white, rgba).convert("RGB")
    histogram = flattened.convert("L").histogram()
    dark = sum(histogram[:128])
    total = width * height
    if dark == 0:
        raise ValueError("No dark foreground found on the light background.")
    if dark / total > 0.95:
        raise ValueError("Nearly all pixels are dark; check background/inversion before tracing.")

    with tempfile.TemporaryDirectory(prefix="handcut-icon-") as scratch:
        scratch = Path(scratch)
        normalized = scratch / "input-white.png"
        raw_svg = scratch / "traced.svg"
        flattened.save(normalized)
        vtracer.convert_image_to_svg_py(
            str(normalized), str(raw_svg),
            colormode="binary", mode="spline", filter_speckle=8,
            corner_threshold=60, length_threshold=4.0,
            max_iterations=10, splice_threshold=45, path_precision=3,
        )
        tree = ET.parse(raw_svg)
        root = tree.getroot()
        root.set("width", str(width))
        root.set("height", str(height))
        root.set("viewBox", f"0 0 {width} {height}")
        paths = list(root.iter(f"{{{SVG_NS}}}path"))
        if not paths:
            raise ValueError("Tracing produced no paths.")
        for path in paths:
            path.set("fill", color)
            if path.get("stroke") not in (None, "none"):
                raise ValueError("Unexpected stroked path in filled-area export.")
        if list(root.iter(f"{{{SVG_NS}}}image")):
            raise ValueError("SVG contains an embedded bitmap.")
        if list(root.iter(f"{{{SVG_NS}}}rect")):
            raise ValueError("Unexpected background rectangle in traced SVG.")

        ET.register_namespace("", SVG_NS)
        clean_svg = scratch / output.name
        tree.write(clean_svg, encoding="utf-8", xml_declaration=True)

        rendered = None
        if preview:
            # Quick Look can return a document icon for a small natural SVG size.
            # Render a temporary large viewport, keeping the original viewBox,
            # then downsample the preview without changing delivered geometry.
            render_edge = max(1024, preview_size)
            scale = render_edge / max(width, height)
            render_root = ET.fromstring(ET.tostring(root))
            render_root.set("width", str(round(width * scale)))
            render_root.set("height", str(round(height * scale)))
            render_svg = scratch / "large-preview-source.svg"
            ET.ElementTree(render_root).write(
                render_svg, encoding="utf-8", xml_declaration=True
            )
            result = subprocess.run(
                [renderer, "-t", "-s", str(render_edge), "-o", str(scratch), str(render_svg)],
                capture_output=True, text=True,
            )
            large_preview = scratch / (render_svg.name + ".png")
            if result.returncode or not large_preview.is_file():
                raise RuntimeError("Quick Look preview failed: " + result.stderr.strip())
            rendered = scratch / "preview.png"
            with Image.open(large_preview) as image:
                image = image.convert("RGBA")
                image.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
                image.save(rendered)

        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(clean_svg, output)
        if rendered:
            shutil.copyfile(rendered, preview_path)

    return {
        "svg": str(output),
        "preview": str(preview_path) if preview else None,
        "viewBox": f"0 0 {width} {height}",
        "paths": len(paths),
        "fill": color,
        "embedded_bitmap": False,
        "background": "transparent",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--color", default="#41403D")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--preview-size", type=int, default=1254)
    parser.add_argument("--force", action="store_true", help="Replace named outputs when authorized")
    args = parser.parse_args()
    try:
        result = export_icon(
            args.input, args.output, args.color, args.preview, args.preview_size, args.force
        )
    except (ValueError, FileExistsError, RuntimeError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
