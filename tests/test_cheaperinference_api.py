"""Tests for Cheaper Inference routing through the OpenAI-compatible client."""

import os
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import (
    CHEAPER_INFERENCE_API_BASE,
    openai_call,
)


def _mock_completion(content="ok"):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestCheaperInferenceRouting(unittest.TestCase):
    def test_cheaperinference_prefix_uses_gateway_base_url(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion("clip plan")

        with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
            result = openai_call(
                "ci-key",
                "cheaperinference/gpt-5.4-mini",
                "subtitle text",
                "find highlights",
            )

        self.assertEqual(result, "clip plan")
        openai_cls.assert_called_once_with(
            api_key="ci-key",
            base_url=CHEAPER_INFERENCE_API_BASE,
        )
        # Cheaper Inference model IDs are bare: the prefix is stripped.
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "gpt-5.4-mini")

    def test_cheaperinference_api_key_falls_back_to_env(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"CHEAPER_INFERENCE_API_KEY": "env-ci-key"}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("", "cheaperinference/gpt-5.4-mini", "text")

        openai_cls.assert_called_once_with(
            api_key="env-ci-key",
            base_url=CHEAPER_INFERENCE_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "gpt-5.4-mini")

    def test_cheaperinference_api_base_env_overrides(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(
            os.environ,
            {"CHEAPER_INFERENCE_API_BASE": "https://gateway.example.com/v1"},
            clear=False,
        ):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("ci-key", "cheaperinference/claude-sonnet-5", "text")

        openai_cls.assert_called_once_with(
            api_key="ci-key",
            base_url="https://gateway.example.com/v1",
        )

    def test_empty_cheaperinference_model_raises(self):
        with self.assertRaises(ValueError):
            openai_call("key", "cheaperinference/", "text")

    def test_missing_cheaperinference_key_does_not_fall_back_to_openai_key(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-only-key"},
            clear=True,
        ):
            with patch("funclip.llm.openai_api.OpenAI") as openai_cls:
                with self.assertRaisesRegex(ValueError, "CHEAPER_INFERENCE_API_KEY"):
                    openai_call("", "cheaperinference/gpt-5.4-mini", "text")

        openai_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
