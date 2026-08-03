"""Regression tests for the supported Gradio/Starlette launch contract."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCH_PATH = ROOT / "funclip" / "launch.py"


def test_gradio4_excludes_breaking_starlette_releases():
    requirements = {
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "gradio>=4.31.3,<5.0" in requirements
    assert "starlette<1.0" in requirements


def test_supported_gradio_stack_renders_index():
    import gradio
    from starlette.testclient import TestClient

    with gradio.Blocks() as demo:
        gradio.Markdown("FunClip runtime smoke test")

    app = gradio.routes.App.create_app(demo)
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "gradio_config" in response.text


def test_local_launch_keeps_gradio_frontend_probe_enabled():
    from funclip.launch_config import build_launch_kwargs

    assert build_launch_kwargs(share=False, port=7860, listen=False) == {
        "share": False,
        "server_port": 7860,
        "server_name": "127.0.0.1",
    }


def test_explicit_listen_skips_only_the_local_frontend_probe():
    from funclip.launch_config import build_launch_kwargs

    assert build_launch_kwargs(share=False, port=12235, listen=True) == {
        "share": False,
        "server_port": 12235,
        "server_name": "0.0.0.0",
        "inbrowser": False,
        "_frontend": False,
    }


def test_explicit_share_choice_is_preserved():
    from funclip.launch_config import build_launch_kwargs

    kwargs = build_launch_kwargs(share=True, port=7860, listen=True)

    assert kwargs["share"] is True


def test_launcher_does_not_patch_dependencies_or_retry_with_public_share():
    tree = ast.parse(LAUNCH_PATH.read_text(encoding="utf-8"))
    launch_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "launch"
    ]
    patched_attributes = [
        target.attr
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(target, ast.Attribute)
        and target.attr in {"TemplateResponse", "cache", "cache_size"}
    ]

    assert len(launch_calls) == 1
    assert patched_attributes == []
