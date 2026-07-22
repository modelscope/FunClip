from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_funasr_minimum_version_matches_current_model_paths():
    requirements = (ROOT / "requirements.txt").read_text()
    assert "funasr>=1.3.23" in requirements
    assert "funasr>=1.1.2" not in requirements


def test_readmes_explain_upgrade_for_existing_installs():
    for readme in ["README.md", "README_zh.md"]:
        text = (ROOT / readme).read_text()
        assert 'pip install -U "funasr>=1.3.23"' in text


def test_english_readme_avoids_visible_typo_regressions():
    text = (ROOT / "README.md").read_text()
    assert "langage" not in text
    assert "open-sourced bu" not in text
    assert "supports recognize and clip" not in text
