#!/usr/bin/env python3
"""
Automated Scaffolding Script for Platform Engineering Repositories.
Supports both interactive (prompting) and non-interactive (CLI arguments) modes.
Zero external dependencies (uses only Python's standard library).
"""

import os
import sys
import json
import shutil
import hashlib
import argparse
import datetime
import subprocess

# Version/inputs stamp written into every scaffolded workspace; consumed by
# scripts/update.py to sync the workspace with newer template versions.
STAMP_FILENAME = ".platform-scaffold.json"

def prompt_choice(question, choices, default):
    choices_str = "/".join(choices)
    while True:
        try:
            val = input(f"{question} [{choices_str}] (default: {default}): ").strip().lower()
            if not val:
                return default
            if val in choices:
                return val
            print(f"Invalid choice. Please choose from: {', '.join(choices)}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            sys.exit(1)

def prompt_input(question, default, required=False):
    while True:
        try:
            val = input(f"{question} (default: {default}): ").strip()
            if not val:
                if not required or default:
                    return default
                print("This option is required.")
                continue
            return val
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            sys.exit(1)

# Transient local artifacts that must never ship into a scaffolded workspace
# (e.g. .terraform/ provider binaries left behind by local validation runs).
SKIP_DIRS = {".git", ".terraform", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
SKIP_FILES = {".terraform.lock.hcl", ".DS_Store"}


def copy_dir(src, dst):
    if not os.path.exists(src):
        return
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if item in SKIP_DIRS:
                continue
            copy_dir(s, d)
        else:
            if item in SKIP_FILES:
                continue
            shutil.copy2(s, d)

def copy_file(src, dst):
    if not os.path.exists(src):
        return
    parent = os.path.dirname(dst)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)
    shutil.copy2(src, dst)

def replace_placeholders_and_paths(target_dir, replacements):
    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip git folder files if any
            if ".git" + os.sep in file_path or file_path.endswith(".git"):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Binary file, skip
                continue

            has_changed = False
            for placeholder, value in replacements.items():
                search_str = f"{{{{{placeholder}}}}}"
                if search_str in content:
                    content = content.replace(search_str, value)
                    has_changed = True
            
            # Update relative module paths to point to the local modules/ folder
            if "../../modules/" in content:
                content = content.replace("../../modules/", "../modules/")
                has_changed = True

            if has_changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

def cleanup_unused(target_dir):
    # Remove any .opencode-scaffold.json files in the target directory
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file == ".opencode-scaffold.json":
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass

def create_gitignore(target_dir, iac_framework):
    gitignore_path = os.path.join(target_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        return
        
    lines = [
        "# OS/System",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".pytest_cache/",
        "",
        "# IDEs/Editors",
        ".vscode/",
        ".idea/",
        "*.suo",
        "*.ntvs*",
        "*.njsproj",
        "*.sln",
        "*.swp",
        "",
    ]
    
    if iac_framework in ("terraform", "both"):
        lines.extend([
            "# Terraform",
            ".terraform/",
            "*.tfstate",
            "*.tfstate.backup",
            ".terraform.lock.hcl",
            "*.tfvars",
            "*.tfvars.json",
            "tfplan",
            "plan_output.txt",
            "",
        ])
        
    if iac_framework in ("bicep", "both"):
        lines.extend([
            "# Bicep",
            "*.bicep.log",
            "plan_output.txt",
            "",
        ])
        
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def get_template_git_info(repo_root):
    """Best-effort git identity of this template repo (works from a tarball too)."""
    info = {"template_repo": "unknown", "template_commit": "unknown"}
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True
        )
        if commit.returncode == 0 and commit.stdout.strip():
            info["template_commit"] = commit.stdout.strip()
        remote = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"], cwd=repo_root, capture_output=True, text=True
        )
        if remote.returncode == 0 and remote.stdout.strip():
            info["template_repo"] = remote.stdout.strip()
    except Exception:
        pass
    return info


