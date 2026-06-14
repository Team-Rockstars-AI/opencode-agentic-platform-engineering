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
param softDeleteRetentionInDays int = 7

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
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    accessPolicies: []
  }
}

output id string = kv.id
output vaultUri string = kv.properties.vaultUri
