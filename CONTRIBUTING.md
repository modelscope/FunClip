# Contributing to FunClip

Thanks for helping improve FunClip. The project is maintained as part of the FunASR ecosystem, so useful reports and focused pull requests are very welcome.

## Before opening an issue

For bugs, include enough detail for maintainers to reproduce the problem without a follow-up round:

- FunClip version or commit
- FunASR version
- Operating system and Python version
- Installation method
- Audio or video input type, duration, language, and a public or minimal sample when possible
- ASR model, hotwords, and LLM provider/model when relevant
- Expected behavior and actual behavior
- Logs or traceback
- Screenshots or clips for UI, subtitle, timestamp, or clipping-result issues

For broad ASR, deployment, or model-selection questions, the FunASR docs and discussions may be the better first stop:

- https://modelscope.github.io/FunASR/
- https://github.com/modelscope/FunASR/discussions

## Local setup

```bash
git clone https://github.com/modelscope/FunClip.git
cd FunClip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

FunClip's current Fun-ASR-Nano, SenseVoice, and subtitle compatibility paths require `funasr>=1.3.26`.

## Validation

Run the focused checks that match your change. For documentation, issue templates, package metadata, and provider-routing changes, start with:

```bash
python3 -m pytest -q tests/test_github_templates.py tests/test_funasr_requirement.py tests/test_openai_api.py
python3 -m py_compile funclip/launch.py funclip/videoclipper.py funclip/utils/subtitle_utils.py
git diff --check
```

Some tests require optional provider packages or live credentials. In particular, `tests/test_litellm_api.py` requires the optional `litellm` package. If you change the LiteLLM provider path, install that dependency and run the LiteLLM tests too:

```bash
pip install 'litellm>=1.83.0'
python3 -m pytest -q tests/test_litellm_api.py
```

If you change clipping behavior, ASR model selection, subtitle generation, or the Gradio UI, also run or manually verify the affected workflow with a short audio/video sample and include the command, model, input media shape, and result in the pull request.

## Pull request checklist

- Keep the change focused on one bug, feature, or docs cleanup.
- Explain the User impact in the PR body.
- Include the Validation commands you ran and any optional dependencies you skipped.
- Add Screenshots or clips for UI or clipping-result changes.
- Update README or issue templates when behavior visible to users changes.
