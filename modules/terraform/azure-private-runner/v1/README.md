# Azure Private Runner Module

This module provisions an event-driven, scale-to-zero **Self-Hosted Runner Pool** using **Azure Container Apps** and **KEDA** within a private subnet.

## Features
- Runs standard **Ubuntu** base environments.
- Integrates KEDA scales to **zero** when idle.
- Uses User-Assigned Managed Identity for secure connection.

## Sizing Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| max_replicas | number | Maximum replica count for the runner Container App (1–25) | `5` | no |
| runner_cpu | string | CPU cores allocated to the runner container | `"0.5"` | no |
| runner_memory | string | Memory allocated to the runner container | `"1.0Gi"` | no |

Defaults are conservative dev/test values per the cost-governance guide; the composed templates raise them to `1.0` CPU / `2.0Gi` / `max_replicas = 5` for `prod`.
