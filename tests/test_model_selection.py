import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "funclip"))

from launch import create_asr_model


class RecordingAutoModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class TestModelSelection(unittest.TestCase):
    def test_fun_asr_nano_is_selected_independently_of_language(self):
        model = create_asr_model(
            "fun-asr-nano", "en", auto_model_cls=RecordingAutoModel
        )

        self.assertEqual(
            model.kwargs,
            {
                "model": "FunAudioLLM/Fun-ASR-Nano-2512",
                "trust_remote_code": True,
                "remote_code": "./model.py",
                "vad_model": "fsmn-vad",
                "vad_kwargs": {"max_single_segment_time": 30000},
                "spk_model": "cam++",
                "hub": "hf",
            },
        )

    def test_sensevoice_is_selected_independently_of_language(self):
        model = create_asr_model(
            "sensevoice", "en", auto_model_cls=RecordingAutoModel
        )

        self.assertEqual(
            model.kwargs,
            {
                "model": "iic/SenseVoiceSmall",
                "vad_model": "fsmn-vad",
                "vad_kwargs": {"max_single_segment_time": 30000},
                "spk_model": "cam++",
            },
        )

    def test_paraformer_keeps_language_specific_model_mapping(self):
        cases = {
            "zh": "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
            "en": "iic/speech_paraformer_asr-en-16k-vocab4199-pytorch",
        }

        for language, expected_model in cases.items():
            with self.subTest(language=language):
                model = create_asr_model(
                    "paraformer", language, auto_model_cls=RecordingAutoModel
                )
                self.assertEqual(model.kwargs["model"], expected_model)
                self.assertEqual(
                    model.kwargs["vad_model"],
                    "damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                )
                self.assertEqual(
                    model.kwargs["punc_model"],
                    "damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                )
                self.assertEqual(
                    model.kwargs["spk_model"],
                    "damo/speech_campplus_sv_zh-cn_16k-common",
                )


if __name__ == "__main__":
    unittest.main()
