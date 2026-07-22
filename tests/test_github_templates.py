from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_issue_templates_collect_funclip_repro_details():
    template_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
    required_files = [
        "bug_report.md",
        "feature_request.md",
        "config.yaml",
    ]

    for name in required_files:
        assert (template_dir / name).exists()

    bug_text = (template_dir / "bug_report.md").read_text()
    required_bug_fields = [
        "FunClip version or commit",
        "FunASR version",
        "Operating system",
        "Python version",
        "Audio or video input",
        "Expected behavior",
        "Actual behavior",
        "Logs or traceback",
    ]
    for field in required_bug_fields:
        assert field in bug_text


def test_pull_request_template_keeps_validation_visible():
    template = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
    assert template.exists()

    text = template.read_text()
    required = [
        "Summary",
        "Validation",
        "User impact",
        "Screenshots or clips",
    ]
    for marker in required:
        assert marker in text


def test_contributing_guide_documents_local_validation_path():
    guide = ROOT / "CONTRIBUTING.md"
    assert guide.exists()

    text = guide.read_text()
    required = [
        "pip install -r requirements.txt",
        "python3 -m pytest -q tests/test_github_templates.py tests/test_funasr_requirement.py tests/test_openai_api.py",
        "python3 -m py_compile funclip/launch.py funclip/videoclipper.py funclip/utils/subtitle_utils.py",
        "Audio or video input",
        "Screenshots or clips",
        "litellm",
    ]
    for marker in required:
        assert marker in text
