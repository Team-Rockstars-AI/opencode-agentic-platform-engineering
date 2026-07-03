"""Tests for scripts/validate-team.py — subprocess regression run + pure-function units."""
import subprocess
import sys

from .conftest import REPO_ROOT, load_script

vt = load_script("validate-team.py")


def test_validate_team_passes_on_repo():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate-team.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_find_skill_refs_backtick():
    assert vt.find_skill_refs("Please use the `audit` skill now") == {"audit"}


def test_find_skill_refs_load_variants():
    content = "First load the `security-checklist` skill, then load the 'plan-tracking' skill."
    refs = vt.find_skill_refs(content)
    assert {"security-checklist", "plan-tracking"} <= refs


def test_find_skill_refs_none():
    assert vt.find_skill_refs("no skills mentioned here") == set()


def test_skill_exists_directory_form(tmp_path):
    skills = tmp_path / "skills"
    (skills / "audit").mkdir(parents=True)
    (skills / "audit" / "SKILL.md").write_text("# audit", encoding="utf-8")
    assert vt.skill_exists("audit", skills)
    assert not vt.skill_exists("missing", skills)


def test_skill_exists_flat_file_form(tmp_path):
    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "debug.md").write_text("# debug", encoding="utf-8")
    assert vt.skill_exists("debug", skills)
