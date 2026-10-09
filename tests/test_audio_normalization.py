import sys
from pathlib import Path

import librosa
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "funclip"))

from videoclipper import VideoClipper


class CaptureASR:
    def generate(self, data, **kwargs):
        self.data = np.array(data, copy=True)
        return [{
            "text": "test",
            "raw_text": "test",
            "timestamp": [[0, 500]],
            "sentence_info": [],
        }]


def _make_audio(rate, channels, dtype):
    t = np.arange(rate) / rate
    left = 0.2 * np.sin(2 * np.pi * 440 * t)
    right = 0.3 * np.sin(2 * np.pi * 880 * t)
    audio = left if channels == 1 else np.stack([left, right], axis=1)
    if dtype == np.int16:
        audio = np.rint(audio * 32767).astype(np.int16)
    else:
        audio = audio.astype(dtype)
    return audio


def _expected_first_channel(audio, rate):
    data = audio[:, 0] if audio.ndim == 2 else audio
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    else:
        data = data.astype(np.float64)
    if rate != 16000:
        data = librosa.resample(data, orig_sr=rate, target_sr=16000)
    return data


def test_recog_normalizes_supported_sample_rates_channels_and_dtypes():
    for rate in (8000, 16000, 44100, 48000):
        for channels in (1, 2):
            for dtype in (np.float32, np.int16):
                audio = _make_audio(rate, channels, dtype)
                original = audio.copy()
                expected = _expected_first_channel(audio, rate)
                model = CaptureASR()
                clipper = VideoClipper(model)
                clipper.lang = "en"

                _, _, state = clipper.recog((rate, audio))

                stored_rate, stored_audio = state["audio_input"]
                assert stored_rate == 16000
                assert stored_audio.ndim == 1
                assert len(stored_audio) == 16000
                assert len(model.data) == 16000
                np.testing.assert_array_equal(audio, original)
                np.testing.assert_allclose(model.data, expected, rtol=1e-7, atol=1e-7)
                np.testing.assert_allclose(stored_audio, expected, rtol=1e-7, atol=1e-7)

                (out_rate, out), _, _ = clipper.clip(
                    "", 0, 0, state, timestamp_list=[[0, 8000]]
                )
                assert out_rate == 16000
                assert len(out) == 8000
                assert len(out) / out_rate == 0.5
                np.testing.assert_allclose(out, expected[:8000], rtol=1e-7, atol=1e-7)
