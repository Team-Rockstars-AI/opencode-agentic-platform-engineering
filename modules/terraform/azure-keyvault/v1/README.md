# Azure Key Vault Terraform Module

This is a self-contained, highly secure Terraform module to provision an Azure Key Vault with RBAC authentication enabled by default.

## Usage

```hcl
module "vault" {
  source              = "./modules/terraform/azure-keyvault/v1"
  name                = "kv-my-platform"
  resource_group_name = "rg-my-resources"
  location            = "eastus2"
  tenant_id           = "YOUR-TENANT-ID"
}
```

## Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| name | string | Name of Key Vault | - | yes |
| resource_group_name | string | Resource group name | - | yes |
| location | string | Azure region | - | yes |
| tenant_id | string | Active Directory tenant ID | - | yes |
| sku_name | string | SKU name (standard/premium) | `standard` | no |
| soft_delete_retention_days | number | Number of days soft-deleted keys are retained. Ensures state resiliency and recovery. | `90` | no |
| purge_protection_enabled | bool | Is purge protection enabled? Prevents permanent deletion during retention window. | `true` | no |
| public_network_access_enabled | bool | Is public network access enabled? Should be disabled for private connectivity. | `false` | no |

## Security Rationale

This module enforces a high-security baseline by default to align with **GDPR, DORA, and BIO** requirements:
- **Soft Delete (90 days):** Ensures that accidentally deleted secrets can be recovered, supporting operational resilience.
- **Purge Protection:** Prevents the immediate permanent deletion of the vault or its objects, protecting against malicious or accidental data loss.
- **Disabled Public Access:** Restricts connectivity to Private Endpoints, ensuring that sensitive cryptographic material is never exposed to the public internet.

## Outputs

| Name | Description |
|------|-------------|
| id | The Resource ID of Key Vault |
| vault_uri | The Vault URI |
