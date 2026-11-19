"""Compose real, matching screenshots with only Before/After captions."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compose_pair(
    before: Path,
    after: Path,
    output: Path,
    crop: list[int] | None = None,
    width: int = 1600,
) -> dict[str, Any]:
    with Image.open(before) as first, Image.open(after) as second:
        first.load()
        second.load()
        if first.size != second.size:
            raise ValueError(
                f"Capture dimensions differ: {first.size} and {second.size}"
            )
        if first.info.get("icc_profile") != second.info.get("icc_profile"):
            raise ValueError(
                "Capture color profiles differ; recapture with the same display/profile"
            )
        profile = first.info.get("icc_profile")
        originals = [first.convert("RGB"), second.convert("RGB")]
    bounds = crop or [0, 0, originals[0].width, originals[0].height]
    if len(bounds) != 4 or not all(isinstance(value, int) for value in bounds):
        raise ValueError("crop must contain four integer pixel coordinates")
    left, top, right, bottom = bounds
    if not (
        0 <= left < right <= originals[0].width
        and 0 <= top < bottom <= originals[0].height
    ):
        raise ValueError(
            f"Crop {bounds} is outside the native image {originals[0].size}"
        )
    if width <= 0:
        raise ValueError("width must be positive")
    width = min(width, right - left)
    height = round((bottom - top) * width / (right - left))
    header, gap = 60, 18
    figure = Image.new("RGB", (width, 2 * (height + header) + gap), "#101214")
    font_path = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    font = (
        ImageFont.truetype(str(font_path), 32)
        if font_path.is_file()
        else ImageFont.load_default(size=32)
    )
    draw = ImageDraw.Draw(figure)
    for index, (capture, label) in enumerate(zip(originals, ["Before", "After"])):
        # One crop/scale is shared by both panels; captions never obscure editor pixels.
        view = capture.crop(bounds).resize((width, height), Image.Resampling.LANCZOS)
        y = index * (height + header + gap)
        figure.paste(view, (0, y + header))
        draw.text(
            (18, y + 12), label, font=font, fill="#f0b8a4" if index == 0 else "#a5e6c1"
        )
    output.mkdir(parents=True, exist_ok=True)
    png, webp = output / "comparison.png", output / "comparison.webp"
    options = {"icc_profile": profile} if profile else {}
    figure.save(png, optimize=True, **options)
    figure.save(webp, lossless=True, quality=100, method=6, exact=True, **options)
    with Image.open(png) as png_image, Image.open(webp) as webp_image:
        if png_image.convert("RGB").tobytes() != webp_image.convert("RGB").tobytes():
            raise RuntimeError("Lossless PNG/WebP verification failed")
    result = {
        "labels": ["Before", "After"],
        "source_dimensions": list(originals[0].size),
        "crop": bounds,
        "dimensions": list(figure.size),
        "original_sha256": {"before": sha256(before), "after": sha256(after)},
        "identical_pixels": originals[0].tobytes() == originals[1].tobytes(),
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in [png, webp]
        },
        "webp_lossless_pixels_verified": True,
    }
    (output / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"{output.name}: {figure.width}x{figure.height}; PNG {png.stat().st_size:,} bytes; WebP {webp.stat().st_size:,} bytes",
        flush=True,
    )
    if result["identical_pixels"]:
        print(
            f"WARNING: {output.name} has identical before/after pixels; inspect the example",
            flush=True,
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path)
    parser.add_argument("--after", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--crop", type=int, nargs=4)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    if args.plan and args.input:
        plan = json.loads(args.plan.read_text())
        manifest_path = args.input / "manifest.json"
        manifest = (
            json.loads(manifest_path.read_text())
            if manifest_path.exists()
            else {"scenes": {}}
        )
        for scene in plan["scenes"]:
            folder = args.input / scene["id"]
            comparison = compose_pair(
                folder / "before.png",
                folder / "after.png",
                folder,
                scene.get("crop"),
                scene.get("width", args.width),
            )
            manifest.setdefault("scenes", {}).setdefault(scene["id"], {})[
                "comparison"
            ] = comparison
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    elif args.before and args.after and args.output:
        compose_pair(args.before, args.after, args.output, args.crop, args.width)
    else:
        parser.error("Use --plan with --input, or --before with --after and --output")


if __name__ == "__main__":
    main()
