from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DISCUSSIONS_URL = "https://github.com/modelscope/FunClip/discussions"


@pytest.mark.parametrize(
    ("readme", "start", "end"),
    (
        ("README.md", '<a name="Community"></a>', "## Ecosystem"),
        ("README_zh.md", '<a name="社区交流"></a>', "## 通过FunASR"),
    ),
)
def test_community_section_has_stable_discussions_fallback(
    readme: str, start: str, end: str
) -> None:
    text = (ROOT / readme).read_text(encoding="utf-8")
    section = text.split(start, 1)[1].split(end, 1)[0]

    assert section.count(f"[GitHub Discussions]({DISCUSSIONS_URL})") == 1
    assert "docs/images/dingding.png" in section
    assert "docs/images/wechat.png" in section
