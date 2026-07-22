"""Tests for OpenAI-compatible LLM routing."""

import os
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import ATLASCLOUD_API_BASE, openai_call


def _mock_completion(content="ok"):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestOpenAICompatibleRouting(unittest.TestCase):
    def test_atlascloud_prefix_uses_atlas_base_url(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion("clip plan")

        with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
            result = openai_call(
                "atlas-key",
                "atlascloud/qwen/qwen3.5-flash",
                "subtitle text",
                "find highlights",
            )

        self.assertEqual(result, "clip plan")
        openai_cls.assert_called_once_with(
            api_key="atlas-key",
            base_url=ATLASCLOUD_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "qwen/qwen3.5-flash")

    def test_atlascloud_api_key_falls_back_to_env(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"ATLASCLOUD_API_KEY": "env-atlas-key"}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("", "atlascloud/deepseek-ai/deepseek-v4-pro", "text")

        openai_cls.assert_called_once_with(
            api_key="env-atlas-key",
            base_url=ATLASCLOUD_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "deepseek-ai/deepseek-v4-pro")

    def test_empty_atlascloud_model_raises(self):
        with self.assertRaises(ValueError):
            openai_call("key", "atlascloud/", "text")


if __name__ == "__main__":
    unittest.main()
