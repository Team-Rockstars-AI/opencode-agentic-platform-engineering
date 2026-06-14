# OpenCode Zen — Model Optimization & In-Project Memory

## Overview
This file serves as a persistent, in-project memory tracking model cost and performance evaluations under the OpenCode Zen framework. It aligns agent roles with the most cost-effective and capable models.

## OpenCode Zen
OpenCode Zen provides cost-price API access to coding-optimized models. It is the default, highly recommended backend configuration.

## Evaluation & Optimization Analysis (Current vs. Recommended)

| Agent | Current Model | Recommended Model (Zen) | Price change (per 1M input / output) | Reasoning |
|---|---|---|---|---|
| **`orchestrator`** | `opencode/gemini-3.1-pro` | `opencode/gemini-3.5-flash` | `$2.00 / $12.00` → `$1.50 / $9.00` | Faster, lower latency, and highly cost-optimized for high-level planning. |
| **`builder-infra-tf`** | `opencode/claude-sonnet-4-5` | `opencode/claude-sonnet-4-6` | `$3.00 / $15.00` → `$3.00 / $15.00` | Upgrade to the newer, more capable iteration of Sonnet for complex multi-resource TF dependency graphing. |
| **`builder-infra-bicep`** | `opencode/claude-sonnet-4-5` | `opencode/claude-sonnet-4-6` | `$3.00 / $15.00` → `$3.00 / $15.00` | Upgrade to the newer, more capable iteration of Sonnet for Bicep template structure design. |
| **`builder-pipelines`** | `opencode/claude-sonnet-4-5` | `opencode/claude-sonnet-4-6` | `$3.00 / $15.00` → `$3.00 / $15.00` | Upgrade to the newer iteration of Sonnet to guarantee maximum pipeline syntax correctness and OIDC flow safety. |
| **`verifier`** | `opencode/gemini-3-flash` | `opencode/deepseek-v4-flash` | `$0.50 / $3.00` → `$0.14 / $0.28` | **Over 10x cheaper on outputs.** Spectacular speed for parsing compiler and linter outputs. |
| **`security-auditor`** | `opencode/gpt-5.4` | `opencode/deepseek-v4-pro` | `$2.50 / $15.00` → `$1.74 / $3.48` | **4.3x cheaper on outputs.** Superior reasoning for threat modeling, compliance gating, and vulnerability scanning. |
| **`plan-validator`** | `opencode/gemini-3-flash` | `opencode/deepseek-v4-flash` | `$0.50 / $3.00` → `$0.14 / $0.28` | **Over 10x cheaper on outputs.** Near-instantaneous plan logs parsing and safety pattern matching. |
| **`code-reviewer`** | `opencode/gpt-5.3-codex` (Deprecated July 23, 2026) | `opencode/deepseek-v4-pro` | `$1.75 / $14.00` → `$1.74 / $3.48` | Avoids imminent deprecation. Provides world-class architectural reviews at a fraction of the cost. |
| **`explorer`** | `ollama/qwen3.5` (Local) | `opencode/deepseek-v4-flash-free` | Local Compute → **FREE (Hosted)** | Completely removes local runtime dependency on Ollama while improving file-system exploration quality. |
| **`test-writer`** | `ollama/qwen3:8b` (Local) | `opencode/big-pickle` | Local Compute → **FREE (Hosted)** | Replaces local compute with a powerful hosted coding-centric model optimized for producing tests. |
| **`docs-writer`** | `ollama/gemma4:latest` (Local) | `opencode/deepseek-v4-flash-free` | Local Compute → **FREE (Hosted)** | Excellent formatting and summarization for ADRs and runbooks completely free of charge. |

## Actions Taken
- Upgraded all builders to Claude Sonnet 4.6.
- Optimized the verifier and plan-validator to use the ultra-low-cost DeepSeek V4 Flash.
- Remapped local Ollama dependents to high-performing Free Zen endpoints.
- Saved these settings persistently in the workspace `opencode.json` configuration file.
