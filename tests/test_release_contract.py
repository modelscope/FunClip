import hashlib
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def _git(repository, *args):
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _create_fixture_repository(repository):
    repository.mkdir()
    _git(repository, "init", "-b", "main")
    _git(repository, "config", "user.name", "FunClip Release Test")
    _git(repository, "config", "user.email", "release-test@example.com")

    fixture_files = {
        "VERSION": "2.1.0\n",
        "README.md": "# FunClip\n",
        "requirements.txt": "funasr>=1.3.29\n",
        "LICENSE": "MIT\n",
        "funclip/__init__.py": "\n",
    }
    for relative_path, content in fixture_files.items():
        path = repository / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(repository, "add", ".")
    _git(repository, "commit", "-m", "fixture")


def test_release_version_and_public_download_routes_are_in_sync():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert version == "2.1.0"
    assert VERSION_PATTERN.fullmatch(version)

    release_url = f"https://github.com/modelscope/FunClip/releases/tag/v{version}"
    for readme in ("README.md", "README_zh.md"):
        text = (ROOT / readme).read_text(encoding="utf-8")
        assert release_url in text
        assert f"FunClip-{version}.tar.gz" in text
        assert f"FunClip-{version}.zip" in text
        assert "SHA256SUMS" in text


def test_release_notes_define_installation_and_asset_boundaries():
    notes = (ROOT / "docs/releases/v2.1.0.md").read_text(encoding="utf-8")
    assert "funasr>=1.3.29" in notes
    assert "Fun-ASR-Nano" in notes
    assert "SenseVoice" in notes
    assert "TwelveLabs" in notes
    assert "FunClip-2.1.0.tar.gz" in notes
    assert "FunClip-2.1.0.zip" in notes
    assert "SHA256SUMS" in notes
    assert "model weights are not bundled" in notes


def test_tag_workflow_builds_and_publishes_all_release_assets():
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert 'tags: ["v*.*.*"]' in workflow
    assert "contents: write" in workflow
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in workflow
    assert "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in workflow
    assert "actions/checkout@v" not in workflow
    assert "actions/setup-python@v" not in workflow
    assert "pytest==8.3.5" in workflow
    assert "python scripts/build_release_assets.py" in workflow
    assert "python -m pytest -q tests/test_release_contract.py" in workflow
    assert "gh release view" in workflow
    assert "gh release create" in workflow
    assert "gh release edit" in workflow
    assert "gh release upload" in workflow
    assert "--clobber" in workflow
    assert "--json apiUrl,isDraft,isImmutable" in workflow
    assert ".apiUrl" in workflow
    assert ".isDraft" in workflow
    assert ".isImmutable" in workflow
    assert "releases/tags/" not in workflow
    assert "--draft" in workflow
    assert "--draft=false" in workflow
    assert "sha256:" in workflow
    assert "already published and verified" in workflow
    assert "--verify-tag" in workflow
    assert "docs/releases/${GITHUB_REF_NAME}.md" in workflow
    assert "dist/FunClip-*.tar.gz" in workflow
    assert "dist/FunClip-*.zip" in workflow
    assert "dist/SHA256SUMS" in workflow


def test_release_builder_creates_reproducible_scoped_archives(tmp_path):
    repository = tmp_path / "fixture"
    _create_fixture_repository(repository)

    outputs = []
    for directory_name in ("dist-one", "dist-two"):
        if outputs:
            time.sleep(2)
        output_dir = tmp_path / directory_name
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/build_release_assets.py"),
                "--repository",
                str(repository),
                "--ref",
                "HEAD",
                "--output-dir",
                str(output_dir),
            ],
            check=True,
        )
        outputs.append(output_dir)

    expected_names = {
        "FunClip-2.1.0.tar.gz",
        "FunClip-2.1.0.zip",
        "SHA256SUMS",
    }
    assert {path.name for path in outputs[0].iterdir()} == expected_names

    for name in expected_names:
        assert (outputs[0] / name).read_bytes() == (outputs[1] / name).read_bytes()

    tar_path = outputs[0] / "FunClip-2.1.0.tar.gz"
    zip_path = outputs[0] / "FunClip-2.1.0.zip"
    with tarfile.open(tar_path, "r:gz") as archive:
        tar_members = {
            member.name for member in archive.getmembers() if member.isfile()
        }
    with zipfile.ZipFile(zip_path) as archive:
        zip_members = {name for name in archive.namelist() if not name.endswith("/")}

    required_members = {
        "FunClip-2.1.0/VERSION",
        "FunClip-2.1.0/README.md",
        "FunClip-2.1.0/requirements.txt",
        "FunClip-2.1.0/LICENSE",
    }
    assert required_members <= tar_members
    assert tar_members == zip_members
    assert all(member.startswith("FunClip-2.1.0/") for member in tar_members)

    checksum_lines = (outputs[0] / "SHA256SUMS").read_text().splitlines()
    assert checksum_lines == [
        f"{_sha256(tar_path)}  {tar_path.name}",
        f"{_sha256(zip_path)}  {zip_path.name}",
    ]


def test_release_builder_rejects_non_commit_refs(tmp_path):
    repository = tmp_path / "fixture"
    repository.mkdir()
    _git(repository, "init", "-b", "main")
    _git(repository, "config", "user.name", "FunClip Release Test")
    _git(repository, "config", "user.email", "release-test@example.com")
    for relative_path in ("VERSION", "README.md", "requirements.txt", "LICENSE"):
        (repository / relative_path).write_text("2.1.0\n", encoding="utf-8")
    _git(repository, "add", ".")
    tree_ref = _git(repository, "write-tree").stdout.strip()

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_release_assets.py"),
            "--repository",
            str(repository),
            "--ref",
            tree_ref,
            "--output-dir",
            str(tmp_path / "dist"),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "release ref must resolve to a commit" in result.stderr


def test_release_builder_supports_cross_filesystem_outputs(tmp_path):
    cross_filesystem_root = Path("/dev/shm")
    if not cross_filesystem_root.is_dir() or (
        os.stat(tmp_path).st_dev == os.stat(cross_filesystem_root).st_dev
    ):
        pytest.skip("a second writable filesystem is not available")

    repository = tmp_path / "fixture"
    _create_fixture_repository(repository)
    with tempfile.TemporaryDirectory(
        prefix="funclip-release-test-", dir=cross_filesystem_root
    ) as temporary:
        output_dir = Path(temporary) / "dist"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/build_release_assets.py"),
                "--repository",
                str(repository),
                "--ref",
                "HEAD",
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            check=False,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        assert (output_dir / "FunClip-2.1.0.tar.gz").is_file()
        assert (output_dir / "FunClip-2.1.0.zip").is_file()
        assert (output_dir / "SHA256SUMS").is_file()
