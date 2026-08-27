"""Regression tests for OrcaRouter choices and prompt routing in the launcher."""

import ast
import unittest
from pathlib import Path


LAUNCH_PATH = Path(__file__).resolve().parents[1] / "funclip" / "launch.py"


class TestOrcaRouterLaunchIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(LAUNCH_PATH.read_text(encoding="utf-8"))

    def test_openai_compatible_route_handles_orcarouter_prefix(self):
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
        # The openai_call dispatch branch must also cover orcarouter/ models.
        dispatch_condition = next(
            node
            for node in ast.walk(llm_inference)
            if isinstance(node, ast.If) and isinstance(node.test, ast.BoolOp)
        )
        self.assertIn("orcarouter/", ast.unparse(dispatch_condition.test))
        self.assertEqual(ast.unparse(openai_call.args[2]), "user_content + '\\n' + srt_text")
        self.assertEqual(ast.unparse(openai_call.args[3]), "system_content")

    def test_support_prefix_list_includes_orcarouter(self):
        llm_inference = next(
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef) and node.name == "llm_inference"
        )
        assigned = [
            node
            for node in ast.walk(llm_inference)
            if isinstance(node, ast.Assign) and node.targets[0].id == "SUPPORT_LLM_PREFIX"
        ]
        self.assertEqual(len(assigned), 1)
        prefix_list = assigned[0].value
        self.assertIsInstance(prefix_list, ast.List)
        prefixes = {
            node.value
            for node in ast.walk(prefix_list)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertIn("orcarouter", prefixes)

    def test_dropdown_lists_orcarouter_gateway_models(self):
        string_literals = {
            node.value
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }

        self.assertIn("orcarouter/auto", string_literals)
        self.assertIn("orcarouter/fusion", string_literals)
        self.assertIn("orcarouter/fusion-flash", string_literals)
        self.assertIn("orcarouter/fusion-mini", string_literals)


if __name__ == "__main__":
    unittest.main()
