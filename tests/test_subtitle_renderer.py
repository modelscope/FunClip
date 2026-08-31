from pathlib import Path

import numpy as np
from moviepy.editor import ColorClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

from funclip.subtitle_renderer import make_text_clip


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "font" / "STHeitiMedium.ttc"


def _foreground_rgb(color):
    clip = make_text_clip("字幕 Test", FONT_PATH, 48, color)
    frame = clip.get_frame(0)
    mask = clip.mask.get_frame(0)

    assert mask.min() == 0
    assert mask.max() > 0.9
    return frame[mask > 0.5]


def test_subtitle_renderer_preserves_selected_colors():
    red = _foreground_rgb("red").mean(axis=0)
    green = _foreground_rgb("green").mean(axis=0)
    black = _foreground_rgb("black").mean(axis=0)
    white = _foreground_rgb("white").mean(axis=0)

    assert red[0] > 200 and red[1] < 40 and red[2] < 40
    assert green[1] > 100 and green[0] < 40 and green[2] < 40
    assert black.max() < 10
    assert white.min() > 240


def test_subtitle_renderer_rejects_invalid_font_size():
    assert make_text_clip("subtitle", FONT_PATH, 48.0, "white").size[0] > 0

    for value in (0, -1, 48.5, "48", True):
        try:
            make_text_clip("subtitle", FONT_PATH, value, "white")
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"font size {value!r} should be rejected")


def test_selected_color_reaches_composited_video_frame():
    background = ColorClip((320, 120), color=(20, 20, 20), duration=1)
    subtitles = SubtitlesClip(
        [((0, 1), "字幕")],
        lambda text: make_text_clip(text, FONT_PATH, 48, "red"),
    ).set_pos(("center", "bottom"))
    frame = CompositeVideoClip([background, subtitles]).get_frame(0.5)

    red_pixels = (
        (frame[:, :, 0] > 180)
        & (frame[:, :, 1] < 60)
        & (frame[:, :, 2] < 60)
    )
    assert red_pixels.sum() > 100


def test_pillow_is_an_explicit_runtime_dependency():
    requirements = {
        line.strip().lower()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "pillow" in requirements
