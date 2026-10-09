import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "funclip"))

from utils.trans_utils import pre_proc, proc
from videoclipper import VideoClipper


def test_proc_matches_contiguous_chinese_using_token_timestamps():
    raw = "嗯那么今天我们就简"
    timestamps = [
        [230, 290], [590, 650], [710, 770],
        [890, 950], [1010, 1070], [1250, 1310],
        [1430, 1490], [1610, 1670], [1970, 2030],
    ]

    assert proc(raw, timestamps, pre_proc(raw[:8])) == [[3680, 26720]]
    assert proc(raw, timestamps, pre_proc("简")) == [[31520, 32480]]


def test_proc_preserves_ascii_case_insensitive_matching():
    timestamps = [[0, 100], [100, 200]]
    assert proc("Hello WORLD", timestamps, "hello world") == [[0, 3200]]


def test_proc_keeps_repeated_matches_non_overlapping():
    timestamps = [[0, 100], [100, 200], [200, 300], [300, 400]]
    expected = [[0, 3200], [3200, 6400]]

    assert proc("哈哈哈哈", timestamps, pre_proc("哈哈")) == expected
    assert proc("哈 哈 哈 哈", timestamps, pre_proc("哈哈")) == expected


def test_clip_does_not_duplicate_audio_for_repeated_matches():
    timestamps = [[0, 100], [100, 200], [200, 300], [300, 400]]
    state = {
        "audio_input": (16000, np.arange(6400, dtype=np.float64)),
        "recog_res_raw": "哈 哈 哈 哈",
        "timestamp": timestamps,
        "sentences": [],
    }
    clipper = VideoClipper(None)

    (_, audio), _, _ = clipper.clip("哈哈", 0, 0, state)

    assert len(audio) == 6400
    np.testing.assert_array_equal(audio, state["audio_input"][1])
