#!/usr/bin/env python3
"""
Utility script to fetch the fonts that our PDF styles rely on.

The script downloads each font into the repository-level `fonts/` directory so
that PDF generation works on any machine (no dependency on macOS system fonts).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, TypedDict
from urllib.request import urlopen
import shutil


class FontSpec(TypedDict):
    family: str
    filename: str
    url: str
    description: str


FONTS: tuple[FontSpec, ...] = (
    {
        "family": "Monaco",
        "filename": "Monaco.ttf",
        "url": "https://github.com/todylu/monaco.ttf/raw/master/monaco.ttf",
        "description": "Monaco monospace font used for code blocks.",
    },
    {
        "family": "San Francisco",
        "filename": "SF-Pro-Text-Regular.otf",
        "url": "https://raw.githubusercontent.com/sahibjotsaggu/San-Francisco-Pro-Fonts/master/SF-Pro-Text-Regular.otf",
        "description": "San Francisco Pro Text regular face for body copy.",
    },
    {
        "family": "San Francisco",
        "filename": "SF-Pro-Text-RegularItalic.otf",
        "url": "https://raw.githubusercontent.com/sahibjotsaggu/San-Francisco-Pro-Fonts/master/SF-Pro-Text-RegularItalic.otf",
        "description": "San Francisco Pro Text regular italic face for emphasis.",
    },
)


def download_font(font: FontSpec, target_dir: Path, force: bool) -> None:
    """Download a font if it does not exist (or when forced)."""
    target_path = target_dir / font["filename"]

    if target_path.exists() and not force:
        print(f"✔ {font['filename']} already present, skipping")
        return

    print(f"⬇ Downloading {font['filename']} ({font['description']})")
    try:
        with urlopen(font["url"]) as response, open(target_path, "wb") as output:
            shutil.copyfileobj(response, output)
    except Exception as exc:  # pragma: no cover - network errors bubble up to the CLI
        if target_path.exists():
            target_path.unlink()
        raise RuntimeError(
            f"Failed to download {font['filename']} from {font['url']}: {exc}"
        ) from exc


def run(fonts: Iterable[FontSpec], target_dir: Path, force: bool) -> None:
    """Download all required fonts into target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for font in fonts:
        download_font(font, target_dir, force)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the fonts required for PDF generation."
    )
    parser.add_argument(
        "--fonts-dir",
        default=str(Path(__file__).resolve().parents[1] / "fonts"),
        help="Directory where fonts should be stored (defaults to <repo>/fonts).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download fonts even if they already exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_dir = Path(args.fonts_dir).expanduser().resolve()
    try:
        run(FONTS, target_dir, args.force)
    except Exception as exc:  # pragma: no cover - surface clear error to CLI
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
