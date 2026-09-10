from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("filename", ["README.md", "README_zh.md", "CONTRIBUTING.md"])
def test_installation_entries_use_one_python_environment(filename):
    text = (ROOT / filename).read_text()
    assert "-m venv .venv" in text
    assert "python -m pip install -r requirements.txt" in text
    assert "python -m pip check" in text
    assert "docs/installation.md" in text


def test_contributor_minimum_matches_application_requirements():
    requirement = next(
        line for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.startswith("funasr>=")
    )
    assert requirement in (ROOT / "CONTRIBUTING.md").read_text()


def test_troubleshooting_keeps_tls_and_runtime_boundaries():
    guide = (ROOT / "docs/installation.md").read_text()
    assert "CERTIFICATE_VERIFY_FAILED" in guide
    assert "sys.executable" in guide
    assert "python -m pip --version" in guide
    assert "python -m pip config debug" in guide
    assert "from funasr import AutoModel" in guide
    assert "https://pip.pypa.io/en/stable/topics/https-certificates/" in guide
    assert "https://www.funasr.com/docs/native-transformers.html" in guide
    assert "https://www.funasr.com/en/docs/native-transformers.html" in guide
    assert "Transformers 4.x" in guide and "Transformers 5.x" in guide
    for block in guide.split("```")[1::2]:
        if block.startswith(("bash\n", "shell\n", "powershell\n")):
            assert "--trusted-host" not in block
            assert "verify=False" not in block
            assert "PIP_TRUSTED_HOST=" not in block
