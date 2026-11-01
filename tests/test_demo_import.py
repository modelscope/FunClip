"""Optional media demos must not run while tools import or collect them."""

from pathlib import Path
import subprocess
import sys


def test_imagemagick_demo_import_is_side_effect_free(tmp_path):
    demo = Path(__file__).resolve().parents[1] / "funclip/test/imagemagick_test.py"
    code = """
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("funclip_imagemagick_demo", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(demo)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []
