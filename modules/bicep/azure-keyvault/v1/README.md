# Azure Key Vault Bicep Module

This is a self-contained, secure Bicep module to provision an Azure Key Vault with RBAC authorization.

## Usage

```bicep
module vault './modules/bicep/azure-keyvault/v1/main.bicep' = {
  name: 'vault-deployment'
  params: {
    name: 'kv-my-platform'
    resourceGroupName: 'rg-my-resources'
    location: 'eastus2'
    tenantId: 'YOUR-TENANT-ID'
  }
}
```

## Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| name | string | Name of the Key Vault | - | yes |
| resourceGroupName | string | Resource group name | - | yes |
| location | string | Azure region | - | yes |
| tenantId | string | Active Directory tenant ID | - | yes |
| skuName | string | SKU name (standard/premium) | `standard` | no |
| softDeleteRetentionInDays | int | Days soft-deleted items are retained (7–90) | `90` | no |
| publicNetworkAccess | string | Public network access (Enabled/Disabled) | `Disabled` | no |
| logAnalyticsWorkspaceId | string | The resource ID of the central Log Analytics workspace for diagnostics | `''` | no |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| id | string | The Resource ID of the Key Vault |
| vaultUri | string | The Vault URI |
