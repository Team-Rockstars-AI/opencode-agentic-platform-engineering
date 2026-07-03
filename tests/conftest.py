"""Shared helpers for the repository's Python tooling tests."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Scaffold-style placeholder tokens ({{project_name}}). Deliberately excludes
# GitHub Actions expressions like `${{ github.ref }}` (spaces/dots don't match).
PLACEHOLDER_PATTERN = r"\{\{[a-z_]+\}\}"


def load_script(filename: str):
    """Import a scripts/*.py file despite hyphens in its name."""
    path = REPO_ROOT / "scripts" / filename
    mod_name = filename.replace("-", "_").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def run_scaffold(target_dir, *extra_args, repo_root=None):
    """Run scaffold.py as a subprocess in non-interactive mode."""
    root = Path(repo_root) if repo_root else REPO_ROOT
    cmd = [
        sys.executable,
        str(root / "scripts" / "scaffold.py"),
        "--non-interactive",
        "--target-dir",
        str(target_dir),
        *extra_args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT
