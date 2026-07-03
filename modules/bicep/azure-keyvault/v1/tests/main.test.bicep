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

// Central diagnostics invocation
module testVaultDiagnostics '../main.bicep' = {
  name: 'test-vault-diagnostics-deployment'
  params: {
    name: 'kv-test-vault-2'
    resourceGroupName: 'rg-test-vault'
    location: location
    tenantId: '00000000-0000-0000-0000-000000000000'
    logAnalyticsWorkspaceId: '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x'
  }
}
