import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "funclip"))

from videoclipper import VideoClipper  # noqa: E402


class DummyVideoClip:
    def __init__(self):
        self.write_calls = []

    def write_videofile(self, *args, **kwargs):
        self.write_calls.append((args, kwargs))


class DummyVideo:
    def __init__(self):
        self.subclip_calls = []

    def subclip(self, start, end):
        self.subclip_calls.append((start, end))
        return DummyVideoClip()


class TestDuplicateTextMatching(unittest.TestCase):
    def setUp(self):
        self.raw_text = "重 复 其 他 重 复"
        self.timestamps = [[i * 100, (i + 1) * 100] for i in range(6)]

    @patch("videoclipper.generate_srt_clip", return_value=("", [], 0))
    def test_audio_clip_keeps_all_repeated_matches_without_offsets(self, _generate_srt):
        clipper = VideoClipper(None)
        audio = np.arange(10000, dtype=np.float32)
        state = {
            "audio_input": (16000, audio),
            "recog_res_raw": self.raw_text,
            "timestamp": self.timestamps,
            "sentences": [],
        }

        (sample_rate, clipped), message, _ = clipper.clip("重复", 0, 0, state)

        self.assertEqual(sample_rate, 16000)
        self.assertEqual(len(clipped), 6400)
        self.assertIn("2 periods found", message)

    @patch(
        "videoclipper.generate_srt_clip",
        return_value=("", [((0.0, 0.2), "重复")], 1),
    )
    def test_video_clip_keeps_all_repeated_matches_without_offsets(self, _generate_srt):
        clipper = VideoClipper(None)
        clipper.lang = "zh"
        video = DummyVideo()
        output_clip = DummyVideoClip()
        state = {
            "recog_res_raw": self.raw_text,
            "timestamp": self.timestamps,
            "sentences": [],
            "video": video,
            "clip_video_file": "/tmp/duplicate_clip.mp4",
            "video_filename": "/tmp/duplicate.mp4",
        }

        with patch(
            "videoclipper.concatenate_videoclips", return_value=output_clip
        ) as concatenate:
            _, message, _ = clipper.video_clip("重复", 0, 0, state)

        self.assertEqual(len(video.subclip_calls), 2)
        self.assertAlmostEqual(video.subclip_calls[0][0], 0.0)
        self.assertAlmostEqual(video.subclip_calls[0][1], 0.2)
        self.assertAlmostEqual(video.subclip_calls[1][0], 0.4)
        self.assertAlmostEqual(video.subclip_calls[1][1], 0.6)
        self.assertEqual(len(concatenate.call_args.args[0]), 2)
        self.assertEqual(len(output_clip.write_calls), 1)
        self.assertIn("2 periods found", message)


if __name__ == "__main__":
    unittest.main()
