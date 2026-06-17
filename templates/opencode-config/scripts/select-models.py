#!/usr/bin/env python3
"""OpenCode ZEN Model Selector & Optimiser.

This script is a *data-gathering and apply* tool. It does NOT decide which model
each agent should use — that reasoning is performed by the orchestrator agent
(see the `model-optimiser` skill), which reads each agent's prompt and skills and
combines them with the freshly discovered model catalogs produced here.

Two subcommands:

  discover   Fetch the live OpenCode ZEN model list and the live Ollama model
             list, classify each model's jurisdiction, filter to the chosen
             policy, and print a structured JSON catalog to stdout.

  apply      Take a mapping JSON ({agent: {model}}) produced by the agent,
             validate that every chosen model actually exists in the live
             environment and is allowed under the policy, then write the
             configuration files and run verification tests (rolling back on
             any failure).
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

import yaml

ZEN_ENDPOINT = "https://opencode.ai/zen/v1"
LOCAL_ENDPOINT = "http://localhost:11434/v1"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
# Pricing is published only as HTML tables on the docs page (the JSON
# /zen/v1/models endpoint exposes availability but no cost). We scrape it
# best-effort: a parse failure must never break model discovery. The last
# successful scrape is cached so we can fall back to it (clearly flagged as
# stale) if a later fetch fails or the docs layout changes.
ZEN_DOCS_URL = "https://opencode.ai/docs/zen/"
PRICING_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".zen-pricing-cache.json")
# Below this many resolved prices a "successful" fetch is treated as a parse
# failure (the docs layout likely changed), triggering the cache fallback.
MIN_EXPECTED_PRICES = 5

CONFIG_FILES = ["opencode.json", "manifest.yaml", "agent_config.py"]

# Jurisdiction inferred from the model-id prefix (the part after "opencode/").
# Order matters only within a tier; the first matching keyword wins.
JURISDICTION_PREFIXES = [
    ("EU", ["mistral", "codestral", "ministral", "magistral", "devstral", "pixtral"]),
    ("US", ["claude", "gpt", "o1", "o3", "gemini", "grok"]),
    ("Sovereign", ["cohere", "north"]),
    ("Global", ["deepseek", "glm", "big-pickle", "qwen", "minimax", "kimi"]),
]
# Anything not matched above is treated as Global (the most-restricted tier),
# so an unknown model can never leak into an EU-only configuration.
DEFAULT_JURISDICTION = "Global"

# Which jurisdictions each policy admits (before the local toggle is applied).
POLICY_ALLOWED = {
    "eu": {"EU", "Sovereign", "Local"},
    "eu+us": {"EU", "Sovereign", "US", "Local"},
    "global": {"EU", "Sovereign", "US", "Global", "Local"},
}


def classify_jurisdiction(model_id):
    """Infer a jurisdiction tier from a model id such as 'opencode/claude-opus-4-8'."""
    base = model_id.split("/", 1)[-1].lower()
    for jurisdiction, prefixes in JURISDICTION_PREFIXES:
        for prefix in prefixes:
            if base.startswith(prefix):
                return jurisdiction
    return DEFAULT_JURISDICTION


def allowed_jurisdictions(policy, allow_local):
    """Resolve the set of permitted jurisdictions for a policy + local toggle."""
    allowed = set(POLICY_ALLOWED[policy])
    if allow_local != "yes":
        allowed.discard("Local")
    return allowed


def check_zen_provider():
    """Verifies if OpenCode ZEN is selected as the active provider."""
    if os.path.exists("manifest.yaml"):
        with open("manifest.yaml", "r", encoding="utf-8") as file_obj:
            manifest = yaml.safe_load(file_obj) or {}
            for cfg in manifest.get("agents", {}).values():
                if ZEN_ENDPOINT in cfg.get("endpoint", ""):
                    return True

    if os.path.exists("opencode.json"):
        with open("opencode.json", "r", encoding="utf-8") as file_obj:
            config = json.load(file_obj)
            for cfg in config.get("agent", {}).values():
                if ZEN_ENDPOINT in cfg.get("endpoint", "") or cfg.get("model", "").startswith("opencode/"):
                    return True

    return False


def get_user_input(prompt, options, default=None):
    """Helper to get validated user input."""
    if default:
        prompt_str = f"{prompt} [{'/'.join(options)}] (default: {default}): "
    else:
        prompt_str = f"{prompt} [{'/'.join(options)}]: "

    while True:
        val = input(prompt_str).strip().lower()
        if not val and default:
            return default.lower()
        for opt in options:
            if val == opt.lower() or val == opt.lower()[0]:
                return opt.lower()
        print(f"Invalid option. Please choose from {options}.")


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #
def fetch_zen_models():
    """Return the live list of OpenCode ZEN model ids via `opencode models`."""
    try:
        result = subprocess.run(
            ["opencode", "models", "opencode"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError(
            "Failed to list ZEN models via `opencode models opencode`. "
            "Is the OpenCode CLI installed and connected to Zen? "
            f"({exc})"
        ) from exc

    models = []
    for line in result.stdout.splitlines():
        model_id = line.strip()
        if model_id.startswith("opencode/"):
            models.append(model_id)
    return models


def _parse_html_tables(doc):
    """Return [(headers, rows)] for every <table> in an HTML document."""
    tables = []
    for table in re.findall(r"<table[^>]*>(.*?)</table>", doc, re.S):
        headers = [
            re.sub(r"<[^>]+>", "", h).strip()
            for h in re.findall(r"<th[^>]*>(.*?)</th>", table, re.S)
        ]
        rows = []
        for row in re.findall(r"<tr>(.*?)</tr>", table, re.S):
            cells = [
                html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            ]
            if cells:
                rows.append(cells)
        tables.append((headers, rows))
    return tables


def _scrape_zen_prices(doc):
    """Parse per-1M-token input/output pricing out of the ZEN docs HTML.

    The docs render two tables: a model table (display name -> model id) and a
    pricing table (display name -> input/output/cached). We join them on the
    display name. Tiered rows (e.g. "GPT 5.4 (> 272K tokens)") are collapsed to
    the first/lower tier. Returns {model_id: {"input": str, "output": str}}.
    """
    tables = _parse_html_tables(doc)

    name_to_id = {}
    for headers, rows in tables:
        if "model id" in " ".join(headers).lower():
            for cells in rows:
                if len(cells) >= 2:
                    name_to_id[cells[0]] = cells[1]

    prices = {}
    for headers, rows in tables:
        joined_headers = " ".join(headers).lower()
        if "input" in joined_headers and "output" in joined_headers:
            for cells in rows:
                if len(cells) < 3:
                    continue
                base_name = re.sub(r"\s*\(.*?\)\s*$", "", cells[0]).strip()
                model_id = name_to_id.get(base_name)
                if model_id and f"opencode/{model_id}" not in prices:
                    prices[f"opencode/{model_id}"] = {"input": cells[1], "output": cells[2]}
    return prices


def _read_pricing_cache():
    """Return the cached pricing snapshot dict, or None if absent/unreadable."""
    try:
        with open(PRICING_CACHE_FILE, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except (OSError, ValueError):
        return None


def _write_pricing_cache(prices):
    """Persist a fresh pricing snapshot as the last-known-good fallback."""
    snapshot = {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "source": ZEN_DOCS_URL,
        "prices": prices,
    }
    try:
        with open(PRICING_CACHE_FILE, "w", encoding="utf-8") as file_obj:
            json.dump(snapshot, file_obj, indent=2)
    except OSError:
        pass  # Caching is best-effort; never block on a write failure.
    return snapshot


def fetch_zen_prices():
    """Resolve ZEN pricing, with a clearly-flagged stale fallback.

    Returns ``(prices, meta)`` where ``meta["status"]`` is one of:
      * ``"live"``      — freshly scraped from the docs page just now.
      * ``"cached"``    — the live fetch failed (unreachable, or the docs layout
                          changed so prices no longer parse); falling back to the
                          last good snapshot. ``meta["fetched_at"]`` says when it
                          was captured and ``meta["reason"]`` why live failed.
      * ``"unavailable"`` — live fetch failed AND no cached snapshot exists, so no
                          prices are known. ``prices`` is ``{}``.
    """
    reason = None
    try:
        req = urllib.request.Request(ZEN_DOCS_URL, headers={"User-Agent": "select-models"})
        with urllib.request.urlopen(req, timeout=5) as response:
            doc = response.read().decode("utf-8", errors="replace")
        prices = _scrape_zen_prices(doc)
        if len(prices) >= MIN_EXPECTED_PRICES:
            snapshot = _write_pricing_cache(prices)
            return prices, {"status": "live", "fetched_at": snapshot["fetched_at"], "source": ZEN_DOCS_URL}
        reason = (
            f"the docs page was reached but only {len(prices)} prices parsed "
            "(the pricing table layout may have changed)"
        )
    except (urllib.error.URLError, OSError) as exc:
        reason = f"the docs page could not be fetched ({exc})"

    cache = _read_pricing_cache()
    if cache and cache.get("prices"):
        return cache["prices"], {
            "status": "cached",
            "fetched_at": cache.get("fetched_at"),
            "source": cache.get("source", ZEN_DOCS_URL),
            "reason": reason,
        }

    return {}, {"status": "unavailable", "reason": reason}


def _parse_param_billions(parameter_size):
    """Convert an Ollama parameter_size string like '7.6B' or '30B' to a float."""
    if not parameter_size:
        return None
    text = parameter_size.strip().upper().rstrip("B")
    try:
        return round(float(text), 1)
    except ValueError:
        return None


def fetch_ollama_models():
    """Return the list of locally installed Ollama models with size metadata.

    Prefers the HTTP /api/tags endpoint (richer metadata); falls back to the
    `ollama list` CLI. Returns [] if Ollama is unreachable.
    """
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
        models = []
        for entry in payload.get("models", []):
            name = entry.get("name")
            if not name:
                continue
            details = entry.get("details", {}) or {}
            param_size = details.get("parameter_size")
            size_bytes = entry.get("size")
            models.append(
                {
                    "id": f"ollama/{name}",
                    "parameter_size": param_size,
                    "parameter_billions": _parse_param_billions(param_size),
                    "size_gb": round(size_bytes / 1e9, 1) if size_bytes else None,
                }
            )
        return models
    except (urllib.error.URLError, ValueError, OSError):
        pass

    # Fallback: parse `ollama list` output.
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    models = []
    for line in result.stdout.splitlines()[1:]:  # skip header
        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        models.append(
            {
                "id": f"ollama/{name}",
                "parameter_size": None,
                "parameter_billions": None,
                "size_gb": None,
            }
        )
    return models


def build_catalog(policy, allow_local, machine_type=None):
    """Build the filtered model catalog the agent reasons over."""
    allowed = allowed_jurisdictions(policy, allow_local)
    prices, pricing_meta = fetch_zen_prices()

    zen = []
    for model_id in fetch_zen_models():
        jurisdiction = classify_jurisdiction(model_id)
        if jurisdiction in allowed:
            price = prices.get(model_id, {})
            zen.append(
                {
                    "id": model_id,
                    "jurisdiction": jurisdiction,
                    "input_per_1m": price.get("input"),
                    "output_per_1m": price.get("output"),
                }
            )

    ollama = []
    if allow_local == "yes":
        for model in fetch_ollama_models():
            model = dict(model)
            model["jurisdiction"] = "Local"
            ollama.append(model)

    return {
        "policy": {
            "jurisdiction": policy,
            "allow_local": allow_local,
            "machine_type": machine_type,
            "allowed_jurisdictions": sorted(allowed),
        },
        "pricing": pricing_meta,
        "zen": zen,
        "ollama": ollama,
    }


# --------------------------------------------------------------------------- #
# Validation + apply
# --------------------------------------------------------------------------- #
def validate_mapping(mapping, policy, allow_local, zen_ids, ollama_ids):
    """Validate a proposed mapping before writing anything.

    Checks, for every agent's chosen model:
      * supported namespace (opencode/ or ollama/)
      * the model actually EXISTS in the freshly discovered environment
      * its inferred jurisdiction is permitted by the policy
    Returns the mapping enriched with the authoritative jurisdiction per agent.
    """
    allowed = allowed_jurisdictions(policy, allow_local)
    enriched = {}

    for agent, cfg in mapping.items():
        model = cfg.get("model", "")
        if model.startswith("ollama/"):
            jurisdiction = "Local"
            if model not in ollama_ids:
                raise ValueError(
                    f"Agent '{agent}' assigned local model '{model}' which is not "
                    f"installed in Ollama. Installed: {sorted(ollama_ids) or '(none)'}"
                )
        elif model.startswith("opencode/"):
            jurisdiction = classify_jurisdiction(model)
            if model not in zen_ids:
                raise ValueError(
                    f"Agent '{agent}' assigned ZEN model '{model}' which is not "
                    f"available in the active OpenCode ZEN environment."
                )
        else:
            raise ValueError(f"Unsupported model namespace for {agent}: {model}")

        if jurisdiction not in allowed:
            raise ValueError(
                f"Agent '{agent}' model '{model}' has jurisdiction '{jurisdiction}', "
                f"not permitted under policy '{policy}' (allowed: {sorted(allowed)})."
            )

        enriched[agent] = {"model": model, "jurisdiction": jurisdiction}

    return enriched


def backup_files():
    """Creates backups of the configuration files."""
    for file_name in CONFIG_FILES:
        if os.path.exists(file_name):
            shutil.copy(file_name, file_name + ".bak")
            print(f"Created backup of {file_name}")


def restore_backups():
    """Restores configuration files from backups."""
    for file_name in CONFIG_FILES:
        if os.path.exists(file_name + ".bak"):
            shutil.move(file_name + ".bak", file_name)
            print(f"Restored backup of {file_name}")


def remove_backups():
    """Removes backup files."""
    for file_name in CONFIG_FILES:
        if os.path.exists(file_name + ".bak"):
            os.remove(file_name + ".bak")


def apply_mapping(mapping, jurisdiction):
    """Applies model mapping to opencode.json, manifest.yaml, and agent_config.py."""
    if os.path.exists("opencode.json"):
        with open("opencode.json", "r", encoding="utf-8") as file_obj:
            config = json.load(file_obj)

        for agent, cfg in mapping.items():
            if agent in config.get("agent", {}):
                config["agent"][agent]["model"] = cfg["model"]
                if cfg["model"].startswith("ollama/"):
                    config["agent"][agent]["endpoint"] = LOCAL_ENDPOINT
                else:
                    config["agent"][agent]["endpoint"] = ZEN_ENDPOINT

        with open("opencode.json", "w", encoding="utf-8") as file_obj:
            json.dump(config, file_obj, indent=2)
        print("Updated opencode.json")

    if os.path.exists("manifest.yaml"):
        with open("manifest.yaml", "r", encoding="utf-8") as file_obj:
            manifest = yaml.safe_load(file_obj) or {}

        manifest["jurisdiction_policy"] = f"{jurisdiction.upper()}-Sovereign" if jurisdiction != "global" else "Global"
        for agent, cfg in mapping.items():
            if agent in manifest.get("agents", {}):
                manifest["agents"][agent]["model"] = cfg["model"]
                manifest["agents"][agent]["jurisdiction"] = cfg["jurisdiction"]
                if cfg["model"].startswith("ollama/"):
                    manifest["agents"][agent]["endpoint"] = LOCAL_ENDPOINT
                else:
                    manifest["agents"][agent]["endpoint"] = ZEN_ENDPOINT

        with open("manifest.yaml", "w", encoding="utf-8") as file_obj:
            yaml.safe_dump(manifest, file_obj, default_flow_style=False)
        print("Updated manifest.yaml")

    if os.path.exists("agent_config.py"):
        with open("agent_config.py", "r", encoding="utf-8") as file_obj:
            lines = file_obj.readlines()

        new_lines = []
        in_policy = False
        for line in lines:
            if "SECURITY_POLICY = {" in line:
                in_policy = True
                new_lines.append(line)
                continue
            if in_policy:
                if "}" in line:
                    in_policy = False
                if "allowed_jurisdictions" in line:
                    if jurisdiction == "eu":
                        new_lines.append('    "allowed_jurisdictions": ["EU", "Sovereign", "Local"],\n')
                    elif jurisdiction == "eu+us":
                        new_lines.append('    "allowed_jurisdictions": ["EU", "Sovereign", "US", "Local"],\n')
                    else:
                        new_lines.append('    "allowed_jurisdictions": ["EU", "Sovereign", "US", "Global", "Local"],\n')
                    continue
                if "default_code_generation_model" in line and "builder-infra-tf" in mapping:
                    new_lines.append(f'    "default_code_generation_model": "{mapping["builder-infra-tf"]["model"]}",\n')
                    continue
                if "default_task_execution_model" in line and "verifier" in mapping:
                    new_lines.append(f'    "default_task_execution_model": "{mapping["verifier"]["model"]}",\n')
                    continue
            new_lines.append(line)

        with open("agent_config.py", "w", encoding="utf-8") as file_obj:
            file_obj.writelines(new_lines)
        print("Updated agent_config.py")


def run_tests():
    """Runs verification tests on the updated configuration."""
    print("\n--- Running Verification Tests ---")

    if os.path.exists("agent_config.py"):
        print("Running agent_config.py self-test...")
        result = subprocess.run([sys.executable, "agent_config.py"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"agent_config.py self-test failed:\n{result.stderr}")
            return False
        print("agent_config.py self-test passed.")

    if os.path.exists("scripts/validate-skills.py"):
        print("Running validate-skills.py...")
        result = subprocess.run([sys.executable, "scripts/validate-skills.py"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"validate-skills.py failed:\n{result.stderr}")
            return False
        print("validate-skills.py passed.")

    print("All verification tests passed successfully!")
    return True


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #
def cmd_discover(args):
    if not check_zen_provider():
        print("ERROR: OpenCode ZEN is not selected as the active provider.", file=sys.stderr)
        print("Please connect to Zen first using: opencode connect --provider zen", file=sys.stderr)
        sys.exit(1)

    jurisdiction = args.jurisdiction
    allow_local = args.allow_local
    machine_type = args.machine_type

    if jurisdiction is None:
        jurisdiction = get_user_input("Select Jurisdiction Policy", ["EU", "EU+US", "Global"], "Global")
    if allow_local is None:
        allow_local = get_user_input("Allow local (Ollama) models?", ["Yes", "No"], "No")
    if allow_local == "yes" and machine_type is None:
        machine_type = get_user_input(
            "Specify machine type running local models", ["Low-end", "Mid-range", "High-end"], "Mid-range"
        )

    catalog = build_catalog(jurisdiction, allow_local, machine_type)
    json.dump(catalog, sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_apply(args):
    if not check_zen_provider():
        print("ERROR: OpenCode ZEN is not selected as the active provider.", file=sys.stderr)
        print("Please connect to Zen first using: opencode connect --provider zen", file=sys.stderr)
        sys.exit(1)

    with open(args.mapping, "r", encoding="utf-8") as file_obj:
        raw_mapping = json.load(file_obj)

    # Re-discover the live environment to validate availability.
    zen_ids = set(fetch_zen_models())
    ollama_ids = {m["id"] for m in fetch_ollama_models()}

    try:
        mapping = validate_mapping(raw_mapping, args.jurisdiction, args.allow_local, zen_ids, ollama_ids)
    except ValueError as exc:
        print(f"ERROR: Invalid mapping — {exc}", file=sys.stderr)
        sys.exit(1)

    print("\n=== APPLYING MODEL MAPPING ===")
    print(f"Jurisdiction Policy: {args.jurisdiction.upper()}")
    print("-" * 60)
    print(f"{'Agent':<22} | {'Model':<36} | {'Jurisdiction':<12}")
    print("-" * 60)
    for agent, cfg in mapping.items():
        print(f"{agent:<22} | {cfg['model']:<36} | {cfg['jurisdiction']:<12}")
    print("-" * 60)

    backup_files()
    try:
        apply_mapping(mapping, args.jurisdiction)
        if run_tests():
            print("\nSUCCESS: All tests passed! Removing backups.")
            remove_backups()
            print("Please update AGENTS.md, BUILD_JOURNAL.md, and DISCOVERIES_LOG.md to document the changes.")
        else:
            print("\nFAILURE: Verification tests failed! Rolling back changes.")
            restore_backups()
            sys.exit(1)
    except Exception as exc:  # noqa: BLE001 - we want to roll back on any failure
        print(f"\nERROR: Implementation failed: {exc}")
        print("Rolling back changes.")
        restore_backups()
        sys.exit(1)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Discover and apply optimised models for OpenCode agents.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_discover = sub.add_parser("discover", help="Print a filtered JSON catalog of available models.")
    p_discover.add_argument("--jurisdiction", choices=["eu", "eu+us", "global"])
    p_discover.add_argument("--allow-local", choices=["yes", "no"], dest="allow_local")
    p_discover.add_argument("--machine-type", choices=["low-end", "mid-range", "high-end"], dest="machine_type")
    p_discover.set_defaults(func=cmd_discover)

    p_apply = sub.add_parser("apply", help="Validate and apply a mapping JSON produced by the agent.")
    p_apply.add_argument("--mapping", required=True, help="Path to the mapping JSON file.")
    p_apply.add_argument("--jurisdiction", choices=["eu", "eu+us", "global"], required=True)
    p_apply.add_argument("--allow-local", choices=["yes", "no"], dest="allow_local", default="no")
    p_apply.set_defaults(func=cmd_apply)

    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
