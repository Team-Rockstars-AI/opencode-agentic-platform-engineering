# Azure Private Runner Module (Bicep)

Deploys scale-to-zero **Self-Hosted Runner Pools** inside an Azure Container Apps Environment using Bicep.

## Sizing Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| maxReplicas | int | Maximum replica count for the runner Container App (1–25) | `5` | no |
| runnerCpu | string | CPU cores allocated to the runner container | `'0.5'` | no |
| runnerMemory | string | Memory allocated to the runner container | `'1.0Gi'` | no |

Defaults are conservative dev/test values per the cost-governance guide; the composed templates raise them to `'1.0'` CPU / `'2.0Gi'` / `maxReplicas: 5` for `prod`.
