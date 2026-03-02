#!/usr/bin/env python3
"""Generate localized portfolio images for Streamflow via OpenAI Image edits.

This script translates text inside existing image assets while preserving the
overall visual composition. It supports resume mode and retries.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_GEN = Path.home() / ".codex" / "skills" / "imagegen" / "scripts" / "image_gen.py"
TMP_DIR = ROOT / "tmp" / "portfolio_localize"

# The image edit API currently returns 3:2 variants; we pad before editing,
# then crop back to the original aspect ratio afterwards.
API_RATIO = 3 / 2


@dataclass(frozen=True)
class SourceSpec:
    source: Path
    target_root: Path
    text_box: tuple[int, int, int, int] | None = None


TARGET_LANGS = {
    "en": "English",
    "pt": "Brazilian Portuguese",
    "es": "Latin American Spanish",
}


def source_specs() -> list[SourceSpec]:
    specs: list[SourceSpec] = []
    portfolio_text_boxes: dict[str, tuple[int, int, int, int]] = {
        # (left, top, right, bottom) - text zones only to avoid moderation
        "1.jpg": (0, 0, 3507, 1973),
        "2.jpg": (0, 0, 2400, 1973),
        "3.jpg": (0, 0, 2550, 1973),
        "4.jpg": (0, 0, 2350, 1973),
        "5.jpg": (430, 0, 2620, 1973),
        "6.jpg": (320, 0, 2860, 1973),
        "7.jpg": (470, 0, 2760, 1973),
        "8.jpg": (580, 0, 3310, 1973),
    }
    for src in sorted((ROOT / "web" / "assets" / "portfolio").glob("*.jpg")):
        specs.append(
            SourceSpec(
                source=src,
                target_root=ROOT / "web" / "assets" / "portfolio",
                text_box=portfolio_text_boxes.get(src.name),
            )
        )
    for name in ("review1.jpg", "review2.jpg"):
        src = ROOT / "media" / name
        if src.exists():
            specs.append(
                SourceSpec(
                    source=src,
                    target_root=ROOT / "media" / "i18n",
                    text_box=None,
                )
            )
    return specs


def ensure_openai_key() -> None:
    if os.getenv("OPENAI_API_KEY", "").strip():
        return
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line.startswith("OPENAI_API_KEY="):
            continue
        value = line.split("=", 1)[1].strip()
        if value:
            os.environ["OPENAI_API_KEY"] = value
        return


def prompt_for(lang_name: str) -> str:
    return (
        f"Translate all Russian text in this portfolio image to fluent {lang_name}. "
        "Preserve the exact visual style, composition, logos, photos, colors, and hierarchy. "
        "Replace text only, keeping typography weight and approximate line breaks. "
        "Do not add new elements. No watermark."
    )


def pad_to_api_ratio(image: Image.Image) -> tuple[Image.Image, tuple[int, int, int, int]]:
    src_w, src_h = image.size
    src_ratio = src_w / src_h
    if abs(src_ratio - API_RATIO) < 1e-3:
        return image.copy(), (0, 0, src_w, src_h)

    if src_ratio > API_RATIO:
        # Add top/bottom bars.
        pad_h = int(round(src_w / API_RATIO))
        pad_w = src_w
        canvas = Image.new("RGB", (pad_w, pad_h), (0, 0, 0))
        y = (pad_h - src_h) // 2
        canvas.paste(image, (0, y))
        crop_box = (0, y, src_w, y + src_h)
        return canvas, crop_box

    # Add left/right bars.
    pad_w = int(round(src_h * API_RATIO))
    pad_h = src_h
    canvas = Image.new("RGB", (pad_w, pad_h), (0, 0, 0))
    x = (pad_w - src_w) // 2
    canvas.paste(image, (x, 0))
    crop_box = (x, 0, x + src_w, src_h)
    return canvas, crop_box


def run_edit(image_path: Path, out_path: Path, prompt: str, retries: int) -> None:
    cmd = [
        sys.executable,
        str(IMAGE_GEN),
        "edit",
        "--image",
        str(image_path),
        "--out",
        str(out_path),
        "--force",
        "--size",
        "auto",
        "--quality",
        "high",
        "--input-fidelity",
        "high",
        "--use-case",
        "text-localization",
        "--prompt",
        prompt,
    ]
    attempt = 0
    while True:
        attempt += 1
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if proc.returncode == 0:
            return
        combined = f"{proc.stdout}\n{proc.stderr}"
        print(combined.strip())
        if attempt > retries:
            raise RuntimeError(f"Image edit failed after {attempt} attempts: {image_path}")
        wait_s = min(20, 4 * attempt)
        print(f"[retry] {image_path.name} in {wait_s}s (attempt {attempt}/{retries + 1})")
        time.sleep(wait_s)


def localize_one(spec: SourceSpec, lang_code: str, lang_name: str, retries: int, force: bool) -> bool:
    src = spec.source
    out_dir = spec.target_root / lang_code
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / src.name
    if out_file.exists() and not force:
        print(f"[skip] {lang_code} {src.name}")
        return False

    source_image = Image.open(src).convert("RGB")
    if spec.text_box:
        left, top, right, bottom = spec.text_box
        image = source_image.crop((left, top, right, bottom))
    else:
        left, top = 0, 0
        image = source_image
        right, bottom = image.size
    padded, crop_box = pad_to_api_ratio(image)

    tmp_in = TMP_DIR / f"{lang_code}-{src.stem}-input.png"
    tmp_out = TMP_DIR / f"{lang_code}-{src.stem}-generated.png"
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    padded.save(tmp_in)

    run_edit(tmp_in, tmp_out, prompt_for(lang_name), retries=retries)

    gen = Image.open(tmp_out).convert("RGB").resize(padded.size, Image.Resampling.LANCZOS)
    localized_region = gen.crop(crop_box)
    if spec.text_box:
        result = source_image.copy()
        result.paste(localized_region, (left, top))
    else:
        result = localized_region
    result.save(out_file, quality=95)

    print(f"[ok] {lang_code} -> {out_file.relative_to(ROOT)}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Localize Streamflow portfolio images.")
    parser.add_argument("--langs", default="en,pt,es", help="Comma-separated language codes")
    parser.add_argument("--retries", type=int, default=2, help="Retries per image edit")
    parser.add_argument("--force", action="store_true", help="Overwrite existing localized files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_openai_key()
    if not os.getenv("OPENAI_API_KEY", "").strip():
        print("OPENAI_API_KEY is not configured.", file=sys.stderr)
        return 1
    if not IMAGE_GEN.exists():
        print(f"image_gen.py not found at {IMAGE_GEN}", file=sys.stderr)
        return 1

    requested_langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    unknown = [code for code in requested_langs if code not in TARGET_LANGS]
    if unknown:
        print(f"Unknown lang codes: {', '.join(unknown)}", file=sys.stderr)
        return 1

    specs = source_specs()
    if not specs:
        print("No source images found.")
        return 0

    generated = 0
    for lang_code in requested_langs:
        lang_name = TARGET_LANGS[lang_code]
        print(f"\n=== {lang_code} ({lang_name}) ===")
        for spec in specs:
            changed = localize_one(spec, lang_code, lang_name, retries=max(0, args.retries), force=args.force)
            if changed:
                generated += 1
    print(f"\nDone. Generated/updated files: {generated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
