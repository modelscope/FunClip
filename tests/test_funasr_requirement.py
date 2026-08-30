from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_funasr_minimum_version_matches_current_model_paths():
    requirements = (ROOT / "requirements.txt").read_text()
    assert "funasr>=1.4.9" in requirements
    assert "funasr>=1.1.2" not in requirements
    assert "funasr>=1.3.26" not in requirements
    assert "funasr>=1.3.27" not in requirements
    assert "funasr>=1.3.28" not in requirements
    assert "funasr>=1.3.29" not in requirements


def test_readmes_explain_upgrade_for_existing_installs():
    for readme in ["README.md", "README_zh.md"]:
        text = (ROOT / readme).read_text()
        assert 'pip install -U "funasr>=1.4.9"' in text
        assert "funasr>=1.3.26" not in text
        assert "funasr>=1.3.27" not in text
        assert "funasr>=1.3.28" not in text
        assert "funasr>=1.3.29" not in text
        assert "sentence_info" in text
        assert "https://github.com/modelscope/FunASR/releases/tag/v1.4.9" in text


def test_readmes_document_moss_ownership_backends_and_timestamp_boundary():
    required = [
        "OpenMOSS/MOSS-Transcribe-Diarize",
        "OpenMOSS-Team/MOSS-Transcribe-Diarize",
        "--model moss",
        "--moss-backend vllm",
        "MOSS_API_KEY",
        "e8681d68e7042738ffca8ac8212bc8fcb1131ab8",
        "https://www.funasr.com/en/deploy/moss-transcribe-diarize.html",
    ]
    for readme in ["README.md", "README_zh.md"]:
        text = (ROOT / readme).read_text()
        for item in required:
            assert item in text
        assert "vad_model" in text
        assert "spk_model" in text
        assert "Paraformer" in text
        assert "--moss-backend sglang" not in text
        assert "--moss-backend hf" not in text


def test_readmes_route_edge_asr_users_to_gguf_runtime():
    required_links = [
        "https://www.funasr.com/llama-cpp.html",
        "https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-GGUF",
        "https://huggingface.co/FunAudioLLM/SenseVoiceSmall-GGUF",
    ]
    for readme in ["README.md", "README_zh.md"]:
        text = (ROOT / readme).read_text()
        for link in required_links:
            assert link in text


def test_english_readme_avoids_visible_typo_regressions():
    text = (ROOT / "README.md").read_text()
    assert "langage" not in text
    assert "open-sourced bu" not in text
    assert "supports recognize and clip" not in text
