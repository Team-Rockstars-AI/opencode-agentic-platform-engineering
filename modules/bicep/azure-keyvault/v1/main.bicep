@minLength(3)
@maxLength(24)
param name string
param resourceGroupName string
param location string
param tenantId string

@allowed([
  'standard'
  'premium'
])
param skuName string = 'standard'

@minValue(7)
@maxValue(90)
param softDeleteRetentionInDays int = 90

@description('The public network access setting for the Key Vault: Enabled or Disabled')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Disabled'

resource kv 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: name
  location: location
  properties: {
    sku: {
      family: 'A'
      name: skuName
    }
    tenantId: tenantId
    enableRbacAuthorization: true
    enabledForDiskEncryption: true
    softDeleteRetentionInDays: softDeleteRetentionInDays
    enablePurgeProtection: true
    publicNetworkAccess: publicNetworkAccess
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    accessPolicies: []
  }
}

output id string = kv.id
output vaultUri string = kv.properties.vaultUri
