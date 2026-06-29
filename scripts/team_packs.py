#!/usr/bin/env python3
"""Helper CLI for discovering and applying Agent Team Packs."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SELECT_MODELS_SCRIPT = REPO_ROOT / "scripts" / "select-models.py"
OPENCODE_CONFIG_PATH = REPO_ROOT / "opencode.json"
MANIFEST_PATH = REPO_ROOT / "manifest.yaml"
AGENT_CONFIG_PATH = REPO_ROOT / "agent_config.py"
PACKS_ROOT = REPO_ROOT / "packs"
TEMPLATE_PACKS_ROOT = REPO_ROOT / "templates" / "opencode-config" / "packs"
PACK_SEARCH_PATHS = [PACKS_ROOT, TEMPLATE_PACKS_ROOT]
ALLOWED_OPTIMISATION_FOCUS = {"cost", "quality", "balanced"}


@dataclass
class PackManifest:
    name: str
    version: str
    dir_label: str
    description: str
    jurisdiction_policy: str
    allow_local: str
    optimisation_focus: str
    agents: Dict[str, Dict[str, object]]
    path: Path


def _normalize_allow_local(value) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)) and value in {0, 1}:
        return "yes" if int(value) == 1 else "no"
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"yes", "y", "true", "1"}:
            return "yes"
        if text in {"no", "n", "false", "0"}:
            return "no"
    raise ValueError(
        f"allow_local must be yes/no, true/false, y/n, 1/0, or boolean (got {value!r})"
    )


def _normalize_jurisdiction(value: str) -> str:
    text = (value or "").strip().lower()
    if text not in {"eu", "eu+us", "global"}:
        raise ValueError(
            f"Unsupported jurisdiction_policy '{value}'. Expected one of: eu, eu+us, global"
        )
    return text


def _discover_pack_files() -> Iterable[Path]:
    for root in PACK_SEARCH_PATHS:
        if not root.exists():
            continue
        for pack_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            for version_dir in sorted(p for p in pack_dir.iterdir() if p.is_dir()):
                manifest_path = version_dir / "pack.yaml"
                if manifest_path.is_file():
                    yield manifest_path


def _load_manifest(path: Path) -> PackManifest:
    with open(path, "r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj) or {}

    required = [
        "name",
        "version",
        "description",
        "jurisdiction_policy",
        "allow_local",
        "optimisation_focus",
        "agents",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Pack {path} missing required fields: {', '.join(missing)}")

    dir_label = path.parent.name  # e.g. v1
    jurisdiction = _normalize_jurisdiction(data["jurisdiction_policy"])
    allow_local = _normalize_allow_local(data["allow_local"])

    agents = data["agents"]
    if not isinstance(agents, dict) or not agents:
        raise ValueError(f"Pack {path} must define at least one agent mapping")

    return PackManifest(
        name=str(data["name"]),
        version=str(data["version"]),
        dir_label=dir_label,
        description=str(data["description"]),
        jurisdiction_policy=jurisdiction,
        allow_local=allow_local,
        optimisation_focus=str(data["optimisation_focus"]),
        agents=agents,
        path=path,
    )


def _load_all_manifests() -> List[PackManifest]:
    manifests: List[PackManifest] = []
    for file_path in _discover_pack_files():
        try:
            manifests.append(_load_manifest(file_path))
        except yaml.YAMLError as exc:
            print(
                f"WARNING: Skipping pack at {file_path}: invalid YAML ({exc})",
                file=sys.stderr,
            )
        except (ValueError, OSError) as exc:
            print(f"WARNING: Skipping pack at {file_path}: {exc}", file=sys.stderr)
    return manifests


def _format_table_row(values: List[str], widths: List[int]) -> str:
    cells = []
    for value, width in zip(values, widths):
        cells.append(value[:width].ljust(width))
    return " | ".join(cells)


def _load_valid_agent_ids() -> Set[str]:
    if not OPENCODE_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"opencode.json not found at {OPENCODE_CONFIG_PATH}. Run this command from the repo root."
        )

    with open(OPENCODE_CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    agents_block = config.get("agent", {})
    if not isinstance(agents_block, dict) or not agents_block:
        raise ValueError("opencode.json does not define any agents to validate against.")

    return set(agents_block.keys())


def _collect_agent_model_refs(agent_cfg: Dict[str, object]) -> List[str]:
    refs: List[str] = []
    model = agent_cfg.get("model")
    if model:
        refs.append(str(model).strip())
    preferred = agent_cfg.get("preferred_model_ids")
    if isinstance(preferred, list):
        refs.extend(str(entry).strip() for entry in preferred if entry)
    return refs


def _run_select_models_discover(jurisdiction: str, allow_local: str) -> Dict[str, object]:
    cmd = [
        sys.executable,
        str(SELECT_MODELS_SCRIPT),
        "discover",
        "--jurisdiction",
        jurisdiction,
        "--allow-local",
        allow_local,
    ]
    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip() or f"exit code {exc.returncode}"
        raise RuntimeError(
            f"select-models discover failed for policy '{jurisdiction}': {detail}"
        ) from exc

    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")

    try:
        return json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise RuntimeError("select-models discover returned invalid JSON output") from exc


def _assess_model_reference(
    model_id: str,
    allow_local: str,
    zen_ids: Set[str],
    ollama_ids: Set[str],
) -> Tuple[str, str]:
    if model_id.startswith("opencode/"):
        if model_id in zen_ids:
            return "OK", "found in OpenCode ZEN catalog"
        return "MISSING", "not present in OpenCode ZEN catalog"

    if model_id.startswith("ollama/"):
        if allow_local != "yes":
            return "DISALLOWED", "allow_local is 'no'"
        if model_id in ollama_ids:
            return "OK", "found in local Ollama catalog"
        return "MISSING", "not installed in local Ollama catalog"

    return "DISALLOWED", "unsupported model namespace"


def _validate_pack_against_catalog(manifest: PackManifest) -> bool:
    print(
        f"\n=== Validating pack '{manifest.name}' ({manifest.dir_label}/{manifest.version}) ==="
    )
    print(
        f"Jurisdiction: {manifest.jurisdiction_policy} | allow_local: {manifest.allow_local}"
    )

    catalog = _run_select_models_discover(manifest.jurisdiction_policy, manifest.allow_local)
    zen_ids = {
        entry.get("id")
        for entry in (catalog.get("zen") or [])
        if entry.get("id")
    }
    ollama_ids = {
        entry.get("id")
        for entry in (catalog.get("ollama") or [])
        if entry.get("id")
    }

    pack_valid = True
    for agent_id in sorted(manifest.agents.keys()):
        refs = [ref for ref in _collect_agent_model_refs(manifest.agents[agent_id]) if ref]
        if not refs:
            print(f"  {agent_id:<22} -> (no models defined) [MISSING] no model references provided")
            pack_valid = False
            continue
        for model_id in refs:
            status, detail = _assess_model_reference(
                model_id,
                manifest.allow_local,
                zen_ids,
                ollama_ids,
            )
            print(f"  {agent_id:<22} -> {model_id:<32} [{status}] {detail}")
            if status != "OK":
                pack_valid = False

    print(f"Pack '{manifest.name}' {'VALID' if pack_valid else 'INVALID'}")
    return pack_valid


def cmd_validate(args):
    _ensure_select_models_script()
    packs = _load_all_manifests()
    if not packs:
        raise SystemExit("No packs available to validate.")

    if args.all:
        manifests_to_check = packs
    else:
        if not args.pack_name:
            raise SystemExit("Pack name is required unless --all is specified.")
        manifests_to_check = [_select_pack(packs, args.pack_name, args.version)]

    any_failures = False
    for manifest in manifests_to_check:
        try:
            success = _validate_pack_against_catalog(manifest)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            success = False
        if not success:
            any_failures = True
            if not args.all:
                break

    if any_failures:
        raise SystemExit(1)


def cmd_list(_args):
    packs = _load_all_manifests()
    if not packs:
        print("No team packs were found. Add YAML manifests under packs/<name>/v*/pack.yaml.")
        return

    widths = [22, 9, 10, 12, 30]
    header = _format_table_row([
        "Pack",
        "Version",
        "Jurisdiction",
        "Focus",
        "Path",
    ], widths)
    print(header)
    print("-" * len(header))

    unique_packs: List[PackManifest] = []
    seen_keys = set()
    for manifest in sorted(packs, key=lambda p: (p.name, p.dir_label, p.path)):
        key = (
            manifest.name,
            manifest.version,
            manifest.jurisdiction_policy,
            manifest.optimisation_focus,
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_packs.append(manifest)

    for manifest in unique_packs:
        print(
            _format_table_row(
                [
                    manifest.name,
                    f"{manifest.dir_label}/{manifest.version}",
                    manifest.jurisdiction_policy,
                    manifest.optimisation_focus,
                    str(manifest.path.relative_to(REPO_ROOT)),
                ],
                widths,
            )
        )


def _select_pack(packs: List[PackManifest], name: str, version: Optional[str]) -> PackManifest:
    candidates = [p for p in packs if p.name == name]
    if not candidates:
        raise ValueError(f"No pack named '{name}' was found.")

    if version:
        normalized = version.strip().lower()
        candidates = [
            p
            for p in candidates
            if p.dir_label.lower() == normalized or p.version.lower() == normalized
        ]
        if not candidates:
            raise ValueError(f"Pack '{name}' does not have version '{version}'.")

    def _version_key(manifest: PackManifest):
        label = manifest.dir_label.lower().lstrip("v")
        try:
            return int(label)
        except ValueError:
            return 0

    return sorted(candidates, key=_version_key, reverse=True)[0]


def _build_mapping(agents: Dict[str, Dict[str, object]]) -> Dict[str, Dict[str, str]]:
    valid_agent_ids = _load_valid_agent_ids()
    mapping: Dict[str, Dict[str, str]] = {}
    for agent_id, cfg in agents.items():
        if not isinstance(cfg, dict):
            raise ValueError(f"Agent '{agent_id}' entry must be a mapping.")
        if agent_id not in valid_agent_ids:
            raise ValueError(
                f"Pack references unknown agent '{agent_id}' not present in opencode.json"
            )
        if "model" in cfg:
            mapping[agent_id] = {"model": str(cfg["model"])}
            continue
        pref = cfg.get("preferred_model_ids")
        if isinstance(pref, list) and pref:
            mapping[agent_id] = {"model": str(pref[0])}
            continue
        raise ValueError(
            f"Agent '{agent_id}' must define either 'model' or a non-empty 'preferred_model_ids' list."
        )
    return mapping


def _ensure_select_models_script():
    if not SELECT_MODELS_SCRIPT.is_file():
        raise FileNotFoundError(
            f"select-models helper not found at {SELECT_MODELS_SCRIPT}. Ensure you are running inside the repo root."
        )


def cmd_apply(args):
    _ensure_select_models_script()
    packs = _load_all_manifests()
    if not packs:
        raise SystemExit("No packs available to apply.")

    manifest = _select_pack(packs, args.pack_name, args.version)
    mapping = _build_mapping(manifest.agents)

    print("Applying pack:\n")
    print(f"  Name: {manifest.name}")
    print(f"  Version: {manifest.dir_label} ({manifest.version})")
    print(f"  Jurisdiction policy: {manifest.jurisdiction_policy}")
    print(f"  Optimisation focus: {manifest.optimisation_focus}")
    print(f"  allow_local: {manifest.allow_local}\n")

    with tempfile.NamedTemporaryFile("w", delete=False, suffix="-mapping.json") as tmp:
        json.dump(mapping, tmp, indent=2)
        tmp_path = tmp.name

    try:
        cmd = [
            sys.executable,
            str(SELECT_MODELS_SCRIPT),
            "apply",
            "--mapping",
            tmp_path,
            "--jurisdiction",
            manifest.jurisdiction_policy,
            "--allow-local",
            manifest.allow_local,
        ]
        try:
            completed = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            error_detail = (exc.stderr or exc.stdout or "").strip()
            if not error_detail:
                error_detail = f"exit code {exc.returncode}"
            print(f"Pack apply failed: {error_detail}", file=sys.stderr)
            raise
        else:
            if completed.stdout:
                print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, end="", file=sys.stderr)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _load_yaml_file(path: Path) -> Dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as file_obj:
        return yaml.safe_load(file_obj) or {}


def _normalize_manifest_policy(raw_value: str) -> str:
    text = (raw_value or "").strip().lower()
    if text.endswith("-sovereign"):
        text = text[: -len("-sovereign")]
    if text in {"eu", "eu+us", "global"}:
        return text
    raise ValueError(
        "Unsupported jurisdiction_policy in manifest. Expected EU-Sovereign, EU+US-Sovereign, or Global."
    )


def _load_security_policy() -> Dict[str, object]:
    if not AGENT_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"agent_config.py not found at {AGENT_CONFIG_PATH}. Cannot derive SECURITY_POLICY."
        )
    source = AGENT_CONFIG_PATH.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(AGENT_CONFIG_PATH))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SECURITY_POLICY":
                    return ast.literal_eval(node.value)
    raise ValueError("SECURITY_POLICY definition not found in agent_config.py")


def _build_export_agents(manifest_data: Dict[str, object], config_data: Dict[str, object]) -> Dict[str, Dict[str, str]]:
    manifest_agents = manifest_data.get("agents") or {}
    config_agents = config_data.get("agent") or {}
    if not manifest_agents or not config_agents:
        raise ValueError("manifest.yaml or opencode.json does not define any agents to export.")

    agent_ids = sorted(set(manifest_agents.keys()) & set(config_agents.keys()))
    if not agent_ids:
        raise ValueError("No overlapping agent definitions between manifest.yaml and opencode.json.")

    exported: Dict[str, Dict[str, str]] = {}
    for agent_id in agent_ids:
        manifest_agent = manifest_agents.get(agent_id) or {}
        role = str(manifest_agent.get("role", "")).strip()
        if not role:
            raise ValueError(f"Agent '{agent_id}' is missing a role in manifest.yaml")
        model = config_agents.get(agent_id, {}).get("model") or manifest_agent.get("model")
        if not model:
            raise ValueError(f"Agent '{agent_id}' is missing a model in both opencode.json and manifest.yaml")
        exported[agent_id] = {
            "role": role,
            "model": str(model),
        }
    return exported


def _write_pack_manifest(path: Path, payload: Dict[str, object]):
    if path.exists():
        raise FileExistsError(f"Pack manifest already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file_obj:
        yaml.safe_dump(payload, file_obj, sort_keys=False)


def cmd_create_from_current(args):
    manifest_data = _load_yaml_file(MANIFEST_PATH)
    with open(OPENCODE_CONFIG_PATH, "r", encoding="utf-8") as config_file:
        opencode_cfg = json.load(config_file)
    security_policy = _load_security_policy()

    jurisdiction_policy = _normalize_manifest_policy(manifest_data.get("jurisdiction_policy", ""))
    allow_local = "yes" if any(
        str(entry).strip().lower() == "local"
        for entry in security_policy.get("allowed_jurisdictions", [])
    ) else "no"

    agents_block = _build_export_agents(manifest_data, opencode_cfg)

    name = args.name.strip()
    if not name:
        raise SystemExit("Pack name is required.")

    focus = args.optimisation_focus.strip().lower()
    if focus not in ALLOWED_OPTIMISATION_FOCUS:
        raise SystemExit(
            f"optimisation-focus must be one of {sorted(ALLOWED_OPTIMISATION_FOCUS)}"
        )

    major = str(args.major).strip().lower()
    if major.startswith("v"):
        major = major[1:]
    if not major.isdigit():
        raise SystemExit("Major version must be numeric (e.g., 1, 2).")

    dir_label = f"v{major}"
    semantic_version = f"{int(major)}.0.0"

    description = args.description.strip()
    if not description:
        raise SystemExit("Description is required.")

    pack_payload = {
        "name": name,
        "version": semantic_version,
        "description": description,
        "jurisdiction_policy": jurisdiction_policy,
        "allow_local": allow_local,
        "optimisation_focus": focus,
        "agents": agents_block,
    }

    pack_path = PACKS_ROOT / name / dir_label / "pack.yaml"
    template_path = TEMPLATE_PACKS_ROOT / name / dir_label / "pack.yaml"

    _write_pack_manifest(pack_path, pack_payload)
    _write_pack_manifest(template_path, pack_payload)

    print("Created pack manifests:")
    print(f"  - {pack_path}")
    print(f"  - {template_path}")
    print(f"Agents exported: {', '.join(agents_block.keys())}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent Team Pack helper commands")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available team packs")
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser(
        "validate",
        help="Validate that a pack's referenced models exist in the live catalog",
    )
    p_validate.add_argument(
        "pack_name",
        nargs="?",
        help="Pack name to validate (omit when using --all)",
    )
    p_validate.add_argument(
        "--version",
        help="Specific pack version (directory label such as v1 or manifest version such as 1.0.0)",
    )
    p_validate.add_argument(
        "--all",
        action="store_true",
        help="Validate every discovered pack manifest",
    )
    p_validate.set_defaults(func=cmd_validate)

    p_apply = sub.add_parser("apply", help="Apply a named pack via select-models")
    p_apply.add_argument("pack_name", help="Pack name as defined in pack.yaml")
    p_apply.add_argument(
        "--version",
        help="Specific pack version (directory label such as v1 or manifest version such as 1.0.0)",
    )
    p_apply.set_defaults(func=cmd_apply)

    p_export = sub.add_parser(
        "create-from-current",
        help="Export the current agent/model configuration as a new pack",
    )
    p_export.add_argument("--name", required=True, help="Name of the new pack")
    p_export.add_argument("--major", required=True, help="Major version number (e.g., 1)")
    p_export.add_argument("--description", required=True, help="Description of the pack")
    p_export.add_argument(
        "--optimisation-focus",
        required=True,
        choices=sorted(ALLOWED_OPTIMISATION_FOCUS),
        help="Intent focus for the pack (cost, quality, balanced)",
    )
    p_export.set_defaults(func=cmd_create_from_current)

    return parser


def main(argv: Optional[List[str]] = None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
