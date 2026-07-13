import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "funclip"))

from llm.twelvelabs_api import (
    _resolve_video_context,
    call_twelvelabs_pegasus,
    PEGASUS_SYSTEM_PROMPT,
)
from utils.trans_utils import extract_timestamps


class TestResolveVideoContext(unittest.TestCase):
    """No-network checks for the video-source routing logic."""

    def test_http_url_becomes_url_context_without_upload(self):
        # client is unused on the URL path; pass None to prove no upload happens.
        ctx = _resolve_video_context(None, "https://example.com/clip.mp4")
        self.assertEqual(ctx.type, "url")
        self.assertEqual(ctx.url, "https://example.com/clip.mp4")

    def test_missing_local_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            _resolve_video_context(None, "/no/such/video.mp4")

    def test_default_prompt_requests_parseable_segment_format(self):
        self.assertIn("[start_time-end_time]", PEGASUS_SYSTEM_PROMPT)


class TestPegasusTimestampNormalization(unittest.TestCase):
    def _call_with_response(self, response_text):
        with patch("twelvelabs.TwelveLabs") as client_class, patch(
            "llm.twelvelabs_api._resolve_video_context", return_value=object()
        ):
            client_class.return_value.analyze.return_value.data = response_text
            return call_twelvelabs_pegasus(
                "test-key", "https://example.com/clip.mp4"
            )

    def test_decimal_and_integer_ranges_feed_existing_parser(self):
        response = (
            "1. [12.5-15.0] first highlight\n"
            "2. [120 - 135] second highlight"
        )

        normalized = self._call_with_response(response)

        self.assertEqual(
            normalized,
            "1. [00:00:12,500-00:00:15,000] first highlight\n"
            "2. [00:02:00,000-00:02:15,000] second highlight",
        )
        self.assertEqual(
            extract_timestamps(normalized), [[12500, 15000], [120000, 135000]]
        )

    def test_existing_srt_range_is_unchanged(self):
        response = "1. [00:00:12,500-00:00:15,000] existing highlight"

        normalized = self._call_with_response(response)

        self.assertEqual(normalized, response)
        self.assertEqual(extract_timestamps(normalized), [[12500, 15000]])

    def test_invalid_ranges_do_not_create_clips(self):
        response = (
            "1. [15-12.5] reversed\n"
            "2. [8-8] empty\n"
            "3. [not-a-time] malformed\n"
            "4. [1.25-2.5] valid"
        )

        normalized = self._call_with_response(response)

        self.assertIn("[15-12.5]", normalized)
        self.assertIn("[8-8]", normalized)
        self.assertIn("[not-a-time]", normalized)
        self.assertEqual(extract_timestamps(normalized), [[1250, 2500]])


@unittest.skipUnless(
    os.environ.get("TWELVELABS_API_KEY"),
    "set TWELVELABS_API_KEY to run the live Pegasus smoke test",
)
class TestPegasusLive(unittest.TestCase):
    def test_analyze_public_url_returns_text(self):
        res = call_twelvelabs_pegasus(
            os.environ["TWELVELABS_API_KEY"],
            "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        )
        self.assertIsInstance(res, str)
        self.assertTrue(len(res) > 0)


if __name__ == "__main__":
    unittest.main()
