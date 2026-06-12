import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "funclip"))

from videoclipper import VideoClipper


class DummyASRModel:
    def __init__(self, result):
        self.result = result

    def generate(self, *args, **kwargs):
        return [self.result]


class TestRecognitionResultCompat(unittest.TestCase):
    def _recognize(self, result):
        clipper = VideoClipper(DummyASRModel(result))
        clipper.lang = "zh"
        audio = (16000, np.zeros(16000, dtype=np.float32))
        return clipper.recog(audio)

    def test_fun_asr_nano_result_without_sentence_info_or_raw_text_still_builds_state(self):
        text, srt, state = self._recognize(
            {
                "key": "utt",
                "text": "你好世界。",
                "text_tn": "你好世界",
                "timestamp": [[0, 500], [500, 1000]],
                "sentence_info": [],
            }
        )

        self.assertEqual(text, "你好世界。")
        self.assertEqual(state["recog_res_raw"], "你好世界")
        self.assertEqual(
            state["sentences"],
            [{"text": "你好世界。", "timestamp": [[0, 500], [500, 1000]]}],
        )
        self.assertIn("00:00:00,000 --> 00:00:01,000", srt)

    def test_none_sentence_timestamp_falls_back_to_top_level_timestamp(self):
        text, srt, state = self._recognize(
            {
                "key": "utt",
                "text": "测试文本",
                "raw_text": "测试文本",
                "timestamp": [[0, 1000]],
                "sentence_info": [{"text": "测试文本", "timestamp": None}],
            }
        )

        self.assertEqual(text, "测试文本")
        self.assertEqual(
            state["sentences"], [{"text": "测试文本", "timestamp": [[0, 1000]]}]
        )
        self.assertIn("测试文本", srt)

    def test_sensevoice_rich_tags_are_removed_from_text_and_srt(self):
        text, srt, state = self._recognize(
            {
                "key": "utt",
                "text": "<|zh|><|NEUTRAL|><|Speech|><|woitn|>你好世界",
                "timestamp": [[0, 300], [300, 600], [600, 900], [900, 1200]],
                "sentence_info": [
                    {
                        "text": "<|zh|><|NEUTRAL|><|Speech|><|woitn|>你好世界",
                        "timestamp": [[0, 300], [300, 600], [600, 900], [900, 1200]],
                    }
                ],
            }
        )

        self.assertEqual(text, "你好世界")
        self.assertEqual(state["sentences"][0]["text"], "你好世界")
        self.assertNotIn("<|zh|>", state["recog_res_raw"])
        self.assertNotIn("<|zh|>", srt)

    def test_long_token_level_sentence_is_split_into_subtitle_chunks(self):
        long_text = "一二三四五六七八九十甲乙"
        timestamps = [[i * 1000, (i + 1) * 1000] for i in range(len(long_text))]

        _, srt, state = self._recognize(
            {
                "key": "utt",
                "text": long_text,
                "timestamp": timestamps,
                "sentence_info": [{"text": long_text, "timestamp": timestamps}],
            }
        )

        self.assertGreater(len(state["sentences"]), 1)
        self.assertIn("00:00:00,000 --> 00:00:08,000", srt)
        self.assertIn("00:00:08,000 --> 00:00:12,000", srt)


if __name__ == "__main__":
    unittest.main()
