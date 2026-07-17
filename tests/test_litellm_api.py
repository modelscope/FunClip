"""Tests for the LiteLLM provider module."""

import unittest
from unittest.mock import MagicMock, patch


def _mock_response(content="Test response"):
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = content
    return resp


def _empty_choices_response():
    resp = MagicMock()
    resp.choices = []
    return resp


def _null_content_response():
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = None
    return resp


class TestLiteLLMApi(unittest.TestCase):

    def test_basic_call(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("Summary result")):
            from funclip.llm.litellm_api import litellm_call
            result = litellm_call("key", "litellm/openai/gpt-4o-mini", "article text", "Summarize")
            self.assertEqual(result, "Summary result")
            call_kwargs = litellm.completion.call_args[1]
            self.assertEqual(call_kwargs["model"], "openai/gpt-4o-mini")

    def test_prefix_stripped(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("key", "litellm/anthropic/claude-sonnet-4-6", "text")
            self.assertEqual(litellm.completion.call_args[1]["model"], "anthropic/claude-sonnet-4-6")

    def test_no_prefix_passes_through(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("key", "openai/gpt-4o", "text")
            self.assertEqual(litellm.completion.call_args[1]["model"], "openai/gpt-4o")

    def test_drop_params_true(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("key", "openai/gpt-4o-mini", "text")
            self.assertTrue(litellm.completion.call_args[1]["drop_params"])

    def test_api_key_forwarded(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("sk-test-123", "openai/gpt-4o-mini", "text")
            self.assertEqual(litellm.completion.call_args[1]["api_key"], "sk-test-123")

    def test_api_key_omitted_when_empty(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("", "openai/gpt-4o-mini", "text")
            self.assertNotIn("api_key", litellm.completion.call_args[1])

    def test_system_content_included(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("key", "openai/gpt-4o-mini", "user text", "system prompt")
            messages = litellm.completion.call_args[1]["messages"]
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]["role"], "system")
            self.assertEqual(messages[0]["content"], "system prompt")

    def test_system_content_skipped_when_empty(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_mock_response("ok")):
            from funclip.llm.litellm_api import litellm_call
            litellm_call("key", "openai/gpt-4o-mini", "user text", "  ")
            messages = litellm.completion.call_args[1]["messages"]
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["role"], "user")

    def test_empty_choices_returns_empty(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_empty_choices_response()):
            from funclip.llm.litellm_api import litellm_call
            result = litellm_call("key", "openai/gpt-4o-mini", "text")
            self.assertEqual(result, "")

    def test_null_content_returns_empty(self):
        import litellm
        with patch.object(litellm, "completion", return_value=_null_content_response()):
            from funclip.llm.litellm_api import litellm_call
            result = litellm_call("key", "openai/gpt-4o-mini", "text")
            self.assertEqual(result, "")

    def test_auth_error_raises(self):
        import litellm
        with patch.object(litellm, "completion",
                          side_effect=litellm.AuthenticationError(message="Bad key", model="test", llm_provider="openai")):
            from funclip.llm.litellm_api import litellm_call
            with self.assertRaises(litellm.AuthenticationError):
                litellm_call("bad-key", "openai/gpt-4o-mini", "text")

    def test_rate_limit_raises(self):
        import litellm
        with patch.object(litellm, "completion",
                          side_effect=litellm.RateLimitError(message="Rate limited", model="test", llm_provider="openai")):
            from funclip.llm.litellm_api import litellm_call
            with self.assertRaises(litellm.RateLimitError):
                litellm_call("key", "openai/gpt-4o-mini", "text")

    def test_timeout_raises(self):
        import litellm
        with patch.object(litellm, "completion",
                          side_effect=litellm.Timeout(message="Timed out", model="test", llm_provider="openai")):
            from funclip.llm.litellm_api import litellm_call
            with self.assertRaises(litellm.Timeout):
                litellm_call("key", "openai/gpt-4o-mini", "text")

    def test_empty_model_after_strip_raises(self):
        from funclip.llm.litellm_api import litellm_call
        with self.assertRaises(ValueError):
            litellm_call("key", "litellm/", "text")


if __name__ == '__main__':
    unittest.main()
