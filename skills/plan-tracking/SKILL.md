---
name: plan-tracking
description: Guidelines for tracking execution plans, milestone status, and session state
license: MIT
compatibility: opencode
---

## Plan Tracking Guidelines

All execution plans and milestone statuses must be tracked and validated to ensure safety and transparency:

### 1. Plan Generation & Conversion
- **Dry-Run Execution:** Generate dry-run execution plans (`terraform plan -out=tfplan` or `az deployment sub what-if`) before applying any changes.
- **JSON Conversion:** Convert Terraform plans to JSON format (`terraform show -json tfplan > tfplan.json`) for automated parsing and validation.

### 2. Resource Action Tracking
- **Create (green):** Track resources scheduled for creation. Verify they conform to naming conventions, tagging rules, and SKU requirements.
- **Update (yellow):** Track resources scheduled for update. Verify that changing properties will not trigger accidental resource recreation.
- **Delete (red):** Track resources scheduled for deletion. Block immediately if any critical stateful resource is marked for destruction.
- **Replace/Recreate (red + green):** Track resources scheduled for replacement. Block immediately if any critical stateful resource is marked for replacement.

### 3. Milestone Status & Session State
- **Milestone Tracking:** Update the build plan / backlog (`BUILD_PLAN.md`) to reflect the current milestone status, and archive completed milestones in `BUILD_JOURNAL.md`.
- **Session State:** Maintain the in-project memory (`.opencode/memory.md`) to track actions taken, model optimizations, and cost reports.
