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

## Outputs

| Name | Description |
|------|-------------|
| id | The Resource ID of Key Vault |
| vault_uri | The Vault URI |
