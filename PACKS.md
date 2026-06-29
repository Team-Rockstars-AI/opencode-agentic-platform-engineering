# Agent Team Packs

## Overview
"Team Packs" are curated, versioned configurations that bundle agents, models, prompts, skills, and policies into sharable and validated presets. They are designed to simplify the management of multi-agent teams by providing "known good" blueprints for different use cases (e.g., "Cost-Optimized Dev", "High-Quality Production", "Sovereign-Only").

Packs work in conjunction with the `/select-models` command and the `model-optimiser` skill. While `model-optimiser` handles the live discovery of available models, a Team Pack provides the strategic mapping and policy constraints for the entire team.

## Core Operations
*Note: These operations are currently in the design phase and will be implemented under Epic 4.*

*   **`pack list`**: Discover available team packs in the local repository and central registry.
*   **`pack apply <pack-name>`**: Apply a pack's configuration to the local `opencode.json`, setting up the agent team and model policies.
*   **`pack create-from-current`**: Export the current, manually-tuned agent and model configuration as a new, reusable pack.
*   **`pack validate`**: Verify that the current pack configuration is compatible with the live model catalog and meets all security/jurisdiction policies.
*   **PR-based Sharing**: Packs are stored as YAML manifests, allowing them to be shared, reviewed, and versioned via standard Pull Requests.

## Jurisdiction & Cost Policy
Team Packs are the primary vehicle for enforcing organizational policies regarding data residency and spend. Each pack defines:
*   **Allowed Jurisdictions**: (e.g., `EU`, `US`, `Global`) to ensure compliance with data sovereignty requirements.
*   **Optimization Focus**: (e.g., `cost`, `quality`, `balanced`) to align agent performance with budget constraints.

For more details on how these policies are enforced at the model level, see [`.opencode/memory.md`](.opencode/memory.md).

## Status
Team Packs are currently **design-level only**. Implementation progress is tracked in [`BUILD_PLAN.md`](BUILD_PLAN.md) under **Epic 4: Agent Team Packs & Model Profiles**.
