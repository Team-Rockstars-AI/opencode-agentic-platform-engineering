# Workflow: Agent Team Packs

- **Name:** Agent Team Packs & Model Profiles
- **Commands:** `/pack-list`, `/pack-apply`
- **Trigger:** Explicit user invocation via `/pack-list` or `/pack-apply`
- **Agent:** `orchestrator`
- **Script:** `python3 scripts/team_packs.py`

## Overview

The Agent Team Pack workflow allows operators to discover and apply curated, versioned "Team Packs" — pre-configured sets of agents and models optimized for specific jurisdictions (EU, EU+US, Global) and goals (Cost, Quality). This ensures consistent, governed, and resilient model configurations across the platform.

## Commands

### `/pack-list`

Lists all available agent team packs discovered in the repository.

**Steps:**
1. **Discovery:** The `orchestrator` runs `python3 scripts/team_packs.py list`.
2. **Presentation:** The script scans `packs/` and `templates/opencode-config/packs/` for `pack.yaml` manifests and displays a table of available packs, including their name, version, jurisdiction policy, and optimization focus.
3. **Selection:** The operator reviews the list to identify the desired pack for their environment.

### `/pack-apply`

Applies a selected agent team pack to the current workspace.

**Steps:**
1. **Selection:** The operator specifies the pack name (and optional version) to apply.
2. **Manifest Loading:** The `orchestrator` runs `python3 scripts/team_packs.py apply <pack-name> [--version vX]`.
3. **Mapping Generation:** The script loads the pack manifest, extracts the agent-to-model mapping, and generates a temporary mapping JSON.
4. **Implementation:** The script delegates to `scripts/select-models.py apply`, passing the mapping, jurisdiction policy, and local model preference from the pack.
5. **Verification:** `select-models.py` validates the models against the live catalog, updates `opencode.json`, `manifest.yaml`, and `agent_config.py`, and runs verification tests.
6. **Summary:** The `orchestrator` summarizes the applied configuration and reminds the team to document the change.

## Agent output contracts

| Stage | Agent | Expected output |
|-------|-------|----------------|
| Pack discovery | `orchestrator` | Table of available packs |
| Pack application | `orchestrator` | `## Milestone plan` (if part of a larger task) or a summary of the applied model matrix |

## Skills used

- `model-optimiser` — used by the underlying `select-models.py` script to validate and apply the mapping.
- `doc-standards` — used to ensure the resulting configuration is correctly documented.
