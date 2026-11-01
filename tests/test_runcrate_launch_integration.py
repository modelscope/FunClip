"""Regression tests for Runcrate choices and prompt routing in the launcher."""

import ast
import unittest
from pathlib import Path


LAUNCH_PATH = Path(__file__).resolve().parents[1] / "funclip" / "launch.py"


class TestRuncrateLaunchIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(LAUNCH_PATH.read_text(encoding="utf-8"))
        cls.llm_inference = next(
            node
            for node in ast.walk(cls.tree)
            if isinstance(node, ast.FunctionDef) and node.name == "llm_inference"
        )

    def test_openai_compatible_route_handles_runcrate_prefix(self):
        # The branch that returns openai_call(...) must also cover runcrate/ models,
        # and pass the transcript as the user message and the system prompt as the system role.
        dispatch = next(
            node
            for node in ast.walk(self.llm_inference)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.BoolOp)
            and any(
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "openai_call"
                for stmt in node.body
                for call in ast.walk(stmt)
            )
        )
        self.assertIn("model.startswith('runcrate/')", ast.unparse(dispatch.test))
        openai_call = next(
            call
            for stmt in dispatch.body
            for call in ast.walk(stmt)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Name)
            and call.func.id == "openai_call"
        )
        self.assertEqual(ast.unparse(openai_call.args[0]), "apikey")
        self.assertEqual(ast.unparse(openai_call.args[1]), "model")
        self.assertEqual(ast.unparse(openai_call.args[2]), "user_content + '\\n' + srt_text")
        self.assertEqual(ast.unparse(openai_call.args[3]), "system_content")

    def test_support_prefix_list_includes_runcrate(self):
        assigned = [
            node
            for node in ast.walk(self.llm_inference)
            if isinstance(node, ast.Assign) and node.targets[0].id == "SUPPORT_LLM_PREFIX"
        ]
        self.assertEqual(len(assigned), 1)
        prefixes = {
            node.value
            for node in ast.walk(assigned[0].value)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertIn("runcrate", prefixes)

    def test_dropdown_lists_vendor_qualified_runcrate_models(self):
        string_literals = {
            node.value
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }

        # Runcrate ids keep their vendor after the runcrate/ prefix is removed.
        self.assertIn("runcrate/deepseek-ai/DeepSeek-V4.1-Flash", string_literals)
        self.assertIn("runcrate/openai/gpt-oss-120b", string_literals)


if __name__ == "__main__":
    unittest.main()
