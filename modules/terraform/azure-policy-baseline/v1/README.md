# Azure Policy Baseline Terraform Module

Subscription-scope assignments of **built-in** Azure Policy definitions that back the platform's secure-by-design baseline at runtime. Authoring-time gates (agent audits, Checkov, checklists) prevent non-compliant IaC from merging; this module prevents non-compliant resources from being *created or kept* in the subscription — including clickops changes made outside the pipelines.

## Policies enforced

| # | Built-in policy (display name) | Definition GUID | Effect |
|---|---|---|---|
| 1 | Allowed locations | `e56962a6-4747-49cd-b67b-bf8b01975c4c` | deny (fixed in definition) |
| 2 | Secure transfer to storage accounts should be enabled | `404c3081-a854-4457-ae30-26a93ef643f9` | `policy_effect` |
| 3 | Storage accounts should disable public network access | `b2982f36-99f2-4db5-8eff-283140c09693` | `policy_effect` |
| 4 | Azure Key Vault should disable public network access | `405c5871-3e91-4644-8a63-58e19d68ff5b` | `policy_effect` |
| 5 | Key vaults should have deletion protection enabled | `0b60c0b2-2dc2-4e1c-b5c9-abbed971de53` | `policy_effect` |
| 6 | Network interfaces should not have public IPs | `83a86a26-fd1f-447c-b59d-e51f44264114` | deny (fixed in definition), toggleable |

GUIDs verified against the [Microsoft Learn built-in policy index](https://learn.microsoft.com/azure/governance/policy/samples/built-in-policies).

> ⚠️ Assignments apply to the **entire subscription**, not just the platform's resource groups. With `enforcement_mode = true` and `policy_effect = "Deny"`, non-compliant deployments anywhere in the subscription are blocked. Start with the defaults (`Audit` + enforce) or `enforcement_mode = false` in shared subscriptions.

## Usage

```hcl
module "policy_baseline" {
  source            = "./modules/terraform/azure-policy-baseline/v1"
  project_name      = "my-platform"
  environment       = "prod"
  subscription_id   = "00000000-0000-0000-0000-000000000000"
  allowed_locations = ["westeurope", "northeurope"]
  policy_effect     = "Deny"
}
```

## Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| project_name | string | Name of the project | - | yes |
| environment | string | Deployment environment (dev/test/prod) | `dev` | no |
| subscription_id | string | Subscription GUID the baseline is assigned to | - | yes |
| allowed_locations | list(string) | Regions resources may be deployed to | `["westeurope", "northeurope"]` | no |
| policy_effect | string | Effect for the parameterisable policies (2–5): Audit/Deny/Disabled | `Audit` | no |
| enforcement_mode | bool | `false` creates all assignments as DoNotEnforce (report only) | `true` | no |
| enable_deny_public_ip_nics | bool | Assign the NIC public-IP deny policy | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| policy_assignment_ids | Map of policy short-name to assignment resource ID |
