"""Tests for the scaffold stamp and templates/opencode-config/scripts/update.py."""
import hashlib
import json
import shutil
import subprocess
import sys

from .conftest import REPO_ROOT, run_scaffold

STAMP = ".platform-scaffold.json"

# What we exclude when copying this repo to simulate an upstream template clone.
COPY_IGNORE = shutil.ignore_patterns(
    ".git", ".venv-ci", "node_modules", "__pycache__",
    ".terraform", ".pytest_cache", ".ruff_cache",
)


def run_update(workdir, template_path, *extra):
    cmd = [sys.executable, str(workdir / "scripts" / "update.py"),
           "--template-path", str(template_path), *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=workdir, check=False)


def make_template_copy(tmp_path, name="template2"):
    """Copy this repo (as if it were an upstream clone) and git-init it."""
    dest = tmp_path / name
    shutil.copytree(REPO_ROOT, dest, ignore=COPY_IGNORE)
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "add", "."], cwd=dest, check=True)
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "template state"],
        cwd=dest, check=True,
    )
    return dest


def commit_template(dest, message):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "add", "."], cwd=dest, check=True)
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message],
        cwd=dest, check=True,
    )


def scaffold_from(template, target, *extra):
    return run_scaffold(
        target, "-i", "terraform", "-d", "github", "-g", "basic", "-p", "upd-check",
        *extra, repo_root=template,
    )


def test_stamp_written_and_valid(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "terraform", "-d", "github", "-g", "basic", "-p", "stamp-check")
    assert result.returncode == 0, result.stderr

    stamp = json.loads((target / STAMP).read_text(encoding="utf-8"))
    assert stamp["schema_version"] == 1
    assert stamp["inputs"]["project_name"] == "stamp-check"
    assert stamp["inputs"]["iac_framework"] == "terraform"
    assert stamp["inputs"]["devops_platform"] == "github"
    assert stamp["inputs"]["governance_tier"] == "basic"
    assert len(stamp["template_commit"]) == 40  # this repo is a git checkout
    assert stamp["files"], "stamp file manifest is empty"

    # Spot-check one manifest hash against a recomputation.
    rel, recorded = next(iter(sorted(stamp["files"].items())))
    actual = hashlib.sha256((target / rel).read_bytes()).hexdigest()
    assert recorded == f"sha256:{actual}"

    # The stamp itself must not be in its own manifest.
    assert STAMP not in stamp["files"]

    # And it must be part of the initial commit.
    tracked = subprocess.run(
        ["git", "-C", str(target), "ls-files", STAMP], capture_output=True, text=True, check=True
    )
    assert tracked.stdout.strip() == STAMP


def test_update_already_up_to_date(tmp_path):
    target = tmp_path / "out"
    assert run_scaffold(target, "-i", "terraform", "-d", "github", "-g", "basic").returncode == 0
    result = run_update(target, REPO_ROOT, "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Already up to date" in result.stdout


def test_update_applies_upstream_change(tmp_path):
    template = make_template_copy(tmp_path)
    target = tmp_path / "out"
    assert scaffold_from(template, target).returncode == 0, "scaffold from template copy failed"

    # Simulate an upstream template improvement.
    agents_md = template / "templates" / "AGENTS.md"
    agents_md.write_text(agents_md.read_text(encoding="utf-8") + "\nUPSTREAM-IMPROVEMENT\n", encoding="utf-8")
    commit_template(template, "feat: upstream improvement")

    result = run_update(target, template)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "UPSTREAM-IMPROVEMENT" in (target / "AGENTS.md").read_text(encoding="utf-8")

    # Stamp moved to the new template commit and re-hashed the applied file.
    stamp = json.loads((target / STAMP).read_text(encoding="utf-8"))
    head = subprocess.run(["git", "-C", str(template), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    assert stamp["template_commit"] == head
    actual = hashlib.sha256((target / "AGENTS.md").read_bytes()).hexdigest()
    assert stamp["files"]["AGENTS.md"] == f"sha256:{actual}"

    # A report was written.
    reports = list((target / "docs" / "reports").glob("update-report-*.md"))
    assert reports, "no update report written"


def test_update_flags_conflict_and_keeps_local_file(tmp_path):
    template = make_template_copy(tmp_path)
    target = tmp_path / "out"
    assert scaffold_from(template, target).returncode == 0

    # Local modification + upstream modification of the same file = conflict.
    local_agents = target / "AGENTS.md"
    local_agents.write_text(local_agents.read_text(encoding="utf-8") + "\nLOCAL-EDIT\n", encoding="utf-8")
    upstream_agents = template / "templates" / "AGENTS.md"
    upstream_agents.write_text(upstream_agents.read_text(encoding="utf-8") + "\nUPSTREAM-EDIT\n", encoding="utf-8")
    commit_template(template, "feat: conflicting change")

    result = run_update(target, template)
    assert result.returncode == 2, result.stdout + result.stderr

    content = local_agents.read_text(encoding="utf-8")
    assert "LOCAL-EDIT" in content and "UPSTREAM-EDIT" not in content, "conflicted file was touched"

    report = next((target / "docs" / "reports").glob("update-report-*.md")).read_text(encoding="utf-8")
    assert "AGENTS.md" in report
    assert "Conflicts (manual merge required)" in report

    # Conflicted file keeps its ORIGINAL stamp hash (stays detectable as modified).
    stamp = json.loads((target / STAMP).read_text(encoding="utf-8"))
    current = hashlib.sha256(local_agents.read_bytes()).hexdigest()
    assert stamp["files"]["AGENTS.md"] != f"sha256:{current}"


def test_update_skips_user_deleted_files(tmp_path):
    template = make_template_copy(tmp_path)
    target = tmp_path / "out"
    assert scaffold_from(template, target).returncode == 0

    (target / "AGENTS.md").unlink()
    # Any upstream change so the commit differs.
    upstream_agents = template / "templates" / "AGENTS.md"
    upstream_agents.write_text(upstream_agents.read_text(encoding="utf-8") + "\nUPSTREAM\n", encoding="utf-8")
    commit_template(template, "feat: change")

    result = run_update(target, template)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (target / "AGENTS.md").exists(), "user-deleted file was recreated"
    report = next((target / "docs" / "reports").glob("update-report-*.md")).read_text(encoding="utf-8")
    assert "Skipped (deleted locally)" in report


def test_update_dry_run_changes_nothing(tmp_path):
    template = make_template_copy(tmp_path)
    target = tmp_path / "out"
    assert scaffold_from(template, target).returncode == 0

    upstream_agents = template / "templates" / "AGENTS.md"
    upstream_agents.write_text(upstream_agents.read_text(encoding="utf-8") + "\nUPSTREAM\n", encoding="utf-8")
    commit_template(template, "feat: change")

    before_stamp = (target / STAMP).read_text(encoding="utf-8")
    before_agents = (target / "AGENTS.md").read_text(encoding="utf-8")

    result = run_update(target, template, "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (target / STAMP).read_text(encoding="utf-8") == before_stamp
    assert (target / "AGENTS.md").read_text(encoding="utf-8") == before_agents
    assert "dry-run" in next((target / "docs" / "reports").glob("update-report-*.md")).read_text(encoding="utf-8")
