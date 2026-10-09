import copy
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "funclip"))

from videoclipper import VideoClipper  # noqa: E402


CUE_TIMES = re.compile(r"(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)")


class TestAudioClipSubtitleTimeline(unittest.TestCase):
    """Subtitles of concatenated audio regions follow the concatenated output."""

    def setUp(self):
        sentences = [
            {"text": "hello", "timestamp": [[1000, 2000]], "spk": 0},
            {"text": "world", "timestamp": [[4000, 5000]], "spk": 0},
        ]
        self.state = {
            "audio_input": (16000, np.zeros(96000)),
            "recog_res_raw": "hello world",
            "timestamp": [[1000, 2000], [4000, 5000]],
            "sentences": sentences,
            "sd_sentences": copy.deepcopy(sentences),
        }

    def clip(self, *args, **kwargs):
        return VideoClipper(None).clip(*args, state=copy.deepcopy(self.state), **kwargs)

    def test_second_region_subtitle_starts_after_the_first_region(self):
        (rate, audio), _, subtitles = self.clip("hello#world", 0, 0)

        self.assertEqual((rate, len(audio)), (16000, 32000))
        self.assertEqual(
            CUE_TIMES.findall(subtitles),
            [("00:00:00,000", "00:00:01,000"), ("00:00:01,000", "00:00:02,000")],
        )

    def test_explicit_timestamps_follow_the_concatenated_output(self):
        (_, audio), _, subtitles = self.clip(
            None, 0, 0, timestamp_list=[[16000, 32000], [64000, 80000]]
        )

        self.assertEqual(len(audio), 32000)
        self.assertEqual(
            CUE_TIMES.findall(subtitles),
            [("00:00:00,000", "00:00:01,000"), ("00:00:01,000", "00:00:02,000")],
        )

    def test_single_region_is_unchanged(self):
        (_, audio), _, subtitles = self.clip("hello", 0, 0)

        self.assertEqual(len(audio), 16000)
        self.assertEqual(CUE_TIMES.findall(subtitles), [("00:00:00,000", "00:00:01,000")])

    def clip_with(self, sentences, seconds, *args, **kwargs):
        state = {
            "audio_input": (16000, np.zeros(16000 * seconds)),
            "recog_res_raw": "",
            "timestamp": [],
            "sentences": sentences,
            "sd_sentences": copy.deepcopy(sentences),
        }
        return VideoClipper(None).clip(*args, state=state, **kwargs)

    def test_region_emptied_by_start_offset_does_not_shift_later_subtitles(self):
        # start_ost=1500ms turns the first region into 2.5-2.0s (nothing appended);
        # the second contributes 5.5-7.0s, so "world" (6-7s) sits at 0.5-1.5s.
        sentences = [
            {"text": "hello", "timestamp": [[1000, 2000]], "spk": 0},
            {"text": "world", "timestamp": [[6000, 7000]], "spk": 0},
        ]
        (_, audio), _, subtitles = self.clip_with(
            sentences, 8, None, 1500, 0, timestamp_list=[[16000, 32000], [64000, 112000]]
        )

        self.assertEqual(len(audio), 24000)
        self.assertEqual(CUE_TIMES.findall(subtitles), [("00:00:00,500", "00:00:01,500")])

    def test_middle_region_emptied_by_start_offset_adds_no_time(self):
        # start_ost=1000ms: the first region becomes 1-3s, the middle one 5-4.5s
        # (start > end, nothing appended) and the last 7-8s.
        sentences = [
            {"text": "one", "timestamp": [[2000, 2800]], "spk": 0},
            {"text": "two", "timestamp": [[7200, 7800]], "spk": 0},
        ]
        (_, audio), _, subtitles = self.clip_with(
            sentences,
            8,
            None,
            1000,
            0,
            timestamp_list=[[0, 48000], [64000, 72000], [96000, 128000]],
        )

        self.assertEqual(len(audio), 48000)
        self.assertEqual(
            CUE_TIMES.findall(subtitles),
            [("00:00:01,000", "00:00:01,800"), ("00:00:02,200", "00:00:02,800")],
        )

    def test_end_offset_clamped_to_audio_length(self):
        # end_ost=2000ms extends the first region to 0-3s and would push the
        # second past the 4s input; it is clamped to 3-4s.
        sentences = [
            {"text": "one", "timestamp": [[0, 1000]], "spk": 0},
            {"text": "two", "timestamp": [[3000, 4000]], "spk": 0},
        ]
        (_, audio), _, subtitles = self.clip_with(
            sentences, 4, None, 0, 2000, timestamp_list=[[0, 16000], [48000, 64000]]
        )

        self.assertEqual(len(audio), 64000)
        self.assertEqual(CUE_TIMES.findall(subtitles)[-1], ("00:00:03,000", "00:00:04,000"))

    def test_accumulated_offset_does_not_lose_a_millisecond_to_float_sums(self):
        # 114240 + 105600 samples is exactly 13.74s, but 7.14 + 6.6 in floats is
        # 13.739999..., which the millisecond formatter truncated to 13.739s.
        seconds = 20
        sentences = [
            {"text": "a", "timestamp": [[0, 7140]], "spk": 0},
            {"text": "b", "timestamp": [[8000, 14600]], "spk": 0},
            {"text": "c", "timestamp": [[15000, 16000]], "spk": 0},
        ]
        (_, audio), _, subtitles = self.clip_with(
            sentences,
            seconds,
            None,
            0,
            0,
            timestamp_list=[[0, 114240], [128000, 233600], [240000, 256000]],
        )

        self.assertEqual(len(audio), 114240 + 105600 + 16000)
        self.assertEqual(CUE_TIMES.findall(subtitles)[2], ("00:00:13,740", "00:00:14,740"))


if __name__ == "__main__":
    unittest.main()
