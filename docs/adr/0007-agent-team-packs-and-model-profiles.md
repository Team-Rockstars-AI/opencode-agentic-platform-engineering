# ADR 0007: Agent Team Packs & Model Profiles

## Status
Accepted

## Date
2026-06-29

## Context
The platform currently utilizes dynamic per-agent model selection via the `/select-models` command and the `model-optimiser` skill. While this provides flexibility, platform engineers encounter significant combinatorial complexity when trying to balance cost, quality, and jurisdiction across a multi-agent team. Furthermore, manually tuned configurations are difficult to share across projects or teams, leading to brittle, non-standardized agent environments.

## Decision
We will introduce versioned "team packs" as higher-level presets that define curated agent and model configurations.

1.  **Pack Manifests:** Introduce a structured manifest format (`pack.yaml`) that defines pack metadata, jurisdiction/cost policies, agent graphs, and specific model-to-agent mappings.
2.  **Explicit Lifecycle:** Codify the pack lifecycle as a five-stage process:
    *   **Discover:** Locate available packs via `pack list`.
    *   **Select:** Choose a pack based on project requirements.
    *   **Apply:** Execute `pack apply` to map the blueprint to the environment.
    *   **Validate:** Automated verification of model availability and policy compliance.
    *   **Share:** Standardized PR-based workflow for contributing new packs.
3.  **Layered Integration:** Packs will be layered on top of the existing `select-models` workflow. A pack provides the "blueprint," while `select-models` continues to handle the live discovery and application of models from the ZEN and Ollama catalogs.
4.  **Sovereignty Enforcement:** Pack-level `jurisdiction_policy` and `allow_local` settings will dynamically update the `SECURITY_POLICY` in `agent_config.py`, ensuring that all agents operate within the project's compliance boundaries.
5.  **Governance & Ownership:** 
    *   **Authorship:** Platform Engineering team authors and maintains core packs.
    *   **Review:** All new packs or version updates must undergo architectural review.
    *   **Versioning:** Semantic versioning (SemVer) is enforced for all packs.
    *   **Deprecation:** Clear lifecycle for retiring old or insecure pack versions.

## Implementation
Milestone 4.1 established the design and documentation for the Team Pack concept.
Milestone 4.2 implemented the core Team Pack infrastructure:
- **`scripts/team_packs.py`**: A helper CLI for discovering and applying packs.
- **Example Packs**: `cost-optimised-dev` and `high-quality-prod` presets shipped under `packs/`.
- **Command Wiring**: Registered `/pack-list` and `/pack-apply` in `opencode.json` to expose the functionality to the agent team.
- **Template Parity**: Included pack manifests and command definitions in the scaffold templates.

## Consequences
- **Positive:** Reduces complexity for end-users by providing "known good" configurations.
- **Positive:** Enables sharing of organizational standards for agent teams.
- **Positive:** Safer upgrade path as packs can be versioned and tested independently.
- **Positive:** Stronger sovereignty guarantees by linking pack selection to `SECURITY_POLICY` enforcement.
- **Negative:** Introduces versioning overhead for pack maintainers.
- **Negative:** Potential for drift between a pack's static definitions and the live, dynamic model catalog.
- **Negative:** Requires governance to prevent a proliferation of redundant or low-quality packs.

## References
- [ADR 0006: Continuous Regulatory Compliance Mapping](./0006-continuous-regulatory-compliance-mapping.md)
- [.opencode/memory.md](../../.opencode/memory.md) (Model Optimization & Zen Integration)
