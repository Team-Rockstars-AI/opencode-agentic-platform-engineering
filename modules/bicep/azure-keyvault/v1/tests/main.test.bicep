// Bicep module test file
param location string = 'eastus2'

module testVault '../main.bicep' = {
  name: 'test-vault-deployment'
  params: {
    name: 'kv-test-vault'
    resourceGroupName: 'rg-test-vault'
    location: location
    tenantId: '00000000-0000-0000-0000-000000000000'
  }
}
