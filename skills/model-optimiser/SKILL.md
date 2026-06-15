---
name: model-optimiser
description: Selects and configures optimized models for each agent based on jurisdiction, cost/quality focus, and local hardware capabilities.
license: MIT
compatibility: opencode
---

## Trigger
This skill is activated when the user runs the `/select-models` slash command or requests model optimization under the OpenCode ZEN provider.

## Steps

### 1. Provider Verification
- Verify that OpenCode ZEN is selected as the active provider.
- If OpenCode ZEN is not selected, halt and instruct the user to connect to Zen first using `opencode connect --provider zen`.

### 2. User Preferences Gathering
Prompt the user to select:
1. **Jurisdiction Policy**:
   - `EU`: Strict EU-sovereign models only (Mistral, local models).
   - `EU+US`: EU-sovereign and US-based models (Anthropic, Google, OpenAI, Mistral).
   - `Global`: All available models including high-performance global models (DeepSeek, Qwen, GLM, MiniMax).
2. **Local Models (Ollama)**:
   - `Yes`: Allow local models to be mixed in for specific roles.
   - `No`: Cloud-only models.
3. **Optimization Focus**:
   - `Cost`: Prioritize free or ultra-low-cost models that still offer good quality suitable for their tasks.
   - `Quality`: Prioritize maximum reasoning and code-generation capabilities.
4. **Hardware Profile** (Only if Local Models = `Yes`):
   - `Low-end`: 8GB - 16GB RAM (runs models up to 8B parameters).
   - `Mid-range`: 16GB - 32GB RAM (runs models up to 27B parameters).
   - `High-end`: 64GB+ RAM (runs models up to 70B+ parameters).

### 3. Model Mapping Matrix

Based on the user's selections, map each agent role to the optimal model:

| Agent Role | Jurisdiction | Focus | Local Allowed | Hardware | Selected Model | Cost (Input/Output per 1M) |
|---|---|---|---|---|---|---|
| **Strategic Planning** (`orchestrator`) | EU | Quality | - | - | `opencode/mistral-large-latest` | $2.00 / $6.00 |
| **Strategic Planning** (`orchestrator`) | EU | Cost | - | - | `opencode/mistral-small-latest` | $1.00 / $3.00 |
| **Strategic Planning** (`orchestrator`) | EU+US | Quality | - | - | `opencode/claude-sonnet-4-6` | $3.00 / $15.00 |
| **Strategic Planning** (`orchestrator`) | EU+US | Cost | - | - | `opencode/gemini-3.5-flash` | $1.50 / $9.00 |
| **Strategic Planning** (`orchestrator`) | Global | Quality | - | - | `opencode/claude-sonnet-4-6` | $3.00 / $15.00 |
| **Strategic Planning** (`orchestrator`) | Global | Cost | - | - | `opencode/deepseek-v4-pro` | $1.74 / $3.84 |
| **Code-Generation** (`builder-*`) | EU | Quality | Yes | Mid/High | `ollama/codestral:22b` | Local (Free) |
| **Code-Generation** (`builder-*`) | EU | Quality | No / Low | - | `opencode/codestral-latest` | $1.00 / $3.00 |
| **Code-Generation** (`builder-*`) | EU | Cost | Yes | Low/Mid/High | `ollama/mistral:7b` | Local (Free) |
| **Code-Generation** (`builder-*`) | EU | Cost | No | - | `opencode/mistral-small-latest` | $1.00 / $3.00 |
| **Code-Generation** (`builder-*`) | EU+US | Quality | - | - | `opencode/claude-sonnet-4-6` | $3.00 / $15.00 |
| **Code-Generation** (`builder-*`) | EU+US | Cost | - | - | `opencode/gpt-5.4-mini` | $0.75 / $4.50 |
| **Code-Generation** (`builder-*`) | Global | Quality | - | - | `opencode/claude-sonnet-4-6` | $3.00 / $15.00 |
| **Code-Generation** (`builder-*`) | Global | Cost | - | - | `opencode/north-mini-code-free` | Free |
| **Task-Execution** (`verifier`, `auditor`, etc.) | EU | Quality | Yes | Low/Mid/High | `ollama/ministral:8b` | Local (Free) |
| **Task-Execution** (`verifier`, `auditor`, etc.) | EU | Quality | No | - | `opencode/mistral-small-latest` | $1.00 / $3.00 |
| **Task-Execution** (`verifier`, `auditor`, etc.) | EU | Cost | Yes | Low/Mid/High | `ollama/mistral:7b` | Local (Free) |
| **Task-Execution** (`verifier`, `auditor`, etc.) | EU | Cost | No | - | `opencode/mistral-small-latest` | $1.00 / $3.00 |
| **Task-Execution** (`verifier`, `auditor`, etc.) | EU+US | Quality | - | - | `opencode/gemini-3.5-flash` | $1.50 / $9.00 |
| **Task-Execution** (`verifier`, `auditor`, etc.) | EU+US | Cost | - | - | `opencode/gemini-3-flash` | $0.50 / $3.00 |
| **Task-Execution** (`verifier`, `auditor`, etc.) | Global | Quality | - | - | `opencode/deepseek-v4-pro` | $1.74 / $3.84 |
| **Task-Execution** (`verifier`, `auditor`, etc.) | Global | Cost | - | - | `opencode/deepseek-v4-flash-free` | Free |

### 4. Proposal Presentation
Present a structured proposal to the user detailing:
- Selected model for each agent.
- Jurisdiction and hosting type (Cloud vs. Local).
- Estimated cost per 1M tokens.
- Total estimated cost change.

### 5. Implementation
Upon user acceptance:
- Backup existing `opencode.json`, `manifest.yaml`, and `agent_config.py`.
- Update the model configurations in `opencode.json` and `manifest.yaml`.
- Update the `SECURITY_POLICY` in `agent_config.py` to match the selected jurisdiction and defaults.

### 6. Verification Testing
- Ask the orchestrator to delegate a non-destructive action to each of the agents (e.g., a simple self-test or validation check).
- If all tests succeed, proceed to documentation.
- If any test fails, attempt to auto-resolve or roll back to the backup configurations.

### 7. Documentation
- Update `AGENTS.md`, `BUILD_JOURNAL.md`, and `DISCOVERIES_LOG.md` to record the new model configuration.
