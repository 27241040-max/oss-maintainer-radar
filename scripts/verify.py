from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    steps = [
        ("unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], None),
        ("example JSON", [sys.executable, "-m", "json.tool", "examples/sample_github_payload.json"], subprocess.DEVNULL),
        ("new project JSON", [sys.executable, "-m", "json.tool", "examples/new_project_payload.json"], subprocess.DEVNULL),
        ("evidence JSON", [sys.executable, "-m", "json.tool", "examples/evidence.json"], subprocess.DEVNULL),
        ("applicant JSON", [sys.executable, "-m", "json.tool", "examples/applicant.example.json"], subprocess.DEVNULL),
        (
            "fixture audit",
            [
                sys.executable,
                "-m",
                "oss_maintainer_radar.cli",
                "audit",
                "--fixture",
                "examples/sample_github_payload.json",
            ],
            subprocess.DEVNULL,
        ),
        (
            "form fields",
            [
                sys.executable,
                "-m",
                "oss_maintainer_radar.cli",
                "form-fields",
                "--fixture",
                "examples/sample_github_payload.json",
                "--evidence",
                "examples/evidence.json",
                "--applicant",
                "examples/applicant.example.json",
                "--role",
                "primary",
            ],
            subprocess.DEVNULL,
        ),
    ]

    for label, command, stdout in steps:
        run(label, command, stdout=stdout, pythonpath=True)

    with tempfile.TemporaryDirectory(prefix="oss-radar-verify-") as tmp:
        tmp_path = Path(tmp)
        build_env = tmp_path / "build-env"
        wheel_env = tmp_path / "wheel-env"
        dist_dir = tmp_path / "dist"

        run("create build env", [sys.executable, "-m", "venv", str(build_env)])
        build_python = build_env / "bin" / "python"
        run("install build tool", [str(build_python), "-m", "pip", "install", "build>=1.2"], stdout=subprocess.DEVNULL)
        run("build package", [str(build_python), "-m", "build", "--outdir", str(dist_dir)])

        wheel = one(dist_dir.glob("oss_maintainer_radar-*.whl"))
        source = one(dist_dir.glob("oss_maintainer_radar-*.tar.gz"))
        inspect_sdist(source)

        run("create wheel env", [sys.executable, "-m", "venv", str(wheel_env)])
        wheel_python = wheel_env / "bin" / "python"
        run("install wheel", [str(wheel_python), "-m", "pip", "install", str(wheel)], stdout=subprocess.DEVNULL)
        wheel_cli = venv_script(wheel_python, "oss-radar")
        run("wheel CLI help", [str(wheel_cli), "--help"], stdout=subprocess.DEVNULL)

    print("verify: all checks passed")
    return 0


def run(label: str, command: list[str], *, stdout=None, pythonpath: bool = False) -> None:
    print(f"verify: {label}")
    env = {**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
    if pythonpath:
        env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(command, cwd=ROOT, env=env, stdout=stdout, check=True)


def one(paths) -> Path:
    items = list(paths)
    if len(items) != 1:
        raise RuntimeError(f"expected exactly one artifact, found {len(items)}")
    return items[0]


def inspect_sdist(source: Path) -> None:
    shutil.unpack_archive(str(source), str(source.parent / "sdist"))
    files = {path.relative_to(source.parent / "sdist").as_posix() for path in (source.parent / "sdist").rglob("*")}
    required_suffixes = [
        "README.md",
        "docs/package-release.md",
        "examples/evidence.json",
        "examples/applicant.example.json",
        "tests/test_cli.py",
    ]
    missing = [suffix for suffix in required_suffixes if not any(item.endswith(suffix) for item in files)]
    if missing:
        raise RuntimeError(f"source distribution is missing: {', '.join(missing)}")


def venv_script(python_executable: Path, script_name: str) -> Path:
    code = (
        "import pathlib, sysconfig; "
        f"print(pathlib.Path(sysconfig.get_path('scripts')) / {script_name!r})"
    )
    script = Path(
        subprocess.check_output([str(python_executable), "-c", code], text=True).strip()
    )
    if not script.exists():
        raise RuntimeError(f"installed console script not found: {script}")
    return script


if __name__ == "__main__":
    raise SystemExit(main())
