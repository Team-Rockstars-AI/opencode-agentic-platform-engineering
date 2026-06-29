#!/usr/bin/env python3
"""
validate-team.py — comprehensive team-consistency validator.

Checks:
  1. opencode.json is valid JSON
  2. Every configured agent has an existing prompt file
  3. Every prompt file is referenced by an active agent
  4. Every skill referenced in a prompt resolves to an existing skill file
  5. Every command references an existing agent
  6. Root and template agent topology are intentionally consistent (same agent names)
  7. AGENTS.md agent names match opencode.json agent names
  8. No orphan skill directories unless explicitly marked unused

Safe and read-only — never modifies any file.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "templates" / "opencode-config"

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(f"  ❌ {msg}")


def warn(msg: str) -> None:
    WARNINGS.append(f"  ⚠️  {msg}")


def ok(msg: str) -> None:
    print(f"  ✅ {msg}")


# ---------------------------------------------------------------------------
# Check 1: JSON validity
# ---------------------------------------------------------------------------

def check_json_valid(path: Path) -> Optional[dict]:
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        ok(f"Valid JSON: {path.relative_to(REPO_ROOT)}")
        return data
    except json.JSONDecodeError as e:
        err(f"Invalid JSON in {path.relative_to(REPO_ROOT)}: {e}")
        return None
    except FileNotFoundError:
        err(f"File not found: {path.relative_to(REPO_ROOT)}")
        return None


# ---------------------------------------------------------------------------
# Check 2+3: Agent prompt files
# ---------------------------------------------------------------------------

def check_agent_prompts(config: dict, prompts_dir: Path, label: str) -> set[str]:
    agents = config.get("agent", {})
    agent_names = set(agents.keys())
    prompt_files = set()

    if prompts_dir.exists():
        prompt_files = {p.stem for p in prompts_dir.glob("*.txt")}

    print(f"\n  [{label}] Agent ↔ prompt cross-check")

    # Every agent must have a prompt file
    for agent_name, agent_cfg in agents.items():
        prompt_ref = agent_cfg.get("prompt", "")
        # Extract filename from {file:./path/to/file.txt}
        match = re.search(r"\{file:(.+?)\}", prompt_ref)
        if match:
            raw = match.group(1)
            # Normalise ./relative → relative
            rel = raw.lstrip("./") if not raw.startswith(".opencode") else raw
            if raw.startswith("./"):
                rel = raw[2:]
            elif raw.startswith("."):
                rel = raw[1:]
            prompt_path = (REPO_ROOT / rel).resolve()
            # For template configs, prompts live at templates/opencode-config/prompts/<name>.txt
            if not prompt_path.exists():
                # Strip any leading .opencode/prompts/ and look in template prompts dir
                filename = Path(rel).name
                template_prompt_path = TEMPLATE_ROOT / "prompts" / filename
                if template_prompt_path.exists():
                    prompt_path = template_prompt_path
            if prompt_path.exists():
                ok(f"Agent '{agent_name}' → prompt exists: {raw}")
            else:
                err(f"[{label}] Agent '{agent_name}' references missing prompt: {raw}")
        else:
            warn(f"[{label}] Agent '{agent_name}' has no file-based prompt reference")

    # Every prompt file should be referenced by an agent
    for stem in prompt_files:
        referenced = any(
            stem in cfg.get("prompt", "")
            for cfg in agents.values()
        )
        if not referenced:
            warn(f"[{label}] Orphan prompt file: {prompts_dir.relative_to(REPO_ROOT)}/{stem}.txt")

    return agent_names


# ---------------------------------------------------------------------------
# Check 4: Skill references in prompts
# ---------------------------------------------------------------------------

SKILL_REF_PATTERNS = [
    r"load the `([^`]+)` skill",
    r"load the '([^']+)' skill",
    r'load the "([^"]+)" skill',
    r"load the ([a-zA-Z0-9_-]+) skill",
    r"use the `([^`]+)` skill",
    r"use the '([^']+)' skill",
    r'use the "([^"]+)" skill',
    r"the `([^`]+)` skill",
]


def find_skill_refs(content: str) -> set[str]:
    skills: set[str] = set()
    for pattern in SKILL_REF_PATTERNS:
        for match in re.findall(pattern, content, re.IGNORECASE):
            skills.add(match.strip())
    return skills


def skill_exists(name: str, skills_dir: Path) -> bool:
    return (skills_dir / name / "SKILL.md").exists() or (skills_dir / f"{name}.md").exists()


def check_skill_refs(prompts_dir: Path, skills_dir: Path, label: str) -> None:
    if not prompts_dir.exists():
        warn(f"[{label}] Prompts directory does not exist: {prompts_dir.relative_to(REPO_ROOT)}")
        return

    print(f"\n  [{label}] Skill reference check")
    for prompt_file in sorted(prompts_dir.glob("*.txt")):
        content = prompt_file.read_text(encoding="utf-8")
        refs = find_skill_refs(content)
        for skill in sorted(refs):
            if skill_exists(skill, skills_dir):
                ok(f"{prompt_file.name} → skill '{skill}' exists")
            else:
                err(f"[{label}] {prompt_file.name} references missing skill '{skill}'")


# ---------------------------------------------------------------------------
# Check 5: Commands reference existing agents
# ---------------------------------------------------------------------------

def check_commands(config: dict, label: str) -> None:
    agents = set(config.get("agent", {}).keys())
    commands = config.get("command", {})
    print(f"\n  [{label}] Command → agent check")
    for cmd_name, cmd_cfg in commands.items():
        agent = cmd_cfg.get("agent")
        if agent is None:
            warn(f"[{label}] Command '/{cmd_name}' has no 'agent' field")
        elif agent not in agents:
            err(f"[{label}] Command '/{cmd_name}' references undefined agent '{agent}'")
        else:
            ok(f"Command '/{cmd_name}' → agent '{agent}' exists")


# ---------------------------------------------------------------------------
# Check 6: Root/template topology parity
# ---------------------------------------------------------------------------

def check_topology_parity(root_agents: set[str], template_agents: set[str]) -> None:
    print("\n  [parity] Root ↔ template agent topology")
    only_root = root_agents - template_agents
    only_template = template_agents - root_agents
    if not only_root and not only_template:
        ok("Root and template agent topologies are identical")
    else:
        if only_root:
            warn(f"Agents in root but not template: {sorted(only_root)}")
        if only_template:
            warn(f"Agents in template but not root: {sorted(only_template)}")


# ---------------------------------------------------------------------------
# Check 7: AGENTS.md agent name coverage
# ---------------------------------------------------------------------------

def check_agents_md(agents_md_path: Path, agent_names: set[str], label: str) -> None:
    print(f"\n  [{label}] AGENTS.md coverage check")
    if not agents_md_path.exists():
        warn(f"[{label}] AGENTS.md not found at {agents_md_path.relative_to(REPO_ROOT)}")
        return
    content = agents_md_path.read_text(encoding="utf-8")
    for agent in sorted(agent_names):
        # Look for backtick-quoted agent name
        if f"`{agent}`" in content:
            ok(f"AGENTS.md documents agent '{agent}'")
        else:
            warn(f"[{label}] AGENTS.md does not mention agent '{agent}'")


# ---------------------------------------------------------------------------
# Check 8: Orphan skills
# ---------------------------------------------------------------------------

def find_command_skill_refs(config: dict) -> set[str]:
    """Collect skill names mentioned in command template strings."""
    refs: set[str] = set()
    for cmd_cfg in config.get("command", {}).values():
        template = cmd_cfg.get("template", "")
        refs |= find_skill_refs(template)
    return refs


def check_orphan_skills(skills_dir: Path, all_prompt_dirs: list[Path], label: str,
                        command_skill_refs: Optional[set[str]] = None) -> None:
    print(f"\n  [{label}] Orphan skill check")
    if not skills_dir.exists():
        warn(f"[{label}] Skills directory not found: {skills_dir.relative_to(REPO_ROOT)}")
        return

    all_skill_refs: set[str] = set()
    for prompts_dir in all_prompt_dirs:
        if not prompts_dir.exists():
            continue
        for prompt_file in prompts_dir.glob("*.txt"):
            all_skill_refs |= find_skill_refs(prompt_file.read_text(encoding="utf-8"))
    if command_skill_refs:
        all_skill_refs |= command_skill_refs

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / "SKILL.md").exists():
            warn(f"[{label}] Skill directory '{skill_dir.name}' has no SKILL.md")
            continue
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        if "unused" in skill_md.lower()[:200]:
            ok(f"Skill '{skill_dir.name}' is explicitly marked unused — skipping orphan check")
            continue
        if skill_dir.name in all_skill_refs:
            ok(f"Skill '{skill_dir.name}' is referenced by at least one prompt")
        else:
            warn(f"[{label}] Skill '{skill_dir.name}' is not referenced by any prompt")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("validate-team.py — platform team consistency validator")
    print(f"Repo root: {REPO_ROOT}")
    print("=" * 60)

    # Paths
    root_config_path = REPO_ROOT / "opencode.json"
    template_config_path = TEMPLATE_ROOT / "opencode.json"
    root_prompts_dir = REPO_ROOT / ".opencode" / "prompts"
    template_prompts_dir = TEMPLATE_ROOT / "prompts"
    root_skills_dir = REPO_ROOT / "skills"
    template_skills_dir = TEMPLATE_ROOT / "skills"
    root_agents_md = REPO_ROOT / "AGENTS.md"
    template_agents_md = REPO_ROOT / "templates" / "AGENTS.md"

    print("\n--- Check 1: JSON validity ---")
    root_config = check_json_valid(root_config_path)
    template_config = check_json_valid(template_config_path)

    root_agent_names: set[str] = set()
    template_agent_names: set[str] = set()

    if root_config:
        print("\n--- Check 2+3: Root agent ↔ prompt files ---")
        root_agent_names = check_agent_prompts(root_config, root_prompts_dir, "root")

        print("\n--- Check 4: Root skill references in prompts ---")
        check_skill_refs(root_prompts_dir, root_skills_dir, "root")

        print("\n--- Check 5: Root command → agent references ---")
        check_commands(root_config, "root")

        print("\n--- Check 7: Root AGENTS.md coverage ---")
        check_agents_md(root_agents_md, root_agent_names, "root")

        print("\n--- Check 8: Root orphan skills ---")
        root_cmd_skill_refs = find_command_skill_refs(root_config)
        check_orphan_skills(root_skills_dir, [root_prompts_dir, template_prompts_dir], "root",
                            command_skill_refs=root_cmd_skill_refs)

    if template_config:
        print("\n--- Check 2+3: Template agent ↔ prompt files ---")
        template_agent_names = check_agent_prompts(template_config, template_prompts_dir, "template")

        print("\n--- Check 4: Template skill references in prompts ---")
        check_skill_refs(template_prompts_dir, template_skills_dir, "template")

        print("\n--- Check 5: Template command → agent references ---")
        check_commands(template_config, "template")

        print("\n--- Check 7: Template AGENTS.md coverage ---")
        check_agents_md(template_agents_md, template_agent_names, "template")

        print("\n--- Check 8: Template orphan skills ---")
        tmpl_cmd_skill_refs = find_command_skill_refs(template_config)
        check_orphan_skills(template_skills_dir, [root_prompts_dir, template_prompts_dir], "template",
                            command_skill_refs=tmpl_cmd_skill_refs)

    if root_config and template_config:
        print("\n--- Check 6: Root ↔ template topology parity ---")
        check_topology_parity(root_agent_names, template_agent_names)

    # Summary
    print("\n" + "=" * 60)
    if WARNINGS:
        print(f"Warnings ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(w)

    if ERRORS:
        print(f"\nErrors ({len(ERRORS)}):")
        for e in ERRORS:
            print(e)
        print(f"\n❌ Validation FAILED with {len(ERRORS)} error(s).")
        return 1

    print(f"✅ All checks passed! ({len(WARNINGS)} warning(s))" if WARNINGS else "✅ All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
