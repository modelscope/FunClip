"""Tests for Opper routing through the OpenAI-compatible client."""

import os
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import (
    OPPER_API_BASE,
    openai_call,
)


def _mock_completion(content="ok"):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestOpperRouting(unittest.TestCase):
    def test_opper_prefix_uses_gateway_base_url(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion("clip plan")

        with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
            result = openai_call(
                "opper-key",
                "opper/gpt-5.4-mini",
                "subtitle text",
                "find highlights",
            )

        self.assertEqual(result, "clip plan")
        openai_cls.assert_called_once_with(
            api_key="opper-key",
            base_url=OPPER_API_BASE,
        )
        # Only the opper/ prefix is stripped; the pool name is sent as is.
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "gpt-5.4-mini")

    def test_opper_api_key_falls_back_to_env(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"OPPER_API_KEY": "env-opper-key"}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("", "opper/gpt-5.4-mini", "text")

        openai_cls.assert_called_once_with(
            api_key="env-opper-key",
            base_url=OPPER_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "gpt-5.4-mini")

    def test_opper_provider_route_keeps_inner_prefix(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch("funclip.llm.openai_api.OpenAI", return_value=client):
            openai_call("opper-key", "opper/anthropic/claude-sonnet-4-6", "text")

        # A provider/model id pins one route and must reach the gateway intact.
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "anthropic/claude-sonnet-4-6")

    def test_opper_api_base_env_overrides(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(
            os.environ,
            {"OPPER_API_BASE": "https://gateway.example.com/v1"},
            clear=False,
        ):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("opper-key", "opper/claude-sonnet-4-6", "text")

        openai_cls.assert_called_once_with(
            api_key="opper-key",
            base_url="https://gateway.example.com/v1",
        )

    def test_empty_opper_model_raises(self):
        with self.assertRaises(ValueError):
            openai_call("key", "opper/", "text")

    def test_missing_opper_key_does_not_fall_back_to_openai_key(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-only-key"},
            clear=True,
        ):
            with patch("funclip.llm.openai_api.OpenAI") as openai_cls:
                with self.assertRaisesRegex(ValueError, "OPPER_API_KEY"):
                    openai_call("", "opper/gpt-5.4-mini", "text")

        openai_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
