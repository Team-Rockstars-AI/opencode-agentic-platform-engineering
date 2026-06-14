param name string
param resourceGroupName string
param location string
param tenantId string
param skuName string = 'standard'
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
    accessPolicies: []
  }
}

output id string = kv.id
output vaultUri string = kv.properties.vaultUri
