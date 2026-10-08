"""API Route client and executable launcher routing regressions."""

import ast
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from funclip.llm.openai_api import API_ROUTE_API_BASE, openai_call


class TestAPIRoute(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = MagicMock()
        self.client.chat.completions.create.return_value.choices[0].message.content = "clip plan"
        self.factory = patch("funclip.llm.openai_api.OpenAI", return_value=self.client)
        self.openai = self.factory.start()
        self.addCleanup(self.factory.stop)

    def test_exact_model_id_and_prompts_reach_gateway(self):
        for model in ("gpt-6.1-sol", "custom/model-id"):
            with self.subTest(model=model):
                self.assertEqual(openai_call("test-key", "api-route/" + model, "subtitles", "system"), "clip plan")
                self.openai.assert_called_with(api_key="test-key", base_url=API_ROUTE_API_BASE)
                self.client.chat.completions.create.assert_called_with(
                    model=model,
                    messages=[{"role": "system", "content": "system"}, {"role": "user", "content": "subtitles"}],
                )

    def test_trimmed_environment_key(self):
        os.environ["API_ROUTE_API_KEY"] = " env-key "
        openai_call("", "api-route/gpt-6.1-sol", "subtitles")
        self.openai.assert_called_once_with(api_key="env-key", base_url=API_ROUTE_API_BASE)

    def test_explicit_key_takes_precedence(self):
        os.environ["API_ROUTE_API_KEY"] = "env-key"
        openai_call("explicit-key", "api-route/gpt-6.1-sol", "subtitles")
        self.openai.assert_called_once_with(api_key="explicit-key", base_url=API_ROUTE_API_BASE)

    def test_empty_model_fails_before_client_creation(self):
        with self.assertRaisesRegex(ValueError, "Model name is empty"):
            openai_call("test-key", "api-route/", "subtitles")
        self.openai.assert_not_called()

    def test_missing_key_does_not_use_openai_key(self):
        os.environ["OPENAI_API_KEY"] = "openai-key"
        with self.assertRaisesRegex(ValueError, "API_ROUTE_API_KEY"):
            openai_call("", "api-route/gpt-6.1-sol", "subtitles")
        self.openai.assert_not_called()

    def test_endpoint_override_and_empty_fallback(self):
        for value, expected in ((" https://example.com/v1 ", "https://example.com/v1"), (" ", API_ROUTE_API_BASE)):
            with self.subTest(value=value):
                os.environ["API_ROUTE_API_BASE"] = value
                openai_call("test-key", "api-route/gpt-6.1-sol", "subtitles")
                self.openai.assert_called_with(api_key="test-key", base_url=expected)

    def test_launcher_preserves_subtitles_and_system_prompt(self):
        path = Path(__file__).resolve().parents[1] / "funclip" / "launch.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        function = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "llm_inference")
        namespace = {"openai_call": openai_call}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), namespace)
        srt = "1\n00:00:00,000 --> 00:00:01,000\nA short clip."
        result = namespace["llm_inference"]("system", "find highlights", srt, "api-route/gpt-6.1-sol", "test-key")
        self.assertEqual(result, "clip plan")
        self.client.chat.completions.create.assert_called_once_with(
            model="gpt-6.1-sol",
            messages=[{"role": "system", "content": "system"}, {"role": "user", "content": "find highlights\n" + srt}],
        )

    def test_model_dropdown_has_api_route_example(self):
        path = Path(__file__).resolve().parents[1] / "funclip" / "launch.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        dropdown = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "llm_model" for target in node.targets))
        choices = next(keyword.value for keyword in dropdown.value.keywords if keyword.arg == "choices")
        self.assertIn("api-route/gpt-6.1-sol", ast.literal_eval(choices))


if __name__ == "__main__":
    unittest.main()
