"""Tests for scripts/validate-skills.py."""
import subprocess
import sys

from .conftest import REPO_ROOT


def test_validate_skills_passes_on_repo():
    """The validator is read-only; the repo itself must always be green."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate-skills.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
