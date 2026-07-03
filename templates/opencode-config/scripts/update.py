#!/usr/bin/env python3
"""Template-update tool for scaffolded platform-engineering repositories.

Syncs this workspace with a newer version of the upstream template repository
it was scaffolded from. Reads the `.platform-scaffold.json` stamp (written at
scaffold time: template commit, scaffold inputs, and a sha256 manifest of every
generated file), re-renders the templates at the *new* template version with the
same inputs, and classifies every file by comparing three states:

    original render (hash in stamp)  vs  current file on disk  vs  new render

Classifications and actions:
    unchanged        original == current == new           -> nothing to do
    auto-update      user never touched it, upstream did  -> apply new version
    user-modified    user touched it, upstream did not    -> keep user's file
    conflict         both user and upstream changed it    -> untouched, listed for manual merge
    new-file         upstream added a file                -> copy in (conflict if a local file is in the way)
    user-deleted     user removed a generated file        -> skipped, noted (never recreated)
    removed-upstream user never touched it, upstream removed it -> delete locally

Fetching the template repository (git clone/pull) is the operator's job — this
tool does no network I/O. Nothing is ever `git commit`ted; review and stage the
result yourself (or let the agent team do it via the /update command).

Exit codes: 0 = success or already up to date, 1 = fatal error,
            2 = success but conflicts need manual merging.

Zero external dependencies (uses only Python's standard library).
"""

import os
import sys
import json
import shutil
import hashlib
import argparse
import datetime
import tempfile
import subprocess

STAMP_FILENAME = ".platform-scaffold.json"


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file_obj:
        digest.update(file_obj.read())
    return f"sha256:{digest.hexdigest()}"


def load_stamp(repo_root):
    stamp_path = os.path.join(repo_root, STAMP_FILENAME)
    if not os.path.exists(stamp_path):
        fail(
            f"{STAMP_FILENAME} not found — this repository was scaffolded before "
            "version stamping existed. Re-scaffold with a current template version, "
            "or create the stamp manually from the template repo's scaffold.py."
        )
    with open(stamp_path, "r", encoding="utf-8") as file_obj:
        stamp = json.load(file_obj)
    if stamp.get("schema_version") != 1:
        fail(f"Unsupported stamp schema_version: {stamp.get('schema_version')}")
    return stamp


def template_head_commit(template_path):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=template_path, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def rerender_template(template_path, inputs):
    """Re-run the template's scaffold.py with the recorded inputs, without git."""
    scaffold_script = os.path.join(template_path, "scripts", "scaffold.py")
    if not os.path.exists(scaffold_script):
        fail(f"scaffold.py not found in template repo: {scaffold_script}")

    render_dir = os.path.join(tempfile.mkdtemp(prefix="platform-update-"), "render")
    cmd = [
        sys.executable, scaffold_script,
        "--non-interactive", "--no-git",
        "--target-dir", render_dir,
        "--iac-framework", inputs["iac_framework"],
        "--devops-platform", inputs["devops_platform"],
        "--governance-tier", inputs["governance_tier"],
        "--project-name", inputs["project_name"],
        "--azure-location", inputs["azure_location"],
        "--subscription-id", inputs["subscription_id"],
        "--tenant-id", inputs["tenant_id"],
        "--github-org-repo", f"{inputs['github_org_name']}/{inputs['github_repo_name']}",
        "--github-runner-pool", inputs["github_runner_pool"],
        "--ado-runner-pool", inputs["ado_runner_pool"],
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"Re-render at the new template version failed:\n{result.stdout}\n{result.stderr}")
    return render_dir


def walk_files(root):
    """Relative posix paths of all files under root, excluding .git and the stamp."""
    found = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            if name == STAMP_FILENAME:
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            found.add(rel)
    return found


def classify(repo_root, render_dir, stamp):
    """Classify every file across original manifest, current tree, and new render."""
    original = stamp.get("files", {})
    current_files = walk_files(repo_root)
    new_files = walk_files(render_dir)

    result = {
        "unchanged": [], "auto-update": [], "user-modified": [],
        "conflict": [], "new-file": [], "user-deleted": [], "removed-upstream": [],
    }

    for rel in sorted(set(original) | current_files | new_files):
        orig_hash = original.get(rel)
        cur_hash = sha256_of(os.path.join(repo_root, rel)) if rel in current_files else None
        new_hash = sha256_of(os.path.join(render_dir, rel)) if rel in new_files else None

        if orig_hash is None:
            # Not part of the original scaffold.
            if new_hash is None:
                continue  # purely local file, none of our business
            if cur_hash is None:
                result["new-file"].append(rel)
            elif cur_hash == new_hash:
                result["unchanged"].append(rel)
            else:
                result["conflict"].append(rel)  # upstream added a file where a local one exists
        elif cur_hash is None:
            result["user-deleted"].append(rel)
        elif new_hash is None:
            if cur_hash == orig_hash:
                result["removed-upstream"].append(rel)
            else:
                result["conflict"].append(rel)  # user modified a file upstream removed
        elif cur_hash == orig_hash:
            result["unchanged" if new_hash == orig_hash else "auto-update"].append(rel)
        else:
            result["user-modified" if new_hash == orig_hash else "conflict"].append(rel)

    return result


