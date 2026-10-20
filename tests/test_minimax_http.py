"""Exercise the launcher dispatcher through the real SDK's HTTP boundary."""

import ast
import json
from pathlib import Path

import httpx
import pytest
from openai import OpenAI

from funclip.llm import openai_api


LAUNCH_PATH = Path(__file__).resolve().parents[1] / "funclip" / "launch.py"


@pytest.fixture
def launcher():
    tree = ast.parse(LAUNCH_PATH.read_text(encoding="utf-8"))
    dispatcher = next(node for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "llm_inference")
    dropdown = next(node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "llm_model"
                            for target in node.targets))
    options = {keyword.arg: ast.literal_eval(keyword.value)
               for keyword in dropdown.keywords}
    # As in the CLI parser tests, execute the actual callback without loading ASR.
    namespace = {"openai_call": openai_api.openai_call}
    exec(compile(ast.Module(body=[dispatcher], type_ignores=[]),
                 str(LAUNCH_PATH), "exec"), namespace)
    return namespace["llm_inference"], options


@pytest.fixture
def requests(monkeypatch):
    captured = []
    clients = []

    def respond(request):
        captured.append(request)
        return httpx.Response(200, json={
            "id": "offline-completion", "object": "chat.completion", "created": 0,
            "model": json.loads(request.content)["model"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": "clip plan"}}],
        })

    def client_factory(**kwargs):
        client = OpenAI(**kwargs, max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(respond)))
        clients.append(client)
        return client

    monkeypatch.setattr(openai_api, "OpenAI", client_factory)
    monkeypatch.delenv("MINIMAX_API_BASE", raising=False)
    monkeypatch.setenv("MINIMAX_API_KEY", "offline-env-key")
    yield captured
    for client in clients:
        client.close()


@pytest.mark.parametrize("base", [None, "  ", "https://api.minimaxi.com/v1",
                                  "https://custom.example/v1"])
@pytest.mark.parametrize("model", [None, "MiniMax-M3", "MiniMax-M2.7",
                                   "MiniMax-M2.7-highspeed", "custom/saved-model"])
@pytest.mark.parametrize("apikey", ["", "offline-explicit-key"])
def test_launcher_serializes_selected_and_custom_models(launcher, requests, monkeypatch,
                                                        base, model, apikey):
    dispatch, options = launcher
    if base is not None:
        monkeypatch.setenv("MINIMAX_API_BASE", base)
    if model is None:
        selected = next(choice for choice in options["choices"]
                        if choice.startswith("minimax/"))
        assert selected == "minimax/MiniMax-M3.1-Flash"
        model = "MiniMax-M3.1-Flash"
    else:
        selected = "minimax/" + model
    assert dispatch("find highlights", "analyze subtitles", "00:00 sample",
                    selected, apikey) == "clip plan"
    assert len(requests) == 1
    request = requests[0]
    expected_base = (base or "").strip() or "https://api.minimax.io/v1"
    assert str(request.url) == expected_base + "/chat/completions"
    assert request.headers["authorization"] == "Bearer " + (apikey or "offline-env-key")
    # Exact payload also guards against unsupported thinking/effort/tier fields.
    assert json.loads(request.content) == {
        "model": model,
        "messages": [{"role": "system", "content": "find highlights"},
                     {"role": "user", "content": "analyze subtitles\n00:00 sample"}],
    }


def test_dropdown_accepts_current_and_explicit_legacy_values(launcher):
    import gradio
    from starlette.testclient import TestClient

    _, options = launcher
    with gradio.Blocks() as demo:
        dropdown = gradio.Dropdown(**options)
    assert dropdown.value == options["value"]
    for model in ("MiniMax-M3.1-Flash", "MiniMax-M3", "MiniMax-M2.7",
                  "MiniMax-M2.7-highspeed", "custom/saved-model"):
        selected = "minimax/" + model
        assert dropdown.preprocess(selected) == selected
    response = TestClient(gradio.routes.App.create_app(demo)).get("/")
    assert response.status_code == 200
    assert "minimax/MiniMax-M3.1-Flash" in response.text


def test_existing_default_route_is_preserved(launcher, requests):
    dispatch, options = launcher
    assert dispatch("system", "user", "subtitle", options["value"],
                    "offline-explicit-key") == "clip plan"
    assert str(requests[0].url) == "https://api.deepseek.com/chat/completions"
    assert json.loads(requests[0].content)["model"] == options["value"]


def test_explicit_content_parts_are_preserved(requests):
    content = [{"type": "text", "text": "describe the frame"},
               {"type": "image_url", "image_url": {"url": "https://example.com/frame.png"}}]
    assert openai_api.openai_call("offline-explicit-key", "minimax/MiniMax-M3",
                                 content) == "clip plan"
    assert json.loads(requests[0].content) == {
        "model": "MiniMax-M3", "messages": [{"role": "user", "content": content}],
    }
