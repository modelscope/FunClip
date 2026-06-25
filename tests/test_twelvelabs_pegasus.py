import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "funclip"))

from llm.twelvelabs_api import (
    _resolve_video_context,
    call_twelvelabs_pegasus,
    PEGASUS_SYSTEM_PROMPT,
)


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
