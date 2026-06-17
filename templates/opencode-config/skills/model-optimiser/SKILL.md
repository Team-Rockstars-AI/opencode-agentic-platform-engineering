---
name: model-optimiser
description: Selects and configures optimized models for each agent based on jurisdiction, cost/quality focus, and local hardware capabilities.
license: MIT
compatibility: opencode
---

## Trigger
This skill is activated when the user runs the `/select-models` slash command or requests model optimization under the OpenCode ZEN provider.

## Overview
Model selection is **agent-driven**. The `scripts/select-models.py` helper only gathers fresh data
(the live OpenCode ZEN catalog and the live Ollama catalog) and applies a final mapping. The
reasoning — matching each agent to the best *available* model — is performed here by reading each
agent's prompt and the skills it relies on, then combining that with the discovered catalog. Never
hard-code a model list: a model is only eligible if it appears in the freshly discovered catalog,
which is the guard against pinning models that do not exist in the active environment.

## Steps

### 1. Provider Verification
- Verify that OpenCode ZEN is selected as the active provider.
- If OpenCode ZEN is not selected, halt and instruct the user to connect to Zen first using `opencode connect --provider zen`.

### 2. User Preferences Gathering
Prompt the user to select:
1. **Jurisdiction Policy** (`eu` / `eu+us` / `global`):
   - `eu`: EU-sovereign and Sovereign-friendly models only (plus local models if enabled).
   - `eu+us`: EU/Sovereign and US-based models (Anthropic, Google, OpenAI).
   - `global`: All available models including high-performance global models (DeepSeek, Qwen, GLM, MiniMax).
2. **Local Models (Ollama)** (`yes` / `no`):
   - `yes`: Allow locally installed Ollama models to be mixed in for specific roles.
   - `no`: Cloud (ZEN) models only.
3. **Optimization Focus** (`cost` / `quality`):
   - `cost`: Prefer free or ultra-low-cost models that are still good enough for the role.
   - `quality`: Prefer maximum reasoning and code-generation capability.
4. **Hardware Profile** (only if Local Models = `yes`): `low-end` (≤8B), `mid-range` (≤27B), or `high-end` (70B+).

### 3. Discover Available Models
Run the discovery helper with the gathered preferences and read the JSON catalog it prints:

```bash
python3 scripts/select-models.py discover --jurisdiction <eu|eu+us|global> --allow-local <yes|no> [--machine-type <low-end|mid-range|high-end>]
```

The catalog contains:
- `zen`: every live ZEN model permitted under the policy, each with an inferred `jurisdiction` and
  its `input_per_1m` / `output_per_1m` price (scraped fresh from the ZEN docs pricing tables; may be
  `null` if a price could not be resolved or `"Free"` for free tiers).
- `ollama`: every locally installed model (only when local is enabled), with `parameter_size`,
  `parameter_billions`, and `size_gb` (local models are always free).
- `policy`: the resolved policy, local toggle, machine type, and `allowed_jurisdictions`.
- `pricing`: the provenance of the price data — `status` is `live`, `cached`, or `unavailable`.

If the catalog is empty or missing expected models, report that to the user rather than inventing ids.

### 3a. Check Pricing Provenance (mandatory)
Inspect `pricing.status` from the catalog **before** building the proposal and act accordingly:
- **`live`** — prices are current. Proceed normally.
- **`cached`** — the live fetch failed (the docs page was unreachable, or its pricing-table layout
  changed and prices no longer parse). **Clearly tell the user that live pricing could not be
  fetched**, state the reason (`pricing.reason`) and the date of the snapshot being used
  (`pricing.fetched_at`), and warn that the figures may be out of date. Then **offer to either
  continue using this last-known pricing or abort** — do not proceed until the user chooses.
- **`unavailable`** — the live fetch failed and there is no cached snapshot. **Clearly tell the user
  no pricing is available**, then offer to continue selecting on capability/jurisdiction alone (the
  proposal will show prices as "unknown") or abort. Do not invent prices.

### 4. Reason Per-Agent Selection
For **each** agent defined in `manifest.yaml`, read its prompt at `.opencode/prompts/<agent>.txt`,
note the skills it references, and its `role`/`tier` from the manifest. Then choose the best model
for that agent **from the discovered catalog only**, using this guidance:

- **Strategic Planning** (`orchestrator`, tier `High-Reasoning`): the strongest reasoning model
  available under the policy/focus.
- **Code-Generation** (`builder-infra-tf`, `builder-infra-bicep`, `builder-pipelines`): prefer
  code-specialized models (e.g. `*-codex`, `codestral`, `qwen*-coder`, `deepseek-coder`).
- **Task-Execution** (`verifier`, `security-auditor`, `plan-validator`, `code-reviewer`,
  `explorer`, `test-writer`, `docs-writer`): cheaper/faster models that meet the task; under `cost`
  focus prefer free tiers.
- For **local** assignments, pick an Ollama model whose `parameter_billions` fits the machine type
  (`low-end` ≤8B, `mid-range` ≤27B, `high-end` larger), and that suits the role (coder models for
  builders, general models for execution).
- Respect the `cost`/`quality` focus throughout.

### 5. Proposal Presentation
Present a structured proposal table to the user: agent → selected model → jurisdiction → hosting
(Cloud/Local) → input/output price per 1M tokens (from the catalog's `input_per_1m` /
`output_per_1m`; show "Free" for local models and free tiers, and "unknown" when a price is null).
State the policy and the overall cost direction versus the current configuration, using the catalog
prices rather than guessing. If `pricing.status` is `cached` or `unavailable`, repeat the warning
from step 3a in the proposal header so the user is reminded the prices are stale or missing.

### 6. Implementation
Upon user acceptance, write the chosen assignments to a mapping file and apply them. The mapping is
`{ "<agent>": { "model": "<id>" }, ... }`:

```bash
python3 scripts/select-models.py apply --mapping /tmp/model-mapping.json --jurisdiction <eu|eu+us|global> --allow-local <yes|no>
```

The `apply` step re-validates that every chosen model still exists in the live environment and is
permitted under the policy, backs up `opencode.json` / `manifest.yaml` / `agent_config.py`, writes
the new configuration (including the `SECURITY_POLICY` defaults in `agent_config.py`), and runs
verification tests. On any failure it rolls back automatically.

### 7. Documentation
- Update `AGENTS.md`, `BUILD_JOURNAL.md`, and `DISCOVERIES_LOG.md` to record the new model configuration.
