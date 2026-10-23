#!/usr/bin/env python3
"""Check the portable bundle and smoke-test its local image helpers.

Run with: uv run --with pillow --with vtracer --with pyyaml python verify_bundle.py
No generation, Figma, deployment, or network requests are performed by this script.
"""

import ast
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

try:
    import yaml
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit(
        "Install test dependencies: uv run --with pillow --with vtracer "
        "--with pyyaml python verify_bundle.py"
    ) from exc


ROOT = Path(__file__).resolve().parent
SKILLS = (
    "ui-copy-code-figma", "handcut-solid-icons", "sudoku-image-style"
)
SVG = "{http://www.w3.org/2000/svg}"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script, *args, ok=True):
    result = subprocess.run(
        [sys.executable, str(ROOT / script), *map(str, args)],
        capture_output=True, text=True, timeout=60,
    )
    require((result.returncode == 0) == ok, f"Unexpected status: {script}: {result.stderr}")
    return result.stdout + result.stderr


def check_structure():
    expected = set(SKILLS)
    actual = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
    require(expected == actual, "Unexpected skill inventory")
    for name in SKILLS:
        skill = ROOT / "skills" / name / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        require(match is not None, f"Missing YAML frontmatter: {name}")
        meta = yaml.safe_load(match.group(1))
        require(meta.get("name") == name, f"Name and folder differ: {name}")
        require(isinstance(meta.get("description"), str) and
                0 < len(meta["description"]) <= 1024, f"Invalid description: {name}")

    for path in ROOT.rglob("*"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        require(not path.is_symlink(), f"Symlink must not enter the bundle: {path.name}")
        if not path.is_file():
            continue
        require(path.name != ".DS_Store" and "__pycache__" not in path.parts,
                f"Cache in bundle: {path.name}")
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if path.suffix in (".yaml", ".yml"):
            yaml.safe_load(path.read_text(encoding="utf-8"))
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
                if re.match(r"[a-zA-Z]+:|#", target):
                    continue
                target = target.split("#", 1)[0]
                linked = (path.parent / target).resolve()
                require(linked.is_relative_to(ROOT) and linked.exists(),
                        f"Broken local link in {path.relative_to(ROOT)}: {target}")


def check_privacy_patterns():
    patterns = (
        re.compile(r"/(?:Users|home)/[^\s/]+/"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{24,}\b"),
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b"),
    )
    for path in ROOT.rglob("*"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        if path.is_file() and path.suffix in (".md", ".py", ".html", ".svg", ".yaml", ".yml"):
            text = path.read_text(encoding="utf-8")
            require(not any(p.search(text) for p in patterns),
                    f"Potential private path/key in {path.relative_to(ROOT)}")


def check_assets():
    assets = [
        ROOT / "skills/handcut-solid-icons/assets/solar-barque-reference.png",
        ROOT / "skills/sudoku-image-style/assets/newsprint-roughness-reference.png",
    ]
    for path in assets:
        with Image.open(path) as image:
            image.verify()
    vector = ET.parse(ROOT / "skills/handcut-solid-icons/assets/solar-barque-reference.svg")
    require(vector.getroot().tag == SVG + "svg", "Reference is not SVG")
    require(vector.getroot().get("viewBox"), "Reference SVG lacks viewBox")
    require(not list(vector.iter(SVG + "image")), "Reference SVG embeds a bitmap")


def check_image_helpers(work):
    grayscale = work / "luma.png"
    image = Image.new("L", (3, 1))
    image.putdata([0, 128, 255])
    image.save(grayscale)
    source_digest = digest(grayscale)
    alpha = work / "alpha.png"
    run("skills/sudoku-image-style/scripts/white2alpha.py", grayscale, alpha)
    with Image.open(alpha) as result:
        require(result.mode == "RGBA", "Transparency helper did not return RGBA")
        require([result.getpixel((x, 0))[3] for x in range(3)] == [255, 127, 0], "Alpha mapping changed")
    require(digest(grayscale) == source_digest, "Transparency helper changed input")

    ink_input = work / "ink.png"
    ink = Image.new("L", (128, 128), 255)
    ImageDraw.Draw(ink).rectangle((16, 16, 110, 110), fill=0)
    ink.save(ink_input)
    original_digest = digest(ink_input)
    for filename in ("texture-a.png", "texture-b.png"):
        run("skills/sudoku-image-style/scripts/ink_texture.py", ink_input, work / filename, 0.022, 50)
    require(digest(work / "texture-a.png") == digest(work / "texture-b.png"), "Texture is not reproducible")
    require(digest(ink_input) == original_digest, "Texture helper changed input")
    with Image.open(work / "texture-a.png") as result:
        require(result.size == ink.size, "Texture helper changed dimensions")
        require(sum(result.histogram()[1:255]) == 0, "Texture helper introduced grayscale")
        require(result.histogram()[0] < ink.histogram()[0], "Texture did not add dry-print flecks")

    balance = work / "balance.png"
    balanced = Image.new("L", (100, 100), 255)
    ImageDraw.Draw(balanced).rectangle((0, 0, 99, 29), fill=0)
    balanced.save(balance)
    output = run("skills/sudoku-image-style/scripts/audit_engraving.py", balance)
    measured = re.search(r"black\(<60\): ([\d.]+)%", output)
    require(measured and float(measured.group(1)) == 30, "Ink coverage does not measure actual pixels")

    grid_path = work / "grid.png"
    grid = Image.new("L", (220, 220), 255)
    draw = ImageDraw.Draw(grid)
    for coordinate in range(10, 191, 20):
        draw.line((coordinate, 10, coordinate, 190), fill=0)
        draw.line((10, coordinate, 190, coordinate), fill=0)
    grid.save(grid_path)
    output = run("skills/sudoku-image-style/scripts/audit_engraving.py", grid_path, 10, 10, 191, 191)
    measured = re.search(r"grid lines: (\d+)V x (\d+)H", output)
    require(measured and measured.groups() == ("10", "10"), "Grid audit does not detect the 9x9 fixture")

def check_vectorizer(work):
    path = work / "icon.png"
    icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle((20, 20, 108, 108), radius=12, fill=(65, 64, 61, 255))
    draw.ellipse((48, 48, 80, 80), fill=(255, 255, 255, 255))
    icon.save(path)
    input_digest = digest(path)
    output = work / "icon.svg"
    run("skills/handcut-solid-icons/scripts/vectorize_icon.py", path, output)
    root = ET.parse(output).getroot()
    require(root.get("viewBox") == "0 0 128 128", "Vectorizer changed canvas")
    paths = list(root.iter(SVG + "path"))
    require(paths and {p.get("fill") for p in paths} == {"#41403D"}, "Vector ink differs")
    require(not list(root.iter(SVG + "image")) and not list(root.iter(SVG + "rect")),
            "Vector output contains bitmap/background rectangle")
    output_digest = digest(output)
    run("skills/handcut-solid-icons/scripts/vectorize_icon.py", path, output, ok=False)
    require(digest(output) == output_digest and digest(path) == input_digest,
            "Overwrite protection or source preservation failed")


def main():
    check_structure()
    check_privacy_patterns()
    check_assets()
    with tempfile.TemporaryDirectory(prefix="design-skills-test-") as directory:
        work = Path(directory)
        check_image_helpers(work)
        check_vectorizer(work)
    print("PASS: 3 skills; metadata, links, syntax, asset integrity and private-path/key patterns checked")
    print("PASS: alpha mapping, texture, ink coverage, 9x9 grid, vectorization and overwrite protection")
    print("Not tested: Figma, image generation, macOS Quick Look preview, simulator/device delivery")
    print("Licensing/provenance still requires maintainer confirmation before public redistribution")


if __name__ == "__main__":
    main()
