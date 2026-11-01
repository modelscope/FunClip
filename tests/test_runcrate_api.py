"""Tests for Runcrate routing through the OpenAI-compatible client."""

import os
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import (
    RUNCRATE_API_BASE,
    openai_call,
)


def _mock_completion(content="ok"):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestRuncrateRouting(unittest.TestCase):
    def test_runcrate_prefix_uses_gateway_base_url(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion("clip plan")

        with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
            result = openai_call(
                "rc-key",
                "runcrate/deepseek-ai/DeepSeek-V4.1-Flash",
                "subtitle text",
                "find highlights",
            )

        self.assertEqual(result, "clip plan")
        openai_cls.assert_called_once_with(
            api_key="rc-key",
            base_url=RUNCRATE_API_BASE,
        )
        # Only the runcrate/ prefix is stripped; the vendor stays in the id.
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "deepseek-ai/DeepSeek-V4.1-Flash")

    def test_runcrate_api_key_falls_back_to_env(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"RUNCRATE_API_KEY": "env-rc-key"}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("", "runcrate/deepseek-ai/DeepSeek-V4.1-Flash", "text")

        openai_cls.assert_called_once_with(
            api_key="env-rc-key",
            base_url=RUNCRATE_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "deepseek-ai/DeepSeek-V4.1-Flash")

    def test_runcrate_api_base_env_overrides(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(
            os.environ,
            {"RUNCRATE_API_BASE": "https://gateway.example.com/v1"},
            clear=False,
        ):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("rc-key", "runcrate/openai/gpt-oss-120b", "text")

        openai_cls.assert_called_once_with(
            api_key="rc-key",
            base_url="https://gateway.example.com/v1",
        )

    def test_empty_runcrate_model_raises(self):
        with self.assertRaises(ValueError):
            openai_call("key", "runcrate/", "text")

    def test_missing_runcrate_key_does_not_fall_back_to_openai_key(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-only-key"},
            clear=True,
        ):
            with patch("funclip.llm.openai_api.OpenAI") as openai_cls:
                with self.assertRaisesRegex(ValueError, "RUNCRATE_API_KEY"):
                    openai_call("", "runcrate/deepseek-ai/DeepSeek-V4.1-Flash", "text")

        openai_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
