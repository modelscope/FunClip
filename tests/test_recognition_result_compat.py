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
    def _recognize(self, result, sd_switch="no"):
        clipper = VideoClipper(DummyASRModel(result))
        clipper.lang = "zh"
        audio = (16000, np.zeros(16000, dtype=np.float32))
        return clipper.recog(audio, sd_switch=sd_switch)

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

    def test_moss_result_preserves_speaker_segments_without_raw_markup(self):
        clipper = VideoClipper(
            DummyASRModel(
                {
                    "key": "utt",
                    "text": "Hello there General Kenobi",
                    "raw_text": (
                        "[0.00][S01]Hello there[1.20]"
                        "[1.25][S02]General Kenobi[2.80]"
                    ),
                    "timestamp": [[0, 1200], [1250, 2800]],
                    "sentence_info": [
                        {
                            "start": 0,
                            "end": 1200,
                            "text": "Hello there",
                            "spk": "S01",
                            "timestamp": [[0, 1200]],
                        },
                        {
                            "start": 1250,
                            "end": 2800,
                            "text": "General Kenobi",
                            "spk": "S02",
                            "timestamp": [[1250, 2800]],
                        },
                    ],
                }
            )
        )
        clipper.lang = "en"
        audio = (16000, np.zeros(48000, dtype=np.float32))

        text, srt, state = clipper.recog(audio, sd_switch="Yes")

        self.assertEqual(text, "Hello there General Kenobi")
        self.assertEqual(state["recog_res_raw"], "Hello there General Kenobi")
        self.assertNotIn("[S01]", srt)
        self.assertIn("spkS01", srt)
        self.assertIn("spkS02", srt)
        self.assertEqual(
            [item["spk"] for item in state["sd_sentences"]], ["S01", "S02"]
        )

        (_, clipped), message, _ = clipper.clip(
            "", 0, 0, state, dest_spk="spkS02"
        )
        self.assertEqual(len(clipped), 24800)
        self.assertIn("1 periods found", message)

        (_, unchanged), message, _ = clipper.clip(
            "General Kenobi", 0, 0, state
        )
        self.assertEqual(len(unchanged), len(audio[1]))
        self.assertIn("No period found", message)

    def test_moss_speaker_clipping_keeps_short_turns(self):
        text, srt, state = self._recognize(
            {
                "key": "utt",
                "text": "Yes",
                "raw_text": "[1.00][S02]Yes[1.40]",
                "timestamp": [[1000, 1400]],
                "sentence_info": [
                    {
                        "start": 1000,
                        "end": 1400,
                        "text": "Yes",
                        "spk": "S02",
                        "timestamp": [[1000, 1400]],
                    }
                ],
            },
            sd_switch="Yes",
        )

        state["audio_input"] = (16000, np.zeros(32000, dtype=np.float32))
        clipper = VideoClipper(DummyASRModel({}))
        (_, clipped), message, _ = clipper.clip(
            "", 0, 0, state, dest_spk="spkS02"
        )
        self.assertEqual(text, "Yes")
        self.assertIn("spkS02", srt)
        self.assertEqual(len(clipped), 6400)
        self.assertIn("1 periods found", message)

    def test_moss_truncated_final_segment_fails_instead_of_silently_dropping_it(self):
        with self.assertRaisesRegex(RuntimeError, "truncated MOSS transcript"):
            self._recognize(
                {
                    "key": "utt",
                    "text": "Complete turn",
                    "raw_text": (
                        "[0.00][S01]Complete turn[1.00]"
                        "[1.10][S02]This final turn has no end timestamp"
                    ),
                    "timestamp": [[0, 1000]],
                    "sentence_info": [
                        {
                            "start": 0,
                            "end": 1000,
                            "text": "Complete turn",
                            "spk": "S01",
                            "timestamp": [[0, 1000]],
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
