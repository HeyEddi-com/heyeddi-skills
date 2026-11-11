#!/usr/bin/env python3
"""Screenshot geometry gate. Compares marks to the local background. No model.

Hard errors (--check exits 1):
  text_wall        almost no marks, and the background is one flat color
  low_contrast     marks exist and almost none of them reach 4.5:1
  clipped_content  type is cut off the top or bottom edge

A gradient with no type is not a text wall. Icons may lower the median
contrast. The page fails only when readable type is missing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

MAX_W = 480
CELL = 24
MARK = 1.35
FLOOR = 3.0
READABLE = 4.5


def _channel(c: float) -> float:
    x = c / 255.0
    return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4


def _lum(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def _ratio(a: float, b: float) -> float:
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def _load(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if image.width > MAX_W:
        scale = MAX_W / image.width
        image = image.resize((MAX_W, max(1, int(image.height * scale))), Image.Resampling.BOX)
    return image


def _background(image: Image.Image) -> list[list[tuple[int, int, int]]]:
    """Cell median color. Thin type does not move the median. A gradient does."""
    width, height = image.size
    pixels = image.load()
    cols = max(1, (width + CELL - 1) // CELL)
    rows = max(1, (height + CELL - 1) // CELL)
    grid: list[list[tuple[int, int, int]]] = []
    for row in range(rows):
        line = []
        for col in range(cols):
            samples = []
            for y in range(row * CELL, min(height, (row + 1) * CELL), 3):
                for x in range(col * CELL, min(width, (col + 1) * CELL), 3):
                    samples.append(pixels[x, y])
            samples.sort(key=_lum)
            line.append(samples[len(samples) // 2])
        grid.append(line)
    return grid


def _edge_vary(pixels, width: int, rows: range) -> float:
    values = [_lum(pixels[x, y]) for y in rows for x in range(0, width, 2)]
    if len(values) < 8:
        return 0.0
    mean = sum(values) / len(values)
    return (sum((value - mean) ** 2 for value in values) / len(values)) ** 0.5


def audit_image(path: Path) -> dict:
    image = _load(path)
    width, height = image.size
    pixels = image.load()
    bg = _background(image)
    mark_at = [[False] * width for _ in range(height)]
    pair_at = [[0.0] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            cell = bg[min(y // CELL, len(bg) - 1)][min(x // CELL, len(bg[0]) - 1)]
            pair = _ratio(_lum(pixels[x, y]), _lum(cell))
            pair_at[y][x] = pair
            mark_at[y][x] = pair >= MARK

    mark_ratios: list[float] = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if not mark_at[y][x]:
                continue
            neighbors = (
                mark_at[y][x - 1] + mark_at[y][x + 1] + mark_at[y - 1][x] + mark_at[y + 1][x]
            )
            if neighbors < 2:
                continue
            mark_ratios.append(pair_at[y][x])

    cell_lums = [_lum(color) for row in bg for color in row]
    bg_mean = sum(cell_lums) / len(cell_lums)
    bg_vary = (sum((value - bg_mean) ** 2 for value in cell_lums) / len(cell_lums)) ** 0.5
    marks = len(mark_ratios)
    fraction = marks / (width * height)
    ordered = sorted(mark_ratios)
    median = ordered[marks // 2] if marks else 0.0
    readable = sum(1 for value in mark_ratios if value >= READABLE) / marks if marks else 0.0

    errors: list[dict[str, str]] = []
    if fraction < 0.004 and bg_vary < 0.04:
        errors.append({"code": "text_wall", "detail": f"marks {fraction:.4f} bg_vary {bg_vary:.3f}"})
    if marks >= 200 and readable < 0.04 and median < FLOOR:
        errors.append(
            {"code": "low_contrast", "detail": f"readable {readable:.3f} median {median:.2f}"}
        )

    if fraction < 0.25:
        top_vary = _edge_vary(pixels, width, range(3))
        bot_vary = _edge_vary(pixels, width, range(height - 3, height))
        if top_vary >= 0.25 and bot_vary < 0.12:
            errors.append({"code": "clipped_content", "detail": f"top vary {top_vary:.2f}"})
        elif bot_vary >= 0.25 and top_vary < 0.12:
            errors.append({"code": "clipped_content", "detail": f"bottom vary {bot_vary:.2f}"})

    return {
        "ok": not errors,
        "image": str(path),
        "size": [width, height],
        "mark_fraction": round(fraction, 4),
        "median_ratio": round(median, 2),
        "readable": round(readable, 3),
        "errors": errors,
    }


def gate_captures(paths: list[Path]) -> dict:
    """Run the gate on captured PNGs. ok is false when any image has a hard error."""
    reports = [audit_image(path) for path in paths]
    return {"ok": all(report["ok"] for report in reports), "reports": reports}


def main() -> int:
    parser = argparse.ArgumentParser(description="Screenshot geometry gate")
    parser.add_argument("--image", required=True, help="PNG or JPEG of one screen")
    parser.add_argument("--check", action="store_true", help="Exit 1 when errors is non-empty")
    args = parser.parse_args()
    path = Path(args.image)
    if not path.is_file():
        print(json.dumps({"ok": False, "errors": [{"code": "missing_image", "detail": str(path)}]}))
        return 1
    report = audit_image(path)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if args.check and not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
