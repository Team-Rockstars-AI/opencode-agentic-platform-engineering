# Agent Team Packs

## Overview
"Team Packs" are curated, versioned configurations that bundle agents, models, prompts, skills, and policies into sharable and validated presets. They are designed to simplify the management of multi-agent teams by providing "known good" blueprints for different use cases (e.g., "Cost-Optimized Dev", "High-Quality Production", "Sovereign-Only").

Packs work in conjunction with the `/select-models` command and the `model-optimiser` skill. While `model-optimiser` handles the live discovery of available models, a Team Pack provides the strategic mapping and policy constraints for the entire team.

## Core Operations
*   **`pack list`**: Discover available team packs in the local repository and central registry.
*   **`pack apply <pack-name>`**: Apply a pack's configuration to the local `opencode.json`, setting up the agent team and model policies.
*   **PR-based Sharing**: Packs are stored as YAML manifests, allowing them to be shared, reviewed, and versioned via standard Pull Requests.

## Pack Schema

Team Packs are defined in `pack.yaml` manifests located under `packs/<pack-name>/<version>/`.

```yaml
name: string                # Unique identifier for the pack
version: string             # Semantic version of the pack (e.g., 1.0.0)
description: string         # Human-readable description of the pack's intent
jurisdiction_policy: string # One of: eu, eu+us, global
allow_local: boolean|string # Whether to allow local Ollama models (yes/no)
optimisation_focus: string  # One of: cost, quality, balanced
agents:                     # Map of agent IDs to their model configuration
  <agent-id>:
    role: string            # Agent role (strategic-planner, code-generation, task-execution, research)
    model: string           # (Optional) Explicit model ID to use
    preferred_model_ids:    # (Optional) List of preferred model IDs; the first available one is used
      - string
```

### Example: Cost-Optimised Dev
Located at `packs/cost-optimised-dev/v1/pack.yaml`:
```yaml
name: cost-optimised-dev
version: 1.0.0
jurisdiction_policy: eu+us
allow_local: no
optimisation_focus: cost
agents:
  orchestrator:
    role: strategic-planner
    preferred_model_ids: ["opencode/gpt-5.1"]
  builder-infra-tf:
    role: code-generation
    model: opencode/gpt-5.1-codex
  # ... other agents
```

## Integration with `/select-models`

Team Packs provide the **blueprint** for the agent team. When a pack is applied via `/pack-apply`:
1.  The `team_packs.py` script parses the manifest.
2.  It generates a model mapping based on the `model` or `preferred_model_ids` fields.
3.  It invokes `select-models.py apply` with the generated mapping, the pack's `jurisdiction_policy`, and the `allow_local` setting.
4.  The `model-optimiser` logic validates that the requested models are available in the live ZEN/Ollama catalogs before updating `opencode.json`.

## Status
Team Packs are **implemented** as of Milestone 4.2. Core discovery and application logic is available via the `/pack-list` and `/pack-apply` commands.
