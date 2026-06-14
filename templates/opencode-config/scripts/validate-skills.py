#!/usr/bin/env python3
import os
import re
import sys

def find_referenced_skills(prompt_content):
    # Match patterns like: load the `name` skill, load the 'name' skill, load the "name" skill, load the name skill
    patterns = [
        r"load the `([^`]+)` skill",
        r"load the '([^']+)' skill",
        r"load the \"([^\"]+)\" skill",
        r"load the ([a-zA-Z0-9_-]+) skill"
    ]
    skills = set()
    for pattern in patterns:
        matches = re.findall(pattern, prompt_content, re.IGNORECASE)
        for match in matches:
            skills.add(match.strip())
    return skills

def verify_skill_exists(skill_name, base_dir):
    # Check skills/<name>/SKILL.md or skills/<name>.md
    paths_to_check = [
        os.path.join(base_dir, "skills", skill_name, "SKILL.md"),
        os.path.join(base_dir, "skills", f"{skill_name}.md"),
        os.path.join(base_dir, ".opencode", "skills", skill_name, "SKILL.md"),
        os.path.join(base_dir, ".opencode", "skills", f"{skill_name}.md")
    ]
    for path in paths_to_check:
        if os.path.exists(path):
            return True
    return False

def main():
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Scanning workspace root: {workspace_root}")
    
    # Directories to scan for prompts
    prompt_dirs = [
        os.path.join(workspace_root, ".opencode", "prompts"),
        os.path.join(workspace_root, "templates", "opencode-config", "prompts")
    ]
    
    errors = 0
    scanned_files = 0
    
    for prompt_dir in prompt_dirs:
        if not os.path.exists(prompt_dir):
            continue
            
        # Determine base directory for skills (templates use templates/opencode-config/ as base)
        if "templates" in prompt_dir:
            skills_base = os.path.join(workspace_root, "templates", "opencode-config")
        else:
            skills_base = workspace_root
            
        for filename in os.listdir(prompt_dir):
            if not filename.endswith(".txt"):
                continue
                
            file_path = os.path.join(prompt_dir, filename)
            scanned_files += 1
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            referenced_skills = find_referenced_skills(content)
            
            for skill in referenced_skills:
                # Skip built-in skills or special references if any
                if skill.lower() in ["plan-tracking", "architecture-review", "doc-standards"]:
                    # These are built-in or conceptual skills, but let's check if they exist
                    # If they don't exist, we can skip or warn, but let's verify them too
                    pass
                    
                if not verify_skill_exists(skill, skills_base):
                    print(f"❌ Error in {os.path.relpath(file_path, workspace_root)}: References non-existent skill '{skill}'")
                    errors += 1
                else:
                    print(f"✅ Verified: {os.path.relpath(file_path, workspace_root)} -> skill '{skill}' exists")
                    
    print(f"\nScan complete. Scanned {scanned_files} prompt files. Found {errors} broken skill references.")
    if errors > 0:
        sys.exit(1)
    else:
        print("🎉 All skill references are valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()
