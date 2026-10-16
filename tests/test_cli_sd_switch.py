import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "funclip"))

from videoclipper import VideoClipper, get_parser


class RecorderASR:
    def generate(self, data, **kwargs):
        self.return_spk_res = kwargs["return_spk_res"]
        return [{"text": "", "raw_text": "", "timestamp": [], "sentence_info": []}]


def _speaker_requested(sd_switch):
    model = RecorderASR()
    clipper = VideoClipper(model)
    clipper.lang = "zh"
    _, _, state = clipper.recog((16000, np.zeros(160)), sd_switch=sd_switch)
    return model.return_spk_res, "sd_sentences" in state


def test_cli_yes_enables_speaker_diarization():
    args = get_parser().parse_args([
        "--stage", "1",
        "--file", "placeholder.wav",
        "--sd_switch", "yes",
    ])
    assert _speaker_requested(args.sd_switch) == (True, True)


def test_cli_no_and_default_keep_speaker_diarization_disabled():
    parser = get_parser()
    explicit = parser.parse_args([
        "--stage", "1",
        "--file", "placeholder.wav",
        "--sd_switch", "no",
    ])
    default = parser.parse_args(["--stage", "1", "--file", "placeholder.wav"])
    assert _speaker_requested(explicit.sd_switch) == (False, False)
    assert _speaker_requested(default.sd_switch) == (False, False)


def test_existing_ui_case_variants_remain_supported():
    assert _speaker_requested("Yes") == (True, True)
    assert _speaker_requested("No") == (False, False)
