# Agent Team Packs

## Overview
"Team Packs" are curated, versioned configurations that bundle agents, models, prompts, skills, and policies into sharable and validated presets. They are designed to simplify the management of multi-agent teams by providing "known good" blueprints for different use cases (e.g., "Cost-Optimized Dev", "High-Quality Production", "Sovereign-Only").

Packs work in conjunction with the `/select-models` command and the `model-optimiser` skill. While `model-optimiser` handles the live discovery of available models, a Team Pack provides the strategic mapping and policy constraints for the entire team.

## Pack Lifecycle
The lifecycle of a Team Pack follows a structured flow to ensure safety and consistency:

1.  **Discover**: Use `/pack-list` to find available packs in the local repository or central registry.
2.  **Select**: Choose a pack that aligns with the project's cost, quality, and jurisdiction requirements.
3.  **Apply**: Use `/pack-apply <name>` to map the pack's blueprint to the local `opencode.json`.
4.  **Validate**: The `select-models.py apply` logic (invoked by `/pack-apply`) validates that the requested models are available in the live ZEN/Ollama catalogs and comply with the `SECURITY_POLICY`.
5.  **Share**: Export custom configurations as new packs and share them via Pull Requests to establish organizational standards.

## Core Operations
*   **`/pack-list`**: Scans `packs/` and `templates/opencode-config/packs/` for `pack.yaml` manifests and displays a summary table of available presets.
*   **`/pack-apply <pack-name> [--version <v>]`**: 
    1.  Loads the specified `pack.yaml`.
    2.  Resolves the model mapping (preferring `model` if set, otherwise the first available entry in `preferred_model_ids`).
    3.  Invokes `scripts/select-models.py apply` with the resolved mapping, `jurisdiction_policy`, and `allow_local` settings.
    4.  Updates `opencode.json`, `manifest.yaml`, and `agent_config.py` upon successful validation.
*   **`/pack-validate <pack-name> [--version <v>]`** (or `--all`):
    1.  Discovers the specified pack(s).
    2.  Runs a live discovery of the OpenCode ZEN and Ollama catalogs.
    3.  Verifies that every model referenced in the pack is available and permitted under the pack's jurisdiction policy.
    4.  Reports a PASS/FAIL status per agent without modifying any configuration.
*   **`/pack-create-from-current --name <name> --major <m> --description <text> --optimisation-focus <focus>`**:
    1.  Captures the active agent/model configuration from `opencode.json` and `manifest.yaml`.
    2.  Derives the jurisdiction and local-model policy from `agent_config.py`.
    3.  Generates a new, versioned `pack.yaml` in both the local `packs/` directory and the `templates/` tree.
    4.  Enables rapid sharing of "known good" configurations via Pull Requests.

## Pack Schema
Team Packs are defined in `pack.yaml` manifests located under `packs/<pack-name>/<version>/`.

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Unique identifier for the pack (e.g., `cost-optimised-dev`). |
| `version` | `string` | Semantic version of the pack (e.g., `1.0.0`). |
| `description` | `string` | Human-readable description of the pack's intent and trade-offs. |
| `jurisdiction_policy` | `string` | Allowed: `eu`, `eu+us`, `global`. Maps to `SECURITY_POLICY` in `agent_config.py`. |
| `allow_local` | `boolean|string` | Whether to allow local Ollama models. Accepts `yes`/`no`, `true`/`false`, `1`/`0`. Normalised internally to `"yes"` or `"no"`. |
| `optimisation_focus` | `string` | Informational intent hint: `cost`, `quality`, or `balanced`. Does not automatically select models; use `/select-models` to optimise against this intent. |
| `agents` | `map` | Map of agent IDs (must match `opencode.json`) to their configuration. |

### Agent Configuration Schema
| Field | Type | Description |
|---|---|---|
| `role` | `string` | The agent's functional role (e.g., `code-generation`, `task-execution`). |
| `model` | `string` | (Optional) Explicit model ID (e.g., `opencode/gpt-5.1-codex`). |
| `preferred_model_ids` | `list<string>` | (Optional) Ordered list of preferred models; the first one available in the live catalog is selected. |

## Sovereignty & Policy Integration
Team Packs are the primary mechanism for enforcing sovereignty at the team level.
*   **Jurisdiction**: The `jurisdiction_policy` in the pack manifest is applied to `manifest.yaml` and used to update the `allowed_jurisdictions` in `agent_config.py`.
*   **Local Execution**: The `allow_local` toggle determines if `Local` (Ollama) models are admitted into the `allowed_jurisdictions` list.
*   **Enforcement**: During `pack apply`, the `select-models.py` script ensures that no agent is assigned a model that violates the resulting `SECURITY_POLICY`.

## Governance
*   **Ownership**: Packs are maintained by the Platform Engineering team.
*   **Versioning**: Packs use semantic versioning. Breaking changes (e.g., removing a model or changing an agent role) require a major version bump.
*   **Deprecation**: Old pack versions are kept for backward compatibility but marked as deprecated in `pack list` once a newer version is validated.

## Pack Authorship Workflow
To contribute or create a new Team Pack, follow this workflow:

1.  **Layout**: Create a new directory under `packs/<name>/v<major>/` (e.g., `packs/high-perf/v1/`).
2.  **Manifest**: Create a `pack.yaml` following the [Pack Schema](#pack-schema).
3.  **Local Validation**:
    *   Run `/pack-list` to ensure the pack is discovered and valid.
    *   Run `/pack-apply <name>` to test the mapping logic against your local environment.
    *   **CI Recommendation**: It is highly recommended to run `/pack-validate --all` in CI pipelines to ensure all committed packs remain valid against the live model catalog.
4.  **Contribution**: Submit a Pull Request containing:
    *   The new pack directory and manifest.
    *   A description of the pack's intent, target use case, and cost/quality trade-offs.
    *   Evidence of successful local validation.
5.  **Review**: All new packs must undergo architectural and security review to ensure they align with platform standards and sovereignty requirements.

## Example: Cost-Optimised Dev
Located at `packs/cost-optimised-dev/v1/pack.yaml`:
```yaml
name: cost-optimised-dev
version: 1.0.0
description: >-
  Lean, cloud-only preset optimised for day-to-day development work. Prioritises
  low to mid-cost Zen models that still meet the EU+US-Sovereign residency
  policy so engineers can iterate quickly without overrunning spend limits.
jurisdiction_policy: eu+us
allow_local: no
optimisation_focus: cost
agents:
  orchestrator:
    role: strategic-planner
    preferred_model_ids:
      - opencode/gpt-5.1 # Balanced choice for planning; use opencode/north-mini-code-free for max savings.
  builder-infra-tf:
    role: code-generation
    preferred_model_ids:
      - opencode/gpt-5.1-codex # High-quality coding; can be swapped for local Ollama models via /select-models.
  # ... other agents
```

> **Note on Cost Optimization:** The models listed above (`gpt-5.1`) represent a balanced trade-off between cost and reasoning quality for development. For maximal cost savings, operators should use `/select-models` to select cheaper models (e.g., `opencode/north-mini-code-free`) or enable `allow_local: yes` to leverage zero-marginal-cost local Ollama models.

## Status
Team Packs are **implemented** as of Milestone 4.2. Core discovery and application logic is available via the `/pack-list` and `/pack-apply` commands.
