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

## Outputs

| Name | Type | Description |
|------|------|-------------|
| id | string | The Resource ID of the Key Vault |
| vaultUri | string | The Vault URI |
