"""Tests for MiniMax routing through the OpenAI-compatible client."""

import os
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import (
    MINIMAX_API_BASE,
    MINIMAX_API_BASE_CN,
    openai_call,
)


def _mock_completion(content="ok"):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestMiniMaxRouting(unittest.TestCase):
    def test_minimax_prefix_uses_global_base_url(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion("clip plan")

        with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
            result = openai_call(
                "minimax-key",
                "minimax/MiniMax-M3",
                "subtitle text",
                "find highlights",
            )

        self.assertEqual(result, "clip plan")
        openai_cls.assert_called_once_with(
            api_key="minimax-key",
            base_url=MINIMAX_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "MiniMax-M3")

    def test_minimax_api_key_falls_back_to_env(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"MINIMAX_API_KEY": "env-minimax-key"}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("", "minimax/MiniMax-M2.7", "text")

        openai_cls.assert_called_once_with(
            api_key="env-minimax-key",
            base_url=MINIMAX_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "MiniMax-M2.7")

    def test_minimax_api_base_env_overrides_region(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"MINIMAX_API_BASE": MINIMAX_API_BASE_CN}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("minimax-key", "minimax/MiniMax-M3", "text")

        openai_cls.assert_called_once_with(
            api_key="minimax-key",
            base_url=MINIMAX_API_BASE_CN,
        )

    def test_empty_minimax_model_raises(self):
        with self.assertRaises(ValueError):
            openai_call("key", "minimax/", "text")

    def test_missing_minimax_key_does_not_fall_back_to_openai_key(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-only-key"},
            clear=True,
        ):
            with patch("funclip.llm.openai_api.OpenAI") as openai_cls:
                with self.assertRaisesRegex(ValueError, "MINIMAX_API_KEY"):
                    openai_call("", "minimax/MiniMax-M2.7", "text")

        openai_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