def apply_changes(repo_root, render_dir, classification):
    for rel in classification["auto-update"] + classification["new-file"]:
        src = os.path.join(render_dir, rel)
        dst = os.path.join(repo_root, rel)
        parent = os.path.dirname(dst)
        if parent and not os.path.exists(parent):
            os.makedirs(parent)
        shutil.copy2(src, dst)
    for rel in classification["removed-upstream"]:
        try:
            os.remove(os.path.join(repo_root, rel))
        except OSError:
            pass


def rewrite_stamp(repo_root, render_dir, stamp, classification, new_commit, template_path):
    """Refresh the stamp: applied files get new-render hashes; user-modified and
    conflict files keep their *original* hashes so they stay detectable as
    modified on the next run; user-deleted entries are kept for the same reason."""
    files = dict(stamp.get("files", {}))
    for rel in classification["auto-update"] + classification["new-file"]:
        files[rel] = sha256_of(os.path.join(render_dir, rel))
    for rel in classification["unchanged"]:
        new_path = os.path.join(render_dir, rel)
        if os.path.exists(new_path):
            files[rel] = sha256_of(new_path)
    for rel in classification["removed-upstream"]:
        files.pop(rel, None)

    stamp = dict(stamp)
    stamp["template_commit"] = new_commit
    stamp["updated_at"] = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    try:
        remote = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=template_path, capture_output=True, text=True,
        )
        if remote.returncode == 0 and remote.stdout.strip():
            stamp["template_repo"] = remote.stdout.strip()
    except Exception:
        pass
    stamp["files"] = files

    with open(os.path.join(repo_root, STAMP_FILENAME), "w", encoding="utf-8") as file_obj:
        json.dump(stamp, file_obj, indent=2, sort_keys=True)
        file_obj.write("\n")


REPORT_SECTIONS = [
    ("conflict", "Conflicts (manual merge required)",
     "Both this workspace and the upstream template changed these files. They were left untouched."),
    ("auto-update", "Auto-updated",
     "Never modified locally; replaced with the new template version."),
    ("new-file", "New files",
     "Added by the upstream template."),
    ("removed-upstream", "Removed upstream",
     "Deleted locally because the template no longer ships them (they were never modified here)."),
    ("user-modified", "Kept local modifications",
     "Modified locally; upstream did not change them, so nothing to do."),
    ("user-deleted", "Skipped (deleted locally)",
     "Part of the original scaffold but deleted in this workspace; not recreated."),
]


def write_report(repo_root, report_dir, stamp_commit, new_commit, classification, dry_run):
    lines = [
        "# Template Update Report",
        "",
        f"**Date:** {datetime.date.today().isoformat()}",
        f"**Template version:** `{stamp_commit[:12]}` → `{new_commit[:12]}`",
        f"**Mode:** {'dry-run (no changes applied)' if dry_run else 'applied'}",
        "",
        "## Summary",
        "",
        "| Classification | Files |",
        "|---|---|",
    ]
    for key, title, _ in REPORT_SECTIONS:
        lines.append(f"| {title} | {len(classification[key])} |")
    lines.append(f"| Unchanged | {len(classification['unchanged'])} |")
    for key, title, blurb in REPORT_SECTIONS:
        if not classification[key]:
            continue
        lines += ["", f"## {title}", "", blurb, ""]
        lines += [f"- `{rel}`" for rel in classification[key]]
    lines.append("")

    os.makedirs(os.path.join(repo_root, report_dir), exist_ok=True)
    report_path = os.path.join(repo_root, report_dir, f"update-report-{datetime.date.today().isoformat()}.md")
    with open(report_path, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines))
    return report_path


def main():
    parser = argparse.ArgumentParser(description="Sync this scaffolded repository with a newer template version.")
    parser.add_argument("--template-path", required=True,
                        help="Path to a local clone of the upstream template repository (already at the desired version)")
    parser.add_argument("--dry-run", action="store_true", help="Only classify and report; change nothing")
    parser.add_argument("--report-path", default="docs/reports", help="Directory (relative to repo root) for the update report")
    args = parser.parse_args()

    repo_root = os.getcwd()
    template_path = os.path.abspath(args.template_path)
    if not os.path.isdir(template_path):
        fail(f"Template path does not exist: {template_path}")

    stamp = load_stamp(repo_root)
    stamp_commit = stamp.get("template_commit", "unknown")
    new_commit = template_head_commit(template_path)

    if new_commit != "unknown" and new_commit == stamp_commit:
        print(f"Already up to date (template commit {new_commit[:12]}). Nothing to do.")
        return 0

    print(f"Re-rendering templates at {new_commit[:12]} with the recorded scaffold inputs...")
    render_dir = rerender_template(template_path, stamp["inputs"])

    classification = classify(repo_root, render_dir, stamp)

    print("\nClassification:")
    for key, title, _ in REPORT_SECTIONS:
        print(f"  {title:<38} {len(classification[key])}")
    print(f"  {'Unchanged':<38} {len(classification['unchanged'])}")

    if not args.dry_run:
        apply_changes(repo_root, render_dir, classification)
        rewrite_stamp(repo_root, render_dir, stamp, classification, new_commit, template_path)

    report_path = write_report(repo_root, args.report_path, stamp_commit, new_commit, classification, args.dry_run)
    print(f"\nReport written to {os.path.relpath(report_path, repo_root)}")

    if classification["conflict"]:
        print(f"\n⚠️  {len(classification['conflict'])} conflict(s) require manual merging — see the report.")
        return 2
    if args.dry_run:
        print("\nDry run — no changes were applied.")
    else:
        print("\n✅ Update applied. Review with `git status` / `git diff`, then commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
