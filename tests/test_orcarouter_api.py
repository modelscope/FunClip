"""Tests for OrcaRouter routing through the OpenAI-compatible client."""

import os
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import (
    ORCAROUTER_API_BASE,
    openai_call,
)


def _mock_completion(content="ok"):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = content
    return completion


class TestOrcaRouterRouting(unittest.TestCase):
    def test_orcarouter_prefix_uses_gateway_base_url(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion("clip plan")

        with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
            result = openai_call(
                "orca-key",
                "orcarouter/auto",
                "subtitle text",
                "find highlights",
            )

        self.assertEqual(result, "clip plan")
        openai_cls.assert_called_once_with(
            api_key="orca-key",
            base_url=ORCAROUTER_API_BASE,
        )
        # OrcaRouter is a multi-provider gateway: the model ID must keep the
        # `orcarouter/` prefix so the router knows which namespace to route to.
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "orcarouter/auto")

    def test_orcarouter_api_key_falls_back_to_env(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(os.environ, {"ORCAROUTER_API_KEY": "env-orca-key"}, clear=False):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("", "orcarouter/auto", "text")

        openai_cls.assert_called_once_with(
            api_key="env-orca-key",
            base_url=ORCAROUTER_API_BASE,
        )
        call_kwargs = client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "orcarouter/auto")

    def test_orcarouter_api_base_env_overrides(self):
        client = MagicMock()
        client.chat.completions.create.return_value = _mock_completion()

        with patch.dict(
            os.environ,
            {"ORCAROUTER_API_BASE": "https://gateway.example.com/v1"},
            clear=False,
        ):
            with patch("funclip.llm.openai_api.OpenAI", return_value=client) as openai_cls:
                openai_call("orca-key", "orcarouter/fusion", "text")

        openai_cls.assert_called_once_with(
            api_key="orca-key",
            base_url="https://gateway.example.com/v1",
        )

    def test_empty_orcarouter_model_raises(self):
        with self.assertRaises(ValueError):
            openai_call("key", "orcarouter/", "text")

    def test_missing_orcarouter_key_does_not_fall_back_to_openai_key(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-only-key"},
            clear=True,
        ):
            with patch("funclip.llm.openai_api.OpenAI") as openai_cls:
                with self.assertRaisesRegex(ValueError, "ORCAROUTER_API_KEY"):
                    openai_call("", "orcarouter/auto", "text")

        openai_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
