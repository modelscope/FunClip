"""Pillow-backed subtitle text rendering for MoviePy 1.x."""

from pathlib import Path
from numbers import Real

import numpy as np
from moviepy.editor import ImageClip
from PIL import Image, ImageColor, ImageDraw, ImageFont


DEFAULT_FONT_PATH = (
    Path(__file__).resolve().parents[1] / "font" / "STHeitiMedium.ttc"
)


def make_text_clip(
    text,
    font_path=DEFAULT_FONT_PATH,
    font_size=32,
    color="white",
):
    """Render transparent subtitle text without ImageMagick."""
    if isinstance(font_size, bool) or not isinstance(font_size, Real):
        raise TypeError("font_size must be a number")
    if font_size <= 0 or not float(font_size).is_integer():
        raise ValueError("font_size must be a positive integer")
    font_size = int(font_size)

    font_path = Path(font_path)
    if not font_path.is_file():
        raise FileNotFoundError(f"subtitle font not found: {font_path}")

    try:
        fill = ImageColor.getrgb(str(color))[:3]
    except ValueError as error:
        raise ValueError(f"unsupported subtitle color: {color!r}") from error

    text = str(text)
    font = ImageFont.truetype(str(font_path), font_size)
    spacing = max(1, font_size // 5)
    probe = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    left, top, right, bottom = draw.multiline_textbbox(
        (0, 0), text, font=font, spacing=spacing
    )
    padding = max(2, font_size // 12)
    width = max(1, right - left + 2 * padding)
    height = max(1, bottom - top + 2 * padding)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.multiline_text(
        (padding - left, padding - top),
        text,
        font=font,
        fill=(*fill, 255),
        spacing=spacing,
    )
    return ImageClip(np.asarray(image), transparent=True)
