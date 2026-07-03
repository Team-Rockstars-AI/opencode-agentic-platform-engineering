"""Tests for scripts/scaffold.py — the scaffolding engine is the repo's product."""
import json
import re
import subprocess

import yaml

from .conftest import PLACEHOLDER_PATTERN, run_scaffold


def _tree(target):
    """Set of paths (as posix strings relative to target), excluding .git."""
    return {
        p.relative_to(target).as_posix()
        for p in target.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(target).parts
    }


def _read_all_text_files(target):
    for path in target.rglob("*"):
        if not path.is_file() or ".git" in path.relative_to(target).parts:
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def test_terraform_github_basic_layout(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "terraform", "-d", "github", "-g", "basic", "-p", "unit-check")
    assert result.returncode == 0, result.stderr

    files = _tree(target)
    # Present
    assert any(f.startswith("terraform/") for f in files)
    assert any(f.startswith("modules/terraform/") for f in files)
    assert any(f.startswith(".github/") for f in files)
    assert any(f.startswith(".opencode/skills/") for f in files)
    assert any(f.startswith(".opencode/prompts/") for f in files)
    for expected in (
        "opencode.json",
        "manifest.yaml",
        "AGENTS.md",
        "agent_config.py",
        "scripts/validate-skills.py",
        "scripts/select-models.py",
        ".gitignore",
        ".pre-commit-config.yaml",
    ):
        assert expected in files, f"missing {expected}"
    # Absent
    assert not any(f.startswith("bicep/") for f in files)
    assert not any(f.startswith("modules/bicep/") for f in files)
    assert "azure-pipelines.yml" not in files


def test_bicep_azure_devops_basic_layout(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "bicep", "-d", "azure-devops", "-g", "basic", "-p", "unit-check")
    assert result.returncode == 0, result.stderr

    files = _tree(target)
    assert any(f.startswith("bicep/") for f in files)
    assert any(f.startswith("modules/bicep/") for f in files)
    assert not any(f.startswith("terraform/") for f in files)
    assert not any(f.startswith("modules/terraform/") for f in files)
    assert not any(f.startswith(".github/") for f in files)
    # Azure DevOps pipeline files land at the target root
    assert any("pipeline" in f for f in files), "no azure-devops pipeline files found"


def test_no_unresolved_placeholders(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "both", "-d", "github", "-g", "enterprise", "-p", "unit-check")
    assert result.returncode == 0, result.stderr

    pattern = re.compile(PLACEHOLDER_PATTERN)
    offenders = []
    for path, content in _read_all_text_files(target):
        # docs/reports/ ships report *templates* whose tokens are filled by
        # agents at report-writing time, not at scaffold time.
        if "reports" in path.relative_to(target).parts:
            continue
        for match in pattern.finditer(content):
            offenders.append(f"{path}: {match.group(0)}")
    assert not offenders, "Unresolved scaffold placeholders:\n" + "\n".join(offenders)


def test_substitution_landed(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(
        target, "-i", "terraform", "-d", "github", "-g", "basic",
        "-p", "sub-check-xyz", "-l", "westeurope",
    )
    assert result.returncode == 0, result.stderr
    combined = "\n".join(content for _, content in _read_all_text_files(target))
    assert "sub-check-xyz" in combined
    assert "westeurope" in combined


def test_module_paths_rewritten(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "terraform", "-d", "github", "-g", "basic")
    assert result.returncode == 0, result.stderr
    for path, content in _read_all_text_files(target):
        assert "../../modules/" not in content, f"unrewritten module path in {path}"


def test_transient_artifacts_not_copied(tmp_path):
    """Local .terraform/ provider binaries etc. must never ship into a scaffold."""
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "both", "-d", "github", "-g", "basic")
    assert result.returncode == 0, result.stderr
    offenders = [
        p.relative_to(target).as_posix()
        for p in target.rglob("*")
        if ".git" not in p.relative_to(target).parts
        and (
            p.name in {".terraform", "__pycache__", ".pytest_cache", ".terraform.lock.hcl"}
        )
    ]
    assert not offenders, f"transient artifacts leaked into scaffold: {offenders}"


def test_scaffold_metadata_removed(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "both", "-d", "github", "-g", "basic")
    assert result.returncode == 0, result.stderr
    leftovers = [f for f in _tree(target) if f.endswith(".opencode-scaffold.json")]
    assert not leftovers, f"scaffold metadata not cleaned up: {leftovers}"


def test_git_initialized_with_initial_commit(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "terraform", "-d", "github", "-g", "basic")
    assert result.returncode == 0, result.stderr
    assert (target / ".git").is_dir()
    log = subprocess.run(
        ["git", "-C", str(target), "log", "--oneline"],
        capture_output=True, text=True, check=True,
    )
    assert "initial platform-engineering template" in log.stdout


def test_github_org_repo_split(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(
        target, "-i", "terraform", "-d", "github", "-g", "basic",
        "-p", "proj-x", "--github-org-repo", "acme/infra-repo",
    )
    assert result.returncode == 0, result.stderr
    combined = "\n".join(content for _, content in _read_all_text_files(target))
    assert "acme" in combined
    assert "infra-repo" in combined


def test_github_org_repo_bare_org_uses_project_name(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(
        target, "-i", "terraform", "-d", "github", "-g", "basic",
        "-p", "proj-y", "--github-org-repo", "acme",
    )
    assert result.returncode == 0, result.stderr
    combined = "\n".join(content for _, content in _read_all_text_files(target))
    assert "acme" in combined
    assert "proj-y" in combined


def test_generated_config_files_parse(tmp_path):
    target = tmp_path / "out"
    result = run_scaffold(target, "-i", "both", "-d", "azure-devops", "-g", "enterprise")
    assert result.returncode == 0, result.stderr

    config = json.loads((target / "opencode.json").read_text(encoding="utf-8"))
    assert config.get("agent"), "generated opencode.json has no agents"

    yaml_files = [
        p for p in target.rglob("*.yml")
        if ".git" not in p.relative_to(target).parts
    ] + [
        p for p in target.rglob("*.yaml")
        if ".git" not in p.relative_to(target).parts
    ]
    assert yaml_files, "no YAML files generated"
    for path in yaml_files:
        list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
