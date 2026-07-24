import argparse
import hashlib
import os
import re
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REQUIRED_FILES = {"VERSION", "README.md", "requirements.txt", "LICENSE"}


def git_output(repository, *args):
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_commit(repository, ref):
    try:
        return git_output(
            repository, "rev-parse", "--verify", f"{ref}^{{commit}}"
        ).strip()
    except subprocess.CalledProcessError as error:
        raise RuntimeError("release ref must resolve to a commit") from error


def archive_members(path):
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            return {name for name in archive.namelist() if not name.endswith("/")}
    with tarfile.open(path, "r:gz") as archive:
        return {member.name for member in archive.getmembers() if member.isfile()}


def validate_members(members, prefix):
    if not members or any(not member.startswith(prefix) for member in members):
        raise RuntimeError(f"release archive contains a path outside {prefix}")

    relative_members = {member.removeprefix(prefix) for member in members}
    missing = REQUIRED_FILES - relative_members
    if missing:
        raise RuntimeError("release archive is missing: " + ", ".join(sorted(missing)))

    unsafe = [
        member
        for member in relative_members
        if ".git" in Path(member).parts
        or "__pycache__" in Path(member).parts
        or member.endswith((".pyc", ".pyo"))
    ]
    if unsafe:
        raise RuntimeError(
            "release archive contains generated metadata: " + ", ".join(unsafe)
        )


def build_release_assets(repository, ref, output_dir):
    repository = repository.resolve()
    output_dir = output_dir.resolve()
    commit = resolve_commit(repository, ref)
    version = git_output(repository, "show", f"{commit}:VERSION").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise RuntimeError(f"VERSION must be semantic x.y.z, got {version!r}")

    prefix = f"FunClip-{version}/"
    archive_names = [f"FunClip-{version}.tar.gz", f"FunClip-{version}.zip"]
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".funclip-release-", dir=output_dir
    ) as temporary:
        temporary_dir = Path(temporary)
        temporary_archives = []
        for archive_name in archive_names:
            archive_path = temporary_dir / archive_name
            archive_format = "zip" if archive_name.endswith(".zip") else "tar.gz"
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "archive",
                    f"--format={archive_format}",
                    f"--prefix={prefix}",
                    f"--output={archive_path}",
                    commit,
                ],
                check=True,
            )
            validate_members(archive_members(archive_path), prefix)
            temporary_archives.append(archive_path)

        first_members = archive_members(temporary_archives[0])
        if archive_members(temporary_archives[1]) != first_members:
            raise RuntimeError("tar.gz and zip archives contain different files")

        checksum_path = temporary_dir / "SHA256SUMS"
        checksum_path.write_text(
            "".join(
                f"{sha256(archive_path)}  {archive_path.name}\n"
                for archive_path in temporary_archives
            ),
            encoding="utf-8",
        )

        for path in [*temporary_archives, checksum_path]:
            os.replace(path, output_dir / path.name)

    return [output_dir / name for name in [*archive_names, "SHA256SUMS"]]


def main():
    parser = argparse.ArgumentParser(
        description="Build versioned FunClip release archives"
    )
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()

    for path in build_release_assets(args.repository, args.ref, args.output_dir):
        print(f"{sha256(path)}  {path.name}")


if __name__ == "__main__":
    main()
