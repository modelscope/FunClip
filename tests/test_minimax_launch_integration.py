"""Regression tests for MiniMax choices and prompt routing in the launcher."""

import ast
import unittest
from pathlib import Path


LAUNCH_PATH = Path(__file__).resolve().parents[1] / "funclip" / "launch.py"


class TestMiniMaxLaunchIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(LAUNCH_PATH.read_text(encoding="utf-8"))

    def test_openai_compatible_route_preserves_prompt_roles(self):
        llm_inference = next(
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef) and node.name == "llm_inference"
        )
        openai_call = next(
            node
            for node in ast.walk(llm_inference)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "openai_call"
        )

        self.assertEqual(ast.unparse(openai_call.args[2]), "user_content + '\\n' + srt_text")
        self.assertEqual(ast.unparse(openai_call.args[3]), "system_content")

        g4f_call = next(
            node
            for node in ast.walk(llm_inference)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "g4f_openai_call"
        )
        self.assertEqual(ast.unparse(g4f_call.args[1]), "user_content + '\\n' + srt_text")
        self.assertEqual(ast.unparse(g4f_call.args[2]), "system_content")

    def test_dropdown_only_lists_documented_minimax_models(self):
        dropdown = next(
            node.value
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "llm_model"
                    for target in node.targets)
        )
        options = {keyword.arg: ast.literal_eval(keyword.value)
                   for keyword in dropdown.keywords}
        self.assertEqual(
            [model for model in options["choices"] if model.startswith("minimax/")],
            ["minimax/MiniMax-M3.1-Flash", "minimax/MiniMax-M3"],
        )
        self.assertTrue(options["allow_custom_value"])
        self.assertEqual(options["value"], "deepseek-chat")


if __name__ == "__main__":
    unittest.main()
