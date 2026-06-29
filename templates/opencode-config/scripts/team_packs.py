#!/usr/bin/env python3
"""Helper CLI for discovering and applying Agent Team Packs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SELECT_MODELS_SCRIPT = REPO_ROOT / "scripts" / "select-models.py"
OPENCODE_CONFIG_PATH = REPO_ROOT / "opencode.json"
PACK_SEARCH_PATHS = [REPO_ROOT / "packs", REPO_ROOT / "templates" / "opencode-config" / "packs"]


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
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"yes", "y", "true", "1"}:
            return "yes"
        if text in {"no", "n", "false", "0"}:
            return "no"
    raise ValueError("allow_local must be yes/no (or boolean)")


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
        except ValueError as exc:
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

    for manifest in sorted(packs, key=lambda p: (p.name, p.dir_label, p.path)):
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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent Team Pack helper commands")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available team packs")
    p_list.set_defaults(func=cmd_list)

    p_apply = sub.add_parser("apply", help="Apply a named pack via select-models")
    p_apply.add_argument("pack_name", help="Pack name as defined in pack.yaml")
    p_apply.add_argument(
        "--version",
        help="Specific pack version (directory label such as v1 or manifest version such as 1.0.0)",
    )
    p_apply.set_defaults(func=cmd_apply)

    return parser


def main(argv: Optional[List[str]] = None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