def write_scaffold_stamp(target_dir, repo_root, inputs):
    """Record template version, scaffold inputs, and a hash manifest of the output.

    Hashes are computed after placeholder substitution, so they reflect exactly
    what the user received; update.py compares against them to detect local edits.
    """
    files = {}
    for root, dirs, names in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in names:
            if name == STAMP_FILENAME:
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, target_dir).replace(os.sep, "/")
            digest = hashlib.sha256()
            with open(path, "rb") as file_obj:
                digest.update(file_obj.read())
            files[rel] = f"sha256:{digest.hexdigest()}"

    stamp = {
        "schema_version": 1,
        **get_template_git_info(repo_root),
        "scaffolded_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "inputs": inputs,
        "files": files,
    }
    with open(os.path.join(target_dir, STAMP_FILENAME), "w", encoding="utf-8") as file_obj:
        json.dump(stamp, file_obj, indent=2, sort_keys=True)
        file_obj.write("\n")


def initialize_git(target_dir):
    print("\nInitializing Git repository in the target directory...")
    try:
        # Run git init
        subprocess.run(["git", "init"], cwd=target_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if local git name/email is set, if not set them locally
        name_check = subprocess.run(["git", "config", "user.name"], cwd=target_dir, capture_output=True, text=True)
        if not name_check.stdout.strip():
            subprocess.run(["git", "config", "user.name", "OpenCode Platform Engineer"], cwd=target_dir, check=True)
        
        # Check email
        email_check = subprocess.run(["git", "config", "user.email"], cwd=target_dir, capture_output=True, text=True)
        if not email_check.stdout.strip():
            subprocess.run(["git", "config", "user.email", "agent@opencode.ai"], cwd=target_dir, check=True)
            
        # git add .
        subprocess.run(["git", "add", "."], cwd=target_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # git commit
        subprocess.run(["git", "commit", "-m", "feat: initial platform-engineering template"], cwd=target_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Git repository initialized and initial commit created successfully.")
    except Exception as e:
        print(f"⚠️ Warning: Failed to initialize Git repository or make the initial commit: {e}")

def main():
    parser = argparse.ArgumentParser(description="Scaffold a new platform-engineering repository.")
    parser.add_argument("-i", "--iac-framework", choices=["terraform", "bicep", "both"], help="IaC Framework")
    parser.add_argument("-d", "--devops-platform", choices=["github", "azure-devops"], help="DevOps Platform")
    parser.add_argument("-g", "--governance-tier", choices=["basic", "enterprise"], help="Governance Tier")
    parser.add_argument("-p", "--project-name", help="Project Name")
    parser.add_argument("-t", "--target-dir", help="Target Directory")
    parser.add_argument("-l", "--azure-location", help="Primary Azure Location")
    parser.add_argument("-s", "--subscription-id", help="Azure Subscription ID")
    parser.add_argument("--tenant-id", "--tenant", help="Azure Tenant ID")
    parser.add_argument("--github-org-repo", help="GitHub Org/Repo (optional, e.g. org/repo)")
    parser.add_argument("--github-org", help="GitHub Organization or Username")
    parser.add_argument("--github-repo", help="GitHub Repository Name")
    parser.add_argument("--github-runner-pool", help="GitHub runner pool (default: ubuntu-latest)")
    parser.add_argument("--ado-runner-pool", help="Azure DevOps runner pool (default: ubuntu-latest)")
    parser.add_argument("--non-interactive", action="store_true", help="Disable interactive prompting")
    parser.add_argument("--no-git", action="store_true", help="Skip git init/commit in the target (used by update.py re-renders)")

    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Interactive flow or default fallbacks
    iac_framework = args.iac_framework
    if iac_framework is None:
        if args.non_interactive:
            iac_framework = 'both'
        else:
            iac_framework = prompt_choice("Select IaC Framework", ["terraform", "bicep", "both"], "both")

    devops_platform = args.devops_platform
    if devops_platform is None:
        if args.non_interactive:
            devops_platform = 'github'
        else:
            devops_platform = prompt_choice("Select DevOps Platform", ["github", "azure-devops"], "github")

    governance_tier = args.governance_tier
    if governance_tier is None:
        if args.non_interactive:
            governance_tier = 'basic'
        else:
            governance_tier = prompt_choice("Select Governance Tier", ["basic", "enterprise"], "basic")

    project_name = args.project_name
    if project_name is None:
        if args.non_interactive:
            project_name = 'platform-core'
        else:
            project_name = prompt_input("Enter Project Name", "platform-core")

    target_dir = args.target_dir
    if target_dir is None:
        if args.non_interactive:
            target_dir = f"./{project_name}"
        else:
            target_dir = prompt_input("Enter Target Directory", f"./{project_name}")

    target_dir = os.path.abspath(target_dir)

    azure_location = args.azure_location
    if azure_location is None:
        if args.non_interactive:
            azure_location = 'eastus2'
        else:
            azure_location = prompt_input("Enter Azure Location", "eastus2")

    subscription_id = args.subscription_id
    if subscription_id is None:
        if args.non_interactive:
            subscription_id = '00000000-0000-0000-0000-000000000000'
        else:
            subscription_id = prompt_input("Enter Azure Subscription ID", "00000000-0000-0000-0000-000000000000")

    tenant_id = args.tenant_id
    if tenant_id is None:
        if args.non_interactive:
            tenant_id = '00000000-0000-0000-0000-000000000000'
        else:
            tenant_id = prompt_input("Enter Azure Tenant ID", "00000000-0000-0000-0000-000000000000")

    # GitHub Org/Repo resolution
    github_org_name = args.github_org
    github_repo_name = args.github_repo
    github_org_repo = args.github_org_repo

    if github_org_repo:
        if '/' in github_org_repo:
            github_org_name, github_repo_name = github_org_repo.split('/', 1)
        else:
            github_org_name = github_org_repo
            github_repo_name = project_name

    if github_org_name is None or github_repo_name is None:
        if args.non_interactive:
            github_org_name = github_org_name or "placeholder-org"
            github_repo_name = github_repo_name or project_name
        else:
            default_val = f"placeholder-org/{project_name}"
            val = prompt_input("Enter GitHub Org/Repo (optional, e.g. org/repo)", default_val)
            if '/' in val:
                github_org_name, github_repo_name = val.split('/', 1)
            else:
                github_org_name = val
                github_repo_name = project_name

    # Runner pools resolution
    github_runner_pool = args.github_runner_pool
    if github_runner_pool is None:
        if devops_platform == 'github':
            if args.non_interactive:
                github_runner_pool = 'ubuntu-latest'
            else:
                github_runner_pool = prompt_input("Enter GitHub runner pool", "ubuntu-latest")
        else:
            github_runner_pool = 'ubuntu-latest'

    ado_runner_pool = args.ado_runner_pool
    if ado_runner_pool is None:
        if devops_platform == 'azure-devops':
            if args.non_interactive:
                ado_runner_pool = 'ubuntu-latest'
            else:
                ado_runner_pool = prompt_input("Enter Azure DevOps runner pool", "ubuntu-latest")
        else:
            ado_runner_pool = 'ubuntu-latest'

    # Print summary
    print("\n" + "=" * 60)
    print("Scaffolding Platform Engineering Repository")
    print("=" * 60)
    print(f"Project Name:      {project_name}")
    print(f"Target Directory:  {target_dir}")
    print(f"IaC Framework:     {iac_framework}")
    print(f"DevOps Platform:   {devops_platform}")
    print(f"Governance Tier:   {governance_tier}")
    print(f"Azure Location:    {azure_location}")
    print(f"Subscription ID:   {subscription_id}")
    print(f"Tenant ID:         {tenant_id}")
    if devops_platform == 'github':
        print(f"GitHub Org/Repo:   {github_org_name}/{github_repo_name}")
        print(f"GitHub Runner:     {github_runner_pool}")
    elif devops_platform == 'azure-devops':
        print(f"ADO Runner:        {ado_runner_pool}")
    print("=" * 60)

    # Perform Scaffolding
    print("\nCopying files...")
    
    # 1. Create target directory
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 2. Copy DevOps templates
    if devops_platform == 'github':
        copy_dir(os.path.join(repo_root, "templates", "github"), os.path.join(target_dir, ".github"))
    elif devops_platform == 'azure-devops':
        copy_dir(os.path.join(repo_root, "templates", "azure-devops"), target_dir)

    # 3. Copy IaC templates and modules
    if iac_framework in ("terraform", "both"):
        copy_dir(os.path.join(repo_root, "templates", "terraform"), os.path.join(target_dir, "terraform"))
        copy_dir(os.path.join(repo_root, "modules", "terraform"), os.path.join(target_dir, "modules", "terraform"))

    if iac_framework in ("bicep", "both"):
        copy_dir(os.path.join(repo_root, "templates", "bicep"), os.path.join(target_dir, "bicep"))
        copy_dir(os.path.join(repo_root, "modules", "bicep"), os.path.join(target_dir, "modules", "bicep"))

    # 3b. Copy Docs templates
    docs_src = os.path.join(repo_root, "templates", "docs")
    if os.path.exists(docs_src):
        copy_dir(docs_src, os.path.join(target_dir, "docs"))

    # 4. Copy OpenCode config and prompts/skills
    config_src = os.path.join(repo_root, "templates", "opencode-config")
    copy_dir(os.path.join(config_src, "skills"), os.path.join(target_dir, ".opencode", "skills"))
    copy_dir(os.path.join(config_src, "prompts"), os.path.join(target_dir, ".opencode", "prompts"))
    copy_file(os.path.join(config_src, "opencode.json"), os.path.join(target_dir, "opencode.json"))
    copy_file(os.path.join(config_src, "manifest.yaml"), os.path.join(target_dir, "manifest.yaml"))
    copy_file(os.path.join(config_src, "agent_config.py"), os.path.join(target_dir, "agent_config.py"))
    copy_file(os.path.join(config_src, "scripts", "validate-skills.py"), os.path.join(target_dir, "scripts", "validate-skills.py"))
    copy_file(os.path.join(config_src, "scripts", "select-models.py"), os.path.join(target_dir, "scripts", "select-models.py"))
    copy_file(os.path.join(config_src, "scripts", "update.py"), os.path.join(target_dir, "scripts", "update.py"))

    # 5. Copy AGENTS.md
    copy_file(os.path.join(repo_root, "templates", "AGENTS.md"), os.path.join(target_dir, "AGENTS.md"))

    # Create .gitignore
    create_gitignore(target_dir, iac_framework)

    # Move .pre-commit-config.yaml to the root of the target repository
    precommit_tf = os.path.join(target_dir, "terraform", ".pre-commit-config.yaml")
    precommit_bicep = os.path.join(target_dir, "bicep", ".pre-commit-config.yaml")
    precommit_target = os.path.join(target_dir, ".pre-commit-config.yaml")

    if os.path.exists(precommit_tf):
        shutil.move(precommit_tf, precommit_target)
        if os.path.exists(precommit_bicep):
            try:
                os.remove(precommit_bicep)
            except Exception:
                pass
    elif os.path.exists(precommit_bicep):
        shutil.move(precommit_bicep, precommit_target)

    # 6. Perform substitutions & path corrections
    print("Performing placeholder substitution and updating module paths...")
    replacements = {
        "project_name": project_name,
        "azure_location": azure_location,
        "governance_tier": governance_tier,
        "subscription_id": subscription_id,
        "tenant_id": tenant_id,
        "github_org_name": github_org_name,
        "github_repo_name": github_repo_name,
        "github_runner_pool": github_runner_pool,
        "ado_runner_pool": ado_runner_pool
    }
    replace_placeholders_and_paths(target_dir, replacements)

    # 7. Cleanup unused scaffolding metadata files
    cleanup_unused(target_dir)

    # 7b. Stamp the workspace with template version + inputs + file manifest
    write_scaffold_stamp(target_dir, repo_root, replacements | {
        "iac_framework": iac_framework,
        "devops_platform": devops_platform,
    })

    # 8. Set execution permissions for any copied scripts
    target_validate_script = os.path.join(target_dir, "scripts", "validate-skills.py")
    if os.path.exists(target_validate_script):
        try:
            os.chmod(target_validate_script, 0o755)
        except Exception:
            pass

    print("✅ Files copied and configured successfully.")

    # 9. Git initialization
    if not args.no_git:
        initialize_git(target_dir)

    print("\n🎉 Scaffolding complete! Your new platform engineering repository is ready at:")
    print(f"   {target_dir}\n")

if __name__ == "__main__":
    main()
