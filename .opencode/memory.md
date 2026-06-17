# OpenCode Zen — Model Optimization & In-Project Memory

## Overview
This file is the persistent, in-project memory for how agent models are selected and optimized under
the OpenCode Zen framework. Model selection is **dynamic and agent-driven** — it is no longer a
hardcoded lookup table. Whenever models need (re)tuning, run `/select-models` rather than editing
`opencode.json` / `manifest.yaml` by hand.

## OpenCode Zen
OpenCode Zen provides cost-price API access to coding-optimized models. It is the default, highly
recommended backend configuration. Optionally, locally installed **Ollama** models can be mixed in
for sovereign, zero-cost execution of selected roles.

## How Model Selection Works (`/select-models`)
The `model-optimiser` skill drives the orchestrator through a discover → reason → apply flow, backed
by `scripts/select-models.py`:

1. **Gather preferences** — jurisdiction (`eu` / `eu+us` / `global`), allow local Ollama models
   (`yes` / `no`), optimization focus (`cost` / `quality`), and hardware tier (when local is on).
2. **Discover** — `python3 scripts/select-models.py discover ...` fetches a *fresh* catalog:
   - Live ZEN models via `opencode models opencode`.
   - Live installed Ollama models via the `/api/tags` endpoint (with parameter sizes).
   - Live per-1M-token pricing scraped from the ZEN docs (`https://opencode.ai/docs/zen/`).
   - Each model is classified by **jurisdiction inferred from its id prefix** (mistral→EU,
     claude/gpt/gemini→US, cohere/north→Sovereign, deepseek/glm/qwen/minimax→Global; unknown→Global),
     then filtered to the policy's allowed set.
3. **Reason** — the orchestrator reads each agent's prompt + skills + role and picks the best
   *available* model per agent from the catalog (never inventing ids).
4. **Apply** — `python3 scripts/select-models.py apply --mapping ...` re-validates that every chosen
   model still exists live and is permitted by the policy, backs up the config files, writes the
   changes, runs verification tests, and rolls back on any failure.

### Pricing Provenance & Fallback
Each discovery reports a `pricing.status`:

| Status | Meaning | Operator action |
|---|---|---|
| `live` | Prices scraped fresh just now (and cached to `scripts/.zen-pricing-cache.json`). | Proceed. |
| `cached` | Live fetch failed — docs unreachable **or** the pricing-table layout changed. The last good snapshot is used. | The skill states this clearly with the snapshot date and reason, then asks whether to continue on the stale pricing or abort. |
| `unavailable` | Live fetch failed and no cache exists. | The skill states no pricing is available and offers to continue selecting on capability/jurisdiction alone. |

## Sovereignty Guardrails
- **`agent_config.py`** enforces a `SECURITY_POLICY` (`allowed_jurisdictions`) that overrides any
  non-compliant model for Code-Generation / Task-Execution roles and raises on restricted-task
  violations. `/select-models apply` keeps this policy in sync with the chosen jurisdiction.
- The `apply` step refuses any mapping containing a model that is not live in the environment or
  whose inferred jurisdiction is outside the policy — preventing the "model not available" breakage
  that takes down the orchestration loop.

## Current Default Configuration
The repository ships with a sovereign-friendly default (see `manifest.yaml` / `opencode.json`):
- **Orchestrator:** `opencode/gemini-3.5-flash` (US authorized fallback).
- **All other subagents:** `opencode/north-mini-code-free` (Sovereign, Cohere) by default; some roles
  may be remapped to local Ollama models when the operator enables them.

Re-run `/select-models` at any time to re-optimize against the *current* live catalog and pricing.
